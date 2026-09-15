from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
from typing import Dict, Optional, Tuple


class Version(str, Enum):
    REACTIVE = "v0_reactive"
    RELATIONSHIP = "v1_relationship"
    AFFECT = "v2_affect"
    CONCERN = "v3_concern"
    HABIT = "v4_habit"


@dataclass(frozen=True)
class Event:
    kind: str = "neutral"
    actor: Optional[str] = None
    intensity: float = 1.0
    context: Optional[str] = None
    available_actions: Tuple[str, ...] = ()
    reward: float = 0.0
    forced_action: Optional[str] = None
    concern: Optional[str] = None


class PersistentCharacter:
    """Tiny non-language character runtime used for controlled mechanism tests.

    The runtime intentionally keeps cognition and presentation separate. It emits
    symbolic actions and state snapshots only. A conversational or narrative
    surface can observe these outputs, but it is never queried during decision
    making.
    """

    def __init__(self, version: Version):
        self.version = Version(version)
        self.tick = 0

        # Base organism-like deficits. Higher means more pressure to act.
        self.fatigue = 0.25
        self.affiliation = 0.55
        self.competence = 0.15

        # Optional mechanisms. They are allocated only when the version enables
        # them so the complexity curve can be measured directly.
        self.relationships: Dict[str, float] = {}
        self.threat_residue = 0.0
        self.active_concern: Optional[str] = None
        self.concern_strength = 0.0
        self.habits: Dict[Tuple[str, str], float] = {}
        self.last_action: Optional[str] = None
        self.last_context: Optional[str] = None

        self.trace = []

    @property
    def has_relationship_memory(self) -> bool:
        return self.version in {
            Version.RELATIONSHIP,
            Version.AFFECT,
            Version.CONCERN,
            Version.HABIT,
        }

    @property
    def has_affect_residue(self) -> bool:
        return self.version in {Version.AFFECT, Version.CONCERN, Version.HABIT}

    @property
    def has_concern_persistence(self) -> bool:
        return self.version in {Version.CONCERN, Version.HABIT}

    @property
    def has_habit_learning(self) -> bool:
        return self.version is Version.HABIT

    def _clamp(self, value: float, low: float = 0.0, high: float = 1.0) -> float:
        return max(low, min(high, value))

    def _drift(self) -> None:
        self.fatigue = self._clamp(self.fatigue + 0.04)
        self.affiliation = self._clamp(self.affiliation + 0.025)
        self.competence = self._clamp(self.competence + 0.02)

        if self.has_relationship_memory:
            for actor, value in list(self.relationships.items()):
                value *= 0.998
                if abs(value) < 0.005:
                    del self.relationships[actor]
                else:
                    self.relationships[actor] = value

        if self.has_affect_residue:
            self.threat_residue *= 0.72
            if self.threat_residue < 0.001:
                self.threat_residue = 0.0

        if self.has_concern_persistence and self.active_concern is not None:
            self.concern_strength *= 0.97
            if self.concern_strength < 0.08:
                self.active_concern = None
                self.concern_strength = 0.0

    def _relationship(self, actor: Optional[str]) -> float:
        if not self.has_relationship_memory or actor is None:
            return 0.0
        return self.relationships.get(actor, 0.0)

    def _process_event(self, event: Event) -> tuple[float, float]:
        immediate_threat = 0.0
        task_pressure = 0.0

        if event.kind == "support" and event.actor:
            if self.has_relationship_memory:
                self.relationships[event.actor] = self._clamp(
                    self.relationships.get(event.actor, 0.0) + 0.22 * event.intensity,
                    -1.0,
                    1.0,
                )

        elif event.kind == "hostility" and event.actor:
            immediate_threat = self._clamp(0.90 * event.intensity)
            if self.has_relationship_memory:
                self.relationships[event.actor] = self._clamp(
                    self.relationships.get(event.actor, 0.0) - 0.28 * event.intensity,
                    -1.0,
                    1.0,
                )
            if self.has_affect_residue:
                self.threat_residue = max(
                    self.threat_residue, self._clamp(0.75 * event.intensity)
                )

        elif event.kind == "shock":
            immediate_threat = self._clamp(event.intensity)
            if self.has_affect_residue:
                self.threat_residue = max(
                    self.threat_residue, self._clamp(0.90 * event.intensity)
                )

        elif event.kind == "task_assign":
            task_pressure = self._clamp(0.80 * event.intensity)
            if self.has_concern_persistence:
                self.active_concern = event.concern or "task"
                self.concern_strength = max(
                    self.concern_strength, self._clamp(0.75 * event.intensity)
                )

        elif event.kind == "task_cancel":
            if self.has_concern_persistence:
                if event.concern is None or event.concern == self.active_concern:
                    self.active_concern = None
                    self.concern_strength = 0.0

        elif event.kind == "outcome" and self.has_habit_learning:
            if self.last_action is not None and self.last_context is not None:
                key = (self.last_context, self.last_action)
                updated = self.habits.get(key, 0.0) + 0.35 * event.reward
                self.habits[key] = self._clamp(updated, -1.0, 1.0)

        return immediate_threat, task_pressure

    def _default_actions(self, event: Event) -> Tuple[str, ...]:
        if event.available_actions:
            return event.available_actions
        if event.actor:
            return (
                f"socialize:{event.actor}",
                f"avoid:{event.actor}",
                "idle",
            )
        return ("rest", "work", "idle")

    def _score_action(
        self,
        action: str,
        event: Event,
        immediate_threat: float,
        task_pressure: float,
    ) -> float:
        if action == "idle":
            return 0.10
        if action == "rest":
            return self.fatigue
        if action == "work":
            score = self.competence + task_pressure
            if self.has_concern_persistence and self.active_concern is not None:
                score += 0.90 * self.concern_strength
            return score

        if action.startswith("socialize:"):
            actor = action.split(":", 1)[1]
            relation = self._relationship(actor)
            return (
                self.affiliation
                + 0.85 * max(relation, 0.0)
                - 0.35 * max(-relation, 0.0)
            )

        if action.startswith("avoid:") or action == "avoid":
            actor = action.split(":", 1)[1] if ":" in action else event.actor
            relation = self._relationship(actor)
            score = immediate_threat + 0.90 * max(-relation, 0.0)
            if self.has_affect_residue:
                score += 0.75 * self.threat_residue
            return score

        # Contextual routine actions have no semantic cognition in the base
        # runtime. Their only learned bias comes from the habit mechanism.
        score = 0.10
        if self.has_habit_learning and event.context is not None:
            score += self.habits.get((event.context, action), 0.0)
        return score

    def _apply_action_effects(self, action: str, event: Event) -> None:
        if action == "rest":
            self.fatigue = self._clamp(self.fatigue - 0.45)
        elif action == "work":
            self.competence = self._clamp(self.competence - 0.45)
            if self.has_concern_persistence and self.active_concern is not None:
                self.concern_strength = self._clamp(self.concern_strength - 0.30)
                if self.concern_strength < 0.20:
                    self.active_concern = None
                    self.concern_strength = 0.0
        elif action.startswith("socialize:"):
            self.affiliation = self._clamp(self.affiliation - 0.45)

        if self.has_habit_learning:
            self.last_action = action
            self.last_context = event.context

    def step(self, event: Event) -> str:
        self.tick += 1
        self._drift()
        immediate_threat, task_pressure = self._process_event(event)

        if event.forced_action is not None:
            action = event.forced_action
            scores = {action: None}
        else:
            actions = self._default_actions(event)
            scored = [
                (
                    self._score_action(
                        action, event, immediate_threat, task_pressure
                    ),
                    -index,
                    action,
                )
                for index, action in enumerate(actions)
            ]
            score, _, action = max(scored)
            scores = {candidate: candidate_score for candidate_score, _, candidate in scored}
            scores["selected_score"] = score

        self._apply_action_effects(action, event)
        snapshot = self.snapshot()
        self.trace.append(
            {
                "tick": self.tick,
                "event": {
                    "kind": event.kind,
                    "actor": event.actor,
                    "context": event.context,
                    "reward": event.reward,
                },
                "action": action,
                "scores": scores,
                "state": snapshot,
            }
        )
        return action

    def snapshot(self) -> dict:
        state = {
            "tick": self.tick,
            "needs": {
                "fatigue": round(self.fatigue, 6),
                "affiliation": round(self.affiliation, 6),
                "competence": round(self.competence, 6),
            },
        }
        if self.has_relationship_memory:
            state["relationships"] = {
                actor: round(value, 6)
                for actor, value in sorted(self.relationships.items())
            }
        if self.has_affect_residue:
            state["threat_residue"] = round(self.threat_residue, 6)
        if self.has_concern_persistence:
            state["active_concern"] = self.active_concern
            state["concern_strength"] = round(self.concern_strength, 6)
        if self.has_habit_learning:
            state["habits"] = {
                f"{context}|{action}": round(value, 6)
                for (context, action), value in sorted(self.habits.items())
            }
            state["last_action"] = self.last_action
            state["last_context"] = self.last_context
        return state

    def persistent_state_bytes(self) -> int:
        return len(json.dumps(self.snapshot(), sort_keys=True).encode("utf-8"))

    def mechanism_count(self) -> int:
        return (
            3
            + int(self.has_relationship_memory)
            + int(self.has_affect_residue)
            + int(self.has_concern_persistence)
            + int(self.has_habit_learning)
        )
