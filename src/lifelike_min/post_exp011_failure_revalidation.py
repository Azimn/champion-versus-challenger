from __future__ import annotations

import argparse
import json
from pathlib import Path

from .exp011_challenger import CapacityThreeProspectiveCharacter
from .runtime import Event


def classify(reproduced: bool, target: bool = False) -> str:
    if reproduced:
        return "still reproduced"
    return "eliminated by target correction" if target else "eliminated"


def rewarded_routine_never_weakens():
    a=CapacityThreeProspectiveCharacter()
    a.step(Event(kind="neutral", context="morning", available_actions=("walk","idle"), forced_action="walk"))
    a.step(Event(kind="outcome", context="morning", reward=1.0, forced_action="idle"))
    initial=a.habits.get(("morning","walk"))
    for i in range(1000):
        a.step(Event(kind="neutral", context=f"unrelated_{i%7}", forced_action="idle"))
    final=a.habits.get(("morning","walk"))
    returned=a.step(Event(kind="neutral", context="morning", available_actions=("walk","idle")))
    reproduced=(initial==0.35 and final==initial and returned=="walk")
    return {"reproduced":reproduced,"initial_value":initial,"after_1000_unrelated":final,"return_action":returned}


def ancient_commitment_reactivates_unchanged():
    a=CapacityThreeProspectiveCharacter()
    a.step(Event(kind="future_commitment", concern="ancient", context="ancient_cue", forced_action="idle"))
    stored_before=dict(a.prospective_commitments)
    for i in range(1000):
        a.step(Event(kind="neutral", context=f"unrelated_{i%7}", forced_action="idle"))
    stored_after=dict(a.prospective_commitments)
    a.step(Event(kind="neutral", context="ancient_cue", forced_action="idle"))
    strength=a.concerns.get("ancient")
    reproduced=(stored_before=={"ancient":"ancient_cue"} and stored_after==stored_before and strength==0.75)
    return {"reproduced":reproduced,"stored_before":stored_before,"stored_after_1000":stored_after,"reactivated_strength":strength}


def third_commitment_is_forgotten():
    a=CapacityThreeProspectiveCharacter()
    for name,cue in (("first","cue_first"),("second","cue_second"),("third","cue_third")):
        a.step(Event(kind="future_commitment", concern=name, context=cue, forced_action="idle"))
    stored=dict(a.prospective_commitments)
    a.step(Event(kind="neutral", context="cue_first", forced_action="idle"))
    reproduced=("first" not in a.concerns)
    return {"reproduced":reproduced,"stored_after_three":stored,"first_reactivated":"first" in a.concerns,"first_strength":a.concerns.get("first")}


def deterministic_rhythm():
    a=CapacityThreeProspectiveCharacter()
    actions=[]
    for _ in range(120):
        actions.append(a.step(Event(kind="neutral")))
    tail=actions[-60:]
    exact_periods=[p for p in range(1,31) if all(tail[i]==tail[i%p] for i in range(len(tail)))]
    expected=["rest","work","idle","rest","idle","idle"]*10
    reproduced=(tail==expected and 6 in exact_periods)
    return {"reproduced":reproduced,"tail":tail,"exact_periods":exact_periods}


def run():
    probes={
        "rewarded_routine_never_weakens": rewarded_routine_never_weakens(),
        "ancient_commitment_reactivates_unchanged": ancient_commitment_reactivates_unchanged(),
        "third_commitment_is_forgotten": third_commitment_is_forgotten(),
        "deterministic_rhythm": deterministic_rhythm(),
    }
    classes={name:classify(row["reproduced"],name=="third_commitment_is_forgotten") for name,row in probes.items()}
    return {
        "phase":"post-EXP-011 exact promoted-behavior revalidation",
        "candidate_version":"v9.4_prospective_capacity_three",
        "classifications":classes,
        "probes":probes,
        "target_eliminated":not probes["third_commitment_is_forgotten"]["reproduced"],
        "remaining_reproduced":[name for name,row in probes.items() if row["reproduced"]],
    }


def main():
    p=argparse.ArgumentParser(); p.add_argument("--json",type=Path); args=p.parse_args()
    r=run(); text=json.dumps(r,indent=2,sort_keys=True); print(text)
    if args.json:
        args.json.parent.mkdir(parents=True,exist_ok=True); args.json.write_text(text+"\n",encoding="utf-8")
    raise SystemExit(0 if r["target_eliminated"] else 2)


if __name__=="__main__": main()
