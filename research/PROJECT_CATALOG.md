# Project Catalog

This catalog records every investigated external system. Classification is not a statement that the project has successfully executed the candidate. `Qualification state` records what this project has actually verified.

## Status vocabulary

`DISCOVERED`: located and minimally identified.

`SOURCE VERIFIED`: repository, implementation language, and license inspected.

`EXECUTION PENDING`: source appears runnable but has not yet been executed by this project.

`EXECUTED`: original system has been run without architectural rewriting.

`ADAPTED`: a thin adapter to the common behavioral world exists.

`BATTERY COMPLETE`: the common scenario battery has been completed and traces preserved.

## PC-001: Ensemble

**Classification:** RUNNABLE BASELINE  
**Qualification state:** SOURCE VERIFIED, EXECUTED  
**Origin:** UC Santa Cruz, evolution of Comme il Faut from Prom Week  
**Repository:** https://github.com/ensemble-engine/ensemble  
**Pinned qualification revision:** `8b74bdec4ba2ef4e14795b7591df3b5d73f283e3`  
**Purpose:** Rules-based social simulation for socially aware characters.  
**Language:** JavaScript  
**License:** BSD-4-Clause, University of California-specific variant  
**Runnable evidence:** Standalone `ensemble.js`, authoring tool, `examples/loversAndRivals`, tests, release builds. EXP-001 executed the shipped Lovers and Rivals domain through native volition calculation, action selection, action execution, trigger processing, timestep advance, and subsequent action recalculation without an adapter or behavioral source modification.  
**Core mechanisms:** Social state schemas, character history, trigger rules, volition rules, action selection, relationship and social-fact reasoning.  
**Expected behavioral strengths:** History-dependent social differentiation, relationship-sensitive action preference, socially contextual action selection, authored social consequences.  
**Known or suspected weaknesses to test:** Heavy authoring burden, rule coverage limits, brittleness outside authored social domains, uncertain support for non-social motives and long-term habits.  
**Reuse note:** Permissive but includes an advertising acknowledgement clause. Preserve license text and verify distribution obligations before direct code reuse.  
**Priority:** 1. Strong whole-system candidate for Champion 0 because the target behavior is social individuality rather than generic problem solving. It is not yet Champion 0 because common-world adaptation and behavioral-battery evidence do not yet exist.

## PC-002: FAtiMA Toolkit

**Classification:** RUNNABLE BASELINE  
**Qualification state:** SOURCE VERIFIED, EXECUTION PENDING  
**Origin:** GAIPS / INESC-ID, continuation of FAtiMA architecture work beginning in 2005  
**Repository:** https://github.com/GAIPS/FAtiMA-Toolkit  
**Purpose:** Characters and robots with social and emotional intelligence.  
**Language:** C#  
**License:** Apache-2.0  
**Runnable evidence:** Solution files, applications, tests, tutorials, authoring tools, releases, Unity demo repository.  
**Core mechanisms:** Emotional appraisal, emotional state, emotion-influenced decision making, beliefs, social importance dynamics, role-play character loop, world model, goals, authoring tools.  
**Expected behavioral strengths:** Emotional continuity, differentiated social behavior, appraisal-driven decisions, explicit integration of beliefs and affect.  
**Known or suspected weaknesses to test:** Potentially author-heavy, emotion rules may become legible or mechanical, uncertain habit learning and prospective-memory behavior, framework breadth may hide which mechanisms carry behavioral value.  
**Reuse note:** Apache-2.0 permits modification and redistribution with notice obligations.  
**Priority:** 2. Strong whole-system baseline and likely donor for appraisal and social decision mechanisms.

## PC-003: PsychSim

**Classification:** RUNNABLE BASELINE  
**Qualification state:** SOURCE VERIFIED, EXECUTION PENDING  
**Origin:** USC Institute for Creative Technologies  
**Repository:** https://github.com/pynadath/psychsim  
**Purpose:** Social simulation with decision-theoretic agents and Theory of Mind.  
**Language:** Python  
**License:** MIT  
**Runnable evidence:** Installable package, documentation, domain scenarios including negotiation and wartime examples.  
**Core mechanisms:** Decision-theoretic action selection, explicit agent models, recursive social reasoning, beliefs over world and other agents, utility/reward models.  
**Expected behavioral strengths:** Prediction of other agents, socially contingent choices, explicit reasoning about differing beliefs and incentives.  
**Known or suspected weaknesses to test:** Rationality may look too clean, computational cost may rise with nested models, weak emotion/habit machinery, old examples may require modernization.  
**Reuse note:** MIT is highly permissive.  
**Priority:** 3. Critical baseline for Theory of Mind and social prediction, even if it does not win as the most lifelike whole character.

## PC-004: inBloom

**Classification:** RUNNABLE BASELINE  
**Qualification state:** SOURCE VERIFIED, EXECUTION PENDING  
**Origin:** University of Osnabrück computational storytelling research  
**Repository:** https://github.com/cartisan/inBloom  
**Purpose:** Computational storytelling using an affective extension of the Jason BDI architecture.  
**Language:** Java / AgentSpeak  
**License:** GPL-3.0  
**Runnable evidence:** Documented Java setup, `RedHenLauncher` example simulation, releases, Little Red Hen example story, research releases used for empirical work.  
**Core mechanisms:** BDI reasoning, Big Five personality, OCC emotions, mood, affect-sensitive plan selection, narrative semantics.  
**Expected behavioral strengths:** Personality-dependent behavior, affect-modulated plan choice, persistent affective context, goal-directed characters.  
**Known or suspected weaknesses to test:** Strong authoring dependence, narrative task bias, possible categorical affect effects, GPL license complicates direct incorporation into a permissively licensed synthesis.  
**Reuse note:** Safe for baseline comparison and study. Direct incorporation requires GPL-compatible distribution strategy or clean-room reimplementation of ideas that are not copyrightable expression.  
**Priority:** 4. Important experimental baseline and donor evidence for affective BDI, but license may favor mechanism study over direct code integration.

## PC-005: MicroPsi2

**Classification:** REQUIRES FURTHER INVESTIGATION  
**Qualification state:** SOURCE VERIFIED, EXECUTION PENDING  
**Origin:** Joscha Bach / micropsi industries  
**Repository:** https://github.com/joschabach/micropsi2  
**Purpose:** Toolkit implementing concepts from the MicroPsi cognitive architecture.  
**Language:** Python  
**License:** MIT unless marked otherwise  
**Runnable evidence:** Server entry point, run script, browser UI, tests, demo data, historical alpha releases. Documentation targets Python 3.4 and 3.5 and includes obsolete dependencies.  
**Core mechanisms:** Motivational dynamics, modulatory variables, node-net cognition, activation spreading, action selection concepts, world interfaces.  
**Expected behavioral strengths:** Competing motives, global cognitive modulation, non-language control dynamics, potentially useful persistence and activation mechanisms.  
**Known or suspected weaknesses to test:** Dependency age, uncertain direct fit to social human-character simulation, unclear baseline scenarios for longitudinal person-like behavior, performance was not an early project priority.  
**Reuse note:** MIT core is attractive, but dependency licenses must be checked individually.  
**Priority:** 5. Modernize only enough to execute the original behavior. Do not rewrite it into our preferred architecture before observing it.

## PC-006: GAMYGDALA

**Classification:** MECHANISM DONOR  
**Qualification state:** SOURCE VERIFIED, EXECUTION PENDING  
**Origin:** Joost Broekens, TU Delft  
**Repository:** https://github.com/broekens/gamygdala  
**Purpose:** Lightweight emotion engine for games.  
**Language:** JavaScript  
**License:** MIT  
**Runnable evidence:** Browser examples and small example games are included; the engine itself is independent of Phaser.  
**Core mechanisms:** Appraisal and emotion simulation for agents, including social emotion contexts.  
**Expected behavioral strengths:** Cheap affective response suitable for many agents, clear causal path from events to emotional state.  
**Known or suspected weaknesses to test:** Not a complete cognitive architecture, emotion without memory/motivation/action systems cannot establish whole-person continuity, risk of mechanical appraisal if used without richer state.  
**Reuse note:** MIT permits direct reuse if the mechanism wins a tournament.  
**Priority:** Donor tournament against FAtiMA and inBloom appraisal components after whole-system baselines are characterized.

## PC-007: openc2e / Creatures lineage

**Classification:** MECHANISM DONOR  
**Qualification state:** SOURCE VERIFIED, EXECUTION PENDING  
**Origin:** Open reimplementation of the Creatures artificial-life game engine  
**Repository:** https://github.com/openc2e/openc2e  
**Purpose:** Run the classic Creatures artificial-life games on modern systems.  
**Language:** C++  
**License:** LGPL-2.1  
**Runnable evidence:** Build instructions for Windows, macOS, and Linux. Current status reports working agents and creature biochemistry, while full creature support remains incomplete. Original game data is normally required.  
**Core mechanisms of interest:** Biochemistry, drives, neural action selection, learning, genome-driven variation, persistent organism state.  
**Expected behavioral strengths:** Old-school continuous organism simulation, body-state consequences, learned associations, behavior emerging from interacting low-level systems rather than a language model.  
**Known or suspected weaknesses to test:** Current engine incompleteness, dependency on proprietary game data for faithful full-system runs, animal-like rather than human-like social cognition.  
**Reuse note:** LGPL permits use with obligations. Distinguish openc2e implementation from proprietary Creatures data and original game assets.  
**Priority:** Historical donor track. Its organism mechanisms may be more valuable than its fitness as a whole human-character baseline.

## PC-008: Oz Project, Hap and Em

**Classification:** REQUIRES FURTHER INVESTIGATION  
**Qualification state:** DISCOVERED  
**Origin:** Carnegie Mellon Oz Project  
**Primary evidence:** https://www.cs.cmu.edu/Groups/oz/  
**Purpose:** Believable autonomous characters and interactive drama.  
**Language:** Historical research implementations; exact reusable source availability not yet established.  
**License:** Not established for reusable source.  
**Runnable evidence:** Historical demonstrations, theses, and reported simulations exist, but a currently obtainable runnable distribution has not yet been verified.  
**Core mechanisms:** Reactive behavior hierarchies, Hap behavior language, Em emotion architecture, personality-rich behavior, situated action, social behavior.  
**Expected behavioral strengths:** The project directly targeted the illusion of life and behaviorally expressed personality.  
**Known or suspected weaknesses to test:** Source availability and buildability may be poor; direct code reuse cannot proceed without license provenance.  
**Reuse note:** No code integration until source and rights are established. Papers remain conceptual evidence.  
**Priority:** High archaeology priority because the research objective aligns unusually closely with this project's target.

## PC-009: ABL / Façade lineage

**Classification:** REQUIRES FURTHER INVESTIGATION  
**Qualification state:** DISCOVERED  
**Origin:** Michael Mateas and Andrew Stern, derived from Hap  
**Purpose:** Reactive planning language for story-based believable agents with multi-character coordination.  
**Language:** Historical ABL implementation, commonly associated with Java tooling.  
**License:** Not established for a complete reusable implementation.  
**Runnable evidence:** Research papers and Façade demonstrate the architecture, but an authoritative reusable source distribution has not yet been verified.  
**Core mechanisms:** Sequential and parallel behaviors, joint goals, multi-agent coordination, reactive planning, meta-behaviors.  
**Expected behavioral strengths:** Continuous action, interruption, coordination, authored personality expression.  
**Known or suspected weaknesses to test:** High authoring effort, dramatic-domain assumptions, source/legal availability.  
**Reuse note:** Treat as conceptual evidence until code provenance is verified.  
**Priority:** Continue archaeology, especially for source releases, descendants, and cleanly licensed reimplementations.

## Baseline qualification order

The initial execution queue is Ensemble, FAtiMA Toolkit, PsychSim, inBloom, then MicroPsi2 if its historical environment can be reproduced without architectural rewriting. Ensemble has passed original execution only; it remains at the head of the adaptation and common-battery queue. GAMYGDALA and openc2e begin as donor tracks rather than complete-person contenders. Oz/Hap/Em and ABL remain archaeology targets until runnable source and licensing are established.

This order is provisional. A newly discovered system may move ahead if evidence indicates stronger whole-character behavior, better reproducibility, or a closer match to the target.
