from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
import json

from .pema_sequence import run_four_experiment_series


def main(argv: list[str] | None = None) -> int:
    parser = ArgumentParser(description="Run the four-stage PEMA causal experiment sequence")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)

    result = run_four_experiment_series()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
