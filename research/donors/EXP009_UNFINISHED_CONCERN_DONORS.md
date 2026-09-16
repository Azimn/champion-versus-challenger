# EXP-009 Archaeology: Unfinished Concern Persistence

## Reproduced behavior that determines this search

Frozen `v9.1_compact` stores an explicitly assigned unfinished concern at strength `0.75`, then multiplies the strength by `0.97` on every tick and deletes the concern below `0.08`. With no completion, cancellation, impossibility, or contradicting evidence, the concern disappears after 74 unrelated events.

Causal characterization shows the observed disappearance time is exactly predicted by that decay rule across tested assignment intensities. Neutral events, unrelated social events, unrelated location observations, and unrelated reliability observations erase the concern at the same rate.

The search question is therefore behavioral rather than architectural:

> What is the smallest historically grounded way to let the current activation/priority of an unfinished intention weaken without treating weak activation itself as evidence that the intention no longer exists?

No challenger implementation exists yet.

## Internal archaeology

### Azimn/DUCK

- Repository: `Azimn/DUCK`
- Branch: `motivated-cognition-v0.10`
- Pinned branch commit inspected: `30a11ea8308ebd0fc89a06bb994ab0e23bd02886`
- Relevant file: `duck/motivated_cognition.py`
- Root `LICENSE`: not present at the inspected ref
- Reuse policy: concept donor only; no source copied

Relevant behavior:

`MotiveRecord` separates persistent motive identity from several changing properties: `strength`, `urgency`, `persistence`, `inhibition`, and `status`. Status can distinguish `dominant`, `active`, `latent`, `inhibited`, `satisfied`, and `impossible`.

The compaction policy protects dominant/active motives from stale retirement. Targeted resolved motives can retire after being marked `satisfied` or `impossible`; weak targeted latent/inhibited motives can retire only under a conjunction involving low strength, low persistence, and age. Thus momentary strength alone is not treated as existence.

Useful donor principle:

**Existence/lifecycle status and momentary activation are separable.**

Unnecessary architecture for the current failure:

- persistent motive records with multiple new scalar fields;
- explicit status field;
- timestamps;
- associative graph;
- cognitive modulation;
- motive competition machinery;
- memory indexing.

None of that is justified by the current frozen failure.

### Azimn/persona_engine_PYTHONX

- Repository: `Azimn/persona_engine_PYTHONX`
- Main commit inspected: `65df9144e7f0876b6e61e28d6446c50f283f9db4`
- Relevant file: `persona_engine/core/intention.py`
- Root `LICENSE`: not present at the inspected ref
- Reuse policy: concept donor only; no source copied

Relevant behavior:

`Intention` is stored as a persistent record containing a name and a mutable priority. `IntentionQueue.select_top()` can reduce priority with age, but retention is controlled separately by an optional explicit `expires_at`; low priority by itself does not delete the intention.

The same file's `OpenLoop` path is less useful for this experiment because it decays urgency and deletes low-urgency loops, reproducing the kind of semantic coupling under investigation.

Useful donor principle:

**Selection priority can decay independently of whether an intention remains in the set.**

Unnecessary architecture for the current failure:

- wall-clock creation time;
- expiration timestamps;
- separate open-loop record type;
- surfaced-count bookkeeping;
- emotional-charge fields.

### Azimn/TinyPersonaEngine

- Repository: `Azimn/TinyPersonaEngine`
- Main commit inspected: `5eb2e84dbb43c828fae7a1459c9fd13535c7b332`
- Relevant file: `src/living_entity_firstperson/models.py`
- Root `LICENSE`: not present; `pyproject.toml` also does not establish a package license
- Reuse policy: concept donor only; no source copied

Relevant behavior:

`ObserverState` stores `goals` separately from transient `ActionPressure.utility`. This is not a full intention lifecycle implementation, but it provides another internal example of objective identity being distinct from the momentary pressure used for action choice.

Useful donor principle:

**A goal/concern can exist independently of current action pressure.**

This donor is weaker than DUCK and `persona_engine_PYTHONX` for the selected failure and supplies no implementation to reuse.

## Narrow external prior art

### Cohen & Levesque, 1990, *Intention is Choice with Commitment*

- Publication: *Artificial Intelligence* 42(2–3), 213–261
- DOI: `10.1016/0004-3702(90)90055-5`
- Source: https://www.sciencedirect.com/science/article/abs/pii/0004370290900555
- Copyrighted publication; concept only

Relevant point:

The paper makes commitment central to intention and explicitly treats the conditions under which an agent may drop a goal as part of the theory of intention. The useful abstraction for this project is not the modal logic. It is the distinction between an intention continuing to be held and the conditions that justify terminating it.

### Rao & Georgeff, 1995, *BDI Agents: From Theory to Practice*

- Proceedings: First International Conference on Multiagent Systems, pp. 312–319
- Official source: https://aaai.org/papers/icmas95-042-bdi-agents-from-theory-to-practice/
- Official PDF: https://cdn.aaai.org/ICMAS/1995/ICMAS95-042.pdf
- Copyright © AAAI; concept only

Relevant point:

Rao and Georgeff explicitly split commitment into a condition that is maintained and a termination condition. Their abstract interpreter subsequently drops successful/satisfied and impossible/unrealizable attitudes. In the practical discussion, intentions can coexist, run, or remain suspended. The useful donor concept is therefore:

**An intention is retained under a commitment policy and is removed by a semantically meaningful termination condition, not merely because its present activation is small.**

This does not imply importing BDI beliefs, desires, plans, intention stacks, theorem proving, or PRS/dMARS machinery.

### AgentSpeak(L), Rao, 1996

- Publication: MAAMAW 1996, pp. 42–55
- DOI: `10.1007/BFB0031845`
- Bibliographic source: https://dblp.org/rec/conf/maamaw/Rao96

AgentSpeak is relevant only as evidence that BDI-style persistent intention handling was subsequently operationalized in a compact agent language. It is not required to explain the present failure, and no AgentSpeak machinery is proposed for EXP-009.

## Archaeology conclusion

All three internal donors and the narrow BDI literature converge on the same distinction:

1. an unfinished concern/intention has an identity or lifecycle state; and
2. current activation, priority, salience, or selection pressure can vary independently.

Frozen v9.1 currently compresses both into one scalar and uses an activation threshold as an implicit termination condition.

The current experiment does **not** yet justify adding a status field, persistence scalar, timestamp, memory tier, intention stack, planner, or BDI subsystem. The frozen organism already has:

- concern identity as the dictionary key;
- activation/priority as the dictionary value;
- explicit `task_cancel` removal;
- action-mediated resolution/removal through `work`;
- bounded capacity/competition.

The minimum hypothesis should first test whether ordinary decay can weaken activation without being sufficient by itself to erase an explicitly unfinished concern. Capacity eviction and existing explicit resolution signals remain available as termination mechanisms.

## Licensing boundary

No donor source is copied into the experiment. The three inspected internal repository roots did not expose a `LICENSE` file at the inspected refs, and the external publications are used as conceptual prior art. Any eventual challenger should be an independently written minimal implementation derived from the observed behavioral principle, not a port of donor code.
