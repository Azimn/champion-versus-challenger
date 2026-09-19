from cvc_research.experiments.information_asymmetry.developmental_world import (
    EPOCH_COUNT,
    WORLD_SEEDS,
    deserialize_history,
    generate_history,
    opportunity_signature,
    serialize_history,
)


def test_all_preregistered_histories_have_exact_opportunity_counts():
    reference = opportunity_signature(generate_history(WORLD_SEEDS[0]))
    assert len(reference) == EPOCH_COUNT * 2
    for seed in WORLD_SEEDS:
        history = generate_history(seed)
        assert len(history) == EPOCH_COUNT * 2
        assert opportunity_signature(history) == reference
        for epoch in range(EPOCH_COUNT):
            events = [event for event in history if event.epoch == epoch]
            assert len(events) == 2
            assert {event.channel for event in events} == {"private", "public"}
            assert {event.role for event in events} == {"PRIVATE", "PUBLIC"}


def test_history_is_deterministic_and_serialization_is_canonical():
    first = generate_history(1103)
    second = generate_history(1103)
    assert first == second
    encoded = serialize_history(first)
    assert serialize_history(second) == encoded
    assert deserialize_history(encoded) == first
    assert serialize_history(deserialize_history(encoded)) == encoded


def test_fresh_instances_do_not_share_mutable_generator_state():
    before = serialize_history(generate_history(2207))
    _ = generate_history(3301)
    after = serialize_history(generate_history(2207))
    assert before == after


def test_seeds_change_informational_history_not_opportunity_structure():
    histories = [generate_history(seed) for seed in WORLD_SEEDS]
    payloads = {serialize_history(history) for history in histories}
    assert len(payloads) == len(WORLD_SEEDS)
    signatures = {opportunity_signature(history) for history in histories}
    assert len(signatures) == 1


def test_unregistered_seed_is_rejected():
    try:
        generate_history(1)
    except ValueError as exc:
        assert "preregistered" in str(exc)
    else:
        raise AssertionError("unregistered seed must not be accepted")
