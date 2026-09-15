from __future__ import annotations

import argparse
import json
from pathlib import Path

from .runtime import Event, PersistentCharacter, Version


CHAMPION = Version.PARTNER_MODEL


def multiple_concerns() -> dict:
    agent = PersistentCharacter(CHAMPION)
    agent.step(Event(kind="task_assign", concern="finish_report", forced_action="idle"))
    first_snapshot = agent.snapshot()
    agent.step(Event(kind="task_assign", concern="call_morgan", forced_action="idle"))
    second_snapshot = agent.snapshot()
    agent.step(Event(kind="task_cancel", concern="call_morgan", forced_action="idle"))
    action = agent.step(Event(kind="neutral", available_actions=("work", "rest", "idle")))
    final_snapshot = agent.snapshot()
    preserved = (
        final_snapshot.get("active_concern") == "finish_report"
        and action == "work"
    )
    return {
        "passed": preserved,
        "failure_if_false": "A second unfinished concern overwrites the first, so resolving the newer concern erases the older commitment.",
        "first_snapshot": first_snapshot,
        "second_snapshot": second_snapshot,
        "final_snapshot": final_snapshot,
        "post_cancel_action": action,
        "trace": agent.trace,
    }


def future_commitment() -> dict:
    agent = PersistentCharacter(CHAMPION)
    agent.step(Event(kind="task_assign", concern="call_morgan", forced_action="idle"))
    for _ in range(90):
        agent.step(Event(kind="neutral", forced_action="idle"))
    action = agent.step(
        Event(
            kind="neutral",
            context="promised_time",
            available_actions=("work", "rest", "idle"),
        )
    )
    snapshot = agent.snapshot()
    remembered = snapshot.get("active_concern") == "call_morgan" and action == "work"
    return {
        "passed": remembered,
        "failure_if_false": "An unfinished commitment disappears solely because time passed, even though nothing satisfied or cancelled it.",
        "post_delay_action": action,
        "final_snapshot": snapshot,
        "trace_tail": agent.trace[-8:],
    }


def relationship_repair() -> dict:
    agent = PersistentCharacter(CHAMPION)
    for _ in range(3):
        agent.step(Event(kind="hostility", actor="Alex", forced_action="idle"))
    hostile_value = agent.snapshot()["relationships"].get("Alex", 0.0)
    for _ in range(5):
        agent.step(Event(kind="support", actor="Alex", forced_action="idle"))
    repaired_value = agent.snapshot()["relationships"].get("Alex", 0.0)
    action = agent.step(
        Event(
            kind="encounter",
            actor="Alex",
            available_actions=("socialize:Alex", "avoid:Alex", "idle"),
        )
    )
    return {
        "passed": hostile_value < 0.0 and repaired_value > hostile_value and action == "socialize:Alex",
        "hostile_relationship": hostile_value,
        "repaired_relationship": repaired_value,
        "choice_after_repair": action,
        "trace": agent.trace,
    }


def habit_reversal() -> dict:
    agent = PersistentCharacter(CHAMPION)
    for _ in range(3):
        agent.step(Event(kind="context", context="morning", available_actions=("walk",)))
        agent.step(Event(kind="outcome", reward=1.0, forced_action="idle"))

    learned_choice = agent.step(
        Event(kind="context", context="morning", available_actions=("tea", "walk"))
    )

    for _ in range(5):
        agent.step(Event(kind="context", context="morning", forced_action="walk"))
        agent.step(Event(kind="outcome", reward=-1.0, forced_action="idle"))
        agent.step(Event(kind="context", context="morning", forced_action="tea"))
        agent.step(Event(kind="outcome", reward=1.0, forced_action="idle"))

    reversed_choice = agent.step(
        Event(kind="context", context="morning", available_actions=("tea", "walk"))
    )
    return {
        "passed": learned_choice == "walk" and reversed_choice == "tea",
        "learned_choice": learned_choice,
        "reversed_choice": reversed_choice,
        "habits": agent.snapshot().get("habits", {}),
        "trace_tail": agent.trace[-12:],
    }


def unrelated_partner_specificity() -> dict:
    agent = PersistentCharacter(CHAMPION)
    for _ in range(4):
        agent.step(Event(kind="observed_reliable", actor="Alex", forced_action="idle"))
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
        "alex_choice": alex,
        "blake_choice": blake,
        "partner_reliability": agent.snapshot().get("partner_reliability", {}),
        "trace": agent.trace,
    }


def run_audit() -> dict:
    probes = {
        "multiple_unfinished_concerns": multiple_concerns(),
        "future_commitment_after_long_delay": future_commitment(),
        "relationship_repair": relationship_repair(),
        "habit_reversal": habit_reversal(),
        "partner_specific_prediction": unrelated_partner_specificity(),
    }
    failures = [name for name, result in probes.items() if not result["passed"]]
    impact_order = [
        "multiple_unfinished_concerns",
        "future_commitment_after_long_delay",
        "relationship_repair",
        "habit_reversal",
        "partner_specific_prediction",
    ]
    selected = next((name for name in impact_order if name in failures), None)
    return {
        "experiment": "EXP-003 adversarial audit",
        "champion": CHAMPION.value,
        "champion_modified": False,
        "probe_count": len(probes),
        "failures": failures,
        "selected_high_impact_failure": selected,
        "selection_basis": "Prefer a failure that is longitudinal, perceptually obvious, and central to the impression that unfinished parts of a life continue to exist.",
        "probes": probes,
    }


def compact(report: dict) -> dict:
    result = dict(report)
    result["probes"] = {
        name: {k: v for k, v in value.items() if k not in {"trace", "trace_tail"}}
        for name, value in report["probes"].items()
    }
    return result


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
