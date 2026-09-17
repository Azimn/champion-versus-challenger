# EXP-012 Preregistration: Habit Temporal Plasticity Without New State

Status: **PREREGISTERED BEFORE CHALLENGER IMPLEMENTATION**

Frozen predecessor:

- version: `v9.4_prospective_capacity_three`
- branch: `champion-v9-4-prospective-capacity-three`
- commit: `5f949c6e882f780e1d4c07f0b6b3bccf330936aa`
- mechanisms: 11
- concern capacity: 3
- prospective capacity: 3
- eligibility capacity: 2
- fresh canonical state: 245 bytes
- fresh diagnostic state: 269 bytes

Foundation characterization:

- workflow: `35277270258`
- Python 3.11: pass
- Python 3.12: pass
- complete historical pytest contract passed before foundation probes

At preregistration time `src/lifelike_min/exp012_challenger.py` does not exist.

## Target failure

`rewarded_routine_never_weakens`

Frozen reproduction:

1. experience `morning`;
2. perform `walk`;
3. receive positive outcome;
4. contextual habit/action value becomes exactly `0.35`;
5. experience 1000 unrelated events;
6. stored value remains exactly `0.35`;
7. return to `morning` and the same learned support is expressed unchanged.

The failure is not merely persistence. The problem under test is **unchanging permanence**: no currently represented process can make a learned routine become less behaviorally supported through prolonged nonuse.

EXP-012 must not solve this by deleting the habit immediately or by applying one generic decay rule to unrelated mechanisms.

## Foundation result 1: age information is absent after eligibility expiry

A matched-history test equalizes total lifetime tick and all current state.

HISTORY OLD:

- learn `morning -> walk` near the beginning;
- experience a long unrelated interval;
- allow eligibility evidence to expire.

HISTORY RECENT:

- experience the unrelated interval first;
- learn the identical `morning -> walk` value near the end;
- allow eligibility evidence to expire;
- equalize total lifetime tick.

Result:

- old habit value = `0.35`;
- recent habit value = `0.35`;
- eligibility empty in both;
- canonical states are byte-identical.

Therefore the frozen organism has no retrospective subject-owned information that can distinguish age of two otherwise identical habit values after the bounded eligibility trace expires.

## Foundation result 2: recency has a behavioral consequence when alternatives compete

A second history learns:

- old `morning -> walk = 0.35`;
- 1000 unrelated events;
- recent `morning -> stretch = 0.35`;
- eligibility expiration.

On return both values are equal. The frozen organism therefore cannot prefer the recently supported routine on the basis of its history; action list ordering resolves the tie.

This gives EXP-012 an observable target beyond a numeric metric.

## Foundation result 3: existing scalar is a possible carrier

The habit mechanism already stores a mutable signed scalar for each `(context, action)` pair.

Unlike EXP-011's lost prospective identity+cue record, EXP-012 does not yet establish that a second persistent field is required. The existing scalar can be mutated online while experience occurs and can therefore implicitly carry changing current strength.

This path must be falsified before adding age or timing metadata.

## Internal archaeology

`persona_engine_PYTHONX` at tree `65df9144e7f0876b6e61e28d6446c50f283f9db4` previously represented habit identity separately from mutable strength, and additionally carried `uses`, `last_used`, and an evidence log. Its `HabitTracker` also contained a global `decay_all()` operation.

This is a **conceptual donor only**.

Do not copy its wall-clock timestamp, use count, evidence log, exact decay constant, or implementation into EXP-012. Those are larger representations than the current compact organism has earned.

`TinyPersonaEngine` at tree `5eb2e84dbb43c828fae7a1459c9fd13535c7b332` contains no narrower dedicated habit-strength mechanism that solves this failure.

## External constraints from prior art

Narrow prior-art review establishes two constraints:

1. Extinction of learned instrumental/Pavlovian behavior is usually studied under changed contingencies or nonreinforcement and often reflects new/context-sensitive inhibitory learning rather than literal erasure of the original association. Relevant reviews: PMID 12437938, PMID 30350221, PMID 32970967.
2. Habits are not established to be permanently fixed. `Habit and persistence` (PMID 38149526) emphasizes context specificity and weak evidence for unusual permanence. Intensive longitudinal human work on deliberate habit degradation reports gradual, heterogeneous decline in habit strength, commonly with asymptotic/logistic trajectories (PMID 39456116); subsequent work associates degradation with nonperformance, cue encounter, and reward conditions (PMID 41664447).

This literature does **not** justify assuming that every unrelated event should erase an action value. EXP-012 therefore treats the first mutation as an engineered minimal hypothesis to test, not as a model of human habit decay.

## Hypothesis H1: existing-scalar nonuse attenuation

The first challenger may alter only the update semantics of the existing habit/action-value scalar.

While subject-owned experience proceeds without fresh reinforcing evidence for a stored habit, the magnitude of that habit's existing signed scalar may move gradually toward neutral.

The first challenger must add:

- zero new persistent field types;
- zero per-habit timestamps;
- zero age fields;
- zero use counters;
- zero confidence fields;
- zero extinction traces;
- zero replay logs;
- zero new bounded stores;
- zero new counted causal mechanisms.

The existing `(context, action) -> scalar` representation remains the only persistent habit representation.

Attenuation must preserve sign while moving magnitude toward neutral. It must not transform positive history directly into negative history or vice versa.

## Important semantic limitation

H1 changes what the existing scalar means.

Under frozen v9.4 it behaves primarily as retained learned contextual action value.

Under H1 it becomes a compact current support/strength value whose magnitude can reflect both reinforcement and subsequent nonuse.

That semantic change is acceptable only if the experiment demonstrates that it improves longitudinal behavior without breaking already-earned reward learning, delayed credit, or short-term persistence.

Do not describe H1 as general forgetting, extinction, memory decay, or human habit theory.

## Required controls

### C0: frozen v9.4

No attenuation. Must reproduce the exact failure.

### C1: context-exposure/nonreinforcement diagnostic

Test whether changing the scalar only when the relevant context/action is re-experienced without reinforcing outcome could address the target.

Expected limitation: because the long-gap history contains no relevant re-exposure, this control cannot distinguish old and recent routines on first return. If confirmed, record it as a semantically plausible but insufficient solution to the exact target.

C1 is a diagnostic solution class, not permission to widen production.

### H1: online nonuse attenuation

The first production challenger class.

## Attenuation-rate tournament

Do not select one constant solely because it makes the 1000-event fixture pass.

Evaluate a monotonic family including:

- no attenuation / frozen control;
- at least one very slow attenuation regime;
- at least one intermediate regime;
- at least one deliberately too-fast regime.

Express rates in an interpretable form such as per-event attenuation or equivalent experiential half-life.

The selected value, if any, must be the **slowest / least destructive** tested value that satisfies all required behavioral gates.

Do not infer a human timescale from simulated event count.

## Primary behavioral gates

A candidate cannot pass solely because `0.35` becomes some smaller number.

It must satisfy all of the following:

1. **Frozen failure reproduction**: C0 remains exactly unchanged across the long gap.
2. **Long-gap weakening**: the challenger old routine's support is measurably and materially lower after prolonged nonuse.
3. **Old-vs-recent discrimination**: after the matched old-walk / recent-stretch history, the recent routine has greater current support.
4. **Order invariance of the recency consequence**: the recent routine wins when action order is `(walk, stretch)` and when it is `(stretch, walk)`.
5. **Short-gap persistence**: recently reinforced routine support remains substantially intact over short unrelated intervals. A correction that rapidly destroys a newly learned routine fails.
6. **Refresh/reinforcement**: renewed reinforcing experience can strengthen a stale routine again using existing learning semantics.
7. **No sign inversion**: stale positive values approach neutral from above; stale negative values approach neutral from below.
8. **No cross-context contamination**: weakening one stored routine must not create value for another context/action pair.

## Identity versus current strength

Do not silently equate neutral current strength with “never learned.”

The first implementation should preserve the existing habit key while testing attenuation whenever practical so that learned identity/context/action and current magnitude remain conceptually distinguishable inside the existing dict representation.

If retaining exact-zero entries creates a separate unbounded occupancy problem, characterize it. Do not solve it during EXP-012 unless it invalidates the candidate.

Do not add a dormant store.

## Positive and negative histories

Test both signs.

The existing scalar carries positive and negative learned action values. H1 must therefore characterize:

- rewarded routines becoming less positively supported through nonuse;
- punished/negative routines becoming less negatively weighted through nonuse;
- subsequent positive reinforcement after old negative history;
- subsequent negative outcome after old positive history.

Do not claim that symmetric attenuation is psychologically correct. It is a structural consequence of using one signed scalar and must survive adversarial review if promoted.

## Repeated reinforcement

Test single reinforcement versus repeated reinforcement.

Because the frozen scalar accumulates updates toward bounded values, stronger/repeatedly reinforced histories may begin farther from neutral and therefore remain behaviorally influential longer even with the same attenuation operator.

Do not add use count solely to make repetition matter.

## Extinction/nonreward distinction

Keep these separate:

- **nonuse attenuation**: current H1, driven by elapsed subject-experienced events without fresh reinforcing evidence for that habit;
- **extinction/nonreward learning**: changed behavior after relevant cue/action experience without expected reinforcement;
- **negative outcome learning**: explicit negative reward evidence;
- **capacity loss**: not involved here;
- **deletion**: not the first hypothesis.

The experiment must not call all of these “decay.”

## Interaction with eligibility trace

This is a critical gate.

The habit scalar participates in immediate and delayed consequence credit.

Test:

- positive delayed credit;
- negative delayed credit;
- context isolation;
- ambiguity abstention;
- eligibility expiration;
- action-order invariance already earned by EXP-007.

Attenuation must not mutate values in a way that makes delayed credit appear to work while actually destroying or fabricating evidence.

Fresh reward updates and nonuse attenuation must have a deterministic documented ordering.

## Interaction with EXP-008 semantic rejection

EXP-008 established that the generic habit/action-value scalar cannot be treated as epistemic failed-search evidence without semantic error.

EXP-012 must not reopen that rejected interpretation.

Habit weakening remains action-value/tendency semantics only. It must not be used to revise subject-owned location facts or infer hidden world state.

## Interaction with other mechanisms

Run explicit isolation checks against:

- concerns;
- prospective commitments;
- relationships;
- partner reliability;
- affect residue;
- location facts;
- fatigue/affiliation/competence;
- eligibility records.

No unrelated persistent mechanism may be attenuated by EXP-012.

## Subjective-access rule

Only subject-experienced progression may drive H1.

Do not use:

- wall-clock time outside the organism;
- hidden simulator time;
- test-harness timestamps;
- unexperienced environment events;
- external logs;
- privileged knowledge that a habit has been “unused.”

If attenuation occurs per event, those events must be events processed by the organism.

## Serialization and reconstruction

Create histories containing:

- fresh positive routine;
- stale positive routine;
- fresh negative routine;
- stale negative routine;
- multiple contexts/actions at different current strengths.

Serialize, destroy, restore, continue.

Because H1 adds no field, reconstruction should preserve only the current scalar state and existing keys. Continued attenuation and reinforcement after restore must be causally identical to uninterrupted execution.

## Causal ablation

The primary ablation removes only the H1 attenuation update while retaining the entire challenger class and all other behavior.

The old-vs-recent distinction must collapse back to the frozen equal-value/order-dependent result.

Do not infer causality merely from candidate success.

## Long-horizon tests

Test substantially beyond the 1000-event fixture.

Characterize:

- whether values asymptote, reach exact neutral, or cross numerical thresholds;
- whether keys remain indefinitely at neutral;
- whether repeated reinforcement after very long nonuse behaves normally;
- whether floating-point underflow or tiny residual values create artificial action preferences;
- whether many stored routines create growing runtime cost.

Do not solve prospective aging or deterministic rhythm during these runs.

## Cost audit

Measure separately:

- mechanism count;
- persistent field/schema count;
- fresh canonical state;
- fresh diagnostic state;
- one/two/many habit entries;
- state occupancy before/after long attenuation;
- per-event cost with zero habits;
- per-event cost with one habit;
- per-event cost with multiple habits;
- reward update cost;
- serialization/reconstruction cost.

H1 is expected to be zero-new-state but not necessarily zero runtime cost because existing habit entries may now be visited during experience.

## Post-freeze reviewer generation

Only after development passes:

1. freeze production;
2. generate reviewer pass 1;
3. preserve every failure before repair;
4. classify failures before changing production;
5. replay reviewer 1 unchanged after any legitimate repair;
6. rerun development, historical contract, causal ablation, and cost audit;
7. only then generate reviewer pass 2 from new histories.

Reviewer attacks should include:

- short versus long gaps;
- different event mixtures with equal event counts;
- old positive versus recent positive competitors;
- old negative versus recent negative competitors;
- repeated reinforcement;
- alternating reinforcement and nonuse;
- multiple contexts;
- serialization boundaries;
- tiny residual values;
- exact-neutral values;
- delayed-credit overlap;
- same context with multiple actions;
- context re-exposure without outcome;
- explicit zero reward versus absent outcome if the runtime distinguishes them;
- massive unrelated histories;
- histories with no habits to detect incidental changes.

## Falsification conditions for H1

Reject the zero-state H1 challenger if any of the following holds after legitimate tuning:

- solving the long-gap target necessarily destroys short-term learned behavior;
- old-vs-recent behavior remains order-dependent;
- repeated reinforcement cannot refresh stale strength coherently;
- delayed-credit capabilities regress;
- symmetric treatment of signed values creates unacceptable already-earned failures;
- nonuse attenuation depends on hidden/unexperienced time;
- state or mechanism schema grows despite the hypothesis forbidding it;
- another persistent mechanism is accidentally weakened;
- only a highly target-specific constant makes the fixture pass while nearby histories become incoherent.

If H1 is rejected, do **not** automatically add a timestamp. Return to diagnosis and compare the now-earned need for:

- per-habit temporal metadata;
- separate extinction/confidence state;
- context-exposure-only learning;
- or reclassification of the original artificiality criterion.

## Promotion criteria

PROMOTE only if:

- frozen v9.4 reproduces the failure;
- H1 introduces no new persistent field or mechanism;
- a least-destructive attenuation regime is selected by preregistered behavioral gates rather than the single fixture;
- old and recent histories become behaviorally distinguishable through the existing scalar;
- short-gap persistence survives;
- refresh/relearning survives;
- signed-value behavior is coherent;
- EXP-007 delayed credit survives;
- subjective-access boundaries survive;
- serialization/reconstruction is exact;
- causal ablation restores the failure;
- both post-freeze reviewer generations survive or any reviewer invalidity is preserved and independently adjudicated;
- the complete historical contract remains green;
- cost is explicitly recorded.

## Claim boundary if promoted

A likely supported claim is approximately:

> Within the current compact architecture, the existing contextual habit/action-value scalar can support bounded temporal plasticity through online subject-experienced nonuse updates, allowing recently reinforced routines to exert more current influence than otherwise equal but long-unused routines without adding a persistent mechanism or temporal metadata.

Do not claim:

- human habit-decay rates;
- human forgetting curves;
- biological extinction;
- general memory decay;
- optimal reinforcement learning;
- a universal habit model;
- that all learned values should weaken with time;
- that nonuse and extinction are the same process.

## Preserved unrelated frontier

During EXP-012 do not modify:

- `ancient_commitment_reactivates_unchanged`;
- `deterministic_rhythm`.

They may be rerun only for historical regression and post-closeout frontier revalidation.
