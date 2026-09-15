from __future__ import annotations

from .runtime import Event, PersistentCharacter, Version


class UncertaintyPolicyCharacter(PersistentCharacter):
    """EXP-003 challenger that generalizes the existing partner model.

    The frozen v5 model stores one signed reliability estimate per partner, but an
    unseen or near-neutral partner makes delegate and verify tie. The inherited
    tie-breaker then lets action ordering decide the behavior.

    This challenger adds no persistent state and no new cognitive subsystem. It
    only gives verification a small premium while reliability evidence is weak.
    """

    uncertainty_threshold = 0.15
    uncertainty_verify_bonus = 0.08

    def __init__(self) -> None:
        super().__init__(Version.PARTNER_MODEL)

    def _score_action(
        self,
        action: str,
        event: Event,
        immediate_threat: float,
        task_pressure: float,
    ) -> float:
        if action.startswith("verify:"):
            actor = action.split(":", 1)[1]
            reliability = self._reliability(actor)
            score = 0.10 + 0.80 * max(-reliability, 0.0)
            if abs(reliability) < self.uncertainty_threshold:
                score += self.uncertainty_verify_bonus
            return score

        if action.startswith("delegate:"):
            actor = action.split(":", 1)[1]
            reliability = self._reliability(actor)
            return 0.10 + 0.80 * max(reliability, 0.0)

        return super()._score_action(
            action,
            event,
            immediate_threat,
            task_pressure,
        )
