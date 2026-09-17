import unittest

from cvc_research.experiments.information_asymmetry.integrated_runtime import (
    IntegratedConfig,
    IntegratedPEMARuntime,
    PrivateActor,
    canonical_variants,
    feedback_phase_grid,
    run_integrated,
    stress_suite,
)


class IntegratedPEMARuntimeTests(unittest.TestCase):
    def test_canonical_run_is_deterministic_and_conserves_resource(self):
        config = IntegratedConfig(seed=0, capacity_per_tick=3)
        first = run_integrated(config, retain_trace=False)
        second = run_integrated(config, retain_trace=False)
        self.assertEqual(first, second)
        self.assertAlmostEqual(first["resource_conservation"]["error"], 0.0, places=9)
        self.assertEqual(first["behavior"]["count"], 6)

    def test_actor_instances_do_not_hold_peer_or_runtime_references(self):
        runtime = IntegratedPEMARuntime(IntegratedConfig())
        for actor in runtime.actors.values():
            self.assertNotIn("runtime", vars(actor))
            self.assertNotIn("actors", vars(actor))
            for value in vars(actor).values():
                self.assertFalse(isinstance(value, PrivateActor))

    def test_all_four_links_operate_together_in_canonical_run(self):
        result = run_integrated(IntegratedConfig(seed=0, capacity_per_tick=3), retain_trace=False)
        self.assertGreater(result["information"]["final_epistemic_divergence"], 0.0)
        self.assertGreater(result["channel_capture"]["exploration_evidence"], 1)
        self.assertEqual(result["concern"]["recall_count"], 6)
        self.assertEqual(result["concern"]["memory_recall_count"], 6)
        self.assertEqual(
            result["behavior"]["choices"],
            [
                "ASK_B_FIRST",
                "SURPRISE_B",
                "SURPRISE_B",
                "SURPRISE_B",
                "SURPRISE_B",
                "SURPRISE_B",
            ],
        )

    def test_feedback_ablation_removes_later_behavioral_shift(self):
        variants = canonical_variants(seed=0, capacity=3)
        baseline = variants["baseline"]
        no_feedback = variants["no_feedback"]
        zero_weight = variants["no_epistemic_feedback_weight"]
        self.assertEqual(baseline["behavior"]["surprise_count"], 5)
        self.assertEqual(no_feedback["behavior"]["surprise_count"], 0)
        self.assertEqual(zero_weight["behavior"]["surprise_count"], 0)

    def test_reserve_ablation_eliminates_latent_concern_recall(self):
        variants = canonical_variants(seed=0, capacity=3)
        self.assertEqual(variants["baseline"]["concern"]["recall_count"], 6)
        self.assertEqual(variants["no_reserve"]["concern"]["recall_count"], 0)

    def test_fatigue_counterpressure_reduces_exploration_capture(self):
        variants = canonical_variants(seed=0, capacity=3)
        baseline_share = variants["baseline"]["channel_capture"]["exploration_share"]
        no_fatigue_share = variants["no_fatigue"]["channel_capture"]["exploration_share"]
        self.assertLess(baseline_share, no_fatigue_share)

    def test_global_broadcast_can_be_more_resource_fragile_than_selective_access(self):
        variants = canonical_variants(seed=0, capacity=3)
        selective = variants["baseline"]
        global_access = variants["global_access"]
        self.assertEqual(selective["information"]["resource_missed"], 0)
        self.assertGreater(global_access["information"]["resource_missed"], 0)
        self.assertLess(
            global_access["information"]["final_epistemic_divergence"],
            selective["information"]["final_epistemic_divergence"],
        )

    def test_capacity_sweep_exposes_non_monotonic_behavioral_regimes(self):
        suite = stress_suite(seeds=range(5), capacities=(2, 3, 4, 5))
        aggregate = suite["aggregate"]
        cap2 = aggregate["capacity_2__baseline"]["mean_surprise_count"]
        cap3 = aggregate["capacity_3__baseline"]["mean_surprise_count"]
        cap4 = aggregate["capacity_4__baseline"]["mean_surprise_count"]
        self.assertGreater(cap3, cap2)
        self.assertEqual(cap4, 0.0)
        self.assertNotEqual(cap3, cap4)

    def test_stress_sweep_conserves_resource_across_seeds_and_ablations(self):
        suite = stress_suite(seeds=range(10), capacities=(2, 3, 4, 5))
        self.assertGreater(len(suite["rows"]), 0)
        self.assertTrue(
            all(abs(row["resource_error"]) < 1e-9 for row in suite["rows"])
        )

    def test_canonical_mid_capacity_result_is_seed_robust(self):
        results = [
            run_integrated(
                IntegratedConfig(seed=seed, capacity_per_tick=3),
                retain_trace=False,
            )
            for seed in range(10)
        ]
        self.assertTrue(all(item["information"]["resource_missed"] == 0 for item in results))
        self.assertTrue(all(item["concern"]["recall_count"] == 6 for item in results))
        self.assertTrue(all(item["behavior"]["surprise_count"] == 5 for item in results))

    def test_feedback_phase_grid_contains_null_and_positive_regimes(self):
        grid = feedback_phase_grid(seeds=range(3))
        by_key = {
            (row["evidence_weight"], row["fatigue_weight"]): row
            for row in grid
        }
        self.assertEqual(by_key[(0.0, 0.055)]["mean_surprise_count"], 0.0)
        self.assertGreater(by_key[(0.045, 0.055)]["mean_surprise_count"], 0.0)
        self.assertEqual(by_key[(0.045, 0.055)]["mean_concern_recalls"], 6.0)


if __name__ == "__main__":
    unittest.main()
