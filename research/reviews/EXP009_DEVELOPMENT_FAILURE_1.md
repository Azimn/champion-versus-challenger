# EXP-009 development failure 1

## Preserved evidence

Workflow run: `35136991980`

Production challenger commit under test: `b5cc3e109ab2fa4de0421dc113009d1ee7fb050d`

The workflow verified that frozen v9.1 production files were unchanged before testing.

## Failure

The repository test suite stopped in `tests/test_exp009.py` while constructing the development report.

The failing path was `legitimate_termination()` -> `assign(third_weaker, "weak_c", 0.1)`.

`assign()` performed the `task_assign` event and then unconditionally indexed `agent.concerns[name]`. Because the concern store was already at capacity two with two stronger concerns, the existing `_bound_concerns()` rule immediately and correctly evicted `weak_c`. The helper then raised `KeyError: 'weak_c'` before the test could inspect the capacity result.

## Classification

**implementation defect in the development harness**

This is not evidence against the challenger. The observed runtime behavior is the behavior the capacity test intended to verify: a newly arriving weaker third concern does not displace two stronger concerns under the frozen capacity-two policy.

## Correction rule

Do not modify production. Correct only the development harness so the weaker-third diagnostic emits the assignment event without assuming the new concern survives capacity enforcement. Replay the full repository suite and EXP-009 evaluation afterward.

This failure remains part of the methodological record and is not deleted or reinterpreted as a passing run.
