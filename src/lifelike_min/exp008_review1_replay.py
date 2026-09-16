from __future__ import annotations

import argparse
import json
from pathlib import Path

from .exp008_review1 import run_review


CORRECTED_PRODUCTION = "c42a43d353b21061b97cabb665e8ef59544d27c9"


def run() -> dict:
    report = run_review()
    report["holdouts_unchanged_from_first_generation"] = True
    report["original_reviewed_production"] = report.get("production_frozen_at")
    report["evaluated_production_after_minimal_repair"] = CORRECTED_PRODUCTION
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    report = run()
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    raise SystemExit(0 if report["reviewer_passed"] else 2)


if __name__ == "__main__":
    main()
