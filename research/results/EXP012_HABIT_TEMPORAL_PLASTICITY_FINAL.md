# EXP-012 Final: Habit Temporal Plasticity Without New State

## Decision

**PROMOTE** the zero-new-state habit temporal-plasticity descendant.

Frozen predecessor: `v9.4_prospective_capacity_three`, commit `5f949c6e882f780e1d4c07f0b6b3bccf330936aa`.

Preregistration: `517408f3c8256671aff77aa4fca03f0a06d7b7e8`.

Evaluated production blob: `9c6474de1918b62e827d32deff2fa10a4b2443d1`.

Strict closeout run: `35281801241`.

Artifacts: Python 3.11 `10522324305`; Python 3.12 `10522573935`.

## Production change

No persistent field, record type, timestamp, age counter, use counter, confidence value, extinction trace, replay log, store, or counted mechanism was added.

The only new production semantics are applied to the already-existing signed contextual habit/action-value scalar.

For each processed subject-experienced event, each pre-existing habit is multiplied by retention factor `0.9995` unless that same event supplies a nonzero learned-value update to that habit through the already-earned immediate or delayed outcome semantics.

Outcome learning executes first. Refreshed habits are exempt from attenuation on that event. Newly created habit entries are not attenuated on their creation event.

The temporal variable is therefore **processed subject-experienced event count**. It is not wall-clock time or simulated elapsed duration.

## Rate tournament

The rate manifest was frozen before challenger results.

- control `1.0`: no long-gap weakening;
- very slow `0.9999`: 10-event retention 0.999000 of initial, but 1000-event retention 0.904833, failing the preregistered material-weakening gate;
- selected `0.9995`: 10-event retention 0.995011 and 1000-event retention 0.606455;
- deliberately fast `0.99`: 10-event retention 0.904382, failing short-gap preservation.

`0.9995` was the least destructive tested rate satisfying all preregistered rate gates.

For an initial 0.35 routine, the selected trajectory was approximately:

- 1 event: 0.349825
- 10: 0.348254
- 100: 0.332926
- 500: 0.272563
- 1000: 0.212259

The operator is multiplicative/exponential toward neutral.

## Behavioral result

The frozen v9.4 failure retained 0.35 after 1000 unrelated experienced events.

EXP-012 reduces the same routine to approximately 0.212259.

In the key old-versus-recent competition:

- old walk: approximately 0.210884
- recent stretch: approximately 0.348080

`stretch` wins whether actions are enumerated `(walk, stretch)` or `(stretch, walk)`.

The observable action-order artifact is therefore eliminated by integrated current-strength difference.

## Signed values and relearning

Positive and negative values both move toward neutral without nonuse sign inversion.

After 1000 qualifying events:
- +0.35 becomes about +0.212259;
- -0.35 becomes about -0.212259.

Explicit opposite evidence can still cross through neutral using the existing outcome learner. Nonuse itself does not cross zero.

Repeated learn/nonuse/refresh cycles remain plastic. Three tested refresh cycles all strengthened the stale routine again.

## Nonuse versus outcome evidence

The experiment preserves the semantic distinction:

- action not performed: nonuse attenuation;
- action performed with zero reward: no learned-value refresh, so nonuse attenuation still applies;
- explicit negative reward: inherited negative learning update, exempt from same-event attenuation;
- explicit positive reward: inherited positive learning update, exempt from same-event attenuation;
- unavailable action and unrelated-context activity: count as experienced nonuse for existing habits.

EXP-012 does not claim this is biological extinction.

## Delayed credit and event ordering

EXP-007 immediate and delayed credit behavior survives.

Reviewer probes confirmed:
- delayed positive credit;
- delayed negative credit;
- ambiguity abstention;
- existing context attribution.

The update order is inherited outcome learning first, then attenuation only for pre-existing habits not refreshed by that event.

## Serialization and offline time

Canonical serialize/destroy/restore preserves exact current scalar state.

No processed event means no attenuation. Runtime destruction, reconstruction, or wall-clock downtime alone does not alter habit strength.

Continued experience after reconstruction matches uninterrupted execution.

## State and cost

Mechanism count remains **11**.

Capacities remain:
- concerns = 3
- prospective commitments = 3
- eligibility traces = 2

Fresh state remains:
- canonical = 245 bytes
- diagnostic = 269 bytes

Persistent field set is unchanged.

For identical habit key sets and scalar text values, structural serialization occupancy is unchanged from frozen v9.4. Differences caused only by changed floating-point text length are serialization-format variance, not an added cognitive dimension.

The computational cost is not zero. The current implementation scans the stored habit dictionary for each processed event, so attenuation update work is **O(n)** in habit-entry count.

Python 3.12 hosted-CI median nonuse-event measurements:
- 0 habits: about 18.75 us
- 1: 17.63 us
- 8: 23.29 us
- 32: 44.57 us
- 128: 118.93 us

These are engineering samples, not general performance claims.

## Event-density limitation

Event count functions as an implicit experiential clock.

One inert experienced event after learning leaves 0.349825; ten leave 0.348254.

Reviewer 2 confirmed:
- adding more inert experienced events causes more attenuation;
- equal event counts with different irrelevant-context mixtures attenuate the habit equally;
- reordering irrelevant events with equal counts does not change the habit scalar.

Therefore EXP-012 models accumulated **processed experience events**, not physical or simulated elapsed time. Event segmentation is a real limitation and claim boundary.

## Reviewer evidence

Reviewer pass 1: 9/9 passed.

Reviewer pass 2: 8/8 passed.

No production repair was needed after production freeze.

Both reviewers replayed the development suite and full repository tests while verifying production blob `9c6474de1918b62e827d32deff2fa10a4b2443d1`.

## Causal ablation

The ablation keeps the EXP-012 code path but sets retention to `1.0`.

After 1000 qualifying events:
- candidate = approximately 0.212259;
- ablated = exactly 0.35.

Removing only attenuation restores the target failure.

## Remaining frontier

Post-EXP-012 revalidation:

- `rewarded_routine_never_weakens`: **eliminated by target correction**;
- `ancient_commitment_reactivates_unchanged`: **still reproduced**, reactivating at 0.75 after 1000 unrelated events;
- `deterministic_rhythm`: **still reproduced**, including exact period 6.

EXP-012 was not tuned against either surviving failure.

## Supported claim

Within this compact architecture, the existing signed contextual habit/action-value scalar can encode gradual current-strength weakening through subject-experienced nonuse, allowing recently reinforced routines to exert more current influence than otherwise equally learned but long-unused routines without adding another persistent state dimension or counted mechanism.

## Not established

EXP-012 does not establish human habit extinction, human forgetting curves, biological habit decay, general memory decay, universal temporal discounting, reinforcement-learning convergence, or optimal habit dynamics.
