from __future__ import annotations

import argparse
import json
from pathlib import Path

from .exp009_challenger import UnresolvedConcernPersistenceCharacter
from .runtime import Event

PRODUCTION_COMMIT = "b5cc3e109ab2fa4de0421dc113009d1ee7fb050d"


def assign(agent, name: str, intensity: float = 1.0) -> None:
    agent.step(Event(kind="task_assign", concern=name, intensity=intensity, forced_action="idle"))


def idle(agent, count: int) -> None:
    for _ in range(count):
        agent.step(Event(kind="neutral", forced_action="idle"))


def very_long_dormancy() -> dict:
    agent = UnresolvedConcernPersistenceCharacter()
    assign(agent, "thesis")
    idle(agent, 10_000)
    value = agent.concerns.get("thesis")
    return {
        "passed": value is not None and 0.0 <= value < 1e-100,
        "strength_after_10000": value,
    }


def extremely_weak_assignment() -> dict:
    agent = UnresolvedConcernPersistenceCharacter()
    assign(agent, "tiny", 1e-9)
    initial = agent.concerns.get("tiny")
    idle(agent, 1000)
    final = agent.concerns.get("tiny")
    return {
        "passed": initial is not None and final is not None and 0.0 <= final < initial,
        "initial": initial,
        "final": final,
    }


def reassignment_after_dormancy() -> dict:
    agent = UnresolvedConcernPersistenceCharacter()
    assign(agent, "return_to_it")
    idle(agent, 10_000)
    before = agent.concerns.get("return_to_it")
    assign(agent, "return_to_it", 0.6)
    after = agent.concerns.get("return_to_it")
    return {
        "passed": before is not None and after == 0.45 and len(agent.concerns) == 1,
        "before": before,
        "after": after,
        "ledger": dict(agent.concerns),
    }


def cancel_after_dormancy() -> dict:
    agent = UnresolvedConcernPersistenceCharacter()
    assign(agent, "cancel_late")
    idle(agent, 10_000)
    agent.step(Event(kind="task_cancel", concern="cancel_late", forced_action="idle"))
    return {"passed": "cancel_late" not in agent.concerns, "ledger": dict(agent.concerns)}


def work_after_dormancy() -> dict:
    agent = UnresolvedConcernPersistenceCharacter()
    assign(agent, "finish_late")
    idle(agent, 10_000)
    before = agent.concerns.get("finish_late")
    agent.step(Event(kind="neutral", forced_action="work"))
    return {
        "passed": before is not None and "finish_late" not in agent.concerns,
        "before": before,
        "ledger": dict(agent.concerns),
    }


def serialization_at_extreme_decay() -> dict:
    agent = UnresolvedConcernPersistenceCharacter()
    assign(agent, "persist_exactly")
    idle(agent, 10_000)
    encoded = agent.serialize_persistent()
    restored = UnresolvedConcernPersistenceCharacter.from_persistent_json(encoded)
    exact = restored.persistent_snapshot() == agent.persistent_snapshot()
    before = restored.concerns.get("persist_exactly")
    idle(restored, 3)
    after = restored.concerns.get("persist_exactly")
    return {
        "passed": exact and before is not None and after is not None and after < before,
        "exact_after_restore": exact,
        "before_continue": before,
        "after_three_more": after,
        "serialized_bytes": len(encoded.encode("utf-8")),
    }


def interleaved_prospective() -> dict:
    agent = UnresolvedConcernPersistenceCharacter()
    assign(agent, "old_active")
    idle(agent, 500)
    agent.step(Event(kind="future_commitment", concern="call_morgan", context="morgan", forced_action="idle"))
    agent.step(Event(kind="future_commitment", concern="email_lee", context="lee", forced_action="idle"))
    agent.step(Event(kind="neutral", context="morgan", forced_action="idle"))
    state = agent.persistent_snapshot()
    return {
        "passed": (
            set(agent.concerns) == {"old_active", "call_morgan"}
            and agent.prospective_commitments.get("email_lee") == "lee"
            and "call_morgan" not in agent.prospective_commitments
        ),
        "concerns": dict(agent.concerns),
        "prospective": dict(agent.prospective_commitments),
        "persistent_keys": sorted(state),
    }


def two_weak_concerns_survive() -> dict:
    agent = UnresolvedConcernPersistenceCharacter()
    assign(agent, "old_a")
    assign(agent, "old_b", 0.8)
    idle(agent, 10_000)
    return {
        "passed": set(agent.concerns) == {"old_a", "old_b"} and all(v >= 0.0 for v in agent.concerns.values()),
        "ledger": dict(agent.concerns),
    }


def strong_new_evicts_weaker_dormant() -> dict:
    agent = UnresolvedConcernPersistenceCharacter()
    assign(agent, "older")
    assign(agent, "newer", 1.0)
    idle(agent, 1000)
    before = dict(agent.concerns)
    assign(agent, "urgent", 1.0)
    after = dict(agent.concerns)
    return {
        "passed": len(after) == 2 and "urgent" in after and "older" not in after and "newer" in after,
        "before": before,
        "after": after,
    }


def weak_concern_does_not_override_meaningful_need_margin() -> dict:
    actions = []
    states = []
    for order in (("rest", "work", "idle"), ("work", "idle", "rest")):
        agent = UnresolvedConcernPersistenceCharacter()
        assign(agent, "barely_active")
        idle(agent, 1000)
        agent.fatigue = 0.90
        agent.competence = 0.80
        before = agent.concerns["barely_active"]
        action = agent.step(Event(kind="neutral", available_actions=order))
        actions.append(action)
        states.append({"before": before, "after": agent.concerns.get("barely_active")})
    return {
        "passed": actions == ["rest", "rest"] and all(row["after"] is not None for row in states),
        "actions": actions,
        "states": states,
    }


def unrelated_outcome_does_not_terminate() -> dict:
    agent = UnresolvedConcernPersistenceCharacter()
    assign(agent, "unrelated_reward")
    before = agent.concerns["unrelated_reward"]
    agent.step(Event(kind="outcome", reward=-1.0, context="elsewhere", forced_action="idle"))
    after = agent.concerns.get("unrelated_reward")
    return {
        "passed": after is not None and abs(after - before * 0.97) < 1e-15,
        "before": before,
        "after": after,
    }


def zero_activation_is_not_nonexistence() -> dict:
    agent = UnresolvedConcernPersistenceCharacter()
    agent.concerns["zero_now"] = 0.0
    agent.fatigue = 0.9
    agent.competence = 0.7
    choice = agent.step(Event(kind="neutral", available_actions=("work", "rest", "idle")))
    present_after_choice = "zero_now" in agent.concerns
    assign(agent, "zero_now", 1.0)
    return {
        "passed": present_after_choice and choice == "rest" and agent.concerns.get("zero_now") == 0.75,
        "choice": choice,
        "reactivated": agent.concerns.get("zero_now"),
    }


def reintroduce_after_eviction() -> dict:
    agent = UnresolvedConcernPersistenceCharacter()
    assign(agent, "old")
    idle(agent, 300)
    assign(agent, "current_a")
    assign(agent, "current_b", 0.9)
    evicted = "old" not in agent.concerns
    assign(agent, "old", 1.0)
    returned = "old" in agent.concerns and len(agent.concerns) == 2
    return {
        "passed": evicted and returned,
        "ledger": dict(agent.concerns),
    }


def resolved_does_not_resurrect_after_restore() -> dict:
    agent = UnresolvedConcernPersistenceCharacter()
    assign(agent, "done")
    idle(agent, 1000)
    agent.step(Event(kind="task_cancel", concern="done", forced_action="idle"))
    encoded = agent.serialize_persistent()
    restored = UnresolvedConcernPersistenceCharacter.from_persistent_json(encoded)
    idle(restored, 100)
    return {
        "passed": "done" not in restored.concerns,
        "ledger": dict(restored.concerns),
    }


def reordered_unrelated_histories_have_same_concern_state() -> dict:
    left = UnresolvedConcernPersistenceCharacter()
    right = UnresolvedConcernPersistenceCharacter()
    assign(left, "order_invariant")
    assign(right, "order_invariant")
    left_events = [
        Event(kind="support", actor="A", forced_action="idle"),
        Event(kind="observe_location", actor="book", context="desk", forced_action="idle"),
        Event(kind="observed_reliable", actor="B", forced_action="idle"),
        Event(kind="neutral", forced_action="idle"),
    ]
    right_events = list(reversed(left_events))
    for event in left_events:
        left.step(event)
    for event in right_events:
        right.step(event)
    return {
        "passed": left.concerns == right.concerns,
        "left": dict(left.concerns),
        "right": dict(right.concerns),
    }


def reviewer() -> dict:
    probes = {
        "very_long_dormancy": very_long_dormancy(),
        "extremely_weak_assignment": extremely_weak_assignment(),
        "reassignment_after_dormancy": reassignment_after_dormancy(),
        "cancel_after_dormancy": cancel_after_dormancy(),
        "work_after_dormancy": work_after_dormancy(),
        "serialization_at_extreme_decay": serialization_at_extreme_decay(),
        "interleaved_prospective": interleaved_prospective(),
        "two_weak_concerns_survive": two_weak_concerns_survive(),
        "strong_new_evicts_weaker_dormant": strong_new_evicts_weaker_dormant(),
        "weak_concern_does_not_override_meaningful_need_margin": weak_concern_does_not_override_meaningful_need_margin(),
        "unrelated_outcome_does_not_terminate": unrelated_outcome_does_not_terminate(),
        "zero_activation_is_not_nonexistence": zero_activation_is_not_nonexistence(),
        "reintroduce_after_eviction": reintroduce_after_eviction(),
        "resolved_does_not_resurrect_after_restore": resolved_does_not_resurrect_after_restore(),
        "reordered_unrelated_histories_have_same_concern_state": reordered_unrelated_histories_have_same_concern_state(),
    }
    failures = [name for name, row in probes.items() if not row["passed"]]
    return {
        "experiment": "EXP-009",
        "reviewer_generation": 1,
        "production_commit": PRODUCTION_COMMIT,
        "probes": probes,
        "failures": failures,
        "reviewer_passed": not failures,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    report = reviewer()
    encoded = json.dumps(report, indent=2, sort_keys=True)
    print(encoded)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(encoded + "\n", encoding="utf-8")
    raise SystemExit(0 if report["reviewer_passed"] else 2)


if __name__ == "__main__":
    main()
