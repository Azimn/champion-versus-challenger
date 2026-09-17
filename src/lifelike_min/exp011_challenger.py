from __future__ import annotations

from .exp010_challenger import CapacityThreeConcernCharacter


class CapacityThreeProspectiveCharacter(CapacityThreeConcernCharacter):
    """EXP-011 minimum prospective-capacity challenger.

    The only production mutation is representational capacity inside the already
    earned prospective commitment mechanism: two identity+cue bindings become three.
    Record schema, cue activation, cancellation, concern interaction, replacement
    rule, renderer, persistence semantics, and mechanism count remain unchanged.
    """

    experimental_version = "exp011_capacity_three_prospective_candidate"
    max_prospective = 3
