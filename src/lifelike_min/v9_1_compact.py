from __future__ import annotations

import json

from .exp007_challenger import EligibilityRecord
from .v9_compact import CompactV9Character


class V91CompactCharacter(CompactV9Character):
    """Final global-ablation candidate descended from frozen behavioral v9.

    This class adds no behavioral capability. It applies only structural reductions
    supported by the completed global-ablation evidence:

    * active_concern and concern_strength remain deterministic views of the bounded
      concern ledger rather than stored organism state;
    * last_action and last_context remain absent, with the age-zero eligibility trace
      supplying immediate context-action evidence;
    * context-idle habit entries that cannot affect idle scoring are not created by
      the trace-backed immediate learner;
    * concern and prospective stores are reduced from capacity three to capacity two,
      the smallest pair that preserved the earned behavioral contract.

    Rejected semantic unions remain rejected: active concerns and latent prospective
    commitments remain independent stores, as do partner reliability and location
    beliefs.

    Persistence is deliberately separate from the rounded diagnostic snapshot. The
    canonical persistent payload stores full-precision mutable organism state so a
    serialized/deserialized individual can continue without numerical divergence.
    """

    structural_version = "v9.1_compact"
    max_concerns = 2
    max_prospective = 2

    def persistent_snapshot(self) -> dict:
        """Return lossless, JSON-compatible mutable organism state.

        Diagnostic views and debug telemetry are excluded. Class/version and policy
        configuration are supplied by constructing this frozen class on restore.
        """
        return {
            "tick": self.tick,
            "needs": {
                "fatigue": self.fatigue,
                "affiliation": self.affiliation,
                "competence": self.competence,
            },
            "relationships": dict(sorted(self.relationships.items())),
            "threat_residue": self.threat_residue,
            "habits": {
                f"{context}|{action}": value
                for (context, action), value in sorted(self.habits.items())
            },
            "partner_reliability": dict(sorted(self.partner_reliability.items())),
            "concern_ledger": dict(sorted(self.concerns.items())),
            "prospective_commitments": dict(sorted(self.prospective_commitments.items())),
            "location_beliefs": dict(sorted(self.location_beliefs.items())),
            "eligibility_records": [
                {
                    "context": row.context,
                    "action": row.action,
                    "age": row.age,
                }
                for row in sorted(
                    self.eligibility_records,
                    key=lambda item: (item.context, item.action),
                )
            ],
        }

    def serialize_persistent(self) -> str:
        return json.dumps(self.persistent_snapshot(), sort_keys=True, separators=(",", ":"))

    @classmethod
    def from_persistent_snapshot(cls, data: dict) -> "V91CompactCharacter":
        agent = cls()
        agent.tick = int(data["tick"])
        needs = data["needs"]
        agent.fatigue = float(needs["fatigue"])
        agent.affiliation = float(needs["affiliation"])
        agent.competence = float(needs["competence"])
        agent.relationships = {
            str(key): float(value)
            for key, value in data.get("relationships", {}).items()
        }
        agent.threat_residue = float(data.get("threat_residue", 0.0))
        agent.habits = {}
        for key, value in data.get("habits", {}).items():
            context, action = str(key).split("|", 1)
            agent.habits[(context, action)] = float(value)
        agent.partner_reliability = {
            str(key): float(value)
            for key, value in data.get("partner_reliability", {}).items()
        }
        agent.concerns = {
            str(key): float(value)
            for key, value in data.get("concern_ledger", {}).items()
        }
        agent.prospective_commitments = {
            str(key): str(value)
            for key, value in data.get("prospective_commitments", {}).items()
        }
        agent.location_beliefs = {
            str(key): str(value)
            for key, value in data.get("location_beliefs", {}).items()
        }
        agent.eligibility_records = [
            EligibilityRecord(
                context=str(row["context"]),
                action=str(row["action"]),
                age=int(row["age"]),
            )
            for row in data.get("eligibility_records", [])
        ]
        agent.trace = []
        return agent

    @classmethod
    def from_persistent_json(cls, encoded: str) -> "V91CompactCharacter":
        return cls.from_persistent_snapshot(json.loads(encoded))
