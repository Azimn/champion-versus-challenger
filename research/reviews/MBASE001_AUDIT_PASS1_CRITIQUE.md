# MBASE-001 adversarial audit review, pass 1

The first exhaustive run (`35266460117`) found no full-coverage subset below 11, but hostile review identified one justified methodology defect before interpreting leverage or synergy.

## Valid objection: relationship probe was contaminated by global affect

`probe_relationship` generated repeated hostility toward Morgan and immediately compared Morgan with unexperienced Sarah. Because threat residue is global carryover, not partner-specific, the probe's Sarah outcome can depend on affect and affiliation as well as relationship history. This caused the first-pass single ablation of affiliation to appear to remove `partner_specific_relationship_history`, overstating cross-mechanism dependence.

This does not create a smaller full-coverage subset by itself because affiliation already has its independently earned `affiliation_pressure` capability. It does, however, make the mechanism-leverage and interaction interpretation methodologically impure.

Correction: preserve the first 2048 rows, then run a second exhaustive audit with only the relationship capability probe changed. After hostility, allow 35 unrelated events so global threat residue falls below immediate behavioral control, then compare `avoid:morgan` versus `idle` and `avoid:sarah` versus `idle`. Morgan should retain partner-specific avoidance while Sarah does not. No production, capacity, mechanism definition, or other probe changes.

## Other objections reviewed

- Disabled base-need scalars still numerically drift in the audit object, but their scoring contribution is explicitly gated off and projected subset persistence excludes them. They are inert audit residue, not hidden causal state.
- Subset byte counts are projected canonical audit snapshots, not claims that 2048 production serializers were separately implemented. This is appropriate for relative state-cost accounting but must be labeled as projected cost.
- Renderer invariance is absent from the 19 mechanism-discriminating probes because it is mechanism-independent. It remains part of the frozen earned manifest and is verified by the unchanged repository regression contract for the full champion.
- The fixed EXP-003 uncertainty policy remains active when partner reliability is absent. This is intentional under the preregistered counting rule because it has no persistent state and is not one of the 11 counted mechanisms. The audit therefore tests the 11 persistent causal mechanisms while holding zero-state architecture policy fixed.
- Habit learning and eligibility trace jointly support compact immediate as well as delayed learning after v9.1 removed obsolete last-action state. Their apparent dependence is therefore a real current-architecture interaction, not automatically an ablation leak.
- Concern/prospective dependence is also structurally meaningful: the prospective mechanism stores a latent cue binding, while cue activation becomes an ordinary concern. Removing the concern mechanism legitimately prevents that behavioral expression.

A corrected exhaustive pass is required before MBASE-001 closeout.
