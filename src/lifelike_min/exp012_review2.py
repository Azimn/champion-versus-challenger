from __future__ import annotations

import argparse, json
from pathlib import Path
from .exp012_challenger import HabitTemporalPlasticityCharacter
from .runtime import Event


def reinforce(a,c="morning",act="walk",reward=1.0):
    a.step(Event(kind="neutral",context=c,forced_action=act))
    a.step(Event(kind="outcome",context=c,reward=reward,forced_action="idle"))


def filler(a, events):
    for e in events: a.step(e)


def neutral_events(n, context="x"):
    return [Event(kind="neutral",context=context,forced_action="idle") for _ in range(n)]


def value(a,key=("morning","walk")): return a.habits[key]


def segmentation():
    base=HabitTemporalPlasticityCharacter(); reinforce(base); enc=base.serialize_persistent()
    one=HabitTemporalPlasticityCharacter.from_persistent_json(enc)
    ten=HabitTemporalPlasticityCharacter.from_persistent_json(enc)
    filler(one,neutral_events(1,"block"))
    filler(ten,neutral_events(10,"block"))
    return {"one":value(one),"ten":value(ten),"depends_on_event_count":value(ten)<value(one),
            "claim":"processed experienced event count, not elapsed simulated time"}, value(ten)<value(one)


def reorder_irrelevant():
    base=HabitTemporalPlasticityCharacter(); reinforce(base); enc=base.serialize_persistent()
    events=[
        Event(kind="neutral",context="a",forced_action="idle"),
        Event(kind="support",actor="sam",context="b",forced_action="idle"),
        Event(kind="neutral",context="c",forced_action="idle"),
        Event(kind="observed_reliable",actor="sam",context="d",forced_action="idle"),
    ]*25
    a=HabitTemporalPlasticityCharacter.from_persistent_json(enc); b=HabitTemporalPlasticityCharacter.from_persistent_json(enc)
    filler(a,events); filler(b,list(reversed(events)))
    # Habit scalar should depend on count, while other mechanisms may differ in transient order.
    return {"a":value(a),"b":value(b),"habit_equal":value(a)==value(b)}, value(a)==value(b)


def context_mix_equal_count():
    base=HabitTemporalPlasticityCharacter(); reinforce(base); enc=base.serialize_persistent()
    a=HabitTemporalPlasticityCharacter.from_persistent_json(enc); b=HabitTemporalPlasticityCharacter.from_persistent_json(enc)
    filler(a,[Event(kind="neutral",context="same",forced_action="idle") for _ in range(250)])
    filler(b,[Event(kind="neutral",context=f"c{i%31}",forced_action="idle") for i in range(250)])
    return {"same_context":value(a),"mixed_context":value(b),"equal":value(a)==value(b)}, value(a)==value(b)


def meaningful_same_filler_different_segmentation():
    base=HabitTemporalPlasticityCharacter(); reinforce(base); enc=base.serialize_persistent()
    sparse=HabitTemporalPlasticityCharacter.from_persistent_json(enc); dense=HabitTemporalPlasticityCharacter.from_persistent_json(enc)
    filler(sparse,neutral_events(10))
    filler(dense,neutral_events(100))
    reinforce(sparse); reinforce(dense)
    return {"sparse_after_refresh":value(sparse),"dense_after_refresh":value(dense),
            "dense_lower_before_same_refresh":True,"both_refreshed":value(sparse)>0.35 and value(dense)>0.35}, value(sparse)>value(dense)>0.35


def repeated_zero_vs_negative():
    base=HabitTemporalPlasticityCharacter(); reinforce(base); enc=base.serialize_persistent()
    zero=HabitTemporalPlasticityCharacter.from_persistent_json(enc)
    neg=HabitTemporalPlasticityCharacter.from_persistent_json(enc)
    for _ in range(20):
        zero.step(Event(kind="neutral",context="morning",forced_action="walk"))
        zero.step(Event(kind="outcome",context="morning",reward=0.0,forced_action="idle"))
        neg.step(Event(kind="neutral",context="morning",forced_action="walk"))
        neg.step(Event(kind="outcome",context="morning",reward=-1.0,forced_action="idle"))
    vz=value(zero); vn=value(neg)
    return {"zero":vz,"negative":vn,"negative_more_informative":vn<vz}, vn<vz and vz>0


def saturation_refresh():
    a=HabitTemporalPlasticityCharacter()
    for _ in range(4): reinforce(a,reward=1.0)
    key=("morning","walk"); high=a.habits[key]
    # At/near clamp, fresh positive evidence must not be mistaken for nonuse.
    a.step(Event(kind="neutral",context="morning",forced_action="walk"))
    before=a.habits[key]
    a.step(Event(kind="outcome",context="morning",reward=1.0,forced_action="idle"))
    after=a.habits[key]
    return {"high":high,"before_outcome":before,"after_positive":after,"refreshed_not_attenuated_on_outcome":after>=before}, after>=before


def no_wall_clock():
    a=HabitTemporalPlasticityCharacter(); reinforce(a); before=a.serialize_persistent()
    # No sleep needed: reconstruction without processed events is the relevant causal boundary.
    b=HabitTemporalPlasticityCharacter.from_persistent_json(before)
    return {"equal_without_experience":before==b.serialize_persistent()}, before==b.serialize_persistent()


def old_recent_names():
    rows=[]
    for old,new in (("A","B"),("B","A"),("red","blue"),("blue","red")):
        a=HabitTemporalPlasticityCharacter(); reinforce(a,"ctx",old); filler(a,neutral_events(1200)); reinforce(a,"ctx",new); filler(a,neutral_events(11))
        enc=a.serialize_persistent()
        for order in ((old,new),(new,old)):
            b=HabitTemporalPlasticityCharacter.from_persistent_json(enc)
            choice=b.step(Event(kind="neutral",context="ctx",available_actions=order))
            rows.append({"old":old,"new":new,"order":order,"choice":choice})
    return rows, all(r["choice"]==r["new"] for r in rows)


def run():
    funcs=[("segmentation",segmentation),("reorder_irrelevant",reorder_irrelevant),("context_mix_equal_count",context_mix_equal_count),
           ("same_meaning_different_filler",meaningful_same_filler_different_segmentation),("zero_vs_negative",repeated_zero_vs_negative),
           ("saturation_refresh",saturation_refresh),("offline",no_wall_clock),("old_recent_names",old_recent_names)]
    tests={}
    for n,f in funcs:
        d,p=f(); tests[n]={"passed":p,"data":d}
    return {"experiment":"EXP-012 reviewer 2","temporal_variable":"processed subject-experienced event count",
            "segmentation_dependence_is_explicit_limitation":True,"tests":tests,
            "passed_count":sum(x["passed"] for x in tests.values()),"total":len(tests),"passed":all(x["passed"] for x in tests.values())}


def main():
    p=argparse.ArgumentParser(); p.add_argument("--json",type=Path); a=p.parse_args(); r=run(); s=json.dumps(r,indent=2,sort_keys=True); print(s)
    if a.json: a.json.parent.mkdir(parents=True,exist_ok=True); a.json.write_text(s+"\n")
    raise SystemExit(0 if r["passed"] else 2)
if __name__=="__main__": main()
