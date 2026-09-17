# EXP-010 Narrow External Prior Art

Scope: mechanisms that preserve an unfinished goal/intention through temporary competition or interruption without requiring it to remain behaviorally dominant. This is not a general cognitive-architecture survey.

## Altmann & Trafton, Memory for Goals (2002)

Reference: Erik M. Altmann and J. Gregory Trafton, “Memory for goals: an activation-based model,” *Cognitive Science* 26(1), 39–83, 2002. DOI: `10.1207/S15516709COG2601_2` / `10.1016/S0364-0213(01)00058-1`.

Relevant result: suspended goals can be modeled using ordinary memory activation and associative priming rather than a dedicated goal stack. Pending goal representations remain retrievable while their activation changes, and interruption/resumption behavior depends on residual activation, strengthening, and cues.

Relevance to EXP-010: strongly supports separating continued representational existence from current accessibility/dominance. It does not imply that this prototype needs a separate goal-memory system. EXP-010 already has an identity-plus-activation concern representation; the immediate question is whether enough such records can coexist.

Unnecessary architecture for the present test: general associative priming, retrieval latency model, interference equations, cue-based goal reconstruction.

## Bratman, Israel & Pollack, Plans and Resource-Bounded Practical Reasoning (1988)

Reference: Michael E. Bratman, David J. Israel, and Martha E. Pollack, “Plans and resource-bounded practical reasoning,” *Computational Intelligence* 4(3), 349–355, 1988. DOI: `10.1111/j.1467-8640.1988.tb00284.x`.

Relevant result: persistent plans/intentions constrain subsequent practical reasoning in a resource-bounded agent. The architecture distinguishes committed plans from momentary alternative evaluation.

Relevance to EXP-010: supports the broader principle that competition for current behavior need not erase an existing commitment. It does not justify importing BDI/planning machinery into this experiment.

## Schut & Wooldridge, Intention Reconsideration (2004)

Reference: Martijn Schut and Michael Wooldridge, “The theory and practice of intention reconsideration,” *Journal of Experimental & Theoretical Artificial Intelligence* 16(4), 2004.

Relevant result: BDI agents require policies for when intentions should be reconsidered because intentions normally persist as commitments even while circumstances change. Abandonment is associated with explicit reconsideration conditions such as infeasibility or better alternatives, not merely with another intention being temporarily stronger.

Relevance to EXP-010: useful termination semantics. Temporary competition alone is weak evidence for deletion. The current experiment nevertheless avoids implementing a general reconsideration policy.

## Maes, Behavior Networks (1989)

Reference: Pattie Maes, “How to do the Right Thing,” *Connection Science* 1(3), 291–323, 1989. DOI: `10.1080/09540098908915643`.

Relevant result: action selection can emerge from activation and inhibition among competence modules, with tunable balance between goal orientation, ongoing activity, adaptivity, and goal conflict.

Relevance to EXP-010: supports the distinction between something remaining in the competitive architecture and something currently winning action selection. It does not itself supply a minimal memory rule for displaced unfinished concern identities.

## Interruption/resumption evidence

Follow-up human task-interruption experiments based on the Memory for Goals model report longer resumption times after longer or more demanding interruptions and support decay/rehearsal effects on resuming suspended goals. Example: Monk, Trafton & Boehm-Davis, 2008/2009, DOI `10.1037/a0014402`.

Relevance: suspension duration can matter, but that is a separate forgetting/reactivation-strength question. EXP-010 must first solve the lower-level representational impossibility that current v9.2 retains zero bits identifying an evicted unfinished concern. Long-duration forgetting is therefore a reviewer/scope-control probe, not an automatic feature requirement.

## Prior-art conclusion

Across these families, the recurring distinction is stable:

- representation/commitment may persist;
- current activation, dominance, or accessibility may fall;
- explicit termination is conceptually different from temporary competition;
- resource bounds still require a loss policy.

None of the reviewed work implies that a new BDI stack, planner, dormant-goal subsystem, or associative memory layer is necessary for EXP-010. The current architecture already contains the relevant semantic pieces: unresolved concern identity, decaying activation, bounded competition, and a derived active winner. The untested quantity is representational capacity.
