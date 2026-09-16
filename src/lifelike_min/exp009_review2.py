from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from .exp009_challenger import UnresolvedConcernPersistenceCharacter
from .runtime import Event

PRODUCTION_COMMIT = "b5cc3e109ab2fa4de0421dc113009d1ee7fb050d"


def assign(agent, concern: str, intensity: float = 1.0) -> None:
    agent.step(Event(kind="task_assign", concern=concern, intensity=intensity, forced_action="idle"))


def neutral(agent, n: int) -> None:
    for _ in range(n):
        agent.step(Event(kind="neutral", forced_action="idle"))


def reordered_equivalent_unrelated_histories() -> dict:
    left = UnresolvedConcernPersistenceCharacter()
    right = UnresolvedConcernPersistenceCharacter()
    assign(left, "unfinished")
    assign(right, "unfinished")
    block = [
        Event(kind="support", actor="A", forced_action="idle"),
        Event(kind="observe_location", actor="book", context="desk", forced_action="idle"),
        Event(kind="observed_reliable", actor="B", forced_action="idle"),
        Event(kind="context", context="morning", forced_action="idle"),
        Event(kind="neutral", forced_action="idle"),
    ]
    for _ in range(40):
        for event in block:
            left.step(event)
        for event in reversed(block):
            right.step(event)
    return {
        "passed": left.concerns == right.concerns and set(left.concerns) == {"unfinished"},
        "left_concern": dict(left.concerns),
        "right_concern": dict(right.concerns),
    }


def cancellation_timing_equivalence() -> dict:
    early = UnresolvedConcernPersistenceCharacter()
    late = UnresolvedConcernPersistenceCharacter()
    assign(early, "cancelled")
    assign(late, "cancelled")
    early.step(Event(kind="task_cancel", concern="cancelled", forced_action="idle"))
    neutral(early, 500)
    neutral(late, 500)
    late.step(Event(kind="task_cancel", concern="cancelled", forced_action="idle"))
    return {
        "passed": "cancelled" not in early.concerns and "cancelled" not in late.concerns,
        "early": dict(early.concerns),
        "late": dict(late.concerns),
    }


def cancel_reassign_cancel_semantics() -> dict:
    agent = UnresolvedConcernPersistenceCharacter()
    assign(agent, "paper", 1.0)
    neutral(agent, 250)
    agent.step(Event(kind="task_cancel", concern="paper", forced_action="idle"))
    absent_once = "paper" not in agent.concerns
    assign(agent, "paper", 0.8)
    reactivated = agent.concerns.get("paper")
    neutral(agent, 250)
    agent.step(Event(kind="task_cancel", concern="paper", forced_action="idle"))
    absent_twice = "paper" not in agent.concerns
    return {
        "passed": absent_once and reactivated is not None and reactivated > 0.0 and absent_twice,
        "reactivated": reactivated,
        "final": dict(agent.concerns),
    }


def work_resolves_current_without_erasing_dormant_other() -> dict:
    agent = UnresolvedConcernPersistenceCharacter()
    assign(agent, "old_weak", 1.0)
    neutral(agent, 300)
    weak_before = agent.concerns["old_weak"]
    assign(agent, "current", 1.0)
    current_initial = agent.concerns["current"]
    for _ in range(4):
        agent.step(Event(kind="neutral", forced_action="work"))
        if "current" not in agent.concerns:
            break
    return {
        "passed": (
            weak_before > 0.0
            and current_initial > weak_before
            and "current" not in agent.concerns
            and "old_weak" in agent.concerns
        ),
        "weak_before": weak_before,
        "current_initial": current_initial,
        "after_work": dict(agent.concerns),
    }


def same_name_active_latent_resolution_then_cue() -> dict:
    agent = UnresolvedConcernPersistenceCharacter()
    assign(agent, "report", 1.0)
    agent.step(Event(kind="future_commitment", concern="report", context="tomorrow", forced_action="idle"))
    coexist_before = "report" in agent.concerns and agent.prospective_commitments.get("report") == "tomorrow"
    for _ in range(4):
        agent.step(Event(kind="neutral", forced_action="work"))
        if "report" not in agent.concerns:
            break
    active_resolved_latent_survives = "report" not in agent.concerns and agent.prospective_commitments.get("report") == "tomorrow"
    agent.step(Event(kind="neutral", context="tomorrow", forced_action="idle"))
    return {
        "passed": coexist_before and active_resolved_latent_survives and "report" in agent.concerns and "report" not in agent.prospective_commitments,
        "coexist_before": coexist_before,
        "after_work_concerns": dict(agent.concerns),
        "after_cue_strength": agent.concerns.get("report"),
        "prospective_after_cue": dict(agent.prospective_commitments),
    }


def zero_activation_loses_capacity_competition() -> dict:
    agent = UnresolvedConcernPersistenceCharacter()
    agent.concerns["zero_old"] = 0.0
    assign(agent, "strong", 1.0)
    assign(agent, "new", 0.8)
    return {
        "passed": len(agent.concerns) == 2 and "zero_old" not in agent.concerns and set(agent.concerns) == {"strong", "new"},
        "ledger": dict(agent.concerns),
    }


def dormant_concern_does_not_beat_social_motive_margin() -> dict:
    actions = []
    for order in (
        ("work", "socialize:Casey", "idle"),
        ("socialize:Casey", "idle", "work"),
    ):
        agent = UnresolvedConcernPersistenceCharacter()
        assign(agent, "dormant")
        neutral(agent, 1000)
        agent.affiliation = 0.90
        agent.competence = 0.65
        agent.fatigue = 0.20
        actions.append(
            agent.step(Event(kind="encounter", actor="Casey", available_actions=order))
        )
    return {
        "passed": actions == ["socialize:Casey", "socialize:Casey"],
        "actions": actions,
    }


def dormant_concern_and_delayed_credit_coexist() -> dict:
    agent = UnresolvedConcernPersistenceCharacter()
    assign(agent, "unfinished")
    neutral(agent, 200)
    before_concern = agent.concerns["unfinished"]
    agent.step(Event(kind="context", context="garden", forced_action="water"))
    agent.step(Event(kind="neutral", forced_action="idle"))
    agent.step(Event(kind="outcome", reward=1.0, context="garden", forced_action="idle"))
    learned = agent.habits.get(("garden", "water"), 0.0)
    after_concern = agent.concerns.get("unfinished")
    return {
        "passed": learned > 0.0 and after_concern is not None and 0.0 <= after_concern < before_concern,
        "learned": learned,
        "before_concern": before_concern,
        "after_concern": after_concern,
        "eligibility": [row.__dict__ for row in agent.eligibility_records],
    }


def reconstruct_then_resolve_by_different_routes() -> dict:
    cancel_agent = UnresolvedConcernPersistenceCharacter()
    work_agent = UnresolvedConcernPersistenceCharacter()
    for agent in (cancel_agent, work_agent):
        assign(agent, "task")
        neutral(agent, 700)
    cancel_agent = UnresolvedConcernPersistenceCharacter.from_persistent_json(cancel_agent.serialize_persistent())
    work_agent = UnresolvedConcernPersistenceCharacter.from_persistent_json(work_agent.serialize_persistent())
    cancel_agent.step(Event(kind="task_cancel", concern="task", forced_action="idle"))
    work_agent.step(Event(kind="neutral", forced_action="work"))
    return {
        "passed": "task" not in cancel_agent.concerns and "task" not in work_agent.concerns,
        "cancel": dict(cancel_agent.concerns),
        "work": dict(work_agent.concerns),
    }


def capacity_eviction_does_not_resurrect_after_cancel() -> dict:
    agent = UnresolvedConcernPersistenceCharacter()
    assign(agent, "old")
    neutral(agent, 400)
    assign(agent, "urgent_a", 1.0)
    assign(agent, "urgent_b", 0.9)
    evicted = "old" not in agent.concerns
    agent.step(Event(kind="task_cancel", concern="urgent_a", forced_action="idle"))
    agent.step(Event(kind="task_cancel", concern="urgent_b", forced_action="idle"))
    return {
        "passed": evicted and "old" not in agent.concerns and not agent.concerns,
        "final": dict(agent.concerns),
    }


def two_routes_same_terminal_absence() -> dict:
    cancelled = UnresolvedConcernPersistenceCharacter()
    worked = UnresolvedConcernPersistenceCharacter()
    assign(cancelled, "finish")
    assign(worked, "finish")
    neutral(cancelled, 100)
    neutral(worked, 100)
    cancelled.step(Event(kind="task_cancel", concern="finish", forced_action="idle"))
    worked.step(Event(kind="neutral", forced_action="work"))
    return {
        "passed": "finish" not in cancelled.concerns and "finish" not in worked.concerns,
        "cancelled": dict(cancelled.concerns),
        "worked": dict(worked.concerns),
    }


def deterministic_decay_matches_event_count_not_event_meaning() -> dict:
    neutral_agent = UnresolvedConcernPersistenceCharacter()
    factual_agent = UnresolvedConcernPersistenceCharacter()
    assign(neutral_agent, "same")
    assign(factual_agent, "same")
    for index in range(300):
        neutral_agent.step(Event(kind="neutral", forced_action="idle"))
        if index % 2 == 0:
            factual_agent.step(Event(kind="observe_location", actor=f"obj{index}", context="room", forced_action="idle"))
        else:
            factual_agent.step(Event(kind="observed_reliable", actor=f"person{index}", forced_action="idle"))
    left = neutral_agent.concerns.get("same")
    right = factual_agent.concerns.get("same")
    return {
        "passed": left is not None and right is not None and math.isclose(left, right, rel_tol=0.0, abs_tol=0.0),
        "neutral_strength": left,
        "factual_strength": right,
    }


def run_review() -> dict:
    probes = {
        "reordered_equivalent_unrelated_histories": reordered_equivalent_unrelated_histories(),
        "cancellation_timing_equivalence": cancellation_timing_equivalence(),
        "cancel_reassign_cancel_semantics": cancel_reassign_cancel_semantics(),
        "work_resolves_current_without_erasing_dormant_other": work_resolves_current_without_erasing_dormant_other(),
        "same_name_active_latent_resolution_then_cue": same_name_active_latent_resolution_then_cue(),
        "zero_activation_loses_capacity_competition": zero_activation_loses_capacity_competition(),
        "dormant_concern_does_not_beat_social_motive_margin": dormant_concern_does_not_beat_social_motive_margin(),
        "dormant_concern_and_delayed_credit_coexist": dormant_concern_and_delayed_credit_coexist(),
        "reconstruct_then_resolve_by_different_routes": reconstruct_then_resolve_by_different_routes(),
        "capacity_eviction_does_not_resurrect_after_cancel": capacity_eviction_does_not_resurrect_after_cancel(),
        "two_routes_same_terminal_absence": two_routes_same_terminal_absence(),
        "deterministic_decay_matches_event_count_not_event_meaning": deterministic_decay_matches_event_count_not_event_meaning(),
    }
    failures = [name for name, row in probes.items() if not row["passed"]]
    return {
        "experiment": "EXP-009",
        "reviewer_generation": 2,
        "production_commit": PRODUCTION_COMMIT,
        "probes": probes,
        "failures": failures,
        "reviewer_passed": not failures,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    report = run_review()
    encoded = json.dumps(report, indent=2, sort_keys=True)
    print(encoded)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(encoded + "\n", encoding="utf-8")
    raise SystemExit(0 if report["reviewer_passed"] else 2)


if __name__ == "__main__":
    main()
