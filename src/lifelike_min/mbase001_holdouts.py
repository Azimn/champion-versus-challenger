from __future__ import annotations

import argparse, json
from pathlib import Path

from .mbase001_audit import BasisAblationCharacter, MECHANISMS
from .runtime import Event

NEAR_MINIMAL = {
    "minus_affect": tuple(m for m in MECHANISMS if m != "affect_residue"),
    "minus_partner_reliability": tuple(m for m in MECHANISMS if m != "partner_reliability"),
    "minus_prospective": tuple(m for m in MECHANISMS if m != "prospective_commitments"),
    "minus_relationship": tuple(m for m in MECHANISMS if m != "relationship_history"),
    "minus_competence": tuple(m for m in MECHANISMS if m != "competence"),
    "minus_fatigue": tuple(m for m in MECHANISMS if m != "fatigue"),
}


def make(enabled): return BasisAblationCharacter(enabled)


def relationship_affect(enabled):
    a=make(enabled)
    a.step(Event(kind="hostility", actor="morgan", intensity=1.0, forced_action="idle"))
    early=a.step(Event(kind="neutral", actor="morgan", available_actions=("idle","avoid:morgan")))
    early_sarah=a.step(Event(kind="neutral", actor="sarah", available_actions=("idle","avoid:sarah")))
    residue_early=a.threat_residue
    for _ in range(35): a.step(Event(kind="neutral", forced_action="idle"))
    residue_late=a.threat_residue
    m_rel=a.relationships.get("morgan",0.0); s_rel=a.relationships.get("sarah",0.0)
    return early=="avoid:morgan" and early_sarah=="idle" and residue_early>residue_late and m_rel<s_rel


def relationship_reliability(enabled):
    a=make(enabled)
    for _ in range(3):
        a.step(Event(kind="support", actor="morgan", forced_action="idle"))
        a.step(Event(kind="observed_unreliable", actor="morgan", forced_action="idle"))
        a.step(Event(kind="hostility", actor="sarah", forced_action="idle"))
        a.step(Event(kind="observed_reliable", actor="sarah", forced_action="idle"))
    m_social=a.step(Event(kind="neutral", actor="morgan", available_actions=("socialize:morgan","avoid:morgan")))
    s_social=a.step(Event(kind="neutral", actor="sarah", available_actions=("socialize:sarah","avoid:sarah")))
    m_task=a.step(Event(kind="neutral", available_actions=("delegate:morgan","verify:morgan")))
    s_task=a.step(Event(kind="neutral", available_actions=("verify:sarah","delegate:sarah")))
    return m_social=="socialize:morgan" and s_social=="avoid:sarah" and m_task=="verify:morgan" and s_task=="delegate:sarah"


def concern_prospective(enabled):
    a=make(enabled)
    a.step(Event(kind="task_assign", concern="report", intensity=1.0, forced_action="idle"))
    a.step(Event(kind="task_assign", concern="grading", intensity=.9, forced_action="idle"))
    a.step(Event(kind="future_commitment", concern="call", context="evening", forced_action="idle"))
    latent="call" in a.prospective_commitments and "call" not in a.concerns and len(a.concerns)==2
    a.step(Event(kind="neutral", context="evening", forced_action="idle"))
    activated="call" in a.concerns and len(a.concerns)==3
    a.step(Event(kind="task_cancel", concern="report", forced_action="idle"))
    return latent and activated and "call" in a.concerns and len(a.concerns)==2


def concern_pressure(enabled):
    a=make(enabled)
    a.step(Event(kind="task_assign", concern="portfolio", intensity=.4, forced_action="idle"))
    for _ in range(25): a.step(Event(kind="neutral", forced_action="idle"))
    exists="portfolio" in a.concerns
    first=a.step(Event(kind="neutral", available_actions=("rest","work","idle")))
    for _ in range(4): a.step(Event(kind="neutral", forced_action="rest"))
    second=a.step(Event(kind="neutral", available_actions=("work","idle")))
    return exists and first=="rest" and second=="work"


def fact_habit_separation(enabled):
    a=make(enabled)
    a.step(Event(kind="context", context="morning", forced_action="walk"))
    a.step(Event(kind="outcome", reward=1.0, forced_action="idle"))
    before=a.habits.get(("morning","walk"),0.0)
    a.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    first=a.step(Event(kind="retrieve", actor="book", available_actions=("search:shelf","search:drawer")))
    a.step(Event(kind="observe_location", actor="book", context="shelf", forced_action="idle"))
    second=a.step(Event(kind="retrieve", actor="book", available_actions=("search:drawer","search:shelf")))
    return before>0 and a.habits.get(("morning","walk"),0.0)==before and first=="search:drawer" and second=="search:shelf"


def habit_eligibility(enabled):
    a=make(enabled)
    a.step(Event(kind="context", context="garden", forced_action="inspect"))
    a.step(Event(kind="context", context="kitchen", forced_action="wait"))
    a.step(Event(kind="outcome", context="garden", reward=1.0, forced_action="idle"))
    return a.habits.get(("garden","inspect"),0)>0 and a.habits.get(("kitchen","wait"),0)==0


def prospective_capacity(enabled):
    a=make(enabled)
    for name,intensity in (("a",1.0),("b",.9),("c",.8)):
        a.step(Event(kind="task_assign", concern=name, intensity=intensity, forced_action="idle"))
    a.step(Event(kind="future_commitment", concern="d", context="cue", forced_action="idle"))
    before=set(a.concerns)
    a.step(Event(kind="neutral", context="cue", forced_action="idle"))
    after=set(a.concerns)
    return before=={"a","b","c"} and len(after)==3 and "d" not in after and "d" not in a.prospective_commitments


def multiprocess_reconstruction(enabled):
    a=make(enabled)
    a.step(Event(kind="support", actor="morgan", forced_action="idle"))
    a.step(Event(kind="observed_reliable", actor="morgan", forced_action="idle"))
    a.step(Event(kind="shock", intensity=.7, forced_action="idle"))
    a.step(Event(kind="context", context="morning", forced_action="walk"))
    a.step(Event(kind="outcome", reward=1.0, forced_action="idle"))
    for name,intensity in (("a",1.0),("b",.9),("c",.8)):
        a.step(Event(kind="task_assign", concern=name, intensity=intensity, forced_action="idle"))
    a.step(Event(kind="future_commitment", concern="call", context="evening", forced_action="idle"))
    a.step(Event(kind="observe_location", actor="book", context="desk", forced_action="idle"))
    encoded=a.serialize_persistent()
    # Reconstruction is evaluated on full champion only; subset candidates are not
    # redesigned with custom serializers. The historical manifest already projects
    # enabled-state reconstruction for subset search.
    from .exp010_challenger import CapacityThreeConcernCharacter
    b=CapacityThreeConcernCharacter.from_persistent_json(encoded)
    seq=[Event(kind="neutral",forced_action="idle"),Event(kind="neutral",context="evening",forced_action="idle"),Event(kind="task_cancel",concern="a",forced_action="idle")]
    same=True
    for e in seq:
        same &= a.step(e)==b.step(e)
    return same and a.persistent_snapshot()==b.persistent_snapshot()

HOLDOUTS={
 "relationship_affect":relationship_affect,
 "relationship_reliability":relationship_reliability,
 "concern_prospective":concern_prospective,
 "concern_pressure":concern_pressure,
 "fact_habit_separation":fact_habit_separation,
 "habit_eligibility":habit_eligibility,
 "prospective_capacity":prospective_capacity,
 "multiprocess_reconstruction":multiprocess_reconstruction,
}

def evaluate(label, enabled):
    out={}
    for name,fn in HOLDOUTS.items():
        if name=="multiprocess_reconstruction" and set(enabled)!=set(MECHANISMS):
            out[name]=None
            continue
        try: out[name]=bool(fn(enabled))
        except Exception as exc: out[name]=f"ERROR:{type(exc).__name__}:{exc}"
    return {"label":label,"enabled":list(enabled),"holdouts":out,"passed":sum(v is True for v in out.values()),"applicable":sum(v is not None for v in out.values())}

def run():
    rows=[evaluate("full_v9.3",MECHANISMS)]
    rows += [evaluate(label,enabled) for label,enabled in NEAR_MINIMAL.items()]
    return {"audit":"MBASE-001","sealed_definition":"research/audits/MBASE001_SEALED_HOLDOUTS.md","rows":rows,"full_pass":all(v is True for v in rows[0]["holdouts"].values())}

def main():
    p=argparse.ArgumentParser(); p.add_argument("--json",type=Path); args=p.parse_args(); r=run(); print(json.dumps(r,indent=2,sort_keys=True));
    if args.json: args.json.parent.mkdir(parents=True,exist_ok=True); args.json.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    if not r["full_pass"]: raise SystemExit(1)
if __name__=="__main__": main()
