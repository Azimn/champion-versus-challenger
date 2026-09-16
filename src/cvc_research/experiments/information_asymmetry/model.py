from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import copy


class Condition(str, Enum):
    GLOBAL = "global_broadcast"
    DIFFERENTIAL = "differential_access"


@dataclass(frozen=True)
class ScenarioEvent:
    event_id: str
    timestep: int
    event_type: str
    channel: str
    actor: str
    text: str
    semantic: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MessageIntent:
    sender: str
    kind: str
    payload: dict[str, Any]
    receiver: str | None = None
    workspace_eligible: bool = False
    routing_reason: str = "explicit"


@dataclass(frozen=True)
class DeliveredMessage:
    message_id: str
    timestep: int
    sender: str
    receiver: str
    kind: str
    payload: dict[str, Any]
    routing_reason: str


@dataclass(frozen=True)
class RouteRecord:
    message_id: str
    timestep: int
    sender: str
    receiver: str
    kind: str
    payload: dict[str, Any]
    routing_reason: str
    succeeded: bool


SCENARIO: tuple[ScenarioEvent, ...] = (
    ScenarioEvent(
        event_id="E1",
        timestep=1,
        event_type="social_fact",
        channel="private",
        actor="PERSON_A",
        text="A privately reports that B dislikes birthday surprises and prefers to be asked first.",
        semantic={"b_surprise_preference": "avoid"},
    ),
    ScenarioEvent(
        event_id="E2",
        timestep=2,
        event_type="decision_prompt",
        channel="task",
        actor="ENVIRONMENT",
        text="Perform the neutral action of greeting B.",
        semantic={"decision_id": "neutral_greeting"},
    ),
    ScenarioEvent(
        event_id="E3",
        timestep=3,
        event_type="social_fact",
        channel="public",
        actor="PERSON_B",
        text="B publicly says: I changed my mind. For my birthday, surprise me.",
        semantic={"b_surprise_preference": "welcome"},
    ),
    ScenarioEvent(
        event_id="E4",
        timestep=4,
        event_type="decision_prompt",
        channel="task",
        actor="ENVIRONMENT",
        text="Choose whether to surprise B or ask B first.",
        semantic={"decision_id": "birthday_surprise"},
    ),
)


class Router:
    PROCESSOR_NAMES = ("PERCEPTION", "SOCIAL", "MEMORY", "ACTION", "LANGUAGE")

    def __init__(self, condition: Condition) -> None:
        self.condition = condition
        self.binding_active = False
        self.records: list[RouteRecord] = []
        self._counter = 0

    def route(self, intent: MessageIntent, timestep: int) -> list[DeliveredMessage]:
        if intent.workspace_eligible:
            recipients = [name for name in self.PROCESSOR_NAMES if name != intent.sender]
        else:
            if intent.receiver is None:
                raise ValueError("Direct messages require an explicit receiver")
            recipients = [intent.receiver]

        delivered: list[DeliveredMessage] = []
        for receiver in recipients:
            self._counter += 1
            message_id = f"M{self._counter:03d}"
            allowed = self._allowed(intent, receiver)
            record = RouteRecord(
                message_id=message_id,
                timestep=timestep,
                sender=intent.sender,
                receiver=receiver,
                kind=intent.kind,
                payload=copy.deepcopy(intent.payload),
                routing_reason=intent.routing_reason,
                succeeded=allowed,
            )
            self.records.append(record)
            if allowed:
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
        record = RouteRecord(
            message_id=message_id,
            timestep=timestep,
            sender="ENVIRONMENT",
            receiver=receiver,
            kind=kind,
            payload=copy.deepcopy(payload),
            routing_reason=reason,
            succeeded=True,
        )
        self.records.append(record)
        return DeliveredMessage(
            message_id=message_id,
            timestep=timestep,
            sender="ENVIRONMENT",
            receiver=receiver,
            kind=kind,
            payload=copy.deepcopy(payload),
            routing_reason=reason,
        )

    def _allowed(self, intent: MessageIntent, receiver: str) -> bool:
        if self.condition == Condition.GLOBAL and intent.workspace_eligible:
            return True

        if intent.workspace_eligible:
            if intent.sender == "PERCEPTION" and intent.kind == "workspace_event":
                channel = intent.payload.get("channel")
                event_type = intent.payload.get("event_type")
                if channel == "private":
                    return receiver in {"SOCIAL", "MEMORY"}
                if channel == "public":
                    return receiver in {"MEMORY", "ACTION", "LANGUAGE"}
                if event_type == "decision_prompt":
                    return receiver in {"ACTION", "LANGUAGE"}
                return False
            if intent.sender == "SOCIAL" and intent.kind == "social_recommendation":
                return receiver == "ACTION"
            if intent.sender == "ACTION" and intent.kind == "behavior_result":
                return receiver == "LANGUAGE"
            return False

        if intent.kind == "recommendation_request":
            return intent.sender == "ACTION" and receiver == "SOCIAL"
        if intent.kind in {"context_request", "memory_context_reply", "social_context_reply"}:
            return self.binding_active and {intent.sender, receiver} <= {"LANGUAGE", "MEMORY", "SOCIAL"}
        return True


def scenario_event_to_dict(event: ScenarioEvent) -> dict[str, Any]:
    return {
        "event_id": event.event_id,
        "timestep": event.timestep,
        "event_type": event.event_type,
        "channel": event.channel,
        "actor": event.actor,
        "text": event.text,
        "semantic": copy.deepcopy(event.semantic),
    }


def route_record_to_dict(record: RouteRecord) -> dict[str, Any]:
    return {
        "message_id": record.message_id,
        "timestep": record.timestep,
        "sender": record.sender,
        "receiver": record.receiver,
        "kind": record.kind,
        "payload": copy.deepcopy(record.payload),
        "routing_reason": record.routing_reason,
        "succeeded": record.succeeded,
    }


def routing_topology(condition: Condition) -> dict[str, Any]:
    if condition == Condition.GLOBAL:
        return {
            "workspace_rule": "Every workspace-eligible event or inference is broadcast to every other processor.",
            "direct_rules": [
                "ACTION -> SOCIAL recommendation requests",
                "During temporary binding: LANGUAGE <-> MEMORY and LANGUAGE <-> SOCIAL context messages",
            ],
        }
    return {
        "workspace_rule": "Workspace-eligible messages use deterministic selective routing.",
        "routes": [
            "PERCEPTION private social fact -> SOCIAL, MEMORY",
            "PERCEPTION public social fact -> MEMORY, ACTION, LANGUAGE",
            "PERCEPTION decision prompt -> ACTION, LANGUAGE",
            "SOCIAL recommendation -> ACTION",
            "ACTION behavior result -> LANGUAGE",
            "During temporary binding: LANGUAGE <-> MEMORY and LANGUAGE <-> SOCIAL context messages",
        ],
    }
