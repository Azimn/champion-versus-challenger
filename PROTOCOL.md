# Research Protocol

## Mission

Build the most behaviorally convincing lightweight simulated human character possible without using an LLM as its cognitive engine.

Prefer reuse, adaptation, porting, or recombination of mechanisms that have already demonstrated useful behavior in historical or contemporary simulations, games, believable-agent systems, cognitive architectures, virtual humans, social simulations, and artificial-life systems.

Do not begin by inventing a new cognitive architecture.

The first question is always:

> Has somebody already implemented this successfully?

The project uses a Champion versus Challenger experimental structure, but the Champion may initially be an existing external system rather than code created by this project.

LLMs may be used as research assistants, programmers, evaluators, documentation tools, and test designers. LLMs must not be required for the simulated character's cognition, decision making, memory, personality, emotions, relationships, planning, or ongoing behavior unless a later experiment explicitly introduces one as a separate comparison condition.

The target is an old-school autonomous simulation architecture capable of producing convincing behavior through simulation.

## Core Principle

Judge mechanisms by behavioral consequences.

Do not give credit for having modules called memory, emotion, personality, drives, goals, Theory of Mind, planning, needs, relationships, or self-modeling. A mechanism matters only if removing or changing it measurably changes longitudinal behavior.

## Stage A: Software Archaeology

Search academic literature, GitHub, archived projects, game-AI resources, believable-agent research, cognitive architectures, social simulations, artificial-life projects, interactive drama systems, virtual humans, and documented commercial-game techniques.

Give special attention to systems predating widespread LLM use. Search for complete runnable systems before searching for isolated ideas.

For every candidate, establish:

- what the system was designed to accomplish;
- whether runnable source code exists;
- whether examples, demonstrations, tests, or scenarios exist;
- its programming language and dependencies;
- its license;
- its computational requirements;
- its architectural mechanisms;
- its demonstrated behavioral strengths;
- its known weaknesses;
- whether components can legally and technically be reused.

Do not assume a famous architecture is useful merely because it is well cited. Do not reject old software simply because its dependencies are obsolete. Determine whether its mechanisms can be ported.

Maintain `research/PROJECT_CATALOG.md` containing every investigated system.

Classify each candidate as one of:

- `RUNNABLE BASELINE`
- `MECHANISM DONOR`
- `CONCEPTUAL DONOR`
- `UNUSABLE`
- `REQUIRES FURTHER INVESTIGATION`

## Stage B: Baseline Qualification

Before extracting pieces from a system, attempt to run the original system.

Preserve the original implementation wherever practical. Create an adapter between the candidate and the common simulated world. Do not rewrite its architecture merely to make comparison easier.

Run every qualifying system through the same behavioral scenario battery. Record actual behavior rather than architectural claims.

A system that performs surprisingly well may become Champion 0. Do not assume our own implementation deserves to be the initial champion.

## Stage C: Behavioral Decomposition

For each system, determine what behavioral phenomena it handles unusually well.

Trace observed behavior back to the smallest mechanism responsible. Separate causal mechanisms from incidental implementation details.

Record each useful mechanism in `research/MECHANISM_CATALOG.md` with its origin, theoretical basis, implementation location, inputs, outputs, persistent state, update rules, dependencies, computational cost, license implications, demonstrated behavioral contribution, and known failure modes.

## Stage D: Mechanism Tournament

When multiple systems address the same behavioral problem, compare the mechanisms directly.

Candidate tournament domains include motivation, emotion appraisal, memory retrieval, forgetting, relationships, social reasoning, goal arbitration, personality, habit formation, planning, attention, Theory of Mind, and action selection.

Construct controlled scenarios capable of distinguishing the competing mechanisms. Do not select a winner based on theoretical sophistication.

Select mechanisms according to behavioral performance, computational cost, interoperability, robustness, and licensing constraints. Preserve losing mechanisms and experimental evidence in the research ledger.

## Stage E: Minimum Hybrid Assembly

Construct a hybrid only after useful mechanisms have been identified experimentally.

Begin with the strongest complete existing system whenever feasible. Replace or augment one mechanism at a time. Do not combine every interesting architecture.

Every addition must address a demonstrated behavioral weakness. For every proposed addition record:

- the observed failure;
- the donor system;
- the donor mechanism;
- why that mechanism should affect the failure;
- the predicted behavioral change;
- the expected computational cost.

Then construct a challenger.

## Stage F: Champion versus Challenger

Freeze the current champion.

Run champion and challenger through identical experiences. Use identical world states, event sequences, social histories, timing, and random seeds where deterministic comparison is useful.

Evaluate behavior over time rather than isolated responses. Promotion requires evidence of meaningful improvement.

A challenger must not replace the champion merely because its architecture appears more sophisticated. It should outperform the champion in the targeted behavioral phenomenon without introducing unacceptable regressions elsewhere.

If the challenger loses, preserve the champion. If it produces mixed results, diagnose why before proceeding.

## Stage G: Artificiality Attack

Attempt to expose behavior that reveals the simulation.

Test for shallow continuity, formulaic relationships, mechanical emotions, perfect rationality, immediate recovery, excessive predictability, meaningless randomness, omniscient knowledge, perfect memory, total forgetting, repetitive routines, inability to maintain unfinished concerns, identical behavior after different histories, lack of habits, lack of social differentiation, absence of competing motives, and state changes that never affect action.

Longitudinal failures count more heavily than cosmetic dialogue problems. Do not use natural-language eloquence as a proxy for lifelikeness. Ideally, many evaluations should be possible without dialogue at all.

## Stage H: Causal Diagnosis

When artificial behavior is found, trace the failure through the architecture:

`experience -> perception -> appraisal -> memory -> persistent state -> motivation -> goal competition -> planning -> action selection -> outcome -> learning`

Determine where histories that should produce different behavior become equivalent. Modify the smallest causal mechanism capable of addressing the failure.

Before inventing a new solution, return to the project catalog and mechanism catalog and search for an existing solution.

## Stage I: Ablation

Whenever a hybrid appears better, remove or disable the newly introduced mechanism and run the same scenarios again.

If behavior remains effectively unchanged, the mechanism has not demonstrated causal value and should normally be removed. Complexity without behavioral leverage counts against the architecture.

## Stage J: Old-School Performance Test

Treat computational efficiency as part of the experiment.

Record simulation time per agent tick, memory consumption, persistent-storage growth, scaling with number of agents, and expensive operations.

Prefer mechanisms that could plausibly operate in a traditional game simulation. A slightly weaker mechanism that supports hundreds of agents may be more valuable than a sophisticated mechanism capable of supporting only one.

## Stage K: Human Observer Test

Once internal evaluation stops finding obvious improvements, expose behavioral traces or interactive simulations to human evaluators.

Whenever possible, hide the implementation identity. Ask evaluators which character appears more like an individual whose current behavior results from its history.

Do not tell evaluators which system is newer or theoretically more sophisticated.

## Permanent Project Memory

Maintain four permanent artifacts:

- `research/PROJECT_CATALOG.md`
- `research/MECHANISM_CATALOG.md`
- `research/EXPERIMENT_LEDGER.md`
- `research/CHAMPION_LINEAGE.md`

Never discard failed approaches. Before implementing a mechanism, check whether the project has already tested the same mechanism or a functional equivalent.

## Automatic Research Loop

Repeat:

`SEARCH EXISTING SYSTEMS`
`-> QUALIFY RUNNABLE PROJECTS`
`-> RUN COMPLETE BASELINES`
`-> IDENTIFY BEHAVIORAL STRENGTHS`
`-> TRACE STRENGTHS TO MECHANISMS`
`-> COMPARE COMPETING MECHANISMS`
`-> SELECT THE BEST DONOR`
`-> BUILD ONE HYBRID CHALLENGER`
`-> RUN CHAMPION VS CHALLENGER`
`-> ATTACK ARTIFICIALITY`
`-> PERFORM CAUSAL DIAGNOSIS`
`-> PERFORM ABLATION`
`-> PROMOTE OR REJECT`
`-> SEARCH PRIOR ART FOR THE NEXT CONFIRMED FAILURE`
`-> REPEAT`

## Important Research Rule

Never allow the project to gradually become an architecture invented almost entirely by the current developer merely because integration is easier than understanding historical systems.

Existing implementations are evidence. Our own ideas are hypotheses.

When a mature existing mechanism and a newly invented mechanism address the same problem, the new mechanism must earn its place experimentally.

## Initial Seed Search

Begin by investigating mature non-LLM systems including FAtiMA Toolkit, PsychSim, MicroPsi and MicroPsi2, GAMYGDALA, affective BDI systems such as inBloom, believable-agent descendants of the Oz tradition, and other runnable social or autonomous-character architectures discovered during research.

This is not a fixed whitelist. Search for stronger candidates.

Do not integrate any code until its license has been checked.

## Initial Objective

The first major milestone is not "create Persona v1."

The first milestone is:

> We have identified, obtained, executed, adapted, and behaviorally compared the strongest practical non-LLM character simulations we can find.

Only after that milestone should the project construct its first synthesis architecture.

## Final Target

The eventual system should behave like a persistent simulated person even if all natural-language generation is removed.

The character should still be recognizable through choices, routines, relationships, avoidance, preferences, memory, goals, mistakes, adaptation, conflicts, habits, spontaneous activity, social expectations, and consequences accumulated through experience.

Language may eventually provide an expressive surface. It must not be the source of the character's apparent mind.
