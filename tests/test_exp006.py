import unittest

from lifelike_min.exp003_evaluation import probe_unknown_order, regression_suite
from lifelike_min.exp004_evaluation import probe_multiple_concerns
from lifelike_min.exp005_evaluation import probe_event_cued_commitment
from lifelike_min.exp006_evaluation import (
    challenger_factory,
    champion_factory,
    probe_epistemic_history,
    reviewer_entity_specificity,
    reviewer_hidden_change_not_omniscient,
    reviewer_observed_revision,
    reviewer_perception_order,
    reviewer_unobserved_entity_has_no_fabricated_belief,
    scope_delayed_credit,
)


class Exp006SubjectiveFactTests(unittest.TestCase):
    def test_frozen_champion_collapses_different_perceived_histories(self):
        self.assertFalse(probe_epistemic_history(champion_factory)["passed"])

    def test_challenger_uses_last_perceived_location(self):
        self.assertTrue(probe_epistemic_history(challenger_factory)["passed"])

    def test_hidden_change_does_not_create_omniscience(self):
        self.assertTrue(reviewer_hidden_change_not_omniscient(challenger_factory)["passed"])

    def test_direct_reobservation_revises_belief(self):
        self.assertTrue(reviewer_observed_revision(challenger_factory)["passed"])
        self.assertTrue(reviewer_perception_order(challenger_factory)["passed"])

    def test_beliefs_are_entity_specific(self):
        self.assertTrue(reviewer_entity_specificity(challenger_factory)["passed"])

    def test_unobserved_entity_gets_no_fabricated_belief(self):
        self.assertTrue(
            reviewer_unobserved_entity_has_no_fabricated_belief(challenger_factory)["passed"]
        )

    def test_all_prior_behavior_is_preserved(self):
        failures = [
            name
            for name, result in regression_suite(challenger_factory).items()
            if not result["passed"]
        ]
        self.assertEqual(failures, [])
        self.assertTrue(probe_unknown_order(challenger_factory)["passed"])
        self.assertTrue(probe_multiple_concerns(challenger_factory)["passed"])
        self.assertTrue(probe_event_cued_commitment(challenger_factory)["passed"])

    def test_delayed_credit_remains_unsolved_scope_control(self):
        self.assertFalse(scope_delayed_credit(challenger_factory)["delayed_credit_solved"])

    def test_one_new_counted_mechanism(self):
        champion = champion_factory()
        challenger = challenger_factory()
        self.assertEqual(challenger.mechanism_count() - champion.mechanism_count(), 1)


if __name__ == "__main__":
    unittest.main()
