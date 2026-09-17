from __future__ import annotations
import argparse, json, statistics, time
from pathlib import Path
from .exp009_challenger import UnresolvedConcernPersistenceCharacter
from .exp010_challenger import CapacityThreeConcernCharacter
from .exp010_evaluation import run as development_run, assign
from .exp010_review1 import run as review1_run
from .exp010_review2 import run as review2_run
from .runtime import Event

PRODUCTION_FROZEN_AT="03baf6bc6f06d3f298701a8ce66c44e00f509d50"

def bytes_at(factory,count):
    a=factory()
    for i in range(count): assign(a,f"concern{i:02d}",.6+.05*i)
    return {"canonical":len(a.serialize_persistent().encode()),"diagnostic":a.persistent_state_bytes(),"entries":len(a.concerns)}

def median_us(fn,n=1000):
    rows=[]
    for _ in range(7):
        t=time.perf_counter_ns()
        for _ in range(n): fn()
        rows.append((time.perf_counter_ns()-t)/n/1000)
    return statistics.median(rows)

def cost_audit():
    c2=UnresolvedConcernPersistenceCharacter; c3=CapacityThreeConcernCharacter
    fresh2=bytes_at(c2,0); fresh3=bytes_at(c3,0); two2=bytes_at(c2,2); two3=bytes_at(c3,2); three3=bytes_at(c3,3)
    def idle2(): c2().step(Event(kind="neutral",forced_action="idle"))
    def idle3(): c3().step(Event(kind="neutral",forced_action="idle"))
    def assign2(): a=c2(); assign(a,"concern00",.8); assign(a,"concern01",.9); assign(a,"concern02",1.0)
    def assign3(): a=c3(); assign(a,"concern00",.8); assign(a,"concern01",.9); assign(a,"concern02",1.0)
    def restore2(): a=c2(); assign(a,"concern00",.8); assign(a,"concern01",.9); c2.from_persistent_json(a.serialize_persistent())
    def restore3(): a=c3(); assign(a,"concern00",.8); assign(a,"concern01",.9); assign(a,"concern02",1.0); c3.from_persistent_json(a.serialize_persistent())
    return {"mechanism_count":{"v9_2":c2().mechanism_count(),"challenger":c3().mechanism_count()},"persistent_field_sets_equal":set(c2().__dict__)==set(c3().__dict__),"fresh":{"v9_2":fresh2,"challenger":fresh3},"matched_two_entries":{"v9_2":two2,"challenger":two3},"challenger_three_entries":three3,"marginal_third_entry_canonical_bytes":three3["canonical"]-two3["canonical"],"timing_us_median":{"idle_fresh_v9_2":median_us(idle2,300),"idle_fresh_challenger":median_us(idle3,300),"three_assignment_v9_2":median_us(assign2,300),"three_assignment_challenger":median_us(assign3,300),"restore_v9_2_two":median_us(restore2,200),"restore_challenger_three":median_us(restore3,200)}}

def second_order():
    return {"supports_new_mechanism":False,"supports_capacity_change_within_existing_concern_mechanism":True,"minimum_information":"The target requires three simultaneously distinguishable unresolved identities. Current concern semantics also require an activation scalar for non-arbitrary later competition, so the selected conservative record is the existing identity->activation pair.","suppression_semantics":"No new suppressed status exists. A represented concern is operationally suppressed when it remains unresolved in the ledger but is not the derived strongest active concern.","bounded_loss_frontier":"Capacity three does not solve general forgetting. A fourth sufficiently strong unresolved identity can still evict a weaker represented concern, after which that identity is again unrecoverable from subject-owned state.","why_not_identity_only_overflow":"An identity-only overflow would require a new storage role and an unearned rule for return activation, cancellation/completion routing, overflow and serialization. Capacity three reuses all existing semantics.","human_perceptibility":"The longitudinal difference is observable: after temporary stronger demands terminate, the earlier unfinished demand becomes behaviorally eligible again instead of vanishing from the individual's future.","minimality_interpretation":{"mechanism_minimality":"11 mechanisms remains defensible for this envelope; EXP-010 adds no independent causal faculty.","representational_capacity":"Concern capacity two is falsified for the three-simultaneous-unresolved target; capacity three is the smallest tested successful capacity.","semantic_minimality":"EXP-009 membership/activation semantics are unchanged; EXP-010 changes only how many records that existing semantic can retain."}}

def run():
    dev=development_run(); r1=review1_run(); r2=review2_run(); costs=cost_audit(); critique=second_order()
    passed=bool(dev["developer_gate"] and r1["passed"] and r2["passed"] and costs["mechanism_count"]=={"v9_2":11,"challenger":11} and costs["persistent_field_sets_equal"])
    return {"experiment":"EXP-010","production_frozen_at":PRODUCTION_FROZEN_AT,"decision":"PROMOTE" if passed else "REJECT","passed":passed,"development_gate":dev["developer_gate"],"review1":{"passed":r1["passed"],"passed_count":r1["passed_count"],"total":r1["total"]},"review2":{"passed":r2["passed"],"passed_count":r2["passed_count"],"total":r2["total"]},"cost":costs,"second_order":critique,"claim":{"behavior_demonstrated":"A third unresolved concern can remain represented but non-dominant while two stronger concerns compete, then regain ordinary behavioral eligibility when stronger concerns terminate.","minimum_information_required":"At least the displaced concern identity must survive. Under the existing concern semantics, retaining the existing identity-plus-activation record avoids inventing a separate return-strength rule.","causal_representation_supported":"Capacity 2 fails and capacity 3 succeeds with otherwise identical concern semantics; capacity 4 is unnecessary for the preregistered three-identity target.","not_established":["general goal memory","planning","BDI architecture","unbounded persistence","human working-memory capacity","general forgetting","optimal resource arbitration"]}}

def main():
    p=argparse.ArgumentParser(); p.add_argument("--json",type=Path); a=p.parse_args(); r=run(); t=json.dumps(r,indent=2,sort_keys=True); print(t)
    if a.json: a.json.parent.mkdir(parents=True,exist_ok=True); a.json.write_text(t+"\n",encoding="utf-8")
    raise SystemExit(0 if r["passed"] else 2)
if __name__=="__main__": main()
