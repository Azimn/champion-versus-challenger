from __future__ import annotations

import argparse, itertools, json, math
from collections import Counter
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path

from .exp012_challenger import HabitTemporalPlasticityCharacter
from .runtime import Event

ACTIONS=("rest","work","idle")


def scores(a):
    e=Event(kind="neutral")
    return {x:a._score_action(x,e,0.0,0.0) for x in ACTIONS}


def full_state(a):
    return {
        "fatigue":a.fatigue,"affiliation":a.affiliation,"competence":a.competence,
        "concerns":dict(a.concerns),"affect":a.threat_residue,
        "habits":dict(a.habits),"prospective":dict(a.prospective_commitments),
        "relationships":dict(a.relationships),"reliability":dict(a.partner_reliability),
        "beliefs":dict(a.location_beliefs),
        "eligibility":[(r.context,r.action,r.age) for r in a.eligibility_records],
    }


def detect_period(seq, max_period=120, min_repeats=8):
    n=len(seq)
    for p in range(1,min(max_period,n//min_repeats)+1):
        width=p*min_repeats
        tail=seq[-width:]
        if all(tail[i]==tail[i%p] for i in range(width)):
            # earliest suffix start with same periodic extension
            start=n-width
            while start>0 and seq[start-1]==seq[(start-1-start)%p]:
                start-=1
            return p,start
    return None,None


def baseline_trace(ticks=5000, init=(.25,.55,.15), order=ACTIONS):
    a=HabitTemporalPlasticityCharacter()
    a.fatigue,a.affiliation,a.competence=init
    rows=[]; acts=[]
    for _ in range(ticks):
        # Production drift occurs before scoring. Capture state pre-step and infer scores after drift
        pre=full_state(a)
        a.tick += 1
        a._drift()
        immediate,task=a._process_event(Event(kind="neutral"))
        sc={x:a._score_action(x,Event(kind="neutral"),immediate,task) for x in order}
        ranked=sorted([(v,-i,k) for i,(k,v) in enumerate(sc.items())],reverse=True)
        win=ranked[0][2]; second=ranked[1][0]; margin=ranked[0][0]-second
        drifted=full_state(a)
        a._apply_action_effects(win,Event(kind="neutral"))
        post=full_state(a)
        rows.append({"tick":a.tick,"pre":pre,"drifted":drifted,"scores":sc,"winner":win,
                     "winner_score":ranked[0][0],"second_score":second,"margin":margin,
                     "exact_tie":abs(margin)==0.0,"post":post})
        acts.append(win)
    p,start=detect_period(acts)
    return a,rows,acts,p,start


def state_periodicity(rows, period=6, tail_pairs=100):
    diffs=[]
    for i in range(max(period,len(rows)-tail_pairs-period),len(rows)-period):
        x=rows[i]["post"]; y=rows[i+period]["post"]
        diffs.append({
            "tick":rows[i]["tick"],
            "fatigue":abs(x["fatigue"]-y["fatigue"]),
            "affiliation":abs(x["affiliation"]-y["affiliation"]),
            "competence":abs(x["competence"]-y["competence"]),
            "other_equal":{k:x[k]==y[k] for k in x if k not in {"fatigue","affiliation","competence"}},
        })
    maxd={k:max(d[k] for d in diffs) for k in ("fatigue","affiliation","competence")}
    exact=all(all(d[k]==0 for k in ("fatigue","affiliation","competence")) and all(d["other_equal"].values()) for d in diffs)
    return {"exact_periodic":exact,"max_abs_period6_difference":maxd,"samples":diffs[-12:]}


def basin():
    vals=[i/10 for i in range(11)]
    affiliations=(0.0,0.55,1.0)
    rows=[]; identities=Counter()
    for f,c,a0 in itertools.product(vals,vals,affiliations):
        _,trace,acts,p,start=baseline_trace(1500,(f,a0,c))
        tail=tuple(acts[-p:]) if p else ()
        # canonicalize cyclic phase
        if tail:
            rots=[tail[i:]+tail[:i] for i in range(len(tail))]
            ident=min(rots)
        else: ident=()
        identities[(p,ident)]+=1
        rows.append({"fatigue0":f,"competence0":c,"affiliation0":a0,"period":p,
                     "transient":start,"phase_tail":list(tail),"attractor_id":list(ident)})
    return {"starts":len(rows),"attractors":[{"period":k[0],"sequence":list(k[1]),"count":v} for k,v in identities.items()],
            "max_transient":max(r["transient"] or 999999 for r in rows),"rows":rows}


def action_order_audit():
    rows=[]
    for order in itertools.permutations(ACTIONS):
        _,trace,acts,p,start=baseline_trace(2000,(.25,.55,.15),order)
        rows.append({"order":order,"period":p,"transient":start,"tail":acts[-12:],
                     "ties_last60":sum(x["exact_tie"] for x in trace[-60:]),
                     "min_margin_last60":min(x["margin"] for x in trace[-60:])})
    return rows


def score_margin_analysis():
    _,rows,acts,p,start=baseline_trace(1000)
    cyc=rows[-12:]
    return {"period":p,"transient":start,"cycle":[{"tick":r["tick"],"scores":r["scores"],"winner":r["winner"],
            "margin":r["margin"],"exact_tie":r["exact_tie"],
            "drifted_needs":{k:r["drifted"][k] for k in ("fatigue","competence","affiliation")},
            "post_needs":{k:r["post"][k] for k in ("fatigue","competence","affiliation")}} for r in cyc],
            "ties":sum(r["exact_tie"] for r in rows[-120:]),
            "min_margin":min(r["margin"] for r in rows[-120:]),
            "max_margin":max(r["margin"] for r in rows[-120:])}


def reduced_sim(kind="float", ticks=1000, drift_first=True, f0=.25,c0=.15, df=.04,dc=.02,rest=.45,work=.45,idle=.10):
    if kind=="decimal":
        getcontext().prec=50; T=Decimal
        f,c=map(lambda x:T(str(x)),(f0,c0)); df,dc,rest,work,idle=map(lambda x:T(str(x)),(df,dc,rest,work,idle))
        clamp=lambda x:max(T("0"),min(T("1"),x))
    elif kind=="fraction":
        T=Fraction
        f,c=T(str(f0)),T(str(c0)); df,dc,rest,work,idle=map(lambda x:T(str(x)),(df,dc,rest,work,idle))
        clamp=lambda x:max(T(0),min(T(1),x))
    else:
        f,c=f0,c0; clamp=lambda x:max(0.0,min(1.0,x))
    acts=[]; states=[]
    for _ in range(ticks):
        if drift_first: f,c=clamp(f+df),clamp(c+dc)
        vals=[(f,0,"rest"),(c,-1,"work"),(idle,-2,"idle")]
        act=max(vals)[2]
        if act=="rest": f=clamp(f-rest)
        elif act=="work": c=clamp(c-work)
        if not drift_first: f,c=clamp(f+df),clamp(c+dc)
        acts.append(act); states.append((str(f),str(c)))
    p,start=detect_period(acts)
    return {"kind":kind,"drift_first":drift_first,"period":p,"transient":start,"tail":acts[-12:],
            "states_tail":states[-12:]}


def precision_and_order():
    return {
        "production_equations_float":reduced_sim("float"),
        "decimal50":reduced_sim("decimal"),
        "exact_fraction":reduced_sim("fraction"),
        "diagnostic_action_then_drift_float":reduced_sim("float",drift_first=False),
        "diagnostic_action_then_drift_fraction":reduced_sim("fraction",drift_first=False),
    }


def parameter_sweep():
    base={"df":.04,"dc":.02,"rest":.45,"work":.45}
    rows=[]
    for name,val in base.items():
        for pct in (-.05,-.01,-.001,.001,.01,.05):
            kw=base.copy(); kw[name]=val*(1+pct)
            r=reduced_sim("float",ticks=3000,**kw)
            rows.append({"parameter":name,"delta_pct":pct*100,"value":kw[name],"period":r["period"],
                         "transient":r["transient"],"tail":r["tail"]})
    return rows


def causal_decomposition():
    variants={
        "baseline":dict(),
        "freeze_fatigue":dict(df=0.0),
        "freeze_competence":dict(dc=0.0),
        "no_rest_effect":dict(rest=0.0),
        "no_work_effect":dict(work=0.0),
        "small_rest_effect":dict(rest=.10),
        "small_work_effect":dict(work=.10),
        "equal_drifts":dict(df=.03,dc=.03),
        "half_effects":dict(rest=.225,work=.225),
        "drift_only_no_effects":dict(rest=0.0,work=0.0),
    }
    return {k:reduced_sim("float",ticks=3000,**v) for k,v in variants.items()}


def perturb_running():
    def settle():
        a=HabitTemporalPlasticityCharacter()
        acts=[a.step(Event(kind="neutral")) for _ in range(1000)]
        return a,acts
    rows={}
    perturbations={
      "fatigue_plus":lambda a:setattr(a,"fatigue",min(1,a.fatigue+.3)),
      "affiliation_plus":lambda a:setattr(a,"affiliation",min(1,a.affiliation+.3)),
      "competence_plus":lambda a:setattr(a,"competence",min(1,a.competence+.3)),
      "shock":lambda a:a.step(Event(kind="shock",intensity=.8,forced_action="idle")),
      "forced_rest":lambda a:a.step(Event(kind="neutral",forced_action="rest")),
      "forced_work":lambda a:a.step(Event(kind="neutral",forced_action="work")),
    }
    canonical=("rest","work","idle","rest","idle","idle")
    def cyclic_match(seq):
        for off in range(6):
            if all(seq[i]==canonical[(i+off)%6] for i in range(len(seq))): return off
        return None
    for name,fn in perturbations.items():
        a,_=settle(); fn(a)
        after=[a.step(Event(kind="neutral")) for _ in range(300)]
        # Find first 36-action suffix segment matching cycle continuously
        rt=None; phase=None
        for s in range(len(after)-36):
            ph=cyclic_match(after[s:s+36])
            if ph is not None: rt=s; phase=ph; break
        rows[name]={"return_time":rt,"phase":phase,"tail":after[-18:]}
    return rows


def perceptual():
    _,_,acts,_,_=baseline_trace(120)
    tail=acts[-60:]
    phrase=" ".join(tail)
    block="rest work idle rest idle idle"
    return {"literal_actions":tail,"six_action_block":block,"block_repetitions":phrase.count(block),
            "externally_observable":tail==list(("rest","work","idle","rest","idle","idle"))*10}


def run():
    agent,rows,acts,p,start=baseline_trace(5000)
    result={
      "basis":"v9.5_habit_temporal_plasticity / 79f747707dadfce9092d89ad19a17a9fcd7dd79b",
      "production_blob":"9c6474de1918b62e827d32deff2fa10a4b2443d1",
      "baseline":{"period":p,"transient":start,"tail":acts[-24:]},
      "state_periodicity":state_periodicity(rows,6),
      "basin":basin(),
      "action_order":action_order_audit(),
      "score_margins":score_margin_analysis(),
      "precision_update_order":precision_and_order(),
      "parameter_sweep":parameter_sweep(),
      "causal_decomposition":causal_decomposition(),
      "running_perturbations":perturb_running(),
      "perceptual":perceptual(),
      "production_update_order":["tick increment","need/relationship/affect/concern/reliability drift","event integration including EXP-012 habit attenuation","action scoring","deterministic argmax with enumeration tie break","action effects","trace snapshot"],
    }
    result["passed"]=p==6 and result["perceptual"]["externally_observable"]
    return result


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--json",type=Path); a=ap.parse_args()
    r=run(); s=json.dumps(r,indent=2,sort_keys=True); print(s)
    if a.json: a.json.parent.mkdir(parents=True,exist_ok=True); a.json.write_text(s+"\n")
    raise SystemExit(0 if r["passed"] else 2)

if __name__=="__main__": main()
