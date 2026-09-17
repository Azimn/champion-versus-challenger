# EXP-011 reviewer pass 1 failure

Workflow run: `35275898549`
Job: `105386337646`
Production blob under review: `4238680bb78c21dd71b55cf279b2e4e2ce0e03a8`

Reviewer result: **42/43 passed**.

Sole failure: `fill_activate_refill_cues`.

Classification: **invalid reviewer assumption / cross-capacity contract error**.

The reviewer created three prospective commitments `a`, `b`, `c`, activated `b`, then inserted `d` into the now-free prospective slot. It then delivered cues for `a`, `c`, and `d` and asserted that all four identities `a`, `b`, `c`, `d` must remain simultaneously present in the active concern ledger.

That assertion contradicts the already-earned EXP-010 contract: concern capacity is exactly three. The observed final state was `a`, `c`, `d` in the concern ledger, with the prospective store empty. This is the expected result after the fourth concern activation under the inherited concern-capacity-three replacement rule. `b` was displaced from the concern ledger only after the later prospective cues correctly activated their associated commitments.

The prospective behavior under review was therefore correct:

1. activating `b` consumed only `b`'s prospective binding;
2. `a` and `c` remained latent;
3. adding `d` filled the third prospective slot without losing `a` or `c`;
4. cue `ca` activated `a` and consumed its binding;
5. cue `cc` activated `c` and consumed its binding;
6. cue `cd` activated `d` and consumed its binding;
7. the concern ledger then enforced its independent capacity-three bound.

No production repair is justified. The original reviewer must remain unchanged. A separate adjudication should replay the original reviewer, require this exact sole failure, and verify the stepwise prospective semantics without requiring four simultaneous active concerns.
