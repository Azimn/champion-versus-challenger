from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
import json

from .metabolic_runner import write_metabolic_outputs


def main(argv: list[str] | None = None) -> int:
    parser = ArgumentParser(description="Run the metabolic information-asymmetry experiment")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/experiments/metabolic-information-asymmetry/artifacts"),
    )
    args = parser.parse_args(argv)
    result = write_metabolic_outputs(args.output)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
