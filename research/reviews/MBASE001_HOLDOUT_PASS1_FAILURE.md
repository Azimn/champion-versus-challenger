# MBASE-001 sealed holdout pass 1 failure classification

Run `35267054601` executed the frozen holdout meanings after the exhaustive subset search. The full v9.3 production regression suite passed 72 tests / 18 subtests. The full mechanism set then scored 6/8 holdouts because two holdout implementations encoded assumptions not present in the sealed definitions.

## `relationship_affect`
Classification: invalid holdout implementation assumption.

The sealed definition says hostility creates both partner-specific negative relationship history and decaying threat residue. `threat_residue` is intentionally global carryover, not partner-specific affect. The implementation incorrectly required Sarah to choose idle on the first post-hostility event. At that point global threat residue legitimately biases avoidance even for Sarah. The corrected implementation must require early global affect and later, after affect decays, partner-specific relationship history to distinguish Morgan from Sarah. This changes no production or mechanism-ablation code.

## `prospective_capacity`
Classification: invalid holdout implementation assumption.

The sealed definition says a cued prospective commitment enters ordinary capacity-three concern competition and that ordinary strength-based capacity decides the represented set. The implementation incorrectly required the cued concern `d` to lose. Existing concerns have already decayed when the cue arrives; cue activation supplies the existing 0.75 concern activation, so `d` may legitimately displace the then-weaker `c`. The corrected implementation must test bounded size three and ordinary strength ordering, not preselect the loser. This changes no production or mechanism-ablation code.

Both raw failures are preserved. No subset result, production behavior, mechanism definition, capacity, or sealed holdout meaning is changed.
