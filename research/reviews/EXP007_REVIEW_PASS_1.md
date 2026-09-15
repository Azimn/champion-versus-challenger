# EXP-007 Adversarial Review Pass 1

Status: REJECTED FIRST IMPLEMENTATION PENDING MINIMAL CORRECTION

Reviewed implementation: first frozen `v9_eligibility_trace_candidate`, production mechanism introduced at commit `94c29f739a4c06a2378a63b3c1e2b1119743c6dc`.

Reviewer holdouts were created only after the implementation and developer evaluation were frozen.

Workflow evidence: EXP-007 run `35016930519`, artifact `exp007-reviewer-pass-1`, artifact ID `10415956205`.

## Result

Nine of ten post-implementation holdouts passed.

Passing holdouts:

- same-context ambiguity caused conservative abstention rather than hidden-cause guessing;
- two context-specific outcomes arriving in reverse action order updated the correct distinct actions;
- similar context names did not leak credit;
- zero-valued outcomes neither learned nor refreshed a trace;
- perception and hidden-world bookkeeping events did not create eligibility records;
- the target survived exactly-at-capacity interference;
- a genuinely evicted trace could not later reconstruct privileged causality;
- positive and negative outcomes were symmetric at equal delay from a neutral learned value;
- novel action names, context names, spacings, and irrelevant social events generalized.

One holdout failed:

`live_boundary_consequence`

Immediately before the consequence event, the trace was still present with:

- context: `orchard`
- action: `inspect`
- age: `10`
- eligibility: `0.137448`

The subsequent matching consequence produced learned value `0.0`.

## Reviewer diagnosis

The failure is classified as an **implementation event-ordering defect**.

It does not currently falsify the eligibility-trace mechanism or the narrow EXP-007 hypothesis. The representation already contained the required subject-owned context, action identity, eligibility value, and age at the instant the consequence event arrived. The loss occurred because the inherited runtime executes `_drift()` before `_process_event()`. The EXP-007 trace therefore crossed its expiry boundary during the consequence tick and was deleted before that same event could resolve it.

The distinction matters. Extending trace lifetime globally would change the mechanism's temporal semantics. Adding causal identifiers would add unjustified state. Neither is warranted by this failure.

## Developer response constraint

Attempt to fix the existing rule without changing the four-field persistent trace representation or adding a new mechanism.

A permissible minimal correction may preserve, transiently and for the current event only, a record that crossed its expiry boundary during that event so that an already-live trace can be resolved by the arriving consequence. Such transient control state must not be serialized, must not survive into a later event, and must not allow a trace that expired on a prior unrelated event to influence learning.

After correction, rerun:

1. the failing boundary holdout;
2. all nine passing reviewer holdouts;
3. all EXP-007 development tests;
4. EXP-002 through EXP-006 regressions;
5. renderer invariance;
6. causal/property ablations;
7. cost measurements.

Then create a second reviewer pass with genuinely new failure modes rather than merely replaying pass 1.
