from __future__ import annotations

import argparse
import itertools
import json
import statistics
import time
from pathlib import Path

from .exp010_challenger import CapacityThreeConcernCharacter
from .exp011_challenger import CapacityThreeProspectiveCharacter
from .runtime import Event


def commit(agent, name: str, cue: str):
    agent.step(Event(kind="future_commitment", concern=name, context=cue, forced_action="idle"))


def cue(agent, cue_name: str):
    agent.step(Event(kind="neutral", context=cue_name, forced_action="idle"))


def canonical(agent):
    return agent.serialize_persistent()


def diag_bytes(agent):
    return len(json.dumps(agent.snapshot(), sort_keys=True, separators=(",", ":")).encode())


def canon_bytes(agent):
    return len(canonical(agent).encode())


def require(results, name, condition, details=None):
    results[name] = {"pass": bool(condition), "details": details}
    if not condition:
        raise AssertionError(f"{name}: {details}")


def prospective_sequence(cls, order=(("first","cue_first"),("second","cue_second"),("third","cue_third"))):
    a = cls()
    states = []
    for name, cue_name in order:
        commit(a, name, cue_name)
        states.append(a.persistent_snapshot())
    return a, states


def timed(fn, n=1000):
    samples=[]
    for _ in range(5):
        t=time.perf_counter_ns()
        for _ in range(n): fn()
        samples.append((time.perf_counter_ns()-t)/n/1000.0)
    return statistics.median(samples)


def run():
    r={"experiment":"EXP-011","tests":{},"capacity_tournament":{},"cost":{},"limitations":[]}
    t=r["tests"]

    # Exact baseline and matched-history information bound.
    base, baseline_states = prospective_sequence(CapacityThreeConcernCharacter)
    baseline_after_three = base.persistent_snapshot()
    require(t,"baseline_capacity_two", base.max_prospective==2, base.max_prospective)
    require(t,"baseline_eviction", list(base.prospective_commitments.items())==[("second","cue_second"),("third","cue_third")], dict(base.prospective_commitments))
    before_cue=canonical(base); cue(base,"cue_first")
    require(t,"baseline_cue_first_fails", "first" not in base.concerns and "first" not in base.prospective_commitments, base.persistent_snapshot())

    history_a=CapacityThreeConcernCharacter(); commit(history_a,"first","cue_first"); commit(history_a,"second","cue_second"); commit(history_a,"third","cue_third")
    history_b=CapacityThreeConcernCharacter(); history_b.step(Event(kind="neutral",forced_action="idle")); commit(history_b,"second","cue_second"); commit(history_b,"third","cue_third")
    require(t,"information_bound_state_identity", canonical(history_a)==canonical(history_b), {"A":history_a.persistent_snapshot(),"B":history_b.persistent_snapshot()})

    # Capacity tournament using same inherited semantics.
    classes={2:CapacityThreeConcernCharacter,3:CapacityThreeProspectiveCharacter}
    class CapacityFour(CapacityThreeProspectiveCharacter): max_prospective=4
    classes[4]=CapacityFour
    for cap, cls in classes.items():
        a,_=prospective_sequence(cls)
        stored=dict(a.prospective_commitments)
        cue(a,"cue_first")
        success="first" in a.concerns
        r["capacity_tournament"][str(cap)]={"stored_after_three":stored,"cue_first_reactivated":success}
    require(t,"capacity_2_fails", not r["capacity_tournament"]["2"]["cue_first_reactivated"],r["capacity_tournament"]["2"])
    require(t,"capacity_3_succeeds", r["capacity_tournament"]["3"]["cue_first_reactivated"],r["capacity_tournament"]["3"])
    require(t,"capacity_4_no_target_advantage", r["capacity_tournament"]["4"]["cue_first_reactivated"]==r["capacity_tournament"]["3"]["cue_first_reactivated"],r["capacity_tournament"])

    # Commitment/cue insertion permutations and cue arrival permutations.
    identities=["alpha","beta","gamma"]
    cues=["cue_alpha","cue_beta","cue_gamma"]
    permutation_cases=0
    for insertion in itertools.permutations(range(3)):
        a=CapacityThreeProspectiveCharacter()
        for i in insertion: commit(a,identities[i],cues[i])
        require(t,f"retain_perm_{insertion}",set(a.prospective_commitments.items())==set(zip(identities,cues)),dict(a.prospective_commitments))
        for cue_order in ((0,1,2),(2,1,0),(1,0,2)):
            x=CapacityThreeProspectiveCharacter()
            for i in insertion: commit(x,identities[i],cues[i])
            for i in cue_order:
                before=set(x.concerns)
                cue(x,cues[i])
                require(t,f"cue_perm_{insertion}_{cue_order}_{i}",identities[i] in x.concerns and identities[i] not in x.prospective_commitments,{"concerns":dict(x.concerns),"prospective":dict(x.prospective_commitments)})
                permutation_cases+=1
    r["permutation_cases"]=permutation_cases

    # One/two/all cue patterns and wrong/unrelated cues.
    for delivered in ((0,), (2,), (1,), (0,2), (2,1), (0,1,2)):
        a,_=prospective_sequence(CapacityThreeProspectiveCharacter, tuple(zip(identities,cues)))
        cue(a,"wrong_cue")
        require(t,f"wrong_cue_{delivered}",not a.concerns,dict(a.concerns))
        for i in delivered: cue(a,cues[i])
        require(t,f"delivered_{delivered}",all(identities[i] in a.concerns for i in delivered),dict(a.concerns))

    # Fourth-record bounded pressure preserves honest loss frontier.
    a=CapacityThreeProspectiveCharacter()
    for i in range(4): commit(a,f"p{i+1}",f"c{i+1}")
    require(t,"fourth_pressure_existing_replacement",list(a.prospective_commitments.items())==[("p2","c2"),("p3","c3"),("p4","c4")],dict(a.prospective_commitments))
    cue(a,"c1")
    require(t,"lost_fourth_frontier_no_magic_recovery","p1" not in a.concerns,dict(a.concerns))
    r["limitations"].append("capacity 3 remains bounded: a fourth distinct commitment evicts the oldest under the inherited replacement rule")

    # Existing semantics, duplicate/same-name behavior, shared cue behavior.
    a=CapacityThreeProspectiveCharacter(); commit(a,"same","cue_a"); commit(a,"same","cue_b")
    require(t,"same_identity_reassignment_existing_semantics",dict(a.prospective_commitments)=={"same":"cue_b"},dict(a.prospective_commitments))
    a=CapacityThreeProspectiveCharacter(); commit(a,"x","shared"); commit(a,"y","shared"); cue(a,"shared")
    require(t,"distinct_identities_same_cue_existing_semantics",set(a.concerns)=={"x","y"} and not a.prospective_commitments,dict(a.concerns))
    a=CapacityThreeProspectiveCharacter(); commit(a,"x","right"); cue(a,"wrong")
    require(t,"wrong_cue_does_not_activate","x" not in a.concerns and a.prospective_commitments.get("x")=="right",a.persistent_snapshot())

    # Active concern and prospective state remain distinct.
    a=CapacityThreeProspectiveCharacter(); a.step(Event(kind="task_assign",concern="A",intensity=1.0,forced_action="idle")); commit(a,"A","later_A"); commit(a,"B","later_B"); commit(a,"C","later_C")
    require(t,"active_and_latent_same_name_coexist","A" in a.concerns and a.prospective_commitments.get("A")=="later_A",a.persistent_snapshot())
    a.step(Event(kind="task_cancel",concern="B",forced_action="idle"))
    require(t,"cancel_latent_only", "B" not in a.prospective_commitments and "A" in a.concerns,a.persistent_snapshot())
    cue(a,"later_A")
    require(t,"cue_same_name_no_duplicate", "A" in a.concerns and "A" not in a.prospective_commitments,a.persistent_snapshot())

    # Full concern pressure uses ordinary concern competition.
    a=CapacityThreeProspectiveCharacter()
    for name,intensity in (("strong1",1.0),("strong2",.9),("strong3",.8)): a.step(Event(kind="task_assign",concern=name,intensity=intensity,forced_action="idle"))
    commit(a,"weak_future","weak_cue"); cue(a,"weak_cue")
    require(t,"prospective_activation_obeys_concern_capacity",len(a.concerns)<=3,a.persistent_snapshot())

    # Cancellation / activation / work / repeated cue.
    a=CapacityThreeProspectiveCharacter(); commit(a,"cancel_me","c_cancel"); a.step(Event(kind="task_cancel",concern="cancel_me",forced_action="idle")); cue(a,"c_cancel")
    require(t,"cancelled_latent_does_not_resurrect","cancel_me" not in a.concerns,a.persistent_snapshot())
    a=CapacityThreeProspectiveCharacter(); commit(a,"work_me","c_work"); cue(a,"c_work"); pre=dict(a.concerns); a.step(Event(kind="neutral",context="none",available_actions=("work",),forced_action="work")); post=dict(a.concerns); cue(a,"c_work")
    require(t,"activation_then_work_no_prospective_resurrection","work_me" not in a.prospective_commitments and "work_me" not in post,a.persistent_snapshot())

    # Subjective access: only experienced event context triggers.
    a=CapacityThreeProspectiveCharacter(); commit(a,"private","experienced_cue")
    for _ in range(5): a.step(Event(kind="neutral",context="objective_elsewhere",forced_action="idle"))
    require(t,"hidden_or_other_context_cannot_trigger","private" not in a.concerns and a.prospective_commitments.get("private")=="experienced_cue",a.persistent_snapshot())
    cue(a,"experienced_cue")
    require(t,"experienced_cue_triggers","private" in a.concerns,a.persistent_snapshot())

    # Exact reconstruction at full capacity and after transitions.
    a,_=prospective_sequence(CapacityThreeProspectiveCharacter)
    encoded=canonical(a); restored=CapacityThreeProspectiveCharacter.from_persistent_json(encoded)
    require(t,"restore_full_three_exact",canonical(restored)==encoded and restored.max_prospective==3,{"before":a.persistent_snapshot(),"after":restored.persistent_snapshot()})
    for c in ("cue_first","cue_second","cue_third"):
        cue(a,c); cue(restored,c)
        require(t,f"restore_continuation_{c}",canonical(a)==canonical(restored),{"a":a.persistent_snapshot(),"b":restored.persistent_snapshot()})
    a=CapacityThreeProspectiveCharacter(); commit(a,"one","c1"); commit(a,"two","c2"); cue(a,"c1"); encoded=canonical(a); restored=CapacityThreeProspectiveCharacter.from_persistent_json(encoded)
    require(t,"restore_after_activation_exact",canonical(restored)==encoded,restored.persistent_snapshot())
    a.step(Event(kind="task_cancel",concern="two",forced_action="idle")); encoded=canonical(a); restored=CapacityThreeProspectiveCharacter.from_persistent_json(encoded)
    require(t,"restore_after_removal_exact",canonical(restored)==encoded,restored.persistent_snapshot())

    # Causal ablation: same challenger class except capacity restored to 2.
    class Ablated(CapacityThreeProspectiveCharacter): max_prospective=2
    a,_=prospective_sequence(Ablated); cue(a,"cue_first")
    require(t,"capacity_ablation_restores_failure","first" not in a.concerns and list(a.prospective_commitments.items())==[("second","cue_second"),("third","cue_third")],a.persistent_snapshot())

    # Current ancient-commitment failure intentionally remains outside scope.
    a=CapacityThreeProspectiveCharacter(); commit(a,"ancient","ancient_cue")
    for i in range(1000): a.step(Event(kind="neutral",context=f"unrelated_{i%7}",forced_action="idle"))
    cue(a,"ancient_cue")
    require(t,"ancient_commitment_failure_preserved","ancient" in a.concerns,a.persistent_snapshot())

    # Mechanism/schema invariants and representational costs.
    fresh=CapacityThreeProspectiveCharacter(); basefresh=CapacityThreeConcernCharacter()
    require(t,"mechanism_count_unchanged",fresh.mechanism_count()==basefresh.mechanism_count()==11,{"candidate":fresh.mechanism_count(),"baseline":basefresh.mechanism_count()})
    sizes={}
    for n in range(4):
        a=CapacityThreeProspectiveCharacter()
        for i in range(n): commit(a,f"k{i}",f"q{i}")
        sizes[str(n)]={"canonical":canon_bytes(a),"diagnostic":diag_bytes(a)}
    r["cost"]["state_bytes_by_prospective_entries"]=sizes
    r["cost"]["third_record_marginal_canonical_bytes"]=sizes["3"]["canonical"]-sizes["2"]["canonical"]
    r["cost"]["fresh_canonical_bytes"]=canon_bytes(fresh)
    r["cost"]["fresh_diagnostic_bytes"]=diag_bytes(fresh)
    full=CapacityThreeProspectiveCharacter(); [commit(full,f"k{i}",f"q{i}") for i in range(3)]
    encoded=canonical(full)
    r["cost"]["serialize_full_three_us"]=timed(lambda: full.serialize_persistent(),500)
    r["cost"]["restore_full_three_us"]=timed(lambda: CapacityThreeProspectiveCharacter.from_persistent_json(encoded),500)
    r["cost"]["insert_us"]=timed(lambda: commit(CapacityThreeProspectiveCharacter(),"x","cx"),500)
    def activate_once():
        x=CapacityThreeProspectiveCharacter(); commit(x,"x","cx"); cue(x,"cx")
    r["cost"]["cue_activation_us"]=timed(activate_once,500)

    r["decision_pre_review"]="PASS_DEVELOPMENT"
    return r


def main():
    p=argparse.ArgumentParser(); p.add_argument("--json",type=Path); args=p.parse_args()
    result=run(); print(json.dumps(result,indent=2,sort_keys=True))
    if args.json:
        args.json.parent.mkdir(parents=True,exist_ok=True)
        args.json.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")


if __name__=="__main__": main()
