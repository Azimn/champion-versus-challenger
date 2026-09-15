from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import median
from time import perf_counter_ns
from typing import Callable

from .exp003_evaluation import probe_unknown_order, regression_suite
from .exp004_evaluation import probe_multiple_concerns
from .exp005_evaluation import probe_event_cued_commitment
from .exp006_challenger import SubjectiveFactCharacter
from .exp006_evaluation import probe_epistemic_history
from .exp007_challenger import EligibilityRecord, EligibilityTraceCharacter
from .runtime import Event, PersistentCharacter
from .surface import SurfaceRenderer


Factory = Callable[[], PersistentCharacter]


def champion_factory() -> PersistentCharacter:
    return SubjectiveFactCharacter()


def challenger_factory() -> PersistentCharacter:
    return EligibilityTraceCharacter()


def habit(agent: PersistentCharacter, context: str, action: str) -> float:
    return float(agent.habits.get((context, action), 0.0))


def delayed_positive(factory: Factory, delay: int, context: str = "morning", action: str = "walk") -> dict:
    agent = factory()
    agent.step(Event(kind="context", context=context, available_actions=(action,)))
    eligibility_after_action = agent.snapshot().get("eligibility_records", [])
    for _ in range(delay):
        agent.step(Event(kind="neutral", forced_action="idle"))
    before_outcome = agent.snapshot().get("eligibility_records", [])
    agent.step(Event(kind="outcome", reward=1.0, context=context, forced_action="idle"))
    value = habit(agent, context, action)
    choice = agent.step(Event(kind="context", context=context, available_actions=("tea", action)))
    return {
        "passed": value > 0.0 and choice == action,
        "delay": delay,
        "learned_value": value,
        "choice": choice,
        "eligibility_after_action": eligibility_after_action,
        "eligibility_before_outcome": before_outcome,
        "trace": agent.trace,
    }


def delayed_negative(factory: Factory, delay: int) -> dict:
    agent = factory()
    for _ in range(3):
        agent.step(Event(kind="context", context="morning", available_actions=("walk",)))
        agent.step(Event(kind="outcome", reward=1.0, forced_action="idle"))
    before = habit(agent, "morning", "walk")
    agent.step(Event(kind="context", context="morning", forced_action="walk"))
    for _ in range(delay):
        agent.step(Event(kind="neutral", forced_action="idle"))
    agent.step(Event(kind="outcome", reward=-1.0, context="morning", forced_action="idle"))
    after = habit(agent, "morning", "walk")
    return {
        "passed": after < before,
        "delay": delay,
        "before": before,
        "after": after,
        "trace": agent.trace,
    }


def cross_context(factory: Factory) -> dict:
    agent = factory()
    agent.step(Event(kind="context", context="morning", available_actions=("walk",)))
    agent.step(Event(kind="context", context="evening", available_actions=("tea",)))
    agent.step(Event(kind="outcome", reward=1.0, context="morning", forced_action="idle"))
    morning = habit(agent, "morning", "walk")
    evening = habit(agent, "evening", "tea")
    return {
        "passed": morning > 0.0 and evening == 0.0,
        "morning_walk": morning,
        "evening_tea": evening,
        "trace": agent.trace,
    }


def multiple_candidates(factory: Factory) -> dict:
    agent = factory()
    agent.step(Event(kind="context", context="morning", available_actions=("walk",)))
    agent.step(Event(kind="context", context="library", available_actions=("read",)))
    agent.step(Event(kind="neutral", forced_action="idle"))
    agent.step(Event(kind="outcome", reward=1.0, context="morning", forced_action="idle"))
    return {
        "passed": habit(agent, "morning", "walk") > 0.0 and habit(agent, "library", "read") == 0.0,
        "morning_walk": habit(agent, "morning", "walk"),
        "library_read": habit(agent, "library", "read"),
        "trace": agent.trace,
    }


def irrelevant_outcome(factory: Factory) -> dict:
    agent = factory()
    agent.step(Event(kind="context", context="morning", available_actions=("walk",)))
    agent.step(Event(kind="outcome", reward=1.0, context="weather", forced_action="idle"))
    return {
        "passed": habit(agent, "morning", "walk") == 0.0,
        "morning_walk": habit(agent, "morning", "walk"),
        "trace": agent.trace,
    }


def immediate_control(factory: Factory) -> dict:
    agent = factory()
    agent.step(Event(kind="context", context="morning", available_actions=("walk",)))
    agent.step(Event(kind="outcome", reward=1.0, forced_action="idle"))
    value = habit(agent, "morning", "walk")
    return {"passed": value == 0.35, "walk_value": value, "trace": agent.trace}


def expired_trace(factory: Factory) -> dict:
    agent = factory()
    agent.step(Event(kind="context", context="morning", available_actions=("walk",)))
    for _ in range(11):
        agent.step(Event(kind="neutral", forced_action="idle"))
    before = agent.snapshot().get("eligibility_records", [])
    agent.step(Event(kind="outcome", reward=1.0, context="morning", forced_action="idle"))
    return {
        "passed": habit(agent, "morning", "walk") == 0.0 and not before,
        "before_outcome": before,
        "walk_value": habit(agent, "morning", "walk"),
        "trace": agent.trace,
    }


def bounded_capacity(factory: Factory) -> dict:
    agent = factory()
    for index in range(8):
        agent.step(
            Event(
                kind="context",
                context=f"ctx_{index}",
                available_actions=(f"act_{index}",),
            )
        )
    rows = agent.snapshot().get("eligibility_records", [])
    return {
        "passed": len(rows) <= 4,
        "count": len(rows),
        "rows": rows,
        "trace": agent.trace,
    }


def action_order_invariance(factory: Factory) -> dict:
    choices = []
    traces = []
    for order in (("tea", "walk"), ("walk", "tea")):
        agent = factory()
        agent.step(Event(kind="context", context="morning", available_actions=("walk",)))
        for _ in range(3):
            agent.step(Event(kind="neutral", forced_action="idle"))
        agent.step(Event(kind="outcome", reward=1.0, context="morning", forced_action="idle"))
        choices.append(agent.step(Event(kind="context", context="morning", available_actions=order)))
        traces.append(agent.trace)
    return {"passed": choices == ["walk", "walk"], "choices": choices, "traces": traces}


def renderer_invariance(factory: Factory) -> dict:
    left = factory()
    right = factory()
    renderer = SurfaceRenderer()
    events = [
        Event(kind="context", context="garden", available_actions=("water",)),
        Event(kind="neutral", forced_action="idle"),
        Event(kind="neutral", forced_action="idle"),
        Event(kind="outcome", reward=1.0, context="garden", forced_action="idle"),
        Event(kind="context", context="garden", available_actions=("read", "water")),
    ]
    left_actions = []
    right_actions = []
    rendered = []
    for event in events:
        left_actions.append(left.step(event))
        action = right.step(event)
        right_actions.append(action)
        rendered.append(renderer.render_action(action))
    return {
        "passed": left_actions == right_actions and left.snapshot() == right.snapshot(),
        "left_actions": left_actions,
        "right_actions": right_actions,
        "rendered": rendered,
    }


def historical_regressions(factory: Factory) -> dict:
    old = regression_suite(factory)
    old["uncertainty_order"] = probe_unknown_order(factory)
    old["multiple_concerns"] = probe_multiple_concerns(factory)
    old["prospective_cue"] = probe_event_cued_commitment(factory)
    old["subjective_fact"] = probe_epistemic_history(factory)
    old["eligibility_renderer_invariance"] = renderer_invariance(factory)
    return old


class DisabledEligibilityCharacter(EligibilityTraceCharacter):
    max_eligibility_records = 0


class ImmediateExpiryCharacter(EligibilityTraceCharacter):
    max_eligibility_age = 0


class ContextBlindCharacter(EligibilityTraceCharacter):
    def _context_candidates(self, context: str) -> list[EligibilityRecord]:
        del context
        return list(self.eligibility_records)


class NoDecayCharacter(EligibilityTraceCharacter):
    eligibility_decay = 1.0


class LargeCapacityCharacter(EligibilityTraceCharacter):
    max_eligibility_records = 1000


class NoActionIdentityCharacter(EligibilityTraceCharacter):
    def _create_eligibility(self, context: str, action: str) -> None:
        super()._create_eligibility(context, "*")


def ablation_context_leak(factory: Factory) -> dict:
    agent = factory()
    agent.step(Event(kind="context", context="evening", available_actions=("tea",)))
    agent.step(Event(kind="outcome", reward=1.0, context="morning", forced_action="idle"))
    wrong = habit(agent, "evening", "tea")
    return {"passed": wrong == 0.0, "wrong_context_value": wrong, "trace": agent.trace}


def ablation_decay_gradient(factory: Factory) -> dict:
    short = delayed_positive(factory, 1)["learned_value"]
    long = delayed_positive(factory, 8)["learned_value"]
    return {"passed": short > long > 0.0, "delay_1_value": short, "delay_8_value": long}


def ablation_capacity_growth(factory: Factory) -> dict:
    agent = factory()
    for index in range(100):
        agent.step(
            Event(
                kind="context",
                context=f"capacity_{index}",
                available_actions=(f"action_{index}",),
            )
        )
    rows = agent.snapshot().get("eligibility_records", [])
    return {"count": len(rows), "state_bytes": agent.persistent_state_bytes()}


def run_ablations() -> dict:
    disabled = delayed_positive(DisabledEligibilityCharacter, 3)
    expired = delayed_positive(ImmediateExpiryCharacter, 3)
    normal_leak = ablation_context_leak(EligibilityTraceCharacter)
    blind_leak = ablation_context_leak(ContextBlindCharacter)
    normal_gradient = ablation_decay_gradient(EligibilityTraceCharacter)
    no_decay_gradient = ablation_decay_gradient(NoDecayCharacter)
    bounded = ablation_capacity_growth(EligibilityTraceCharacter)
    unbounded = ablation_capacity_growth(LargeCapacityCharacter)
    no_action = delayed_positive(NoActionIdentityCharacter, 3)
    return {
        "eligibility_disabled": {
            "passed_if_improvement_disappears": not disabled["passed"],
            "probe": disabled,
        },
        "immediate_expiry": {
            "passed_if_improvement_disappears": not expired["passed"],
            "probe": expired,
        },
        "context_specificity": {
            "normal": normal_leak,
            "context_blind": blind_leak,
            "diagnostic_passed": normal_leak["passed"] and not blind_leak["passed"],
        },
        "decay": {
            "normal": normal_gradient,
            "no_decay": no_decay_gradient,
            "diagnostic_passed": normal_gradient["passed"] and not no_decay_gradient["passed"],
        },
        "capacity": {
            "bounded": bounded,
            "large_capacity": unbounded,
            "diagnostic_passed": bounded["count"] <= 4 and unbounded["count"] > bounded["count"],
        },
        "action_identity": {
            "passed_if_improvement_disappears": not no_action["passed"],
            "probe": no_action,
        },
    }


def benchmark(factory: Factory, repeats: int = 7, ticks: int = 4000) -> dict:
    samples = []
    for _ in range(repeats):
        agent = factory()
        start = perf_counter_ns()
        for index in range(ticks):
            slot = index % 12
            if slot == 0:
                agent.step(Event(kind="context", context="morning", available_actions=("walk", "tea")))
            elif slot == 4:
                agent.step(Event(kind="outcome", reward=1.0, context="morning", forced_action="idle"))
            elif slot == 6:
                agent.step(Event(kind="context", context="library", available_actions=("read", "idle")))
            elif slot == 10:
                agent.step(Event(kind="outcome", reward=-0.5, context="library", forced_action="idle"))
            else:
                agent.step(Event(kind="neutral", forced_action="idle"))
        samples.append((perf_counter_ns() - start) / ticks / 1000.0)

    representative = factory()
    representative.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    representative.step(Event(kind="task_assign", concern="finish_report", forced_action="idle"))
    representative.step(Event(kind="future_commitment", concern="call_morgan", context="morgan_arrives", forced_action="idle"))
    representative.step(Event(kind="support", actor="Alex", forced_action="idle"))
    representative.step(Event(kind="observed_reliable", actor="Alex", forced_action="idle"))
    representative.step(Event(kind="context", context="morning", available_actions=("walk",)))
    representative.step(Event(kind="neutral", forced_action="idle"))
    return {
        "median_microseconds_per_tick": round(median(samples), 4),
        "persistent_state_bytes": representative.persistent_state_bytes(),
        "mechanism_count": representative.mechanism_count(),
    }


def event_processing_cost(factory: Factory, repeats: int = 9, batches: int = 2000) -> dict:
    create_samples = []
    outcome_samples = []
    for _ in range(repeats):
        agent = factory()
        start = perf_counter_ns()
        for index in range(batches):
            agent.step(Event(kind="context", context=f"c{index % 3}", forced_action="walk"))
        create_samples.append((perf_counter_ns() - start) / batches / 1000.0)

        agent = factory()
        for index in range(3):
            agent.step(Event(kind="context", context=f"c{index}", forced_action="walk"))
        start = perf_counter_ns()
        for index in range(batches):
            agent.step(Event(kind="outcome", context=f"c{index % 3}", reward=0.2, forced_action="idle"))
        outcome_samples.append((perf_counter_ns() - start) / batches / 1000.0)
    return {
        "context_action_us": round(median(create_samples), 4),
        "outcome_us": round(median(outcome_samples), 4),
    }


def development_suite(factory: Factory) -> dict:
    return {
        "delayed_positive_1": delayed_positive(factory, 1),
        "delayed_positive_3": delayed_positive(factory, 3),
        "delayed_positive_8": delayed_positive(factory, 8),
        "delayed_negative_1": delayed_negative(factory, 1),
        "delayed_negative_3": delayed_negative(factory, 3),
        "delayed_negative_8": delayed_negative(factory, 8),
        "cross_context": cross_context(factory),
        "multiple_candidates": multiple_candidates(factory),
        "irrelevant_outcome": irrelevant_outcome(factory),
        "immediate_control": immediate_control(factory),
        "expired_trace": expired_trace(factory),
        "bounded_capacity": bounded_capacity(factory),
        "action_order_invariance": action_order_invariance(factory),
    }


def compact(value):
    if isinstance(value, dict):
        return {k: compact(v) for k, v in value.items() if k not in {"trace", "traces"}}
    if isinstance(value, list):
        return [compact(v) for v in value]
    return value


def run_evaluation() -> dict:
    champion = development_suite(champion_factory)
    challenger = development_suite(challenger_factory)
    regressions = historical_regressions(challenger_factory)
    ablations = run_ablations()
    champion_cost = benchmark(champion_factory)
    challenger_cost = benchmark(challenger_factory)
    overhead = {
        "champion": event_processing_cost(champion_factory),
        "challenger": event_processing_cost(challenger_factory),
    }

    champion_target_failures = [name for name, row in champion.items() if name != "immediate_control" and not row["passed"]]
    challenger_passed = all(row["passed"] for row in challenger.values())
    regressions_passed = all(row["passed"] for row in regressions.values())
    ablation_passed = (
        ablations["eligibility_disabled"]["passed_if_improvement_disappears"]
        and ablations["immediate_expiry"]["passed_if_improvement_disappears"]
        and ablations["context_specificity"]["diagnostic_passed"]
        and ablations["decay"]["diagnostic_passed"]
        and ablations["capacity"]["diagnostic_passed"]
        and ablations["action_identity"]["passed_if_improvement_disappears"]
    )
    initial_gate = (
        len(champion_target_failures) >= 1
        and champion["immediate_control"]["passed"]
        and challenger_passed
        and regressions_passed
        and ablation_passed
        and challenger_cost["mechanism_count"] == champion_cost["mechanism_count"] + 1
    )
    return {
        "experiment": "EXP-007 delayed consequence credit",
        "phase": "developer matched evaluation before reviewer holdouts",
        "champion": "v8_subjective_fact",
        "challenger": "v9_eligibility_trace_candidate",
        "champion_development_suite": champion,
        "challenger_development_suite": challenger,
        "historical_regressions": regressions,
        "ablations": ablations,
        "cost": {"champion": champion_cost, "challenger": challenger_cost, "event_processing": overhead},
        "champion_target_failures": champion_target_failures,
        "initial_developer_gate": initial_gate,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    parser.add_argument("--compact-json", type=Path)
    args = parser.parse_args()
    report = run_evaluation()
    print(json.dumps(compact(report), indent=2, sort_keys=True))
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.compact_json:
        args.compact_json.parent.mkdir(parents=True, exist_ok=True)
        args.compact_json.write_text(json.dumps(compact(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    raise SystemExit(0 if report["initial_developer_gate"] else 2)


if __name__ == "__main__":
    main()
