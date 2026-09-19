from __future__ import annotations

from dataclasses import replace

import pytest

from cvc_research.experiments.information_asymmetry.developmental_bridge import (
    build_runtime_input,
    to_world_event,
)
from cvc_research.experiments.information_asymmetry.developmental_world import (
    WORLD_SEEDS,
    generate_history,
)
from cvc_research.experiments.information_asymmetry.integrated_runtime import IntegratedConfig


def test_bridge_preserves_transport_semantics_exactly() -> None:
    event = generate_history(WORLD_SEEDS[0], epochs=1)[0]
    bridged = to_world_event(event)
    assert bridged.event_id == event.event_id
    assert bridged.cycle == event.epoch
    assert bridged.channel == event.channel
    assert bridged.value == event.value
    assert bridged.salience == event.salience
    assert bridged.born_tick == event.born_tick


def test_runtime_inputs_are_fresh_and_value_equal_for_identical_history() -> None:
    history = generate_history(WORLD_SEEDS[0], epochs=4)
    first = build_runtime_input(history)
    second = build_runtime_input(history)
    assert first == second
    assert first is not second
    assert first.events is not second.events


def test_bridge_rejects_duplicate_ids() -> None:
    history = list(generate_history(WORLD_SEEDS[0], epochs=1))
    history.append(replace(history[-1], born_tick=history[-1].born_tick + 1))
    with pytest.raises(ValueError, match="duplicate event id"):
        build_runtime_input(history)


def test_bridge_rejects_out_of_order_history() -> None:
    history = generate_history(WORLD_SEEDS[0], epochs=1)
    with pytest.raises(ValueError, match="ordered by born_tick"):
        build_runtime_input(tuple(reversed(history)))


def test_bridge_rejects_runtime_that_truncates_history() -> None:
    history = generate_history(WORLD_SEEDS[0], epochs=2)
    with pytest.raises(ValueError, match="ends before"):
        build_runtime_input(history, config=IntegratedConfig(ticks=1))


def test_different_seed_histories_keep_runtime_config_independent() -> None:
    first = build_runtime_input(generate_history(WORLD_SEEDS[0], epochs=3))
    second = build_runtime_input(generate_history(WORLD_SEEDS[1], epochs=3))
    assert first.config == second.config
    assert first.events != second.events
