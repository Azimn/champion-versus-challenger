import unittest

from cvc_research.experiments.information_asymmetry.developmental_bridge import build_runtime_input
from cvc_research.experiments.information_asymmetry.developmental_runtime import DevelopmentalPEMARuntime
from cvc_research.experiments.information_asymmetry.developmental_world import generate_history
from cvc_research.experiments.information_asymmetry.mature_probe import (
    PROBE_CYCLE_OFFSET,
    PROBE_EPOCHS,
    PROBE_TICKS,
    FrozenProbeConcernActor,
    run_mature_probe,
)
from cvc_research.experiments.information_asymmetry.integrated_runtime import ConcernActor, IntegratedConfig


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

    def test_probe_suppresses_reserve_banking_operations(self):
        result = run_mature_probe(self._small_mature_runtime())
        granted_kinds = [
            grant["kind"]
            for row in result["timeline"]
            for grant in row["granted"]
        ]
        self.assertNotIn("BANK_RESERVE", granted_kinds)

    def test_probe_recall_proposal_preserves_inherited_mature_reserve_priority(self):
        config = IntegratedConfig()
        frozen = FrozenProbeConcernActor()
        inherited = ConcernActor()
        for actor in (frozen, inherited):
            actor.reserve = 1.25
            actor.set_context_match(True)
        self.assertEqual(frozen.propose(16, config), inherited.propose(16, config))
        self.assertEqual(frozen.propose(16, config)[0].kind, "RECALL")

    def test_probe_resource_accounting_conserves_with_mature_reserve_as_carry_in(self):
        result = run_mature_probe(self._small_mature_runtime())
        conservation = result["probe_resource_conservation"]
        self.assertAlmostEqual(conservation["error"], 0.0, places=9)
        self.assertEqual(
            conservation["initial_reserve"],
            result["frozen_learning_state"]["concern_reserve"],
        )
        self.assertEqual(conservation["initial_reserve"], conservation["final_reserve"])

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
