from __future__ import annotations

import argparse
import json
from pathlib import Path

from .exp010_challenger import CapacityThreeConcernCharacter
from .runtime import Event

PRODUCTION_FROZEN_AT = "03baf6bc6f06d3f298701a8ce66c44e00f509d50"


def assign(a, name, intensity):
    a.step(Event(kind="task_assign", concern=name, intensity=intensity, forced_action="idle"))


def cancel(a, name):
    a.step(Event(kind="task_cancel", concern=name, forced_action="idle"))


def abc():
    a = CapacityThreeConcernCharacter()
    assign(a, "A", .5); assign(a, "B", 1.0); assign(a, "C", .9)
    return a


def probe_long_dormancy():
    a = abc()
    for _ in range(10000): a.step(Event(kind="neutral", forced_action="idle"))
    before = dict(a.concerns); cancel(a, "B"); cancel(a, "C")
    return "A" in before and a.active_concern == "A"


def probe_cancel_suppressed():
    a = abc(); cancel(a, "A"); cancel(a, "B"); cancel(a, "C")
    return "A" not in a.concerns


def probe_work_does_not_hit_suppressed():
    a = abc(); before = dict(a.concerns); a.step(Event(kind="neutral", forced_action="work"))
    return a.concerns.get("A") is not None and a.concerns["A"] <= before["A"] and a.concerns.get("B", 0) < before["B"]


def probe_fourth_boundary():
    a = abc(); assign(a, "D", 1.0)
    return len(a.concerns) == 3 and "A" not in a.concerns and set(a.concerns) == {"B", "C", "D"}


def probe_equal_strength_order():
    survivors = []
    for order in (("A","B","C","D"),("D","C","B","A")):
        a = CapacityThreeConcernCharacter()
        for x in order: assign(a, x, .8)
        survivors.append(tuple(a.concerns))
    return len(survivors[0]) == 3 and len(survivors[1]) == 3 and survivors[0] != survivors[1]


def probe_reassign_suppressed():
    a = abc(); old = a.concerns["A"]; assign(a, "A", .95)
    return len(a.concerns) == 3 and a.concerns["A"] > old and a.active_concern == "A"


def probe_prospective_overlap():
    a = abc()
    a.step(Event(kind="future_commitment", concern="A", context="tomorrow", forced_action="idle"))
    return "A" in a.concerns and a.prospective_commitments.get("A") == "tomorrow"


def probe_serialization_suppressed():
    a = abc(); encoded = a.serialize_persistent(); b = CapacityThreeConcernCharacter.from_persistent_json(encoded)
    return b.serialize_persistent() == encoded and set(b.concerns) == {"A","B","C"} and b.active_concern == "B"


def probe_serialization_returned():
    a = abc(); cancel(a,"B"); cancel(a,"C"); encoded=a.serialize_persistent(); b=CapacityThreeConcernCharacter.from_persistent_json(encoded)
    return b.serialize_persistent() == encoded and b.active_concern == "A" and set(b.concerns)=={"A"}


def probe_no_ghost_after_resolution():
    a=abc(); cancel(a,"A"); encoded=a.serialize_persistent(); b=CapacityThreeConcernCharacter.from_persistent_json(encoded); cancel(b,"B"); cancel(b,"C")
    return "A" not in b.concerns and b.active_concern is None


def probe_repeated_cycles():
    a=CapacityThreeConcernCharacter(); assign(a,"A",.5)
    for i in range(12):
        assign(a,"B",1.0); assign(a,"C",.9)
        if "A" not in a.concerns or a.active_concern == "A": return False
        cancel(a,"B"); cancel(a,"C")
        if a.active_concern != "A": return False
    return set(a.concerns)=={"A"}


def probe_non_dominance_action():
    left=abc(); right=CapacityThreeConcernCharacter(); assign(right,"B",1.0); assign(right,"C",.9)
    event=Event(kind="neutral", available_actions=("work","rest","idle"))
    return left.step(event)==right.step(event) and left.active_concern==right.active_concern


def run():
    probes = {
        "long_dormancy_10000": probe_long_dormancy,
        "cancel_while_suppressed": probe_cancel_suppressed,
        "work_targets_active_not_suppressed": probe_work_does_not_hit_suppressed,
        "fourth_identity_is_bounded_loss": probe_fourth_boundary,
        "equal_strength_order_exposes_tie_policy": probe_equal_strength_order,
        "same_name_reassignment_no_duplicate": probe_reassign_suppressed,
        "prospective_same_name_remains_distinct": probe_prospective_overlap,
        "serialization_while_suppressed": probe_serialization_suppressed,
        "serialization_after_return": probe_serialization_returned,
        "resolved_identity_does_not_ghost": probe_no_ghost_after_resolution,
        "repeated_suppression_return_cycles": probe_repeated_cycles,
        "suppressed_identity_non_dominant_action": probe_non_dominance_action,
    }
    rows={}
    for name, fn in probes.items():
        try:
            passed=bool(fn()); rows[name]={"passed":passed}
        except Exception as exc:
            rows[name]={"passed":False,"error":f"{type(exc).__name__}: {exc}"}
    return {"production_frozen_at":PRODUCTION_FROZEN_AT,"passed":all(r["passed"] for r in rows.values()),"passed_count":sum(r["passed"] for r in rows.values()),"total":len(rows),"probes":rows}


def main():
    p=argparse.ArgumentParser(); p.add_argument("--json",type=Path); args=p.parse_args(); result=run()
    text=json.dumps(result,indent=2,sort_keys=True); print(text)
    if args.json: args.json.parent.mkdir(parents=True,exist_ok=True); args.json.write_text(text+"\n",encoding="utf-8")
    raise SystemExit(0 if result["passed"] else 1)

if __name__ == "__main__": main()
