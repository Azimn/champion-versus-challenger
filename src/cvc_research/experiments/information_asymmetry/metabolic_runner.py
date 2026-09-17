from __future__ import annotations

from pathlib import Path
from typing import Any
import copy
import gzip
import json

from .metabolic import (
    ABUNDANT_CAPACITY,
    SCARCE_CAPACITY,
    MetabolicRouter,
    ResourceRegime,
    metabolic_record_to_dict,
)
from .model import Condition, SCENARIO, routing_topology, scenario_event_to_dict
from .processors import ActionProcessor, LanguageProcessor
from .runner import ExperimentRunner, final_behavior, report_for


class MetabolicExperimentRunner(ExperimentRunner):
    """PR-14 cognition with a single finite resource applied to communication."""

    def __init__(
        self,
        access_condition: Condition,
        resource_regime: ResourceRegime,
        *,
        initial_capacity: int | None = None,
    ) -> None:
        super().__init__(access_condition)
        self.resource_regime = resource_regime
        if initial_capacity is None:
            initial_capacity = (
                ABUNDANT_CAPACITY
                if resource_regime == ResourceRegime.ABUNDANT
                else SCARCE_CAPACITY
            )
        self.initial_capacity = initial_capacity
        self.router = MetabolicRouter(access_condition, initial_capacity)

    def run(self) -> dict[str, Any]:
        trace = super().run()
        trace.update(
            {
                "experiment": "metabolic_information_asymmetry",
                "access_condition": self.condition.value,
                "resource_regime": self.resource_regime.value,
                "initial_capacity_per_processor": self.initial_capacity,
                "resource_model": {
                    "resource_types": 1,
                    "replenishment": 0,
                    "social_fact_send_cost_per_recipient": 1,
                    "social_fact_assimilation_cost": 1,
                    "recommendation_and_binding_message_send_cost": 1,
                    "recommendation_and_binding_message_assimilation_cost": 1,
                    "task_prompts_and_behavior_observation_cost": 0,
                    "broadcast_funding": "atomic at sender",
                },
                "resource_conservation": {
                    "initial_total": self.router.ledger.initial_total,
                    "current_total": self.router.ledger.current_total,
                    "consumed_total": self.router.ledger.consumed_total,
                    "error": self.router.ledger.conservation_error(),
                },
            }
        )
        return trace

    def _record_timestep(self, timestep: int, label: str) -> None:
        processors: dict[str, Any] = {}
        for name, processor in self._processors.items():
            processors[name] = {
                "local_state": processor.snapshot(),
                "currently_inaccessible_relevant_information": sorted(
                    self.occurred_event_ids - processor.known_event_ids
                ),
                "resource_balance": self.router.ledger.balance(name),
            }
        messages = [
            metabolic_record_to_dict(record)
            for record in self.router.records
            if record.timestep == timestep
        ]
        self.timeline.append(
            {
                "timestep": timestep,
                "label": label,
                "processors": processors,
                "messages": messages,
                "resource_balances": self.router.ledger.snapshot(),
                "resource_consumed_total": self.router.ledger.consumed_total,
                "selected_behavior": self._latest_behavior(),
                "linguistic_report": self._latest_report(),
            }
        )


def run_metabolic_condition(
    access_condition: Condition,
    resource_regime: ResourceRegime,
    *,
    initial_capacity: int | None = None,
) -> dict[str, Any]:
    return MetabolicExperimentRunner(
        access_condition,
        resource_regime,
        initial_capacity=initial_capacity,
    ).run()


def _step(trace: dict[str, Any], timestep: int) -> dict[str, Any]:
    return next(item for item in trace["timeline"] if item["timestep"] == timestep)


def _knows(trace: dict[str, Any], timestep: int, processor: str, event_id: str) -> bool:
    return event_id in _step(trace, timestep)["processors"][processor]["local_state"][
        "known_event_ids"
    ]


def summarize_metabolic_trace(trace: dict[str, Any]) -> dict[str, Any]:
    step3 = _step(trace, 3)
    e3_routes = [
        record
        for record in step3["messages"]
        if record["sender"] == "PERCEPTION"
        and record["kind"] == "workspace_event"
        and record["payload"].get("event_id") == "E3"
    ]
    resource_failures = [
        record
        for step in trace["timeline"]
        for record in step["messages"]
        if record.get("failure_stage") in {"send_budget", "assimilation_budget"}
    ]
    return {
        "access_condition": trace["access_condition"],
        "resource_regime": trace["resource_regime"],
        "initial_capacity_per_processor": trace["initial_capacity_per_processor"],
        "final_behavior": final_behavior(trace),
        "social_knows_e3_at_t3": _knows(trace, 3, "SOCIAL", "E3"),
        "action_knows_e3_at_t3": _knows(trace, 3, "ACTION", "E3"),
        "language_knows_e3_at_t3": _knows(trace, 3, "LANGUAGE", "E3"),
        "e3_route_successes": sum(1 for record in e3_routes if record["succeeded"]),
        "e3_topology_blocks": sum(
            1 for record in e3_routes if record["failure_stage"] == "topology"
        ),
        "e3_resource_blocks": sum(
            1
            for record in e3_routes
            if record["failure_stage"] in {"send_budget", "assimilation_budget"}
        ),
        "resource_failure_count": len(resource_failures),
        "resource_consumed_total": trace["resource_conservation"]["consumed_total"],
        "resource_conservation_error": trace["resource_conservation"]["error"],
        "pre_binding_language_report": report_for(trace, "Q1_PRE_BINDING"),
        "post_binding_language_report": report_for(trace, "Q2_POST_BINDING"),
    }


def run_canonical_matrix() -> dict[str, dict[str, Any]]:
    matrix: dict[str, dict[str, Any]] = {}
    for access in (Condition.GLOBAL, Condition.DIFFERENTIAL):
        for regime in (ResourceRegime.ABUNDANT, ResourceRegime.SCARCE):
            key = f"{access.value}__{regime.value}"
            trace = run_metabolic_condition(access, regime)
            matrix[key] = summarize_metabolic_trace(trace)
    return matrix


def run_capacity_sweep(
    capacities: range = range(4, 11),
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for capacity in capacities:
        for access in (Condition.GLOBAL, Condition.DIFFERENTIAL):
            trace = run_metabolic_condition(
                access,
                ResourceRegime.SCARCE,
                initial_capacity=capacity,
            )
            summary = summarize_metabolic_trace(trace)
            rows.append(
                {
                    "capacity": capacity,
                    "access_condition": access.value,
                    "final_behavior": summary["final_behavior"],
                    "social_knows_e3_at_t3": summary["social_knows_e3_at_t3"],
                    "action_knows_e3_at_t3": summary["action_knows_e3_at_t3"],
                    "language_knows_e3_at_t3": summary["language_knows_e3_at_t3"],
                    "e3_resource_blocks": summary["e3_resource_blocks"],
                }
            )
    return rows


def matrix_analysis(matrix: dict[str, dict[str, Any]]) -> dict[str, Any]:
    gb_a = matrix["global_broadcast__abundant"]
    gb_s = matrix["global_broadcast__scarce"]
    da_a = matrix["differential_access__abundant"]
    da_s = matrix["differential_access__scarce"]
    return {
        "behavior_table": {
            "global_abundant": gb_a["final_behavior"],
            "global_scarce": gb_s["final_behavior"],
            "differential_abundant": da_a["final_behavior"],
            "differential_scarce": da_s["final_behavior"],
        },
        "scarcity_changes_global_behavior": gb_a["final_behavior"] != gb_s["final_behavior"],
        "scarcity_changes_differential_behavior": da_a["final_behavior"] != da_s["final_behavior"],
        "scarce_global_created_resource_asymmetry": (
            gb_s["e3_resource_blocks"] > 0
            and not gb_s["social_knows_e3_at_t3"]
            and not gb_s["action_knows_e3_at_t3"]
            and not gb_s["language_knows_e3_at_t3"]
        ),
        "scarce_differential_preserved_permitted_e3_routes": (
            da_s["action_knows_e3_at_t3"] and da_s["language_knows_e3_at_t3"]
        ),
        "interpretation": (
            "Under the canonical capacity, communication scarcity changes the global-broadcast run "
            "from SURPRISE_B to ASK_B_FIRST because PERCEPTION can finance E1's four-recipient "
            "broadcast but cannot later finance E3's four-recipient broadcast. Differential routing "
            "uses less capacity, so its permitted E3 deliveries remain affordable."
        ),
    }


def write_metabolic_outputs(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    traces: dict[str, dict[str, Any]] = {}
    for access in (Condition.GLOBAL, Condition.DIFFERENTIAL):
        for regime in (ResourceRegime.ABUNDANT, ResourceRegime.SCARCE):
            key = f"{access.value}__{regime.value}"
            traces[key] = run_metabolic_condition(access, regime)

    matrix = {key: summarize_metabolic_trace(trace) for key, trace in traces.items()}
    analysis = matrix_analysis(matrix)
    sweep = run_capacity_sweep()

    (output_dir / "matrix_summary.json").write_text(
        json.dumps({"conditions": matrix, "analysis": analysis}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "capacity_sweep.json").write_text(
        json.dumps(sweep, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    for key, trace in traces.items():
        payload = json.dumps(trace, sort_keys=True, separators=(",", ":")).encode("utf-8")
        (output_dir / f"trace_{key}.json.gz").write_bytes(gzip.compress(payload, mtime=0))
    return {"conditions": matrix, "analysis": analysis, "capacity_sweep": sweep}
