# Baseline Qualification Playbook

This playbook operationalizes Stage B. A candidate can be classified as a `RUNNABLE BASELINE` in the project catalog before it is successfully executed by this project. Qualification state records what has actually happened here.

## Gate Q0: Provenance

Record the upstream repository or archive, immutable commit or release, license, language, dependency requirements, original examples or scenarios, and any non-code assets required to reproduce behavior.

A mutable branch name is not sufficient as the experimental reference.

## Gate Q1: Original execution

Attempt to build and run the original system before creating a common-world adapter.

Prefer a shipped example, demo, regression test, or scenario that exercises the candidate's intended behavior. Preserve output and the exact execution command.

If execution fails, classify the failure before changing code:

`MISSING DEPENDENCY`: an expected external package or runtime is absent.

`OBSOLETE ENVIRONMENT`: the implementation depends on an old runtime, API, build tool, or platform assumption.

`MISSING ASSET`: code exists but necessary data or proprietary assets are unavailable.

`SOURCE DEFECT`: the pinned upstream source does not execute as documented even in an appropriate environment.

`UNKNOWN`: evidence is not yet sufficient to classify the failure.

Do not reinterpret an environment failure as evidence that the cognitive mechanism is weak.

## Gate Q2: Environment compatibility

When a modern host requires a compatibility change, prefer an external shim or containerized historical environment over modification of candidate logic.

Every compatibility intervention must be recorded. It must not introduce memory, goals, planning, social state, appraisal, action ranking, learning, or other cognition.

If original source must be patched to execute, preserve the patch separately and identify every changed line. A patch that can alter decision behavior creates a challenger and cannot stand in for the original baseline.

## Gate Q3: Native behavior trace

Once the original system executes, capture a native trace before common-world adaptation. The trace should include enough internal or externally visible state to prove that the system is doing more than launching.

For a social simulation this may include agent identities, initial social state, action candidates, selected actions, state transitions, trigger results, and subsequent changed action preferences. For a cognitive architecture it may instead include active motives, chosen actions, world transitions, or other native observables.

This gate changes qualification state to `EXECUTED` only when behavior has actually advanced through at least one meaningful state transition.

## Gate Q4: Thin adapter

Implement only the mapping defined in `adapters/ADAPTER_CONTRACT.md`.

The adapter must preserve native action records and must not repair missing cognition. A scenario the candidate cannot express is recorded as `NOT EXPRESSIBLE`.

Passing this gate changes qualification state to `ADAPTED`.

## Gate Q5: Common behavioral battery

Run all expressible scenarios in `scenarios/BEHAVIORAL_BATTERY.md` using controlled histories and seeds where supported.

Store raw traces before derived metrics. Repetitions are required when the candidate is stochastic and cannot be deterministically seeded.

A candidate cannot receive `BATTERY COMPLETE` while silently omitting difficult scenarios. Every scenario must be either completed or explicitly marked `NOT EXPRESSIBLE` with the architectural reason.

## Gate Q6: Performance profile

Measure initialization cost, tick or decision time, memory, persistent-storage growth, and scaling. Use the population sizes required by the performance battery where the candidate architecture supports them.

Performance is part of baseline characterization, not a post-hoc optimization step.

## Gate Q7: Artificiality attack

Run the attacks in Stage G against the baseline. Record failures without correcting them first.

The purpose of baseline qualification is to discover what the original system actually does well and poorly. Correcting a failure before preserving it destroys donor evidence.

## Gate Q8: Baseline report

Create a report that separates observations from interpretation. The report must identify strong behavioral phenomena, weak phenomena, unexpressible phenomena, measured computational cost, licensing constraints, and candidate mechanisms worth isolating.

Only after this report may the project decide whether the system is a plausible Champion 0 or primarily a mechanism donor.

## Initial queue

`PC-001 Ensemble`: execute pinned Lovers and Rivals first, then create a thin social-world adapter. Highest-priority initial scenarios are B01, B02, B14, B15, B18, B19, and B20.

`PC-002 FAtiMA Toolkit`: execute a shipped tutorial or application that exercises appraisal, decision making, and Social Importance Dynamics before adaptation. Highest-priority initial scenarios are B01, B02, B05, B14, and B18.

`PC-003 PsychSim`: execute a shipped social scenario and preserve explicit model-of-other-agent behavior. Highest-priority initial scenarios are B02, B09, B17, and B19.

`PC-004 inBloom`: execute Little Red Hen or another shipped scenario with affective BDI and personality active. Highest-priority initial scenarios are B04, B05, B10, B16, and B17.

`PC-005 MicroPsi2`: reproduce the historical runtime closely enough to observe unmodified architecture behavior before considering modernization. Highest-priority initial scenarios are B03, B04, B11, B13, B16, and B17.

The order can change when archaeology finds a stronger complete system. The queue is not a commitment to synthesize these candidates.
