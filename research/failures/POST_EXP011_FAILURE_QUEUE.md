# Post-EXP-011 Failure Queue

Frozen basis: `v9.4_prospective_capacity_three`

Frozen branch: `champion-v9-4-prospective-capacity-three`

Frozen commit: `5f949c6e882f780e1d4c07f0b6b3bccf330936aa`

Independent frozen verification: workflow `35276731608`.

Post-freeze frontier diagnosis: workflow `35276885005`, artifact `10521350357`.

## Revalidated failures

### 1. rewarded_routine_never_weakens

**STILL REPRODUCED.**

A once-rewarded `morning -> walk` habit is `0.35` immediately after learning and remains exactly `0.35` after 1000 unrelated experienced events. On return to the morning context it still contributes the same action-value support.

EXP-012 foundation additionally establishes:

- gap lengths 0, 1, 10, 100, 1000, and 10000 do not alter the stored habit value;
- after temporary eligibility evidence expires, an old 0.35 routine and a recently reinforced 0.35 routine can be made canonically identical at the same lifetime tick;
- an old and a recently reinforced competing routine in the same context therefore remain tied at 0.35 and the action list order determines the winner;
- repeated context/action exposure without an outcome does not alter the value;
- negative learned action values also remain exactly unchanged across unrelated experience.

This is selected for EXP-012 because the existing habit mechanism already owns a mutable signed scalar that could, in principle, carry changing current strength without a new persistent field. No such semantic change is yet accepted.

### 2. ancient_commitment_reactivates_unchanged

**STILL REPRODUCED.**

The prospective pair `{ancient: ancient_cue}` remains exactly unchanged after 1000 unrelated events and later cue activation recreates the concern at strength `0.75`.

Matched-history diagnosis shows an old prospective pair and a recently created identical pair can be made canonically identical at the same lifetime tick. Unlike the habit representation, the prospective record contains only identity + cue. It has no mutable strength, age, last-refresh time, or other temporal carrier.

This creates a stronger apparent information deficit than the habit failure. It remains queued and must not be modified during EXP-012.

### 3. deterministic_rhythm

**STILL REPRODUCED.**

Under repeated neutral autonomous input, the long-run action tail settles into the exact period-six sequence:

`rest, work, idle, rest, idle, idle`

with exact periods 6, 12, 18, 24, and 30 detected in the tested tail.

Post-v9.4 perturbation testing from low, high, asymmetric, and epsilon-shifted initial need values also converged to exact period-six behavior, sometimes phase-shifted. This therefore appears to be an endogenous deterministic-dynamics / action-selection interaction rather than an obvious missing-history problem.

It remains queued and must stay separate from temporal-plasticity work.

## EXP-011 target

`third_commitment_is_forgotten`: **ELIMINATED BY TARGET CORRECTION.**

The frozen v9.4 champion retains all first/second/third prospective identity+cue records and `cue_first` later reactivates `first` at the inherited strength `0.75`.

## Current ordering

1. `rewarded_routine_never_weakens` -> EXP-012 candidate after archaeology and preregistration.
2. `ancient_commitment_reactivates_unchanged` -> preserved temporal-persistence frontier with a stronger representation deficit.
3. `deterministic_rhythm` -> preserved endogenous-dynamics frontier.

This ordering is experimental, not a claim of psychological importance.
