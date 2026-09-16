from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import exp008_evaluation as base
from .exp008_challenger import SearchExperiencePolicyCharacter
from .runtime import Event


def corrected_unknown_entity_control() -> dict:
    # Separate the unknown-belief tie control from positive-learning so the learning
    # case does not create two live same-context actions before the outcome.
    tie_agent = SearchExperiencePolicyCharacter()
    initial = tie_agent.step(
        Event(
            kind="retrieve",
            actor="map",
            context="find_map",
            available_actions=("search:desk", "search:shelf"),
        )
    )

    learner = SearchExperiencePolicyCharacter()
    learner.step(
        Event(
            kind="retrieve",
            actor="map",
            context="find_map",
            forced_action="search:shelf",
        )
    )
    learner.step(
        Event(
            kind="outcome",
            actor="map",
            context="find_map",
            reward=1.0,
            forced_action="idle",
        )
    )
    learned = learner.step(
        Event(
            kind="retrieve",
            actor="map",
            context="find_map",
            available_actions=("search:desk", "search:shelf"),
        )
    )
    learned_value = base.habit(
        learner,
        base.experience_context(learner, "map", "find_map"),
        "search:shelf",
    )
    return {
        "passed": (
            initial == "search:desk"
            and learned == "search:shelf"
            and learned_value > 0.0
            and "map" not in learner.location_beliefs
        ),
        "initial_unknown_tie_choice": initial,
        "learned_choice": learned,
        "learned_value": learned_value,
        "location_beliefs": dict(learner.location_beliefs),
        "correction_reason": "The first development test accidentally left two same-context actions live before the positive outcome, invoking EXP-007 ambiguity abstention.",
    }


def corrected_contradictory_outcomes() -> dict:
    agent = SearchExperiencePolicyCharacter()
    actor, task, action = "book", "find_book", "search:drawer"
    agent.step(
        Event(kind="observe_location", actor=actor, context="drawer", forced_action="idle")
    )
    for _ in range(3):
        agent.step(
            Event(kind="retrieve", actor=actor, context=task, forced_action=action)
        )
        agent.step(
            Event(
                kind="outcome",
                actor=actor,
                context=task,
                reward=-1.0,
                forced_action="idle",
            )
        )

    negative = base.habit(
        agent, base.experience_context(agent, actor, task), action
    )

    # Demonstrate the behavioral consequence on a reconstructed copy so choosing
    # the alternative does not itself insert a second same-context action into the
    # trace used for the later reversal test.
    avoidance_copy = SearchExperiencePolicyCharacter.from_persistent_json(
        agent.serialize_persistent()
    )
    avoidance = avoidance_copy.step(
        Event(
            kind="retrieve",
            actor=actor,
            context=task,
            available_actions=(action, "search:shelf"),
        )
    )

    for _ in range(4):
        agent.step(
            Event(kind="retrieve", actor=actor, context=task, forced_action=action)
        )
        agent.step(
            Event(
                kind="outcome",
                actor=actor,
                context=task,
                reward=1.0,
                forced_action="idle",
            )
        )

    recovered = base.habit(
        agent, base.experience_context(agent, actor, task), action
    )
    return_choice = agent.step(
        Event(
            kind="retrieve",
            actor=actor,
            context=task,
            available_actions=("search:shelf", action),
        )
    )
    return {
        "passed": (
            negative < 0.0
            and avoidance == "search:shelf"
            and recovered > negative
            and recovered > 0.0
            and return_choice == action
        ),
        "negative": negative,
        "avoidance_on_copy": avoidance,
        "recovered": recovered,
        "return_choice": return_choice,
        "correction_reason": "The first development test created a competing shelf trace before asking positive outcomes to update drawer; EXP-007 correctly abstained under same-context ambiguity.",
    }


def run() -> dict:
    # The v1 development file and its failed artifact are preserved. Only the two
    # controls classified as test-design errors are replaced here. Production code
    # is evaluated exactly as imported.
    original_unknown = base.unknown_entity_control
    original_contradictory = base.contradictory_outcomes
    try:
        base.unknown_entity_control = corrected_unknown_entity_control
        base.contradictory_outcomes = corrected_contradictory_outcomes
        report = base.run()
    finally:
        base.unknown_entity_control = original_unknown
        base.contradictory_outcomes = original_contradictory

    report["development_validation_generation"] = 2
    report["pass1_run"] = 35052130403
    report["pass1_artifact"] = 10429581428
    report["production_encoding_correction_commit"] = "ec269c949e2334c0df4ec2f9c5f55c8a202e1ac7"
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    report = run()
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    raise SystemExit(0 if report["passed"] else 2)


if __name__ == "__main__":
    main()
