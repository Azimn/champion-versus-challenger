from __future__ import annotations

import argparse
import json
from pathlib import Path

from .exp003_challenger import UncertaintyPolicyCharacter
from .exp007_evaluation import renderer_invariance
from .exp009_challenger import UnresolvedConcernPersistenceCharacter
from .global_ablation_v9 import earned_suite
from .runtime import Event
from .v9_1_compact import V91CompactCharacter


class RestoreThresholdDeletionCharacter(UnresolvedConcernPersistenceCharacter):
    """Causal ablation: restore only frozen v9.1 concern drift/deletion."""

    def _drift(self) -> None:
        V91CompactCharacter._drift(self)


class NoConcernDecayCharacter(UnresolvedConcernPersistenceCharacter):
    """Diagnostic: preserve membership and remove ordinary concern activation decay."""

    def _drift(self) -> None:
        UncertaintyPolicyCharacter._drift(self)
        self._sync_active_concern()


def assign(agent, name: str = "finish_portfolio", intensity: float = 1.0) -> float:
    agent.step(
        Event(
            kind="task_assign",
            concern=name,
            intensity=intensity,
            forced_action="idle",
        )
    )
    return float(agent.concerns[name])


def unrelated_event(kind: str, index: int = 0) -> Event:
    if kind == "social":
        return Event(kind="support", actor=f"Unrelated{index % 3}", forced_action="idle")
    if kind == "location":
        return Event(
            kind="observe_location",
            actor=f"object{index % 3}",
            context=f"place{index % 2}",
            forced_action="idle",
        )
    if kind == "reliability":
        return Event(kind="observed_reliable", actor=f"Partner{index % 3}", forced_action="idle")
    if kind == "context":
        return Event(kind="context", context=f"ctx{index % 3}", forced_action="idle")
    return Event(kind="neutral", forced_action="idle")


def run_unrelated(agent, count: int, mode: str = "neutral") -> None:
    kinds = ("neutral", "social", "location", "reliability", "context")
    for index in range(count):
        kind = kinds[index % len(kinds)] if mode == "mixed" else mode
        agent.step(unrelated_event(kind, index))


def matched_retention() -> dict:
    rows = []
    for intensity in (0.25, 0.50, 0.75, 1.00):
        champion = V91CompactCharacter()
        challenger = UnresolvedConcernPersistenceCharacter()
        c_initial = assign(champion, intensity=intensity)
        x_initial = assign(challenger, intensity=intensity)
        run_unrelated(champion, 200)
        run_unrelated(challenger, 200)
        rows.append(
            {
                "assignment_intensity": intensity,
                "champion_initial": c_initial,
                "challenger_initial": x_initial,
                "champion_present": "finish_portfolio" in champion.concerns,
                "challenger_present": "finish_portfolio" in challenger.concerns,
                "challenger_strength": challenger.concerns.get("finish_portfolio"),
                "passed": (
                    "finish_portfolio" not in champion.concerns
                    and "finish_portfolio" in challenger.concerns
                    and 0.0 <= challenger.concerns["finish_portfolio"] < x_initial
                ),
            }
        )

    exact_strength_rows = []
    for strength in (0.25, 0.50, 0.75, 1.00):
        champion = V91CompactCharacter()
        challenger = UnresolvedConcernPersistenceCharacter()
        champion.concerns["exact"] = strength
        challenger.concerns["exact"] = strength
        run_unrelated(champion, 200)
        run_unrelated(challenger, 200)
        exact_strength_rows.append(
            {
                "starting_strength": strength,
                "champion_present": "exact" in champion.concerns,
                "challenger_present": "exact" in challenger.concerns,
                "challenger_strength": challenger.concerns.get("exact"),
                "passed": "exact" not in champion.concerns and "exact" in challenger.concerns,
            }
        )
    return {
        "passed": all(row["passed"] for row in rows + exact_strength_rows),
        "assignment_intensity_rows": rows,
        "exact_starting_strength_diagnostics": exact_strength_rows,
    }


def unrelated_kind_invariance() -> dict:
    rows = []
    for kind in ("neutral", "social", "location", "reliability", "mixed"):
        agent = UnresolvedConcernPersistenceCharacter()
        initial = assign(agent)
        run_unrelated(agent, 200, kind)
        rows.append(
            {
                "history": kind,
                "present": "finish_portfolio" in agent.concerns,
                "strength": agent.concerns.get("finish_portfolio"),
                "weakened": agent.concerns.get("finish_portfolio", initial) < initial,
            }
        )
    return {
        "passed": all(row["present"] and row["weakened"] for row in rows),
        "rows": rows,
    }


def low_activation_non_dominance() -> dict:
    agent = UnresolvedConcernPersistenceCharacter()
    initial = assign(agent)
    run_unrelated(agent, 500)
    weak = float(agent.concerns["finish_portfolio"])
    threat_choice = agent.step(
        Event(
            kind="shock",
            intensity=1.0,
            available_actions=("work", "avoid", "idle"),
        )
    )

    two = UnresolvedConcernPersistenceCharacter()
    assign(two, "old_weak", 1.0)
    run_unrelated(two, 300)
    old_strength = float(two.concerns["old_weak"])
    assign(two, "urgent", 1.0)
    active = two.active_concern
    return {
        "passed": (
            weak < initial
            and threat_choice == "avoid"
            and "finish_portfolio" in agent.concerns
            and old_strength < two.concerns["urgent"]
            and active == "urgent"
            and "old_weak" in two.concerns
        ),
        "initial": initial,
        "weak_strength": weak,
        "threat_choice": threat_choice,
        "old_strength": old_strength,
        "urgent_strength": two.concerns.get("urgent"),
        "active_after_urgent": active,
    }


def legitimate_termination() -> dict:
    cancelled = UnresolvedConcernPersistenceCharacter()
    assign(cancelled, "cancel_me")
    run_unrelated(cancelled, 300)
    cancelled.step(Event(kind="task_cancel", concern="cancel_me", forced_action="idle"))

    worked = UnresolvedConcernPersistenceCharacter()
    assign(worked, "work_me")
    run_unrelated(worked, 300)
    before_work = worked.concerns.get("work_me")
    worked.step(Event(kind="neutral", forced_action="work"))

    capacity = UnresolvedConcernPersistenceCharacter()
    assign(capacity, "old_weak")
    run_unrelated(capacity, 300)
    assign(capacity, "new_strong", 1.0)
    assign(capacity, "new_second", 0.9)

    third_weaker = UnresolvedConcernPersistenceCharacter()
    assign(third_weaker, "strong_a", 1.0)
    assign(third_weaker, "strong_b", 0.9)
    assign(third_weaker, "weak_c", 0.1)

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


def long_horizon_and_reconstruction() -> dict:
    agent = UnresolvedConcernPersistenceCharacter()
    initial = assign(agent)
    run_unrelated(agent, 500, "mixed")
    midpoint = float(agent.concerns["finish_portfolio"])
    encoded_mid = agent.serialize_persistent()
    restored = UnresolvedConcernPersistenceCharacter.from_persistent_json(encoded_mid)
    midpoint_equal = restored.persistent_snapshot() == agent.persistent_snapshot()

    for _ in range(2):
        run_unrelated(restored, 250, "mixed")
        encoded = restored.serialize_persistent()
        restored = UnresolvedConcernPersistenceCharacter.from_persistent_json(encoded)

    final_strength = float(restored.concerns["finish_portfolio"])
    still_present = "finish_portfolio" in restored.concerns
    before_cancel_payload = json.loads(restored.serialize_persistent())
    restored.step(Event(kind="task_cancel", concern="finish_portfolio", forced_action="idle"))
    resolved_encoded = restored.serialize_persistent()
    resolved = UnresolvedConcernPersistenceCharacter.from_persistent_json(resolved_encoded)
    return {
        "passed": (
            midpoint_equal
            and still_present
            and 0.0 <= final_strength < midpoint < initial
            and "finish_portfolio" in before_cancel_payload["concern_ledger"]
            and "finish_portfolio" not in resolved.concerns
            and "finish_portfolio" not in json.loads(resolved_encoded)["concern_ledger"]
        ),
        "initial": initial,
        "midpoint_strength": midpoint,
        "final_strength_after_1000": final_strength,
        "midpoint_serialized_bytes": len(encoded_mid.encode("utf-8")),
        "persistent_keys": sorted(before_cancel_payload),
        "post_resolution_concerns": dict(resolved.concerns),
    }


def reactivation_existing_machinery() -> dict:
    agent = UnresolvedConcernPersistenceCharacter()
    initial = assign(agent, "return_later", 1.0)
    run_unrelated(agent, 500)
    weak = float(agent.concerns["return_later"])
    count_before = len(agent.concerns)
    agent.step(
        Event(
            kind="task_assign",
            concern="return_later",
            intensity=1.0,
            forced_action="idle",
        )
    )
    raised = float(agent.concerns["return_later"])
    return {
        "passed": weak < initial and raised > weak and raised == 0.75 and len(agent.concerns) == count_before,
        "initial": initial,
        "weak": weak,
        "raised": raised,
        "ledger": dict(agent.concerns),
    }


def suppressed_concern_scope_control() -> dict:
    agent = UnresolvedConcernPersistenceCharacter()
    agent.step(Event(kind="task_assign", concern="low_priority", intensity=0.5, forced_action="idle"))
    agent.step(Event(kind="task_assign", concern="urgent_one", intensity=1.0, forced_action="idle"))
    agent.step(Event(kind="task_assign", concern="urgent_two", intensity=0.9, forced_action="idle"))
    after_three = dict(agent.concerns)
    agent.step(Event(kind="task_cancel", concern="urgent_one", forced_action="idle"))
    agent.step(Event(kind="task_cancel", concern="urgent_two", forced_action="idle"))
    after_resolution = dict(agent.concerns)
    reproduced = "low_priority" not in after_three and "low_priority" not in after_resolution
    return {
        "passed": reproduced,
        "classification": "unchanged" if reproduced else "changed",
        "after_three": after_three,
        "after_resolution": after_resolution,
    }


def prospective_interaction() -> dict:
    agent = UnresolvedConcernPersistenceCharacter()
    agent.step(Event(kind="future_commitment", concern="call_morgan", context="morgan_arrives", forced_action="idle"))
    agent.step(Event(kind="future_commitment", concern="email_lee", context="lee_arrives", forced_action="idle"))
    agent.step(Event(kind="neutral", context="morgan_arrives", forced_action="idle"))
    activated = dict(agent.concerns)
    latent_after_activation = dict(agent.prospective_commitments)
    run_unrelated(agent, 300)
    weak_active = dict(agent.concerns)
    still_latent = dict(agent.prospective_commitments)

    same = UnresolvedConcernPersistenceCharacter()
    assign(same, "report")
    same.step(Event(kind="future_commitment", concern="report", context="tomorrow", forced_action="idle"))
    coexist = "report" in same.concerns and same.prospective_commitments.get("report") == "tomorrow"
    same.step(Event(kind="task_cancel", concern="report", forced_action="idle"))
    cancelled_both = "report" not in same.concerns and "report" not in same.prospective_commitments

    return {
        "passed": (
            "call_morgan" in activated
            and latent_after_activation.get("email_lee") == "lee_arrives"
            and "call_morgan" in weak_active
            and still_latent.get("email_lee") == "lee_arrives"
            and coexist
            and cancelled_both
        ),
        "activated": activated,
        "latent_after_activation": latent_after_activation,
        "weak_active": weak_active,
        "still_latent": still_latent,
        "same_name_coexist": coexist,
        "same_name_cancelled_both": cancelled_both,
    }


def nonconcern_state(snapshot: dict) -> dict:
    state = dict(snapshot)
    state.pop("concern_ledger", None)
    return state


def unrelated_state_isolation() -> dict:
    champion = V91CompactCharacter()
    challenger = UnresolvedConcernPersistenceCharacter()
    events = [
        Event(kind="shock", intensity=0.7, forced_action="avoid"),
        Event(kind="support", actor="Alex", forced_action="idle"),
        Event(kind="observed_reliable", actor="Alex", forced_action="idle"),
        Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"),
        Event(kind="context", context="morning", forced_action="walk"),
        Event(kind="outcome", reward=0.5, forced_action="idle"),
    ]
    actions_equal = True
    for event in events:
        actions_equal = actions_equal and champion.step(event) == challenger.step(event)
    no_concern_equal = champion.persistent_snapshot() == challenger.persistent_snapshot()

    champion2 = V91CompactCharacter()
    challenger2 = UnresolvedConcernPersistenceCharacter()
    assign(champion2, "unfinished")
    assign(challenger2, "unfinished")
    run_unrelated(champion2, 120, "mixed")
    run_unrelated(challenger2, 120, "mixed")
    other_equal = nonconcern_state(champion2.persistent_snapshot()) == nonconcern_state(challenger2.persistent_snapshot())

    return {
        "passed": actions_equal and no_concern_equal and other_equal,
        "actions_equal_without_concern": actions_equal,
        "exact_state_equal_without_concern": no_concern_equal,
        "nonconcern_state_equal_after_divergent_concern_lifecycle": other_equal,
    }


def schema_and_mechanism_invariance() -> dict:
    champion = V91CompactCharacter()
    challenger = UnresolvedConcernPersistenceCharacter()
    return {
        "passed": (
            challenger.mechanism_count() == champion.mechanism_count() == 11
            and set(challenger.__dict__) == set(champion.__dict__)
            and set(challenger.persistent_snapshot()) == set(champion.persistent_snapshot())
            and challenger.max_concerns == champion.max_concerns == 2
            and challenger.max_prospective == champion.max_prospective == 2
            and challenger.max_eligibility_records == champion.max_eligibility_records == 2
        ),
        "mechanism_count": challenger.mechanism_count(),
        "fresh_instance_fields_champion": sorted(champion.__dict__),
        "fresh_instance_fields_challenger": sorted(challenger.__dict__),
        "persistent_keys": sorted(challenger.persistent_snapshot()),
        "capacities": {
            "concerns": challenger.max_concerns,
            "prospective": challenger.max_prospective,
            "eligibility": challenger.max_eligibility_records,
        },
    }


def causal_ablations() -> dict:
    champion = V91CompactCharacter()
    challenger = UnresolvedConcernPersistenceCharacter()
    threshold = RestoreThresholdDeletionCharacter()
    no_decay = NoConcernDecayCharacter()
    for agent in (champion, challenger, threshold, no_decay):
        assign(agent)
        run_unrelated(agent, 120)
    rows = {
        "champion": dict(champion.concerns),
        "challenger": dict(challenger.concerns),
        "threshold_restored": dict(threshold.concerns),
        "no_decay": dict(no_decay.concerns),
    }
    x_strength = challenger.concerns.get("finish_portfolio", 0.0)
    no_decay_strength = no_decay.concerns.get("finish_portfolio", 0.0)
    return {
        "passed": (
            "finish_portfolio" not in champion.concerns
            and "finish_portfolio" in challenger.concerns
            and "finish_portfolio" not in threshold.concerns
            and no_decay_strength == 0.75
            and 0.0 <= x_strength < no_decay_strength
        ),
        "rows": rows,
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
        "matched_retention": matched_retention(),
        "unrelated_kind_invariance": unrelated_kind_invariance(),
        "low_activation_non_dominance": low_activation_non_dominance(),
        "legitimate_termination": legitimate_termination(),
        "long_horizon_and_reconstruction": long_horizon_and_reconstruction(),
        "reactivation_existing_machinery": reactivation_existing_machinery(),
        "suppressed_concern_scope_control": suppressed_concern_scope_control(),
        "prospective_interaction": prospective_interaction(),
        "unrelated_state_isolation": unrelated_state_isolation(),
        "schema_and_mechanism_invariance": schema_and_mechanism_invariance(),
        "causal_ablations": causal_ablations(),
        "historical_contract": historical_contract(),
    }
    failures = [name for name, row in sections.items() if not row["passed"]]
    return {
        "experiment": "EXP-009 unresolved concern existence versus activation",
        "phase": "development matched evaluation before reviewer holdouts",
        "frozen_champion": "v9.1_compact",
        "frozen_commit": "2856ec6a32be0347a9243f6eff6faa404a9a0e6c",
        "challenger": "exp009_unresolved_concern_persistence_candidate",
        "new_persistent_fields": 0,
        "new_counted_mechanisms": 0,
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
