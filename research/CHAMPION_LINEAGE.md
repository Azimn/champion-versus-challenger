# Champion Lineage

The champion lineage records only experimentally earned champions. A system is not entered as Champion 0 because it is famous, theoretically attractive, recently implemented, or convenient to modify.

## Current state

**Champion:** Unassigned  
**Reason:** No candidate has yet completed the common external baseline qualification battery in this repository.  
**Frozen reference:** None  
**Promotion experiment:** None

This global Champion 0 status is separate from the branch-local minimal-organism experimental lineage below.

## Promotion requirements

A proposed champion must have a preserved, versioned implementation reference; an adapter that does not rewrite its decision architecture; common scenario traces; longitudinal behavioral measures; old-school performance measurements; and a documented artificiality attack.

For later challengers, promotion additionally requires paired comparison against the frozen champion under identical experiences and an ablation when the challenger introduces or replaces a mechanism.

A challenger can be rejected for meaningful regressions even if its aggregate score rises. Essential behavioral dimensions are not freely exchangeable.

## Global lineage table

| Champion | System/version | Promoted by | Target improvement | Regressions accepted | Status |
| --- | --- | --- | --- | --- | --- |
| C0 | Unassigned | None | Baseline qualification | None | Pending |

## Branch-local minimal-organism lineage

This lineage records the experimentally promoted sequence used by the minimal non-LLM organism research loop. It does not assign the repository's global Champion 0.

| Version | Promotion experiment | Earned change | Counted mechanisms after promotion | Frozen production reference | Status |
| --- | --- | --- | ---: | --- | --- |
| `v5_partner_model` | EXP-002 | Partner-specific reliability expectation on top of prior relationship, affect, concern, and habit mechanisms | 8 | EXP-002 record | Historical |
| `v5_1_uncertainty_policy` | EXP-003 | Order-invariant conservative behavior near unknown partner reliability | 8 | EXP-003 record | Historical |
| `v6_bounded_concern_ledger` | EXP-004 | Multiple bounded simultaneous unfinished concerns | 9 | EXP-004 record | Historical |
| `v7_prospective_cue` | EXP-005 | Latent future commitment reactivated by an experienced environmental cue | 10 | EXP-005 record | Historical |
| `v8_subjective_fact` | EXP-006 | Subject-owned factual belief kept distinct from hidden world state | 11 | EXP-006 record | Superseded by v9 |
| `v9_context_eligibility_trace` | EXP-007 | Bounded context-cued delayed consequence credit across intervening activity | 12 | production behavior `8c1e692e2b115200e3d758e481eb12576aced907`; branch `champion-v9-context-eligibility-trace`; closeout run `35025493280` | Frozen behavioral ancestor |
| `v9.1_compact` | Global structural ablation | No new behavior; removes redundant concern compatibility state, duplicate last-action state, dead idle-habit storage, and unearned store capacity | 11 | branch `champion-v9-1-compact`; commit `2856ec6a32be0347a9243f6eff6faa404a9a0e6c`; closeout run `35051162103` | Superseded by v9.2 |
| `v9.2_unresolved_concern_persistence` | EXP-009 | Separates unresolved concern membership from momentary activation without new persistent fields or mechanisms | 11 | branch `champion-v9-2-unresolved-concern-persistence`; commit `bd1ca22ca58e82012f1a8237e3de4bfee4dbf59d`; closeout run `35138150402` | Superseded by v9.3 |
| `v9.3_concern_capacity_three` | EXP-010 | Raises existing concern-ledger capacity from two to three after proving the suppressed concern was irrecoverably absent at capacity two | 11 | branch `champion-v9-3-concern-capacity-three`; commit `a10bc27579bf5bd0ff1a90d6ad6e3f337d8ed7bc` | Superseded by v9.4 |
| `v9.4_prospective_capacity_three` | EXP-011 | Raises existing prospective identity+cue capacity from two to three after proving the evicted third commitment was irrecoverably absent at capacity two | 11 | branch `champion-v9-4-prospective-capacity-three`; commit `5f949c6e882f780e1d4c07f0b6b3bccf330936aa`; production blob `4238680bb78c21dd71b55cf279b2e4e2ce0e03a8`; closeout run `35276313274`; frozen verification run `35276731608` | Current branch-local behavioral champion |

### v9 freeze note

The final EXP-007 organism stores at most two eligibility records. Each contains only `context`, `action`, and `age`. Eligibility is derived from age. Capacity one failed already-earned cross-context and multiple-candidate behavior; capacities two through four preserved the current earned suite, so two was selected as the smallest supported bound. The detailed trajectory and cost evidence are preserved in `research/results/EXP007_DELAYED_CREDIT_FINAL.md` and `.json`.

### v9.1 structural note

Global structural ablation re-litigated accumulated mechanisms rather than adding a capability. The promoted compact descendant stores no `active_concern`, `concern_strength`, `last_action`, or `last_context` fields; concern and prospective stores were each bounded at two; eligibility remained bounded at two. The first structural closeout rejected the candidate because the inherited rounded diagnostic snapshot was not lossless across reconstruction. The corrected full-precision persistence representation passed the complete closeout without changing behavioral policy. Full evidence is preserved in `research/results/GLOBAL_ABLATION_V9_CLOSEOUT.md` and `.json`.

### v9.2 EXP-009 note

EXP-009 changed no persistent schema and added no counted mechanism. The bounded concern dictionary key/membership carries the narrow experimentally supported meaning that the named concern remains unresolved, while its existing scalar remains current activation. Ordinary drift still multiplies activation by 0.97 but no longer deletes the concern solely for crossing the old 0.08 threshold. Explicit cancellation, existing work-mediated resolution, and bounded replacement remain deletion paths.

Reviewer generation 1 produced one preserved exact-floating-point assertion failure, adjudicated as numerically invalid without production changes. Reviewer generation 2 passed 12/12. The first strict closeout was preserved as a harness rejection because it incorrectly required a concern to survive a later legitimate work-resolution event. Corrected closeout run `35138150402` passed the complete historical contract and promoted the candidate.

### v9.3 EXP-010 note

EXP-010 established a genuine information-loss boundary: with concern capacity two, a lower-priority unresolved concern can be removed from subject-owned state by temporary competition, leaving no information from which it can later return after stronger concerns resolve. The minimum successful challenger increased only the existing concern capacity from two to three. No new concern schema, dormant store, status field, or mechanism was introduced. Capacity four did not earn additional target behavior.

### v9.4 EXP-011 note

EXP-011 established the analogous prospective boundary. With prospective capacity two, a history in which `first` existed and was evicted becomes canonically byte-identical to a matched history in which `first` never existed. Because prospective recovery requires the already-earned pair of commitment identity + future cue, no zero-information policy could recover the lost commitment.

The production mutation was exactly `max_prospective = 3`. Capacity two failed, capacity three succeeded, and capacity four added no required behavior for the three-commitment target. No persistent field type, cue semantic, replacement rule, planner, rehearsal process, or counted mechanism changed. Fresh state stayed 245 canonical / 269 diagnostic bytes; occupying the third normalized prospective record cost +30 canonical / +32 diagnostic bytes relative to two entries.

Reviewer pass 1 produced one preserved invalid cross-capacity assumption: it required four cue-activated commitments to coexist in the independently bounded concern ledger of capacity three. Separate adjudication verified the prospective transitions with no production change. Reviewer pass 2 passed 31/31. Strict closeout passed on Python 3.11 and 3.12, and independent frozen-ref verification passed from commit `5f949c6e882f780e1d4c07f0b6b3bccf330936aa`.

Post-freeze revalidation eliminated `third_commitment_is_forgotten` and preserved three failures: `rewarded_routine_never_weakens`, `ancient_commitment_reactivates_unchanged`, and `deterministic_rhythm`.

## Freeze rule

Once a champion is named for an experiment series, its code, configuration, adapter, scenario mappings, and dependency environment are frozen for that series. Bug fixes or configuration changes create a new candidate reference. They are not silently applied to the champion during comparison.
