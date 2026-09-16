# EXP-008 Final Result: Existing-State Search Interaction

## Final decision

**REJECT**

The frozen champion remains:

- version: `v9.1_compact`
- branch: `champion-v9-1-compact`
- commit: `2856ec6a32be0347a9243f6eff6faa404a9a0e6c`
- counted persistent causal mechanisms: 11

The repaired EXP-008 production candidate remains experimental evidence only:

- production commit: `c42a43d353b21061b97cabb665e8ef59544d27c9`
- no new persistent field category
- no new counted persistent mechanism

It is not promoted and must not be inherited as champion cognition.

## Reproduced failure

Frozen v9.1 directly observes an entity at a location, repeatedly searches that location, accumulates an existing negative contextual action value down to `-1.0`, and nevertheless continues to choose the last-observed location because search scoring ignores the learned action value.

The failure reproduced across novel entity/location names, neutral task contexts, and action-order permutations.

## Experiment trajectory preserved

EXP-008 did not proceed as a single clean implementation.

1. The first implementation exposed a persistence-key encoding defect.
2. Two development assumptions were found to violate EXP-007's already-earned same-context ambiguity-abstention semantics.
3. A delimiter-safe entity/task-qualified representation corrected the key defect without new persistent state.
4. The corrected development implementation fixed the repeated-failure target.
5. Reviewer generation 1 then exposed a substantive fresh-reobservation failure: a `-1.0` learned search value could overpower a newer direct observation at the same location.
6. A minimal repair made direct observation delete only negative matching search values for the same entity/location while preserving positive search values, other locations/entities, non-search values, and eligibility traces.
7. Reviewer generation 1 replayed unchanged and passed 7/7.
8. Reviewer generation 2 ran untouched against the frozen repaired production. Nine of ten probes passed. The sole raw failure, `matching_negative_only`, was classified as an invalid reviewer assumption because the supposedly preserved second-location negative value had never been learned under EXP-007's ambiguity contract. The original reviewer source and failure are preserved.
9. Complete closeout then identified a deeper semantic problem that blocks promotion.

## Reviewer generation 2

Untouched reviewer-2 run:

- run: `35061378333`
- artifact: `10432691986`
- frozen production verification passed before reviewer execution.

Raw result: 9/10 probes passed.

Passed attacks included:

- hidden-world non-interference;
- preservation of positive search experience;
- preservation of another entity's negative experience;
- preservation of non-search learned state;
- live eligibility preservation;
- serialization after invalidation;
- Unicode/delimiter-heavy entity specificity;
- cross-task matching-location invalidation;
- proportionate delayed old negative evidence.

The raw failing `matching_negative_only` probe assumed two negative location values existed in one task/entity context. EXP-007 had correctly abstained from learning the second because two distinct actions were simultaneously live in that context. A follow-up diagnostic using causally unambiguous histories confirmed that when both negative values genuinely exist, direct observation of drawer removes only drawer and preserves shelf.

See `research/reviews/EXP008_REVIEW_PASS2.md`.

## Complete mechanical closeout

Complete closeout run:

- run: `35061913740`
- artifact: `10432841218`

Production was verified unchanged from `c42a43d...`.

The repository regression suite passed 61/61 tests. The explicit v9.1 structural closeout also passed fully.

Two legacy EXP-008 development checks remained raw failures because they demand credit assignment after creating multiple live actions in one experienced context. They are preserved and classified in `research/reviews/EXP008_DEVELOPMENT_REPLAY_CLASSIFICATION.md`; the rest of the historical/earned/EXP-007/renderer/serialization contract remained green.

Additional closeout diagnostics passed:

- reviewer-2 intended location-isolation behavior under an unambiguous history;
- all tested temporal contradiction histories;
- subject-access information boundary;
- adversarial key-identity uniqueness and persistence round trip;
- cross-task selectivity under the current search interpretation;
- preservation of positive search experience;
- preservation of unrelated non-search experience;
- live eligibility-trace behavior;
- serialize/destroy/restore/continue in both required invalidation orders;
- mechanism count unchanged at 11;
- fresh state unchanged.

## Negative search-value semantics

This is the promotion-blocking finding.

The learned store is historically:

`habits[(context, action)] -> scalar`

It is updated from the runtime's generic scalar `Event.reward`.

Its demonstrated uses before and during EXP-008 include:

- reward-shaped contextual routine preference, such as the EXP-002 morning-walk habit;
- positive and negative delayed consequences of arbitrary actions in EXP-007;
- qualified search success/failure action value in EXP-008.

The runtime does not encode an outcome type that distinguishes:

1. `I searched for X at Y and failed to locate it`, from
2. `performing the search action at Y was costly, unpleasant, ineffective, or otherwise negatively rewarded`.

A direct observation of X at Y contradicts interpretation 1. It does not necessarily contradict interpretation 2.

The repaired invalidation rule deletes a matching negative scalar under either interpretation because both produce the same persistent state. Therefore the rule can erase historically valid generic action utility while treating it as though it were contradicted epistemic evidence.

This violates the required semantic gate.

## Minimum-operation audit

For a **purely epistemic** failed-to-locate value:

- sparse deletion and reset-to-neutral are behaviorally equivalent;
- sparse deletion stores less state and is therefore the smaller operation;
- a positive counter-update would assert unsupported positive success;
- preserving the full negative fails the fresh-reobservation case.

But because the current scalar is not known to be purely epistemic, there is no unconditional correct operation among deletion, neutral reset, positive counter-update, or preservation.

A temporary observation-priority policy without mutating learned history is not available under the present state contract: after observing the same location again, `location_beliefs[entity]` contains the same location string as before, so later action selection has no signal indicating that this observation is newer than the old action experience.

Adding recency, confidence, typed outcome, or another persistent representation would exceed EXP-008 and was therefore not introduced.

## Temporal contradiction result

The implemented rule passed the tested alternating histories. In particular:

- old failures do not permanently overpower a newer direct observation;
- a direct observation does not make the organism permanently optimistic;
- later experienced failures can relearn a negative expectation and again cause avoidance;
- hidden-world changes do not trigger reconciliation.

These are mechanically useful results but do not resolve the value-semantics ambiguity.

## Information boundary

Passed.

Matched agents with the same prior experienced state were given either:

- a direct subject-accessible observation; or
- only a hidden simulator-world change.

Only direct observation caused invalidation. Behavior diverged according to experienced history rather than simulator truth.

EXP-008 therefore did not introduce an observed subjective-access leak.

## Key and identity audit

Passed under the current runtime contract.

Percent-encoded derived contexts remained distinct across:

- delimiter-heavy identifiers;
- prefix/suffix relationships;
- numeric-like identifiers;
- one-character/minimal supported fragments;
- Unicode;
- pairs that collide under naive concatenation.

Canonical persistence round-tripped those identities exactly.

Entity and task qualification are causally supported. Entity-blind and task-blind diagnostic variants reintroduced cross-entity and cross-task contamination respectively.

## Positive evidence and cross-task behavior

Direct observation preserved positive matching search values and unrelated non-search learned state.

Negative search values matching the same entity/location were cleared across search-task contexts. That is coherent only if those values mean failure to locate the entity there. It is not necessarily coherent if a task-specific negative value includes non-epistemic search cost or difficulty.

Positive and negative outcomes for one context/action do not coexist as separate histories. They collapse into one net scalar. EXP-008 does not add separate positive/negative histories.

## Eligibility-trace interaction

Passed.

Direct observation does not erase live eligibility records. An unrelated live contextual action retained eligibility and later received delayed consequence credit while search-value reconciliation occurred independently.

## Persistence

Passed in both required directions:

1. negative experience -> serialize -> destroy/restore -> direct reobservation -> continue;
2. negative experience -> direct reobservation/invalidation -> serialize -> destroy/restore -> continue.

Unrelated learned state survived reconstruction exactly.

## Causal ablation

The experiment separates two different effects.

### Original repeated-failure target

- frozen `v9.1_compact`: `search:drawer`
- EXP-008 challenger: `search:shelf`
- challenger with observation invalidation disabled: `search:shelf`
- challenger with learned search value removed from scoring: `search:drawer`

Therefore **qualified learned-value scoring is causal for the original repeated-failure improvement**. Observation-triggered invalidation is not.

### Fresh same-location reobservation target

When invalidation alone is disabled, the agent stays with `search:shelf` before and after directly reobserving the book in the drawer.

Therefore **observation-triggered invalidation is causal for the reviewer-1 fresh-reobservation correction**.

### Identity qualification

Entity-blind and task-blind variants reintroduced contamination. Qualified identity is therefore behaviorally necessary for the tested interaction.

## Cost audit

Normalized cost run:

- run: `35062110019`
- artifact: `10432713139`

The established v9.1 project metrics use `persistent_state_bytes()` over the diagnostic snapshot:

- fresh: 269 bytes for both v9.1 and EXP-008;
- representative: 577 bytes for both;
- maximum bounded-store fixture: 577 bytes for both;
- mechanisms: 11 for both.

The separate canonical full-precision persistence payload is:

- fresh: 245 bytes for both;
- representative: 533 bytes for both;
- maximum bounded fixture: 533 bytes for both.

EXP-008 does have representational cost once search history exists. With matched 8-character source entity/task identifiers:

- 1 entry: 305 canonical bytes EXP-008 vs 277 v9.1;
- 16 entries: 1,220 vs 772;
- 128 entries: 8,052 vs 4,468.

This is approximately 28 additional canonical serialized bytes per qualified search entry in the 128-entry audit.

Hosted-CI medians in this run were approximately:

- search decision: 14.51 us EXP-008 vs 11.69 us v9.1;
- search outcome update: 5.83 us vs 2.63 us;
- observation with 128 stored histories: 58.31 us vs 52.49 us;
- reconstruction with 128 histories: 63.29 us vs 54.20 us.

These are engineering estimates, not precise performance claims. They establish only that EXP-008 is not zero-cost even though it adds no counted mechanism.

## Second-order critique

See `research/reviews/EXP008_SECOND_ORDER.md`.

The decisive points are:

- the original behavioral inconsistency is genuine;
- the smaller search-scoring interaction is causally supported;
- the observation-deletion repair is mechanically selective;
- direct perception remains subject-bound;
- identity qualification is necessary;
- but the generic learned scalar cannot tell contradicted epistemic evidence from still-valid utility;
- direct observation therefore receives unjustified authority over part of the generic action-value store;
- no human-observer study was conducted;
- and promoting the candidate would inherit a broader semantic claim than the representation supports.

## BEHAVIOR DEMONSTRATED

The experiments demonstrate that:

- frozen v9.1 can ignore strong existing negative search experience because search scoring bypasses the existing habit/action-value signal;
- including an entity/task-qualified existing learned value in search scoring changes that longitudinal behavior without adding persistent fields or a counted mechanism;
- entity/task qualification prevents demonstrated cross-entity and cross-task contamination;
- the repaired invalidation policy can mechanically make newer direct observation regain behavioral priority and can do so selectively in the tested histories;
- later failures can relearn negative search value after observation;
- hidden simulator state does not trigger the reconciliation;
- persistence, eligibility, positive evidence, and unrelated learned state can remain intact under the implemented rule.

## CAUSAL INTERACTION SUPPORTED

Supported causal statements are limited to:

1. **Search-scoring interaction:** using already-existing qualified learned action value during search scoring is causal for the original repeated-failed-search correction.
2. **Identity qualification:** preserving target entity and task identity is causal for preventing the tested contamination failures.
3. **Observation invalidation:** deleting matching negative search entries is causal for the specific fresh-same-location reobservation correction.

The third statement is causal about behavior, not a validation that deletion is semantically correct cognition.

## CLAIMS NOT ESTABLISHED

EXP-008 does **not** establish:

- coherent general reconciliation of factual observation and learned utility;
- general belief revision;
- general epistemic reasoning;
- causal inference;
- memory consolidation;
- a principled typed distinction between search failure and search cost;
- separate positive and negative evidence histories;
- confidence or recency reasoning;
- improved human-perceived lifelikeness.

## Strict decision

**REJECT**

Reason: the repaired candidate satisfies the mechanical interaction tests but fails the mandatory semantic criterion. The existing generic reward-shaped action scalar cannot identify which negative information a new direct observation actually contradicts. Selective deletion is therefore not justified for every persistent state the current representation permits.

`v9.1_compact` remains the frozen champion unchanged.

## Follow-up discipline

Do not turn this rejection into an immediate typed-outcome/confidence/recency feature proposal. First revalidate the six previously reproduced longitudinal failures against exact frozen `v9.1_compact`, select the strongest remaining observable failure, and test whether an interaction among already-earned mechanisms can explain it before proposing new persistent machinery.
