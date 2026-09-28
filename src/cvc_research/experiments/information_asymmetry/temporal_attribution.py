from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from .developmental_world import DevelopmentalEvent, EPOCH_TICKS


def temporal_only_history(events: Iterable[DevelopmentalEvent]) -> tuple[DevelopmentalEvent, ...]:
    """Normalize only within-epoch timing/order to the inherited repeated-world schedule.

    Event identity, value, channel, role, salience, and epoch are preserved exactly.
    PRIVATE is placed at epoch offset 1 and PUBLIC at offset 6, matching the inherited
    40-tick repeated-world social ordering. No runtime or cognitive parameter changes.
    """
    source = tuple(events)
    by_epoch: dict[int, list[DevelopmentalEvent]] = {}
    for event in source:
        by_epoch.setdefault(event.epoch, []).append(event)

    normalized: list[DevelopmentalEvent] = []
    for epoch in sorted(by_epoch):
        rows = by_epoch[epoch]
        if len(rows) != 2 or {row.role for row in rows} != {"PRIVATE", "PUBLIC"}:
            raise ValueError(f"epoch {epoch} does not contain exactly PRIVATE and PUBLIC")
        base = epoch * EPOCH_TICKS
        for row in rows:
            born_tick = base + (1 if row.role == "PRIVATE" else 6)
            normalized.append(replace(row, born_tick=born_tick))
    return tuple(sorted(normalized, key=lambda event: (event.born_tick, event.event_id)))


def non_temporal_signature(events: Iterable[DevelopmentalEvent]) -> tuple[tuple[object, ...], ...]:
    """Fields that TEMPORAL_ONLY is forbidden to alter."""
    return tuple(sorted(
        (e.event_id, e.epoch, e.channel, e.value, e.salience, e.role)
        for e in events
    ))
