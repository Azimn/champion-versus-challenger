from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean, median, pstdev
from time import perf_counter_ns

from .exp008_challenger import SearchExperiencePolicyCharacter
from .runtime import Event
from .v9_1_compact import V91CompactCharacter


FROZEN_CHAMPION = "2856ec6a32be0347a9243f6eff6faa404a9a0e6c"
FROZEN_EXP008_PRODUCTION = "c42a43d353b21061b97cabb665e8ef59544d27c9"


def ctx(agent: SearchExperiencePolicyCharacter, actor: str, task: str) -> str:
    value = agent._search_experience_context(
        Event(kind="retrieve", actor=actor, context=task)
    )
    assert value is not None
    return value


def habit(agent, context: str, action: str) -> float:
    return float(agent.habits.get((context, action), 0.0))


def learn_search(
    agent,
    actor: str,
    task: str,
    location: str,
    reward: float,
    *,
    delay: int = 0,
) -> float:
    action = f"search:{location}"
    agent.step(
        Event(
            kind="retrieve",
            actor=actor,
            context=task,
            forced_action=action,
        )
    )
    for _ in range(delay):
        agent.step(Event(kind="neutral", forced_action="idle"))
    agent.step(
        Event(
            kind="outcome",
            actor=actor,
            context=task,
            reward=reward,
            forced_action="idle",
        )
    )
    if isinstance(agent, SearchExperiencePolicyCharacter):
        key_context = ctx(agent, actor, task)
    else:
        key_context = task
    return habit(agent, key_context, action)


def expire_eligibility(agent, count: int = 11) -> None:
    for _ in range(count):
        agent.step(Event(kind="neutral", forced_action="idle"))


class NoObservationInvalidation(SearchExperiencePolicyCharacter):
    def _invalidate_negative_search_experience_for_observation(
        self, actor: str, location: str
    ) -> None:
        return None


class NoSearchScoreInteraction(SearchExperiencePolicyCharacter):
    def _score_action(
        self,
        action: str,
        event: Event,
        immediate_threat: float,
        task_pressure: float,
    ) -> float:
        if action.startswith("search:"):
            return V91CompactCharacter._score_action(
                self, action, event, immediate_threat, task_pressure
            )
        return super()._score_action(
            action, event, immediate_threat, task_pressure
        )


class EntityBlindSearch(SearchExperiencePolicyCharacter):
    @staticmethod
    def _search_experience_context(event: Event) -> str | None:
        if event.context is None:
            return None
        from urllib.parse import quote
        return f"search_task:{quote(str(event.context), safe='')}"

    @staticmethod
    def _encoded_actor_suffix(actor: str) -> str:
        # This diagnostic intentionally makes entity identity unavailable to the
        # derived key. Observation invalidation is disabled so only key collapse is
        # tested.
        return ";entity:__never__"


class TaskBlindSearch(SearchExperiencePolicyCharacter):
    @staticmethod
    def _search_experience_context(event: Event) -> str | None:
        if event.actor is None:
            return None
        from urllib.parse import quote
        return f"search_entity:{quote(str(event.actor), safe='')}"

    @staticmethod
    def _encoded_actor_suffix(actor: str) -> str:
        return ";entity:__never__"


def reviewer2_intended_isolation_diagnostic() -> dict:
    """Resolve the invalid reviewer assumption without modifying the reviewer."""
    agent = SearchExperiencePolicyCharacter()
    actor, task = "book", "find_home"
    drawer = learn_search(agent, actor, task, "drawer", -1.0)
    expire_eligibility(agent)
    shelf = learn_search(agent, actor, task, "shelf", -1.0)
    before = {
        "drawer": habit(agent, ctx(agent, actor, task), "search:drawer"),
        "shelf": habit(agent, ctx(agent, actor, task), "search:shelf"),
    }
    agent.step(
        Event(kind="observe_location", actor=actor, context="drawer", forced_action="idle")
    )
    after = {
        "drawer": habit(agent, ctx(agent, actor, task), "search:drawer"),
        "shelf": habit(agent, ctx(agent, actor, task), "search:shelf"),
    }
    return {
        "passed": drawer < 0 and shelf < 0 and after["drawer"] == 0.0 and after["shelf"] < 0,
        "before": before,
        "after": after,
        "interpretation": (
            "When both negative values genuinely exist under EXP-007's ambiguity contract, "
            "observation of drawer removes only the drawer value and preserves shelf."
        ),
    }


def semantic_audit() -> dict:
    """Determine what the existing scalar has actually been demonstrated to mean."""
    agent = SearchExperiencePolicyCharacter()
    actor, task, location = "book", "find_book", "drawer"
    agent.step(
        Event(kind="observe_location", actor=actor, context=location, forced_action="idle")
    )
    for _ in range(3):
        learn_search(agent, actor, task, location, -1.0)
    key_context = ctx(agent, actor, task)
    before = habit(agent, key_context, "search:drawer")

    # The runtime receives only a scalar reward. It has no outcome-type field that
    # distinguishes "failed to locate" from "search was costly/undesirable". The
    # same causal input therefore admits two meanings that demand different updates
    # after direct observation.
    encoded_before = agent.serialize_persistent()
    copy_epistemic = SearchExperiencePolicyCharacter.from_persistent_json(encoded_before)
    copy_utility = SearchExperiencePolicyCharacter.from_persistent_json(encoded_before)
    observation = Event(
        kind="observe_location", actor=actor, context=location, forced_action="idle"
    )
    copy_epistemic.step(observation)
    copy_utility.step(observation)
    after_epistemic = habit(copy_epistemic, key_context, "search:drawer")
    after_utility = habit(copy_utility, key_context, "search:drawer")

    return {
        "historical_representation": {
            "store": "habits[(context, action)] -> scalar",
            "update": "existing generic Event.reward through habit/delayed-credit learning",
            "demonstrated_uses": [
                "reward-shaped contextual routine preference (EXP-002 v4)",
                "positive and negative arbitrary action consequence credit (EXP-007)",
                "search success/failure action value (EXP-008)",
            ],
            "separate_outcome_type_available": False,
            "separate_epistemic_and_utility_components_available": False,
        },
        "search_value_before_observation": before,
        "two_semantic_interpretations_of_identical_runtime_state": {
            "epistemic": "repeated search failed to locate the entity at this location",
            "utility": "performing this search action in this context was costly/undesirable",
        },
        "current_rule_after_same_observation": {
            "epistemic_interpretation": after_epistemic,
            "utility_interpretation": after_utility,
        },
        "identical_input_cannot_distinguish_interpretation": (
            copy_epistemic.persistent_snapshot() == copy_utility.persistent_snapshot()
        ),
        "semantic_gate_passed": False,
        "reason": (
            "Direct observation logically contradicts the failed-to-locate interpretation but "
            "does not necessarily contradict generic negative action utility. The current scalar "
            "and Event.reward contract do not encode which meaning produced the value, so deleting "
            "every matching negative value overclaims what the organism knows."
        ),
    }


def minimum_operation_audit() -> dict:
    agent = SearchExperiencePolicyCharacter()
    actor, task, location = "book", "find_book", "drawer"
    agent.step(Event(kind="observe_location", actor=actor, context=location, forced_action="idle"))
    for _ in range(3):
        learn_search(agent, actor, task, location, -1.0)
    key = (ctx(agent, actor, task), "search:drawer")
    negative = agent.habits[key]

    # Sparse removal and an explicit zero are behaviorally equivalent because all
    # habit reads default missing entries to 0.0, but removal is smaller persistent
    # state. A positive counter-update asserts more than observation establishes.
    removed = dict(agent.habits)
    removed.pop(key, None)
    explicit_zero = dict(agent.habits)
    explicit_zero[key] = 0.0
    counter_positive = dict(agent.habits)
    counter_positive[key] = 0.35

    no_invalidation = NoObservationInvalidation.from_persistent_json(
        agent.serialize_persistent()
    )
    no_invalidation.step(
        Event(kind="observe_location", actor=actor, context=location, forced_action="idle")
    )
    preserve_choice = no_invalidation.step(
        Event(
            kind="retrieve",
            actor=actor,
            context=task,
            available_actions=("search:drawer", "search:shelf"),
        )
    )

    return {
        "starting_negative": negative,
        "alternatives": {
            "complete_removal": {
                "effective_value": removed.get(key, 0.0),
                "stores_entry": key in removed,
            },
            "explicit_reset_to_neutral": {
                "effective_value": explicit_zero[key],
                "stores_entry": True,
                "behaviorally_equivalent_to_removal": explicit_zero[key] == removed.get(key, 0.0),
            },
            "counter_update_positive": {
                "effective_value": counter_positive[key],
                "adds_unsupported_positive_success_claim": True,
            },
            "preserve_history": {
                "effective_value": no_invalidation.habits[key],
                "post_reobservation_choice": preserve_choice,
                "fails_fresh_observation_case": preserve_choice != "search:drawer",
            },
            "temporary_observation_priority_without_state": {
                "available_under_current_contract": False,
                "reason": (
                    "After a same-location reobservation, location_beliefs contains the same value it "
                    "contained before; no observation-recency signal exists. A future search cannot "
                    "tell fresh from stale observation without changing persistent/event semantics."
                ),
            },
        },
        "minimum_if_negative_is_pure_epistemic": "sparse removal/reset-to-neutral",
        "minimum_correct_operation_unconditionally": None,
        "reason": "The scalar's generic utility semantics make unconditional deletion semantically unsafe.",
    }


def temporal_contradictions() -> dict:
    def choice(agent, actor="book", task="find_book", a="drawer", b="shelf"):
        return agent.step(
            Event(
                kind="retrieve",
                actor=actor,
                context=task,
                available_actions=(f"search:{b}", f"search:{a}"),
            )
        )

    probes = {}

    a = SearchExperiencePolicyCharacter()
    a.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    learn_search(a, "book", "find_book", "drawer", -1.0)
    learn_search(a, "book", "find_book", "drawer", -1.0)
    a.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    probes["failure_failure_observation_search"] = choice(a) == "search:drawer"

    b = SearchExperiencePolicyCharacter()
    b.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    learn_search(b, "book", "find_book", "drawer", -1.0)
    learn_search(b, "book", "find_book", "drawer", -1.0)
    b.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    probes["observation_failure_failure_observation_search"] = choice(b) == "search:drawer"

    c = SearchExperiencePolicyCharacter()
    c.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    learn_search(c, "book", "find_book", "drawer", -1.0)
    c.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    learn_search(c, "book", "find_book", "drawer", -1.0)
    probes["failure_observation_failure_search"] = choice(c) == "search:drawer"

    d = SearchExperiencePolicyCharacter()
    d.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    learn_search(d, "book", "find_book", "drawer", 1.0)
    learn_search(d, "book", "find_book", "drawer", -1.0)
    before_d = habit(d, ctx(d, "book", "find_book"), "search:drawer")
    d.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    after_d = habit(d, ctx(d, "book", "find_book"), "search:drawer")
    probes["positive_negative_observation_search"] = (
        after_d >= 0.0 and choice(d) == "search:drawer"
    )

    e = SearchExperiencePolicyCharacter()
    e.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    e.step(Event(kind="hidden_world_change", actor="book", context="shelf", forced_action="idle"))
    learn_search(e, "book", "find_book", "drawer", -1.0)
    before_reobserve = habit(e, ctx(e, "book", "find_book"), "search:drawer")
    e.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    probes["observation_hidden_move_failed_search_reobservation_search"] = (
        before_reobserve < 0.0 and choice(e) == "search:drawer"
    )

    f = SearchExperiencePolicyCharacter()
    f.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    f.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    for _ in range(3):
        learn_search(f, "book", "find_book", "drawer", -1.0)
    probes["reobservation_repeated_later_failure_search"] = choice(f) == "search:shelf"

    return {
        "passed": all(probes.values()),
        "probes": probes,
        "positive_negative_value_before_observation": before_d,
        "positive_negative_value_after_observation": after_d,
    }


def information_boundary_audit() -> dict:
    actor, task, location = "book", "find_book", "drawer"

    direct = SearchExperiencePolicyCharacter()
    hidden = SearchExperiencePolicyCharacter()
    for agent in (direct, hidden):
        agent.step(Event(kind="observe_location", actor=actor, context=location, forced_action="idle"))
        for _ in range(3):
            learn_search(agent, actor, task, location, -1.0)

    key_direct = ctx(direct, actor, task)
    direct_before = habit(direct, key_direct, "search:drawer")
    hidden_before = habit(hidden, ctx(hidden, actor, task), "search:drawer")

    # Objective description may be the same to the simulator, but only one agent
    # receives direct subject-accessible observation.
    direct.step(Event(kind="observe_location", actor=actor, context=location, forced_action="idle"))
    hidden.step(Event(kind="hidden_world_change", actor=actor, context=location, forced_action="idle"))

    direct_after = habit(direct, key_direct, "search:drawer")
    hidden_after = habit(hidden, ctx(hidden, actor, task), "search:drawer")
    direct_choice = direct.step(Event(kind="retrieve", actor=actor, context=task, available_actions=("search:shelf", "search:drawer")))
    hidden_choice = hidden.step(Event(kind="retrieve", actor=actor, context=task, available_actions=("search:shelf", "search:drawer")))

    return {
        "passed": (
            direct_before < 0
            and hidden_before < 0
            and direct_after == 0.0
            and hidden_after == hidden_before
            and direct_choice == "search:drawer"
            and hidden_choice == "search:shelf"
        ),
        "direct": {"before": direct_before, "after": direct_after, "choice": direct_choice},
        "hidden": {"before": hidden_before, "after": hidden_after, "choice": hidden_choice},
        "interpretation": "Behavior follows experienced history, not simulator-only relocation information.",
    }


def key_identity_audit() -> dict:
    agent = SearchExperiencePolicyCharacter()
    pairs = [
        ("a", "bc"),
        ("ab", "c"),
        ("1", "23"),
        ("12", "3"),
        ("prefix", "prefix-suffix"),
        ("prefix-suffix", "prefix"),
        ("book|alpha;%", "find|room:;%"),
        ("book%7Calpha", "find%3Aroom"),
        ("β", "ζητῶ"),
        ("0", "0"),
    ]
    encoded = [ctx(agent, actor, task) for actor, task in pairs]
    unique = len(encoded) == len(set(encoded))

    # Test serialization with a location/action containing the persistence delimiter.
    for index, (actor, task) in enumerate(pairs):
        context = ctx(agent, actor, task)
        action = f"search:loc|{index};:%β"
        agent.habits[(context, action)] = -0.1 - index * 0.01
    serialized = agent.serialize_persistent()
    restored = SearchExperiencePolicyCharacter.from_persistent_json(serialized)
    roundtrip = agent.persistent_snapshot() == restored.persistent_snapshot()

    # Empty actor/task strings are not legal behavioral identities in the current
    # runtime because actor/context are truth-tested. Minimal supported fragments are
    # represented above by "0" and one-character strings.
    return {
        "passed": unique and roundtrip,
        "encoded_contexts": encoded,
        "unique": unique,
        "roundtrip": roundtrip,
        "empty_identifier_supported_by_behavior_contract": False,
    }


def cross_task_and_positive_audit() -> dict:
    agent = SearchExperiencePolicyCharacter()
    actor, location = "book", "drawer"
    negative_tasks = ("find_book_home", "find_book_office")
    for task in negative_tasks:
        learn_search(agent, actor, task, location, -1.0)
        expire_eligibility(agent)
    positive_task = "find_book_library"
    learn_search(agent, actor, positive_task, location, 1.0)
    expire_eligibility(agent)
    unrelated_key = ("retrieve_heavy", "retrieve:drawer")
    agent.habits[unrelated_key] = -0.65

    before = {
        task: habit(agent, ctx(agent, actor, task), "search:drawer")
        for task in (*negative_tasks, positive_task)
    }
    agent.step(Event(kind="observe_location", actor=actor, context=location, forced_action="idle"))
    after = {
        task: habit(agent, ctx(agent, actor, task), "search:drawer")
        for task in (*negative_tasks, positive_task)
    }
    return {
        "passed": (
            all(before[t] < 0 and after[t] == 0.0 for t in negative_tasks)
            and before[positive_task] > 0
            and after[positive_task] == before[positive_task]
            and agent.habits[unrelated_key] == -0.65
        ),
        "before": before,
        "after": after,
        "unrelated_non_search": agent.habits[unrelated_key],
        "scalar_history_limitation": (
            "Positive and negative outcomes for one context/action are folded into one net scalar; "
            "the representation does not retain separate positive and negative histories."
        ),
    }


def eligibility_interaction_audit() -> dict:
    agent = SearchExperiencePolicyCharacter()
    actor, task = "book", "find_book"
    agent.step(Event(kind="retrieve", actor=actor, context=task, forced_action="search:drawer"))
    agent.step(Event(kind="context", context="evening", forced_action="walk"))
    before = list(agent.snapshot()["eligibility_records"])
    agent.step(Event(kind="observe_location", actor=actor, context="drawer", forced_action="idle"))
    after_observation = list(agent.snapshot()["eligibility_records"])
    agent.step(Event(kind="outcome", context="evening", reward=1.0, forced_action="idle"))
    unrelated_value = habit(agent, "evening", "walk")
    search_value = habit(agent, ctx(agent, actor, task), "search:drawer")
    return {
        "passed": (
            len(before) == 2
            and len(after_observation) == 2
            and unrelated_value > 0.0
            and search_value == 0.0
        ),
        "before": before,
        "after_observation": after_observation,
        "unrelated_delayed_value": unrelated_value,
        "search_value": search_value,
    }


def reconstruction_audit() -> dict:
    # Order A: negative -> serialize -> destroy/restore -> direct observation -> continue.
    a = SearchExperiencePolicyCharacter()
    a.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    for _ in range(3):
        learn_search(a, "book", "find_book", "drawer", -1.0)
    a.habits[("morning", "walk")] = 0.4
    a.habits[("evening", "tea")] = -0.25
    encoded_a = a.serialize_persistent()
    restored_a = SearchExperiencePolicyCharacter.from_persistent_json(encoded_a)
    restored_a.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    choice_a = restored_a.step(Event(kind="retrieve", actor="book", context="find_book", available_actions=("search:shelf", "search:drawer")))

    # Order B: negative -> direct observation/invalidation -> serialize -> restore -> continue.
    b = SearchExperiencePolicyCharacter()
    b.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    for _ in range(3):
        learn_search(b, "book", "find_book", "drawer", -1.0)
    b.habits[("morning", "walk")] = 0.4
    b.habits[("evening", "tea")] = -0.25
    b.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    encoded_b = b.serialize_persistent()
    restored_b = SearchExperiencePolicyCharacter.from_persistent_json(encoded_b)
    exact_b = b.persistent_snapshot() == restored_b.persistent_snapshot()
    choice_b = restored_b.step(Event(kind="retrieve", actor="book", context="find_book", available_actions=("search:shelf", "search:drawer")))

    return {
        "passed": (
            choice_a == "search:drawer"
            and choice_b == "search:drawer"
            and exact_b
            and restored_a.habits.get(("morning", "walk")) == 0.4
            and restored_a.habits.get(("evening", "tea")) == -0.25
            and restored_b.habits.get(("morning", "walk")) == 0.4
            and restored_b.habits.get(("evening", "tea")) == -0.25
        ),
        "pre_observation_restore_then_continue": choice_a,
        "post_invalidation_restore_exact": exact_b,
        "post_invalidation_choice": choice_b,
        "serialized_bytes_pre_observation": len(encoded_a.encode("utf-8")),
        "serialized_bytes_post_invalidation": len(encoded_b.encode("utf-8")),
    }


def repeated_failure_choice(factory) -> dict:
    agent = factory()
    actor, task, believed, alternate = "book", "find_book", "drawer", "shelf"
    agent.step(Event(kind="observe_location", actor=actor, context=believed, forced_action="idle"))
    for _ in range(3):
        learn_search(agent, actor, task, believed, -1.0)
    choice = agent.step(Event(kind="retrieve", actor=actor, context=task, available_actions=(f"search:{alternate}", f"search:{believed}")))
    return {"agent": agent, "choice": choice}


def causal_ablation_audit() -> dict:
    champion = repeated_failure_choice(V91CompactCharacter)
    challenger = repeated_failure_choice(SearchExperiencePolicyCharacter)
    no_invalidation = repeated_failure_choice(NoObservationInvalidation)
    no_score = repeated_failure_choice(NoSearchScoreInteraction)

    # Reviewer-1 target isolates observation-triggered invalidation.
    fresh = NoObservationInvalidation()
    fresh.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    for _ in range(3):
        learn_search(fresh, "book", "find_book", "drawer", -1.0)
    before_fresh = fresh.step(Event(kind="retrieve", actor="book", context="find_book", available_actions=("search:drawer", "search:shelf")))
    fresh.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    after_fresh = fresh.step(Event(kind="retrieve", actor="book", context="find_book", available_actions=("search:shelf", "search:drawer")))

    entity_blind = EntityBlindSearch()
    for actor in ("book", "keys"):
        entity_blind.step(Event(kind="observe_location", actor=actor, context="drawer", forced_action="idle"))
    for _ in range(3):
        learn_search(entity_blind, "book", "find_object", "drawer", -1.0)
    entity_blind_choice = entity_blind.step(Event(kind="retrieve", actor="keys", context="find_object", available_actions=("search:drawer", "search:shelf")))

    task_blind = TaskBlindSearch()
    task_blind.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    for _ in range(3):
        learn_search(task_blind, "book", "home", "drawer", -1.0)
    task_blind_choice = task_blind.step(Event(kind="retrieve", actor="book", context="office", available_actions=("search:drawer", "search:shelf")))

    return {
        "original_failure": {
            "v9_1_compact": champion["choice"],
            "challenger": challenger["choice"],
            "no_observation_invalidation": no_invalidation["choice"],
            "no_search_score_interaction": no_score["choice"],
            "interpretation": (
                "The original repeated-failure improvement is caused by consulting qualified learned "
                "search value during scoring. Observation invalidation is not causal for that original "
                "target; it was added to repair the later fresh-reobservation reviewer failure."
            ),
        },
        "fresh_reobservation_ablation": {
            "before_reobservation": before_fresh,
            "after_reobservation_without_invalidation": after_fresh,
            "invalidation_required_for_reviewer1_target": after_fresh != "search:drawer",
        },
        "identity_ablations": {
            "entity_blind_other_entity_choice": entity_blind_choice,
            "entity_contamination_returns": entity_blind_choice == "search:shelf",
            "task_blind_other_task_choice": task_blind_choice,
            "task_contamination_returns": task_blind_choice == "search:shelf",
        },
    }


def fill_search_histories(agent, count: int) -> None:
    # Direct assignment isolates representational cost from training-time trace
    # ambiguity. Identifiers have matched source lengths across champion/challenger.
    for i in range(count):
        actor = f"ent{i:05d}"  # length 8
        task = f"tsk{i:05d}"   # length 8
        action = f"search:loc{i:05d}"
        if isinstance(agent, SearchExperiencePolicyCharacter):
            context = ctx(agent, actor, task)
        else:
            context = task
        agent.habits[(context, action)] = -0.35


def distribution(values: list[float]) -> dict:
    return {
        "n": len(values),
        "mean": mean(values),
        "median": median(values),
        "pstdev": pstdev(values) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
    }


def time_operation(factory, setup, op, iterations=1000, rounds=9) -> dict:
    samples = []
    for _ in range(rounds):
        agent = factory()
        setup(agent)
        start = perf_counter_ns()
        for _ in range(iterations):
            op(agent)
        elapsed = perf_counter_ns() - start
        samples.append(elapsed / iterations / 1000.0)
    return distribution(samples)


def cost_audit() -> dict:
    champion = V91CompactCharacter()
    challenger = SearchExperiencePolicyCharacter()
    fresh = {
        "champion": len(champion.serialize_persistent().encode("utf-8")),
        "challenger": len(challenger.serialize_persistent().encode("utf-8")),
    }

    sizes = {}
    for count in (1, 16, 128):
        c = V91CompactCharacter()
        x = SearchExperiencePolicyCharacter()
        fill_search_histories(c, count)
        fill_search_histories(x, count)
        sizes[str(count)] = {
            "champion": len(c.serialize_persistent().encode("utf-8")),
            "challenger": len(x.serialize_persistent().encode("utf-8")),
        }
    one_overhead = sizes["1"]["challenger"] - sizes["1"]["champion"]
    base_overhead = fresh["challenger"] - fresh["champion"]
    per_entry_incremental_overhead = one_overhead - base_overhead

    def setup_empty(_agent):
        return None

    def setup_one(agent):
        fill_search_histories(agent, 1)
        agent.location_beliefs["ent00000"] = "loc00000"

    def setup_128(agent):
        fill_search_histories(agent, 128)
        agent.location_beliefs["ent00000"] = "loc00000"

    search_event = Event(
        kind="retrieve",
        actor="ent00000",
        context="tsk00000",
        available_actions=("search:loc99999", "search:loc00000"),
    )
    observation_event = Event(
        kind="observe_location",
        actor="ent00000",
        context="loc00000",
        forced_action="idle",
    )

    search_timing = {
        "champion": time_operation(V91CompactCharacter, setup_one, lambda a: a.step(search_event), 500, 7),
        "challenger": time_operation(SearchExperiencePolicyCharacter, setup_one, lambda a: a.step(search_event), 500, 7),
    }
    observation_timing = {
        "champion_128_histories": time_operation(V91CompactCharacter, setup_128, lambda a: a.step(observation_event), 250, 7),
        "challenger_128_histories": time_operation(SearchExperiencePolicyCharacter, setup_128, lambda a: a.step(observation_event), 250, 7),
    }

    def reconstruct_samples(factory, count=128, rounds=15):
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

    return {
        "mechanism_count": {
            "champion": champion.mechanism_count(),
            "challenger": challenger.mechanism_count(),
        },
        "fresh_serialized_bytes": fresh,
        "search_history_bytes": sizes,
        "maximum_tested_search_history_entries": 128,
        "normalized_source_identifier_lengths": {"entity": 8, "task": 8},
        "incremental_serialized_overhead_for_first_qualified_entry_bytes": per_entry_incremental_overhead,
        "search_tick_us": search_timing,
        "observation_tick_us_with_128_histories": observation_timing,
        "reconstruction_us_128_histories": {
            "champion": reconstruct_samples(V91CompactCharacter),
            "challenger": reconstruct_samples(SearchExperiencePolicyCharacter),
        },
        "architectural_cost_interpretation": "No new field category and no new counted mechanism.",
        "representational_cost_interpretation": (
            "Qualified entity/task keys increase serialized learned-state size, and observation-time "
            "invalidation scans the existing habit mapping. These are real information/runtime costs."
        ),
        "timing_caveat": "Hosted CI microbenchmarks are engineering estimates, not speed claims.",
    }


def run() -> dict:
    reviewer_resolution = reviewer2_intended_isolation_diagnostic()
    semantics = semantic_audit()
    minimum = minimum_operation_audit()
    temporal = temporal_contradictions()
    information = information_boundary_audit()
    identity = key_identity_audit()
    cross_task = cross_task_and_positive_audit()
    eligibility = eligibility_interaction_audit()
    reconstruction = reconstruction_audit()
    causal = causal_ablation_audit()
    cost = cost_audit()

    mechanical_gates = {
        "reviewer2_intended_isolation": reviewer_resolution["passed"],
        "temporal_contradictions": temporal["passed"],
        "information_boundary": information["passed"],
        "key_identity": identity["passed"],
        "cross_task_positive_preservation": cross_task["passed"],
        "eligibility_interaction": eligibility["passed"],
        "reconstruction": reconstruction["passed"],
        "mechanism_count_unchanged": cost["mechanism_count"] == {"champion": 11, "challenger": 11},
        "fresh_state_unchanged": cost["fresh_serialized_bytes"]["champion"] == cost["fresh_serialized_bytes"]["challenger"],
    }

    promotion_eligible = all(mechanical_gates.values()) and semantics["semantic_gate_passed"]
    return {
        "experiment": "EXP-008 closeout audit",
        "frozen_champion": FROZEN_CHAMPION,
        "frozen_exp008_production": FROZEN_EXP008_PRODUCTION,
        "mechanical_gates": mechanical_gates,
        "reviewer2_failure_resolution": reviewer_resolution,
        "negative_search_value_semantics": semantics,
        "minimum_operation_audit": minimum,
        "temporal_contradictions": temporal,
        "information_boundary": information,
        "key_identity": identity,
        "cross_task_and_positive": cross_task,
        "eligibility_interaction": eligibility,
        "reconstruction": reconstruction,
        "causal_ablation": causal,
        "cost": cost,
        "promotion_eligible": promotion_eligible,
        "provisional_decision": "PROMOTE" if promotion_eligible else "REJECT",
        "decision_reason": (
            "All mechanical interaction checks may pass, but promotion additionally requires a clear "
            "semantics for the negative learned quantity. Current generic scalar reward cannot "
            "distinguish contradicted failed-to-locate evidence from still-valid negative action utility."
            if not semantics["semantic_gate_passed"]
            else "All closeout gates passed."
        ),
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


if __name__ == "__main__":
    main()
