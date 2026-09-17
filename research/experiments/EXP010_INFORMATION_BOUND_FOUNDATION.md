# EXP-010 Foundation: Suppression Versus Deletion Information Bound

## Status

Pre-archaeology, pre-preregistration. No EXP-010 challenger exists.

Frozen branch-local champion: `v9.2_unresolved_concern_persistence`  
Frozen champion branch: `champion-v9-2-unresolved-concern-persistence`  
Frozen champion commit: `bd1ca22ca58e82012f1a8237e3de4bfee4dbf59d`  
Evaluated production implementation unchanged since: `b5cc3e109ab2fa4de0421dc113009d1ee7fb050d`

Corrected foundation run: `35168343395`  
Corrected foundation artifact: `10476051325`

The workflow verified frozen production files were unchanged, passed the complete repository test suite, replayed the strict v9.2 EXP-009 closeout successfully, and then passed the corrected EXP-010 foundation.

## Preserved first foundation failure

Initial foundation run `35168160541`, artifact `10475731437`, failed only the expected fresh diagnostic byte gate. The new harness had directly compact-JSON-serialized the complete diagnostic snapshot, producing 290 bytes, rather than using the project's established `persistent_state_bytes()` diagnostic metric, which is 269 bytes for the frozen champion.

Classification: **foundation-harness metric-definition error**.

The failed harness remains unchanged. Production was not modified. The information-loss comparison in that failed run already produced the same state-identity result later confirmed by the corrected foundation.

## Frozen baseline reconstruction

The corrected foundation confirmed:

- 11 counted persistent causal mechanisms;
- 269-byte fresh diagnostic persistent state;
- 245-byte fresh canonical persistent state;
- concern capacity 2;
- prospective commitment capacity 2;
- eligibility trace capacity 2;
- complete historical/reviewer contract still passes;
- strict v9.2 closeout still passes.

The selected failure reproduced exactly:

1. assign `low_priority` with intensity 0.5 -> concern strength 0.375;
2. assign `urgent_one` with intensity 1.0 -> `low_priority` 0.36375, `urgent_one` 0.75;
3. assign `urgent_two` with intensity 0.9 -> capacity keeps `urgent_one` 0.7275 and `urgent_two` 0.675; `low_priority` is absent;
4. cancel `urgent_one` -> only `urgent_two` 0.65475 remains;
5. cancel `urgent_two` -> concern ledger is empty.

`low_priority` does not return.

## Matched-history information-loss test

A naive comparison between "A existed" and "A never existed" is confounded because a task-assignment event also advances time and changes ordinary need state. The experiment therefore used identity-matched histories with identical event types, intensities, counts, and non-concern side effects.

### History A

- weak concern identity = `low_priority`, intensity 0.5;
- then `urgent_one` 1.0;
- then `urgent_two` 0.9;
- cancel `urgent_one`;
- cancel `urgent_two`.

### History B

- `low_priority` never exists;
- a different weak identity, `matched_control`, receives the same intensity-0.5 assignment event;
- then the identical `urgent_one`, `urgent_two`, and cancellation sequence.

Before capacity eviction the canonical organism states differ only because the weak concern identities differ. At the third assignment, both weak concern identities are evicted.

**At that exact point the complete canonical persistent organism states become byte-identical.**

They remain byte-identical after the first stronger concern resolves and after the second stronger concern resolves.

## Existing-state trace search

After eviction, no subject-owned representation contains `low_priority`:

- concern ledger: absent;
- prospective commitments: absent;
- habits: absent;
- relationships: absent;
- partner reliability: absent;
- subjective location beliefs: absent;
- eligibility records: absent;
- canonical serialized state: no identity occurrence.

The remaining canonical state also contains only the ordinary needs, affect residue, tick, and the other earned stores. Because the matched histories are byte-identical after eviction, none of those fields encodes which weak concern previously occupied the lost slot.

## Information lower bound

The experiment establishes a direct representational lower bound:

> At least the evicted concern's identity must remain in subject-owned causal state if the organism is later to distinguish "this unfinished concern existed and was temporarily displaced" from "this concern never existed."

Under frozen v9.2, the two histories map to exactly the same internal persistent state after eviction. Therefore any deterministic policy whose inputs are restricted to current subject-owned state must behave identically from that point onward under identical future inputs.

A zero-retained-information recovery of `low_priority` is impossible without either:

- external or privileged history unavailable to the subject; or
- new/expanded subject-owned representation that preserves at least enough information to distinguish the histories.

EXP-010 must not use the former.

This lower bound does **not** yet establish that historical strength must be retained. Identity is necessary. Whether strength is necessary remains an empirical design question because return activation might be derived from existing rules, continue decaying in the existing concern representation, or be reset by an already-earned reassignment rule.

## Causal characterization of loss

The frozen concern ledger keeps the two entries with the highest **current concern strengths**. The failure is therefore driven by fixed capacity plus strength ordering, not by recency alone.

Observed permutations:

- old and weak A is lost when stronger B and C arrive;
- recent but weak A is also lost;
- old but sufficiently strong A survives while a weaker new C is rejected;
- cancelling B before C or C before B does not restore A after A has already been evicted;
- a long unrelated delay before B/C resolution does not restore A;
- nominally equal assignment intensities are not an exact tie after sequential drift because earlier concerns have already decayed when later concerns arrive.

Thus the selected failure class is not one scripted order. It is **complete destruction of an unresolved identity when it loses bounded strength competition**.

## Semantic boundary entering archaeology

For EXP-010 analysis:

- **active concern**: the currently strongest represented concern, as derived by existing policy;
- **low-activation concern**: represented unresolved concern whose scalar activation is small;
- **suppressed concern**: candidate semantic category for an unresolved identity temporarily ineligible to win current competition while its existence remains causally representable;
- **evicted concern under v9.2**: concern whose identity/value are removed from subject-owned persistent state because capacity competition discarded it;
- **resolved concern**: concern removed by existing work-mediated resolution;
- **cancelled concern**: concern removed by explicit task cancellation.

EXP-009 established that low activation is not deletion. EXP-010 now asks whether capacity displacement should remain deletion or whether the minimum concern representation must preserve a bounded distinction between displacement and resolution.

No answer is selected in this foundation record. Internal archaeology, narrow prior art, and explicit minimum-candidate comparison must occur before preregistration and before any challenger implementation.
