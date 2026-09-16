# EXP-008 Development Pass 1

Run: `35052130403`  
Artifact: `10429581428` (`exp008-development`)  
Result: **FAIL**

Repository regression tests: pass.  
Historical earned behavior: pass.  
EXP-007 development behavior: pass.  
Renderer invariance: pass.  
Base pressures: pass.  
Causal ablations: pass.  
Zero new object fields: pass.  
Zero new counted mechanisms: pass.

The selected repeated-failed-search target itself passed. The frozen champion continued searching the believed location after its action value reached `-1.0`; the challenger accumulated `-0.35`, `-0.70`, then `-1.0` and subsequently selected the alternative location while leaving the factual location belief unchanged. Entity specificity, task specificity, action-order invariance, direct reobservation, delayed outcome compatibility, positive outcome learning, and unlabeled delayed abstention also passed.

Three development gates failed and are preserved here before correction.

## 1. Contradictory-outcome test design violated inherited ambiguity semantics

The test first allowed the challenger to choose the alternative search action after negative learning, then forced the original search action and supplied a positive outcome. At that moment the bounded trace contained two live actions for the same derived context. EXP-007 explicitly established that a same-context outcome with multiple plausible live actions must conservatively abstain. The unchanged `-1.0` value was therefore the correct inherited behavior, not a failure of reversibility.

Correction: test reversibility from an identical pre-choice serialized state. Use one reconstructed copy to demonstrate that the learned negative state would choose the alternative, while the original receives later forced positive experiences without first introducing a competing same-context action. No production change is justified by this test failure.

## 2. Unknown-entity positive-learning test design also introduced ambiguity

The test made an initial unknown-location choice (`search:desk`), then forced `search:shelf`, leaving both actions live in the same derived context before the positive outcome. EXP-007 correctly abstained from assigning the outcome because two actions were plausible.

Correction: separate the unknown-location tie-control and the positive-experience learning control into identical fresh agents. The positive-learning agent receives only the forced candidate before its outcome. No production change is justified by this test failure.

## 3. Derived-context encoding broke the frozen persistence codec

This is a genuine challenger implementation defect.

The challenger encoded search experience as:

`search_task:<task>|entity:<actor>`

The compact persistence codec serializes habit keys as:

`<context>|<action>`

and reconstructs them by splitting on the first `|`. The challenger therefore introduced a reserved delimiter into the existing context string. Before serialization, behavior was correct. After restoration, the habit key was reconstructed with a truncated context and malformed action, causing persistent state divergence and later behavioral divergence.

This defect does not require new state or a changed scientific hypothesis. It is an unsafe string encoding within the preregistered derived-context implementation detail.

Correction: use a deterministic delimiter-safe encoding for task and entity components so the derived context cannot contain the persistence codec's `|` separator. Restart the complete development validation after correction.

## Scientific classification

- Core hypothesis falsified: **no**
- Production behavior correction required: **yes, encoding only**
- New persistent field required: **no**
- New cognitive mechanism required: **no**
- Historical behavior regression: **no**
- First-pass failure preserved: **yes**
