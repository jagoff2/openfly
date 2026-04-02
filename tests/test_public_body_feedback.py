from __future__ import annotations

import numpy as np
import pytest

from analysis.public_body_feedback import (
    PublicBodyFeedbackChannels,
    public_body_feedback_from_aimon_regressor,
    public_body_feedback_from_schaffer_covariates,
    public_body_observation_from_channels,
)
from bridge.encoder import EncoderConfig, SensoryEncoder
from vision.feature_extractor import VisionFeatures


def test_public_body_feedback_from_aimon_regressor_derives_transition_channels() -> None:
    channels = public_body_feedback_from_aimon_regressor(
        timebase_s=np.asarray([0.0, 0.5, 1.0], dtype=np.float32),
        regressor_values=np.asarray([0.0, 0.5, 1.0], dtype=np.float32),
        sample_index=1,
        forward_speed_scale=2.0,
        contact_force_scale=3.0,
    )

    assert channels.forward_speed == 1.0
    assert channels.contact_force == 1.5
    assert channels.forward_accel == 2.0
    assert channels.walk_state == 0.5
    assert channels.stop_state == 0.5
    assert channels.transition_on == 1.0
    assert channels.transition_off == 0.0
    assert channels.behavioral_state_level == 0.5
    assert channels.behavioral_state_transition == 0.0


def test_public_body_feedback_from_schaffer_covariates_uses_ball_and_state_summary() -> None:
    channels = public_body_feedback_from_schaffer_covariates(
        timebase_s=np.asarray([0.0, 0.5, 1.0], dtype=np.float32),
        ball_motion_values=np.asarray([0.0, 0.5, 1.0], dtype=np.float32),
        behavioral_state_values=np.asarray(
            [
                [0.0, 1.0, 1.0],
                [0.0, 0.2, 0.4],
            ],
            dtype=np.float32,
        ),
        sample_index=1,
        forward_speed_scale=2.0,
        contact_force_scale=3.0,
    )

    assert channels.forward_speed == 1.0
    assert channels.contact_force == pytest.approx(channels.walk_state * 3.0)
    assert channels.forward_accel == 2.0
    assert 0.5 < channels.walk_state < 1.0
    assert 0.0 < channels.stop_state < 0.5
    assert channels.transition_on == 1.0
    assert channels.transition_off == 0.0
    assert channels.behavioral_state_level > 0.7
    assert channels.behavioral_state_transition > 0.0


def test_public_body_observation_from_channels_reaches_encoder_mechanosensory_path() -> None:
    observation = public_body_observation_from_channels(
        sim_time_s=0.25,
        channels=PublicBodyFeedbackChannels(
            forward_speed=1.0,
            contact_force=0.5,
            forward_accel=0.75,
            walk_state=0.8,
            stop_state=0.1,
            transition_on=0.3,
            transition_off=0.0,
            behavioral_state_level=0.6,
            behavioral_state_transition=0.2,
        ),
        metadata={"source": "unit-test"},
    )

    encoder = SensoryEncoder(
        EncoderConfig(
            speed_gain_hz=2.0,
            contact_gain_hz=3.0,
            accel_gain_hz=5.0,
            state_gain_hz=7.0,
            transition_gain_hz=11.0,
            stop_suppression_hz=13.0,
        )
    )
    encoding = encoder.encode(observation, VisionFeatures(0.0, 0.0, 0.0, 0.0))

    expected_bilateral = (
        (3.0 * 0.5)
        + (2.0 * 1.0 + 5.0 * 0.75 + 11.0 * 0.3)
        + (7.0 * 0.8 - 13.0 * 0.1)
    )
    assert encoding.pool_rates["mech_left"] == pytest.approx(expected_bilateral)
    assert encoding.pool_rates["mech_right"] == pytest.approx(expected_bilateral)
    assert encoding.metadata["forward_accel"] == 0.75
    assert encoding.metadata["walk_state"] == 0.8
    assert encoding.metadata["behavioral_state_level"] == 0.6
    assert encoding.metadata["mech_ce_bilateral"] == pytest.approx(1.5)
    assert encoding.metadata["mech_f_bilateral"] > 0.0
    assert encoding.metadata["mech_dm_bilateral"] > 0.0
    assert observation.metadata["public_body_feedback"]["walk_state"] == 0.8
