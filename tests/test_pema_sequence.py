import unittest

from cvc_research.experiments.information_asymmetry.model import Condition
from cvc_research.experiments.information_asymmetry.pema_sequence import (
    run_endogenous_demand_experiment,
    run_epistemic_feedback_experiment,
    run_experiment_2,
    run_experiment_3,
    run_experiment_4,
    run_four_experiment_series,
    run_latent_concern_experiment,
)


class PemaCausalSequenceTests(unittest.TestCase):
    def test_experiment_1_baseline_remains_positive(self):
        series = run_four_experiment_series()
        self.assertTrue(series["causal_chain"]["scarcity_to_access"])

    def test_experiment_2_local_knowledge_changes_operation_priority(self):
        global_run = run_endogenous_demand_experiment(Condition.GLOBAL)
        differential_run = run_endogenous_demand_experiment(Condition.DIFFERENTIAL)
        global_priorities = {
            item["actor_id"]: item["priority"] for item in global_run["proposals"]
        }
        differential_priorities = {
            item["actor_id"]: item["priority"] for item in differential_run["proposals"]
        }
        self.assertEqual(global_priorities["SOCIAL"], 0.95)
        self.assertEqual(differential_priorities["SOCIAL"], 0.60)
        self.assertEqual(global_priorities["MEMORY"], differential_priorities["MEMORY"])

    def test_experiment_2_knowledge_changes_allocator_winner(self):
        result = run_experiment_2()
        self.assertEqual(result["global"]["winner_actors"], ["SOCIAL"])
        self.assertEqual(result["differential"]["winner_actors"], ["MEMORY"])
        self.assertTrue(result["knowledge_changed_allocator_winner"])

    def test_experiment_2_produces_expected_behavior_with_same_selection_rule(self):
        result = run_experiment_2()
        self.assertEqual(result["global"]["final_behavior"], "SURPRISE_B")
        self.assertEqual(result["differential"]["final_behavior"], "ASK_B_FIRST")
        self.assertEqual(
            result["global"]["social_recommendation_delivered"], "SURPRISE_B"
        )
        self.assertTrue(result["differential"]["history_conflict_surfaced"])

    def test_experiment_3_history_changes_future_competitiveness(self):
        result = run_experiment_3()
        self.assertTrue(result["history_changed_future_competitiveness"])
        self.assertEqual(result["history"]["winner_actor"], "CONCERN")
        self.assertEqual(result["no_history_ablation"]["winner_actor"], "DISTRACTOR")

    def test_experiment_3_requires_no_explicit_reminder(self):
        history = run_latent_concern_experiment(with_history=True)
        self.assertFalse(history["explicit_reminder_used"])
        self.assertTrue(all(not row["external_reminder"] for row in history["trace"]))
        self.assertEqual(history["reserve_at_context"], 1.5)
        self.assertEqual(history["recalled_event"], "E1_UNRESOLVED")

    def test_experiment_3_no_history_ablation_does_not_recall(self):
        control = run_latent_concern_experiment(with_history=False)
        self.assertEqual(control["reserve_at_context"], 0.0)
        self.assertIsNone(control["recalled_event"])

    def test_experiment_4_feedback_changes_future_knowledge(self):
        feedback = run_epistemic_feedback_experiment(feedback_enabled=True)
        self.assertTrue(feedback["allocation_changed_knowledge"])
        self.assertEqual(feedback["final_evidence"]["EXPLORATION"], 7)
        self.assertEqual(feedback["wins"]["EXPLORATION"], 6)
        self.assertEqual(feedback["wins"]["ROUTINE"], 0)

    def test_experiment_4_no_feedback_allows_fatigue_to_break_dominance(self):
        control = run_epistemic_feedback_experiment(feedback_enabled=False)
        winners = [row["winner_actor"] for row in control["trace"]]
        self.assertEqual(winners, [
            "EXPLORATION",
            "EXPLORATION",
            "ROUTINE",
            "EXPLORATION",
            "EXPLORATION",
            "ROUTINE",
        ])
        self.assertEqual(control["wins"]["EXPLORATION"], 4)
        self.assertEqual(control["wins"]["ROUTINE"], 2)

    def test_experiment_4_closes_resource_epistemic_feedback_loop(self):
        result = run_experiment_4()
        self.assertTrue(result["feedback_increased_exploration_capture"])
        self.assertTrue(result["closed_loop_observed"])

    def test_full_series_reports_all_four_causal_links(self):
        series = run_four_experiment_series()
        self.assertEqual(
            series["causal_chain"],
            {
                "scarcity_to_access": True,
                "knowledge_to_demand": True,
                "history_to_competitiveness": True,
                "allocation_to_future_knowledge": True,
            },
        )

    def test_sequence_is_deterministic(self):
        self.assertEqual(run_four_experiment_series(), run_four_experiment_series())


if __name__ == "__main__":
    unittest.main()
