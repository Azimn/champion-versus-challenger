from __future__ import annotations

import unittest

from cvc_research.experiments.information_asymmetry.developmental_bridge import build_runtime_input
from cvc_research.experiments.information_asymmetry.developmental_runtime import run_developmental
from cvc_research.experiments.information_asymmetry.developmental_world import WORLD_SEEDS, generate_history


class DevelopmentalRuntimeTests(unittest.TestCase):
    def _run(self, seed: int, epochs: int = 3):
        return run_developmental(
            build_runtime_input(generate_history(seed, epochs=epochs)),
            retain_trace=True,
        )

    def test_generated_history_executes_for_complete_epochs(self) -> None:
        result = self._run(WORLD_SEEDS[0], epochs=3)
        self.assertEqual(result["config"]["ticks"], 120)
        self.assertEqual(len(result["timeline"]), 120)
        self.assertEqual(result["behavior"]["count"], 3)
        self.assertEqual(len(result["behavior"]["choices"]), 3)
        self.assertAlmostEqual(result["resource_conservation"]["error"], 0.0, places=9)

    def test_identical_history_replicates_are_exact(self) -> None:
        history = generate_history(WORLD_SEEDS[0], epochs=4)
        first = run_developmental(build_runtime_input(history), retain_trace=True)
        second = run_developmental(build_runtime_input(history), retain_trace=True)
        self.assertEqual(first, second)

    def test_different_histories_do_not_share_runtime_state(self) -> None:
        first = self._run(WORLD_SEEDS[0], epochs=4)
        second = self._run(WORLD_SEEDS[1], epochs=4)
        self.assertEqual(first["config"]["ticks"], second["config"]["ticks"])
        self.assertAlmostEqual(first["resource_conservation"]["error"], 0.0, places=9)
        self.assertAlmostEqual(second["resource_conservation"]["error"], 0.0, places=9)
        self.assertEqual(first["behavior"]["count"], second["behavior"]["count"])

    def test_actor_snapshots_remain_actor_local(self) -> None:
        result = self._run(WORLD_SEEDS[0], epochs=2)
        for snapshot in result["actor_snapshots"].values():
            self.assertNotIn("actors", snapshot)
            self.assertNotIn("runtime", snapshot)
            self.assertNotIn("peers", snapshot)


if __name__ == "__main__":
    unittest.main()
