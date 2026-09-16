from __future__ import annotations

import argparse
import json
from pathlib import Path

from .exp008_challenger import SearchExperiencePolicyCharacter
from .exp008_evaluation import experience_context, habit
from .runtime import Event


PRODUCTION_FROZEN_AT = "c42a43d353b21061b97cabb665e8ef59544d27c9"


def learn(agent, actor: str, task: str, location: str, reward: float, repeats: int = 1) -> float:
    action = f"search:{location}"
    for _ in range(repeats):
        agent.step(Event(kind="retrieve", actor=actor, context=task, forced_action=action))
        agent.step(Event(kind="outcome", actor=actor, context=task, reward=reward, forced_action="idle"))
    return habit(agent, experience_context(agent, actor, task), action)


def direct_observation_clears_only_matching_negative() -> dict:
    agent = SearchExperiencePolicyCharacter()
    actor = "book"
    agent.step(Event(kind="observe_location", actor=actor, context="drawer", forced_action="idle"))
    drawer = learn(agent, actor, "find_home", "drawer", -1.0, 2)
    shelf = learn(agent, actor, "find_home", "shelf", -1.0, 2)
    before = dict(agent.habits)
    agent.step(Event(kind="observe_location", actor=actor, context="drawer", forced_action="idle"))
    drawer_after = habit(agent, experience_context(agent, actor, "find_home"), "search:drawer")
    shelf_after = habit(agent, experience_context(agent, actor, "find_home"), "search:shelf")
    return {
        "passed": drawer < 0.0 and shelf < 0.0 and drawer_after == 0.0 and shelf_after < 0.0,
        "before": {str(k): v for k, v in before.items()},
        "drawer_after": drawer_after,
        "shelf_after": shelf_after,
        "claim": "Direct observation of one location should invalidate negative search experience for that entity/location only, not another location.",
    }


def positive_experience_survives_observation() -> dict:
    agent = SearchExperiencePolicyCharacter()
    actor, task, location = "keys", "find_keys", "hook"
    positive = learn(agent, actor, task, location, 1.0, 2)
    agent.step(Event(kind="observe_location", actor=actor, context=location, forced_action="idle"))
    after = habit(agent, experience_context(agent, actor, task), f"search:{location}")
    return {
        "passed": positive > 0.0 and after == positive,
        "before": positive,
        "after": after,
        "claim": "Fresh direct perception should not erase compatible positive search experience.",
    }


def other_actor_negative_survives() -> dict:
    agent = SearchExperiencePolicyCharacter()
    value_book = learn(agent, "book", "find_object", "drawer", -1.0, 2)
    value_keys = learn(agent, "keys", "find_object", "drawer", -1.0, 2)
    agent.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    book_after = habit(agent, experience_context(agent, "book", "find_object"), "search:drawer")
    keys_after = habit(agent, experience_context(agent, "keys", "find_object"), "search:drawer")
    return {
        "passed": value_book < 0 and value_keys < 0 and book_after == 0.0 and keys_after == value_keys,
        "book_after": book_after,
        "keys_after": keys_after,
        "claim": "One entity's observation must not clear another entity's search experience at the same physical location.",
    }


def non_search_habit_survives() -> dict:
    agent = SearchExperiencePolicyCharacter()
    agent.habits[("morning", "walk")] = -0.7
    search_value = learn(agent, "book", "find_book", "drawer", -1.0, 2)
    agent.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    return {
        "passed": search_value < 0.0 and agent.habits.get(("morning", "walk")) == -0.7,
        "non_search_value": agent.habits.get(("morning", "walk")),
        "claim": "Search-specific evidence invalidation must not erase unrelated learned routines.",
    }


def hidden_world_change_does_not_clear() -> dict:
    agent = SearchExperiencePolicyCharacter()
    actor, task, location = "book", "find_book", "drawer"
    negative = learn(agent, actor, task, location, -1.0, 2)
    agent.step(Event(kind="hidden_world_change", actor=actor, context=location, forced_action="idle"))
    after = habit(agent, experience_context(agent, actor, task), f"search:{location}")
    return {
        "passed": negative < 0.0 and after == negative,
        "before": negative,
        "after": after,
        "claim": "Privileged hidden-world changes must not invalidate subject-owned search experience.",
    }


def unicode_actor_cleanup_is_specific() -> dict:
    agent = SearchExperiencePolicyCharacter()
    actor_a = "book|α;%"
    actor_b = "book|β;%"
    task = "find|thing;%"
    a = learn(agent, actor_a, task, "drawer", -1.0, 2)
    b = learn(agent, actor_b, task, "drawer", -1.0, 2)
    agent.step(Event(kind="observe_location", actor=actor_a, context="drawer", forced_action="idle"))
    a_after = habit(agent, experience_context(agent, actor_a, task), "search:drawer")
    b_after = habit(agent, experience_context(agent, actor_b, task), "search:drawer")
    return {
        "passed": a < 0 and b < 0 and a_after == 0.0 and b_after == b,
        "actor_a_after": a_after,
        "actor_b_after": b_after,
        "claim": "Encoded actor identity must remain exact when invalidating stale negative experience.",
    }


def direct_observation_clears_same_location_across_tasks() -> dict:
    agent = SearchExperiencePolicyCharacter()
    actor, location = "book", "drawer"
    home = learn(agent, actor, "find_book_home", location, -1.0, 2)
    office = learn(agent, actor, "find_book_office", location, -1.0, 2)
    agent.step(Event(kind="observe_location", actor=actor, context=location, forced_action="idle"))
    home_after = habit(agent, experience_context(agent, actor, "find_book_home"), "search:drawer")
    office_after = habit(agent, experience_context(agent, actor, "find_book_office"), "search:drawer")
    return {
        "passed": home < 0 and office < 0 and home_after == 0.0 and office_after == 0.0,
        "home_after": home_after,
        "office_after": office_after,
        "claim": "Fresh direct location evidence is about the entity/location, so stale negative searches for that same pair should be invalidated across search-task contexts.",
    }


def delayed_old_negative_after_observation_is_proportionate() -> dict:
    agent = SearchExperiencePolicyCharacter()
    actor, task = "book", "find_book"
    agent.step(Event(kind="observe_location", actor=actor, context="drawer", forced_action="idle"))
    # Create one eligible search, then reobserve before the delayed outcome arrives.
    agent.step(Event(kind="retrieve", actor=actor, context=task, forced_action="search:drawer"))
    agent.step(Event(kind="neutral", forced_action="idle"))
    agent.step(Event(kind="observe_location", actor=actor, context="drawer", forced_action="idle"))
    agent.step(Event(kind="outcome", actor=actor, context=task, reward=-1.0, forced_action="idle"))
    value = habit(agent, experience_context(agent, actor, task), "search:drawer")
    choice = agent.step(Event(kind="retrieve", actor=actor, context=task, available_actions=("search:shelf", "search:drawer")))
    return {
        "passed": value < 0.0 and value > -0.85 and choice == "search:drawer",
        "value": value,
        "choice": choice,
        "claim": "A single delayed old failure arriving after fresh direct observation may reduce confidence in the search action but should not automatically overpower the fresh direct-location prior.",
    }


def invalidation_survives_serialization() -> dict:
    agent = SearchExperiencePolicyCharacter()
    actor, task = "book", "find_book"
    learn(agent, actor, task, "drawer", -1.0, 3)
    agent.step(Event(kind="observe_location", actor=actor, context="drawer", forced_action="idle"))
    encoded = agent.serialize_persistent()
    restored = SearchExperiencePolicyCharacter.from_persistent_json(encoded)
    key = experience_context(agent, actor, task)
    return {
        "passed": (
            habit(agent, key, "search:drawer") == 0.0
            and habit(restored, key, "search:drawer") == 0.0
            and agent.persistent_snapshot() == restored.persistent_snapshot()
        ),
        "serialized_bytes": len(encoded.encode("utf-8")),
        "claim": "The invalidated state must remain invalidated after runtime reconstruction.",
    }


def direct_observation_does_not_clear_live_trace() -> dict:
    agent = SearchExperiencePolicyCharacter()
    actor, task = "book", "find_book"
    agent.step(Event(kind="retrieve", actor=actor, context=task, forced_action="search:drawer"))
    before = list(agent.snapshot()["eligibility_records"])
    agent.step(Event(kind="observe_location", actor=actor, context="drawer", forced_action="idle"))
    after = list(agent.snapshot()["eligibility_records"])
    return {
        "passed": bool(before) and bool(after),
        "before": before,
        "after": after,
        "claim": "The minimal repair should not silently erase eligibility evidence; it invalidates learned negative value only.",
    }


def run_review() -> dict:
    probes = {
        "matching_negative_only": direct_observation_clears_only_matching_negative(),
        "positive_survives": positive_experience_survives_observation(),
        "other_actor_survives": other_actor_negative_survives(),
        "non_search_survives": non_search_habit_survives(),
        "hidden_world_does_not_clear": hidden_world_change_does_not_clear(),
        "unicode_actor_specificity": unicode_actor_cleanup_is_specific(),
        "same_location_across_tasks": direct_observation_clears_same_location_across_tasks(),
        "delayed_old_negative_proportionate": delayed_old_negative_after_observation_is_proportionate(),
        "serialization_after_invalidation": invalidation_survives_serialization(),
        "live_trace_not_erased": direct_observation_does_not_clear_live_trace(),
    }
    failures = [name for name, row in probes.items() if not row["passed"]]
    return {
        "experiment": "EXP-008 second adversarial reviewer generation",
        "created_after_repair_freeze": True,
        "production_frozen_at": PRODUCTION_FROZEN_AT,
        "probe_count": len(probes),
        "failures": failures,
        "reviewer_passed": not failures,
        "probes": probes,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    report = run_review()
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    raise SystemExit(0 if report["reviewer_passed"] else 2)


if __name__ == "__main__":
    main()
