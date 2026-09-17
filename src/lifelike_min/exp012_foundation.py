from __future__ import annotations

import argparse
import json
from pathlib import Path

from .exp011_challenger import CapacityThreeProspectiveCharacter
from .runtime import Event


def reinforce(agent, context: str, action: str, reward: float = 1.0) -> None:
    agent.step(Event(kind="neutral", context=context, available_actions=(action, "idle"), forced_action=action))
    agent.step(Event(kind="outcome", context=context, reward=reward, forced_action="idle"))


def unrelated(agent, count: int) -> None:
    for i in range(count):
        agent.step(Event(kind="neutral", context=f"unrelated_{i % 7}", forced_action="idle"))


def exact_original_failure() -> dict:
    a = CapacityThreeProspectiveCharacter()
    reinforce(a, "morning", "walk")
    initial = a.habits.get(("morning", "walk"))
    unrelated(a, 1000)
    after = a.habits.get(("morning", "walk"))
    chosen = a.step(Event(kind="neutral", context="morning", available_actions=("walk", "idle")))
    return {
        "initial_value": initial,
        "after_1000_unrelated": after,
        "return_action": chosen,
        "reproduced": initial == 0.35 and after == initial and chosen == "walk",
    }


def gap_sweep() -> dict:
    rows = {}
    for gap in (0, 1, 10, 100, 1000, 10000):
        a = CapacityThreeProspectiveCharacter()
        reinforce(a, "morning", "walk")
        unrelated(a, gap)
        rows[str(gap)] = {
            "value": a.habits.get(("morning", "walk")),
            "eligibility_count": len(a.eligibility_records),
            "tick": a.tick,
        }
    return rows


def matched_age_identity() -> dict:
    # Equalize total lifetime length. The only intended difference is whether the
    # same 0.35 habit value was learned near the beginning or near the end. Eleven
    # trailing events ensure temporary eligibility evidence has expired in both.
    old = CapacityThreeProspectiveCharacter()
    recent = CapacityThreeProspectiveCharacter()

    reinforce(old, "morning", "walk")
    unrelated(old, 1011)

    unrelated(recent, 1000)
    reinforce(recent, "morning", "walk")
    unrelated(recent, 11)

    old_encoded = old.serialize_persistent()
    recent_encoded = recent.serialize_persistent()
    return {
        "same_tick": old.tick == recent.tick,
        "tick": old.tick,
        "old_value": old.habits.get(("morning", "walk")),
        "recent_value": recent.habits.get(("morning", "walk")),
        "old_eligibility": [vars(row) for row in old.eligibility_records],
        "recent_eligibility": [vars(row) for row in recent.eligibility_records],
        "canonical_equal": old_encoded == recent_encoded,
        "old_canonical": old_encoded,
        "recent_canonical": recent_encoded,
    }


def nonreinforced_reexposure() -> dict:
    a = CapacityThreeProspectiveCharacter()
    reinforce(a, "morning", "walk")
    initial = a.habits[("morning", "walk")]
    for _ in range(20):
        a.step(Event(kind="neutral", context="morning", available_actions=("walk", "idle"), forced_action="walk"))
        # No outcome event follows. This is repeated context/action exposure without
        # reward information, not a negative reward supplied by the simulator.
    return {
        "initial": initial,
        "after_20_unreinforced_exposures": a.habits[("morning", "walk")],
        "unchanged": a.habits[("morning", "walk")] == initial,
    }


def old_vs_recent_competitor() -> dict:
    a = CapacityThreeProspectiveCharacter()
    reinforce(a, "morning", "walk")
    unrelated(a, 1000)
    reinforce(a, "morning", "stretch")
    unrelated(a, 11)

    values = {
        "walk": a.habits.get(("morning", "walk")),
        "stretch": a.habits.get(("morning", "stretch")),
    }

    first = CapacityThreeProspectiveCharacter.from_persistent_json(a.serialize_persistent())
    second = CapacityThreeProspectiveCharacter.from_persistent_json(a.serialize_persistent())
    order_a = first.step(Event(kind="neutral", context="morning", available_actions=("walk", "stretch")))
    order_b = second.step(Event(kind="neutral", context="morning", available_actions=("stretch", "walk")))
    return {
        "values": values,
        "walk_old_stretch_recent": True,
        "choice_walk_first": order_a,
        "choice_stretch_first": order_b,
        "order_dependent": order_a != order_b,
        "interpretation": "The frozen organism cannot express recency once temporary eligibility has expired: equally rewarded old and recent routines have equal scalar value, so the current action order resolves the tie.",
    }


def negative_value_stability() -> dict:
    a = CapacityThreeProspectiveCharacter()
    reinforce(a, "morning", "walk", reward=-1.0)
    initial = a.habits.get(("morning", "walk"))
    unrelated(a, 1000)
    return {
        "initial": initial,
        "after_1000_unrelated": a.habits.get(("morning", "walk")),
        "unchanged": a.habits.get(("morning", "walk")) == initial,
    }


def run() -> dict:
    original = exact_original_failure()
    age = matched_age_identity()
    competitor = old_vs_recent_competitor()
    reexposure = nonreinforced_reexposure()
    negative = negative_value_stability()
    passed = bool(
        original["reproduced"]
        and age["canonical_equal"]
        and competitor["order_dependent"]
        and reexposure["unchanged"]
        and negative["unchanged"]
    )
    return {
        "experiment": "EXP-012 foundation",
        "frozen_basis": "v9.4_prospective_capacity_three / 5f949c6e882f780e1d4c07f0b6b3bccf330936aa",
        "passed": passed,
        "original_failure": original,
        "gap_sweep": gap_sweep(),
        "matched_age_identity": age,
        "nonreinforced_reexposure": reexposure,
        "old_vs_recent_competitor": competitor,
        "negative_value_stability": negative,
        "causal_localization": {
            "stored_information": "The habit mechanism retains context, action, and one signed scalar action value. Temporary eligibility retains context/action/age for at most the earned eligibility lifetime, then expires.",
            "missing_information_after_eligibility_expiry": "There is no per-habit age, last-reinforcement tick, use count, timestamp, or separate current-activation variable.",
            "existing_mutable_carrier": "The habit scalar itself can be updated online and therefore could encode changing current strength without adding a field, if a defensible update rule is earned.",
            "frozen_update_semantics": "Positive or negative reward updates habit value. Unrelated events, nonreinforced context/action exposure, and mere passage of experienced events do not change it.",
            "state_identity_result": "At the same lifetime tick after eligibility expiry, a habit reinforced near the beginning and an otherwise identical habit reinforced near the end are canonically identical.",
        },
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--json", type=Path)
    args = p.parse_args()
    result = run()
    text = json.dumps(result, indent=2, sort_keys=True)
    print(text)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(text + "\n", encoding="utf-8")
    raise SystemExit(0 if result["passed"] else 2)


if __name__ == "__main__":
    main()
