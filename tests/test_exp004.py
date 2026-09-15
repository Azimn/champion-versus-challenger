import unittest

from lifelike_min.exp004_evaluation import (
    challenger_factory,
    champion_factory,
    probe_multiple_concerns,
    reviewer_bounded_capacity,
    reviewer_duplicate_assignment,
    reviewer_interruption,
    reviewer_reverse_order,
    reviewer_unrelated_cancel,
)
from lifelike_min.exp003_evaluation import probe_unknown_order, regression_suite


class Exp004ConcernLedgerTests(unittest.TestCase):
    def test_frozen_champion_loses_older_unfinished_concern(self):
        self.assertFalse(probe_multiple_concerns(champion_factory)["passed"])

    def test_challenger_preserves_older_unfinished_concern(self):
        self.assertTrue(probe_multiple_concerns(challenger_factory)["passed"])

    def test_assignment_order_does_not_define_which_concern_can_survive(self):
        self.assertTrue(reviewer_reverse_order(challenger_factory)["passed"])

    def test_unrelated_cancel_does_not_clear_other_concerns(self):
        self.assertTrue(reviewer_unrelated_cancel(challenger_factory)["passed"])

    def test_duplicate_assignment_does_not_duplicate_concern(self):
        self.assertTrue(reviewer_duplicate_assignment(challenger_factory)["passed"])

    def test_ledger_is_bounded(self):
        self.assertTrue(reviewer_bounded_capacity(challenger_factory)["passed"])

    def test_interruption_preserves_concern_set(self):
        self.assertTrue(reviewer_interruption(challenger_factory)["passed"])

    def test_prior_behavior_and_exp003_correction_are_preserved(self):
        failures = [
            name
            for name, result in regression_suite(challenger_factory).items()
            if not result["passed"]
        ]
        self.assertEqual(failures, [])
        self.assertTrue(probe_unknown_order(challenger_factory)["passed"])

    def test_one_new_counted_mechanism(self):
        champion = champion_factory()
        challenger = challenger_factory()
        self.assertEqual(challenger.mechanism_count() - champion.mechanism_count(), 1)


if __name__ == "__main__":
    unittest.main()
