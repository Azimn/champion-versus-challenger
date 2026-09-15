from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import median
from time import perf_counter_ns
from typing import Callable

from .exp003_evaluation import probe_unknown_order, regression_suite
from .exp004_evaluation import probe_multiple_concerns
from .exp005_challenger import ProspectiveCueCharacter
from .exp005_evaluation import probe_event_cued_commitment
from .exp006_audit import delayed_consequence_credit
from .exp006_challenger import SubjectiveFactCharacter
from .runtime import Event, PersistentCharacter


Factory = Callable[[], PersistentCharacter]


def champion_factory() -> PersistentCharacter:
    return ProspectiveCueCharacter()


def challenger_factory() -> PersistentCharacter:
    return SubjectiveFactCharacter()


def _search_after_history(
    factory: Factory,
    seen_location: str,
    hidden_location: str,
    actions: tuple[str, str],
    actor: str = "book",
) -> tuple[str, PersistentCharacter]:
    agent = factory()
    agent.step(
        Event(
            kind="observe_location",
            actor=actor,
            context=seen_location,
            forced_action="idle",
        )
    )
    agent.step(
        Event(
            kind="hidden_world_change",
            actor=actor,
            context=hidden_location,
            forced_action="idle",
        )
    )
    action = agent.step(
        Event(kind="retrieve", actor=actor, available_actions=actions)
    )
    return action, agent


def probe_epistemic_history(factory: Factory) -> dict:
    observations = {}
    passed = True
    for seen, hidden in (("drawer", "shelf"), ("shelf", "drawer")):
        expected = f"search:{seen}"
        actions = []
        traces = []
        states = []
        for order in (
            ("search:drawer", "search:shelf"),
            ("search:shelf", "search:drawer"),
        ):
            action, agent = _search_after_history(factory, seen, hidden, order)
            actions.append(action)
            traces.append(agent.trace)
            states.append(agent.snapshot())
        row_passed = actions == [expected, expected]
        passed = passed and row_passed
        observations[seen] = {
            "expected": expected,
            "actions": actions,
            "states": states,
            "traces": traces,
        }
    return {"passed": passed, "observations": observations}


def reviewer_observed_revision(factory: Factory) -> dict:
    actions = []
    traces = []
    for order in (
        ("search:drawer", "search:shelf"),
        ("search:shelf", "search:drawer"),
    ):
        agent = factory()
        agent.step(
            Event(kind="observe_location", actor="book", context="drawer", forced_action="idle")
        )
        agent.step(
            Event(kind="observe_location", actor="book", context="shelf", forced_action="idle")
        )
        actions.append(
            agent.step(Event(kind="retrieve", actor="book", available_actions=order))
        )
        traces.append(agent.trace)
    return {
        "passed": actions == ["search:shelf", "search:shelf"],
        "actions": actions,
        "traces": traces,
    }


def reviewer_hidden_change_not_omniscient(factory: Factory) -> dict:
    action, agent = _search_after_history(
        factory,
        "drawer",
        "shelf",
        ("search:shelf", "search:drawer"),
    )
    state = agent.snapshot()
    return {
        "passed": action == "search:drawer" and state.get("location_beliefs", {}).get("book") == "drawer",
        "action": action,
        "state": state,
        "trace": agent.trace,
    }


def reviewer_entity_specificity(factory: Factory) -> dict:
    agent = factory()
    agent.step(
        Event(kind="observe_location", actor="book", context="drawer", forced_action="idle")
    )
    agent.step(
        Event(kind="observe_location", actor="keys", context="shelf", forced_action="idle")
    )
    book_action = agent.step(
        Event(
            kind="retrieve",
            actor="book",
            available_actions=("search:shelf", "search:drawer"),
        )
    )
    keys_action = agent.step(
        Event(
            kind="retrieve",
            actor="keys",
            available_actions=("search:drawer", "search:shelf"),
        )
    )
    return {
        "passed": book_action == "search:drawer" and keys_action == "search:shelf",
        "book_action": book_action,
        "keys_action": keys_action,
        "state": agent.snapshot(),
        "trace": agent.trace,
    }


def reviewer_unobserved_entity_has_no_fabricated_belief(factory: Factory) -> dict:
    agent = factory()
    agent.step(
        Event(kind="hidden_world_change", actor="phone", context="shelf", forced_action="idle")
    )
    state = agent.snapshot()
    return {
        "passed": "phone" not in state.get("location_beliefs", {}),
        "state": state,
        "trace": agent.trace,
    }


def reviewer_perception_order(factory: Factory) -> dict:
    agent = factory()
    agent.step(
        Event(kind="observe_location", actor="book", context="drawer", forced_action="idle")
    )
    agent.step(
        Event(kind="hidden_world_change", actor="book", context="shelf", forced_action="idle")
    )
    before = agent.snapshot().get("location_beliefs", {}).get("book")
    agent.step(
        Event(kind="observe_location", actor="book", context="shelf", forced_action="idle")
    )
    after = agent.snapshot().get("location_beliefs", {}).get("book")
    return {
        "passed": before == "drawer" and after == "shelf",
        "before_reobservation": before,
        "after_reobservation": after,
        "trace": agent.trace,
    }


def benchmark(factory: Factory, repeats: int = 7, ticks: int = 4000) -> dict:
    samples = []
    for _ in range(repeats):
        agent = factory()
        start = perf_counter_ns()
        for index in range(ticks):
            actor = "book" if index % 2 == 0 else "keys"
            if index % 37 == 0:
                location = "drawer" if (index // 37) % 2 == 0 else "shelf"
                agent.step(
                    Event(
                        kind="observe_location",
                        actor=actor,
                        context=location,
                        forced_action="idle",
                    )
                )
            elif index % 41 == 0:
                location = "shelf" if (index // 41) % 2 == 0 else "drawer"
                agent.step(
                    Event(
                        kind="hidden_world_change",
                        actor=actor,
                        context=location,
                        forced_action="idle",
                    )
                )
            else:
                agent.step(
                    Event(
                        kind="retrieve",
                        actor=actor,
                        available_actions=("search:drawer", "search:shelf"),
                    )
                )
        samples.append((perf_counter_ns() - start) / ticks / 1000.0)

    representative = factory()
    representative.step(
        Event(kind="observe_location", actor="book", context="drawer", forced_action="idle")
    )
    representative.step(
        Event(kind="task_assign", concern="finish_report", forced_action="idle")
    )
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


def scope_delayed_credit(factory: Factory) -> dict:
    # Delayed consequence credit is the next reproduced failure. The epistemic
    # challenger should not silently solve it.
    agent = factory()
    agent.step(Event(kind="context", context="morning", available_actions=("walk",)))
    for _ in range(3):
        agent.step(Event(kind="neutral", forced_action="idle"))
    agent.step(Event(kind="outcome", reward=1.0, forced_action="idle"))
    choice = agent.step(
        Event(kind="context", context="morning", available_actions=("tea", "walk"))
    )
    return {
        "delayed_credit_solved": choice == "walk",
        "choice": choice,
        "habits": agent.snapshot().get("habits", {}),
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
    champion_target = probe_epistemic_history(champion_factory)
    challenger_target = probe_epistemic_history(challenger_factory)
    regressions = regression_suite(challenger_factory)
    uncertainty_preserved = probe_unknown_order(challenger_factory)
    multiple_concerns_preserved = probe_multiple_concerns(challenger_factory)
    prospective_preserved = probe_event_cued_commitment(challenger_factory)
    reviewers = {
        "observed_revision": reviewer_observed_revision(challenger_factory),
        "hidden_change_not_omniscient": reviewer_hidden_change_not_omniscient(challenger_factory),
        "entity_specificity": reviewer_entity_specificity(challenger_factory),
        "unobserved_entity_has_no_belief": reviewer_unobserved_entity_has_no_fabricated_belief(challenger_factory),
        "reobservation_updates_stale_belief": reviewer_perception_order(challenger_factory),
    }
    scope_control = scope_delayed_credit(challenger_factory)
    champion_cost = benchmark(champion_factory)
    challenger_cost = benchmark(challenger_factory)

    target_gain = not champion_target["passed"] and challenger_target["passed"]
    prior_preserved = (
        all(result["passed"] for result in regressions.values())
        and uncertainty_preserved["passed"]
        and multiple_concerns_preserved["passed"]
        and prospective_preserved["passed"]
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
        and not scope_control["delayed_credit_solved"]
        and mechanism_delta == 1
        and runtime_ratio <= 1.30
    )

    return {
        "experiment": "EXP-006 subject-owned perceived fact",
        "champion": "v7_prospective_cue",
        "challenger": "v8_subjective_fact",
        "champion_modified": False,
        "target_failure": "Different perceived world histories collapse to the same retrieval behavior because the organism stores no subject-owned belief about an observed location.",
        "minimal_hypothesis": "The failure does not require a world model. One bounded class of subject-owned fact, the last directly perceived location per entity, should preserve history divergence and false-belief behavior under hidden changes.",
        "target_gain": target_gain,
        "champion_target": champion_target,
        "challenger_target": challenger_target,
        "prior_regression_suite": regressions,
        "exp003_uncertainty_behavior_preserved": uncertainty_preserved,
        "exp004_multiple_concern_behavior_preserved": multiple_concerns_preserved,
        "exp005_prospective_behavior_preserved": prospective_preserved,
        "reviewer_probes": reviewers,
        "scope_control_delayed_credit": scope_control,
        "prior_behavior_preserved": prior_preserved,
        "reviewers_pass": reviewers_pass,
        "champion_cost": champion_cost,
        "challenger_cost": challenger_cost,
        "mechanism_delta": mechanism_delta,
        "persistent_state_delta_bytes": state_delta,
        "runtime_ratio": round(runtime_ratio, 4),
        "causal_ablation": "The frozen v7 champion receives the same perceived observation and hidden world change but has no subject-owned location state, so search behavior follows action ordering rather than lived history.",
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
