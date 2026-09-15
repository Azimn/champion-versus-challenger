# Experiment Ledger

Every experiment receives a permanent record, including failures. Results must distinguish observed behavior from interpretation.

## Required experiment record

**Experiment ID:**  
**Date:**  
**Stage:**  
**Question:**  
**Target behavioral phenomenon:**  
**Champion:**  
**Challenger:**  
**Candidate systems/mechanisms:**  
**Repository refs/versions:**  
**Scenario IDs:**  
**Seeds:**  
**World-state equivalence controls:**  
**History equivalence controls:**  
**Adapter versions:**  
**Hypothesis:**  
**Predicted behavioral difference:**  
**Primary measures:**  
**Secondary measures:**  
**Performance measures:** tick time, memory, persistent-storage growth, scaling  
**Raw trace locations:**  
**Observed behavior:**  
**Paired differences:**  
**Regressions:**  
**Artificiality attack findings:**  
**Causal diagnosis:**  
**Ablation result:**  
**Human-observer result, if applicable:**  
**Decision:** promote, reject, mixed, or no-decision  
**Reason:**  
**Follow-up:**  

## EXP-000: Protocol reset and archaeology-first initialization

**Date:** 2026-09-15  
**Stage:** A  
**Question:** Is there an existing project implementation in this repository that should serve as the initial champion?  
**Champion:** None  
**Challenger:** None  
**Observed behavior:** The repository contained only a one-line README before this protocol reset. There was no implementation to preserve, execute, or compare.  
**Decision:** no-decision  
**Reason:** Champion 0 must be earned by an external or later internal system through common baseline qualification. The project must not manufacture an internal champion merely to populate the lineage.  
**Follow-up:** Execute the baseline qualification queue beginning with Ensemble, then FAtiMA Toolkit and PsychSim unless new archaeology reveals a stronger practical complete system.

## EXP-001: Ensemble original-domain execution qualification

**Date:** 2026-09-15  
**Stage:** B  
**Question:** Can the pinned original Ensemble Lovers and Rivals domain be executed through a meaningful native state transition on a modern host without changing Ensemble's social reasoning architecture?  
**Target behavioral phenomenon:** Baseline executability and native social action/state transition only. This experiment does not test comparative lifelikeness.  
**Champion:** None  
**Challenger:** None  
**Candidate systems/mechanisms:** PC-001 Ensemble. MC-001 remains unverified because this smoke execution does not isolate causal contribution.  
**Repository refs/versions:** Ensemble commit `8b74bdec4ba2ef4e14795b7591df3b5d73f283e3`; shipped artifact `examples/loversAndRivals/ensemble.js`; research workflow run `34939796873`.  
**Scenario IDs:** None. This is original-domain qualification prior to the common behavioral battery.  
**Seeds:** Not applicable to the observed smoke path.  
**World-state equivalence controls:** Not applicable.  
**History equivalence controls:** Original shipped Lovers and Rivals history was preserved.  
**Adapter versions:** None. `adapter_used=false`.  
**Hypothesis:** The original shipped domain can run headlessly with environment-only compatibility handling and can advance through its native social action, trigger, timestep, and subsequent action-calculation path.  
**Predicted behavioral difference:** None. This is an execution gate, not a champion-versus-challenger comparison.  
**Primary measures:** Successful loading of original schema, cast, trigger rules, volition rules, actions, and history; native volition/action calculation; one native action execution; trigger processing; timestep advance; successful recalculation after the state transition.  
**Secondary measures:** Native action counts and post-transition social-state query.  
**Performance measures:** Not yet measured.  
**Raw trace locations:** GitHub Actions run `34939796873`; uploaded artifact `ensemble-original-domain-smoke`, artifact ID `10384588014`.  
**Observed behavior:** The pinned shipped domain executed successfully on Node 20.20.2 under Ubuntu 24.04. The cast was `hero`, `love`, and `rival`. Before the exercised transition, Ensemble returned two candidate actions from hero to love, zero from love to hero, and zero from hero to rival. The selected native action was `writeLoveNoteReject`, display name `Write Love Note <REJECT>`, weight 20. Ensemble executed the action, ran trigger rules, advanced the timestep, and successfully recalculated two hero-to-love actions. The queried hero-to-love closeness fact had value 10 at time 0.  
**Compatibility findings:** The first headless attempt showed that the browser-oriented bundle expects Underscore as global `_`. An external host shim supplied that symbol without changing Ensemble logic. A later attempt to regenerate the standalone bundle exposed an upstream historical build-script race: `build-library.js` combines synchronous initialization with asynchronous module appends, which can reorder modules on a modern host. The qualification therefore uses the fixed standalone bundle already shipped with Lovers and Rivals instead of modifying or repairing candidate source. One intermediate smoke assertion also incorrectly treated the absence of a love-to-hero action as an execution failure; the harness was corrected so absence of a native action is recorded as behavior rather than judged as a software defect.  
**Paired differences:** Not applicable.  
**Regressions:** None assessed.  
**Artificiality attack findings:** Not yet run.  
**Causal diagnosis:** Not applicable.  
**Ablation result:** Not applicable.  
**Human-observer result, if applicable:** Not run.  
**Decision:** no-decision on Champion 0; advance PC-001 qualification state to `EXECUTED`.  
**Reason:** The original system has now been observed performing a meaningful native state transition without an adapter or behavioral patch, satisfying the original-execution gate. It has not yet been adapted to the common world or run through the behavioral battery, so there is no evidence for champion promotion.  
**Follow-up:** Build the thinnest defensible Ensemble adapter and run its high-priority social scenarios B01, B02, B14, B15, B18, B19, and B20 while preserving native actions and state traces.

## EXP-002: Minimal non-LLM lifelikeness mechanism loop, Run 001

**Date:** 2026-09-15  
**Stage:** D through I, branch-local mechanism tournament and causal-ablation loop  
**Question:** Can common longitudinal artificiality failures be removed one at a time by adding the smallest donor-derived non-LLM mechanism that produces a causal behavioral difference, while preserving previous gains and keeping cost low?  
**Target behavioral phenomena:** History divergence, recovery inertia, unfinished concern persistence, experience-shaped habit formation, and first-order social prediction.  
**Champion:** Branch-local initial champion `v0_reactive`. This does not replace the project's global external-baseline Champion 0 decision process.  
**Challengers:** `v1_relationship`, `v2_affect`, `v3_concern`, `v4_habit`, `v5_partner_model`.  
**Candidate systems/mechanisms:** Ensemble / Comme il Faut social history, FAtiMA and GAMYGDALA affect persistence, BDI intention commitment, reinforcement-shaped habits with The Sims and artificial-life precedent, and PsychSim-style explicit partner modeling reduced to a first-order reliability estimate.  
**Repository refs/versions:** Branch `minimal-lifelike-loop`, PR #8. Donor repositories and licensing boundaries are recorded in `research/DONOR_PROVENANCE.md`.  
**Scenario IDs:** Branch-local targeted probes `history_divergence`, `recovery_inertia`, `unfinished_concern`, `habit_formation`, and `social_prediction`, plus one falsification probe per cycle and a surface-invariance test.  
**Seeds:** Deterministic. No random action selection is used in the current experiment.  
**World-state equivalence controls:** Each champion/challenger pair receives the same event sequence and available actions for the targeted comparison.  
**History equivalence controls:** Each pair receives identical supportive, hostile, shock, task, reinforcement, or partner-observation histories as appropriate.  
**Adapter versions:** None. These are clean minimal functional analogues, not adapters around donor implementations.  
**Hypothesis:** Small persistent state variables can remove specific artificiality failures without importing complete donor architectures.  
**Predicted behavioral difference:** Each challenger should pass exactly one new targeted longitudinal probe, preserve all previously passed probes, remain invariant to optional language rendering, and survive an adversarial reviewer probe aimed at leakage or pathological persistence.  
**Primary measures:** Target-probe pass/fail, prior-probe regression, reviewer falsification result, and surface invariance.  
**Secondary measures:** Mechanism count and representative persistent-state size.  
**Performance measures:** Median microseconds per tick on GitHub Actions and serialized representative state size.  
**Raw trace locations:** GitHub Actions run `34990051759`; artifact `minimal-lifelike-loop-results`, artifact ID `10404648308`; permanent summary `research/results/MINIMAL_LIFELIKE_RUN_001.md`.  
**Observed behavior:** Five consecutive challengers were promoted. v1 changed hostile-history behavior from `socialize:Alex` to `avoid:Alex` while preserving social behavior toward unrelated Blake. v2 produced temporary post-shock avoidance that decayed back to idle. v3 returned to an unfinished task after an interruption but dropped the concern after explicit cancellation. v4 learned a rewarded morning walk without applying the routine in the evening. v5 delegated to an actor observed to be reliable, verified an actor observed to be unreliable, did not transfer Alex's model to Blake, and revised Alex after contradictory evidence.  
**Paired differences:** Behavioral-probe coverage increased monotonically from 0/5 at v0 to 5/5 at v5. Counted mechanisms increased from 3 to 8. The final report measured approximately 12.23 microseconds per tick for v0 and 15.82 microseconds per tick for v5. Representative serialized persistent state increased from 81 to 320 bytes.  
**Regressions:** No regressions were found in previously earned targeted probes under the EXP-002 battery. Both Python 3.11 and 3.12 CI test jobs passed.  
**Artificiality attack findings:** v5 remains intentionally incomplete. Confirmed or obvious next attack surfaces include multiple simultaneous motives, prospective deadlines, false-belief persistence, differentiated forgetting, habit reversal, multi-step spontaneous activity, and richer social models beyond scalar reliability.  
**Causal diagnosis:** Each improvement disappears in the immediately preceding champion, which functions as the ablation condition for the newly added mechanism.  
**Ablation result:** All five added mechanisms demonstrated causal value on their targeted probe under the EXP-002 battery. EXP-003 later found that one reviewer claim about unknown-partner behavior was brittle under action reordering. The original record is preserved here rather than silently rewritten.  
**Human-observer result, if applicable:** Not run.  
**Decision:** promote `v5_partner_model` as the branch-local experimental champion for the next artificiality attack, subject to later adversarial falsification.  
**Reason:** The branch achieved five independently targeted longitudinal gains with one counted mechanism added per cycle, no detected regression in prior probes, preserved cognition/surface separation, and modest measured runtime/state growth.  
**Follow-up:** Continue adversarial attacks before assuming each earned behavior is robust.

## EXP-003: Adversarial audit and uncertainty policy correction

**Date:** 2026-09-15  
**Stage:** G through I, adversarial attack, causal diagnosis, minimal challenger, falsification, promotion  
**Question:** Which previously untested longitudinal or adversarial condition most strongly breaks `v5_partner_model`, and can the highest-priority failure be corrected without adding a new cognitive subsystem?  
**Target behavioral phenomenon:** Robust partner-specific prediction under uncertainty and action reordering.  
**Champion:** Frozen `v5_partner_model` from EXP-002 commit `3faa41a7e13d4dba755b4a10baa95ce57ba169ed`.  
**Challenger:** `v5_1_uncertainty_policy`, implemented as `UncertaintyPolicyCharacter`.  
**Candidate systems/mechanisms:** Existing v5 scalar partner reliability generalized with an explicit uncertainty policy. Internal donors inspected first: `Azimn/DUCK` motivated cognition, planning, and expectation ledger; `Azimn/TinyPersonaEngine` lightweight beliefs, goals, attention, and action pressures. External comparison points: Beta Reputation System and PsychSim uncertainty over other-agent models.  
**Repository refs/versions:** Branch `exp003-adversarial-audit`, PR #9. Donor boundaries are recorded in `research/DONOR_PROVENANCE.md`.  
**Scenario IDs:** EXP-003 audit probes for multiple unfinished concerns, long-delay commitment, relationship repair, habit reversal, and partner-specific prediction; matched order-invariance target; reviewer probes for known evidence, contradictory evidence reversal, near-neutral evidence, person specificity, prior earned behavior, and renderer invariance.  
**Seeds:** Deterministic.  
**World-state equivalence controls:** Champion and challenger receive identical histories, action alternatives, action-order permutations, and renderer conditions.  
**History equivalence controls:** Partner evidence histories are identical for each paired comparison.  
**Adapter versions:** None.  
**Hypothesis:** The persistent representation is already sufficient for the observed failure. Near-zero reliability evidence needs an explicit conservative uncertainty policy so behavior is not determined by action ordering.  
**Predicted behavioral difference:** An unseen or near-neutral partner should be verified regardless of whether `verify` or `delegate` appears first. Strong positive evidence should still cause delegation and strong negative evidence should still cause verification.  
**Primary measures:** Order-invariance target, preservation of all five EXP-002 target behaviors, four adversarial reviewer families, renderer invariance.  
**Secondary measures:** Counted mechanism delta and serialized persistent-state delta.  
**Performance measures:** Matched median microseconds per tick, mechanism count, serialized representative persistent state.  
**Raw trace locations:** Initial frozen-champion audit run `35012684583`, artifact `10413988647`; matched challenger run `35013090805`, artifact `exp003-results`, artifact ID `10414372707`; permanent summary `research/results/EXP003_UNCERTAINTY_POLICY.md`.  
**Observed behavior:** The initial audit found three failures: multiple concerns overwrite one another, a long-delay commitment decays away without completion or cancellation, and unknown-partner prediction was action-order dependent. Relationship repair and habit reversal passed. The social-prediction failure was prioritized because it falsified part of the EXP-002 reviewer evidence. Frozen v5 chose `verify:Blake` when verification was listed first and `delegate:Blake` when delegation was listed first. The challenger chose `verify:Blake` under both orderings. It continued to delegate to a reliably observed Alex and verify an unreliably observed Alex under both orderings. Contradictory evidence reversed Alex from delegation to verification. Near-neutral evidence remained conservative. Alex evidence did not transfer to Blake.  
**Paired differences:** Target changed from fail to pass. All five previously earned target behaviors and renderer invariance passed. Counted mechanisms remained 8. Representative persistent state remained 325 bytes in the matched benchmark.  
**Regressions:** None detected.  
**Artificiality attack findings:** Two confirmed high-impact failures remain after the correction: only one unfinished concern can exist, and a future commitment can disappear solely through time-based concern decay.  
**Causal diagnosis:** The v5 partner model represented observed reliability but assigned equal utility to delegation and verification at zero reliability. Deterministic tie-breaking therefore leaked action ordering into behavior.  
**Ablation result:** Frozen v5 is the causal ablation. It has identical persistent partner state but lacks the uncertainty premium and fails the target.  
**Human-observer result, if applicable:** Not run.  
**Decision:** promote `v5_1_uncertainty_policy` as the next branch-local champion.  
**Reason:** The challenger repairs a falsified earned behavior with no new persistent state, no new counted mechanism, no detected regression, and no runtime-cost regression. The matched CI sample measured 8.8102 microseconds per tick for v5 and 8.0190 for v5.1; this timing difference is treated as CI variance rather than a speed claim.  
**Follow-up:** Freeze v5.1 and attack the reproduced multiple-unfinished-concerns failure with the smallest bounded concern representation. Do not import DUCK's full motive or planning architecture unless a smaller ledger fails.

## Evidence policy

Architectural descriptions, paper claims, screenshots, videos, and developer statements can justify investigation but cannot by themselves justify promotion. Promotion evidence must ultimately be tied to preserved traces from controlled scenarios.

If a result cannot be reproduced from a recorded version, adapter, scenario, seed where applicable, and trace, treat it as anecdotal rather than experimental evidence.
