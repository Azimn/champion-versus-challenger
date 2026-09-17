# EXP-011 development failure 1

Run: `35275519835`

Classification: **invalid evaluator assumption / termination-semantics error**.

The complete repository regression suite passed on Python 3.11 and 3.12. The EXP-011 evaluator then failed `activation_then_work_no_prospective_resurrection` because the harness assumed a single forced `work` action must completely resolve a cue-activated concern.

Observed state after one work action retained `work_me` in the ordinary concern ledger at approximately `0.414675`, while the prospective binding was correctly absent. This is consistent with the pre-existing concern semantics: work reduces the currently active concern incrementally and removes it only after the earned work-mediated resolution threshold is crossed.

No production change is justified. Correct the evaluator to distinguish:

1. prospective binding consumed on cue activation;
2. ordinary concern may remain unresolved after one work action;
3. repeated ordinary work can later resolve it;
4. repeated cue delivery after legitimate resolution must not resurrect it without a retained prospective binding.

The original failed workflow is preserved as evidence and must not be reinterpreted as an EXP-011 production failure.
