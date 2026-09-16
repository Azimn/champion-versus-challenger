from __future__ import annotations

from urllib.parse import quote

from .exp007_challenger import EligibilityTraceCharacter
from .runtime import Event
from .v9_1_compact import V91CompactCharacter


class SearchExperiencePolicyCharacter(V91CompactCharacter):
    """EXP-008 zero-new-field interaction between search belief and experience.

    Search decisions retain the v9.1 subject-owned last-observed-location prior but
    also read the existing habit value for an actor-qualified, subject-accessible
    search-task context. Search action/outcome history is stored in the already
    existing habit table and bounded eligibility trace. No factual location belief
    is revised from reward alone.
    """

    @staticmethod
    def _search_experience_context(event: Event) -> str | None:
        if event.actor is None or event.context is None:
            return None
        # v9.1's canonical habit serialization reserves `|` between context and
        # action. Percent-encode both subject-accessible components so the derived
        # context remains one losslessly reconstructible string without adding state.
        task = quote(str(event.context), safe="")
        actor = quote(str(event.actor), safe="")
        return f"search_task:{task};entity:{actor}"

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
                belief_score = 0.10
            else:
                belief_score = 0.90 if believed == location else 0.05

            experience_context = self._search_experience_context(event)
            learned = (
                self.habits.get((experience_context, action), 0.0)
                if experience_context is not None
                else 0.0
            )
            return belief_score + learned

        return super()._score_action(
            action,
            event,
            immediate_threat,
            task_pressure,
        )

    def _apply_delayed_outcome(self, event: Event) -> bool:
        experience_context = self._search_experience_context(event)
        if experience_context is None or event.reward == 0.0:
            return super()._apply_delayed_outcome(event)

        candidates = self._context_candidates(experience_context)
        actions = {row.action for row in candidates}
        if not actions:
            # This may be an ordinary non-search outcome carrying an actor. Preserve
            # the inherited raw-context rule rather than fabricating search credit.
            return super()._apply_delayed_outcome(event)
        if len(actions) != 1:
            return False

        row = min(candidates, key=lambda item: item.age)
        key = (row.context, row.action)
        updated = self.habits.get(key, 0.0) + (
            self.habit_learning_rate * event.reward * self._eligibility(row)
        )
        self.habits[key] = self._clamp(updated, -1.0, 1.0)
        return True

    def _apply_action_effects(self, action: str, event: Event) -> None:
        experience_context = (
            self._search_experience_context(event)
            if action.startswith("search:")
            else None
        )
        if experience_context is None:
            super()._apply_action_effects(action, event)
            return

        # Run every inherited action effect except EligibilityTraceCharacter's raw
        # context record creation, then create one actor-qualified record instead.
        super(EligibilityTraceCharacter, self)._apply_action_effects(action, event)
        if event.kind != "outcome" and action != "idle":
            self._create_eligibility(experience_context, action)

    def mechanism_count(self) -> int:
        # EXP-008 adds a policy interaction but no independent persistent mechanism.
        return super().mechanism_count()
