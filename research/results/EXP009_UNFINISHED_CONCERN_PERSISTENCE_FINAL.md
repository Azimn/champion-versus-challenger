# EXP-009 Final Result: Unresolved Concern Existence Versus Activation

## Decision

**PROMOTE** branch-local successor `v9.2_unresolved_concern_persistence`.

Frozen behavioral ancestor: `v9.1_compact`, commit `2856ec6a32be0347a9243f6eff6faa404a9a0e6c`.

Evaluated EXP-009 production implementation: `src/lifelike_min/exp009_challenger.py` as frozen at commit `b5cc3e109ab2fa4de0421dc113009d1ee7fb050d`.

Corrected strict closeout run: `35138150402`.

Corrected strict closeout artifact: `10464196939`.

The production file was not modified after its initial implementation. Later commits contain only evaluation, reviewer, adjudication, closeout, workflow, and research records.

## Reproduced failure

Frozen v9.1 represented an unfinished concern in a bounded concern ledger but coupled ordinary activation decay to deletion:

`strength *= 0.97`

then delete membership when strength `< 0.08`.

Therefore an explicitly unfinished matter disappeared solely because unrelated events passed, without completion, cancellation, impossibility, contradiction, or capacity pressure.

The frozen baseline reproduced the preserved disappearance points exactly:

| task-assignment intensity | initial ledger strength | unrelated events until deletion |
| ---: | ---: | ---: |
| 0.25 | 0.1875 | 28 |
| 0.50 | 0.375 | 51 |
| 0.75 | 0.5625 | 65 |
| 1.00 | 0.75 | 74 |

Neutral, social, location-observation, and partner-reliability events all produced the same 74-event disappearance for the intensity-1.0 case.

## Semantic distinction tested

EXP-009 tested whether the existing concern representation could carry two meanings without additional persistent information:

- ledger key/membership: the named concern remains unresolved;
- existing scalar value: current activation, salience, or behavioral pressure.

Ordinary time may reduce activation. Ordinary time alone is not evidence of completion or cancellation.

The experiment did not add a persistence flag, status, timestamp, dormant store, completion marker, extra slot, planner, intention stack, or BDI machinery.

## Production change

The challenger retains exactly the existing bounded concern dictionary and scalar. It changes only ordinary concern drift:

- activation still multiplies by `0.97` each drift;
- drift alone no longer deletes the dictionary entry when activation becomes small;
- explicit `task_cancel` remains a termination path;
- existing work-mediated resolution remains a termination path;
- existing capacity-two eviction remains a loss path.

Repeated floating-point decay may approach or reach zero. Zero activation is allowed to coexist with ledger membership; existing reassignment can raise activation again.

## Development evidence

The first development run, `35136991980`, failed because the development helper assumed a newly assigned weaker third concern would survive capacity enforcement and immediately indexed it. Capacity two correctly evicted that concern, producing a `KeyError`. This was preserved as a development-harness implementation defect in `research/reviews/EXP009_DEVELOPMENT_FAILURE_1.md`. Production was not changed.

The corrected harness then passed on Python 3.11 and 3.12 in run `35137210760`, while CI verified the production file remained identical to `b5cc3e109ab2fa4de0421dc113009d1ee7fb050d`.

Matched evidence included:

- frozen v9.1 lost each tested concern after ordinary unrelated time;
- EXP-009 retained the same unresolved identity after 200 events for assignment intensities 0.25, 0.50, 0.75, and 1.00;
- activation continued to decay;
- after 500 unrelated events, an intensity-1 concern remained with activation approximately `1.8235950157343605e-07`;
- after 1,000 unrelated events and multiple serialize/restore cycles it remained with activation approximately `4.4339983752149414e-14`;
- reassignment used the existing rule to raise a dormant concern back to normal activation without duplicating it;
- a strong threat or stronger current concern still defeated a very weak dormant concern in action selection;
- explicit cancellation still removed the concern;
- work still resolved it;
- a stronger third concern could still evict a dormant concern under capacity two;
- a newly arriving weaker third concern was itself evicted;
- active concerns and latent prospective commitments remained separate;
- unrelated affect, relationship, reliability, factual, habit, eligibility, and need state remained isolated;
- mechanism count and persistent schema remained unchanged.

The unchanged `suppressed_concern_never_returns` reproduction still failed. Once capacity eviction removes a concern, EXP-009 has no hidden archive from which it can return.

## Causal ablation

Three matched variants establish separable contributions:

1. frozen v9.1: activation decays and threshold deletion occurs;
2. EXP-009: activation decays but ledger membership survives unrelated time;
3. threshold-restoration ablation: restoring only the old `< 0.08` deletion condition restores the original evaporation failure;
4. no-decay diagnostic: membership persists and activation remains at its original value.

After 120 unrelated events, representative states were:

- frozen v9.1: concern absent;
- EXP-009: concern present at approximately `0.019394088601361163`;
- threshold-restoration ablation: concern absent;
- no-decay diagnostic: concern present at `0.75`.

This supports the narrow causal distinction that unresolved membership and momentary activation can make separable behavioral contributions using the existing representation.

## Reviewer generation 1

Raw run: `35137413998`.

Raw artifact: `10463856104`.

Raw result: **14/15**.

The sole failure was `reassignment_after_dormancy`, which asserted binary floating-point output exactly equaled decimal `0.45`. Observed activation was `0.44999999999999996`; the concern reactivated correctly and remained a single ledger entry. The raw failure was classified as a numerical artifact / invalid exact-float reviewer assumption and preserved in `research/reviews/EXP009_REVIEW1_FAILURE.md`.

A separate adjudication replayed the untouched reviewer, required that this was the only raw failure, and verified the intended numerical relation with explicit floating-point tolerance. Production and the original reviewer were both frozen. The adjudication passed in run `35137685770`.

All other reviewer-1 attacks passed, including 10,000-event dormancy, extremely weak activation, long-dormancy cancellation and work resolution, exact reconstruction, prospective interaction, two weak concerns, stronger-third capacity competition, competing behavioral needs, unrelated outcomes, explicit zero activation, eviction/reintroduction, non-resurrection after resolution, and reordered unrelated histories.

## Reviewer generation 2

Independent reviewer generation 2 was created only after reviewer-1 adjudication and without production changes.

Run: `35137803066`.

Artifact: `10463767721`.

Result: **12/12 passed**.

It covered reordered equivalent histories, cancellation timing, cancel/reassign/cancel semantics, work resolution with another dormant concern present, same-name active and latent prospective state, zero-activation capacity competition, social motivation versus dormant concern pressure, coexistence with delayed credit, reconstruction followed by multiple resolution routes, non-resurrection after eviction, equivalent terminal absence through different resolution routes, and event-count versus event-meaning decay.

## First closeout rejection and correction

The first strict closeout run `35137960593`, artifact `10463248914`, emitted **REJECT** because one closeout assertion required the dormant concern to remain present after a continuation sequence.

That continuation itself allowed autonomous `work`. Both uninterrupted and reconstructed agents selected the same actions, maintained exactly equal persistent states, and legitimately resolved the weak concern through the already-earned work-resolution path. The invalid closeout assertion therefore treated successful legitimate termination as failed persistence.

This was preserved in `research/reviews/EXP009_CLOSEOUT_FAILURE_1.md`. Production and both reviewer generations were not changed.

The corrected reconstruction gate requires the unresolved concern to exist immediately after restoration and then requires exact causal equivalence through continuation, while allowing later legitimate resolution. In the corrected closeout the restored concern was present at approximately `1.664345933795326e-07`; all subsequent actions and persistent states matched exactly; both copies eventually selected `work` and removed the concern identically.

## Complete historical regression

The corrected strict closeout passed the complete earned contract:

- EXP-002 through EXP-006 promoted behavior;
- EXP-003 uncertainty reversal, near-neutral behavior, and person specificity;
- EXP-004 multiple concerns, cancellation, duplication, boundedness, and interruption;
- EXP-005 prospective cancellation, wrong cues, multiple commitments, one-shot activation, and boundedness;
- EXP-006 subjective observation, revision, hidden-world non-interference, entity specificity, and perception order;
- EXP-007 delayed positive/negative credit, context isolation, ambiguity abstention, expiration, ordering invariance, and all three adversarial reviewer generations except the already-adjudicated obsolete four-record implementation assertion;
- direct fatigue, affiliation, and competence behavior;
- renderer invariance;
- subjective-access boundary;
- canonical full-precision serialize/destroy/restore continuation;
- capacity bounds and v9.1 structural invariants.

The full repository test suite also passed in the final closeout workflow.

## Cost and representation audit

EXP-009 adds **zero new persistent fields** and **zero counted mechanisms**.

Fresh and standard bounded-state measurements remain unchanged:

| measure | v9.1 | EXP-009 |
| --- | ---: | ---: |
| counted mechanisms | 11 | 11 |
| fresh diagnostic bytes | 269 | 269 |
| fresh canonical bytes | 245 | 245 |
| representative diagnostic bytes | 577 | 577 |
| representative canonical bytes | 533 | 533 |
| maximum tested bounded diagnostic bytes | 577 | 577 |
| maximum tested bounded canonical bytes | 533 | 533 |

Lifetime occupancy is not zero-cost. After 1,000 unrelated events in the matched one-concern fixture:

- v9.1 has deleted the concern and serializes to 245 canonical / 269 diagnostic bytes;
- EXP-009 retains activation `4.4339983752149414e-14` and serializes to 279 canonical / 304 diagnostic bytes.

That is +34 canonical bytes and +35 diagnostic bytes in this fixture. It is retained information occupying the existing bounded schema, not a new field category.

Final hosted-CI engineering estimates from run `35138150402` were:

| operation | v9.1 median us | EXP-009 median us |
| --- | ---: | ---: |
| idle, no concern | 11.0492 | 11.2533 |
| idle, one concern | 11.2137 | 13.6052 |
| idle, two concerns | 11.2840 | 14.2349 |
| assignment | 13.721 | 13.641 |
| cancellation | 11.458 | 11.317 |
| work resolution after long dormancy fixture | 11.357 | 13.230 |
| serialize long-dormancy fixture | 14.132 | 16.355 |
| restore long-dormancy fixture | 11.557 | 13.520 |

These are hosted-CI microbenchmarks and are treated as engineering estimates, not precision speed claims. The persistent concern requires ongoing decay and serialization work that frozen v9.1 eventually avoids by deleting it.

## Second-order methodological result

The evidence supports the semantic distinction only within the current concern mechanism.

Ledger membership is defensible as unresolved identity because that ledger was experimentally earned to represent simultaneous unfinished concerns, and existing cancellation, work-mediated resolution, reassignment, and capacity competition already operate on that identity. The scalar remains a coherent activation value because it still decays and still influences the derived active concern and action scoring.

EXP-009 does shift the remaining forgetting problem. A dormant concern can occupy one of the two slots indefinitely in the absence of resolution or stronger competition. Capacity eviction is therefore now the principal concern-loss mechanism. That is bounded and explicit, but it is not claimed to be human-like forgetting.

The existing `suppressed_concern_never_returns` failure remains unchanged. Therefore EXP-009 did **not** produce the hoped-for second improvement from the same principle. It establishes a narrower primitive: suppression by low activation is distinct from deletion, but capacity eviction is still deletion.

The existence-versus-current-expression distinction may recur elsewhere, including prospective commitments, habits, and relationships. EXP-009 provides no evidence for changing those systems and makes no such refactor.

## BEHAVIOR DEMONSTRATED

An explicitly unfinished concern can remain in the organism's existing bounded persistent concern state through long unrelated histories while its existing activation scalar decays to extremely small values. It can later be reactivated by ordinary reassignment, cancelled explicitly, resolved by existing work behavior, or evicted under the existing capacity-two policy.

## CAUSAL SEMANTIC DISTINCTION SUPPORTED

Restoring only decay-threshold deletion restores the original evaporation failure. Removing activation decay separately freezes activation without changing membership. Unresolved membership and momentary activation therefore have separable behavioral effects without adding persistent state.

## CLAIMS NOT ESTABLISHED

EXP-009 does not establish general intention theory, human-like motivation, planning, general goal persistence, general forgetting, BDI semantics, long-term memory, or recovery of concerns after capacity eviction.

## Promotion claim

The supported claim is:

> An unresolved concern can remain part of the organism's persistent state while its momentary activation decays, and explicit resolution, cancellation, or bounded replacement rather than low activation alone determines disappearance.
