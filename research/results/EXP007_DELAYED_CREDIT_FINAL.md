# EXP-007 Final Result: Context-Cued Delayed Consequence Credit

**Decision:** PROMOTE  
**Promoted branch-local champion:** `v9_context_eligibility_trace`  
**Frozen production-behavior commit:** `8c1e692e2b115200e3d758e481eb12576aced907`  
**Closeout evidence commit:** `52b3f28c0b099140b78b7a3d6a84b12e50430794`  
**Closeout CI run:** `35025493280`  
**Closeout artifact:** `exp007-closeout`, artifact ID `10419755673`

This result is branch-local experimental promotion. It does not alter the repository's still-unassigned global external-baseline Champion 0.

## Decision

EXP-007 promotes. The final implementation contains one added counted mechanism: a bounded context-action temporal trace. Each record contains only:

- `context`
- `action`
- `age`

Eligibility strength is derived as `0.82 ** age` when needed. It is not stored. The final empirically selected capacity is **two live records**, and the finite lifetime is **age 0 through age 10**.

The complete closeout gate passed. Frozen `v8_subjective_fact` reproduced at 11 counted mechanisms and exactly 451 representative serialized bytes. The final challenger reproduced all previously promoted behavior, passed the EXP-007 developer suite, passed the surviving semantic claims from reviewer pass 1, passed reviewer passes 2 and 3, passed the repeated causal ablations, passed the event-boundary audit, passed the corrected subjective-access audit, and demonstrated that capacity two is the smallest tested bound that preserves the current earned behavior.

## BEHAVIOR DEMONSTRATED

The organism can retain bounded subject-accessible evidence that a recent context-action pair occurred and let a later experienced consequence influence that behavior across unrelated intervening activity when subjective context uniquely identifies one live candidate.

The demonstrated behavior includes delayed positive and negative updates at several short delays, isolation from unrelated intervening contexts, resistance to later-action reward theft, monotonic temporal weakening, finite expiry, opposite-valence updates, repeated-action refresh, conservative abstention under same-context ambiguity, and later action-choice changes following repeated delayed consequences.

## MECHANISM CAUSALLY SUPPORTED

A **two-record, finite-lifetime, age-weighted context-action trace** is sufficient for the tested form of context-cued delayed consequence credit.

Causal support was repeated against the final three-field representation. Disabling the trace or forcing immediate expiry removes delayed-credit learning. Removing context specificity causes contamination. Removing action identity destroys useful attribution. Removing temporal decay removes the demonstrated recency gradient. Relaxing the capacity bound increases retained state without demonstrating additional value under the currently earned behavioral suite.

## CLAIMS NOT ESTABLISHED

EXP-007 does not establish:

- general causal inference;
- arbitrary long-horizon reinforcement learning;
- hidden-cause attribution;
- resolution of ambiguous same-context causes;
- unbounded temporal credit;
- planning;
- general episodic memory.

An unlabeled delayed consequence does not receive hidden-cause attribution merely because the simulator knows its true source. When the organism lacks sufficient subject-accessible evidence, it abstains.

## Experimental trajectory preserved

### 1. Pre-registration

EXP-007 began from the reproduced v8 failure. Frozen v8 either failed to learn after neutral intervening activity or could update a more recent unrelated context-action pair because the existing habit mechanism retained only one immediate `last_action` / `last_context` pair.

The preregistered challenger proposed a bounded decaying context-action eligibility trace. The initial proposed representation contained `context`, `action`, stored `eligibility`, and `age`, with provisional capacity four.

### 2. First developer implementation

The first four-field challenger passed the preregistered developer suite and causal/property ablations. It preserved all earlier promoted probes and renderer invariance.

### 3. First reviewer rejection

Reviewer pass 1 found a real event-boundary defect. A trace could be live immediately before a consequence event but expire in pre-event drift before the consequence was processed. The first implementation was therefore not promoted.

### 4. Minimal boundary correction

A temporary correction made a trace that crossed expiry during the current event available to that event only. This repaired the reviewer failure without adding persistent state. Reviewer pass 1 then passed.

### 5. Second reviewer pass

A new holdout generation tested prior-event expiry, zero-reward boundary events, unlabeled outcomes, context revisitation, repeated-action refresh, delayed habit extinction, reward magnitude, interleaved opposite-valence outcomes, and negative boundary consequences. These probes passed.

### 6. Stored-state redundancy discovered

Second-order review found that stored `eligibility` was exactly derivable from `age`. It also found that the separate minimum-eligibility threshold could never activate before the age-10 lifetime bound. The four-field representation was rejected as unnecessarily large.

`eligibility` and the unreachable threshold were removed. The challenger became a three-field `context`, `action`, `age` representation.

### 7. Boundary special case removed

Further semantic review found that the temporary `_expired_this_tick` rescue gave eligibility records privileged timing semantics not shared by the runtime. Production behavior was revised again before final promotion.

The final temporal rule is coherent and general for this event-indexed record:

1. evidence that is live at event arrival may be read by that event;
2. existing evidence ages and expires after event processing;
3. a contextual action executed during the current event is then recorded at age zero.

There is no expired-record side channel in the final implementation. The runtime supports one `Event` per `step`; multi-event atomic transitions are therefore outside the current runtime contract.

### 8. Third simplification-specific holdout generation

After the generalized three-field production behavior was frozen, a third holdout set tested numerical age-derived weighting, before/at/after expiry behavior, refresh without duplication, opposite-valence specificity, ambiguity after refresh, semantically reordered contexts, and zero-reward boundary consumption. All seven passed.

### 9. First final subjective-access audit invalidated

The first final-validation harness included a flawed hidden-cause control. It placed an unlabeled outcome immediately after the action. That legitimately activated the pre-existing immediate habit pathway and produced a 0.35 update. This was a test-design error, not evidence of hidden simulator leakage.

The failed audit is preserved. The corrected audit inserted unrelated intervening activity before the unlabeled consequence, thereby removing the legitimate immediate-adjacency pathway. Under that corrected condition the organism learned nothing without subject-accessible outcome context, learned when exact subject-accessible context uniquely identified a live candidate, and abstained when two same-context actions remained plausible.

### 10. Capacity four rejected

The final-validation capacity tournament tested capacities 1, 2, 3, and 4. Capacity one failed already-earned `cross_context` and `multiple_candidates` behavior. Capacities two, three, and four preserved the current earned suite.

The production capacity was therefore reduced from four to two and the final closeout was rerun. The original reviewer assertion that required exactly four live records is preserved as historical evidence but is classified as an implementation-bound assertion overturned by the later capacity tournament. Its underlying semantic requirement, finite bounded retention with real eviction and no post-eviction hidden reconstruction, remains tested at capacity two.

## Final closeout results

No historical promoted regression, developer-suite failure, or causal-ablation failure remained in the final closeout.

- historical failures: none
- EXP-007 developer failures: none
- causal-ablation failures: none
- reviewer pass 1 raw failure after capacity reduction: `capacity_pressure_near_bound` only, an obsolete exact-capacity-four assertion
- reviewer pass 1 remaining semantic failures: none
- reviewer pass 2 failures: none
- reviewer pass 3 failures: none
- event-boundary audit: pass
- corrected subjective-access audit: pass
- selected capacity semantics: pass
- minimum tested capacity preserving earned behavior: 2

## Final cost audit

All numbers below are engineering measurements from one hosted CI environment, not hardware-independent constants.

| Measure | v8 champion | v9 challenger |
| --- | ---: | ---: |
| Counted mechanisms | 11 | 12 |
| Fresh serialized state | 334 B | 361 B |
| Representative state with no active trace | 451 B | 478 B |
| Mixed workload median, 15 samples | 13.5527 us/tick | 16.4786 us/tick |
| Mixed workload mean | 13.8388 us/tick | 16.8648 us/tick |
| Mixed workload population SD | 0.5552 us | 0.6722 us |
| Idle median | 12.7734 us/tick | 13.7592 us/tick |
| Context-event median | 13.1045 us | 15.4058 us |
| Outcome-event median | 15.4598 us | 13.6647 us |
| Initialization median | 1.0760 us | 1.2209 us |

The final two-record trace payload measured 79 bytes serialized in isolation, 77 bytes above an empty list, or approximately 38.5 bytes per representative record with the short test strings used in the audit. A runtime scenario at full two-record capacity measured 490 serialized bytes, although state size depends on what other mechanisms are populated and on string lengths.

The v9 mixed-workload overhead is measurable in this run, but individual hosted-CI timing measurements have varied enough across EXP-007 that the project does not claim a universal percentage slowdown. The persistent-state simplification is less ambiguous: the rejected four-field representation had measured 553 bytes in its comparable EXP-007 representative workload, while the final design stores no eligibility float and permits only two records.

## Promotion rationale

The delayed-credit artificiality failure is materially reduced, the improvement depends on the trace mechanism, positive and negative delayed consequences behave appropriately, unrelated intervening actions do not steal credit under tested conditions, subject-owned information boundaries are preserved, old evidence expires, the trace is explicitly bounded, three adversarial generations have been run, all previous promoted behavior remains intact, renderer invariance remains intact, and capacity/state were reduced after second-order critique rather than retained by default.

This is sufficient to promote `v9_context_eligibility_trace` as the next branch-local empirical champion.

## Next research phase

No new behavioral mechanism should be added yet. The next phase is **global structural ablation** of v9. It should test whether accumulated mechanisms remain independently necessary in the current organism and whether any pair can be consolidated into a genuinely smaller persistent substrate without losing earned behavior. Code abstraction without reduced persistent or conceptual machinery does not count as simplification.
