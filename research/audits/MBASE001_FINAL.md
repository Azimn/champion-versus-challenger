# MBASE-001 final mechanism-basis audit

## Decision

**CLOSED.** No production v9.3 behavior was modified.

Under exact frozen `v9.3_concern_capacity_three`, fixed capacities (concerns 3, prospective 2, eligibility 2), and the frozen tested behavioral envelope, the 11 counted persistent causal mechanisms form a **local subset-minimal basis**. Exhaustive enumeration of all 2048 subsets found exactly one full-coverage subset: the complete 11-mechanism set.

This is a local result about this architecture and these demonstrated consequences. It is not a claim that 11 mechanisms are universally necessary, sufficient for personhood, or minimal across alternative architectures.

## Verification and behavioral frontier

Independent frozen verification run `35249449797` checked the exact v9.3 ref and evaluated production bytes, then passed the repository contract, EXP-010 evaluation, both EXP-010 reviewers, and strict closeout. Separate post-v9.3 revalidation run `35249531720` again verified production bytes and closeout before replaying the preserved failure queue.

EXP-010's suppressed-concern failure is eliminated. Four failures remain reproduced: rewarded routine never weakens; ancient prospective commitment reactivates unchanged; third prospective commitment is forgotten at capacity two; deterministic six-action rhythm.

## Audit methodology

The behavioral manifest and 11-mechanism inventory were frozen before exhaustive results. Capacities remained fixed. The EXP-003 uncertainty policy remained fixed as a zero-persistent-state causal policy and was not reclassified as one of the 11 mechanisms.

The first exhaustive pass was not accepted uncritically. Hostile review found that the partner-specific relationship probe was contaminated by global affect. A second pass isolated relationship history after affect decay. A second hostile review then found that ambiguity abstention could pass vacuously in organisms unable to learn at all. The final pass required an unambiguous learning control before ambiguous abstention counted. Both earlier matrices and objections remain preserved.

Final corrected exhaustive run: `35267544831`, artifact `10516954416`. Full repository regression immediately before enumeration: 72 tests plus 18 subtests passed.

## Final coverage frontier

Best observed manifest coverage out of 19 mechanism-discriminating families by mechanism count:

- 0 mechanisms: 2/19
- 1: 5/19
- 2: 8/19
- 3: 9/19
- 4: 12/19
- 5: 13/19
- 6: 14/19
- 7: 15/19
- 8: 16/19
- 9: 17/19
- 10: 18/19
- 11: 19/19

The two residual families available with zero counted mechanisms are fixed architecture-level behavior/invariants rather than evidence of cognition without state: EXP-003's zero-state uncertainty policy and trivial reconstruction of an organism with no enabled persistent mechanism state. The frontier is therefore a coverage frontier for the frozen manifest, not a scalar lifelikeness score.

## Single-ablation necessity

Every mechanism has at least one earned family that disappears when it is absent. Seven mechanisms have a narrow unique signature in this envelope: fatigue -> fatigue pressure; affiliation -> affiliation pressure; competence -> competence pressure; relationship history -> partner-specific relationship behavior; affect residue -> affective carryover/decay; partner reliability -> reliability expectation; prospective commitments -> prospective cue reactivation.

Four mechanisms currently have broader leverage. Subjective facts support three fact-related families. Concern ledger supports bounded unresolved concerns, existence-versus-activation, three-way suppression/return, and prospective cue expression. Habit learning and eligibility trace each participate in four learned-action families after structural compaction removed obsolete last-action persistence.

Frequency is not psychological importance. It is observed leverage under this test envelope.

## Observable nonlinear interactions

Two strict pairwise synergies were found where the relevant capability is observed with both mechanisms but cannot be obtained with A-only, B-only, or neither anywhere in the enumerated architecture:

1. Habit learning + eligibility trace: contextual habit learning, compact immediate action learning, bounded delayed credit, and nonvacuous ambiguity abstention.
2. Concern ledger + prospective commitments: prospective cue reactivation.

These are behavioral interactions, not merely code-call dependencies.

## Sealed holdouts

The first holdout execution (`35267054601`) preserved two invalid holdout implementation assumptions: it accidentally treated global affect as partner-specific, and it preselected which concern should lose a capacity competition rather than allowing the existing strength rule to decide. Both were documented before correction; production and ablation code did not change.

Corrected holdout run `35267172876` passed all 8/8 interactions for full v9.3. There was no smaller historical full-coverage candidate to challenge. Selected ten-mechanism near-minimal subsets showed additional interaction losses. The minus-competence subset happened to pass all seven applicable interaction holdouts, but remains behaviorally non-equivalent because it fails the independently earned competence-pressure family.

## Mechanism minimality

**Result:** 11/11 are required for full demonstrated coverage within current v9.3. No multi-removal combination produced a hidden smaller full-coverage architecture. Exhaustive search therefore strengthens the earlier single-ablation evidence and specifically rejects a monotonicity shortcut.

## Representational-capacity minimality

This audit deliberately did not reoptimize capacity. Current earned bounds are concern=3, prospective=2, eligibility=2. EXP-010 directly falsified concern capacity two for the earned concern-continuity envelope and found three to be the minimum tested successful value. Prospective and eligibility capacity two remain their current earned bounds, not universal minima.

Projected subset byte counts remove disabled fields from an audit snapshot to estimate state cost. They are not claims that 2048 independent production serializers were implemented. Full v9.3 remains 245 fresh canonical bytes / 269 diagnostic bytes under the established production metrics.

## Semantic minimality

Several behavioral gains did not require new persistent mechanisms. EXP-003 corrected uncertainty decision semantics with no persistent state. EXP-009 separated unresolved existence from current activation without adding state. EXP-010 demonstrated a different case: information was genuinely absent, but the minimum correction was additional bounded capacity inside the existing concern mechanism rather than another mechanism.

This distinction is now empirically important: mechanism minimality, representational-capacity minimality, and semantic minimality are separate dimensions.

## Adversarial conclusion

The strongest surviving objection is scope, not an observed smaller subset. The current mechanism boundaries partly reflect the present implementation interfaces and earned behavior definitions. Another architecture might combine or factor these causal roles differently. MBASE-001 therefore supports **subset minimality of the current v9.3 basis**, not ontological independence of eleven universal cognitive primitives.

The audit also found no evidence that state migrated into the environment, renderer, or test harness to rescue disabled mechanisms. Capacities remained fixed. Disabled mechanism contributions were gated without replacement behavior. The final relationship and ambiguity corrections reduce two identified test-specific artifacts rather than changing production.

## Next boundary

MBASE-001 closes before EXP-011. Behavioral evolution should resume from the already-revalidated four-failure frontier using the now-established diagnostic order: information already present -> semantics -> mechanism interaction -> capacity -> only then genuinely missing mechanism.
