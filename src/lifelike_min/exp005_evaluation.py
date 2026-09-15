from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import median
from time import perf_counter_ns
from typing import Callable

from .exp003_evaluation import probe_unknown_order, regression_suite
from .exp004_challenger import ConcernLedgerCharacter
from .exp004_evaluation import probe_multiple_concerns
from .exp005_challenger import ProspectiveCueCharacter
from .runtime import Event, PersistentCharacter


Factory = Callable[[], PersistentCharacter]


def champion_factory() -> PersistentCharacter:
    return ConcernLedgerCharacter()


def challenger_factory() -> PersistentCharacter:
    return ProspectiveCueCharacter()


def _encode_future(agent: PersistentCharacter, concern: str = "call_morgan", cue: str = "morgan_arrives") -> None:
    agent.step(
        Event(
            kind="future_commitment",
            concern=concern,
            context=cue,
            forced_action="idle",
        )
    )


def _long_delay(agent: PersistentCharacter, ticks: int = 90) -> None:
    for _ in range(ticks):
        agent.step(Event(kind="neutral", forced_action="idle"))


def probe_event_cued_commitment(factory: Factory) -> dict:
    agent = factory()
    _encode_future(agent)
    encoded = agent.snapshot()
    _long_delay(agent)
    retained = agent.snapshot()

    agent.step(Event(kind="neutral", context="wrong_context", forced_action="idle"))
    wrong_context = agent.snapshot()

    # Lower current competence immediately before the cue so ordinary need scores
    # cannot accidentally mimic prospective recall.
    agent.step(Event(kind="neutral", forced_action="work"))
    action = agent.step(
        Event(
            kind="neutral",
            context="morgan_arrives",
            available_actions=("work", "rest", "idle"),
        )
    )
    after_cue = agent.snapshot()

    prospective = retained.get("prospective_commitments", {})
    passed = (
        prospective.get("call_morgan") == "morgan_arrives"
        and wrong_context.get("active_concern") is None
        and action == "work"
        and after_cue.get("active_concern") == "call_morgan"
        and "call_morgan" not in after_cue.get("prospective_commitments", {})
    )
    return {
        "passed": passed,
        "encoded": encoded,
        "retained_after_delay": retained,
        "wrong_context": wrong_context,
        "cue_action": action,
        "after_cue": after_cue,
        "trace_tail": agent.trace[-10:],
    }


def reviewer_cancel_before_cue(factory: Factory) -> dict:
    agent = factory()
    _encode_future(agent)
    agent.step(Event(kind="task_cancel", concern="call_morgan", forced_action="idle"))
    agent.step(Event(kind="neutral", context="morgan_arrives", forced_action="idle"))
    state = agent.snapshot()
    return {
        "passed": (
            "call_morgan" not in state.get("prospective_commitments", {})
            and "call_morgan" not in state.get("concern_ledger", {})
            and state.get("active_concern") != "call_morgan"
        ),
        "state": state,
        "trace": agent.trace,
    }


def reviewer_wrong_cues(factory: Factory) -> dict:
    agent = factory()
    _encode_future(agent)
    states = []
    for cue in ("alex_arrives", "meeting_starts", "hallway"):
        agent.step(Event(kind="neutral", context=cue, forced_action="idle"))
        states.append(agent.snapshot())
    final = states[-1]
    return {
        "passed": (
            final.get("active_concern") is None
            and final.get("prospective_commitments", {}).get("call_morgan") == "morgan_arrives"
        ),
        "states": states,
        "trace": agent.trace,
    }


def reviewer_multiple_future_commitments(factory: Factory) -> dict:
    agent = factory()
    _encode_future(agent, "call_morgan", "morgan_arrives")
    _encode_future(agent, "send_report", "meeting_ends")
    agent.step(Event(kind="neutral", context="morgan_arrives", forced_action="idle"))
    after_first = agent.snapshot()
    agent.step(Event(kind="task_cancel", concern="call_morgan", forced_action="idle"))
    agent.step(Event(kind="neutral", context="meeting_ends", forced_action="idle"))
    after_second = agent.snapshot()
    return {
        "passed": (
            "call_morgan" in after_first.get("concern_ledger", {})
            and after_first.get("prospective_commitments", {}).get("send_report") == "meeting_ends"
            and "send_report" in after_second.get("concern_ledger", {})
            and not after_second.get("prospective_commitments", {})
        ),
        "after_first": after_first,
        "after_second": after_second,
        "trace": agent.trace,
    }


def reviewer_one_shot_activation(factory: Factory) -> dict:
    agent = factory()
    _encode_future(agent)
    agent.step(Event(kind="neutral", context="morgan_arrives", forced_action="idle"))
    first = agent.snapshot()
    agent.step(Event(kind="neutral", context="morgan_arrives", forced_action="idle"))
    second = agent.snapshot()
    ledger = second.get("concern_ledger", {})
    return {
        "passed": (
            not first.get("prospective_commitments", {})
            and not second.get("prospective_commitments", {})
            and list(ledger).count("call_morgan") == 1
        ),
        "first": first,
        "second": second,
        "trace": agent.trace,
    }


def reviewer_bounded_store(factory: Factory) -> dict:
    agent = factory()
    for index in range(6):
        _encode_future(agent, f"future_{index}", f"cue_{index}")
    store = agent.snapshot().get("prospective_commitments", {})
    return {
        "passed": 1 <= len(store) <= 3,
        "store": store,
        "trace": agent.trace,
    }


def benchmark(factory: Factory, repeats: int = 7, ticks: int = 4000) -> dict:
    samples = []
    for _ in range(repeats):
        agent = factory()
        start = perf_counter_ns()
        for index in range(ticks):
            if index % 101 == 0:
                agent.step(
                    Event(
                        kind="future_commitment",
                        concern=f"future_{(index // 101) % 3}",
                        context=f"cue_{(index // 101) % 3}",
                        forced_action="idle",
                    )
                )
            elif index % 97 == 0:
                agent.step(
                    Event(
                        kind="neutral",
                        context=f"cue_{(index // 97) % 3}",
                        available_actions=("work", "rest", "idle"),
                    )
                )
            else:
                agent.step(Event(kind="neutral", available_actions=("work", "rest", "idle")))
        samples.append((perf_counter_ns() - start) / ticks / 1000.0)

    representative = factory()
    representative.step(Event(kind="task_assign", concern="finish_report", forced_action="idle"))
    representative.step(
        Event(
            kind="future_commitment",
            concern="call_morgan",
            context="morgan_arrives",
            forced_action="idle",
        )
    )
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
            if key not in {"trace", "traces", "trace_tail"}
        }
    if isinstance(value, list):
        return [_compact(item) for item in value]
    return value


def run_experiment() -> dict:
    champion_target = probe_event_cued_commitment(champion_factory)
    challenger_target = probe_event_cued_commitment(challenger_factory)
    regressions = regression_suite(challenger_factory)
    uncertainty_preserved = probe_unknown_order(challenger_factory)
    multi_concern_preserved = probe_multiple_concerns(challenger_factory)
    reviewers = {
        "cancel_before_cue": reviewer_cancel_before_cue(challenger_factory),
        "wrong_cues_do_not_activate": reviewer_wrong_cues(challenger_factory),
        "multiple_future_commitments": reviewer_multiple_future_commitments(challenger_factory),
        "one_shot_activation": reviewer_one_shot_activation(challenger_factory),
        "bounded_store": reviewer_bounded_store(challenger_factory),
    }
    champion_cost = benchmark(champion_factory)
    challenger_cost = benchmark(challenger_factory)

    target_gain = not champion_target["passed"] and challenger_target["passed"]
    prior_preserved = (
        all(result["passed"] for result in regressions.values())
        and uncertainty_preserved["passed"]
        and multi_concern_preserved["passed"]
    )
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
        "experiment": "EXP-005 event-cued prospective commitment",
        "champion": "v6_bounded_concern_ledger",
        "challenger": "v7_prospective_cue",
        "champion_modified": False,
        "target_failure": "A future commitment cannot remain latent through unrelated activity and later become behaviorally active when its environmental cue occurs.",
        "minimal_hypothesis": "A future commitment does not require a scheduler or planner for this failure. A bounded concern-to-cue binding can remain inert until its cue appears, then convert into the already validated ordinary concern representation.",
        "target_gain": target_gain,
        "champion_target": champion_target,
        "challenger_target": challenger_target,
        "prior_regression_suite": regressions,
        "exp003_uncertainty_behavior_preserved": uncertainty_preserved,
        "exp004_multiple_concern_behavior_preserved": multi_concern_preserved,
        "reviewer_probes": reviewers,
        "prior_behavior_preserved": prior_preserved,
        "reviewers_pass": reviewers_pass,
        "champion_cost": champion_cost,
        "challenger_cost": challenger_cost,
        "mechanism_delta": mechanism_delta,
        "persistent_state_delta_bytes": state_delta,
        "runtime_ratio": round(runtime_ratio, 4),
        "causal_ablation": "The frozen v6 champion receives the identical future-commitment event and later cue but has no cue-binding state, so nothing is retained or activated.",
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
