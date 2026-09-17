# EXP-012 Archaeology: Habit Temporal Plasticity

Frozen basis: `v9.4_prospective_capacity_three`, commit `5f949c6e882f780e1d4c07f0b6b3bccf330936aa`.

Foundation workflow: `35277270258`.

Target: `rewarded_routine_never_weakens`.

No EXP-012 challenger exists at the time of this record.

## Current causal localization

The frozen habit representation is:

`(context, action) -> signed scalar action value`

Reward changes that scalar. Temporary eligibility records can connect later outcomes to earlier context/action pairs, but those records expire after the already-earned eligibility lifetime.

After eligibility expiration there is no habit-specific:

- age;
- last-reinforcement tick;
- last-use tick;
- use count;
- confidence;
- activation;
- separate extinction state.

The EXP-012 matched-history test shows that a habit reinforced near the beginning of a lifetime and an otherwise identical habit reinforced near the end can be canonically identical at the same lifetime tick. Therefore the frozen state cannot retrospectively infer which identical scalar is older.

Unlike the prospective mechanism, however, the habit mechanism already owns a mutable scalar. An online update rule could make stale and recent experience diverge prospectively without adding a second field. That zero-new-state path must be tested before temporal metadata is earned.

## Internal archaeology

### persona_engine_PYTHONX

Pinned tree: `65df9144e7f0876b6e61e28d6446c50f283f9db4`.

Relevant donor: `persona_engine/core/habit.py`.

That earlier system represented a habit with:

- identity/name;
- trigger;
- response pattern;
- scalar strength;
- use count;
- `last_used` wall-clock timestamp;
- evidence log.

It also exposed `decay_all(amount=0.001)`, subtracting a small amount from every habit strength toward zero.

Use here: **conceptual donor only**.

It establishes that earlier project work already separated habit identity from mutable strength and experimented with weakening. It does **not** justify importing `last_used`, timestamps, evidence logs, use counts, or the exact decay constant into the compact champion. Those would be representational additions and are not yet earned.

### TinyPersonaEngine

Pinned tree: `5eb2e84dbb43c828fae7a1459c9fd13535c7b332`.

Inspection found no dedicated habit-strength mechanism comparable to the compact champion or persona_engine habit tracker. It therefore provides no narrower reusable mechanism for this failure.

## Narrow external prior art

The external literature gives two constraints rather than one obvious implementation.

1. Instrumental/Pavlovian extinction is generally driven by changed outcome contingencies or nonreinforcement, and substantial evidence treats extinction as new or inhibitory learning rather than simple erasure of the original association. Relevant reviews include Bouton 2002 (PMID 12437938), Trask et al./Bouton instrumental extinction review 2018 (PMID 30350221), and the 2021 Physiological Reviews extinction review (PMID 32970967).

2. Habits are not necessarily permanent. Bouton's selective review, `Habit and persistence` (PMID 38149526), concludes that surprisingly little evidence supports permanent or unusually persistent habits and emphasizes context specificity. Recent intensive longitudinal human work on deliberate habit degradation found habit strength often declines over time with substantial individual heterogeneity and commonly asymptotic/logistic trajectories (Edgren, Baretta & Inauen; PMID 39456116). A newer follow-up reports lower habit strength on days with non-performance and effects of cue encounter/reward (PMID 41664447).

These sources do **not** establish that every unrelated event should automatically erase a learned action value. They therefore argue against treating generic global decay as settled psychology.

## Candidate solution classes

### A. Frozen semantics / no temporal plasticity

Habit values change only when a reward outcome is attributed to the context/action pair.

Advantages:
- preserves current action-value interpretation;
- no incidental forgetting.

Failure:
- exactly reproduces the target;
- cannot distinguish an ancient and recently supported equal-valued routine after eligibility expires.

### B. Context-exposure extinction only

Update the existing scalar toward neutral when the relevant context/action is experienced without expected reinforcement.

Advantages:
- aligns more directly with instrumental extinction/nonreward literature;
- zero new persistent state may be possible.

Limitation:
- it cannot, by itself, distinguish a 1000-event-old routine from a recent one on the **first** return if the relevant context/action was never re-experienced during the gap.
- therefore it does not solve the exact nonuse continuity target preregistered for EXP-012.

Treat as an important diagnostic/control, not the first production hypothesis.

### C. Online nonuse attenuation of the existing scalar

While a habit is not being reinforced, gradually move its existing signed scalar toward neutral as subject-experienced events accumulate. Reinforcement can subsequently strengthen it again. Habit identity/context/action remain represented by the existing key.

Advantages:
- zero new persistent fields;
- zero new counted mechanisms;
- can make old and recent histories diverge before the next cue encounter;
- can produce an observable old-vs-recent action preference rather than a metric-only change.

Risks:
- event count becomes an implicit experiential clock;
- generic attenuation can weaken old negative as well as positive values;
- too-fast attenuation recreates the opposite artificiality: rapid arbitrary forgetting;
- applying the same rate to all contexts may be psychologically crude;
- the current scalar mixes learned utility and tendency/strength, so attenuation changes its semantics.

This is the minimum first challenger class because it tests the existing scalar before adding temporal metadata.

### D. Per-habit last-use / last-reinforcement metadata

Add a tick/timestamp or age field and compute recency explicitly.

Advantages:
- represents the missing information directly;
- can distinguish elapsed age without continuously mutating the value.

Cost:
- new persistent record schema and bytes;
- imports a design element seen in persona_engine before zero-state alternatives are falsified.

**Not yet earned.** Do not implement in the first EXP-012 challenger.

### E. Separate extinction/confidence trace

Keep action value intact and add another variable representing current confidence, inhibition, or extinction learning.

Advantages:
- semantically cleaner distinction between learned outcome value and present expression.

Cost:
- new state and potentially a new causal mechanism;
- significantly wider than the current failure requires.

**Not earned.**

## Selection

Pre-register class C first: online nonuse attenuation of the already-existing signed habit scalar, with no timestamp, age, confidence, additional trace, or new mechanism.

The experiment must explicitly compare it against:

- frozen no-attenuation control;
- context-exposure-only extinction diagnostic;
- multiple attenuation rates/half-lives;
- short-gap retention;
- old-vs-recent competition;
- repeated reinforcement/refresh;
- positive and negative values;
- delayed-credit interaction;
- serialization/reconstruction;
- full historical behavior.

If the zero-new-state hypothesis cannot solve the target without unacceptable collateral loss, EXP-012 should be rejected rather than silently adding temporal metadata.
