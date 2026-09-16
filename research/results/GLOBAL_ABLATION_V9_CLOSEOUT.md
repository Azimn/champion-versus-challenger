# Global Structural Ablation v9 Closeout

## Decision

**PROMOTE `v9.1_compact` as the minimal structural descendant of `v9_context_eligibility_trace`.**

This is an architectural compaction result, not a new behavioral capability. The behavioral ancestor remains frozen independently at `8c1e692e2b115200e3d758e481eb12576aced907` on `champion-v9-context-eligibility-trace`.

The EXP-007 behavioral claim is unchanged: the organism can perform bounded, context-cued delayed consequence credit using subject-accessible evidence. This result does not establish general causal inference, hidden-cause attribution, arbitrary long-horizon reinforcement learning, ambiguous same-context attribution, planning, unbounded temporal credit, or general episodic memory.

## Completed evidence recovered without rerun

The unresolved pairwise and bounded-capacity questions were adjudicated from the already-completed global-ablation run rather than rerun.

- Workflow run: `35027204622`
- Artifact: `10419708926` (`global-ablation-v9-full-review`)
- Relevant files: `pairwise-consolidation.json`, `capacity-tournament.json`

### Concern / prospective consolidation

**Rejected as representationally invalid.**

The corrected one-value-per-name union preserved the ordinary earned suite but failed the stronger same-name modal holdout. The frozen architecture can simultaneously represent a concern named `report` as active now and also scheduled for later reactivation. One value under the key `report` cannot encode both states simultaneously. The original failed transition-ordering attempt is preserved separately: cue activation initially overwrote the latent value before deletion. Correcting that ordering did not solve the deeper representational collision.

Adding tags, nested records, compound keys, or parallel mode bookkeeping would restore the missing information and cease to be genuine compression. Active concerns and latent prospective commitments therefore remain separate semantic stores.

### Reliability / location belief consolidation

**Rejected as representationally invalid.**

The same entity can simultaneously have an independently revised reliability expectation and a location belief. The collision holdout assigns both to `Alex`. A one-value dictionary cannot preserve both. A typed common container would retain the same semantic information and update separation, so it would be implementation refactoring rather than cognitive simplification.

### Affect temporal abstraction

**Rejected as organism simplification.**

Threat residue is already one scalar. The tested generic temporal representation was larger and retained distinct affect semantics. A shared helper could be used in code, but replacing the scalar with a tagged temporal record would increase representation cost.

### Habit update helper

**Classified as source-code refactoring only.**

Immediate and delayed credit already update the same habit table. A shared helper would remove no persistent state and therefore does not reduce organism architecture.

## Capacity tournaments

The completed capacity tournament tested concern and prospective capacities 1, 2, and 3 across the earned suite, targeted store probes, and at-capacity operation.

**Concern capacity:** 2  
Capacity 1 fails already-earned multiple-concern behavior, including interruption and assignment-order cases. Capacities 2 and 3 are behaviorally indistinguishable under the meaningful current contract. Capacity 2 is therefore selected.

**Prospective capacity:** 2  
Capacity 1 fails the already-earned multiple-future-commitment behavior. Capacities 2 and 3 preserve the contract. Capacity 2 is therefore selected.

**Eligibility capacity:** 2  
This was already established in EXP-007. Capacity 1 loses earned cross-context/multiple-candidate behavior; capacity 2 preserves it.

Thus the compact organism uses a `2 / 2 / 2` bounded configuration for concerns, prospective commitments, and eligibility records.

## Accepted structural reductions

The compact descendant retains only reductions supported by direct evidence:

1. `active_concern` is no longer stored. It is deterministically derived from the concern ledger.
2. `concern_strength` is no longer stored. It is deterministically derived from the concern ledger.
3. `last_action` is removed.
4. `last_context` is removed.
5. Immediate contextual credit reuses the age-zero context-action eligibility trace instead of a duplicate last-action pair.
6. Immediate `context|idle` habits that cannot affect idle scoring are no longer created.
7. Concern capacity is reduced from 3 to 2.
8. Prospective capacity is reduced from 3 to 2.

Direct object inspection confirms that `active_concern`, `concern_strength`, `last_action`, and `last_context` are absent from stored object state. The first two survive only as derived diagnostic views.

## Mechanism reclassification

The mechanism count was recomputed from causal organization rather than inherited software structure.

The compact organism contains **11 independently defended persistent causal mechanisms**:

1. fatigue pressure
2. affiliation pressure
3. competence pressure
4. relationship history
5. affect residue
6. contextual habit learning
7. partner reliability expectation
8. bounded concern persistence
9. prospective cue binding
10. subjective location fact
11. bounded context-action eligibility trace

The uncertainty policy remains causally necessary for behavior near unknown reliability but adds no independent persistent state, so it is documented as a policy rather than counted as a persistent mechanism. Derived concern views, renderer behavior, debug traces, tick chronology, and class/version configuration are not counted as cognitive mechanisms.

## Removal and reverse-ablation results

Global removal re-litigation showed that relationship history, affect residue, concern persistence, habit learning, partner reliability, prospective commitments, subjective facts, delayed-credit traces, and competence pressure remain defended by earned behavior.

Fatigue and affiliation were initially under-covered by later promotion suites. Direct action-order-invariant tests demonstrated that fatigue independently drives rest and affiliation independently drives unscripted social approach, so both remain defended.

Reverse ablation of the compact form showed:

- concern capacity 1 breaks earned multiple-concern behavior;
- prospective capacity 1 breaks earned multiple-future behavior;
- removing age-zero trace information breaks immediate contextual credit;
- removing the concern ledger breaks concern and prospective-transition behavior;
- removing the trace breaks immediate and delayed contextual credit;
- restoring dead idle-habit storage adds persistent state without changing later choice.

These results identify the retained state as causal rather than historical baggage.

## Structural adversarial review

Novel post-compaction holdouts passed for:

- derived concern views through multiple transitions;
- immediate learning after delayed-credit activity;
- delayed learning after immediate habit learning;
- prospective activation while another concern is active;
- same-name active and latent concern coexistence;
- cancellation under mixed active/latent state;
- one entity simultaneously participating in relationship, reliability, and location-belief domains;
- eligibility capacity pressure followed by immediate learning;
- concern capacity pressure followed by prospective activation;
- semantically reordered behavior where ordering should not matter.

No accepted simplification required hidden simulator truth, renderer state, or environment metadata to replace removed organism state.

## Persistence closeout failure and correction

The first structural closeout correctly returned **REJECT**.

- Workflow run: `35028834468`
- Failure: serialization/reconstruction continuity

The organism selected the same actions before and after restore, and the displayed snapshots initially matched, but persistent state diverged after continuing. The cause was not cognitive behavior. `persistent_snapshot()` still reused the six-decimal diagnostic snapshot, while the uninterrupted object retained higher-precision floating-point state. After subsequent decay, the hidden numerical difference became visible.

This failure is preserved because it exposed an important distinction: a readable diagnostic snapshot is not necessarily a valid persistence format.

The correction introduced a canonical full-precision persistent payload and explicit reconstruction methods on `V91CompactCharacter`. Rounded `snapshot()` output remains diagnostic only. No behavioral policy or cognitive state variable was added.

The entire closeout was then restarted because serialization representation and state-size measurements had changed.

### Corrected closeout

- Workflow run: `35051162103`
- Artifact: `10428882688` (`v9-1-compact-closeout`)
- Decision: **PROMOTE**

All gates passed:

- explicit earned-behavior manifest
- structural adversarial review
- persistent-state inventory
- mechanism reclassification
- reverse ablations
- serialize/destroy/restore/continue continuity
- second-order structural review
- state reduction
- mechanism-count reduction

The reconstruction test serialized relationship state, affect, active concern ledger state, latent prospective commitment state, contextual habit state, partner reliability, subjective location belief, and live eligibility records. After reconstruction, six continuation events produced identical actions and exact persistent state at every step.

The debug trace is intentionally excluded from persistence. Frozen class/version policy configuration is restored by constructing the frozen class and is not mutable organism memory.

## Final state and cost audit

Measured in the same hosted CI run:

| Measure | Frozen v9 | v9.1 compact | Change |
| --- | ---: | ---: | ---: |
| Counted mechanisms | 12 | 11 | -1 |
| Fresh serialized state | 361 B | 269 B | -92 B (-25.48%) |
| Representative serialized state | 607 B | 577 B | -30 B (-4.94%) |
| Maximum bounded-store scenario | 649 B | 577 B | -72 B |
| Concern capacity | 3 | 2 | -1 |
| Prospective capacity | 3 | 2 | -1 |
| Eligibility capacity | 2 | 2 | unchanged |

The representative reduction is smaller than in the earlier rounded-snapshot measurement because the corrected compact persistence format now stores full-precision floats. That is the scientifically appropriate comparison for a genuinely reconstructible individual.

Timing samples overlap and vary across hosted runs. In the final run, compact idle timing was effectively similar while mixed/event-heavy medians were somewhat higher. No stable speed improvement or regression is claimed. The supported result is persistent-state and explanatory compression.

## Strict persistent-state inventory

Persistent organism state:

- `fatigue`: scalar
- `affiliation`: scalar
- `competence`: scalar
- `relationships`: actor → signed relationship value
- `threat_residue`: scalar
- `habits`: `(context, action)` → learned value
- `partner_reliability`: actor → reliability expectation
- `concerns`: bounded to 2 concern-strength pairs
- `prospective_commitments`: bounded to 2 concern-cue pairs
- `location_beliefs`: entity → last directly perceived location
- `eligibility_records`: bounded to 2 `(context, action, age)` records

Derived diagnostic values:

- `active_concern`
- `concern_strength`

Runtime/test infrastructure excluded from cognitive mechanism count:

- `tick`
- debug `trace`
- class/version configuration
- renderer state
- environment state

The current runtime still leaves relationship, habit, reliability, and subjective-fact dictionaries unbounded by cardinality. This closeout does not claim those stores are globally minimal; it establishes only that the tested reductions are currently defensible.

## Second-order structural conclusion

The compaction removed real persistent organism state rather than renaming it. No generic container was accepted merely because it reduced class count. Semantic stores that need independent coexistence remain independent. Derived values reconstruct only information already present in the authoritative concern ledger. No removed information moved into the renderer or privileged world state.

The strongest negative result of this phase is also important: several superficially attractive unifications are not valid compression because independent modal or semantic states must coexist.

## Final structural result

`v9.1_compact` preserves the earned behavioral contract of behavioral v9 while using fewer persistent causal mechanisms and less persistent state. It is therefore promoted as the minimal structural descendant of v9.

Frozen behavioral v9 remains preserved independently. `v9.1_compact` should be the baseline for subsequent failure-driven evolution once a clean frozen-ref verification passes.
