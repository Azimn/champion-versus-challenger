# Metabolic Information Asymmetry

This experiment extends PR 14's persistent-information-asymmetry prototype with the smallest resource mechanism capable of testing an interaction between cognitive scarcity and differential information access.

It is not the full PEMA architecture. It deliberately excludes actor bidding, multiple resource classes, hoarding, learning, fatigue, persistent concerns, vector-state deformation, coalition formation, and LLMs. The only new causal mechanism is a single finite internal resource consumed by selected inter-processor communication and assimilation.

## Research question

Does making internal communication metabolically costly create additional persistent information asymmetry, and does that effect interact with the hard communication topology?

The four canonical conditions form a 2 by 2 design:

| Access | Resources | Label |
|---|---|---|
| Global broadcast | Abundant | GB-A |
| Global broadcast | Scarce | GB-S |
| Differential access | Abundant | DA-A |
| Differential access | Scarce | DA-S |

All conditions use the same processors, scenario, action-selection rule, local state, and message semantics. Only routing permission and resource availability vary.

## Resource model

Every cognitive processor begins with the same finite resource balance. The abundant condition assigns 100 units per processor. The canonical scarce condition assigns 6.

A social-fact transmission costs the sender one unit per topology-eligible recipient and the receiver one unit to assimilate it. Recommendation and temporary-binding messages use the same 1-unit send and 1-unit assimilation cost.

Task prompts, environment injection, research interview messages, and behavior observation are cost-exempt. This prevents the manipulation from starving the task itself or hiding the selected behavior from the researcher.

Workspace broadcasts are funded atomically at the sender. If the sender cannot afford the complete topology-eligible broadcast, none of its intended recipients receive that message. This avoids an arbitrary recipient-order effect.

There is no replenishment in this first experiment. Resource accounting must satisfy:

`initial total = current total + consumed total`

exactly.

## Why six units is the canonical scarce condition

For PERCEPTION in the existing scenario, global broadcast requires four units to distribute private event E1 and another four units to distribute public update E3. Differential routing requires two units for E1 and three units for E3.

At six units, both architectures can transmit E1. Differential routing can still finance its permitted E3 routes, while global broadcast cannot finance the second four-recipient broadcast.

The experiment also sweeps capacities from 4 through 10 so this result can be inspected across the relevant thresholds rather than relying only on the six-unit choice.

## Run

From the repository root:

```bash
python -m cvc_research.experiments.information_asymmetry.metabolic_main \
  --output research/experiments/metabolic-information-asymmetry/artifacts

python -m unittest discover -s tests -p 'test_metabolic_information_asymmetry.py' -v
```

The runner writes the four complete deterministic traces as gzip JSON, a matrix summary, and the capacity sweep.

## Falsification interpretation

This experiment should not be read as evidence for the complete internal-resource-economy proposal. A positive result establishes only that a finite communication resource can create resource-induced information asymmetry and can interact with routing topology.

The stronger PEMA hypothesis remains untested until actors themselves generate resource demand from local cognitive operations and resource allocation changes future information access endogenously.
