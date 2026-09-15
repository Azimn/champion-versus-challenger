from __future__ import annotations

from typing import Dict

from .exp004_challenger import ConcernLedgerCharacter
from .runtime import Event


class ProspectiveCueCharacter(ConcernLedgerCharacter):
    """EXP-005 challenger with a minimal event-cued prospective intention store.

    Future commitments remain latent as concern-to-cue bindings. They do not add
    action pressure while the cue is absent. When the matching context appears,
    the commitment becomes an ordinary concern and reuses the existing concern
    machinery.
    """

    max_prospective = 3

    def __init__(self) -> None:
        super().__init__()
        self.prospective_commitments: Dict[str, str] = {}

    def _bound_prospective(self) -> None:
        while len(self.prospective_commitments) > self.max_prospective:
            oldest = next(iter(self.prospective_commitments))
            del self.prospective_commitments[oldest]

    def _activate_cue(self, context: str | None) -> None:
        if not context:
            return
        matched = [
            concern
            for concern, cue in self.prospective_commitments.items()
            if cue == context
        ]
        for concern in matched:
            self.concerns[concern] = max(self.concerns.get(concern, 0.0), 0.75)
            del self.prospective_commitments[concern]
        if matched:
            self._bound_concerns()
            self._sync_active_concern()

    def _process_event(self, event: Event) -> tuple[float, float]:
        if event.kind == "future_commitment":
            concern = event.concern or "future_task"
            cue = event.context or ""
            if cue:
                self.prospective_commitments[concern] = cue
                self._bound_prospective()
            return 0.0, 0.0

        if event.kind == "task_cancel":
            if event.concern is None:
                self.prospective_commitments.clear()
            else:
                self.prospective_commitments.pop(event.concern, None)

        self._activate_cue(event.context)
        return super()._process_event(event)

    def snapshot(self) -> dict:
        state = super().snapshot()
        state["prospective_commitments"] = dict(self.prospective_commitments)
        return state

    def mechanism_count(self) -> int:
        return super().mechanism_count() + 1
