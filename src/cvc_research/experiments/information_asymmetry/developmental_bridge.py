from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .developmental_world import DevelopmentalEvent
from .integrated_runtime import IntegratedConfig, WorldEvent


@dataclass(frozen=True)
class DevelopmentalRuntimeInput:
    """Immutable, per-life input boundary between world generation and PEMA.

    The bridge deliberately contains no actor references and no outcome feedback.
    A life receives only a frozen config and a tuple of transport-level events.
    """

    config: IntegratedConfig
    events: tuple[WorldEvent, ...]


def to_world_event(event: DevelopmentalEvent) -> WorldEvent:
    """Translate generator transport semantics without adding cognition."""
    return WorldEvent(
        event_id=event.event_id,
        cycle=event.epoch,
        channel=event.channel,
        value=event.value,
        salience=event.salience,
        born_tick=event.born_tick,
    )


def build_runtime_input(
    events: Iterable[DevelopmentalEvent],
    *,
    config: IntegratedConfig | None = None,
) -> DevelopmentalRuntimeInput:
    """Create a fresh immutable runtime input for one isolated developmental life."""
    materialized = tuple(events)
    if not materialized:
        raise ValueError("developmental history must not be empty")

    previous_tick = -1
    ids: set[str] = set()
    converted: list[WorldEvent] = []
    for event in materialized:
        if event.event_id in ids:
            raise ValueError(f"duplicate event id: {event.event_id}")
        if event.born_tick < previous_tick:
            raise ValueError("developmental history must be ordered by born_tick")
        ids.add(event.event_id)
        previous_tick = event.born_tick
        converted.append(to_world_event(event))

    runtime_config = config or IntegratedConfig(ticks=max(event.born_tick for event in materialized) + 1)
    if runtime_config.ticks <= max(event.born_tick for event in materialized):
        raise ValueError("runtime config ends before the final developmental event")

    return DevelopmentalRuntimeInput(config=runtime_config, events=tuple(converted))
