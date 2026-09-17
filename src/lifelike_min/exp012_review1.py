from __future__ import annotations

import argparse, json, math, time
from pathlib import Path
from .exp012_challenger import HabitTemporalPlasticityCharacter
from .runtime import Event


def reinforce(a,c="morning",act="walk",reward=1.0):
    a.step(Event(kind="neutral",context=c,forced_action=act))
    a.step(Event(kind="outcome",context=c,reward=reward,forced_action="idle"))


def neutral(a,n,context="elsewhere"):
    for _ in range(n): a.step(Event(kind="neutral",context=context,forced_action="idle"))


def test_short_and_long():
    a=HabitTemporalPlasticityCharacter(); reinforce(a); v0=a.habits[("morning","walk")]
    vals={}
    last=0
    for horizon in (1,3,5,10,100,500,1000,10000):
        neutral(a,horizon-last); vals[str(horizon)]=a.habits[("morning","walk")]; last=horizon
    return vals, vals["10"]>0.97*v0 and vals["1000"]<0.86*v0 and vals["10000"]>0


def test_order_permutations():
    rows=[]
    for old,new in (("walk","stretch"),("alpha","beta"),("left","right")):
        a=HabitTemporalPlasticityCharacter(); reinforce(a,"ctx",old); neutral(a,1000); reinforce(a,"ctx",new); neutral(a,11)
        enc=a.serialize_persistent()
        for order in ((old,new),(new,old)):
            b=HabitTemporalPlasticityCharacter.from_persistent_json(enc)
            choice=b.step(Event(kind="neutral",context="ctx",available_actions=order))
            rows.append({"old":old,"new":new,"order":order,"choice":choice,"values":dict((k[1],v) for k,v in a.habits.items() if k[0]=="ctx")})
    return rows, all(r["choice"]==r["new"] for r in rows)


def test_reward_semantics():
    a=HabitTemporalPlasticityCharacter(); reinforce(a); key=("morning","walk"); base=a.habits[key]
    neutral(a,10); stale=a.habits[key]
    # zero outcome supplies no learned update
    a.step(Event(kind="outcome",context="morning",reward=0.0,forced_action="idle")); zero=a.habits[key]
    # explicit negative evidence after a fresh eligible action
    a.step(Event(kind="neutral",context="morning",forced_action="walk")); before_neg=a.habits[key]
    a.step(Event(kind="outcome",context="morning",reward=-1.0,forced_action="idle")); neg=a.habits[key]
    return {"base":base,"stale":stale,"zero":zero,"before_neg":before_neg,"negative":neg}, zero<stale and neg<before_neg


def test_delayed_credit():
    p=HabitTemporalPlasticityCharacter()
    p.step(Event(kind="neutral",context="project",forced_action="plan"))
    p.step(Event(kind="neutral",context="other",forced_action="idle"))
    p.step(Event(kind="outcome",context="project",reward=1.0,forced_action="idle"))
    pos=p.habits.get(("project","plan"),0.0)

    n=HabitTemporalPlasticityCharacter()
    n.step(Event(kind="neutral",context="project",forced_action="plan"))
    n.step(Event(kind="neutral",context="other",forced_action="idle"))
    n.step(Event(kind="outcome",context="project",reward=-1.0,forced_action="idle"))
    neg=n.habits.get(("project","plan"),0.0)

    amb=HabitTemporalPlasticityCharacter()
    amb.step(Event(kind="neutral",context="amb",forced_action="a"))
    amb.step(Event(kind="neutral",context="amb",forced_action="b"))
    amb.step(Event(kind="outcome",context="amb",reward=1.0,forced_action="idle"))
    amb_values={str(k):v for k,v in amb.habits.items()}
    return {"positive":pos,"negative":neg,"ambiguous":amb_values}, pos>0 and neg<0 and ("amb","a") not in amb.habits and ("amb","b") not in amb.habits


def test_serialization():
    a=HabitTemporalPlasticityCharacter(); reinforce(a); neutral(a,123); before=a.serialize_persistent()
    time.sleep(0.01)
    b=HabitTemporalPlasticityCharacter.from_persistent_json(before)
    offline=(before==b.serialize_persistent())
    c=HabitTemporalPlasticityCharacter.from_persistent_json(before)
    neutral(b,77); neutral(c,77)
    return {"offline_unchanged":offline,"continuation_equal":b.serialize_persistent()==c.serialize_persistent()}, offline and b.serialize_persistent()==c.serialize_persistent()


def test_density():
    base=HabitTemporalPlasticityCharacter(); reinforce(base); enc=base.serialize_persistent()
    one=HabitTemporalPlasticityCharacter.from_persistent_json(enc); hundred=HabitTemporalPlasticityCharacter.from_persistent_json(enc)
    neutral(one,1); neutral(hundred,100)
    v1=one.habits[("morning","walk")]; v100=hundred.habits[("morning","walk")]
    return {"one_inert_event":v1,"hundred_inert_events":v100,"event_count_is_clock":v100<v1,"ratio":v100/v1}, v100<v1


def test_equal_event_count_mixtures():
    a=HabitTemporalPlasticityCharacter(); b=HabitTemporalPlasticityCharacter(); reinforce(a); reinforce(b)
    for i in range(200):
        a.step(Event(kind="neutral",context=f"a{i%2}",forced_action="idle"))
        b.step(Event(kind=("support" if i%2 else "neutral"),actor=("sam" if i%2 else None),context=f"b{i%11}",forced_action="idle"))
    va=a.habits[("morning","walk")]; vb=b.habits[("morning","walk")]
    return {"a":va,"b":vb,"equal":va==vb}, va==vb


def test_near_zero_and_refresh():
    a=HabitTemporalPlasticityCharacter(); reinforce(a); key=("morning","walk"); neutral(a,50000)
    tiny=a.habits[key]; key_present=key in a.habits
    reinforce(a); refreshed=a.habits[key]
    return {"tiny":tiny,"key_present":key_present,"refreshed":refreshed}, key_present and tiny>0 and refreshed>tiny


def test_large_store():
    a=HabitTemporalPlasticityCharacter()
    for i in range(512): a.habits[(f"c{i}",f"a{i}")]=0.35
    before=len(a.habits); a.step(Event(kind="neutral",context="x",forced_action="idle"))
    vals=list(a.habits.values())
    return {"count":len(a.habits),"min":min(vals),"max":max(vals)}, len(a.habits)==before and all(0<v<0.35 for v in vals)


def run():
    tests={}
    for name,fn in [
        ("short_long",test_short_and_long),("order_permutations",test_order_permutations),
        ("reward_semantics",test_reward_semantics),("delayed_credit",test_delayed_credit),
        ("serialization",test_serialization),("density",test_density),
        ("equal_event_count_mixtures",test_equal_event_count_mixtures),("near_zero_refresh",test_near_zero_and_refresh),
        ("large_store",test_large_store)
    ]:
        data,passed=fn(); tests[name]={"passed":passed,"data":data}
    return {"experiment":"EXP-012 reviewer 1","production_freeze_branch":"exp012-production-freeze-1",
            "production_blob_expected":"9c6474de1918b62e827d32deff2fa10a4b2443d1",
            "tests":tests,"passed_count":sum(x["passed"] for x in tests.values()),"total":len(tests),
            "passed":all(x["passed"] for x in tests.values())}


def main():
    p=argparse.ArgumentParser(); p.add_argument("--json",type=Path); a=p.parse_args(); r=run(); s=json.dumps(r,indent=2,sort_keys=True); print(s)
    if a.json: a.json.parent.mkdir(parents=True,exist_ok=True); a.json.write_text(s+"\n")
    raise SystemExit(0 if r["passed"] else 2)
if __name__=="__main__": main()
