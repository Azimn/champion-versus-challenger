from __future__ import annotations
import argparse,json
from pathlib import Path
from .exp010_challenger import CapacityThreeConcernCharacter as C
from .runtime import Event

def habit(a,c,x): return float(a.habits.get((c,x),0.0))
def rewarded_routine_never_weakens():
 a=C(); a.step(Event(kind="context",context="morning",forced_action="walk")); a.step(Event(kind="outcome",reward=1.0,forced_action="idle")); learned=habit(a,"morning","walk")
 for _ in range(1000): a.step(Event(kind="neutral",forced_action="idle"))
 after=habit(a,"morning","walk"); choice=a.step(Event(kind="context",context="morning",available_actions=("tea","walk")))
 return {"reproduced":learned>0 and after==learned and choice=="walk","learned":learned,"after_1000":after,"choice":choice}
def ancient_commitment_reactivates_unchanged():
 a=C(); a.step(Event(kind="future_commitment",concern="call_morgan",context="morgan_arrives",forced_action="idle"))
 for _ in range(1000): a.step(Event(kind="neutral",forced_action="idle"))
 before=a.snapshot(); a.step(Event(kind="neutral",context="morgan_arrives",forced_action="idle")); after=a.snapshot()
 return {"reproduced":before["prospective_commitments"].get("call_morgan")=="morgan_arrives" and "call_morgan" in after["concern_ledger"],"before":before["prospective_commitments"],"after":after["concern_ledger"]}
def third_commitment_is_forgotten():
 a=C()
 for n,c in (("first","cue_first"),("second","cue_second"),("third","cue_third")): a.step(Event(kind="future_commitment",concern=n,context=c,forced_action="idle"))
 stored=dict(a.snapshot()["prospective_commitments"]); a.step(Event(kind="neutral",context="cue_first",forced_action="idle")); active=dict(a.snapshot()["concern_ledger"])
 return {"reproduced":"first" not in stored and "first" not in active,"stored":stored,"after_first_cue":active}
def suppressed_concern_never_returns():
 a=C(); a.step(Event(kind="task_assign",concern="low_priority",intensity=.5,forced_action="idle")); a.step(Event(kind="task_assign",concern="urgent_one",intensity=1,forced_action="idle")); a.step(Event(kind="task_assign",concern="urgent_two",intensity=.9,forced_action="idle")); after_three=dict(a.snapshot()["concern_ledger"]); a.step(Event(kind="task_cancel",concern="urgent_one",forced_action="idle")); a.step(Event(kind="task_cancel",concern="urgent_two",forced_action="idle")); final=dict(a.snapshot()["concern_ledger"])
 return {"reproduced":"low_priority" not in after_three and "low_priority" not in final,"after_three":after_three,"final":final,"target_corrected":"low_priority" in after_three and "low_priority" in final}
def deterministic_rhythm():
 a=C(); actions=[a.step(Event(kind="neutral",available_actions=("rest","work","idle"))) for _ in range(120)]; tail=actions[-60:]; periods=[p for p in range(1,21) if all(tail[i]==tail[i%p] for i in range(len(tail)))]
 return {"reproduced":bool(periods),"periods":periods,"last_60":tail}
def run():
 rows={"rewarded_routine_never_weakens":rewarded_routine_never_weakens(),"ancient_commitment_reactivates_unchanged":ancient_commitment_reactivates_unchanged(),"third_commitment_is_forgotten":third_commitment_is_forgotten(),"suppressed_concern_never_returns":suppressed_concern_never_returns(),"deterministic_rhythm":deterministic_rhythm()}
 return {"frozen_champion":"v9.3_concern_capacity_three","frozen_commit":"a10bc27579bf5bd0ff1a90d6ad6e3f337d8ed7bc","production_commit":"03baf6bc6f06d3f298701a8ce66c44e00f509d50","rows":rows,"still_reproduced":[k for k,v in rows.items() if v["reproduced"]],"eliminated":[k for k,v in rows.items() if not v["reproduced"]]}
def main():
 p=argparse.ArgumentParser();p.add_argument("--json",type=Path);a=p.parse_args();r=run();t=json.dumps(r,indent=2,sort_keys=True);print(t)
 if a.json:a.json.parent.mkdir(parents=True,exist_ok=True);a.json.write_text(t+"\n",encoding="utf-8")
if __name__=="__main__":main()
