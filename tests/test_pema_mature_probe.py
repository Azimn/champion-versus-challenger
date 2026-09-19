import unittest

from cvc_research.experiments.information_asymmetry.developmental_bridge import build_runtime_input
from cvc_research.experiments.information_asymmetry.developmental_runtime import DevelopmentalPEMARuntime
from cvc_research.experiments.information_asymmetry.developmental_world import generate_history
from cvc_research.experiments.information_asymmetry.mature_probe import (
    PROBE_CYCLE_OFFSET,
    PROBE_EPOCHS,
    PROBE_TICKS,
    run_mature_probe,
)
from cvc_research.experiments.information_asymmetry.integrated_runtime import IntegratedConfig


class MatureProbeTests(unittest.TestCase):
    def _small_mature_runtime(self):
        history = generate_history(1103)
        config = IntegratedConfig(ticks=40, seed=1103)
        runtime = DevelopmentalPEMARuntime(build_runtime_input(history[:2], config=config))
        runtime.run(retain_trace=False)
        return runtime

    def test_probe_is_exactly_six_common_epochs(self):
        result = run_mature_probe(self._small_mature_runtime())
        self.assertEqual(len(result["decision_signature"]), PROBE_EPOCHS)
        self.assertEqual(len(result["allocation_shares"]), PROBE_EPOCHS)
        self.assertEqual(len(result["timeline"]), PROBE_TICKS)

    def test_probe_does_not_mutate_mature_runtime(self):
        runtime = self._small_mature_runtime()
        before = (
            runtime.exploration.evidence,
            runtime.routine.evidence,
            runtime.concern.reserve,
            len(runtime.action.behaviors),
            tuple(runtime.social.event_order),
        )
        run_mature_probe(runtime)
        after = (
            runtime.exploration.evidence,
            runtime.routine.evidence,
            runtime.concern.reserve,
            len(runtime.action.behaviors),
            tuple(runtime.social.event_order),
        )
        self.assertEqual(before, after)

    def test_probe_learning_state_is_frozen(self):
        result = run_mature_probe(self._small_mature_runtime())
        self.assertEqual(result["frozen_learning_state"], result["learning_state_after_probe"])

    def test_probe_uses_fresh_held_out_event_namespace(self):
        result = run_mature_probe(self._small_mature_runtime())
        probe_behaviors = result["behaviors"]
        self.assertEqual(
            [row["cycle"] for row in probe_behaviors],
            list(range(PROBE_CYCLE_OFFSET, PROBE_CYCLE_OFFSET + PROBE_EPOCHS)),
        )
        self.assertTrue(all(row["decision_id"].startswith("PROBE_D") for row in probe_behaviors))

    def test_identical_mature_state_replays_identically(self):
        runtime = self._small_mature_runtime()
        first = run_mature_probe(runtime)
        second = run_mature_probe(runtime)
        self.assertEqual(first["decision_signature"], second["decision_signature"])
        self.assertEqual(first["allocation_shares"], second["allocation_shares"])
        self.assertEqual(first["frozen_learning_state"], second["frozen_learning_state"])


if __name__ == "__main__":
    unittest.main()
