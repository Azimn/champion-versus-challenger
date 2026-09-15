# Minimal Lifelike Run 001

Date: 2026-09-15

Branch: `minimal-lifelike-loop`

Pull request: #8

GitHub Actions run: `34990051759`

Preserved artifact: `minimal-lifelike-loop-results`, artifact ID `10404648308`

## Result

Final promoted champion: `v5_partner_model`

This result is limited to the current five targeted behavioral probes and their falsification probes. It does not establish that v5 is a complete human simulation or that these are the only mechanisms required for lifelikeness.

| Version | Behavioral probes passed | Counted mechanisms | Median microseconds/tick | Representative persistent state bytes | Lifelikeness/mechanism |
| --- | ---: | ---: | ---: | ---: | ---: |
| v0_reactive | 0/5 | 3 | 12.2282 | 81 | 0.0000 |
| v1_relationship | 1/5 | 4 | 13.3294 | 118 | 0.2500 |
| v2_affect | 2/5 | 5 | 13.9155 | 144 | 0.4000 |
| v3_concern | 3/5 | 6 | 14.2421 | 199 | 0.5000 |
| v4_habit | 4/5 | 7 | 14.9472 | 284 | 0.5714 |
| v5_partner_model | 5/5 | 8 | 15.8204 | 320 | 0.6250 |

The version-table timings above are from the final report pass. Per-cycle benchmark timings vary slightly because they are rerun independently on the shared CI host. Timing differences should therefore be treated as approximate engineering measurements rather than precise microbenchmarks.

## Cycle 1: history divergence

Champion `v0_reactive` produced `socialize:Alex` after both supportive and hostile histories.

Challenger `v1_relationship` produced `socialize:Alex` after the supportive history and `avoid:Alex` after the hostile history.

Reviewer attack: hostility from Alex did not leak to an unrelated Blake. The challenger chose `socialize:Blake`.

Decision: PROMOTE.

## Cycle 2: recovery inertia

Champion `v1_relationship` returned immediately to `idle` on every neutral tick after a non-social shock.

Challenger `v2_affect` produced five consecutive `avoid` decisions after the shock, then returned to `idle` as the residue decayed.

Reviewer attack: a longer neutral run confirmed that avoidance did not become permanent.

Decision: PROMOTE.

## Cycle 3: unfinished concern

Champion `v2_affect` followed the sequence `work`, `avoid`, `rest` after task assignment, interruption, and return to neutral conditions.

Challenger `v3_concern` followed `work`, `avoid`, `work`, showing return to the unfinished concern after interruption.

Reviewer attack: explicit task cancellation removed the concern and the agent chose `rest` rather than returning to work.

Decision: PROMOTE.

## Cycle 4: habit formation

Champion `v3_concern` chose the default `tea` when both `tea` and `walk` became available after repeated rewarded forced walks.

Challenger `v4_habit` chose `walk`, reflecting experience-shaped context-action preference.

Reviewer attack: the learned morning walk did not leak into the evening context. The challenger chose `tea` in the untrained evening context.

Decision: PROMOTE.

## Cycle 5: social prediction

Champion `v4_habit` chose `verify:Alex` after both reliable and unreliable observed histories because it had no model of Alex's behavioral tendency.

Challenger `v5_partner_model` chose `delegate:Alex` after repeated reliable observations and `verify:Alex` after repeated unreliable observations.

Reviewer attack: evidence about Alex did not leak to Blake, for whom the agent chose `verify:Blake`. Additional contradictory evidence about Alex reversed the earlier optimistic prediction and restored `verify:Alex`.

Decision: PROMOTE.

## Surface separation

Every version passed the surface-invariance test. Running the optional natural-language renderer did not change symbolic actions or persistent state. The expressive surface therefore remains observational rather than cognitive in this experiment.

## Interpretation

The important result is not that eight mechanisms are sufficient for a human-like character. The result is that five common artificiality failures were removed one at a time with small persistent mechanisms while preserving earlier gains and keeping runtime cost low.

The current architecture remains intentionally underpowered. It has no full episodic memory, no prospective deadlines, no multiple simultaneous concerns, no false-belief representation, no recursive Theory of Mind, no differentiated forgetting, no multi-step planning, and no natural-language cognition.

Those absences are now useful because they give the next artificiality attack clear targets. Future mechanisms should be added only after the current champion visibly fails a discriminating scenario and a donor mechanism earns its complexity against a cheaper alternative.
