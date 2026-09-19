from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from typing import Any

from .developmental_bridge import build_runtime_input
from .developmental_experiment import condition_config
from .developmental_runtime import DevelopmentalPEMARuntime
from .developmental_world import DEVELOPMENT_TICKS, generate_history
from .integrated_runtime import (
    ConcernActor,
    Effect,
    IntegratedPEMARuntime,
    Operation,
    WorldEvent,
)


PROBE_EPOCHS = 6
PROBE_EPOCH_TICKS = 40
PROBE_TICKS = PROBE_EPOCHS * PROBE_EPOCH_TICKS
PROBE_CYCLE_OFFSET = DEVELOPMENT_TICKS // PROBE_EPOCH_TICKS


class FrozenProbeConcernActor(ConcernActor):
    """Concern actor with mature reserve held fixed during evaluation.

    The inherited proposal rule still reads the mature reserve and therefore keeps
    its causal effect on operation priority. A granted probe recall records the
    recall and emits the same explicit MEMORY effect, but it cannot consume reserve.
    This is the minimum evaluation-only change required by the frozen protocol's
    non-learning probe contract.
    """

    def execute(self, operation: Operation, tick: int, config) -> list[Effect]:
        if operation.kind == "RECALL":
            self.recall_count += 1
            return [Effect(self.actor_id, "MEMORY", "concern_recall", f"UNRESOLVED_{tick}")]
        return []


class MatureProbeRuntime(IntegratedPEMARuntime):
    """A mature PEMA state exposed to the inherited controlled social probe.

    Instances are created only by deep-copying a completed developmental runtime.
    The probe uses fresh event identifiers beyond the developmental cycle range and
    disables evidence acquisition and reserve banking while retaining their mature
    values as causal inputs to operation demand.
    """

    def _world_step(self, tick: int) -> None:
        local_cycle = (tick - 1) // PROBE_EPOCH_TICKS
        cycle = PROBE_CYCLE_OFFSET + local_cycle
        position = (tick - 1) % PROBE_EPOCH_TICKS
        if position == 0:
            self.perception.observe(
                WorldEvent(
                    event_id=f"E{cycle}_PRIVATE",
                    cycle=cycle,
                    channel="private",
                    value="avoid",
                    salience=0.72,
                    born_tick=tick,
                ),
                self.config,
            )
        if position == 5:
            self.perception.observe(
                WorldEvent(
                    event_id=f"E{cycle}_PUBLIC",
                    cycle=cycle,
                    channel="public",
                    value="welcome",
                    salience=0.86,
                    born_tick=tick,
                ),
                self.config,
            )
        if position == 6:
            self.action.start_decision(f"PROBE_D{local_cycle}", cycle, tick)
        self.concern.set_context_match(position == 15)


def _learning_state(runtime: IntegratedPEMARuntime) -> dict[str, float]:
    return {
        "exploration_evidence": float(runtime.exploration.evidence),
        "routine_evidence": float(runtime.routine.evidence),
        "concern_reserve": float(runtime.concern.reserve),
    }


def _allocation_by_epoch(timeline: list[dict[str, Any]]) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    for epoch in range(PROBE_EPOCHS):
        window = timeline[epoch * PROBE_EPOCH_TICKS : (epoch + 1) * PROBE_EPOCH_TICKS]
        counts = {"EXPLORATION": 0, "ROUTINE": 0, "CONCERN": 0}
        for row in window:
            for grant in row["granted"]:
                actor_id = grant["actor_id"]
                if actor_id in counts:
                    counts[actor_id] += 1
        total = sum(counts.values())
        rows.append(
            {
                actor_id: (count / total if total else 0.0)
                for actor_id, count in counts.items()
            }
        )
    return rows


def run_mature_probe(mature: IntegratedPEMARuntime) -> dict[str, Any]:
    """Evaluate a completed developmental runtime without learning.

    The completed runtime is never mutated. A deep copy receives the six frozen
    40-tick probe epochs. Feedback is disabled, reserve conversion is zero, and
    probe recall cannot consume reserve, so mature evidence and reserve remain
    fixed while continuing to affect operation demand.
    """
    probe = deepcopy(mature)
    probe.__class__ = MatureProbeRuntime
    probe.concern.__class__ = FrozenProbeConcernActor
    probe.config = replace(
        probe.config,
        ticks=PROBE_TICKS,
        feedback_enabled=False,
        bank_conversion=0.0,
    )
    before = _learning_state(probe)
    behavior_start = len(probe.action.behaviors)
    result = probe.run(retain_trace=True)
    after = _learning_state(probe)
    if before != after:
        raise RuntimeError("mature probe mutated frozen learning-relevant state")

    behaviors = probe.action.behaviors[behavior_start:]
    if len(behaviors) != PROBE_EPOCHS:
        raise RuntimeError("mature probe did not produce exactly six decisions")
    timeline = result["timeline"]
    if len(timeline) != PROBE_TICKS:
        raise RuntimeError("mature probe did not execute exactly 240 ticks")

    return {
        "decision_signature": [row["choice"] for row in behaviors],
        "behaviors": behaviors,
        "allocation_shares": _allocation_by_epoch(timeline),
        "frozen_learning_state": before,
        "learning_state_after_probe": after,
        "timeline": timeline,
    }


def develop_mature_runtime(seed: int, condition: str) -> IntegratedPEMARuntime:
    """Create one isolated mature runtime under a preregistered condition."""
    config = condition_config(seed, condition)
    if condition == "REPEATED_DIFFERENTIAL":
        runtime: IntegratedPEMARuntime = IntegratedPEMARuntime(config)
    else:
        history = generate_history(seed)
        runtime = DevelopmentalPEMARuntime(build_runtime_input(history, config=config))
    runtime.run(retain_trace=False)
    return runtime


def run_development_and_probe(seed: int, condition: str) -> dict[str, Any]:
    mature = develop_mature_runtime(seed, condition)
    return run_mature_probe(mature)
