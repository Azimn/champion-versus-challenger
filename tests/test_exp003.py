import unittest

from lifelike_min.exp003_evaluation import (
    champion_factory,
    challenger_factory,
    probe_history_divergence,
    probe_recovery_inertia,
    probe_unfinished_concern,
    probe_habit_formation,
    probe_social_prediction,
    probe_surface_invariance,
    probe_unknown_order,
    reviewer_near_neutral_evidence,
    reviewer_person_specificity,
    reviewer_reversal,
)


class Exp003UncertaintyPolicyTests(unittest.TestCase):
    def test_frozen_v5_exposes_action_order_artifact(self):
        result = probe_unknown_order(champion_factory)
        self.assertFalse(result["passed"])
        self.assertEqual(result["actions"], ["verify:Blake", "delegate:Blake"])

    def test_challenger_fixes_unknown_partner_order_dependence(self):
        result = probe_unknown_order(challenger_factory)
        self.assertTrue(result["passed"])
        self.assertEqual(result["actions"], ["verify:Blake", "verify:Blake"])

    def test_previously_earned_behavior_is_preserved(self):
        probes = (
            probe_history_divergence,
            probe_recovery_inertia,
            probe_unfinished_concern,
            probe_habit_formation,
            probe_social_prediction,
            probe_surface_invariance,
        )
        failures = [probe.__name__ for probe in probes if not probe(challenger_factory)["passed"]]
        self.assertEqual(failures, [])

    def test_reviewer_counterexamples(self):
        reviewers = (
            probe_social_prediction,
            reviewer_reversal,
            reviewer_near_neutral_evidence,
            reviewer_person_specificity,
        )
        failures = [review.__name__ for review in reviewers if not review(challenger_factory)["passed"]]
        self.assertEqual(failures, [])

    def test_challenger_adds_no_persistent_state_or_counted_mechanism(self):
        champion = champion_factory()
        challenger = challenger_factory()
        self.assertEqual(champion.mechanism_count(), challenger.mechanism_count())
        self.assertEqual(champion.snapshot(), challenger.snapshot())
        self.assertEqual(champion.persistent_state_bytes(), challenger.persistent_state_bytes())


if __name__ == "__main__":
    unittest.main()
