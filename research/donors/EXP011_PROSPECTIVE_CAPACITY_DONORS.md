# EXP-011 pre-preregistration archaeology: prospective capacity

## Selected frontier failure
`third_commitment_is_forgotten`, selected only after MBASE-001 closed. It is the strongest remaining continuity failure with a clean information-bound signature: an explicitly formed future commitment is silently erased solely because two later commitments occupy the bounded prospective store; its experienced cue then produces no recognition.

## Foundation
Run `35267809371`, artifact `10516994582`, passed the unchanged 72-test / 18-subtest repository contract and reproduced the failure. Prospective capacity is 2. After `first`, `second`, `third`, only second and third remain. `cue_first` activates no concern.

Matched histories establish an information boundary. History A formed first, second, third. History B used a matched neutral event instead of ever forming first, then formed second and third. Immediately after first is evicted, complete canonical persistent serialization is identical between A and B. Thus current subject-owned state retains no bit distinguishing 'first existed and was evicted' from 'first never existed'. Deterministic current-state policy cannot later recover first.

Order permutations show FIFO/oldest replacement: a,b,c -> b,c; c,b,a -> b,a; b,a,c -> a,c. This is insertion-order capacity loss, not strength competition.

## Minimum information lower bound
For an event-based prospective commitment to react to its future cue, retaining concern identity alone is insufficient: the organism must also retain which experienced cue is associated with that identity. Cue alone is likewise insufficient to recover which commitment should activate. The existing prospective record already stores exactly this pair: `concern -> cue`. The minimum current-architecture representation therefore appears to be one additional bounded instance of the existing pair, not a new field type.

## Existing-state trace search
- Concern ledger: semantically active unresolved concerns; using it for latent commitments would recreate the previously rejected active/prospective union and could create premature behavioral pressure.
- Eligibility trace: action/outcome attribution semantics and max age 10; does not encode future commitment identity/cue.
- Habit values: context/action utility semantics; not an intention store.
- Relationship, reliability, affect, needs, subjective facts: no prospective identity/cue semantics.
No earned existing mechanism legitimately retains the evicted prospective pair.

## Internal archaeology

### Current EXP-005 prospective mechanism
`src/lifelike_min/exp005_challenger.py` uses an `OrderedDict` mapping concern identity to cue. `max_prospective = 2`; adding a third distinct binding pops the oldest. Cue activation removes the binding and inserts an ordinary concern. This is the direct causal source and already supplies the exact representation needed if capacity is sufficient.

### Azimn/persona_engine_PYTHONX
Pinned `65df9144e7f0876b6e61e28d6446c50f283f9db4`, `persona_engine/core/intention.py`. `IntentionQueue` retains intention identity plus priority/source/time/optional expiration in a list, selecting an active top intention separately. Useful donor principle: an intention can remain represented while not selected. It is much heavier than required here and has no fixed minimal capacity result. License status was not established in this audit; conceptual use only, no code copied.

### Azimn/DUCK v0.10
Pinned `30a11ea8308ebd0fc89a06bb994ab0e23bd02886`, `duck/motivated_cognition.py`. Persistent `MotiveRecord` separates identity and lifecycle/status from transient activation; `MAX_MOTIVES=24`, `MAX_ACTIVE_MOTIVES=3`, with latent/inhibited states. Useful donor principle: retained identity can exceed currently active competition. This machinery includes strength, urgency, persistence, inhibition, status, timestamps, links, associative graph and modulation and is far beyond the information lower bound. Conceptual donor only.

## Narrow external prior art

- McDaniel, Howard & Butler (2008), *Implementation intentions facilitate prospective memory under high attention demands*, Memory & Cognition 36(4), 716-724, DOI 10.3758/MC.36.4.716. Relevant principle: prospective performance benefits from a robust association between a target situation/cue and intended action.
- Rummel, Einstein & Rampey (2012), *Implementation-intention encoding in a prospective memory task enhances spontaneous retrieval of intentions*, Memory 20(8), 803-817, DOI 10.1080/09658211.2012.707214. Relevant principle: an intention can be suspended during intervening activity and later be retrieved by its cue; cue-intention association is central.
- Smith (2003), *The cost of remembering to remember in event-based prospective memory: investigating the capacity demands of delayed intention performance*, JEP:LMC 29(3), 347-361, DOI 10.1037/0278-7393.29.3.347. Relevant principle: delayed intentions have capacity demands; this supports treating representational capacity as a real dimension without importing a cognitive architecture.

These sources motivate the information representation question only. They do not establish that biological prospective memory uses a three-slot store or justify this implementation's capacity.

## Candidate classes before implementation
A. Replacement policy only at capacity 2: rejected as insufficient for the target history if all three simultaneously valid commitments must remain distinguishable; any two-record deterministic store must erase at least one of three independent identity/cue pairs.
B. Prospective capacity 2 -> 3: smallest direct representation of all three existing identity/cue pairs; zero new fields and zero new mechanism; preserves existing activation semantics. Selected first hypothesis.
C. One separate overflow prospective record: same information count as capacity 3 but adds a distinct storage/status path and return/merge policy. Larger semantic machinery than B.
D. Reuse concern ledger: rejected preimplementation because latent commitments and active concerns have empirically distinct semantics and same-name coexistence was previously required.
E. Reuse eligibility/habit/fact/social state: rejected as semantically unrelated and would corrupt earned meanings.

Selected minimum hypothesis: increase only existing prospective commitment capacity from 2 to 3, then run a 2/3/4 capacity tournament. This is a representational-capacity hypothesis, not a twelfth-mechanism hypothesis.
