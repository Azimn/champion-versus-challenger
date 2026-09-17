from __future__ import annotations

import argparse, json
from pathlib import Path

from .exp012_challenger import HabitTemporalPlasticityCharacter
from .runtime import Event


def prospective_age_identity():
    old=HabitTemporalPlasticityCharacter()
    recent=HabitTemporalPlasticityCharacter()

    old.step(Event(kind="future_commitment",concern="remember",context="cue",forced_action="idle"))
    for i in range(1000):
        old.step(Event(kind="neutral",context=f"u{i%7}",forced_action="idle"))

    for i in range(1000):
        recent.step(Event(kind="neutral",context=f"u{i%7}",forced_action="idle"))
    recent.step(Event(kind="future_commitment",concern="remember",context="cue",forced_action="idle"))

    same_tick=old.tick==recent.tick
    old_state=old.serialize_persistent()
    recent_state=recent.serialize_persistent()

    old.step(Event(kind="neutral",context="cue",forced_action="idle"))
    recent.step(Event(kind="neutral",context="cue",forced_action="idle"))

    return {
        "same_tick":same_tick,
        "canonical_equal_before_cue":old_state==recent_state,
        "old_record":{"remember":"cue"},
        "recent_record":{"remember":"cue"},
        "old_reactivated_strength":old.concerns.get("remember"),
        "recent_reactivated_strength":recent.concerns.get("remember"),
        "information_present":"identity + cue only; no per-record age, strength, creation tick, refresh count, or confidence",
        "interpretation":"Age-sensitive prospective behavior cannot distinguish these histories from current subject-owned state. The missing distinction is representational, not a capacity shortage."
    }


def periods(actions,max_period=30):
    return [p for p in range(1,max_period+1) if all(actions[i]==actions[i%p] for i in range(len(actions)))]


def rhythm_case(fatigue,affiliation,competence):
    a=HabitTemporalPlasticityCharacter()
    a.fatigue=fatigue; a.affiliation=affiliation; a.competence=competence
    actions=[a.step(Event(kind="neutral")) for _ in range(240)]
    tail=actions[-120:]
    return {
        "initial":[fatigue,affiliation,competence],
        "tail":tail,
        "exact_periods":periods(tail),
        "final_needs":{"fatigue":a.fatigue,"affiliation":a.affiliation,"competence":a.competence},
        "habit_count":len(a.habits)
    }


def rhythm_diagnosis():
    cases={
        "baseline":rhythm_case(.25,.55,.15),
        "low":rhythm_case(.01,.02,.03),
        "high":rhythm_case(.91,.83,.77),
        "asymmetric":rhythm_case(.13,.92,.41),
        "epsilon":rhythm_case(.250001,.549999,.150002),
    }
    return {
        "cases":cases,
        "all_period_six":all(6 in x["exact_periods"] for x in cases.values()),
        "information_present":"Current fatigue, affiliation, competence and deterministic policy state are present.",
        "interpretation":"The exact cycle is an attractor of deterministic need drift, action effects, scoring, and tie-breaking. No missing autobiographical fact is required to generate or diagnose it. This is primarily an interaction/dynamics failure class."
    }


def run():
    p=prospective_age_identity()
    r=rhythm_diagnosis()
    return {
        "phase":"post-v9.5 survivor diagnosis before EXP-013",
        "frozen_basis":"v9.5_habit_temporal_plasticity / 79f747707dadfce9092d89ad19a17a9fcd7dd79b",
        "survivors":{
            "ancient_commitment_reactivates_unchanged":p,
            "deterministic_rhythm":r,
        },
        "diagnostic_order":{
            "ancient_commitment_reactivates_unchanged":{
                "required_information_already_present":False,
                "semantics_only_sufficient":False,
                "interaction_only_sufficient":"not established",
                "capacity_sufficient":False,
                "current_best_classification":"representational temporal-information deficit inside the existing prospective mechanism"
            },
            "deterministic_rhythm":{
                "required_information_already_present":True,
                "semantics_or_interaction_path_available":True,
                "capacity_sufficient":"not relevant",
                "current_best_classification":"endogenous deterministic dynamics / interaction-policy failure"
            }
        },
        "next_failure_for_full_preimplementation_diagnosis":"deterministic_rhythm",
        "selection_reason":"Under the established decision order, the rhythm failure should be examined first because the relevant current state already exists and a semantics/interaction correction may be possible without adding persistent information. Prospective aging has a demonstrated missing temporal distinction and should not be patched before lower-cost existing-state explanations for the other survivor are exhausted.",
        "exp013_not_implemented":True,
        "exp013_not_preregistered":True
    }


def main():
    p=argparse.ArgumentParser(); p.add_argument("--json",type=Path); a=p.parse_args(); r=run(); s=json.dumps(r,indent=2,sort_keys=True); print(s)
    if a.json:
        a.json.parent.mkdir(parents=True,exist_ok=True); a.json.write_text(s+"\n")
    raise SystemExit(0 if r["survivors"]["ancient_commitment_reactivates_unchanged"]["canonical_equal_before_cue"] and r["survivors"]["deterministic_rhythm"]["all_period_six"] else 2)

if __name__=="__main__": main()
