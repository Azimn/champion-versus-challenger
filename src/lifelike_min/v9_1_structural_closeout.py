from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean, median, pstdev
from time import perf_counter_ns

from . import exp007_review, exp007_review2, exp007_review3
from .exp003_evaluation import probe_unknown_order
from .exp007_challenger import EligibilityRecord, EligibilityTraceCharacter
from .exp007_evaluation import development_suite, renderer_invariance
from .global_ablation_v9 import base_need_roles, earned_suite
from .runtime import Event
from .v9_1_compact import V91CompactCharacter


BEHAVIORAL_ANCESTOR = "v9_context_eligibility_trace"
BEHAVIORAL_ANCESTOR_COMMIT = "8c1e692e2b115200e3d758e481eb12576aced907"
STRUCTURAL_CANDIDATE = "v9.1_compact"
GLOBAL_ABLATION_EVIDENCE_RUN = 35027204622
GLOBAL_ABLATION_EVIDENCE_ARTIFACT = 10419708926


def habit(agent, context: str, action: str) -> float:
    return float(agent.habits.get((context, action), 0.0))


def compact_json(value):
    if isinstance(value, dict):
        return {str(k): compact_json(v) for k, v in value.items() if k not in {"trace", "traces"}}
    if isinstance(value, tuple):
        return [compact_json(v) for v in value]
    if isinstance(value, list):
        return [compact_json(v) for v in value]
    return value


def patched_exp007_review(module) -> dict:
    original = module.EligibilityTraceCharacter
    module.EligibilityTraceCharacter = V91CompactCharacter
    try:
        return module.run_review()
    finally:
        module.EligibilityTraceCharacter = original


def base_need_order_invariance() -> dict:
    rows = {}

    fatigue_actions = []
    for order in (("rest", "work", "idle"), ("idle", "work", "rest"), ("work", "rest", "idle")):
        agent = V91CompactCharacter()
        fatigue_actions.append(agent.step(Event(kind="neutral", available_actions=order)))
    rows["fatigue"] = fatigue_actions

    affiliation_actions = []
    for order in (
        ("socialize:Stranger", "avoid:Stranger", "idle"),
        ("idle", "avoid:Stranger", "socialize:Stranger"),
    ):
        agent = V91CompactCharacter()
        affiliation_actions.append(agent.step(Event(kind="encounter", actor="Stranger", available_actions=order)))
    rows["affiliation"] = affiliation_actions

    competence_actions = []
    for order in (("work", "rest", "idle"), ("idle", "rest", "work")):
        agent = V91CompactCharacter()
        agent.step(Event(kind="neutral", forced_action="rest"))
        competence_actions.append(agent.step(Event(kind="neutral", available_actions=order)))
    rows["competence"] = competence_actions

    return {
        "passed": (
            fatigue_actions == ["rest", "rest", "rest"]
            and affiliation_actions == ["socialize:Stranger", "socialize:Stranger"]
            and competence_actions == ["work", "work"]
        ),
        "actions": rows,
    }


def corrected_subjective_access_boundary() -> dict:
    hidden = V91CompactCharacter()
    hidden.step(Event(kind="context", context="greenhouse", forced_action="open_vent"))
    hidden.step(Event(kind="neutral", forced_action="idle"))
    # The simulator may know the true cause, but that hidden metadata is deliberately
    # not supplied to the organism. Temporal adjacency has also been broken.
    simulator_true_cause = {"context": "greenhouse", "action": "open_vent"}
    hidden.step(Event(kind="outcome", reward=1.0, context=None, forced_action="idle"))

    sufficient = V91CompactCharacter()
    sufficient.step(Event(kind="context", context="greenhouse", forced_action="open_vent"))
    sufficient.step(Event(kind="neutral", forced_action="idle"))
    sufficient.step(Event(kind="outcome", reward=1.0, context="greenhouse", forced_action="idle"))

    ambiguous = V91CompactCharacter()
    ambiguous.step(Event(kind="context", context="lab", forced_action="heat"))
    ambiguous.step(Event(kind="context", context="lab", forced_action="stir"))
    ambiguous.step(Event(kind="outcome", reward=1.0, context="lab", forced_action="idle"))

    hidden_value = habit(hidden, "greenhouse", "open_vent")
    sufficient_value = habit(sufficient, "greenhouse", "open_vent")
    heat = habit(ambiguous, "lab", "heat")
    stir = habit(ambiguous, "lab", "stir")
    return {
        "passed": hidden_value == 0.0 and sufficient_value > 0.0 and heat == 0.0 and stir == 0.0,
        "simulator_true_cause_not_passed_to_agent": simulator_true_cause,
        "hidden_unlabeled_value": hidden_value,
        "subjectively_unique_value": sufficient_value,
        "ambiguous_values": {"heat": heat, "stir": stir},
    }


def explicit_earned_behavior_manifest() -> dict:
    earned = earned_suite(V91CompactCharacter)
    development = development_suite(V91CompactCharacter)
    renderer = renderer_invariance(V91CompactCharacter)
    needs = base_need_roles(V91CompactCharacter)
    order = base_need_order_invariance()
    uncertainty = probe_unknown_order(V91CompactCharacter)
    subjective = corrected_subjective_access_boundary()

    review1 = patched_exp007_review(exp007_review)
    review2 = patched_exp007_review(exp007_review2)
    review3 = patched_exp007_review(exp007_review3)

    # EXP-007 review pass 1 contained one implementation-bound assertion requiring
    # four simultaneous eligibility records. EXP-007 later established capacity two
    # as the minimum earned bound. Preserve the raw failure but do not redefine it as
    # a current behavioral requirement.
    review1_semantic_failures = [
        name for name in review1["failures"]
        if name != "capacity_pressure_near_bound"
    ]
    obsolete_capacity_assertion = "capacity_pressure_near_bound" in review1["failures"]

    development_failures = [name for name, row in development.items() if not row["passed"]]
    gates = {
        "earned_suite": earned["passed"],
        "exp007_development": not development_failures,
        "renderer_invariance": renderer["passed"],
        "direct_base_needs": all(
            needs[key]
            for key in (
                "fatigue_drives_rest",
                "affiliation_drives_unscripted_social_approach",
                "competence_drives_work_after_rest",
            )
        ),
        "base_need_order_invariance": order["passed"],
        "uncertainty_order_invariance": uncertainty["passed"],
        "subjective_access_boundary": subjective["passed"],
        "exp007_review1_semantic": not review1_semantic_failures,
        "exp007_review2": review2["reviewer_passed"],
        "exp007_review3": review3["reviewer_passed"],
    }
    return {
        "passed": all(gates.values()),
        "gates": gates,
        "earned_failures": earned["failures"],
        "development_failures": development_failures,
        "review1_raw_failures": review1["failures"],
        "review1_semantic_failures": review1_semantic_failures,
        "review1_obsolete_capacity_four_assertion_preserved": obsolete_capacity_assertion,
        "review2_failures": review2["failures"],
        "review3_failures": review3["failures"],
        "base_needs": needs,
        "base_need_order": order,
        "subjective_access": subjective,
        "manifest_sections": [
            "EXP-002 through EXP-006 historical promoted regressions",
            "EXP-003 uncertainty reversal, near-neutral behavior, and person specificity",
            "EXP-004 multiple-concern ordering, cancellation, duplication, boundedness, and interruption",
            "EXP-005 prospective cancellation, wrong cues, multiple commitments, one-shot activation, and boundedness",
            "EXP-006 observation revision, hidden-change non-omniscience, entity specificity, unknown-entity abstention, and perception order",
            "EXP-007 positive/negative delays 1/3/8, cross-context isolation, ambiguity abstention, expiration, ordering invariance, and causal controls",
            "all three EXP-007 adversarial generations except the explicitly obsolete four-record implementation assertion",
            "direct fatigue, affiliation, and competence behavior with action-order permutations",
            "renderer invariance",
            "corrected subjective-access boundary",
        ],
    }


def structural_adversarial_holdouts() -> dict:
    probes = {}

    # Derived concern views through assignment, interruption, work, cancellation.
    agent = V91CompactCharacter()
    sequence = [
        Event(kind="task_assign", concern="alpha", intensity=0.5, forced_action="idle"),
        Event(kind="task_assign", concern="beta", intensity=1.0, forced_action="idle"),
        Event(kind="shock", intensity=1.0, forced_action="avoid"),
        Event(kind="neutral", available_actions=("work", "rest", "idle")),
        Event(kind="task_cancel", concern="beta", forced_action="idle"),
    ]
    rows = []
    derived_ok = True
    for event in sequence:
        action = agent.step(event)
        ledger = agent.snapshot()["concern_ledger"]
        expected_name = max(ledger, key=ledger.get) if ledger else None
        expected_strength = max(ledger.values()) if ledger else 0.0
        state = agent.snapshot()
        ok = state["active_concern"] == expected_name and abs(state["concern_strength"] - expected_strength) < 1e-6
        derived_ok = derived_ok and ok
        rows.append({"action": action, "ledger": ledger, "active": state["active_concern"], "strength": state["concern_strength"], "passed": ok})
    probes["derived_concern_views_after_transitions"] = {"passed": derived_ok, "rows": rows}

    # Immediate learning after prior delayed-credit activity.
    agent = V91CompactCharacter()
    agent.step(Event(kind="context", context="garden", forced_action="water"))
    agent.step(Event(kind="neutral", forced_action="idle"))
    agent.step(Event(kind="outcome", reward=0.8, context="garden", forced_action="idle"))
    agent.step(Event(kind="context", context="kitchen", forced_action="cook"))
    agent.step(Event(kind="outcome", reward=1.0, forced_action="idle"))
    probes["immediate_after_delayed"] = {
        "passed": habit(agent, "garden", "water") > 0.0 and habit(agent, "kitchen", "cook") == 0.35,
        "delayed": habit(agent, "garden", "water"),
        "immediate": habit(agent, "kitchen", "cook"),
    }

    # Delayed learning after immediate habit learning.
    agent = V91CompactCharacter()
    agent.step(Event(kind="context", context="morning", forced_action="walk"))
    agent.step(Event(kind="outcome", reward=1.0, forced_action="idle"))
    agent.step(Event(kind="context", context="studio", forced_action="paint"))
    agent.step(Event(kind="neutral", forced_action="idle"))
    agent.step(Event(kind="outcome", reward=-0.7, context="studio", forced_action="idle"))
    probes["delayed_after_immediate"] = {
        "passed": habit(agent, "morning", "walk") == 0.35 and habit(agent, "studio", "paint") < 0.0,
        "immediate": habit(agent, "morning", "walk"),
        "delayed": habit(agent, "studio", "paint"),
    }

    # Prospective activation while another concern is active.
    agent = V91CompactCharacter()
    agent.step(Event(kind="task_assign", concern="finish_report", intensity=0.7, forced_action="idle"))
    agent.step(Event(kind="future_commitment", concern="call_morgan", context="morgan_arrives", forced_action="idle"))
    before = agent.snapshot()
    agent.step(Event(kind="neutral", context="morgan_arrives", forced_action="idle"))
    after = agent.snapshot()
    probes["prospective_activation_with_active_concern"] = {
        "passed": (
            "finish_report" in before["concern_ledger"]
            and before["prospective_commitments"].get("call_morgan") == "morgan_arrives"
            and "finish_report" in after["concern_ledger"]
            and "call_morgan" in after["concern_ledger"]
            and not after["prospective_commitments"]
        ),
        "before": before,
        "after": after,
    }

    # Same named concern active now and latent for later remains representable.
    agent = V91CompactCharacter()
    agent.step(Event(kind="task_assign", concern="report", forced_action="idle"))
    agent.step(Event(kind="future_commitment", concern="report", context="tomorrow", forced_action="idle"))
    mixed = agent.snapshot()
    probes["same_name_active_and_latent_coexist"] = {
        "passed": "report" in mixed["concern_ledger"] and mixed["prospective_commitments"].get("report") == "tomorrow",
        "state": mixed,
    }

    # Cancellation semantics remain the frozen behavior: named cancellation clears
    # both active and latent instances with that concern name.
    frozen = EligibilityTraceCharacter()
    compact = V91CompactCharacter()
    for subject in (frozen, compact):
        subject.step(Event(kind="task_assign", concern="report", forced_action="idle"))
        subject.step(Event(kind="future_commitment", concern="report", context="tomorrow", forced_action="idle"))
        subject.step(Event(kind="task_cancel", concern="report", forced_action="idle"))
    probes["mixed_mode_cancellation_matches_frozen"] = {
        "passed": (
            "report" not in frozen.snapshot()["concern_ledger"]
            and "report" not in frozen.snapshot()["prospective_commitments"]
            and "report" not in compact.snapshot()["concern_ledger"]
            and "report" not in compact.snapshot()["prospective_commitments"]
        ),
        "frozen": frozen.snapshot(),
        "compact": compact.snapshot(),
    }

    # One entity can participate independently in relationship, reliability, and location domains.
    agent = V91CompactCharacter()
    agent.step(Event(kind="support", actor="Alex", forced_action="idle"))
    agent.step(Event(kind="observed_reliable", actor="Alex", forced_action="idle"))
    agent.step(Event(kind="observe_location", actor="Alex", context="studio", forced_action="idle"))
    state = agent.snapshot()
    probes["same_entity_multiple_state_domains"] = {
        "passed": (
            state["relationships"].get("Alex", 0.0) > 0.0
            and state["partner_reliability"].get("Alex", 0.0) > 0.0
            and state["location_beliefs"].get("Alex") == "studio"
        ),
        "state": state,
    }

    # Eligibility at capacity must still support immediate learning from the newest age-zero record.
    agent = V91CompactCharacter()
    agent.step(Event(kind="context", context="older", forced_action="inspect"))
    agent.step(Event(kind="context", context="newer", forced_action="repair"))
    before = agent.snapshot()["eligibility_records"]
    agent.step(Event(kind="outcome", reward=0.5, forced_action="idle"))
    probes["trace_capacity_then_immediate_learning"] = {
        "passed": len(before) == 2 and habit(agent, "newer", "repair") == 0.175 and habit(agent, "older", "inspect") == 0.0,
        "before": before,
        "newer": habit(agent, "newer", "repair"),
        "older": habit(agent, "older", "inspect"),
    }

    # Concern store at capacity, then a prospective cue activates. The activated target
    # must survive the bound and remain behaviorally available.
    agent = V91CompactCharacter()
    agent.step(Event(kind="task_assign", concern="minor", intensity=0.4, forced_action="idle"))
    agent.step(Event(kind="task_assign", concern="major", intensity=0.8, forced_action="idle"))
    agent.step(Event(kind="future_commitment", concern="urgent_future", context="door_opens", forced_action="idle"))
    agent.step(Event(kind="neutral", context="door_opens", forced_action="idle"))
    state = agent.snapshot()
    probes["concern_capacity_then_prospective_activation"] = {
        "passed": len(state["concern_ledger"]) == 2 and "urgent_future" in state["concern_ledger"],
        "state": state,
    }

    failures = [name for name, row in probes.items() if not row["passed"]]
    return {"passed": not failures, "failures": failures, "probes": probes}


def persistent_inventory() -> dict:
    agent = V91CompactCharacter()
    agent.step(Event(kind="support", actor="Alex", forced_action="idle"))
    agent.step(Event(kind="shock", intensity=0.8, forced_action="avoid"))
    agent.step(Event(kind="task_assign", concern="report", forced_action="idle"))
    agent.step(Event(kind="future_commitment", concern="call_morgan", context="morgan_arrives", forced_action="idle"))
    agent.step(Event(kind="observed_reliable", actor="Alex", forced_action="idle"))
    agent.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    agent.step(Event(kind="context", context="morning", forced_action="walk"))

    stored = agent.__dict__
    persistent = agent.persistent_snapshot()
    fields = [
        {"name": "fatigue", "type": "float", "cardinality": "1", "created": "initialization", "updated": "per-step drift and rest action", "deleted": "never", "read_by": "rest scoring", "classification": "persistent organism state", "experiment": "base pressure re-litigation"},
        {"name": "affiliation", "type": "float", "cardinality": "1", "created": "initialization", "updated": "per-step drift and socialization", "deleted": "never", "read_by": "socialize scoring", "classification": "persistent organism state", "experiment": "base pressure re-litigation"},
        {"name": "competence", "type": "float", "cardinality": "1", "created": "initialization", "updated": "per-step drift and work", "deleted": "never", "read_by": "work scoring", "classification": "persistent organism state", "experiment": "base pressure re-litigation"},
        {"name": "relationships", "type": "dict[str,float]", "cardinality": "unbounded by current runtime", "created": "support/hostility perception", "updated": "social evidence and slow decay", "deleted": "near-zero decay", "read_by": "socialize/avoid scoring", "classification": "persistent organism state", "experiment": "EXP-002"},
        {"name": "threat_residue", "type": "float", "cardinality": "1", "created": "initialization; raised by shock/hostility", "updated": "decay", "deleted": "represented as 0.0 below threshold", "read_by": "avoid scoring", "classification": "persistent organism state", "experiment": "EXP-002 lineage affect promotion"},
        {"name": "habits", "type": "dict[(context,action),float]", "cardinality": "unbounded by current runtime", "created": "experienced outcome update", "updated": "immediate or delayed consequence", "deleted": "no deletion rule", "read_by": "contextual action scoring", "classification": "persistent organism state", "experiment": "EXP-002/EXP-007"},
        {"name": "partner_reliability", "type": "dict[str,float]", "cardinality": "unbounded by current runtime", "created": "observed reliability evidence", "updated": "reliability evidence and slow decay", "deleted": "near-zero decay", "read_by": "delegate/verify scoring and uncertainty policy", "classification": "persistent organism state", "experiment": "EXP-002/EXP-003"},
        {"name": "concerns", "type": "dict[str,float]", "cardinality": "max 2", "created": "task assignment or prospective cue activation", "updated": "decay/work", "deleted": "completion, cancellation, decay, or bounded eviction", "read_by": "derived active concern and work scoring", "classification": "persistent organism state", "experiment": "EXP-004 plus global capacity tournament"},
        {"name": "prospective_commitments", "type": "dict[str,str]", "cardinality": "max 2", "created": "future commitment", "updated": "replacement by same concern", "deleted": "cue activation, cancellation, or bounded eviction", "read_by": "cue activation", "classification": "persistent organism state", "experiment": "EXP-005 plus global capacity tournament"},
        {"name": "location_beliefs", "type": "dict[str,str]", "cardinality": "unbounded by current runtime", "created": "direct location observation", "updated": "later direct observation", "deleted": "no deletion rule", "read_by": "search scoring", "classification": "persistent organism state", "experiment": "EXP-006"},
        {"name": "eligibility_records", "type": "list[EligibilityRecord]", "cardinality": "max 2", "created": "non-idle contextual action", "updated": "age increment or repeated-pair refresh", "deleted": "age > 10 or bounded eviction", "read_by": "delayed outcome attribution and immediate age-zero attribution", "classification": "persistent organism state", "experiment": "EXP-007"},
        {"name": "active_concern", "type": "derived str|None", "cardinality": "not stored", "created": "derived from concern ledger", "updated": "recomputed on read", "deleted": "not applicable", "read_by": "diagnostic view/work policy", "classification": "derived diagnostic view", "experiment": "global structural ablation H1"},
        {"name": "concern_strength", "type": "derived float", "cardinality": "not stored", "created": "derived from concern ledger", "updated": "recomputed on read", "deleted": "not applicable", "read_by": "diagnostic view/work policy", "classification": "derived diagnostic view", "experiment": "global structural ablation H1"},
        {"name": "tick", "type": "int", "cardinality": "1", "created": "initialization", "updated": "every step", "deleted": "never", "read_by": "trace chronology only", "classification": "runtime chronology metadata, not counted cognition", "experiment": "runtime infrastructure"},
        {"name": "trace", "type": "list[dict]", "cardinality": "unbounded diagnostic history", "created": "initialization", "updated": "every step", "deleted": "not automatically", "read_by": "tests/debugging only", "classification": "test/runtime telemetry, excluded from persistent snapshot", "experiment": "test infrastructure"},
        {"name": "version", "type": "enum", "cardinality": "1", "created": "initialization", "updated": "never", "deleted": "never", "read_by": "base feature gates", "classification": "runtime configuration metadata", "experiment": "runtime infrastructure"},
    ]

    forbidden = {"active_concern", "concern_strength", "last_action", "last_context"}
    return {
        "passed": not (forbidden & set(stored)) and not ({"last_action", "last_context"} & set(persistent)),
        "object_dict_keys": sorted(stored),
        "persistent_snapshot_keys": sorted(persistent),
        "forbidden_stored_fields": sorted(forbidden),
        "fields": fields,
        "renderer_state_inside_organism": False,
        "environment_state_inside_organism": False,
    }


def mechanism_reclassification() -> dict:
    mechanisms = [
        {"name": "fatigue pressure", "state": ["fatigue"], "behavior": "rest pressure", "ablation": "direct fatigue-pressure re-litigation"},
        {"name": "affiliation pressure", "state": ["affiliation"], "behavior": "unscripted social approach", "ablation": "direct affiliation-pressure re-litigation"},
        {"name": "competence pressure", "state": ["competence"], "behavior": "work pressure", "ablation": "direct competence-pressure re-litigation and prospective-cue regression"},
        {"name": "relationship history", "state": ["relationships"], "behavior": "history-dependent social approach/avoidance", "ablation": "global removal tournament history_divergence"},
        {"name": "affect residue", "state": ["threat_residue"], "behavior": "recovery inertia", "ablation": "global removal tournament recovery_inertia"},
        {"name": "contextual habit learning", "state": ["habits"], "behavior": "experience-shaped contextual routine", "ablation": "global removal tournament habit_formation/immediate/delayed credit"},
        {"name": "partner reliability expectation", "state": ["partner_reliability"], "behavior": "partner-specific delegate/verify prediction", "ablation": "global removal tournament social_prediction/reversal/person_specificity"},
        {"name": "bounded concern persistence", "state": ["concerns"], "behavior": "unfinished and competing concerns survive interruption", "ablation": "global removal tournament multiple_concerns/unfinished_concern"},
        {"name": "prospective cue binding", "state": ["prospective_commitments"], "behavior": "latent future commitment reactivation", "ablation": "global removal tournament prospective_cue/multiple_future"},
        {"name": "subjective location fact", "state": ["location_beliefs"], "behavior": "behavior follows perceived rather than hidden world state", "ablation": "global removal tournament subjective_fact/observation revision"},
        {"name": "bounded context-action eligibility trace", "state": ["eligibility_records"], "behavior": "tested context-cued delayed consequence credit", "ablation": "EXP-007 disabled/immediate-expiry/context/action/aging ablations"},
    ]
    uncounted = [
        {"name": "uncertainty policy", "reason": "causally necessary policy over partner reliability but adds no independent persistent state"},
        {"name": "active concern/strength views", "reason": "deterministic views of concern ledger"},
        {"name": "renderer", "reason": "external presentation layer, causally invariant"},
        {"name": "tick/version/trace", "reason": "runtime/test metadata rather than cognitive mechanisms"},
    ]
    agent = V91CompactCharacter()
    return {
        "passed": agent.mechanism_count() == len(mechanisms) == 11,
        "reported_mechanism_count": agent.mechanism_count(),
        "reclassified_count": len(mechanisms),
        "counted": mechanisms,
        "uncounted_but_documented": uncounted,
    }


def reverse_ablations() -> dict:
    class ConcernCapacityOne(V91CompactCharacter):
        max_concerns = 1

    class ProspectiveCapacityOne(V91CompactCharacter):
        max_prospective = 1

    class NoConcernLedger(V91CompactCharacter):
        max_concerns = 0

    class NoEligibility(V91CompactCharacter):
        max_eligibility_records = 0

    class NoAgeZeroImmediate(V91CompactCharacter):
        def _apply_immediate_outcome(self, event: Event) -> bool:
            return False

    concern_one = earned_suite(ConcernCapacityOne)
    prospective_one = earned_suite(ProspectiveCapacityOne)
    no_concern = earned_suite(NoConcernLedger)
    no_trace = earned_suite(NoEligibility)
    no_age_zero = development_suite(NoAgeZeroImmediate)

    # Restore the old duplicate last-action learner only to show that it can recreate
    # the dead context-idle habit while leaving choice unchanged because idle scoring
    # never reads habits.
    frozen = EligibilityTraceCharacter()
    compact = V91CompactCharacter()
    for agent in (frozen, compact):
        agent.step(Event(kind="context", context="hall", forced_action="idle"))
        agent.step(Event(kind="outcome", reward=1.0, forced_action="idle"))
    choices = {}
    for label, agent in (("frozen", frozen), ("compact", compact)):
        choices[label] = [
            agent.step(Event(kind="context", context="hall", available_actions=order))
            for order in (("idle", "read"), ("read", "idle"))
        ]

    probes = {
        "concern_capacity_one_breaks_earned_behavior": {"passed": not concern_one["passed"], "failures": concern_one["failures"]},
        "prospective_capacity_one_breaks_earned_behavior": {"passed": not prospective_one["passed"], "failures": prospective_one["failures"]},
        "removing_concern_ledger_breaks_behavior": {"passed": not no_concern["passed"], "failures": no_concern["failures"]},
        "removing_trace_breaks_behavior": {"passed": not no_trace["passed"], "failures": no_trace["failures"]},
        "removing_age_zero_information_breaks_immediate_credit": {"passed": not no_age_zero["immediate_control"]["passed"], "immediate_control": no_age_zero["immediate_control"]},
        "restoring_dead_idle_habit_adds_state_not_behavior": {
            "passed": habit(frozen, "hall", "idle") == 0.35 and habit(compact, "hall", "idle") == 0.0 and choices["frozen"] == choices["compact"],
            "frozen_idle_habit": habit(frozen, "hall", "idle"),
            "compact_idle_habit": habit(compact, "hall", "idle"),
            "choices": choices,
        },
    }
    failures = [name for name, row in probes.items() if not row["passed"]]
    return {"passed": not failures, "failures": failures, "probes": probes}


def serialize_persistent(agent: V91CompactCharacter) -> str:
    return json.dumps(agent.persistent_snapshot(), sort_keys=True, separators=(",", ":"))


def restore_persistent(encoded: str) -> V91CompactCharacter:
    data = json.loads(encoded)
    agent = V91CompactCharacter()
    agent.tick = int(data["tick"])
    needs = data["needs"]
    agent.fatigue = float(needs["fatigue"])
    agent.affiliation = float(needs["affiliation"])
    agent.competence = float(needs["competence"])
    agent.relationships = {str(k): float(v) for k, v in data.get("relationships", {}).items()}
    agent.threat_residue = float(data.get("threat_residue", 0.0))
    agent.concerns = {str(k): float(v) for k, v in data.get("concern_ledger", {}).items()}
    agent.prospective_commitments = {str(k): str(v) for k, v in data.get("prospective_commitments", {}).items()}
    agent.habits = {}
    for key, value in data.get("habits", {}).items():
        context, action = key.split("|", 1)
        agent.habits[(context, action)] = float(value)
    agent.partner_reliability = {str(k): float(v) for k, v in data.get("partner_reliability", {}).items()}
    agent.location_beliefs = {str(k): str(v) for k, v in data.get("location_beliefs", {}).items()}
    agent.eligibility_records = [
        EligibilityRecord(context=str(row["context"]), action=str(row["action"]), age=int(row["age"]))
        for row in data.get("eligibility_records", [])
    ]
    return agent


def serialization_reconstruction_check() -> dict:
    original = V91CompactCharacter()
    original.step(Event(kind="support", actor="Alex", forced_action="idle"))
    original.step(Event(kind="shock", intensity=0.8, forced_action="avoid"))
    original.step(Event(kind="task_assign", concern="report", intensity=0.7, forced_action="idle"))
    original.step(Event(kind="future_commitment", concern="call_morgan", context="morgan_arrives", forced_action="idle"))
    original.step(Event(kind="observed_reliable", actor="Alex", forced_action="idle"))
    original.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    original.step(Event(kind="context", context="morning", forced_action="walk"))
    original.step(Event(kind="neutral", forced_action="idle"))
    original.step(Event(kind="outcome", reward=0.8, context="morning", forced_action="idle"))

    encoded = serialize_persistent(original)
    restored = restore_persistent(encoded)
    before_equal = original.persistent_snapshot() == restored.persistent_snapshot()

    continuation = [
        Event(kind="retrieve", actor="book", available_actions=("search:shelf", "search:drawer")),
        Event(kind="request_help", actor="Alex", available_actions=("verify:Alex", "delegate:Alex")),
        Event(kind="neutral", context="morgan_arrives", forced_action="idle"),
        Event(kind="context", context="morning", available_actions=("tea", "walk")),
    ]
    action_rows = []
    continued_equal = True
    for event in continuation:
        a = original.step(event)
        b = restored.step(event)
        same = a == b and original.persistent_snapshot() == restored.persistent_snapshot()
        continued_equal = continued_equal and same
        action_rows.append({"original": a, "restored": b, "same_state": same})

    return {
        "passed": before_equal and continued_equal,
        "serialized_bytes": len(encoded.encode("utf-8")),
        "before_equal": before_equal,
        "continuation": action_rows,
        "temporary_state_not_serialized": ["debug trace list"],
        "note": "The debug trace is intentionally diagnostic/test telemetry. Version/class configuration is restored by constructing the frozen class; all behaviorally relevant mutable state is restored from the persistent payload.",
    }


def distribution(samples: list[float]) -> dict:
    ordered = sorted(samples)
    return {
        "mean": round(mean(samples), 4),
        "median": round(median(samples), 4),
        "pstdev": round(pstdev(samples), 4),
        "min": round(ordered[0], 4),
        "max": round(ordered[-1], 4),
        "n": len(samples),
    }


def bench(factory, event_builder, repeats: int = 15, batch: int = 1800) -> dict:
    samples = []
    for _ in range(repeats):
        agent = factory()
        for _ in range(20):
            agent.step(Event(kind="neutral", forced_action="idle"))
        start = perf_counter_ns()
        for index in range(batch):
            agent.step(event_builder(index))
        samples.append((perf_counter_ns() - start) / batch / 1000.0)
    return distribution(samples)


def populated_state(factory, maximum_bounded: bool = False):
    agent = factory()
    agent.step(Event(kind="support", actor="Alex", forced_action="idle"))
    agent.step(Event(kind="shock", intensity=0.8, forced_action="avoid"))
    concern_count = agent.max_concerns if maximum_bounded else min(2, agent.max_concerns)
    prospective_count = agent.max_prospective if maximum_bounded else min(2, agent.max_prospective)
    for index in range(concern_count):
        agent.step(Event(kind="task_assign", concern=f"task_{index}", intensity=0.7 + 0.1 * index, forced_action="idle"))
    for index in range(prospective_count):
        agent.step(Event(kind="future_commitment", concern=f"future_{index}", context=f"cue_{index}", forced_action="idle"))
    agent.step(Event(kind="observed_reliable", actor="Alex", forced_action="idle"))
    agent.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    for index in range(agent.max_eligibility_records):
        agent.step(Event(kind="context", context=f"ctx_{index}", forced_action=f"act_{index}"))
    return agent


def cost_and_state_audit() -> dict:
    idle = lambda i: Event(kind="neutral", forced_action="idle")
    mixed = lambda i: (
        Event(kind="support", actor="Alex", forced_action="idle") if i % 17 == 0 else
        Event(kind="observed_reliable", actor="Alex", forced_action="idle") if i % 19 == 0 else
        Event(kind="observe_location", actor="book", context="drawer", forced_action="idle") if i % 23 == 0 else
        Event(kind="context", context="morning", forced_action="walk") if i % 11 == 0 else
        Event(kind="outcome", context="morning", reward=0.3, forced_action="idle") if i % 11 == 3 else
        Event(kind="neutral", available_actions=("work", "rest", "idle"))
    )
    event_heavy = lambda i: (
        Event(kind="task_assign", concern=f"task_{i % 2}", intensity=0.7, forced_action="idle") if i % 6 == 0 else
        Event(kind="future_commitment", concern=f"future_{i % 2}", context=f"cue_{i % 2}", forced_action="idle") if i % 6 == 1 else
        Event(kind="observed_reliable", actor="Alex", forced_action="idle") if i % 6 == 2 else
        Event(kind="observe_location", actor="book", context="drawer", forced_action="idle") if i % 6 == 3 else
        Event(kind="context", context="yard", forced_action="sweep") if i % 6 == 4 else
        Event(kind="outcome", context="yard", reward=0.2, forced_action="idle")
    )

    rows = {}
    for label, factory in (("frozen_v9", EligibilityTraceCharacter), ("v9_1_compact", V91CompactCharacter)):
        representative = populated_state(factory, maximum_bounded=False)
        maximum = populated_state(factory, maximum_bounded=True)
        rows[label] = {
            "fresh_serialized_bytes": factory().persistent_state_bytes(),
            "representative_serialized_bytes": representative.persistent_state_bytes(),
            "maximum_bounded_store_scenario_bytes": maximum.persistent_state_bytes(),
            "mechanism_count": factory().mechanism_count(),
            "bounded_capacities": {
                "concerns": factory.max_concerns,
                "prospective": factory.max_prospective,
                "eligibility": factory.max_eligibility_records,
            },
            "idle_tick_us": bench(factory, idle),
            "mixed_tick_us": bench(factory, mixed),
            "event_heavy_tick_us": bench(factory, event_heavy),
            "serialization_size_bytes": len(json.dumps(representative.persistent_snapshot() if hasattr(representative, "persistent_snapshot") else representative.snapshot(), sort_keys=True).encode("utf-8")),
        }

    frozen = rows["frozen_v9"]
    compact = rows["v9_1_compact"]
    fresh_delta = compact["fresh_serialized_bytes"] - frozen["fresh_serialized_bytes"]
    repr_delta = compact["representative_serialized_bytes"] - frozen["representative_serialized_bytes"]
    return {
        "rows": rows,
        "fresh_delta_bytes": fresh_delta,
        "fresh_reduction_percent": round((-fresh_delta / frozen["fresh_serialized_bytes"]) * 100.0, 2),
        "representative_delta_bytes": repr_delta,
        "representative_reduction_percent": round((-repr_delta / frozen["representative_serialized_bytes"]) * 100.0, 2),
        "timing_interpretation": "Hosted CI microbenchmarks are engineering estimates. Unless distributions separate consistently, the supported result is architectural/state compression rather than a speed claim.",
    }


def second_order_structural_review(inventory: dict, mechanisms: dict, manifest: dict, adversarial: dict, serialization: dict) -> dict:
    agent = V91CompactCharacter()
    stored = set(agent.__dict__)
    persistent = set(agent.persistent_snapshot())
    probes = {
        "real_state_removed_not_renamed": not ({"active_concern", "concern_strength", "last_action", "last_context"} & stored),
        "no_generic_union_hidden_state": "commitments" not in persistent and "beliefs" not in persistent,
        "semantic_stores_remain_independent": "concern_ledger" in persistent and "prospective_commitments" in persistent and "partner_reliability" in persistent and "location_beliefs" in persistent,
        "derived_views_are_not_stored": "active_concern" not in persistent and "concern_strength" not in persistent,
        "no_renderer_state": inventory["renderer_state_inside_organism"] is False,
        "no_environment_truth_store": inventory["environment_state_inside_organism"] is False,
        "mechanism_reclassification_consistent": mechanisms["passed"],
        "earned_contract_intact": manifest["passed"],
        "structural_holdouts_intact": adversarial["passed"],
        "serialization_preserves_individual": serialization["passed"],
        "smallest_earned_bounded_pair": agent.max_concerns == 2 and agent.max_prospective == 2 and agent.max_eligibility_records == 2,
    }
    failures = [name for name, passed in probes.items() if not passed]
    return {
        "passed": not failures,
        "failures": failures,
        "probes": probes,
        "conclusions": {
            "concern_prospective_union": "REJECT: representationally invalid consolidation; same-name active and latent instances must coexist.",
            "reliability_location_union": "REJECT: representationally invalid consolidation; one entity may hold both belief types simultaneously.",
            "affect_generic_temporal_record": "REJECT: increases representation from the existing scalar and retains distinct semantics.",
            "habit_update_helper": "CODE REFACTOR ONLY: removes no persistent organism information.",
            "capacity_pair": "ACCEPT 2/2: capacity one fails previously earned multiple-state behavior; capacity two and three are behaviorally equivalent under the completed meaningful suite.",
        },
    }


def run_closeout() -> dict:
    manifest = explicit_earned_behavior_manifest()
    adversarial = structural_adversarial_holdouts()
    inventory = persistent_inventory()
    mechanisms = mechanism_reclassification()
    reverse = reverse_ablations()
    serialization = serialization_reconstruction_check()
    costs = cost_and_state_audit()
    second_order = second_order_structural_review(inventory, mechanisms, manifest, adversarial, serialization)

    gates = {
        "explicit_earned_behavior_manifest": manifest["passed"],
        "structural_adversarial_review": adversarial["passed"],
        "persistent_inventory_clean": inventory["passed"],
        "mechanism_reclassification": mechanisms["passed"],
        "reverse_ablations": reverse["passed"],
        "serialization_reconstruction": serialization["passed"],
        "second_order_structural_review": second_order["passed"],
        "state_reduced": costs["fresh_delta_bytes"] < 0 and costs["representative_delta_bytes"] < 0,
        "mechanism_count_reduced": costs["rows"]["v9_1_compact"]["mechanism_count"] < costs["rows"]["frozen_v9"]["mechanism_count"],
    }
    decision = "PROMOTE" if all(gates.values()) else "REJECT"
    return {
        "phase": "GLOBAL STRUCTURAL ABLATION v9 closeout",
        "behavioral_ancestor": BEHAVIORAL_ANCESTOR,
        "behavioral_ancestor_commit": BEHAVIORAL_ANCESTOR_COMMIT,
        "candidate": STRUCTURAL_CANDIDATE,
        "completed_evidence_provenance": {
            "workflow_run": GLOBAL_ABLATION_EVIDENCE_RUN,
            "artifact": GLOBAL_ABLATION_EVIDENCE_ARTIFACT,
            "files": ["pairwise-consolidation.json", "capacity-tournament.json"],
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
        "manifest": manifest,
        "structural_adversarial": adversarial,
        "persistent_inventory": inventory,
        "mechanism_reclassification": mechanisms,
        "reverse_ablations": reverse,
        "serialization_reconstruction": serialization,
        "cost_state_audit": costs,
        "second_order_review": second_order,
        "gates": gates,
        "decision": decision,
        "behavioral_claim_change": "NONE: this is architectural compaction only.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    report = compact_json(run_closeout())
    encoded = json.dumps(report, indent=2, sort_keys=True)
    print(encoded)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(encoded + "\n", encoding="utf-8")
    raise SystemExit(0 if report["decision"] == "PROMOTE" else 2)


if __name__ == "__main__":
    main()
