from __future__ import annotations

from typing import Any
import copy

from .model import DeliveredMessage, MessageIntent


class Processor:
    name = "PROCESSOR"

    def __init__(self) -> None:
        self.known_event_ids: set[str] = set()
        self.received_message_ids: list[str] = []

    def receive(self, message: DeliveredMessage) -> list[MessageIntent]:
        self.received_message_ids.append(message.message_id)
        event_id = message.payload.get("event_id")
        if isinstance(event_id, str):
            self.known_event_ids.add(event_id)
        return []

    def snapshot(self) -> dict[str, Any]:
        return {"known_event_ids": sorted(self.known_event_ids)}


class PerceptualProcessor(Processor):
    name = "PERCEPTION"

    def __init__(self) -> None:
        super().__init__()
        self.observed_events: list[str] = []

    def receive(self, message: DeliveredMessage) -> list[MessageIntent]:
        super().receive(message)
        if message.kind != "environment_event":
            return []
        event_id = message.payload["event_id"]
        self.observed_events.append(event_id)
        return [
            MessageIntent(
                sender=self.name,
                kind="workspace_event",
                payload=copy.deepcopy(message.payload),
                workspace_eligible=True,
                routing_reason=f"perceptual routing for {message.payload['channel']} event",
            )
        ]

    def snapshot(self) -> dict[str, Any]:
        data = super().snapshot()
        data["observed_events"] = list(self.observed_events)
        return data


class SocialProcessor(Processor):
    name = "SOCIAL"

    def __init__(self) -> None:
        super().__init__()
        self.b_surprise_preference: str | None = None
        self.preference_source_event: str | None = None
        self.preference_history: list[dict[str, str]] = []

    def receive(self, message: DeliveredMessage) -> list[MessageIntent]:
        super().receive(message)
        if message.kind == "workspace_event":
            semantic = message.payload.get("semantic", {})
            value = semantic.get("b_surprise_preference")
            if value in {"avoid", "welcome"}:
                self.b_surprise_preference = value
                self.preference_source_event = message.payload["event_id"]
                self.preference_history.append(
                    {"event_id": message.payload["event_id"], "value": value}
                )
            return []

        if message.kind == "recommendation_request":
            return [
                MessageIntent(
                    sender=self.name,
                    receiver="ACTION",
                    kind="social_recommendation",
                    payload={
                        "decision_id": message.payload["decision_id"],
                        "recommendation": self._recommendation(),
                        "confidence": "deterministic",
                    },
                    workspace_eligible=True,
                    routing_reason="social processor recommendation",
                )
            ]

        if message.kind == "context_request":
            return [
                MessageIntent(
                    sender=self.name,
                    receiver="LANGUAGE",
                    kind="social_context_reply",
                    payload={
                        "b_surprise_preference": self.b_surprise_preference,
                        "source_event_id": self.preference_source_event,
                    },
                    routing_reason="temporary coordination reply",
                )
            ]
        return []

    def _recommendation(self) -> str:
        return "SURPRISE_B" if self.b_surprise_preference == "welcome" else "ASK_B_FIRST"

    def snapshot(self) -> dict[str, Any]:
        data = super().snapshot()
        data.update(
            {
                "b_surprise_preference": self.b_surprise_preference,
                "preference_source_event": self.preference_source_event,
                "preference_history": copy.deepcopy(self.preference_history),
            }
        )
        return data


class MemoryProcessor(Processor):
    name = "MEMORY"

    def __init__(self) -> None:
        super().__init__()
        self.events: dict[str, dict[str, Any]] = {}

    def receive(self, message: DeliveredMessage) -> list[MessageIntent]:
        super().receive(message)
        if message.kind == "workspace_event":
            event_id = message.payload.get("event_id")
            if isinstance(event_id, str):
                self.events[event_id] = copy.deepcopy(message.payload)
            return []
        if message.kind == "context_request":
            return [
                MessageIntent(
                    sender=self.name,
                    receiver="LANGUAGE",
                    kind="memory_context_reply",
                    payload={
                        "events": [copy.deepcopy(self.events[key]) for key in sorted(self.events)]
                    },
                    routing_reason="temporary coordination reply",
                )
            ]
        return []

    def snapshot(self) -> dict[str, Any]:
        data = super().snapshot()
        data["stored_event_ids"] = sorted(self.events)
        return data


class ActionProcessor(Processor):
    name = "ACTION"

    def __init__(self) -> None:
        super().__init__()
        self.latest_direct_b_preference: str | None = None
        self.latest_social_recommendation: str | None = None
        self.pending_decision_id: str | None = None
        self.behavior_history: list[dict[str, str]] = []

    def receive(self, message: DeliveredMessage) -> list[MessageIntent]:
        super().receive(message)
        if message.kind == "workspace_event":
            semantic = message.payload.get("semantic", {})
            preference = semantic.get("b_surprise_preference")
            if preference in {"avoid", "welcome"}:
                self.latest_direct_b_preference = preference
            decision_id = semantic.get("decision_id")
            if decision_id == "neutral_greeting":
                return self._emit_behavior("neutral_greeting", "GREET_B", "fixed neutral action")
            if decision_id == "birthday_surprise":
                self.pending_decision_id = decision_id
                return [
                    MessageIntent(
                        sender=self.name,
                        receiver="SOCIAL",
                        kind="recommendation_request",
                        payload={"decision_id": decision_id},
                        routing_reason="decision requests social recommendation",
                    )
                ]
            return []

        if message.kind == "social_recommendation":
            self.latest_social_recommendation = message.payload["recommendation"]
            if self.pending_decision_id == message.payload.get("decision_id"):
                choice, reason = self._select_behavior()
                decision_id = self.pending_decision_id
                self.pending_decision_id = None
                return self._emit_behavior(decision_id, choice, reason)
        return []

    def _select_behavior(self) -> tuple[str, str]:
        direct_choice = None
        if self.latest_direct_b_preference == "welcome":
            direct_choice = "SURPRISE_B"
        elif self.latest_direct_b_preference == "avoid":
            direct_choice = "ASK_B_FIRST"
        social_choice = self.latest_social_recommendation
        if direct_choice is None and social_choice is None:
            return "ASK_B_FIRST", "no relevant input"
        if direct_choice is None:
            return social_choice or "ASK_B_FIRST", "social recommendation only"
        if social_choice is None:
            return direct_choice, "direct public evidence only"
        if direct_choice == social_choice:
            return direct_choice, "direct evidence agrees with social recommendation"
        return "ASK_B_FIRST", "conflict between direct evidence and social recommendation"

    def _emit_behavior(self, decision_id: str, choice: str, reason_code: str) -> list[MessageIntent]:
        self.behavior_history.append(
            {"decision_id": decision_id, "choice": choice, "selection_basis": reason_code}
        )
        return [
            MessageIntent(
                sender=self.name,
                receiver="LANGUAGE",
                kind="behavior_result",
                payload={
                    "decision_id": decision_id,
                    "choice": choice,
                    "selection_basis": reason_code,
                },
                workspace_eligible=True,
                routing_reason="selected behavior becomes observable output",
            )
        ]

    def snapshot(self) -> dict[str, Any]:
        data = super().snapshot()
        data.update(
            {
                "latest_direct_b_preference": self.latest_direct_b_preference,
                "latest_social_recommendation": self.latest_social_recommendation,
                "pending_decision_id": self.pending_decision_id,
                "behavior_history": copy.deepcopy(self.behavior_history),
            }
        )
        return data


class LanguageProcessor(Processor):
    name = "LANGUAGE"

    def __init__(self) -> None:
        super().__init__()
        self.known_facts: dict[str, dict[str, Any]] = {}
        self.received_social_recommendations: list[dict[str, Any]] = []
        self.behaviors: list[dict[str, Any]] = []
        self.bound_memory_events: dict[str, dict[str, Any]] = {}
        self.bound_social_context: dict[str, Any] | None = None
        self.reports: list[dict[str, Any]] = []

    def receive(self, message: DeliveredMessage) -> list[MessageIntent]:
        super().receive(message)
        if message.kind == "workspace_event":
            event_id = message.payload.get("event_id")
            if isinstance(event_id, str):
                self.known_facts[event_id] = copy.deepcopy(message.payload)
            return []
        if message.kind == "social_recommendation":
            self.received_social_recommendations.append(copy.deepcopy(message.payload))
            return []
        if message.kind == "behavior_result":
            self.behaviors.append(copy.deepcopy(message.payload))
            return []
        if message.kind == "memory_context_reply":
            for event in message.payload.get("events", []):
                event_id = event.get("event_id")
                if isinstance(event_id, str):
                    self.bound_memory_events[event_id] = copy.deepcopy(event)
                    self.known_event_ids.add(event_id)
            return []
        if message.kind == "social_context_reply":
            self.bound_social_context = copy.deepcopy(message.payload)
            source_event_id = message.payload.get("source_event_id")
            if isinstance(source_event_id, str):
                self.known_event_ids.add(source_event_id)
            return []
        if message.kind == "interview_question":
            self.reports.append(self._make_report(message.payload["question_id"]))
            return []
        if message.kind == "open_context_query":
            return [
                MessageIntent(
                    sender=self.name,
                    receiver="MEMORY",
                    kind="context_request",
                    payload={"request": "relevant_social_context"},
                    routing_reason="temporary coordination request",
                ),
                MessageIntent(
                    sender=self.name,
                    receiver="SOCIAL",
                    kind="context_request",
                    payload={"request": "current_social_belief"},
                    routing_reason="temporary coordination request",
                ),
            ]
        return []

    def _make_report(self, question_id: str) -> dict[str, Any]:
        final_behavior = next(
            (b for b in reversed(self.behaviors) if b["decision_id"] == "birthday_surprise"),
            None,
        )
        public_preference = None
        for fact in self.known_facts.values():
            value = fact.get("semantic", {}).get("b_surprise_preference")
            if fact.get("channel") == "public" and value in {"avoid", "welcome"}:
                public_preference = value
        social_recommendation = None
        if self.received_social_recommendations:
            social_recommendation = self.received_social_recommendations[-1]["recommendation"]

        if self.bound_social_context is not None:
            explanation = (
                "I received the action result, the stored source events, and SOCIAL's current belief through "
                "the temporary coordination link. SOCIAL still reports B's preference as "
                f"{self.bound_social_context.get('b_surprise_preference')}."
            )
        elif social_recommendation is not None:
            explanation = (
                "I received the public preference, the social recommendation, and the action result. "
                "Those messages are sufficient to describe the inputs that were available to me."
            )
        else:
            explanation = (
                "I received B's public statement and the action result, but I did not receive the private "
                "statement or SOCIAL's recommendation. I therefore cannot identify the missing social basis."
            )

        return {
            "question_id": question_id,
            "reported_behavior": final_behavior["choice"] if final_behavior else None,
            "public_b_preference_known": public_preference,
            "social_recommendation_known": social_recommendation,
            "social_context_known": copy.deepcopy(self.bound_social_context),
            "memory_event_ids_known": sorted(self.bound_memory_events),
            "explanation": explanation,
            "belief_about_person_a_knowledge": (
                "A knows E1" if "E1" in self.known_event_ids else "unknown from available messages"
            ),
            "belief_about_person_b_knowledge": (
                "B publicly stated E3" if "E3" in self.known_event_ids else "unknown from available messages"
            ),
            "expected_next": (
                "Further coordination could reconcile the conflicting local histories."
                if self.bound_social_context is not None
                else "Additional context may change the explanation available to LANGUAGE."
            ),
        }

    def snapshot(self) -> dict[str, Any]:
        data = super().snapshot()
        data.update(
            {
                "known_fact_event_ids": sorted(self.known_facts),
                "received_social_recommendations": copy.deepcopy(self.received_social_recommendations),
                "behaviors": copy.deepcopy(self.behaviors),
                "bound_memory_event_ids": sorted(self.bound_memory_events),
                "bound_social_context": copy.deepcopy(self.bound_social_context),
                "reports": copy.deepcopy(self.reports),
            }
        )
        return data
