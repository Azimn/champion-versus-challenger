from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Callable

from .exp003_evaluation import (
    reviewer_near_neutral_evidence,
    reviewer_person_specificity,
    reviewer_reversal,
)
from .exp004_evaluation import (
    reviewer_bounded_capacity as concern_bounded_capacity,
    reviewer_duplicate_assignment,
    reviewer_interruption,
    reviewer_reverse_order,
    reviewer_unrelated_cancel,
)
from .exp005_evaluation import (
    reviewer_bounded_store as prospective_bounded_store,
    reviewer_cancel_before_cue,
    reviewer_multiple_future_commitments,
    reviewer_one_shot_activation,
    reviewer_wrong_cues,
)
from .exp006_evaluation import (
    reviewer_entity_specificity,
    reviewer_hidden_change_not_omniscient,
    reviewer_observed_revision,
    reviewer_perception_order,
    reviewer_unobserved_entity_has_no_fabricated_belief,
)
from .exp007_challenger import EligibilityRecord, EligibilityTraceCharacter
from .exp007_evaluation import development_suite, historical_regressions
from .runtime import Event, PersistentCharacter


Factory = Callable[[], PersistentCharacter]


def _passed(result: dict) -> bool:
    return bool(result.get("passed", False))


def autonomous_continuation(factory: Factory) -> dict:
    agent = factory()
    agent.step(Event(kind="task_assign", concern="finish_report", forced_action="idle"))
    actions = [
        agent.step(Event(kind="neutral", available_actions=("work", "rest", "idle")))
        for _ in range(6)
    ]
    state = agent.snapshot()
    active = state.get("active_concern")
    if active is None and state.get("concern_ledger"):
        active = max(state["concern_ledger"], key=state["concern_ledger"].get)
    return {
        "passed": "work" in actions and active is None,
        "actions": actions,
        "state": state,
    }


def base_need_roles(factory: Factory) -> dict:
    # These are not new capabilities. They document the direct observable role of
    # the three original v0 pressure variables during global re-litigation.
    fatigue_agent = factory()
    fatigue_choice = fatigue_agent.step(
        Event(kind="neutral", available_actions=("rest", "work", "idle"))
    )

    affiliation_agent = factory()
    affiliation_choice = affiliation_agent.step(
        Event(
            kind="encounter",
            actor="Stranger",
            available_actions=("socialize:Stranger", "avoid:Stranger", "idle"),
        )
    )

    competence_agent = factory()
    competence_agent.step(Event(kind="neutral", forced_action="rest"))
    competence_choice = competence_agent.step(
        Event(kind="neutral", available_actions=("work", "rest", "idle"))
    )

    return {
        "fatigue_drives_rest": fatigue_choice == "rest",
        "affiliation_drives_unscripted_social_approach": affiliation_choice == "socialize:Stranger",
        "competence_drives_work_after_rest": competence_choice == "work",
        "choices": {
            "fatigue": fatigue_choice,
            "affiliation": affiliation_choice,
            "competence": competence_choice,
        },
    }


def earned_suite(factory: Factory) -> dict:
    historical = historical_regressions(factory)
    development = development_suite(factory)
    extra = {
        "exp003_reversal": reviewer_reversal(factory),
        "exp003_near_neutral": reviewer_near_neutral_evidence(factory),
        "exp003_person_specificity": reviewer_person_specificity(factory),
        "exp004_reverse_order": reviewer_reverse_order(factory),
        "exp004_unrelated_cancel": reviewer_unrelated_cancel(factory),
        "exp004_duplicate_assignment": reviewer_duplicate_assignment(factory),
        "exp004_bounded_capacity": concern_bounded_capacity(factory),
        "exp004_interruption": reviewer_interruption(factory),
        "exp005_cancel_before_cue": reviewer_cancel_before_cue(factory),
        "exp005_wrong_cues": reviewer_wrong_cues(factory),
        "exp005_multiple_future": reviewer_multiple_future_commitments(factory),
        "exp005_one_shot": reviewer_one_shot_activation(factory),
        "exp005_bounded_store": prospective_bounded_store(factory),
        "exp006_observed_revision": reviewer_observed_revision(factory),
        "exp006_hidden_not_omniscient": reviewer_hidden_change_not_omniscient(factory),
        "exp006_entity_specificity": reviewer_entity_specificity(factory),
        "exp006_unobserved_no_belief": reviewer_unobserved_entity_has_no_fabricated_belief(factory),
        "exp006_perception_order": reviewer_perception_order(factory),
        "autonomous_continuation": autonomous_continuation(factory),
    }
    flat = {**historical, **development, **extra}
    failures = sorted(name for name, result in flat.items() if not _passed(result))
    return {
        "passed": not failures,
        "failures": failures,
        "historical_failures": sorted(name for name, result in historical.items() if not _passed(result)),
        "development_failures": sorted(name for name, result in development.items() if not _passed(result)),
        "extra_failures": sorted(name for name, result in extra.items() if not _passed(result)),
    }


class NoRelationshipCharacter(EligibilityTraceCharacter):
    @property
    def has_relationship_memory(self) -> bool:
        return False


class NoAffectCharacter(EligibilityTraceCharacter):
    @property
    def has_affect_residue(self) -> bool:
        return False


class NoConcernLedgerCharacter(EligibilityTraceCharacter):
    max_concerns = 0


class NoHabitCharacter(EligibilityTraceCharacter):
    @property
    def has_habit_learning(self) -> bool:
        return False


class NoPartnerReliabilityCharacter(EligibilityTraceCharacter):
    @property
    def has_partner_model(self) -> bool:
        return False


class NoUncertaintyPolicyCharacter(EligibilityTraceCharacter):
    def _score_action(self, action, event, immediate_threat, task_pressure):
        if action.startswith("verify:") or action.startswith("delegate:"):
            return PersistentCharacter._score_action(
                self, action, event, immediate_threat, task_pressure
            )
        return super()._score_action(action, event, immediate_threat, task_pressure)


class NoProspectiveCharacter(EligibilityTraceCharacter):
    max_prospective = 0


class NoSubjectiveFactsCharacter(EligibilityTraceCharacter):
    def _process_event(self, event: Event) -> tuple[float, float]:
        if event.kind in {"observe_location", "hidden_world_change"}:
            # Preserve event timing while removing subject-owned fact acquisition.
            self._advance_eligibility_age()
            return 0.0, 0.0
        return super()._process_event(event)

    def _score_action(self, action, event, immediate_threat, task_pressure):
        if action.startswith("search:"):
            return 0.10
        return super()._score_action(action, event, immediate_threat, task_pressure)


class NoDelayedTraceCharacter(EligibilityTraceCharacter):
    max_eligibility_records = 0


class NoFatigueCharacter(EligibilityTraceCharacter):
    @property
    def fatigue(self) -> float:
        return 0.0

    @fatigue.setter
    def fatigue(self, value: float) -> None:
        del value


class NoAffiliationCharacter(EligibilityTraceCharacter):
    @property
    def affiliation(self) -> float:
        return 0.0

    @affiliation.setter
    def affiliation(self, value: float) -> None:
        del value


class NoCompetenceCharacter(EligibilityTraceCharacter):
    @property
    def competence(self) -> float:
        return 0.0

    @competence.setter
    def competence(self, value: float) -> None:
        del value


class DerivedConcernViewCharacter(EligibilityTraceCharacter):
    """GSA-H1: concern compatibility state is derived, not independently stored."""

    @property
    def active_concern(self):
        concerns = getattr(self, "concerns", {})
        if not concerns:
            return None
        return max(concerns.items(), key=lambda item: item[1])[0]

    @active_concern.setter
    def active_concern(self, value) -> None:
        # Compatibility writes are intentionally discarded. `concerns` is the
        # authoritative persistent state.
        del value

    @property
    def concern_strength(self) -> float:
        concerns = getattr(self, "concerns", {})
        if not concerns:
            return 0.0
        return max(concerns.values())

    @concern_strength.setter
    def concern_strength(self, value: float) -> None:
        del value

    def persistent_state_bytes(self) -> int:
        state = self.snapshot()
        state.pop("active_concern", None)
        state.pop("concern_strength", None)
        return len(json.dumps(state, sort_keys=True).encode("utf-8"))

    def mechanism_count(self) -> int:
        # Base single-concern persistence is no longer independent machinery. The
        # bounded concern ledger is the sole persistent concern mechanism.
        return super().mechanism_count() - 1


class TraceBackedImmediateHabitCharacter(EligibilityTraceCharacter):
    """GSA-H2: use age-zero trace state instead of duplicated last-action fields."""

    @property
    def last_action(self):
        return None

    @last_action.setter
    def last_action(self, value) -> None:
        del value

    @property
    def last_context(self):
        return None

    @last_context.setter
    def last_context(self, value) -> None:
        del value

    def _apply_immediate_outcome(self, event: Event) -> bool:
        if event.context is not None or event.reward == 0.0:
            return False
        current = [row for row in self.eligibility_records if row.age == 0]
        if len(current) != 1:
            return False
        row = current[0]
        key = (row.context, row.action)
        updated = self.habits.get(key, 0.0) + self.habit_learning_rate * event.reward
        self.habits[key] = self._clamp(updated, -1.0, 1.0)
        return True

    def snapshot(self) -> dict:
        state = super().snapshot()
        state.pop("last_action", None)
        state.pop("last_context", None)
        return state


class CompressedV9Character(DerivedConcernViewCharacter):
    """Combination of H1 and H2 after each is tested independently."""

    @property
    def last_action(self):
        return None

    @last_action.setter
    def last_action(self, value) -> None:
        del value

    @property
    def last_context(self):
        return None

    @last_context.setter
    def last_context(self, value) -> None:
        del value

    def _apply_immediate_outcome(self, event: Event) -> bool:
        if event.context is not None or event.reward == 0.0:
            return False
        current = [row for row in self.eligibility_records if row.age == 0]
        if len(current) != 1:
            return False
        row = current[0]
        key = (row.context, row.action)
        updated = self.habits.get(key, 0.0) + self.habit_learning_rate * event.reward
        self.habits[key] = self._clamp(updated, -1.0, 1.0)
        return True

    def snapshot(self) -> dict:
        state = super().snapshot()
        state.pop("last_action", None)
        state.pop("last_context", None)
        return state


def immediate_noncontext_intervener(factory: Factory) -> dict:
    agent = factory()
    agent.step(Event(kind="context", context="morning", forced_action="walk"))
    agent.step(Event(kind="encounter", actor="Alex", forced_action="socialize:Alex"))
    agent.step(Event(kind="outcome", reward=1.0, context=None, forced_action="idle"))
    return {
        "passed": agent.habits.get(("morning", "walk"), 0.0) == 0.0,
        "morning_walk": agent.habits.get(("morning", "walk"), 0.0),
    }


def simplification_metrics(factory: Factory) -> dict:
    fresh = factory()
    representative = factory()
    representative.step(Event(kind="task_assign", concern="finish_report", forced_action="idle"))
    representative.step(Event(kind="task_assign", concern="call_morgan", forced_action="idle"))
    representative.step(Event(kind="context", context="morning", forced_action="walk"))
    representative.step(Event(kind="support", actor="Alex", forced_action="idle"))
    representative.step(Event(kind="observed_reliable", actor="Alex", forced_action="idle"))
    representative.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    return {
        "mechanism_count": representative.mechanism_count(),
        "fresh_persistent_bytes": representative.__class__().persistent_state_bytes(),
        "representative_persistent_bytes": representative.persistent_state_bytes(),
        "representative_snapshot": representative.snapshot(),
    }


def removal_tournament() -> dict:
    ablations = {
        "relationship_history": NoRelationshipCharacter,
        "affect_residue": NoAffectCharacter,
        "concern_ledger": NoConcernLedgerCharacter,
        "habit_learning": NoHabitCharacter,
        "partner_reliability": NoPartnerReliabilityCharacter,
        "uncertainty_policy": NoUncertaintyPolicyCharacter,
        "prospective_commitments": NoProspectiveCharacter,
        "subjective_facts": NoSubjectiveFactsCharacter,
        "delayed_credit_trace": NoDelayedTraceCharacter,
        "fatigue_pressure": NoFatigueCharacter,
        "affiliation_pressure": NoAffiliationCharacter,
        "competence_pressure": NoCompetenceCharacter,
    }
    rows = {}
    for name, factory in ablations.items():
        suite = earned_suite(factory)
        rows[name] = {
            "earned_suite_passed": suite["passed"],
            "failures": suite["failures"],
            "base_need_roles": base_need_roles(factory) if name.endswith("_pressure") else None,
        }
    return rows


def simplification_tournament() -> dict:
    candidates = {
        "frozen_v9": EligibilityTraceCharacter,
        "H1_derived_concern_view": DerivedConcernViewCharacter,
        "H2_trace_backed_immediate_habit": TraceBackedImmediateHabitCharacter,
        "H1_H2_combined": CompressedV9Character,
    }
    rows = {}
    for name, factory in candidates.items():
        suite = earned_suite(factory)
        extra = immediate_noncontext_intervener(factory)
        rows[name] = {
            "earned_suite_passed": suite["passed"],
            "failures": suite["failures"],
            "immediate_noncontext_intervener": extra,
            "metrics": simplification_metrics(factory),
        }
    return rows


def run() -> dict:
    frozen_suite = earned_suite(EligibilityTraceCharacter)
    removals = removal_tournament()
    simplifications = simplification_tournament()
    return {
        "phase": "GLOBAL STRUCTURAL ABLATION v9, pass 1",
        "frozen_v9_earned_suite_passed": frozen_suite["passed"],
        "frozen_v9_failures": frozen_suite["failures"],
        "removal_tournament": removals,
        "simplification_tournament": simplifications,
        "interpretation_rules": {
            "removal_failure": "Mechanism remains causally defended by at least one current earned probe, subject to checking that the ablation is specific.",
            "removal_pass": "Not automatic deletion. It means the current earned suite does not defend the mechanism; original/base behavioral role must be re-litigated before subtraction.",
            "simplification_pass": "Eligible for deeper adversarial review only if state and/or independently counted machinery are actually reduced.",
        },
    }


def compact(value):
    if isinstance(value, dict):
        return {
            key: compact(item)
            for key, item in value.items()
            if key not in {"trace", "traces", "representative_snapshot"}
        }
    if isinstance(value, list):
        return [compact(item) for item in value]
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    report = compact(run())
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not report["frozen_v9_earned_suite_passed"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
