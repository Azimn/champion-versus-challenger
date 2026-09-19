from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from .developmental_bridge import DevelopmentalRuntimeInput
from .integrated_runtime import IntegratedPEMARuntime, WorldEvent


class DevelopmentalPEMARuntime(IntegratedPEMARuntime):
    """Existing PEMA runtime driven by a frozen external developmental history.

    Only the world-input boundary changes. Actor implementations, allocator,
    operation costs, feedback, reserve, fatigue, decisions, and message routing
    are inherited unchanged from ``IntegratedPEMARuntime``.
    """

    def __init__(self, runtime_input: DevelopmentalRuntimeInput) -> None:
        super().__init__(runtime_input.config)
        by_tick: dict[int, list[WorldEvent]] = defaultdict(list)
        for event in runtime_input.events:
            by_tick[event.born_tick].append(event)
        self._developmental_events = {
            tick: tuple(sorted(events, key=lambda item: item.event_id))
            for tick, events in by_tick.items()
        }

    def _world_step(self, tick: int) -> None:
        cycle = (tick - 1) // 40
        position = (tick - 1) % 40
        for event in self._developmental_events.get(tick, ()):
            self.perception.observe(event, self.config)
        if position == 6:
            self.action.start_decision(f"D{cycle}", cycle, tick)
        self.concern.set_context_match(position == 15)


def run_developmental(
    runtime_input: DevelopmentalRuntimeInput,
    *,
    retain_trace: bool = True,
) -> dict[str, object]:
    """Run one isolated developmental life from a pre-generated history."""
    return DevelopmentalPEMARuntime(runtime_input).run(retain_trace=retain_trace)
