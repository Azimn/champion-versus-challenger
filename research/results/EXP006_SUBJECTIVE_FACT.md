# EXP-006: Subject-Owned Perceived Fact

Date: 2026-09-15

Branch: `exp006-adversarial-audit`

Pull request: #12

Frozen champion: `v7_prospective_cue`

Promoted challenger: `v8_subjective_fact`

## Adversarial audit

The frozen v7 organism was attacked in five new domains before any new mechanism was added.

Observed results:

- FAIL: epistemic history divergence;
- FAIL: delayed consequence credit;
- PASS: competing concern priority;
- PASS: autonomous continuation;
- PASS: prospective lure resistance.

The epistemic failure was selected because two different perceived histories collapsed into equivalent search behavior. The organism could observe a book in a drawer or on a shelf, but because it retained no subject-owned location fact, later retrieval behavior followed action ordering rather than lived history.

## Internal archaeology

`Azimn/TinyPersonaEngine`, pinned main commit `5eb2e84dbb43c828fae7a1459c9fd13535c7b332`, contains lightweight belief records with confidence and perception provenance.

`Azimn/DUCK`, pinned motivated-cognition-v0.10 commit `30a11ea8308ebd0fc89a06bb994ab0e23bd02886`, contains subject-owned expectations and an experiential boundary between what the continuing subject has evidence for and hidden host or world state.

Neither architecture was imported.

## External prior art

BDI systems provide a useful upper-bound precedent in which an agent's belief base may be incomplete or wrong relative to the actual environment and is updated through perception. PsychSim provides a richer probabilistic comparison point for agent-specific beliefs and partial observability.

The reproduced failure did not justify either full architecture.

## Minimal hypothesis

One persistent class of subject-owned fact is enough for the current failure: the last location directly perceived for an entity.

The mechanism stores `entity -> perceived_location`.

A direct `observe_location` event updates the subject-owned fact. A `hidden_world_change` event deliberately does not update it. Retrieval prefers the location stored by the subject rather than hidden truth or action ordering.

No confidence model, inference engine, world simulator, recursive Theory of Mind, or general POMDP representation is added.

## Matched result

The frozen champion failed both action-order permutations after each perceived history.

The challenger searched the drawer after seeing the book in the drawer, even when the world secretly moved it to the shelf. It searched the shelf after seeing the book on the shelf, even when the world secretly moved it to the drawer. Both behaviors were invariant to the ordering of the available search actions.

This is intentionally false-belief persistence. Hidden world state does not overwrite subjective state.

## Reviewer attack

The challenger passed all reviewer probes:

- a later direct observation revised a stale belief;
- a hidden change did not create omniscience;
- beliefs remained entity-specific;
- an unobserved entity received no fabricated location belief;
- reobservation changed the belief only after new perceptual evidence;
- all earlier EXP-002 behavior remained green;
- EXP-003 uncertainty behavior remained green;
- EXP-004 multiple-concern behavior remained green;
- EXP-005 prospective behavior remained green;
- renderer invariance remained green.

## Causal ablation

The frozen v7 champion is the ablation. It receives exactly the same observations and hidden world changes but has no subject-owned location state, so search behavior is controlled by action ordering.

## Cost

GitHub Actions run: `35014608463`

Artifact: `exp006-results`, artifact ID `10414378796`

| Measure | v7 champion | v8 challenger |
| --- | ---: | ---: |
| Counted mechanisms | 10 | 11 |
| Representative persistent state | 411 bytes | 451 bytes |
| Median microseconds per tick | 16.1351 | 16.1124 |

Runtime ratio: approximately 0.9986. The small timing difference is treated as CI variance, not a speed improvement.

## Scope control

Delayed consequence credit remains unsolved. A rewarded morning walk followed by three unrelated actions still fails to reinforce the earlier walk. The later choice remains `tea`, and the habit table remains empty.

## Decision

PROMOTE `v8_subjective_fact` as the next branch-local champion.

## Next pressure

The next reproduced failure is delayed consequence credit. The next experiment should search internal donors first for bounded causal traces or recent-action associations, then compare those against the smallest external reinforcement-learning precedent. It should not add a general learning architecture unless a short bounded eligibility trace fails.
