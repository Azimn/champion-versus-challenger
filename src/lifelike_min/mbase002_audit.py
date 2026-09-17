from __future__ import annotations

import argparse, json
from pathlib import Path

from . import mbase001_audit as v1
from . import mbase001_audit_v2 as v2
from . import mbase001_audit_v3 as v3
from .exp012_challenger import HabitTemporalPlasticityCharacter
from .runtime import Event

MECHANISMS = v1.MECHANISMS


class MBase002Character(HabitTemporalPlasticityCharacter):
    """Audit-only post-EXP-012 mechanism gating over the exact v9.5 behavior."""

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

    def _activate_cue(self, context):
        if not self._on("prospective_commitments") or not self._on("concern_ledger"):
            return
        return super()._activate_cue(context)

    def _create_eligibility(self, context, action):
        if self._on("eligibility_trace"):
            return super()._create_eligibility(context, action)

    def _advance_eligibility_age(self):
        if self._on("eligibility_trace"):
            return super()._advance_eligibility_age()
        self.eligibility_records.clear()

    def _apply_delayed_outcome(self, event):
        if not self._on("eligibility_trace") or not self._on("habit_learning"):
            return False
        return super()._apply_delayed_outcome(event)

    def _apply_immediate_outcome(self, event):
        if not self._on("eligibility_trace") or not self._on("habit_learning"):
            return False
        return super()._apply_immediate_outcome(event)

    def _process_event(self, event):
        if event.kind == "future_commitment" and not self._on("prospective_commitments"):
            return 0.0, 0.0
        if event.kind in {"observe_location", "hidden_world_change"} and not self._on("subjective_facts"):
            return 0.0, 0.0
        if event.kind in {"task_assign", "task_cancel"} and not self._on("concern_ledger"):
            if event.kind == "task_assign":
                return 0.0, self._clamp(0.80 * event.intensity)
            return 0.0, 0.0
        return super()._process_event(event)

    def _drift(self):
        super()._drift()
        if not self._on("concern_ledger"):
            self.concerns.clear()
        if not self._on("prospective_commitments"):
            self.prospective_commitments.clear()
        if not self._on("subjective_facts"):
            self.location_beliefs.clear()
        if not self._on("eligibility_trace"):
            self.eligibility_records.clear()
        if not self._on("habit_learning"):
            self.habits.clear()

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
            actor=action.split(":",1)[1]
            relation=self._relationship(actor) if self._on("relationship_history") else 0.0
            affiliation=self.affiliation if self._on("affiliation") else 0.0
            return affiliation + 0.85*max(relation,0.0)-0.35*max(-relation,0.0)
        if action.startswith("avoid:") or action=="avoid":
            actor=action.split(":",1)[1] if ":" in action else event.actor
            relation=self._relationship(actor) if self._on("relationship_history") else 0.0
            score=immediate_threat + 0.90*max(-relation,0.0)
            if self._on("affect_residue"):
                score += 0.75*self.threat_residue
            return score
        if action.startswith("delegate:"):
            actor=action.split(":",1)[1]
            reliability=self._reliability(actor) if self._on("partner_reliability") else 0.0
            return 0.10+0.80*max(reliability,0.0)
        if action.startswith("verify:"):
            actor=action.split(":",1)[1]
            reliability=self._reliability(actor) if self._on("partner_reliability") else 0.0
            score=0.10+0.80*max(-reliability,0.0)
            if abs(reliability)<self.uncertainty_threshold:
                score += self.uncertainty_verify_bonus
            return score
        if action.startswith("search:") and event.actor:
            if not self._on("subjective_facts"):
                return 0.10
            location=action.split(":",1)[1]
            believed=self.location_beliefs.get(event.actor)
            if believed is None:
                return 0.10
            return 0.90 if believed==location else 0.05
        score=0.10
        if self._on("habit_learning") and event.context is not None:
            score += self.habits.get((event.context,action),0.0)
        return score

    def audit_persistent_snapshot(self):
        full=self.persistent_snapshot()
        if not self._on("fatigue"): full["needs"].pop("fatigue",None)
        if not self._on("affiliation"): full["needs"].pop("affiliation",None)
        if not self._on("competence"): full["needs"].pop("competence",None)
        mapping={
            "relationship_history":"relationships",
            "affect_residue":"threat_residue",
            "habit_learning":"habits",
            "partner_reliability":"partner_reliability",
            "concern_ledger":"concern_ledger",
            "prospective_commitments":"prospective_commitments",
            "subjective_facts":"location_beliefs",
            "eligibility_trace":"eligibility_records",
        }
        for mechanism,field in mapping.items():
            if not self._on(mechanism):
                full.pop(field,None)
        return full

    def audit_canonical_bytes(self):
        return len(json.dumps(self.audit_persistent_snapshot(),sort_keys=True,separators=(",",":")).encode())


# Redirect legacy probe helpers to the post-EXP-012 audit character.
v1.BasisAblationCharacter=MBase002Character
v2.BasisAblationCharacter=MBase002Character
v3.BasisAblationCharacter=MBase002Character
v1.CapacityThreeConcernCharacter=HabitTemporalPlasticityCharacter


def agent(enabled):
    return MBase002Character(enabled)


def probe_habit_temporal_plasticity(enabled):
    a=agent(enabled)
    a.step(Event(kind="context",context="morning",forced_action="walk"))
    a.step(Event(kind="outcome",context="morning",reward=1.0,forced_action="idle"))
    initial=a.habits.get(("morning","walk"))
    if initial is None:
        return False
    for i in range(1000):
        a.step(Event(kind="neutral",context=f"u{i%7}",forced_action="idle"))
    final=a.habits.get(("morning","walk"))
    return final is not None and 0.0 < final < initial


def probe_reconstruction(enabled):
    a=agent(enabled)
    a.step(Event(kind="support",actor="morgan",forced_action="idle"))
    a.step(Event(kind="shock",intensity=.5,forced_action="idle"))
    a.step(Event(kind="task_assign",concern="report",intensity=.8,forced_action="idle"))
    a.step(Event(kind="future_commitment",concern="call",context="evening",forced_action="idle"))
    a.step(Event(kind="observe_location",actor="book",context="desk",forced_action="idle"))
    a.step(Event(kind="context",context="morning",forced_action="walk"))
    a.step(Event(kind="outcome",context="morning",reward=1.0,forced_action="idle"))
    for _ in range(7):
        a.step(Event(kind="neutral",forced_action="idle"))
    encoded=a.serialize_persistent()
    b=HabitTemporalPlasticityCharacter.from_persistent_json(encoded)
    aa=a.audit_persistent_snapshot()
    full=b.persistent_snapshot()
    projected={k:full[k] for k in aa}
    if "needs" in aa:
        projected["needs"]={k:full["needs"][k] for k in aa["needs"]}
    return aa==projected


PROBES=dict(v3.PROBES)
PROBES["persistent_reconstruction"]=probe_reconstruction
PROBES["habit_temporal_plasticity"]=probe_habit_temporal_plasticity


def evaluate_subset(enabled):
    enabled=tuple(enabled); outcomes={}; errors={}
    for name,probe in PROBES.items():
        try:
            outcomes[name]=bool(probe(enabled))
        except Exception as exc:
            outcomes[name]=False
            errors[name]=f"{type(exc).__name__}: {exc}"
    sample=agent(enabled)
    return {
        "enabled":list(enabled),"count":len(enabled),"structurally_valid":not errors,
        "capabilities":outcomes,"coverage":sum(outcomes.values()),"total_capabilities":len(outcomes),
        "full_coverage":all(outcomes.values()),"fresh_projected_canonical_bytes":sample.audit_canonical_bytes(),
        "errors":errors
    }


def run():
    rows=[
        evaluate_subset([m for i,m in enumerate(MECHANISMS) if mask&(1<<i)])
        for mask in range(1<<len(MECHANISMS))
    ]
    full=rows[-1]
    frontier={}
    for n in range(len(MECHANISMS)+1):
        group=[r for r in rows if r["count"]==n]
        best=max(r["coverage"] for r in group)
        winners=[r for r in group if r["coverage"]==best]
        frontier[str(n)]={
            "best_coverage":best,"total_capabilities":full["total_capabilities"],
            "best_subsets":[r["enabled"] for r in winners[:20]],"best_subset_count":len(winners)
        }
    full_rows=[r for r in rows if r["full_coverage"]]
    minimum=min((r["count"] for r in full_rows),default=None)
    allset=set(MECHANISMS)
    single={}
    for m in MECHANISMS:
        row=next(r for r in rows if set(r["enabled"])==allset-{m})
        single[m]={"coverage":row["coverage"],"lost":[k for k,v in row["capabilities"].items() if not v]}
    return {
        "audit":"MBASE-002","basis":"v9.5_habit_temporal_plasticity",
        "basis_commit":"79f747707dadfce9092d89ad19a17a9fcd7dd79b",
        "production_blob":"9c6474de1918b62e827d32deff2fa10a4b2443d1",
        "mechanisms":list(MECHANISMS),
        "fixed_capacities":{"concerns":3,"prospective":3,"eligibility":2},
        "subset_count":len(rows),"full_reference":full,
        "minimum_full_coverage_count":minimum,
        "minimal_full_coverage_subsets":[r["enabled"] for r in full_rows if r["count"]==minimum],
        "full_coverage_subset_count":len(full_rows),
        "single_ablation":single,"coverage_frontier":frontier,"rows":rows,
        "pass":len(rows)==2048 and minimum==11 and len(full_rows)==1 and full["full_coverage"]
    }


def main():
    p=argparse.ArgumentParser(); p.add_argument("--json",type=Path); a=p.parse_args(); r=run()
    print(json.dumps({k:v for k,v in r.items() if k!="rows"},indent=2,sort_keys=True))
    if a.json:
        a.json.parent.mkdir(parents=True,exist_ok=True)
        a.json.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    raise SystemExit(0 if r["pass"] else 2)

if __name__=="__main__": main()
