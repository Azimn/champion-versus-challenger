from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable
import copy
import gzip
import json

from .model import (
    Condition,
    DeliveredMessage,
    MessageIntent,
    Router,
    SCENARIO,
    ScenarioEvent,
    route_record_to_dict,
    routing_topology,
    scenario_event_to_dict,
)
from .processors import (
    ActionProcessor,
    LanguageProcessor,
    MemoryProcessor,
    PerceptualProcessor,
    Processor,
    SocialProcessor,
)
from .reporting import results_markdown


class ExperimentRunner:
    def __init__(self, condition: Condition) -> None:
        self.condition = condition
        self.router = Router(condition)
        self._processors: dict[str, Processor] = {
            "PERCEPTION": PerceptualProcessor(),
            "SOCIAL": SocialProcessor(),
            "MEMORY": MemoryProcessor(),
            "ACTION": ActionProcessor(),
            "LANGUAGE": LanguageProcessor(),
        }
        self.timeline: list[dict[str, Any]] = []
        self.occurred_event_ids: set[str] = set()

    @property
    def processors_for_researcher(self) -> dict[str, Processor]:
        return self._processors

    def run(self) -> dict[str, Any]:
        for event in SCENARIO:
            self._deliver_scenario_event(event)
            self._record_timestep(event.timestep, f"scenario event {event.event_id}")

        self._deliver_to_processor(
            self.router.environment_message(
                timestep=5,
                receiver="LANGUAGE",
                kind="interview_question",
                payload={"question_id": "Q1_PRE_BINDING"},
                reason="research interview",
            )
        )
        self._record_timestep(5, "pre-binding interview")

        self.router.binding_active = True
        binding_outputs = self._deliver_to_processor(
            self.router.environment_message(
                timestep=6,
                receiver="LANGUAGE",
                kind="open_context_query",
                payload={"binding": "LANGUAGE_WITH_MEMORY_AND_SOCIAL"},
                reason="temporary coordination window opened",
            )
        )
        self._drain(binding_outputs, timestep=6)
        self.router.binding_active = False
        self._record_timestep(6, "temporary coordination window")

        self._deliver_to_processor(
            self.router.environment_message(
                timestep=7,
                receiver="LANGUAGE",
                kind="interview_question",
                payload={"question_id": "Q2_POST_BINDING"},
                reason="research interview",
            )
        )
        self._record_timestep(7, "post-binding interview")

        return {
            "condition": self.condition.value,
            "objective_ground_truth": [scenario_event_to_dict(event) for event in SCENARIO],
            "routing_topology": routing_topology(self.condition),
            "timeline": copy.deepcopy(self.timeline),
        }

    def _deliver_scenario_event(self, event: ScenarioEvent) -> None:
        self.occurred_event_ids.add(event.event_id)
        message = self.router.environment_message(
            timestep=event.timestep,
            receiver="PERCEPTION",
            kind="environment_event",
            payload=scenario_event_to_dict(event),
            reason="objective scenario event delivered to perception only",
        )
        self._drain(self._deliver_to_processor(message), timestep=event.timestep)

    def _deliver_to_processor(self, message: DeliveredMessage) -> list[MessageIntent]:
        return self._processors[message.receiver].receive(message)

    def _drain(self, initial: Iterable[MessageIntent], timestep: int) -> None:
        queue = list(initial)
        while queue:
            intent = queue.pop(0)
            for message in self.router.route(intent, timestep):
                queue.extend(self._deliver_to_processor(message))

    def _record_timestep(self, timestep: int, label: str) -> None:
        processors: dict[str, Any] = {}
        for name, processor in self._processors.items():
            processors[name] = {
                "local_state": processor.snapshot(),
                "currently_inaccessible_relevant_information": sorted(
                    self.occurred_event_ids - processor.known_event_ids
                ),
            }
        messages = [
            route_record_to_dict(record)
            for record in self.router.records
            if record.timestep == timestep
        ]
        self.timeline.append(
            {
                "timestep": timestep,
                "label": label,
                "processors": processors,
                "messages": messages,
                "selected_behavior": self._latest_behavior(),
                "linguistic_report": self._latest_report(),
            }
        )

    def _latest_behavior(self) -> dict[str, Any] | None:
        action = self._processors["ACTION"]
        assert isinstance(action, ActionProcessor)
        return copy.deepcopy(action.behavior_history[-1]) if action.behavior_history else None

    def _latest_report(self) -> dict[str, Any] | None:
        language = self._processors["LANGUAGE"]
        assert isinstance(language, LanguageProcessor)
        return copy.deepcopy(language.reports[-1]) if language.reports else None


def run_condition(condition: Condition) -> dict[str, Any]:
    return ExperimentRunner(condition).run()


def final_behavior(trace: dict[str, Any]) -> str | None:
    for step in reversed(trace["timeline"]):
        behavior = step.get("selected_behavior")
        if behavior and behavior.get("decision_id") == "birthday_surprise":
            return behavior["choice"]
    return None


def report_for(trace: dict[str, Any], question_id: str) -> dict[str, Any] | None:
    for step in trace["timeline"]:
        report = step.get("linguistic_report")
        if report and report.get("question_id") == question_id:
            return report
    return None


def compare_traces(global_trace: dict[str, Any], differential_trace: dict[str, Any]) -> dict[str, Any]:
    global_neutral = global_trace["timeline"][1]["selected_behavior"]
    differential_neutral = differential_trace["timeline"][1]["selected_behavior"]
    return {
        "neutral_behavior_identical_despite_asymmetry": global_neutral == differential_neutral,
        "neutral_behavior": global_neutral,
        "final_behavior_global": final_behavior(global_trace),
        "final_behavior_differential": final_behavior(differential_trace),
        "final_behavior_diverged": final_behavior(global_trace) != final_behavior(differential_trace),
        "earliest_causal_information_pathway_divergence": {
            "timestep": 3,
            "event_id": "E3",
            "control": "PERCEPTION broadcast E3 to SOCIAL, updating SOCIAL to welcome surprises.",
            "experimental": "PERCEPTION did not route public E3 to SOCIAL, so SOCIAL retained E1 as its local source.",
            "downstream": (
                "At timestep 4 the same recommendation and action rules produced different SOCIAL recommendations. "
                "ACTION saw agreement in control and a direct-versus-social conflict in the experimental condition."
            ),
        },
        "pre_binding_language_global": report_for(global_trace, "Q1_PRE_BINDING"),
        "pre_binding_language_differential": report_for(differential_trace, "Q1_PRE_BINDING"),
        "post_binding_language_global": report_for(global_trace, "Q2_POST_BINDING"),
        "post_binding_language_differential": report_for(differential_trace, "Q2_POST_BINDING"),
    }


def scenario_json() -> dict[str, Any]:
    return {
        "name": "birthday_surprise_information_asymmetry",
        "deterministic_seed": 0,
        "events": [scenario_event_to_dict(event) for event in SCENARIO],
        "interviews": [
            {"timestep": 5, "question_id": "Q1_PRE_BINDING"},
            {"timestep": 7, "question_id": "Q2_POST_BINDING"},
        ],
        "temporary_binding": {
            "timestep": 6,
            "links": ["LANGUAGE <-> MEMORY", "LANGUAGE <-> SOCIAL"],
            "duration_timesteps": 1,
        },
    }


def _write_trace_parts(output_dir: Path, trace: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "condition": trace["condition"],
        "objective_ground_truth": trace["objective_ground_truth"],
        "routing_topology": trace["routing_topology"],
        "timesteps": [step["timestep"] for step in trace["timeline"]],
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    for step in trace["timeline"]:
        path = output_dir / f"t{step['timestep']:02d}.json"
        path.write_text(json.dumps(step, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_outputs(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    global_trace = run_condition(Condition.GLOBAL)
    differential_trace = run_condition(Condition.DIFFERENTIAL)
    comparison = compare_traces(global_trace, differential_trace)

    (output_dir / "scenario.json").write_text(
        json.dumps(scenario_json(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "RESULTS.md").write_text(results_markdown(comparison), encoding="utf-8")

    global_bytes = json.dumps(global_trace, sort_keys=True, separators=(",", ":")).encode("utf-8")
    differential_bytes = json.dumps(
        differential_trace, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    (output_dir / "trace_global.json.gz").write_bytes(gzip.compress(global_bytes, mtime=0))
    (output_dir / "trace_differential.json.gz").write_bytes(
        gzip.compress(differential_bytes, mtime=0)
    )

    _write_trace_parts(output_dir / "global", global_trace)
    _write_trace_parts(output_dir / "differential", differential_trace)
    return comparison
