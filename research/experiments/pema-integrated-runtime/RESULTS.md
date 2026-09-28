# Integrated PEMA Shared-Economy Results

## Overall result

The integrated runtime preserved all four causal mechanisms under one shared resource pool, but it did not settle into one simple monotonic behavioral pattern. Capacity, epistemic feedback, reserve, fatigue, and routing topology interacted to create distinct deterministic regimes.

That is the main result.

The experiment should not be read as evidence that the system became lifelike. It shows that the mechanisms do not merely work in isolation: when combined, they can alter one another's ability to acquire information, reconcile conflicting evidence, retrieve latent concerns, and influence action.

## Canonical run

The canonical configuration uses differential access, three resource units per tick, feedback enabled, reserve enabled, fatigue enabled, seed 0, and 240 ticks.

Resource conservation error remains within floating-point tolerance.

The six repeated social decisions are:

`ASK_B_FIRST, SURPRISE_B, SURPRISE_B, SURPRISE_B, SURPRISE_B, SURPRISE_B`

The first decision retains enough reconciliation pressure to produce the conservative response. Later in the run, the continuing resource economy changes which optional operations remain competitive before the decision deadline, and ACTION increasingly resolves from its direct public `welcome` evidence without receiving the stale social recommendation in time.

This behavior is not hard-coded as a developmental transition. The same action-selection rule is used for all six decisions.

The unresolved CONCERN successfully recalls on all six later matching contexts. The recalled item reaches MEMORY through an explicit effect message.

Final pairwise epistemic divergence across SOCIAL, MEMORY, ACTION, and LANGUAGE is approximately 0.583. This reflects the differential routing policy rather than random message loss in the canonical run: all topology-permitted environment deliveries are successfully delivered at capacity 3.

## Feedback ablation

With allocation-dependent evidence acquisition disabled, the six decisions become:

`ASK_B_FIRST, ASK_B_FIRST, ASK_B_FIRST, ASK_B_FIRST, ASK_B_FIRST, ASK_B_FIRST`

The same result occurs when channel evidence is allowed to exist but its weight in future demand is set to zero.

This is a stronger result than simply observing different allocation counts. Removing the epistemic feedback path removes the later behavioral transition while leaving the world schedule, resource capacity, routing topology, action-selection rule, concern system, and fatigue rule unchanged.

Observed integrated path:

`winning allocation -> new local evidence -> changed later demand -> changed competition -> changed availability of reconciliation before action`

## Reserve ablation

With persistent reserve disabled, CONCERN recalls fall from six to zero at the canonical capacity.

The later matching contexts still occur. The concern still exists. What disappears is its ability to accumulate quiet-time economic history strongly enough to become competitive later.

This preserves the Experiment 3 result inside the shared economy:

`history -> reserve -> later competitiveness`

The no-reserve behavioral sequence still differs slightly from the baseline, which is itself evidence that reserve allocation is not isolated from the rest of the economy. Capacity spent on reserve changes what else can execute.

## Fatigue ablation

Removing utilization fatigue increases EXPLORATION's share of the EXPLORATION plus ROUTINE allocation from about 0.518 to about 0.551 in the canonical seed.

Fatigue therefore provides measurable counterpressure against positive-feedback capture. It does not eliminate capture completely and does not impose a global fairness rule.

## Routing ablation

At capacity 3, differential routing delivers all topology-permitted environment messages and ends with epistemic divergence near 0.583.

Global access reduces final epistemic divergence to about 0.208, but it also creates resource-induced message loss. Across ten seeds, the global-access condition misses an average of five legal environment deliveries, while differential access misses zero.

This reproduces the earlier metabolic result inside the full shared economy: broader legal access is not equivalent to broader realized access when every additional route competes for the same finite processing resource.

## Capacity stress sweep

Ten deterministic seeds were run at capacities 2, 3, 4, and 5 for every canonical ablation.

The baseline social behavior is non-monotonic in capacity:

| Capacity | Mean `SURPRISE_B` decisions out of 6 | Mean resource-missed deliveries | Mean concern recalls |
|---:|---:|---:|---:|
| 2 | 3 | 0 | 6 |
| 3 | 5 | 0 | 6 |
| 4 | 0 | 0 | 6 |
| 5 | 0 | 0 | 6 |

More capacity therefore does not simply move behavior in one direction.

At capacity 2, the strongest feedback process captures the optional channel competition more aggressively.

At capacity 3, the system enters a regime in which direct public evidence often reaches ACTION while some reconciliation operations lose competition before the decision deadline, producing five `SURPRISE_B` decisions.

At capacities 4 and 5, more reconciliation work becomes affordable. Under differential routing, SOCIAL still holds its stale private interpretation while MEMORY holds conflicting history, so ACTION again receives enough conflict information to select `ASK_B_FIRST` on all six decisions.

This is not evidence that one capacity is better. It is evidence of a qualitative regime transition created by interactions among the mechanisms.

## Feedback and fatigue phase grid

A second sweep varied evidence weight across 0.0, 0.02, 0.045, and 0.07 and fatigue weight across 0.0, 0.03, 0.055, and 0.08 at capacity 3.

When evidence weight is zero, mean `SURPRISE_B` count is zero for every tested fatigue setting.

At evidence weight 0.02, the mean `SURPRISE_B` count ranges from about 1.2 to 4 depending on fatigue.

At the canonical evidence weight 0.045, the mean ranges from 4 to 5.

At evidence weight 0.07, the mean remains above 3 in every tested fatigue condition.

The effect therefore occupies a parameter region rather than a single exact setting. Fatigue can weaken the positive feedback effect, but the epistemic feedback coefficient is the stronger determinant in the tested grid.

## Seed sensitivity

The canonical capacity-3 differential run is stable across the ten tested seeds: all ten runs preserve all legal environment deliveries, produce six concern recalls, and produce five `SURPRISE_B` decisions.

Seed sensitivity appears more clearly in the global-access condition because broader routing creates more exact competitions under scarcity. Across ten seeds, global access averages 4.8 `SURPRISE_B` decisions rather than producing one invariant trajectory.

This is useful because it separates effects driven by priority structure from effects dependent on exact tie resolution.

## Resource accounting

Across the full multi-seed, multi-capacity, multi-ablation stress suite, the maximum absolute conservation error is approximately `1.14e-13`, consistent with floating-point arithmetic.

The accounting equation is:

`supplied = processing spent + reserve conversion loss + current reserve + reserve consumed + expired unused capacity`

No tested result depends on unlogged resource creation.

## What This Experiment Actually Demonstrated

Direct observation: all four causal links can operate simultaneously through one shared resource economy without requiring a global semantic state object.

Direct observation: allocation-dependent information acquisition can alter later demand strongly enough to change downstream behavior under an otherwise unchanged decision rule.

Direct observation: persistent reserve continues to support later concern recurrence under shared competition, and removing reserve eliminates that recurrence at the canonical capacity.

Direct observation: fatigue reduces positive-feedback capture but does not force equal allocation.

Direct observation: routing topology and resource scarcity continue to interact. A broader global topology can lose more actual messages than a selective topology because it creates more costly delivery opportunities.

Direct observation: behavior changes non-monotonically as capacity increases. The integrated system has multiple deterministic operating regimes rather than a single linear scarcity-to-performance curve.

## What It Did Not Demonstrate

The world remains controlled and repetitive. Actor demand functions remain hand specified. The unresolved concern is supplied rather than spontaneously formed. EXPLORATION and ROUTINE have explicitly defined evidence channels. No semantic learning, personality development, LLM, vector process field, or autonomous goal formation is present.

The results therefore do not demonstrate spontaneous rumination, curiosity, personality, selfhood, consciousness, or general lifelikeness.

The strongest supported conclusion is narrower: the proposed economic and epistemic mechanisms form a functioning coupled dynamical system, and their interaction creates measurable regime changes that disappear or change under targeted ablation.

The next serious test should replace the repeated hand-authored social schedule with a small generative environment and ask whether the same internal dynamics produce stable, recognizable behavioral tendencies across longer developmental histories.
