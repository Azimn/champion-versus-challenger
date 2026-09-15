# Candidate Adapter Contract

The adapter exists to make unlike systems observable in the same experimental world. It must not become a hidden replacement architecture.

## Boundary

A candidate remains responsible for its own cognition, persistent internal state, decision making, learning, planning, emotion, social reasoning, and action selection to the extent that those capabilities exist in the original system.

The adapter may translate common world events into the candidate's native input representation; expose candidate actions in a common action vocabulary; synchronize simulated time; seed candidate randomness where supported; capture state snapshots that the original system already exposes; and record performance telemetry.

The adapter must not add memory the candidate does not possess; preserve goals externally for a candidate that would otherwise forget them; add relationship state; add appraisal; add planning; add Theory of Mind; rerank candidate actions; repair irrational choices; inject context the candidate would not normally perceive; or use an LLM to decide what the candidate meant or should do.

If a system cannot express a common scenario without adding a cognitive capability through the adapter, mark that scenario `NOT EXPRESSIBLE` for that candidate and record why. Do not silently make the adapter smarter.

## Common world vocabulary

The first battery assumes only generic primitives that can be mapped into most simulation systems:

`agent`, `location`, `object`, `resource`, `time`, `event`, `observation`, `action`, `social_actor`, `task`, `goal_opportunity`, `cost`, `reward`, `availability`, and `private_information`.

Systems may retain richer native representations internally. The common vocabulary is an experimental exchange format, not an ontology the candidate must adopt.

## Common action vocabulary

Adapters should map native actions to the smallest defensible semantic categories needed by the scenario, for example `approach`, `avoid`, `help`, `refuse`, `share`, `withhold`, `cooperate`, `retaliate`, `wait`, `work`, `rest`, `explore`, `consume`, `communicate`, `inspect`, `resume_task`, and `abandon_goal`.

Preserve the native action and parameters alongside the normalized action. Never discard the original trace.

## Trace record

Each action/event record should include at least:

```json
{
  "run_id": "...",
  "scenario_id": "B01",
  "candidate_id": "PC-001",
  "candidate_version": "commit/tag",
  "sim_time": 0.0,
  "tick": 0,
  "actor": "subject",
  "record_type": "event|observation|action|state|metric",
  "native_type": "candidate-specific label",
  "normalized_type": "common label when applicable",
  "target": null,
  "payload": {},
  "seed": null,
  "wall_clock_ns": null
}
```

A candidate may emit additional fields. Adapters must not fabricate hidden internal state that is unavailable from the original system.

## Determinism

Where the candidate exposes random seeds, record and control them. Where it does not, run sufficient repetitions to characterize variation and explicitly mark the candidate as non-seedable.

Do not force determinism by replacing native stochastic mechanisms.

## Preservation

Store the exact external repository URL, commit or release, dependency lock information where obtainable, adapter version, scenario version, and run command with every experiment.

If old dependencies require patches to execute, preserve each patch separately and classify it as one of:

`ENVIRONMENT COMPATIBILITY PATCH`: required only to build/run on modern infrastructure and intended not to change behavior.

`BEHAVIORAL PATCH`: changes candidate logic and therefore creates a challenger rather than an original baseline.

Compatibility patches must receive their own regression check against any historical demo, test, or documented trace that can still be reproduced.
