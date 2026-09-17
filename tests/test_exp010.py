from __future__ import annotations

import unittest

from lifelike_min.exp010_evaluation import (
    CapacityTwoAblation,
    capacity_tournament,
    causal_ablation,
    long_duration,
    non_dominance,
    reconstruction_states,
    run,
    target_trace,
)
from lifelike_min.exp010_challenger import CapacityThreeConcernCharacter
from lifelike_min.exp009_challenger import UnresolvedConcernPersistenceCharacter


class Exp010MinimumInformationTests(unittest.TestCase):
    def test_frozen_v9_2_reproduces_suppressed_concern_failure(self):
        self.assertFalse(target_trace(UnresolvedConcernPersistenceCharacter)["passed"])

    def test_capacity_three_recovers_retained_non_dominant_concern(self):
        self.assertTrue(target_trace(CapacityThreeConcernCharacter)["passed"])

    def test_capacity_two_causal_ablation_restores_failure(self):
        self.assertFalse(target_trace(CapacityTwoAblation)["passed"])
        self.assertTrue(causal_ablation()["passed"])

    def test_suppressed_concern_is_behaviorally_non_dominant(self):
        self.assertTrue(non_dominance()["passed"])

    def test_long_duration_remains_bounded_and_returnable(self):
        self.assertTrue(long_duration()["passed"])

    def test_capacity_three_is_smallest_tested_success(self):
        result = capacity_tournament()
        self.assertTrue(result["passed"])
        self.assertEqual(result["smallest_successful_capacity"], 3)

    def test_serialization_preserves_suppression_semantics(self):
        self.assertTrue(reconstruction_states()["passed"])

    def test_complete_development_gate(self):
        report = run()
        self.assertEqual(report["failures"], [])
        self.assertTrue(report["developer_gate"])
        self.assertEqual(report["new_counted_mechanisms"], 0)
        self.assertEqual(report["new_persistent_fields"], 0)


if __name__ == "__main__":
    unittest.main()
