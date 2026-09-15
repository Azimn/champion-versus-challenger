"""Command-line entry points for research-state and trace validation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .state import validate_research_state
from .trace import TraceValidationError, validate_trace_file


def validate_trace_main() -> int:
    parser = argparse.ArgumentParser(description="Validate a common behavioral JSONL trace.")
    parser.add_argument("trace", type=Path)
    args = parser.parse_args()

    try:
        summary = validate_trace_file(args.trace)
    except (OSError, TraceValidationError) as exc:
        print(str(exc))
        return 1

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def validate_state_main() -> int:
    parser = argparse.ArgumentParser(description="Validate permanent Champion versus Challenger research state.")
    parser.add_argument("root", nargs="?", default=".", type=Path)
    args = parser.parse_args()

    errors = validate_research_state(args.root)
    if errors:
        for error in errors:
            print(error)
        return 1

    print("research state valid")
    return 0
