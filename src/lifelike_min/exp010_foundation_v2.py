from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import exp010_foundation as v1

PRIOR_FOUNDATION_RUN = 35168160541
PRIOR_FOUNDATION_ARTIFACT = 10475731437


def established_diagnostic_bytes(agent) -> int:
    """Use the established project diagnostic persistent-state metric.

    EXP-009 and the v9.1 structural closeout report diagnostic state with
    persistent_state_bytes(). The first EXP-010 foundation harness instead JSON-
    serialized the complete diagnostic snapshot directly, producing 290 bytes and
    causing only the expected 269-byte baseline gate to fail. This wrapper preserves
    that failed harness unchanged and corrects only the metric definition.
    """
    return agent.persistent_state_bytes()


def run() -> dict:
    original = v1.diagnostic_bytes
    v1.diagnostic_bytes = established_diagnostic_bytes
    try:
        report = v1.run()
    finally:
        v1.diagnostic_bytes = original

    report["phase"] = "corrected pre-archaeology information-loss foundation; no challenger"
    report["foundation_version"] = 2
    report["prior_foundation_failure"] = {
        "run": PRIOR_FOUNDATION_RUN,
        "artifact": PRIOR_FOUNDATION_ARTIFACT,
        "classification": "foundation-harness metric-definition error",
        "failed_gate": "frozen_baseline_matches",
        "observed_incorrect_diagnostic_measurement": 290,
        "established_diagnostic_measurement": report["baseline"]["fresh_diagnostic_bytes"],
        "production_changed": False,
        "information_loss_result_changed": False,
    }
    return report


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
    raise SystemExit(0 if report["foundation_passed"] else 2)


if __name__ == "__main__":
    main()
