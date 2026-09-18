from __future__ import annotations

import json

from .exp012_challenger import HabitTemporalPlasticityCharacter
from .runtime import Event


class AdaptiveMobilizationThresholdCharacter(HabitTemporalPlasticityCharacter):
    """EXP-013 single-hypothesis dynamical arbitration challenger.

    Adds one persistent global scalar representing current mobilization resistance.
    It contains no previous-action identity and no RNG state.
    """

    experimental_version = "exp013_adaptive_mobilization_threshold_candidate"

    mobilization_baseline = 0.10
    mobilization_relaxation = 0.98
    mobilization_pulse = 0.08

    def __init__(self) -> None:
        super().__init__()
        self.action_mobilization_threshold = self.mobilization_baseline

    def _drift(self) -> None:
        super()._drift()
        b = self.mobilization_baseline
        self.action_mobilization_threshold = self._clamp(
            b + (self.action_mobilization_threshold - b) * self.mobilization_relaxation,
            b,
            1.0,
        )

    def _score_action(
        self,
        action: str,
        event: Event,
        immediate_threat: float,
        task_pressure: float,
    ) -> float:
        if action == "idle":
            return self.action_mobilization_threshold
        return super()._score_action(action, event, immediate_threat, task_pressure)

    def _apply_action_effects(self, action: str, event: Event) -> None:
        super()._apply_action_effects(action, event)
        if action != "idle":
            self.action_mobilization_threshold = self._clamp(
                self.action_mobilization_threshold + self.mobilization_pulse,
                self.mobilization_baseline,
                1.0,
            )

    def mechanism_count(self) -> int:
        return super().mechanism_count() + 1

    def snapshot(self) -> dict:
        state = super().snapshot()
        state["action_mobilization_threshold"] = round(
            self.action_mobilization_threshold, 6
        )
        return state

    def persistent_snapshot(self) -> dict:
        state = super().persistent_snapshot()
        state["action_mobilization_threshold"] = self.action_mobilization_threshold
        return state

    @classmethod
    def from_persistent_snapshot(cls, data: dict) -> "AdaptiveMobilizationThresholdCharacter":
        agent = super().from_persistent_snapshot(data)
        agent.action_mobilization_threshold = float(
            data.get("action_mobilization_threshold", cls.mobilization_baseline)
        )
        return agent

    @classmethod
    def from_persistent_json(cls, encoded: str) -> "AdaptiveMobilizationThresholdCharacter":
        return cls.from_persistent_snapshot(json.loads(encoded))


class NoAdaptiveMobilizationCharacter(AdaptiveMobilizationThresholdCharacter):
    """Causal ablation retaining the EXP-013 class but disabling threshold dynamics."""

    mobilization_relaxation = 1.0
    mobilization_pulse = 0.0
