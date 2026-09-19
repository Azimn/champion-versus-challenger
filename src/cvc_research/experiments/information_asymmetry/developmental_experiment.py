from __future__ import annotations

from dataclasses import asdict, replace
from typing import Any

from .developmental_bridge import build_runtime_input
from .developmental_runtime import run_developmental
from .developmental_world import (
    DEVELOPMENT_TICKS,
    WORLD_SEEDS,
    generate_history,
    serialize_history,
)
from .integrated_runtime import IntegratedConfig, run_integrated


GENERATED_CONDITIONS = {
    "GENERATIVE_DIFFERENTIAL": {},
    "GENERATIVE_NO_FEEDBACK": {"feedback_enabled": False},
    "GENERATIVE_NO_RESERVE": {"reserve_enabled": False},
    "GENERATIVE_GLOBAL": {"access": "global"},
}
BLOCK_TICKS = 4_000
BLOCK_COUNT = DEVELOPMENT_TICKS // BLOCK_TICKS


def condition_config(seed: int, condition: str) -> IntegratedConfig:
    """Construct one preregistered condition without changing inherited defaults."""
    if seed not in WORLD_SEEDS:
        raise ValueError(f"seed {seed} is not preregistered")
    if condition == "REPEATED_DIFFERENTIAL":
        return IntegratedConfig(ticks=DEVELOPMENT_TICKS, seed=seed)
    if condition not in GENERATED_CONDITIONS:
        raise ValueError(f"unknown developmental condition: {condition}")
    base = IntegratedConfig(ticks=DEVELOPMENT_TICKS, seed=seed)
    return replace(base, **GENERATED_CONDITIONS[condition])


def summarize_blocks(timeline: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Expose six fixed developmental windows so aggregates cannot hide regime changes."""
    if len(timeline) != DEVELOPMENT_TICKS:
        raise ValueError("developmental timeline must contain exactly 24,000 ticks")
    blocks: list[dict[str, Any]] = []
    for block_index in range(BLOCK_COUNT):
        start = block_index * BLOCK_TICKS
        rows = timeline[start : start + BLOCK_TICKS]
        grants = {"EXPLORATION": 0, "ROUTINE": 0, "CONCERN": 0}
        for row in rows:
            for grant in row["granted"]:
                actor_id = grant["actor_id"]
                if actor_id in grants:
                    grants[actor_id] += 1
        channel_total = grants["EXPLORATION"] + grants["ROUTINE"]
        blocks.append(
            {
                "block": block_index + 1,
                "start_tick": start + 1,
                "end_tick": start + BLOCK_TICKS,
                "allocation_counts": grants,
                "exploration_share": grants["EXPLORATION"] / channel_total if channel_total else 0.0,
                "final_exploration_evidence": rows[-1]["exploration_evidence"],
                "final_routine_evidence": rows[-1]["routine_evidence"],
                "final_concern_reserve": rows[-1]["concern_reserve"],
                "final_concern_recalls": rows[-1]["concern_recalls"],
            }
        )
    return blocks


def run_condition(seed: int, condition: str, *, retain_trace: bool = False) -> dict[str, Any]:
    """Run one isolated preregistered developmental condition.

    Generated conditions reuse the byte-identical serialized history for a seed.
    The repeated control uses the inherited static world for exactly the same duration.
    """
    config = condition_config(seed, condition)
    if condition == "REPEATED_DIFFERENTIAL":
        result = run_integrated(config, retain_trace=True)
        history_json = None
    else:
        history = generate_history(seed)
        history_json = serialize_history(history)
        runtime_input = build_runtime_input(history, config=config)
        result = run_developmental(runtime_input, retain_trace=True)

    timeline = result["timeline"]
    result["developmental_blocks"] = summarize_blocks(timeline)
    result["experiment"] = {
        "condition": condition,
        "world_seed": seed,
        "config": asdict(config),
        "serialized_history": history_json,
    }
    if not retain_trace:
        result.pop("timeline", None)
    return result
