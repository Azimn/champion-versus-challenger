from __future__ import annotations

import argparse
import json
from pathlib import Path

from .runtime import Event
from .v9_1_compact import V91CompactCharacter
from .v9_1_structural_closeout import (
    BEHAVIORAL_ANCESTOR,
    BEHAVIORAL_ANCESTOR_COMMIT,
    GLOBAL_ABLATION_EVIDENCE_ARTIFACT,
    GLOBAL_ABLATION_EVIDENCE_RUN,
    STRUCTURAL_CANDIDATE,
    cost_and_state_audit,
    explicit_earned_behavior_manifest,
    mechanism_reclassification,
    persistent_inventory,
    reverse_ablations,
    second_order_structural_review,
    structural_adversarial_holdouts,
)


def serialization_reconstruction_check() -> dict:
    original = V91CompactCharacter()
    original.step(Event(kind="support", actor="Alex", forced_action="idle"))
    original.step(Event(kind="shock", intensity=0.8, forced_action="avoid"))
    original.step(Event(kind="task_assign", concern="finish_report", intensity=0.8, forced_action="idle"))
    original.step(Event(kind="future_commitment", concern="call_morgan", context="morgan_arrives", forced_action="idle"))
    original.step(Event(kind="observed_reliable", actor="Alex", forced_action="idle"))
    original.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    original.step(Event(kind="context", context="morning", forced_action="walk"))
    original.step(Event(kind="outcome", reward=0.5, forced_action="idle"))
    original.step(Event(kind="context", context="garden", forced_action="water"))

    encoded = original.serialize_persistent()
    payload = json.loads(encoded)
    restored = V91CompactCharacter.from_persistent_json(encoded)
    before_equal = original.persistent_snapshot() == restored.persistent_snapshot()

    required_state_present = {
        "relationship": bool(payload.get("relationships")),
        "affect": payload.get("threat_residue", 0.0) > 0.0,
        "active_concern": bool(payload.get("concern_ledger")),
        "latent_prospective": bool(payload.get("prospective_commitments")),
        "habit": bool(payload.get("habits")),
        "partner_expectation": bool(payload.get("partner_reliability")),
        "subjective_fact": bool(payload.get("location_beliefs")),
        "live_eligibility": bool(payload.get("eligibility_records")),
    }

    continuation = [
        Event(kind="retrieve", actor="book", available_actions=("search:shelf", "search:drawer")),
        Event(kind="request_help", actor="Alex", available_actions=("verify:Alex", "delegate:Alex")),
        Event(kind="neutral", context="morgan_arrives", forced_action="idle"),
        Event(kind="outcome", reward=0.8, context="garden", forced_action="idle"),
        Event(kind="context", context="morning", available_actions=("walk", "tea")),
        Event(kind="neutral", available_actions=("work", "rest", "idle")),
    ]
    rows = []
    continued_equal = True
    for event in continuation:
        original_action = original.step(event)
        restored_action = restored.step(event)
        state_equal = original.persistent_snapshot() == restored.persistent_snapshot()
        action_equal = original_action == restored_action
        continued_equal = continued_equal and state_equal and action_equal
        rows.append(
            {
                "event": event.kind,
                "original_action": original_action,
                "restored_action": restored_action,
                "action_equal": action_equal,
                "persistent_state_equal": state_equal,
            }
        )

    return {
        "passed": before_equal and continued_equal and all(required_state_present.values()),
        "serialized_bytes": len(encoded.encode("utf-8")),
        "before_equal": before_equal,
        "required_state_present": required_state_present,
        "continuation": rows,
        "temporary_state_not_serialized": ["debug trace list"],
        "configuration_not_serialized": ["frozen class/version policy configuration"],
        "precision_rule": "Canonical persistence stores full-precision mutable organism values; rounded snapshot() output is diagnostic only.",
        "prior_closeout_failure": "The first closeout serialized rounded diagnostic state, so restored and uninterrupted instances diverged numerically after subsequent decay despite initially equal displayed snapshots.",
    }


def run_closeout() -> dict:
    manifest = explicit_earned_behavior_manifest()
    adversarial = structural_adversarial_holdouts()
    inventory = persistent_inventory()
    mechanisms = mechanism_reclassification()
    reverse = reverse_ablations()
    serialization = serialization_reconstruction_check()
    costs = cost_and_state_audit()
    second_order = second_order_structural_review(
        inventory, mechanisms, manifest, adversarial, serialization
    )

    gates = {
        "explicit_earned_behavior_manifest": manifest["passed"],
        "structural_adversarial_review": adversarial["passed"],
        "persistent_inventory_clean": inventory["passed"],
        "mechanism_reclassification": mechanisms["passed"],
        "reverse_ablations": reverse["passed"],
        "serialization_reconstruction": serialization["passed"],
        "second_order_structural_review": second_order["passed"],
        "state_reduced": costs["fresh_delta_bytes"] < 0 and costs["representative_delta_bytes"] < 0,
        "mechanism_count_reduced": mechanisms["reclassified_count"] < 12,
    }
    decision = "PROMOTE" if all(gates.values()) else "REJECT"
    return {
        "phase": "GLOBAL STRUCTURAL ABLATION v9 closeout after persistence correction",
        "candidate": STRUCTURAL_CANDIDATE,
        "behavioral_ancestor": BEHAVIORAL_ANCESTOR,
        "behavioral_ancestor_commit": BEHAVIORAL_ANCESTOR_COMMIT,
        "behavioral_claim_change": "NONE: architectural compaction and persistence-contract correction only.",
        "completed_evidence_provenance": {
            "workflow_run": GLOBAL_ABLATION_EVIDENCE_RUN,
            "artifact": GLOBAL_ABLATION_EVIDENCE_ARTIFACT,
            "files": ["pairwise-consolidation.json", "capacity-tournament.json"],
        },
        "prior_closeout": {
            "workflow_run": 35028834468,
            "decision": "REJECT",
            "reason": "rounded diagnostic snapshot was not a lossless persistence representation",
            "production_behavior_changed_by_correction": False,
        },
        "adjudications": {
            "concern_prospective_consolidation": "REJECT_REPRESENTATIONALLY_INVALID",
            "reliability_location_consolidation": "REJECT_REPRESENTATIONALLY_INVALID",
            "affect_generic_temporal_container": "REJECT_GENERIC_CONSOLIDATION",
            "habit_shared_update_helper": "CODE_REFACTOR_ONLY",
            "concern_capacity": 2,
            "prospective_capacity": 2,
            "eligibility_capacity": 2,
        },
        "gates": gates,
        "decision": decision,
        "manifest": manifest,
        "structural_adversarial": adversarial,
        "persistent_inventory": inventory,
        "mechanism_reclassification": mechanisms,
        "reverse_ablations": reverse,
        "serialization_reconstruction": serialization,
        "cost_state_audit": costs,
        "second_order_review": second_order,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    report = run_closeout()
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    raise SystemExit(0 if report["decision"] == "PROMOTE" else 2)


if __name__ == "__main__":
    main()
