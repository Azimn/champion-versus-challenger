from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import median
from time import perf_counter_ns
from typing import Callable

from .exp003_challenger import UncertaintyPolicyCharacter
from .runtime import Event, PersistentCharacter, Version
from .surface import SurfaceRenderer


Factory = Callable[[], PersistentCharacter]


def champion_factory() -> PersistentCharacter:
    return PersistentCharacter(Version.PARTNER_MODEL)


def challenger_factory() -> PersistentCharacter:
    return UncertaintyPolicyCharacter()


def _train_reliability(agent: PersistentCharacter, actor: str, kind: str, count: int) -> None:
    for _ in range(count):
        agent.step(Event(kind=kind, actor=actor, forced_action="idle"))


def probe_unknown_order(factory: Factory) -> dict:
    actions = []
    traces = []
    for available in (
        ("verify:Blake", "delegate:Blake"),
        ("delegate:Blake", "verify:Blake"),
    ):
        agent = factory()
        action = agent.step(
            Event(kind="request_help", actor="Blake", available_actions=available)
        )
        actions.append(action)
        traces.append(agent.trace)
    return {
        "passed": actions == ["verify:Blake", "verify:Blake"],
        "actions": actions,
        "traces": traces,
    }


def probe_history_divergence(factory: Factory) -> dict:
    outcomes = {}
    traces = {}
    for kind in ("support", "hostility"):
        agent = factory()
        for _ in range(3):
            agent.step(Event(kind=kind, actor="Alex", forced_action="idle"))
        action = agent.step(
            Event(
                kind="encounter",
                actor="Alex",
                available_actions=("socialize:Alex", "avoid:Alex", "idle"),
            )
        )
        outcomes[kind] = action
        traces[kind] = agent.trace
    return {
        "passed": outcomes["support"] == "socialize:Alex" and outcomes["hostility"] == "avoid:Alex",
        "actions": outcomes,
        "traces": traces,
    }


def probe_recovery_inertia(factory: Factory) -> dict:
    agent = factory()
    agent.step(Event(kind="shock", intensity=1.0, forced_action="avoid"))
    actions = [
        agent.step(Event(kind="neutral", available_actions=("avoid", "idle")))
        for _ in range(9)
    ]
    return {
        "passed": actions[0] == "avoid" and actions[-1] == "idle",
        "actions": actions,
        "trace": agent.trace,
    }


def probe_unfinished_concern(factory: Factory) -> dict:
    agent = factory()
    assigned = agent.step(
        Event(kind="task_assign", concern="finish_project", available_actions=("work", "idle"))
    )
    interrupted = agent.step(
        Event(kind="shock", intensity=1.0, available_actions=("avoid", "work", "idle"))
    )
    resumed = agent.step(
        Event(kind="neutral", available_actions=("work", "rest", "idle"))
    )
    return {
        "passed": assigned == "work" and interrupted == "avoid" and resumed == "work",
        "actions": [assigned, interrupted, resumed],
        "trace": agent.trace,
    }


def _train_morning_walk(agent: PersistentCharacter) -> None:
    for _ in range(3):
        agent.step(Event(kind="context", context="morning", available_actions=("walk",)))
        agent.step(Event(kind="outcome", reward=1.0, forced_action="idle"))


def probe_habit_formation(factory: Factory) -> dict:
    agent = factory()
    _train_morning_walk(agent)
    action = agent.step(
        Event(kind="context", context="morning", available_actions=("tea", "walk"))
    )
    return {"passed": action == "walk", "action": action, "trace": agent.trace}


def probe_social_prediction(factory: Factory) -> dict:
    observations = {}
    traces = {}
    for label, kind, expected in (
        ("reliable", "observed_reliable", "delegate:Alex"),
        ("unreliable", "observed_unreliable", "verify:Alex"),
    ):
        agent = factory()
        _train_reliability(agent, "Alex", kind, 4)
        choices = []
        for available in (
            ("verify:Alex", "delegate:Alex"),
            ("delegate:Alex", "verify:Alex"),
        ):
            choices.append(
                agent.step(Event(kind="request_help", actor="Alex", available_actions=available))
            )
        observations[label] = choices
        traces[label] = agent.trace
        if choices != [expected, expected]:
            return {
                "passed": False,
                "choices": observations,
                "traces": traces,
            }
    return {"passed": True, "choices": observations, "traces": traces}


def reviewer_reversal(factory: Factory) -> dict:
    agent = factory()
    _train_reliability(agent, "Alex", "observed_reliable", 4)
    before = agent.step(
        Event(
            kind="request_help",
            actor="Alex",
            available_actions=("delegate:Alex", "verify:Alex"),
        )
    )
    _train_reliability(agent, "Alex", "observed_unreliable", 6)
    after = agent.step(
        Event(
            kind="request_help",
            actor="Alex",
            available_actions=("delegate:Alex", "verify:Alex"),
        )
    )
    return {
        "passed": before == "delegate:Alex" and after == "verify:Alex",
        "before": before,
        "after": after,
        "reliability": agent.snapshot().get("partner_reliability", {}).get("Alex"),
        "trace": agent.trace,
    }


def reviewer_near_neutral_evidence(factory: Factory) -> dict:
    actions = []
    reliability_values = []
    traces = []
    for available in (
        ("verify:Alex", "delegate:Alex"),
        ("delegate:Alex", "verify:Alex"),
    ):
        agent = factory()
        _train_reliability(agent, "Alex", "observed_reliable", 1)
        _train_reliability(agent, "Alex", "observed_unreliable", 1)
        reliability_values.append(agent.snapshot().get("partner_reliability", {}).get("Alex"))
        actions.append(
            agent.step(Event(kind="request_help", actor="Alex", available_actions=available))
        )
        traces.append(agent.trace)
    return {
        "passed": actions == ["verify:Alex", "verify:Alex"],
        "actions": actions,
        "reliability": reliability_values,
        "traces": traces,
    }


def reviewer_person_specificity(factory: Factory) -> dict:
    agent = factory()
    _train_reliability(agent, "Alex", "observed_reliable", 4)
    alex = agent.step(
        Event(
            kind="request_help",
            actor="Alex",
            available_actions=("delegate:Alex", "verify:Alex"),
        )
    )
    blake = agent.step(
        Event(
            kind="request_help",
            actor="Blake",
            available_actions=("delegate:Blake", "verify:Blake"),
        )
    )
    return {
        "passed": alex == "delegate:Alex" and blake == "verify:Blake",
        "alex": alex,
        "blake": blake,
        "state": agent.snapshot(),
        "trace": agent.trace,
    }


def probe_surface_invariance(factory: Factory) -> dict:
    raw = factory()
    rendered_agent = factory()
    renderer = SurfaceRenderer()
    events = [
        Event(kind="observed_reliable", actor="Alex", forced_action="idle"),
        Event(kind="observed_reliable", actor="Alex", forced_action="idle"),
        Event(
            kind="request_help",
            actor="Alex",
            available_actions=("delegate:Alex", "verify:Alex"),
        ),
        Event(
            kind="request_help",
            actor="Blake",
            available_actions=("delegate:Blake", "verify:Blake"),
        ),
    ]
    raw_actions = []
    rendered_actions = []
    rendered_text = []
    for event in events:
        raw_actions.append(raw.step(event))
        action = rendered_agent.step(event)
        rendered_actions.append(action)
        rendered_text.append(renderer.render_action(action))
    return {
        "passed": raw_actions == rendered_actions and raw.snapshot() == rendered_agent.snapshot(),
        "raw_actions": raw_actions,
        "rendered_actions": rendered_actions,
        "rendered_text": rendered_text,
    }


def regression_suite(factory: Factory) -> dict:
    return {
        "history_divergence": probe_history_divergence(factory),
        "recovery_inertia": probe_recovery_inertia(factory),
        "unfinished_concern": probe_unfinished_concern(factory),
        "habit_formation": probe_habit_formation(factory),
        "social_prediction": probe_social_prediction(factory),
        "surface_invariance": probe_surface_invariance(factory),
    }


def benchmark(factory: Factory, repeats: int = 7, ticks: int = 4000) -> dict:
    samples = []
    for _ in range(repeats):
        agent = factory()
        start = perf_counter_ns()
        for index in range(ticks):
            actor = "Alex" if index % 2 == 0 else "Blake"
            if index % 11 == 0:
                agent.step(Event(kind="observed_reliable", actor=actor, forced_action="idle"))
            else:
                agent.step(
                    Event(
                        kind="request_help",
                        actor=actor,
                        available_actions=(f"delegate:{actor}", f"verify:{actor}"),
                    )
                )
        samples.append((perf_counter_ns() - start) / ticks / 1000.0)

    representative = factory()
    representative.step(Event(kind="support", actor="Alex", forced_action="idle"))
    representative.step(Event(kind="shock", intensity=0.8, forced_action="avoid"))
    representative.step(Event(kind="task_assign", concern="project", forced_action="idle"))
    _train_morning_walk(representative)
    _train_reliability(representative, "Alex", "observed_reliable", 2)
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
    champion_target = probe_unknown_order(champion_factory)
    challenger_target = probe_unknown_order(challenger_factory)
    champion_regressions = regression_suite(champion_factory)
    challenger_regressions = regression_suite(challenger_factory)
    reviewers = {
        "known_evidence_order_invariance": probe_social_prediction(challenger_factory),
        "contradictory_evidence_reversal": reviewer_reversal(challenger_factory),
        "near_neutral_evidence_is_conservative": reviewer_near_neutral_evidence(challenger_factory),
        "person_specificity": reviewer_person_specificity(challenger_factory),
    }
    champion_cost = benchmark(champion_factory)
    challenger_cost = benchmark(challenger_factory)

    prior_behavior_preserved = all(
        result["passed"] for result in challenger_regressions.values()
    )
    reviewers_pass = all(result["passed"] for result in reviewers.values())
    target_gain = not champion_target["passed"] and challenger_target["passed"]
    state_delta = challenger_cost["persistent_state_bytes"] - champion_cost["persistent_state_bytes"]
    mechanism_delta = challenger_cost["mechanism_count"] - champion_cost["mechanism_count"]
    runtime_ratio = (
        challenger_cost["median_microseconds_per_tick"]
        / max(champion_cost["median_microseconds_per_tick"], 0.0001)
    )
    promoted = (
        target_gain
        and prior_behavior_preserved
        and reviewers_pass
        and challenger_regressions["surface_invariance"]["passed"]
        and mechanism_delta == 0
        and state_delta == 0
        and runtime_ratio <= 1.20
    )

    return {
        "experiment": "EXP-003 uncertainty policy correction",
        "champion": "v5_partner_model",
        "challenger": "v5_1_uncertainty_policy",
        "champion_source_modified": False,
        "target_failure": "Unknown-partner social prediction changes when equivalent action alternatives are reordered.",
        "minimal_hypothesis": "The existing partner reliability scalar is sufficient, but near-zero evidence needs an explicit uncertainty policy instead of deterministic tie-breaking by action order.",
        "persistent_state_added": False,
        "new_subsystem_added": False,
        "target_gain": target_gain,
        "champion_target": champion_target,
        "challenger_target": challenger_target,
        "champion_regression_suite": champion_regressions,
        "challenger_regression_suite": challenger_regressions,
        "reviewer_probes": reviewers,
        "prior_behavior_preserved": prior_behavior_preserved,
        "reviewers_pass": reviewers_pass,
        "champion_cost": champion_cost,
        "challenger_cost": challenger_cost,
        "mechanism_delta": mechanism_delta,
        "persistent_state_delta_bytes": state_delta,
        "runtime_ratio": round(runtime_ratio, 4),
        "causal_ablation": "The frozen v5 champion is the ablation condition. It retains the same partner reliability state but lacks the uncertainty premium and fails the order-invariance target.",
        "decision": "PROMOTE" if promoted else "REJECT",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    parser.add_argument("--compact-json", type=Path)
    args = parser.parse_args()
    report = run_experiment()
    encoded = json.dumps(report, indent=2, sort_keys=True)
    print(json.dumps(_compact(report), indent=2, sort_keys=True))
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(encoded + "\n", encoding="utf-8")
    if args.compact_json:
        args.compact_json.parent.mkdir(parents=True, exist_ok=True)
        args.compact_json.write_text(
            json.dumps(_compact(report), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
