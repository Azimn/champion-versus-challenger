# EXP-007 Outcome Addendum

The original `EXP007_DELAYED_CREDIT.md` remains the preregistration and is intentionally not rewritten after observing results.

**Final decision:** PROMOTE  
**Promoted version:** `v9_context_eligibility_trace`  
**Frozen production-behavior commit:** `8c1e692e2b115200e3d758e481eb12576aced907`  
**Strict closeout CI run:** `35025493280`  
**Closeout artifact ID:** `10419755673`

The preregistered four-field representation was not promoted. EXP-007's empirical trajectory instead produced a smaller final mechanism:

- `context`
- `action`
- `age`
- capacity: 2 records
- lifetime: age 0 through 10
- eligibility: deterministic derived value `0.82 ** age`

The full historical trajectory, reviewer rejection, corrections, structural ablations, invalidated test assumptions, cost measurements, causal evidence, narrowed claim, and claims not established are preserved in:

- `research/results/EXP007_DELAYED_CREDIT_FINAL.md`
- `research/results/EXP007_DELAYED_CREDIT_FINAL.json`

This addendum exists specifically so that the preregistration can remain historical evidence rather than being edited to resemble the final implementation.
