from __future__ import annotations

import argparse
import json
from pathlib import Path

from .runtime import Event
from .v9_1_compact import V91CompactCharacter
from .v9_1_structural_closeout import populated_state
from .v9_1_structural_closeout_v2 import (
    explicit_earned_behavior_manifest,
    serialization_reconstruction_check,
)

FROZEN_VERSION = "v9.1_compact"
FROZEN_COMMIT = "2856ec6a32be0347a9243f6eff6faa404a9a0e6c"
EXPECTED_FRESH_BYTES = 269
EXPECTED_REPRESENTATIVE_BYTES = 577
EXPECTED_MAXIMUM_BYTES = 577
EXPECTED_MECHANISMS = 11
EXPECTED_CAPACITY = 2


def disappearance_trace(intensity: float, event_kind: str = "neutral") -> dict:
    agent = V91CompactCharacter()
    concern = f"unfinished_{intensity:.2f}"
    agent.step(
        Event(
            kind="task_assign",
            concern=concern,
            intensity=intensity,
            forced_action="idle",
        )
    )
    initial = float(agent.concerns[concern])
    rows = [{"offset": 0, "present": True, "strength": initial}]
    vanished_at = None
    for offset in range(1, 200):
        if event_kind == "social":
            event = Event(kind="support", actor="Unrelated", forced_action="idle")
        elif event_kind == "location":
            event = Event(kind="observe_location", actor="unrelated_object", context="hall", forced_action="idle")
        elif event_kind == "reliability":
            event = Event(kind="observed_reliable", actor="Unrelated", forced_action="idle")
        else:
            event = Event(kind="neutral", forced_action="idle")
        agent.step(event)
        present = concern in agent.concerns
        strength = float(agent.concerns.get(concern, 0.0))
        rows.append({"offset": offset, "present": present, "strength": strength})
        if not present:
            vanished_at = offset
            break
    return {
        "intensity": intensity,
        "event_kind": event_kind,
        "initial_strength": initial,
        "vanished_at": vanished_at,
        "last_present": next((row for row in reversed(rows) if row["present"]), None),
        "final": rows[-1],
        "rows": rows,
    }


def run() -> dict:
    agent = V91CompactCharacter()
    representative = populated_state(V91CompactCharacter, maximum_bounded=False)
    maximum = populated_state(V91CompactCharacter, maximum_bounded=True)
    manifest = explicit_earned_behavior_manifest()
    reconstruction = serialization_reconstruction_check()

    intensity_rows = [disappearance_trace(value) for value in (0.25, 0.50, 0.75, 1.00)]
    event_rows = [disappearance_trace(1.0, kind) for kind in ("neutral", "social", "location", "reliability")]

    metrics = {
        "mechanism_count": agent.mechanism_count(),
        "fresh_diagnostic_bytes": agent.persistent_state_bytes(),
        "representative_diagnostic_bytes": representative.persistent_state_bytes(),
        "maximum_bounded_store_diagnostic_bytes": maximum.persistent_state_bytes(),
        "concern_capacity": agent.max_concerns,
        "prospective_capacity": agent.max_prospective,
        "eligibility_capacity": agent.max_eligibility_records,
        "canonical_fresh_bytes": len(agent.serialize_persistent().encode("utf-8")),
    }

    expected_vanish = {0.25: 28, 0.50: 51, 0.75: 65, 1.00: 74}
    gates = {
        "earned_manifest": manifest["passed"],
        "canonical_reconstruction": reconstruction["passed"],
        "mechanism_count": metrics["mechanism_count"] == EXPECTED_MECHANISMS,
        "fresh_state": metrics["fresh_diagnostic_bytes"] == EXPECTED_FRESH_BYTES,
        "representative_state": metrics["representative_diagnostic_bytes"] == EXPECTED_REPRESENTATIVE_BYTES,
        "maximum_state": metrics["maximum_bounded_store_diagnostic_bytes"] == EXPECTED_MAXIMUM_BYTES,
        "capacities": metrics["concern_capacity"] == metrics["prospective_capacity"] == metrics["eligibility_capacity"] == EXPECTED_CAPACITY,
        "intensity_reproduction": all(row["vanished_at"] == expected_vanish[row["intensity"]] for row in intensity_rows),
        "unrelated_event_invariance": all(row["vanished_at"] == 74 for row in event_rows),
    }
    return {
        "phase": "EXP-009 frozen baseline reconstruction",
        "frozen_version": FROZEN_VERSION,
        "frozen_commit": FROZEN_COMMIT,
        "metrics": metrics,
        "gates": gates,
        "passed": all(gates.values()),
        "intensity_traces": intensity_rows,
        "unrelated_event_traces": event_rows,
        "earned_manifest": manifest,
        "reconstruction": reconstruction,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    report = run()
    encoded = json.dumps(report, indent=2, sort_keys=True)
    print(encoded)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(encoded + "\n", encoding="utf-8")
    raise SystemExit(0 if report["passed"] else 2)


if __name__ == "__main__":
    main()
