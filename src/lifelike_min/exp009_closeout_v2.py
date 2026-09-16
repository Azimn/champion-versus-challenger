from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import exp009_closeout as v1
from .exp009_challenger import UnresolvedConcernPersistenceCharacter
from .runtime import Event

PRIOR_CLOSEOUT_RUN = 35137960593
PRIOR_CLOSEOUT_ARTIFACT = 10463248914


def corrected_canonical_reconstruction() -> dict:
    original = UnresolvedConcernPersistenceCharacter()
    original.step(Event(kind="task_assign", concern="unfinished", intensity=1.0, forced_action="idle"))
    for _ in range(500):
        original.step(Event(kind="neutral", forced_action="idle"))
    original.step(Event(kind="support", actor="Alex", forced_action="idle"))
    original.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    original.step(Event(kind="context", context="garden", forced_action="water"))

    encoded = original.serialize_persistent()
    restored = UnresolvedConcernPersistenceCharacter.from_persistent_json(encoded)
    initial_equal = restored.persistent_snapshot() == original.persistent_snapshot()
    present_immediately_after_restore = "unfinished" in restored.concerns
    restored_strength = restored.concerns.get("unfinished")

    continuation = [
        Event(kind="neutral", forced_action="idle"),
        Event(kind="outcome", context="garden", reward=0.5, forced_action="idle"),
        Event(kind="request_help", actor="Alex", available_actions=("verify:Alex", "delegate:Alex")),
        Event(kind="neutral", available_actions=("rest", "work", "idle")),
    ]
    rows = []
    continued = True
    for event in continuation:
        a = original.step(event)
        b = restored.step(event)
        action_equal = a == b
        state_equal = original.persistent_snapshot() == restored.persistent_snapshot()
        continued = continued and action_equal and state_equal
        rows.append(
            {
                "event": event.kind,
                "original_action": a,
                "restored_action": b,
                "action_equal": action_equal,
                "state_equal": state_equal,
                "concern_present_original": "unfinished" in original.concerns,
                "concern_present_restored": "unfinished" in restored.concerns,
            }
        )

    final_resolved_identically = (
        ("unfinished" in original.concerns) == ("unfinished" in restored.concerns)
    )
    return {
        "passed": initial_equal and present_immediately_after_restore and continued and final_resolved_identically,
        "initial_equal": initial_equal,
        "present_immediately_after_restore": present_immediately_after_restore,
        "restored_strength": restored_strength,
        "continued": continued,
        "final_resolved_identically": final_resolved_identically,
        "final_concern_present": "unfinished" in restored.concerns,
        "rows": rows,
        "serialized_bytes": len(encoded.encode("utf-8")),
        "interpretation": "Persistence is established at restore. Later work-mediated resolution is valid and must remain identical across uninterrupted and restored copies, not be prohibited by the reconstruction test.",
    }


def run() -> dict:
    report = v1.run()
    corrected = corrected_canonical_reconstruction()
    report["prior_closeout"] = {
        "run": PRIOR_CLOSEOUT_RUN,
        "artifact": PRIOR_CLOSEOUT_ARTIFACT,
        "decision": "REJECT",
        "failed_gate": "canonical_reconstruction",
        "classification": "invalid closeout-harness assumption / termination-semantics error",
    }
    report["canonical_reconstruction"] = corrected
    report["gates"]["canonical_reconstruction"] = corrected["passed"]
    report["decision"] = "PROMOTE" if all(report["gates"].values()) else "REJECT"
    report["closeout_version"] = 2
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    report = run()
    encoded = json.dumps(v1.compact(report), indent=2, sort_keys=True)
    print(encoded)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(encoded + "\n", encoding="utf-8")
    raise SystemExit(0 if report["decision"] == "PROMOTE" else 2)


if __name__ == "__main__":
    main()
