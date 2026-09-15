# EXP-005 Prospective Commitment Donors

## Internal donor: Azimn/DUCK

Repository: `Azimn/DUCK`

Inspected branch: `motivated-cognition-v0.10`

Pinned archaeology commit: `30a11ea8308ebd0fc89a06bb994ab0e23bd02886`

Relevant files:

- `duck/expectations_v010.py`
- `duck/motivated_cognition.py`
- `duck/planning_simulation.py`

Observed donor concepts include subject-owned expectation records, optional due ticks, prospective and opportunity control tags, persistent motives, and plans that survive interruption.

Conceptual provenance used in EXP-005: a future-oriented state can remain owned by the continuing subject and later become relevant when an opportunity or cue occurs.

Implementation provenance used in EXP-005: none. No DUCK source, schema, identifiers, update rules, constants, or serialization is copied. The challenger independently implements only a bounded mapping from concern identifier to cue string.

License status: unresolved in the current archaeology pass. Direct source reuse remains prohibited until licensing is established.

## External prior art: event-based prospective memory

Primary behavioral reference family: Marsh, Hicks, and colleagues on event-based prospective memory; later prospective-memory literature on cue detection and delayed intention retrieval.

Observed conceptual precedent: an intention can be established earlier, remain pending during an ongoing task, and be retrieved when a previously associated environmental event occurs.

Conceptual provenance used in EXP-005: delayed intention plus environmental cue association.

Implementation provenance used in EXP-005: none. This is behavioral and cognitive-science prior art, not source-code reuse.

Licensing status: no software licensing dependency is introduced.

## External agent comparison point

BDI and agent-programming literature allows goals to carry additional metadata such as deadlines and manages future courses of action as intentions. This is retained only as an upper-bound comparison. EXP-005 does not implement deadline monitoring, intention stacks, plan libraries, or a BDI interpreter.

## Boundary decision

The demonstrated failure did not require planning. The smallest successful challenger retains a cue binding and reuses the already tested concern mechanism after cue detection.
