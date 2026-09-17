from __future__ import annotations

import argparse
import json
from pathlib import Path

from .exp011_challenger import CapacityThreeProspectiveCharacter
from .runtime import Event

PRODUCTION_BLOB_SHA = "4238680bb78c21dd71b55cf279b2e4e2ce0e03a8"


def commit(a, name, cue):
    a.step(Event(kind="future_commitment", concern=name, context=cue, forced_action="idle"))


def deliver(a, cue):
    a.step(Event(kind="neutral", context=cue, forced_action="idle"))


def check(rows, name, condition, details=None):
    rows.append({"name":name,"pass":bool(condition),"details":details})


def run():
    rows=[]

    # Reverse insertion and non-corresponding cue order.
    a=CapacityThreeProspectiveCharacter()
    for name,cue in (("gamma","c3"),("alpha","c1"),("beta","c2")): commit(a,name,cue)
    for cue,name in (("c2","beta"),("c3","gamma"),("c1","alpha")):
        deliver(a,cue); check(rows,f"reordered_{name}",name in a.concerns and name not in a.prospective_commitments,a.persistent_snapshot())

    # Wrong and prefix/suffix-near cues must not trigger.
    a=CapacityThreeProspectiveCharacter(); commit(a,"exact","cue_exact")
    for wrong in ("cue_exac","cue_exact_extra","CUE_EXACT","", " cue_exact"):
        deliver(a,wrong); check(rows,f"wrong_exact_{repr(wrong)}","exact" not in a.concerns and a.prospective_commitments.get("exact")=="cue_exact",a.persistent_snapshot())
    deliver(a,"cue_exact"); check(rows,"exact_eventually_triggers","exact" in a.concerns,a.persistent_snapshot())

    # Fill, activate middle, refill, then ensure retained association remains correct.
    a=CapacityThreeProspectiveCharacter()
    for n,c in (("a","ca"),("b","cb"),("c","cc")): commit(a,n,c)
    deliver(a,"cb"); commit(a,"d","cd")
    check(rows,"fill_activate_refill",dict(a.prospective_commitments)=={"a":"ca","c":"cc","d":"cd"},a.persistent_snapshot())
    deliver(a,"ca"); deliver(a,"cc"); deliver(a,"cd")
    check(rows,"fill_activate_refill_cues",set(("a","b","c","d"))<=set(a.concerns),a.persistent_snapshot())

    # Four-record pressure from varied insertion order. Oldest surviving identity is the inherited rule.
    for order in (("w","x","y","z"),("z","w","y","x"),("x","z","w","y")):
        a=CapacityThreeProspectiveCharacter()
        for name in order: commit(a,name,"cue_"+name)
        lost=order[0]
        check(rows,f"pressure_store_{order}",lost not in a.prospective_commitments and set(a.prospective_commitments)==set(order[1:]),dict(a.prospective_commitments))
        deliver(a,"cue_"+lost)
        check(rows,f"pressure_no_recovery_{order}",lost not in a.concerns,a.persistent_snapshot())

    # Same identity reassignment cannot preserve an obsolete cue as a hidden second record.
    a=CapacityThreeProspectiveCharacter(); commit(a,"same","old"); commit(a,"same","new")
    deliver(a,"old"); check(rows,"same_name_old_cue_dead","same" not in a.concerns and a.prospective_commitments.get("same")=="new",a.persistent_snapshot())
    deliver(a,"new"); check(rows,"same_name_new_cue_live","same" in a.concerns and "same" not in a.prospective_commitments,a.persistent_snapshot())

    # Duplicate cue semantics stay inherited: all identities with exact same cue activate.
    a=CapacityThreeProspectiveCharacter()
    for n in ("one","two","three"): commit(a,n,"shared")
    deliver(a,"shared")
    check(rows,"shared_cue_all_three",set(a.concerns)=={"one","two","three"} and not a.prospective_commitments,a.persistent_snapshot())
    deliver(a,"shared")
    check(rows,"repeated_shared_cue_no_duplicate",set(a.concerns)=={"one","two","three"} and not a.prospective_commitments,a.persistent_snapshot())

    # Reconstruction while full, then pressure, then cues.
    a=CapacityThreeProspectiveCharacter()
    for n in ("r1","r2","r3"): commit(a,n,"cue_"+n)
    encoded=a.serialize_persistent(); b=CapacityThreeProspectiveCharacter.from_persistent_json(encoded)
    check(rows,"reconstruct_full_exact",b.serialize_persistent()==encoded and dict(b.prospective_commitments)==dict(a.prospective_commitments),b.persistent_snapshot())
    commit(a,"r4","cue_r4"); commit(b,"r4","cue_r4")
    check(rows,"reconstruct_pressure_exact",a.serialize_persistent()==b.serialize_persistent(),{"a":a.persistent_snapshot(),"b":b.persistent_snapshot()})
    for c in ("cue_r1","cue_r2","cue_r3","cue_r4"):
        deliver(a,c); deliver(b,c)
        check(rows,f"reconstruct_continue_{c}",a.serialize_persistent()==b.serialize_persistent(),{"a":a.persistent_snapshot(),"b":b.persistent_snapshot()})

    # Active concerns do not consume prospective slots.
    a=CapacityThreeProspectiveCharacter()
    for n,intensity in (("active1",1.0),("active2",.9),("active3",.8)):
        a.step(Event(kind="task_assign",concern=n,intensity=intensity,forced_action="idle"))
    for n in ("future1","future2","future3"): commit(a,n,"cue_"+n)
    check(rows,"concern_prospective_capacity_independent",len(a.concerns)==3 and len(a.prospective_commitments)==3,a.persistent_snapshot())
    deliver(a,"cue_future1")
    check(rows,"activation_respects_concern_bound",len(a.concerns)==3 and "future1" in a.concerns,a.persistent_snapshot())

    # Explicit cancellation of one prospective identity leaves other two intact.
    a=CapacityThreeProspectiveCharacter()
    for n in ("keep1","cancel","keep2"): commit(a,n,"cue_"+n)
    a.step(Event(kind="task_cancel",concern="cancel",forced_action="idle"))
    check(rows,"targeted_cancel_isolated",dict(a.prospective_commitments)=={"keep1":"cue_keep1","keep2":"cue_keep2"},a.persistent_snapshot())
    deliver(a,"cue_cancel")
    check(rows,"cancel_cue_no_revival","cancel" not in a.concerns,a.persistent_snapshot())

    # Long latency does not alter existing prospective semantics, and unrelated events do not fake cue experience.
    for horizon in (10,100,1000):
        a=CapacityThreeProspectiveCharacter(); commit(a,"late","real_cue")
        for i in range(horizon): a.step(Event(kind="neutral",context=f"other_{i%5}",forced_action="idle"))
        check(rows,f"latency_{horizon}_still_latent",a.prospective_commitments.get("late")=="real_cue" and "late" not in a.concerns,a.persistent_snapshot())
        deliver(a,"real_cue")
        check(rows,f"latency_{horizon}_reactivates","late" in a.concerns and "late" not in a.prospective_commitments,a.persistent_snapshot())

    # Unicode and delimiter-heavy values remain exact through serialization; no parsing schema was introduced.
    a=CapacityThreeProspectiveCharacter()
    cases=(("a|b","cue:semicolon;|"),("雪","未来/雪"),("quote\"name","cue\nline"))
    for n,c in cases: commit(a,n,c)
    encoded=a.serialize_persistent(); b=CapacityThreeProspectiveCharacter.from_persistent_json(encoded)
    check(rows,"opaque_identity_cue_roundtrip",b.serialize_persistent()==encoded and dict(b.prospective_commitments)==dict(a.prospective_commitments),b.persistent_snapshot())
    for n,c in cases:
        deliver(b,c); check(rows,f"opaque_cue_{repr(n)}",n in b.concerns,b.persistent_snapshot())

    # Subjective access: an unexperienced objective-label event cannot trigger an unrelated retained cue.
    a=CapacityThreeProspectiveCharacter(); commit(a,"subjective","heard_bell")
    a.step(Event(kind="neutral",context="world_bell_occurred_elsewhere",forced_action="idle"))
    check(rows,"subjective_access_no_hidden_world_trigger","subjective" not in a.concerns and a.prospective_commitments.get("subjective")=="heard_bell",a.persistent_snapshot())
    deliver(a,"heard_bell")
    check(rows,"subjective_access_experienced_trigger","subjective" in a.concerns,a.persistent_snapshot())

    passed=sum(1 for x in rows if x["pass"])
    return {"experiment":"EXP-011","reviewer":"pass1","production_blob_sha":PRODUCTION_BLOB_SHA,"passed":passed==len(rows),"passed_count":passed,"total":len(rows),"failures":[x for x in rows if not x["pass"]],"results":rows}


def main():
    p=argparse.ArgumentParser(); p.add_argument("--json",type=Path); args=p.parse_args()
    r=run(); text=json.dumps(r,indent=2,sort_keys=True); print(text)
    if args.json:
        args.json.parent.mkdir(parents=True,exist_ok=True); args.json.write_text(text+"\n",encoding="utf-8")
    raise SystemExit(0 if r["passed"] else 2)


if __name__=="__main__": main()
