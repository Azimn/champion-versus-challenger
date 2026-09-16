# Post-v9.1 Artificiality Failure Queue

Frozen organism under attack: `v9.1_compact` at `2856ec6a32be0347a9243f6eff6faa404a9a0e6c`.

Discovery run: `35051440293`, artifact `10429211713`.

No production code changed during discovery. All failures below were reproduced in the symbolic organism, not the renderer.

## Experimental-priority queue

### 1. Repeated experienced search failure does not change search behavior

**Observable behavior:** After repeatedly searching the location it believes contains an object and receiving explicit negative outcomes, the organism continues selecting that same location. In the original attack, five failures drove the existing contextual action value for the repeated search to `-1.0`, yet the next search still selected the believed location even when action order was reversed.

**Why it appears artificial:** The character behaves as though one part of its experience does not inform another. It can remember where it last saw the object and can learn that an action in a context repeatedly failed, but those two histories do not interact when deciding where to search.

**Minimal reproduction:** Directly observe an object's location, repeatedly choose that search action in a neutral search-task context, receive negative experienced outcomes, then offer the believed and alternate search locations again.

**Likely human visibility:** High. Repeatedly looking in a place where the object has just failed to be found is immediately legible as mechanical behavior.

**Current mechanisms expected to matter:** subjective location fact; contextual habit learning; context-cued consequence credit.

**New failure or weak coverage:** New interaction failure. Each contributing mechanism is individually covered, but their interaction was not.

**Renderer involvement:** None.

**Priority reason:** High perceptual impact, deterministic reproduction, cross-name/action-order generalization, and existing state already contains relevant negative evidence. This should be tested before adding persistent machinery.

### 2. A weaker unfinished demand disappears under stronger competing demands and never returns

A lower-strength unfinished concern is evicted when two stronger concerns fill the capacity-two ledger. Resolving both stronger concerns leaves the ledger empty rather than allowing the earlier unfinished demand to return.

This is perceptually important because suppression and forgetting become indistinguishable. It directly attacks the minimal capacity tradeoff established during structural ablation, so it remains a high-value later experiment if the first failure does not dominate.

### 3. An unfinished activity evaporates after unrelated time without completion or cancellation

A maximum-intensity unfinished concern disappears after 74 unrelated events solely through decay. No completion, cancellation, impossibility, or contrary evidence is required.

This is longitudinally visible and challenges whether concern decay is representing reduced urgency or erasing the existence of unfinished activity.

### 4. A third simultaneous future commitment silently deletes the oldest one

With prospective capacity two, creating a third commitment evicts the first. When the first commitment's cue later occurs, nothing reactivates.

This is a real consequence of the empirically minimal existing capacity rather than a coding bug. It should be revisited only if longitudinal scenarios establish that three simultaneous distinct commitments are behaviorally important enough to justify additional state.

### 5. A once-rewarded routine retains exactly unchanged strength across 1000 unrelated events

A learned contextual routine remains at `0.35` after 1000 unrelated events and immediately dominates its context on return.

The behavior is reproducible but less decisive than failure #1 because long-lived habits can be plausible. The artificiality claim requires stronger observer-facing scenarios before architectural work.

### 6. An ancient latent commitment reactivates at full strength after 1000 unrelated events

A future commitment receives no temporal change while latent. Its cue after 1000 unrelated events converts it into a `0.75` concern exactly as if almost no time had passed.

Potentially conspicuous, but whether persistence is wrong depends on the semantics of the commitment. A promise deliberately retained for a long time may be appropriate.

### 7. Unchanging conditions produce an exact short autonomous rhythm

Over the last 60 ticks of a 120-tick neutral run, the autonomous action sequence is exactly periodic with base period 6 (and therefore also 12 and 18).

This can look synthetic, but deterministic periodicity by itself does not establish that variability would improve lifelikeness. It requires observer-facing validation before becoming an additive experiment.

## Selected failure

**Selected for the next experiment:** repeated experienced search failure does not change search behavior.

A separate characterization run removes a possible test artifact by using neutral task contexts such as `find_book`, rather than encoding the chosen location in `Event.context`. It varies entity names, location names, and action order. The failure reproduces across all cases. Direct reobservation of the alternate location remains a positive control and correctly changes the search choice.

The next step is therefore not to add a new memory. It is to determine whether the existing organism already contains the minimum causal information required to correct this failure.
