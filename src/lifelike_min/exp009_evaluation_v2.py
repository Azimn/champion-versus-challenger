from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import exp009_evaluation as v1
from .exp007_evaluation import renderer_invariance
from .exp009_challenger import UnresolvedConcernPersistenceCharacter
from .global_ablation_v9 import earned_suite
from .runtime import Event


def legitimate_termination() -> dict:
    """Corrected harness only: do not assume a weaker third concern survives bounding."""
    cancelled = UnresolvedConcernPersistenceCharacter()
    v1.assign(cancelled, "cancel_me")
    v1.run_unrelated(cancelled, 300)
    cancelled.step(Event(kind="task_cancel", concern="cancel_me", forced_action="idle"))

    worked = UnresolvedConcernPersistenceCharacter()
    v1.assign(worked, "work_me")
    v1.run_unrelated(worked, 300)
    before_work = worked.concerns.get("work_me")
    worked.step(Event(kind="neutral", forced_action="work"))

    capacity = UnresolvedConcernPersistenceCharacter()
    v1.assign(capacity, "old_weak")
    v1.run_unrelated(capacity, 300)
    v1.assign(capacity, "new_strong", 1.0)
    v1.assign(capacity, "new_second", 0.9)

    third_weaker = UnresolvedConcernPersistenceCharacter()
    v1.assign(third_weaker, "strong_a", 1.0)
    v1.assign(third_weaker, "strong_b", 0.9)
    third_weaker.step(
        Event(
            kind="task_assign",
            concern="weak_c",
            intensity=0.1,
            forced_action="idle",
        )
    )

    return {
        "passed": (
            "cancel_me" not in cancelled.concerns
            and before_work is not None
            and "work_me" not in worked.concerns
            and len(capacity.concerns) == 2
            and "old_weak" not in capacity.concerns
            and {"new_strong", "new_second"} == set(capacity.concerns)
            and len(third_weaker.concerns) == 2
            and "weak_c" not in third_weaker.concerns
        ),
        "after_cancel": dict(cancelled.concerns),
        "before_work": before_work,
        "after_work": dict(worked.concerns),
        "capacity_after_stronger_third": dict(capacity.concerns),
        "capacity_after_weaker_third": dict(third_weaker.concerns),
    }


def historical_contract() -> dict:
    suite = earned_suite(UnresolvedConcernPersistenceCharacter)
    renderer = renderer_invariance(UnresolvedConcernPersistenceCharacter)
    return {
        "passed": suite["passed"] and renderer["passed"],
        "earned_suite": suite,
        "renderer_invariance": renderer,
    }


def run() -> dict:
    sections = {
        "matched_retention": v1.matched_retention(),
        "unrelated_kind_invariance": v1.unrelated_kind_invariance(),
        "low_activation_non_dominance": v1.low_activation_non_dominance(),
        "legitimate_termination": legitimate_termination(),
        "long_horizon_and_reconstruction": v1.long_horizon_and_reconstruction(),
        "reactivation_existing_machinery": v1.reactivation_existing_machinery(),
        "suppressed_concern_scope_control": v1.suppressed_concern_scope_control(),
        "prospective_interaction": v1.prospective_interaction(),
        "unrelated_state_isolation": v1.unrelated_state_isolation(),
        "schema_and_mechanism_invariance": v1.schema_and_mechanism_invariance(),
        "causal_ablations": v1.causal_ablations(),
        "historical_contract": historical_contract(),
    }
    failures = [name for name, row in sections.items() if not row["passed"]]
    return {
        "experiment": "EXP-009 unresolved concern existence versus activation",
        "phase": "corrected development matched evaluation before reviewer holdouts",
        "production_commit": "b5cc3e109ab2fa4de0421dc113009d1ee7fb050d",
        "production_changes_since_failed_development_run": False,
        "frozen_champion": "v9.1_compact",
        "frozen_commit": "2856ec6a32be0347a9243f6eff6faa404a9a0e6c",
        "challenger": "exp009_unresolved_concern_persistence_candidate",
        "new_persistent_fields": 0,
        "new_counted_mechanisms": 0,
        "preserved_prior_harness_failure_run": 35136991980,
        "sections": sections,
        "failures": failures,
        "developer_gate": not failures,
    }


def compact(value):
    if isinstance(value, dict):
        return {key: compact(val) for key, val in value.items() if key not in {"trace", "traces"}}
    if isinstance(value, list):
        return [compact(val) for val in value]
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    report = run()
    encoded = json.dumps(compact(report), indent=2, sort_keys=True)
    print(encoded)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(encoded + "\n", encoding="utf-8")
    raise SystemExit(0 if report["developer_gate"] else 2)


if __name__ == "__main__":
    main()
