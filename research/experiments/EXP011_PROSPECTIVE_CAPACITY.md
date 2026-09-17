# EXP-011: prospective commitment capacity

## Status
**PREREGISTERED. No EXP-011 challenger implementation exists at this commit.**

MBASE-001 is closed before this experiment. Frozen champion remains `v9.3_concern_capacity_three`, commit `a10bc27579bf5bd0ff1a90d6ad6e3f337d8ed7bc`, 11 counted persistent causal mechanisms.

## Selected reproduced failure
`third_commitment_is_forgotten`: prospective capacity 2 silently discards the oldest of three distinct future commitments. Its later experienced cue produces no concern activation.

Foundation run `35267809371` reproduced the failure and established that after eviction, a matched history in which the first commitment existed and a matched history in which it never existed have identical complete canonical subject-owned persistent state. Recovery is therefore impossible without retained information or external/privileged history.

## Information lower bound
Meaningful event-based recovery requires the existing prospective pair: commitment/concern identity plus its cue association. Identity alone cannot determine which cue should reactivate it; cue alone cannot determine which commitment to activate. No other earned mechanism legitimately stores the evicted pair.

## Selected minimum hypothesis
Increase only the existing prospective store capacity from 2 to 3. Do not add fields, status, queue type, dormant tier, rehearsal process, priority scalar, timestamp, planner, or mechanism. Existing OrderedDict binding semantics, cue activation, cancellation, concern interaction, renderer, and serialization remain unchanged.

This is explicitly a representational-capacity experiment inside the already-earned prospective-commitment mechanism.

## Alternatives rejected before implementation
- Capacity-two replacement-policy changes cannot simultaneously preserve three independent valid identity/cue pairs.
- A separate overflow record retains the same information as a third ordinary record while adding a new storage/return semantic path.
- Concern-ledger reuse violates the empirically earned active-versus-latent distinction and previously rejected union.
- Eligibility, habits, facts, relationships, reliability, affect, and needs have incompatible earned semantics.

## Development tests
1. Frozen v9.3 exact reproduction: first/second/third leaves second+third; cue_first fails.
2. Capacity-three challenger retains all three distinct prospective pairs.
3. Before any cue, all three remain behaviorally latent and do not create active concerns.
4. Each cue activates only its own commitment into the ordinary concern ledger and removes that prospective binding.
5. Cue order permutations produce corresponding activation without insertion-order forgetting.
6. Cancellation of one latent commitment removes only that binding.
7. Same-name prospective reassignment retains existing replacement semantics without duplication.
8. Same-name active concern plus latent prospective commitment preserves the historically earned separation.
9. Prospective activation into a full capacity-three concern ledger obeys ordinary concern competition; prospective capacity is not a hidden active-concern slot.
10. Serialize/destroy/restore with three latent commitments is exact; post-restore cues behave identically.
11. Long unrelated histories preserve the current prospective semantics. EXP-011 does not attempt to solve `ancient_commitment_reactivates_unchanged`; report it unchanged or changed incidentally.
12. Four and five simultaneous commitments remain bounded and expose the new loss frontier rather than unbounded memory.
13. Complete EXP-002 through EXP-010 earned regression contract remains green.
14. Renderer and subjective-access invariants remain green.

## Capacity tournament
Evaluate prospective capacities 2, 3, and 4 under the target three-commitment history and additional bounded-overflow histories. Capacity 2 is predicted to fail the target. Capacity 3 is predicted to be the smallest target-successful value. Capacity 4 must not be retained merely because inexpensive; any additional behavior is reported but not part of the target claim.

## Causal ablation
From the challenger, restore only prospective capacity 2 while leaving all other challenger behavior unchanged. The target failure must return. No test-harness history may recover an evicted commitment.

## Cost audit
Report separately: mechanism count; persistent fields; fresh canonical/diagnostic state; two-record, three-record, and maximum tested prospective-store state; marginal canonical bytes for the third pair under normalized identifiers; serialization/reconstruction time; commitment insertion; cue activation. Zero new mechanism does not mean zero occupancy cost.

## Reserved post-freeze reviewer attacks
Generate only after production freeze. Include: 10/100/1000 unrelated events; cue order permutations; cancellation before/after other cues; repeated same-name commitment; same cue for different commitments; three commitments plus full concern pressure; four/five commitment overflow; reconstruction at full prospective capacity; repeated fill/activate/refill cycles; Unicode/delimiter-heavy names and cues; hidden-world events; action-order changes; and attempts to make prospective bindings behaviorally active before their cue.

## Promotion criteria
Promote only if capacity three preserves all three target identity/cue pairs; latent commitments remain non-dominant before cue; correct cue-specific activation occurs; cancellation/completion interactions remain coherent; storage remains bounded; serialization and subjective access pass; capacity-two ablation restores failure; historical earned behavior remains intact; adversarial reviewers survive; and no new persistent mechanism or semantic storage tier was introduced.

## Rejection criteria
Reject if capacity three does not solve the target; if it changes latent commitments into active pressure; if a new field/status/queue semantics is required; if bounded overflow becomes unprincipled relative to the narrow claim; if reconstruction fails; or if historical behavior regresses.

## Expected non-effects
Do not expect EXP-011 to solve rewarded-routine non-weakening, ancient-commitment aging, deterministic rhythm, general forgetting, planning, rehearsal, intention prioritization, or arbitrary numbers of simultaneous future commitments.

## Narrow possible claim
If promoted: within the existing prospective-commitment mechanism, three simultaneous event-based identity/cue bindings require enough bounded representation to preserve all three; increasing capacity from two to three can restore later cue-triggered eligibility without adding a new causal mechanism.

Do not claim human prospective-memory capacity, general intention theory, BDI, planning, or universal three-slot necessity.
