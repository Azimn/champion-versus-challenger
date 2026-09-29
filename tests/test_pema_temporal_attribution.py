from cvc_research.experiments.information_asymmetry.developmental_world import (
    EPOCH_TICKS,
    WORLD_SEEDS,
    generate_history,
    opportunity_signature,
)
from cvc_research.experiments.information_asymmetry.temporal_attribution import (
    non_temporal_signature,
    temporal_only_history,
)


def test_temporal_only_preserves_all_preregistered_non_temporal_content():
    for seed in WORLD_SEEDS:
        source = generate_history(seed)
        transformed = temporal_only_history(source)
        assert len(transformed) == len(source)
        assert non_temporal_signature(transformed) == non_temporal_signature(source)
        assert opportunity_signature(transformed) == opportunity_signature(source)
        assert temporal_only_history(transformed) == transformed


def test_temporal_only_uses_exact_inherited_offsets_for_every_seed():
    changed = False
    for seed in WORLD_SEEDS:
        source = generate_history(seed)
        transformed = temporal_only_history(source)
        changed = changed or transformed != source
        for event in transformed:
            expected = event.epoch * EPOCH_TICKS + (1 if event.role == "PRIVATE" else 6)
            assert event.born_tick == expected
    assert changed
