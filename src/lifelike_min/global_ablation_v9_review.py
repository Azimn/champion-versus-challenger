from __future__ import annotations

import argparse
import json
from pathlib import Path

from .exp007_challenger import EligibilityTraceCharacter
from .exp007_evaluation import (
    delayed_positive,
    delayed_negative,
    immediate_control,
    historical_regressions,
    development_suite,
)
from .global_ablation_v9 import (
    DerivedConcernViewCharacter,
    TraceBackedImmediateHabitCharacter,
    CompressedV9Character,
    NoConcernLedgerCharacter,
    base_need_roles,
    earned_suite,
    simplification_metrics,
)
from .runtime import Event


def _habit(agent, context: str, action: str) -> float:
    return float(agent.habits.get((context, action), 0.0))


def concern_trajectory_equivalence() -> dict:
    frozen = EligibilityTraceCharacter()
    derived = DerivedConcernViewCharacter()
    events = [
        Event(kind="task_assign", concern="minor", intensity=0.5, forced_action="idle"),
        Event(kind="task_assign", concern="urgent", intensity=1.0, forced_action="idle"),
        Event(kind="shock", intensity=0.8, forced_action="avoid"),
        Event(kind="neutral", forced_action="idle"),
        Event(kind="neutral", available_actions=("work", "rest", "idle")),
        Event(kind="task_cancel", concern="urgent", forced_action="idle"),
        Event(kind="neutral", available_actions=("work", "rest", "idle")),
    ]
    rows = []
    passed = True
    for event in events:
        frozen_action = frozen.step(event)
        derived_action = derived.step(event)
        fs = frozen.snapshot()
        ds = derived.snapshot()
        row = {
            "frozen_action": frozen_action,
            "derived_action": derived_action,
            "frozen_active": fs.get("active_concern"),
            "derived_active": ds.get("active_concern"),
            "frozen_strength": fs.get("concern_strength"),
            "derived_strength": ds.get("concern_strength"),
            "frozen_ledger": fs.get("concern_ledger", {}),
            "derived_ledger": ds.get("concern_ledger", {}),
        }
        row_passed = (
            frozen_action == derived_action
            and row["frozen_active"] == row["derived_active"]
            and row["frozen_strength"] == row["derived_strength"]
            and row["frozen_ledger"] == row["derived_ledger"]
        )
        row["passed"] = row_passed
        passed = passed and row_passed
        rows.append(row)
    return {"passed": passed, "rows": rows}


def concern_equal_strength_order() -> dict:
    outcomes = []
    for order in (("a", "b"), ("b", "a")):
        pair = []
        for factory in (EligibilityTraceCharacter, DerivedConcernViewCharacter):
            agent = factory()
            for concern in order:
                agent.step(Event(kind="task_assign", concern=concern, intensity=1.0, forced_action="idle"))
            pair.append(agent.snapshot().get("active_concern"))
        outcomes.append({"order": order, "frozen": pair[0], "derived": pair[1]})
    return {
        "passed": all(row["frozen"] == row["derived"] for row in outcomes),
        "outcomes": outcomes,
        "interpretation": "Tie ordering remains inherited from ledger insertion order; H1 must not introduce a new priority rule.",
    }


def concern_single_decay_and_work_update() -> dict:
    frozen = EligibilityTraceCharacter()
    derived = DerivedConcernViewCharacter()
    for agent in (frozen, derived):
        agent.step(Event(kind="task_assign", concern="report", intensity=1.0, forced_action="idle"))
    before = (frozen.concerns["report"], derived.concerns["report"])
    for agent in (frozen, derived):
        agent.step(Event(kind="neutral", forced_action="idle"))
    after_drift = (frozen.concerns["report"], derived.concerns["report"])
    for agent in (frozen, derived):
        agent.step(Event(kind="neutral", forced_action="work"))
    after_work = (
        frozen.concerns.get("report", 0.0),
        derived.concerns.get("report", 0.0),
    )
    return {
        "passed": before[0] == before[1] and after_drift[0] == after_drift[1] and after_work[0] == after_work[1],
        "before": before,
        "after_drift": after_drift,
        "after_work": after_work,
        "interpretation": "Derived compatibility fields must not accidentally double or suppress ledger decay/work effects.",
    }


def concern_reverse_ablation() -> dict:
    removed = earned_suite(NoConcernLedgerCharacter)
    restored = earned_suite(DerivedConcernViewCharacter)
    return {
        "passed": (not removed["passed"]) and restored["passed"],
        "removed_failures": removed["failures"],
        "restored_failures": restored["failures"],
        "interpretation": "The ledger itself remains essential; only the duplicated compatibility storage is removed.",
    }


def h1_persistence_classification() -> dict:
    agent = DerivedConcernViewCharacter()
    agent.step(Event(kind="task_assign", concern="report", forced_action="idle"))
    diagnostic = agent.snapshot()
    # H1 intentionally keeps derived fields visible in diagnostic snapshots for
    # backward-compatible observation, while persistent_state_bytes excludes them.
    full_bytes = len(json.dumps(diagnostic, sort_keys=True).encode("utf-8"))
    persistent_bytes = agent.persistent_state_bytes()
    return {
        "passed": (
            diagnostic.get("active_concern") == "report"
            and diagnostic.get("concern_strength") is not None
            and persistent_bytes < full_bytes
        ),
        "diagnostic_snapshot_bytes": full_bytes,
        "persistent_payload_bytes": persistent_bytes,
        "derived_fields_visible_diagnostically": ["active_concern", "concern_strength"],
        "interpretation": "H1 is a persistence reclassification, not deletion of observability. The ledger is authoritative; active concern/strength are deterministic views.",
    }


def h2_immediate_equivalence() -> dict:
    rows = []
    passed = True
    for context, action, reward in (
        ("morning", "walk", 1.0),
        ("studio", "paint", -0.6),
        ("garage", "inspect", 0.25),
    ):
        values = []
        for factory in (EligibilityTraceCharacter, TraceBackedImmediateHabitCharacter):
            agent = factory()
            agent.step(Event(kind="context", context=context, forced_action=action))
            agent.step(Event(kind="outcome", reward=reward, context=None, forced_action="idle"))
            values.append(_habit(agent, context, action))
        row_passed = abs(values[0] - values[1]) < 1e-12
        passed = passed and row_passed
        rows.append({"context": context, "action": action, "reward": reward, "frozen": values[0], "trace_backed": values[1], "passed": row_passed})
    return {"passed": passed, "rows": rows}


def h2_most_recent_context_action() -> dict:
    frozen = EligibilityTraceCharacter()
    trace_backed = TraceBackedImmediateHabitCharacter()
    for agent in (frozen, trace_backed):
        agent.step(Event(kind="context", context="morning", forced_action="walk"))
        agent.step(Event(kind="context", context="office", forced_action="file"))
        agent.step(Event(kind="outcome", reward=1.0, context=None, forced_action="idle"))
    values = {
        "frozen_morning": _habit(frozen, "morning", "walk"),
        "frozen_office": _habit(frozen, "office", "file"),
        "trace_morning": _habit(trace_backed, "morning", "walk"),
        "trace_office": _habit(trace_backed, "office", "file"),
    }
    return {
        "passed": values["frozen_morning"] == values["trace_morning"] == 0.0 and values["frozen_office"] == values["trace_office"] == 0.35,
        **values,
    }


def h2_same_context_recent_action() -> dict:
    frozen = EligibilityTraceCharacter()
    trace_backed = TraceBackedImmediateHabitCharacter()
    for agent in (frozen, trace_backed):
        agent.step(Event(kind="context", context="kitchen", forced_action="stir"))
        agent.step(Event(kind="context", context="kitchen", forced_action="taste"))
        agent.step(Event(kind="outcome", reward=1.0, context=None, forced_action="idle"))
    return {
        "passed": (
            _habit(frozen, "kitchen", "stir") == _habit(trace_backed, "kitchen", "stir") == 0.0
            and _habit(frozen, "kitchen", "taste") == _habit(trace_backed, "kitchen", "taste") == 0.35
        ),
        "frozen": dict(frozen.habits),
        "trace_backed": dict(trace_backed.habits),
        "interpretation": "Immediate adjacency may identify the age-zero action even when older same-context candidates exist; delayed same-context ambiguity still abstains.",
    }


def h2_noncontext_intervener() -> dict:
    rows = []
    passed = True
    for factory in (EligibilityTraceCharacter, TraceBackedImmediateHabitCharacter):
        agent = factory()
        agent.step(Event(kind="context", context="morning", forced_action="walk"))
        agent.step(Event(kind="encounter", actor="Alex", forced_action="socialize:Alex"))
        agent.step(Event(kind="outcome", reward=1.0, context=None, forced_action="idle"))
        value = _habit(agent, "morning", "walk")
        rows.append({"factory": factory.__name__, "value": value})
        passed = passed and value == 0.0
    return {"passed": passed, "rows": rows}


def h2_idle_habit_is_dead_state() -> dict:
    frozen = EligibilityTraceCharacter()
    trace_backed = TraceBackedImmediateHabitCharacter()
    for agent in (frozen, trace_backed):
        agent.step(Event(kind="context", context="quiet", forced_action="idle"))
        agent.step(Event(kind="outcome", reward=1.0, context=None, forced_action="idle"))
    frozen_idle = _habit(frozen, "quiet", "idle")
    trace_idle = _habit(trace_backed, "quiet", "idle")
    choices = []
    for factory in (EligibilityTraceCharacter, TraceBackedImmediateHabitCharacter):
        for order in (("idle", "read"), ("read", "idle")):
            agent = factory()
            agent.step(Event(kind="context", context="quiet", forced_action="idle"))
            agent.step(Event(kind="outcome", reward=1.0, context=None, forced_action="idle"))
            choices.append((factory.__name__, order, agent.step(Event(kind="context", context="quiet", available_actions=order))))
    equivalent = (
        choices[0][2] == choices[2][2]
        and choices[1][2] == choices[3][2]
    )
    return {
        "passed": frozen_idle == 0.35 and trace_idle == 0.0 and equivalent,
        "frozen_idle_habit": frozen_idle,
        "trace_backed_idle_habit": trace_idle,
        "choices": [(name, list(order), choice) for name, order, choice in choices],
        "interpretation": "The frozen implementation can store a context-idle habit that cannot affect idle scoring. H2 removes this behaviorally unreadable persistent state.",
    }


def h2_delayed_regression() -> dict:
    rows = {
        "positive_1": delayed_positive(TraceBackedImmediateHabitCharacter, 1),
        "positive_8": delayed_positive(TraceBackedImmediateHabitCharacter, 8),
        "negative_3": delayed_negative(TraceBackedImmediateHabitCharacter, 3),
        "immediate": immediate_control(TraceBackedImmediateHabitCharacter),
    }
    failures = [name for name, result in rows.items() if not result["passed"]]
    return {"passed": not failures, "failures": failures}


def h2_reverse_ablation() -> dict:
    class NoLastNoTrace(TraceBackedImmediateHabitCharacter):
        max_eligibility_records = 0

    removed = immediate_control(NoLastNoTrace)
    restored = immediate_control(TraceBackedImmediateHabitCharacter)
    return {
        "passed": (not removed["passed"]) and restored["passed"],
        "removed": removed,
        "restored": restored,
        "interpretation": "Once last-action fields are removed, the age-zero trace record is the minimum restored information needed for the earned immediate update path.",
    }


def base_need_relitigation() -> dict:
    normal = base_need_roles(EligibilityTraceCharacter)
    permutations = {"fatigue": [], "affiliation": [], "competence": []}

    for order in (("rest", "work", "idle"), ("idle", "work", "rest"), ("work", "rest", "idle")):
        agent = EligibilityTraceCharacter()
        permutations["fatigue"].append(agent.step(Event(kind="neutral", available_actions=order)))

    for order in (("socialize:Stranger", "avoid:Stranger", "idle"), ("idle", "avoid:Stranger", "socialize:Stranger")):
        agent = EligibilityTraceCharacter()
        permutations["affiliation"].append(agent.step(Event(kind="encounter", actor="Stranger", available_actions=order)))

    for order in (("work", "rest", "idle"), ("idle", "rest", "work")):
        agent = EligibilityTraceCharacter()
        agent.step(Event(kind="neutral", forced_action="rest"))
        permutations["competence"].append(agent.step(Event(kind="neutral", available_actions=order)))

    passed = (
        normal["fatigue_drives_rest"]
        and normal["affiliation_drives_unscripted_social_approach"]
        and normal["competence_drives_work_after_rest"]
        and permutations["fatigue"] == ["rest", "rest", "rest"]
        and permutations["affiliation"] == ["socialize:Stranger", "socialize:Stranger"]
        and permutations["competence"] == ["work", "work"]
    )
    return {
        "passed": passed,
        "normal": normal,
        "action_order_permutations": permutations,
        "interpretation": "The three base pressures have direct order-invariant behavioral effects in v9. Fatigue and affiliation are therefore retained despite being underrepresented in the later promotion suite.",
    }


def combined_full_suite() -> dict:
    suite = earned_suite(CompressedV9Character)
    historical = historical_regressions(CompressedV9Character)
    development = development_suite(CompressedV9Character)
    return {
        "passed": suite["passed"] and all(r["passed"] for r in historical.values()) and all(r["passed"] for r in development.values()),
        "suite_failures": suite["failures"],
        "historical_failures": [name for name, row in historical.items() if not row["passed"]],
        "development_failures": [name for name, row in development.items() if not row["passed"]],
        "metrics": simplification_metrics(CompressedV9Character),
    }


def run_review() -> dict:
    probes = {
        "H1_concern_trajectory_equivalence": concern_trajectory_equivalence(),
        "H1_equal_strength_order": concern_equal_strength_order(),
        "H1_single_decay_and_work_update": concern_single_decay_and_work_update(),
        "H1_reverse_ablation": concern_reverse_ablation(),
        "H1_persistence_classification": h1_persistence_classification(),
        "H2_immediate_equivalence": h2_immediate_equivalence(),
        "H2_most_recent_context_action": h2_most_recent_context_action(),
        "H2_same_context_recent_action": h2_same_context_recent_action(),
        "H2_noncontext_intervener": h2_noncontext_intervener(),
        "H2_idle_habit_is_dead_state": h2_idle_habit_is_dead_state(),
        "H2_delayed_regression": h2_delayed_regression(),
        "H2_reverse_ablation": h2_reverse_ablation(),
        "base_need_relitigation": base_need_relitigation(),
        "combined_full_suite": combined_full_suite(),
    }
    failures = [name for name, result in probes.items() if not result["passed"]]
    return {
        "phase": "GLOBAL STRUCTURAL ABLATION v9 adversarial review of H1/H2",
        "probe_count": len(probes),
        "failures": failures,
        "passed": not failures,
        "probes": probes,
    }


def compact(value):
    if isinstance(value, dict):
        return {
            str(key): compact(item)
            for key, item in value.items()
            if key not in {"trace", "traces"}
        }
    if isinstance(value, tuple):
        return [compact(item) for item in value]
    if isinstance(value, list):
        return [compact(item) for item in value]
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    report = compact(run_review())
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    raise SystemExit(0 if report["passed"] else 2)


if __name__ == "__main__":
    main()
