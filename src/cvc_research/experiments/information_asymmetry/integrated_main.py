from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
import json

from .integrated_runtime import (
    IntegratedConfig,
    canonical_variants,
    feedback_phase_grid,
    run_integrated,
    stress_suite,
)


def main(argv: list[str] | None = None) -> int:
    parser = ArgumentParser(description="Run the integrated PEMA shared-economy experiment")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/experiments/pema-integrated-runtime/artifacts"),
    )
    parser.add_argument("--seeds", type=int, default=10)
    args = parser.parse_args(argv)

    args.output.mkdir(parents=True, exist_ok=True)
    canonical = run_integrated(IntegratedConfig(), retain_trace=True)
    variants = canonical_variants()
    stress = stress_suite(seeds=range(args.seeds))
    phase_grid = feedback_phase_grid()

    (args.output / "canonical_trace.json").write_text(
        json.dumps(canonical, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output / "canonical_ablations.json").write_text(
        json.dumps(variants, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output / "stress_suite.json").write_text(
        json.dumps(stress, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output / "feedback_phase_grid.json").write_text(
        json.dumps(phase_grid, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    summary = {
        "canonical": {
            "behavior": canonical["behavior"],
            "concern": canonical["concern"],
            "channel_capture": canonical["channel_capture"],
            "information": canonical["information"],
            "resource_conservation": canonical["resource_conservation"],
        },
        "stress_aggregate": stress["aggregate"],
        "feedback_phase_grid": phase_grid,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
