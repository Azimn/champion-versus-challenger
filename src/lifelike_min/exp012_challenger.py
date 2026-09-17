from __future__ import annotations

from .exp011_challenger import CapacityThreeProspectiveCharacter
from .runtime import Event


class HabitTemporalPlasticityCharacter(CapacityThreeProspectiveCharacter):
    """EXP-012 zero-new-state habit temporal-plasticity challenger.

    Existing habit keys remain identity/context/action records. The existing signed
    scalar becomes current learned support and is attenuated multiplicatively toward
    neutral once for each subject-experienced event that does not itself supply a
    nonzero learned-value update to that habit.

    No timestamp, age, use count, confidence value, extinction record, second scalar,
    new store, or counted mechanism is added.
    """

    experimental_version = "exp012_habit_temporal_plasticity_candidate"
    habit_nonuse_retention = 0.9995

    def _outcome_refreshed_habit_keys(self, event: Event) -> set[tuple[str, str]]:
        """Identify habits that existing outcome semantics will update this event."""
        if event.kind != "outcome" or event.reward == 0.0:
            return set()

        if event.context is not None:
            candidates = [
                row for row in self.eligibility_records
                if row.context == event.context
            ]
            actions = {row.action for row in candidates}
            if len(actions) != 1:
                return set()
            row = min(candidates, key=lambda item: item.age)
            return {(row.context, row.action)}

        current = [row for row in self.eligibility_records if row.age == 0]
        if len(current) != 1:
            return set()
        row = current[0]
        return {(row.context, row.action)}

    def _attenuate_nonrefreshed_habits(
        self,
        preexisting_keys: set[tuple[str, str]],
        refreshed: set[tuple[str, str]],
    ) -> None:
        r = self.habit_nonuse_retention
        if r >= 1.0:
            return
        for key in preexisting_keys:
            if key in refreshed or key not in self.habits:
                continue
            value = self.habits[key]
            # Multiplication by a positive factor preserves sign and approaches
            # neutral asymptotically. Keys are intentionally retained.
            self.habits[key] = value * r

    def _process_event(self, event: Event) -> tuple[float, float]:
        preexisting = set(self.habits)
        refreshed = self._outcome_refreshed_habit_keys(event)

        # Preserve the complete inherited event semantics first, including immediate
        # and delayed credit. A habit receiving nonzero learned evidence is then
        # exempt from attenuation on this same event.
        result = super()._process_event(event)
        self._attenuate_nonrefreshed_habits(preexisting, refreshed)
        return result


class NoAttenuationHabitTemporalPlasticityCharacter(HabitTemporalPlasticityCharacter):
    """Causal ablation retaining EXP-012 code path but disabling attenuation."""
    habit_nonuse_retention = 1.0
