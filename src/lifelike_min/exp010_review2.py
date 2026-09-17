from __future__ import annotations
import argparse, json
from pathlib import Path
from .exp010_challenger import CapacityThreeConcernCharacter
from .runtime import Event

PRODUCTION_FROZEN_AT="03baf6bc6f06d3f298701a8ce66c44e00f509d50"

def assign(a,n,i): a.step(Event(kind="task_assign",concern=n,intensity=i,forced_action="idle"))
def cancel(a,n): a.step(Event(kind="task_cancel",concern=n,forced_action="idle"))

def reordered_equivalence():
    finals=[]
    for order in (("B","C"),("C","B")):
        a=CapacityThreeConcernCharacter(); assign(a,"A",.5)
        for n in order: assign(a,n,1.0 if n=="B" else .9)
        cancel(a,"B"); cancel(a,"C"); finals.append((set(a.concerns),a.active_concern))
    return finals[0]==finals[1]==({"A"},"A")

def cancel_then_reassign():
    a=CapacityThreeConcernCharacter(); assign(a,"A",.5); assign(a,"B",1); assign(a,"C",.9); cancel(a,"A"); assign(a,"A",.6); cancel(a,"B"); cancel(a,"C")
    return set(a.concerns)=={"A"} and a.active_concern=="A"

def overflow_no_resurrection():
    a=CapacityThreeConcernCharacter(); assign(a,"A",.4); assign(a,"B",.8); assign(a,"C",.9); assign(a,"D",1.0); cancel(a,"B"); cancel(a,"C"); cancel(a,"D")
    return "A" not in a.concerns and a.active_concern is None

def hidden_history_irrelevant():
    a=CapacityThreeConcernCharacter(); b=CapacityThreeConcernCharacter()
    a.concerns={"B":.8,"C":.7,"D":.6}; b.concerns=dict(a.concerns); a._sync_active_concern(); b._sync_active_concern()
    return a.serialize_persistent()==b.serialize_persistent() and a.step(Event(kind="neutral"))==b.step(Event(kind="neutral"))

def cue_while_three_full():
    a=CapacityThreeConcernCharacter(); assign(a,"A",.4); assign(a,"B",.8); assign(a,"C",.7)
    a.step(Event(kind="future_commitment",concern="P",context="cue",forced_action="idle")); a.step(Event(kind="neutral",context="cue",forced_action="idle"))
    return len(a.concerns)==3 and "P" in a.concerns and "A" not in a.concerns and "P" not in a.prospective_commitments

def cancel_all_clears_active_and_latent():
    a=CapacityThreeConcernCharacter(); assign(a,"A",.4); assign(a,"B",.8); a.step(Event(kind="future_commitment",concern="P",context="cue",forced_action="idle")); a.step(Event(kind="task_cancel",concern=None,forced_action="idle"))
    return not a.concerns and not a.prospective_commitments and a.active_concern is None

def restore_then_overflow():
    a=CapacityThreeConcernCharacter(); assign(a,"A",.4); assign(a,"B",.8); assign(a,"C",.7); b=CapacityThreeConcernCharacter.from_persistent_json(a.serialize_persistent()); assign(b,"D",1.0)
    return len(b.concerns)==3 and "A" not in b.concerns and set(b.concerns)=={"B","C","D"}

def very_weak_survivor_non_dominant():
    a=CapacityThreeConcernCharacter(); assign(a,"A",.5); assign(a,"B",1); assign(a,"C",.9)
    for _ in range(1000): a.step(Event(kind="neutral",forced_action="idle"))
    return "A" in a.concerns and a.active_concern=="B" and a.concerns["A"] < a.concerns["C"] < a.concerns["B"]

def mechanism_and_fields():
    a=CapacityThreeConcernCharacter(); base=CapacityThreeConcernCharacter.__mro__[1](); return a.mechanism_count()==base.mechanism_count()==11 and set(a.__dict__)==set(base.__dict__)

def fourth_is_explicit_loss_frontier():
    a=CapacityThreeConcernCharacter()
    for n,i in (("A",.4),("B",.6),("C",.8),("D",1.0)): assign(a,n,i)
    encoded=a.serialize_persistent()
    return len(a.concerns)==3 and "A" not in a.concerns and '"A"' not in encoded

def run():
    probes={"reordered_equivalent_outcomes":reordered_equivalence,"cancel_then_reassign":cancel_then_reassign,"overflow_identity_does_not_resurrect":overflow_no_resurrection,"no_privileged_hidden_history":hidden_history_irrelevant,"prospective_cue_competes_through_same_bound":cue_while_three_full,"cancel_all_active_and_latent":cancel_all_clears_active_and_latent,"restore_then_capacity_competition":restore_then_overflow,"very_weak_retained_but_non_dominant":very_weak_survivor_non_dominant,"mechanism_count_and_fields_unchanged":mechanism_and_fields,"fourth_identity_is_explicit_loss_frontier":fourth_is_explicit_loss_frontier}
    rows={}
    for n,f in probes.items():
        try: rows[n]={"passed":bool(f())}
        except Exception as e: rows[n]={"passed":False,"error":f"{type(e).__name__}: {e}"}
    return {"production_frozen_at":PRODUCTION_FROZEN_AT,"passed":all(x["passed"] for x in rows.values()),"passed_count":sum(x["passed"] for x in rows.values()),"total":len(rows),"probes":rows}

def main():
    p=argparse.ArgumentParser(); p.add_argument("--json",type=Path); a=p.parse_args(); r=run(); t=json.dumps(r,indent=2,sort_keys=True); print(t)
    if a.json: a.json.parent.mkdir(parents=True,exist_ok=True); a.json.write_text(t+"\n",encoding="utf-8")
    raise SystemExit(0 if r["passed"] else 1)
if __name__=="__main__": main()
