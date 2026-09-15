import unittest

from lifelike_min.exp003_evaluation import probe_unknown_order, regression_suite
from lifelike_min.exp004_evaluation import probe_multiple_concerns
from lifelike_min.exp005_evaluation import (
    challenger_factory,
    champion_factory,
    probe_event_cued_commitment,
    reviewer_bounded_store,
    reviewer_cancel_before_cue,
    reviewer_multiple_future_commitments,
    reviewer_one_shot_activation,
    reviewer_wrong_cues,
)


class Exp005ProspectiveCueTests(unittest.TestCase):
    def test_frozen_champion_cannot_retain_and_activate_future_cue(self):
        self.assertFalse(probe_event_cued_commitment(champion_factory)["passed"])

    def test_challenger_retains_and_activates_future_cue(self):
        self.assertTrue(probe_event_cued_commitment(challenger_factory)["passed"])

    def test_wrong_cues_do_not_activate_commitment(self):
        self.assertTrue(reviewer_wrong_cues(challenger_factory)["passed"])

    def test_cancel_before_cue_removes_commitment(self):
        self.assertTrue(reviewer_cancel_before_cue(challenger_factory)["passed"])

    def test_multiple_future_commitments_remain_specific(self):
        self.assertTrue(reviewer_multiple_future_commitments(challenger_factory)["passed"])

    def test_activation_is_one_shot(self):
        self.assertTrue(reviewer_one_shot_activation(challenger_factory)["passed"])

    def test_prospective_store_is_bounded(self):
        self.assertTrue(reviewer_bounded_store(challenger_factory)["passed"])

    def test_all_prior_behavior_is_preserved(self):
        failures = [
            name
            for name, result in regression_suite(challenger_factory).items()
            if not result["passed"]
        ]
        self.assertEqual(failures, [])
        self.assertTrue(probe_unknown_order(challenger_factory)["passed"])
        self.assertTrue(probe_multiple_concerns(challenger_factory)["passed"])

    def test_one_new_counted_mechanism(self):
        champion = champion_factory()
        challenger = challenger_factory()
        self.assertEqual(challenger.mechanism_count() - champion.mechanism_count(), 1)


if __name__ == "__main__":
    unittest.main()
