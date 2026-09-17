# EXP-010 Final: Minimum Information for Suppression Versus Deletion

## Decision

**PROMOTE** the capacity-three concern descendant.

Evaluated production commit: `03baf6bc6f06d3f298701a8ce66c44e00f509d50`.

Strict closeout run: `35249321377`.
Artifact: `10508776574`.

Frozen predecessor: `v9.2_unresolved_concern_persistence`, commit `bd1ca22ca58e82012f1a8237e3de4bfee4dbf59d`.

## Foundational information result

Before implementation, matched histories established a many-to-one state transition. Once the weak unresolved concern A is evicted by stronger B/C under capacity two, the complete canonical subject-owned persistent state becomes identical to a matched history in which A never existed and remains identical through later B/C resolution. No existing persistent subsystem contains A.

Therefore no deterministic policy operating only on current subject-owned state can recover which concern was lost. At least concern identity must survive.

Corrected foundation run: `35168343395`, artifact `10476051325`.

## Selected minimum representation

The target history contains exactly three simultaneously unresolved identities. The challenger changes only:

`max_concerns = 2` -> `max_concerns = 3`.

No new field, status, archive, suppression queue, return rule, timestamp, planner, memory tier, or counted mechanism was added.

The existing EXP-009 semantics remain unchanged:

- ledger membership = unresolved existence;
- scalar = current activation;
- strongest ledger entry = current active concern;
- cancellation/work resolution terminate concerns;
- bounded strength competition still destroys information beyond capacity.

A concern is therefore operationally suppressed when it remains represented but is not currently strongest. This is not a new stored status.

## Why capacity three is minimal for this target

Capacity tournament:

- capacity 2: target fails;
- capacity 3: target passes;
- capacity 4: target passes but adds no target behavior.

Capacity two cannot represent three simultaneous unresolved identities and foundation testing found no semantically legitimate redundant representation elsewhere. Capacity three is therefore the smallest tested successful representational capacity.

An identity-only overflow record was rejected before implementation because it would introduce a new storage role plus unearned rules for return activation, termination routing, overflow, same-name behavior and serialization. Reusing prospective commitments was rejected because their earned cue-triggered latent semantics are distinct.

## Reviewer evidence

Reviewer generation 1: 12/12 passed after one preserved infrastructure-only workflow failure caused by shallow Git history preventing the production-freeze check. The reviewer and production files were unchanged; rerun `35249191013` passed.

Reviewer generation 2: 10/10 passed, run `35249246180`.

Holdouts covered long dormancy, non-dominance, cancellation, work semantics, fourth-identity loss, equal-strength tie behavior, reassignment, prospective overlap, reconstruction, repeated cycles, reordered histories, no privileged history, zero-new-fields/mechanisms and explicit bounded-loss frontier.

## Historical regression

Strict closeout passed:

- repository: 72 tests + 18 subtests;
- EXP-007 adversarial generations replayed, with the historically adjudicated first-generation capacity assertion remaining raw evidence rather than a semantic regression;
- EXP-009 strict closeout replayed;
- EXP-010 development replayed;
- reviewer generations 1 and 2 replayed unchanged;
- renderer, subjective-access, serialization and earlier earned behavior remain intact.

## Cost

Mechanism count: `11 -> 11`.

Persistent field set: unchanged.

Fresh state:

- v9.2: 245 canonical / 269 diagnostic bytes;
- EXP-010: 245 canonical / 269 diagnostic bytes.

Matched two-entry state is identical: 352 canonical / 379 diagnostic bytes in the closeout fixture.

Three-entry challenger state: 382 canonical / 411 diagnostic bytes in the same normalized fixture.

Marginal third concern entry: **30 canonical bytes** for the normalized identifiers used in the closeout fixture.

Hosted-CI timing sample, median microseconds:

- fresh idle: 8.71 v9.2 vs 8.87 challenger;
- three assignments: 34.07 v9.2 vs 33.31 challenger;
- reconstruction: 34.04 for v9.2/two entries vs 45.98 for challenger/three entries.

These are engineering estimates, not speed claims.

## Second-order interpretation

### MECHANISM MINIMALITY

EXP-010 provides no evidence for a twelfth mechanism. The 11-mechanism count remains defensible for the currently earned envelope.

### REPRESENTATIONAL CAPACITY

Concern capacity two is falsified for the reproduced three-simultaneous-unresolved history. Capacity three is the smallest tested successful capacity.

### SEMANTIC MINIMALITY

No new concern semantics were required. EXP-009's existence-versus-activation distinction is retained unchanged. EXP-010 changes only how many instances of that already-earned representation can coexist.

The result therefore supports the interpretation that this failure was a representational-capacity limit, not a missing cognitive faculty.

## Bounded limitation

The experiment does **not** solve general forgetting. Capacity three moves the explicit information-destruction frontier from the third simultaneous unresolved identity to the fourth. Once a fourth stronger concern evicts a weaker identity, that identity again becomes unrecoverable from subject-owned state.

This limitation is part of the claim, not an implementation defect hidden by promotion.

## Narrow claim

### BEHAVIOR DEMONSTRATED

A third unresolved concern can remain represented but behaviorally non-dominant while two stronger concerns compete, then regain ordinary behavioral eligibility after stronger competitors terminate.

### MINIMUM INFORMATION REQUIRED

At least the displaced concern identity must survive. Under the current concern semantics, retaining the existing identity-plus-activation record is the smallest tested representation that avoids inventing a separate return-strength rule.

### CAUSAL REPRESENTATION SUPPORTED

Capacity two fails and capacity three succeeds with otherwise identical concern semantics; capacity four is unnecessary for the preregistered target.

### CLAIMS NOT ESTABLISHED

EXP-010 does not establish general goal memory, planning, BDI architecture, unbounded persistence, human working-memory capacity, general forgetting, or optimal resource arbitration.
