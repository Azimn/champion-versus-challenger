from __future__ import annotations

from .exp003_challenger import UncertaintyPolicyCharacter
from .v9_1_compact import V91CompactCharacter


class UnresolvedConcernPersistenceCharacter(V91CompactCharacter):
    """EXP-009 zero-new-state challenger.

    The bounded concern ledger already contains two pieces of information: the key
    identifies the named unresolved concern and the value supplies current activation.
    Frozen v9.1 multiplied activation by 0.97 each drift and then treated activation
    below 0.08 as implicit termination. EXP-009 removes only that inference.

    Ordinary time still weakens activation. Ledger membership is retained until an
    already-earned removal path fires: explicit cancellation, work-mediated
    resolution, or bounded-capacity eviction.

    No persistent field, status flag, timestamp, dormant store, or mechanism is
    added. If repeated floating-point decay eventually underflows to 0.0, zero is a
    coherent activation value while dictionary membership continues to represent the
    unresolved identity.
    """

    experimental_version = "exp009_unresolved_concern_persistence_candidate"

    def _drift(self) -> None:
        # ConcernLedgerCharacter._drift is the only inherited drift layer that
        # couples activation decay to deletion. Call its parent directly so all
        # lower-level need/affect drift remains unchanged, then reproduce the same
        # 0.97 concern activation decay without the <0.08 deletion condition.
        UncertaintyPolicyCharacter._drift(self)
        for concern, strength in list(self.concerns.items()):
            self.concerns[concern] = strength * 0.97
        self._sync_active_concern()
