"""Frozen execution harness for the preregistered PEMA developmental experiment."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from cvc_research.experiments.information_asymmetry.developmental_experiment import (
    GENERATED_CONDITIONS,
    run_condition,
    summarize_blocks,
)
from cvc_research.experiments.information_asymmetry.developmental_world import (
    DEVELOPMENT_TICKS,
    WORLD_SEEDS,
    generate_history,
    serialize_history,
)
from cvc_research.experiments.information_asymmetry.mature_probe import (
    develop_mature_runtime_with_result,
    run_development_and_probe,
    run_mature_probe,
)

REVIEWED_SCIENTIFIC_BASELINE = "282fd73d10660f66352afe36e5f48a20b74dc9af"
CONDITIONS = (*GENERATED_CONDITIONS.keys(), "REPEATED_DIFFERENTIAL")
IDENTICAL_HISTORY_SEED = 1103


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def conservation_ok(result: dict[str, Any]) -> bool:
    conservation = result.get("resource_conservation")
    if conservation is None:
        conservation = result.get("conservation")
    if conservation is None:
        raise RuntimeError("developmental result lacks resource-conservation record")
    if isinstance(conservation, dict) and "error" in conservation:
        return abs(float(conservation["error"])) <= 1e-9
    if isinstance(conservation, bool):
        return conservation
    raise RuntimeError("unrecognized resource-conservation record")


def paired_history_hash(seed: int) -> str:
    return hashlib.sha256(serialize_history(generate_history(seed)).encode("utf-8")).hexdigest()


def run_one(seed: int, condition: str) -> dict[str, Any]:
    """Develop one lifetime exactly once, then probe that exact mature runtime."""
    mature, developmental = develop_mature_runtime_with_result(seed, condition, retain_trace=True)
    if not conservation_ok(developmental):
        raise RuntimeError(f"developmental conservation failed: {seed} {condition}")
    timeline = developmental["timeline"]
    blocks = summarize_blocks(timeline)
    probe = run_mature_probe(mature)
    probe_conservation = probe["probe_resource_conservation"]
    if abs(float(probe_conservation["error"])) > 1e-9:
        raise RuntimeError(f"probe conservation failed: {seed} {condition}")
    return {
        "seed": seed,
        "condition": condition,
        "development_ticks": DEVELOPMENT_TICKS,
        "history_sha256": None if condition == "REPEATED_DIFFERENTIAL" else paired_history_hash(seed),
        "developmental_blocks": blocks,
        "development_endpoint": {
            "exploration_evidence": timeline[-1]["exploration_evidence"],
            "routine_evidence": timeline[-1]["routine_evidence"],
            "concern_reserve": timeline[-1]["concern_reserve"],
            "concern_recalls": timeline[-1]["concern_recalls"],
            "resource_conservation": developmental["resource_conservation"],
        },
        "probe": probe,
    }


def identical_history_gate() -> dict[str, Any]:
    first = run_condition(IDENTICAL_HISTORY_SEED, "GENERATIVE_DIFFERENTIAL", retain_trace=True)
    second = run_condition(IDENTICAL_HISTORY_SEED, "GENERATIVE_DIFFERENTIAL", retain_trace=True)
    first_hash = digest(first)
    second_hash = digest(second)
    if first_hash != second_hash:
        raise RuntimeError("identical-history developmental traces differ")
    first_probe = run_development_and_probe(IDENTICAL_HISTORY_SEED, "GENERATIVE_DIFFERENTIAL")
    second_probe = run_development_and_probe(IDENTICAL_HISTORY_SEED, "GENERATIVE_DIFFERENTIAL")
    first_probe_hash = digest(first_probe)
    second_probe_hash = digest(second_probe)
    if first_probe_hash != second_probe_hash:
        raise RuntimeError("identical-history mature probe signatures/traces differ")
    return {"seed": IDENTICAL_HISTORY_SEED, "developmental_trace_sha256": first_hash, "replicate_developmental_trace_sha256": second_hash, "probe_sha256": first_probe_hash, "replicate_probe_sha256": second_probe_hash, "exact_match": True}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("artifacts/pema-developmental-world"))
    args = parser.parse_args()
    output: Path = args.output
    output.mkdir(parents=True, exist_ok=True)
    head = git_head()
    provenance = {"execution_commit": head, "reviewed_scientific_baseline": REVIEWED_SCIENTIFIC_BASELINE, "world_seeds": list(WORLD_SEEDS), "conditions": list(CONDITIONS), "development_ticks": DEVELOPMENT_TICKS, "identical_history_seed": IDENTICAL_HISTORY_SEED}
    write_json(output / "provenance.json", provenance)
    history_hashes = {str(seed): paired_history_hash(seed) for seed in WORLD_SEEDS}
    write_json(output / "history_hashes.json", history_hashes)
    artifact_index: list[dict[str, Any]] = []
    for seed in WORLD_SEEDS:
        expected_history = history_hashes[str(seed)]
        for condition in CONDITIONS:
            result = run_one(seed, condition)
            if condition != "REPEATED_DIFFERENTIAL" and result["history_sha256"] != expected_history:
                raise RuntimeError(f"paired history mismatch: {seed} {condition}")
            relative = Path("per_seed") / str(seed) / f"{condition}.json"
            write_json(output / relative, result)
            artifact_index.append({"seed": seed, "condition": condition, "path": relative.as_posix(), "sha256": digest(result)})
    replicate = identical_history_gate()
    write_json(output / "identical_history_replicate.json", replicate)
    write_json(output / "artifact_index.json", artifact_index)
    manifest = {"provenance": provenance, "per_seed_artifact_count": len(artifact_index), "identical_history": replicate, "artifact_index_sha256": digest(artifact_index), "status": "execution_complete_uninterpreted"}
    write_json(output / "manifest.json", manifest)


if __name__ == "__main__":
    main()
