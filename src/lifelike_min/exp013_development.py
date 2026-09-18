from __future__ import annotations

import argparse, itertools, json, statistics, time
from collections import Counter
from pathlib import Path

from .exp012_challenger import HabitTemporalPlasticityCharacter
from .exp013_challenger import (
    AdaptiveMobilizationThresholdCharacter,
    NoAdaptiveMobilizationCharacter,
)
from .runtime import Event


GRID=(0.0,0.1,0.25,0.5,0.75,1.0)


def detect_tail_period(actions, max_period=2000, repeats=12):
    n=len(actions)
    for p in range(1,min(max_period,n//repeats)+1):
        tail=actions[-p*repeats:]
        if all(tail[i]==tail[i%p] for i in range(len(tail))):
            return p
    return None


def canonical_cycle(seq):
    if not seq:
        return ()
    rots=[tuple(seq[i:]+seq[:i]) for i in range(len(seq))]
    return min(rots)


def run_autonomy(cls, f0=.25,c0=.15,ticks=20000, order=("rest","work","idle")):
    a=cls()
    a.fatigue=f0
    a.competence=c0
    actions=[]
    fatigue=[]
    competence=[]
    threshold=[]
    for _ in range(ticks):
        action=a.step(Event(kind="neutral",available_actions=order))
        actions.append(action)
        fatigue.append(a.fatigue)
        competence.append(a.competence)
        threshold.append(getattr(a,"action_mobilization_threshold",0.10))
    period=detect_tail_period(actions)
    tailcycle=canonical_cycle(actions[-period:]) if period else ()
    return {
      "period":period,
      "cycle":list(tailcycle),
      "actions_tail":actions[-120:],
      "frequency_last5000":dict(Counter(actions[-5000:])),
      "fatigue_bounds_last5000":[min(fatigue[-5000:]),max(fatigue[-5000:])],
      "competence_bounds_last5000":[min(competence[-5000:]),max(competence[-5000:])],
      "threshold_bounds_last5000":[min(threshold[-5000:]),max(threshold[-5000:])],
      "serialized":a.serialize_persistent(),
    }


def frozen_control():
    r=run_autonomy(HabitTemporalPlasticityCharacter,ticks=5000)
    return {"period":r["period"],"cycle":r["cycle"],"passed":r["period"]==6}


def grid_test():
    rows=[]
    identities=Counter()
    for f,c in itertools.product(GRID,repeat=2):
        r=run_autonomy(AdaptiveMobilizationThresholdCharacter,f,c)
        ident=(r["period"],tuple(r["cycle"]))
        identities[ident]+=1
        freq=r["frequency_last5000"]
        safe=(
          r["period"] is not None and r["period"]>30
          and all(x in freq and freq[x]>0 for x in ("rest","work","idle"))
          and max(freq.values())/5000 < .95
          and 0<=r["fatigue_bounds_last5000"][0]<=r["fatigue_bounds_last5000"][1]<=1
          and 0<=r["competence_bounds_last5000"][0]<=r["competence_bounds_last5000"][1]<=1
        )
        rows.append({"initial":[f,c],"period":r["period"],"cycle":r["cycle"],
                     "frequency":freq,"fatigue_bounds":r["fatigue_bounds_last5000"],
                     "competence_bounds":r["competence_bounds_last5000"],
                     "threshold_bounds":r["threshold_bounds_last5000"],"passes":safe})
    return {
      "rows":rows,
      "distinct_attractors":len(identities),
      "attractors":[{"period":k[0],"cycle":list(k[1]),"count":v} for k,v in identities.items()],
      "passed":all(r["passes"] for r in rows) and len(identities)>=2,
    }


def action_order():
    rows=[]
    for order in itertools.permutations(("rest","work","idle")):
        r=run_autonomy(AdaptiveMobilizationThresholdCharacter,ticks=12000,order=order)
        rows.append({"order":order,"period":r["period"],"cycle":r["cycle"],
                     "frequency":r["frequency_last5000"]})
    return {"rows":rows,"passed":all(r["period"] and r["period"]>30 for r in rows)}


def causal_ablation():
    control=run_autonomy(NoAdaptiveMobilizationCharacter,ticks=5000)
    challenger=run_autonomy(AdaptiveMobilizationThresholdCharacter,ticks=5000)
    return {"ablated_period":control["period"],"challenger_period":challenger["period"],
            "passed":control["period"]==6 and challenger["period"] and challenger["period"]>30}


def serialization():
    a=AdaptiveMobilizationThresholdCharacter()
    for _ in range(11):
        a.step(Event(kind="neutral",forced_action="rest"))
    elevated=a.action_mobilization_threshold
    encoded=a.serialize_persistent()
    b=AdaptiveMobilizationThresholdCharacter.from_persistent_json(encoded)
    exact=(a.persistent_snapshot()==b.persistent_snapshot())
    a_actions=[]; b_actions=[]
    for _ in range(250):
        a_actions.append(a.step(Event(kind="neutral")))
        b_actions.append(b.step(Event(kind="neutral")))
    return {"elevated_threshold":elevated,"exact_restore":exact,
            "continuation_actions_equal":a_actions==b_actions,
            "continuation_state_equal":a.serialize_persistent()==b.serialize_persistent(),
            "passed":exact and a_actions==b_actions and a.serialize_persistent()==b.serialize_persistent()}


def perturbations():
    rows={}
    def settled():
        a=AdaptiveMobilizationThresholdCharacter()
        for _ in range(10000): a.step(Event(kind="neutral"))
        return a
    cases={
      "fatigue_plus":lambda a:setattr(a,"fatigue",min(1,a.fatigue+.3)),
      "competence_plus":lambda a:setattr(a,"competence",min(1,a.competence+.3)),
      "forced_rest":lambda a:a.step(Event(kind="neutral",forced_action="rest")),
      "forced_work":lambda a:a.step(Event(kind="neutral",forced_action="work")),
      "neutral_observation":lambda a:a.step(Event(kind="observe_location",actor="stone",context="shelf",forced_action="idle")),
      "shock":lambda a:a.step(Event(kind="shock",intensity=.8,forced_action="idle")),
    }
    for name,fn in cases.items():
        a=settled(); fn(a); actions=[a.step(Event(kind="neutral")) for _ in range(5000)]
        p=detect_tail_period(actions)
        rows[name]={"period":p,"frequency":dict(Counter(actions[-2000:])),
                    "threshold":a.action_mobilization_threshold}
    return {"rows":rows,"passed":all(v["period"] and v["period"]>30 for v in rows.values())}


def history_sensitivity():
    # Habit remains causal under the new threshold.
    h=AdaptiveMobilizationThresholdCharacter()
    h.step(Event(kind="neutral",context="morning",forced_action="walk"))
    h.step(Event(kind="outcome",context="morning",reward=1.0,forced_action="idle"))
    habit_choice=h.step(Event(kind="neutral",context="morning",available_actions=("tea","walk")))

    # Relationship history remains causal.
    rel=AdaptiveMobilizationThresholdCharacter()
    for _ in range(3):
        rel.step(Event(kind="hostility",actor="morgan",intensity=1.0,forced_action="idle"))
    for _ in range(35):
        rel.step(Event(kind="neutral",forced_action="idle"))
    relation_choice=rel.step(Event(kind="neutral",actor="morgan",available_actions=("idle","avoid:morgan")))

    # Concern remains causal.
    con=AdaptiveMobilizationThresholdCharacter()
    con.step(Event(kind="task_assign",concern="report",intensity=1.0,forced_action="idle"))
    concern_choice=con.step(Event(kind="neutral",available_actions=("idle","work")))

    # Subjective fact remains causal.
    fact=AdaptiveMobilizationThresholdCharacter()
    fact.step(Event(kind="observe_location",actor="book",context="drawer",forced_action="idle"))
    fact_choice=fact.step(Event(kind="retrieve",actor="book",available_actions=("search:shelf","search:drawer")))

    return {
      "habit_choice":habit_choice,
      "relationship_choice":relation_choice,
      "concern_choice":concern_choice,
      "fact_choice":fact_choice,
      "passed":habit_choice=="walk" and relation_choice=="avoid:morgan" and concern_choice=="work" and fact_choice=="search:drawer",
    }


def ancient_prospective_preserved():
    a=AdaptiveMobilizationThresholdCharacter()
    a.step(Event(kind="future_commitment",concern="ancient",context="ancient_cue",forced_action="idle"))
    before=dict(a.prospective_commitments)
    for i in range(1000):
        a.step(Event(kind="neutral",context=f"u{i%7}",forced_action="idle"))
    after=dict(a.prospective_commitments)
    a.step(Event(kind="neutral",context="ancient_cue",forced_action="idle"))
    strength=a.concerns.get("ancient")
    return {"before":before,"after":after,"strength":strength,
            "passed":before==after=={"ancient":"ancient_cue"} and strength==.75}


def state_cost():
    c=AdaptiveMobilizationThresholdCharacter()
    f=HabitTemporalPlasticityCharacter()
    return {
      "mechanism_count":c.mechanism_count(),
      "old_mechanism_count":f.mechanism_count(),
      "fresh_candidate_canonical":len(c.serialize_persistent().encode()),
      "fresh_frozen_canonical":len(f.serialize_persistent().encode()),
      "fresh_candidate_diagnostic":c.persistent_state_bytes(),
      "fresh_frozen_diagnostic":f.persistent_state_bytes(),
      "new_fields":sorted(set(c.persistent_snapshot())-set(f.persistent_snapshot())),
      "passed":c.mechanism_count()==12 and set(c.persistent_snapshot())-set(f.persistent_snapshot())=={"action_mobilization_threshold"},
    }


def benchmark():
    def median_us(fn,n=1000):
        vals=[]
        for _ in range(n):
            t=time.perf_counter_ns(); fn(); vals.append((time.perf_counter_ns()-t)/1000)
        return statistics.median(vals)
    a=AdaptiveMobilizationThresholdCharacter()
    b=HabitTemporalPlasticityCharacter()
    event=Event(kind="neutral",forced_action="idle")
    return {
      "candidate_tick_us":median_us(lambda:a.step(event),300),
      "frozen_tick_us":median_us(lambda:b.step(event),300),
      "candidate_serialize_us":median_us(lambda:a.serialize_persistent(),300),
      "frozen_serialize_us":median_us(lambda:b.serialize_persistent(),300),
      "expected_incremental_complexity":"O(1) scalar drift, idle score substitution, and optional action pulse",
    }


def run():
    parts={
      "frozen_control":frozen_control(),
      "grid":grid_test(),
      "action_order":action_order(),
      "causal_ablation":causal_ablation(),
      "serialization":serialization(),
      "perturbations":perturbations(),
      "history_sensitivity":history_sensitivity(),
      "ancient_prospective":ancient_prospective_preserved(),
      "state_cost":state_cost(),
      "benchmark":benchmark(),
    }
    required=("frozen_control","grid","action_order","causal_ablation","serialization","perturbations",
              "history_sensitivity","ancient_prospective","state_cost")
    return {"experiment":"EXP-013 development","parameters":{"baseline":.10,"relaxation":.98,"pulse":.08},
            "parts":parts,"passed":all(parts[k]["passed"] for k in required)}


def main():
    p=argparse.ArgumentParser(); p.add_argument("--json",type=Path); a=p.parse_args()
    r=run(); s=json.dumps(r,indent=2,sort_keys=True); print(s)
    if a.json: a.json.parent.mkdir(parents=True,exist_ok=True); a.json.write_text(s+"\n")
    raise SystemExit(0 if r["passed"] else 2)

if __name__=="__main__": main()
