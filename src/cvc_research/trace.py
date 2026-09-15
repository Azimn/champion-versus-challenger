"""Validation for architecture-neutral JSONL behavioral traces."""

from __future__ import annotations

import json
import math
import re
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any


RECORD_TYPES = frozenset({"event", "observation", "action", "state", "metric"})
CANDIDATE_ID_RE = re.compile(r"^PC-\d{3}$")
SCENARIO_ID_RE = re.compile(r"^B\d{2}$")
REQUIRED_FIELDS = frozenset(
    {
        "run_id",
        "scenario_id",
        "candidate_id",
        "candidate_version",
        "sim_time",
        "tick",
        "actor",
        "record_type",
        "native_type",
        "payload",
    }
)


class TraceValidationError(ValueError):
    """Raised when one or more trace records violate the common contract."""

    def __init__(self, errors: list[str]):
        self.errors = tuple(errors)
        super().__init__("\n".join(errors))


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _require_nonempty_string(record: Mapping[str, Any], key: str, label: str, errors: list[str]) -> None:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}: {key} must be a non-empty string")


def validate_trace_records(records: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Validate trace records and return a compact summary.

    Multiple run IDs may coexist in one file. Within a run, scenario, candidate,
    and candidate version are immutable, while tick and simulation time must be
    monotonic nondecreasing.
    """

    materialized = list(records)
    if not materialized:
        raise TraceValidationError(["trace contains no records"])

    errors: list[str] = []
    last_position: dict[str, tuple[int, float]] = {}
    run_metadata: dict[str, tuple[str, str, str]] = {}
    record_type_counts: dict[str, int] = {kind: 0 for kind in sorted(RECORD_TYPES)}

    for index, record in enumerate(materialized, start=1):
        label = f"record {index}"
        if not isinstance(record, Mapping):
            errors.append(f"{label}: record must be a JSON object")
            continue

        missing = sorted(REQUIRED_FIELDS.difference(record.keys()))
        if missing:
            errors.append(f"{label}: missing required fields: {', '.join(missing)}")
            continue

        for key in ("run_id", "scenario_id", "candidate_id", "candidate_version", "actor", "record_type", "native_type"):
            _require_nonempty_string(record, key, label, errors)

        run_id = record.get("run_id")
        scenario_id = record.get("scenario_id")
        candidate_id = record.get("candidate_id")
        candidate_version = record.get("candidate_version")
        record_type = record.get("record_type")
        tick = record.get("tick")
        sim_time = record.get("sim_time")

        if isinstance(scenario_id, str) and not SCENARIO_ID_RE.fullmatch(scenario_id):
            errors.append(f"{label}: scenario_id must match BNN, for example B01")
        if isinstance(candidate_id, str) and not CANDIDATE_ID_RE.fullmatch(candidate_id):
            errors.append(f"{label}: candidate_id must match PC-NNN, for example PC-001")
        if isinstance(record_type, str) and record_type not in RECORD_TYPES:
            errors.append(f"{label}: unknown record_type {record_type!r}")
        elif isinstance(record_type, str):
            record_type_counts[record_type] += 1

        if not isinstance(tick, int) or isinstance(tick, bool) or tick < 0:
            errors.append(f"{label}: tick must be a non-negative integer")
        if not _is_number(sim_time) or sim_time < 0:
            errors.append(f"{label}: sim_time must be a finite non-negative number")
        if not isinstance(record.get("payload"), dict):
            errors.append(f"{label}: payload must be a JSON object")

        normalized_type = record.get("normalized_type")
        if normalized_type is not None and (not isinstance(normalized_type, str) or not normalized_type.strip()):
            errors.append(f"{label}: normalized_type must be null or a non-empty string")

        target = record.get("target")
        if target is not None and (not isinstance(target, str) or not target.strip()):
            errors.append(f"{label}: target must be null or a non-empty string")

        wall_clock_ns = record.get("wall_clock_ns")
        if wall_clock_ns is not None and (
            not isinstance(wall_clock_ns, int) or isinstance(wall_clock_ns, bool) or wall_clock_ns < 0
        ):
            errors.append(f"{label}: wall_clock_ns must be null or a non-negative integer")

        if isinstance(run_id, str) and run_id.strip():
            current_metadata = (str(scenario_id), str(candidate_id), str(candidate_version))
            previous_metadata = run_metadata.get(run_id)
            if previous_metadata is None:
                run_metadata[run_id] = current_metadata
            elif current_metadata != previous_metadata:
                errors.append(
                    f"{label}: run_id {run_id!r} changed scenario/candidate/version metadata "
                    f"from {previous_metadata!r} to {current_metadata!r}"
                )

            if isinstance(tick, int) and not isinstance(tick, bool) and tick >= 0 and _is_number(sim_time) and sim_time >= 0:
                previous_position = last_position.get(run_id)
                current_position = (tick, float(sim_time))
                if previous_position is not None:
                    if tick < previous_position[0]:
                        errors.append(
                            f"{label}: tick regressed within run {run_id!r} from {previous_position[0]} to {tick}"
                        )
                    if float(sim_time) < previous_position[1]:
                        errors.append(
                            f"{label}: sim_time regressed within run {run_id!r} "
                            f"from {previous_position[1]} to {sim_time}"
                        )
                last_position[run_id] = current_position

    if errors:
        raise TraceValidationError(errors)

    return {
        "records": len(materialized),
        "runs": len(run_metadata),
        "record_types": record_type_counts,
        "run_ids": sorted(run_metadata),
    }


def validate_trace_file(path: str | Path) -> dict[str, Any]:
    """Load and validate a UTF-8 JSONL trace file."""

    trace_path = Path(path)
    records: list[dict[str, Any]] = []
    parse_errors: list[str] = []

    with trace_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                parse_errors.append(f"line {line_number}: invalid JSON: {exc.msg}")
                continue
            if not isinstance(value, dict):
                parse_errors.append(f"line {line_number}: top-level JSON value must be an object")
                continue
            records.append(value)

    if parse_errors:
        raise TraceValidationError(parse_errors)

    return validate_trace_records(records)
