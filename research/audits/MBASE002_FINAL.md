# MBASE-002 Final: Post-EXP-012 Mechanism Basis Audit

## Scope

MBASE-002 re-evaluates mechanism subset-minimality after EXP-012 changed the semantics of the existing habit scalar.

Frozen behavioral basis:

- version: `v9.5_habit_temporal_plasticity`
- frozen branch: `champion-v9-5-habit-temporal-plasticity`
- frozen commit: `79f747707dadfce9092d89ad19a17a9fcd7dd79b`
- production blob: `9c6474de1918b62e827d32deff2fa10a4b2443d1`
- concern capacity: 3
- prospective capacity: 3
- eligibility capacity: 2

Audit workflow run: `35282117455`

Artifact: `10521904810`

The full repository contract passed immediately before the exhaustive audit: 72 tests and 18 subtests.

## Method

All `2^11 = 2048` mechanism subsets were evaluated.

MBASE-002 retains the corrected MBASE-001 capability probes and post-EXP-012 capacities, and adds one newly demonstrated capability family:

- `habit_temporal_plasticity`

The post-EXP-012 manifest therefore contains 20 capability families.

## Result

Exactly one subset preserves all 20 demonstrated capability families.

That subset is the complete 11-mechanism architecture.

No 10-, 9-, or smaller-mechanism subset preserves full coverage.

Coverage frontier:

| Mechanisms | Best capability coverage |
| ---: | ---: |
| 0 | 2/20 |
| 1 | 5/20 |
| 2 | 8/20 |
| 3 | 10/20 |
| 4 | 13/20 |
| 5 | 14/20 |
| 6 | 15/20 |
| 7 | 16/20 |
| 8 | 17/20 |
| 9 | 18/20 |
| 10 | 19/20 |
| 11 | 20/20 |

The complete 11-mechanism subset is the unique full-coverage subset.

## Single-mechanism ablations

Every leave-one-out ablation loses demonstrated capability.

- fatigue: 19/20, loses `fatigue_pressure`
- affiliation: 19/20, loses `affiliation_pressure`
- competence: 19/20, loses `competence_pressure`
- relationship history: 19/20, loses `partner_specific_relationship_history`
- affect residue: 19/20, loses `affective_carryover_decay`
- habit learning: 15/20, loses contextual habit learning, immediate learning, delayed credit, ambiguity abstention, and habit temporal plasticity
- partner reliability: 19/20, loses `partner_reliability_expectation`
- concern ledger: 16/20, loses bounded concerns, existence-versus-activation, three-way suppression return, and prospective cue reactivation
- prospective commitments: 19/20, loses `prospective_cue_reactivation`
- subjective facts: 17/20, loses subjective location, hidden-world non-interference, and direct-observation revision
- eligibility trace: 15/20, loses contextual habit learning, immediate learning, delayed credit, ambiguity abstention, and habit temporal plasticity

## Interpretation

MBASE-001's exact result is not being silently extended. MBASE-002 independently re-ran the exhaustive subset test after the habit mechanism's semantics changed.

The local subset-minimality result remains stable:

> Within frozen v9.5, capacities 3/3/2, and the current 20-family demonstrated behavioral envelope, all 11 counted mechanisms are jointly required for full coverage.

This remains a local architectural result. It does not establish universal cognitive minimality or prove that a future failure cannot require a qualitatively new mechanism.
