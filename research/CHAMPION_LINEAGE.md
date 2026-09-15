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
| `v9_context_eligibility_trace` | EXP-007 | Bounded context-cued delayed consequence credit across intervening activity | 12 | production behavior `8c1e692e2b115200e3d758e481eb12576aced907`; closeout run `35025493280` | Current branch-local champion |

### v9 freeze note

The final EXP-007 organism stores at most two eligibility records. Each contains only `context`, `action`, and `age`. Eligibility is derived from age. Capacity one failed already-earned cross-context and multiple-candidate behavior; capacities two through four preserved the current earned suite, so two was selected as the smallest supported bound. The detailed trajectory and cost evidence are preserved in `research/results/EXP007_DELAYED_CREDIT_FINAL.md` and `.json`.

## Freeze rule

Once a champion is named for an experiment series, its code, configuration, adapter, scenario mappings, and dependency environment are frozen for that series. Bug fixes or configuration changes create a new candidate reference. They are not silently applied to the champion during comparison.
