# Post-v9.3 preserved failure revalidation

Frozen subject: `v9.3_concern_capacity_three`, branch `champion-v9-3-concern-capacity-three`, commit `a10bc27579bf5bd0ff1a90d6ad6e3f337d8ed7bc`.

Independent frozen verification run `35249449797` passed: exact frozen ref, evaluated production byte identity, 72 repository tests / 18 subtests, EXP-010 evaluation, both EXP-010 reviewers, and strict EXP-010 closeout.

Separate audit branch revalidation run `35249531720` also verified frozen production bytes, passed 72 tests / 18 subtests and strict EXP-010 closeout, then replayed the preserved failure definitions against v9.3.

## Frontier

- `rewarded_routine_never_weakens`: **still reproduced**. Learned morning-walk value remains exactly `0.35` after 1000 unrelated events and walk wins on return.
- `ancient_commitment_reactivates_unchanged`: **still reproduced**. `call_morgan -> morgan_arrives` remains intact through 1000 unrelated events and reactivates as a concern at approximately `0.7275` after cue/event drift.
- `third_commitment_is_forgotten`: **still reproduced**. Prospective capacity remains 2; after first/second/third commitments, only second and third remain, and `cue_first` does not recover first.
- `deterministic_rhythm`: **still reproduced**. The final 60 neutral autonomous actions repeat the exact six-action pattern `rest, work, idle, rest, idle, idle`; exact periods <=20 are 6, 12, and 18.
- `suppressed_concern_never_returns`: **eliminated by EXP-010**. Capacity three retains `low_priority` alongside the two stronger concerns; after both stronger concerns are cancelled, `low_priority` remains represented at approximately `0.30446`.

This is the exact behavioral frontier used by MBASE-001. No EXP-011 target was selected before the basis audit.
