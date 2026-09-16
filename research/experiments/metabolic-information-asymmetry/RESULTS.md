# Metabolic Information Asymmetry Results

## Canonical 2 by 2 result

| Condition | E3 available to SOCIAL at t3 | E3 available to ACTION at t3 | E3 available to LANGUAGE at t3 | Final behavior |
|---|---:|---:|---:|---|
| Global broadcast, abundant | yes | yes | yes | `SURPRISE_B` |
| Global broadcast, scarce | no | no | no | `ASK_B_FIRST` |
| Differential access, abundant | no | yes | yes | `ASK_B_FIRST` |
| Differential access, scarce | no | yes | yes | `ASK_B_FIRST` |

The abundant conditions reproduce the original PR 14 result. Global broadcast synchronizes E3 and produces `SURPRISE_B`. Differential access keeps E3 away from SOCIAL, so ACTION receives a current direct `welcome` cue and an outdated SOCIAL `ASK_B_FIRST` recommendation, then selects the conservative `ASK_B_FIRST` response under the unchanged action rule.

The new result appears in global broadcast under scarcity. PERCEPTION spends four of its six units distributing E1. At timestep 3 it has two units remaining, but E3 requires four units to broadcast to every topology-eligible processor. Because broadcasts are funded atomically, the E3 transmission fails for every recipient. SOCIAL, ACTION, and LANGUAGE all continue without E3. SOCIAL recommends `ASK_B_FIRST`, and ACTION also retains the older E1-derived direct preference, so the selected behavior becomes `ASK_B_FIRST`.

Scarcity therefore changes behavior in the global-broadcast condition but not in the differential-access condition.

## Capacity sweep

The capacity sweep exposes two deterministic thresholds.

For differential routing, E1 costs two units and E3 costs three more. E3 therefore becomes affordable at capacity 5.

For global broadcast, E1 costs four units and E3 costs four more. E3 therefore becomes affordable at capacity 8.

The expected sweep from capacity 4 through 10 is:

| Capacity | Global E3 | Global behavior | Differential E3 permitted routes | Differential behavior |
|---:|---|---|---|---|
| 4 | blocked by resource | `ASK_B_FIRST` | blocked by resource | `ASK_B_FIRST` |
| 5 | blocked by resource | `ASK_B_FIRST` | delivered | `ASK_B_FIRST` |
| 6 | blocked by resource | `ASK_B_FIRST` | delivered | `ASK_B_FIRST` |
| 7 | blocked by resource | `ASK_B_FIRST` | delivered | `ASK_B_FIRST` |
| 8 | delivered | `SURPRISE_B` | delivered | `ASK_B_FIRST` |
| 9 | delivered | `SURPRISE_B` | delivered | `ASK_B_FIRST` |
| 10 | delivered | `SURPRISE_B` | delivered | `ASK_B_FIRST` |

The differential condition changes epistemically at capacity 5 even though its final behavior does not change. Below 5, ACTION never receives E3. At 5 and above, ACTION receives E3 but still receives SOCIAL's stale recommendation based on E1, so the same action rule resolves the conflict as `ASK_B_FIRST`.

This is an important negative result inside the positive finding. A change in information availability does not automatically produce a behavioral change.

## Resource conservation

Automated tests require exact conservation in all four conditions:

`initial resource total = remaining resource total + consumed resource total`

The manipulation therefore cannot create or destroy capacity except through explicitly logged consumption.

## Causal interpretation

The minimum new causal difference is not a new belief rule, personality variable, or action policy. It is the affordability of the E3 transmission.

In the abundant global condition:

`E1 broadcast -> remaining capacity sufficient for E3 -> E3 reaches SOCIAL and ACTION -> both support SURPRISE_B`

In the scarce global condition:

`E1 broadcast -> remaining capacity insufficient for E3 broadcast -> E3 reaches neither SOCIAL nor ACTION -> both retain the older avoid interpretation -> ASK_B_FIRST`

In scarce differential access:

`E1 selective route -> lower communication expenditure -> E3 selective route remains affordable -> ACTION receives E3 while SOCIAL does not -> local conflict -> ASK_B_FIRST`

The resource mechanism therefore changes the information topology actually realized during execution, even though the configured hard topology has not changed.

## What This Experiment Actually Demonstrated

Direct observation: adding one finite internal communication resource to the existing PR 14 system was sufficient to create a second source of persistent information asymmetry. Under scarcity, a route could be legally available yet fail because the sender could not afford the transmission. This changed the global-broadcast run's final behavior under the unchanged cognitive rules.

Direct observation: selective differential routing consumed less communication capacity in this scenario. It preserved E3 delivery to ACTION and LANGUAGE at resource levels where the broader global broadcast could no longer finance E3.

Direct observation: information changes and behavior changes remained separable. Differential access crossed its E3 affordability threshold at five units without changing its final action.

Interpretation: these results support the narrower proposition that metabolic communication cost can interact with epistemic topology rather than acting only as uniform performance degradation.

Alternative explanation: this remains a deliberately constructed threshold experiment. The resource model contains no bidding, learning, replenishment, hoarding, fatigue, actor-generated demand, or endogenous resource valuation. It does not yet demonstrate the stronger claim that a full internal resource economy will spontaneously produce rumination, habit, personality, or other lifelike cognitive dynamics.

The next experiment should therefore move one step deeper, from resource-priced routing to actor-generated operation demand, while retaining this 2 by 2 experiment as the baseline control.
