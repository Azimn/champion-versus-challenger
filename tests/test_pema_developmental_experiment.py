from __future__ import annotations

import unittest

from cvc_research.experiments.information_asymmetry.developmental_experiment import (
    BLOCK_COUNT,
    BLOCK_TICKS,
    GENERATED_CONDITIONS,
    condition_config,
    summarize_blocks,
)
from cvc_research.experiments.information_asymmetry.developmental_world import (
    DEVELOPMENT_TICKS,
    WORLD_SEEDS,
    generate_history,
    serialize_history,
)


class DevelopmentalExperimentTests(unittest.TestCase):
    def test_condition_matrix_changes_only_preregistered_mechanism(self) -> None:
        seed = WORLD_SEEDS[0]
        baseline = condition_config(seed, "GENERATIVE_DIFFERENTIAL")
        no_feedback = condition_config(seed, "GENERATIVE_NO_FEEDBACK")
        no_reserve = condition_config(seed, "GENERATIVE_NO_RESERVE")
        global_access = condition_config(seed, "GENERATIVE_GLOBAL")
        repeated = condition_config(seed, "REPEATED_DIFFERENTIAL")

        self.assertEqual(baseline.ticks, DEVELOPMENT_TICKS)
        self.assertEqual(repeated, baseline)
        self.assertEqual(no_feedback, baseline.__class__(**{**baseline.__dict__, "feedback_enabled": False}))
        self.assertEqual(no_reserve, baseline.__class__(**{**baseline.__dict__, "reserve_enabled": False}))
        self.assertEqual(global_access, baseline.__class__(**{**baseline.__dict__, "access": "global"}))

    def test_all_generated_conditions_reuse_byte_identical_history(self) -> None:
        seed = WORLD_SEEDS[0]
        expected = serialize_history(generate_history(seed))
        for condition in GENERATED_CONDITIONS:
            self.assertEqual(serialize_history(generate_history(seed)), expected, condition)

    def test_unregistered_seed_and_condition_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "not preregistered"):
            condition_config(999, "GENERATIVE_DIFFERENTIAL")
        with self.assertRaisesRegex(ValueError, "unknown developmental condition"):
            condition_config(WORLD_SEEDS[0], "GENERATIVE_UNKNOWN")

    def test_block_summary_has_six_fixed_nonoverlapping_windows(self) -> None:
        timeline = []
        for tick in range(1, DEVELOPMENT_TICKS + 1):
            timeline.append(
                {
                    "tick": tick,
                    "granted": [
                        {"actor_id": "EXPLORATION"},
                        {"actor_id": "ROUTINE"},
                        {"actor_id": "CONCERN"},
                    ],
                    "exploration_evidence": tick,
                    "routine_evidence": tick + 1,
                    "concern_reserve": 0.5,
                    "concern_recalls": tick // 40,
                }
            )
        blocks = summarize_blocks(timeline)
        self.assertEqual(len(blocks), BLOCK_COUNT)
        self.assertEqual(blocks[0]["start_tick"], 1)
        self.assertEqual(blocks[-1]["end_tick"], DEVELOPMENT_TICKS)
        for index, block in enumerate(blocks):
            self.assertEqual(block["start_tick"], index * BLOCK_TICKS + 1)
            self.assertEqual(block["end_tick"], (index + 1) * BLOCK_TICKS)
            self.assertEqual(block["allocation_counts"]["EXPLORATION"], BLOCK_TICKS)
            self.assertEqual(block["allocation_counts"]["ROUTINE"], BLOCK_TICKS)
            self.assertEqual(block["allocation_counts"]["CONCERN"], BLOCK_TICKS)
            self.assertEqual(block["exploration_share"], 0.5)


if __name__ == "__main__":
    unittest.main()
