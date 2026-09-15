# EXP-006 Epistemic History Donors

## Internal donor: Azimn/TinyPersonaEngine

Repository: `Azimn/TinyPersonaEngine`

Pinned main commit: `5eb2e84dbb43c828fae7a1459c9fd13535c7b332`

Relevant inspected file: `src/living_entity_firstperson/models.py`

Observed concepts include lightweight belief records with confidence and perception provenance, goal sets, attention state, and action-pressure records.

Conceptual provenance used in EXP-006: a continuing character may own a belief derived from perception rather than reading authoritative hidden world state at decision time.

Implementation provenance used in EXP-006: none. No TinyPersonaEngine source code, classes, field names, update rules, or serialization formats were copied.

License status: unresolved in the current archaeology pass. Direct source reuse remains prohibited until licensing is established.

## Internal donor: Azimn/DUCK

Repository: `Azimn/DUCK`

Pinned motivated-cognition-v0.10 commit: `30a11ea8308ebd0fc89a06bb994ab0e23bd02886`

Relevant inspected evidence includes `duck/expectations_v010.py` and the documented experiential boundary between subject-owned evidence and hidden world or host state.

Conceptual provenance used in EXP-006: hidden world changes must not silently rewrite the continuing subject's own informational state.

Implementation provenance used in EXP-006: none.

License status: unresolved in the current archaeology pass. Direct source reuse remains prohibited until licensing is established.

## External prior art: BDI belief bases

Reference family: Rao and Georgeff BDI agents, AgentSpeak, and related BDI implementations.

Observed conceptual precedent: an agent belief base represents what the agent currently believes about the environment and may be incomplete or wrong relative to the actual environment. Perceptions update beliefs rather than granting omniscient access to world state.

Conceptual provenance used in EXP-006: subjective informational state can diverge from hidden reality.

Implementation provenance used in EXP-006: none.

## External comparison point: PsychSim

PsychSim supports agent-specific beliefs and partial observability, including explicit models of other agents.

Role in EXP-006: upper-bound comparison only. The reproduced failure does not require probabilistic beliefs, recursive models, or a decision-theoretic world model.

Implementation provenance used in EXP-006: none.

## Boundary decision

The smallest successful mechanism is one entity-to-last-perceived-location map. The challenger does not infer hidden state, does not represent confidence, and does not generalize beyond the directly tested class of subjective fact. Richer epistemic machinery remains unjustified until a later failure demonstrates the need.
