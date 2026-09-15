from __future__ import annotations

import argparse
import json
from pathlib import Path

from .exp007_challenger import EligibilityTraceCharacter
from .runtime import Event


def habit(agent: EligibilityTraceCharacter, context: str, action: str) -> float:
    return float(agent.habits.get((context, action), 0.0))


def derived_weight_matches_age() -> dict:
    rows = []
    passed = True
    for delay in (2, 5, 9):
        agent = EligibilityTraceCharacter()
        agent.step(Event(kind="context", context="courtyard", forced_action="sweep"))
        for _ in range(delay):
            agent.step(Event(kind="neutral", forced_action="idle"))
        before = agent.snapshot()["eligibility_records"]
        expected = agent.habit_learning_rate * (agent.eligibility_decay ** delay)
        agent.step(Event(kind="outcome", reward=1.0, context="courtyard", forced_action="idle"))
        observed = habit(agent, "courtyard", "sweep")
        ok = bool(before and before[0]["age"] == delay and abs(observed - expected) < 1e-12)
        passed = passed and ok
        rows.append({"delay": delay, "before": before, "expected": expected, "observed": observed, "passed": ok})
    return {
        "passed": passed,
        "rows": rows,
        "claim": "Age-derived weighting should be numerically equivalent to the declared decay rule without a stored eligibility field.",
    }


def boundary_three_way() -> dict:
    def run(neutral_events: int) -> float:
        agent = EligibilityTraceCharacter()
        agent.step(Event(kind="context", context="shed", forced_action="oil_hinge"))
        for _ in range(neutral_events):
            agent.step(Event(kind="neutral", forced_action="idle"))
        agent.step(Event(kind="outcome", reward=1.0, context="shed", forced_action="idle"))
        return habit(agent, "shed", "oil_hinge")

    before = run(9)
    at = run(10)
    after = run(11)
    return {
        "passed": before > at > 0.0 and after == 0.0,
        "before_boundary": before,
        "at_boundary": at,
        "after_boundary": after,
        "claim": "The event at the finite lifetime boundary may still use live evidence, while the following event may not.",
    }


def refresh_replaces_without_duplication() -> dict:
    agent = EligibilityTraceCharacter()
    agent.step(Event(kind="context", context="laundry", forced_action="fold"))
    for _ in range(6):
        agent.step(Event(kind="neutral", forced_action="idle"))
    aged = agent.snapshot()["eligibility_records"]
    agent.step(Event(kind="context", context="laundry", forced_action="fold"))
    refreshed = agent.snapshot()["eligibility_records"]
    return {
        "passed": bool(aged) and aged[0]["age"] == 6 and len(refreshed) == 1 and refreshed[0]["age"] == 0,
        "aged": aged,
        "refreshed": refreshed,
        "claim": "Repeating one context-action pair should refresh exactly one record rather than duplicating state.",
    }


def opposite_valence_updates_remain_specific() -> dict:
    agent = EligibilityTraceCharacter()
    agent.step(Event(kind="context", context="porch", forced_action="seal_wood"))
    agent.step(Event(kind="neutral", forced_action="idle"))
    agent.step(Event(kind="context", context="office", forced_action="skip_backup"))
    agent.step(Event(kind="neutral", forced_action="idle"))
    agent.step(Event(kind="outcome", reward=0.8, context="porch", forced_action="idle"))
    agent.step(Event(kind="outcome", reward=-0.7, context="office", forced_action="idle"))
    good = habit(agent, "porch", "seal_wood")
    bad = habit(agent, "office", "skip_backup")
    return {
        "passed": good > 0.0 and bad < 0.0,
        "positive": good,
        "negative": bad,
        "claim": "Opposite-valence delayed outcomes should remain isolated by subject-accessible context.",
    }


def ambiguity_still_abstains_after_refresh() -> dict:
    agent = EligibilityTraceCharacter()
    agent.step(Event(kind="context", context="kitchen", forced_action="stir"))
    agent.step(Event(kind="neutral", forced_action="idle"))
    agent.step(Event(kind="context", context="kitchen", forced_action="taste"))
    agent.step(Event(kind="neutral", forced_action="idle"))
    agent.step(Event(kind="context", context="kitchen", forced_action="stir"))
    before = agent.snapshot()["eligibility_records"]
    agent.step(Event(kind="outcome", reward=1.0, context="kitchen", forced_action="idle"))
    return {
        "passed": habit(agent, "kitchen", "stir") == 0.0 and habit(agent, "kitchen", "taste") == 0.0,
        "before_outcome": before,
        "stir": habit(agent, "kitchen", "stir"),
        "taste": habit(agent, "kitchen", "taste"),
        "claim": "Recency must not override same-context causal ambiguity when two actions remain plausible.",
    }


def semantically_reordered_contexts() -> dict:
    def run(order: tuple[str, str]) -> dict:
        agent = EligibilityTraceCharacter()
        actions = {"greenhouse": "vent", "studio": "cover_canvas"}
        for context in order:
            agent.step(Event(kind="context", context=context, forced_action=actions[context]))
        agent.step(Event(kind="neutral", forced_action="idle"))
        agent.step(Event(kind="outcome", reward=1.0, context="greenhouse", forced_action="idle"))
        return {
            "greenhouse": habit(agent, "greenhouse", "vent"),
            "studio": habit(agent, "studio", "cover_canvas"),
        }

    a = run(("greenhouse", "studio"))
    b = run(("studio", "greenhouse"))
    return {
        "passed": a["greenhouse"] > 0.0 and b["greenhouse"] > 0.0 and a["studio"] == 0.0 and b["studio"] == 0.0,
        "first_order": a,
        "second_order": b,
        "claim": "Semantically equivalent reordering should not redirect the outcome to an unrelated context-action pair.",
    }


def zero_reward_at_boundary_consumes_time_not_credit() -> dict:
    agent = EligibilityTraceCharacter()
    agent.step(Event(kind="context", context="basement", forced_action="check_pump"))
    for _ in range(10):
        agent.step(Event(kind="neutral", forced_action="idle"))
    before = agent.snapshot()["eligibility_records"]
    agent.step(Event(kind="outcome", reward=0.0, context="basement", forced_action="idle"))
    after_zero = agent.snapshot()["eligibility_records"]
    agent.step(Event(kind="outcome", reward=1.0, context="basement", forced_action="idle"))
    value = habit(agent, "basement", "check_pump")
    return {
        "passed": bool(before) and not after_zero and value == 0.0,
        "before_zero": before,
        "after_zero": after_zero,
        "later_value": value,
        "claim": "A zero-value boundary event may consume the final lifetime slot but cannot refresh or preserve credit for a later event.",
    }


def run_review() -> dict:
    probes = {
        "derived_weight_matches_age": derived_weight_matches_age(),
        "boundary_three_way": boundary_three_way(),
        "refresh_replaces_without_duplication": refresh_replaces_without_duplication(),
        "opposite_valence_specific": opposite_valence_updates_remain_specific(),
        "ambiguity_after_refresh_abstains": ambiguity_still_abstains_after_refresh(),
        "semantic_reordering": semantically_reordered_contexts(),
        "zero_reward_boundary": zero_reward_at_boundary_consumes_time_not_credit(),
    }
    failures = [name for name, row in probes.items() if not row["passed"]]
    return {
        "experiment": "EXP-007 third adversarial holdout generation",
        "production_behavior_frozen_at": "f395d45b1418b87e06b06ffa226564ecb8ff0734",
        "created_after_production_freeze": True,
        "probe_count": len(probes),
        "failures": failures,
        "reviewer_passed": not failures,
        "probes": probes,
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
    raise SystemExit(0 if report["reviewer_passed"] else 2)


if __name__ == "__main__":
    main()
