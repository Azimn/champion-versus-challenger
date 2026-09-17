from __future__ import annotations
import argparse, json
from pathlib import Path
from .exp012_challenger import HabitTemporalPlasticityCharacter
from .runtime import Event


def rewarded_routine_never_weakens():
    a=HabitTemporalPlasticityCharacter()
    a.step(Event(kind="neutral",context="morning",forced_action="walk"))
    a.step(Event(kind="outcome",context="morning",reward=1.0,forced_action="idle"))
    initial=a.habits[("morning","walk")]
    for i in range(1000): a.step(Event(kind="neutral",context=f"u{i%7}",forced_action="idle"))
    final=a.habits[("morning","walk")]
    returned=a.step(Event(kind="neutral",context="morning",available_actions=("walk","idle")))
    reproduced=(initial==final==0.35)
    return {"reproduced":reproduced,"initial":initial,"after_1000":final,"return_action":returned}


def ancient_commitment_reactivates_unchanged():
    a=HabitTemporalPlasticityCharacter()
    a.step(Event(kind="future_commitment",concern="ancient",context="ancient_cue",forced_action="idle"))
    before=dict(a.prospective_commitments)
    for i in range(1000): a.step(Event(kind="neutral",context=f"u{i%7}",forced_action="idle"))
    after=dict(a.prospective_commitments)
    a.step(Event(kind="neutral",context="ancient_cue",forced_action="idle"))
    strength=a.concerns.get("ancient")
    return {"reproduced":before==after=={"ancient":"ancient_cue"} and strength==0.75,"stored_before":before,"stored_after":after,"reactivated_strength":strength}


def deterministic_rhythm():
    a=HabitTemporalPlasticityCharacter(); acts=[a.step(Event(kind="neutral")) for _ in range(120)]
    tail=acts[-60:]; periods=[p for p in range(1,31) if all(tail[i]==tail[i%p] for i in range(len(tail)))]
    expected=["rest","work","idle","rest","idle","idle"]*10
    return {"reproduced":tail==expected and 6 in periods,"tail":tail,"exact_periods":periods}


def run():
    p={"rewarded_routine_never_weakens":rewarded_routine_never_weakens(),
       "ancient_commitment_reactivates_unchanged":ancient_commitment_reactivates_unchanged(),
       "deterministic_rhythm":deterministic_rhythm()}
    cls={
      "rewarded_routine_never_weakens":"eliminated by target correction" if not p["rewarded_routine_never_weakens"]["reproduced"] else "still reproduced",
      "ancient_commitment_reactivates_unchanged":"still reproduced" if p["ancient_commitment_reactivates_unchanged"]["reproduced"] else "changed form",
      "deterministic_rhythm":"still reproduced" if p["deterministic_rhythm"]["reproduced"] else "changed form"}
    return {"phase":"post-EXP-012 frontier revalidation","candidate_version":"exp012_habit_temporal_plasticity_candidate",
            "classifications":cls,"probes":p,"target_eliminated":not p["rewarded_routine_never_weakens"]["reproduced"],
            "remaining_reproduced":[k for k,v in p.items() if v["reproduced"]]}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--json",type=Path); a=ap.parse_args(); r=run(); s=json.dumps(r,indent=2,sort_keys=True); print(s)
    if a.json: a.json.parent.mkdir(parents=True,exist_ok=True); a.json.write_text(s+"\n")
    raise SystemExit(0 if r["target_eliminated"] else 2)
if __name__=="__main__": main()
