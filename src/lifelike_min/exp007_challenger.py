from __future__ import annotations

from dataclasses import dataclass

from .exp006_challenger import SubjectiveFactCharacter
from .runtime import Event


@dataclass
class EligibilityRecord:
    """One bounded temporary context-action eligibility record."""

    context: str
    action: str
    age: int


class EligibilityTraceCharacter(SubjectiveFactCharacter):
    """EXP-007 challenger for context-cued delayed consequence credit.

    This is intentionally not a general reinforcement-learning system. The only new
    persistent mechanism is a tiny finite set of recent context-action records. A
    later experienced outcome may update a prior action only when its experienced
    context uniquely identifies a live eligible action.

    Eligibility strength is derived from age rather than stored independently. This
    removes redundant persistent state while preserving deterministic decay.
    """

    max_eligibility_records = 4
    max_eligibility_age = 10
    eligibility_decay = 0.82
    habit_learning_rate = 0.35

    def __init__(self) -> None:
        super().__init__()
        self.eligibility_records: list[EligibilityRecord] = []
        # Transient only. If a record was live at the start of the current event but
        # crossed its expiry boundary during this event's drift, the arriving event
        # may still resolve it. The list is cleared on every subsequent drift and is
        # never serialized.
        self._expired_this_tick: list[EligibilityRecord] = []

    def _eligibility(self, row: EligibilityRecord) -> float:
        return self.eligibility_decay ** row.age

    def _drift(self) -> None:
        self._expired_this_tick = []
        super()._drift()
        survivors: list[EligibilityRecord] = []
        for row in self.eligibility_records:
            row.age += 1
            if row.age <= self.max_eligibility_age:
                survivors.append(row)
            else:
                self._expired_this_tick.append(row)
        self.eligibility_records = survivors

    def _bound_eligibility(self) -> None:
        while len(self.eligibility_records) > self.max_eligibility_records:
            oldest_age = max(row.age for row in self.eligibility_records)
            oldest = [
                index
                for index, row in enumerate(self.eligibility_records)
                if row.age == oldest_age
            ]
            victim = min(
                oldest,
                key=lambda index: (
                    self.eligibility_records[index].context,
                    self.eligibility_records[index].action,
                ),
            )
            del self.eligibility_records[victim]

    def _create_eligibility(self, context: str, action: str) -> None:
        if self.max_eligibility_records <= 0 or not context or not action:
            return
        # Replacing trace: repeating the same context-action pair refreshes the
        # existing record instead of accumulating duplicates.
        for row in self.eligibility_records:
            if row.context == context and row.action == action:
                row.age = 0
                return
        self.eligibility_records.append(
            EligibilityRecord(
                context=context,
                action=action,
                age=0,
            )
        )
        self._bound_eligibility()

    def _context_candidates(self, context: str) -> list[EligibilityRecord]:
        current = [row for row in self.eligibility_records if row.context == context]
        boundary = [row for row in self._expired_this_tick if row.context == context]
        return current + boundary

    def _apply_delayed_outcome(self, event: Event) -> bool:
        if not event.context or event.reward == 0.0:
            return False
        candidates = self._context_candidates(event.context)
        actions = {row.action for row in candidates}
        if len(actions) != 1:
            # The experienced context is either unsupported or causally ambiguous.
            # The organism does not infer a hidden simulator cause.
            return False
        row = min(candidates, key=lambda item: item.age)
        key = (row.context, row.action)
        updated = self.habits.get(key, 0.0) + (
            self.habit_learning_rate * event.reward * self._eligibility(row)
        )
        self.habits[key] = self._clamp(updated, -1.0, 1.0)
        return True

    def _apply_immediate_outcome(self, event: Event) -> bool:
        if event.context is not None or event.reward == 0.0:
            return False
        if self.last_action is None or self.last_context is None:
            return False
        key = (self.last_context, self.last_action)
        updated = self.habits.get(key, 0.0) + self.habit_learning_rate * event.reward
        self.habits[key] = self._clamp(updated, -1.0, 1.0)
        return True

    def _process_event(self, event: Event) -> tuple[float, float]:
        if event.kind == "outcome" and self.has_habit_learning:
            # Intercept the inherited one-step learner so a delayed outcome cannot
            # silently update whichever unrelated action happened most recently.
            if not self._apply_delayed_outcome(event):
                self._apply_immediate_outcome(event)
            return 0.0, 0.0
        return super()._process_event(event)

    def _apply_action_effects(self, action: str, event: Event) -> None:
        super()._apply_action_effects(action, event)
        if (
            event.kind != "outcome"
            and event.context is not None
            and action != "idle"
        ):
            self._create_eligibility(event.context, action)

    def snapshot(self) -> dict:
        state = super().snapshot()
        state["eligibility_records"] = [
            {
                "context": row.context,
                "action": row.action,
                "age": row.age,
            }
            for row in sorted(
                self.eligibility_records,
                key=lambda item: (item.context, item.action),
            )
        ]
        return state

    def mechanism_count(self) -> int:
        return super().mechanism_count() + 1
