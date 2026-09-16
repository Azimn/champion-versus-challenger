from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import failure_discovery_v9_1 as original_queue
from .exp009_challenger import UnresolvedConcernPersistenceCharacter

PROMOTED_VERSION = "v9.2_unresolved_concern_persistence"
PRODUCTION_COMMIT = "b5cc3e109ab2fa4de0421dc113009d1ee7fb050d"


def unchanged_probe(function):
    """Run the original v9.1 reproduction unchanged against the promoted class."""
    original = original_queue.V91CompactCharacter
    original_queue.V91CompactCharacter = UnresolvedConcernPersistenceCharacter
    try:
        return function()
    finally:
        original_queue.V91CompactCharacter = original


def run() -> dict:
    probes = {
        "unfinished_activity_evaporates": unchanged_probe(original_queue.unfinished_activity_evaporates),
        "rewarded_routine_never_weakens": unchanged_probe(original_queue.rewarded_routine_never_weakens),
        "ancient_commitment_reactivates_unchanged": unchanged_probe(original_queue.ancient_commitment_reactivates_unchanged),
        "third_commitment_is_forgotten": unchanged_probe(original_queue.third_commitment_is_forgotten),
        "suppressed_concern_never_returns": unchanged_probe(original_queue.suppressed_concern_never_returns),
        "deterministic_rhythm": unchanged_probe(original_queue.deterministic_rhythm),
    }
    previous = {
        "unfinished_activity_evaporates": True,
        "rewarded_routine_never_weakens": True,
        "ancient_commitment_reactivates_unchanged": True,
        "third_commitment_is_forgotten": True,
        "suppressed_concern_never_returns": True,
        "deterministic_rhythm": True,
    }
    classifications = {}
    for name, row in probes.items():
        now = bool(row["reproduced"])
        before = previous[name]
        if before and now:
            classification = "still reproduced"
        elif before and not now:
            classification = "eliminated incidentally" if name != "unfinished_activity_evaporates" else "eliminated by target correction"
        else:
            classification = "changed form"
        classifications[name] = classification

    return {
        "phase": "post-EXP-009 revalidation using unchanged original failure reproductions",
        "promoted_version": PROMOTED_VERSION,
        "production_commit": PRODUCTION_COMMIT,
        "original_reproduction_module_unchanged": "src/lifelike_min/failure_discovery_v9_1.py",
        "classifications": classifications,
        "probes": probes,
        "target_eliminated": not probes["unfinished_activity_evaporates"]["reproduced"],
        "suppressed_concern_incidental_gain": not probes["suppressed_concern_never_returns"]["reproduced"],
        "remaining_reproduced": [
            name for name, row in probes.items()
            if name != "unfinished_activity_evaporates" and row["reproduced"]
        ],
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
    raise SystemExit(0 if report["target_eliminated"] else 2)


if __name__ == "__main__":
    main()
