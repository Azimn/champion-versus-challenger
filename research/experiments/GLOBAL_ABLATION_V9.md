# Global Structural Ablation of v9

Status: PRE-REGISTERED before simplification challengers.

Frozen branch-local champion: `v9_context_eligibility_trace` on branch `champion-v9-context-eligibility-trace`, frozen branch commit `41c284d108d782f3fc09ed8751f785227cbfde19`. The production behavior promoted by EXP-007 was introduced at `8c1e692e2b115200e3d758e481eb12576aced907`.

This is not EXP-008 and does not introduce a new behavioral capability. The purpose is to determine whether the current organism contains persistent machinery that can now be removed, derived, or consolidated while preserving every earned behavior.

## Questions

1. Which currently counted mechanisms remain independently necessary in v9?
2. Which stored fields are deterministically derivable from other persistent state?
3. Did later evolution make earlier compatibility state redundant?
4. Can pairwise mechanisms share a smaller representation without merely hiding equivalent complexity behind an abstraction?
5. Does the current mechanism count overstate the number of independently persistent primitives?

## Current persistent-state inventory and hypotheses

### Base needs

`fatigue`, `affiliation`, and `competence` are three continuously drifting scalar pressures. They are counted separately in the base runtime. Their necessity must be re-tested in the current v9 organism rather than assumed from the original v0 design.

### Relationship history

`relationships[actor] -> signed value`. Created by support/hostility, slowly decays, read by social/avoid scoring, and required by the original history-divergence claim unless later state can reconstruct the behavior.

### Affect residue

`threat_residue -> scalar`. Created by hostility/shock, decays rapidly, read by avoid scoring. Candidate for removal only if another existing temporal state now reproduces recovery inertia without semantic leakage.

### Concern persistence

The base runtime still exposes `active_concern` and `concern_strength`, while EXP-004 also stores the authoritative bounded `concerns[concern] -> strength` ledger. In the current subclass, active concern and strength are synchronized from the ledger. Hypothesis GSA-H1: these two compatibility fields are redundant persistent state and the earlier base concern count may be double-counting the same mechanism.

### Habit learning

`habits[(context, action)] -> learned value`, plus base `last_action` and `last_context` for immediate outcome association. EXP-007 later added a recent context-action trace. Hypothesis GSA-H2: `last_action` and `last_context` may now be redundant because the newest trace record can support the already-earned immediate update pathway.

### Partner reliability

`partner_reliability[actor] -> signed value`. Created by observed reliability/unreliability, slowly decays, read by delegate/verify scoring. It is subject-owned social expectation state.

### Uncertainty policy

No persistent state. It changes scoring near zero reliability. It should be classified as policy rather than memory. Removal will still be re-tested because its earlier necessity was demonstrated only against the pre-v6 organism.

### Prospective commitments

`prospective_commitments[concern] -> cue`. Latent until an experienced context cue activates the commitment into the concern ledger. Candidate consolidation with concern state is plausible because both represent one commitment in different temporal modes, but unification must reduce state or conceptual machinery rather than merely replace two dictionaries with a more generic class.

### Subjective facts

`location_beliefs[entity] -> location`. Updated only by observation, not hidden world change, and read by search behavior. Candidate for a shared belief substrate with partner reliability, but only if that substrate reduces total machinery while preserving type-specific semantics and subjective-access boundaries.

### Delayed-credit trace

At most two `context/action/age` records. Age determines temporal weight. Created by contextual non-idle action, ages after each event, expires after age 10, and is read by experienced delayed outcomes. Candidate overlap with the base habit `last_action/last_context` pair is specifically tested in GSA-H2.

## First removal tournament

Freeze v9 and create diagnostic subclasses that remove or neutralize one existing mechanism at a time without adding substitute state. Run the same earned regression battery against each. Expected interpretation:

- A mechanism whose removal breaks its earned behavior remains necessary under current evidence.
- A mechanism whose removal preserves all earned behavior becomes a serious deletion candidate.
- A result is not sufficient if the ablation accidentally changes unrelated mechanisms or the test does not exercise the removed state.

The first tournament will include relationship history, affect residue, concern persistence, habit learning, partner reliability, uncertainty policy, prospective commitments, subjective facts, delayed-credit trace, and the three base needs.

## Pairwise simplification hypotheses

### GSA-H1: concern ledger can eliminate duplicated active-concern storage

Create a challenger in which `active_concern` and `concern_strength` are derived views of `concerns` and are not serialized as independent persistent state. The complete historical suite must pass. If it passes with lower state and one fewer legitimately counted persistence mechanism, prefer the smaller representation.

### GSA-H2: eligibility trace can replace habit last-action/context storage

Create a challenger in which `last_action` and `last_context` are not retained. Immediate habit learning must instead use the most recent live context-action trace. Delayed learning remains unchanged. The complete historical suite, immediate outcome controls, ambiguity behavior, and subjective-access boundaries must pass. If it passes with lower state and no added mechanism, prefer the smaller representation.

### Later pairwise candidates

Only after H1 and H2 are decided, examine prospective commitments with concerns, partner reliability with subjective facts, affect residue with generic temporal-record machinery, and habit value updating with delayed-credit updating. A shared class or container that leaves the same state and semantics intact does not count as simplification.

## Promotion rule for structural simplification

A simplification challenger may replace v9 only if it preserves all earned behavior and adversarial constraints, reduces persistent state and/or defensibly reduces independently counted machinery, does not add hidden simulator access, does not make the renderer causal, and does not merely relocate equivalent complexity.

Negative consolidation results are permanent evidence. No new behavioral feature may be introduced in this phase.
