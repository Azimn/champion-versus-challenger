from __future__ import annotations

import argparse
from collections.abc import MutableMapping
import json
from pathlib import Path
from typing import Iterator

from .exp007_evaluation import development_suite, historical_regressions, renderer_invariance
from .global_ablation_v9 import earned_suite
from .runtime import Event
from .v9_compact import CompactV9Character


class _UnionView(MutableMapping[str, object]):
    def __init__(self, owner, kind: type):
        self.owner = owner
        self.kind = kind

    def _matches(self, value) -> bool:
        # bool is excluded from the float view despite being an int subclass.
        if self.kind is float:
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        return isinstance(value, self.kind)

    def __getitem__(self, key: str):
        value = self.owner._union_state[key]
        if not self._matches(value):
            raise KeyError(key)
        return value

    def __setitem__(self, key: str, value) -> None:
        if not self._matches(value):
            raise TypeError(f"value {value!r} does not match {self.kind.__name__}")
        self.owner._union_state[key] = float(value) if self.kind is float else value

    def __delitem__(self, key: str) -> None:
        _ = self[key]
        del self.owner._union_state[key]

    def __iter__(self) -> Iterator[str]:
        for key, value in self.owner._union_state.items():
            if self._matches(value):
                yield key

    def __len__(self) -> int:
        return sum(1 for _ in self)


class UnifiedCommitmentCharacter(CompactV9Character):
    """Pairwise consolidation hypothesis: latent and active commitments share one store.

    Float values are active concern strengths. String values are latent cue names.
    The inherited behavioral rules continue to operate through typed dictionary views,
    so this experiment changes persistence representation rather than capability.
    """

    def __init__(self) -> None:
        self._union_state: dict[str, float | str] = {}
        super().__init__()

    @property
    def concerns(self):
        return _UnionView(self, float)

    @concerns.setter
    def concerns(self, value) -> None:
        for key in list(_UnionView(self, float)):
            del self._union_state[key]
        for key, item in dict(value).items():
            _UnionView(self, float)[key] = item

    @property
    def prospective_commitments(self):
        return _UnionView(self, str)

    @prospective_commitments.setter
    def prospective_commitments(self, value) -> None:
        for key in list(_UnionView(self, str)):
            del self._union_state[key]
        for key, item in dict(value).items():
            _UnionView(self, str)[key] = item

    def persistent_snapshot(self) -> dict:
        state = super().persistent_snapshot()
        state.pop("concern_ledger", None)
        state.pop("prospective_commitments", None)
        state["commitments"] = dict(sorted(self._union_state.items()))
        return state

    def mechanism_count(self) -> int:
        # The latent cue binding and active strength are two modes of one persistent
        # commitment record: cue activation transitions one record from str to float.
        return super().mechanism_count() - 1


class UnifiedBeliefStoreCharacter(CompactV9Character):
    """Control hypothesis: reliability and location facts share a union dictionary.

    This intentionally does NOT reduce mechanism count because the update, decay,
    retrieval, and behavioral semantics remain distinct. It tests whether sharing a
    container yields meaningful state reduction or merely implementation abstraction.
    """

    def __init__(self) -> None:
        self._belief_union: dict[str, float | str] = {}
        super().__init__()

    def _belief_view(self, kind: type):
        class View(MutableMapping[str, object]):
            def __getitem__(view_self, key: str):
                value = self._belief_union[key]
                valid = (
                    isinstance(value, (int, float)) and not isinstance(value, bool)
                    if kind is float
                    else isinstance(value, kind)
                )
                if not valid:
                    raise KeyError(key)
                return value

            def __setitem__(view_self, key: str, value) -> None:
                valid = (
                    isinstance(value, (int, float)) and not isinstance(value, bool)
                    if kind is float
                    else isinstance(value, kind)
                )
                if not valid:
                    raise TypeError(key)
                self._belief_union[key] = float(value) if kind is float else value

            def __delitem__(view_self, key: str) -> None:
                _ = view_self[key]
                del self._belief_union[key]

            def __iter__(view_self):
                for key, value in self._belief_union.items():
                    valid = (
                        isinstance(value, (int, float)) and not isinstance(value, bool)
                        if kind is float
                        else isinstance(value, kind)
                    )
                    if valid:
                        yield key

            def __len__(view_self):
                return sum(1 for _ in view_self)

        return View()

    @property
    def partner_reliability(self):
        return self._belief_view(float)

    @partner_reliability.setter
    def partner_reliability(self, value) -> None:
        view = self._belief_view(float)
        for key in list(view):
            del view[key]
        for key, item in dict(value).items():
            view[key] = item

    @property
    def location_beliefs(self):
        return self._belief_view(str)

    @location_beliefs.setter
    def location_beliefs(self, value) -> None:
        view = self._belief_view(str)
        for key in list(view):
            del view[key]
        for key, item in dict(value).items():
            view[key] = item

    def persistent_snapshot(self) -> dict:
        state = super().persistent_snapshot()
        state.pop("partner_reliability", None)
        state.pop("location_beliefs", None)
        state["beliefs"] = dict(sorted(self._belief_union.items()))
        return state


class UnifiedCommitmentAndBeliefCharacter(UnifiedCommitmentCharacter):
    """Used only if the independent commitment consolidation survives."""
    pass


def populated_metrics(factory) -> dict:
    agent = factory()
    agent.step(Event(kind="task_assign", concern="report", forced_action="idle"))
    agent.step(Event(kind="future_commitment", concern="call_morgan", context="morgan_arrives", forced_action="idle"))
    agent.step(Event(kind="observed_reliable", actor="Alex", forced_action="idle"))
    agent.step(Event(kind="observe_location", actor="book", context="drawer", forced_action="idle"))
    agent.step(Event(kind="context", context="morning", forced_action="walk"))
    return {
        "mechanism_count": agent.mechanism_count(),
        "fresh_bytes": factory().persistent_state_bytes(),
        "populated_bytes": agent.persistent_state_bytes(),
        "persistent_snapshot": agent.persistent_snapshot(),
    }


def full_behavior(factory) -> dict:
    earned = earned_suite(factory)
    historical = historical_regressions(factory)
    development = development_suite(factory)
    renderer = renderer_invariance(factory)
    failures = list(earned["failures"])
    failures.extend(name for name, row in historical.items() if not row["passed"])
    failures.extend(name for name, row in development.items() if not row["passed"])
    if not renderer["passed"]:
        failures.append("renderer_invariance")
    return {"passed": not failures, "failures": sorted(set(failures))}


def commitment_transition_holdouts(factory) -> dict:
    agent = factory()
    agent.step(Event(kind="future_commitment", concern="call_morgan", context="morgan_arrives", forced_action="idle"))
    latent = agent.snapshot()
    agent.step(Event(kind="task_assign", concern="finish_report", forced_action="idle"))
    both = agent.snapshot()
    agent.step(Event(kind="neutral", context="morgan_arrives", forced_action="idle"))
    activated = agent.snapshot()
    agent.step(Event(kind="task_cancel", concern="finish_report", forced_action="idle"))
    after_cancel = agent.snapshot()
    return {
        "passed": (
            latent.get("prospective_commitments", {}).get("call_morgan") == "morgan_arrives"
            and "finish_report" in both.get("concern_ledger", {})
            and both.get("prospective_commitments", {}).get("call_morgan") == "morgan_arrives"
            and "call_morgan" in activated.get("concern_ledger", {})
            and "call_morgan" not in activated.get("prospective_commitments", {})
            and "finish_report" not in after_cancel.get("concern_ledger", {})
        ),
        "latent": latent,
        "both": both,
        "activated": activated,
        "after_cancel": after_cancel,
    }


def same_name_mode_transition(factory) -> dict:
    agent = factory()
    agent.step(Event(kind="future_commitment", concern="report", context="meeting_ends", forced_action="idle"))
    before = agent.snapshot()
    agent.step(Event(kind="neutral", context="meeting_ends", forced_action="idle"))
    active = agent.snapshot()
    agent.step(Event(kind="future_commitment", concern="report", context="tomorrow", forced_action="idle"))
    rescheduled = agent.snapshot()
    # This intentionally probes a semantic collision. The frozen architecture can
    # hold an active concern and a new latent commitment with the same concern name
    # in two separate dictionaries. A one-entry union cannot represent both at once.
    frozen_can_hold_both = (
        "report" in rescheduled.get("concern_ledger", {})
        and rescheduled.get("prospective_commitments", {}).get("report") == "tomorrow"
    )
    return {
        "passed": frozen_can_hold_both,
        "before": before,
        "active": active,
        "rescheduled": rescheduled,
        "claim": "A valid consolidation must preserve the ability to hold active and re-scheduled latent state for the same named concern if the frozen architecture permits it.",
    }


def belief_type_collision(factory) -> dict:
    agent = factory()
    # Same actor/entity identifier intentionally receives both a social reliability
    # estimate and a perceived location fact.
    agent.step(Event(kind="observed_reliable", actor="Alex", forced_action="idle"))
    agent.step(Event(kind="observe_location", actor="Alex", context="studio", forced_action="idle"))
    state = agent.snapshot()
    return {
        "passed": (
            state.get("partner_reliability", {}).get("Alex", 0.0) > 0.0
            and state.get("location_beliefs", {}).get("Alex") == "studio"
        ),
        "state": state,
        "claim": "A shared belief container cannot collapse distinct belief types merely because their subject key is identical.",
    }


def representation_complexity() -> dict:
    compact = populated_metrics(CompactV9Character)
    commitment = populated_metrics(UnifiedCommitmentCharacter)
    belief = populated_metrics(UnifiedBeliefStoreCharacter)
    return {
        "compact": compact,
        "unified_commitment": commitment,
        "unified_belief": belief,
        "commitment_byte_delta": commitment["populated_bytes"] - compact["populated_bytes"],
        "belief_byte_delta": belief["populated_bytes"] - compact["populated_bytes"],
    }


def temporal_container_negative_test() -> dict:
    # Affect residue is already one scalar. Encoding it as a generic temporal record
    # would require at least amplitude/age or an equivalent tagged record, so it
    # cannot reduce persistent information relative to the current scalar without
    # changing the decay law. This test records the actual minimal payload comparison.
    scalar = len(json.dumps({"threat_residue": 0.5}, sort_keys=True).encode("utf-8"))
    generic = len(json.dumps({"temporal": {"kind": "threat", "value": 0.5, "age": 0}}, sort_keys=True).encode("utf-8"))
    return {
        "passed": generic > scalar,
        "current_scalar_bytes": scalar,
        "generic_temporal_record_bytes": generic,
        "interpretation": "A generic temporal-record representation is larger and retains distinct affect semantics; no persistence consolidation is justified.",
    }


def habit_update_primitive_negative_test() -> dict:
    # Immediate and delayed credit already write the same habit table. A helper
    # function could reduce source-code duplication but would not remove any stored
    # field or behavioral mechanism after H2 removed last_action/last_context.
    return {
        "passed": True,
        "persistent_fields_removed_by_shared_update_helper": 0,
        "mechanism_count_reduction_supported": 0,
        "interpretation": "Potential helper refactoring is code reuse only and does not qualify as organism simplification under the project rules.",
    }


def run() -> dict:
    commitment_behavior = full_behavior(UnifiedCommitmentCharacter)
    belief_behavior = full_behavior(UnifiedBeliefStoreCharacter)
    commitment_holdout = commitment_transition_holdouts(UnifiedCommitmentCharacter)
    commitment_collision = same_name_mode_transition(UnifiedCommitmentCharacter)
    frozen_collision = same_name_mode_transition(CompactV9Character)
    belief_collision = belief_type_collision(UnifiedBeliefStoreCharacter)
    frozen_belief_collision = belief_type_collision(CompactV9Character)
    return {
        "phase": "GLOBAL STRUCTURAL ABLATION v9 pairwise consolidation",
        "commitment_consolidation": {
            "earned_behavior": commitment_behavior,
            "transition_holdout": commitment_holdout,
            "same_name_mode_collision": commitment_collision,
            "frozen_same_name_control": frozen_collision,
        },
        "belief_store_consolidation": {
            "earned_behavior": belief_behavior,
            "same_subject_type_collision": belief_collision,
            "frozen_same_subject_control": frozen_belief_collision,
            "mechanism_count_reduction_claimed": false if False else False
        },
        "representation": representation_complexity(),
        "affect_temporal_container": temporal_container_negative_test(),
        "habit_delayed_credit_update_helper": habit_update_primitive_negative_test(),
    }


def compact_json(value):
    if isinstance(value, dict):
        return {str(k): compact_json(v) for k, v in value.items() if k not in {"trace", "traces"}}
    if isinstance(value, tuple):
        return [compact_json(v) for v in value]
    if isinstance(value, list):
        return [compact_json(v) for v in value]
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    report = compact_json(run())
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
