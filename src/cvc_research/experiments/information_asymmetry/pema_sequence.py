from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
from math import tanh
from typing import Any

from .metabolic_runner import matrix_analysis, run_canonical_matrix
from .model import Condition


@dataclass(frozen=True)
class OperationProposal:
    actor_id: str
    operation: str
    priority: float
    cost: int
    reason: str


@dataclass(frozen=True)
class AllocationRecord:
    actor_id: str
    operation: str
    priority: float
    granted: bool
    cost: int


def _tie_key(seed: int, round_id: str, proposal: OperationProposal) -> str:
    payload = f"{seed}|{round_id}|{proposal.actor_id}|{proposal.operation}".encode("utf-8")
    return sha256(payload).hexdigest()


def allocate_operations(
    proposals: list[OperationProposal],
    *,
    capacity: int,
    seed: int = 0,
    round_id: str = "round",
) -> list[AllocationRecord]:
    """Deterministic one-resource allocator for Experiments 2-4.

    Priorities are actor-generated. Exact ties use a seeded hash rather than
    actor-id ordering. Operations are indivisible at this stage.
    """
    if capacity < 0:
        raise ValueError("capacity must be non-negative")
    ordered = sorted(
        proposals,
        key=lambda item: (-item.priority, _tie_key(seed, round_id, item)),
    )
    remaining = capacity
    granted: set[tuple[str, str]] = set()
    for proposal in ordered:
        if proposal.cost <= remaining:
            remaining -= proposal.cost
            granted.add((proposal.actor_id, proposal.operation))
    return [
        AllocationRecord(
            actor_id=proposal.actor_id,
            operation=proposal.operation,
            priority=proposal.priority,
            granted=(proposal.actor_id, proposal.operation) in granted,
            cost=proposal.cost,
        )
        for proposal in proposals
    ]


def _birthday_local_state(access: Condition) -> dict[str, dict[str, str]]:
    if access == Condition.GLOBAL:
        return {
            "SOCIAL": {"E1": "avoid", "E3": "welcome"},
            "MEMORY": {"E1": "avoid", "E3": "welcome"},
            "ACTION": {"E1": "avoid", "E3": "welcome"},
            "LANGUAGE": {"E1": "avoid", "E3": "welcome"},
        }
    return {
        "SOCIAL": {"E1": "avoid"},
        "MEMORY": {"E1": "avoid", "E3": "welcome"},
        "ACTION": {"E3": "welcome"},
        "LANGUAGE": {"E3": "welcome"},
    }


def _changed_preference(events: dict[str, str]) -> bool:
    return "E1" in events and "E3" in events and events["E1"] != events["E3"]


def _latest_preference(events: dict[str, str]) -> str | None:
    if "E3" in events:
        return events["E3"]
    if "E1" in events:
        return events["E1"]
    return None


def _experiment_2_proposals(
    local: dict[str, dict[str, str]], *, uniform_priority: bool
) -> list[OperationProposal]:
    social = local["SOCIAL"]
    memory = local["MEMORY"]
    action = local["ACTION"]
    language = local["LANGUAGE"]

    if uniform_priority:
        priorities = {"SOCIAL": 0.50, "MEMORY": 0.50, "ACTION": 0.50, "LANGUAGE": 0.50}
    else:
        priorities = {
            "SOCIAL": 0.95 if _changed_preference(social) else 0.60,
            "MEMORY": 0.85 if _changed_preference(memory) else 0.45,
            "ACTION": 0.80 if _changed_preference(action) else (0.75 if "E3" in action else 0.40),
            "LANGUAGE": 0.50 if _changed_preference(language) else (0.70 if "E3" in language else 0.35),
        }

    return [
        OperationProposal(
            "SOCIAL",
            "SEND_RECOMMENDATION",
            priorities["SOCIAL"],
            1,
            "priority rises when SOCIAL locally detects a changed preference",
        ),
        OperationProposal(
            "MEMORY",
            "SURFACE_HISTORY",
            priorities["MEMORY"],
            1,
            "priority rises when MEMORY locally holds conflicting temporal evidence",
        ),
        OperationProposal(
            "ACTION",
            "QUERY_CONTEXT",
            priorities["ACTION"],
            1,
            "priority rises when ACTION has current evidence requiring reconciliation",
        ),
        OperationProposal(
            "LANGUAGE",
            "REQUEST_EXPLANATORY_CONTEXT",
            priorities["LANGUAGE"],
            1,
            "priority rises when LANGUAGE has a current fact without older context",
        ),
    ]


def _select_birthday_behavior(
    *,
    direct_preference: str | None,
    social_recommendation: str | None,
    history_conflict: bool,
) -> str:
    direct_choice = None
    if direct_preference == "welcome":
        direct_choice = "SURPRISE_B"
    elif direct_preference == "avoid":
        direct_choice = "ASK_B_FIRST"

    if social_recommendation is not None:
        if direct_choice is None:
            return social_recommendation
        if direct_choice == social_recommendation:
            return direct_choice
        return "ASK_B_FIRST"
    if history_conflict:
        return "ASK_B_FIRST"
    return direct_choice or "ASK_B_FIRST"


def run_endogenous_demand_experiment(
    access: Condition,
    *,
    capacity: int = 1,
    uniform_priority: bool = False,
) -> dict[str, Any]:
    """Experiment 2: local knowledge changes demand and therefore allocation."""
    local = _birthday_local_state(access)
    proposals = _experiment_2_proposals(local, uniform_priority=uniform_priority)
    round_id = "experiment2:uniform" if uniform_priority else f"experiment2:endogenous:{access.value}"
    allocation = allocate_operations(
        proposals,
        capacity=capacity,
        seed=0,
        round_id=round_id,
    )
    winners = [record for record in allocation if record.granted]

    social_recommendation = None
    history_conflict = False
    for winner in winners:
        if winner.actor_id == "SOCIAL":
            preference = _latest_preference(local["SOCIAL"])
            social_recommendation = "SURPRISE_B" if preference == "welcome" else "ASK_B_FIRST"
        elif winner.actor_id == "MEMORY":
            history_conflict = _changed_preference(local["MEMORY"])

    final_behavior = _select_birthday_behavior(
        direct_preference=_latest_preference(local["ACTION"]),
        social_recommendation=social_recommendation,
        history_conflict=history_conflict,
    )
    return {
        "experiment": 2,
        "access_condition": access.value,
        "priority_mode": "uniform_ablation" if uniform_priority else "endogenous_local_demand",
        "capacity": capacity,
        "local_state": local,
        "proposals": [asdict(item) for item in proposals],
        "allocation": [asdict(item) for item in allocation],
        "winner_actors": [item.actor_id for item in winners],
        "social_recommendation_delivered": social_recommendation,
        "history_conflict_surfaced": history_conflict,
        "final_behavior": final_behavior,
    }


def run_experiment_2() -> dict[str, Any]:
    global_run = run_endogenous_demand_experiment(Condition.GLOBAL)
    differential_run = run_endogenous_demand_experiment(Condition.DIFFERENTIAL)
    uniform_global = run_endogenous_demand_experiment(Condition.GLOBAL, uniform_priority=True)
    uniform_differential = run_endogenous_demand_experiment(
        Condition.DIFFERENTIAL, uniform_priority=True
    )
    return {
        "global": global_run,
        "differential": differential_run,
        "uniform_ablation_global": uniform_global,
        "uniform_ablation_differential": uniform_differential,
        "knowledge_changed_allocator_winner": (
            global_run["winner_actors"] != differential_run["winner_actors"]
        ),
        "uniform_ablation_removed_knowledge_dependent_winner_change": (
            uniform_global["winner_actors"] == uniform_differential["winner_actors"]
        ),
    }


def _concern_priority(reserve: float, context_match: float) -> float:
    return 0.25 + 0.25 * context_match + 0.25 * tanh(reserve)


def run_latent_concern_experiment(
    *,
    quiet_ticks: int = 6,
    with_history: bool = True,
) -> dict[str, Any]:
    """Experiment 3: accumulated history changes later competitiveness."""
    reserve = 0.0
    trace: list[dict[str, Any]] = []
    for tick in range(1, quiet_ticks + 1):
        before = reserve
        if with_history:
            # The unresolved concern banks a fraction of otherwise unused quiet capacity.
            reserve = min(1.5, reserve + 0.25)
        trace.append(
            {
                "tick": tick,
                "context_match": 0.0,
                "reserve_before": before,
                "reserve_after": reserve,
                "external_reminder": False,
            }
        )

    context_tick = quiet_ticks + 1
    concern = OperationProposal(
        "CONCERN",
        "RECRUIT_MEMORY",
        _concern_priority(reserve, 1.0),
        1,
        "later context matches the unresolved concern; stored reserve contributes bounded bid strength",
    )
    distractor = OperationProposal(
        "DISTRACTOR",
        "PROCESS_CURRENT_DISTRACTOR",
        0.70,
        1,
        "strong current competitor",
    )
    allocation = allocate_operations(
        [concern, distractor], capacity=1, seed=0, round_id="experiment3:context"
    )
    winner = next(record for record in allocation if record.granted)
    recalled_event = "E1_UNRESOLVED" if winner.actor_id == "CONCERN" else None
    return {
        "experiment": 3,
        "with_history": with_history,
        "quiet_ticks": quiet_ticks,
        "reserve_at_context": reserve,
        "trace": trace,
        "context_tick": context_tick,
        "context_match": 1.0,
        "proposals": [asdict(concern), asdict(distractor)],
        "allocation": [asdict(item) for item in allocation],
        "winner_actor": winner.actor_id,
        "recalled_event": recalled_event,
        "explicit_reminder_used": False,
    }


def run_experiment_3() -> dict[str, Any]:
    history = run_latent_concern_experiment(with_history=True)
    no_history = run_latent_concern_experiment(with_history=False)
    return {
        "history": history,
        "no_history_ablation": no_history,
        "history_changed_future_competitiveness": (
            history["winner_actor"] == "CONCERN"
            and no_history["winner_actor"] != "CONCERN"
        ),
    }


def run_epistemic_feedback_experiment(
    *,
    feedback_enabled: bool,
    ticks: int = 6,
) -> dict[str, Any]:
    """Experiment 4: winning resources changes knowledge, which changes future demand."""
    evidence = {"EXPLORATION": 1, "ROUTINE": 0}
    win_streak = {"EXPLORATION": 0, "ROUTINE": 0}
    trace: list[dict[str, Any]] = []

    for tick in range(1, ticks + 1):
        proposals: list[OperationProposal] = []
        for actor in ("EXPLORATION", "ROUTINE"):
            priority = 0.50 + 0.08 * evidence[actor] - 0.06 * win_streak[actor]
            proposals.append(
                OperationProposal(
                    actor,
                    "SAMPLE_RELEVANT_CHANNEL",
                    priority,
                    1,
                    "local evidence raises expected value while sustained use creates fatigue",
                )
            )
        allocation = allocate_operations(
            proposals, capacity=1, seed=0, round_id=f"experiment4:{tick}"
        )
        winner = next(record for record in allocation if record.granted).actor_id
        before = dict(evidence)

        for actor in win_streak:
            if actor == winner:
                win_streak[actor] += 1
            else:
                win_streak[actor] = 0

        discovered = None
        if feedback_enabled:
            evidence[winner] += 1
            discovered = f"{winner}_EVIDENCE_{evidence[winner]}"

        trace.append(
            {
                "tick": tick,
                "evidence_before": before,
                "proposals": [asdict(item) for item in proposals],
                "winner_actor": winner,
                "new_evidence": discovered,
                "evidence_after": dict(evidence),
                "win_streak_after": dict(win_streak),
            }
        )

    exploration_wins = sum(1 for row in trace if row["winner_actor"] == "EXPLORATION")
    routine_wins = sum(1 for row in trace if row["winner_actor"] == "ROUTINE")
    return {
        "experiment": 4,
        "feedback_enabled": feedback_enabled,
        "ticks": ticks,
        "trace": trace,
        "final_evidence": dict(evidence),
        "wins": {"EXPLORATION": exploration_wins, "ROUTINE": routine_wins},
        "allocation_changed_knowledge": any(row["new_evidence"] is not None for row in trace),
    }


def run_experiment_4() -> dict[str, Any]:
    feedback = run_epistemic_feedback_experiment(feedback_enabled=True)
    no_feedback = run_epistemic_feedback_experiment(feedback_enabled=False)
    return {
        "feedback": feedback,
        "no_feedback_ablation": no_feedback,
        "feedback_increased_exploration_capture": (
            feedback["wins"]["EXPLORATION"] > no_feedback["wins"]["EXPLORATION"]
        ),
        "closed_loop_observed": (
            feedback["allocation_changed_knowledge"]
            and feedback["final_evidence"]["EXPLORATION"]
            > no_feedback["final_evidence"]["EXPLORATION"]
            and feedback["wins"]["EXPLORATION"]
            > no_feedback["wins"]["EXPLORATION"]
        ),
    }


def run_four_experiment_series() -> dict[str, Any]:
    matrix = run_canonical_matrix()
    experiment_1 = {
        "matrix": matrix,
        "analysis": matrix_analysis(matrix),
        "causal_link": "scarcity changes realized information access",
    }
    experiment_2 = run_experiment_2()
    experiment_3 = run_experiment_3()
    experiment_4 = run_experiment_4()
    return {
        "experiment_1": experiment_1,
        "experiment_2": experiment_2,
        "experiment_3": experiment_3,
        "experiment_4": experiment_4,
        "causal_chain": {
            "scarcity_to_access": experiment_1["analysis"]["scarce_global_created_resource_asymmetry"],
            "knowledge_to_demand": experiment_2["knowledge_changed_allocator_winner"],
            "history_to_competitiveness": experiment_3["history_changed_future_competitiveness"],
            "allocation_to_future_knowledge": experiment_4["closed_loop_observed"],
        },
    }
