# PEMA Causal Sequence Results

## Overall result

The four staged experiments each produced the expected causal effect under deterministic tests.

| Experiment | Tested link | Result |
|---|---|---|
| 1 | Scarcity -> realized information access | observed |
| 2 | Local knowledge -> demand/allocation | observed |
| 3 | Persistent history -> later competitiveness | observed |
| 4 | Allocation -> new knowledge -> future demand | observed |

This is evidence that the proposed links can coexist conceptually as a causal chain. It is not yet evidence that the complete chain will remain stable or interesting when all links operate simultaneously in one shared runtime.

## Experiment 1

PR 14's metabolic extension remains the baseline result. Communication scarcity changes the topology actually realized during execution. At six units, global PERCEPTION cannot finance both four-recipient broadcasts, while differential routing can finance its two-recipient E1 route and three-recipient E3 route.

Global broadcast changes from `SURPRISE_B` under abundance to `ASK_B_FIRST` under scarcity. Differential access remains `ASK_B_FIRST`.

The capacity sweep establishes the relevant thresholds at 5 units for differential E3 delivery and 8 units for global E3 delivery.

## Experiment 2

With one unit available for the decision-stage cognitive operation, locally generated priorities change the winner.

Global access:

- SOCIAL knows E1 and E3.
- SOCIAL detects a changed preference.
- SOCIAL priority = 0.95.
- MEMORY priority = 0.85.
- SOCIAL wins.
- SOCIAL emits `SURPRISE_B`.
- ACTION selects `SURPRISE_B`.

Differential access:

- SOCIAL knows only E1.
- SOCIAL priority = 0.60.
- MEMORY knows E1 and E3 and detects temporal conflict.
- MEMORY priority = 0.85.
- MEMORY wins.
- conflicting history is surfaced.
- ACTION selects `ASK_B_FIRST`.

The allocator therefore responds to private epistemic state rather than a globally assigned importance value.

In the uniform-priority ablation, every operation receives 0.50 and both access conditions use the same deterministic tie context. The same actor wins in both runs. Removing epistemically derived priority therefore removes the knowledge-dependent allocation difference.

This does not establish that the particular priority equation is psychologically correct. The priority values are deliberately hand specified to test the causal link itself.

## Experiment 3

The concern condition banks 0.25 units of otherwise unused quiet capacity for six ticks, capped at 1.5. There are no external reminders during those ticks.

At the later matching context:

- with history, CONCERN priority is approximately 0.726 and defeats the 0.70 distractor;
- without history, CONCERN priority is 0.50 and loses to the same distractor.

Only the history condition recalls `E1_UNRESOLVED`.

This demonstrates that stored metabolic history can change later competition without an explicit reminder callback.

It does not yet demonstrate spontaneous concern formation. The concern's existence and reserve rule are supplied by the experiment.

## Experiment 4

Both actors use:

`priority = 0.50 + 0.08 * local_evidence - 0.06 * consecutive_wins`

EXPLORATION begins with one local cue. ROUTINE begins with zero.

### Feedback condition

Each allocation permits the winner to sample its relevant channel and acquire one new item of evidence.

EXPLORATION wins all six allocations:

`E, E, E, E, E, E`

Its evidence count grows from 1 to 7. The evidence term increases fast enough to offset the utilization-fatigue term.

### No-feedback ablation

Winning does not reveal additional evidence.

Allocation becomes:

`E, E, R, E, E, R`

EXPLORATION wins four times and ROUTINE wins twice. Fatigue therefore breaks the initial dominance when allocation is disconnected from information acquisition.

The difference isolates the positive feedback path:

`allocation -> evidence -> future demand -> allocation`

## What These Four Experiments Actually Demonstrated

The sequence establishes four existence proofs in the current toy architecture.

First, computation cost can alter which information actually reaches a processor even when a hard route exists.

Second, different private information can alter actor-generated resource demand and therefore determine which cognitive operation executes.

Third, accumulated metabolic history can make an inactive unresolved process more competitive later without scheduling a direct reminder.

Fourth, when winning resources reveals information relevant to the winning process, that new information can increase future demand strongly enough to alter later allocation. This closes the minimal feedback loop proposed by the resource-economy design.

## What It Did Not Demonstrate

The experiments are intentionally constructed and separated. They do not show that the combined runtime will automatically generate lifelike behavior, personality, rumination, curiosity, mood, selfhood, or consciousness.

Experiment 2 uses explicit priority equations rather than learned valuation. Experiment 3 supplies a concern and a reserve-accumulation rule. Experiment 4 supplies actor-specific evidence channels. These are mechanisms being tested, not emergent discoveries.

The strongest unresolved question is now interaction rather than component existence:

> What happens when all four causal links operate simultaneously, continuously, and compete through the same resource ledger?

That should be the next experiment before adding multiple currencies, vector process fields, long-term learning, coalitions, or an LLM.
