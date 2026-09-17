# EXP-010 Outcome

Decision: **PROMOTE**.

Promoted behavioral/representational descendant: `v9.3_concern_capacity_three`.

Production behavior is frozen at `03baf6bc6f06d3f298701a8ce66c44e00f509d50`; later commits contain tests, reviewers, closeout, and permanent records only.

EXP-010 establishes an information lower bound and a capacity result, not a new cognitive mechanism.

- The target's three simultaneously unresolved identities cannot be represented by the v9.2 two-entry concern store once one identity is evicted; matched-history canonical states collapse to identity.
- No existing semantically appropriate subject-owned state retains the evicted identity.
- Capacity 2 fails the target.
- Capacity 3 passes the target.
- Capacity 4 adds no target behavior.
- No new field or counted mechanism is introduced; mechanism count remains 11.
- The third existing-format concern record costs 30 canonical bytes in the normalized closeout fixture when occupied.
- Capacity loss remains explicit at the fourth sufficiently strong simultaneous unresolved identity.

Supported claim: **A third unresolved concern can remain represented but non-dominant while two stronger concerns compete, then regain ordinary behavioral eligibility when those competitors terminate. At least its identity must remain subject-owned; the smallest tested successful implementation retains one additional existing-format concern record.**

Not established: general goal memory, planning, BDI architecture, unbounded persistence, general forgetting, human working-memory capacity, or optimal arbitration.

Strict closeout: run `35249321377`, artifact `10508776574`.
