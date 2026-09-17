from __future__ import annotations
import argparse,json
from pathlib import Path
from .exp010_challenger import CapacityThreeConcernCharacter
from .runtime import Event

def commit(a,name,cue): a.step(Event(kind="future_commitment",concern=name,context=cue,forced_action="idle"))
def run():
    a=CapacityThreeConcernCharacter(); commit(a,"first","cue_first"); commit(a,"second","cue_second"); commit(a,"third","cue_third")
    after_three=a.persistent_snapshot(); encoded_a=a.serialize_persistent(); a.step(Event(kind="neutral",context="cue_first",forced_action="idle")); after_cue=a.persistent_snapshot()
    b=CapacityThreeConcernCharacter(); b.step(Event(kind="neutral",forced_action="idle")); commit(b,"second","cue_second"); commit(b,"third","cue_third"); encoded_b=b.serialize_persistent()
    permutations=[]
    for order in (("a","b","c"),("c","b","a"),("b","a","c")):
        x=CapacityThreeConcernCharacter()
        for n in order: commit(x,n,"cue_"+n)
        permutations.append({"order":list(order),"stored":dict(x.prospective_commitments)})
    return {"target":"third_commitment_is_forgotten","reproduced":"first" not in after_three["prospective_commitments"] and "first" not in after_cue["concern_ledger"],"capacity":a.max_prospective,"history_A_after_eviction":after_three["prospective_commitments"],"history_B_never_first":b.persistent_snapshot()["prospective_commitments"],"canonical_state_identical_after_eviction":encoded_a==encoded_b,"information_lower_bound":"If true, current subject-owned state contains no bit distinguishing an evicted prospective identity from a matched history in which it never existed.","permutations":permutations,"cue_first_after_eviction_concerns":after_cue["concern_ledger"]}
def main():
 p=argparse.ArgumentParser(); p.add_argument("--json",type=Path); a=p.parse_args(); r=run(); print(json.dumps(r,indent=2,sort_keys=True));
 if a.json: a.json.parent.mkdir(parents=True,exist_ok=True); a.json.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
if __name__=="__main__": main()
