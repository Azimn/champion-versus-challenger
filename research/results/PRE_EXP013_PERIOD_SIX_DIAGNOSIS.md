# Pre-EXP-013 Diagnostic Report: v9.5 Period-Six Attractor

Status: **CAUSAL CHARACTERIZATION COMPLETE, BEFORE EXP-013 PREREGISTRATION**

Frozen basis:

- version: `v9.5_habit_temporal_plasticity`
- branch: `champion-v9-5-habit-temporal-plasticity`
- commit: `79f747707dadfce9092d89ad19a17a9fcd7dd79b`
- production blob: `9c6474de1918b62e827d32deff2fa10a4b2443d1`
- mechanisms: 11
- capacities: concerns 3, prospective 3, eligibility 2
- fresh state: 245 canonical / 269 diagnostic bytes

No EXP-013 production challenger exists at this report.

## Reproduced failure

Neutral autonomous operation converges to the literal repeating action block:

`rest, work, idle, rest, idle, idle`

up to cyclic phase.

The last 60 frozen actions contain ten exact repetitions. The pattern is therefore behaviorally visible, not merely a hidden numerical regularity.

Primary diagnosis run: `35290482876`, artifact `10525968426`.

## Full state versus action periodicity

The failure is a genuine exact state-space limit cycle.

Across the settled tail, complete relevant causal state at t and t+6 is exactly equal, including:

- fatigue
- affiliation
- competence
- concerns
- affect residue
- habits
- prospective commitments
- relationships
- partner reliability
- beliefs
- eligibility records

Maximum observed period-six difference for fatigue, affiliation, and competence was exactly zero.

The six post-action fatigue/competence states in exact rational form are:

1. 1/25, 3/50
2. 2/25, 2/25
3. 0, 1/10
4. 1/25, 0
5. 2/25, 1/50
6. 0, 1/25

then repeat.

## Basin of attraction

A deterministic grid sampled 363 starts:

- fatigue: 0.0 through 1.0 in 0.1 increments
- competence: 0.0 through 1.0 in 0.1 increments
- affiliation: 0.0, 0.55, 1.0

All 363 entered the same period-six attractor up to cyclic phase.

Therefore the observed basin covers the entire sampled homeostatic region. This is a local sampled-basin result, not a mathematical proof over all real-valued initial states.

## Action-order audit

All six permutations of `rest`, `work`, and `idle` preserve the period-six attractor and semantic action sequence up to phase.

No exact tie occurs in the settled cycle.

Minimum settled winning margin is approximately 0.02; maximum is approximately 0.04.

The failure is not an enumeration-order tie artifact.

## Score-margin structure

The settled controller repeatedly crosses the fixed idle score 0.10:

- fatigue 0.04, competence 0.06 -> idle
- fatigue 0.08, competence 0.08 -> idle
- fatigue 0.12, competence 0.10 -> rest
- fatigue 0.04, competence 0.12 -> work
- fatigue 0.08, competence 0.02 -> idle
- fatigue 0.12, competence 0.04 -> rest

The winners are unique. The cycle is produced by deterministic threshold crossings, not score equality.

## Production update order

Frozen v9.5 performs:

1. tick increment
2. need / relationship / affect / concern / reliability drift
3. event integration, including EXP-012 habit attenuation
4. action scoring
5. deterministic argmax
6. action effects
7. trace snapshot

A reduced diagnostic moved drift after action selection. Both ordinary float and exact rational arithmetic still produced period six.

Therefore synchronous update ordering is not the primary source.

## Numerical precision

The reduced frozen equations were replayed using:

- ordinary Python float
- Decimal with 50-digit precision
- exact Fraction arithmetic

All produce the same period-six action and state cycle.

The attractor is structural, not a floating-point artifact.

## Parameter robustness

Each of the following was perturbed independently by ±0.1%, ±1%, and ±5%:

- fatigue drift
- competence drift
- rest relief
- work relief

Every tested variant retained the same qualitative period-six cycle.

The failure is structurally robust over the tested neighborhood rather than finely tuned to exact constants.

## Causal decomposition

Neutral default arbitration contains only `rest`, `work`, and `idle`.

Affiliation therefore cannot win and eventually saturates at 1.0. No habit state is involved.

Reduced-subsystem ablations show:

- freeze competence drift -> period 3
- freeze fatigue drift -> period 5
- remove rest effect -> rest fixation
- remove work effect -> period-12 work-dominant behavior
- equalize fatigue/competence drift -> period 4
- halve both action effects -> period 6
- smaller rest effect -> period 5
- smaller work effect -> period 15

The smallest identified oscillator subsystem is:

**fatigue drift + competence drift + fixed idle utility + deterministic winner selection + rest/work relief transitions**.

## Transition geometry

Frozen action relief is an absolute subtraction of 0.45.

At settled selection, rest/work pressures are only about 0.12. Each action therefore overshoots its regulated quantity and clips it exactly to zero.

These repeated boundary resets erase residual state differences and return the organism to a small affine lattice. Deterministic hard selection over that lattice produces the observed exact orbit.

This clipping-reset geometry explains why modest parameter perturbations leave the cycle unchanged: the action effects remain large enough to hit the same zero boundary.

## Perturbing the running cycle

After full convergence:

- +fatigue returns to the same cycle within 3 autonomous actions
- forced rest returns within 2
- competence increase, forced work, shock, and affiliation increase collapse immediately to the existing orbit or a phase-shifted copy

The attractor is therefore strongly restoring under the tested subject-accessible perturbations.

## Perceptual significance

The existing renderer is noncausal.

Because the external action sequence itself repeats the same six-action block ten times in 60 actions, an observer can directly perceive the regularity without access to internal state.

The target is therefore retained as a meaningful artificiality symptom.

## Diagnostic solution classes tested before preregistration

### 1. Parameter adjustment

Rejected.

Small parameter changes preserve period six. Larger isolated changes merely produce other short cycles or fixation.

### 2. Proportional rest/work relief

Rejected.

Across 36 sampled fatigue/competence starts:

- relief fraction .25 -> universal period 3
- .50 -> universal period 3
- .75 -> universal period 4
- .90 -> universal period 6

This changes the orbit but does not solve the dynamical pathology.

### 3. Reconnect affiliation to neutral arbitration

Rejected.

Adding a deterministic `seek_connection` action driven by already-existing affiliation pressure creates richer action content, but all 216 sampled three-need starts converge to one exact period-18 attractor.

This demonstrates that the failure is not merely omission of the third base pressure.

### 4. Previous-action refractory penalty / hysteresis

Rejected as the EXP-013 minimum.

One- to three-action refractory windows and one-step hysteresis across tested magnitudes produced universal exact attractors with periods 3 through 12.

These policies also require action-history state that v9.5 does not currently own.

They relocate the cycle and add more semantic machinery than justified.

### 5. Current-score decision-margin gate

Rejected.

Tested score margins from .005 through .12 produced exact periods 6, 9, 10, 13, or 33, plus one idle fixation.

A memoryless confidence threshold does not remove the finite-orbit pathology.

### 6. One-scalar adaptive mobilization threshold

This is the first tested solution class that materially changes the attractor structure while remaining deterministic and action-identity-free.

Diagnostic semantics:

- baseline mobilization threshold = 0.10
- threshold relaxes toward baseline each experienced tick
- completing any non-idle action raises the threshold
- idle competes using the current threshold
- no RNG
- no previous-action identity
- no per-action cooldown
- one scalar dynamic variable

The broad diagnostic family tested decay factors .80, .90, .95, .98, .995 and action pulses .005 through .12 across 36 initial fatigue/competence states.

Fast relaxation or small pulses still give short universal cycles. Slower relaxation produces longer recurrence and, for some parameter regions, multiple basin-dependent attractors.

The minimum selection rule for the production hypothesis is frozen as:

1. no detected exact period <= 30 across the 36-start diagnostic grid;
2. at least two distinct cyclic attractor identities across that grid, so initial-state information is not universally erased into one orbit;
3. deterministic bounded homeostasis;
4. choose the **fastest relaxation** among tested factors satisfying 1-3;
5. within that factor choose the **smallest pulse** satisfying 1-3.

Under the already completed diagnostic grid this selects:

- relaxation factor: **0.98**
- non-idle action pulse: **0.08**
- baseline threshold: **0.10**

At this setting the reduced diagnostic produced period 45 across the 36 starts but nine distinct cyclic attractor identities. This is not a claim that period 45 is intrinsically lifelike. It establishes a falsifiable change from one globally attracting six-state orbit to longer, basin-sensitive deterministic trajectories.

## Internal archaeology

### DUCK current main

Repository tree inspected at current main tree `4db5df076eb87a40a5e57d38188821eee7ac804a`.

Relevant donors:

- `duck/living.py`: deterministic utility-style action candidates and hard winner selection; endogenous action options include rest and conditional seek-connection.
- `duck/living_v08.py`: prospective agency uses recent-action repetition penalties and explicit cooldown state for active concerns.

The v0.8 pattern demonstrates a known internal design family for refractory behavior, but it requires recent-action identity, cooldown counters, attempts/deferrals, and substantial prospective machinery. EXP-013 does not copy it.

No root LICENSE file was observed in the current DUCK tree and no license declaration was present in the inspected `pyproject.toml`. Treat source as conceptual archaeology only.

## Narrow external prior art

The relevant external family is switched deterministic control and utility/action selection, not general cognitive architecture.

- Utility-AI documentation explicitly identifies decision oscillation and commonly uses momentum on the previous decision or “keep running until finished.” These methods require prior action/decision state.
- Game-AI utility literature describes inertia as a standard response when frequent rescoring causes oscillation.
- Switched-system control literature uses hysteresis and minimum dwell time to suppress chattering; the switching policy becomes dependent on prior mode or elapsed dwell state.
- Action-oscillation research in discrete policies similarly treats policy inertia as a distinct control problem.

These sources support the general proposition that purely instantaneous winner-take-all arbitration can require dynamical switching state. They do **not** establish that the particular EXP-013 adaptive threshold is biologically or cognitively correct.

Selected external references:

- Deaecto, Souza & Geromel (2014), *Chattering free control of continuous-time switched linear systems*, DOI 10.1049/iet-cta.2013.0065.
- Qi et al. (2020), switched-system hysteresis/dwell-time control discussion.
- Chen et al. (2021), *Addressing Action Oscillations through Learning Policy Inertia*, AAAI, DOI 10.1609/aaai.v35i8.16864.
- Game AI Pro, Chapter 9, utility theory and inertia.
- Utility Intelligence documentation, “Oscillation between decision-target pairs” and Momentum Bonus.

## Candidate causal explanations

| Explanation | Evidence | Status before EXP-013 |
| --- | --- | --- |
| A. tie-breaking | no settled ties; all action orders preserve cycle | falsified as primary cause |
| B. fixed action effects overshoot | rest/work repeatedly clip regulated pressure to exactly zero | strongly supported as part of causal source |
| C. synchronous update order | action-then-drift reduced diagnostic remains period 6 | falsified as primary cause |
| D. linear scoring + hard argmax | deterministic threshold crossings organize every cycle step | supported component |
| E. missing switching hysteresis | standard prior-art family, but simple tested hysteresis only relocates cycle | insufficient in tested simple form |
| F. fatigue/competence interaction | reduced subsystem alone generates cycle; freezing either changes period | strongly supported |
| G. clipping | exact rational zero resets and parameter robustness support this | strongly supported |
| H. lack of a slower arbitration state | one-scalar adaptive threshold is first tested class producing longer and basin-sensitive deterministic dynamics | selected hypothesis class |

## Causal diagnosis

The period-six attractor is not caused by randomness absence, tie breaking, floating-point error, or one unlucky constant.

It is generated by the interaction of:

1. low-dimensional homeostatic drift;
2. hard instantaneous action arbitration against a fixed idle threshold;
3. large fixed relief actions;
4. zero-bound clipping that repeatedly erases residual state;
5. no slower arbitration variable capable of carrying mobilization cost across otherwise identical local threshold crossings.

The first four create a robust finite state lattice. The fifth leaves arbitration memoryless at that slower timescale.

## Minimum EXP-013 hypothesis class

The minimum selected hypothesis is **one global adaptive mobilization threshold**.

This is not semantically owned by any of the existing 11 persistent mechanisms. It is an arbitration state that changes how difficult it is to mobilize another non-idle action immediately after acting, then relaxes.

Accordingly, EXP-013 will provisionally treat it as a **new causal arbitration mechanism and one new persistent scalar**, subject to strict closeout and MBASE-003 if promoted.

No randomness or action identity is required.

## Success criterion frozen before production implementation

The challenger must satisfy all of the following:

1. The frozen v9.5 period-six state/action attractor remains exactly reproducible in control.
2. Across the preregistered 36-start fatigue/competence grid, no challenger tail may have an exact action period <= 30.
3. At least two distinct attractor identities must remain across that grid rather than universal collapse to one orbit.
4. Fatigue and competence remain bounded in [0,1] and both rest and work remain behaviorally expressed.
5. Idle remains available; no permanent fixation or starvation is allowed.
6. Deterministic replay from identical serialized state remains exact.
7. Removing only adaptive-threshold dynamics restores the original period-six attractor.
8. All EXP-002 through EXP-012 behavior and all 20 MBASE-002 capability families remain valid.
9. No RNG, hidden simulator history, renderer state, or test-harness history may influence action.
10. Reviewer passes must fail any candidate that merely relocates behavior to a universal trivial short cycle.

The experiment does not require absence of all mathematical recurrence. The tested organism is a bounded deterministic dynamical system. The target is the reproduced universally attracting, externally obvious, very-short behavioral cycle.

## Claim boundary

If promoted, the strongest expected claim is narrow:

> A compact deterministic homeostatic agent whose instantaneous winner-take-all controller collapses into a universal short limit cycle can acquire longer, basin-sensitive autonomous trajectories by adding one slowly relaxing global mobilization threshold to action arbitration.

This would not establish human action persistence, biological refractory dynamics, optimal control, consciousness, free will, or universal anti-oscillation theory.
