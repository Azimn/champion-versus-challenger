# EXP-007 Second-Order Methodological Review

Status: CHALLENGER SURVIVES BEHAVIORAL REVIEW, BUT SIMPLIFICATION REQUIRED BEFORE PROMOTION

This review critiques the research claim and experimental validity rather than merely code correctness.

## 1. Are the tests merely encoding the implementation?

Not entirely. The pre-implementation development cases specify behavioral consequences: delayed positive/negative learning, intervening-action isolation, context isolation, expiry, boundedness, and immediate-learning compatibility. Two later reviewer passes were generated after implementation and varied names, contexts, timing, ordering, valence, reward magnitude, capacity pressure, ambiguity, hidden-world events, and expiry boundaries.

However, several diagnostics inspect trace state directly. Those diagnostics are useful for causal intelligibility but must not be confused with independent behavioral evidence. Promotion therefore rests on both externally observable learned choices/values and internal trace diagnostics.

## 2. Is "delayed credit" defined too broadly?

Yes, if stated without qualification.

The evidence supports **context-cued delayed consequence credit**. The challenger can retain a recent context-action candidate and use a later experienced outcome carrying the same canonical context to update the appropriate learned preference.

The experiment does **not** establish general causal attribution across arbitrary unlabeled delayed consequences. Reviewer pass 2 explicitly confirms that a delayed consequence with no experienced matching context produces no learning. This conservative abstention is preferable to privileged guessing, but the scientific claim must remain narrow.

Recommended promoted identifier if the experiment survives: `v9_context_eligibility_trace` rather than an unqualified claim of general delayed credit.

## 3. Does the environment reveal information a real subject would not have?

Potentially, if `Event.context` is populated from hidden simulator causality rather than experienced situation information.

EXP-007 pre-registered an authority constraint: outcome context may be used only when it represents information available in the experienced consequence event. The current runtime has no provenance field that can mechanically prove this. The experiments therefore enforce the boundary procedurally:

- hidden-world bookkeeping events do not create eligibility;
- outcomes with no experienced context do not trigger delayed attribution;
- mismatched contexts do not trigger attribution;
- same-context ambiguity across two different actions causes abstention rather than hidden-cause inference.

This is sufficient for the present experiment, but host integrations must preserve the context-authority contract. EXP-007 does not justify adding provenance metadata solely to enforce a boundary already controlled by the experimental interface.

## 4. Is the mechanism only a scripted delayed lookup?

It is deliberately small, but not merely a scenario-specific lookup. The selected update depends causally on:

- action identity;
- context identity;
- temporary persistence;
- temporal age/decay;
- finite capacity;
- experienced outcome magnitude and sign.

Ablations show that disabling the trace removes the gain, removing context specificity creates contamination, removing action identity eliminates target learning, and removing decay eliminates the recency gradient. Post-implementation holdouts generalize across previously unseen names, contexts, spacings, ordering, signs, and magnitudes.

The mechanism remains much narrower than TD learning or causal inference and should be described that way.

## 5. Could the same behavior be produced by simpler existing machinery?

The existing one-step habit learner cannot survive unrelated intervening actions because it stores only `last_action` and `last_context`. Generalizing it to a short per-context recent-action buffer is functionally the new eligibility mechanism.

However, the current challenger contains a genuine redundancy: each record stores both `age` and `eligibility`, while eligibility is deterministically `eligibility_decay ** age` after creation/refresh. The stored float therefore carries no independent information.

A second redundancy also exists: `minimum_eligibility = 0.05` is behaviorally unreachable before `max_eligibility_age = 10` at `eligibility_decay = 0.82`. At age 10, computed eligibility remains approximately 0.137. The age bound always removes the trace first.

These redundancies conflict with the project's smallest-organism objective. They should be removed before promotion and all evidence rerun. The simplified persistent record should contain only:

- `context`;
- `action`;
- `age`.

Eligibility strength should be computed from age when needed. The minimum-eligibility cutoff should be deleted unless a future failure demonstrates independent value.

## 6. Capacity brittleness

The production bound is four live distinct context-action pairs. Reviewer pass 2 confirms that a target trace is evicted after four newer distinct pairs. This is a real capacity cliff.

The review does not recommend increasing the bound merely to move the cliff from four to six or eight. No evidence currently identifies a superior threshold, and a larger arbitrary bound would increase worst-case state without changing the mechanism. The empirical claim must therefore include the bound: v9 can bridge delayed outcomes while the relevant pair remains among the four live eligible records and within the temporal lifetime.

Capacity-dependent state cost must be reported explicitly.

## 7. Would a human observer notice the difference?

No human-observer study has been run. The behavioral difference is nevertheless externally visible: frozen v8 either fails to learn after delay or credits an unrelated recent action, while the challenger changes later choice after delayed positive/negative consequences and can extinguish a previously learned preference after repeated delayed failures.

This is strong enough for a branch-local mechanism promotion if all other criteria survive, but it is not evidence that human observers rate the whole organism as lifelike.

## Decision from second-order review

Do not promote the current implementation unchanged.

Perform a structural simplification ablation by removing stored eligibility strength and the unreachable minimum-eligibility cutoff while preserving the same context-cued temporal-credit behavior. Then rerun:

- all EXP-007 development cases;
- both reviewer passes;
- historical EXP-002 through EXP-006 regressions;
- renderer invariance;
- causal/property ablations;
- state and runtime cost measurements.

If behavior survives, prefer the smaller representation and update the final EXP-007 claim accordingly.
