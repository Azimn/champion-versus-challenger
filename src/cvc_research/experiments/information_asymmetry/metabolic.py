from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any
import copy

from .model import Condition, DeliveredMessage, MessageIntent, Router


class ResourceRegime(str, Enum):
    ABUNDANT = "abundant"
    SCARCE = "scarce"


ABUNDANT_CAPACITY = 100
SCARCE_CAPACITY = 6


@dataclass(frozen=True)
class ResourceDebit:
    timestep: int
    actor_id: str
    amount: int
    reason: str
    balance_before: int
    balance_after: int


class ResourceLedger:
    """One deliberately simple conserved cognitive resource.

    This first metabolic experiment uses a finite stock with no replenishment,
    hoarding, conversion, or learning. The purpose is to isolate communication
    cost before introducing the rest of the proposed internal economy.
    """

    def __init__(self, actors: tuple[str, ...], initial_capacity: int) -> None:
        if initial_capacity < 0:
            raise ValueError("initial_capacity must be non-negative")
        self.initial_capacity = initial_capacity
        self._balances = {actor: initial_capacity for actor in actors}
        self.debits: list[ResourceDebit] = []

    def balance(self, actor_id: str) -> int | None:
        return self._balances.get(actor_id)

    def can_afford(self, actor_id: str, amount: int) -> bool:
        if amount < 0:
            raise ValueError("resource cost must be non-negative")
        balance = self.balance(actor_id)
        return balance is None or balance >= amount

    def debit(self, actor_id: str, amount: int, *, timestep: int, reason: str) -> None:
        if amount < 0:
            raise ValueError("resource cost must be non-negative")
        if amount == 0 or actor_id not in self._balances:
            return
        before = self._balances[actor_id]
        if before < amount:
            raise ValueError(f"{actor_id} cannot afford {amount}; balance={before}")
        after = before - amount
        self._balances[actor_id] = after
        self.debits.append(
            ResourceDebit(
                timestep=timestep,
                actor_id=actor_id,
                amount=amount,
                reason=reason,
                balance_before=before,
                balance_after=after,
            )
        )

    def snapshot(self) -> dict[str, int]:
        return dict(sorted(self._balances.items()))

    @property
    def consumed_total(self) -> int:
        return sum(item.amount for item in self.debits)

    @property
    def initial_total(self) -> int:
        return self.initial_capacity * len(self._balances)

    @property
    def current_total(self) -> int:
        return sum(self._balances.values())

    def conservation_error(self) -> int:
        return self.initial_total - self.current_total - self.consumed_total


@dataclass(frozen=True)
class MetabolicRouteRecord:
    message_id: str
    timestep: int
    sender: str
    receiver: str
    kind: str
    payload: dict[str, Any]
    routing_reason: str
    succeeded: bool
    topology_allowed: bool
    send_cost: int
    assimilation_cost: int
    failure_stage: str | None
    sender_balance_before: int | None
    sender_balance_after: int | None
    receiver_balance_before: int | None
    receiver_balance_after: int | None


class MetabolicRouter(Router):
    """Router that makes selected internal communication metabolically costly.

    Workspace broadcasts are charged atomically at the sender. Either the sender
    can finance every topology-eligible recipient or none of those deliveries
    occur. This intentionally prevents recipient ordering from deciding which
    processor receives a partially funded broadcast.
    """

    def __init__(self, condition: Condition, initial_capacity: int) -> None:
        super().__init__(condition)
        self.ledger = ResourceLedger(self.PROCESSOR_NAMES, initial_capacity)
        self.records: list[MetabolicRouteRecord] = []

    def route(self, intent: MessageIntent, timestep: int) -> list[DeliveredMessage]:
        if intent.workspace_eligible:
            recipients = [name for name in self.PROCESSOR_NAMES if name != intent.sender]
        else:
            if intent.receiver is None:
                raise ValueError("Direct messages require an explicit receiver")
            recipients = [intent.receiver]

        allowed: list[str] = []
        blocked: list[str] = []
        for receiver in recipients:
            if self._allowed(intent, receiver):
                allowed.append(receiver)
            else:
                blocked.append(receiver)

        send_cost, assimilation_cost = self._costs(intent)
        delivered: list[DeliveredMessage] = []

        sender_before = self.ledger.balance(intent.sender)
        sender_total_cost = send_cost * len(allowed)
        sender_can_afford = self.ledger.can_afford(intent.sender, sender_total_cost)

        if sender_can_afford:
            self.ledger.debit(
                intent.sender,
                sender_total_cost,
                timestep=timestep,
                reason=f"send:{intent.kind}:{len(allowed)}_recipient(s)",
            )
        sender_after = self.ledger.balance(intent.sender)

        for receiver in blocked:
            self._counter += 1
            message_id = f"M{self._counter:03d}"
            receiver_balance = self.ledger.balance(receiver)
            self.records.append(
                MetabolicRouteRecord(
                    message_id=message_id,
                    timestep=timestep,
                    sender=intent.sender,
                    receiver=receiver,
                    kind=intent.kind,
                    payload=copy.deepcopy(intent.payload),
                    routing_reason=intent.routing_reason,
                    succeeded=False,
                    topology_allowed=False,
                    send_cost=0,
                    assimilation_cost=0,
                    failure_stage="topology",
                    sender_balance_before=sender_before,
                    sender_balance_after=sender_after,
                    receiver_balance_before=receiver_balance,
                    receiver_balance_after=receiver_balance,
                )
            )

        for receiver in allowed:
            self._counter += 1
            message_id = f"M{self._counter:03d}"
            receiver_before = self.ledger.balance(receiver)

            if not sender_can_afford:
                self.records.append(
                    MetabolicRouteRecord(
                        message_id=message_id,
                        timestep=timestep,
                        sender=intent.sender,
                        receiver=receiver,
                        kind=intent.kind,
                        payload=copy.deepcopy(intent.payload),
                        routing_reason=intent.routing_reason,
                        succeeded=False,
                        topology_allowed=True,
                        send_cost=send_cost,
                        assimilation_cost=assimilation_cost,
                        failure_stage="send_budget",
                        sender_balance_before=sender_before,
                        sender_balance_after=sender_after,
                        receiver_balance_before=receiver_before,
                        receiver_balance_after=receiver_before,
                    )
                )
                continue

            if not self.ledger.can_afford(receiver, assimilation_cost):
                self.records.append(
                    MetabolicRouteRecord(
                        message_id=message_id,
                        timestep=timestep,
                        sender=intent.sender,
                        receiver=receiver,
                        kind=intent.kind,
                        payload=copy.deepcopy(intent.payload),
                        routing_reason=intent.routing_reason,
                        succeeded=False,
                        topology_allowed=True,
                        send_cost=send_cost,
                        assimilation_cost=assimilation_cost,
                        failure_stage="assimilation_budget",
                        sender_balance_before=sender_before,
                        sender_balance_after=sender_after,
                        receiver_balance_before=receiver_before,
                        receiver_balance_after=receiver_before,
                    )
                )
                continue

            self.ledger.debit(
                receiver,
                assimilation_cost,
                timestep=timestep,
                reason=f"assimilate:{intent.kind}:from:{intent.sender}",
            )
            receiver_after = self.ledger.balance(receiver)
            self.records.append(
                MetabolicRouteRecord(
                    message_id=message_id,
                    timestep=timestep,
                    sender=intent.sender,
                    receiver=receiver,
                    kind=intent.kind,
                    payload=copy.deepcopy(intent.payload),
                    routing_reason=intent.routing_reason,
                    succeeded=True,
                    topology_allowed=True,
                    send_cost=send_cost,
                    assimilation_cost=assimilation_cost,
                    failure_stage=None,
                    sender_balance_before=sender_before,
                    sender_balance_after=sender_after,
                    receiver_balance_before=receiver_before,
                    receiver_balance_after=receiver_after,
                )
            )
            delivered.append(
                DeliveredMessage(
                    message_id=message_id,
                    timestep=timestep,
                    sender=intent.sender,
                    receiver=receiver,
                    kind=intent.kind,
                    payload=copy.deepcopy(intent.payload),
                    routing_reason=intent.routing_reason,
                )
            )

        return delivered

    def environment_message(
        self,
        *,
        timestep: int,
        receiver: str,
        kind: str,
        payload: dict[str, Any],
        reason: str,
    ) -> DeliveredMessage:
        self._counter += 1
        message_id = f"M{self._counter:03d}"
        receiver_balance = self.ledger.balance(receiver)
        self.records.append(
            MetabolicRouteRecord(
                message_id=message_id,
                timestep=timestep,
                sender="ENVIRONMENT",
                receiver=receiver,
                kind=kind,
                payload=copy.deepcopy(payload),
                routing_reason=reason,
                succeeded=True,
                topology_allowed=True,
                send_cost=0,
                assimilation_cost=0,
                failure_stage=None,
                sender_balance_before=None,
                sender_balance_after=None,
                receiver_balance_before=receiver_balance,
                receiver_balance_after=receiver_balance,
            )
        )
        return DeliveredMessage(
            message_id=message_id,
            timestep=timestep,
            sender="ENVIRONMENT",
            receiver=receiver,
            kind=kind,
            payload=copy.deepcopy(payload),
            routing_reason=reason,
        )

    @staticmethod
    def _costs(intent: MessageIntent) -> tuple[int, int]:
        # Research prompts and behavior observation are cost-exempt so that the
        # manipulation targets internal evidence propagation rather than the
        # ability to receive the task or measure its outcome.
        if intent.kind == "workspace_event":
            if intent.payload.get("event_type") == "social_fact":
                return 1, 1
            return 0, 0
        if intent.kind in {
            "recommendation_request",
            "social_recommendation",
            "context_request",
            "memory_context_reply",
            "social_context_reply",
        }:
            return 1, 1
        return 0, 0


def metabolic_record_to_dict(record: MetabolicRouteRecord) -> dict[str, Any]:
    return {
        "message_id": record.message_id,
        "timestep": record.timestep,
        "sender": record.sender,
        "receiver": record.receiver,
        "kind": record.kind,
        "payload": copy.deepcopy(record.payload),
        "routing_reason": record.routing_reason,
        "succeeded": record.succeeded,
        "topology_allowed": record.topology_allowed,
        "send_cost": record.send_cost,
        "assimilation_cost": record.assimilation_cost,
        "failure_stage": record.failure_stage,
        "sender_balance_before": record.sender_balance_before,
        "sender_balance_after": record.sender_balance_after,
        "receiver_balance_before": record.receiver_balance_before,
        "receiver_balance_after": record.receiver_balance_after,
    }
