from __future__ import annotations

from typing import Dict

from .exp005_challenger import ProspectiveCueCharacter
from .runtime import Event


class SubjectiveFactCharacter(ProspectiveCueCharacter):
    """EXP-006 challenger with one minimal class of subject-owned fact.

    The organism records the last location it actually perceived for an entity.
    Hidden world changes do not alter this state. A later direct observation revises
    it. This is intentionally smaller than a general world model or belief system.
    """

    def __init__(self) -> None:
        super().__init__()
        self.location_beliefs: Dict[str, str] = {}

    def _process_event(self, event: Event) -> tuple[float, float]:
        if event.kind == "observe_location" and event.actor and event.context:
            self.location_beliefs[event.actor] = event.context
            return 0.0, 0.0

        if event.kind == "hidden_world_change":
            # Hidden environment changes are not perceptions and therefore do not
            # alter the subject's belief state.
            return 0.0, 0.0

        return super()._process_event(event)

    def _score_action(
        self,
        action: str,
        event: Event,
        immediate_threat: float,
        task_pressure: float,
    ) -> float:
        if action.startswith("search:") and event.actor:
            location = action.split(":", 1)[1]
            believed = self.location_beliefs.get(event.actor)
            if believed is None:
                return 0.10
            return 0.90 if believed == location else 0.05

        return super()._score_action(
            action,
            event,
            immediate_threat,
            task_pressure,
        )

    def snapshot(self) -> dict:
        state = super().snapshot()
        state["location_beliefs"] = dict(sorted(self.location_beliefs.items()))
        return state

    def mechanism_count(self) -> int:
        return super().mechanism_count() + 1
