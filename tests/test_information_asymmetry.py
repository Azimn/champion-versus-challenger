import json
import tempfile
import unittest
from pathlib import Path

from cvc_research.experiments.information_asymmetry import (
    ActionProcessor,
    Condition,
    ExperimentRunner,
    LanguageProcessor,
    MemoryProcessor,
    Processor,
    SocialProcessor,
    compare_traces,
    final_behavior,
    run_condition,
    write_outputs,
)


class PersistentInformationAsymmetryTests(unittest.TestCase):
    def setUp(self):
        self.global_trace = run_condition(Condition.GLOBAL)
        self.diff_trace = run_condition(Condition.DIFFERENTIAL)

    def _step(self, trace, timestep):
        return next(step for step in trace["timeline"] if step["timestep"] == timestep)

    def test_global_broadcast_synchronizes_relevant_event_access(self):
        step3 = self._step(self.global_trace, 3)
        for name in ("SOCIAL", "MEMORY", "ACTION", "LANGUAGE"):
            self.assertIn("E3", step3["processors"][name]["local_state"]["known_event_ids"])

    def test_differential_routing_preserves_private_histories(self):
        step3 = self._step(self.diff_trace, 3)
        self.assertNotIn("E3", step3["processors"]["SOCIAL"]["local_state"]["known_event_ids"])
        self.assertIn("E3", step3["processors"]["ACTION"]["local_state"]["known_event_ids"])
        self.assertIn("E3", step3["processors"]["LANGUAGE"]["local_state"]["known_event_ids"])
        self.assertIn("E3", step3["processors"]["MEMORY"]["local_state"]["known_event_ids"])

    def test_neutral_behavior_is_identical_despite_knowledge_asymmetry(self):
        global_step2 = self._step(self.global_trace, 2)["selected_behavior"]
        diff_step2 = self._step(self.diff_trace, 2)["selected_behavior"]
        self.assertEqual(global_step2["choice"], "GREET_B")
        self.assertEqual(global_step2, diff_step2)

    def test_final_behavior_diverges_under_same_action_rule(self):
        self.assertEqual(final_behavior(self.global_trace), "SURPRISE_B")
        self.assertEqual(final_behavior(self.diff_trace), "ASK_B_FIRST")
        global_action = self._step(self.global_trace, 4)["processors"]["ACTION"]["local_state"]
        diff_action = self._step(self.diff_trace, 4)["processors"]["ACTION"]["local_state"]
        self.assertEqual(global_action["latest_direct_b_preference"], "welcome")
        self.assertEqual(diff_action["latest_direct_b_preference"], "welcome")
        self.assertEqual(global_action["latest_social_recommendation"], "SURPRISE_B")
        self.assertEqual(diff_action["latest_social_recommendation"], "ASK_B_FIRST")

    def test_language_is_not_given_hidden_social_evidence_before_binding(self):
        step5 = self._step(self.diff_trace, 5)
        language = step5["processors"]["LANGUAGE"]["local_state"]
        self.assertNotIn("E1", language["known_event_ids"])
        self.assertEqual(language["received_social_recommendations"], [])
        report = step5["linguistic_report"]
        self.assertIn("cannot identify the missing social basis", report["explanation"])

    def test_temporary_binding_transmits_context_without_state_merging(self):
        step7 = self._step(self.diff_trace, 7)
        language = step7["processors"]["LANGUAGE"]["local_state"]
        self.assertIn("E1", language["known_event_ids"])
        self.assertIn("E3", language["known_event_ids"])
        self.assertEqual(language["bound_social_context"]["b_surprise_preference"], "avoid")
        report = step7["linguistic_report"]
        self.assertIn("temporary coordination link", report["explanation"])

    def test_blocked_route_is_explicitly_logged(self):
        blocked = [
            record
            for step in self.diff_trace["timeline"]
            for record in step["messages"]
            if record["timestep"] == 3
            and record["sender"] == "PERCEPTION"
            and record["receiver"] == "SOCIAL"
            and record["kind"] == "workspace_event"
        ]
        self.assertEqual(len(blocked), 1)
        self.assertFalse(blocked[0]["succeeded"])

    def test_processors_do_not_hold_references_to_peer_processors_router_or_runner(self):
        runner = ExperimentRunner(Condition.DIFFERENTIAL)
        processor_types = (Processor, SocialProcessor, MemoryProcessor, ActionProcessor, LanguageProcessor)
        for processor in runner.processors_for_researcher.values():
            for value in vars(processor).values():
                self.assertFalse(isinstance(value, processor_types))
                self.assertIsNot(value, runner.router)
                self.assertIsNot(value, runner)

    def test_comparison_identifies_minimum_causal_route(self):
        comparison = compare_traces(self.global_trace, self.diff_trace)
        cause = comparison["earliest_causal_information_pathway_divergence"]
        self.assertEqual(cause["timestep"], 3)
        self.assertEqual(cause["event_id"], "E3")
        self.assertTrue(comparison["neutral_behavior_identical_despite_asymmetry"])
        self.assertTrue(comparison["final_behavior_diverged"])

    def test_generated_artifacts_are_reproducible(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            first = Path(temp_dir) / "first"
            second = Path(temp_dir) / "second"
            write_outputs(first)
            write_outputs(second)
            names = {
                "scenario.json",
                "trace_global.json",
                "trace_differential.json",
                "RESULTS.md",
            }
            self.assertEqual({path.name for path in first.iterdir()}, names)
            for name in names:
                self.assertEqual((first / name).read_bytes(), (second / name).read_bytes())
            json.loads((first / "trace_global.json").read_text())
            json.loads((first / "trace_differential.json").read_text())


if __name__ == "__main__":
    unittest.main()
