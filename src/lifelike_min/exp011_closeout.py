from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

from .exp010_challenger import CapacityThreeConcernCharacter
from .exp011_challenger import CapacityThreeProspectiveCharacter
from .exp011_evaluation import run as development_run
from .exp011_review1_adjudication import run as review1_adjudication_run
from .exp011_review2 import run as review2_run
from .runtime import Event

PRODUCTION_FROZEN_COMMIT = "359682f463393dadeef53c8fc7a8c65eef5be8b4"
PRODUCTION_BLOB_SHA = "4238680bb78c21dd71b55cf279b2e4e2ce0e03a8"


def commit(a, name, cue):
    a.step(Event(kind="future_commitment", concern=name, context=cue, forced_action="idle"))


def deliver(a, cue):
    a.step(Event(kind="neutral", context=cue, forced_action="idle"))


def state_bytes(cls, count):
    a = cls()
    for i in range(count):
        commit(a, f"commitment{i:02d}", f"future_cue{i:02d}")
    return {
        "canonical": len(a.serialize_persistent().encode()),
        "diagnostic": a.persistent_state_bytes(),
        "entries": len(a.prospective_commitments),
    }


def median_us(fn, n=300):
    rows=[]
    for _ in range(7):
        t=time.perf_counter_ns()
        for _ in range(n):
            fn()
        rows.append((time.perf_counter_ns()-t)/n/1000.0)
    return statistics.median(rows)


def cost_audit():
    c2=CapacityThreeConcernCharacter
    c3=CapacityThreeProspectiveCharacter
    fresh2=state_bytes(c2,0); fresh3=state_bytes(c3,0)
    one2=state_bytes(c2,1); one3=state_bytes(c3,1)
    two2=state_bytes(c2,2); two3=state_bytes(c3,2)
    three3=state_bytes(c3,3)

    def insert2():
        a=c2(); commit(a,"commitment00","future_cue00")
    def insert3():
        a=c3(); commit(a,"commitment00","future_cue00")
    def cue2():
        a=c2(); commit(a,"commitment00","future_cue00"); deliver(a,"future_cue00")
    def cue3():
        a=c3(); commit(a,"commitment00","future_cue00"); deliver(a,"future_cue00")
    def restore2():
        a=c2(); commit(a,"commitment00","future_cue00"); commit(a,"commitment01","future_cue01"); c2.from_persistent_json(a.serialize_persistent())
    def restore3():
        a=c3();
        for i in range(3): commit(a,f"commitment{i:02d}",f"future_cue{i:02d}")
        c3.from_persistent_json(a.serialize_persistent())

    return {
        "mechanism_count": {"v9_3": c2().mechanism_count(), "challenger": c3().mechanism_count()},
        "persistent_field_sets_equal": set(c2().__dict__) == set(c3().__dict__),
        "fresh": {"v9_3": fresh2, "challenger": fresh3},
        "one_entry": {"v9_3": one2, "challenger": one3},
        "two_entries": {"v9_3": two2, "challenger": two3},
        "challenger_three_entries": three3,
        "marginal_third_entry_canonical_bytes": three3["canonical"] - two3["canonical"],
        "marginal_third_entry_diagnostic_bytes": three3["diagnostic"] - two3["diagnostic"],
        "timing_us_median": {
            "insert_v9_3": median_us(insert2),
            "insert_challenger": median_us(insert3),
            "cue_cycle_v9_3": median_us(cue2),
            "cue_cycle_challenger": median_us(cue3),
            "restore_v9_3_two": median_us(restore2,200),
            "restore_challenger_three": median_us(restore3,200),
        },
    }


def direct_causal_gate():
    class Ablated(CapacityThreeProspectiveCharacter):
        max_prospective=2

    rows={}
    for label,cls in (("baseline",CapacityThreeConcernCharacter),("candidate",CapacityThreeProspectiveCharacter),("ablated",Ablated)):
        a=cls()
        for name,cue in (("first","cue_first"),("second","cue_second"),("third","cue_third")):
            commit(a,name,cue)
        retained=dict(a.prospective_commitments)
        deliver(a,"cue_first")
        rows[label]={"retained_before_cue":retained,"first_reactivated":"first" in a.concerns}
    passed=(
        rows["baseline"]["first_reactivated"] is False
        and rows["candidate"]["first_reactivated"] is True
        and rows["ablated"]["first_reactivated"] is False
    )
    return {"passed":passed,"rows":rows}


def capacity_four_check():
    class CapacityFour(CapacityThreeProspectiveCharacter):
        max_prospective=4
    results={}
    for cap,cls in ((3,CapacityThreeProspectiveCharacter),(4,CapacityFour)):
        a=cls()
        for n,c in (("first","c1"),("second","c2"),("third","c3")):
            commit(a,n,c)
        deliver(a,"c1")
        results[str(cap)]={"target_reactivated":"first" in a.concerns,"retained_after_target":dict(a.prospective_commitments)}
    return {"passed":results["3"]["target_reactivated"] and results["4"]["target_reactivated"],"capacity4_adds_required_target_behavior":False,"results":results}


def second_order():
    return {
        "did_capacity_three_solve_continuity_failure": True,
        "minimum_information": "For this tested prospective behavior, later recovery requires the retained commitment identity plus its associated experienced future cue. Identity alone cannot determine which later cue should reactivate which commitment.",
        "recoverable_from_other_existing_mechanism": False,
        "test_harness_retains_causal_association": False,
        "capacity_three_earned_not_convenient": "Capacity two loses one of three identity+cue pairs and becomes state-identical to a history in which that pair never existed. Capacity three preserves all three. Capacity four adds no required behavior in the preregistered three-commitment target.",
        "replacement_semantics_changed": False,
        "cue_dependence": "The third retained commitment affects behavior only when its own actually experienced cue arrives. Wrong and unexperienced cues do not activate it.",
        "prospective_aging": "Long-lived prospective records remain unchanged. That is explicitly the separate ancient_commitment_reactivates_unchanged failure and is not solved here.",
        "bounded_loss_frontier": "Capacity three remains finite. A fourth distinct prospective commitment can still evict the oldest extant identity+cue pair under the inherited replacement rule, after which that lost pair is unrecoverable from subject-owned state.",
        "minimality_dimensions": {
            "mechanism_minimality": "MBASE-001 remains unchanged: the existing 11 mechanisms are locally subset-minimal for the tested envelope.",
            "representational_capacity_minimality": "For the demonstrated three-simultaneous-prospective target, capacity two is falsified and capacity three is the smallest tested successful bound; four is unnecessary for that target.",
            "semantic_minimality": "No prospective record schema or cue/reactivation semantic changed. Only the bounded number of existing identity+cue records changed.",
        },
    }


def run():
    dev=development_run()
    r1=review1_adjudication_run()
    r2=review2_run()
    causal=direct_causal_gate()
    cap4=capacity_four_check()
    costs=cost_audit()
    critique=second_order()

    passed=bool(
        dev["decision_pre_review"]=="PASS_DEVELOPMENT"
        and r1["passed"]
        and r2["passed"]
        and causal["passed"]
        and cap4["passed"]
        and costs["mechanism_count"]=={"v9_3":11,"challenger":11}
        and costs["persistent_field_sets_equal"]
        and costs["fresh"]["v9_3"]==costs["fresh"]["challenger"]
    )

    return {
        "experiment":"EXP-011",
        "production_frozen_commit":PRODUCTION_FROZEN_COMMIT,
        "production_blob_sha":PRODUCTION_BLOB_SHA,
        "passed":passed,
        "decision":"PROMOTE" if passed else "REJECT",
        "development":"PASS" if dev["decision_pre_review"]=="PASS_DEVELOPMENT" else "FAIL",
        "review1":{"adjudication_passed":r1["passed"],"raw_review_passed_count":r1["original_review"]["passed_count"],"raw_review_total":r1["original_review"]["total"],"classification":r1["classification"]},
        "review2":{"passed":r2["passed"],"passed_count":r2["passed_count"],"total":r2["total"]},
        "causal_ablation":causal,
        "capacity_four":cap4,
        "cost":costs,
        "second_order":critique,
        "claim":{
            "behavior_demonstrated":"Three simultaneous prospective identity+cue associations can remain represented, and each retained commitment can later reactivate through its own actually experienced cue without changing existing prospective semantics.",
            "information_lower_bound":"After capacity-two eviction, the lost history is canonically indistinguishable from a history in which that commitment never existed. Prospective recovery additionally requires the cue association, not identity alone.",
            "capacity_minimum_tested":"Capacity two fails the three-commitment target; capacity three succeeds; capacity four adds no required target behavior.",
            "mechanism_count":11,
            "not_established":["general prospective memory capacity","human working-memory limits","planning","rehearsal","forgetting","intention prioritization","unlimited future commitments","prospective aging or extinction"],
        },
    }


def main():
    p=argparse.ArgumentParser(); p.add_argument("--json",type=Path); args=p.parse_args()
    r=run(); text=json.dumps(r,indent=2,sort_keys=True); print(text)
    if args.json:
        args.json.parent.mkdir(parents=True,exist_ok=True); args.json.write_text(text+"\n",encoding="utf-8")
    raise SystemExit(0 if r["passed"] else 2)


if __name__=="__main__": main()
