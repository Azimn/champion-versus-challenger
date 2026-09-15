from __future__ import annotations

import argparse
import json
from pathlib import Path

from .exp007_challenger import EligibilityTraceCharacter
from .runtime import Event


def habit(agent: EligibilityTraceCharacter, context: str, action: str) -> float:
    return float(agent.habits.get((context, action), 0.0))


def expired_on_prior_event_cannot_resurrect() -> dict:
    agent = EligibilityTraceCharacter()
    agent.step(Event(kind="context", context="patio", forced_action="sweep"))
    for _ in range(agent.max_eligibility_age + 1):
        agent.step(Event(kind="neutral", forced_action="idle"))
    after_expiry_event = agent.snapshot()["eligibility_records"]
    agent.step(Event(kind="outcome", reward=1.0, context="patio", forced_action="idle"))
    value = habit(agent, "patio", "sweep")
    return {
        "passed": not after_expiry_event and value == 0.0,
        "after_expiry_event": after_expiry_event,
        "learned_value": value,
        "claim": "The transient boundary correction must not resurrect a trace that expired on a prior event.",
    }


def zero_reward_boundary_then_late_reward() -> dict:
    agent = EligibilityTraceCharacter()
    agent.step(Event(kind="context", context="dock", forced_action="tie_rope"))
    for _ in range(agent.max_eligibility_age):
        agent.step(Event(kind="neutral", forced_action="idle"))
    before_zero = agent.snapshot()["eligibility_records"]
    agent.step(Event(kind="outcome", reward=0.0, context="dock", forced_action="idle"))
    after_zero = agent.snapshot()["eligibility_records"]
    agent.step(Event(kind="outcome", reward=1.0, context="dock", forced_action="idle"))
    value = habit(agent, "dock", "tie_rope")
    return {
        "passed": bool(before_zero) and not after_zero and value == 0.0,
        "before_zero": before_zero,
        "after_zero": after_zero,
        "late_reward_value": value,
        "claim": "A zero-valued boundary event may advance expiry but must not let the expired trace leak into a later reward event.",
    }


def unlabeled_delayed_outcome_does_not_infer_hidden_cause() -> dict:
    agent = EligibilityTraceCharacter()
    agent.step(Event(kind="context", context="greenhouse", forced_action="open_vent"))
    for _ in range(3):
        agent.step(Event(kind="neutral", forced_action="idle"))
    agent.step(Event(kind="outcome", reward=1.0, context=None, forced_action="idle"))
    value = habit(agent, "greenhouse", "open_vent")
    return {
        "passed": value == 0.0,
        "learned_value": value,
        "claim": "If the experienced consequence carries no matching context, the organism must not infer a hidden simulator cause from temporal proximity alone.",
    }


def context_only_idle_does_not_refresh() -> dict:
    agent = EligibilityTraceCharacter()
    agent.step(Event(kind="context", context="foyer", forced_action="wipe_table"))
    for _ in range(3):
        agent.step(Event(kind="neutral", forced_action="idle"))
    before = agent.snapshot()["eligibility_records"][0]
    agent.step(Event(kind="context", context="foyer", forced_action="idle"))
    after = agent.snapshot()["eligibility_records"][0]
    return {
        "passed": after["age"] > before["age"] and after["eligibility"] < before["eligibility"],
        "before": before,
        "after": after,
        "claim": "Merely revisiting a context without repeating the action must not refresh action eligibility.",
    }


def repeated_action_refreshes_same_record() -> dict:
    agent = EligibilityTraceCharacter()
    agent.step(Event(kind="context", context="kitchen", forced_action="stir"))
    for _ in range(5):
        agent.step(Event(kind="neutral", forced_action="idle"))
    before = agent.snapshot()["eligibility_records"]
    agent.step(Event(kind="context", context="kitchen", forced_action="stir"))
    after = agent.snapshot()["eligibility_records"]
    agent.step(Event(kind="neutral", forced_action="idle"))
    agent.step(Event(kind="outcome", reward=1.0, context="kitchen", forced_action="idle"))
    value = habit(agent, "kitchen", "stir")
    refreshed = (
        len(after) == 1
        and after[0]["age"] == 0
        and after[0]["eligibility"] == 1.0
    )
    return {
        "passed": bool(before) and refreshed and value > 0.0,
        "before_repeat": before,
        "after_repeat": after,
        "learned_value": value,
        "claim": "Repeating the same action in the same context should refresh one trace rather than accumulate duplicate records.",
    }


def delayed_negative_extinction_changes_choice() -> dict:
    agent = EligibilityTraceCharacter()
    for _ in range(3):
        agent.step(Event(kind="context", context="trail", forced_action="shortcut"))
        agent.step(Event(kind="outcome", reward=1.0, forced_action="idle"))
    before = habit(agent, "trail", "shortcut")
    for _ in range(6):
        agent.step(Event(kind="context", context="trail", forced_action="shortcut"))
        for _ in range(2):
            agent.step(Event(kind="neutral", forced_action="idle"))
        agent.step(Event(kind="outcome", reward=-1.0, context="trail", forced_action="idle"))
    after = habit(agent, "trail", "shortcut")
    choice = agent.step(Event(kind="context", context="trail", available_actions=("main_path", "shortcut")))
    return {
        "passed": before > 0.0 and after < 0.0 and choice == "main_path",
        "before": before,
        "after": after,
        "choice": choice,
        "claim": "Repeated delayed negative consequences should eventually extinguish and reverse an earlier learned preference.",
    }


def reward_magnitude_is_monotonic() -> dict:
    def run(reward: float) -> float:
        agent = EligibilityTraceCharacter()
        agent.step(Event(kind="context", context="bench", forced_action="organize"))
        for _ in range(3):
            agent.step(Event(kind="neutral", forced_action="idle"))
        agent.step(Event(kind="outcome", reward=reward, context="bench", forced_action="idle"))
        return habit(agent, "bench", "organize")

    weak = run(0.25)
    strong = run(1.0)
    return {
        "passed": 0.0 < weak < strong,
        "weak": weak,
        "strong": strong,
        "claim": "At equal delay and state, a stronger experienced consequence should produce a larger update than a weaker one.",
    }


def interleaved_outcomes_remain_specific() -> dict:
    agent = EligibilityTraceCharacter()
    agent.step(Event(kind="context", context="music_room", forced_action="practice"))
    agent.step(Event(kind="neutral", forced_action="idle"))
    agent.step(Event(kind="context", context="garage", forced_action="charge_battery"))
    for _ in range(2):
        agent.step(Event(kind="neutral", forced_action="idle"))
    agent.step(Event(kind="outcome", reward=0.8, context="music_room", forced_action="idle"))
    agent.step(Event(kind="neutral", forced_action="idle"))
    agent.step(Event(kind="outcome", reward=-0.6, context="garage", forced_action="idle"))
    practice = habit(agent, "music_room", "practice")
    charge = habit(agent, "garage", "charge_battery")
    return {
        "passed": practice > 0.0 and charge < 0.0,
        "practice": practice,
        "charge_battery": charge,
        "claim": "Multiple live traces must remain context-specific across interleaved delays and opposite-valence outcomes.",
    }


def negative_boundary_consequence() -> dict:
    agent = EligibilityTraceCharacter()
    agent.step(Event(kind="context", context="attic", forced_action="move_box"))
    for _ in range(agent.max_eligibility_age):
        agent.step(Event(kind="neutral", forced_action="idle"))
    before = agent.snapshot()["eligibility_records"]
    agent.step(Event(kind="outcome", reward=-1.0, context="attic", forced_action="idle"))
    value = habit(agent, "attic", "move_box")
    return {
        "passed": bool(before) and value < 0.0,
        "before_outcome": before,
        "learned_value": value,
        "claim": "The boundary correction must work for negative as well as positive consequences.",
    }


def capacity_brittleness_diagnostic() -> dict:
    agent = EligibilityTraceCharacter()
    agent.step(Event(kind="context", context="target", forced_action="target_action"))
    for index in range(4):
        agent.step(Event(kind="context", context=f"ordinary_{index}", forced_action=f"action_{index}"))
    rows = agent.snapshot()["eligibility_records"]
    target_live = any(row["context"] == "target" for row in rows)
    return {
        "diagnostic_only": True,
        "target_survives_four_distinct_intervening_actions": target_live,
        "capacity": agent.max_eligibility_records,
        "rows": rows,
        "interpretation": "This records the finite-memory tradeoff. Failure to retain the fifth distinct pair is not automatically a mechanism falsification, but it constrains the empirical claim and should be considered in the second-order review.",
    }


def run_review() -> dict:
    probes = {
        "expired_prior_event_cannot_resurrect": expired_on_prior_event_cannot_resurrect(),
        "zero_reward_boundary_then_late_reward": zero_reward_boundary_then_late_reward(),
        "unlabeled_delayed_outcome_no_hidden_inference": unlabeled_delayed_outcome_does_not_infer_hidden_cause(),
        "context_only_idle_does_not_refresh": context_only_idle_does_not_refresh(),
        "repeated_action_refreshes_same_record": repeated_action_refreshes_same_record(),
        "delayed_negative_extinction_changes_choice": delayed_negative_extinction_changes_choice(),
        "reward_magnitude_monotonic": reward_magnitude_is_monotonic(),
        "interleaved_outcomes_specific": interleaved_outcomes_remain_specific(),
        "negative_boundary_consequence": negative_boundary_consequence(),
    }
    failures = [name for name, row in probes.items() if not row["passed"]]
    return {
        "experiment": "EXP-007 second adversarial reviewer pass",
        "holdouts_new_after_first_reviewer_correction": True,
        "probe_count": len(probes),
        "failures": failures,
        "reviewer_passed": not failures,
        "probes": probes,
        "capacity_brittleness": capacity_brittleness_diagnostic(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    report = run_review()
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
