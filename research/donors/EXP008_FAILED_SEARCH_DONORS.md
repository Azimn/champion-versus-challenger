# EXP-008 Donor Archaeology: Repeated Failed Search

## Behavioral target

Frozen `v9.1_compact` repeatedly searches the last directly observed location of an entity even after repeated subject-experienced negative outcomes have driven the existing contextual action value for that search to `-1.0`. Direct reobservation of another location changes the search immediately. The failure is therefore an interaction failure between already-earned subject-owned factual state and already-earned action-outcome state, not a demonstration that the organism cannot revise any state.

Selected-failure characterization:

- frozen champion: `v9.1_compact`
- frozen commit: `2856ec6a32be0347a9243f6eff6faa404a9a0e6c`
- characterization run: `35051523901`
- characterization artifact: `10429290802`
- result: reproduced across book/drawer, keys/hook, and notebook/desk cases with neutral task contexts and alternating action orders

No production code was changed during failure discovery or characterization.

## Internal archaeology

### Azimn/DUCK

Inspected branch: `motivated-cognition-v0.10`  
Pinned commit: `30a11ea8308ebd0fc89a06bb994ab0e23bd02886`

Relevant files:

- `duck/strategy_v010.py`
- `duck/motivated_cognition.py`

Relevant mechanism:

DUCK stores learned `strategy_success` and context-specific `strategy_contexts`. An experienced outcome updates strategy value, and later selection can query a contextual reliability/value estimate. This demonstrates a useful donor principle: subject-experienced action outcomes can alter later action selection without requiring the system to rewrite an unrelated factual world representation.

Why it is not imported:

DUCK's strategy-learning substrate contains substantially more state and machinery than the current failure requires, including global/contextual strategy values, evidence counts, cognitive regimes, pending strategy context, and associative graph machinery. Importing that substrate would violate the minimal-change objective.

License status:

No root `LICENSE` file was found in the inspected branch. Concept only. No source copied.

### Azimn/persona_engine_PYTHONX

Inspected branch: `main`  
Pinned commit: `65df9144e7f0876b6e61e28d6446c50f283f9db4`

Relevant files:

- `persona_engine/core/habit.py`
- `persona_engine/core/belief_ledger.py`

Relevant mechanisms:

`HabitTracker` represents learned response tendencies with explicit strength and supports strengthening and decay. `BeliefLedger` represents slower evidence-gated belief drift in separate persistent records. Together they illustrate an architectural distinction between action tendency and belief state.

Why it is not imported:

The failed-search reproduction already contains a learned negative action value in the champion's existing habit table. Adding another habit tracker would duplicate state. The belief ledger would add value/range/decay metadata and a new belief representation before evidence shows that explicit belief-confidence state is necessary.

License status:

No root `LICENSE` file was found in the inspected main branch. Concept only. No source copied.

### Azimn/TinyPersonaEngine

Inspected branch: `main`  
Pinned commit: `5eb2e84dbb43c828fae7a1459c9fd13535c7b332`

Relevant family:

- private first-person/perception state
- memory/models with provenance-oriented representation

Prior archaeology found subject-relative experiences and beliefs but no smaller outcome-to-search-choice mechanism that improves on the already-existing state in `v9.1_compact`.

License status:

No root `LICENSE` file was found, and the inspected `pyproject.toml` does not declare a project license. Concept only. No source copied.

### Azimn/FirstPersonLoopTest

Inspected main reference: commit `f61b39d4b70eb5b905a225ec6f4cb728a452e922`, tree `3028d967df583cb2e1aa2c59c6d64cd48a9f1356`.

Prior archaeology found no reward/outcome pathway relevant to this failure. It is not a useful donor for EXP-008.

## External prior art

### BDI failure recovery and belief revision

Archibald et al., *Quantitative modelling and analysis of BDI agents* (Software and Systems Modeling, 2024; published online 2023) describes BDI systems in which action failures are normally sensed and can lead to belief revision or selection of alternative plans. This is direct prior art for the general principle that failed action outcomes should be behaviorally consequential.

Source: https://link.springer.com/article/10.1007/s10270-023-01121-5

### Agent programming and belief/plan updates

*Agent programming in the cognitive era* describes belief-change events and modification/replacement of intentions when a selected plan fails. It establishes a larger, conventional architecture for reacting to conflicting evidence or failed plans.

Source: https://link.springer.com/article/10.1007/s10458-020-09453-y

### Formal belief revision after observation

Engesser, Herzig, and Perrotin, *Towards Epistemic-Doxastic Planning with Observation and Revision* (AAAI 2024), provides a formal belief-revision framework for observation in the presence of false beliefs.

Source: https://ojs.aaai.org/index.php/AAAI/article/view/28919

Why these are not the first implementation:

All of these external lines justify taking failure feedback seriously, but explicit belief revision, epistemic planning, probabilistic belief state, and plan replacement are qualitatively larger than necessary for the first test. The current champion already has both pieces of information needed for a smaller hypothesis:

1. a subject-owned last-observed location fact;
2. a learned contextual action value reflecting repeated experienced failure.

## Donor conclusion

The smallest justified next test is not a new belief system.

The donor-supported hypothesis is to allow existing subject-owned factual evidence and existing learned action-value evidence to jointly influence a search choice when the outcome attribution is subject-accessible.

This should first be tested as a policy interaction with **zero new persistent fields**.

Only if that interaction fails scientifically should EXP-008 escalate to explicit confidence, probabilistic belief, contradiction records, plan-failure memory, or another new persistent mechanism.

## Reuse boundary

- No donor source code is copied.
- No donor architecture is merged.
- License status is unresolved for the inspected internal donors, so only high-level concepts are used.
- External prior art supplies scientific context, not implementation code.
