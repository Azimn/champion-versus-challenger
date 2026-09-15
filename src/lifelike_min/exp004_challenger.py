from __future__ import annotations

from typing import Dict

from .exp003_challenger import UncertaintyPolicyCharacter
from .runtime import Event


class ConcernLedgerCharacter(UncertaintyPolicyCharacter):
    """EXP-004 challenger with the smallest bounded multi-concern state.

    The EXP-003 champion can persist one concern, so a later concern overwrites an
    earlier unfinished one. This challenger stores at most three concern strengths.
    The inherited active_concern and concern_strength fields remain a compatibility
    view of the currently strongest ledger entry.
    """

    max_concerns = 3

    def __init__(self) -> None:
        super().__init__()
        self.concerns: Dict[str, float] = {}

    def _sync_active_concern(self) -> None:
        if not self.concerns:
            self.active_concern = None
            self.concern_strength = 0.0
            return
        concern, strength = max(self.concerns.items(), key=lambda item: item[1])
        self.active_concern = concern
        self.concern_strength = strength

    def _bound_concerns(self) -> None:
        if len(self.concerns) <= self.max_concerns:
            return
        ranked = sorted(
            self.concerns.items(),
            key=lambda item: item[1],
            reverse=True,
        )
        self.concerns = dict(ranked[: self.max_concerns])

    def _drift(self) -> None:
        super()._drift()
        for concern, strength in list(self.concerns.items()):
            strength *= 0.97
            if strength < 0.08:
                del self.concerns[concern]
            else:
                self.concerns[concern] = strength
        self._sync_active_concern()

    def _process_event(self, event: Event) -> tuple[float, float]:
        if event.kind == "task_assign":
            concern = event.concern or "task"
            strength = self._clamp(0.75 * event.intensity)
            self.concerns[concern] = max(self.concerns.get(concern, 0.0), strength)
            self._bound_concerns()
            self._sync_active_concern()
            return 0.0, self._clamp(0.80 * event.intensity)

        if event.kind == "task_cancel":
            if event.concern is None:
                self.concerns.clear()
            else:
                self.concerns.pop(event.concern, None)
            self._sync_active_concern()
            return 0.0, 0.0

        return super()._process_event(event)

    def _apply_action_effects(self, action: str, event: Event) -> None:
        current = self.active_concern
        super()._apply_action_effects(action, event)
        if action == "work" and current is not None and current in self.concerns:
            strength = self._clamp(self.concerns[current] - 0.30)
            if strength < 0.20:
                del self.concerns[current]
            else:
                self.concerns[current] = strength
            self._sync_active_concern()

    def snapshot(self) -> dict:
        state = super().snapshot()
        state["concern_ledger"] = {
            concern: round(strength, 6)
            for concern, strength in self.concerns.items()
        }
        return state

    def mechanism_count(self) -> int:
        return super().mechanism_count() + 1
