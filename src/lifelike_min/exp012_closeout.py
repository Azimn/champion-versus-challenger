from __future__ import annotations
import argparse, json
from pathlib import Path
from . import exp012_development as development
from . import exp012_review1 as review1
from . import exp012_review2 as review2
from . import post_exp012_failure_revalidation as frontier
from .exp012_challenger import HabitTemporalPlasticityCharacter, NoAttenuationHabitTemporalPlasticityCharacter


def second_order(dev, r1, r2, f):
    return {
      "models_nonuse_or_event_passage":"The implemented temporal variable is processed subject-experienced event count. It does not measure wall-clock or simulated elapsed duration.",
      "event_density_hidden_clock":True,
      "event_density_interpretation":"Segmentation dependence is real and disclosed. Equal event counts with different irrelevant context mixtures attenuate equally; adding inert experienced events changes current habit support.",
      "context_absence_counts_as_nonuse":True,
      "negative_attenuation":"Negative learned values move toward neutral symmetrically; explicit negative evidence can still drive them more negative.",
      "scalar_conflation":"The scalar now represents current learned support, integrating reward history and subsequent nonuse. Detailed age is not retained.",
      "future_divergence_after_scalar_identity":"If two histories converge to the same scalar and all other subject-owned state is equal, EXP-012 intentionally predicts identical future habit behavior.",
      "delayed_credit_regression":not r1["tests"]["delayed_credit"]["passed"],
      "computational_scaling":"O(n) over stored habit entries per qualifying processed event.",
      "observer_difference":"Ancient and recently reinforced equal-initial-value routines now produce order-invariant different choices because current scalar strengths differ.",
      "slower_rate_tested":"0.9999 preserved more structure but failed the preregistered long-gap material-weakening gate.",
      "selected_rate":0.9995,
      "unrelated_frontier":f["classifications"],
    }


def run():
    d=development.run(); r1=review1.run(); r2=review2.run(); f=frontier.run()
    a=HabitTemporalPlasticityCharacter(); ab=NoAttenuationHabitTemporalPlasticityCharacter()
    invariants={
      "mechanisms":a.mechanism_count(),"concerns":a.max_concerns,"prospective":a.max_prospective,"eligibility":a.max_eligibility_records,
      "fresh_canonical":len(a.serialize_persistent().encode()),"fresh_diagnostic":a.persistent_state_bytes(),
      "persistent_fields":sorted(a.persistent_snapshot().keys()),
      "same_fields_as_ablation":set(a.persistent_snapshot())==set(ab.persistent_snapshot())
    }
    passed=(d["passed"] and r1["passed"] and r2["passed"] and f["target_eliminated"] and
            invariants["mechanisms"]==11 and invariants["concerns"]==3 and invariants["prospective"]==3 and invariants["eligibility"]==2 and
            invariants["fresh_canonical"]==245 and invariants["fresh_diagnostic"]==269 and invariants["same_fields_as_ablation"])
    return {
      "experiment":"EXP-012","decision":"PROMOTE" if passed else "REJECT","passed":passed,
      "production_blob":"9c6474de1918b62e827d32deff2fa10a4b2443d1","retention_factor":0.9995,
      "nonuse_semantics":"Each processed subject-experienced event attenuates each pre-existing habit unless that same event supplies a nonzero learned-value update to that habit.",
      "temporal_variable":"processed subject-experienced event count",
      "development":d,"review1":{"passed":r1["passed"],"passed_count":r1["passed_count"],"total":r1["total"]},
      "review2":{"passed":r2["passed"],"passed_count":r2["passed_count"],"total":r2["total"]},
      "frontier":f,"invariants":invariants,"second_order":second_order(d,r1,r2,f),
      "claim":{"behavior":"Ancient learned routines weaken while recently reinforced routines retain greater current influence and win order-invariant competition.",
               "scalar_semantics":"Existing signed contextual habit/action-value scalar represents current learned support and can integrate subject-experienced nonuse without another persistent dimension.",
               "not_established":["human habit extinction","human forgetting curve","biological habit decay","universal temporal discounting","optimal reinforcement learning","general memory decay"]}}
    

def main():
    p=argparse.ArgumentParser(); p.add_argument("--json",type=Path); a=p.parse_args(); r=run(); s=json.dumps(r,indent=2,sort_keys=True); print(s)
    if a.json: a.json.parent.mkdir(parents=True,exist_ok=True); a.json.write_text(s+"\n")
    raise SystemExit(0 if r["passed"] else 2)
if __name__=="__main__": main()
