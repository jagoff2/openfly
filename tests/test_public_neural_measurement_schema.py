from __future__ import annotations

from analysis.public_neural_measurement_schema import (
    CanonicalDatasetBundle,
    CanonicalNeuronTrace,
    CanonicalStimulus,
    CanonicalTrial,
    canonical_schema_reference,
)


def test_canonical_schema_reference_exposes_required_sections() -> None:
    reference = canonical_schema_reference()
    assert "dataset_level" in reference
    assert "trial_level" in reference
    assert "trace_level" in reference
    assert reference["required_splits"] == ["train", "val", "test"]


def test_canonical_dataset_bundle_serializes_nested_objects() -> None:
    bundle = CanonicalDatasetBundle(
        dataset_key="test",
        citation_label="Test",
        modality="calcium",
        normalization={"trace_transform": "dff"},
        identity_strategy={"primary": "cell_type"},
        trials=(
            CanonicalTrial(
                trial_id="trial-1",
                split="train",
                behavior_context="walking",
                stimulus=CanonicalStimulus(
                    stimulus_family="optic_flow",
                    stimulus_name="front_to_back",
                    units="mm_s",
                    parameters={"speed": -4.0},
                ),
                timebase_path="trial-1/time.npy",
                traces=(
                    CanonicalNeuronTrace(
                        trace_id="trace-1",
                        recorded_entity_id="T5a",
                        recorded_entity_type="cell_type",
                        hemisphere="L",
                        trace_index=0,
                        sampling_rate_hz=20.0,
                        units="dff",
                        transform="zscore",
                        values_path="trial-1/trace-1.npy",
                    ),
                ),
            ),
        ),
    )
    payload = bundle.to_dict()
    assert payload["dataset_key"] == "test"
    assert payload["trials"][0]["stimulus"]["stimulus_name"] == "front_to_back"
    assert payload["trials"][0]["traces"][0]["recorded_entity_id"] == "T5a"
    assert payload["trials"][0]["traces"][0]["trace_index"] == 0
