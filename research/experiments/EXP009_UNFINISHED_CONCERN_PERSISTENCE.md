# EXP-009 Preregistration: Unfinished Concern Persistence

## Status

**PREREGISTERED BEFORE CHALLENGER IMPLEMENTATION**

Preregistration branch: `exp009-unfinished-concern-persistence`

Frozen champion under test:

- version: `v9.1_compact`
- branch: `champion-v9-1-compact`
- commit: `2856ec6a32be0347a9243f6eff6faa404a9a0e6c`
- counted persistent causal mechanisms: 11

EXP-008 is closed as **REJECTED** and contributes no champion behavior.

## Reproduced failure

An explicitly assigned unfinished concern disappears solely because unrelated time passes.

Frozen reproduction:

1. `task_assign(concern="finish_portfolio", intensity=1.0)` creates concern strength `0.75`.
2. No completion, cancellation, impossibility, contradicting event, or relevant action occurs.
3. Every tick multiplies concern strength by `0.97`.
4. The concern is deleted once strength falls below `0.08`.
5. It disappears after exactly 74 unrelated events.

The disappearance time is mathematically predicted by the current rule and reproduced across multiple kinds of unrelated experienced events.

Intensity sweep:

- intensity 0.25: observed/predicted disappearance 28 events
- intensity 0.50: 51
- intensity 0.75: 65
- intensity 1.00: 74

Neutral, unrelated social, unrelated location-observation, and unrelated reliability-observation histories all erase the concern at the same offset.

## Why this is an artificiality failure

The current representation conflates at least two distinct behavioral questions:

1. How strongly is this unfinished matter currently activated or prioritized?
2. Does this unfinished matter still exist as an unresolved concern?

A continuing individual may stop actively thinking about an obligation without the obligation thereby becoming completed, cancelled, impossible, or forgotten at a deterministic threshold after 74 unrelated experiences.

This experiment treats that mismatch as a behavioral property. It does not assume a philosophical theory of intention.

## Causal localization already established

The authoritative concern ledger already stores concern identity as the dictionary key and current strength as the value.

Existing resolution/removal paths already exist:

- `task_cancel` explicitly removes the concern;
- sufficiently successful `work` reduces and eventually removes the active concern;
- bounded capacity can evict lower-ranked concerns when stronger concerns arrive.

A diagnostic ablation that prevents ordinary decay from deleting concern identity keeps the concern alive without adding persistent fields. A diagnostic low-activation floor also prevents silent loss while preserving existing `task_cancel` and work-mediated removal.

These diagnostics are not challengers and are not promotion evidence. They establish only that the selected failure can be causally localized to the current interaction between activation decay and concern existence.

## Internal archaeology conclusion

See `research/donors/EXP009_UNFINISHED_CONCERN_DONORS.md`.

Relevant internal principles:

- DUCK v0.10 separates motive identity/status/persistence from changing activation-like quantities and does not retire active motives merely because strength is low.
- `persona_engine_PYTHONX` allows intention priority to change while intention retention is controlled separately by explicit expiry.
- TinyPersonaEngine stores goals independently from transient action-pressure utility.

No donor implementation will be copied. The inspected internal roots did not establish source reuse licenses at the inspected refs.

## Narrow external prior art conclusion

Cohen and Levesque's commitment account and Rao and Georgeff's BDI commitment semantics distinguish maintaining an intention from the termination condition under which it is dropped. Rao and Georgeff's abstract interpreter removes successful/satisfied and impossible/unrealizable attitudes rather than using momentary activation alone as a generic termination criterion.

EXP-009 does not adopt BDI, PRS, AgentSpeak, modal logic, plans, intention stacks, or a belief/desire/intention architecture. The donor concept is only:

> **Termination of an unfinished intention should be controlled by semantically relevant termination evidence, not inferred automatically from low current activation.**

## Minimal causal hypothesis

Frozen `v9.1_compact` already contains enough persistent information to prevent the selected failure.

The hypothesis is:

> **Ordinary activation decay may reduce the priority/strength of an explicitly unfinished concern, but low activation alone should not delete its identity. Existing explicit resolution signals and existing bounded-capacity competition should remain sufficient to remove it.**

This is an existing-mechanism interaction hypothesis.

It does **not** preregister a new persistent mechanism.

## Expected implementation class

The first challenger must attempt to use only existing concern state and existing resolution/capacity rules.

Allowed first-pass changes include a minimal rewrite of concern decay/removal policy, such as preserving a bounded low activation for unresolved concerns or otherwise preventing decay alone from being a deletion condition.

The first challenger must not add:

- a concern-status field;
- a separate persistence scalar;
- timestamps or age fields;
- completion flags;
- a new memory tier;
- a planner;
- intention stacks;
- BDI machinery;
- a dormant-concern store;
- an archival queue;
- a third concern slot;
- a new counted persistent mechanism.

If such information becomes necessary, the zero-new-state hypothesis must first be falsified and the new requirement preregistered separately before implementation.

## Predicted primary behavioral difference

Under identical assignment and unrelated-history sequences:

### Frozen champion

`finish_portfolio` disappears after 74 unrelated events.

### Challenger

`finish_portfolio` remains represented as unresolved after the same history, although its current activation may weaken substantially.

The challenger must not preserve full initial activation indefinitely merely to pass the test.

## Predicted existing-resolution behavior

The challenger should preserve existing semantics that provide actual termination evidence:

- explicit `task_cancel(concern=X)` removes X;
- sufficient work on the active concern can remove X;
- bounded concern competition remains active;
- no capacity increase is permitted.

A concern is not required to survive capacity eviction. EXP-009 targets spontaneous decay-to-nonexistence, not loss under an explicitly bounded store.

## Expected non-effects

EXP-009 is not expected to solve:

- third prospective commitment eviction;
- suppressed concern return after capacity eviction;
- non-decaying habits;
- ancient prospective commitments;
- deterministic autonomous rhythm;
- general forgetting;
- general planning;
- prospective deadlines;
- multi-step task representation;
- concern impossibility reasoning;
- human-like spontaneous recall.

These must remain separate failure-queue items unless the experiment changes them incidentally, in which case that effect must be reported rather than silently claimed.

## Development tests

The initial development battery must include at minimum:

1. **Frozen reproduction**
   - confirm the exact champion still loses the assigned concern under ordinary unrelated drift.

2. **Long unrelated retention**
   - assign one concern and run at least 120 unrelated events;
   - extend at least one probe to 1000 unrelated events;
   - concern identity should remain without full-strength preservation.

3. **Activation weakening**
   - verify current strength decreases from its initial value rather than staying artificially frozen.

4. **Explicit cancellation**
   - cancel the weakened concern and confirm immediate removal.

5. **Work-mediated resolution**
   - after prolonged weakening, perform relevant work and confirm the existing resolution path can still remove the concern.

6. **Reassignment/reactivation**
   - reassign an already weak unresolved concern and verify existing assignment semantics can increase its activation without duplicating identity.

7. **Multiple concerns within capacity**
   - two unresolved concerns may coexist and weaken without spontaneous threshold deletion.

8. **Capacity pressure**
   - add a stronger third concern under the frozen capacity of two;
   - verify bounded eviction remains active rather than creating hidden unlimited persistence.

9. **Unrelated event invariance**
   - neutral, social, epistemic, and partner-observation events should not implicitly terminate an unrelated concern.

10. **Action-selection effect**
    - a very weak unresolved concern must not dominate behavior merely because its identity persists.

11. **Renderer invariance**
    - optional surface rendering must not change concern state or actions.

12. **Serialization continuity**
    - serialize/destroy/restore both a strongly active and a weak-but-unresolved concern and continue interaction exactly.

13. **Historical earned contract**
    - replay EXP-002 through EXP-007 and v9.1 structural closeout.

14. **Failure-queue scope controls**
    - rerun minimal probes for the other five remaining queue failures and report whether they remain unchanged, weaken, or change form.

## Reserved reviewer space

Post-implementation reviewer probes must be created only after production behavior freezes.

Reviewer generation should attack at least:

- extremely weak initial assignments;
- 10,000 unrelated ticks if computationally cheap;
- repeated weakening then reassignment;
- cancel after long dormancy;
- work after long dormancy;
- competing weak concerns;
- capacity eviction order;
- reintroduction after eviction;
- concern-name edge cases and serialization;
- whether low persistent concerns create unwanted chronic work bias;
- whether concern identity becomes immortal when it should resolve;
- whether unrelated reward/outcome events accidentally alter concern lifecycle;
- whether prospective-cue activation creates a concern that now persists pathologically;
- reconstruction at or near the minimum activation representation.

Reviewer tests must not be rewritten after seeing failures. Invalid reviewer assumptions must be preserved and classified explicitly.

## Causal ablation

At minimum compare:

1. frozen `v9.1_compact`;
2. the zero-new-state challenger;
3. a diagnostic variant that restores the original decay-threshold deletion while leaving every other challenger behavior intact.

The selected failure should return only when decay is again allowed to terminate an unresolved concern.

Additional diagnostic comparisons may separate:

- no activation decay at all;
- activation decay with bounded unresolved retention.

The purpose is to show that preserving concern identity does not require freezing activation strength.

## State and runtime cost measures

Measure:

- mechanism count;
- fresh diagnostic-state bytes;
- canonical persistence bytes;
- representative-state bytes;
- maximum bounded concern-store bytes;
- bytes for a weak unresolved concern versus an active concern;
- median tick cost under no concerns, one concern, and two concerns;
- assignment, cancellation, work-resolution, and ordinary drift cost;
- serialize/restore cost.

A zero-new-field policy can still have runtime or long-lived-state occupancy cost. Do not call the challenger zero-cost solely because mechanism count remains 11.

## Promotion criteria

PROMOTE only if all of the following hold:

- the frozen failure is materially corrected;
- concern identity survives long unrelated histories without full activation being frozen;
- explicit cancellation still removes concerns;
- existing work-mediated resolution still removes concerns;
- bounded capacity remains two;
- capacity competition still works;
- no new persistent field category appears;
- counted mechanism count remains 11 unless a later preregistered falsification phase explicitly changes the hypothesis;
- no historical earned behavior regresses;
- renderer invariance passes;
- serialization fidelity passes;
- at least one post-freeze reviewer generation passes or any failures are preserved and legitimately resolved;
- causal ablation shows ordinary decay-as-termination is responsible for the frozen failure;
- second-order review finds that the challenger has not merely created immortal zombie concerns or hidden persistence state;
- state/runtime cost is documented.

## Rejection criteria

REJECT the zero-new-state hypothesis if any of the following is required to obtain coherent behavior:

- a new persistent status/phase field;
- a persistence or confidence scalar distinct from current concern strength;
- an age/timestamp field;
- a second dormant/archive store;
- capacity expansion;
- hidden simulator information;
- permanent full-strength preservation;
- special-case concern names or test-specific logic;
- regression of explicit cancellation or action-mediated resolution;
- unacceptable chronic action bias from weak unresolved concerns;
- failure of serialization continuity;
- inability to distinguish unresolved low activation from genuinely resolved concern using existing signals.

A rejection is informative: it would show that the current concern scalar cannot safely carry both activation and lifecycle semantics even after the deletion rule is corrected.

## Claim boundaries

If successful, EXP-009 may support only a narrow claim similar to:

> **An explicitly unfinished concern can retain identity while its current activation weakens, using existing resolution and bounded-capacity signals rather than treating low activation itself as completion.**

EXP-009 must not claim:

- general intention theory;
- general BDI behavior;
- human-like goal persistence;
- general memory/forgetting;
- prospective planning;
- impossibility reasoning;
- multi-step task planning;
- consciousness or sentience.

## Recursive review questions

After every apparent correction ask:

- Did concern existence move into hidden state or an implicit key?
- Did activation silently become a lifecycle flag?
- Did lifecycle semantics silently become activation?
- Can explicit cancellation still remove a weak concern?
- Can relevant work still resolve it?
- Can capacity still evict it?
- Does a weak unresolved concern exert an unjustifiably large action pressure?
- Can it become a zombie that survives forever despite evidence of resolution?
- Is any new information being inferred from mere passage of time?
- Do semantically equivalent histories produce equivalent concern state?
- Does serialization preserve low activation exactly?
- Could the same behavioral gain use even less information?
- Is the difference longitudinally visible to an observer?

If these questions expose a substantive defect, return to investigation before promotion.

## Implementation prohibition until this preregistration commit

No EXP-009 challenger production code may be written before this preregistration is committed.
