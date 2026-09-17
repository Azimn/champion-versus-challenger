from __future__ import annotations

import argparse, json, math, statistics, time
from pathlib import Path

from .exp011_challenger import CapacityThreeProspectiveCharacter
from .exp012_challenger import (
    HabitTemporalPlasticityCharacter,
    NoAttenuationHabitTemporalPlasticityCharacter,
)
from .runtime import Event

RATES = {
    "control": 1.0,
    "very_slow": 0.9999,
    "intermediate": 0.9995,
    "too_fast": 0.99,
}


def cls_for(rate: float):
    return type(f"Rate_{rate}", (HabitTemporalPlasticityCharacter,), {"habit_nonuse_retention": rate})


def reinforce(a, context="morning", action="walk", reward=1.0):
    a.step(Event(kind="neutral", context=context, available_actions=(action, "idle"), forced_action=action))
    a.step(Event(kind="outcome", context=context, reward=reward, forced_action="idle"))


def unrelated(a, n: int, prefix="u"):
    for i in range(n):
        a.step(Event(kind="neutral", context=f"{prefix}_{i%7}", forced_action="idle"))


def value_after(rate: float, gap: int, reward=1.0):
    C=cls_for(rate); a=C(); reinforce(a,reward=reward); initial=a.habits[("morning","walk")]; unrelated(a,gap)
    return initial, a.habits[("morning","walk")]


def rate_tournament():
    rows={}
    passing=[]
    for name,r in RATES.items():
        i1,v1=value_after(r,1); i10,v10=value_after(r,10); _,v100=value_after(r,100); _,v500=value_after(r,500); _,v1000=value_after(r,1000)
        short=v10/i10
        long=v1000/i10
        passes=(short>=0.97 and long<=0.86 and name!="control")
        rows[name]={"retention":r,"gap1":v1,"gap10":v10,"gap100":v100,"gap500":v500,"gap1000":v1000,
                    "short_fraction":short,"long_fraction":long,"passes_rate_gates":passes}
        if passes: passing.append((r,name))
    selected=max(passing)[1] if passing else None
    return {"rows":rows,"selected":selected,"expected_selected":"intermediate","passed":selected=="intermediate"}


def old_recent_order():
    a=HabitTemporalPlasticityCharacter(); reinforce(a,"morning","walk"); unrelated(a,1000); reinforce(a,"morning","stretch"); unrelated(a,11)
    vals={k[1]:v for k,v in a.habits.items() if k[0]=="morning"}
    encoded=a.serialize_persistent()
    x=HabitTemporalPlasticityCharacter.from_persistent_json(encoded); y=HabitTemporalPlasticityCharacter.from_persistent_json(encoded)
    ca=x.step(Event(kind="neutral",context="morning",available_actions=("walk","stretch")))
    cb=y.step(Event(kind="neutral",context="morning",available_actions=("stretch","walk")))
    return {"values":vals,"choice_a":ca,"choice_b":cb,"passed":vals["stretch"]>vals["walk"] and ca=="stretch" and cb=="stretch"}


def signed_behavior():
    out={}
    for reward in (1.0,-1.0):
        a=HabitTemporalPlasticityCharacter(); reinforce(a,reward=reward)
        initial=a.habits[("morning","walk")]; unrelated(a,1000); stale=a.habits[("morning","walk")]
        sign_ok=(stale>=0 if initial>=0 else stale<=0) and abs(stale)<abs(initial)
        reinforce(a,reward=(-1.0 if reward>0 else 1.0))
        after_opposite=a.habits[("morning","walk")]
        out[str(reward)]={"initial":initial,"stale":stale,"after_opposite_evidence":after_opposite,"sign_ok":sign_ok}
    out["passed"]=all(v["sign_ok"] for k,v in out.items() if k!="passed")
    return out


def nonuse_nonreward():
    seed=HabitTemporalPlasticityCharacter(); reinforce(seed); encoded=seed.serialize_persistent()
    absent=HabitTemporalPlasticityCharacter.from_persistent_json(encoded)
    zero=HabitTemporalPlasticityCharacter.from_persistent_json(encoded)
    neg=HabitTemporalPlasticityCharacter.from_persistent_json(encoded)
    pos=HabitTemporalPlasticityCharacter.from_persistent_json(encoded)
    unavailable=HabitTemporalPlasticityCharacter.from_persistent_json(encoded)
    unrelated_ctx=HabitTemporalPlasticityCharacter.from_persistent_json(encoded)
    absent.step(Event(kind="neutral",context="morning",forced_action="idle"))
    zero.step(Event(kind="outcome",context="morning",reward=0.0,forced_action="idle"))
    # Create fresh eligible action for outcome evidence.
    neg.step(Event(kind="neutral",context="morning",forced_action="walk")); neg.step(Event(kind="outcome",context="morning",reward=-1.0,forced_action="idle"))
    pos.step(Event(kind="neutral",context="morning",forced_action="walk")); pos.step(Event(kind="outcome",context="morning",reward=1.0,forced_action="idle"))
    unavailable.step(Event(kind="neutral",context="morning",available_actions=("idle",),forced_action="idle"))
    unrelated_ctx.step(Event(kind="neutral",context="elsewhere",forced_action="idle"))
    key=("morning","walk")
    vals={n:o.habits[key] for n,o in [("not_performed",absent),("zero_reward",zero),("negative",neg),("positive",pos),("unavailable",unavailable),("unrelated_context",unrelated_ctx)]}
    return {"values":vals,"passed":vals["negative"]<vals["zero_reward"]<vals["positive"]}


def refresh_cycles():
    a=HabitTemporalPlasticityCharacter(); reinforce(a); initial=a.habits[("morning","walk")]
    rows=[]
    for _ in range(3):
        unrelated(a,1000); before=a.habits[("morning","walk")]; reinforce(a); after=a.habits[("morning","walk")]
        rows.append({"before_refresh":before,"after_refresh":after})
    return {"initial":initial,"cycles":rows,"passed":all(x["after_refresh"]>x["before_refresh"] for x in rows)}


def serialization():
    a=HabitTemporalPlasticityCharacter(); reinforce(a); before=a.habits.copy(); enc=a.serialize_persistent()
    b=HabitTemporalPlasticityCharacter.from_persistent_json(enc)
    offline_same=b.habits==before
    c=HabitTemporalPlasticityCharacter.from_persistent_json(enc)
    unrelated(b,50); unrelated(c,50)
    continuous_equal=b.serialize_persistent()==c.serialize_persistent()
    return {"offline_same":offline_same,"continued_equal":continuous_equal,"passed":offline_same and continuous_equal}


def density_clock():
    a=HabitTemporalPlasticityCharacter(); b=HabitTemporalPlasticityCharacter(); reinforce(a); reinforce(b)
    unrelated(a,1,"segment"); unrelated(b,10,"segment")
    va=a.habits[("morning","walk")]; vb=b.habits[("morning","walk")]
    return {"one_event":va,"ten_events":vb,"segmentation_matters":vb<va,"temporal_variable":"processed experienced event count","passed":vb<va}


def causal_ablation():
    a=HabitTemporalPlasticityCharacter(); b=NoAttenuationHabitTemporalPlasticityCharacter()
    reinforce(a); reinforce(b); unrelated(a,1000); unrelated(b,1000)
    va=a.habits[("morning","walk")]; vb=b.habits[("morning","walk")]
    return {"candidate":va,"ablated":vb,"passed":va<0.35 and vb==0.35}


def state_cost():
    fresh=HabitTemporalPlasticityCharacter(); frozen=CapacityThreeProspectiveCharacter()
    rows={}
    for n in (0,1,8,32,128):
        a=HabitTemporalPlasticityCharacter(); b=CapacityThreeProspectiveCharacter()
        for i in range(n):
            a.habits[(f"c{i}",f"a{i}")]=0.35; b.habits[(f"c{i}",f"a{i}")]=0.35
        rows[str(n)]={"candidate_canonical":len(a.serialize_persistent().encode()),"frozen_canonical":len(b.serialize_persistent().encode()),
                      "candidate_diagnostic":a.persistent_state_bytes(),"frozen_diagnostic":b.persistent_state_bytes()}
    return {"fresh_candidate":len(fresh.serialize_persistent().encode()),"fresh_frozen":len(frozen.serialize_persistent().encode()),
            "field_sets_equal":set(fresh.persistent_snapshot())==set(frozen.persistent_snapshot()),"rows":rows,
            "passed":len(fresh.serialize_persistent().encode())==245 and fresh.persistent_state_bytes()==269 and rows["32"]["candidate_canonical"]==rows["32"]["frozen_canonical"]}


def bench():
    def med(fn, reps=200):
        xs=[]
        for _ in range(reps):
            t=time.perf_counter_ns(); fn(); xs.append((time.perf_counter_ns()-t)/1000)
        return statistics.median(xs)
    rows={}
    for n in (0,1,8,32,128):
        a=HabitTemporalPlasticityCharacter()
        for i in range(n): a.habits[(f"c{i}",f"a{i}")]=0.35
        rows[str(n)]={"nonuse_us":med(lambda: a.step(Event(kind="neutral",context="x",forced_action="idle")),50)}
    r=HabitTemporalPlasticityCharacter(); reinforce(r)
    rows["reward_update_us"]=med(lambda: (r.step(Event(kind="neutral",context="morning",forced_action="walk")),r.step(Event(kind="outcome",context="morning",reward=1.0,forced_action="idle"))),50)
    rows["serialize_128_us"]=med(lambda: a.serialize_persistent(),100)
    enc=a.serialize_persistent(); rows["restore_128_us"]=med(lambda: HabitTemporalPlasticityCharacter.from_persistent_json(enc),100)
    return {"rows":rows,"expected_update_scaling":"O(n) over stored habit entries per processed event"}


def invariants():
    a=HabitTemporalPlasticityCharacter()
    return {"mechanisms":a.mechanism_count(),"concerns":a.max_concerns,"prospective":a.max_prospective,"eligibility":a.max_eligibility_records,
            "fresh_canonical":len(a.serialize_persistent().encode()),"fresh_diagnostic":a.persistent_state_bytes(),
            "passed":a.mechanism_count()==11 and a.max_concerns==3 and a.max_prospective==3 and a.max_eligibility_records==2 and len(a.serialize_persistent().encode())==245 and a.persistent_state_bytes()==269}


def run():
    r={"experiment":"EXP-012 development","operational_nonuse":"one attenuation per processed subject-experienced event for each pre-existing habit not receiving nonzero learned-value evidence on that event",
       "event_order":"inherited outcome learning first; attenuation second only for non-refreshed pre-existing habits",
       "rate_tournament":rate_tournament(),"old_recent_order":old_recent_order(),"signed":signed_behavior(),
       "nonuse_nonreward":nonuse_nonreward(),"refresh_cycles":refresh_cycles(),"serialization":serialization(),
       "density_clock":density_clock(),"causal_ablation":causal_ablation(),"state_cost":state_cost(),"benchmark":bench(),"invariants":invariants()}
    r["passed"]=all(r[k].get("passed",True) for k in ("rate_tournament","old_recent_order","signed","nonuse_nonreward","refresh_cycles","serialization","density_clock","causal_ablation","state_cost","invariants"))
    return r


def main():
    p=argparse.ArgumentParser(); p.add_argument("--json",type=Path); args=p.parse_args(); r=run(); s=json.dumps(r,indent=2,sort_keys=True); print(s)
    if args.json: args.json.parent.mkdir(parents=True,exist_ok=True); args.json.write_text(s+"\n")
    raise SystemExit(0 if r["passed"] else 2)

if __name__=="__main__": main()
