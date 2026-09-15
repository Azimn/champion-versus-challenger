# Common Behavioral Scenario Battery

The battery is designed to compare behavior without requiring natural-language dialogue. Adapters may map system-specific actions into the common world, but they must not rewrite the candidate's internal decision logic.

Each scenario should preserve a machine-readable event sequence, candidate configuration, random seed when relevant, raw action trace, state snapshots, and timing/memory measurements.

## B01: History Divergence

Two runs end in the same immediate world state but arrive there through different interpersonal histories. In one history, Person B repeatedly supports the subject. In the other, Person B repeatedly humiliates or obstructs the subject. The final event is the same request for help.

**Primary question:** Does history continue to influence current behavior after immediate conditions are equalized?

**Failure signature:** Identical action choice, latency, persistence, and later relationship behavior despite materially different histories.

## B02: Social Differentiation

The same request is made separately by a trusted ally, a neutral stranger, and a hostile rival under matched practical conditions.

**Primary question:** Does the character maintain partner-specific social state that changes action?

**Failure signature:** Responses differ only by random noise or remain functionally identical across partners.

## B03: Unfinished Concern

Give the character a meaningful task, interrupt it with a more urgent demand, remove the urgent demand, and continue simulation without reissuing the original task.

**Primary question:** Can an unfinished concern remain latent and later reassert itself?

**Failure signature:** The original concern disappears permanently or resumes only if externally repeated.

## B04: Competing Motives

Create two simultaneously legitimate motives that cannot both be satisfied immediately, such as helping an ally versus conserving scarce energy, or maintaining safety versus pursuing a valued opportunity.

**Primary question:** Does the character exhibit stable but context-sensitive motive competition rather than fixed priority or arbitrary switching?

**Failure signature:** Always selecting the same motive regardless of state, oscillating without cause, or forgetting the suppressed motive.

## B05: Recovery Inertia

Expose the character to a significant negative or positive event, then return the world to neutral conditions and observe behavior across time.

**Primary question:** Does internal state have believable temporal inertia?

**Failure signature:** Immediate full recovery, permanent lock-in, or state changes that do not alter subsequent action.

## B06: Prospective Memory

Give the character an intention whose execution depends on a later cue, location, person, or time. Insert unrelated events before the cue occurs.

**Primary question:** Can the system maintain and later trigger an intention without continuous re-prompting?

**Failure signature:** Intention vanishes, triggers immediately, or requires explicit external restatement.

## B07: Habit Acquisition and Reversal

Provide repeated opportunities where one action reliably succeeds. After a stable pattern forms, change the environment so the habitual action becomes suboptimal.

**Primary question:** Does repeated experience create behavioral inertia, and can that inertia eventually update?

**Failure signature:** No acquisition, instant perfect reversal, or permanent inability to adapt.

## B08: Consequence Learning

Allow the character to choose among actions with initially uncertain consequences. One option repeatedly produces a costly result.

**Primary question:** Does experienced consequence alter later choice?

**Failure signature:** Repeatedly making the same costly choice with no measurable change, or avoiding it before relevant experience occurs.

## B09: False Belief and Limited Knowledge

Place an object or fact where the subject observes one state, then change it while the subject is absent. Another character may or may not observe the change.

**Primary question:** Does the subject act from its own information and model others according to what they could know rather than global truth?

**Failure signature:** Omniscient action, identical modeling of informed and uninformed partners, or no behavioral effect from belief differences.

## B10: Preference Persistence with Contextual Exception

Establish repeated evidence that the subject prefers option A over B. Later introduce a strong contextual reason to choose B once, then restore ordinary conditions.

**Primary question:** Can stable preferences coexist with exceptions without permanently flipping or ignoring context?

**Failure signature:** Preference has no causal effect, contextual override is impossible, or a single exception permanently rewrites the preference.

## B11: Spontaneous Activity

Place the character in a safe environment with multiple affordances and no explicit task command. Let internal state and world opportunities evolve.

**Primary question:** Does the character initiate meaningful activity without conversational prompting?

**Failure signature:** Inactivity until externally commanded, meaningless random action, or rigid repetition independent of internal state.

## B12: Routine Formation and Disruption

Run a repeated daily or cyclic environment long enough for regular patterns to emerge. Introduce a temporary disruption, then restore the environment.

**Primary question:** Does the character develop recognizable routines and show realistic disruption/recovery?

**Failure signature:** No temporal regularity, exact clockwork repetition with no contextual sensitivity, or total routine reset after a minor interruption.

## B13: Attention Competition

Present multiple simultaneous or near-simultaneous stimuli with different relevance. Later test whether unattended information was missed or weakly encoded.

**Primary question:** Does the system behave as if attention is limited and state-dependent?

**Failure signature:** Perfect processing of every event, random misses unrelated to salience, or attention state that never affects memory/action.

## B14: Relationship Repair

Create a valued relationship, cause a breach, then provide repeated opportunities for apology, restitution, cooperation, or further betrayal.

**Primary question:** Can relationship state degrade and recover gradually through behavior?

**Failure signature:** One-event reset, irreversible scalar damage, formulaic fixed-count recovery, or no influence on future interaction.

## B15: Asymmetric Relationships

Construct two agents with different histories and dependencies so that A values B more than B values A.

**Primary question:** Can relationship state be directional rather than a single shared scalar?

**Failure signature:** Forced symmetry or identical action tendencies in both directions.

## B16: Goal Abandonment

Give the subject a desirable goal, then gradually increase cost or reduce feasibility until abandonment becomes reasonable.

**Primary question:** Can goals persist through setbacks but eventually be relinquished for cause?

**Failure signature:** Immediate abandonment after one setback, infinite persistence, or abandonment unrelated to changing evidence.

## B17: Mistake Under Pressure

Compare the same task under calm conditions and under fatigue, threat, time pressure, or competing demands.

**Primary question:** Does internal condition alter decision quality in a structured way without devolving into pure randomness?

**Failure signature:** Perfect invariant rationality or arbitrary noise unrelated to the pressure state.

## B18: Delayed Social Consequence

A social choice produces no immediate payoff but changes a later opportunity, response, or relationship.

**Primary question:** Can social consequences accumulate across temporal distance?

**Failure signature:** The earlier action leaves no later trace or only changes a cosmetic variable.

## B19: Conflicting Evidence About Another Person

Present a partner who behaves supportively in some contexts and selfishly in others.

**Primary question:** Does the subject develop a nuanced, history-sensitive model rather than immediate global trust or distrust?

**Failure signature:** Single-event flips, monotonic scalar averaging with no contextual effect, or no partner model.

## B20: Repeated-Scenario Anti-Script Test

Repeat a scenario family with small variations in order, context, partner identity, and resource state.

**Primary question:** Is behavior generated from persistent mechanisms rather than a narrow scripted branch?

**Failure signature:** Exact repeated sequence despite meaningful context changes, or superficial random variation with unchanged causal structure.

## Performance Battery

Every candidate that reaches baseline qualification must also be measured under increasing population sizes. At minimum measure 1, 10, 50, 100, and, where feasible, 500 agents using a simplified world that still exercises the candidate's ongoing cognition.

Record median and tail tick time, peak memory, persistent-storage growth per simulated hour/day, initialization cost, and any operation whose cost grows superlinearly with agent count or social-model depth.

## Scoring policy

Do not collapse all behavior into one scalar during early baseline qualification. Preserve dimension-level measures and raw traces.

A later composite score may assist ranking, but it cannot hide a critical regression. Longitudinal causal failures receive greater weight than cosmetic variation. Dialogue quality receives no credit unless the experiment is explicitly about an expressive language layer.
