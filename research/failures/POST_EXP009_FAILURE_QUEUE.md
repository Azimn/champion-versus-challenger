# Post-EXP-009 Longitudinal Failure Queue

Frozen promoted champion: `v9.2_unresolved_concern_persistence`.

Frozen champion branch: `champion-v9-2-unresolved-concern-persistence`.

Frozen champion commit: `bd1ca22ca58e82012f1a8237e3de4bfee4dbf59d`.

Evaluated production file frozen since: `b5cc3e109ab2fa4de0421dc113009d1ee7fb050d`.

Audit branch: `post-v9-2-failure-revalidation`.

Audit commit with the exact original v9.1 failure-discovery blob attached: `8c03d5a2fcd72b255a15a9287dd48ad0aa716746`.

Workflow run: `35138838058`.

Artifact: `10464207788`.

The original failure-discovery source was attached byte-for-byte from blob `e153ad052e7033f802ed3b85d9781df31a48761b`; the reproduction functions themselves were not rewritten for v9.2.

## Revalidation

| Failure | v9.2 result | Classification |
| --- | --- | --- |
| `unfinished_activity_evaporates` | no longer reproduced; `finish_portfolio` remains in the ledger after the unchanged 120-event reproduction at activation about `0.019394` | eliminated by target correction |
| `rewarded_routine_never_weakens` | learned morning-walk value remains exactly `0.35` after 1,000 unrelated events and walk still wins on return | still reproduced |
| `ancient_commitment_reactivates_unchanged` | commitment remains latent through 1,000 unrelated events and returns at concern activation `0.75` when cue occurs | still reproduced |
| `third_commitment_is_forgotten` | third commitment leaves only `second` and `third`; later `cue_first` produces no concern | still reproduced |
| `suppressed_concern_never_returns` | `low_priority` is removed when two stronger concerns arrive and does not return after both stronger concerns are cancelled | still reproduced |
| `deterministic_rhythm` | final 60 actions retain exact period 6, with periods 6, 12, and 18 detected | still reproduced |

## EXP-009 secondary-consequence check

`suppressed_concern_never_returns` is **unchanged**. EXP-009 did not incidentally fix it.

That result narrows the new primitive. Low activation no longer means deletion, but capacity eviction still means deletion because the evicted concern has no surviving representation.

## Brief architectural interpretation

The surviving failures cluster into three analytic groups rather than five obvious new modules:

1. **Persistence and loss semantics**
   - rewarded routine history versus current utility;
   - ancient prospective existence versus current relevance;
   - suppressed concern versus capacity deletion;
   - third prospective commitment versus capacity deletion.
2. **Capacity loss versus resolution**
   - both `suppressed_concern_never_returns` and `third_commitment_is_forgotten` erase identity because a bounded store is full, not because the represented matter was resolved.
3. **Behavioral dynamics**
   - deterministic rhythm is distinct from the persistence failures and concerns endogenous action dynamics rather than retention semantics.

EXP-009 therefore supports a more precise minimality question: whether the runtime is conflating an item being outside the current bounded competitive set with the item no longer existing.

## Next selected failure

Selected for EXP-010 characterization: `suppressed_concern_never_returns`.

Selection rationale:

- high longitudinal importance: unfinished business vanishes during temporary competition;
- direct perceptual consequence: after urgent matters resolve, the individual behaves as if the earlier unfinished demand never existed;
- deterministic reproduction;
- clean localization to the concern store's capacity rule;
- directly tests suppression-versus-deletion, a plausible primitive exposed by EXP-009;
- stronger continuity interpretation than mere long retention or an exact deterministic action rhythm.

This selection does not pre-commit to increasing capacity, creating a dormant store, or adding a memory mechanism. Existing-state recoverability must be tested first.
