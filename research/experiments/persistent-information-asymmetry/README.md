# Persistent Information Asymmetry as a Source of Lifelike Cognitive Effects

This directory contains a small, disposable experiment that tests one narrow hypothesis: persistent information asymmetry between semi-independent processors can produce structured behavioral and reporting effects that are absent or different under global broadcast.

This is not a DUCK refactor, not a replacement architecture, and not a model of consciousness. It deliberately excludes LLMs, neural models, vector databases, affect systems, planners, autobiographical memory systems, and other machinery that is unnecessary for the causal test.

## Experimental design

The prototype contains five processors: PERCEPTION, SOCIAL, MEMORY, ACTION, and LANGUAGE. Every processor owns private state. Processors do not hold references to peers, the router, the experiment runner, or objective ground truth. Inter-processor information transfer occurs only through explicit messages, and every attempted route is logged as succeeded or blocked.

The global-broadcast control sends every workspace-eligible event or inference to every other processor. The differential-access condition uses a deterministic routing topology. Private social facts reach SOCIAL and MEMORY. Public social facts reach MEMORY, ACTION, and LANGUAGE. SOCIAL recommendations reach ACTION. ACTION behavior reports reach LANGUAGE. A one-timestep temporary coordination window later permits explicit LANGUAGE queries to MEMORY and SOCIAL.

The deterministic scenario first gives A a private statement about B's dislike of birthday surprises, then asks for a neutral greeting, then gives B a public contradictory update welcoming a birthday surprise, and finally asks ACTION to choose how to proceed. LANGUAGE is interviewed before and after the temporary coordination window.

## Run

From the repository root:

```bash
python -m cvc_research.experiments.information_asymmetry \
  --output research/experiments/persistent-information-asymmetry/artifacts
python -m unittest discover -s tests -p 'test_information_asymmetry.py' -v
```

The generated artifacts are deterministic. Each condition is emitted as a manifest plus one JSON file per timestep for direct audit. The same complete runs are also written as deterministic `trace_global.json.gz` and `trace_differential.json.gz` snapshots for compact storage. Re-running the experiment should reproduce the committed trace snapshots byte for byte.

## Researcher instrumentation boundary

The experiment runner may serialize processor-local state for evaluation, but processors cannot inspect that researcher view. The objective scenario definition is stored separately and is delivered to cognition only through explicit environment-to-PERCEPTION messages. The router stores message records but no processor state.

## Reference material

CTM-AI official project site: https://consciousness-lab.github.io/

CTM-AI repository: https://github.com/consciousness-lab/ctm-ai

CTM-AI paper: https://arxiv.org/abs/2605.04097

Lenore Blum and Manuel Blum, A Theory of Consciousness from a Theoretical Computer Science Perspective: Insights from the Conscious Turing Machine: https://pmc.ncbi.nlm.nih.gov/articles/PMC9171770/

James Newman, Putting the Puzzle Together: Towards a General Theory of the Neural Correlates of Consciousness: https://www.jstage.jst.go.jp/article/jcss/4/3/4_3_3_15/_article

Nengo basal ganglia example: https://www.nengo.ai/nengo/examples/networks/basal-ganglia.html

Nengo reusable networks, including BasalGanglia and Thalamus: https://www.nengo.ai/nengo/networks.html

These sources are conceptual donors only. No donor code is imported into this experiment.
