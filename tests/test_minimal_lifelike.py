import unittest

from lifelike_min.evaluation import (
    probe_habit_formation,
    probe_history_divergence,
    probe_recovery_inertia,
    probe_social_prediction,
    probe_surface_invariance,
    probe_unfinished_concern,
    reviewer_affect_decay,
    reviewer_concern_cancellation,
    reviewer_habit_context_specificity,
    reviewer_partner_model_specificity_and_reversal,
    reviewer_relationship_specificity,
    run_experiment,
)
from lifelike_min.runtime import Version


class MinimalLifelikeTests(unittest.TestCase):
    def test_relationship_is_causal_for_history_divergence(self):
        self.assertFalse(probe_history_divergence(Version.REACTIVE)["passed"])
        self.assertTrue(probe_history_divergence(Version.RELATIONSHIP)["passed"])
        self.assertTrue(reviewer_relationship_specificity(Version.RELATIONSHIP)["passed"])

    def test_affect_is_causal_for_recovery_inertia(self):
        self.assertFalse(probe_recovery_inertia(Version.RELATIONSHIP)["passed"])
        self.assertTrue(probe_recovery_inertia(Version.AFFECT)["passed"])
        self.assertTrue(reviewer_affect_decay(Version.AFFECT)["passed"])

    def test_concern_is_causal_for_interrupted_goal_return(self):
        self.assertFalse(probe_unfinished_concern(Version.AFFECT)["passed"])
        self.assertTrue(probe_unfinished_concern(Version.CONCERN)["passed"])
        self.assertTrue(reviewer_concern_cancellation(Version.CONCERN)["passed"])

    def test_habit_is_causal_for_experience_shaped_routine(self):
        self.assertFalse(probe_habit_formation(Version.CONCERN)["passed"])
        self.assertTrue(probe_habit_formation(Version.HABIT)["passed"])
        self.assertTrue(reviewer_habit_context_specificity(Version.HABIT)["passed"])

    def test_partner_model_is_causal_for_social_prediction(self):
        self.assertFalse(probe_social_prediction(Version.HABIT)["passed"])
        self.assertTrue(probe_social_prediction(Version.PARTNER_MODEL)["passed"])
        self.assertTrue(
            reviewer_partner_model_specificity_and_reversal(Version.PARTNER_MODEL)["passed"]
        )

    def test_surface_never_changes_cognition(self):
        for version in Version:
            self.assertTrue(probe_surface_invariance(version)["passed"])

    def test_champion_lineage_promotes_only_one_mechanism_per_cycle(self):
        report = run_experiment()
        self.assertEqual(report["final_champion"], Version.PARTNER_MODEL.value)
        self.assertEqual(len(report["cycles"]), 5)
        for cycle in report["cycles"]:
            self.assertEqual(cycle["decision"], "PROMOTE")
            self.assertEqual(cycle["complexity_delta"], 1)
            self.assertTrue(cycle["target_gain"])
            self.assertTrue(cycle["reviewer_failed_to_falsify"])


if __name__ == "__main__":
    unittest.main()
