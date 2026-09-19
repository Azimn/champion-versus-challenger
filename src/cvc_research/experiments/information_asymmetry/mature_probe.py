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
    """Concern actor with mature reserve held fixed during evaluation."""

    def propose(self, tick: int, config) -> list[Operation]:
        if not self.context_match:
            return []
        return super().propose(tick, config)

    def execute(self, operation: Operation, tick: int, config) -> list[Effect]:
        if operation.kind == "RECALL":
            self.recall_count += 1
            return [Effect(self.actor_id, "MEMORY", "concern_recall", f"UNRESOLVED_{tick}")]
        return []


class MatureProbeRuntime(IntegratedPEMARuntime):
    """A mature PEMA state exposed to the inherited controlled social probe."""

    def _world_step(self, tick: int) -> None:
        local_cycle = (tick - 1) // PROBE_EPOCH_TICKS
        cycle = PROBE_CYCLE_OFFSET + local_cycle
        position = (tick - 1) % PROBE_EPOCH_TICKS
        if position == 0:
            self.perception.observe(WorldEvent(event_id=f"E{cycle}_PRIVATE", cycle=cycle, channel="private", value="avoid", salience=0.72, born_tick=tick), self.config)
        if position == 5:
            self.perception.observe(WorldEvent(event_id=f"E{cycle}_PUBLIC", cycle=cycle, channel="public", value="welcome", salience=0.86, born_tick=tick), self.config)
        if position == 6:
            self.action.start_decision(f"PROBE_D{local_cycle}", cycle, tick)
        self.concern.set_context_match(position == 15)


def _learning_state(runtime: IntegratedPEMARuntime) -> dict[str, float]:
    return {"exploration_evidence": float(runtime.exploration.evidence), "routine_evidence": float(runtime.routine.evidence), "concern_reserve": float(runtime.concern.reserve)}


def _resource_accounting_state(runtime: IntegratedPEMARuntime) -> dict[str, float]:
    return {"processing_spent": float(runtime.processing_spent), "conversion_loss": float(runtime.conversion_loss), "expired_unused": float(runtime.expired_unused), "reserve": float(runtime.concern.reserve), "reserve_consumed": float(runtime.concern.reserve_consumed)}


def _probe_resource_conservation(before: dict[str, float], after: dict[str, float], *, capacity_per_tick: int) -> dict[str, float]:
    supplied = float(PROBE_TICKS * capacity_per_tick)
    processing = after["processing_spent"] - before["processing_spent"]
    conversion_loss = after["conversion_loss"] - before["conversion_loss"]
    expired_unused = after["expired_unused"] - before["expired_unused"]
    reserve_consumed = after["reserve_consumed"] - before["reserve_consumed"]
    initial_reserve = before["reserve"]
    final_reserve = after["reserve"]
    error = (supplied + initial_reserve) - (processing + conversion_loss + expired_unused + reserve_consumed + final_reserve)
    return {"supplied": supplied, "initial_reserve": initial_reserve, "processing_spent": processing, "conversion_loss": conversion_loss, "expired_unused": expired_unused, "reserve_consumed": reserve_consumed, "final_reserve": final_reserve, "error": error}


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
        rows.append({actor_id: (count / total if total else 0.0) for actor_id, count in counts.items()})
    return rows


def run_mature_probe(mature: IntegratedPEMARuntime) -> dict[str, Any]:
    """Evaluate a completed developmental runtime without learning or mutating it."""
    probe = deepcopy(mature)
    probe.__class__ = MatureProbeRuntime
    probe.concern.__class__ = FrozenProbeConcernActor
    probe.config = replace(probe.config, ticks=PROBE_TICKS, feedback_enabled=False, bank_conversion=0.0)
    # Development may retain a 24,000-tick trace on the mature runtime. The
    # probe runs on a deepcopy, so reset only this observational buffer before
    # evaluation. This keeps the probe artifact scoped to its own 240 ticks
    # without changing any cognitive, learned, or resource-accounting state.
    probe.tick_records = []
    before = _learning_state(probe)
    resource_before = _resource_accounting_state(probe)
    behavior_start = len(probe.action.behaviors)
    result = probe.run(retain_trace=True)
    after = _learning_state(probe)
    resource_after = _resource_accounting_state(probe)
    conservation = _probe_resource_conservation(resource_before, resource_after, capacity_per_tick=probe.config.capacity_per_tick)
    if before != after:
        raise RuntimeError("mature probe mutated frozen learning-relevant state")
    if abs(conservation["error"]) > 1e-9:
        raise RuntimeError("mature probe violated probe-local resource conservation")
    behaviors = probe.action.behaviors[behavior_start:]
    if len(behaviors) != PROBE_EPOCHS:
        raise RuntimeError("mature probe did not produce exactly six decisions")
    timeline = result["timeline"]
    if len(timeline) != PROBE_TICKS:
        raise RuntimeError("mature probe did not execute exactly 240 ticks")
    return {"decision_signature": [row["choice"] for row in behaviors], "behaviors": behaviors, "allocation_shares": _allocation_by_epoch(timeline), "frozen_learning_state": before, "learning_state_after_probe": after, "probe_resource_conservation": conservation, "timeline": timeline}


def develop_mature_runtime_with_result(seed: int, condition: str, *, retain_trace: bool = False) -> tuple[IntegratedPEMARuntime, dict[str, Any]]:
    """Execute exactly one isolated developmental lifetime and return that runtime and result."""
    config = condition_config(seed, condition)
    if condition == "REPEATED_DIFFERENTIAL":
        runtime: IntegratedPEMARuntime = IntegratedPEMARuntime(config)
    else:
        history = generate_history(seed)
        runtime = DevelopmentalPEMARuntime(build_runtime_input(history, config=config))
    result = runtime.run(retain_trace=retain_trace)
    return runtime, result


def develop_mature_runtime(seed: int, condition: str) -> IntegratedPEMARuntime:
    runtime, _ = develop_mature_runtime_with_result(seed, condition, retain_trace=False)
    return runtime


def run_development_and_probe(seed: int, condition: str) -> dict[str, Any]:
    mature = develop_mature_runtime(seed, condition)
    return run_mature_probe(mature)
