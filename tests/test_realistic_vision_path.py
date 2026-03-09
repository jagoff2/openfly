from __future__ import annotations

from dataclasses import replace
import numpy as np

from body.interfaces import BodyObservation
from bridge.controller import ClosedLoopBridge
from brain.mock_backend import MockWholeBrainBackend
from vision.feature_extractor import RealisticVisionFeatureExtractor, VisionFeatures
from vision.inferred_lateralized import InferredLateralizedFeatureExtractor


def test_realistic_vision_extractor_uses_nn_activity_channels() -> None:
    extractor = RealisticVisionFeatureExtractor()
    features = extractor.extract({"T2": [[0.1, 0.2], [0.8, 1.0]], "Tm1": [[0.2, 0.3], [0.7, 0.9]], "T4a": [[0.0, 0.1], [0.4, 0.5]], "T5a": [[0.0, 0.1], [0.4, 0.5]]})
    assert features.salience_right > features.salience_left
    assert features.forward_salience > 0.0


def test_realistic_vision_fast_path_matches_mapping_path() -> None:
    extractor = RealisticVisionFeatureExtractor(tracking_cells=["T2", "Tm1"], flow_cells=["T4a", "T5a"])
    nn_mapping = {
        "T2": np.array([[0.1, 0.2], [0.8, 1.0]], dtype=float),
        "Tm1": np.array([[0.2, 0.3], [0.7, 0.9]], dtype=float),
        "T4a": np.array([[0.0, 0.1], [0.4, 0.5]], dtype=float),
        "T5a": np.array([[0.0, 0.1], [0.4, 0.5]], dtype=float),
    }
    node_types = np.array(["T2", "Tm1", "T4a", "T5a"], dtype=object)
    cache = extractor.build_index_cache(node_types)
    nn_array = np.stack(
        [
            nn_mapping["T2"].mean(axis=1),
            nn_mapping["Tm1"].mean(axis=1),
            nn_mapping["T4a"].mean(axis=1),
            nn_mapping["T5a"].mean(axis=1),
        ],
        axis=1,
    )

    legacy = extractor.extract(nn_mapping)
    fast = extractor.extract_from_array(nn_array, cache)

    assert fast.salience_left == legacy.salience_left
    assert fast.salience_right == legacy.salience_right
    assert fast.flow_left == legacy.flow_left
    assert fast.flow_right == legacy.flow_right


def test_realistic_vision_extractor_prefers_precomputed_fast_features() -> None:
    extractor = RealisticVisionFeatureExtractor()
    observation = BodyObservation(
        sim_time=0.0,
        position_xy=(0.0, 0.0),
        yaw=0.0,
        forward_speed=0.0,
        yaw_rate=0.0,
        contact_force=0.0,
        realistic_vision={"T2": [0.1, 0.9]},
        realistic_vision_features=VisionFeatures(0.3, 0.7, -0.2, 0.4).to_dict(),
        vision_payload_mode="fast",
    )

    features = extractor.extract_observation(observation)

    assert np.isclose(features.salience_left, 0.3)
    assert np.isclose(features.salience_right, 0.7)
    assert np.isclose(features.flow_left, -0.2)
    assert np.isclose(features.flow_right, 0.4)


def test_fast_and_legacy_control_outputs_match_exactly_for_same_input() -> None:
    extractor = RealisticVisionFeatureExtractor(tracking_cells=["T2", "Tm1"], flow_cells=["T4a", "T5a"])
    nn_mapping = {
        "T2": np.array([[0.1, 0.2], [0.8, 1.0]], dtype=float),
        "Tm1": np.array([[0.2, 0.3], [0.7, 0.9]], dtype=float),
        "T4a": np.array([[0.0, 0.1], [0.4, 0.5]], dtype=float),
        "T5a": np.array([[0.0, 0.1], [0.4, 0.5]], dtype=float),
    }
    node_types = np.array(["T2", "Tm1", "T4a", "T5a"], dtype=object)
    cache = extractor.build_index_cache(node_types)
    nn_array = np.stack(
        [
            nn_mapping["T2"].mean(axis=1),
            nn_mapping["Tm1"].mean(axis=1),
            nn_mapping["T4a"].mean(axis=1),
            nn_mapping["T5a"].mean(axis=1),
        ],
        axis=1,
    )
    legacy_observation = BodyObservation(
        sim_time=0.0,
        position_xy=(0.0, 0.0),
        yaw=0.0,
        forward_speed=0.25,
        yaw_rate=-0.1,
        contact_force=0.8,
        realistic_vision=nn_mapping,
        realistic_vision_array=nn_array,
        realistic_vision_index_cache=cache,
        vision_payload_mode="legacy",
    )
    fast_observation = replace(
        legacy_observation,
        realistic_vision={},
        realistic_vision_features=extractor.extract(nn_mapping).to_dict(),
        vision_payload_mode="fast",
    )

    legacy_bridge = ClosedLoopBridge(MockWholeBrainBackend(), vision_extractor=extractor)
    fast_bridge = ClosedLoopBridge(MockWholeBrainBackend(), vision_extractor=extractor)
    legacy_readout, legacy_info = legacy_bridge.step(legacy_observation, num_brain_steps=20)
    fast_readout, fast_info = fast_bridge.step(fast_observation, num_brain_steps=20)

    assert fast_info["vision_features"] == legacy_info["vision_features"]
    assert fast_info["sensor_pool_rates"] == legacy_info["sensor_pool_rates"]
    assert fast_info["sensor_metadata"] == legacy_info["sensor_metadata"]
    assert fast_readout.neuron_rates == legacy_readout.neuron_rates
    assert fast_readout.command.left_drive == legacy_readout.command.left_drive
    assert fast_readout.command.right_drive == legacy_readout.command.right_drive


def test_realistic_vision_extractor_can_attach_inferred_turn_features_from_array() -> None:
    inferred_turn_extractor = InferredLateralizedFeatureExtractor.from_probe_csv(
        "outputs/metrics/inferred_lateralized_visual_candidates.csv",
        min_score=0.02,
        tracking_limit=1,
        flow_limit=1,
    )
    extractor = RealisticVisionFeatureExtractor(
        tracking_cells=["TmY14"],
        flow_cells=["T5d"],
        inferred_turn_extractor=inferred_turn_extractor,
    )
    node_types = np.array(["TmY14", "T5d"], dtype=object)
    cache = extractor.build_index_cache(node_types)
    nn_array = np.array([[3.0, 4.0], [1.0, 1.0]], dtype=float)

    features = extractor.extract_from_array(nn_array, cache)

    assert features.inferred_turn_bias > 0.0
    assert features.inferred_right_evidence > 0.0
    assert features.inferred_left_evidence == 0.0
    assert features.inferred_candidate_count == 2
