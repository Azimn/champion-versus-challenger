# EXP-007: Delayed Consequence Credit

Status: PRE-REGISTERED before challenger implementation.

## Frozen champion

`v8_subjective_fact` on branch `exp007-delayed-credit`, inherited unchanged from EXP-006. The champion class is `SubjectiveFactCharacter` in `src/lifelike_min/exp006_challenger.py`.

## Reproduced failure

The current habit mechanism updates only the immediately remembered `last_action` / `last_context` pair. When a consequence arrives after unrelated activity, v8 either learns nothing after neutral interveners or can assign the consequence to a more recent unrelated contextual action. The failure is reproduced independently in `exp007_baseline.py` before challenger code exists.

Pre-implementation development cases include:

- delayed positive outcome after 1, 3, and 8 neutral intervening ticks;
- delayed negative outcome after 1, 3, and 8 neutral intervening ticks;
- a later unrelated contextual action that can steal credit;
- multiple potentially eligible earlier context-action pairs;
- an outcome whose context is irrelevant to the earlier action;
- an immediate-outcome control that must continue to work.

These cases are development and baseline-characterization tests. Additional reviewer holdouts must be created only after the challenger implementation is frozen.

## Narrow causal hypothesis

A short, bounded, decaying context-action eligibility trace is sufficient to preserve a temporary causal candidate after an action, allow a later subject-observed consequence in the same context to update that prior action, prevent unrelated contexts from stealing credit, and expire old candidates without importing a general reinforcement-learning architecture.

The hypothesis is provisional. EXP-007 is designed to reject it if the trace cannot survive nearby counterexamples without substantial expansion.

## Minimum proposed representation

Each live trace may contain only fields directly required by the hypothesis:

- `context`
- `action`
- `eligibility`
- `age`

The implementation must have explicit finite capacity and lifetime. Trace creation, decay, matching, replacement, and expiry must be deterministic.

No Q-table, planner, causal graph, global event history, reward model, neural component, episodic-memory subsystem, or general RL framework may be introduced in EXP-007.

## Outcome authority boundary

Delayed credit may use the existing `Event.context` only when that context represents information available in the experienced consequence event. Hidden simulator-only causal identifiers are forbidden. A consequence without an experienced matching context is not permission to infer a hidden cause.

Immediate outcome learning remains an existing behavior and may preserve its current one-step pathway for compatibility.

## Predicted behavioral improvement

Compared with frozen v8, the challenger should:

1. learn from delayed positive outcomes when the relevant context-action trace is still live;
2. reduce the appropriate learned value after delayed negative outcomes;
3. avoid updating unrelated intervening context-action pairs;
4. keep distinct contexts isolated;
5. stop learning from expired traces;
6. remain bounded under capacity pressure;
7. preserve immediate outcome behavior;
8. preserve all EXP-002 through EXP-006 promoted behaviors and renderer invariance.

## Expected failure modes

The reviewer should specifically attempt to expose:

- recency bias toward the wrong action;
- action-order dependence;
- cross-context contamination;
- reward leakage from irrelevant outcomes;
- positive/negative asymmetry;
- accidental trace refresh by irrelevant events;
- excessive persistence or insufficient persistence;
- capacity-sensitive pathological eviction;
- multiple-candidate ambiguity;
- hidden-world or privileged-causal information leakage;
- renderer contamination;
- accidental coupling to concern, belief, relationship, or prospective-cue mechanisms.

## Promotion criteria

Promotion requires all of the following:

- frozen v8 fails the delayed-credit target under matched conditions;
- the challenger materially reduces the reproduced failure;
- positive and negative delayed outcomes behave appropriately;
- unrelated intervening actions do not steal credit;
- context contamination is controlled;
- traces decay and expire;
- capacity is finite and enforced;
- true post-implementation reviewer holdouts survive;
- the full historical promoted regression suite passes;
- renderer invariance passes;
- subjective-state boundaries remain intact;
- disabling or expiring eligibility removes the improvement;
- property-level ablations demonstrate why context, action identity, decay, and bounding matter where behaviorally relevant;
- measured cost is proportionate to the gain.

## Rejection criteria

Reject rather than expand automatically if:

- correct delayed attribution requires privileged simulator causality;
- nearby holdouts show systematic credit leakage that cannot be repaired within the same small representation;
- the trace must grow into a general event history or RL subsystem;
- old promoted behaviors regress;
- renderer behavior becomes causal;
- causal ablation does not remove the improvement;
- cost or state growth is disproportionate to the behavioral effect.

## Causal ablation plan

The primary ablation is frozen v8 under identical events. Additional challenger ablations will disable or manipulate only the trace properties:

- eligibility disabled/zeroed;
- immediate expiry;
- context matching removed;
- decay removed;
- capacity bound relaxed for diagnostic measurement only;
- action identity collapsed.

Ablations are diagnostic and do not automatically justify extra fields.

## Cost metrics

Measure:

- mechanism count;
- representative serialized persistent-state bytes;
- median tick time under a matched mixed-event workload;
- trace-memory cost at capacity;
- additional event-processing cost around trace creation and consequence handling;
- implementation size where useful.

## Evidence policy

The historical record is not rewritten if EXP-007 overturns an earlier claim. CI artifacts are temporary evidence only. Compact permanent results, reviewer findings, donor provenance, and the final promotion/rejection decision must be committed to the repository.
