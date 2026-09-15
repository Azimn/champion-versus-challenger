from __future__ import annotations

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
    """

    structural_version = "v9.1_compact"
    max_concerns = 2
    max_prospective = 2
