# EXP-010 Preregistration: Minimum Information for Suppression Versus Deletion

Status at this commit: **PREREGISTERED, NO CHALLENGER IMPLEMENTATION EXISTS**.

Frozen champion: `v9.2_unresolved_concern_persistence`

Frozen branch: `champion-v9-2-unresolved-concern-persistence`

Frozen branch commit: `bd1ca22ca58e82012f1a8237e3de4bfee4dbf59d`

Evaluated production implementation remains byte-identical to commit: `b5cc3e109ab2fa4de0421dc113009d1ee7fb050d`

Counted persistent causal mechanisms: 11.

## Reproduced target failure

`suppressed_concern_never_returns` is reproduced unchanged.

History:

1. assign unfinished `A` at intensity 0.5;
2. assign stronger `B` at intensity 1.0;
3. assign stronger `C` at intensity 0.9;
4. capacity two retains `B` and `C` and deletes `A`;
5. resolve/cancel `B`;
6. resolve/cancel `C`;
7. `A` never returns.

The failure is capacity deletion, not low activation. EXP-009 already established that ledger membership can represent unresolved existence while the scalar represents momentary activation.

## Foundational information-loss result

Corrected pre-archaeology foundation run: `35168343395`.

Artifact: `10476051325`.

The first foundation run `35168160541` is preserved as a harness-metric failure because it measured diagnostic bytes with a different serialization helper. The complete repository suite, strict v9.2 earned contract, target reproduction, and information-collapse result all passed in that run. Production was unchanged.

Matched histories were constructed with equal event counts and equal non-concern side effects:

- History A used weak identity `low_priority` before B and C displaced it.
- History B used a different weak identity `matched_control` before the same B and C history.

Before capacity eviction the organism states differ only in the weak concern identity. At the C insertion that forces eviction, complete canonical persistent states become byte-identical. They remain identical after B resolves and after C resolves.

No `low_priority` identity survives in:

- concern ledger;
- prospective commitments;
- habits;
- relationships;
- partner reliability;
- subjective location facts;
- eligibility records;
- canonical serialization.

Therefore the current representation creates a many-to-one state transition: “A existed and was evicted” and “A never existed” collapse to the same subject-owned state. A deterministic policy operating only on current organism state cannot later distinguish those histories.

### Information lower bound

At least concern identity must survive if later return is to distinguish an actually unfinished A from a history in which A never existed.

Identity alone is enough to break state identity, but it is not yet enough to preserve the champion's existing concern semantics without another rule. Current concern behavior depends on an identity plus a continuously decaying activation scalar. If only identity were retained, return strength would have to be invented, reset, inferred from unavailable history, or supplied by a new event. That would add a reactivation policy not currently earned.

The smallest semantically conservative retained record is therefore the already-existing concern record: `{identity: activation}`.

## Causal characterization of eviction

Existing capacity enforcement keeps the `max_concerns` highest current concern strengths. It is strength-based, not simply recency-based.

Foundation probes established:

- old-but-strong A survives a weaker later C;
- recent-but-weak A can be immediately discarded;
- weak A is lost regardless of whether B or C later resolves first;
- long unrelated delay does not recreate A;
- equal-strength ties inherit stable insertion ordering from Python's stable sort/dictionary order;
- cancellation after eviction cannot reveal A because no A representation remains.

## Candidate semantics

These definitions add no persistent status flags.

- **active concern**: the strongest currently represented unresolved concern, exposed through the existing deterministic `active_concern` view.
- **low-activation concern**: an unresolved ledger entry whose scalar has decayed and exerts little current pressure.
- **suppressed concern**: an unresolved concern identity still represented in the bounded ledger but not currently selected as `active_concern` because stronger represented concerns exist.
- **evicted concern**: an unresolved identity removed by bounded-capacity replacement. Under current state it is indistinguishable from never having existed unless some independent semantically valid representation survives.
- **resolved concern**: removed through the already-earned work-mediated completion path.
- **cancelled concern**: removed through explicit `task_cancel`.

The experiment tests whether a third represented unresolved concern can function as suppressed state using the same concern mechanism, not whether a new suppression status is required.

## Minimum candidate comparison before implementation

### A. Replacement-policy-only change at capacity two

Persistent information: still at most two `{identity: activation}` records.

Mechanism change: policy only.

Prediction: cannot preserve all three simultaneously unresolved identities A, B, and C. Any deterministic capacity-two replacement rule must discard at least one identity. It may choose a different victim, but cannot solve the semantic class without sacrificing another unresolved concern.

Decision: rejected before implementation by the representation lower bound.

### B. Existing concern capacity 2 -> 3

Persistent information: one additional possible existing `{identity: activation}` record.

Mechanism change: none anticipated. Same concern ledger, same activation decay, same winner selection, same assignment, same cancellation, same work resolution, same strength competition.

Semantic change: greater representational capacity only.

Boundedness: remains fixed at three concern records.

Prediction: A remains represented but non-dominant while B and C are stronger. When stronger records terminate, existing winner selection makes A behaviorally eligible again. No return bonus or new reactivation rule is needed because A's activation continues to decay under existing semantics.

Decision: **selected hypothesis**.

### C. One separate minimal suppressed-concern record

Persistent information: at least identity; likely identity plus enough activation information to avoid arbitrary reset.

Mechanism/state change: introduces a second concern storage role plus rules for transfer into it, decay/freeze, cancellation/completion while suppressed, return, duplication, and overflow.

Prediction: can solve the target but moves capacity eviction one layer deeper and adds distinct suppression semantics.

Decision: rejected before implementation unless capacity expansion fails.

### D. Reuse prospective commitment, eligibility, habit, relationship, fact, or narrative memory state

Persistent information: available but semantically unrelated.

Decision: rejected. Spare capacity does not justify semantic aliasing. Active concerns and prospective commitments were already empirically shown to require independent meanings.

### E. DUCK-style explicit latent/inhibited motive status

Persistent information: identity plus status and several additional motive variables/rules.

Decision: rejected as unnecessary architecture for the reproduced lower bound.

## Selected minimum hypothesis

**H1:** Restoring the existing concern ledger from capacity two to capacity three, with no other production change, is sufficient for the selected three-simultaneous-unresolved-concern counterexample. The third record will be behaviorally suppressed automatically because only the strongest ledger entry is exposed as `active_concern` and contributes concern strength to work scoring.

This predicts that EXP-010 can remain at 11 counted mechanisms while increasing bounded representational capacity.

## Expected behavioral improvement

In the target history:

- A remains causally represented while B and C dominate;
- A is not `active_concern` while either stronger concern remains stronger;
- resolving B and C does not require special recovery code;
- A becomes the derived active concern once it is the strongest remaining unresolved record;
- cancellation/completion of A removes it normally;
- serialize/destroy/restore preserves whichever three unresolved identities and strengths currently exist.

## Expected non-effects

EXP-010 is not expected to change:

- relationship behavior;
- affect dynamics;
- habits;
- uncertainty policy;
- prospective commitment behavior or capacity;
- subjective facts;
- delayed-credit eligibility traces or capacity;
- renderer invariance;
- subjective-access boundaries;
- concern activation decay rate;
- work-mediated resolution threshold;
- task cancellation semantics;
- general forgetting;
- prospective commitment forgetting;
- habit weakening;
- deterministic rhythm.

## Development tests

Development evidence will include:

1. frozen v9.2 target reproduction and matched challenger history;
2. complete internal trace for A/B/C insertion, active winner, B/C resolution, and A return;
3. non-dominance while A is weaker;
4. return after one slot opens and after both stronger competitors terminate;
5. B-first and C-first termination order;
6. cancel versus work-mediated completion of stronger concerns;
7. 10, 100, and 1,000 unrelated-event suppression intervals;
8. 3, 4, 5, and larger concern sequences to expose the new bounded-loss boundary;
9. capacity tournament 2, 3, 4, selecting the smallest capacity that fixes the preregistered target;
10. cancel A while non-dominant;
11. work opportunity while A is non-dominant;
12. same-name reassignment while non-dominant;
13. active A plus prospective A coexistence and separation;
14. serialize/destroy/restore with A active, suppressed, returned, resolved, and cancelled;
15. repeated suppression/resumption cycles;
16. historical earned contract with the intended capacity change carved out explicitly rather than silently redefining v9.1's previous capacity-two result.

## Causal ablation

Primary ablation: set the challenger concern capacity back to two while leaving all other EXP-010 code/semantics unchanged. The original `suppressed_concern_never_returns` failure must reappear.

Property diagnostics:

- capacity 4 should not improve the preregistered three-identity target beyond capacity 3, but should consume more state;
- an identity-removal diagnostic should demonstrate that erasing A again makes return impossible;
- no new return policy is expected, so there is no separate return-rule ablation in the selected hypothesis.

## Reviewer holdout reservation

No reviewer-generation-1 probes will be authored until the production challenger and development suite are frozen.

Reviewer generation 1 will then attack at least:

- completion/cancellation during suppression;
- very long suppression;
- multiple suppressed demands beyond capacity;
- equal-strength ties and order permutations;
- same-name reassignment;
- prospective overlap;
- reconstruction;
- oscillation/thrashing;
- repeated suppression/resumption;
- weak/strong return ordering;
- storage leaks and ghost resurrection.

Reviewer generation 2 will be authored only after generation 1 is classified and any justified minimal correction is frozen.

## Cost measures

Report separately:

- mechanism count;
- persistent field/schema keys;
- concern capacity;
- prospective capacity;
- eligibility capacity;
- fresh canonical and diagnostic bytes;
- representative canonical and diagnostic bytes;
- maximum bounded canonical and diagnostic bytes;
- marginal bytes from the third concern record;
- marginal bytes for capacity 4;
- idle tick cost at 0/1/2/3 concerns;
- assignment/competition cost;
- cancellation cost;
- work-resolution/resume cost;
- canonical serialization and reconstruction cost.

Hosted CI timings are engineering estimates only.

## Promotion criteria

PROMOTE only if all are true:

- target suppressed unfinished identity survives temporary competition;
- concern storage remains bounded;
- A is behaviorally non-dominant while stronger concerns exist;
- legitimate completion removes the appropriate concern;
- legitimate cancellation removes the appropriate concern;
- A returns only because subject-owned concern state survived;
- no simulator/test-harness history is consulted;
- reconstruction preserves active/suppressed/returned/terminated states;
- capacity two causal ablation restores the failure;
- capacity three is sufficient and capacity four is unnecessary for the preregistered target;
- historical behaviors survive except the intentionally changed capacity invariant;
- two reviewer generations survive or all preserved failures are validly adjudicated without post-hoc production broadening;
- mechanism count, capacity, fields, and bytes are reported separately;
- second-order review supports treating the result as increased representational capacity rather than a new cognitive mechanism.

## Rejection criteria

REJECT if any of these occur:

- capacity three does not recover A;
- A remains behaviorally dominant despite stronger B/C;
- recovery requires hidden history or an extra unstated rule;
- cancellation/completion can resurrect A incorrectly;
- the new capacity causes unbounded growth;
- serialization loses or duplicates concern identity;
- fixing reviewer failures requires adding a new suppression subsystem within this experiment;
- historical regressions appear outside the intended capacity change;
- capacity four is required for the preregistered three-identity target;
- the claimed 11-mechanism interpretation cannot be defended after second-order review.

## Narrow claim boundary

If promoted, EXP-010 may support only a claim of this form:

> A bounded unresolved concern that is temporarily non-dominant can remain represented in the existing concern mechanism and later regain behavioral eligibility when stronger represented concerns terminate, provided the mechanism has sufficient bounded capacity to preserve its identity and activation.

EXP-010 will not establish general goal memory, planning, BDI architecture, human working-memory capacity, optimal resource arbitration, unbounded persistence, or human-like forgetting.
