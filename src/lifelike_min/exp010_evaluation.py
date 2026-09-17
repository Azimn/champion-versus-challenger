from __future__ import annotations

import argparse
import json
from pathlib import Path

from .exp007_evaluation import development_suite, renderer_invariance
from .exp009_challenger import UnresolvedConcernPersistenceCharacter
from .exp010_challenger import CapacityThreeConcernCharacter
from .global_ablation_v9 import base_need_roles, earned_suite
from .runtime import Event
from .v9_1_compact import V91CompactCharacter

FROZEN_CHAMPION = "v9.2_unresolved_concern_persistence"
FROZEN_CHAMPION_COMMIT = "bd1ca22ca58e82012f1a8237e3de4bfee4dbf59d"
EVALUATED_PRODUCTION_COMMIT = "b5cc3e109ab2fa4de0421dc113009d1ee7fb050d"
PREREGISTRATION_COMMIT = "bcf8a038bae8e69040f41be173626d098f0ea720"
CHALLENGER_PRODUCTION_COMMIT = "03baf6bc6f06d3f298701a8ce66c44e00f509d50"


class CapacityTwoAblation(CapacityThreeConcernCharacter):
    max_concerns = 2


class CapacityFourDiagnostic(CapacityThreeConcernCharacter):
    max_concerns = 4


def assign(agent, name: str, intensity: float) -> str:
    return agent.step(Event(kind="task_assign", concern=name, intensity=intensity, forced_action="idle"))


def cancel(agent, name: str) -> str:
    return agent.step(Event(kind="task_cancel", concern=name, forced_action="idle"))


def target_trace(factory) -> dict:
    agent = factory()
    rows = []

    def capture(label: str) -> None:
        rows.append({
            "label": label,
            "concerns": dict(agent.concerns),
            "active": agent.active_concern,
            "strength": agent.concern_strength,
            "canonical": agent.serialize_persistent(),
        })

    assign(agent, "A", 0.5)
    capture("after_A")
    assign(agent, "B", 1.0)
    capture("after_B")
    assign(agent, "C", 0.9)
    capture("after_C")
    cancel(agent, "B")
    capture("after_B_cancel")
    cancel(agent, "C")
    capture("after_C_cancel")

    suppressed = rows[2]
    final = rows[-1]
    return {
        "rows": rows,
        "a_retained_under_competition": "A" in suppressed["concerns"],
        "a_non_dominant_under_competition": suppressed["active"] != "A",
        "a_returns": final["active"] == "A" and "A" in final["concerns"],
        "passed": (
            "A" in suppressed["concerns"]
            and suppressed["active"] == "B"
            and final["active"] == "A"
            and set(final["concerns"]) == {"A"}
        ),
    }


def non_dominance() -> dict:
    left = CapacityThreeConcernCharacter()
    right = CapacityThreeConcernCharacter()
    # Match every state variable except the extra weak unresolved identity.
    left.concerns = {"A": 0.30, "B": 0.75, "C": 0.67}
    right.concerns = {"B": 0.75, "C": 0.67}
    left._sync_active_concern()
    right._sync_active_concern()
    event = Event(kind="neutral", available_actions=("work", "rest", "idle"))
    left_action = left.step(event)
    right_action = right.step(event)
    return {
        "passed": (
            left.active_concern == right.active_concern
            and abs(left.concern_strength - right.concern_strength) < 1e-12
            and left_action == right_action
        ),
        "with_suppressed_A": {
            "active": left.active_concern,
            "strength": left.concern_strength,
            "action": left_action,
            "concerns": dict(left.concerns),
        },
        "without_A": {
            "active": right.active_concern,
            "strength": right.concern_strength,
            "action": right_action,
            "concerns": dict(right.concerns),
        },
    }


def termination_order() -> dict:
    rows = {}
    for order in (("B", "C"), ("C", "B")):
        agent = CapacityThreeConcernCharacter()
        assign(agent, "A", 0.5)
        assign(agent, "B", 1.0)
        assign(agent, "C", 0.9)
        first_active = agent.active_concern
        cancel(agent, order[0])
        after_first = agent.active_concern
        cancel(agent, order[1])
        after_second = agent.active_concern
        rows["-then-".join(order)] = {
            "first_active": first_active,
            "after_first": after_first,
            "after_second": after_second,
            "final": dict(agent.concerns),
        }
    return {
        "passed": all(row["after_second"] == "A" and set(row["final"]) == {"A"} for row in rows.values()),
        "rows": rows,
    }


def long_duration() -> dict:
    rows = {}
    for delay in (10, 100, 1000):
        agent = CapacityThreeConcernCharacter()
        assign(agent, "A", 0.5)
        assign(agent, "B", 1.0)
        assign(agent, "C", 0.9)
        for _ in range(delay):
            agent.step(Event(kind="neutral", forced_action="idle"))
        before = dict(agent.concerns)
        cancel(agent, "B")
        cancel(agent, "C")
        rows[str(delay)] = {
            "before_resolution": before,
            "a_strength_before_resolution": before.get("A"),
            "final": dict(agent.concerns),
            "active": agent.active_concern,
            "passed": "A" in before and agent.active_concern == "A",
        }
    return {"passed": all(row["passed"] for row in rows.values()), "rows": rows}


def capacity_overflow() -> dict:
    rows = {}
    for count in (3, 4, 5, 8):
        agent = CapacityThreeConcernCharacter()
        for index in range(count):
            # Increasing strength ensures later entries can displace earlier weak ones.
            assign(agent, f"c{index}", 0.35 + 0.08 * index)
        rows[str(count)] = {
            "count": len(agent.concerns),
            "keys": list(agent.concerns),
            "bounded": len(agent.concerns) <= 3,
        }
    return {
        "passed": all(row["bounded"] for row in rows.values()) and rows["3"]["count"] == 3,
        "rows": rows,
        "interpretation": "EXP-010 moves the explicit bounded-loss frontier from the third simultaneous unresolved identity to the fourth; it does not create an archive.",
    }


def capacity_tournament() -> dict:
    rows = {}
    for capacity, factory in (
        (2, CapacityTwoAblation),
        (3, CapacityThreeConcernCharacter),
        (4, CapacityFourDiagnostic),
    ):
        result = target_trace(factory)
        agent = factory()
        assign(agent, "A", 0.5)
        assign(agent, "B", 1.0)
        assign(agent, "C", 0.9)
        rows[str(capacity)] = {
            "target_passed": result["passed"],
            "mechanism_count": agent.mechanism_count(),
            "canonical_bytes_three_concerns": len(agent.serialize_persistent().encode("utf-8")),
            "diagnostic_bytes_three_concerns": agent.persistent_state_bytes(),
            "concerns": dict(agent.concerns),
        }
    return {
        "passed": (not rows["2"]["target_passed"] and rows["3"]["target_passed"] and rows["4"]["target_passed"]),
        "smallest_successful_capacity": 3 if rows["3"]["target_passed"] else None,
        "rows": rows,
    }


def cancel_while_suppressed() -> dict:
    agent = CapacityThreeConcernCharacter()
    assign(agent, "A", 0.5)
    assign(agent, "B", 1.0)
    assign(agent, "C", 0.9)
    suppressed_before = agent.active_concern != "A" and "A" in agent.concerns
    cancel(agent, "A")
    after_cancel = dict(agent.concerns)
    cancel(agent, "B")
    cancel(agent, "C")
    return {
        "passed": suppressed_before and "A" not in after_cancel and "A" not in agent.concerns,
        "after_cancel": after_cancel,
        "final": dict(agent.concerns),
    }


def work_semantics() -> dict:
    agent = CapacityThreeConcernCharacter()
    assign(agent, "A", 0.5)
    assign(agent, "B", 1.0)
    assign(agent, "C", 0.9)
    before = dict(agent.concerns)
    active_before = agent.active_concern
    agent.step(Event(kind="neutral", forced_action="work"))
    after = dict(agent.concerns)
    return {
        "passed": active_before == "B" and after.get("A") is not None and after.get("B", 0.0) < before["B"],
        "active_before": active_before,
        "before": before,
        "after": after,
        "interpretation": "Existing work semantics operate on the current active concern. No hidden target is invented to complete a suppressed concern.",
    }


def reassign_while_suppressed() -> dict:
    agent = CapacityThreeConcernCharacter()
    assign(agent, "A", 0.5)
    assign(agent, "B", 1.0)
    assign(agent, "C", 0.9)
    before = agent.concerns["A"]
    assign(agent, "A", 0.5)
    after = agent.concerns["A"]
    return {
        "passed": len(agent.concerns) == 3 and after >= before and list(agent.concerns).count("A") == 1,
        "before": before,
        "after": after,
        "active": agent.active_concern,
        "concerns": dict(agent.concerns),
    }


def prospective_overlap() -> dict:
    agent = CapacityThreeConcernCharacter()
    assign(agent, "A", 0.5)
    agent.step(Event(kind="future_commitment", concern="A", context="later", forced_action="idle"))
    coexist = "A" in agent.concerns and agent.prospective_commitments.get("A") == "later"
    agent.step(Event(kind="neutral", context="later", forced_action="idle"))
    return {
        "passed": coexist and "A" in agent.concerns and "A" not in agent.prospective_commitments,
        "coexist_before": coexist,
        "concerns_after": dict(agent.concerns),
        "prospective_after": dict(agent.prospective_commitments),
    }


def roundtrip(agent: CapacityThreeConcernCharacter) -> bool:
    encoded = agent.serialize_persistent()
    restored = CapacityThreeConcernCharacter.from_persistent_json(encoded)
    return restored.persistent_snapshot() == agent.persistent_snapshot()


def reconstruction_states() -> dict:
    probes = {}

    active = CapacityThreeConcernCharacter()
    assign(active, "A", 1.0)
    probes["active"] = roundtrip(active)

    suppressed = CapacityThreeConcernCharacter()
    assign(suppressed, "A", 0.5)
    assign(suppressed, "B", 1.0)
    assign(suppressed, "C", 0.9)
    suppressed_ok = roundtrip(suppressed)
    restored = CapacityThreeConcernCharacter.from_persistent_json(suppressed.serialize_persistent())
    suppressed_ok = suppressed_ok and restored.active_concern == "B" and "A" in restored.concerns
    probes["suppressed"] = suppressed_ok

    returned = restored
    cancel(returned, "B")
    cancel(returned, "C")
    probes["returned"] = returned.active_concern == "A" and roundtrip(returned)

    resolved = CapacityThreeConcernCharacter.from_persistent_json(returned.serialize_persistent())
    # Existing work-mediated completion may require multiple work actions for a weak concern.
    for _ in range(4):
        if "A" not in resolved.concerns:
            break
        resolved.step(Event(kind="neutral", forced_action="work"))
    probes["resolved"] = "A" not in resolved.concerns and roundtrip(resolved)

    cancelled = CapacityThreeConcernCharacter()
    assign(cancelled, "A", 0.5)
    cancel(cancelled, "A")
    probes["cancelled"] = "A" not in cancelled.concerns and roundtrip(cancelled)

    return {"passed": all(probes.values()), "probes": probes}


def repeated_cycles() -> dict:
    agent = CapacityThreeConcernCharacter()
    rows = []
    passed = True
    for cycle in range(5):
        assign(agent, "A", 0.5)
        assign(agent, f"B{cycle}", 1.0)
        assign(agent, f"C{cycle}", 0.9)
        suppressed = "A" in agent.concerns and agent.active_concern != "A"
        cancel(agent, f"B{cycle}")
        cancel(agent, f"C{cycle}")
        returned = agent.active_concern == "A"
        rows.append({"cycle": cycle, "suppressed": suppressed, "returned": returned, "concerns": dict(agent.concerns)})
        passed = passed and suppressed and returned
    return {"passed": passed, "rows": rows}


def exp009_semantics() -> dict:
    agent = CapacityThreeConcernCharacter()
    assign(agent, "unfinished", 1.0)
    for _ in range(500):
        agent.step(Event(kind="neutral", forced_action="idle"))
    persists = "unfinished" in agent.concerns and agent.concerns["unfinished"] < 0.75
    cancel(agent, "unfinished")
    cancelled = "unfinished" not in agent.concerns

    worker = CapacityThreeConcernCharacter()
    assign(worker, "work_item", 1.0)
    for _ in range(4):
        if "work_item" not in worker.concerns:
            break
        worker.step(Event(kind="neutral", forced_action="work"))
    resolved = "work_item" not in worker.concerns
    return {"passed": persists and cancelled and resolved, "persists": persists, "cancelled": cancelled, "resolved": resolved}


def structural_invariants() -> dict:
    champion = UnresolvedConcernPersistenceCharacter()
    challenger = CapacityThreeConcernCharacter()
    champion_keys = set(champion.persistent_snapshot())
    challenger_keys = set(challenger.persistent_snapshot())
    return {
        "passed": (
            champion_keys == challenger_keys
            and set(champion.__dict__) == set(challenger.__dict__)
            and champion.mechanism_count() == challenger.mechanism_count() == 11
            and challenger.max_concerns == 3
            and challenger.max_prospective == champion.max_prospective == 2
            and challenger.max_eligibility_records == champion.max_eligibility_records == 2
        ),
        "mechanism_count": challenger.mechanism_count(),
        "persistent_keys_equal": champion_keys == challenger_keys,
        "instance_fields_equal": set(champion.__dict__) == set(challenger.__dict__),
        "capacities": {
            "champion_concerns": champion.max_concerns,
            "challenger_concerns": challenger.max_concerns,
            "prospective": challenger.max_prospective,
            "eligibility": challenger.max_eligibility_records,
        },
    }


def historical_contract() -> dict:
    earned = earned_suite(CapacityThreeConcernCharacter)
    exp007 = development_suite(CapacityThreeConcernCharacter)
    renderer = renderer_invariance(CapacityThreeConcernCharacter)
    needs = base_need_roles(CapacityThreeConcernCharacter)
    exp007_failures = [name for name, row in exp007.items() if not row["passed"]]
    base_need_passed = all(needs[key] for key in (
        "fatigue_drives_rest",
        "affiliation_drives_unscripted_social_approach",
        "competence_drives_work_after_rest",
    ))
    return {
        "passed": earned["passed"] and not exp007_failures and renderer["passed"] and base_need_passed,
        "earned_failures": earned.get("failures", []),
        "exp007_development_failures": exp007_failures,
        "renderer_passed": renderer["passed"],
        "base_needs_passed": base_need_passed,
    }


def causal_ablation() -> dict:
    champion = target_trace(UnresolvedConcernPersistenceCharacter)
    ablated = target_trace(CapacityTwoAblation)
    challenger = target_trace(CapacityThreeConcernCharacter)
    return {
        "passed": not champion["passed"] and not ablated["passed"] and challenger["passed"],
        "frozen_v9_2_target_passed": champion["passed"],
        "capacity_two_ablation_target_passed": ablated["passed"],
        "capacity_three_target_passed": challenger["passed"],
    }


def run() -> dict:
    sections = {
        "target": {
            "champion": target_trace(UnresolvedConcernPersistenceCharacter),
            "challenger": target_trace(CapacityThreeConcernCharacter),
        },
        "non_dominance": non_dominance(),
        "termination_order": termination_order(),
        "long_duration": long_duration(),
        "capacity_overflow": capacity_overflow(),
        "capacity_tournament": capacity_tournament(),
        "cancel_while_suppressed": cancel_while_suppressed(),
        "work_semantics": work_semantics(),
        "reassign_while_suppressed": reassign_while_suppressed(),
        "prospective_overlap": prospective_overlap(),
        "reconstruction": reconstruction_states(),
        "repeated_cycles": repeated_cycles(),
        "exp009_semantics": exp009_semantics(),
        "structural_invariants": structural_invariants(),
        "historical_contract": historical_contract(),
        "causal_ablation": causal_ablation(),
    }
    failures = []
    if sections["target"]["champion"]["passed"]:
        failures.append("frozen_target_not_reproduced")
    if not sections["target"]["challenger"]["passed"]:
        failures.append("challenger_target")
    for name, row in sections.items():
        if name == "target":
            continue
        if not row["passed"]:
            failures.append(name)
    return {
        "experiment": "EXP-010 minimum-information suppression versus deletion",
        "phase": "development matched evaluation before reviewer holdouts",
        "frozen_champion": FROZEN_CHAMPION,
        "frozen_champion_commit": FROZEN_CHAMPION_COMMIT,
        "evaluated_production_commit": EVALUATED_PRODUCTION_COMMIT,
        "preregistration_commit": PREREGISTRATION_COMMIT,
        "challenger_production_commit": CHALLENGER_PRODUCTION_COMMIT,
        "challenger": CapacityThreeConcernCharacter.experimental_version,
        "selected_mutation": "existing concern capacity 2 -> 3 only",
        "new_persistent_fields": 0,
        "new_counted_mechanisms": 0,
        "sections": sections,
        "failures": failures,
        "developer_gate": not failures,
    }


def compact(value):
    if isinstance(value, dict):
        return {key: compact(item) for key, item in value.items() if key not in {"canonical"}}
    if isinstance(value, list):
        return [compact(item) for item in value]
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
