# EXP-007 Donor Archaeology: Delayed Consequence Credit

This record was completed after the frozen v8 baseline was reproduced and before production challenger implementation.

## Research question

What is the smallest historically supported mechanism capable of assigning a delayed experienced consequence to an earlier context-action pair without importing a general reinforcement-learning architecture?

## Internal donor: Azimn/DUCK

Repository: `https://github.com/Azimn/DUCK`

Inspected branch: `motivated-cognition-v0.10`

Commit: `30a11ea8308ebd0fc89a06bb994ab0e23bd02886`

Relevant modules:

- `duck/strategy_v010.py`
- `duck/motivated_cognition.py`

Observed behavior/mechanism:

- bounded strategy values;
- context-sensitive strategy reliability;
- a serialized `pending_strategy_context` containing an action identifier and cognitive regime;
- immediate `record_strategy_outcome(...)` updates to global and regime-specific strategy values after a registered outcome.

Fit to reproduced failure:

Partial only. DUCK demonstrates that action-selection context can be retained until an outcome and that subsequent outcomes can update learned strategy values. The inspected mechanism does not provide a short multi-action decaying context-action eligibility trace that can survive arbitrary unrelated intervening behavior while preventing later unrelated actions from stealing credit.

Reuse decision:

Conceptual donor only. Importing the motivated-cognition subsystem would add motives, associative graphs, strategy calibration, cognitive regimes, and other machinery not justified by EXP-007.

License:

No root `LICENSE` file was present on the inspected branch and no license declaration was established from the package metadata during this archaeology pass. No DUCK source is copied.

## Internal donor: Azimn/persona_engine_PYTHONX

Repository: `https://github.com/Azimn/persona_engine_PYTHONX`

Inspected branch: `main`

Commit: `9965d9316b61089293310444af934316ef752ba6`

Relevant module:

- `persona_engine/core/habit.py`

Observed behavior/mechanism:

The habit system stores deterministic learned preferences and applies decay. It is useful evidence that a small bounded learning mechanism can remain context-sensitive and cheap.

Fit to reproduced failure:

Negative. Inspection of the habit and engine paths did not reveal delayed reward attribution, an eligibility trace, or a recent-action buffer that links a later consequence to an earlier action after intervening activity.

Reuse decision:

No code or architecture reused. The existing EXP-002 habit table is already smaller for the present experiment.

License:

No root license file was present in the inspected tree and `pyproject.toml` contains no project license declaration. Concept only; no source copied.

## Internal donor: Azimn/TinyPersonaEngine

Repository: `https://github.com/Azimn/TinyPersonaEngine`

Inspected branch: `main`

Commit: `5eb2e84dbb43c828fae7a1459c9fd13535c7b332`

Relevant modules:

- `src/living_entity_firstperson/memory.py`
- `src/living_entity_firstperson/models.py`

Observed behavior/mechanism:

The project can retain first-person experiences, percepts, memory associations, goals, beliefs, and action pressures with provenance.

Fit to reproduced failure:

Negative for EXP-007. The inspected memory layer records or retrieves experiences but does not assign a later reward or punishment to an earlier context-action pair. Reusing it would introduce a generalized memory abstraction when the reproduced failure requires only temporary action eligibility.

Reuse decision:

No code reused.

License:

No explicit project license was established in the inspected root/package metadata during this pass. No source copied.

## Internal donor: Azimn/FirstPersonLoopTest

Repository: `https://github.com/Azimn/FirstPersonLoopTest`

Inspected branch: `main`

Inspected tree: `3028d967df583cb2e1aa2c59c6d64cd48a9f1356`

Relevant module:

- `subjective_character_loop_v0_1/subjective_loop.py`

Observed behavior/mechanism:

First-person loop and subjective processing experiments.

Fit to reproduced failure:

Negative. Searches and direct inspection found no reward-attribution pathway or delayed action-outcome mechanism relevant to EXP-007.

Reuse decision:

None.

License:

No root license file is present in the inspected repository tree. No source copied.

## Internal archaeology conclusion

The second archaeology pass found useful neighboring mechanisms but no internal implementation that solves the reproduced failure more minimally than a clean experiment-specific trace. The strongest internal analogue is DUCK's retained pending strategy context, but importing that subsystem would be disproportionate and still would not directly solve multiple intervening actions.

This is a negative result worth preserving: the EXP-007 challenger is not being written because internal reuse was ignored. It is being written because the inspected internal mechanisms either address a different problem or carry unnecessary architecture.

## External prior art: eligibility traces

Primary sources:

- Sutton, R. S. (1988). *Learning to Predict by the Methods of Temporal Differences*. Machine Learning, 3, 9-44.
- Sutton, R. S., and Barto, A. G. *Reinforcement Learning: An Introduction*, 2nd ed., Chapter 12, Eligibility Traces. Official material: `https://incompleteideas.net/`
- Precup, D., Sutton, R. S., and Singh, S. (2000). *Eligibility Traces for Off-Policy Policy Evaluation*.
- Maei, H. R., and Sutton, R. S. (2010). *GQ(lambda): A General Gradient Algorithm for Temporal-Difference Prediction Learning with Eligibility Traces*.

Narrow relevance:

Eligibility traces are historically used to keep prior states, features, or state-action events temporarily eligible for later learning updates. Sutton's publication record explicitly describes them as bridging temporal gaps in cause and effect and prior work characterizes credit as varying with recency.

EXP-007 does **not** import TD(lambda), Sarsa(lambda), Q(lambda), value functions, bootstrapping, policies, or a general RL algorithm. The experiment extracts only the narrower causal idea supported by this literature:

> a recent context-action event can retain a bounded decaying eligibility value so a later experienced consequence can update it.

## Selected hypothesis and reuse boundary

Selected mechanism: independently implemented bounded decaying context-action eligibility records.

Code reuse: none.

Concept reuse: eligibility/recency trace principle only.

Required fields remain those pre-registered before implementation:

- context;
- action;
- eligibility strength;
- age.

The challenger must remain finite, deterministic, context-gated, and unable to infer hidden simulator causality. If this representation cannot survive the adversarial review without expanding into a general history or reward-attribution system, the mechanism should be rejected rather than enlarged automatically.
