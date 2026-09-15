# EXP-004: Bounded Concern Ledger

Date: 2026-09-15

Branch: `exp004-concern-ledger`

Pull request: #10

Frozen champion: `v5_1_uncertainty_policy`

Promoted challenger: `v6_bounded_concern_ledger`

## Reproduced failure

The frozen champion can persist one unfinished concern, but a second task replaces the first in the single `active_concern` slot. If the newer task is then cancelled, the older unfinished task has vanished from the organism even though it was never completed or cancelled.

Matched target history:

1. assign `finish_report`;
2. assign `call_morgan`;
3. cancel `call_morgan`;
4. return to neutral action selection.

The frozen champion ended with no active concern and chose `rest`.

## Internal archaeology

The internal donor search found substantially richer machinery in `Azimn/DUCK`, especially bounded persistent `MotiveRecord` collections, multiple active motives, and persistent planning state. That architecture is treated as an upper bound and donor, not as code to merge.

The experiment asks whether the observed failure requires anything more than making the already useful concern scalar plural.

## External prior art

BDI traditions commonly represent sets of concurrent intentions, with intentions acting as persistent commitments to goals. Contemporary summaries of AgentSpeak and BDI execution likewise describe an intention set rather than a single global intention.

EXP-004 does not implement plans, belief logic, desire selection, or a BDI interpreter. Those mechanisms are not required by the reproduced failure.

## Minimal hypothesis

The existing concern mechanism is causally useful. Its storage cardinality is the failure.

Replace the single authoritative concern slot with a bounded map from concern identifier to the same existing strength scalar. Keep the inherited `active_concern` and `concern_strength` values only as a compatibility view of the currently strongest concern.

The ledger is bounded to three entries for this experiment.

## Challenger behavior

The challenger preserved both concerns after assignment. After cancelling `call_morgan`, `finish_report` remained active and the character selected `work`.

The reviewer then attacked the implementation with:

- reversed assignment order;
- cancellation of an unrelated concern;
- duplicate assignment of the same concern;
- five assignments against a three-entry capacity;
- interruption by a shock while two concerns were unfinished.

All reviewer probes passed.

The EXP-003 unknown-partner uncertainty correction also remained invariant to action ordering, and every EXP-002 target behavior plus renderer invariance remained green.

## Causal ablation

The frozen v5.1 champion is the ablation condition. It receives the same task history but cannot represent both unfinished concerns at once and loses the older task.

## Cost

GitHub Actions run: `35013600984`

Artifact: `exp004-results`, artifact ID `10413943662`

| Measure | v5.1 champion | v6 challenger |
| --- | ---: | ---: |
| Counted mechanisms | 8 | 9 |
| Representative persistent state | 299 bytes | 371 bytes |
| Median microseconds per tick | 14.0465 | 15.0871 |

The runtime ratio was approximately 1.0741. Timing is treated as an engineering estimate from shared CI rather than a precise benchmark.

## Scope control

A 90-tick delayed commitment still disappeared from the concern ledger solely through decay. EXP-004 therefore does not accidentally claim to solve prospective or long-delay commitment memory.

## Decision

PROMOTE `v6_bounded_concern_ledger` as the branch-local champion.

The mechanism earned its added state because it removed a reproduced longitudinal failure, survived adversarial variation, preserved all prior behaviors, and remained small relative to the richer donor architectures.

## Next pressure

The next directly reproduced failure is now isolated: a commitment can disappear merely because time passes, despite no completion, cancellation, or evidence that it became impossible.

EXP-005 should first test whether a tiny commitment-retention rule or cue-bound concern record can correct that failure. It should not import a scheduler, planner, or full prospective-memory system unless the smaller mechanism fails.
