# Integrated PEMA Shared-Economy Experiment

This experiment is the first run in PR 14 where the four previously isolated causal links operate at the same time through one continuously replenished resource pool.

It remains a disposable research model. It is not a DUCK refactor and it is not the full PEMA production architecture.

## Research question

What happens when information asymmetry, local actor-generated demand, persistent reserve, utilization fatigue, and allocation-dependent information acquisition operate simultaneously and compete through one finite economy?

The target loop is:

`scarcity -> realized access -> local knowledge -> local demand -> allocation -> new local knowledge -> later demand`

Persistent concern reserve adds a second temporal path:

`unresolved history -> banked reserve -> later competitiveness -> recall`

## Runtime

The canonical run lasts 240 ticks with three resource units supplied per tick. Every granted operation costs one unit unless it is a concern banking operation.

The private actors are PERCEPTION, SOCIAL, MEMORY, ACTION, LANGUAGE, EXPLORATION, ROUTINE, CONCERN, and MAINTENANCE. Actors do not hold references to peers or the runtime. Inter-actor influence is represented by explicit `Effect` messages applied by the scheduler after the allocation phase.

PERCEPTION receives periodic social events from the environment. In differential access, private events are legally routable to SOCIAL and MEMORY, while public updates are legally routable to MEMORY, ACTION, and LANGUAGE. In global access, both event types can be routed to all four cognitive recipients. Legal routes still have to win resource allocation before the event is delivered, and undelivered events expire after a bounded TTL.

Every 40 ticks the world presents the same controlled social sequence: a private `avoid` preference, a later public `welcome` update, and then a decision about whether to surprise B. The action rule is unchanged from the earlier PR 14 experiments.

EXPLORATION and ROUTINE compete continuously. Their demand is:

`priority = baseline + evidence_weight * local_evidence - fatigue_weight * consecutive_wins`

When feedback is enabled, winning SAMPLE_CHANNEL produces one new locally relevant evidence item for that actor. That changes later demand.

CONCERN can spend ordinary quiet-time capacity on `BANK_RESERVE`. One unit of current capacity converts into 0.05 persistent reserve and 0.95 conversion loss. At later matching-context ticks, reserve increases the priority of `RECALL`. Winning recall consumes a bounded reserve stake and explicitly sends the recalled unresolved item to MEMORY.

MAINTENANCE is a constant-priority background competitor. It exists to prevent every quiet tick from trivially granting all optional operations.

## Conservation rule

The integrated economy checks:

`resource supplied = processing consumed + conversion loss + current reserve + consumed reserve + expired unused capacity`

The stress suite rejects any run whose conservation error exceeds floating-point tolerance.

## Canonical ablations

The same runtime is rerun under six configurations:

| Variant | Removed or changed mechanism |
|---|---|
| baseline | none |
| no_feedback | winning no longer reveals new channel evidence |
| no_reserve | CONCERN cannot bank persistent reserve |
| no_fatigue | consecutive wins do not increase future cost |
| global_access | broad routing replaces differential routing |
| no_epistemic_feedback_weight | local evidence no longer increases channel demand |

These are mechanism ablations, not new scenarios.

## Stress program

The standard stress suite sweeps capacities 2, 3, 4, and 5 across ten deterministic seeds for every canonical variant. It records resource conservation, resource-induced delivery failures, final epistemic divergence, concern recurrence, decision trajectory, exploration capture, and allocation concentration.

A second phase grid varies evidence feedback strength against fatigue strength at the canonical capacity. This is intended to reveal parameter regimes rather than report one tuned point.

## Run

From the repository root:

```bash
python -m cvc_research.experiments.information_asymmetry.integrated_main \
  --output research/experiments/pema-integrated-runtime/artifacts \
  --seeds 10

python -m unittest discover -s tests -p 'test_pema_integrated_runtime.py' -v
```

The runner writes a full canonical trace, canonical ablations, the multi-seed stress suite, and the feedback/fatigue phase grid.

## Falsification boundary

A positive result does not demonstrate personality, consciousness, selfhood, or human-like cognition. The actors still use transparent hand-specified local policies and a controlled world.

The experiment is successful only in the narrower sense if the integrated mechanisms preserve their causal effects under shared competition, produce reproducible interaction effects, survive ablation, and expose parameter regimes that are not reducible to random tie order.
