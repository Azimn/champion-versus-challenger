from __future__ import annotations

from .exp009_challenger import UnresolvedConcernPersistenceCharacter


class CapacityThreeConcernCharacter(UnresolvedConcernPersistenceCharacter):
    """EXP-010 minimum-information challenger.

    The only production mutation is representational capacity within the already
    earned bounded concern mechanism: two concern records become three.

    No new persistent field, status, archive, suppression queue, return rule, or
    counted mechanism is introduced. Existing concern semantics remain authoritative:

    * dictionary membership represents unresolved existence;
    * the existing scalar represents current activation and continues to decay;
    * ``active_concern`` is the existing deterministic strongest-entry view;
    * cancellation and work-mediated resolution remain the only ordinary explicit
      termination paths;
    * bounded strength-based replacement still applies once more than three distinct
      unresolved concerns compete.

    A weaker concern can therefore be represented while non-dominant without a new
    suppression state. If stronger concerns terminate, ordinary winner selection can
    expose the retained weaker concern again.
    """

    experimental_version = "exp010_capacity_three_concern_candidate"
    max_concerns = 3
