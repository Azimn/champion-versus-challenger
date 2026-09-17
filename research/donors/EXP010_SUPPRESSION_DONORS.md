# EXP-010 Internal Archaeology: Suppression Without Deletion

## Search question

After the EXP-010 matched-history foundation established that capacity eviction erases all subject-owned information identifying the displaced concern, internal archaeology searched for the smallest already-existing representation that could preserve an unfinished identity without keeping it behaviorally dominant.

No source code is reused by EXP-010. Licensing was treated conservatively. Where a repository did not expose an explicit license in the inspected root/package metadata, only conceptual comparison was permitted.

## Azimn/DUCK

- repository: `Azimn/DUCK`
- branch: `motivated-cognition-v0.10`
- commit: `30a11ea8308ebd0fc89a06bb994ab0e23bd02886`
- relevant implementation: `duck/motivated_cognition.py`
- relevant behavior: persistent `MotiveRecord` objects carry identity plus strength, urgency, persistence, inhibition, status, timestamps, and links. Status distinguishes `dominant`, `active`, `latent`, `inhibited`, `satisfied`, and `impossible`. A separate active-motive selection can therefore leave other motive identities persistent but non-dominant. State is bounded by `MAX_MOTIVES = 24`; stale targeted latent/inhibited motives may later retire under explicit age/strength/persistence criteria.
- persistent information required: substantially more than EXP-010's lower bound. At minimum DUCK stores motive identity, theme, target, strength, urgency, persistence, inhibition, status, creation/update time, and links.
- termination semantics: explicit statuses plus age/strength/persistence retirement and capacity compaction.
- reactivation semantics: repeated pressure can reactivate an existing motive identity and reduce inhibition; impossible motives can return to latent when pressure is sufficient.
- capacity behavior: many persistent motive records with a distinct active subset; global bound 24 and active subset bound 3.
- license status: no `LICENSE` file was present in the inspected branch root and `pyproject.toml` contains no license declaration. Treat as licensing unclear.
- unnecessary architecture for EXP-010: explicit status ontology, inhibition, urgency, persistence, timestamps, associative graph, active-motive set, retirement policy, strategy learning, cognitive modulation.
- conclusion: strong conceptual evidence that persistence and dominance can be distinct, but far larger than the minimum-information target. Not selected for reuse.

## Azimn/persona_engine_PYTHONX

- repository: `Azimn/persona_engine_PYTHONX`
- branch: `main`
- commit: `65df9144e7f0876b6e61e28d6446c50f283f9db4`
- relevant inspected implementation: `persona_engine/core/habit.py`, package structure under `persona_engine/core/`
- behavior provided: deterministic persistent tendencies and many other organism subsystems. The inspected habit representation retains named trigger/response identities with strength, use count, and last-used time, and supports decay without deletion.
- suppression/resumption finding: no smaller structured unfinished-concern suppression primitive was found in the inspected material. Habit persistence is semantically a learned routine, not an unresolved demand.
- license status: `pyproject.toml` contains no project license declaration and no explicit root license was established during this pass. Treat as licensing unclear.
- conclusion: do not repurpose habit state merely because it can retain an identity. Its semantics are wrong for unresolved concerns.

## Azimn/TinyPersonaEngine

- repository: `Azimn/TinyPersonaEngine`
- branch: `main`
- commit: `5eb2e84dbb43c828fae7a1459c9fd13535c7b332`
- relevant inspected implementation: `src/living_entity_firstperson/models.py`, `memory.py`, architecture files.
- behavior provided: first-person perception, attention, experiences, beliefs, memory associations, action pressures. `ObserverState` includes a set of goals used as perceptual/attention context.
- suppression/resumption finding: the inspected goal field is not an earned dynamic bounded unresolved-goal competition mechanism with termination and resumption semantics. Memory can retain experiences, but using it as a hidden concern archive would add a new retrieval and interpretation mechanism.
- conclusion: no semantically appropriate lower-cost donor than the champion's existing concern ledger.

## Azimn/FirstPersonLoopTest

- repository: `Azimn/FirstPersonLoopTest`
- branch: `main`
- commit: `f61b39d4b70eb5b905a225ec6f4cb728a452e922`
- relevant inspected implementation: `subjective_character_loop_v0_1/subjective_loop.py`
- behavior provided: persistent narrative episodes in SQLite plus hidden organism variables converted to first-person experience.
- suppression/resumption finding: the journal can remember prose about unfinished matters, but there is no structured bounded concern-competition mechanism that can causally restore a displaced concern without language interpretation. Reusing narrative history would violate EXP-010's mechanism-minimality and subjective-access constraints.
- conclusion: not a donor for the selected causal representation.

## Azimn/personaconsolev5A

- repository: `Azimn/personaconsolev5A`
- branch: `main`
- commit: `3099a28a99b105261bfe11e6a71a2b7928f5e7cb`
- inspected tree contains only `PersonaConsole_v5.zip`.
- no source-level suppression mechanism was available for clean inspection through the repository tree in this pass.
- conclusion: no claim made about internal behavior; no reuse.

## Internal conclusion

The most relevant prior mechanism is already inside the champion lineage itself:

1. EXP-004 established a bounded concern ledger capable of holding multiple unfinished identities.
2. v9/v9.1 established that `active_concern` and `concern_strength` are deterministic views of the strongest ledger entry rather than separate persistent state.
3. EXP-009 established that ledger membership means unresolved existence while the scalar means current activation.
4. v9.1 reduced concern capacity from three to two because two was sufficient for the then-earned behavioral contract.
5. EXP-010 now supplies a new three-simultaneous-unresolved-identity counterexample.

This makes a capacity-3 diagnostic especially informative. It is not importing a new faculty. It tests whether the previously compacted existing concern representation now lacks the minimum representational capacity required by the newly reproduced failure.
