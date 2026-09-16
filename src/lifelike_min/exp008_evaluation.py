from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean, median, pstdev
from time import perf_counter_ns

from .exp007_evaluation import development_suite, historical_regressions, renderer_invariance
from .global_ablation_v9 import base_need_roles, earned_suite
from .runtime import Event
from .v9_1_compact import V91CompactCharacter
from .exp008_challenger import SearchExperiencePolicyCharacter


def habit(agent, context: str, action: str) -> float:
    return float(agent.habits.get((context, action), 0.0))


def experience_context(agent, actor: str, task: str) -> str:
    value = agent._search_experience_context(Event(kind="retrieve", actor=actor, context=task))
    assert value is not None
    return value


def repeated_failure(factory, actor="book", believed="drawer", alternate="shelf", task="find_book", failures=5):
    agent = factory()
    agent.step(Event(kind="observe_location", actor=actor, context=believed, forced_action="idle"))
    rows = []
    for index in range(failures):
        actions = (f"search:{believed}", f"search:{alternate}") if index % 2 == 0 else (f"search:{alternate}", f"search:{believed}")
        choice = agent.step(Event(kind="retrieve", actor=actor, context=task, available_actions=actions))
        agent.step(Event(kind="outcome", actor=actor, context=task, reward=-1.0, forced_action="idle"))
        if isinstance(agent, SearchExperiencePolicyCharacter):
            key_context = experience_context(agent, actor, task)
        else:
            key_context = task
        rows.append({"attempt": index + 1, "choice": choice, "value": habit(agent, key_context, f"search:{believed}"), "belief": agent.location_beliefs.get(actor)})
    final = agent.step(Event(kind="retrieve", actor=actor, context=task, available_actions=(f"search:{alternate}", f"search:{believed}")))
    return {"agent": agent, "rows": rows, "final": final}


def baseline_and_target() -> dict:
    champion = repeated_failure(V91CompactCharacter)
    challenger = repeated_failure(SearchExperiencePolicyCharacter)
    return {
        "passed": (
            champion["final"] == "search:drawer"
            and challenger["rows"][0]["choice"] == "search:drawer"
            and challenger["rows"][1]["choice"] == "search:drawer"
            and challenger["rows"][2]["choice"] == "search:drawer"
            and challenger["final"] == "search:shelf"
            and challenger["agent"].location_beliefs.get("book") == "drawer"
        ),
        "champion": {"rows": champion["rows"], "final": champion["final"]},
        "challenger": {"rows": challenger["rows"], "final": challenger["final"]},
    }


def accumulation_trajectory() -> dict:
    agent = SearchExperiencePolicyCharacter()
    actor, task = "book", "find_book"
    agent.step(Event(kind="observe_location", actor=actor, context="drawer", forced_action="idle"))
    choices = []
    values = []
    for _ in range(3):
        choice = agent.step(Event(kind="retrieve", actor=actor, context=task, available_actions=("search:shelf", "search:drawer")))
        choices.append(choice)
        agent.step(Event(kind="outcome", actor=actor, context=task, reward=-1.0, forced_action="idle"))
        values.append(habit(agent, experience_context(agent, actor, task), "search:drawer"))
    after_three = agent.step(Event(kind="retrieve", actor=actor, context=task, available_actions=("search:drawer", "search:shelf")))
    return {
        "passed": choices == ["search:drawer", "search:drawer", "search:drawer"] and values[0] < 0 and values[0] > values[1] > values[2] and after_three == "search:shelf",
        "choices_before_each_failure": choices,
        "values": values,
        "choice_after_three_failures": after_three,
    }


def positive_outcome_control() -> dict:
    agent = SearchExperiencePolicyCharacter()
    actor, task = "keys", "find_keys"
    agent.step(Event(kind="observe_location", actor=actor, context="hook", forced_action="idle"))
    for _ in range(3):
        agent.step(Event(kind="retrieve", actor=actor, context=task, forced_action="search:hook"))
        agent.step(Event(kind="outcome", actor=actor, context=task, reward=1.0, forced_action="idle"))
    value = habit(agent, experience_context(agent, actor, task), "search:hook")
    choice = agent.step(Event(kind="retrieve", actor=actor, context=task, available_actions=("search:table", "search:hook")))
    return {"passed": value > 0.0 and choice == "search:hook", "value": value, "choice": choice}


def reobservation_control() -> dict:
    result = repeated_failure(SearchExperiencePolicyCharacter, failures=3)
    agent = result["agent"]
    before = result["final"]
    agent.step(Event(kind="observe_location", actor="book", context="shelf", forced_action="idle"))
    after = agent.step(Event(kind="retrieve", actor="book", context="find_book", available_actions=("search:drawer", "search:shelf")))
    return {"passed": before == "search:shelf" and agent.location_beliefs["book"] == "shelf" and after == "search:shelf", "before": before, "after": after, "belief": agent.location_beliefs["book"]}


def entity_specificity() -> dict:
    agent = SearchExperiencePolicyCharacter()
    task = "find_object"
    for actor in ("book", "keys"):
        agent.step(Event(kind="observe_location", actor=actor, context="drawer", forced_action="idle"))
    for _ in range(3):
        agent.step(Event(kind="retrieve", actor="book", context=task, forced_action="search:drawer"))
        agent.step(Event(kind="outcome", actor="book", context=task, reward=-1.0, forced_action="idle"))
    book_choice = agent.step(Event(kind="retrieve", actor="book", context=task, available_actions=("search:drawer", "search:shelf")))
    keys_choice = agent.step(Event(kind="retrieve", actor="keys", context=task, available_actions=("search:shelf", "search:drawer")))
    return {
        "passed": book_choice == "search:shelf" and keys_choice == "search:drawer",
        "book_choice": book_choice,
        "keys_choice": keys_choice,
        "book_value": habit(agent, experience_context(agent, "book", task), "search:drawer"),
        "keys_value": habit(agent, experience_context(agent, "keys", task), "search:drawer"),
    }


def task_specificity() -> dict:
    agent = SearchExperiencePolicyCharacter()
    agent.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    for _ in range(3):
        agent.step(Event(kind="retrieve", actor="book", context="find_book_home", forced_action="search:drawer"))
        agent.step(Event(kind="outcome", actor="book", context="find_book_home", reward=-1.0, forced_action="idle"))
    home = agent.step(Event(kind="retrieve", actor="book", context="find_book_home", available_actions=("search:drawer", "search:shelf")))
    office = agent.step(Event(kind="retrieve", actor="book", context="find_book_office", available_actions=("search:shelf", "search:drawer")))
    return {"passed": home == "search:shelf" and office == "search:drawer", "home": home, "office": office}


def unknown_entity_control() -> dict:
    agent = SearchExperiencePolicyCharacter()
    initial = agent.step(Event(kind="retrieve", actor="map", context="find_map", available_actions=("search:desk", "search:shelf")))
    agent.step(Event(kind="retrieve", actor="map", context="find_map", forced_action="search:shelf"))
    agent.step(Event(kind="outcome", actor="map", context="find_map", reward=1.0, forced_action="idle"))
    learned = agent.step(Event(kind="retrieve", actor="map", context="find_map", available_actions=("search:desk", "search:shelf")))
    return {"passed": initial == "search:desk" and learned == "search:shelf" and "map" not in agent.location_beliefs, "initial": initial, "learned": learned, "location_beliefs": dict(agent.location_beliefs)}


def unlabeled_delayed_control() -> dict:
    agent = SearchExperiencePolicyCharacter()
    agent.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    agent.step(Event(kind="retrieve", actor="book", context="find_book", forced_action="search:drawer"))
    agent.step(Event(kind="neutral", forced_action="idle"))
    agent.step(Event(kind="outcome", context="find_book", reward=-1.0, forced_action="idle"))
    value = habit(agent, experience_context(agent, "book", "find_book"), "search:drawer")
    return {"passed": value == 0.0 and agent.location_beliefs["book"] == "drawer", "value": value, "belief": agent.location_beliefs["book"]}


def action_order_invariance() -> dict:
    def run(final_order):
        result = repeated_failure(SearchExperiencePolicyCharacter, failures=3)
        agent = result["agent"]
        return agent.step(Event(kind="retrieve", actor="book", context="find_book", available_actions=final_order))
    a = run(("search:drawer", "search:shelf"))
    b = run(("search:shelf", "search:drawer"))
    return {"passed": a == b == "search:shelf", "first": a, "second": b}


def contradictory_outcomes() -> dict:
    agent = SearchExperiencePolicyCharacter()
    actor, task, action = "book", "find_book", "search:drawer"
    agent.step(Event(kind="observe_location", actor=actor, context="drawer", forced_action="idle"))
    for _ in range(3):
        agent.step(Event(kind="retrieve", actor=actor, context=task, forced_action=action))
        agent.step(Event(kind="outcome", actor=actor, context=task, reward=-1.0, forced_action="idle"))
    negative = habit(agent, experience_context(agent, actor, task), action)
    avoidance = agent.step(Event(kind="retrieve", actor=actor, context=task, available_actions=(action, "search:shelf")))
    for _ in range(4):
        agent.step(Event(kind="retrieve", actor=actor, context=task, forced_action=action))
        agent.step(Event(kind="outcome", actor=actor, context=task, reward=1.0, forced_action="idle"))
    recovered = habit(agent, experience_context(agent, actor, task), action)
    return_choice = agent.step(Event(kind="retrieve", actor=actor, context=task, available_actions=("search:shelf", action)))
    return {"passed": negative < 0.0 and avoidance == "search:shelf" and recovered > negative and return_choice == action, "negative": negative, "avoidance": avoidance, "recovered": recovered, "return_choice": return_choice}


def delayed_outcome_compatibility() -> dict:
    agent = SearchExperiencePolicyCharacter()
    actor, task, action = "book", "find_book", "search:drawer"
    agent.step(Event(kind="observe_location", actor=actor, context="drawer", forced_action="idle"))
    agent.step(Event(kind="retrieve", actor=actor, context=task, forced_action=action))
    for _ in range(3):
        agent.step(Event(kind="neutral", forced_action="idle"))
    before = agent.snapshot()["eligibility_records"]
    agent.step(Event(kind="outcome", actor=actor, context=task, reward=-1.0, forced_action="idle"))
    value = habit(agent, experience_context(agent, actor, task), action)
    return {"passed": bool(before) and value < 0.0, "before": before, "value": value}


class NoSearchExperienceInteraction(SearchExperiencePolicyCharacter):
    def _score_action(self, action, event, immediate_threat, task_pressure):
        if action.startswith("search:"):
            return V91CompactCharacter._score_action(self, action, event, immediate_threat, task_pressure)
        return super()._score_action(action, event, immediate_threat, task_pressure)


class ContextBlindSearchExperience(SearchExperiencePolicyCharacter):
    @staticmethod
    def _search_experience_context(event: Event) -> str | None:
        if event.actor is None:
            return None
        return f"search_entity:{event.actor}"


class EntityBlindSearchExperience(SearchExperiencePolicyCharacter):
    @staticmethod
    def _search_experience_context(event: Event) -> str | None:
        if event.context is None:
            return None
        return f"search_task:{event.context}"


def ablations() -> dict:
    no_interaction = repeated_failure(NoSearchExperienceInteraction, failures=5)

    context_blind = ContextBlindSearchExperience()
    context_blind.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    for _ in range(3):
        context_blind.step(Event(kind="retrieve", actor="book", context="home", forced_action="search:drawer"))
        context_blind.step(Event(kind="outcome", actor="book", context="home", reward=-1.0, forced_action="idle"))
    context_blind_other_task = context_blind.step(Event(kind="retrieve", actor="book", context="office", available_actions=("search:drawer", "search:shelf")))

    entity_blind = EntityBlindSearchExperience()
    for actor in ("book", "keys"):
        entity_blind.step(Event(kind="observe_location", actor=actor, context="drawer", forced_action="idle"))
    for _ in range(3):
        entity_blind.step(Event(kind="retrieve", actor="book", context="find_object", forced_action="search:drawer"))
        entity_blind.step(Event(kind="outcome", actor="book", context="find_object", reward=-1.0, forced_action="idle"))
    entity_blind_keys = entity_blind.step(Event(kind="retrieve", actor="keys", context="find_object", available_actions=("search:drawer", "search:shelf")))

    return {
        "no_search_experience_interaction": {
            "passed_if_failure_returns": no_interaction["final"] == "search:drawer",
            "final": no_interaction["final"],
        },
        "context_blind_contaminates_other_task": {
            "passed_if_contamination_appears": context_blind_other_task == "search:shelf",
            "choice": context_blind_other_task,
        },
        "entity_blind_contaminates_other_entity": {
            "passed_if_contamination_appears": entity_blind_keys == "search:shelf",
            "choice": entity_blind_keys,
        },
    }


def serialization_continuity() -> dict:
    agent = SearchExperiencePolicyCharacter()
    result = repeated_failure(lambda: agent, failures=2)
    encoded = agent.serialize_persistent()
    restored = SearchExperiencePolicyCharacter.from_persistent_json(encoded)
    before = agent.persistent_snapshot() == restored.persistent_snapshot()
    continuation = [
        Event(kind="retrieve", actor="book", context="find_book", available_actions=("search:shelf", "search:drawer")),
        Event(kind="outcome", actor="book", context="find_book", reward=-1.0, forced_action="idle"),
        Event(kind="retrieve", actor="book", context="find_book", available_actions=("search:drawer", "search:shelf")),
    ]
    rows = []
    passed = before
    for event in continuation:
        aa = agent.step(event)
        bb = restored.step(event)
        same = agent.persistent_snapshot() == restored.persistent_snapshot()
        passed = passed and aa == bb and same
        rows.append({"event": event.kind, "action_original": aa, "action_restored": bb, "state_equal": same})
    return {"passed": passed, "before_equal": before, "continuation": rows, "serialized_bytes": len(encoded.encode("utf-8"))}


def distribution(values):
    return {"mean": mean(values), "median": median(values), "pstdev": pstdev(values), "min": min(values), "max": max(values), "n": len(values)}


def benchmark(factory, mode: str, repeats=15, ticks=1500):
    samples = []
    for _ in range(repeats):
        agent = factory()
        agent.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
        start = perf_counter_ns()
        for i in range(ticks):
            if mode == "search":
                if i % 2 == 0:
                    agent.step(Event(kind="retrieve", actor="book", context="find_book", available_actions=("search:drawer", "search:shelf")))
                else:
                    agent.step(Event(kind="outcome", actor="book", context="find_book", reward=-0.2, forced_action="idle"))
            elif mode == "mixed" and i % 11 == 0:
                agent.step(Event(kind="retrieve", actor="book", context="find_book", available_actions=("search:drawer", "search:shelf")))
            elif mode == "mixed" and i % 11 == 1:
                agent.step(Event(kind="outcome", actor="book", context="find_book", reward=-0.2, forced_action="idle"))
            else:
                agent.step(Event(kind="neutral", forced_action="idle"))
        samples.append((perf_counter_ns() - start) / ticks / 1000.0)
    return distribution(samples)


def state_cost() -> dict:
    champion = V91CompactCharacter()
    challenger = SearchExperiencePolicyCharacter()
    for agent in (champion, challenger):
        agent.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
        agent.step(Event(kind="retrieve", actor="book", context="find_book", forced_action="search:drawer"))
        agent.step(Event(kind="outcome", actor="book", context="find_book", reward=-1.0, forced_action="idle"))
    return {
        "champion": {"mechanisms": champion.mechanism_count(), "fresh_bytes": V91CompactCharacter().persistent_state_bytes(), "search_history_bytes": champion.persistent_state_bytes()},
        "challenger": {"mechanisms": challenger.mechanism_count(), "fresh_bytes": SearchExperiencePolicyCharacter().persistent_state_bytes(), "search_history_bytes": challenger.persistent_state_bytes()},
        "object_fields_equal": set(V91CompactCharacter().__dict__) == set(SearchExperiencePolicyCharacter().__dict__),
    }


def run() -> dict:
    development = {
        "baseline_and_target": baseline_and_target(),
        "accumulation_trajectory": accumulation_trajectory(),
        "positive_outcome_control": positive_outcome_control(),
        "reobservation_control": reobservation_control(),
        "entity_specificity": entity_specificity(),
        "task_specificity": task_specificity(),
        "unknown_entity_control": unknown_entity_control(),
        "unlabeled_delayed_control": unlabeled_delayed_control(),
        "action_order_invariance": action_order_invariance(),
        "contradictory_outcomes": contradictory_outcomes(),
        "delayed_outcome_compatibility": delayed_outcome_compatibility(),
    }
    historical = historical_regressions(SearchExperiencePolicyCharacter)
    exp007 = development_suite(SearchExperiencePolicyCharacter)
    earned = earned_suite(SearchExperiencePolicyCharacter)
    renderer = renderer_invariance(SearchExperiencePolicyCharacter)
    base_needs = base_need_roles(SearchExperiencePolicyCharacter)
    causal = ablations()
    persistence = serialization_continuity()
    cost = state_cost()
    gates = {
        "development": all(row["passed"] for row in development.values()),
        "historical": all(row["passed"] for row in historical.values()),
        "exp007": all(row["passed"] for row in exp007.values()),
        "earned": earned["passed"],
        "renderer": renderer["passed"],
        "base_needs": all(base_needs[key] for key in ("fatigue_drives_rest", "affiliation_drives_unscripted_social_approach", "competence_drives_work_after_rest")),
        "ablations": all(row[next(key for key in row if key.startswith("passed_"))] for row in causal.values()),
        "serialization": persistence["passed"],
        "zero_new_fields": cost["object_fields_equal"],
        "zero_new_mechanisms": cost["challenger"]["mechanisms"] == cost["champion"]["mechanisms"],
    }
    return {
        "experiment": "EXP-008 development evaluation",
        "pre_registration_commit": "82812de89b512e3cb2ecc0f12c357b534086922d",
        "champion": "v9.1_compact",
        "challenger": "search_experience_policy_candidate",
        "gates": gates,
        "passed": all(gates.values()),
        "development": development,
        "historical_failures": [name for name, row in historical.items() if not row["passed"]],
        "exp007_failures": [name for name, row in exp007.items() if not row["passed"]],
        "earned": earned,
        "renderer": renderer,
        "base_needs": base_needs,
        "ablations": causal,
        "serialization": persistence,
        "cost": cost,
        "timing": {
            "champion_search": benchmark(V91CompactCharacter, "search"),
            "challenger_search": benchmark(SearchExperiencePolicyCharacter, "search"),
            "champion_mixed": benchmark(V91CompactCharacter, "mixed"),
            "challenger_mixed": benchmark(SearchExperiencePolicyCharacter, "mixed"),
            "interpretation": "Hosted CI microbenchmarks are engineering estimates; do not treat overlapping distributions as a speed claim.",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    report = run()
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    raise SystemExit(0 if report["passed"] else 2)


if __name__ == "__main__":
    main()
