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


def cancel(a, name):
    a.step(Event(kind="task_cancel", concern=name, forced_action="idle"))


def record(rows, name, ok, details=None):
    rows.append({"name": name, "pass": bool(ok), "details": details})


def run():
    rows=[]

    # Equivalent retained prospective set despite unrelated-event interleaving.
    a=CapacityThreeProspectiveCharacter(); b=CapacityThreeProspectiveCharacter()
    for name,cue in (("one","c1"),("two","c2"),("three","c3")):
        commit(a,name,cue)
    commit(b,"one","c1"); b.step(Event(kind="neutral",context="noise",forced_action="idle")); commit(b,"two","c2"); b.step(Event(kind="neutral",context="other",forced_action="idle")); commit(b,"three","c3")
    record(rows,"interleaved_history_same_prospective_content",dict(a.prospective_commitments)==dict(b.prospective_commitments)=={"one":"c1","two":"c2","three":"c3"},{"a":a.persistent_snapshot(),"b":b.persistent_snapshot()})
    for cue,name in (("c3","three"),("c1","one"),("c2","two")):
        deliver(a,cue); deliver(b,cue)
        record(rows,f"interleaved_equivalent_cue_{name}",name in a.concerns and name in b.concerns and name not in a.prospective_commitments and name not in b.prospective_commitments,{"a":a.persistent_snapshot(),"b":b.persistent_snapshot()})

    # Same prospective content reconstructed at different boundaries behaves equivalently.
    a=CapacityThreeProspectiveCharacter(); commit(a,"red","r"); commit(a,"green","g")
    mid=CapacityThreeProspectiveCharacter.from_persistent_json(a.serialize_persistent())
    commit(a,"blue","b"); commit(mid,"blue","b")
    final=CapacityThreeProspectiveCharacter.from_persistent_json(mid.serialize_persistent())
    record(rows,"boundary_reconstruction_full_content",dict(a.prospective_commitments)==dict(mid.prospective_commitments)==dict(final.prospective_commitments),{"a":a.persistent_snapshot(),"mid":mid.persistent_snapshot(),"final":final.persistent_snapshot()})
    for cue,name in (("g","green"),("b","blue"),("r","red")):
        for x in (a,mid,final): deliver(x,cue)
        record(rows,f"boundary_reconstruction_{name}",all(name in x.concerns and name not in x.prospective_commitments for x in (a,mid,final)),[x.persistent_snapshot() for x in (a,mid,final)])

    # Resolve active concerns between cue deliveries so prospective results cannot be confounded by concern capacity.
    a=CapacityThreeProspectiveCharacter()
    for n,c in (("p","cp"),("q","cq"),("r","cr")): commit(a,n,c)
    for n,c in (("q","cq"),("p","cp"),("r","cr")):
        deliver(a,c)
        record(rows,f"serial_activation_{n}",n in a.concerns and n not in a.prospective_commitments,a.persistent_snapshot())
        cancel(a,n)
        record(rows,f"serial_resolution_{n}",n not in a.concerns,a.persistent_snapshot())
    record(rows,"serial_all_bindings_consumed",not a.prospective_commitments,a.persistent_snapshot())

    # Capacity boundary transition: 3 -> activate one -> add two, with only oldest extant prospective record lost at overflow.
    a=CapacityThreeProspectiveCharacter()
    for n in ("a","b","c"): commit(a,n,"cue_"+n)
    deliver(a,"cue_b")
    commit(a,"d","cue_d")
    commit(a,"e","cue_e")
    # After b was consumed, a/c remain; d fills third; e evicts oldest extant a.
    record(rows,"boundary_transition_store",dict(a.prospective_commitments)=={"c":"cue_c","d":"cue_d","e":"cue_e"},a.persistent_snapshot())
    deliver(a,"cue_a")
    record(rows,"boundary_transition_lost_a_no_recovery","a" not in a.concerns,a.persistent_snapshot())
    for n in ("c","d","e"):
        deliver(a,"cue_"+n)
        record(rows,f"boundary_transition_retained_{n}",n in a.concerns,a.persistent_snapshot())

    # Reassignment after activation creates a new prospective binding only when explicitly recommitted.
    a=CapacityThreeProspectiveCharacter(); commit(a,"repeat","first_cue"); deliver(a,"first_cue")
    record(rows,"activation_consumes_original", "repeat" in a.concerns and "repeat" not in a.prospective_commitments,a.persistent_snapshot())
    commit(a,"repeat","second_cue")
    record(rows,"explicit_recommit_creates_new_binding",a.prospective_commitments.get("repeat")=="second_cue",a.persistent_snapshot())
    cancel(a,"repeat")
    deliver(a,"second_cue")
    record(rows,"cancel_after_recommit_prevents_reactivation","repeat" not in a.concerns and "repeat" not in a.prospective_commitments,a.persistent_snapshot())

    # Shared cue plus independent third identity.
    a=CapacityThreeProspectiveCharacter(); commit(a,"x","shared"); commit(a,"y","shared"); commit(a,"z","solo")
    deliver(a,"shared")
    record(rows,"shared_two_activate_independent_remains",set(a.concerns)=={"x","y"} and dict(a.prospective_commitments)=={"z":"solo"},a.persistent_snapshot())
    deliver(a,"solo")
    record(rows,"independent_third_later_activates",set(a.concerns)=={"x","y","z"} and not a.prospective_commitments,a.persistent_snapshot())

    # Objective-state-equivalent histories that differ only by experienced cue must diverge according to subjective history.
    experienced=CapacityThreeProspectiveCharacter(); unexperienced=CapacityThreeProspectiveCharacter()
    for x in (experienced,unexperienced): commit(x,"remember","door_chime")
    deliver(experienced,"door_chime")
    unexperienced.step(Event(kind="neutral",context="same_room_objective_state",forced_action="idle"))
    record(rows,"experienced_history_controls_reactivation","remember" in experienced.concerns and "remember" not in unexperienced.concerns and unexperienced.prospective_commitments.get("remember")=="door_chime",{"experienced":experienced.persistent_snapshot(),"unexperienced":unexperienced.persistent_snapshot()})

    # Long latency plus reconstruction does not corrupt current semantics. This deliberately confirms, rather than solves, the separate aging failure.
    a=CapacityThreeProspectiveCharacter()
    for n in ("old1","old2","old3"): commit(a,n,"cue_"+n)
    for i in range(500): a.step(Event(kind="neutral",context=f"noise_{i%11}",forced_action="idle"))
    b=CapacityThreeProspectiveCharacter.from_persistent_json(a.serialize_persistent())
    record(rows,"long_latency_reconstruction_retains_three",dict(b.prospective_commitments)=={"old1":"cue_old1","old2":"cue_old2","old3":"cue_old3"},b.persistent_snapshot())
    deliver(b,"cue_old2")
    record(rows,"long_latency_exact_cue_activates","old2" in b.concerns and "old2" not in b.prospective_commitments,b.persistent_snapshot())

    # Fourth-pressure information loss is irreversible and not reconstructed from active concerns or logs.
    a=CapacityThreeProspectiveCharacter()
    for n in ("l1","l2","l3","l4"): commit(a,n,"cue_"+n)
    encoded=a.serialize_persistent(); b=CapacityThreeProspectiveCharacter.from_persistent_json(encoded)
    record(rows,"overflow_roundtrip_preserves_only_survivors",dict(b.prospective_commitments)=={"l2":"cue_l2","l3":"cue_l3","l4":"cue_l4"},b.persistent_snapshot())
    deliver(b,"cue_l1")
    record(rows,"overflow_lost_identity_stays_lost","l1" not in b.concerns,b.persistent_snapshot())

    # Three distinct identities and cues remain distinguishable after arbitrary cue order and cancellation of one latent item.
    a=CapacityThreeProspectiveCharacter(); commit(a,"north","n"); commit(a,"south","s"); commit(a,"west","w")
    cancel(a,"south")
    deliver(a,"w"); deliver(a,"s"); deliver(a,"n")
    record(rows,"latent_cancel_is_identity_specific",set(a.concerns)=={"north","west"} and "south" not in a.concerns and not a.prospective_commitments,a.persistent_snapshot())

    passed=sum(x["pass"] for x in rows)
    return {"experiment":"EXP-011","reviewer":"pass2","production_blob_sha":PRODUCTION_BLOB_SHA,"passed":passed==len(rows),"passed_count":passed,"total":len(rows),"failures":[x for x in rows if not x["pass"]],"results":rows}


def main():
    p=argparse.ArgumentParser(); p.add_argument("--json",type=Path); args=p.parse_args()
    r=run(); text=json.dumps(r,indent=2,sort_keys=True); print(text)
    if args.json:
        args.json.parent.mkdir(parents=True,exist_ok=True); args.json.write_text(text+"\n",encoding="utf-8")
    raise SystemExit(0 if r["passed"] else 2)


if __name__=="__main__": main()
