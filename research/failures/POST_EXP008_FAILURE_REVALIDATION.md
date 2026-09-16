# Post-EXP-008 Failure Queue Revalidation

## Authority

EXP-008 final decision: **REJECT**.

Frozen champion retained unchanged:

- `v9.1_compact`
- branch `champion-v9-1-compact`
- commit `2856ec6a32be0347a9243f6eff6faa404a9a0e6c`

Revalidation branch `post-exp008-failure-revalidation` was created directly from that commit. The workflow diff-checked the champion production files against the frozen commit and reran the v9.1 structural closeout before executing the queue.

Evidence:

- workflow run `35062450635`
- artifact `post-exp008-failure-revalidation`, artifact ID `10433140706`

## Result

All six remaining pre-EXP-008 failures are **still reproduced**. None was weakened, eliminated incidentally, changed form, or invalidated by newer semantics.

### Unfinished activity evaporates

Initial explicit concern `finish_portfolio` had strength `0.75`.

With only unrelated neutral events and no completion, cancellation, impossibility, or contradicting event, it disappeared after 74 events.

Classification: **still reproduced**.

### Rewarded routine never weakens

A rewarded morning walk reached contextual learned value `0.35`.

After 1000 unrelated events the value remained exactly `0.35`, and `walk` still won when the morning context returned.

Classification: **still reproduced**.

### Ancient commitment reactivates unchanged

`call_morgan -> morgan_arrives` remained intact through 1000 unrelated events. At tick 1001 the cue still activated `call_morgan` at concern strength `0.75`.

Classification: **still reproduced**.

### Third commitment is forgotten

With prospective capacity two, adding `first`, `second`, then `third` left only `second` and `third`. Later `cue_first` produced no active concern.

Classification: **still reproduced**.

### Suppressed concern never returns

`low_priority` was displaced when two stronger concerns arrived. After both stronger concerns were explicitly cancelled, the weaker unfinished concern did not return.

Classification: **still reproduced**.

### Deterministic rhythm

Under a constant neutral environment the final 60 actions repeated the exact six-step sequence:

`rest, work, idle, rest, idle, idle`

Exact matching periods at or below 20 were 6, 12, and 18.

Classification: **still reproduced**.

## Next-failure selection

The strongest next target is **unfinished activity evaporates**.

Selection basis:

- **Perceptual importance:** disappearance of an explicitly unfinished obligation without any resolving event is directly observable as loss of personal continuity.
- **Longitudinal significance:** it occurs only over extended interaction, exactly where a persistent artificial individual should differ from a reactive agent.
- **Reproducibility:** deterministic disappearance at 74 unrelated events from an initial strength of `0.75` under the frozen champion.
- **Causal localization:** the concern exists in the authoritative ledger and is removed by the ledger's unconditional per-tick decay threshold.
- **Continuing-individual discrimination:** an ongoing individual can become less activated by an obligation without the obligation ceasing to exist. The current organism conflates these conditions.

The capacity failures are also serious but are partly explicit bounded-memory tradeoffs. Deterministic rhythm is obvious but less tightly localized. Non-decaying habit and prospective state expose long-term forgetting questions but do not erase an explicitly active unfinished task. The unfinished-activity failure therefore provides the cleanest next empirical target.

## Existing-mechanism interaction hypothesis before archaeology

No new mechanism is yet justified.

The current concern representation already provides:

- persistent concern identity;
- a strength used for prioritization;
- explicit cancellation;
- action-mediated progress/removal through `work`;
- bounded competition/capacity.

The failure arises because `ConcernLedgerCharacter._drift()` multiplies every concern strength by `0.97` every tick and deletes a concern below `0.08`, regardless of whether any completion or cancellation evidence occurred.

This means one stored scalar currently carries two logically different meanings:

1. current activation/priority strength;
2. continued existence of an unfinished obligation.

A first investigation should therefore ask whether existing concern identity plus existing explicit resolution signals can interact more coherently, for example by allowing activation to weaken without silently treating low activation as completion/forgetting.

This is only a causal hypothesis for EXP-009 characterization. No production change has been made and no new persistent field is proposed at this stage.
