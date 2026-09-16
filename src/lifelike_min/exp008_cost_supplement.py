from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean, median, pstdev
from time import perf_counter_ns

from .exp007_challenger import EligibilityRecord
from .exp008_challenger import SearchExperiencePolicyCharacter
from .runtime import Event
from .v9_1_compact import V91CompactCharacter
from .v9_1_structural_closeout import populated_state


def distribution(values):
    return {
        "n": len(values),
        "mean": mean(values),
        "median": median(values),
        "pstdev": pstdev(values) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
    }


def exp_context(agent, actor: str, task: str) -> str:
    value = agent._search_experience_context(Event(kind="retrieve", actor=actor, context=task))
    assert value is not None
    return value


def fill_search_histories(agent, count: int) -> None:
    for i in range(count):
        actor = f"ent{i:05d}"  # length 8
        task = f"tsk{i:05d}"   # length 8
        action = f"search:loc{i:05d}"
        context = exp_context(agent, actor, task) if isinstance(agent, SearchExperiencePolicyCharacter) else task
        agent.habits[(context, action)] = -0.35


def state_sizes(factory) -> dict:
    fresh = factory()
    representative = populated_state(factory, maximum_bounded=False)
    maximum_bounded = populated_state(factory, maximum_bounded=True)
    return {
        "fresh_diagnostic_state_bytes": fresh.persistent_state_bytes(),
        "fresh_canonical_persistence_bytes": len(fresh.serialize_persistent().encode("utf-8")),
        "representative_diagnostic_state_bytes": representative.persistent_state_bytes(),
        "representative_canonical_persistence_bytes": len(representative.serialize_persistent().encode("utf-8")),
        "maximum_bounded_diagnostic_state_bytes": maximum_bounded.persistent_state_bytes(),
        "maximum_bounded_canonical_persistence_bytes": len(maximum_bounded.serialize_persistent().encode("utf-8")),
        "mechanism_count": fresh.mechanism_count(),
    }


def search_history_sizes(factory, counts=(0, 1, 16, 128)) -> dict:
    rows = {}
    for count in counts:
        agent = factory()
        fill_search_histories(agent, count)
        rows[str(count)] = {
            "diagnostic_state_bytes": agent.persistent_state_bytes(),
            "canonical_persistence_bytes": len(agent.serialize_persistent().encode("utf-8")),
        }
    return rows


def timed(factory, setup, operation, iterations, rounds=9) -> dict:
    samples = []
    for _ in range(rounds):
        agent = factory()
        setup(agent)
        start = perf_counter_ns()
        for _ in range(iterations):
            operation(agent)
        samples.append((perf_counter_ns() - start) / iterations / 1000.0)
    return distribution(samples)


def setup_search(agent):
    agent.location_beliefs["ent00000"] = "loc00000"
    fill_search_histories(agent, 1)


def search_op(agent):
    agent.step(Event(
        kind="retrieve",
        actor="ent00000",
        context="tsk00000",
        available_actions=("search:loc99999", "search:loc00000"),
    ))


def setup_observation(agent):
    fill_search_histories(agent, 128)
    agent.location_beliefs["ent00000"] = "loc00000"


def observation_op(agent):
    agent.step(Event(kind="observe_location", actor="ent00000", context="loc00000", forced_action="idle"))


def setup_update(agent):
    actor, task, action = "ent00000", "tsk00000", "search:loc00000"
    if isinstance(agent, SearchExperiencePolicyCharacter):
        context = exp_context(agent, actor, task)
    else:
        context = task
    agent.habits[(context, action)] = 0.0
    agent.eligibility_records = [EligibilityRecord(context=context, action=action, age=0)]


def update_op(agent):
    actor, task, action = "ent00000", "tsk00000", "search:loc00000"
    if isinstance(agent, SearchExperiencePolicyCharacter):
        context = exp_context(agent, actor, task)
        event = Event(kind="outcome", actor=actor, context=task, reward=-0.1, forced_action="idle")
    else:
        context = task
        event = Event(kind="outcome", context=task, reward=-0.1, forced_action="idle")
    # Keep one unambiguous live candidate so each timed operation measures a real update.
    agent.eligibility_records = [EligibilityRecord(context=context, action=action, age=0)]
    agent._apply_delayed_outcome(event)


def reconstruction(factory, count=128, rounds=21) -> dict:
    agent = factory()
    fill_search_histories(agent, count)
    payload = agent.serialize_persistent()
    samples = []
    for _ in range(rounds):
        start = perf_counter_ns()
        restored = factory.from_persistent_json(payload)
        _ = restored.tick
        samples.append((perf_counter_ns() - start) / 1000.0)
    return distribution(samples)


def run() -> dict:
    champion_sizes = state_sizes(V91CompactCharacter)
    challenger_sizes = state_sizes(SearchExperiencePolicyCharacter)
    champion_hist = search_history_sizes(V91CompactCharacter)
    challenger_hist = search_history_sizes(SearchExperiencePolicyCharacter)

    per_entry_overhead = (
        (challenger_hist["128"]["canonical_persistence_bytes"] - challenger_hist["0"]["canonical_persistence_bytes"])
        - (champion_hist["128"]["canonical_persistence_bytes"] - champion_hist["0"]["canonical_persistence_bytes"])
    ) / 128.0

    return {
        "experiment": "EXP-008 representational cost supplement",
        "production_commit": "c42a43d353b21061b97cabb665e8ef59544d27c9",
        "metric_note": (
            "The project's established 269/577-byte v9.1 figures use persistent_state_bytes(), "
            "which serializes the diagnostic snapshot. serialize_persistent() is the separate canonical "
            "lossless payload and is reported independently here."
        ),
        "state": {
            "v9_1_compact": champion_sizes,
            "exp008": challenger_sizes,
        },
        "normalized_search_history": {
            "source_identifier_lengths": {"entity": 8, "task": 8},
            "maximum_tested_entries": 128,
            "v9_1_compact": champion_hist,
            "exp008": challenger_hist,
            "incremental_key_qualification_overhead_bytes_per_entry_at_128": per_entry_overhead,
        },
        "timing_us": {
            "search_decision": {
                "v9_1_compact": timed(V91CompactCharacter, setup_search, search_op, 500, 9),
                "exp008": timed(SearchExperiencePolicyCharacter, setup_search, search_op, 500, 9),
            },
            "observation_event_with_128_history_entries": {
                "v9_1_compact": timed(V91CompactCharacter, setup_observation, observation_op, 250, 9),
                "exp008": timed(SearchExperiencePolicyCharacter, setup_observation, observation_op, 250, 9),
            },
            "search_outcome_update": {
                "v9_1_compact": timed(V91CompactCharacter, setup_update, update_op, 1000, 9),
                "exp008": timed(SearchExperiencePolicyCharacter, setup_update, update_op, 1000, 9),
            },
            "reconstruction_128_history_entries": {
                "v9_1_compact": reconstruction(V91CompactCharacter),
                "exp008": reconstruction(SearchExperiencePolicyCharacter),
            },
        },
        "architectural_cost": "0 new persistent field categories; mechanism count remains 11.",
        "representational_cost": (
            "Entity/task qualification increases each search-history key. Observation-triggered invalidation "
            "also scans the existing habit mapping, so EXP-008 is not zero-cost even though mechanism count is unchanged."
        ),
        "timing_caveat": "Hosted CI timing is an engineering estimate; use direction and scale, not small differences as speed claims.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    report = run()
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
