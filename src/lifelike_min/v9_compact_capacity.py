from __future__ import annotations

import argparse
import json
from pathlib import Path

from .exp004_evaluation import (
    probe_multiple_concerns,
    reviewer_bounded_capacity as concern_bounded_capacity,
    reviewer_interruption,
    reviewer_reverse_order,
)
from .exp005_evaluation import (
    probe_event_cued_commitment,
    reviewer_bounded_store as prospective_bounded_store,
    reviewer_multiple_future_commitments,
    reviewer_wrong_cues,
)
from .global_ablation_v9 import earned_suite
from .runtime import Event
from .v9_compact import CompactV9Character


def class_with_capacities(concern_capacity: int, prospective_capacity: int):
    return type(
        f"CompactC{concern_capacity}P{prospective_capacity}",
        (CompactV9Character,),
        {
            "max_concerns": concern_capacity,
            "max_prospective": prospective_capacity,
        },
    )


def concern_specific(factory) -> dict:
    probes = {
        "multiple_concerns": probe_multiple_concerns(factory),
        "reverse_order": reviewer_reverse_order(factory),
        "interruption": reviewer_interruption(factory),
        "bounded": concern_bounded_capacity(factory),
    }
    failures = [name for name, row in probes.items() if not row["passed"]]
    return {"passed": not failures, "failures": failures}


def prospective_specific(factory) -> dict:
    probes = {
        "event_cued": probe_event_cued_commitment(factory),
        "multiple_future": reviewer_multiple_future_commitments(factory),
        "wrong_cues": reviewer_wrong_cues(factory),
        "bounded": prospective_bounded_store(factory),
    }
    failures = [name for name, row in probes.items() if not row["passed"]]
    return {"passed": not failures, "failures": failures}


def at_capacity_behavior(factory, concern_capacity: int, prospective_capacity: int) -> dict:
    concern_agent = factory()
    for index in range(concern_capacity):
        concern_agent.step(Event(kind="task_assign", concern=f"task_{index}", intensity=0.6 + 0.1 * index, forced_action="idle"))
    concern_before = dict(concern_agent.snapshot().get("concern_ledger", {}))
    concern_agent.step(Event(kind="neutral", available_actions=("work", "rest", "idle")))

    prospective_agent = factory()
    for index in range(prospective_capacity):
        prospective_agent.step(Event(kind="future_commitment", concern=f"future_{index}", context=f"cue_{index}", forced_action="idle"))
    prospective_before = dict(prospective_agent.snapshot().get("prospective_commitments", {}))
    activation = {}
    for index in range(prospective_capacity):
        prospective_agent.step(Event(kind="neutral", context=f"cue_{index}", forced_action="idle"))
        activation[f"future_{index}"] = f"future_{index}" in prospective_agent.snapshot().get("concern_ledger", {})

    return {
        "passed": (
            len(concern_before) == concern_capacity
            and len(prospective_before) == prospective_capacity
            and all(activation.values())
        ),
        "concern_before": concern_before,
        "prospective_before": prospective_before,
        "prospective_activation": activation,
    }


def capacity_state_bytes(factory, concern_capacity: int, prospective_capacity: int) -> dict:
    agent = factory()
    for index in range(concern_capacity):
        agent.step(Event(kind="task_assign", concern=f"task_{index}", forced_action="idle"))
    for index in range(prospective_capacity):
        agent.step(Event(kind="future_commitment", concern=f"future_{index}", context=f"cue_{index}", forced_action="idle"))
    return {
        "persistent_bytes": agent.persistent_state_bytes(),
        "concerns": len(agent.snapshot().get("concern_ledger", {})),
        "prospective": len(agent.snapshot().get("prospective_commitments", {})),
    }


def run() -> dict:
    rows = {}
    for c in (1, 2, 3):
        for p in (1, 2, 3):
            factory = class_with_capacities(c, p)
            earned = earned_suite(factory)
            concerns = concern_specific(factory)
            prospective = prospective_specific(factory)
            rows[f"c{c}_p{p}"] = {
                "earned_passed": earned["passed"],
                "earned_failures": earned["failures"],
                "concern_specific": concerns,
                "prospective_specific": prospective,
                "at_capacity": at_capacity_behavior(factory, c, p),
                "state": capacity_state_bytes(factory, c, p),
            }

    valid = [
        (c, p)
        for c in (1, 2, 3)
        for p in (1, 2, 3)
        if rows[f"c{c}_p{p}"]["earned_passed"]
        and rows[f"c{c}_p{p}"]["concern_specific"]["passed"]
        and rows[f"c{c}_p{p}"]["prospective_specific"]["passed"]
        and rows[f"c{c}_p{p}"]["at_capacity"]["passed"]
    ]
    minimum = min(valid, key=lambda pair: (sum(pair), pair[0], pair[1])) if valid else None
    return {
        "phase": "v9 compact bounded-store capacity tournament",
        "rows": rows,
        "valid_capacity_pairs": [list(pair) for pair in valid],
        "minimum_pair_preserving_current_earned_behavior": list(minimum) if minimum else None,
        "current_inherited_pair": [CompactV9Character.max_concerns, CompactV9Character.max_prospective],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    report = run()
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
