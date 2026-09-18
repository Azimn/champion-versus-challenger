# EXP-013 Preregistration: Adaptive Mobilization Threshold

Status: **PREREGISTERED BEFORE CHALLENGER IMPLEMENTATION**

Frozen predecessor:

- version: `v9.5_habit_temporal_plasticity`
- branch: `champion-v9-5-habit-temporal-plasticity`
- commit: `79f747707dadfce9092d89ad19a17a9fcd7dd79b`
- production blob: `9c6474de1918b62e827d32deff2fa10a4b2443d1`
- counted mechanisms: 11
- concerns: 3
- prospective commitments: 3
- eligibility traces: 2
- fresh canonical state: 245 bytes
- fresh diagnostic state: 269 bytes

Pre-EXP-013 diagnosis:

- permanent report: `research/results/PRE_EXP013_PERIOD_SIX_DIAGNOSIS.md`
- primary diagnosis run: `35290482876`
- expanded solution-class diagnostic runs: `35290762175`, `35290861518`, `35290971311`, `35291096533`, `35291237418`

At preregistration, `src/lifelike_min/exp013_challenger.py` must not exist.

## Target failure

Frozen v9.5 neutral autonomous dynamics converge across the full sampled 363-start basin to an exact state/action period-six limit cycle, externally visible as repetition of:

`rest, work, idle, rest, idle, idle`

up to phase.

The target is not determinism itself.

The target is the **universally attracting, very-short, externally obvious autonomous limit cycle**.

## Causal diagnosis

The smallest identified causal subsystem contains:

- fatigue drift;
- competence drift;
- fixed idle utility;
- hard deterministic winner selection;
- fixed absolute rest/work relief;
- clipping at the zero need boundary.

Rest/work are selected at pressures around 0.12, but each subtracts 0.45. The controlled pressure therefore clips exactly to zero. These repeated resets erase residual differences and return state to a small affine lattice.

The cycle is:

- not a tie-breaking artifact;
- not action-enumeration dependent;
- not a floating-point artifact;
- not primarily an update-order artifact;
- robust to ±5% tested parameter perturbations;
- strongly restoring after tested perturbations.

Simple memoryless parameter/scoring corrections, proportional relief, affiliation reintegration, current-score margin gates, and simple previous-action refractory/hysteresis classes were all tested diagnostically and rejected because they merely produced another exact short or universal cycle.

## Selected hypothesis H1

**H1: one global adaptive mobilization threshold is the minimum tested dynamical state capable of preventing collapse into the frozen universal very-short attractor while preserving deterministic homeostatic action selection.**

The threshold represents temporary resistance to immediately mobilizing another non-idle action after action has occurred.

It is not per-action memory.

It contains no action identity.

It is not random.

It is not a cooldown record.

It is not a habit, concern, eligibility trace, affect value, relationship value, or prospective commitment.

## Production semantics

Add exactly one persistent scalar:

`action_mobilization_threshold`

Baseline:

`0.10`

At each processed organism tick during ordinary drift:

`threshold_next = 0.10 + (threshold - 0.10) * 0.98`

During action scoring:

- the score for `idle` becomes the current mobilization threshold instead of the frozen constant 0.10;
- all non-idle action scores remain inherited and unchanged.

After a selected non-idle action:

`threshold_next = clamp(threshold + 0.08, 0.10, 1.0)`

Selecting `idle` does not add a pulse.

Forced non-idle action still counts as experienced mobilization and raises the threshold.

The threshold is subject-owned causal state for persistence purposes but need not be introspectively exposed as a numeric value.

## Parameter selection

Parameters are frozen from the preimplementation diagnostic grid, not tuned during production.

Candidate decay factors tested:

`.80, .90, .95, .98, .995`

Candidate pulses tested:

`.005, .01, .02, .04, .08, .12`

The selection rule was:

1. no detected exact period <= 30 across all 36 fatigue/competence diagnostic starts;
2. at least two distinct attractor identities across those starts;
3. deterministic bounded dynamics;
4. choose the fastest tested relaxation satisfying 1-3;
5. within it choose the smallest tested pulse satisfying 1-3.

This selects:

- relaxation factor: `0.98`
- pulse: `0.08`
- baseline: `0.10`

No parameter may be changed after production implementation merely to make a reviewer pass.

## Mechanism accounting

H1 adds:

- one persistent scalar dimension;
- one new dynamical update law;
- one new causal influence on action arbitration.

It does not fit the established semantics of any existing 11 mechanism.

Therefore EXP-013 provisionally counts H1 as **mechanism 12: adaptive mobilization threshold**.

If promoted, MBASE-003 must independently test the 12-mechanism dependency structure. Do not assume the count or dependency structure from MBASE-002.

## Primary dynamical success gates

Across a 36-start deterministic grid:

fatigue, competence in `{0, .1, .25, .5, .75, 1.0}`

the challenger must satisfy:

1. no exact tail action period <= 30;
2. at least two distinct tail attractor identities;
3. rest occurs;
4. work occurs;
5. idle occurs;
6. fatigue remains in [0,1];
7. competence remains in [0,1];
8. no single action occupies > 95% of the final 5,000 actions.

The experiment does **not** require mathematical aperiodicity.

A period above 30 is not automatically success if reviewer evidence shows it is merely another trivial universal loop.

## Long-horizon evaluation

For champion and challenger, run at least 20,000 autonomous ticks per tested initial state where computationally inexpensive.

Record:

- detected exact action period up to at least 2,000;
- state recurrence;
- transient length;
- action frequencies;
- fatigue/competence bounds;
- threshold range;
- distinct attractor identities;
- basin membership.

Use explicit recurrence detection, not visual inspection.

## Perturbation evaluation

After settling, inject separately:

- fatigue increase;
- competence increase;
- forced rest;
- forced work;
- neutral unrelated observation;
- shock or affect perturbation where behaviorally noncausal.

Measure:

- return or transition time;
- resulting attractor identity;
- whether perturbations can move the organism between deterministic basin trajectories.

Do not require permanent divergence from every perturbation.

## Homeostatic safety

Reject if H1 creates:

- unbounded need state;
- permanent rest fixation;
- permanent work fixation;
- idle fixation;
- starvation of fatigue regulation;
- starvation of competence regulation;
- rapid alternate-action thrashing;
- loss of deterministic replay.

## Character sensitivity

Verify H1 does not flatten already-earned state-sensitive behavior.

Representative histories must include:

- positive and negative habit learning;
- unresolved concerns;
- relationship history;
- affect residue;
- prospective commitment;
- subjective location fact;
- delayed eligibility credit.

Neutral autonomy need not express every mechanism, but H1 must not erase their established behavioral effects.

## Causal ablation

Create an audit-only ablation retaining the H1 code path but fixing:

- threshold baseline = 0.10;
- relaxation irrelevant;
- pulse = 0.

The original frozen period-six attractor must return.

This establishes causal responsibility.

## Serialization

The new scalar is persistent.

Test:

- serialize/destroy/restore exactly;
- no wall-clock drift;
- continuation equality;
- reconstruction while threshold > baseline;
- reconstruction at baseline.

No test harness history may restore or infer the scalar.

## Cost audit

Measure separately:

- mechanism count;
- persistent-field count;
- fresh canonical bytes;
- fresh diagnostic bytes;
- representative serialized bytes with elevated threshold;
- tick processing;
- action scoring;
- serialization;
- reconstruction.

H1 should be O(1) additional update work per tick.

Do not call it zero cost.

## Historical regression

Before promotion run:

- complete repository test suite;
- all EXP-002 through EXP-012 earned behavior;
- all 20 MBASE-002 capability families;
- renderer invariance;
- subjective-access boundary;
- canonical persistence;
- capacities 3/3/2;
- EXP-012 habit temporal plasticity;
- preserved ancient prospective failure unchanged.

## Reviewer reservation

Only after development passes and production is frozen:

1. generate reviewer pass 1;
2. preserve and classify every failure before modifying production;
3. if a legitimate repair remains within H1, freeze production again and replay reviewer 1 unchanged;
4. rerun development, regression, causal ablation, and cost;
5. generate genuinely new reviewer pass 2.

Reviewers must attack:

- all action orders;
- extreme initial needs;
- near-threshold states;
- very long horizons;
- alternative basin starts;
- repeated perturbations;
- serialization at elevated threshold;
- forced actions;
- history-sensitive mechanisms;
- possibility that period 45 is merely another trivial universal loop;
- hidden state;
- threshold saturation;
- starvation;
- action frequency collapse.

## Failure conditions

REJECT H1 if:

- any preregistered basin start retains an exact period <= 30;
- all starts collapse to one trivial attractor and second-order review finds the change merely hides the original cycle;
- homeostatic regulation fails;
- historical capabilities regress;
- exact reconstruction fails;
- the new scalar must be supplemented by previous-action identity, RNG, per-action cooldown, or another new state dimension;
- reviewer failures require changing the frozen `0.98 / 0.08 / 0.10` parameters;
- causal ablation does not restore period six.

If rejected, do not rescue EXP-013 by adding stochasticity or per-action refractory state.

## Promotion criterion

PROMOTE only if:

- H1 passes all dynamical gates;
- basin behavior is materially less globally collapsed;
- regulation remains functional;
- causal ablation restores the frozen failure;
- deterministic reproducibility survives;
- exact persistence survives;
- both reviewer generations survive;
- complete historical regression remains green;
- cost and mechanism impact are explicitly recorded;
- second-order critique supports the interpretation that one slower arbitration variable adds real dynamical capacity rather than cosmetic period inflation.

## Claim boundary if promoted

Likely supported claim:

> In this compact deterministic homeostatic architecture, adding one slowly relaxing global mobilization threshold to action arbitration can prevent collapse into the previously universal six-state limit cycle and preserve multiple longer deterministic trajectories without RNG or per-action history.

Do not claim:

- human action inertia;
- biological refractory dynamics;
- free will;
- consciousness;
- optimal hybrid control;
- universal elimination of deterministic recurrence;
- that period 45 is intrinsically human-like;
- that every agent requires this mechanism.

## Out-of-scope preserved failure

`ancient_commitment_reactivates_unchanged` remains out of scope.

EXP-013 must not alter prospective temporal semantics.
