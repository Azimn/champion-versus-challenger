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

## Evidence policy

Architectural descriptions, paper claims, screenshots, videos, and developer statements can justify investigation but cannot by themselves justify promotion. Promotion evidence must ultimately be tied to preserved traces from controlled scenarios.

If a result cannot be reproduced from a recorded version, adapter, scenario, seed where applicable, and trace, treat it as anecdotal rather than experimental evidence.
