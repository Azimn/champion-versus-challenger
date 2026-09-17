# EXP-011 Final: Minimum Prospective Capacity

## Decision

**PROMOTE** the capacity-three prospective descendant.

Evaluated production commit: `359682f463393dadeef53c8fc7a8c65eef5be8b4`.
Frozen production blob: `4238680bb78c21dd71b55cf279b2e4e2ce0e03a8`.
Strict closeout run: `35276313274`.
Python 3.12 artifact: `10520497574`.

Frozen predecessor: `v9.3_concern_capacity_three`, commit `a10bc27579bf5bd0ff1a90d6ad6e3f337d8ed7bc`.
Preregistration: `9cf3cfab5259cd9e12f58e6dbf95f28eae7218d9`.

## Information lower bound

Under prospective capacity two, creating `first`, `second`, and `third` leaves only the second and third identity+cue associations. A matched history in which `first` never existed becomes canonically identical to the history in which `first` existed and was evicted. The exact EXP-011 implementation reconfirmed this before crediting the challenger.

Therefore no policy operating only on current subject-owned state can reconstruct the lost first commitment after eviction.

Prospective recovery requires more than commitment identity. It requires the already-earned pair:

- commitment identity;
- associated future cue.

Without the cue association the organism cannot determine which later experienced event should reactivate which commitment.

## Production mutation

The only production change is:

`max_prospective = 2` -> `max_prospective = 3`.

No persistent field type, status field, queue type, rehearsal process, planner, timestamp, age value, priority metadata, confidence value, decay rule, cue semantic, reactivation semantic, replacement rule, renderer behavior, or counted causal mechanism was added.

Mechanism count remains **11**.

## Capacity tournament

- capacity 2: fails the three-commitment target;
- capacity 3: preserves all three identity+cue records and later `cue_first` reactivates `first`;
- capacity 4: also passes, but adds no required behavior for the preregistered target.

Capacity three is therefore the smallest tested successful bound for this demonstrated behavior.

## Permutations and semantics

Development testing exercised six insertion permutations and multiple cue-arrival permutations, producing 54 permutation cue cases. Results depended on retained identity+cue records, not insertion position.

The inherited prospective semantics remain intact:

- wrong cues do not activate commitments;
- exact experienced cues activate their associated commitments;
- cue activation consumes that prospective binding;
- unrelated cues do nothing;
- same-identity reassignment retains the pre-existing one-value-per-identity semantics;
- distinct identities sharing one cue retain the pre-existing shared-cue behavior;
- active concerns and latent prospective commitments remain distinct representations;
- cancellation removes the targeted prospective binding;
- work-mediated concern resolution does not recreate a consumed prospective binding.

## Fourth-commitment frontier

Capacity three remains bounded. A fourth distinct prospective commitment applies the inherited replacement policy and evicts the oldest extant prospective identity+cue record. Delivering the lost record's cue does not reconstruct or reactivate it.

EXP-011 therefore moves the demonstrated information-loss frontier from the third simultaneous prospective commitment to the fourth. It does not solve general forgetting or unlimited prospective storage.

## Subjective access

Prospective retrieval remains dependent on subject-owned retained cue association plus an actually experienced cue event. Matched histories with equivalent external circumstances but different experienced cues diverged according to experienced history. Hidden simulator knowledge, external logs, and objective events not represented by the experienced cue do not reactivate commitments.

## Reconstruction

All three prospective slots survive canonical serialize/destroy/restore exactly. Cue delivery after reconstruction matches uninterrupted execution. Reconstruction was also tested after activation, removal, long latency, and overflow.

## Causal ablation

The strict closeout ablated only:

`max_prospective = 3` -> `2`.

With all other candidate behavior held constant, the original `third_commitment_is_forgotten` failure returned. Baseline and ablated conditions retained only second+third and failed to reactivate first; the capacity-three candidate retained first+second+third and reactivated first.

## Reviewer evidence

Development run `35275519835` first exposed one preserved evaluator error: the harness incorrectly required a single work action to fully resolve a concern. The production candidate was unchanged. The corrected development run `35275738887` passed on Python 3.11 and 3.12.

Reviewer generation 1 run `35275898549` produced 42/43 raw passes. Its sole failure incorrectly required four cue-activated commitments to remain simultaneously in the independently bounded concern ledger, contradicting the earned concern capacity of three. The reviewer was preserved unchanged. Separate adjudication run `35276094004` required that exact sole raw failure and verified the prospective transitions step by step. No production repair occurred.

Reviewer generation 2 run `35276185423` passed 31/31 new tests, including reordered experience, reconstruction boundaries, capacity transitions, identity-specific cancellation, long latency, subjective access, shared cues, explicit recommitment, and irreversible overflow.

Strict closeout run `35276313274` passed on Python 3.11 and 3.12, including `72 passed, 18 subtests passed` in the repository suite, development replay, reviewer-1 adjudication replay, reviewer 2, causal ablation, capacity-four comparison, state-cost audit, and reconstruction.

## Representational cost

Mechanism count: `11 -> 11`.
Persistent field set: unchanged.

Fresh state is unchanged:

- v9.3: 245 canonical / 269 diagnostic bytes;
- EXP-011: 245 canonical / 269 diagnostic bytes.

Using the normalized closeout fixture:

- one prospective entry: 303 canonical / 328 diagnostic bytes;
- two prospective entries: 348 canonical / 375 diagnostic bytes;
- three prospective entries: 378 canonical / 407 diagnostic bytes.

Marginal third entry relative to the matched two-entry state:

- +30 canonical bytes;
- +32 diagnostic bytes.

Hosted-CI timing sample from Python 3.12 closeout, median microseconds:

- insert: 12.73 v9.3 vs 12.70 challenger;
- cue cycle: 27.16 v9.3 vs 27.10 challenger;
- reconstruction: 42.50 for v9.3/two entries vs 56.02 for challenger/three entries.

These are engineering measurements, not speed claims. EXP-011 is zero-new-mechanism and zero-new-schema, but it has positive bounded occupancy cost when the third slot is used.

## Second-order interpretation

### MECHANISM MINIMALITY

MBASE-001 is unchanged. Within the current architecture, fixed experimentally earned capacities used by that audit, and demonstrated capability envelope, the 11 mechanisms remain locally subset-minimal. EXP-011 adds no twelfth mechanism.

### REPRESENTATIONAL CAPACITY MINIMALITY

For the demonstrated three-simultaneous-prospective target, capacity two is falsified and capacity three is the smallest tested successful bound. Capacity four is unnecessary for that target.

### SEMANTIC MINIMALITY

No prospective record meaning changed. The record remains exactly commitment identity + future cue association. EXP-011 changes only how many such records can coexist.

## Narrow supported claim

For the current demonstrated behavioral envelope, the existing prospective commitment mechanism requires capacity for three simultaneous identity + cue associations; capacity two causes irreversible information loss in the tested three-commitment history.

## Claims not established

EXP-011 does not establish general prospective-memory capacity, human working-memory limits, planning, rehearsal, forgetting, intention prioritization, unlimited future commitments, prospective aging, or extinction.

The separate `ancient_commitment_reactivates_unchanged` failure remains intentionally unresolved by EXP-011.
