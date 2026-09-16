from __future__ import annotations

import argparse
import json
from pathlib import Path

from .runtime import Event
from .v9_1_compact import V91CompactCharacter


def habit(agent, context: str, action: str) -> float:
    return float(agent.habits.get((context, action), 0.0))


def run_case(entity: str, believed: str, alternate: str, task_context: str, reverse_initial_order: bool) -> dict:
    agent = V91CompactCharacter()
    agent.step(Event(kind="observe_location", actor=entity, context=believed, forced_action="idle"))
    believed_action = f"search:{believed}"
    alternate_action = f"search:{alternate}"
    order = (alternate_action, believed_action) if reverse_initial_order else (believed_action, alternate_action)
    attempts = []
    for index in range(5):
        choice = agent.step(
            Event(kind="retrieve", actor=entity, context=task_context, available_actions=order)
        )
        agent.step(Event(kind="outcome", reward=-1.0, context=task_context, forced_action="idle"))
        attempts.append(
            {
                "attempt": index + 1,
                "choice": choice,
                "experienced_action_value": habit(agent, task_context, believed_action),
                "belief": agent.location_beliefs.get(entity),
            }
        )
        order = tuple(reversed(order))

    final_order = (alternate_action, believed_action)
    final_choice = agent.step(
        Event(kind="retrieve", actor=entity, context=task_context, available_actions=final_order)
    )

    # Direct perception remains a positive control: the existing belief mechanism can
    # change search behavior when the alternate location is actually observed.
    agent.step(Event(kind="observe_location", actor=entity, context=alternate, forced_action="idle"))
    after_reobservation = agent.step(
        Event(kind="retrieve", actor=entity, context=task_context, available_actions=(believed_action, alternate_action))
    )

    negative_value = habit(agent, task_context, believed_action)
    current_belief_score = 0.90
    current_alternate_score = 0.05
    hypothetical_existing_state_interaction = {
        "believed_score_plus_existing_habit": current_belief_score + negative_value,
        "alternate_score_plus_existing_habit": current_alternate_score + habit(agent, task_context, alternate_action),
    }

    return {
        "reproduced": (
            all(row["choice"] == believed_action for row in attempts)
            and final_choice == believed_action
            and negative_value <= -1.0
            and after_reobservation == alternate_action
        ),
        "entity": entity,
        "believed": believed,
        "alternate": alternate,
        "task_context": task_context,
        "attempts": attempts,
        "final_reordered_choice": final_choice,
        "after_direct_reobservation_choice": after_reobservation,
        "negative_experience_value": negative_value,
        "hypothetical_existing_state_interaction": hypothetical_existing_state_interaction,
    }


def unlabeled_control() -> dict:
    agent = V91CompactCharacter()
    agent.step(Event(kind="observe_location", actor="map", context="desk", forced_action="idle"))
    action = agent.step(Event(kind="retrieve", actor="map", available_actions=("search:desk", "search:shelf")))
    agent.step(Event(kind="outcome", reward=-1.0, forced_action="idle"))
    return {
        "passed": action == "search:desk" and not agent.habits,
        "interpretation": "Without any subject-accessible task context, current delayed/immediate credit does not fabricate an attribution. This is a scope control, not evidence for changing the belief.",
    }


def run() -> dict:
    cases = [
        run_case("book", "drawer", "shelf", "find_book", False),
        run_case("keys", "hook", "table", "find_keys", True),
        run_case("notebook", "desk", "bag", "find_notebook", False),
    ]
    return {
        "phase": "selected failure characterization",
        "frozen_champion": "v9.1_compact",
        "failure": "repeated negative search experience does not alter search choice while direct reobservation does",
        "production_changes": False,
        "cases": cases,
        "unlabeled_scope_control": unlabeled_control(),
        "reproduced_across_cases": all(case["reproduced"] for case in cases),
        "action_order_invariant": all(case["reproduced"] for case in cases),
        "existing_state_already_contains_negative_experience": all(case["negative_experience_value"] <= -1.0 for case in cases),
        "renderer_involved": False,
        "privileged_world_truth_used": False,
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
    raise SystemExit(0 if report["reproduced_across_cases"] else 2)


if __name__ == "__main__":
    main()
