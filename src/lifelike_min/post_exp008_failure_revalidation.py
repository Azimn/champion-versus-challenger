from __future__ import annotations

import argparse
import json
from pathlib import Path

from .runtime import Event
from .v9_1_compact import V91CompactCharacter


FROZEN_CHAMPION_COMMIT = "2856ec6a32be0347a9243f6eff6faa404a9a0e6c"
EXP008_DECISION = "REJECT"


def habit(agent, context: str, action: str) -> float:
    return float(agent.habits.get((context, action), 0.0))


def unfinished_activity_evaporates() -> dict:
    agent = V91CompactCharacter()
    agent.step(Event(kind="task_assign", concern="finish_portfolio", intensity=1.0, forced_action="idle"))
    initial = dict(agent.snapshot()["concern_ledger"])
    vanished_at = None
    for offset in range(1, 121):
        agent.step(Event(kind="neutral", forced_action="idle"))
        if "finish_portfolio" not in agent.snapshot()["concern_ledger"]:
            vanished_at = offset
            break
    reproduced = vanished_at is not None
    return {
        "reproduced": reproduced,
        "classification": "still reproduced" if reproduced else "eliminated incidentally",
        "initial": initial,
        "vanished_after_unrelated_events": vanished_at,
        "final_concerns": dict(agent.snapshot()["concern_ledger"]),
        "observable_behavior": "An explicitly unfinished activity disappears despite no completion, cancellation, or contradicting event.",
    }


def rewarded_routine_never_weakens() -> dict:
    agent = V91CompactCharacter()
    agent.step(Event(kind="context", context="morning", forced_action="walk"))
    agent.step(Event(kind="outcome", reward=1.0, forced_action="idle"))
    learned = habit(agent, "morning", "walk")
    for _ in range(1000):
        agent.step(Event(kind="neutral", forced_action="idle"))
    after_absence = habit(agent, "morning", "walk")
    choice = agent.step(Event(kind="context", context="morning", available_actions=("tea", "walk")))
    reproduced = learned > 0.0 and after_absence == learned and choice == "walk"
    return {
        "reproduced": reproduced,
        "classification": "still reproduced" if reproduced else "changed form",
        "learned_value": learned,
        "value_after_1000_unrelated_events": after_absence,
        "return_choice": choice,
        "observable_behavior": "A once-rewarded routine retains exactly the same learned strength across 1000 unrelated events.",
    }


def ancient_commitment_reactivates_unchanged() -> dict:
    agent = V91CompactCharacter()
    agent.step(Event(kind="future_commitment", concern="call_morgan", context="morgan_arrives", forced_action="idle"))
    for _ in range(1000):
        agent.step(Event(kind="neutral", forced_action="idle"))
    before = agent.snapshot()
    agent.step(Event(kind="neutral", context="morgan_arrives", forced_action="idle"))
    after = agent.snapshot()
    reproduced = (
        before["prospective_commitments"].get("call_morgan") == "morgan_arrives"
        and "call_morgan" in after["concern_ledger"]
    )
    return {
        "reproduced": reproduced,
        "classification": "still reproduced" if reproduced else "changed form",
        "tick_before_cue": before["tick"],
        "prospective_before_cue": dict(before["prospective_commitments"]),
        "concerns_after_cue": dict(after["concern_ledger"]),
        "observable_behavior": "A latent commitment remains perfectly intact for 1000 unrelated events and later reactivates without weakening.",
    }


def third_commitment_is_forgotten() -> dict:
    agent = V91CompactCharacter()
    for concern, cue in (("first", "cue_first"), ("second", "cue_second"), ("third", "cue_third")):
        agent.step(Event(kind="future_commitment", concern=concern, context=cue, forced_action="idle"))
    stored = dict(agent.snapshot()["prospective_commitments"])
    agent.step(Event(kind="neutral", context="cue_first", forced_action="idle"))
    activated = dict(agent.snapshot()["concern_ledger"])
    reproduced = "first" not in stored and "first" not in activated
    return {
        "reproduced": reproduced,
        "classification": "still reproduced" if reproduced else "changed form",
        "stored_after_three": stored,
        "after_first_cue_concerns": activated,
        "observable_behavior": "A third simultaneous future commitment silently evicts the oldest, whose later cue has no effect.",
    }


def suppressed_concern_never_returns() -> dict:
    agent = V91CompactCharacter()
    agent.step(Event(kind="task_assign", concern="low_priority", intensity=0.5, forced_action="idle"))
    agent.step(Event(kind="task_assign", concern="urgent_one", intensity=1.0, forced_action="idle"))
    agent.step(Event(kind="task_assign", concern="urgent_two", intensity=0.9, forced_action="idle"))
    after_three = dict(agent.snapshot()["concern_ledger"])
    agent.step(Event(kind="task_cancel", concern="urgent_one", forced_action="idle"))
    agent.step(Event(kind="task_cancel", concern="urgent_two", forced_action="idle"))
    after_resolution = dict(agent.snapshot()["concern_ledger"])
    reproduced = "low_priority" not in after_three and "low_priority" not in after_resolution
    return {
        "reproduced": reproduced,
        "classification": "still reproduced" if reproduced else "changed form",
        "after_three": after_three,
        "after_stronger_resolved": after_resolution,
        "observable_behavior": "A weaker unfinished demand discarded under capacity pressure never returns after stronger demands resolve.",
    }


def deterministic_rhythm() -> dict:
    agent = V91CompactCharacter()
    actions = [
        agent.step(Event(kind="neutral", available_actions=("rest", "work", "idle")))
        for _ in range(120)
    ]
    tail = actions[-60:]
    periods = [
        p for p in range(1, 21)
        if all(tail[index] == tail[index % p] for index in range(len(tail)))
    ]
    reproduced = bool(periods)
    return {
        "reproduced": reproduced,
        "classification": "still reproduced" if reproduced else "changed form",
        "exact_periods_le_20": periods,
        "last_60_actions": tail,
        "observable_behavior": "A constant environment produces an exactly repeating short autonomous action cycle.",
    }


def run() -> dict:
    failures = {
        "unfinished_activity_evaporates": unfinished_activity_evaporates(),
        "rewarded_routine_never_weakens": rewarded_routine_never_weakens(),
        "ancient_commitment_reactivates_unchanged": ancient_commitment_reactivates_unchanged(),
        "third_commitment_is_forgotten": third_commitment_is_forgotten(),
        "suppressed_concern_never_returns": suppressed_concern_never_returns(),
        "deterministic_rhythm": deterministic_rhythm(),
    }
    return {
        "phase": "post-EXP-008 failure queue revalidation",
        "exp008_decision": EXP008_DECISION,
        "champion": "v9.1_compact",
        "champion_commit": FROZEN_CHAMPION_COMMIT,
        "production_changes": False,
        "queue_size": len(failures),
        "still_reproduced": [name for name, row in failures.items() if row["classification"] == "still reproduced"],
        "changed": [name for name, row in failures.items() if row["classification"] != "still reproduced"],
        "failures": failures,
    }


def main():
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
