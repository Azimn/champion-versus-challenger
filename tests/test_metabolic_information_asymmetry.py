import unittest

from cvc_research.experiments.information_asymmetry.metabolic import (
    SCARCE_CAPACITY,
    ResourceRegime,
)
from cvc_research.experiments.information_asymmetry.metabolic_runner import (
    matrix_analysis,
    run_canonical_matrix,
    run_capacity_sweep,
    run_metabolic_condition,
    summarize_metabolic_trace,
)
from cvc_research.experiments.information_asymmetry.model import Condition
from cvc_research.experiments.information_asymmetry.runner import final_behavior


class MetabolicInformationAsymmetryTests(unittest.TestCase):
    def setUp(self):
        self.global_abundant = run_metabolic_condition(
            Condition.GLOBAL, ResourceRegime.ABUNDANT
        )
        self.global_scarce = run_metabolic_condition(
            Condition.GLOBAL, ResourceRegime.SCARCE
        )
        self.diff_abundant = run_metabolic_condition(
            Condition.DIFFERENTIAL, ResourceRegime.ABUNDANT
        )
        self.diff_scarce = run_metabolic_condition(
            Condition.DIFFERENTIAL, ResourceRegime.SCARCE
        )

    @staticmethod
    def _step(trace, timestep):
        return next(step for step in trace["timeline"] if step["timestep"] == timestep)

    def test_abundant_conditions_reproduce_original_behavioral_result(self):
        self.assertEqual(final_behavior(self.global_abundant), "SURPRISE_B")
        self.assertEqual(final_behavior(self.diff_abundant), "ASK_B_FIRST")

    def test_scarcity_changes_global_broadcast_behavior(self):
        self.assertEqual(final_behavior(self.global_scarce), "ASK_B_FIRST")
        self.assertNotEqual(
            final_behavior(self.global_abundant), final_behavior(self.global_scarce)
        )

    def test_scarcity_does_not_change_differential_behavior(self):
        self.assertEqual(final_behavior(self.diff_abundant), "ASK_B_FIRST")
        self.assertEqual(final_behavior(self.diff_scarce), "ASK_B_FIRST")

    def test_scarce_global_e3_broadcast_fails_atomically(self):
        step3 = self._step(self.global_scarce, 3)
        e3 = [
            record
            for record in step3["messages"]
            if record["sender"] == "PERCEPTION"
            and record["kind"] == "workspace_event"
            and record["payload"].get("event_id") == "E3"
        ]
        self.assertEqual(len(e3), 4)
        self.assertTrue(all(record["topology_allowed"] for record in e3))
        self.assertTrue(all(not record["succeeded"] for record in e3))
        self.assertTrue(all(record["failure_stage"] == "send_budget" for record in e3))

    def test_scarce_global_creates_information_asymmetry_from_resource_failure(self):
        step3 = self._step(self.global_scarce, 3)
        for actor in ("SOCIAL", "ACTION", "LANGUAGE"):
            self.assertNotIn(
                "E3", step3["processors"][actor]["local_state"]["known_event_ids"]
            )
        self.assertEqual(
            step3["processors"]["PERCEPTION"]["resource_balance"],
            SCARCE_CAPACITY - 4,
        )

    def test_scarce_differential_preserves_its_permitted_e3_routes(self):
        step3 = self._step(self.diff_scarce, 3)
        self.assertNotIn(
            "E3", step3["processors"]["SOCIAL"]["local_state"]["known_event_ids"]
        )
        for actor in ("MEMORY", "ACTION", "LANGUAGE"):
            self.assertIn(
                "E3", step3["processors"][actor]["local_state"]["known_event_ids"]
            )
        self.assertEqual(
            step3["processors"]["PERCEPTION"]["resource_balance"],
            SCARCE_CAPACITY - 5,
        )

    def test_resource_conservation_holds_in_all_four_conditions(self):
        for trace in (
            self.global_abundant,
            self.global_scarce,
            self.diff_abundant,
            self.diff_scarce,
        ):
            self.assertEqual(trace["resource_conservation"]["error"], 0)
            self.assertEqual(
                trace["resource_conservation"]["initial_total"],
                trace["resource_conservation"]["current_total"]
                + trace["resource_conservation"]["consumed_total"],
            )

    def test_manipulation_is_not_only_a_language_reporting_effect(self):
        global_abundant_action = self._step(self.global_abundant, 4)["selected_behavior"]
        global_scarce_action = self._step(self.global_scarce, 4)["selected_behavior"]
        self.assertEqual(global_abundant_action["choice"], "SURPRISE_B")
        self.assertEqual(global_scarce_action["choice"], "ASK_B_FIRST")

    def test_matrix_analysis_reports_access_by_resource_interaction(self):
        matrix = run_canonical_matrix()
        analysis = matrix_analysis(matrix)
        self.assertTrue(analysis["scarcity_changes_global_behavior"])
        self.assertFalse(analysis["scarcity_changes_differential_behavior"])
        self.assertTrue(analysis["scarce_global_created_resource_asymmetry"])
        self.assertTrue(analysis["scarce_differential_preserved_permitted_e3_routes"])

    def test_capacity_sweep_exposes_expected_topology_cost_thresholds(self):
        rows = run_capacity_sweep(range(4, 9))
        by_key = {(row["capacity"], row["access_condition"]): row for row in rows}

        # Differential routing needs 2 units for E1 and 3 more for E3.
        self.assertGreater(
            by_key[(4, Condition.DIFFERENTIAL.value)]["e3_resource_blocks"], 0
        )
        self.assertEqual(
            by_key[(5, Condition.DIFFERENTIAL.value)]["e3_resource_blocks"], 0
        )

        # Global broadcast needs 4 units for E1 and 4 more for E3.
        self.assertGreater(by_key[(7, Condition.GLOBAL.value)]["e3_resource_blocks"], 0)
        self.assertEqual(by_key[(8, Condition.GLOBAL.value)]["e3_resource_blocks"], 0)
        self.assertEqual(
            by_key[(8, Condition.GLOBAL.value)]["final_behavior"], "SURPRISE_B"
        )


if __name__ == "__main__":
    unittest.main()
