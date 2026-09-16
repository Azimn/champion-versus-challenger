# EXP-008: Failed-Search Adaptation by Existing-State Interaction

## Status

**PRE-REGISTERED BEFORE CHALLENGER PRODUCTION CODE**

Frozen champion:

- version: `v9.1_compact`
- branch: `champion-v9-1-compact`
- commit: `2856ec6a32be0347a9243f6eff6faa404a9a0e6c`

This experiment begins only after global structural ablation closed and the compact champion passed frozen-ref verification.

## Reproduced artificiality failure

The organism directly observes an entity at a location, repeatedly searches that believed location, receives subject-experienced negative outcomes, and nevertheless continues to search the believed location after the existing contextual action value for that search has reached `-1.0`.

The failure reproduces across multiple entity/location names and action-order permutations when a neutral search-task context is used. Direct reobservation of a different location correctly changes the search choice, establishing that the existing subjective-fact mechanism itself can revise when it receives direct perception.

Failure evidence:

- discovery run: `35051440293`
- discovery artifact: `10429211713`
- selected characterization run: `35051523901`
- selected characterization artifact: `10429290802`

## Observable failure, not theoretical feature

The observable defect is:

> Repeated experienced failure of a search action does not influence a later search decision even though the organism already stores both the last perceived location and the learned negative action value.

The experiment does not begin by assuming a probabilistic belief system, confidence representation, planning module, contradiction ledger, or new memory mechanism is required.

## Causal explanation under test

`SubjectiveFactCharacter` gives search actions a belief-derived score and returns immediately from the search-scoring branch. The generic contextual habit value is therefore not consulted for search actions.

The proposed explanation is that the organism has sufficient existing state but lacks an interaction rule between:

1. subject-owned factual evidence about where the entity was last perceived; and
2. subject-experienced success/failure value for trying a particular search action in the current task/entity context.

## Minimal hypothesis

A search choice should combine the existing location-belief prior with the existing learned contextual action value when and only when the outcome attribution is subject-accessible.

No new persistent field is proposed.

For search experience only, derive an experience context deterministically from information already supplied to the subject:

`search_experience_context = task_context + target_entity`

The precise encoding is an implementation detail; the semantic requirement is that the task context and entity identity are both subject-accessible and that no hidden simulator causal ID is used.

The existing bounded context-action trace and existing habit table may use this derived context so that search outcomes remain entity-specific. The trace record remains exactly three fields:

- context
- action
- age

The habit store remains the existing `(context, action) -> value` mapping.

Search scoring will then combine:

- the existing belief score for the candidate location; and
- the already-learned action value for the subject-accessible search experience context.

The initial minimal scoring hypothesis is additive:

`search_score = belief_score + learned_action_value`

where the current belief scores remain unchanged from v9.1 (`0.90` for the last perceived location, `0.05` for a contradicting candidate, `0.10` when no location belief exists).

## Important semantic boundary

The challenger must **not** change `location_beliefs` merely because a search outcome is negative.

A failed search is evidence about the success of the attempted action under the experienced circumstances. It is not automatically equivalent to a direct perception of the entity somewhere else.

Direct observation remains the authoritative mechanism for replacing the stored location fact in this experiment.

This keeps EXP-008 narrower than general belief revision.

## Subjective-access contract

A search outcome may influence entity-specific search experience only if the organism receives enough subject-accessible information to associate the outcome with that search task and target entity.

Forbidden attribution inputs:

- hidden causal IDs
- simulator-known source actions not represented in experienced state
- hidden world history
- ground-truth current entity location
- test harness metadata unavailable to the subject

If target identity or usable task context is absent, the challenger must not fabricate entity-specific credit.

## Development scenarios

### D1: Baseline failure reproduction

Frozen champion and challenger receive identical history:

1. directly observe `book` in `drawer`;
2. repeatedly search for the book in the `find_book` task context;
3. receive negative outcomes explicitly associated with the book/search task;
4. offer `search:drawer` and `search:shelf` again with reversed action ordering.

Champion is expected to keep selecting `search:drawer` after strong negative action experience.

Challenger should eventually select the alternative after sufficient repeated failure.

### D2: Evidence accumulation rather than one-shot contradiction

One negative outcome should not automatically erase or reverse a direct location observation.

The expected additive trajectory from a zero habit value is approximately:

- direct-belief prior: `0.90`
- after one full negative update: belief-backed search remains competitive (`0.55` if the action value is `-0.35`)
- after two: still positive (`0.20` if the value is `-0.70`)
- after three: negative learned value can outweigh the stale believed-location preference (`-0.10` if the value is `-1.0`)

Exact choice depends on candidate scores, but adaptation must emerge from accumulated experienced evidence rather than a hard-coded failure count.

### D3: Positive outcome control

Positive experienced search outcomes should strengthen rather than weaken the selected search action. A successful search at the believed location must not make the challenger prefer an unsupported alternative.

### D4: Direct reobservation remains authoritative

After failure-driven avoidance of a previously believed location, directly observing the entity at a location must update `location_beliefs` exactly as before. The search policy must then use the revised fact plus any relevant experience rather than blocking belief revision.

### D5: Entity specificity

Negative experience searching for `book` must not make `keys` avoid the same physical location when the two tasks share a generic task label. Entity identity must prevent cross-entity contamination.

### D6: Task/context specificity

Negative experience from an unrelated task context must not contaminate a search decision merely because the candidate action string contains the same location.

### D7: Unknown entity control

When no location belief exists, search candidates remain governed by the existing unknown-belief baseline plus only subject-owned experience relevant to that same target/task. The challenger must not fabricate a location belief.

### D8: Unlabeled outcome control

If a delayed or immediate outcome lacks sufficient subject-accessible target/task information, the challenger must conservatively abstain from entity-specific search learning rather than infer hidden causality.

### D9: Action-order invariance

Semantically identical candidate sets in different order must produce the same choice once scores differ.

### D10: Contradictory outcomes

Repeated negative outcomes should be reversible by later positive outcomes through the existing bounded habit value. The experiment should not create an irreversible failure flag.

### D11: Delayed experienced outcome

When target entity and task context remain subject-accessible on the outcome event, the existing eligibility trace may carry search-action eligibility across intervening activity. This is a compatibility test with EXP-007, not a claim of new long-horizon causality.

### D12: Renderer invariance

Rendering or suppressing surface text must not change action selection or persistent state.

## Historical regression contract

The challenger must preserve the full explicit earned-behavior contract of `v9.1_compact`, including:

- fatigue, affiliation, competence pressures
- relationship specificity
- affect carryover and decay
- contextual habit behavior
- partner reliability and uncertainty ordering invariance
- multiple concerns at the earned capacity
- prospective cue behavior at the earned capacity
- subjective fact persistence and direct revision
- hidden-world non-omniscience
- entity specificity
- immediate credit
- bounded delayed credit
- same-context ambiguity abstention
- renderer invariance
- serialize/destroy/restore/continue continuity

## Causal ablations

At minimum:

1. **No search-experience interaction:** keep all existing state but ignore learned action value during search scoring. The selected failure should return.
2. **Context-blind search experience:** remove task specificity. This should produce inappropriate contamination in a deliberately colliding scenario.
3. **Entity-blind search experience:** remove target identity from the derived experience context. This should allow one entity's failures to contaminate another's search behavior.
4. **No action value:** retain factual belief but remove the learned action-value contribution. Failure should return.

These ablations are intended to establish which interaction dimensions are necessary. They do not imply each dimension is a new persistent mechanism.

## State/cost hypothesis

Expected new persistent fields: **0**.

Expected counted persistent mechanisms: **unchanged at 11** if the challenger succeeds as a policy interaction.

The existing habit and eligibility stores may contain longer derived context strings for search-specific experience. State-byte growth caused by longer keys must be measured and reported rather than hidden.

Measure:

- fresh persistent bytes
- representative persistent bytes
- search-history state bytes after equal experiences
- mechanism count
- mixed tick distribution
- search-decision tick distribution
- outcome-processing distribution
- serialization continuity

## Promotion criteria

PROMOTE only if the challenger:

- corrects the reproduced repeated-failed-search behavior across novel entities, locations, and action-order permutations;
- uses no privileged world truth;
- adds no new persistent field;
- keeps location belief revision tied to direct observation rather than silently converting failure into a new factual belief;
- survives entity-specificity and task-specificity contamination tests;
- preserves conservative abstention when target/task attribution is unavailable;
- preserves positive learning and contradictory-evidence reversibility;
- preserves every earlier earned behavior;
- remains renderer invariant;
- survives serialization/reconstruction;
- has proportionate state/runtime cost;
- and survives post-implementation reviewer holdouts not used to design the challenger.

## Rejection criteria

REJECT if any of the following occurs:

- one entity's failures alter another entity's search behavior;
- unrelated task contexts contaminate one another;
- negative outcome directly rewrites a factual location belief without direct perception;
- unlabeled outcomes cause entity-specific learning through hidden inference;
- action ordering determines the result when scores should determine it;
- direct reobservation no longer behaves correctly;
- the historical earned suite regresses;
- the correction requires a new persistent confidence/belief field to pass the stated hypothesis;
- state growth is disproportionate to the demonstrated behavioral gain;
- or reviewer holdouts expose that the apparent improvement is specific to development scenarios.

## Falsification

The hypothesis is falsified if combining existing factual and learned-action state cannot fix the reproduced behavior without contamination or regression.

If falsified, EXP-008 should not silently escalate into a belief-confidence system. The negative result should be preserved and a qualitatively different mechanism should be considered in a later experiment.

## Reviewer reservation

No post-implementation reviewer holdouts have been written at preregistration time. They are intentionally reserved until challenger production behavior is frozen.

## Prior-art boundary

See `research/donors/EXP008_FAILED_SEARCH_DONORS.md`.

Internal and external archaeology supports the general importance of outcome-sensitive action choice and belief/plan revision after failures. EXP-008 deliberately tests the smaller existing-state interaction before importing any richer architecture.
