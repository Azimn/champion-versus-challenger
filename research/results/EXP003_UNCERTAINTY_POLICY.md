# EXP-003: Adversarial Audit and Uncertainty Policy Correction

Date: 2026-09-15

Branch: `exp003-adversarial-audit`

Pull request: #9

Frozen champion: `v5_partner_model`

Promoted challenger: `v5_1_uncertainty_policy`

## Adversarial audit

The frozen EXP-002 champion was attacked before any new cognition was implemented. Five holdout behaviors were tested: multiple unfinished concerns, long-delay future commitments, relationship repair, habit reversal, and partner-specific prediction under a reordered action set.

Three failures were observed:

1. A second unfinished concern overwrote the first concern.
2. A long-delay commitment disappeared through concern-strength decay even though nothing completed or cancelled it.
3. The previously reported unknown-partner verification behavior was action-order dependent.

The third finding takes priority because it falsifies part of a behavior previously treated as earned in EXP-002. The original reviewer presented `verify` before `delegate`. With zero partner evidence, both actions scored 0.10, so the inherited deterministic tie-breaker selected whichever equivalent alternative appeared first.

Relationship repair and habit reversal survived the new audit.

## Internal archaeology

The Azimn repository set was inspected before external prior art.

`Azimn/DUCK`, branch `motivated-cognition-v0.10`, contains persistent motive records, bounded multiple active motives, planning experiments, and a subject-owned expectation ledger with explicit confidence and calibration. It demonstrates prior internal work on explicit uncertainty, multiple continuing commitments, prospective state, and bounded persistence.

`Azimn/TinyPersonaEngine` contains lightweight goal sets, belief records with confidence and provenance, attention state, memory associations, and action pressures.

Neither repository was merged. No source code was copied into the challenger.

## External prior art

The Beta Reputation System provides a compact precedent for treating lack of evidence as uncertainty rather than negative evidence or a deterministic action preference. PsychSim provides a substantially richer comparison point in which agents maintain uncertain models of other agents.

EXP-003 deliberately chose the smaller hypothesis instead of importing either full mechanism family.

## Minimal hypothesis

The existing partner-reliability scalar is sufficient for the current social-prediction behavior. The failure comes from the decision policy around weak evidence, not from insufficient persistent representation.

When the magnitude of reliability evidence is below a small threshold, verification should receive a conservative utility premium. Strong positive evidence should still support delegation. Negative evidence should still support verification.

## Challenger

`v5_1_uncertainty_policy` subclasses the frozen v5 runtime and changes only scoring of `verify:<actor>` near zero reliability.

It adds:

- no new persistent state,
- no new memory structure,
- no new subsystem,
- no new counted mechanism.

The threshold is 0.15 and the verification premium is 0.08 in this experiment.

## Causal comparison

The frozen v5 champion is the ablation condition.

For an unseen Blake:

- action order `verify, delegate`: v5 chose `verify:Blake`;
- action order `delegate, verify`: v5 chose `delegate:Blake`.

The challenger chose `verify:Blake` under both orderings.

Known reliable Alex was delegated to under both action orderings. Known unreliable Alex was verified under both orderings.

## Reviewer attack

The challenger passed all adversarial reviewer probes:

- known evidence remained invariant to action ordering;
- contradictory evidence changed Alex from delegation to verification;
- near-neutral contradictory evidence produced verification under both action orderings;
- evidence about Alex did not transfer to an unseen Blake;
- all five previously earned EXP-002 behavioral probes still passed;
- renderer invariance still passed.

## Cost

GitHub Actions run: `35013090805`

Artifact: `exp003-results`, artifact ID `10414372707`

The final matched run measured:

| Measure | v5 champion | v5.1 challenger |
| --- | ---: | ---: |
| Counted mechanisms | 8 | 8 |
| Representative persistent state | 325 bytes | 325 bytes |
| Median microseconds per tick | 8.8102 | 8.0190 |

The timing difference is treated as ordinary CI microbenchmark variance. The defensible cost result is that no measurable persistent-state or counted-mechanism cost was added and no runtime regression was detected.

## Decision

PROMOTE `v5_1_uncertainty_policy` as the next branch-local champion.

This is a correction and strengthening of the fifth EXP-002 capability, not a claim that a sixth independent cognitive capability has been added.

## Remaining confirmed failures

The audit leaves two directly reproduced high-impact failures:

- multiple unfinished concerns cannot coexist;
- future commitments decay away solely because time passes.

The next experiment should attack multiple unfinished concerns first. It is the broader structural failure and internal DUCK archaeology already provides a useful upper-bound donor: bounded multiple persistent motives and plans. The next challenger should test a much smaller bounded concern ledger before any planner or general motive architecture is imported.
