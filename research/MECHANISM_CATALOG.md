# Mechanism Catalog

This catalog is intentionally stricter than the project catalog. A mechanism does not receive causal credit because a paper or repository says it exists. Entries can be registered before testing, but they remain `UNVERIFIED` until an experiment demonstrates a behavioral contribution and an ablation shows that contribution disappears when the mechanism is removed or neutralized.

## Evidence states

`UNVERIFIED`: candidate mechanism identified from prior art, not yet causally tested here.

`TRACE-SUPPORTED`: behavior correlated with the mechanism in a complete baseline, but no direct mechanism isolation yet.

`TOURNAMENT-SUPPORTED`: mechanism outperformed at least one competing mechanism in a controlled tournament.

`ABLATION-SUPPORTED`: disabling the mechanism removed or materially weakened the target behavior.

`REJECTED`: mechanism failed to provide sufficient behavioral leverage, robustness, cost efficiency, or legal/technical feasibility.

## MC-001: Ensemble volition rules and social history

**Evidence state:** UNVERIFIED  
**Origin:** Ensemble / Comme il Faut lineage  
**Behavioral problem:** Social differentiation and history-sensitive action preference.  
**Theoretical basis:** Rule-based social reasoning over persistent social state and history.  
**Implementation location:** `ensemble-engine/ensemble`, core library plus example domains. Exact functions will be recorded during qualification.  
**Inputs:** Current social state, character history, rule conditions, candidate social actions.  
**Outputs:** Volition values and ranked social action preferences.  
**Persistent state:** Social facts, relationship values/statuses, event history.  
**Update rules:** Domain-authored trigger and volition rules.  
**Dependencies:** Ensemble runtime and authored domain data.  
**Computational-cost hypothesis:** Low to moderate for game-scale casts, dominated by rule evaluation across social state. Must be measured.  
**License implication:** BSD-4-Clause variant with advertising acknowledgement requirement.  
**Predicted behavioral contribution:** Two characters with different histories should prefer different social actions under the same immediate stimulus.  
**Known failure modes to probe:** Rule explosion, insufficient generalization, brittle unhandled contexts, social behavior that becomes too legible after repeated observation.  
**Required test:** Paired supportive versus hostile history, then identical opportunity for cooperation, disclosure, avoidance, or retaliation. Follow with ablation of relevant history/volition rule path.

## MC-002: FAtiMA emotional appraisal

**Evidence state:** UNVERIFIED  
**Origin:** FAtiMA Toolkit  
**Behavioral problem:** Emotional continuity and event-sensitive behavior.  
**Theoretical basis:** Appraisal-based affect, including OCC-style emotional categories in modern toolkit versions.  
**Implementation location:** FAtiMA Emotional Appraisal assets. Exact classes and update path will be recorded during code audit.  
**Inputs:** Perceived events, beliefs, authored appraisal rules.  
**Outputs:** Emotional-state updates.  
**Persistent state:** Beliefs and emotional state.  
**Update rules:** Appraisal rules triggered by events and current state.  
**Dependencies:** FAtiMA core and authored scenario configuration.  
**Computational-cost hypothesis:** Suitable for game/robot agents, but must be benchmarked per tick and per event.  
**License implication:** Apache-2.0.  
**Predicted behavioral contribution:** Equivalent current world states reached through different emotionally significant histories should yield different action tendencies.  
**Known failure modes to probe:** Instant or overly categorical emotion changes, rapid recovery, repeated appraisal patterns, emotion state that changes numerically but does not alter action.  
**Required test:** Matched histories differing only in supportive versus humiliating events, followed by identical social request. Ablate appraisal or clamp affect to neutral.

## MC-003: FAtiMA Social Importance Dynamics

**Evidence state:** UNVERIFIED  
**Origin:** FAtiMA Toolkit  
**Behavioral problem:** Relationship-sensitive social appropriateness and interpersonal differentiation.  
**Theoretical basis:** Relational appraisal of socially appropriate actions.  
**Implementation location:** Social Importance Dynamics asset.  
**Inputs:** Perceived other, relational/social state, possible actions.  
**Outputs:** Social appropriateness or importance effects used in decision making.  
**Persistent state:** Relationship-relevant social state.  
**Update rules:** Toolkit-specific relational dynamics and authored rules.  
**Dependencies:** FAtiMA belief/world model and decision assets.  
**Computational-cost hypothesis:** Low enough for interactive systems, pending measurement.  
**License implication:** Apache-2.0.  
**Predicted behavioral contribution:** Identical requests from friend, stranger, and adversary should not produce identical choices.  
**Known failure modes to probe:** Relationship changes too quickly, symmetrical or scalar-only relationships, weak carryover from past interactions.  
**Required test:** Multi-partner social differentiation scenario with relationship history reversal.

## MC-004: PsychSim recursive agent models

**Evidence state:** UNVERIFIED  
**Origin:** PsychSim  
**Behavioral problem:** Theory of Mind, prediction of other agents, behavior under asymmetric beliefs.  
**Theoretical basis:** Decision-theoretic agents maintaining models of other agents and world state.  
**Implementation location:** PsychSim agent/world/model code. Exact model recursion path will be documented during audit.  
**Inputs:** Beliefs, action alternatives, modeled utilities, model of others.  
**Outputs:** Expected outcomes and action choices.  
**Persistent state:** World state and agent models/beliefs.  
**Update rules:** Bayesian or model-transition machinery as implemented by PsychSim.  
**Dependencies:** PsychSim package and domain model.  
**Computational-cost hypothesis:** Potentially expensive as model depth and branching increase.  
**License implication:** MIT.  
**Predicted behavioral contribution:** An agent should act on what another agent believes rather than omniscient ground truth when those diverge.  
**Known failure modes to probe:** Excessive rationality, brittle utility authoring, computational growth, lack of affective or habitual interference.  
**Required test:** False-belief and deception scenarios at multiple model depths, with model-depth ablation and runtime measurement.

## MC-005: inBloom affect-sensitive BDI plan selection

**Evidence state:** UNVERIFIED  
**Origin:** inBloom / extended Jason  
**Behavioral problem:** Personality and mood affecting goal-directed behavior.  
**Theoretical basis:** BDI plan selection constrained or prioritized by personality and affect annotations.  
**Implementation location:** Extended Jason architecture and AgentSpeak plan annotations.  
**Inputs:** Beliefs, desires/goals, available plans, personality traits, mood, emotions.  
**Outputs:** Selected plan or altered plan preference.  
**Persistent state:** BDI beliefs, goals, personality, mood and emotion state.  
**Update rules:** Jason reasoning cycle plus inBloom affective extensions.  
**Dependencies:** Java, Jason framework, inBloom extensions.  
**Computational-cost hypothesis:** Moderate and likely practical for small casts. Must be measured.  
**License implication:** GPL-3.0, so direct incorporation may constrain the license of a combined derivative.  
**Predicted behavioral contribution:** Stable personality differences should alter plan choice across repeated but not identical situations, with mood creating temporary deviations rather than personality replacement.  
**Known failure modes to probe:** Discrete plan gating, author dependence, personality becoming a superficial switch, affect changing narration more than action.  
**Required test:** Crossed personality-by-mood scenario with repeated choice opportunities and personality/mood ablations.

## MC-006: MicroPsi motivational dynamics

**Evidence state:** UNVERIFIED  
**Origin:** MicroPsi / MicroPsi2  
**Behavioral problem:** Competing motives, persistence, switching, context-sensitive mobilization.  
**Theoretical basis:** MicroPsi motivational and modulatory control concepts.  
**Implementation location:** To be established during MicroPsi2 code audit; the repository also has related motivation demonstration work.  
**Inputs:** Need states, activation, modulatory variables, environmental signals.  
**Outputs:** Motive priorities and control modulation.  
**Persistent state:** Need/motive and network activation state.  
**Update rules:** Architecture-specific activation and modulation dynamics.  
**Dependencies:** MicroPsi2 runtime, historically old Python and optional Theano/spock dependencies.  
**Computational-cost hypothesis:** Unknown in current environments; original project explicitly did not prioritize performance in early releases.  
**License implication:** MIT core unless marked otherwise.  
**Predicted behavioral contribution:** A suppressed motive should remain latent, return when conditions change, and compete with other motives rather than disappearing after one choice.  
**Known failure modes to probe:** Difficult authoring/tuning, node-network opacity, weak social grounding, old runtime friction.  
**Required test:** Long-horizon interrupted-goal and competing-needs scenario, followed by motive-system clamp/ablation.

## MC-007: GAMYGDALA appraisal engine

**Evidence state:** UNVERIFIED  
**Origin:** GAMYGDALA  
**Behavioral problem:** Low-cost emotional response for game agents.  
**Theoretical basis:** Computational appraisal model designed for games.  
**Implementation location:** `broekens/gamygdala`, JavaScript engine.  
**Inputs:** Events, goals, agent relations/configuration.  
**Outputs:** Agent emotional-state changes.  
**Persistent state:** Emotion/appraisal-related agent state.  
**Update rules:** GAMYGDALA appraisal update rules.  
**Dependencies:** Core library is engine-independent; browser examples use JavaScript and optional Phaser integrations.  
**Computational-cost hypothesis:** Intentionally lightweight. Must be measured under multi-agent load.  
**License implication:** MIT.  
**Predicted behavioral contribution:** Provides event-sensitive affect at much lower cost than a full architecture.  
**Known failure modes to probe:** Affect may be causally inert without a strong action-selection coupling; emotional trajectories may be formulaic.  
**Required test:** Appraisal tournament against FAtiMA and inBloom using the same event histories and action-coupling policy.

## MC-008: Creatures-style biochemical drives and learned associations

**Evidence state:** UNVERIFIED  
**Origin:** Creatures lineage; current code archaeology begins with openc2e and documented original techniques.  
**Behavioral problem:** Continuous organism-like state, body consequences, habit/association learning, nonverbal spontaneous behavior.  
**Theoretical basis:** Artificial-life simulation combining biochemical drives, neural control, learning, and persistent organism state.  
**Implementation location:** openc2e currently implements parts of Creatures biochemistry; full original creature behavior requires additional historical archaeology and may depend on proprietary data.  
**Inputs:** Body chemistry, sensory events, neural/associative state, environmental affordances.  
**Outputs:** Drive changes, learned associations, action tendencies.  
**Persistent state:** Biochemistry, learned neural weights/associations, genome/organism state.  
**Update rules:** Continuous biochemical and neural simulation.  
**Dependencies:** openc2e plus compatible game data for faithful full-system execution.  
**Computational-cost hypothesis:** Historically designed for consumer hardware, making it especially relevant to the old-school performance target. Modern reimplementation cost must still be measured.  
**License implication:** openc2e is LGPL-2.1; original game data and code have separate rights and must not be conflated.  
**Predicted behavioral contribution:** Character state should drift continuously, past reinforcement should alter later choices, and behavior should occur without requiring explicit conversational prompts.  
**Known failure modes to probe:** Animal-level cognition, weak human social modeling, difficulty isolating causal subsystems, incomplete modern engine support.  
**Required test:** Habit acquisition, extinction, spontaneous action, and competing bodily-drive scenarios.

## Tournament rule

No mechanism above is selected for synthesis merely because it is documented here. A mechanism enters a hybrid only after the relevant complete baselines have been observed, a specific behavioral failure has been demonstrated, competing donor mechanisms have been compared where practical, and the selected mechanism has a falsifiable predicted behavioral effect.
