# EXP-008 Reviewer Pass 1

Run: `35052387933`  
Artifact: `10429122411` (`exp008-review1`)  
Production under review: `ec269c949e2334c0df4ec2f9c5f55c8a202e1ac7`  
Result: **FAIL, 1 of 7 holdouts**

Passing holdouts:

- persistence-safe delimiter/Unicode round-trip
- actor-mismatched outcome abstention
- inherited same-context ambiguity abstention
- fractional evidence accumulation rather than a hard-coded failure count
- semantically similar task names remain isolated
- zero-value outcome does not create search experience

## Reviewer failure: fresh direct observation cannot overcome stale negative search experience

Sequence:

1. Directly observe `book` in `drawer`.
2. Accumulate three explicit failed drawer searches until search experience reaches `-1.0`.
3. Confirm the challenger now chooses `search:shelf`.
4. Directly observe the book in `drawer` again.
5. Offer `search:shelf` and `search:drawer`.

Observed result:

- factual location belief: `drawer`
- stale search experience for drawer: `-1.0`
- choice before reobservation: `search:shelf`
- choice after fresh direct reobservation: `search:shelf`

This violates the preregistered requirement that direct perception remain authoritative. The policy correctly learned from failure but had no rule for invalidating experience contradicted by newer direct perception.

## Causal diagnosis

The factual belief was correctly updated. No hidden-world leak occurred. The failure arises entirely in the interaction policy: the same stale negative action value continues to subtract from the newly refreshed factual prior.

## Minimal developer response

Do not add confidence, timestamps, observation histories, or another belief record.

When a direct `observe_location(entity, location)` event is experienced, invalidate only negative search-experience habit entries that satisfy all of the following:

- they are actor-qualified for that same entity;
- their search action targets that same directly observed location;
- their learned value is negative.

Do not clear:

- positive search experience;
- negative experience for other locations;
- other entities' experience;
- non-search habits;
- the factual belief store;
- unrelated eligibility records unless a later failure demonstrates this is necessary.

This is treated as a minimal interaction correction within the preregistered hypothesis, not a new persistent mechanism.

After correction, rerun the complete development evidence and all seven reviewer holdouts. Then freeze the corrected implementation and create a genuinely new reviewer generation.
