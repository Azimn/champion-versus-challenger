from __future__ import annotations

import argparse
import json
from pathlib import Path

from .global_consolidation_v9 import (
    UnifiedCommitmentCharacter,
    UnifiedBeliefStoreCharacter,
    belief_type_collision,
    commitment_transition_holdouts,
    full_behavior,
    habit_update_primitive_negative_test,
    populated_metrics,
    same_name_mode_transition,
    temporal_container_negative_test,
)
from .v9_compact import CompactV9Character


FAILED_INITIAL_PAIRWISE_RUN = {
    "ci_run": 35027013932,
    "classification": "experimental challenger implementation defect",
    "failure": "Unified commitment activation overwrote the latent string with an active float before the inherited code attempted to delete the latent typed view, producing KeyError('call_morgan').",
    "response": "Preserve the failed implementation. Change only the experimental transition order: consume latent state first, then create active state.",
}


class TransitionOrderedUnifiedCommitmentCharacter(UnifiedCommitmentCharacter):
    """Same union-store hypothesis with an atomic latent -> active transition order."""

    def _activate_cue(self, context: str | None) -> None:
        if not context:
            return
        matching = [
            concern
            for concern, cue in self.prospective_commitments.items()
            if cue == context
        ]
        for concern in matching:
            # A one-key union cannot represent latent str and active float at once,
            # so consume the latent mode before creating the active mode.
            del self.prospective_commitments[concern]
            self.concerns[concern] = max(self.concerns.get(concern, 0.0), 0.75)
        if matching:
            self._bound_concerns()
            self._sync_active_concern()


def representation_complexity() -> dict:
    compact = populated_metrics(CompactV9Character)
    commitment = populated_metrics(TransitionOrderedUnifiedCommitmentCharacter)
    belief = populated_metrics(UnifiedBeliefStoreCharacter)
    return {
        "compact": compact,
        "unified_commitment": commitment,
        "unified_belief": belief,
        "commitment_byte_delta": commitment["populated_bytes"] - compact["populated_bytes"],
        "belief_byte_delta": belief["populated_bytes"] - compact["populated_bytes"],
    }


def run() -> dict:
    commitment_behavior = full_behavior(TransitionOrderedUnifiedCommitmentCharacter)
    commitment_transition = commitment_transition_holdouts(TransitionOrderedUnifiedCommitmentCharacter)
    commitment_collision = same_name_mode_transition(TransitionOrderedUnifiedCommitmentCharacter)
    frozen_commitment_collision = same_name_mode_transition(CompactV9Character)

    belief_behavior = full_behavior(UnifiedBeliefStoreCharacter)
    belief_collision = belief_type_collision(UnifiedBeliefStoreCharacter)
    frozen_belief_collision = belief_type_collision(CompactV9Character)

    return {
        "phase": "GLOBAL STRUCTURAL ABLATION v9 pairwise consolidation, corrected experimental transition",
        "initial_failed_run_preserved": FAILED_INITIAL_PAIRWISE_RUN,
        "commitment_consolidation": {
            "earned_behavior": commitment_behavior,
            "transition_holdout": commitment_transition,
            "same_name_active_plus_future_holdout": commitment_collision,
            "frozen_same_name_control": frozen_commitment_collision,
            "decision": (
                "REJECT" if not commitment_collision["passed"] else "REVIEW"
            ),
            "interpretation": "Passing the old suite is insufficient if the union cannot represent an active concern and a newly scheduled future instance of that same concern simultaneously."
        },
        "belief_store_consolidation": {
            "earned_behavior": belief_behavior,
            "same_subject_two_belief_types_holdout": belief_collision,
            "frozen_same_subject_control": frozen_belief_collision,
            "mechanism_count_reduction_claimed": False,
            "decision": (
                "REJECT" if not belief_collision["passed"] else "REVIEW"
            ),
            "interpretation": "Reliability and location beliefs have different semantics and may coexist for the same subject identifier. A value-type union that overwrites one with the other is not a valid substrate."
        },
        "representation": representation_complexity(),
        "affect_temporal_container": {
            **temporal_container_negative_test(),
            "decision": "REJECT_GENERIC_CONSOLIDATION",
        },
        "habit_delayed_credit_update_helper": {
            **habit_update_primitive_negative_test(),
            "decision": "CODE_REFACTOR_ONLY",
        },
    }


def compact_json(value):
    if isinstance(value, dict):
        return {
            str(key): compact_json(item)
            for key, item in value.items()
            if key not in {"trace", "traces"}
        }
    if isinstance(value, tuple):
        return [compact_json(item) for item in value]
    if isinstance(value, list):
        return [compact_json(item) for item in value]
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
