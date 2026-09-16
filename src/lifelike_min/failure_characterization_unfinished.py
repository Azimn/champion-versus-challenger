from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from .runtime import Event
from .v9_1_compact import V91CompactCharacter


FROZEN_CHAMPION = "2856ec6a32be0347a9243f6eff6faa404a9a0e6c"


class NoConcernDecayDiagnostic(V91CompactCharacter):
    """Diagnostic ablation only: preserve concern ledger across ordinary drift."""

    def _drift(self) -> None:
        concerns_before = dict(self.concerns)
        super()._drift()
        self.concerns = concerns_before


class ConcernFloorDiagnostic(V91CompactCharacter):
    """Diagnostic interaction only: activation can weaken without erasing identity."""

    def _drift(self) -> None:
        concerns_before = dict(self.concerns)
        super()._drift()
        for concern, strength in concerns_before.items():
            if concern not in self.concerns:
                self.concerns[concern] = 0.08
            else:
                self.concerns[concern] = max(self.concerns[concern], 0.08)


def vanish_time(factory, intensity=1.0, limit=200) -> dict:
    agent = factory()
    concern = "finish_portfolio"
    agent.step(Event(kind="task_assign", concern=concern, intensity=intensity, forced_action="idle"))
    initial = float(agent.concerns.get(concern, 0.0))
    trajectory = []
    vanished = None
    for offset in range(1, limit + 1):
        agent.step(Event(kind="neutral", forced_action="idle"))
        value = agent.concerns.get(concern)
        if offset in {1, 10, 25, 50, 73, 74, 75, 100, limit}:
            trajectory.append({"offset": offset, "value": value})
        if value is None:
            vanished = offset
            break
    return {
        "initial": initial,
        "vanished_after": vanished,
        "trajectory": trajectory,
        "final": agent.concerns.get(concern),
    }


def explicit_resolution(factory) -> dict:
    cancelled = factory()
    cancelled.step(Event(kind="task_assign", concern="report", intensity=1.0, forced_action="idle"))
    cancelled.step(Event(kind="task_cancel", concern="report", forced_action="idle"))

    worked = factory()
    worked.step(Event(kind="task_assign", concern="report", intensity=1.0, forced_action="idle"))
    work_rows = []
    for index in range(1, 5):
        action = worked.step(Event(kind="neutral", forced_action="work"))
        work_rows.append({"work_event": index, "action": action, "concern": worked.concerns.get("report")})
        if "report" not in worked.concerns:
            break

    return {
        "cancel_removes": "report" not in cancelled.concerns,
        "work_removes": "report" not in worked.concerns,
        "work_rows": work_rows,
    }


def unrelated_event_types() -> dict:
    event_factories = {
        "neutral": lambda i: Event(kind="neutral", forced_action="idle"),
        "social_support_other": lambda i: Event(kind="support", actor="Alex", forced_action="idle"),
        "location_observation_other": lambda i: Event(kind="observe_location", actor="keys", context="hook", forced_action="idle"),
        "reliability_observation_other": lambda i: Event(kind="observed_reliable", actor="Morgan", forced_action="idle"),
    }
    rows = {}
    for name, event_factory in event_factories.items():
        agent = V91CompactCharacter()
        agent.step(Event(kind="task_assign", concern="finish_portfolio", intensity=1.0, forced_action="idle"))
        vanished = None
        for offset in range(1, 121):
            agent.step(event_factory(offset))
            if "finish_portfolio" not in agent.concerns:
                vanished = offset
                break
        rows[name] = vanished
    return {
        "passed_if_decay_is_event_agnostic": len(set(rows.values())) == 1,
        "vanish_offsets": rows,
    }


def intensity_sweep() -> dict:
    rows = {}
    for intensity in (0.25, 0.5, 0.75, 1.0):
        result = vanish_time(V91CompactCharacter, intensity=intensity, limit=200)
        initial = 0.75 * intensity
        expected = None
        for n in range(1, 201):
            if initial * (0.97 ** n) < 0.08:
                expected = n
                break
        rows[str(intensity)] = {
            "observed": result["vanished_after"],
            "predicted_from_0_97_decay_threshold": expected,
            "matches_rule": result["vanished_after"] == expected,
        }
    return rows


def diagnostic_existing_state_interaction() -> dict:
    frozen = vanish_time(V91CompactCharacter, 1.0, 120)
    no_decay = vanish_time(NoConcernDecayDiagnostic, 1.0, 120)
    floor = vanish_time(ConcernFloorDiagnostic, 1.0, 120)
    floor_resolution = explicit_resolution(ConcernFloorDiagnostic)
    return {
        "frozen": frozen,
        "no_concern_decay": no_decay,
        "activation_floor_without_new_state": floor,
        "floor_still_honors_existing_resolution_signals": floor_resolution,
        "causal_localization": (
            frozen["vanished_after"] is not None
            and no_decay["vanished_after"] is None
            and floor["vanished_after"] is None
            and floor_resolution["cancel_removes"]
            and floor_resolution["work_removes"]
        ),
        "new_persistent_fields_in_diagnostics": 0,
        "interpretation": (
            "Concern identity already exists and explicit cancel/work already provide removal signals. "
            "The reproduced disappearance is caused by treating low activation as nonexistence. "
            "A diagnostic floor shows the selected failure can be prevented without adding state, "
            "while existing explicit resolution still removes the concern. This is not yet a promoted fix."
        ),
    }


def run() -> dict:
    base = vanish_time(V91CompactCharacter, 1.0, 120)
    return {
        "phase": "pre-EXP-009 characterization",
        "champion": "v9.1_compact",
        "champion_commit": FROZEN_CHAMPION,
        "selected_failure": "unfinished_activity_evaporates",
        "production_changes": False,
        "base_reproduction": base,
        "initial_strength_formula": "0.75 * event.intensity",
        "drift_rule": "strength *= 0.97 each tick; delete when strength < 0.08",
        "theoretical_vanish_for_intensity_1": next(n for n in range(1, 200) if 0.75 * (0.97 ** n) < 0.08),
        "intensity_sweep": intensity_sweep(),
        "unrelated_event_types": unrelated_event_types(),
        "existing_resolution_paths": explicit_resolution(V91CompactCharacter),
        "existing_state_interaction_diagnostic": diagnostic_existing_state_interaction(),
        "pre_archaeology_hypothesis": (
            "The ledger already represents unfinished concern identity and has explicit resolution paths. "
            "The selected failure may therefore be an interaction/semantics defect: activation decay "
            "is currently also used as an implicit completion/forgetting signal."
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    report = run()
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
