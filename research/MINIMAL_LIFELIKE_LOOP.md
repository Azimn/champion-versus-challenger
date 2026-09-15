# Minimal Lifelike Non-LLM Loop

## Objective

Discover the smallest persistent non-LLM architecture that produces measurable longitudinal individuality. External architectures are treated as baselines and mechanism donors. Their names, module boundaries, and implementation complexity do not earn credit by themselves.

The experimental subject emits symbolic actions and persistent state only. Natural-language rendering is an optional observer. It cannot alter cognition, memory, appraisal, motivation, learning, or action selection.

## Optimization target

Optimize behavioral leverage per unit of complexity.

A mechanism is retained only when all of the following are true:

1. The current champion exhibits a reproducible artificiality failure.
2. Prior art provides evidence that a mechanism family addresses that kind of failure.
3. A minimal functional analogue produces the predicted behavioral change under identical history and scenario controls.
4. The reviewer cannot explain the apparent gain as leakage, overgeneralization, meaningless randomness, or a test artifact.
5. Previously earned behavioral gains remain intact.
6. The added persistent state and runtime cost are recorded.
7. Ablation, represented here by the immediately preceding champion, removes the improvement.

## Champion 0

`v0_reactive`

Persistent state is limited to three drifting pressures: fatigue, affiliation, and competence. Actions are selected by lightweight utility scoring. This deliberately resembles the minimum useful old-school autonomous game character rather than a cognitive architecture.

Champion 0 is expected to look alive moment to moment but artificial across history.

## Cycle 1

Observed artificiality failure: supportive and hostile histories collapse to the same later social behavior.

Prior-art donor family: Ensemble / Comme il Faut style social state and history-sensitive social action selection.

Minimal hypothesis: one partner-specific signed relationship scalar is sufficient to make otherwise identical present encounters diverge according to social history.

Challenger: `v1_relationship`.

Added mechanism: partner-keyed relationship value updated by supportive and hostile events and consulted during social action scoring.

Falsification probe: hostility from Alex must not cause avoidance of unrelated Blake.

Known limitation: a signed scalar cannot represent ambivalence, role structure, reputation, obligation, or multidimensional relationships.

## Cycle 2

Observed artificiality failure: once an aversive event ends, the character recovers immediately because only the current event affects action.

Prior-art donor family: GAMYGDALA and FAtiMA appraisal systems, both of which model emotional state that persists beyond the triggering event and can influence later behavior.

Minimal hypothesis: a single decaying threat residue is sufficient to create short recovery inertia without importing a full OCC emotion taxonomy.

Challenger: `v2_affect`.

Added mechanism: one bounded threat residue updated by aversive events, decayed each tick, and consulted during avoidance scoring.

Falsification probe: residue must decay enough that neutral behavior returns. Permanent avoidance is not emotional continuity.

Known limitation: one threat scalar cannot distinguish fear, anger, shame, grief, or mixed affect.

## Cycle 3

Observed artificiality failure: an interrupted task disappears from behavior when it is no longer present in immediate perception.

Prior-art donor family: BDI intention commitment and practical intention maintenance.

Minimal hypothesis: one explicit active concern with slow decay is sufficient to make the character return to unfinished activity after an interruption.

Challenger: `v3_concern`.

Added mechanism: one concern identifier plus one strength value. It persists across interruption, biases relevant action, and can be explicitly cancelled.

Falsification probe: a cancelled concern must stop affecting behavior. Persistence that ignores changed circumstances is not lifelikeness.

Known limitation: only one concern can be represented, so genuine multi-motive conflict is still absent.

## Cycle 4

Observed artificiality failure: routine choices do not change from repeated experience when no explicit goal or social state changes.

Prior-art donor family: reinforcement-shaped artificial-life systems and old-school simulation designs in which repeated outcomes alter future action tendency. The Sims lineage is also relevant as evidence that very simple need and utility mechanisms can generate convincing autonomy cheaply.

Minimal hypothesis: context-action reinforcement values are sufficient to create learned routine preference without planning or language.

Challenger: `v4_habit`.

Added mechanism: bounded context-action habit values updated from reward or punishment after action.

Falsification probe: a morning routine must not leak into an unrelated evening context.

Known limitation: this is simple cached action tendency, not sequence learning or skill acquisition.

## Cycle 5

Observed artificiality failure: the character can remember how it feels about another person but cannot learn what that person is likely to do from observations of that person's behavior.

Prior-art donor family: PsychSim's explicit models of other agents and observation-driven model updating.

Minimal hypothesis: full recursive Theory of Mind is not required for the first useful social-prediction gain. A single partner-specific reliability estimate should be enough to distinguish a repeatedly reliable actor from a repeatedly unreliable one when deciding whether to delegate or verify.

Challenger: `v5_partner_model`.

Added mechanism: one signed reliability estimate per observed partner. Reliable evidence raises the estimate, unreliable evidence lowers it, and the value biases delegation versus verification.

Falsification probe: evidence about Alex must not change behavior toward Blake, and later contradictory evidence about Alex must be able to reverse the prediction.

Known limitation: this is a first-order behavioral model, not recursive Theory of Mind. It does not represent another agent's beliefs, goals, false beliefs, or beliefs about the character.

## Reviewer role

The reviewer is adversarial. A challenger is not promoted because it passes its target scenario. The reviewer independently tries to expose a cheaper explanation or a side effect that would make the character look less like a persistent individual.

The initial reviewer probes test partner specificity, emotional recovery, concern cancellation, habit context specificity, social-model specificity, and social-model revision. Future cycles should add adversarial probes before implementation whenever possible.

## Complexity accounting

Every version records median decision time, a representative serialized persistent-state size, and mechanism count. These metrics are intentionally simple and reproducible. They do not claim to represent production memory allocation exactly.

The experiment also reports behavioral probes passed per mechanism. This ratio is a diagnostic, not an optimization oracle. A mechanism can still be rejected for severe qualitative regressions even if the ratio rises.

## Next confirmed gaps after v5

If v5 survives evaluation, the next artificiality attacks should focus on multi-motive conflict, prospective memory with deadlines, false belief and limited knowledge, differentiated forgetting, habit reversal under changed contingencies, and multi-step spontaneous activity.

Do not add these mechanisms until a scenario demonstrates the failure in the current champion.
