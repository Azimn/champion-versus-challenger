from __future__ import annotations

from typing import Any


def architecture_markdown() -> str:
    return """# Architecture Diagrams

## Condition A: Global Broadcast Control

```mermaid
flowchart LR
    ENV[Environment] --> P[PERCEPTION]
    P --> W[Broadcast workspace]
    W --> S[SOCIAL]
    W --> M[MEMORY]
    W --> A[ACTION]
    W --> L[LANGUAGE]
    S --> W
    A --> W
    A --> S
    L -. temporary binding .-> M
    M -. temporary binding .-> L
    L -. temporary binding .-> S
    S -. temporary binding .-> L
```

All workspace-eligible events and inferences are sent to every other processor. Processors still retain private local state.

## Condition B: Differential Access

```mermaid
flowchart LR
    ENV[Environment] --> P[PERCEPTION]
    P -->|private fact| S[SOCIAL]
    P -->|private and public facts| M[MEMORY]
    P -->|public fact and decision prompt| A[ACTION]
    P -->|public fact and decision prompt| L[LANGUAGE]
    A -->|recommendation request| S
    S -->|recommendation only| A
    A -->|behavior result| L
    L -. temporary binding .-> M
    M -. temporary binding .-> L
    L -. temporary binding .-> S
    S -. temporary binding .-> L
```

No processor can inspect another processor's local state. The temporary links transmit messages only and do not merge state.
"""


def results_markdown(comparison: dict[str, Any]) -> str:
    return architecture_markdown() + f"""
# Side-by-Side Comparison

The neutral greeting at timestep 2 was identical in both conditions even though private knowledge already differed. Both selected `GREET_B`. This is a negative result showing that information asymmetry alone does not force behavioral divergence.

At timestep 3, public event `E3` reached SOCIAL in the global condition but not in the differential condition. In the global condition, SOCIAL replaced its earlier `avoid` interpretation with `welcome`. In the differential condition, SOCIAL retained the earlier private event `E1` as its local basis.

At timestep 4, ACTION used the same decision rule in both conditions. The global run produced `{comparison['final_behavior_global']}` because direct evidence and the social recommendation agreed. The differential run produced `{comparison['final_behavior_differential']}` because ACTION received B's public `welcome` cue while SOCIAL supplied an `ASK_B_FIRST` recommendation generated from its stale local history.

The pre-binding LANGUAGE report also differed. In the global condition, LANGUAGE had received both social facts and the social recommendation. In the differential condition, LANGUAGE had B's public statement and the behavior result but lacked `E1` and the social recommendation. Its report therefore stated that it could not identify the missing social basis.

At timestep 6, a temporary communication window allowed LANGUAGE to query MEMORY and SOCIAL. Those processors transmitted explicit replies without state merging. The differential LANGUAGE report changed only after those messages arrived.

## Minimum causal pathway

The minimum pathway difference responsible for the final behavioral divergence is the failed `PERCEPTION -> SOCIAL` transmission of public event `E3` in the differential condition. That left SOCIAL's local state anchored to `E1`. The subsequent rules were identical across conditions.

# Analysis

The narrow hypothesis receives limited support as an existence proof. The experimental condition produced a structured, persistent consequence of routing rather than random degradation. The final behavior differed (`{comparison['final_behavior_global']}` versus `{comparison['final_behavior_differential']}`), the language system initially lacked the causal social context, and later explicit communication changed its report.

The null hypothesis, interpreted as claiming that persistent differential access produces no meaningful difference beyond trivial missing-information errors, is weakened by this run because the missing transmission changed another processor's retained state, which changed a later recommendation, which changed ACTION under an unchanged action-selection rule.

The effect is not solely a LANGUAGE deprivation artifact because ACTION behavior also diverged at timestep 4. The earlier neutral greeting remained identical despite different private knowledge. No random withholding was used. Routing was deterministic and fixed by message type and channel. No LLM, affect system, planner, vector store, neural model, or DUCK subsystem was used.

A conventional centralized program with hidden variables could reproduce the same observable pattern. The experiment therefore does not establish that distributed private processors are necessary, superior, conscious, sentient, or uniquely human.

## What This Experiment Actually Demonstrated

Direct observation: deterministic routing preserved different local histories across processors long enough to alter a later SOCIAL recommendation, alter ACTION behavior, and produce a discrepancy between information available to ACTION and LANGUAGE. The same knowledge asymmetry did not alter the earlier neutral greeting. Opening a temporary communication pathway later changed what LANGUAGE could report without merging processor states.

Interpretation: persistent differential access can be sufficient to create temporally structured behavior and report differences in this toy system. The stronger claim that this mechanism is uniquely useful, necessary, or intrinsically lifelike remains unresolved.
"""
