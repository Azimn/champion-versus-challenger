"""Execute a native PsychSim Theory of Mind path without modifying PsychSim.

PsychSim commit c7b2b92 ships a stale unit test whose reward helper calls no
longer match the reward.py API at the same commit. This harness reconstructs
that test's intended behavior using the pinned source's current function
signatures. It changes no PsychSim source or decision logic.
"""

from __future__ import print_function

import json
import os

from psychsim.agent import Agent
from psychsim.probability import Distribution
from psychsim.pwl import stateKey, modelKey, makeTree, incrementMatrix
from psychsim.reward import maximizeFeature, minimizeFeature
from psychsim.world import World


def probability_of_model(agent, belief_dist, model_name):
    key = modelKey(agent.name)
    for belief in belief_dist.domain():
        if agent.index2model(belief[key]) == model_name:
            return belief_dist[belief]
    raise AssertionError("Model %s not present in belief distribution" % model_name)


def main():
    world = World()
    tom = Agent("Tom")
    jerry = Agent("Jerry")
    world.addAgent(tom)
    world.addAgent(jerry)

    world.defineState(tom.name, "health", int, lo=0, hi=100)
    world.setState(tom.name, "health", 50)
    world.defineState(jerry.name, "health", int, lo=0, hi=100)
    world.setState(jerry.name, "health", 50)

    chase = tom.addAction({"verb": "chase", "object": jerry.name})
    hit = tom.addAction({"verb": "hit", "object": jerry.name})
    jerry.addAction({"verb": "run away"})
    jerry.addAction({"verb": "trick", "object": tom.name})

    tree = makeTree(incrementMatrix(stateKey(jerry.name, "health"), -10))
    world.setDynamics(stateKey(jerry.name, "health"), hit, tree, enforceMin=True)

    tom.addModel("friend", rationality=1.0, parent=True)
    tom.setReward(
        maximizeFeature(stateKey(jerry.name, "health"), tom.name),
        1.0,
        "friend",
    )
    tom.addModel("foe", rationality=1.0, parent=True)
    tom.setReward(
        minimizeFeature(stateKey(jerry.name, "health"), tom.name),
        1.0,
        "foe",
    )

    world.setOrder([tom.name])
    world.setModel(jerry.name, True)
    world.setMentalModel(jerry.name, tom.name, {"friend": 0.5, "foe": 0.5})

    actions = {tom.name: hit}
    world.step(actions)
    vector = world.state[None].domain()[0]
    jerry_model = world.getModel(jerry.name, vector)
    belief01 = jerry.getAttribute("beliefs", jerry_model)
    prob01 = probability_of_model(tom, belief01, "foe")
    assert prob01 > 0.5, "A hostile action should increase Jerry's belief that Tom is a foe"

    tom.setAttribute("rationality", 10.0, "foe")
    tom.setAttribute("rationality", 10.0, "friend")
    world.setMentalModel(jerry.name, tom.name, {"friend": 0.5, "foe": 0.5})
    world.step(actions)
    vector = world.state[None].domain()[0]
    jerry_model = world.getModel(jerry.name, vector)
    belief10 = jerry.getAttribute("beliefs", jerry_model)
    prob10 = probability_of_model(tom, belief10, "foe")
    assert prob10 > prob01, "Higher assumed rationality should strengthen model inference"

    world.step(actions)
    vector = world.state[None].domain()[0]
    jerry_model = world.getModel(jerry.name, vector)
    belief1010 = jerry.getAttribute("beliefs", jerry_model)
    prob1010 = probability_of_model(tom, belief1010, "foe")
    assert prob1010 > prob10, "Repeated hostile evidence should further strengthen foe belief"

    result = {
        "candidate_id": "PC-003",
        "candidate": "PsychSim",
        "upstream_commit": "c7b2b92e6ff8b83b2e832acda02c4baafabdf06f",
        "execution_type": "NATIVE THEORY-OF-MIND COMPATIBILITY RECONSTRUCTION",
        "architecture_modified": False,
        "candidate_source_modified": False,
        "adapter_used": False,
        "source_test_reference": "psychsim/test/tomjerry.py::TestAgents.testRewardModels",
        "compatibility_difference": "reward helper calls include the agent argument required by reward.py at the same pinned commit",
        "observations": {
            "foe_probability_after_first_hit": prob01,
            "foe_probability_after_high_rationality_hit": prob10,
            "foe_probability_after_repeated_hit": prob1010,
        },
        "status": "EXECUTED",
    }

    os.makedirs("qualification-results", exist_ok=True)
    with open("qualification-results/psychsim-native-tom.json", "w") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
