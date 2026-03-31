from __future__ import annotations

import numpy as np
import pytest

from analysis.imaging_observation_model import (
    augment_feature_matrix_with_observation_basis,
    normalize_observation_taus,
)


def test_normalize_observation_taus_deduplicates_and_preserves_order() -> None:
    assert normalize_observation_taus([0.3, 1.0, 0.3]) == (0.3, 1.0)


def test_normalize_observation_taus_rejects_nonpositive_values() -> None:
    with pytest.raises(ValueError, match="must be positive"):
        normalize_observation_taus([0.0, 0.5])


def test_augment_feature_matrix_with_observation_basis_appends_causal_lowpass() -> None:
    feature_matrix = np.asarray([[0.0, 1.0, 0.0, 1.0]], dtype=np.float32)
    timebase_s = np.asarray([0.0, 1.0, 2.0, 3.0], dtype=np.float32)
    augmented, names = augment_feature_matrix_with_observation_basis(
        feature_matrix,
        timebase_s,
        observation_taus_s=(1.0,),
        feature_names=("f0",),
    )
    assert augmented.shape == (2, 4)
    np.testing.assert_allclose(augmented[0], feature_matrix[0], atol=1e-6)
    expected = np.empty(4, dtype=np.float32)
    expected[0] = 0.0
    alpha = float(np.exp(-1.0))
    expected[1] = (1.0 - alpha) * 1.0
    expected[2] = alpha * expected[1]
    expected[3] = alpha * expected[2] + (1.0 - alpha) * 1.0
    np.testing.assert_allclose(augmented[1], expected, atol=1e-6)
    assert names == ("f0", "f0::obs_lp_tau_1s")
