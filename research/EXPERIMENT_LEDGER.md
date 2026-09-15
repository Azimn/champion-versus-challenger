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
**Regressions:** No regressions were found in previously earned targeted probes. Both Python 3.11 and 3.12 CI test jobs passed.  
**Artificiality attack findings:** v5 remains intentionally incomplete. Confirmed or obvious next attack surfaces include multiple simultaneous motives, prospective deadlines, false-belief persistence, differentiated forgetting, habit reversal, multi-step spontaneous activity, and richer social models beyond scalar reliability.  
**Causal diagnosis:** Each improvement disappears in the immediately preceding champion, which functions as the ablation condition for the newly added mechanism.  
**Ablation result:** All five added mechanisms demonstrated causal value on their targeted probe under the current battery.  
**Human-observer result, if applicable:** Not run.  
**Decision:** promote `v5_partner_model` as the branch-local experimental champion for the next artificiality attack. Do not treat it as proof of complete lifelikeness or as the project's global Champion 0.  
**Reason:** The branch achieved five independently targeted longitudinal gains with one counted mechanism added per cycle, no detected regression in prior probes, preserved cognition/surface separation, and modest measured runtime/state growth.  
**Follow-up:** Attack v5 with a discriminating false-belief or prospective-memory scenario before adding another mechanism. Compare a minimal belief-state or deadline mechanism against stronger donors such as PsychSim or BDI systems only if the failure is reproduced.

## Evidence policy

Architectural descriptions, paper claims, screenshots, videos, and developer statements can justify investigation but cannot by themselves justify promotion. Promotion evidence must ultimately be tied to preserved traces from controlled scenarios.

If a result cannot be reproduced from a recorded version, adapter, scenario, seed where applicable, and trace, treat it as anecdotal rather than experimental evidence.
