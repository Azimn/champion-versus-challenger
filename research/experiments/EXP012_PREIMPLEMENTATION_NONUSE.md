# EXP-012 Preimplementation Operational Note

Frozen after preregistration and before challenger production code.

## Subject-experienced nonuse

For H1, one **processed organism event** is the only temporal unit.

For each already-stored habit `(context, action) -> scalar`:

- if that event produces a nonzero learned-value update to that same habit through existing immediate or delayed outcome semantics, that habit is **refreshed** on the event and is not attenuated on that event;
- otherwise the habit qualifies for one nonuse attenuation update.

Therefore mere action execution without nonzero outcome evidence does not count as reinforcement. Explicit zero reward is distinct from negative reward but, because it supplies no learned-value update in the frozen runtime, it does not refresh the habit. Action unavailability, unrelated-context activity, and other experienced events also count as nonuse for already-stored habits.

Hidden simulator activity, wall-clock downtime, and unexperienced events never attenuate habits.

## Event ordering

Existing outcome learning executes first. The challenger observes which habit scalars changed because of that event. Only unchanged pre-existing habit scalars are then attenuated. This guarantees that a freshly earned positive or negative update is not immediately attenuated on the same event.

A newly created habit entry is not attenuated on its creation/update event.

## Temporal variable actually used

H1 uses **experienced event count**, not elapsed simulated time, wall-clock time, context exposure count, or opportunity count. Event segmentation is therefore expected to matter. EXP-012 must measure and disclose that dependence rather than relabeling it as time.

## Attenuation operator

For a qualifying habit value `v` and retention factor `r`:

`v_next = v * r`

with `0 < r <= 1`.

This is multiplicative/exponential attenuation toward neutral. It preserves sign and never crosses through zero by the attenuation operation alone. Habit keys are retained even for extremely small values; EXP-012 does not add deletion semantics.
