from __future__ import annotations

import argparse
import json
from pathlib import Path

from .runtime import Event
from .v9_1_compact import V91CompactCharacter


FROZEN_COMPACT_COMMIT = "2856ec6a32be0347a9243f6eff6faa404a9a0e6c"


def habit(agent, context: str, action: str) -> float:
    return float(agent.habits.get((context, action), 0.0))


def repeated_failed_search() -> dict:
    agent = V91CompactCharacter()
    agent.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    rows = []
    for attempt in range(5):
        action = agent.step(
            Event(
                kind="retrieve",
                actor="book",
                context="drawer",
                available_actions=("search:drawer", "search:shelf"),
            )
        )
        agent.step(Event(kind="outcome", reward=-1.0, context="drawer", forced_action="idle"))
        rows.append(
            {
                "attempt": attempt + 1,
                "chosen_search": action,
                "drawer_action_value": habit(agent, "drawer", "search:drawer"),
                "location_belief": agent.location_beliefs.get("book"),
            }
        )
    final_action = agent.step(
        Event(
            kind="retrieve",
            actor="book",
            context="drawer",
            available_actions=("search:shelf", "search:drawer"),
        )
    )
    reproduced = all(row["chosen_search"] == "search:drawer" for row in rows) and final_action == "search:drawer"
    return {
        "reproduced": reproduced,
        "observable_behavior": "After five explicitly negative search outcomes at the believed location, the organism still searches the same location even though it has accumulated negative action experience there.",
        "rows": rows,
        "final_reordered_choice": final_action,
        "expected_current_mechanisms": ["subjective location fact", "contextual habit learning", "delayed consequence credit"],
        "renderer_involved": False,
        "subjective_information_available": True,
    }


def unfinished_activity_evaporates() -> dict:
    agent = V91CompactCharacter()
    agent.step(Event(kind="task_assign", concern="finish_portfolio", intensity=1.0, forced_action="idle"))
    initial = agent.snapshot()["concern_ledger"].copy()
    vanished_at = None
    for offset in range(1, 121):
        agent.step(Event(kind="neutral", forced_action="idle"))
        if "finish_portfolio" not in agent.snapshot()["concern_ledger"]:
            vanished_at = offset
            break
    return {
        "reproduced": vanished_at is not None,
        "observable_behavior": "An explicitly unfinished activity disappears from organism state after unrelated time passes even though no completion, cancellation, or contradicting event occurred.",
        "initial": initial,
        "vanished_after_unrelated_events": vanished_at,
        "final_concerns": agent.snapshot()["concern_ledger"],
        "expected_current_mechanisms": ["bounded concern persistence"],
        "renderer_involved": False,
    }


def rewarded_routine_never_weakens() -> dict:
    agent = V91CompactCharacter()
    agent.step(Event(kind="context", context="morning", forced_action="walk"))
    agent.step(Event(kind="outcome", reward=1.0, forced_action="idle"))
    learned = habit(agent, "morning", "walk")
    for _ in range(1000):
        agent.step(Event(kind="neutral", forced_action="idle"))
    after_absence = habit(agent, "morning", "walk")
    choice = agent.step(
        Event(kind="context", context="morning", available_actions=("tea", "walk"))
    )
    return {
        "reproduced": learned > 0.0 and after_absence == learned and choice == "walk",
        "observable_behavior": "A once-rewarded contextual routine retains exactly the same learned strength across 1000 unrelated events and immediately dominates the same context on return.",
        "learned_value": learned,
        "value_after_1000_unrelated_events": after_absence,
        "return_choice": choice,
        "expected_current_mechanisms": ["contextual habit learning"],
        "renderer_involved": False,
    }


def ancient_commitment_reactivates_unchanged() -> dict:
    agent = V91CompactCharacter()
    agent.step(Event(kind="future_commitment", concern="call_morgan", context="morgan_arrives", forced_action="idle"))
    for _ in range(1000):
        agent.step(Event(kind="neutral", forced_action="idle"))
    before_cue = agent.snapshot()
    agent.step(Event(kind="neutral", context="morgan_arrives", forced_action="idle"))
    after_cue = agent.snapshot()
    return {
        "reproduced": (
            before_cue["prospective_commitments"].get("call_morgan") == "morgan_arrives"
            and "call_morgan" in after_cue["concern_ledger"]
        ),
        "observable_behavior": "A latent commitment remains perfectly intact through 1000 unrelated events and reactivates at full concern strength when its cue finally occurs.",
        "before_cue": {
            "prospective": before_cue["prospective_commitments"],
            "tick": before_cue["tick"],
        },
        "after_cue": {
            "concerns": after_cue["concern_ledger"],
            "prospective": after_cue["prospective_commitments"],
        },
        "expected_current_mechanisms": ["prospective cue binding", "bounded concern persistence"],
        "renderer_involved": False,
    }


def third_commitment_is_forgotten() -> dict:
    agent = V91CompactCharacter()
    for concern, cue in (
        ("first", "cue_first"),
        ("second", "cue_second"),
        ("third", "cue_third"),
    ):
        agent.step(Event(kind="future_commitment", concern=concern, context=cue, forced_action="idle"))
    stored = dict(agent.snapshot()["prospective_commitments"])
    agent.step(Event(kind="neutral", context="cue_first", forced_action="idle"))
    activated = dict(agent.snapshot()["concern_ledger"])
    return {
        "reproduced": "first" not in stored and "first" not in activated,
        "observable_behavior": "Creating a third simultaneous future commitment silently discards the oldest one; its later cue produces no recognition or action tendency.",
        "stored_after_three": stored,
        "after_first_cue_concerns": activated,
        "expected_current_mechanisms": ["prospective cue binding"],
        "renderer_involved": False,
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
    return {
        "reproduced": "low_priority" not in after_three and "low_priority" not in after_resolution,
        "observable_behavior": "A weaker unfinished demand is discarded when two stronger demands arrive and does not return after the stronger demands are resolved.",
        "after_three": after_three,
        "after_stronger_resolved": after_resolution,
        "expected_current_mechanisms": ["bounded concern persistence"],
        "renderer_involved": False,
    }


def deterministic_rhythm() -> dict:
    agent = V91CompactCharacter()
    actions = []
    for _ in range(120):
        actions.append(
            agent.step(Event(kind="neutral", available_actions=("rest", "work", "idle")))
        )

    tail = actions[-60:]
    periods = []
    for period in range(1, 21):
        if all(tail[index] == tail[index % period] for index in range(len(tail))):
            periods.append(period)
    return {
        "reproduced": bool(periods),
        "observable_behavior": "Under an unchanging environment, the autonomous action sequence settles into an exactly repeating short cycle rather than showing any endogenous variability.",
        "last_60_actions": tail,
        "exact_periods_le_20": periods,
        "expected_current_mechanisms": ["fatigue pressure", "competence pressure"],
        "renderer_involved": False,
    }


def run() -> dict:
    failures = {
        "repeated_failed_search": repeated_failed_search(),
        "unfinished_activity_evaporates": unfinished_activity_evaporates(),
        "rewarded_routine_never_weakens": rewarded_routine_never_weakens(),
        "ancient_commitment_reactivates_unchanged": ancient_commitment_reactivates_unchanged(),
        "third_commitment_is_forgotten": third_commitment_is_forgotten(),
        "suppressed_concern_never_returns": suppressed_concern_never_returns(),
        "deterministic_rhythm": deterministic_rhythm(),
    }
    reproduced = [name for name, row in failures.items() if row["reproduced"]]
    return {
        "phase": "post-v9.1 behavioral artificiality attack",
        "frozen_champion": "v9.1_compact",
        "frozen_commit": FROZEN_COMPACT_COMMIT,
        "production_changes": False,
        "reproduced_failures": reproduced,
        "failures": failures,
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
