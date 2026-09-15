from __future__ import annotations

import argparse
import json
from pathlib import Path

from .exp005_challenger import ProspectiveCueCharacter
from .runtime import Event


def epistemic_history_divergence() -> dict:
    observations = {}
    for seen_location, hidden_location in (
        ("drawer", "shelf"),
        ("shelf", "drawer"),
    ):
        order_results = []
        traces = []
        for actions in (
            ("search:drawer", "search:shelf"),
            ("search:shelf", "search:drawer"),
        ):
            agent = ProspectiveCueCharacter()
            agent.step(
                Event(
                    kind="observe_location",
                    actor="book",
                    context=seen_location,
                    forced_action="idle",
                )
            )
            agent.step(
                Event(
                    kind="hidden_world_change",
                    actor="book",
                    context=hidden_location,
                    forced_action="idle",
                )
            )
            action = agent.step(
                Event(kind="retrieve", actor="book", available_actions=actions)
            )
            order_results.append(action)
            traces.append(agent.trace)
        observations[seen_location] = {
            "expected": f"search:{seen_location}",
            "actions": order_results,
            "traces": traces,
        }

    passed = all(
        row["actions"] == [row["expected"], row["expected"]]
        for row in observations.values()
    )
    return {
        "passed": passed,
        "failure_if_false": "Different perceived histories collapse to equivalent behavior because the organism stores no subject-owned world belief. Hidden changes and observations are behaviorally indistinguishable.",
        "observations": observations,
    }


def delayed_consequence_credit() -> dict:
    agent = ProspectiveCueCharacter()
    agent.step(
        Event(
            kind="context",
            context="morning",
            available_actions=("walk",),
        )
    )
    for _ in range(3):
        agent.step(Event(kind="neutral", forced_action="idle"))
    agent.step(Event(kind="outcome", reward=1.0, forced_action="idle"))
    choice = agent.step(
        Event(
            kind="context",
            context="morning",
            available_actions=("tea", "walk"),
        )
    )
    return {
        "passed": choice == "walk",
        "failure_if_false": "A delayed outcome cannot reinforce the action that caused it because the habit learner remembers only the immediately preceding action and context.",
        "choice": choice,
        "habits": agent.snapshot().get("habits", {}),
        "trace": agent.trace,
    }


def competing_concern_priority() -> dict:
    agent = ProspectiveCueCharacter()
    agent.step(
        Event(
            kind="task_assign",
            concern="minor_task",
            intensity=0.4,
            forced_action="idle",
        )
    )
    agent.step(
        Event(
            kind="task_assign",
            concern="urgent_task",
            intensity=1.0,
            forced_action="idle",
        )
    )
    before = agent.snapshot()
    agent.step(Event(kind="task_cancel", concern="urgent_task", forced_action="idle"))
    after = agent.snapshot()
    return {
        "passed": (
            before.get("active_concern") == "urgent_task"
            and after.get("active_concern") == "minor_task"
        ),
        "before": before,
        "after": after,
        "trace": agent.trace,
    }


def autonomous_continuation() -> dict:
    agent = ProspectiveCueCharacter()
    agent.step(
        Event(
            kind="task_assign",
            concern="finish_report",
            forced_action="idle",
        )
    )
    actions = [
        agent.step(
            Event(kind="neutral", available_actions=("work", "rest", "idle"))
        )
        for _ in range(6)
    ]
    return {
        "passed": "work" in actions and agent.snapshot().get("active_concern") is None,
        "actions": actions,
        "final_state": agent.snapshot(),
        "trace": agent.trace,
    }


def prospective_lure_resistance() -> dict:
    agent = ProspectiveCueCharacter()
    agent.step(
        Event(
            kind="future_commitment",
            concern="call_morgan",
            context="morgan_arrives",
            forced_action="idle",
        )
    )
    for cue in ("morgan_calls", "alex_arrives", "morgan_left"):
        agent.step(Event(kind="neutral", context=cue, forced_action="idle"))
    before_target = agent.snapshot()
    agent.step(Event(kind="neutral", context="morgan_arrives", forced_action="idle"))
    after_target = agent.snapshot()
    return {
        "passed": (
            before_target.get("active_concern") is None
            and before_target.get("prospective_commitments", {}).get("call_morgan") == "morgan_arrives"
            and after_target.get("active_concern") == "call_morgan"
        ),
        "before_target": before_target,
        "after_target": after_target,
        "trace": agent.trace,
    }


def run_audit() -> dict:
    probes = {
        "epistemic_history_divergence": epistemic_history_divergence(),
        "delayed_consequence_credit": delayed_consequence_credit(),
        "competing_concern_priority": competing_concern_priority(),
        "autonomous_continuation": autonomous_continuation(),
        "prospective_lure_resistance": prospective_lure_resistance(),
    }
    failures = [name for name, result in probes.items() if not result["passed"]]
    impact_order = [
        "epistemic_history_divergence",
        "delayed_consequence_credit",
        "competing_concern_priority",
        "autonomous_continuation",
        "prospective_lure_resistance",
    ]
    selected = next((name for name in impact_order if name in failures), None)
    return {
        "experiment": "EXP-006 adversarial audit",
        "champion": "v7_prospective_cue",
        "champion_modified": False,
        "probe_count": len(probes),
        "failures": failures,
        "selected_high_impact_failure": selected,
        "selection_basis": "Prefer perceptually obvious collapse of different lived histories into identical choices, then failures of learning from consequences, then lower-impact control failures.",
        "probes": probes,
    }


def compact(value):
    if isinstance(value, dict):
        return {
            key: compact(item)
            for key, item in value.items()
            if key not in {"trace", "traces"}
        }
    if isinstance(value, list):
        return [compact(item) for item in value]
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    report = run_audit()
    encoded = json.dumps(compact(report), indent=2, sort_keys=True)
    print(encoded)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(encoded + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
