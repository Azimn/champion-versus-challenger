from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import median
from time import perf_counter_ns

from .runtime import Event, PersistentCharacter, Version
from .surface import SurfaceRenderer


TARGET_PROBES = (
    "history_divergence",
    "recovery_inertia",
    "unfinished_concern",
    "habit_formation",
)


def _history_case(version: Version, kind: str, actor: str = "Alex") -> tuple[str, list]:
    agent = PersistentCharacter(version)
    for _ in range(3):
        agent.step(Event(kind=kind, actor=actor, forced_action="idle"))
    action = agent.step(
        Event(
            kind="encounter",
            actor=actor,
            available_actions=(f"socialize:{actor}", f"avoid:{actor}", "idle"),
        )
    )
    return action, agent.trace


def probe_history_divergence(version: Version) -> dict:
    supportive, support_trace = _history_case(version, "support")
    hostile, hostile_trace = _history_case(version, "hostility")
    passed = supportive == "socialize:Alex" and hostile == "avoid:Alex"
    return {
        "passed": passed,
        "supportive_action": supportive,
        "hostile_action": hostile,
        "supportive_trace": support_trace,
        "hostile_trace": hostile_trace,
    }


def probe_recovery_inertia(version: Version) -> dict:
    agent = PersistentCharacter(version)
    agent.step(Event(kind="shock", intensity=1.0, forced_action="avoid"))
    actions = []
    for _ in range(9):
        actions.append(
            agent.step(
                Event(kind="neutral", available_actions=("avoid", "idle"))
            )
        )
    passed = actions[0] == "avoid" and actions[-1] == "idle"
    return {"passed": passed, "actions": actions, "trace": agent.trace}


def probe_unfinished_concern(version: Version) -> dict:
    agent = PersistentCharacter(version)
    assigned = agent.step(
        Event(
            kind="task_assign",
            concern="finish_project",
            available_actions=("work", "idle"),
        )
    )
    interrupted = agent.step(
        Event(kind="shock", intensity=1.0, available_actions=("avoid", "work", "idle"))
    )
    resumed = agent.step(
        Event(kind="neutral", available_actions=("work", "rest", "idle"))
    )
    passed = assigned == "work" and interrupted == "avoid" and resumed == "work"
    return {
        "passed": passed,
        "assigned_action": assigned,
        "interruption_action": interrupted,
        "resume_action": resumed,
        "trace": agent.trace,
    }


def _train_morning_walk(agent: PersistentCharacter) -> None:
    for _ in range(3):
        agent.step(
            Event(
                kind="context",
                context="morning",
                available_actions=("walk",),
            )
        )
        agent.step(Event(kind="outcome", reward=1.0, forced_action="idle"))


def probe_habit_formation(version: Version) -> dict:
    agent = PersistentCharacter(version)
    _train_morning_walk(agent)
    action = agent.step(
        Event(
            kind="context",
            context="morning",
            available_actions=("tea", "walk"),
        )
    )
    passed = action == "walk"
    return {"passed": passed, "choice": action, "trace": agent.trace}


def reviewer_relationship_specificity(version: Version) -> dict:
    agent = PersistentCharacter(version)
    for _ in range(3):
        agent.step(Event(kind="hostility", actor="Alex", forced_action="idle"))
    action = agent.step(
        Event(
            kind="encounter",
            actor="Blake",
            available_actions=("socialize:Blake", "avoid:Blake", "idle"),
        )
    )
    return {
        "passed": action == "socialize:Blake",
        "choice_with_unrelated_person": action,
        "trace": agent.trace,
    }


def reviewer_affect_decay(version: Version) -> dict:
    agent = PersistentCharacter(version)
    agent.step(Event(kind="shock", intensity=1.0, forced_action="avoid"))
    actions = [
        agent.step(Event(kind="neutral", available_actions=("avoid", "idle")))
        for _ in range(14)
    ]
    return {
        "passed": actions[0] == "avoid" and actions[-1] == "idle",
        "actions": actions,
        "trace": agent.trace,
    }


def reviewer_concern_cancellation(version: Version) -> dict:
    agent = PersistentCharacter(version)
    agent.step(
        Event(
            kind="task_assign",
            concern="finish_project",
            available_actions=("work", "idle"),
        )
    )
    agent.step(
        Event(kind="task_cancel", concern="finish_project", forced_action="idle")
    )
    action = agent.step(
        Event(kind="neutral", available_actions=("work", "rest", "idle"))
    )
    return {
        "passed": action != "work",
        "post_cancel_choice": action,
        "trace": agent.trace,
    }


def reviewer_habit_context_specificity(version: Version) -> dict:
    agent = PersistentCharacter(version)
    _train_morning_walk(agent)
    action = agent.step(
        Event(
            kind="context",
            context="evening",
            available_actions=("tea", "walk"),
        )
    )
    return {
        "passed": action == "tea",
        "evening_choice": action,
        "trace": agent.trace,
    }


def probe_surface_invariance(version: Version) -> dict:
    without_surface = PersistentCharacter(version)
    with_surface = PersistentCharacter(version)
    renderer = SurfaceRenderer()
    events = [
        Event(kind="support", actor="Alex", forced_action="idle"),
        Event(
            kind="encounter",
            actor="Alex",
            available_actions=("socialize:Alex", "avoid:Alex", "idle"),
        ),
        Event(kind="shock", available_actions=("avoid", "idle")),
        Event(kind="neutral", available_actions=("avoid", "idle")),
    ]
    actions_a = []
    actions_b = []
    rendered = []
    for event in events:
        actions_a.append(without_surface.step(event))
        action = with_surface.step(event)
        actions_b.append(action)
        rendered.append(renderer.render_action(action))
    return {
        "passed": actions_a == actions_b and without_surface.snapshot() == with_surface.snapshot(),
        "actions_without_surface": actions_a,
        "actions_with_surface": actions_b,
        "rendered": rendered,
    }


def target_results(version: Version) -> dict:
    return {
        "history_divergence": probe_history_divergence(version),
        "recovery_inertia": probe_recovery_inertia(version),
        "unfinished_concern": probe_unfinished_concern(version),
        "habit_formation": probe_habit_formation(version),
        "surface_invariance": probe_surface_invariance(version),
    }


def seed_representative_state(agent: PersistentCharacter) -> None:
    agent.step(Event(kind="support", actor="Alex", forced_action="idle"))
    agent.step(Event(kind="shock", intensity=0.8, forced_action="avoid"))
    agent.step(
        Event(kind="task_assign", concern="project", forced_action="idle")
    )
    if agent.has_habit_learning:
        agent.step(
            Event(
                kind="context",
                context="morning",
                available_actions=("walk",),
            )
        )
        agent.step(Event(kind="outcome", reward=1.0, forced_action="idle"))


def benchmark(version: Version, repeats: int = 7, ticks: int = 3000) -> dict:
    samples = []
    for _ in range(repeats):
        agent = PersistentCharacter(version)
        start = perf_counter_ns()
        for index in range(ticks):
            actor = "Alex" if index % 2 == 0 else "Blake"
            agent.step(
                Event(
                    kind="encounter",
                    actor=actor,
                    available_actions=(
                        f"socialize:{actor}",
                        f"avoid:{actor}",
                        "idle",
                    ),
                )
            )
        elapsed = perf_counter_ns() - start
        samples.append(elapsed / ticks / 1000.0)

    representative = PersistentCharacter(version)
    seed_representative_state(representative)
    return {
        "median_microseconds_per_tick": round(median(samples), 4),
        "representative_persistent_state_bytes": representative.persistent_state_bytes(),
        "mechanism_count": representative.mechanism_count(),
    }


def run_cycle(
    cycle: int,
    champion: Version,
    challenger: Version,
    target: str,
    reviewer_name: str,
    reviewer_fn,
    prior_targets: tuple[str, ...],
) -> dict:
    champion_results = target_results(champion)
    challenger_results = target_results(challenger)
    review = reviewer_fn(challenger)
    champion_cost = benchmark(champion)
    challenger_cost = benchmark(challenger)

    target_gain = (
        not champion_results[target]["passed"]
        and challenger_results[target]["passed"]
    )
    no_regression = all(
        challenger_results[name]["passed"] for name in prior_targets
    )
    surface_separation = challenger_results["surface_invariance"]["passed"]
    complexity_delta = (
        challenger_cost["mechanism_count"] - champion_cost["mechanism_count"]
    )

    promoted = (
        target_gain
        and no_regression
        and review["passed"]
        and surface_separation
        and complexity_delta <= 1
    )

    return {
        "cycle": cycle,
        "champion": champion.value,
        "challenger": challenger.value,
        "target_failure": target,
        "reviewer_probe": reviewer_name,
        "target_gain": target_gain,
        "prior_behavior_preserved": no_regression,
        "reviewer_failed_to_falsify": review["passed"],
        "surface_separation_preserved": surface_separation,
        "complexity_delta": complexity_delta,
        "champion_cost": champion_cost,
        "challenger_cost": challenger_cost,
        "champion_target_observation": champion_results[target],
        "challenger_target_observation": challenger_results[target],
        "reviewer_observation": review,
        "decision": "PROMOTE" if promoted else "REJECT",
    }


def compact_probe(probe: dict) -> dict:
    return {key: value for key, value in probe.items() if key != "trace"}


def compact_cycle(cycle: dict) -> dict:
    result = dict(cycle)
    result["champion_target_observation"] = compact_probe(
        result["champion_target_observation"]
    )
    result["challenger_target_observation"] = compact_probe(
        result["challenger_target_observation"]
    )
    result["reviewer_observation"] = compact_probe(result["reviewer_observation"])
    return result


def run_experiment() -> dict:
    cycle_specs = (
        (
            Version.REACTIVE,
            Version.RELATIONSHIP,
            "history_divergence",
            "relationship_specificity",
            reviewer_relationship_specificity,
            (),
        ),
        (
            Version.RELATIONSHIP,
            Version.AFFECT,
            "recovery_inertia",
            "affect_decay",
            reviewer_affect_decay,
            ("history_divergence",),
        ),
        (
            Version.AFFECT,
            Version.CONCERN,
            "unfinished_concern",
            "concern_cancellation",
            reviewer_concern_cancellation,
            ("history_divergence", "recovery_inertia"),
        ),
        (
            Version.CONCERN,
            Version.HABIT,
            "habit_formation",
            "habit_context_specificity",
            reviewer_habit_context_specificity,
            ("history_divergence", "recovery_inertia", "unfinished_concern"),
        ),
    )

    cycles = []
    for index, spec in enumerate(cycle_specs, start=1):
        cycle = run_cycle(index, *spec)
        cycles.append(cycle)
        if cycle["decision"] != "PROMOTE":
            break

    versions = {}
    for version in Version:
        results = target_results(version)
        passed = sum(int(results[name]["passed"]) for name in TARGET_PROBES)
        cost = benchmark(version)
        versions[version.value] = {
            "target_probes_passed": passed,
            "target_probes_total": len(TARGET_PROBES),
            "lifelikeness_per_mechanism": round(
                passed / cost["mechanism_count"], 4
            ),
            "cost": cost,
            "results": {
                name: compact_probe(results[name])
                for name in (*TARGET_PROBES, "surface_invariance")
            },
        }

    final_champion = Version.REACTIVE.value
    for cycle in cycles:
        if cycle["decision"] == "PROMOTE":
            final_champion = cycle["challenger"]
        else:
            break

    return {
        "experiment": "minimal_lifelike_non_llm_loop",
        "final_champion": final_champion,
        "cycles": cycles,
        "versions": versions,
    }


def to_markdown(report: dict) -> str:
    lines = [
        "# Minimal Lifelike Loop Results",
        "",
        f"Final champion: `{report['final_champion']}`",
        "",
        "| Version | Behavioral probes | Mechanisms | Median us/tick | State bytes | Lifelikeness/mechanism |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for version, data in report["versions"].items():
        cost = data["cost"]
        lines.append(
            f"| {version} | {data['target_probes_passed']}/{data['target_probes_total']} | "
            f"{cost['mechanism_count']} | {cost['median_microseconds_per_tick']} | "
            f"{cost['representative_persistent_state_bytes']} | "
            f"{data['lifelikeness_per_mechanism']} |"
        )

    lines.extend(["", "## Champion versus challenger cycles", ""])
    for cycle in report["cycles"]:
        lines.extend(
            [
                f"### Cycle {cycle['cycle']}: {cycle['target_failure']}",
                "",
                f"Champion: `{cycle['champion']}`  ",
                f"Challenger: `{cycle['challenger']}`  ",
                f"Reviewer falsification probe: `{cycle['reviewer_probe']}`  ",
                f"Decision: **{cycle['decision']}**  ",
                f"Target gain: `{cycle['target_gain']}`  ",
                f"Prior behavior preserved: `{cycle['prior_behavior_preserved']}`  ",
                f"Reviewer failed to falsify: `{cycle['reviewer_failed_to_falsify']}`  ",
                f"Complexity delta: `{cycle['complexity_delta']}`",
                "",
            ]
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args()

    report = run_experiment()
    compact = dict(report)
    compact["cycles"] = [compact_cycle(cycle) for cycle in report["cycles"]]

    encoded = json.dumps(compact, indent=2, sort_keys=True)
    print(encoded)
    if args.json:
        args.json.write_text(encoded + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(to_markdown(report), encoding="utf-8")


if __name__ == "__main__":
    main()
