# Baseline Evidence Matrix

This artifact prevents Champion 0 selection from collapsing into architectural preference or a single aggregate score.

The first comparison cohort is Ensemble, PsychSim, and FAtiMA Toolkit. Additional systems can enter the cohort if software archaeology identifies a stronger complete baseline before Gate C.

## Evidence vocabulary

`OBSERVED STRENGTH`: preserved behavior demonstrates useful performance on the dimension.

`OBSERVED WEAKNESS`: preserved behavior demonstrates a material failure on the dimension.

`MIXED`: behavior is useful in some conditions but fails in others.

`NOT EXPRESSIBLE`: the candidate architecture cannot represent the scenario without adding cognition through the adapter.

`NOT TESTED`: evidence has not yet been collected.

`NATIVE EVIDENCE`: behavior has been observed in an original shipped test, demo, or scenario but not yet in the common battery.

## Current matrix

| Dimension | Ensemble PC-001 | PsychSim PC-003 | FAtiMA PC-002 |
| --- | --- | --- | --- |
| Native execution | EXECUTED, EXP-001 | NOT TESTED | NOT TESTED |
| B01 History Divergence | NOT TESTED | NOT TESTED | NOT TESTED |
| B02 Social Differentiation | NOT TESTED | NOT TESTED | NOT TESTED |
| B03 Unfinished Concern | NOT TESTED | NOT TESTED | NOT TESTED |
| B09 False Belief and Limited Knowledge | NOT TESTED | NOT TESTED | NOT TESTED |
| Emotional inertia | NOT TESTED | NOT TESTED | NOT TESTED |
| Motive competition | NOT TESTED | NOT TESTED | NOT TESTED |
| Consequence learning | NOT TESTED | NOT TESTED | NOT TESTED |
| Spontaneous activity | NOT TESTED | NOT TESTED | NOT TESTED |
| Partner-specific internal state | NATIVE EVIDENCE | NOT TESTED | NOT TESTED |
| Explicit Theory of Mind | NOT TESTED | NATIVE SOURCE EVIDENCE, execution pending | NOT TESTED |
| Decision latency | NOT TESTED | NOT TESTED | NOT TESTED |
| Memory footprint | NOT TESTED | NOT TESTED | NOT TESTED |
| Population scaling | NOT TESTED | NOT TESTED | NOT TESTED |
| Authoring burden | NOT TESTED | NOT TESTED | NOT TESTED |
| License constraint | BSD-4-Clause variant | MIT | Apache-2.0 |

## Champion 0 decision record

Champion 0 remains unassigned until all three candidates have either completed or explicitly failed the following minimum evidence set:

1. Original native execution through a meaningful state transition.
2. Thin-adapter attempt for B01, B02, B03, and B09.
3. Preserved common traces for every expressible core scenario.
4. Initial latency and memory measurement.
5. Artificiality notes identifying the most obvious longitudinal failure.

A candidate does not lose merely because a scenario is NOT EXPRESSIBLE. That result is evaluated relative to the final target. For example, a system with excellent Theory of Mind but no persistent motivational machinery may still be a high-value donor while being a poor whole-system Champion 0.

## Promotion rule

Champion 0 should maximize practical behavioral coverage per unit of complexity while retaining a tractable path for targeted replacement of weak mechanisms.

Selection should favor demonstrated longitudinal behavioral leverage, not module count, publication prestige, recency, implementation language, or ease of integration.

If no candidate provides a defensible whole-system starting point, record `NO CHAMPION SELECTED` and qualify the next complete candidate rather than manufacturing an internal architecture to fill the slot.
