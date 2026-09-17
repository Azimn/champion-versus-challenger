from __future__ import annotations

import argparse
import json
from pathlib import Path

from .exp011_challenger import CapacityThreeProspectiveCharacter
from .exp011_review1 import run as original_review_run
from .runtime import Event


def commit(a, name, cue):
    a.step(Event(kind="future_commitment", concern=name, context=cue, forced_action="idle"))


def deliver(a, cue):
    a.step(Event(kind="neutral", context=cue, forced_action="idle"))


def run():
    original = original_review_run()
    failures = original["failures"]
    exact_original_failure = (
        original["passed"] is False
        and original["passed_count"] == 42
        and original["total"] == 43
        and len(failures) == 1
        and failures[0]["name"] == "fill_activate_refill_cues"
    )

    a = CapacityThreeProspectiveCharacter()
    for name, cue in (("a", "ca"), ("b", "cb"), ("c", "cc")):
        commit(a, name, cue)
    initial_full = dict(a.prospective_commitments)

    deliver(a, "cb")
    after_b = {
        "concerns": dict(a.concerns),
        "prospective": dict(a.prospective_commitments),
    }

    commit(a, "d", "cd")
    after_refill = dict(a.prospective_commitments)

    activations = []
    for cue_name, identity in (("ca", "a"), ("cc", "c"), ("cd", "d")):
        deliver(a, cue_name)
        activations.append({
            "cue": cue_name,
            "identity": identity,
            "identity_active": identity in a.concerns,
            "binding_consumed": identity not in a.prospective_commitments,
            "concerns": dict(a.concerns),
            "prospective": dict(a.prospective_commitments),
        })

    adjudicated = (
        exact_original_failure
        and initial_full == {"a": "ca", "b": "cb", "c": "cc"}
        and "b" in after_b["concerns"]
        and after_b["prospective"] == {"a": "ca", "c": "cc"}
        and after_refill == {"a": "ca", "c": "cc", "d": "cd"}
        and all(x["identity_active"] and x["binding_consumed"] for x in activations)
        and not a.prospective_commitments
        and len(a.concerns) == 3
        and set(a.concerns) == {"a", "c", "d"}
        and "b" not in a.concerns
    )

    return {
        "experiment": "EXP-011",
        "adjudication": "review1",
        "passed": adjudicated,
        "classification": "invalid reviewer assumption / cross-capacity contract error",
        "original_review": {
            "passed_count": original["passed_count"],
            "total": original["total"],
            "failures": failures,
            "exact_expected_failure": exact_original_failure,
        },
        "replay": {
            "initial_full": initial_full,
            "after_b": after_b,
            "after_refill": after_refill,
            "activations": activations,
            "final_concerns": dict(a.concerns),
            "final_prospective": dict(a.prospective_commitments),
        },
        "production_change_required": False,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--json", type=Path)
    args = p.parse_args()
    r = run()
    text = json.dumps(r, indent=2, sort_keys=True)
    print(text)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(text + "\n", encoding="utf-8")
    raise SystemExit(0 if r["passed"] else 2)


if __name__ == "__main__":
    main()
