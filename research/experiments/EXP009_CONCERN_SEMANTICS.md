# EXP-009 concern semantics before implementation

This record is committed after the EXP-009 preregistration and before challenger production code.

## Evidence already earned

The concern ledger was introduced in EXP-004 to preserve more than one unfinished concern. Existing behavior demonstrates that the dictionary key identifies a named unresolved concern and that the scalar value influences which concern is currently strongest. Frozen v9.1 derives `active_concern` and `concern_strength` from that ledger rather than storing duplicate state.

The frozen runtime currently removes concern entries through three different kinds of event:

1. `task_cancel` removes the named concern explicitly.
2. `work` reduces the currently active concern and removes it once the work-resolution rule crosses its existing completion threshold.
3. `_bound_concerns` removes lower-ranked concerns when the bounded ledger exceeds capacity two.

A fourth path, ordinary per-event decay, multiplies every concern strength by 0.97 and deletes an entry below 0.08. EXP-009 is motivated specifically because this path treats low current activation as evidence that unresolved business no longer exists, even when no resolving event occurred.

## Intended meanings under test

### Concern identity
The concern name/key identifies what unfinished matter the organism is carrying. It is not itself a timestamp, status flag, completion marker, or activation value.

### Concern ledger membership
Membership is tested as the minimal existing representation that the named concern remains unresolved. This is a hypothesis, not a general theory of intention. Membership may still end through explicit cancellation, existing action-mediated resolution, or bounded-capacity eviction.

### Concern strength
The existing scalar is interpreted as current activation, salience, or behavioral pressure for that unresolved concern. It may decay with unrelated time. It is not, under the EXP-009 hypothesis, sufficient by itself to prove completion or cancellation.

### Concern activation
Activation is the current magnitude stored as the ledger value and used by existing selection policy. A concern may remain represented with very low or zero floating-point activation. Existence therefore does not imply current behavioral dominance.

### Concern resolution
Resolution is an already-earned event-mediated state transition in which relevant `work` reduces the active concern enough for the existing resolution rule to remove the ledger entry.

### Concern cancellation
Cancellation is the explicit `task_cancel` event removing the target concern, or all concerns when no target is supplied.

### Concern eviction
Eviction is loss caused by the explicitly bounded concern store when more than two concerns compete. It is not interpreted as completion. EXP-009 does not add state to remember evicted concerns and does not claim that eviction is psychologically realistic.

## Compatibility with earned behavior

This interpretation preserves the distinctions already exercised by EXP-004 and the v9.1 structural closeout: multiple concerns may coexist; the strongest current concern drives the derived active view; work may resolve the active concern; cancellation removes concerns; and the store remains bounded.

No previously earned behavioral contract requires ordinary unrelated decay itself to delete a concern. The selected failure is therefore a direct test of whether deletion can be removed from ordinary decay without adding state or breaking those established behaviors.

## Minimum representation rule to test

The first challenger will retain the existing dictionary and existing scalar only. Ordinary decay will continue multiplying strength by 0.97. It will no longer delete ledger membership solely because the decayed value is below 0.08.

No floor or replacement threshold is required. If floating-point decay eventually reaches zero, zero is a coherent current activation while dictionary membership continues to encode unresolved existence. Existing reassignment can raise the value again through the already-present `max(current, assigned_strength)` rule.

This uses less information than adding a dormant flag, status, timestamp, persistence value, or second store.
