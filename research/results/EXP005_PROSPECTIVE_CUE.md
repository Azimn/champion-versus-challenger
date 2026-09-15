# EXP-005: Event-Cued Prospective Commitment

Date: 2026-09-15

Branch: `exp005-prospective-cue`

Pull request: #11

Frozen champion: `v6_bounded_concern_ledger`

Promoted challenger: `v7_prospective_cue`

## Reproduced failure

The EXP-004 champion can hold several current concerns but cannot represent a future intention that should remain latent during unrelated activity and become active only when a later environmental cue occurs.

The matched scenario encoded a commitment to `call_morgan` when `morgan_arrives`, ran 90 unrelated ticks, presented a wrong context, and then presented the correct cue.

The frozen champion retained no representation and chose `rest` at the cue. The challenger retained the latent binding throughout the delay and converted it into the ordinary concern ledger when `morgan_arrives` appeared, producing `work`.

## Minimal mechanism

One bounded `concern -> cue` map.

Future commitments do not continuously contribute utility. They remain latent until an exact environmental context matches the stored cue. On a match, the binding is removed from the prospective store and converted into the already validated ordinary concern representation.

No scheduler, planner, clock monitor, recursive goal representation, or language model is involved.

## Reviewer attack

The challenger passed:

- three unrelated cues without premature activation;
- cancellation before the cue;
- two different future commitments with two different cues;
- one-shot activation, preventing repeated cue duplication;
- bounded prospective-store pressure;
- all EXP-002 behavioral probes;
- EXP-003 unknown-partner order invariance;
- EXP-004 multiple-concern persistence;
- renderer invariance.

## Causal ablation

The frozen v6 champion receives the identical `future_commitment` event and later cue but has no cue-binding state. It therefore retains nothing and cannot activate the intention.

## Cost

GitHub Actions run: `35014023657`

Artifact: `exp005-results`, artifact ID `10415081119`

| Measure | v6 champion | v7 challenger |
| --- | ---: | ---: |
| Counted mechanisms | 9 | 10 |
| Representative persistent state | 348 bytes | 410 bytes |
| Median microseconds per tick | 15.7488 | 16.0119 |

Runtime ratio: approximately 1.0167.

## Prior art boundary

Internal DUCK work contains much richer expectation, prospective, due-tick, motive, and planning machinery. Event-based prospective-memory research likewise describes delayed intentions retrieved by environmental cues. EXP-005 uses only the minimal common functional claim: retain an intention-to-cue association and retrieve it when the cue occurs.

No donor source code is copied.

## Decision

PROMOTE `v7_prospective_cue` as the next branch-local champion.

The next experiment must begin by trying to break v7 in a behavior not already covered. Candidate domains remain epistemic history, false beliefs, conflicting motives, delayed consequences, spontaneous multi-step activity, forgetting, and other longitudinal failures, but none should be implemented until a new audit reproduces one.
