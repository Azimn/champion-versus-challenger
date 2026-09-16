# EXP-009 closeout failure 1

Workflow run: `35137960593`

Artifact: `10463248914`

Frozen production under test: `b5cc3e109ab2fa4de0421dc113009d1ee7fb050d`

## Raw closeout result

Decision emitted by the first closeout harness: **REJECT**.

Only failed gate: `canonical_reconstruction`.

The reconstruction evidence itself showed:

- the canonical serialized state restored exactly before continuation;
- original and restored actions matched on every continuation event;
- original and restored persistent state matched after every continuation event;
- therefore reconstruction did not lose or alter causal state.

The harness nevertheless marked the check failed because it additionally required the dormant `unfinished` concern to remain present at the end of the continuation.

## Why that assertion is invalid

The final continuation event allows ordinary autonomous actions `(rest, work, idle)`. By that point the concern is extremely weak. Both the uninterrupted and restored organism can legitimately select `work` under the existing action policy. Existing work-mediated concern resolution then removes the concern. EXP-009 explicitly preserves work-mediated resolution as a valid termination path.

Requiring the concern to remain present after a legitimate resolution event contradicts the experiment's preregistered termination semantics.

## Classification

**invalid closeout-harness assumption / termination-semantics error**

This is not a serialization defect and not evidence of concern resurrection or loss. Production, reviewer generation 1, and reviewer generation 2 remain frozen.

## Corrective rule

A corrected reconstruction gate must require:

1. exact persistent-state equality immediately after restore;
2. the dormant unresolved concern to be present immediately after restore;
3. identical subsequent actions and persistent states for uninterrupted and restored organisms;
4. no requirement that the concern survive a later event that legitimately resolves it.

The original failed closeout and its REJECT output remain preserved as methodological evidence.
