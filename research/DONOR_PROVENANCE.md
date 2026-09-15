# Donor Provenance and Licensing Boundaries

This branch uses external systems as empirical and conceptual donors. No donor source code is copied into the experimental runtime unless explicitly recorded here. The current implementation is a clean functional reconstruction of general mechanisms from published descriptions and observed system behavior.

## Ensemble / Comme il Faut lineage

Repository: https://github.com/ensemble-engine/ensemble

Role in this branch: conceptual and behavioral donor for partner-specific social state, history-sensitive social reasoning, and social action selection.

License: BSD 4-Clause University of California variant.

Reuse boundary: no Ensemble source code is copied into `lifelike_min`. The experiment implements only the general hypothesis that partner-specific social state can causally differentiate later behavior after different histories.

## FAtiMA Toolkit

Repository: https://github.com/GAIPS/FAtiMA-Toolkit

Role in this branch: conceptual and behavioral donor for appraisal, persistent emotional state, and emotion-influenced decision making.

License: Apache-2.0.

Reuse boundary: no FAtiMA source code, rules, serialized assets, or test fixtures are copied. The challenger uses a single decaying threat residue rather than FAtiMA's architecture or emotion representation.

## GAMYGDALA

Repository: https://github.com/broekens/gamygdala

Project page: https://ii.tudelft.nl/~joostb/gamygdala/index.html

Reference: Popescu, A., Broekens, J., and van Someren, M. (2014). GAMYGDALA: An Emotion Engine for Games. IEEE Transactions on Affective Computing, 5(1), 32-44.

Role in this branch: conceptual donor for low-cost appraisal with emotion decay that can be used independently of the rest of the game AI.

License: MIT for the published JavaScript implementation.

Reuse boundary: no GAMYGDALA source code is copied. The experiment tests the much smaller hypothesis that decaying post-event affect can eliminate instantaneous recovery.

## BDI intention commitment

Primary references: Rao, A. S., and Georgeff, M. P. (1995). BDI Agents: From Theory to Practice; Bratman-style intention commitment as operationalized by BDI systems.

Role in this branch: conceptual donor for maintaining an intention or concern across time and interruption rather than reselecting solely from the current percept.

Reuse boundary: this is literature-derived conceptual prior art. No BDI platform source code is incorporated. The challenger stores only an active concern identifier and strength.

## The Sims and utility-based autonomous simulation lineage

Evidence source: historical descriptions of The Sims' needs, object advertisements, and utility scoring, including Game Developer and Game Developer Magazine coverage.

Role in this branch: baseline design precedent for the three-pressure reactive champion and for the broader principle that simple interacting needs and affordances can generate convincing autonomy at game scale.

Reuse boundary: no Maxis or EA source code, data, tuning values, or proprietary behavior assets are used.

## Reinforcement-shaped habits

Role in this branch: conceptual donor family covering artificial-life and game simulations in which outcomes alter future action tendency.

Relevant historical family: Creatures and later open reimplementations such as openc2e are retained in the project catalog as mechanism-donor evidence for drive, reinforcement, and persistent organism state.

Reuse boundary: the current habit challenger is a generic bounded context-action reinforcement table written independently for this experiment. It does not copy Creatures neural rules, genome data, biochemical constants, assets, or openc2e source.

## PsychSim

Repositories: https://github.com/usc-psychsim/psychsim and historical https://github.com/pynadath/psychsim

Reference family: Pynadath and Marsella's PsychSim work on decision-theoretic agents with explicit models of other agents, observation-sensitive beliefs, and Theory of Mind.

Role in this branch: conceptual donor for Cycle 5 social prediction. PsychSim demonstrates the value of maintaining explicit models of other actors and updating those models from observed behavior. The experimental challenger intentionally tests whether a much smaller first-order reliability estimate can obtain useful behavioral leverage before recursive Theory of Mind is justified.

License: MIT for the open-source implementation.

Reuse boundary: no PsychSim source code, domain files, reward functions, or tests are incorporated into `lifelike_min`. Cycle 5 is an independently written scalar partner model. PsychSim remains available for a later direct mechanism tournament if false-belief or recursive social-reasoning failures demonstrate that the scalar model is insufficient.

## Licensing rule

A permissive license does not automatically justify incorporation. Direct donor code is introduced only if a mechanism tournament shows that reusing the implementation provides behavioral value beyond a clean minimal analogue.

GPL or otherwise reciprocal code may be executed and studied as a baseline, but direct incorporation requires an explicit compatibility decision. Proprietary game code and assets are evidence only and are never copied.
