# MBASE-001 adversarial audit review, pass 2

Corrected exhaustive run `35267334476` again found exactly one full-coverage subset, the complete 11-mechanism set. The relationship-isolation correction worked: affiliation now loses only `affiliation_pressure`, while relationship history loses only its partner-specific relationship capability.

A second hostile inspection found one remaining justified capability-probe defect before closeout.

## Valid objection: ambiguity abstention could pass vacuously

The pass-2 `ambiguity_abstention` probe asserted only that an ambiguous same-context outcome did not change habits. A subset with habit learning and/or eligibility removed also makes no update, but for the wrong causal reason: it cannot perform the corresponding unambiguous learning operation. This let the empty mechanism subset receive credit for ambiguity abstention.

Correction: preserve pass 2, then run a final exhaustive pass in which the ambiguity capability requires both halves in fresh agents: (1) a uniquely eligible context/action receives credit from the experienced outcome, proving the learning path exists; (2) two distinct live actions in the same context receive no invented credit from the ambiguous outcome. No production, capacity, mechanism definition, or other probe changes.

## Persistence/reconstruction accounting note

`persistent_reconstruction` is retained in the capability vector because it is an earned architecture-level invariant. Very small subsets can satisfy it trivially when little or no enabled causal state exists. Therefore the coverage frontier should be read as coverage of the frozen capability manifest, not as a psychometric lifelikeness score. The minimal full-coverage decision is unaffected because every substantive mechanism-specific family remains required independently.

A final corrected exhaustive pass is required before closeout.
