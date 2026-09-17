from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

from .exp010_challenger import CapacityThreeConcernCharacter
from .runtime import Event

MECHANISMS = (
    "fatigue",
    "affiliation",
    "competence",
    "relationship_history",
    "affect_residue",
    "habit_learning",
    "partner_reliability",
    "concern_ledger",
    "prospective_commitments",
    "subjective_facts",
    "eligibility_trace",
)


class BasisAblationCharacter(CapacityThreeConcernCharacter):
    """Audit-only v9.3 with independently gated causal contributions.

    This class is not a production challenger. Capacities and environment/event rules
    remain frozen. Disabled mechanisms receive no replacement behavior or hidden
    storage. The EXP-003 zero-state uncertainty policy remains fixed because it is not
    one of the 11 counted persistent mechanisms.
    """

    def __init__(self, enabled=MECHANISMS):
        self._basis_enabled = frozenset(enabled)
        super().__init__()

    def _on(self, name: str) -> bool:
        return name in self._basis_enabled

    @property
    def has_relationship_memory(self) -> bool:
        return self._on("relationship_history")

    @property
    def has_affect_residue(self) -> bool:
        return self._on("affect_residue")

    @property
    def has_habit_learning(self) -> bool:
        return self._on("habit_learning")

    @property
    def has_partner_model(self) -> bool:
        return self._on("partner_reliability")

    def _activate_cue(self, context: str | None) -> None:
        if not self._on("prospective_commitments") or not self._on("concern_ledger"):
            return
        super()._activate_cue(context)

    def _create_eligibility(self, context: str, action: str) -> None:
        if self._on("eligibility_trace"):
            super()._create_eligibility(context, action)

    def _advance_eligibility_age(self) -> None:
        if self._on("eligibility_trace"):
            super()._advance_eligibility_age()
        else:
            self.eligibility_records.clear()

    def _apply_delayed_outcome(self, event: Event) -> bool:
        if not self._on("eligibility_trace") or not self._on("habit_learning"):
            return False
        return super()._apply_delayed_outcome(event)

    def _apply_immediate_outcome(self, event: Event) -> bool:
        if not self._on("eligibility_trace") or not self._on("habit_learning"):
            return False
        return super()._apply_immediate_outcome(event)

    def _process_event(self, event: Event) -> tuple[float, float]:
        if event.kind == "future_commitment" and not self._on("prospective_commitments"):
            return 0.0, 0.0
        if event.kind in {"observe_location", "hidden_world_change"} and not self._on("subjective_facts"):
            return 0.0, 0.0
        if event.kind in {"task_assign", "task_cancel"} and not self._on("concern_ledger"):
            if event.kind == "task_assign":
                return 0.0, self._clamp(0.80 * event.intensity)
            return 0.0, 0.0
        return super()._process_event(event)

    def _drift(self) -> None:
        super()._drift()
        if not self._on("concern_ledger"):
            self.concerns.clear()
        if not self._on("prospective_commitments"):
            self.prospective_commitments.clear()
        if not self._on("subjective_facts"):
            self.location_beliefs.clear()
        if not self._on("eligibility_trace"):
            self.eligibility_records.clear()

    def _score_action(self, action, event, immediate_threat, task_pressure):
        if action == "idle":
            return 0.10
        if action == "rest":
            return self.fatigue if self._on("fatigue") else 0.0
        if action == "work":
            score = self.competence if self._on("competence") else 0.0
            score += task_pressure
            if self._on("concern_ledger") and self.active_concern is not None:
                score += 0.90 * self.concern_strength
            return score
        if action.startswith("socialize:"):
            actor = action.split(":", 1)[1]
            relation = self._relationship(actor) if self._on("relationship_history") else 0.0
            affiliation = self.affiliation if self._on("affiliation") else 0.0
            return affiliation + 0.85 * max(relation, 0.0) - 0.35 * max(-relation, 0.0)
        if action.startswith("avoid:") or action == "avoid":
            actor = action.split(":", 1)[1] if ":" in action else event.actor
            relation = self._relationship(actor) if self._on("relationship_history") else 0.0
            score = immediate_threat + 0.90 * max(-relation, 0.0)
            if self._on("affect_residue"):
                score += 0.75 * self.threat_residue
            return score
        if action.startswith("delegate:"):
            actor = action.split(":", 1)[1]
            reliability = self._reliability(actor) if self._on("partner_reliability") else 0.0
            return 0.10 + 0.80 * max(reliability, 0.0)
        if action.startswith("verify:"):
            actor = action.split(":", 1)[1]
            reliability = self._reliability(actor) if self._on("partner_reliability") else 0.0
            score = 0.10 + 0.80 * max(-reliability, 0.0)
            # Fixed EXP-003 policy is not one of the 11 persistent mechanisms.
            if abs(reliability) < self.uncertainty_threshold:
                score += self.uncertainty_verify_bonus
            return score
        if action.startswith("search:") and event.actor:
            if not self._on("subjective_facts"):
                return 0.10
            location = action.split(":", 1)[1]
            believed = self.location_beliefs.get(event.actor)
            if believed is None:
                return 0.10
            return 0.90 if believed == location else 0.05
        score = 0.10
        if self._on("habit_learning") and event.context is not None:
            score += self.habits.get((event.context, action), 0.0)
        return score

    def audit_persistent_snapshot(self) -> dict:
        full = self.persistent_snapshot()
        if not self._on("fatigue"):
            full["needs"].pop("fatigue", None)
        if not self._on("affiliation"):
            full["needs"].pop("affiliation", None)
        if not self._on("competence"):
            full["needs"].pop("competence", None)
        mapping = {
            "relationship_history": "relationships",
            "affect_residue": "threat_residue",
            "habit_learning": "habits",
            "partner_reliability": "partner_reliability",
            "concern_ledger": "concern_ledger",
            "prospective_commitments": "prospective_commitments",
            "subjective_facts": "location_beliefs",
            "eligibility_trace": "eligibility_records",
        }
        for mechanism, field in mapping.items():
            if not self._on(mechanism):
                full.pop(field, None)
        return full

    def audit_canonical_bytes(self) -> int:
        return len(json.dumps(self.audit_persistent_snapshot(), sort_keys=True, separators=(",", ":")).encode())


def agent(enabled):
    return BasisAblationCharacter(enabled)


def probe_fatigue(enabled):
    a = agent(enabled)
    for _ in range(18):
        a.step(Event(kind="neutral", forced_action="idle"))
    before = a.fatigue
    choice = a.step(Event(kind="neutral", available_actions=("idle", "rest")))
    return choice == "rest" and a.fatigue < before


def probe_affiliation(enabled):
    a = agent(enabled)
    choice = a.step(Event(kind="neutral", actor="morgan", available_actions=("idle", "socialize:morgan")))
    return choice == "socialize:morgan"


def probe_competence(enabled):
    a = agent(enabled)
    for _ in range(20):
        a.step(Event(kind="neutral", forced_action="idle"))
    choice = a.step(Event(kind="neutral", available_actions=("idle", "work")))
    return choice == "work"


def probe_relationship(enabled):
    a = agent(enabled)
    for _ in range(3):
        a.step(Event(kind="hostility", actor="morgan", intensity=1.0, forced_action="idle"))
    m = a.step(Event(kind="neutral", actor="morgan", available_actions=("socialize:morgan", "avoid:morgan")))
    s = a.step(Event(kind="neutral", actor="sarah", available_actions=("socialize:sarah", "avoid:sarah")))
    return m == "avoid:morgan" and s == "socialize:sarah"


def probe_affect(enabled):
    a = agent(enabled)
    a.step(Event(kind="shock", intensity=1.0, forced_action="idle"))
    first = a.step(Event(kind="neutral", available_actions=("idle", "avoid")))
    for _ in range(20):
        a.step(Event(kind="neutral", forced_action="idle"))
    later = a.step(Event(kind="neutral", available_actions=("idle", "avoid")))
    return first == "avoid" and later == "idle"


def learn_walk(a):
    a.step(Event(kind="context", context="morning", forced_action="walk"))
    a.step(Event(kind="outcome", reward=1.0, forced_action="idle"))


def probe_habit(enabled):
    a = agent(enabled)
    learn_walk(a)
    same = a.step(Event(kind="context", context="morning", available_actions=("tea", "walk")))
    other = a.step(Event(kind="context", context="evening", available_actions=("tea", "walk")))
    return same == "walk" and other == "tea"


def probe_reliability(enabled):
    a = agent(enabled)
    for _ in range(3):
        a.step(Event(kind="observed_reliable", actor="morgan", forced_action="idle"))
        a.step(Event(kind="observed_unreliable", actor="sarah", forced_action="idle"))
    m = a.step(Event(kind="neutral", available_actions=("verify:morgan", "delegate:morgan")))
    s = a.step(Event(kind="neutral", available_actions=("delegate:sarah", "verify:sarah")))
    return m == "delegate:morgan" and s == "verify:sarah"


def probe_uncertainty(enabled):
    a = agent(enabled)
    x = a.step(Event(kind="neutral", available_actions=("delegate:new", "verify:new")))
    y = a.step(Event(kind="neutral", available_actions=("verify:new2", "delegate:new2")))
    return x == "verify:new" and y == "verify:new2"


def probe_concerns(enabled):
    a = agent(enabled)
    a.step(Event(kind="task_assign", concern="a", intensity=.5, forced_action="idle"))
    a.step(Event(kind="task_assign", concern="b", intensity=1.0, forced_action="idle"))
    a.step(Event(kind="task_assign", concern="c", intensity=.9, forced_action="idle"))
    three = set(a.concerns) == {"a", "b", "c"}
    a.step(Event(kind="task_cancel", concern="b", forced_action="idle"))
    a.step(Event(kind="task_cancel", concern="c", forced_action="idle"))
    return three and "a" in a.concerns and a.active_concern == "a"


def probe_unresolved_decay(enabled):
    a = agent(enabled)
    a.step(Event(kind="task_assign", concern="portfolio", intensity=1.0, forced_action="idle"))
    for _ in range(1000):
        a.step(Event(kind="neutral", forced_action="idle"))
    weak = "portfolio" in a.concerns and a.concerns.get("portfolio", 1.0) < .08
    a.step(Event(kind="task_cancel", concern="portfolio", forced_action="idle"))
    return weak and "portfolio" not in a.concerns


def probe_prospective(enabled):
    a = agent(enabled)
    a.step(Event(kind="future_commitment", concern="call", context="arrives", forced_action="idle"))
    latent = "call" in a.prospective_commitments and "call" not in a.concerns
    a.step(Event(kind="neutral", context="arrives", forced_action="idle"))
    return latent and "call" in a.concerns and "call" not in a.prospective_commitments


def probe_fact(enabled):
    a = agent(enabled)
    a.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    choice = a.step(Event(kind="retrieve", actor="book", available_actions=("search:shelf", "search:drawer")))
    return choice == "search:drawer"


def probe_hidden(enabled):
    a = agent(enabled)
    a.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    a.step(Event(kind="hidden_world_change", actor="book", context="shelf", forced_action="idle"))
    return a.location_beliefs.get("book") == "drawer"


def probe_revision(enabled):
    a = agent(enabled)
    a.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    a.step(Event(kind="observe_location", actor="book", context="shelf", forced_action="idle"))
    choice = a.step(Event(kind="retrieve", actor="book", available_actions=("search:drawer", "search:shelf")))
    return choice == "search:shelf"


def probe_immediate_learning(enabled):
    a = agent(enabled)
    a.step(Event(kind="context", context="morning", forced_action="walk"))
    a.step(Event(kind="outcome", reward=1.0, forced_action="idle"))
    return a.habits.get(("morning", "walk"), 0.0) > 0


def probe_delayed(enabled):
    a = agent(enabled)
    a.step(Event(kind="context", context="garden", forced_action="inspect"))
    a.step(Event(kind="neutral", forced_action="idle"))
    a.step(Event(kind="outcome", context="garden", reward=1.0, forced_action="idle"))
    return a.habits.get(("garden", "inspect"), 0.0) > 0


def probe_ambiguity(enabled):
    a = agent(enabled)
    a.step(Event(kind="context", context="lab", forced_action="inspect"))
    a.step(Event(kind="context", context="lab", forced_action="wait"))
    before = dict(a.habits)
    a.step(Event(kind="outcome", context="lab", reward=1.0, forced_action="idle"))
    return a.habits == before


def probe_reconstruction(enabled):
    a = agent(enabled)
    a.step(Event(kind="support", actor="morgan", forced_action="idle"))
    a.step(Event(kind="shock", intensity=.5, forced_action="idle"))
    a.step(Event(kind="task_assign", concern="report", intensity=.8, forced_action="idle"))
    a.step(Event(kind="future_commitment", concern="call", context="evening", forced_action="idle"))
    a.step(Event(kind="observe_location", actor="book", context="desk", forced_action="idle"))
    a.step(Event(kind="context", context="morning", forced_action="walk"))
    encoded = a.serialize_persistent()
    b = CapacityThreeConcernCharacter.from_persistent_json(encoded)
    # Full reconstruction is an architecture invariant. For subset accounting,
    # compare only enabled mechanism fields through a fresh audit wrapper snapshot.
    aa = a.audit_persistent_snapshot()
    full = b.persistent_snapshot()
    keys = set(aa)
    projected = {k: full[k] for k in keys}
    if "needs" in aa:
        projected["needs"] = {k: full["needs"][k] for k in aa["needs"]}
    return aa == projected


PROBES = {
    "fatigue_pressure": probe_fatigue,
    "affiliation_pressure": probe_affiliation,
    "competence_pressure": probe_competence,
    "partner_specific_relationship_history": probe_relationship,
    "affective_carryover_decay": probe_affect,
    "contextual_habit_learning": probe_habit,
    "partner_reliability_expectation": probe_reliability,
    "uncertainty_behavior": probe_uncertainty,
    "bounded_unresolved_concerns": probe_concerns,
    "unresolved_existence_vs_activation": probe_unresolved_decay,
    "three_way_concern_suppression_return": probe_concerns,
    "prospective_cue_reactivation": probe_prospective,
    "subjective_location_fact": probe_fact,
    "hidden_world_non_interference": probe_hidden,
    "direct_observation_revision": probe_revision,
    "immediate_action_learning": probe_immediate_learning,
    "bounded_context_delayed_credit": probe_delayed,
    "ambiguity_abstention": probe_ambiguity,
    "persistent_reconstruction": probe_reconstruction,
}


def evaluate_subset(enabled):
    enabled = tuple(enabled)
    outcomes = {}
    errors = {}
    for name, probe in PROBES.items():
        try:
            outcomes[name] = bool(probe(enabled))
        except Exception as exc:  # preserve structural/runtime failures as data
            outcomes[name] = False
            errors[name] = f"{type(exc).__name__}: {exc}"
    sample = agent(enabled)
    return {
        "enabled": list(enabled),
        "count": len(enabled),
        "structurally_valid": not errors,
        "capabilities": outcomes,
        "coverage": sum(outcomes.values()),
        "total_capabilities": len(outcomes),
        "full_coverage": all(outcomes.values()),
        "fresh_audit_canonical_bytes": sample.audit_canonical_bytes(),
        "errors": errors,
    }


def run():
    rows = []
    for mask in range(1 << len(MECHANISMS)):
        enabled = [m for i, m in enumerate(MECHANISMS) if mask & (1 << i)]
        rows.append(evaluate_subset(enabled))
    full = rows[-1]
    by_count = {}
    for n in range(len(MECHANISMS) + 1):
        group = [r for r in rows if r["count"] == n]
        best_cov = max(r["coverage"] for r in group)
        best = [r for r in group if r["coverage"] == best_cov]
        by_count[str(n)] = {
            "best_coverage": best_cov,
            "total_capabilities": full["total_capabilities"],
            "best_subsets": [r["enabled"] for r in best[:20]],
            "best_subset_count": len(best),
        }
    full_rows = [r for r in rows if r["full_coverage"]]
    min_count = min((r["count"] for r in full_rows), default=None)
    minimal = [r for r in full_rows if r["count"] == min_count]
    single_ablation = {}
    full_set = set(MECHANISMS)
    for m in MECHANISMS:
        row = next(r for r in rows if set(r["enabled"]) == full_set - {m})
        single_ablation[m] = {
            "coverage": row["coverage"],
            "lost": [k for k, v in row["capabilities"].items() if not v],
        }
    return {
        "audit":"MBASE-001",
        "champion":"v9.3_concern_capacity_three",
        "champion_commit":"a10bc27579bf5bd0ff1a90d6ad6e3f337d8ed7bc",
        "mechanisms":list(MECHANISMS),
        "fixed_capacities":{"concerns":3,"prospective":2,"eligibility":2},
        "subset_count":len(rows),
        "full_reference":full,
        "minimum_full_coverage_count":min_count,
        "minimal_full_coverage_subsets":[r["enabled"] for r in minimal],
        "full_coverage_subset_count":len(full_rows),
        "single_ablation":single_ablation,
        "coverage_frontier":by_count,
        "rows":rows,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    report = run()
    summary = {k:v for k,v in report.items() if k != "rows"}
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2, sort_keys=True)+"\n", encoding="utf-8")

if __name__ == "__main__":
    main()
