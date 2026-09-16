# EXP-008 Second-Order Methodological Critique

## Scope

This review attacks the interpretation of EXP-008 after the repaired production implementation `c42a43d353b21061b97cabb665e8ef59544d27c9` completed its mechanical closeout.

Relevant evidence:

- reviewer generation 2 run `35061378333`, artifact `10432691986`
- full closeout run `35061913740`, artifact `10432841218`
- normalized cost run `35062110019`, artifact `10432713139`
- preserved reviewer-2 classification: `research/reviews/EXP008_REVIEW_PASS2.md`
- preserved development replay classification: `research/reviews/EXP008_DEVELOPMENT_REPLAY_CLASSIFICATION.md`

Production remained unchanged from `c42a43d...` throughout these closeout runs.

## Did EXP-008 fix a genuine behavioral inconsistency?

**Yes, partially.** Frozen v9.1 possessed both a last-observed location fact and negative learned action experience, but search scoring ignored the learned value. Adding the existing qualified learned value to search scoring causally changed repeated failed-search behavior. Frozen v9.1 continued to search the believed location after the learned value reached `-1.0`; EXP-008 eventually chose the alternative.

That gain is not caused by observation-triggered invalidation. A `NoObservationInvalidation` ablation still fixes the original repeated-failure target. A `NoSearchScoreInteraction` ablation restores the original failure. Therefore the original EXP-008 target supports a narrower result: **search action selection was ignoring relevant already-earned action experience.**

## Did the later invalidation rule fix a real reviewer failure?

**Mechanically, yes.** Reviewer generation 1 showed that after the policy learned strong negative search experience, a newer direct observation at the same location could not restore the directly observed location to behavioral priority. Disabling only invalidation reproduces that reviewer failure.

However, causal necessity for one reviewer scenario is not sufficient to establish semantic correctness.

## What does the negative search scalar mean?

The existing `habits[(context, action)] -> scalar` representation was not created as a search-specific epistemic belief.

Its demonstrated lineage is broader:

1. EXP-002 v4 used it as reward-shaped contextual routine preference, such as learning a morning walk.
2. EXP-007 used the same scalar and the same generic `Event.reward` channel for positive and negative delayed consequences of arbitrary actions.
3. EXP-008 reused that scalar for qualified search actions.

There is no stored outcome type distinguishing:

- `I searched here and failed to locate the entity`, from
- `searching here was costly, unpleasant, ineffective, or otherwise negatively rewarded`.

Those interpretations are behaviorally distinguishable but persist as the same state.

A new direct observation of entity X at location Y strongly contradicts the first interpretation. It does not necessarily contradict the second. The current invalidation rule deletes the negative scalar in both cases because the organism has no information with which to distinguish them.

This is the decisive semantic problem.

## Is deletion the minimum correct reconciliation operation?

Only conditionally.

If a negative value were known to mean purely `failed to locate X at Y`, sparse deletion is equivalent to resetting the value to neutral and is the smaller representation. A positive counter-update would overclaim because seeing the entity does not demonstrate that searching is positively rewarding. Preserving the entire negative value fails the fresh-reobservation behavior.

But the current runtime cannot establish that the negative scalar is purely epistemic. Therefore no unconditional operation among deletion, neutral reset, positive counter-update, or preservation is correct for all meanings admitted by the existing state.

A temporary observation-priority rule that preserves historical action value would require some persistent or event-carried indication that the observation is newer than the stored experience. After a same-location observation, `location_beliefs[entity]` contains exactly the same location string as before; no observation-recency signal exists. Adding such information would exceed the current EXP-008 hypothesis and must not be smuggled into this experiment.

## Does deletion destroy historically valid information?

Potentially yes. If the negative scalar includes non-epistemic action utility, direct observation deletes still-valid history about difficulty, cost, or undesirability of the search action.

The mechanical tests cannot distinguish this case because `Event.reward` does not identify why reward was negative.

## Did a utility silently become a belief?

The risk is substantial enough to block promotion. EXP-008 uses a generic action-value scalar as evidence about search success, then treats direct factual observation as authority to erase negative entries. This gives the scalar belief-like semantics during reconciliation even though its historical contract remains generic utility/reward-shaped preference.

The problem is not naming. It is representational indistinguishability.

## Did a belief silently become a utility?

Search scoring intentionally combines the subjective location fact with learned action value. That interaction is defensible for action selection and is causally supported by the original target. The location fact itself is not rewritten by negative outcomes, so EXP-008 does not directly collapse factual belief into utility.

## Did simulator truth leak into subject state?

No leak was found. The matched information-boundary audit passed: direct subject-accessible observation reset the targeted negative entry, while an otherwise matched `hidden_world_change` did not. Behavior followed experienced history rather than simulator-only relocation information.

## Does a new observation erase too much learned state?

Mechanically, the implementation is selective:

- matching negative search entries are removed;
- positive matching search experience is preserved;
- other locations are preserved when they genuinely exist;
- other entities are preserved;
- unrelated non-search habit state is preserved;
- eligibility records are preserved.

Reviewer generation 2's sole raw failure (`matching_negative_only`) was an invalid test assumption: the supposedly preserved second-location negative value had never been learned because the test violated EXP-007 same-context ambiguity abstention. A follow-up diagnostic with unambiguous histories demonstrated drawer negative reset while shelf negative remained intact.

Selectivity does not resolve the semantic ambiguity of the value being selected for deletion.

## Can later contradictory experience reverse the observation effect?

Yes. Temporal contradiction tests passed. After a direct observation removes a negative matching entry, later experienced failures can learn a new negative value and eventually cause avoidance again. The organism is not permanently optimistic after observation.

## Is identity representation collision-safe?

Under the tested contract, yes. Percent-encoded actor/task components remained distinct for delimiter-heavy strings, prefix/suffix pairs, numeric-like identifiers, Unicode, and serialization round trips. Empty actor/context identifiers are not legal behavioral identities because the runtime contract truth-tests those fields; minimal one-character and numeric-string identifiers were tested instead.

Entity and task qualification are behaviorally causal rather than decorative. Isolated entity-blind and task-blind diagnostic variants reproduce cross-entity and cross-task contamination.

## Does the test suite merely favor the chosen entity/task decomposition?

The decomposition is partly implementation-shaped, but its necessity is independently supported by contamination ablations: without entity identity, one object's failures affect another object; without task identity, one task's failures affect another task. That supports qualified identity for this experiment's demonstrated contexts.

It does not prove this decomposition is universally sufficient for all search semantics.

## Are cross-task invalidation semantics coherent?

The current rule invalidates matching negative **search** entries across task contexts for the same entity and directly observed location. This is defensible only if those negatives mean failure to locate the entity there. It is not defensible for a task-specific negative meaning such as difficulty retrieving, accessing, carrying, asking about, or otherwise acting on the entity.

EXP-008 correctly leaves non-search actions untouched, but the generic reward scalar means even search actions may contain task-specific non-epistemic utility. This reinforces the semantic rejection.

## Positive and negative evidence representation

Positive matching search experience is preserved by direct observation. However, positive and negative outcomes for the same context/action do not coexist as separate histories. They are folded into one bounded net scalar.

That is an accepted limitation of the current architecture, not a reason to add richer memory in EXP-008. It does mean the system cannot later recover which component of a net value was epistemic versus utility-based.

## Eligibility-trace interaction

Passed. Direct observation does not clear live eligibility records. An unrelated live contextual action retained eligibility and subsequently received delayed credit while the search value remained unaffected. EXP-008's reconciliation operates on persistent learned value, not the temporal-credit substrate.

## Persistence and reconstruction

Passed in both required orders:

1. negative search experience -> serialize -> destroy/restore -> direct observation -> continue;
2. negative search experience -> direct observation/invalidation -> serialize -> destroy/restore -> continue.

Unrelated positive, negative, and non-search habit values survived reconstruction. Key qualification and invalidation state were preserved exactly.

## Semantically equivalent reordered histories

The tested temporal histories tolerate multiple interleavings of failure, observation, hidden change, and later failure while producing the expected direction of behavior. However, the underlying habit scalar is bounded and updated sequentially; arbitrary permutations of positive and negative rewards are not guaranteed to be mathematically commutative, especially near saturation. Temporal order can legitimately matter, so order equality is not adopted as a universal requirement.

No evidence was found that mere candidate-action ordering determines the EXP-008 choice once scores differ.

## Is direct observation unjustifiably privileged?

For factual location state, direct perception already has earned authority from EXP-006 and hidden-world non-interference. That privilege is justified for replacing `location_beliefs`.

It is **not automatically justified for erasing generic action utility**. EXP-008 extends perceptual authority from the factual store into the generic habit/action-value store without having outcome semantics sufficient to know that the targeted negative value is contradicted. This is precisely where the experiment overreaches.

## Could the same original gain emerge from a smaller rule?

Yes. The original repeated-failed-search target is fixed by a smaller interaction: include the already-existing qualified learned search value during action scoring. Observation-triggered invalidation is not needed for that original target.

The invalidation rule was introduced only after reviewer generation 1 exposed a second problem involving newer direct evidence. Because the current representation cannot solve that second problem without semantic ambiguity, the smaller supported result should be retained as evidence rather than promoting the broader repaired candidate.

## Would a human observer notice the corrected behavior?

The action difference is externally observable and plausibly perceptible longitudinally: repeatedly searching a failed location and ignoring a fresh direct observation are both obvious behavioral inconsistencies. No human-observer study was conducted, so EXP-008 cannot claim a measured increase in perceived lifelikeness.

## Cost interpretation

Architectural mechanism cost is zero: no new persistent field category and mechanism count remains 11.

Representational and execution cost are nonzero. With matched 8-character source identifiers, entity/task qualification adds approximately 28 canonical serialized bytes per learned search entry in the 128-entry audit. At 128 entries, canonical learned-state payload size was 8,052 bytes for EXP-008 versus 4,468 bytes for v9.1. Search scoring and search-update paths were also slower in the hosted CI sample. Observation invalidation scans the existing habit mapping, so its cost grows with that store.

These measurements are engineering estimates and do not justify precise performance claims, but they rule out describing EXP-008 as zero-cost.

## Second-order conclusion

EXP-008 produced two real findings:

1. search action selection should consume relevant already-earned learned action experience rather than ignoring it;
2. entity/task qualification is necessary to avoid demonstrated contamination in this representation.

The repaired observation-triggered deletion rule is mechanically selective and passes the tested temporal, persistence, information-boundary, identity, and eligibility interactions. It nevertheless fails the required semantic standard because the runtime cannot know whether the deleted negative scalar is contradicted epistemic search evidence or still-valid generic action utility.

Promoting the repaired candidate would therefore convert an unresolved representation ambiguity into an architectural claim.

**Second-order recommendation: REJECT EXP-008 as a champion promotion. Retain frozen `v9.1_compact`. Preserve the narrower scoring-interaction result as evidence for future work, but do not inherit the observation-triggered deletion rule as established cognition.**
