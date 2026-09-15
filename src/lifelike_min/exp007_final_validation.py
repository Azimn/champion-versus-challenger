from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean, median, pstdev
from time import perf_counter_ns

from .exp006_challenger import SubjectiveFactCharacter
from .exp006_evaluation import benchmark as exp006_benchmark
from .exp007_challenger import EligibilityRecord, EligibilityTraceCharacter
from .exp007_evaluation import (
    development_suite,
    historical_regressions,
    run_ablations,
)
from .exp007_review import run_review as run_review1
from .exp007_review2 import run_review as run_review2
from .exp007_review3 import run_review as run_review3
from .runtime import Event


FROZEN_PRODUCTION_COMMIT = "f395d45b1418b87e06b06ffa226564ecb8ff0734"


def habit(agent, context: str, action: str) -> float:
    return float(agent.habits.get((context, action), 0.0))


def boundary_probe(neutral_events: int, reward: float = 1.0) -> dict:
    agent = EligibilityTraceCharacter()
    agent.step(Event(kind="context", context="garage", forced_action="tighten_bolt"))
    for _ in range(neutral_events):
        agent.step(Event(kind="neutral", forced_action="idle"))
    before = agent.snapshot()["eligibility_records"]
    derived = [
        {**row, "derived_eligibility": agent.eligibility_decay ** row["age"]}
        for row in before
    ]
    agent.step(Event(kind="outcome", reward=reward, context="garage", forced_action="idle"))
    return {
        "neutral_events": neutral_events,
        "before_outcome": derived,
        "learned_value": habit(agent, "garage", "tighten_bolt"),
        "after_outcome": agent.snapshot()["eligibility_records"],
    }


def boundary_audit() -> dict:
    before = boundary_probe(9)
    at = boundary_probe(10)
    after = boundary_probe(11)

    zero = EligibilityTraceCharacter()
    zero.step(Event(kind="context", context="cellar", forced_action="check_valve"))
    for _ in range(10):
        zero.step(Event(kind="neutral", forced_action="idle"))
    zero_before = zero.snapshot()["eligibility_records"]
    zero.step(Event(kind="outcome", reward=0.0, context="cellar", forced_action="idle"))
    zero_after = zero.snapshot()["eligibility_records"]
    zero.step(Event(kind="outcome", reward=1.0, context="cellar", forced_action="idle"))

    unrelated = EligibilityTraceCharacter()
    unrelated.step(Event(kind="context", context="garden", forced_action="water"))
    for _ in range(9):
        unrelated.step(Event(kind="neutral", forced_action="idle"))
    unrelated.step(Event(kind="context", context="hall", forced_action="dust"))
    target_before = [row for row in unrelated.snapshot()["eligibility_records"] if row["context"] == "garden"]
    unrelated.step(Event(kind="outcome", reward=1.0, context="garden", forced_action="idle"))

    passed = (
        before["learned_value"] > at["learned_value"] > 0.0
        and after["learned_value"] == 0.0
        and bool(zero_before)
        and not zero_after
        and habit(zero, "cellar", "check_valve") == 0.0
        and bool(target_before)
        and habit(unrelated, "garden", "water") > 0.0
    )
    return {
        "passed": passed,
        "semantic_rule": "Existing event-indexed evidence is read at event arrival, then aged/expired after event processing; the current action is recorded afterward at age zero.",
        "before_expiry": before,
        "at_boundary": at,
        "one_event_after_expiry": after,
        "zero_value_boundary": {
            "before": zero_before,
            "after_zero": zero_after,
            "later_reward_value": habit(zero, "cellar", "check_valve"),
        },
        "unrelated_context_at_boundary": {
            "target_before_outcome": target_before,
            "target_value": habit(unrelated, "garden", "water"),
            "unrelated_value": habit(unrelated, "hall", "dust"),
        },
        "multiple_events_per_transition_supported": False,
        "note": "The runtime accepts one Event per step, so multi-event atomic transitions are outside the current runtime contract rather than silently simulated.",
    }


def subjective_access_audit() -> dict:
    hidden = EligibilityTraceCharacter()
    hidden.step(Event(kind="context", context="greenhouse", forced_action="open_vent"))
    simulator_true_cause = {"context": "greenhouse", "action": "open_vent"}
    hidden.step(Event(kind="outcome", reward=1.0, context=None, forced_action="idle"))
    hidden_value = habit(hidden, "greenhouse", "open_vent")

    sufficient = EligibilityTraceCharacter()
    sufficient.step(Event(kind="context", context="greenhouse", forced_action="open_vent"))
    sufficient.step(Event(kind="neutral", forced_action="idle"))
    sufficient.step(Event(kind="outcome", reward=1.0, context="greenhouse", forced_action="idle"))
    sufficient_value = habit(sufficient, "greenhouse", "open_vent")

    ambiguous = EligibilityTraceCharacter()
    ambiguous.step(Event(kind="context", context="lab", forced_action="heat"))
    ambiguous.step(Event(kind="context", context="lab", forced_action="stir"))
    ambiguous.step(Event(kind="outcome", reward=1.0, context="lab", forced_action="idle"))
    heat = habit(ambiguous, "lab", "heat")
    stir = habit(ambiguous, "lab", "stir")

    return {
        "passed": hidden_value == 0.0 and sufficient_value > 0.0 and heat == 0.0 and stir == 0.0,
        "simulator_knows_but_subject_does_not": {
            "simulator_true_cause_not_passed_to_agent": simulator_true_cause,
            "organism_received_context": None,
            "learned_value": hidden_value,
        },
        "subjectively_unique": {"learned_value": sufficient_value},
        "subjectively_ambiguous": {"heat": heat, "stir": stir},
        "forbidden_inputs_used": [],
    }


def capacity_factory(capacity: int):
    return type(
        f"Capacity{capacity}EligibilityCharacter",
        (EligibilityTraceCharacter,),
        {"max_eligibility_records": capacity},
    )


def capacity_scenario(factory, concurrent: int) -> dict:
    agent = factory()
    agent.step(Event(kind="context", context="target", forced_action="target_action"))
    for index in range(concurrent - 1):
        agent.step(Event(kind="context", context=f"other_{index}", forced_action=f"other_action_{index}"))
    before = agent.snapshot()["eligibility_records"]
    agent.step(Event(kind="outcome", reward=1.0, context="target", forced_action="idle"))
    value = habit(agent, "target", "target_action")
    return {"concurrent_pairs": concurrent, "retained": value > 0.0, "target_value": value, "before": before}


def capacity_tournament() -> dict:
    rows = {}
    for capacity in (1, 2, 3, 4):
        factory = capacity_factory(capacity)
        historical = historical_regressions(factory)
        development = development_suite(factory)
        earned_failures = [name for name, row in historical.items() if not row["passed"]]
        earned_failures.extend(
            name
            for name in (
                "delayed_positive_1",
                "delayed_positive_3",
                "delayed_positive_8",
                "delayed_negative_1",
                "delayed_negative_3",
                "delayed_negative_8",
                "cross_context",
                "multiple_candidates",
                "irrelevant_outcome",
                "action_order_invariance",
            )
            if not development[name]["passed"]
        )
        rows[str(capacity)] = {
            "earned_behavior_failures": sorted(set(earned_failures)),
            "passes_all_earned_behavior": not earned_failures,
            "concurrency": {
                str(count): capacity_scenario(factory, count)
                for count in (1, 2, 3, 4)
            },
        }
    minimum = next((int(cap) for cap, row in rows.items() if row["passes_all_earned_behavior"]), None)
    return {
        "rows": rows,
        "minimum_capacity_preserving_current_earned_behavior": minimum,
        "capacity_four_behaviorally_earned": minimum == 4,
        "interpretation": "Concurrency probes expose the finite-memory tradeoff; the minimum is selected from previously earned behavioral claims, not from an arbitrary n+1 capacity challenge.",
    }


def distribution(samples: list[float]) -> dict:
    ordered = sorted(samples)
    return {
        "mean": round(mean(samples), 4),
        "median": round(median(samples), 4),
        "pstdev": round(pstdev(samples), 4),
        "min": round(ordered[0], 4),
        "p10": round(ordered[max(0, int(len(ordered) * 0.10) - 1)], 4),
        "p90": round(ordered[min(len(ordered) - 1, int(len(ordered) * 0.90))], 4),
        "max": round(ordered[-1], 4),
        "n": len(samples),
    }


def time_steps(factory, event_builder, repeats: int = 15, batch: int = 2000) -> dict:
    samples = []
    for repeat in range(repeats):
        agent = factory()
        # Warm the object without creating a large state difference between runs.
        for _ in range(20):
            agent.step(Event(kind="neutral", forced_action="idle"))
        start = perf_counter_ns()
        for index in range(batch):
            agent.step(event_builder(index))
        samples.append((perf_counter_ns() - start) / batch / 1000.0)
    return distribution(samples)


def initialization_cost(factory, repeats: int = 21, batch: int = 4000) -> dict:
    samples = []
    for _ in range(repeats):
        start = perf_counter_ns()
        for _ in range(batch):
            factory()
        samples.append((perf_counter_ns() - start) / batch / 1000.0)
    return distribution(samples)


def trace_payload_bytes(capacity: int) -> dict:
    agent = EligibilityTraceCharacter()
    agent.eligibility_records = [
        EligibilityRecord(context=f"c{index}", action=f"a{index}", age=index)
        for index in range(capacity)
    ]
    rows = agent.snapshot()["eligibility_records"]
    encoded = len(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    empty = len(json.dumps([], separators=(",", ":")).encode("utf-8"))
    return {
        "records": capacity,
        "trace_payload_bytes": encoded,
        "increment_over_empty": encoded - empty,
        "average_increment_per_record": round((encoded - empty) / capacity, 2) if capacity else 0.0,
    }


def representative_state(factory) -> int:
    agent = factory()
    agent.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    agent.step(Event(kind="task_assign", concern="finish_report", forced_action="idle"))
    agent.step(Event(kind="future_commitment", concern="call_morgan", context="morgan_arrives", forced_action="idle"))
    agent.step(Event(kind="support", actor="Alex", forced_action="idle"))
    agent.step(Event(kind="observed_reliable", actor="Alex", forced_action="idle"))
    return agent.persistent_state_bytes()


def max_capacity_state_bytes() -> int:
    agent = EligibilityTraceCharacter()
    for index in range(agent.max_eligibility_records):
        agent.step(Event(kind="context", context=f"capacity_{index}", forced_action=f"action_{index}"))
    return agent.persistent_state_bytes()


def cost_audit() -> dict:
    champion = SubjectiveFactCharacter
    challenger = EligibilityTraceCharacter
    champion_reference = exp006_benchmark(champion)
    challenger_reference = exp006_benchmark(challenger)

    mixed = lambda index: (
        Event(kind="context", context="morning", available_actions=("walk", "tea"))
        if index % 12 == 0
        else Event(kind="outcome", reward=0.8, context="morning", forced_action="idle")
        if index % 12 == 4
        else Event(kind="context", context="library", available_actions=("read", "idle"))
        if index % 12 == 6
        else Event(kind="outcome", reward=-0.5, context="library", forced_action="idle")
        if index % 12 == 10
        else Event(kind="neutral", forced_action="idle")
    )
    idle = lambda index: Event(kind="neutral", forced_action="idle")
    context = lambda index: Event(kind="context", context=f"c{index % 2}", forced_action="act")
    outcome = lambda index: Event(kind="outcome", context=f"c{index % 2}", reward=0.2, forced_action="idle")

    return {
        "champion": {
            "mechanism_count": SubjectiveFactCharacter().mechanism_count(),
            "fresh_state_bytes": SubjectiveFactCharacter().persistent_state_bytes(),
            "representative_state_bytes": representative_state(champion),
            "exp006_reference": champion_reference,
            "mixed_tick_us": time_steps(champion, mixed),
            "idle_tick_us": time_steps(champion, idle),
            "context_event_us": time_steps(champion, context),
            "outcome_event_us": time_steps(champion, outcome),
            "initialization_us": initialization_cost(champion),
        },
        "challenger": {
            "mechanism_count": EligibilityTraceCharacter().mechanism_count(),
            "fresh_state_bytes": EligibilityTraceCharacter().persistent_state_bytes(),
            "representative_state_bytes_no_active_trace": representative_state(challenger),
            "max_capacity_state_bytes_runtime_scenario": max_capacity_state_bytes(),
            "trace_payload": trace_payload_bytes(EligibilityTraceCharacter.max_eligibility_records),
            "exp006_reference": challenger_reference,
            "mixed_tick_us": time_steps(challenger, mixed),
            "idle_tick_us": time_steps(challenger, idle),
            "context_event_us": time_steps(challenger, context),
            "outcome_event_us": time_steps(challenger, outcome),
            "initialization_us": initialization_cost(challenger),
        },
        "rejected_four_field_archived_reference": {
            "persistent_state_bytes_in_comparable_exp007_representative": 553,
            "mixed_tick_median_us_observed_range": [13.5256, 19.9099],
            "note": "Archived CI runs varied materially; use the state reduction as the reliable simplification result and treat timing differences as noisy.",
        },
    }


def final_validation() -> dict:
    champion_baseline = exp006_benchmark(SubjectiveFactCharacter)
    historical = historical_regressions(EligibilityTraceCharacter)
    development = development_suite(EligibilityTraceCharacter)
    review1 = run_review1()
    review2 = run_review2()
    review3 = run_review3()
    ablations = run_ablations()
    boundary = boundary_audit()
    subjective = subjective_access_audit()
    capacity = capacity_tournament()
    costs = cost_audit()

    historical_failures = [name for name, row in historical.items() if not row["passed"]]
    development_failures = [name for name, row in development.items() if not row["passed"]]
    ablation_failures = [
        name for name, row in ablations.items()
        if not (
            row.get("diagnostic_passed", row.get("passed_if_improvement_disappears", False))
        )
    ]

    gate = {
        "champion_11_mechanisms": champion_baseline["mechanism_count"] == 11,
        "champion_state_near_recorded_451": 430 <= champion_baseline["persistent_state_bytes"] <= 480,
        "historical_regressions": not historical_failures,
        "developer_suite": not development_failures,
        "reviewer_pass_1": review1["reviewer_passed"],
        "reviewer_pass_2": review2["reviewer_passed"],
        "reviewer_pass_3": review3["reviewer_passed"],
        "causal_ablations": not ablation_failures,
        "event_boundary_semantics": boundary["passed"],
        "subjective_access_boundary": subjective["passed"],
        "bounded": len(EligibilityTraceCharacter().eligibility_records) <= EligibilityTraceCharacter.max_eligibility_records,
    }

    return {
        "experiment": "EXP-007 final validation of simplified context-action-age representation",
        "production_behavior_frozen_at": FROZEN_PRODUCTION_COMMIT,
        "production_modified_by_this_harness": False,
        "champion": "v8_subjective_fact",
        "challenger": "v9_context_eligibility_trace_candidate",
        "gate": gate,
        "all_required_validation_gates_pass": all(gate.values()),
        "historical_failures": historical_failures,
        "development_failures": development_failures,
        "ablation_failures": ablation_failures,
        "boundary_audit": boundary,
        "subjective_access_audit": subjective,
        "reviewer_pass_1": review1,
        "reviewer_pass_2": review2,
        "reviewer_pass_3": review3,
        "capacity_tournament": capacity,
        "cost_audit": costs,
        "claim_boundary": {
            "behavior_demonstrated": "Bounded subject-accessible evidence that a recent context-action pair occurred can let a later experienced consequence alter that behavior across intervening activity when context uniquely identifies one live candidate.",
            "mechanism_causally_supported": "A short bounded age-weighted context-action trace is sufficient for the tested form of context-cued delayed consequence credit.",
            "claims_not_established": [
                "general causal inference",
                "arbitrary long-horizon reinforcement learning",
                "hidden-cause attribution",
                "ambiguous same-context attribution",
                "unbounded temporal credit",
                "planning",
                "general episodic memory",
            ],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    report = final_validation()
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    raise SystemExit(0 if report["all_required_validation_gates_pass"] else 2)


if __name__ == "__main__":
    main()
