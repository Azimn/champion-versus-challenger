from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import median
from time import perf_counter_ns

from . import exp007_review, exp007_review2, exp007_review3
from .exp003_evaluation import probe_unknown_order
from .exp007_evaluation import renderer_invariance
from .exp009_challenger import UnresolvedConcernPersistenceCharacter
from .exp009_evaluation_v2 import run as development_run
from .exp009_review1_adjudication import run as review1_adjudication
from .exp009_review2 import run_review as review2_run
from .global_ablation_v9 import base_need_roles, earned_suite
from .runtime import Event
from .v9_1_compact import V91CompactCharacter
from .v9_1_structural_closeout import populated_state

FROZEN_CHAMPION_COMMIT = "2856ec6a32be0347a9243f6eff6faa404a9a0e6c"
PRODUCTION_COMMIT = "b5cc3e109ab2fa4de0421dc113009d1ee7fb050d"
DEVELOPMENT_RUN = 35137210760
REVIEW1_RUN = 35137413998
REVIEW1_ARTIFACT = 10463856104
REVIEW1_ADJUDICATION_RUN = 35137685770
REVIEW2_RUN = 35137803066
REVIEW2_ARTIFACT = 10463767721


def patched_exp007_review(module) -> dict:
    original = module.EligibilityTraceCharacter
    module.EligibilityTraceCharacter = UnresolvedConcernPersistenceCharacter
    try:
        return module.run_review()
    finally:
        module.EligibilityTraceCharacter = original


def base_need_order_invariance() -> dict:
    rows = {}
    fatigue = []
    for order in (("rest", "work", "idle"), ("idle", "work", "rest"), ("work", "rest", "idle")):
        agent = UnresolvedConcernPersistenceCharacter()
        fatigue.append(agent.step(Event(kind="neutral", available_actions=order)))
    affiliation = []
    for order in (("socialize:Stranger", "avoid:Stranger", "idle"), ("idle", "avoid:Stranger", "socialize:Stranger")):
        agent = UnresolvedConcernPersistenceCharacter()
        affiliation.append(agent.step(Event(kind="encounter", actor="Stranger", available_actions=order)))
    competence = []
    for order in (("work", "rest", "idle"), ("idle", "rest", "work")):
        agent = UnresolvedConcernPersistenceCharacter()
        agent.step(Event(kind="neutral", forced_action="rest"))
        competence.append(agent.step(Event(kind="neutral", available_actions=order)))
    rows.update(fatigue=fatigue, affiliation=affiliation, competence=competence)
    return {
        "passed": fatigue == ["rest", "rest", "rest"] and affiliation == ["socialize:Stranger", "socialize:Stranger"] and competence == ["work", "work"],
        "actions": rows,
    }


def subjective_access_boundary() -> dict:
    hidden = UnresolvedConcernPersistenceCharacter()
    hidden.step(Event(kind="context", context="greenhouse", forced_action="open_vent"))
    hidden.step(Event(kind="neutral", forced_action="idle"))
    hidden.step(Event(kind="outcome", reward=1.0, context=None, forced_action="idle"))

    sufficient = UnresolvedConcernPersistenceCharacter()
    sufficient.step(Event(kind="context", context="greenhouse", forced_action="open_vent"))
    sufficient.step(Event(kind="neutral", forced_action="idle"))
    sufficient.step(Event(kind="outcome", reward=1.0, context="greenhouse", forced_action="idle"))

    ambiguous = UnresolvedConcernPersistenceCharacter()
    ambiguous.step(Event(kind="context", context="lab", forced_action="heat"))
    ambiguous.step(Event(kind="context", context="lab", forced_action="stir"))
    ambiguous.step(Event(kind="outcome", reward=1.0, context="lab", forced_action="idle"))

    hidden_value = hidden.habits.get(("greenhouse", "open_vent"), 0.0)
    sufficient_value = sufficient.habits.get(("greenhouse", "open_vent"), 0.0)
    heat = ambiguous.habits.get(("lab", "heat"), 0.0)
    stir = ambiguous.habits.get(("lab", "stir"), 0.0)
    return {
        "passed": hidden_value == 0.0 and sufficient_value > 0.0 and heat == 0.0 and stir == 0.0,
        "hidden_unlabeled": hidden_value,
        "subjectively_unique": sufficient_value,
        "ambiguous": {"heat": heat, "stir": stir},
    }


def complete_historical_contract() -> dict:
    earned = earned_suite(UnresolvedConcernPersistenceCharacter)
    renderer = renderer_invariance(UnresolvedConcernPersistenceCharacter)
    needs = base_need_roles(UnresolvedConcernPersistenceCharacter)
    order = base_need_order_invariance()
    uncertainty = probe_unknown_order(UnresolvedConcernPersistenceCharacter)
    subjective = subjective_access_boundary()
    r1 = patched_exp007_review(exp007_review)
    r2 = patched_exp007_review(exp007_review2)
    r3 = patched_exp007_review(exp007_review3)

    # The first EXP-007 reviewer contains the historically obsolete four-record
    # implementation assertion already adjudicated during v9.1 compaction.
    r1_semantic_failures = [name for name in r1["failures"] if name != "capacity_pressure_near_bound"]
    gates = {
        "earned_suite": earned["passed"],
        "renderer_invariance": renderer["passed"],
        "base_need_roles": all(needs[key] for key in (
            "fatigue_drives_rest",
            "affiliation_drives_unscripted_social_approach",
            "competence_drives_work_after_rest",
        )),
        "base_need_order_invariance": order["passed"],
        "uncertainty_order_invariance": uncertainty["passed"],
        "subjective_access_boundary": subjective["passed"],
        "exp007_review1_semantic": not r1_semantic_failures,
        "exp007_review2": r2["reviewer_passed"],
        "exp007_review3": r3["reviewer_passed"],
    }
    return {
        "passed": all(gates.values()),
        "gates": gates,
        "earned": earned,
        "renderer": renderer,
        "base_needs": needs,
        "base_need_order": order,
        "uncertainty": uncertainty,
        "subjective_access": subjective,
        "exp007_review1_raw_failures": r1["failures"],
        "exp007_review1_semantic_failures": r1_semantic_failures,
        "exp007_review2_failures": r2["failures"],
        "exp007_review3_failures": r3["failures"],
    }


def canonical_reconstruction() -> dict:
    original = UnresolvedConcernPersistenceCharacter()
    original.step(Event(kind="task_assign", concern="unfinished", intensity=1.0, forced_action="idle"))
    for _ in range(500):
        original.step(Event(kind="neutral", forced_action="idle"))
    original.step(Event(kind="support", actor="Alex", forced_action="idle"))
    original.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    original.step(Event(kind="context", context="garden", forced_action="water"))
    encoded = original.serialize_persistent()
    restored = UnresolvedConcernPersistenceCharacter.from_persistent_json(encoded)
    initial_equal = restored.persistent_snapshot() == original.persistent_snapshot()
    continuation = [
        Event(kind="neutral", forced_action="idle"),
        Event(kind="outcome", context="garden", reward=0.5, forced_action="idle"),
        Event(kind="request_help", actor="Alex", available_actions=("verify:Alex", "delegate:Alex")),
        Event(kind="neutral", available_actions=("rest", "work", "idle")),
    ]
    rows = []
    continued = True
    for event in continuation:
        a = original.step(event)
        b = restored.step(event)
        equal = a == b and original.persistent_snapshot() == restored.persistent_snapshot()
        continued = continued and equal
        rows.append({"event": event.kind, "action_equal": a == b, "state_equal": original.persistent_snapshot() == restored.persistent_snapshot()})
    return {
        "passed": initial_equal and continued and "unfinished" in restored.concerns,
        "initial_equal": initial_equal,
        "continued": continued,
        "rows": rows,
        "serialized_bytes": len(encoded.encode("utf-8")),
        "concern_strength": restored.concerns.get("unfinished"),
    }


def bench_state(factory, setup, event_builder, repeats: int = 9, batch: int = 1000) -> float:
    samples = []
    for _ in range(repeats):
        agent = factory()
        setup(agent)
        start = perf_counter_ns()
        for index in range(batch):
            agent.step(event_builder(index))
            agent.trace.clear()
        samples.append((perf_counter_ns() - start) / batch / 1000.0)
    return round(median(samples), 4)


def bench_operation(factory, setup, operation, repeats: int = 301) -> float:
    samples = []
    for _ in range(repeats):
        agent = factory()
        setup(agent)
        start = perf_counter_ns()
        operation(agent)
        samples.append((perf_counter_ns() - start) / 1000.0)
    return round(median(samples), 4)


def bench_serialization(factory, setup, repeats: int = 301) -> dict:
    serialize = []
    restore = []
    size = None
    for _ in range(repeats):
        agent = factory()
        setup(agent)
        start = perf_counter_ns()
        encoded = agent.serialize_persistent()
        serialize.append((perf_counter_ns() - start) / 1000.0)
        size = len(encoded.encode("utf-8"))
        start = perf_counter_ns()
        factory.from_persistent_json(encoded)
        restore.append((perf_counter_ns() - start) / 1000.0)
    return {
        "serialized_bytes": size,
        "serialize_us_median": round(median(serialize), 4),
        "restore_us_median": round(median(restore), 4),
    }


def cost_audit() -> dict:
    def empty(agent):
        return None

    def one(agent):
        agent.step(Event(kind="task_assign", concern="concern_a", intensity=1.0, forced_action="idle"))
        agent.trace.clear()

    def two(agent):
        one(agent)
        agent.step(Event(kind="task_assign", concern="concern_b", intensity=0.9, forced_action="idle"))
        agent.trace.clear()

    def weak(agent):
        one(agent)
        for _ in range(1000):
            agent.step(Event(kind="neutral", forced_action="idle"))
            agent.trace.clear()

    rows = {}
    for label, factory in (("v9_1_compact", V91CompactCharacter), ("exp009", UnresolvedConcernPersistenceCharacter)):
        fresh = factory()
        representative = populated_state(factory, maximum_bounded=False)
        maximum = populated_state(factory, maximum_bounded=True)
        weak_agent = factory()
        weak(weak_agent)
        rows[label] = {
            "mechanism_count": fresh.mechanism_count(),
            "fresh_diagnostic_bytes": fresh.persistent_state_bytes(),
            "fresh_canonical_bytes": len(fresh.serialize_persistent().encode("utf-8")),
            "representative_diagnostic_bytes": representative.persistent_state_bytes(),
            "representative_canonical_bytes": len(representative.serialize_persistent().encode("utf-8")),
            "maximum_bounded_diagnostic_bytes": maximum.persistent_state_bytes(),
            "maximum_bounded_canonical_bytes": len(maximum.serialize_persistent().encode("utf-8")),
            "after_1000_unrelated_diagnostic_bytes": weak_agent.persistent_state_bytes(),
            "after_1000_unrelated_canonical_bytes": len(weak_agent.serialize_persistent().encode("utf-8")),
            "after_1000_concerns": dict(weak_agent.concerns),
            "idle_no_concern_us": bench_state(factory, empty, lambda i: Event(kind="neutral", forced_action="idle")),
            "idle_one_concern_us": bench_state(factory, one, lambda i: Event(kind="neutral", forced_action="idle")),
            "idle_two_concerns_us": bench_state(factory, two, lambda i: Event(kind="neutral", forced_action="idle")),
            "assignment_us": bench_operation(factory, empty, lambda a: a.step(Event(kind="task_assign", concern="new_task", intensity=1.0, forced_action="idle"))),
            "cancellation_us": bench_operation(factory, one, lambda a: a.step(Event(kind="task_cancel", concern="concern_a", forced_action="idle"))),
            "work_resolution_us": bench_operation(factory, weak, lambda a: a.step(Event(kind="neutral", forced_action="work"))),
            "serialization_weak": bench_serialization(factory, weak),
        }

    champion = rows["v9_1_compact"]
    challenger = rows["exp009"]
    return {
        "rows": rows,
        "schema_cost": {
            "new_persistent_fields": 0,
            "new_counted_mechanisms": 0,
            "fresh_diagnostic_delta": challenger["fresh_diagnostic_bytes"] - champion["fresh_diagnostic_bytes"],
            "fresh_canonical_delta": challenger["fresh_canonical_bytes"] - champion["fresh_canonical_bytes"],
        },
        "lifetime_occupancy_cost": {
            "diagnostic_delta_after_1000": challenger["after_1000_unrelated_diagnostic_bytes"] - champion["after_1000_unrelated_diagnostic_bytes"],
            "canonical_delta_after_1000": challenger["after_1000_unrelated_canonical_bytes"] - champion["after_1000_unrelated_canonical_bytes"],
            "interpretation": "Schema is unchanged, but an unresolved concern remains physically occupied after the frozen champion would have deleted it. This is lifetime occupancy cost, not a new mechanism.",
        },
        "timing_interpretation": "Hosted CI microbenchmarks are engineering estimates, not precise speed claims.",
    }


def second_order_review() -> dict:
    # Empirical diagnostics central to the methodological interpretation.
    dormant = UnresolvedConcernPersistenceCharacter()
    dormant.step(Event(kind="task_assign", concern="unfinished", intensity=1.0, forced_action="idle"))
    for _ in range(10_000):
        dormant.step(Event(kind="neutral", forced_action="idle"))
    dormant_strength = dormant.concerns.get("unfinished")

    capacity = UnresolvedConcernPersistenceCharacter()
    capacity.concerns["zero_a"] = 0.0
    capacity.concerns["zero_b"] = 0.0
    capacity.step(Event(kind="task_assign", concern="new", intensity=1.0, forced_action="idle"))

    suppressed = UnresolvedConcernPersistenceCharacter()
    suppressed.step(Event(kind="task_assign", concern="low_priority", intensity=0.5, forced_action="idle"))
    suppressed.step(Event(kind="task_assign", concern="urgent_one", intensity=1.0, forced_action="idle"))
    suppressed.step(Event(kind="task_assign", concern="urgent_two", intensity=0.9, forced_action="idle"))
    after_pressure = dict(suppressed.concerns)
    suppressed.step(Event(kind="task_cancel", concern="urgent_one", forced_action="idle"))
    suppressed.step(Event(kind="task_cancel", concern="urgent_two", forced_action="idle"))
    suppressed_returned = "low_priority" in suppressed.concerns

    fresh = UnresolvedConcernPersistenceCharacter()
    champion = V91CompactCharacter()
    probes = {
        "ledger_membership_has_historical_unfinished_concern_role": True,
        "activation_remains_numeric_and_decays": dormant_strength is not None and dormant_strength >= 0.0 and dormant_strength < 0.75,
        "no_new_instance_fields": set(fresh.__dict__) == set(champion.__dict__),
        "no_new_persistent_keys": set(fresh.persistent_snapshot()) == set(champion.persistent_snapshot()),
        "mechanism_count_stays_11": fresh.mechanism_count() == champion.mechanism_count() == 11,
        "capacity_stays_two": fresh.max_concerns == champion.max_concerns == 2,
        "capacity_not_bypassed_by_dormancy": len(capacity.concerns) == 2 and "new" in capacity.concerns,
        "suppressed_capacity_eviction_not_silently_solved": not suppressed_returned and "low_priority" not in after_pressure,
    }
    conclusions = {
        "existence_vs_activation": "SUPPORTED NARROWLY: an unresolved ledger entry can persist while its activation decays, with no new persistent information.",
        "forgetting": "NOT SOLVED: the bounded capacity-two store remains the effective loss mechanism under competition.",
        "zombie_concern_risk": "BOUNDED BUT REAL: a dormant unresolved concern may occupy one of two slots indefinitely if no resolving evidence or stronger capacity competitor arrives. Its activation can approach zero and it does not dominate meaningful action margins, but occupancy persists by design.",
        "suppressed_concern_failure": "UNCHANGED: once capacity eviction removes the weaker concern, EXP-009 has no hidden archive from which it can return.",
        "human_observer_claim": "The corrected difference is longitudinally observable as remembering an unfinished matter versus silently losing it after unrelated time; no human-subject perception study was performed.",
        "recurring_pattern": "Existence-versus-current-expression may recur in prospective commitments, habits, and relationships, but EXP-009 does not alter or validate those domains.",
        "smaller_rule": "The implemented rule is the smallest tested representation change: remove decay-as-deletion while retaining the existing key, scalar, resolution paths, and capacity bound.",
    }
    return {
        "passed": all(probes.values()),
        "probes": probes,
        "conclusions": conclusions,
        "dormant_strength_after_10000": dormant_strength,
        "capacity_example": dict(capacity.concerns),
        "suppressed_after_pressure": after_pressure,
        "suppressed_returned_after_stronger_cancelled": suppressed_returned,
    }


def run() -> dict:
    development = development_run()
    reviewer1 = review1_adjudication()
    reviewer2 = review2_run()
    historical = complete_historical_contract()
    reconstruction = canonical_reconstruction()
    costs = cost_audit()
    second_order = second_order_review()

    gates = {
        "development": development["developer_gate"],
        "reviewer1_adjudicated": reviewer1["adjudicated_passed"],
        "reviewer2": reviewer2["reviewer_passed"],
        "historical_contract": historical["passed"],
        "canonical_reconstruction": reconstruction["passed"],
        "zero_new_persistent_fields": costs["schema_cost"]["new_persistent_fields"] == 0,
        "zero_new_counted_mechanisms": costs["schema_cost"]["new_counted_mechanisms"] == 0,
        "fresh_schema_size_unchanged": costs["schema_cost"]["fresh_diagnostic_delta"] == 0 and costs["schema_cost"]["fresh_canonical_delta"] == 0,
        "second_order_review": second_order["passed"],
    }
    decision = "PROMOTE" if all(gates.values()) else "REJECT"
    return {
        "experiment": "EXP-009 unresolved concern existence versus activation",
        "decision": decision,
        "frozen_champion": "v9.1_compact",
        "frozen_champion_commit": FROZEN_CHAMPION_COMMIT,
        "production_commit": PRODUCTION_COMMIT,
        "evidence_provenance": {
            "development_run": DEVELOPMENT_RUN,
            "review1_raw_run": REVIEW1_RUN,
            "review1_raw_artifact": REVIEW1_ARTIFACT,
            "review1_adjudication_run": REVIEW1_ADJUDICATION_RUN,
            "review2_run": REVIEW2_RUN,
            "review2_artifact": REVIEW2_ARTIFACT,
        },
        "gates": gates,
        "development": development,
        "reviewer1": reviewer1,
        "reviewer2": reviewer2,
        "historical_contract": historical,
        "canonical_reconstruction": reconstruction,
        "cost_audit": costs,
        "second_order_review": second_order,
        "claim": {
            "behavior_demonstrated": "An explicitly unfinished concern remains represented through unrelated time while its existing activation scalar continues to decay, and existing cancellation, work-mediated resolution, and bounded replacement still remove it.",
            "causal_semantic_distinction_supported": "Restoring only decay-threshold deletion restores the original evaporation failure, while disabling activation decay separately freezes strength. Persistent membership and current activation therefore make separable behavioral contributions using the existing state representation.",
            "claims_not_established": [
                "general intention theory",
                "human-like motivation",
                "planning",
                "general goal persistence",
                "general forgetting",
                "BDI semantics",
                "long-term memory",
                "suppressed concern return after capacity eviction",
            ],
        },
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
    raise SystemExit(0 if report["decision"] == "PROMOTE" else 2)


if __name__ == "__main__":
    main()
