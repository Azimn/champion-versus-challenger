from __future__ import annotations

import argparse
import json
from pathlib import Path

from .exp006_challenger import SubjectiveFactCharacter
from .exp006_evaluation import benchmark as exp006_benchmark
from .exp007_challenger import EligibilityTraceCharacter
from .exp007_evaluation import development_suite, historical_regressions, run_ablations
from .exp007_final_validation import boundary_audit, capacity_tournament, cost_audit
from .exp007_review import run_review as run_review1
from .exp007_review2 import run_review as run_review2
from .exp007_review3 import run_review as run_review3
from .runtime import Event


FROZEN_PRODUCTION_COMMIT = "8c1e692e2b115200e3d758e481eb12576aced907"
INVALIDATED_REVIEWER_ASSERTIONS = {
    "capacity_pressure_near_bound": (
        "This first-generation reviewer probe encoded the provisional capacity-four implementation by requiring exactly four live records. "
        "The later preregistered capacity tournament showed that capacity two preserves every previously earned behavioral claim while capacity one does not. "
        "The original probe is preserved and replayed, but its exact-four assertion is no longer a valid promotion gate."
    )
}


def habit(agent, context: str, action: str) -> float:
    return float(agent.habits.get((context, action), 0.0))


def corrected_subjective_access_audit() -> dict:
    # Simulator-side truth exists only in this test variable. It is deliberately not
    # represented in Event and therefore cannot be read by the organism.
    simulator_true_cause = {"context": "greenhouse", "action": "open_vent"}

    hidden = EligibilityTraceCharacter()
    hidden.step(Event(kind="context", context="greenhouse", forced_action="open_vent"))
    # Remove the legitimate immediate-adjacency inference path. The delayed outcome
    # now carries no subject-accessible context linking it to the earlier action.
    hidden.step(Event(kind="neutral", forced_action="idle"))
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
        "methodological_correction": (
            "The first final-audit attempt incorrectly placed an unlabeled outcome immediately after the action, "
            "which legitimately exercised the already-earned immediate habit rule. This corrected control inserts unrelated activity first."
        ),
        "simulator_knows_but_subject_does_not": {
            "simulator_true_cause_not_passed_to_agent": simulator_true_cause,
            "intervening_event": "neutral/idle",
            "outcome_context_available_to_subject": None,
            "learned_value": hidden_value,
        },
        "subjectively_unique": {"learned_value": sufficient_value},
        "subjectively_ambiguous": {"heat": heat, "stir": stir},
        "hidden_causal_ids_used": False,
        "privileged_world_history_used": False,
        "test_harness_metadata_used_by_agent": False,
    }


def selected_capacity_semantics() -> dict:
    at_capacity = EligibilityTraceCharacter()
    at_capacity.step(Event(kind="context", context="target", forced_action="target_action"))
    at_capacity.step(Event(kind="context", context="other", forced_action="other_action"))
    before = at_capacity.snapshot()["eligibility_records"]
    at_capacity.step(Event(kind="outcome", reward=1.0, context="target", forced_action="idle"))
    retained_value = habit(at_capacity, "target", "target_action")

    over_capacity = EligibilityTraceCharacter()
    over_capacity.step(Event(kind="context", context="target", forced_action="target_action"))
    over_capacity.step(Event(kind="context", context="other_a", forced_action="other_a"))
    over_capacity.step(Event(kind="context", context="other_b", forced_action="other_b"))
    after_eviction = over_capacity.snapshot()["eligibility_records"]
    over_capacity.step(Event(kind="outcome", reward=1.0, context="target", forced_action="idle"))
    evicted_value = habit(over_capacity, "target", "target_action")

    return {
        "passed": len(before) == 2 and retained_value > 0.0 and len(after_eviction) == 2 and evicted_value == 0.0,
        "capacity": EligibilityTraceCharacter.max_eligibility_records,
        "exact_capacity": {"before_outcome": before, "target_value": retained_value},
        "one_over_capacity": {"before_outcome": after_eviction, "target_value": evicted_value},
    }


def closeout() -> dict:
    champion_reference = exp006_benchmark(SubjectiveFactCharacter)
    historical = historical_regressions(EligibilityTraceCharacter)
    development = development_suite(EligibilityTraceCharacter)
    review1 = run_review1()
    review2 = run_review2()
    review3 = run_review3()
    ablations = run_ablations()
    boundary = boundary_audit()
    subjective = corrected_subjective_access_audit()
    capacities = capacity_tournament()
    selected_capacity = selected_capacity_semantics()
    costs = cost_audit()

    historical_failures = [name for name, row in historical.items() if not row["passed"]]
    development_failures = [name for name, row in development.items() if not row["passed"]]
    ablation_failures = [
        name for name, row in ablations.items()
        if not row.get("diagnostic_passed", row.get("passed_if_improvement_disappears", False))
    ]
    review1_raw_failures = list(review1["failures"])
    review1_semantic_failures = [
        name for name in review1_raw_failures if name not in INVALIDATED_REVIEWER_ASSERTIONS
    ]

    selected_minimum = capacities["minimum_capacity_preserving_current_earned_behavior"]
    capacity_is_minimum = selected_minimum == EligibilityTraceCharacter.max_eligibility_records == 2

    gate = {
        "champion_11_mechanisms": champion_reference["mechanism_count"] == 11,
        "champion_451_byte_reference_reproduced": champion_reference["persistent_state_bytes"] == 451,
        "historical_regressions": not historical_failures,
        "developer_suite": not development_failures,
        "reviewer_pass_1_semantic_claims": not review1_semantic_failures,
        "reviewer_pass_2": review2["reviewer_passed"],
        "reviewer_pass_3": review3["reviewer_passed"],
        "causal_ablations": not ablation_failures,
        "event_boundary_semantics": boundary["passed"],
        "subjective_access_boundary": subjective["passed"],
        "selected_capacity_semantics": selected_capacity["passed"],
        "selected_capacity_is_earned_minimum": capacity_is_minimum,
        "mechanism_count_12": EligibilityTraceCharacter().mechanism_count() == 12,
    }

    return {
        "experiment": "EXP-007 strict closeout after structural simplification",
        "production_behavior_frozen_at": FROZEN_PRODUCTION_COMMIT,
        "champion": "v8_subjective_fact",
        "challenger": "v9_context_eligibility_trace_candidate",
        "gate": gate,
        "all_required_validation_gates_pass": all(gate.values()),
        "historical_failures": historical_failures,
        "development_failures": development_failures,
        "ablation_failures": ablation_failures,
        "reviewer_pass_1": {
            "raw_result": review1,
            "raw_failures": review1_raw_failures,
            "invalidated_test_design_assertions": {
                name: INVALIDATED_REVIEWER_ASSERTIONS[name]
                for name in review1_raw_failures
                if name in INVALIDATED_REVIEWER_ASSERTIONS
            },
            "remaining_semantic_failures": review1_semantic_failures,
        },
        "reviewer_pass_2": review2,
        "reviewer_pass_3": review3,
        "event_boundary_audit": boundary,
        "subjective_access_audit": subjective,
        "capacity_tournament": capacities,
        "selected_capacity_semantics": selected_capacity,
        "cost_audit": costs,
        "second_order_methodological_review": {
            "contexts_do_causal_work": "Only subject-accessible exact context is used as a retrieval cue; context is insufficient when multiple live actions share it.",
            "context_is_not_hidden_causal_id": True,
            "unlabeled_delayed_outcome_abstains": subjective["simulator_knows_but_subject_does_not"]["learned_value"] == 0.0,
            "abstention_scope": "Abstention is counted as correct only when the organism lacks enough subject-accessible evidence to choose among live causes; it is not counted as acquisition of a new capability.",
            "existing_habit_mechanism_alone_sufficient": False,
            "evidence": "Frozen v8 loses delayed credit after interveners and can assign it to the wrong recent context-action pair.",
            "temporal_weighting_changes_behavioral_update": True,
            "delay_scope": "Short event buffer only: ages 0 through 10. Arbitrary long-horizon credit is not established.",
            "reward_magnitude_binary": False,
            "contradictory_consequences_tested": True,
            "positive_and_negative_updates_change_later_choice": True,
            "one_record_design_sufficient": False,
            "one_record_failure": capacities["rows"]["1"]["earned_behavior_failures"],
            "two_record_design_sufficient_for_current_earned_claims": capacities["rows"]["2"]["passes_all_earned_behavior"],
        },
        "scientific_claim": {
            "behavior_demonstrated": "The organism can retain bounded subject-accessible evidence that a recent context-action pair occurred and let a later experienced consequence influence that behavior across unrelated intervening activity when subjective context uniquely identifies one live candidate.",
            "mechanism_causally_supported": "A two-record, finite-lifetime, age-weighted context-action trace is sufficient for the tested form of context-cued delayed consequence credit.",
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
    report = closeout()
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    raise SystemExit(0 if report["all_required_validation_gates_pass"] else 2)


if __name__ == "__main__":
    main()
