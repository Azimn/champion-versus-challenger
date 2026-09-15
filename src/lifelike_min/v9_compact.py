from __future__ import annotations

import json

from .exp007_challenger import EligibilityTraceCharacter
from .runtime import Event


class CompactV9Character(EligibilityTraceCharacter):
    """Structural-compaction challenger derived from frozen v9.

    This class adds no behavioral capability. It removes two duplicate persistence
    paths demonstrated redundant by the v9 global-ablation tournament:

    1. The old single-concern compatibility state (`active_concern` and
       `concern_strength`) is not stored and the old base concern persistence branch
       is disabled. The bounded `concerns` ledger is authoritative. Active concern
       and strength remain available as deterministic diagnostic views.
    2. The old immediate-habit `last_action` and `last_context` fields are not
       stored. The age-zero v9 context-action trace supplies the same immediately
       preceding subject-accessible pair when an unlabeled immediate outcome arrives.

    The language renderer remains external and non-causal.
    """

    @property
    def has_concern_persistence(self) -> bool:
        # Disable the obsolete base single-concern state/update branch. EXP-004's
        # bounded concern ledger remains active through ConcernLedgerCharacter.
        return False

    @property
    def active_concern(self):
        concerns = getattr(self, "concerns", {})
        if not concerns:
            return None
        return max(concerns.items(), key=lambda item: item[1])[0]

    @active_concern.setter
    def active_concern(self, value) -> None:
        # Base/compatibility writes are deliberately not persisted.
        del value

    @property
    def concern_strength(self) -> float:
        concerns = getattr(self, "concerns", {})
        if not concerns:
            return 0.0
        return max(concerns.values())

    @concern_strength.setter
    def concern_strength(self, value: float) -> None:
        del value

    @property
    def last_action(self):
        return None

    @last_action.setter
    def last_action(self, value) -> None:
        del value

    @property
    def last_context(self):
        return None

    @last_context.setter
    def last_context(self, value) -> None:
        del value

    def _score_action(
        self,
        action: str,
        event: Event,
        immediate_threat: float,
        task_pressure: float,
    ) -> float:
        if action == "work":
            # This is the same work policy previously reached through the base
            # single-concern compatibility fields, but it reads the authoritative
            # concern ledger directly through derived views.
            score = self.competence + task_pressure
            if self.active_concern is not None:
                score += 0.90 * self.concern_strength
            return score
        return super()._score_action(
            action,
            event,
            immediate_threat,
            task_pressure,
        )

    def _apply_immediate_outcome(self, event: Event) -> bool:
        if event.context is not None or event.reward == 0.0:
            return False
        # An age-zero trace is the contextual action selected on the immediately
        # preceding event. A non-context action intervening in between ages the old
        # trace, leaving no age-zero candidate and therefore no immediate attribution.
        current = [row for row in self.eligibility_records if row.age == 0]
        if len(current) != 1:
            return False
        row = current[0]
        key = (row.context, row.action)
        updated = self.habits.get(key, 0.0) + self.habit_learning_rate * event.reward
        self.habits[key] = self._clamp(updated, -1.0, 1.0)
        return True

    def snapshot(self) -> dict:
        state = super().snapshot()
        # Diagnostic views preserve the historical observation contract without
        # creating stored state.
        state["active_concern"] = self.active_concern
        state["concern_strength"] = round(self.concern_strength, 6)
        # These fields no longer exist as stored or derived organism state.
        state.pop("last_action", None)
        state.pop("last_context", None)
        return state

    def persistent_snapshot(self) -> dict:
        """Persistent payload excluding deterministic diagnostic views."""
        state = self.snapshot()
        state.pop("active_concern", None)
        state.pop("concern_strength", None)
        return state

    def persistent_state_bytes(self) -> int:
        return len(json.dumps(self.persistent_snapshot(), sort_keys=True).encode("utf-8"))
