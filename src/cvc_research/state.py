"""Guards for permanent research state and champion provenance."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


PERMANENT_ARTIFACTS = (
    "research/PROJECT_CATALOG.md",
    "research/MECHANISM_CATALOG.md",
    "research/EXPERIMENT_LEDGER.md",
    "research/CHAMPION_LINEAGE.md",
)

ALLOWED_CLASSIFICATIONS = frozenset(
    {
        "RUNNABLE BASELINE",
        "MECHANISM DONOR",
        "CONCEPTUAL DONOR",
        "UNUSABLE",
        "REQUIRES FURTHER INVESTIGATION",
    }
)

ALLOWED_QUALIFICATION_STATES = frozenset(
    {
        "DISCOVERED",
        "SOURCE VERIFIED",
        "EXECUTION PENDING",
        "EXECUTED",
        "ADAPTED",
        "BATTERY COMPLETE",
    }
)

CANDIDATE_ID_RE = re.compile(r"^PC-\d{3}$")
EXPERIMENT_ID_RE = re.compile(r"^EXP-\d{3,}$")


def _load_state(root: Path) -> dict[str, Any]:
    state_path = root / "research" / "state.json"
    try:
        with state_path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except FileNotFoundError:
        raise ValueError("research/state.json is missing") from None
    except json.JSONDecodeError as exc:
        raise ValueError(f"research/state.json is invalid JSON: {exc.msg}") from None

    if not isinstance(value, dict):
        raise ValueError("research/state.json must contain a JSON object")
    return value


def validate_research_state(root: str | Path = ".") -> list[str]:
    """Return validation errors for research state, or an empty list when valid."""

    repo_root = Path(root)
    errors: list[str] = []

    for relative_path in PERMANENT_ARTIFACTS:
        path = repo_root / relative_path
        if not path.is_file():
            errors.append(f"missing permanent artifact: {relative_path}")

    try:
        state = _load_state(repo_root)
    except ValueError as exc:
        errors.append(str(exc))
        return errors

    protocol_version = state.get("protocol_version")
    if not isinstance(protocol_version, str) or not protocol_version.strip():
        errors.append("protocol_version must be a non-empty string")

    candidates = state.get("candidates")
    if not isinstance(candidates, dict) or not candidates:
        errors.append("candidates must be a non-empty object")
    else:
        for candidate_id, candidate in candidates.items():
            prefix = f"candidate {candidate_id}"
            if not isinstance(candidate_id, str) or not CANDIDATE_ID_RE.fullmatch(candidate_id):
                errors.append(f"{prefix}: id must match PC-NNN")
                continue
            if not isinstance(candidate, dict):
                errors.append(f"{prefix}: entry must be an object")
                continue

            classification = candidate.get("classification")
            if classification not in ALLOWED_CLASSIFICATIONS:
                errors.append(f"{prefix}: invalid classification {classification!r}")

            qualification = candidate.get("qualification_state")
            if not isinstance(qualification, list) or not qualification:
                errors.append(f"{prefix}: qualification_state must be a non-empty list")
            else:
                unknown = [item for item in qualification if item not in ALLOWED_QUALIFICATION_STATES]
                if unknown:
                    errors.append(f"{prefix}: unknown qualification states {unknown!r}")
                if "BATTERY COMPLETE" in qualification:
                    evidence = candidate.get("evidence_experiment")
                    if not isinstance(evidence, str) or not EXPERIMENT_ID_RE.fullmatch(evidence):
                        errors.append(
                            f"{prefix}: BATTERY COMPLETE requires evidence_experiment matching EXP-NNN"
                        )

            source = candidate.get("source")
            if not isinstance(source, str) or not source.strip():
                errors.append(f"{prefix}: source must be a non-empty string")

    champion = state.get("champion")
    if champion is not None:
        if not isinstance(champion, dict):
            errors.append("champion must be null or an object")
        else:
            candidate_id = champion.get("candidate_id")
            if not isinstance(candidate_id, str) or not CANDIDATE_ID_RE.fullmatch(candidate_id):
                errors.append("champion.candidate_id must match PC-NNN")
            elif isinstance(candidates, dict) and candidate_id not in candidates:
                errors.append(f"champion candidate {candidate_id} is not present in candidates")

            frozen_ref = champion.get("frozen_ref")
            if not isinstance(frozen_ref, str) or not frozen_ref.strip():
                errors.append("champion.frozen_ref must be a non-empty immutable commit/tag reference")

            promotion_experiment = champion.get("promotion_experiment")
            if not isinstance(promotion_experiment, str) or not EXPERIMENT_ID_RE.fullmatch(promotion_experiment):
                errors.append("champion.promotion_experiment must match EXP-NNN")
            elif promotion_experiment == "EXP-000":
                errors.append("EXP-000 cannot promote a champion")

            if isinstance(candidates, dict) and isinstance(candidate_id, str) and candidate_id in candidates:
                qualification = candidates[candidate_id].get("qualification_state", [])
                if "BATTERY COMPLETE" not in qualification:
                    errors.append("champion candidate must have BATTERY COMPLETE qualification")
                evidence = candidates[candidate_id].get("evidence_experiment")
                if evidence != promotion_experiment:
                    errors.append(
                        "champion promotion_experiment must equal the candidate's BATTERY COMPLETE evidence_experiment"
                    )

    last_experiment = state.get("last_experiment")
    if not isinstance(last_experiment, str) or not EXPERIMENT_ID_RE.fullmatch(last_experiment):
        errors.append("last_experiment must match EXP-NNN")

    return errors
