from __future__ import annotations

from pathlib import Path
import argparse
import json

from .runner import write_outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the persistent information asymmetry experiment")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/experiments/persistent-information-asymmetry/artifacts"),
    )
    args = parser.parse_args(argv)
    comparison = write_outputs(args.output)
    print(json.dumps(comparison, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
