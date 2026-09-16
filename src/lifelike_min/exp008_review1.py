from __future__ import annotations

import argparse
import json
from pathlib import Path

from .exp008_challenger import SearchExperiencePolicyCharacter
from .exp008_evaluation import experience_context, habit
from .runtime import Event


PRODUCTION_FROZEN_AT = "ec269c949e2334c0df4ec2f9c5f55c8a202e1ac7"


def fresh_same_location_reobservation() -> dict:
    agent = SearchExperiencePolicyCharacter()
    actor, task, action = "book", "find_book", "search:drawer"
    agent.step(Event(kind="observe_location", actor=actor, context="drawer", forced_action="idle"))
    for _ in range(3):
        agent.step(Event(kind="retrieve", actor=actor, context=task, forced_action=action))
        agent.step(Event(kind="outcome", actor=actor, context=task, reward=-1.0, forced_action="idle"))
    negative = habit(agent, experience_context(agent, actor, task), action)
    before = agent.step(Event(kind="retrieve", actor=actor, context=task, available_actions=(action, "search:shelf")))

    # The subject now directly sees the book in the drawer again. This is newer and
    # more direct evidence than the old failed-search experience.
    agent.step(Event(kind="observe_location", actor=actor, context="drawer", forced_action="idle"))
    after = agent.step(Event(kind="retrieve", actor=actor, context=task, available_actions=("search:shelf", action)))
    return {
        "passed": negative < 0.0 and before == "search:shelf" and after == action,
        "negative_value": negative,
        "before_reobservation": before,
        "after_fresh_same_location_observation": after,
        "belief": agent.location_beliefs.get(actor),
        "failure_claim": "A fresh direct perception of the entity at the previously failed location should not be overruled indefinitely by stale failed-search experience.",
    }


def delimiter_and_unicode_roundtrip() -> dict:
    actor = "book|α;%"
    task = "find|book;room:%"
    location = "drawer"
    agent = SearchExperiencePolicyCharacter()
    agent.step(Event(kind="observe_location", actor=actor, context=location, forced_action="idle"))
    agent.step(Event(kind="retrieve", actor=actor, context=task, forced_action=f"search:{location}"))
    agent.step(Event(kind="outcome", actor=actor, context=task, reward=-1.0, forced_action="idle"))
    key = experience_context(agent, actor, task)
    value = habit(agent, key, f"search:{location}")
    encoded = agent.serialize_persistent()
    restored = SearchExperiencePolicyCharacter.from_persistent_json(encoded)
    restored_value = habit(restored, key, f"search:{location}")
    return {
        "passed": value < 0.0 and restored_value == value and restored.persistent_snapshot() == agent.persistent_snapshot() and "|" not in key,
        "derived_context": key,
        "value": value,
        "restored_value": restored_value,
        "failure_claim": "Actor/task names containing persistence delimiters or Unicode must remain losslessly isolated and serializable.",
    }


def actor_mismatch_abstains() -> dict:
    agent = SearchExperiencePolicyCharacter()
    agent.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    agent.step(Event(kind="retrieve", actor="book", context="find_object", forced_action="search:drawer"))
    agent.step(Event(kind="neutral", forced_action="idle"))
    agent.step(Event(kind="outcome", actor="keys", context="find_object", reward=-1.0, forced_action="idle"))
    book_value = habit(agent, experience_context(agent, "book", "find_object"), "search:drawer")
    keys_value = habit(agent, experience_context(agent, "keys", "find_object"), "search:drawer")
    return {
        "passed": book_value == 0.0 and keys_value == 0.0,
        "book_value": book_value,
        "keys_value": keys_value,
        "failure_claim": "An outcome attributed to a different target entity must not update the prior search action.",
    }


def same_derived_context_ambiguity_is_preserved() -> dict:
    agent = SearchExperiencePolicyCharacter()
    agent.step(Event(kind="observe_location", actor="tool", context="bench", forced_action="idle"))
    agent.step(Event(kind="retrieve", actor="tool", context="find_tool", forced_action="search:bench"))
    agent.step(Event(kind="retrieve", actor="tool", context="find_tool", forced_action="search:cabinet"))
    before = agent.snapshot()["eligibility_records"]
    agent.step(Event(kind="outcome", actor="tool", context="find_tool", reward=-1.0, forced_action="idle"))
    ctx = experience_context(agent, "tool", "find_tool")
    return {
        "passed": habit(agent, ctx, "search:bench") == 0.0 and habit(agent, ctx, "search:cabinet") == 0.0,
        "before": before,
        "bench": habit(agent, ctx, "search:bench"),
        "cabinet": habit(agent, ctx, "search:cabinet"),
        "failure_claim": "EXP-008 must not bypass EXP-007's conservative abstention when two actions remain plausible in one experienced context.",
    }


def fractional_evidence_threshold() -> dict:
    agent = SearchExperiencePolicyCharacter()
    actor, task = "folder", "find_folder"
    agent.step(Event(kind="observe_location", actor=actor, context="cabinet", forced_action="idle"))
    rows = []
    for index in range(4):
        choice = agent.step(Event(kind="retrieve", actor=actor, context=task, available_actions=("search:desk", "search:cabinet")))
        agent.step(Event(kind="outcome", actor=actor, context=task, reward=-0.8, forced_action="idle"))
        rows.append({"choice": choice, "value": habit(agent, experience_context(agent, actor, task), "search:cabinet")})
    final = agent.step(Event(kind="retrieve", actor=actor, context=task, available_actions=("search:cabinet", "search:desk")))
    return {
        "passed": rows[0]["choice"] == rows[1]["choice"] == rows[2]["choice"] == "search:cabinet" and final == "search:desk",
        "rows": rows,
        "final": final,
        "failure_claim": "Adaptation should arise from accumulated action value rather than an implicit integer failure counter.",
    }


def similar_task_names_do_not_collide() -> dict:
    agent = SearchExperiencePolicyCharacter()
    agent.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    for _ in range(3):
        agent.step(Event(kind="retrieve", actor="book", context="find_book", forced_action="search:drawer"))
        agent.step(Event(kind="outcome", actor="book", context="find_book", reward=-1.0, forced_action="idle"))
    exact = agent.step(Event(kind="retrieve", actor="book", context="find_book", available_actions=("search:drawer", "search:shelf")))
    similar = agent.step(Event(kind="retrieve", actor="book", context="find_book ", available_actions=("search:shelf", "search:drawer")))
    return {
        "passed": exact == "search:shelf" and similar == "search:drawer",
        "exact": exact,
        "similar": similar,
        "failure_claim": "String-near but semantically distinct task contexts must not share learned search failure state.",
    }


def zero_reward_does_not_create_experience() -> dict:
    agent = SearchExperiencePolicyCharacter()
    agent.step(Event(kind="observe_location", actor="photo", context="album", forced_action="idle"))
    agent.step(Event(kind="retrieve", actor="photo", context="find_photo", forced_action="search:album"))
    agent.step(Event(kind="outcome", actor="photo", context="find_photo", reward=0.0, forced_action="idle"))
    ctx = experience_context(agent, "photo", "find_photo")
    return {
        "passed": habit(agent, ctx, "search:album") == 0.0,
        "value": habit(agent, ctx, "search:album"),
        "failure_claim": "A zero-value outcome may consume time but must not create positive or negative search experience.",
    }


def run_review() -> dict:
    probes = {
        "fresh_same_location_reobservation": fresh_same_location_reobservation(),
        "delimiter_unicode_roundtrip": delimiter_and_unicode_roundtrip(),
        "actor_mismatch_abstains": actor_mismatch_abstains(),
        "same_context_ambiguity_preserved": same_derived_context_ambiguity_is_preserved(),
        "fractional_evidence_threshold": fractional_evidence_threshold(),
        "similar_task_names_do_not_collide": similar_task_names_do_not_collide(),
        "zero_reward_no_experience": zero_reward_does_not_create_experience(),
    }
    failures = [name for name, row in probes.items() if not row["passed"]]
    return {
        "experiment": "EXP-008 first post-freeze adversarial reviewer generation",
        "production_frozen_at": PRODUCTION_FROZEN_AT,
        "created_after_production_freeze": True,
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
