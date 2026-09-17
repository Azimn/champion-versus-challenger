# PEMA Causal Experiment Sequence

This series extends PR 14 without attempting to build the complete PEMA architecture. Each stage adds exactly one causal link and retains an explicit ablation.

## Experiment 1: scarcity changes realized information access

The existing metabolic information-asymmetry experiment is the baseline. It showed that a route can be topologically legal yet fail because communication is unaffordable. Under the canonical six-unit condition, global broadcast loses E3 while differential routing can still finance its permitted E3 routes.

Observed link:

`resource scarcity -> realized information access`

## Experiment 2: local knowledge changes resource demand

The birthday scenario is reduced to one scarce allocation round after E1 and E3 have produced the existing local histories. Each processor proposes one inspectable operation. Priority is derived only from that processor's local evidence.

Under global access, SOCIAL has both E1 and E3 and detects that B's preference changed. Its SEND_RECOMMENDATION operation receives priority 0.95 and wins the one-unit allocation.

Under differential access, SOCIAL still has only E1 and receives priority 0.60. MEMORY has both E1 and E3, detects temporal conflict, receives priority 0.85, and wins instead.

Observed link:

`local knowledge -> operation priority -> allocation winner`

The action-selection policy is unchanged across conditions. Global access produces `SURPRISE_B`; differential access surfaces conflicting history and produces `ASK_B_FIRST`.

This experiment is intentionally small. It does not yet model strategic bidding, reserve staking, multiple resources, or learned demand functions.

## Experiment 3: history changes future competitiveness

A persistent CONCERN receives one unresolved event. During six quiet ticks there are no reminders. The unresolved process can bank a bounded fraction of otherwise unused quiet capacity, reaching a reserve of 1.5.

At tick 7, a later context matches the unresolved concern. The concern and a strong current distractor compete for one unit.

With accumulated history, the concern's bounded reserve contribution raises its priority above the distractor and it wins RECRUIT_MEMORY, causing `E1_UNRESOLVED` to return.

In the no-history ablation, the exact same later context occurs but reserve remains zero. The distractor wins and no old event is recalled.

Observed link:

`persistent history -> stored reserve -> later competitiveness`

The effect does not use an explicit reminder callback.

## Experiment 4: allocation changes future knowledge

EXPLORATION and ROUTINE compete for one processing unit over six ticks. Their demand is local:

`priority = 0.50 + 0.08 * local_evidence - 0.06 * consecutive_wins`

The consecutive-win term supplies endogenous utilization fatigue.

EXPLORATION starts with one relevant cue. If feedback is enabled, whichever process wins the scarce processing resource discovers one additional item from its own relevant channel. That new local evidence raises its future demand.

With feedback enabled, EXPLORATION wins all six rounds and grows from one to seven evidence items. The information gained from one allocation is sufficient to offset the accumulating fatigue term and preserve competitiveness.

In the no-feedback ablation, winning does not reveal new evidence. Fatigue breaks EXPLORATION's initial dominance and the allocation sequence becomes:

`EXPLORATION, EXPLORATION, ROUTINE, EXPLORATION, EXPLORATION, ROUTINE`

Observed link:

`allocation -> new local knowledge -> stronger future demand -> later allocation`

This closes the minimal resource-epistemic feedback loop.

## Combined causal chain

The four experiments now separately exercise:

`scarcity -> information access`

`information -> demand`

`history -> competitiveness`

`allocation -> future information`

Together these form the smallest tested version of the proposed loop:

`local information -> valuation/demand -> resource allocation -> processing/information acquisition -> changed local information`

## Important limitation

These are constructed mechanism tests, not evidence that a full artificial organism will spontaneously produce personality, rumination, or lifelike cognition. Experiments 2 through 4 intentionally use transparent hand-specified local priority equations so the causal links can be falsified directly. The next question is whether the links survive when combined in one shared runtime rather than tested separately.

## Run

The repository-wide test suite executes all four experiments through `tests/test_pema_sequence.py`. The PEMA sequence is deterministic and is tested alongside the original information-asymmetry and metabolic experiments on Python 3.11 and 3.12.
