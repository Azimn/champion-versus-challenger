# EXP-009 reviewer generation 1 failure and classification

## Preserved evidence

Workflow run: `35137413998`

Artifact: `10463856104`

Frozen production implementation under review: `b5cc3e109ab2fa4de0421dc113009d1ee7fb050d`

The workflow verified the production file was unchanged from that commit before executing reviewer generation 1.

## Raw result

Reviewer generation 1: **14 / 15 probes passed**.

Only failed probe: `reassignment_after_dormancy`.

Observed trace:

- concern remained present after 10,000 unrelated ticks;
- activation before reassignment: approximately `3.912045756967751e-133`;
- reassignment used intensity `0.6`;
- resulting activation: `0.44999999999999996`;
- ledger contained exactly one `return_to_it` entry.

The reviewer asserted exact equality with decimal `0.45` and therefore reported failure.

## Classification

**numerical artifact / invalid reviewer assumption**

The runtime uses IEEE-754 binary floating-point values. `0.75 * 0.6` is represented as `0.44999999999999996` on the tested Python runtime. The behavior relevant to the hypothesis is that reassignment raises an extremely weak unresolved concern to the ordinary assignment activation, without duplicating concern identity. That behavior occurred.

This failure does not attack:

- concern persistence semantics;
- cancellation;
- work-mediated resolution;
- bounded capacity;
- action selection;
- serialization;
- hidden persistent state;
- or the zero-new-state hypothesis.

## Methodological treatment

The original reviewer file is retained unchanged and its failing run remains part of the record.

Production will not be modified for this failure.

A separate adjudication may verify the intended numeric relation with a floating-point tolerance while also requiring all other reviewer probes to remain passing. The raw reviewer result must continue to be reported as 14/15 with one classified invalid exact-float assertion.
