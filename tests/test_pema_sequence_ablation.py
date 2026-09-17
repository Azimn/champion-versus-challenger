import unittest

from cvc_research.experiments.information_asymmetry.pema_sequence import run_experiment_2


class PemaSequenceAblationTests(unittest.TestCase):
    def test_uniform_priorities_remove_knowledge_dependent_winner_change(self):
        result = run_experiment_2()
        self.assertTrue(result["uniform_ablation_removed_knowledge_dependent_winner_change"])
        self.assertEqual(
            result["uniform_ablation_global"]["winner_actors"],
            result["uniform_ablation_differential"]["winner_actors"],
        )


if __name__ == "__main__":
    unittest.main()
