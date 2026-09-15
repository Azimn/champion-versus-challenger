from __future__ import annotations

import argparse
import json
from pathlib import Path

from .exp003_evaluation import probe_unknown_order, regression_suite
from .exp004_evaluation import probe_multiple_concerns
from .exp005_evaluation import probe_event_cued_commitment
from .exp006_challenger import SubjectiveFactCharacter
from .exp006_evaluation import benchmark as exp006_benchmark, probe_epistemic_history
from .runtime import Event


def factory() -> SubjectiveFactCharacter:
    return SubjectiveFactCharacter()


def habit(agent: SubjectiveFactCharacter, context: str, action: str) -> float:
    return float(agent.habits.get((context, action), 0.0))


def immediate_positive_control() -> dict:
    agent = factory()
    agent.step(Event(kind="context", context="morning", available_actions=("walk",)))
    agent.step(Event(kind="outcome", reward=1.0, forced_action="idle"))
    choice = agent.step(Event(kind="context", context="morning", available_actions=("tea", "walk")))
    return {
        "passed": choice == "walk" and habit(agent, "morning", "walk") > 0.0,
        "choice": choice,
        "walk_value": habit(agent, "morning", "walk"),
        "trace": agent.trace,
    }


def delayed_positive(delay: int) -> dict:
    agent = factory()
    agent.step(Event(kind="context", context="morning", available_actions=("walk",)))
    for _ in range(delay):
        agent.step(Event(kind="neutral", forced_action="idle"))
    agent.step(Event(kind="outcome", reward=1.0, context="morning", forced_action="idle"))
    value = habit(agent, "morning", "walk")
    choice = agent.step(Event(kind="context", context="morning", available_actions=("tea", "walk")))
    return {
        "passed": value > 0.0 and choice == "walk",
        "delay": delay,
        "walk_value": value,
        "choice": choice,
        "trace": agent.trace,
    }


def delayed_negative(delay: int) -> dict:
    agent = factory()
    # Establish a visible preference first so failure to apply delayed punishment is observable.
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


def intervening_context_steals_credit() -> dict:
    agent = factory()
    agent.step(Event(kind="context", context="morning", available_actions=("walk",)))
    agent.step(Event(kind="context", context="evening", available_actions=("tea",)))
    agent.step(Event(kind="outcome", reward=1.0, context="morning", forced_action="idle"))
    morning_walk = habit(agent, "morning", "walk")
    evening_tea = habit(agent, "evening", "tea")
    return {
        "passed": morning_walk > 0.0 and evening_tea == 0.0,
        "morning_walk": morning_walk,
        "evening_tea": evening_tea,
        "trace": agent.trace,
    }


def multiple_candidate_prior_actions() -> dict:
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


def cross_context_irrelevant_outcome() -> dict:
    agent = factory()
    agent.step(Event(kind="context", context="morning", available_actions=("walk",)))
    agent.step(Event(kind="outcome", reward=1.0, context="weather", forced_action="idle"))
    value = habit(agent, "morning", "walk")
    return {
        "passed": value == 0.0,
        "morning_walk": value,
        "trace": agent.trace,
    }


def characterize() -> dict:
    positive = {str(delay): delayed_positive(delay) for delay in (1, 3, 8)}
    negative = {str(delay): delayed_negative(delay) for delay in (1, 3, 8)}
    probes = {
        "immediate_positive_control": immediate_positive_control(),
        "delayed_positive": positive,
        "delayed_negative": negative,
        "intervening_context_steals_credit": intervening_context_steals_credit(),
        "multiple_candidate_prior_actions": multiple_candidate_prior_actions(),
        "irrelevant_cross_context_outcome": cross_context_irrelevant_outcome(),
    }
    return probes


def compact(value):
    if isinstance(value, dict):
        return {k: compact(v) for k, v in value.items() if k != "trace"}
    if isinstance(value, list):
        return [compact(v) for v in value]
    return value


def run_baseline() -> dict:
    regressions = regression_suite(factory)
    uncertainty = probe_unknown_order(factory)
    multiple = probe_multiple_concerns(factory)
    prospective = probe_event_cued_commitment(factory)
    epistemic = probe_epistemic_history(factory)
    cost = exp006_benchmark(factory)
    failure = characterize()

    prior_pass = (
        all(row["passed"] for row in regressions.values())
        and uncertainty["passed"]
        and multiple["passed"]
        and prospective["passed"]
        and epistemic["passed"]
    )
    mechanism_exact = cost["mechanism_count"] == 11
    state_reasonable = 430 <= cost["persistent_state_bytes"] <= 480
    runtime_reasonable = 8.0 <= cost["median_microseconds_per_tick"] <= 32.0
    delayed_failure_reproduced = (
        all(not row["passed"] for row in failure["delayed_positive"].values())
        and all(not row["passed"] for row in failure["delayed_negative"].values())
        and not failure["intervening_context_steals_credit"]["passed"]
        and not failure["multiple_candidate_prior_actions"]["passed"]
        and not failure["irrelevant_cross_context_outcome"]["passed"]
        and failure["immediate_positive_control"]["passed"]
    )
    baseline_verified = (
        prior_pass
        and mechanism_exact
        and state_reasonable
        and runtime_reasonable
        and delayed_failure_reproduced
    )
    return {
        "experiment": "EXP-007 frozen baseline and failure characterization",
        "champion": "v8_subjective_fact",
        "champion_modified": False,
        "prior_regressions": regressions,
        "exp003_uncertainty": uncertainty,
        "exp004_multiple_concerns": multiple,
        "exp005_prospective_cue": prospective,
        "exp006_subjective_fact": epistemic,
        "cost": cost,
        "recorded_reference": {
            "mechanism_count": 11,
            "representative_state_bytes_approx": 451,
            "median_microseconds_per_tick_approx": 16.1,
        },
        "failure_characterization": failure,
        "diagnosis": {
            "forgets_delayed_cause_after_neutral_interveners": True,
            "most_recent_context_action_can_steal_credit": True,
            "outcome_context_is_not_used_by_v8_habit_learning": True,
            "temporal_distance_1_3_8_all_fail": True,
            "existing_immediate_habit_learning_still_works": True,
        },
        "baseline_verified": baseline_verified,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    parser.add_argument("--compact-json", type=Path)
    args = parser.parse_args()
    report = run_baseline()
    print(json.dumps(compact(report), indent=2, sort_keys=True))
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.compact_json:
        args.compact_json.parent.mkdir(parents=True, exist_ok=True)
        args.compact_json.write_text(json.dumps(compact(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    raise SystemExit(0 if report["baseline_verified"] else 2)


if __name__ == "__main__":
    main()
