from __future__ import annotations

from dataclasses import replace
import unittest

from cvc_research.experiments.information_asymmetry.developmental_bridge import (
    build_runtime_input,
    to_world_event,
)
from cvc_research.experiments.information_asymmetry.developmental_world import (
    WORLD_SEEDS,
    generate_history,
)
from cvc_research.experiments.information_asymmetry.integrated_runtime import IntegratedConfig


class DevelopmentalBridgeTests(unittest.TestCase):
    def test_bridge_preserves_transport_semantics_exactly(self) -> None:
        event = generate_history(WORLD_SEEDS[0], epochs=1)[0]
        bridged = to_world_event(event)
        self.assertEqual(bridged.event_id, event.event_id)
        self.assertEqual(bridged.cycle, event.epoch)
        self.assertEqual(bridged.channel, event.channel)
        self.assertEqual(bridged.value, event.value)
        self.assertEqual(bridged.salience, event.salience)
        self.assertEqual(bridged.born_tick, event.born_tick)

    def test_runtime_inputs_are_fresh_and_value_equal_for_identical_history(self) -> None:
        history = generate_history(WORLD_SEEDS[0], epochs=4)
        first = build_runtime_input(history)
        second = build_runtime_input(history)
        self.assertEqual(first, second)
        self.assertIsNot(first, second)
        self.assertIsNot(first.events, second.events)

    def test_bridge_rejects_duplicate_ids(self) -> None:
        history = list(generate_history(WORLD_SEEDS[0], epochs=1))
        history.append(replace(history[-1], born_tick=history[-1].born_tick + 1))
        with self.assertRaisesRegex(ValueError, "duplicate event id"):
            build_runtime_input(history)

    def test_bridge_rejects_out_of_order_history(self) -> None:
        history = generate_history(WORLD_SEEDS[0], epochs=1)
        with self.assertRaisesRegex(ValueError, "ordered by born_tick"):
            build_runtime_input(tuple(reversed(history)))

    def test_bridge_rejects_runtime_that_truncates_history(self) -> None:
        history = generate_history(WORLD_SEEDS[0], epochs=2)
        with self.assertRaisesRegex(ValueError, "ends before"):
            build_runtime_input(history, config=IntegratedConfig(ticks=1))

    def test_different_seed_histories_keep_runtime_config_independent(self) -> None:
        first = build_runtime_input(generate_history(WORLD_SEEDS[0], epochs=3))
        second = build_runtime_input(generate_history(WORLD_SEEDS[1], epochs=3))
        self.assertEqual(first.config, second.config)
        self.assertNotEqual(first.events, second.events)


if __name__ == "__main__":
    unittest.main()
