from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .developmental_world import DevelopmentalEvent, EPOCH_TICKS
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
    """Translate generator transport semantics into the inherited runtime vocabulary.

    The integrated Action actor recognizes the existing ``E{cycle}_PUBLIC`` and
    ``E{cycle}_PRIVATE`` transport identifiers. The generator uses ``G`` IDs to
    keep generated histories visibly distinct on disk, so the bridge performs
    this deterministic namespace translation without changing channel, value,
    salience, timing, or actor-local cognition.
    """
    if event.role not in {"PRIVATE", "PUBLIC"}:
        raise ValueError(f"unsupported developmental event role: {event.role}")
    return WorldEvent(
        event_id=f"E{event.epoch}_{event.role}",
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
    source_ids: set[str] = set()
    runtime_ids: set[str] = set()
    converted: list[WorldEvent] = []
    for event in materialized:
        if event.event_id in source_ids:
            raise ValueError(f"duplicate event id: {event.event_id}")
        if event.born_tick < previous_tick:
            raise ValueError("developmental history must be ordered by born_tick")
        source_ids.add(event.event_id)
        previous_tick = event.born_tick
        bridged = to_world_event(event)
        if bridged.event_id in runtime_ids:
            raise ValueError(f"duplicate runtime event id: {bridged.event_id}")
        runtime_ids.add(bridged.event_id)
        converted.append(bridged)

    final_tick = max(event.born_tick for event in materialized)
    full_epoch_duration = (max(event.epoch for event in materialized) + 1) * EPOCH_TICKS
    runtime_config = config or IntegratedConfig(ticks=full_epoch_duration)
    if runtime_config.ticks <= final_tick:
        raise ValueError("runtime config ends before the final developmental event")

    return DevelopmentalRuntimeInput(config=runtime_config, events=tuple(converted))
