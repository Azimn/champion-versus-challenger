from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import random
from typing import Iterable


WORLD_SEEDS = (1103, 2207, 3301, 4409, 5501, 6607, 7703, 8807, 9901, 11113)
EPOCH_TICKS = 40
DEVELOPMENT_TICKS = 24_000
EPOCH_COUNT = DEVELOPMENT_TICKS // EPOCH_TICKS


@dataclass(frozen=True)
class DevelopmentalEvent:
    event_id: str
    epoch: int
    born_tick: int
    channel: str
    value: str
    salience: float
    role: str


def _epoch_events(epoch: int, rng: random.Random) -> list[DevelopmentalEvent]:
    """Build one fixed-opportunity epoch, then deterministically permute its history.

    Every epoch has one private and one public social observation. Their values are
    drawn as a balanced pair, so histories vary in ordering and informational
    relation without varying event count, channel count, resource supply, or
    evaluation opportunity. Generation is completed before runtime execution.
    """
    relation = rng.choice(("supportive", "conflicting", "repairing", "neutral"))
    if relation == "supportive":
        private_value, public_value = "welcome", "welcome"
    elif relation == "conflicting":
        private_value, public_value = "avoid", "welcome"
    elif relation == "repairing":
        private_value, public_value = "welcome", "avoid"
    else:
        private_value, public_value = "avoid", "avoid"

    templates = [
        ("PRIVATE", "private", private_value, 0.72),
        ("PUBLIC", "public", public_value, 0.86),
    ]
    rng.shuffle(templates)
    positions = [0, 5]
    rng.shuffle(positions)
    base = epoch * EPOCH_TICKS
    return [
        DevelopmentalEvent(
            event_id=f"G{epoch}_{role}",
            epoch=epoch,
            born_tick=base + position + 1,
            channel=channel,
            value=value,
            salience=salience,
            role=role,
        )
        for position, (role, channel, value, salience) in zip(positions, templates)
    ]


def generate_history(seed: int, *, epochs: int = EPOCH_COUNT) -> tuple[DevelopmentalEvent, ...]:
    if seed not in WORLD_SEEDS:
        raise ValueError(f"seed must be preregistered: {seed}")
    if epochs <= 0:
        raise ValueError("epochs must be positive")
    rng = random.Random(seed)
    events: list[DevelopmentalEvent] = []
    for epoch in range(epochs):
        events.extend(_epoch_events(epoch, rng))
    return tuple(sorted(events, key=lambda event: (event.born_tick, event.event_id)))


def serialize_history(events: Iterable[DevelopmentalEvent]) -> str:
    payload = [asdict(event) for event in events]
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def deserialize_history(payload: str) -> tuple[DevelopmentalEvent, ...]:
    raw = json.loads(payload)
    events = tuple(DevelopmentalEvent(**item) for item in raw)
    return tuple(sorted(events, key=lambda event: (event.born_tick, event.event_id)))


def opportunity_signature(events: Iterable[DevelopmentalEvent]) -> tuple[tuple[int, str, str], ...]:
    """Return only preregistered opportunity structure, excluding history values/order."""
    counts: dict[tuple[int, str, str], int] = {}
    for event in events:
        key = (event.epoch, event.channel, event.role)
        counts[key] = counts.get(key, 0) + 1
    return tuple(sorted((*key, count) for key, count in counts.items()))
