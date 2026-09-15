from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean, median, pstdev
from time import perf_counter_ns

from .exp006_evaluation import benchmark as exp006_benchmark
from .exp007_challenger import EligibilityTraceCharacter
from .exp007_evaluation import (
    action_order_invariance,
    cross_context,
    delayed_negative,
    delayed_positive,
    development_suite,
    historical_regressions,
    immediate_control,
    irrelevant_outcome,
    multiple_candidates,
    renderer_invariance,
)
from .global_ablation_v9 import earned_suite
from .runtime import Event
from .v9_compact import CompactV9Character


FROZEN_COMPACTION_CANDIDATE_COMMIT = "1e95aa633b1e0440631e71c5760c8b7829df581a"


def habit(agent, context: str, action: str) -> float:
    return float(agent.habits.get((context, action), 0.0))


def no_duplicate_fields_in_object_state() -> dict:
    agent = CompactV9Character()
    agent.step(Event(kind="task_assign", concern="report", forced_action="idle"))
    agent.step(Event(kind="context", context="morning", forced_action="walk"))
    raw_keys = sorted(agent.__dict__)
    forbidden = ["active_concern", "concern_strength", "last_action", "last_context"]
    diagnostic = agent.snapshot()
    persistent = agent.persistent_snapshot()
    return {
        "passed": (
            not any(name in agent.__dict__ for name in forbidden)
            and diagnostic.get("active_concern") == "report"
            and diagnostic.get("concern_strength", 0.0) > 0.0
            and "active_concern" not in persistent
            and "concern_strength" not in persistent
            and "last_action" not in persistent
            and "last_context" not in persistent
        ),
        "object_dict_keys": raw_keys,
        "forbidden_stored_fields": forbidden,
        "diagnostic_active_concern": diagnostic.get("active_concern"),
        "diagnostic_concern_strength": diagnostic.get("concern_strength"),
        "persistent_keys": sorted(persistent),
    }


def matched_concern_sequences() -> dict:
    frozen = EligibilityTraceCharacter()
    compact = CompactV9Character()
    events = [
        Event(kind="task_assign", concern="alpha", intensity=0.5, forced_action="idle"),
        Event(kind="task_assign", concern="beta", intensity=1.0, forced_action="idle"),
        Event(kind="neutral", forced_action="idle"),
        Event(kind="shock", intensity=0.7, forced_action="avoid"),
        Event(kind="neutral", available_actions=("work", "rest", "idle")),
        Event(kind="task_cancel", concern="beta", forced_action="idle"),
        Event(kind="neutral", available_actions=("work", "rest", "idle")),
    ]
    rows = []
    passed = True
    for event in events:
        fa = frozen.step(event)
        ca = compact.step(event)
        fs = frozen.snapshot()
        cs = compact.snapshot()
        ok = (
            fa == ca
            and fs.get("active_concern") == cs.get("active_concern")
            and fs.get("concern_strength") == cs.get("concern_strength")
            and fs.get("concern_ledger") == cs.get("concern_ledger")
        )
        passed = passed and ok
        rows.append({
            "passed": ok,
            "frozen_action": fa,
            "compact_action": ca,
            "frozen_active": fs.get("active_concern"),
            "compact_active": cs.get("active_concern"),
            "frozen_strength": fs.get("concern_strength"),
            "compact_strength": cs.get("concern_strength"),
            "frozen_ledger": fs.get("concern_ledger"),
            "compact_ledger": cs.get("concern_ledger"),
        })
    return {"passed": passed, "rows": rows}


def prospective_to_concern_transition() -> dict:
    frozen = EligibilityTraceCharacter()
    compact = CompactV9Character()
    for agent in (frozen, compact):
        agent.step(Event(kind="future_commitment", concern="call_morgan", context="morgan_arrives", forced_action="idle"))
        for _ in range(6):
            agent.step(Event(kind="neutral", forced_action="idle"))
        agent.step(Event(kind="neutral", context="morgan_arrives", forced_action="idle"))
    fs = frozen.snapshot()
    cs = compact.snapshot()
    return {
        "passed": (
            fs.get("active_concern") == cs.get("active_concern") == "call_morgan"
            and fs.get("concern_strength") == cs.get("concern_strength")
            and fs.get("concern_ledger") == cs.get("concern_ledger")
            and fs.get("prospective_commitments") == cs.get("prospective_commitments") == {}
        ),
        "frozen": {k: fs.get(k) for k in ("active_concern", "concern_strength", "concern_ledger", "prospective_commitments")},
        "compact": {k: cs.get(k) for k in ("active_concern", "concern_strength", "concern_ledger", "prospective_commitments")},
    }


def immediate_and_delayed_learning_matrix() -> dict:
    probes = {
        "immediate": immediate_control(CompactV9Character),
        "positive_1": delayed_positive(CompactV9Character, 1),
        "positive_3": delayed_positive(CompactV9Character, 3),
        "positive_8": delayed_positive(CompactV9Character, 8),
        "negative_1": delayed_negative(CompactV9Character, 1),
        "negative_3": delayed_negative(CompactV9Character, 3),
        "negative_8": delayed_negative(CompactV9Character, 8),
        "cross_context": cross_context(CompactV9Character),
        "multiple_candidates": multiple_candidates(CompactV9Character),
        "irrelevant_outcome": irrelevant_outcome(CompactV9Character),
        "action_order": action_order_invariance(CompactV9Character),
    }
    failures = [name for name, row in probes.items() if not row["passed"]]
    return {"passed": not failures, "failures": failures}


def noncontext_and_idle_controls() -> dict:
    compact = CompactV9Character()
    compact.step(Event(kind="context", context="morning", forced_action="walk"))
    compact.step(Event(kind="encounter", actor="Alex", forced_action="socialize:Alex"))
    compact.step(Event(kind="outcome", reward=1.0, context=None, forced_action="idle"))
    noncontext = habit(compact, "morning", "walk")

    idle = CompactV9Character()
    idle.step(Event(kind="context", context="quiet", forced_action="idle"))
    idle.step(Event(kind="outcome", reward=1.0, context=None, forced_action="idle"))
    idle_habit = habit(idle, "quiet", "idle")
    choices = [
        idle.step(Event(kind="context", context="quiet", available_actions=order))
        for order in (("idle", "read"), ("read", "idle"))
    ]
    return {
        "passed": noncontext == 0.0 and idle_habit == 0.0 and choices == ["idle", "read"],
        "stale_context_value_after_noncontext_intervener": noncontext,
        "idle_habit_value": idle_habit,
        "idle_choice_orders": choices,
    }


def same_context_ambiguity() -> dict:
    agent = CompactV9Character()
    agent.step(Event(kind="context", context="lab", forced_action="heat"))
    agent.step(Event(kind="context", context="lab", forced_action="stir"))
    # Immediate unlabeled consequence legitimately selects the age-zero action.
    agent.step(Event(kind="outcome", reward=0.5, context=None, forced_action="idle"))
    immediate_heat = habit(agent, "lab", "heat")
    immediate_stir = habit(agent, "lab", "stir")

    delayed = CompactV9Character()
    delayed.step(Event(kind="context", context="lab", forced_action="heat"))
    delayed.step(Event(kind="context", context="lab", forced_action="stir"))
    delayed.step(Event(kind="neutral", forced_action="idle"))
    delayed.step(Event(kind="outcome", reward=1.0, context="lab", forced_action="idle"))
    return {
        "passed": (
            immediate_heat == 0.0
            and immediate_stir > 0.0
            and habit(delayed, "lab", "heat") == 0.0
            and habit(delayed, "lab", "stir") == 0.0
        ),
        "immediate": {"heat": immediate_heat, "stir": immediate_stir},
        "delayed": {"heat": habit(delayed, "lab", "heat"), "stir": habit(delayed, "lab", "stir")},
    }


def reverse_ablation() -> dict:
    class CompactNoConcerns(CompactV9Character):
        max_concerns = 0

    class CompactNoTrace(CompactV9Character):
        max_eligibility_records = 0

    no_concerns = earned_suite(CompactNoConcerns)
    no_trace = earned_suite(CompactNoTrace)
    restored = earned_suite(CompactV9Character)
    return {
        "passed": (
            (not no_concerns["passed"])
            and (not no_trace["passed"])
            and restored["passed"]
        ),
        "no_concern_failures": no_concerns["failures"],
        "no_trace_failures": no_trace["failures"],
        "restored_failures": restored["failures"],
    }


def full_suite() -> dict:
    earned = earned_suite(CompactV9Character)
    historical = historical_regressions(CompactV9Character)
    development = development_suite(CompactV9Character)
    renderer = renderer_invariance(CompactV9Character)
    failures = list(earned["failures"])
    failures.extend(name for name, row in historical.items() if not row["passed"])
    failures.extend(name for name, row in development.items() if not row["passed"])
    if not renderer["passed"]:
        failures.append("renderer_invariance")
    return {"passed": not failures, "failures": sorted(set(failures))}


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


def mixed_benchmark(factory, repeats: int = 15, ticks: int = 2500) -> dict:
    samples = []
    for _ in range(repeats):
        agent = factory()
        start = perf_counter_ns()
        for index in range(ticks):
            if index % 29 == 0:
                agent.step(Event(kind="task_assign", concern=f"task_{index % 3}", forced_action="idle"))
            elif index % 31 == 0:
                agent.step(Event(kind="context", context="morning", available_actions=("walk", "tea")))
            elif index % 37 == 0:
                agent.step(Event(kind="outcome", reward=0.6, context="morning", forced_action="idle"))
            elif index % 41 == 0:
                agent.step(Event(kind="observed_reliable", actor="Alex", forced_action="idle"))
            elif index % 43 == 0:
                agent.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
            else:
                agent.step(Event(kind="neutral", available_actions=("work", "rest", "idle")))
        samples.append((perf_counter_ns() - start) / ticks / 1000.0)
    return distribution(samples)


def cost_comparison() -> dict:
    frozen = EligibilityTraceCharacter()
    compact = CompactV9Character()
    for agent in (frozen, compact):
        agent.step(Event(kind="task_assign", concern="finish_report", forced_action="idle"))
        agent.step(Event(kind="task_assign", concern="call_morgan", forced_action="idle"))
        agent.step(Event(kind="context", context="morning", forced_action="walk"))
        agent.step(Event(kind="support", actor="Alex", forced_action="idle"))
        agent.step(Event(kind="observed_reliable", actor="Alex", forced_action="idle"))
        agent.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    return {
        "frozen": {
            "mechanism_count": frozen.mechanism_count(),
            "fresh_bytes": EligibilityTraceCharacter().persistent_state_bytes(),
            "representative_bytes": frozen.persistent_state_bytes(),
            "exp006_benchmark": exp006_benchmark(EligibilityTraceCharacter),
            "mixed": mixed_benchmark(EligibilityTraceCharacter),
        },
        "compact": {
            "mechanism_count": compact.mechanism_count(),
            "fresh_bytes": CompactV9Character().persistent_state_bytes(),
            "representative_bytes": compact.persistent_state_bytes(),
            "exp006_benchmark": exp006_benchmark(CompactV9Character),
            "mixed": mixed_benchmark(CompactV9Character),
        },
    }


def run_review() -> dict:
    probes = {
        "no_duplicate_fields_in_object_state": no_duplicate_fields_in_object_state(),
        "matched_concern_sequences": matched_concern_sequences(),
        "prospective_to_concern_transition": prospective_to_concern_transition(),
        "immediate_and_delayed_learning_matrix": immediate_and_delayed_learning_matrix(),
        "noncontext_and_idle_controls": noncontext_and_idle_controls(),
        "same_context_ambiguity": same_context_ambiguity(),
        "reverse_ablation": reverse_ablation(),
        "full_suite": full_suite(),
    }
    failures = [name for name, row in probes.items() if not row["passed"]]
    return {
        "phase": "v9 structural compaction post-freeze review",
        "candidate_code_frozen_at": FROZEN_COMPACTION_CANDIDATE_COMMIT,
        "probe_count": len(probes),
        "failures": failures,
        "passed": not failures,
        "probes": probes,
        "cost": cost_comparison(),
    }


def compact_json(value):
    if isinstance(value, dict):
        return {str(k): compact_json(v) for k, v in value.items() if k not in {"trace", "traces"}}
    if isinstance(value, tuple):
        return [compact_json(v) for v in value]
    if isinstance(value, list):
        return [compact_json(v) for v in value]
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    report = compact_json(run_review())
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    raise SystemExit(0 if report["passed"] else 2)


if __name__ == "__main__":
    main()
