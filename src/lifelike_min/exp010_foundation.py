from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

from .exp009_challenger import UnresolvedConcernPersistenceCharacter
from .runtime import Event

FROZEN_CHAMPION = "v9.2_unresolved_concern_persistence"
FROZEN_CHAMPION_COMMIT = "bd1ca22ca58e82012f1a8237e3de4bfee4dbf59d"
EVALUATED_PRODUCTION_COMMIT = "b5cc3e109ab2fa4de0421dc113009d1ee7fb050d"


def diagnostic_bytes(agent: UnresolvedConcernPersistenceCharacter) -> int:
    return len(json.dumps(agent.snapshot(), sort_keys=True, separators=(",", ":")).encode("utf-8"))


def canonical_bytes(agent: UnresolvedConcernPersistenceCharacter) -> int:
    return len(agent.serialize_persistent().encode("utf-8"))


def task(agent, concern: str, intensity: float) -> None:
    agent.step(Event(kind="task_assign", concern=concern, intensity=intensity, forced_action="idle"))


def cancel(agent, concern: str) -> None:
    agent.step(Event(kind="task_cancel", concern=concern, forced_action="idle"))


def reproduce_target() -> dict:
    agent = UnresolvedConcernPersistenceCharacter()
    task(agent, "low_priority", 0.5)
    after_a = dict(agent.concerns)
    task(agent, "urgent_one", 1.0)
    after_b = dict(agent.concerns)
    task(agent, "urgent_two", 0.9)
    after_c = dict(agent.concerns)
    cancel(agent, "urgent_one")
    after_b_resolved = dict(agent.concerns)
    cancel(agent, "urgent_two")
    final = dict(agent.concerns)
    return {
        "reproduced": "low_priority" not in after_c and "low_priority" not in final,
        "after_a": after_a,
        "after_b": after_b,
        "after_c": after_c,
        "after_b_resolved": after_b_resolved,
        "final": final,
    }


def matched_identity_history(weak_identity: str) -> tuple[UnresolvedConcernPersistenceCharacter, list[dict]]:
    """Same event types/intensities; only the weak concern identity differs.

    The control identity is deliberately a different concern rather than a neutral
    event. This preserves tick count and all non-concern task-assignment side effects.
    In the control history A literally never exists.
    """
    agent = UnresolvedConcernPersistenceCharacter()
    rows = []

    def capture(label: str) -> None:
        rows.append(
            {
                "label": label,
                "concerns": dict(agent.concerns),
                "canonical": agent.persistent_snapshot(),
                "serialized": agent.serialize_persistent(),
            }
        )

    task(agent, weak_identity, 0.5)
    capture("after_weak")
    task(agent, "urgent_one", 1.0)
    capture("after_b")
    task(agent, "urgent_two", 0.9)
    capture("after_c_eviction")
    cancel(agent, "urgent_one")
    capture("after_b_resolution")
    cancel(agent, "urgent_two")
    capture("after_c_resolution")
    return agent, rows


def information_loss_test() -> dict:
    history_a, trace_a = matched_identity_history("low_priority")
    history_b, trace_b = matched_identity_history("matched_control")

    labels = [row["label"] for row in trace_a]
    comparisons = []
    for left, right in zip(trace_a, trace_b):
        comparisons.append(
            {
                "label": left["label"],
                "canonical_equal": left["serialized"] == right["serialized"],
                "concerns_a": left["concerns"],
                "concerns_b": right["concerns"],
            }
        )

    eviction_index = labels.index("after_c_eviction")
    post_eviction = comparisons[eviction_index:]
    identity_collapsed = all(row["canonical_equal"] for row in post_eviction)

    encoded = history_a.serialize_persistent()
    snapshot = history_a.persistent_snapshot()
    identity_mentions = {
        "canonical_contains_low_priority": "low_priority" in encoded,
        "concern_ledger": "low_priority" in snapshot["concern_ledger"],
        "prospective_commitments": "low_priority" in snapshot["prospective_commitments"],
        "habits": any("low_priority" in str(key) for key in snapshot["habits"]),
        "relationships": "low_priority" in snapshot["relationships"],
        "partner_reliability": "low_priority" in snapshot["partner_reliability"],
        "location_beliefs": "low_priority" in snapshot["location_beliefs"],
        "eligibility_records": any(
            "low_priority" in str(row.get("context")) or "low_priority" in str(row.get("action"))
            for row in snapshot["eligibility_records"]
        ),
    }

    return {
        "history_a": "low_priority existed unfinished, then was capacity-evicted",
        "history_b": "low_priority never existed; matched_control occupied the same weak slot and was capacity-evicted",
        "non_concern_side_effects_matched": True,
        "comparisons": comparisons,
        "state_identical_from_eviction_onward": identity_collapsed,
        "surviving_low_priority_trace": identity_mentions,
        "any_surviving_low_priority_trace": any(identity_mentions.values()),
        "information_lower_bound": (
            "At least concern identity must remain subject-owned if low_priority is to be distinguishable from a history in which it never existed. "
            "The present representation contains zero surviving bits that identify which weak concern was evicted."
            if identity_collapsed and not any(identity_mentions.values())
            else "A surviving distinction exists and must be characterized before claiming a lower bound."
        ),
    }


def run_sequence(spec: Iterable[tuple[str, str, float]]) -> dict:
    agent = UnresolvedConcernPersistenceCharacter()
    trace = []
    for kind, concern, intensity in spec:
        if kind == "assign":
            task(agent, concern, intensity)
        elif kind == "cancel":
            cancel(agent, concern)
        elif kind == "neutral":
            agent.step(Event(kind="neutral", forced_action="idle"))
        else:
            raise ValueError(kind)
        trace.append({"event": [kind, concern, intensity], "concerns": dict(agent.concerns)})
    return {"trace": trace, "final": dict(agent.concerns)}


def causal_characterization() -> dict:
    scenarios = {
        "weak_old": [
            ("assign", "A", 0.5), ("assign", "B", 1.0), ("assign", "C", 0.9),
        ],
        "a_old_but_strong": [
            ("assign", "A", 1.0), ("assign", "B", 0.9), ("assign", "C", 0.5),
        ],
        "a_recent_but_weak": [
            ("assign", "B", 1.0), ("assign", "C", 0.9), ("assign", "A", 0.5),
        ],
        "equal_strength": [
            ("assign", "A", 1.0), ("assign", "B", 1.0), ("assign", "C", 1.0),
        ],
        "resolve_b_then_c": [
            ("assign", "A", 0.5), ("assign", "B", 1.0), ("assign", "C", 0.9),
            ("cancel", "B", 0.0), ("cancel", "C", 0.0),
        ],
        "resolve_c_then_b": [
            ("assign", "A", 0.5), ("assign", "B", 1.0), ("assign", "C", 0.9),
            ("cancel", "C", 0.0), ("cancel", "B", 0.0),
        ],
        "long_delay_then_resolve": [
            ("assign", "A", 0.5), ("assign", "B", 1.0), ("assign", "C", 0.9),
            *[("neutral", "", 0.0) for _ in range(100)],
            ("cancel", "B", 0.0), ("cancel", "C", 0.0),
        ],
    }
    rows = {name: run_sequence(spec) for name, spec in scenarios.items()}
    return {
        "policy_from_source": "capacity keeps the two highest current concern strengths; equal-strength ties inherit stable insertion ordering",
        "scenarios": rows,
        "weakness_not_recency": (
            "A" not in rows["weak_old"]["final"]
            and "A" in rows["a_old_but_strong"]["final"]
            and "A" not in rows["a_recent_but_weak"]["final"]
        ),
    }


def baseline_contract() -> dict:
    fresh = UnresolvedConcernPersistenceCharacter()
    return {
        "mechanism_count": fresh.mechanism_count(),
        "fresh_diagnostic_bytes": diagnostic_bytes(fresh),
        "fresh_canonical_bytes": canonical_bytes(fresh),
        "concern_capacity": fresh.max_concerns,
        "prospective_capacity": fresh.max_prospective,
        "eligibility_capacity": fresh.max_eligibility_records,
        "target": reproduce_target(),
    }


def run() -> dict:
    baseline = baseline_contract()
    information = information_loss_test()
    characterization = causal_characterization()
    gates = {
        "frozen_baseline_matches": (
            baseline["mechanism_count"] == 11
            and baseline["fresh_diagnostic_bytes"] == 269
            and baseline["fresh_canonical_bytes"] == 245
            and baseline["concern_capacity"] == 2
            and baseline["prospective_capacity"] == 2
            and baseline["eligibility_capacity"] == 2
            and baseline["target"]["reproduced"]
        ),
        "information_identity_collapses": information["state_identical_from_eviction_onward"],
        "no_subject_owned_identity_trace_survives": not information["any_surviving_low_priority_trace"],
    }
    return {
        "experiment": "EXP-010 minimum-information suppression versus deletion foundation",
        "phase": "pre-archaeology, pre-preregistration, no challenger",
        "frozen_champion": FROZEN_CHAMPION,
        "frozen_champion_commit": FROZEN_CHAMPION_COMMIT,
        "evaluated_production_commit": EVALUATED_PRODUCTION_COMMIT,
        "baseline": baseline,
        "information_loss": information,
        "causal_characterization": characterization,
        "gates": gates,
        "foundation_passed": all(gates.values()),
        "challenger_exists": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    report = run()
    encoded = json.dumps(report, indent=2, sort_keys=True)
    print(encoded)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(encoded + "\n", encoding="utf-8")
    raise SystemExit(0 if report["foundation_passed"] else 2)


if __name__ == "__main__":
    main()
