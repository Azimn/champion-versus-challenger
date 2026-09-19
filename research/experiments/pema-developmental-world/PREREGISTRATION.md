# PEMA Developmental World Experiment: Preregistration

Status: FROZEN BEFORE IMPLEMENTATION OR PHENOTYPE EXECUTION

Parent evidence: `experiment/persistent-information-asymmetry` at `f3d47e2bd7adf68e974cf59d5453dddae87da20a`.

## Question

Does replacing the 240-tick repeated hand-authored schedule with a deterministic small generative world, while preserving the integrated PEMA resource economy, produce history-dependent behavioral tendencies that persist into common held-out probe windows?

This experiment tests developmental persistence in the existing toy system. It does not test or claim personality, selfhood, consciousness, sentience, or general lifelikeness.

## Frozen architecture boundary

The actor-local PEMA pipeline and integrated resource economy inherited from the parent are unchanged. Actors retain private state and no peer or runtime references. Inter-actor effects remain explicit messages applied after allocation. The shared allocator remains content-blind. Transport semantics remain distinct from actor-local cognitive semantics. Existing evidence feedback, concern reserve, fatigue, delivery legality, and exact resource-accounting rules remain separately ablatable. No language model or language-generated cognition is introduced.

## World generator

The developmental world is deterministic given a world seed. It generates mundane events from the same event vocabulary and legal delivery paths already accepted by the integrated runtime rather than adding new cognitive mechanisms.

Each 40-tick epoch contains exactly the same event-opportunity counts across histories. Within an epoch, a seeded permutation changes ordering, actor exposure, and whether ambiguous evidence about the recurring social alternatives is supportive, conflicting, repairing, or neutral. The generator may change informational history but may not change total resource capacity, total legal delivery opportunities, operation costs, actor set, or the number of evaluation opportunities.

World generation is performed before the run from the world seed. Runtime behavior cannot alter future generated events in this experiment. This prevents policy-dependent environment generation from becoming an uncontrolled causal path.

## Conditions

`GENERATIVE_DIFFERENTIAL`: generated history with normal differential routing.

`GENERATIVE_NO_FEEDBACK`: byte-identical generated history with allocation-dependent evidence feedback disabled.

`GENERATIVE_NO_RESERVE`: byte-identical generated history with concern reserve disabled.

`GENERATIVE_GLOBAL`: byte-identical generated history with the existing global-routing comparison.

`REPEATED_DIFFERENTIAL`: the inherited repeated 40-tick world extended to the same total duration with normal differential routing. This is the static-world duration control.

`IDENTICAL_HISTORY_REPLICATE`: two independent runtime instances consume the exact same serialized generated history and configuration. Their event streams, allocation traces, private-state snapshots, and probe signatures must match exactly under deterministic execution. Failure is an execution blocker, not a scientific result.

## Seeds and pairing

World seeds are frozen as `1103, 2207, 3301, 4409, 5501, 6607, 7703, 8807, 9901, 11113`.

Every seed is reused across all generated conditions. Ablations receive the byte-identical serialized history for their paired seed. Runtime random sources, if any remain, must be explicitly seeded and recorded separately from the world seed. Seed state must be recreated for every condition, never shared by mutable generator objects.

The identical-history control uses world seed `1103` twice from fresh runtime instances.

## Duration and evaluation windows

Each developmental run lasts exactly 24,000 ticks, or 600 40-tick epochs. This is 100 times the integrated 240-tick demonstration while remaining inexpensive enough for paired deterministic sweeps.

Developmental behavior is summarized in six non-overlapping 4,000-tick blocks to expose regime changes rather than hiding them in one aggregate.

After tick 24,000, learning-relevant state is frozen. Each mature runtime is then evaluated with six identical 40-tick probe epochs derived from the inherited controlled social sequence. Probe inputs, order, capacity, and legal deliveries are identical across all conditions and seeds. Probe execution may update transient runtime bookkeeping needed to execute a tick but must not update learned evidence, reserve baselines, or developmental summaries. If the inherited implementation cannot support a non-learning probe without semantic changes, implementation must stop for a new preregistration rather than silently changing this rule.

## Primary outcome

For each seed and condition, the mature probe signature is the ordered six-element social decision sequence already used by the integrated experiment, together with the corresponding per-probe allocation shares for `EXPLORATION`, `ROUTINE`, and `CONCERN` and the actor-local evidence values that are causally upstream of those decisions.

A `stable behavioral tendency` is preregistered as follows: a generated history produces a seed-specific mature tendency only when its six-probe decision signature differs from `REPEATED_DIFFERENTIAL` for that same seed in at least four of six probe epochs, and the direction of that difference is supported by the causally upstream private evidence/allocation trace rather than by illegal delivery, resource-accounting failure, or a probe-time learning update.

The experiment-level developmental-persistence criterion is met only if at least 7 of 10 paired seeds satisfy that seed-specific rule in `GENERATIVE_DIFFERENTIAL`, while `GENERATIVE_NO_FEEDBACK` reduces the number of qualifying seeds by at least half. This threshold is a decision rule for this toy experiment, not a population-statistical claim.

## Secondary outcomes

Report, without substituting them for the primary criterion: per-block operation allocation shares; concern recall count; legal/missed deliveries; private evidence trajectories; fatigue trajectories; count of each mature decision; and pairwise probe-signature Hamming distance among seeds.

Report every seed before aggregates.

## Required controls and failure gates

Resource conservation must hold at every tick within the existing numerical tolerance. No actor may gain a peer or runtime reference. No illegal message delivery may be counted as evidence. Generated conditions paired by seed must have identical serialized histories. Event-opportunity counts and resource capacity must match across paired generated conditions. The repeated-world control must have exactly the same tick count and capacity schedule as the generated conditions. The identical-history replicate must be exactly reproducible.

Any violation above blocks interpretation until repaired and rerun.

## Interpretation matrix

If generated differential histories satisfy the primary criterion and the no-feedback ablation collapses it, the result supports the narrow claim that the existing PEMA feedback path can convert differing long histories into persistent differences observable under a common probe.

If generated and repeated histories remain similar, the result does not support developmental persistence at this duration and generator complexity.

If generated histories diverge but no-feedback does not reduce divergence, history dependence is not attributable to the preregistered evidence-feedback mechanism.

If divergence is explained by capacity saturation, missed legal deliveries, event-count imbalance, probe-time learning, or nondeterminism, the scientific result is invalid until the execution defect is corrected.

The global-routing and no-reserve conditions are mechanistic context. They cannot rescue a failed primary comparison.

## Anti-tuning rule

After implementation begins, do not alter the generator distribution, seed set, 24,000-tick duration, probe battery, primary criterion, thresholds, capacity schedule, inclusion rules, or ablations in response to observed phenotype results. Any scientifically meaningful change becomes a separately preregistered successor experiment.
