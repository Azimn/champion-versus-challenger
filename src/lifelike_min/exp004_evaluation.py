from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import median
from time import perf_counter_ns
from typing import Callable

from .exp003_challenger import UncertaintyPolicyCharacter
from .exp003_evaluation import probe_unknown_order, regression_suite
from .exp004_challenger import ConcernLedgerCharacter
from .runtime import Event, PersistentCharacter


Factory = Callable[[], PersistentCharacter]


def champion_factory() -> PersistentCharacter:
    return UncertaintyPolicyCharacter()


def challenger_factory() -> PersistentCharacter:
    return ConcernLedgerCharacter()


def probe_multiple_concerns(factory: Factory) -> dict:
    agent = factory()
    agent.step(Event(kind="task_assign", concern="finish_report", forced_action="idle"))
    agent.step(Event(kind="task_assign", concern="call_morgan", forced_action="idle"))
    before_cancel = agent.snapshot()
    agent.step(Event(kind="task_cancel", concern="call_morgan", forced_action="idle"))
    action = agent.step(
        Event(kind="neutral", available_actions=("work", "rest", "idle"))
    )
    after = agent.snapshot()
    survived = after.get("active_concern") == "finish_report"
    if "concern_ledger" in after:
        survived = survived and "finish_report" in after["concern_ledger"]
    return {
        "passed": survived and action == "work",
        "before_cancel": before_cancel,
        "after": after,
        "action": action,
        "trace": agent.trace,
    }


def reviewer_reverse_order(factory: Factory) -> dict:
    agent = factory()
    agent.step(Event(kind="task_assign", concern="call_morgan", forced_action="idle"))
    agent.step(Event(kind="task_assign", concern="finish_report", forced_action="idle"))
    agent.step(Event(kind="task_cancel", concern="finish_report", forced_action="idle"))
    action = agent.step(
        Event(kind="neutral", available_actions=("work", "rest", "idle"))
    )
    state = agent.snapshot()
    return {
        "passed": state.get("active_concern") == "call_morgan" and action == "work",
        "state": state,
        "action": action,
        "trace": agent.trace,
    }


def reviewer_unrelated_cancel(factory: Factory) -> dict:
    agent = factory()
    agent.step(Event(kind="task_assign", concern="finish_report", forced_action="idle"))
    agent.step(Event(kind="task_assign", concern="call_morgan", forced_action="idle"))
    before = agent.snapshot()
    agent.step(Event(kind="task_cancel", concern="buy_milk", forced_action="idle"))
    after = agent.snapshot()
    before_ledger = before.get("concern_ledger")
    after_ledger = after.get("concern_ledger")
    return {
        "passed": before_ledger is not None and set(after_ledger) == set(before_ledger),
        "before": before,
        "after": after,
        "trace": agent.trace,
    }


def reviewer_duplicate_assignment(factory: Factory) -> dict:
    agent = factory()
    agent.step(Event(kind="task_assign", concern="finish_report", forced_action="idle"))
    agent.step(Event(kind="task_assign", concern="finish_report", forced_action="idle"))
    state = agent.snapshot()
    ledger = state.get("concern_ledger", {})
    return {
        "passed": list(ledger) == ["finish_report"] and len(ledger) == 1,
        "state": state,
        "trace": agent.trace,
    }


def reviewer_bounded_capacity(factory: Factory) -> dict:
    agent = factory()
    for concern in ("a", "b", "c", "d", "e"):
        agent.step(Event(kind="task_assign", concern=concern, forced_action="idle"))
    state = agent.snapshot()
    ledger = state.get("concern_ledger", {})
    return {
        "passed": 1 <= len(ledger) <= 3 and state.get("active_concern") in ledger,
        "ledger": ledger,
        "active": state.get("active_concern"),
        "trace": agent.trace,
    }


def reviewer_interruption(factory: Factory) -> dict:
    agent = factory()
    agent.step(Event(kind="task_assign", concern="finish_report", forced_action="idle"))
    agent.step(Event(kind="task_assign", concern="call_morgan", forced_action="idle"))
    agent.step(
        Event(kind="shock", intensity=1.0, available_actions=("avoid", "work", "idle"))
    )
    state = agent.snapshot()
    ledger = state.get("concern_ledger", {})
    return {
        "passed": set(ledger) == {"finish_report", "call_morgan"},
        "ledger": ledger,
        "trace": agent.trace,
    }


def scope_control_long_delay(factory: Factory) -> dict:
    agent = factory()
    agent.step(Event(kind="task_assign", concern="call_morgan", forced_action="idle"))
    for _ in range(90):
        agent.step(Event(kind="neutral", forced_action="idle"))
    state = agent.snapshot()
    return {
        "long_delay_commitment_survives": state.get("active_concern") == "call_morgan",
        "state": state,
    }


def benchmark(factory: Factory, repeats: int = 7, ticks: int = 4000) -> dict:
    samples = []
    for _ in range(repeats):
        agent = factory()
        start = perf_counter_ns()
        for index in range(ticks):
            if index % 41 == 0:
                agent.step(
                    Event(
                        kind="task_assign",
                        concern=f"task_{(index // 41) % 4}",
                        forced_action="idle",
                    )
                )
            elif index % 53 == 0:
                agent.step(
                    Event(
                        kind="task_cancel",
                        concern=f"task_{(index // 53) % 4}",
                        forced_action="idle",
                    )
                )
            else:
                agent.step(
                    Event(kind="neutral", available_actions=("work", "rest", "idle"))
                )
        samples.append((perf_counter_ns() - start) / ticks / 1000.0)

    representative = factory()
    representative.step(Event(kind="task_assign", concern="finish_report", forced_action="idle"))
    representative.step(Event(kind="task_assign", concern="call_morgan", forced_action="idle"))
    representative.step(Event(kind="support", actor="Alex", forced_action="idle"))
    representative.step(Event(kind="observed_reliable", actor="Alex", forced_action="idle"))
    return {
        "median_microseconds_per_tick": round(median(samples), 4),
        "persistent_state_bytes": representative.persistent_state_bytes(),
        "mechanism_count": representative.mechanism_count(),
    }


def _compact(value):
    if isinstance(value, dict):
        return {
            key: _compact(item)
            for key, item in value.items()
            if key not in {"trace", "traces"}
        }
    if isinstance(value, list):
        return [_compact(item) for item in value]
    return value


def run_experiment() -> dict:
    champion_target = probe_multiple_concerns(champion_factory)
    challenger_target = probe_multiple_concerns(challenger_factory)
    regressions = regression_suite(challenger_factory)
    uncertainty_preserved = probe_unknown_order(challenger_factory)
    reviewers = {
        "reverse_assignment_order": reviewer_reverse_order(challenger_factory),
        "unrelated_cancellation": reviewer_unrelated_cancel(challenger_factory),
        "duplicate_assignment": reviewer_duplicate_assignment(challenger_factory),
        "bounded_capacity": reviewer_bounded_capacity(challenger_factory),
        "interruption_preserves_all_concerns": reviewer_interruption(challenger_factory),
    }
    scope_control = scope_control_long_delay(challenger_factory)
    champion_cost = benchmark(champion_factory)
    challenger_cost = benchmark(challenger_factory)

    target_gain = not champion_target["passed"] and challenger_target["passed"]
    prior_preserved = all(result["passed"] for result in regressions.values()) and uncertainty_preserved["passed"]
    reviewers_pass = all(result["passed"] for result in reviewers.values())
    mechanism_delta = challenger_cost["mechanism_count"] - champion_cost["mechanism_count"]
    state_delta = challenger_cost["persistent_state_bytes"] - champion_cost["persistent_state_bytes"]
    runtime_ratio = challenger_cost["median_microseconds_per_tick"] / max(
        champion_cost["median_microseconds_per_tick"], 0.0001
    )
    promoted = (
        target_gain
        and prior_preserved
        and reviewers_pass
        and regressions["surface_invariance"]["passed"]
        and mechanism_delta == 1
        and runtime_ratio <= 1.30
    )

    return {
        "experiment": "EXP-004 bounded concern ledger",
        "champion": "v5_1_uncertainty_policy",
        "challenger": "v6_bounded_concern_ledger",
        "champion_modified": False,
        "target_failure": "A newer unfinished concern overwrites an older unfinished concern, so resolving the newer one erases part of the character's ongoing life.",
        "minimal_hypothesis": "The existing concern mechanism is behaviorally useful but its single storage slot is insufficient. A bounded mapping of concern identifiers to the same existing strength scalar should preserve concurrent unfinished concerns without adding planning or a general motive architecture.",
        "target_gain": target_gain,
        "champion_target": champion_target,
        "challenger_target": challenger_target,
        "prior_regression_suite": regressions,
        "exp003_uncertainty_behavior_preserved": uncertainty_preserved,
        "reviewer_probes": reviewers,
        "scope_control": scope_control,
        "prior_behavior_preserved": prior_preserved,
        "reviewers_pass": reviewers_pass,
        "champion_cost": champion_cost,
        "challenger_cost": challenger_cost,
        "mechanism_delta": mechanism_delta,
        "persistent_state_delta_bytes": state_delta,
        "runtime_ratio": round(runtime_ratio, 4),
        "causal_ablation": "The frozen v5.1 champion retains the original one-slot concern representation and loses finish_report after call_morgan is assigned and then cancelled.",
        "decision": "PROMOTE" if promoted else "REJECT",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    parser.add_argument("--compact-json", type=Path)
    args = parser.parse_args()
    report = run_experiment()
    print(json.dumps(_compact(report), indent=2, sort_keys=True))
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.compact_json:
        args.compact_json.parent.mkdir(parents=True, exist_ok=True)
        args.compact_json.write_text(
            json.dumps(_compact(report), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
