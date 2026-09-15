# EXP-004 Concern Persistence Donors

## Internal donor: Azimn/DUCK

Repository: `Azimn/DUCK`

Inspected branch: `motivated-cognition-v0.10`

Pinned archaeology commit: `30a11ea8308ebd0fc89a06bb994ab0e23bd02886`

Relevant files inspected:

- `duck/motivated_cognition.py`
- `duck/planning_simulation.py`
- `duck/expectations_v010.py`

Observed donor mechanisms:

- persistent `MotiveRecord` objects;
- a bounded set of multiple active motives;
- persistent plans that can survive interruption and restart;
- subject-owned expectations with confidence, evidence resolution, and optional due ticks.

Conceptual provenance used in EXP-004: more than one unfinished motivational object may coexist without requiring one to overwrite another.

Implementation provenance used in EXP-004: none. No DUCK source, constants, data structures, tests, serialization formats, or algorithms were copied. The challenger independently implements a three-entry `concern -> strength` dictionary around the already existing EXP-002 concern scalar.

License status: unresolved in this archaeology pass. Direct source reuse is therefore prohibited until licensing is established.

## Internal comparison point: Azimn/TinyPersonaEngine

Repository: `Azimn/TinyPersonaEngine`

Relevant inspected file: `src/living_entity_firstperson/models.py`

Observed donor concepts include a set of goals and lightweight belief/action-pressure records.

Implementation provenance used in EXP-004: none.

License status: unresolved in this archaeology pass. Direct source reuse is prohibited until licensing is established.

## External prior art: BDI and AgentSpeak intention sets

Reference family: Rao and Georgeff, BDI agents; AgentSpeak and later BDI implementations.

Observed conceptual precedent: BDI agents may maintain several concurrent intentions rather than forcing all ongoing commitments through one global slot. Modern descriptions of AgentSpeak likewise define an intention set containing plans the agent has chosen to pursue.

Conceptual provenance used in EXP-004: concurrency of unfinished commitments is a known functional requirement in agent systems.

Implementation provenance used in EXP-004: none. No AgentSpeak, Jason, 2APL, or other BDI source is incorporated.

Licensing status: literature-only conceptual use for EXP-004, so no source-license dependency is introduced.

## Boundary decision

The donor systems contain substantially more machinery than the reproduced failure requires. EXP-004 therefore tests only the smallest functional analogue: plural bounded storage for the concern mechanism that had already earned causal value in EXP-002.
