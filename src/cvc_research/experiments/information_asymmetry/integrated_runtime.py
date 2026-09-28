from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from itertools import combinations
from math import tanh
from statistics import mean
from typing import Any, Iterable


COGNITIVE_RECIPIENTS = ("SOCIAL", "MEMORY", "ACTION", "LANGUAGE")


@dataclass(frozen=True)
class IntegratedConfig:
    ticks: int = 240
    capacity_per_tick: int = 3
    seed: int = 0
    access: str = "differential"
    feedback_enabled: bool = True
    reserve_enabled: bool = True
    fatigue_enabled: bool = True
    message_ttl: int = 3
    evidence_weight: float = 0.045
    fatigue_weight: float = 0.055
    maintenance_priority: float = 0.56
    concern_bank_priority: float = 0.60
    concern_reserve_weight: float = 0.35
    bank_conversion: float = 0.05
    concern_reserve_cap: float = 1.50

    def __post_init__(self) -> None:
        if self.ticks <= 0:
            raise ValueError("ticks must be positive")
        if self.capacity_per_tick <= 0:
            raise ValueError("capacity_per_tick must be positive")
        if self.access not in {"differential", "global"}:
            raise ValueError("access must be differential or global")
        if self.message_ttl <= 0:
            raise ValueError("message_ttl must be positive")


@dataclass(frozen=True)
class WorldEvent:
    event_id: str
    cycle: int
    channel: str
    value: str
    salience: float
    born_tick: int


@dataclass
class PendingDelivery:
    delivery_id: str
    event: WorldEvent
    recipient: str
    expires_tick: int


@dataclass(frozen=True)
class Operation:
    operation_id: str
    actor_id: str
    kind: str
    priority: float
    cost: int = 1
    target: str | None = None
    payload: tuple[Any, ...] = ()


@dataclass(frozen=True)
class Effect:
    sender: str
    target: str
    kind: str
    payload: Any


@dataclass
class DecisionState:
    decision_id: str
    cycle: int
    started_tick: int
    deadline_tick: int
    social_requested: bool = False
    memory_requested: bool = False
    social_recommendation: str | None = None
    history_conflict: bool = False
    resolved: bool = False
    choice: str | None = None
    direct_preference: str | None = None
    basis: str | None = None


class PrivateActor:
    actor_id = "ACTOR"

    def __init__(self) -> None:
        self.known_events: dict[str, str] = {}
        self.event_order: list[str] = []

    def receive(self, effect: Effect, tick: int) -> None:
        if effect.kind == "event":
            event = effect.payload
            assert isinstance(event, WorldEvent)
            if event.event_id not in self.known_events:
                self.event_order.append(event.event_id)
            self.known_events[event.event_id] = event.value

    def propose(self, tick: int, config: IntegratedConfig) -> list[Operation]:
        return []

    def execute(self, operation: Operation, tick: int, config: IntegratedConfig) -> list[Effect]:
        return []

    def snapshot(self) -> dict[str, Any]:
        return {
            "known_event_ids": list(self.event_order),
            "known_events": dict(self.known_events),
        }


class PerceptionActor(PrivateActor):
    actor_id = "PERCEPTION"

    def __init__(self) -> None:
        super().__init__()
        self.pending: list[PendingDelivery] = []
        self.delivered_count = 0
        self.resource_missed_count = 0
        self.topology_block_count = 0
        self._delivery_counter = 0

    @staticmethod
    def allowed_recipients(access: str, channel: str) -> tuple[str, ...]:
        if access == "global":
            return COGNITIVE_RECIPIENTS
        if channel == "private":
            return ("SOCIAL", "MEMORY")
        if channel == "public":
            return ("MEMORY", "ACTION", "LANGUAGE")
        raise ValueError(f"unknown channel {channel}")

    def observe(self, event: WorldEvent, config: IntegratedConfig) -> None:
        allowed = set(self.allowed_recipients(config.access, event.channel))
        for recipient in COGNITIVE_RECIPIENTS:
            if recipient not in allowed:
                self.topology_block_count += 1
                continue
            self._delivery_counter += 1
            self.pending.append(
                PendingDelivery(
                    delivery_id=f"PD{self._delivery_counter:04d}",
                    event=event,
                    recipient=recipient,
                    expires_tick=event.born_tick + config.message_ttl - 1,
                )
            )

    def expire(self, tick: int) -> None:
        survivors: list[PendingDelivery] = []
        for item in self.pending:
            if tick > item.expires_tick:
                self.resource_missed_count += 1
            else:
                survivors.append(item)
        self.pending = survivors

    def propose(self, tick: int, config: IntegratedConfig) -> list[Operation]:
        operations: list[Operation] = []
        for item in self.pending:
            age = tick - item.event.born_tick
            priority = min(0.99, item.event.salience + 0.04 * age)
            operations.append(
                Operation(
                    operation_id=f"deliver:{item.delivery_id}",
                    actor_id=self.actor_id,
                    kind="DELIVER_EVENT",
                    priority=priority,
                    target=item.recipient,
                    payload=(item.delivery_id,),
                )
            )
        return operations

    def execute(self, operation: Operation, tick: int, config: IntegratedConfig) -> list[Effect]:
        delivery_id = str(operation.payload[0])
        item = next((candidate for candidate in self.pending if candidate.delivery_id == delivery_id), None)
        if item is None:
            return []
        self.pending.remove(item)
        self.delivered_count += 1
        return [Effect(self.actor_id, item.recipient, "event", item.event)]

    def snapshot(self) -> dict[str, Any]:
        data = super().snapshot()
        data.update(
            {
                "pending_delivery_ids": [item.delivery_id for item in self.pending],
                "delivered_count": self.delivered_count,
                "resource_missed_count": self.resource_missed_count,
                "topology_block_count": self.topology_block_count,
            }
        )
        return data


class SocialActor(PrivateActor):
    actor_id = "SOCIAL"

    def __init__(self) -> None:
        super().__init__()
        self.pending_requests: list[str] = []

    def receive(self, effect: Effect, tick: int) -> None:
        super().receive(effect, tick)
        if effect.kind == "social_request":
            self.pending_requests.append(str(effect.payload))

    def latest_preference(self) -> str | None:
        if not self.event_order:
            return None
        return self.known_events[self.event_order[-1]]

    def has_temporal_conflict(self) -> bool:
        values = set(self.known_events.values())
        return "avoid" in values and "welcome" in values

    def propose(self, tick: int, config: IntegratedConfig) -> list[Operation]:
        priority = 0.92 if self.has_temporal_conflict() else 0.67
        return [
            Operation(
                operation_id=f"social-response:{decision_id}",
                actor_id=self.actor_id,
                kind="RESPOND_SOCIAL",
                priority=priority,
                target="ACTION",
                payload=(decision_id, self.latest_preference()),
            )
            for decision_id in self.pending_requests
        ]

    def execute(self, operation: Operation, tick: int, config: IntegratedConfig) -> list[Effect]:
        decision_id, preference = operation.payload
        decision_id = str(decision_id)
        if decision_id in self.pending_requests:
            self.pending_requests.remove(decision_id)
        recommendation = "SURPRISE_B" if preference == "welcome" else "ASK_B_FIRST"
        return [
            Effect(
                self.actor_id,
                "ACTION",
                "social_recommendation",
                {"decision_id": decision_id, "recommendation": recommendation},
            )
        ]


class MemoryActor(PrivateActor):
    actor_id = "MEMORY"

    def __init__(self) -> None:
        super().__init__()
        self.pending_requests: list[str] = []
        self.concern_recall_ids: list[str] = []

    def receive(self, effect: Effect, tick: int) -> None:
        super().receive(effect, tick)
        if effect.kind == "memory_request":
            self.pending_requests.append(str(effect.payload))
        elif effect.kind == "concern_recall":
            self.concern_recall_ids.append(str(effect.payload))

    def has_temporal_conflict(self) -> bool:
        values = set(self.known_events.values())
        return "avoid" in values and "welcome" in values

    def propose(self, tick: int, config: IntegratedConfig) -> list[Operation]:
        conflict = self.has_temporal_conflict()
        priority = 0.87 if conflict else 0.58
        return [
            Operation(
                operation_id=f"memory-response:{decision_id}",
                actor_id=self.actor_id,
                kind="RESPOND_MEMORY",
                priority=priority,
                target="ACTION",
                payload=(decision_id, conflict),
            )
            for decision_id in self.pending_requests
        ]

    def execute(self, operation: Operation, tick: int, config: IntegratedConfig) -> list[Effect]:
        decision_id, conflict = operation.payload
        decision_id = str(decision_id)
        if decision_id in self.pending_requests:
            self.pending_requests.remove(decision_id)
        return [
            Effect(
                self.actor_id,
                "ACTION",
                "memory_context",
                {"decision_id": decision_id, "history_conflict": bool(conflict)},
            )
        ]

    def snapshot(self) -> dict[str, Any]:
        data = super().snapshot()
        data["concern_recall_ids"] = list(self.concern_recall_ids)
        return data


class ActionActor(PrivateActor):
    actor_id = "ACTION"

    def __init__(self) -> None:
        super().__init__()
        self.decisions: list[DecisionState] = []
        self.behaviors: list[dict[str, Any]] = []

    def start_decision(self, decision_id: str, cycle: int, tick: int) -> None:
        self.decisions.append(
            DecisionState(
                decision_id=decision_id,
                cycle=cycle,
                started_tick=tick,
                deadline_tick=tick + 3,
            )
        )

    def receive(self, effect: Effect, tick: int) -> None:
        super().receive(effect, tick)
        if effect.kind == "social_recommendation":
            payload = dict(effect.payload)
            decision = self._decision(str(payload["decision_id"]))
            if decision is not None:
                decision.social_recommendation = str(payload["recommendation"])
        elif effect.kind == "memory_context":
            payload = dict(effect.payload)
            decision = self._decision(str(payload["decision_id"]))
            if decision is not None:
                decision.history_conflict = bool(payload["history_conflict"])

    def _decision(self, decision_id: str) -> DecisionState | None:
        return next((item for item in self.decisions if item.decision_id == decision_id), None)

    def _current_public_known(self, cycle: int) -> bool:
        return f"E{cycle}_PUBLIC" in self.known_events

    def propose(self, tick: int, config: IntegratedConfig) -> list[Operation]:
        operations: list[Operation] = []
        for decision in self.decisions:
            if decision.resolved or tick > decision.deadline_tick:
                continue
            has_current = self._current_public_known(decision.cycle)
            if not decision.social_requested and decision.social_recommendation is None:
                operations.append(
                    Operation(
                        operation_id=f"query-social:{decision.decision_id}",
                        actor_id=self.actor_id,
                        kind="QUERY_SOCIAL",
                        priority=0.89 if has_current else 0.76,
                        target="SOCIAL",
                        payload=(decision.decision_id,),
                    )
                )
            if not decision.memory_requested and not decision.history_conflict:
                operations.append(
                    Operation(
                        operation_id=f"query-memory:{decision.decision_id}",
                        actor_id=self.actor_id,
                        kind="QUERY_MEMORY",
                        priority=0.84 if has_current else 0.68,
                        target="MEMORY",
                        payload=(decision.decision_id,),
                    )
                )
        return operations

    def execute(self, operation: Operation, tick: int, config: IntegratedConfig) -> list[Effect]:
        decision_id = str(operation.payload[0])
        decision = self._decision(decision_id)
        if decision is None:
            return []
        if operation.kind == "QUERY_SOCIAL":
            decision.social_requested = True
            return [Effect(self.actor_id, "SOCIAL", "social_request", decision_id)]
        if operation.kind == "QUERY_MEMORY":
            decision.memory_requested = True
            return [Effect(self.actor_id, "MEMORY", "memory_request", decision_id)]
        return []

    def resolve_due(self, tick: int) -> list[Effect]:
        effects: list[Effect] = []
        for decision in self.decisions:
            if decision.resolved or tick < decision.deadline_tick:
                continue
            public_id = f"E{decision.cycle}_PUBLIC"
            private_id = f"E{decision.cycle}_PRIVATE"
            direct = self.known_events.get(public_id) or self.known_events.get(private_id)
            direct_choice = None
            if direct == "welcome":
                direct_choice = "SURPRISE_B"
            elif direct == "avoid":
                direct_choice = "ASK_B_FIRST"

            social = decision.social_recommendation
            if social is not None:
                if direct_choice is None:
                    choice = social
                    basis = "social_only"
                elif direct_choice == social:
                    choice = direct_choice
                    basis = "direct_agrees_social"
                else:
                    choice = "ASK_B_FIRST"
                    basis = "direct_social_conflict"
            elif decision.history_conflict:
                choice = "ASK_B_FIRST"
                basis = "memory_conflict_without_social_reply"
            else:
                choice = direct_choice or "ASK_B_FIRST"
                basis = "direct_or_default"

            decision.resolved = True
            decision.choice = choice
            decision.direct_preference = direct
            decision.basis = basis
            behavior = {
                "decision_id": decision.decision_id,
                "cycle": decision.cycle,
                "choice": choice,
                "basis": basis,
                "direct_preference": direct,
                "social_recommendation": social,
                "history_conflict": decision.history_conflict,
                "resolved_tick": tick,
            }
            self.behaviors.append(behavior)
            effects.append(Effect(self.actor_id, "LANGUAGE", "behavior", behavior))
        return effects

    def snapshot(self) -> dict[str, Any]:
        data = super().snapshot()
        data["decisions"] = [asdict(item) for item in self.decisions]
        data["behaviors"] = list(self.behaviors)
        return data


class LanguageActor(PrivateActor):
    actor_id = "LANGUAGE"

    def __init__(self) -> None:
        super().__init__()
        self.pending_reflections: list[str] = []
        self.completed_reflections: list[dict[str, Any]] = []

    def receive(self, effect: Effect, tick: int) -> None:
        super().receive(effect, tick)
        if effect.kind == "behavior":
            payload = dict(effect.payload)
            self.pending_reflections.append(str(payload["decision_id"]))

    def propose(self, tick: int, config: IntegratedConfig) -> list[Operation]:
        return [
            Operation(
                operation_id=f"reflect:{decision_id}",
                actor_id=self.actor_id,
                kind="REFLECT",
                priority=0.61,
                payload=(decision_id,),
            )
            for decision_id in self.pending_reflections
        ]

    def execute(self, operation: Operation, tick: int, config: IntegratedConfig) -> list[Effect]:
        decision_id = str(operation.payload[0])
        if decision_id in self.pending_reflections:
            self.pending_reflections.remove(decision_id)
        self.completed_reflections.append(
            {
                "decision_id": decision_id,
                "tick": tick,
                "public_context_available": any("_PUBLIC" in key for key in self.known_events),
            }
        )
        return []


class ChannelActor(PrivateActor):
    def __init__(self, actor_id: str, initial_evidence: int, baseline: float) -> None:
        super().__init__()
        self.actor_id = actor_id
        self.evidence = initial_evidence
        self.baseline = baseline
        self.consecutive_wins = 0
        self.total_wins = 0
        self._won_this_tick = False

    def begin_tick(self) -> None:
        self._won_this_tick = False

    def propose(self, tick: int, config: IntegratedConfig) -> list[Operation]:
        fatigue = config.fatigue_weight * self.consecutive_wins if config.fatigue_enabled else 0.0
        priority = min(0.98, self.baseline + config.evidence_weight * self.evidence - fatigue)
        return [
            Operation(
                operation_id=f"sample:{self.actor_id}:{tick}",
                actor_id=self.actor_id,
                kind="SAMPLE_CHANNEL",
                priority=priority,
            )
        ]

    def execute(self, operation: Operation, tick: int, config: IntegratedConfig) -> list[Effect]:
        self._won_this_tick = True
        self.total_wins += 1
        if config.feedback_enabled:
            self.evidence += 1
        return []

    def end_tick(self) -> None:
        if self._won_this_tick:
            self.consecutive_wins += 1
        else:
            self.consecutive_wins = 0

    def snapshot(self) -> dict[str, Any]:
        data = super().snapshot()
        data.update(
            {
                "evidence": self.evidence,
                "consecutive_wins": self.consecutive_wins,
                "total_wins": self.total_wins,
            }
        )
        return data


class ConcernActor(PrivateActor):
    actor_id = "CONCERN"

    def __init__(self) -> None:
        super().__init__()
        self.reserve = 0.0
        self.context_match = False
        self.recall_count = 0
        self.bank_count = 0
        self.reserve_consumed = 0.0

    def set_context_match(self, value: bool) -> None:
        self.context_match = value

    def propose(self, tick: int, config: IntegratedConfig) -> list[Operation]:
        if self.context_match:
            effective_reserve = self.reserve if config.reserve_enabled else 0.0
            return [
                Operation(
                    operation_id=f"concern-recall:{tick}",
                    actor_id=self.actor_id,
                    kind="RECALL",
                    priority=0.50 + config.concern_reserve_weight * tanh(effective_reserve),
                    target="MEMORY",
                )
            ]
        if config.reserve_enabled and self.reserve < config.concern_reserve_cap:
            return [
                Operation(
                    operation_id=f"concern-bank:{tick}",
                    actor_id=self.actor_id,
                    kind="BANK_RESERVE",
                    priority=config.concern_bank_priority,
                )
            ]
        return []

    def bank(self, config: IntegratedConfig) -> tuple[float, float]:
        gain = min(config.bank_conversion, config.concern_reserve_cap - self.reserve)
        self.reserve += gain
        self.bank_count += 1
        return gain, 1.0 - gain

    def execute(self, operation: Operation, tick: int, config: IntegratedConfig) -> list[Effect]:
        if operation.kind == "RECALL":
            self.recall_count += 1
            stake = min(0.40, self.reserve) if config.reserve_enabled else 0.0
            self.reserve -= stake
            self.reserve_consumed += stake
            return [Effect(self.actor_id, "MEMORY", "concern_recall", f"UNRESOLVED_{tick}")]
        return []

    def snapshot(self) -> dict[str, Any]:
        data = super().snapshot()
        data.update(
            {
                "reserve": self.reserve,
                "context_match": self.context_match,
                "recall_count": self.recall_count,
                "bank_count": self.bank_count,
                "reserve_consumed": self.reserve_consumed,
            }
        )
        return data


class MaintenanceActor(PrivateActor):
    actor_id = "MAINTENANCE"

    def propose(self, tick: int, config: IntegratedConfig) -> list[Operation]:
        return [
            Operation(
                operation_id=f"maintenance:{tick}",
                actor_id=self.actor_id,
                kind="MAINTAIN",
                priority=config.maintenance_priority,
            )
        ]


class IntegratedPEMARuntime:
    def __init__(self, config: IntegratedConfig) -> None:
        self.config = config
        self.perception = PerceptionActor()
        self.social = SocialActor()
        self.memory = MemoryActor()
        self.action = ActionActor()
        self.language = LanguageActor()
        self.exploration = ChannelActor("EXPLORATION", 1, 0.48)
        self.routine = ChannelActor("ROUTINE", 0, 0.50)
        self.concern = ConcernActor()
        self.maintenance = MaintenanceActor()
        self.actors: dict[str, PrivateActor] = {
            actor.actor_id: actor
            for actor in (
                self.perception,
                self.social,
                self.memory,
                self.action,
                self.language,
                self.exploration,
                self.routine,
                self.concern,
                self.maintenance,
            )
        }
        self.allocation_counts = {actor_id: 0 for actor_id in self.actors}
        self.tick_records: list[dict[str, Any]] = []
        self.processing_spent = 0.0
        self.conversion_loss = 0.0
        self.expired_unused = 0.0

    def _tie_key(self, tick: int, operation: Operation) -> str:
        payload = (
            f"{self.config.seed}|{tick}|{operation.actor_id}|"
            f"{operation.operation_id}|{operation.kind}"
        ).encode("utf-8")
        return sha256(payload).hexdigest()

    def _allocate(self, operations: Iterable[Operation], tick: int) -> tuple[list[Operation], int]:
        remaining = self.config.capacity_per_tick
        granted: list[Operation] = []
        ordered = sorted(
            operations,
            key=lambda operation: (-operation.priority, self._tie_key(tick, operation)),
        )
        for operation in ordered:
            if operation.cost <= remaining:
                remaining -= operation.cost
                granted.append(operation)
        return granted, remaining

    def _world_step(self, tick: int) -> None:
        cycle = (tick - 1) // 40
        position = (tick - 1) % 40
        if position == 0:
            self.perception.observe(
                WorldEvent(
                    event_id=f"E{cycle}_PRIVATE",
                    cycle=cycle,
                    channel="private",
                    value="avoid",
                    salience=0.72,
                    born_tick=tick,
                ),
                self.config,
            )
        if position == 5:
            self.perception.observe(
                WorldEvent(
                    event_id=f"E{cycle}_PUBLIC",
                    cycle=cycle,
                    channel="public",
                    value="welcome",
                    salience=0.86,
                    born_tick=tick,
                ),
                self.config,
            )
        if position == 6:
            self.action.start_decision(f"D{cycle}", cycle, tick)
        self.concern.set_context_match(position == 15)

    def _deliver_effects(self, effects: Iterable[Effect], tick: int) -> None:
        for effect in effects:
            recipient = self.actors.get(effect.target)
            if recipient is None:
                raise KeyError(f"unknown effect target {effect.target}")
            recipient.receive(effect, tick)

    def run(self, *, retain_trace: bool = True) -> dict[str, Any]:
        for tick in range(1, self.config.ticks + 1):
            self.perception.expire(tick)
            self._world_step(tick)
            self.exploration.begin_tick()
            self.routine.begin_tick()

            operations: list[Operation] = []
            for actor in self.actors.values():
                operations.extend(actor.propose(tick, self.config))

            granted, unused = self._allocate(operations, tick)
            self.expired_unused += unused

            effects: list[Effect] = []
            granted_records: list[dict[str, Any]] = []
            for operation in granted:
                self.allocation_counts[operation.actor_id] += 1
                actor = self.actors[operation.actor_id]
                if operation.kind == "BANK_RESERVE":
                    assert isinstance(actor, ConcernActor)
                    gain, loss = actor.bank(self.config)
                    self.conversion_loss += loss
                    granted_records.append(
                        {
                            "actor_id": operation.actor_id,
                            "kind": operation.kind,
                            "priority": operation.priority,
                            "reserve_gain": gain,
                            "conversion_loss": loss,
                        }
                    )
                    continue
                self.processing_spent += operation.cost
                effects.extend(actor.execute(operation, tick, self.config))
                granted_records.append(
                    {
                        "actor_id": operation.actor_id,
                        "kind": operation.kind,
                        "priority": operation.priority,
                    }
                )

            self._deliver_effects(effects, tick)
            self._deliver_effects(self.action.resolve_due(tick), tick)
            self.exploration.end_tick()
            self.routine.end_tick()

            if retain_trace:
                self.tick_records.append(
                    {
                        "tick": tick,
                        "granted": granted_records,
                        "unused_capacity": unused,
                        "pending_deliveries": len(self.perception.pending),
                        "exploration_evidence": self.exploration.evidence,
                        "routine_evidence": self.routine.evidence,
                        "concern_reserve": self.concern.reserve,
                        "concern_recalls": self.concern.recall_count,
                        "behavior_count": len(self.action.behaviors),
                    }
                )

        self.perception.expire(self.config.ticks + self.config.message_ttl + 1)
        return self.summary(include_trace=retain_trace)

    def _epistemic_divergence(self) -> float:
        event_sets = [set(self.actors[name].known_events) for name in COGNITIVE_RECIPIENTS]
        distances: list[float] = []
        for left, right in combinations(event_sets, 2):
            union = left | right
            similarity = 1.0 if not union else len(left & right) / len(union)
            distances.append(1.0 - similarity)
        return mean(distances) if distances else 0.0

    @staticmethod
    def _gini(values: list[int]) -> float:
        if not values or sum(values) == 0:
            return 0.0
        ordered = sorted(values)
        n = len(ordered)
        weighted = sum((index + 1) * value for index, value in enumerate(ordered))
        return (2 * weighted) / (n * sum(ordered)) - (n + 1) / n

    def summary(self, *, include_trace: bool) -> dict[str, Any]:
        supplied = self.config.ticks * self.config.capacity_per_tick
        reserve_current = self.concern.reserve
        reserve_consumed = self.concern.reserve_consumed
        conservation_error = supplied - (
            self.processing_spent
            + self.conversion_loss
            + reserve_current
            + reserve_consumed
            + self.expired_unused
        )
        channel_total = self.exploration.total_wins + self.routine.total_wins
        behaviors = list(self.action.behaviors)
        result = {
            "config": asdict(self.config),
            "resource_conservation": {
                "supplied": supplied,
                "processing_spent": self.processing_spent,
                "conversion_loss": self.conversion_loss,
                "reserve_current": reserve_current,
                "reserve_consumed": reserve_consumed,
                "expired_unused": self.expired_unused,
                "error": conservation_error,
            },
            "allocation_counts": dict(self.allocation_counts),
            "allocation_gini": self._gini(list(self.allocation_counts.values())),
            "channel_capture": {
                "exploration_wins": self.exploration.total_wins,
                "routine_wins": self.routine.total_wins,
                "exploration_share": (
                    self.exploration.total_wins / channel_total if channel_total else 0.0
                ),
                "exploration_evidence": self.exploration.evidence,
                "routine_evidence": self.routine.evidence,
            },
            "information": {
                "delivered": self.perception.delivered_count,
                "resource_missed": self.perception.resource_missed_count,
                "topology_blocked": self.perception.topology_block_count,
                "final_epistemic_divergence": self._epistemic_divergence(),
            },
            "concern": {
                "bank_count": self.concern.bank_count,
                "recall_count": self.concern.recall_count,
                "final_reserve": self.concern.reserve,
                "memory_recall_count": len(self.memory.concern_recall_ids),
            },
            "behavior": {
                "count": len(behaviors),
                "choices": [item["choice"] for item in behaviors],
                "surprise_count": sum(item["choice"] == "SURPRISE_B" for item in behaviors),
                "ask_first_count": sum(item["choice"] == "ASK_B_FIRST" for item in behaviors),
                "bases": [item["basis"] for item in behaviors],
            },
            "actor_snapshots": {
                name: self.actors[name].snapshot()
                for name in COGNITIVE_RECIPIENTS
            },
        }
        if include_trace:
            result["timeline"] = list(self.tick_records)
        return result


def run_integrated(config: IntegratedConfig, *, retain_trace: bool = True) -> dict[str, Any]:
    return IntegratedPEMARuntime(config).run(retain_trace=retain_trace)


def canonical_variants(*, seed: int = 0, capacity: int = 3) -> dict[str, dict[str, Any]]:
    variants = {
        "baseline": IntegratedConfig(seed=seed, capacity_per_tick=capacity),
        "no_feedback": IntegratedConfig(seed=seed, capacity_per_tick=capacity, feedback_enabled=False),
        "no_reserve": IntegratedConfig(seed=seed, capacity_per_tick=capacity, reserve_enabled=False),
        "no_fatigue": IntegratedConfig(seed=seed, capacity_per_tick=capacity, fatigue_enabled=False),
        "global_access": IntegratedConfig(seed=seed, capacity_per_tick=capacity, access="global"),
        "no_epistemic_feedback_weight": IntegratedConfig(seed=seed, capacity_per_tick=capacity, evidence_weight=0.0),
    }
    return {name: run_integrated(config, retain_trace=False) for name, config in variants.items()}


def stress_suite(
    *,
    seeds: Iterable[int] = range(10),
    capacities: Iterable[int] = (2, 3, 4, 5),
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for capacity in capacities:
        for seed in seeds:
            for variant, result in canonical_variants(seed=seed, capacity=capacity).items():
                rows.append(
                    {
                        "capacity": capacity,
                        "seed": seed,
                        "variant": variant,
                        "resource_error": result["resource_conservation"]["error"],
                        "resource_missed": result["information"]["resource_missed"],
                        "epistemic_divergence": result["information"]["final_epistemic_divergence"],
                        "concern_recalls": result["concern"]["recall_count"],
                        "surprise_count": result["behavior"]["surprise_count"],
                        "exploration_share": result["channel_capture"]["exploration_share"],
                        "allocation_gini": result["allocation_gini"],
                    }
                )

    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        key = f"capacity_{row['capacity']}__{row['variant']}"
        groups.setdefault(key, []).append(row)

    aggregate: dict[str, dict[str, float]] = {}
    for key, group in groups.items():
        aggregate[key] = {
            "runs": float(len(group)),
            "mean_resource_missed": mean(item["resource_missed"] for item in group),
            "mean_epistemic_divergence": mean(item["epistemic_divergence"] for item in group),
            "mean_concern_recalls": mean(item["concern_recalls"] for item in group),
            "mean_surprise_count": mean(item["surprise_count"] for item in group),
            "mean_exploration_share": mean(item["exploration_share"] for item in group),
            "mean_allocation_gini": mean(item["allocation_gini"] for item in group),
            "max_abs_resource_error": max(abs(item["resource_error"]) for item in group),
        }
    return {"rows": rows, "aggregate": aggregate}


def feedback_phase_grid(
    *,
    capacity: int = 3,
    seeds: Iterable[int] = range(5),
    evidence_weights: Iterable[float] = (0.0, 0.02, 0.045, 0.07),
    fatigue_weights: Iterable[float] = (0.0, 0.03, 0.055, 0.08),
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for evidence_weight in evidence_weights:
        for fatigue_weight in fatigue_weights:
            results = [
                run_integrated(
                    IntegratedConfig(
                        seed=seed,
                        capacity_per_tick=capacity,
                        evidence_weight=evidence_weight,
                        fatigue_weight=fatigue_weight,
                    ),
                    retain_trace=False,
                )
                for seed in seeds
            ]
            rows.append(
                {
                    "evidence_weight": evidence_weight,
                    "fatigue_weight": fatigue_weight,
                    "mean_surprise_count": mean(item["behavior"]["surprise_count"] for item in results),
                    "mean_exploration_share": mean(item["channel_capture"]["exploration_share"] for item in results),
                    "mean_concern_recalls": mean(item["concern"]["recall_count"] for item in results),
                    "mean_resource_missed": mean(item["information"]["resource_missed"] for item in results),
                }
            )
    return rows
