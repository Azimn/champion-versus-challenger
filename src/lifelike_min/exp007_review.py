from __future__ import annotations

import argparse
import json
from pathlib import Path

from .exp007_challenger import EligibilityTraceCharacter
from .runtime import Event


def habit(agent: EligibilityTraceCharacter, context: str, action: str) -> float:
    return float(agent.habits.get((context, action), 0.0))


def live_boundary_consequence() -> dict:
    """A trace live at consequence arrival should be eligible before end-of-tick decay."""
    agent = EligibilityTraceCharacter()
    agent.step(Event(kind="context", context="orchard", available_actions=("inspect",)))
    for _ in range(agent.max_eligibility_age):
        agent.step(Event(kind="neutral", forced_action="idle"))
    before = agent.snapshot()["eligibility_records"]
    was_live = any(row["context"] == "orchard" and row["action"] == "inspect" for row in before)
    agent.step(Event(kind="outcome", reward=1.0, context="orchard", forced_action="idle"))
    learned = habit(agent, "orchard", "inspect")
    return {
        "passed": was_live and learned > 0.0,
        "was_live_at_event_start": was_live,
        "before_outcome": before,
        "learned_value": learned,
        "failure_claim": "A trace that is still live immediately before the consequence event should not expire before that event can resolve it.",
    }


def same_context_ambiguity_abstains() -> dict:
    agent = EligibilityTraceCharacter()
    agent.step(Event(kind="context", context="garden", forced_action="water"))
    agent.step(Event(kind="neutral", forced_action="idle"))
    agent.step(Event(kind="context", context="garden", forced_action="prune"))
    before = agent.snapshot()["eligibility_records"]
    agent.step(Event(kind="outcome", reward=1.0, context="garden", forced_action="idle"))
    water = habit(agent, "garden", "water")
    prune = habit(agent, "garden", "prune")
    return {
        "passed": water == 0.0 and prune == 0.0,
        "water": water,
        "prune": prune,
        "before_outcome": before,
        "failure_claim": "When experienced context does not disambiguate two live actions, the organism should abstain rather than guess a hidden cause.",
    }


def reverse_outcome_order() -> dict:
    agent = EligibilityTraceCharacter()
    agent.step(Event(kind="context", context="garden", forced_action="water"))
    agent.step(Event(kind="context", context="library", forced_action="read"))
    agent.step(Event(kind="neutral", forced_action="idle"))
    agent.step(Event(kind="outcome", reward=-1.0, context="library", forced_action="idle"))
    agent.step(Event(kind="outcome", reward=1.0, context="garden", forced_action="idle"))
    water = habit(agent, "garden", "water")
    read = habit(agent, "library", "read")
    return {
        "passed": water > 0.0 and read < 0.0,
        "garden_water": water,
        "library_read": read,
        "failure_claim": "Two live context-action traces should be resolved by experienced context even when outcomes arrive in reverse action order.",
    }


def similar_context_lure() -> dict:
    agent = EligibilityTraceCharacter()
    agent.step(Event(kind="context", context="studio", forced_action="paint"))
    agent.step(Event(kind="context", context="studio_annex", forced_action="clean"))
    agent.step(Event(kind="outcome", reward=1.0, context="studio", forced_action="idle"))
    return {
        "passed": habit(agent, "studio", "paint") > 0.0 and habit(agent, "studio_annex", "clean") == 0.0,
        "studio_paint": habit(agent, "studio", "paint"),
        "studio_annex_clean": habit(agent, "studio_annex", "clean"),
        "failure_claim": "Context matching should be exact rather than lexical or prefix leakage.",
    }


def zero_reward_does_not_refresh() -> dict:
    agent = EligibilityTraceCharacter()
    agent.step(Event(kind="context", context="workshop", forced_action="sand"))
    for _ in range(3):
        agent.step(Event(kind="neutral", forced_action="idle"))
    before = agent.snapshot()["eligibility_records"]
    agent.step(Event(kind="outcome", reward=0.0, context="workshop", forced_action="idle"))
    after = agent.snapshot()["eligibility_records"]
    before_row = before[0] if before else None
    after_row = after[0] if after else None
    progressed = bool(
        before_row
        and after_row
        and after_row["age"] > before_row["age"]
        and after_row["eligibility"] < before_row["eligibility"]
    )
    return {
        "passed": progressed and habit(agent, "workshop", "sand") == 0.0,
        "before": before,
        "after": after,
        "failure_claim": "A zero-valued outcome should neither learn nor refresh eligibility.",
    }


def hidden_world_context_does_not_create_trace() -> dict:
    agent = EligibilityTraceCharacter()
    agent.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    after_observe = agent.snapshot()["eligibility_records"]
    agent.step(Event(kind="hidden_world_change", actor="book", context="shelf", forced_action="idle"))
    after_hidden = agent.snapshot()["eligibility_records"]
    return {
        "passed": not after_observe and not after_hidden,
        "after_observe": after_observe,
        "after_hidden": after_hidden,
        "failure_claim": "Perceptual and hidden-world bookkeeping events must not accidentally become eligible actions.",
    }


def capacity_pressure_near_bound() -> dict:
    agent = EligibilityTraceCharacter()
    agent.step(Event(kind="context", context="target", forced_action="target_action"))
    for index in range(3):
        agent.step(Event(kind="context", context=f"distractor_{index}", forced_action=f"act_{index}"))
    before = agent.snapshot()["eligibility_records"]
    agent.step(Event(kind="outcome", reward=1.0, context="target", forced_action="idle"))
    return {
        "passed": len(before) == 4 and habit(agent, "target", "target_action") > 0.0,
        "before_outcome": before,
        "target_value": habit(agent, "target", "target_action"),
        "failure_claim": "A target trace should survive exactly-at-capacity interference rather than being replaced prematurely.",
    }


def capacity_eviction_is_real() -> dict:
    agent = EligibilityTraceCharacter()
    agent.step(Event(kind="context", context="target", forced_action="target_action"))
    for index in range(4):
        agent.step(Event(kind="context", context=f"distractor_{index}", forced_action=f"act_{index}"))
    before = agent.snapshot()["eligibility_records"]
    target_live = any(row["context"] == "target" for row in before)
    agent.step(Event(kind="outcome", reward=1.0, context="target", forced_action="idle"))
    return {
        "passed": (not target_live) and habit(agent, "target", "target_action") == 0.0,
        "target_live": target_live,
        "before_outcome": before,
        "target_value": habit(agent, "target", "target_action"),
        "failure_claim": "Once finite capacity has actually evicted a trace, the organism must not reconstruct privileged causality later.",
    }


def positive_negative_symmetry() -> dict:
    def run(reward: float) -> float:
        agent = EligibilityTraceCharacter()
        agent.step(Event(kind="context", context="gallery", forced_action="sketch"))
        for _ in range(4):
            agent.step(Event(kind="neutral", forced_action="idle"))
        agent.step(Event(kind="outcome", reward=reward, context="gallery", forced_action="idle"))
        return habit(agent, "gallery", "sketch")

    positive = run(1.0)
    negative = run(-1.0)
    return {
        "passed": positive > 0.0 and negative < 0.0 and abs(abs(positive) - abs(negative)) < 1e-9,
        "positive": positive,
        "negative": negative,
        "failure_claim": "With symmetric unclamped starting state and equal delay, positive and negative consequences should have symmetric magnitude.",
    }


def names_contexts_and_spacing_holdout() -> dict:
    rows = []
    passed = True
    for context, action, delays in (
        ("atrium", "stretch", 2),
        ("north_lot", "check_tires", 5),
        ("archive_room", "label_box", 7),
    ):
        agent = EligibilityTraceCharacter()
        agent.step(Event(kind="context", context=context, forced_action=action))
        for index in range(delays):
            if index % 2:
                agent.step(Event(kind="support", actor=f"Person{index}", forced_action="idle"))
            else:
                agent.step(Event(kind="neutral", forced_action="idle"))
        agent.step(Event(kind="outcome", reward=0.6, context=context, forced_action="idle"))
        value = habit(agent, context, action)
        rows.append({"context": context, "action": action, "delay": delays, "value": value})
        passed = passed and value > 0.0
    return {
        "passed": passed,
        "rows": rows,
        "failure_claim": "The behavioral principle should survive novel names, contexts, temporal spacing, and irrelevant social events.",
    }


def run_review() -> dict:
    probes = {
        "live_boundary_consequence": live_boundary_consequence(),
        "same_context_ambiguity_abstains": same_context_ambiguity_abstains(),
        "reverse_outcome_order": reverse_outcome_order(),
        "similar_context_lure": similar_context_lure(),
        "zero_reward_does_not_refresh": zero_reward_does_not_refresh(),
        "hidden_world_context_does_not_create_trace": hidden_world_context_does_not_create_trace(),
        "capacity_pressure_near_bound": capacity_pressure_near_bound(),
        "capacity_eviction_is_real": capacity_eviction_is_real(),
        "positive_negative_symmetry": positive_negative_symmetry(),
        "novel_names_contexts_spacing": names_contexts_and_spacing_holdout(),
    }
    failures = [name for name, row in probes.items() if not row["passed"]]
    return {
        "experiment": "EXP-007 first adversarial reviewer pass",
        "implementation_under_review": "v9_eligibility_trace_candidate at first frozen implementation",
        "holdouts_created_after_implementation": True,
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
    # Reviewer discovery must preserve failures as evidence rather than suppressing
    # the artifact through a failing process exit. Promotion gating happens later.


if __name__ == "__main__":
    main()
