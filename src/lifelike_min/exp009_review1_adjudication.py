from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from . import exp009_review1
from .exp009_challenger import UnresolvedConcernPersistenceCharacter
from .runtime import Event

PRODUCTION_COMMIT = "b5cc3e109ab2fa4de0421dc113009d1ee7fb050d"
RAW_REVIEW_RUN = 35137413998
RAW_REVIEW_ARTIFACT = 10463856104
EXPECTED_RAW_FAILURE = "reassignment_after_dormancy"


def numerical_adjudication() -> dict:
    agent = UnresolvedConcernPersistenceCharacter()
    agent.step(Event(kind="task_assign", concern="return_to_it", intensity=1.0, forced_action="idle"))
    for _ in range(10_000):
        agent.step(Event(kind="neutral", forced_action="idle"))
    before = agent.concerns.get("return_to_it")
    before_count = len(agent.concerns)
    agent.step(Event(kind="task_assign", concern="return_to_it", intensity=0.6, forced_action="idle"))
    after = agent.concerns.get("return_to_it")
    return {
        "passed": (
            before is not None
            and before >= 0.0
            and after is not None
            and math.isclose(after, 0.45, rel_tol=1e-15, abs_tol=1e-15)
            and after > before
            and len(agent.concerns) == before_count == 1
        ),
        "before": before,
        "after": after,
        "expected_mathematical_value": 0.45,
        "isclose_rel_tol": 1e-15,
        "isclose_abs_tol": 1e-15,
        "ledger_count": len(agent.concerns),
    }


def run() -> dict:
    raw = exp009_review1.reviewer()
    other_failures = [name for name in raw["failures"] if name != EXPECTED_RAW_FAILURE]
    numeric = numerical_adjudication()
    gates = {
        "raw_failure_set_exactly_preserved": raw["failures"] == [EXPECTED_RAW_FAILURE],
        "all_other_raw_probes_pass": not other_failures,
        "numeric_reassignment_behavior_valid": numeric["passed"],
        "production_commit_matches_frozen_record": raw["production_commit"] == PRODUCTION_COMMIT,
    }
    return {
        "experiment": "EXP-009",
        "phase": "reviewer generation 1 adjudication",
        "production_commit": PRODUCTION_COMMIT,
        "raw_review_run": RAW_REVIEW_RUN,
        "raw_review_artifact": RAW_REVIEW_ARTIFACT,
        "raw_reviewer_passed": raw["reviewer_passed"],
        "raw_failures": raw["failures"],
        "classification": {
            EXPECTED_RAW_FAILURE: "numerical artifact / invalid exact-float reviewer assumption"
        },
        "numeric_adjudication": numeric,
        "gates": gates,
        "adjudicated_passed": all(gates.values()),
        "note": "The untouched reviewer remains 14/15. This adjudication does not rewrite that evidence and does not modify production.",
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
    raise SystemExit(0 if report["adjudicated_passed"] else 2)


if __name__ == "__main__":
    main()
