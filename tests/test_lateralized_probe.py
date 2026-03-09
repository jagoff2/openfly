from __future__ import annotations

import numpy as np

from vision.lateralized_probe import (
    build_body_side_mask,
    build_body_side_stimuli,
    compute_mirror_selectivity_scores,
    compute_retina_geometry,
)


def test_body_side_masks_flip_across_eyes() -> None:
    ommatidia_id_map = np.array(
        [
            [1, 1, 2, 2],
            [3, 3, 4, 4],
        ],
        dtype=int,
    )
    geometry = compute_retina_geometry(ommatidia_id_map)

    left_eye_left_mask = build_body_side_mask(geometry, 0, "left", side_fraction=0.49)
    right_eye_left_mask = build_body_side_mask(geometry, 1, "left", side_fraction=0.49)
    left_eye_right_mask = build_body_side_mask(geometry, 0, "right", side_fraction=0.49)
    right_eye_right_mask = build_body_side_mask(geometry, 1, "right", side_fraction=0.49)

    assert left_eye_left_mask.tolist() == [True, False, True, False]
    assert right_eye_left_mask.tolist() == [False, True, False, True]
    assert left_eye_right_mask.tolist() == [False, True, False, True]
    assert right_eye_right_mask.tolist() == [True, False, True, False]


def test_body_side_stimuli_apply_dark_patch_to_expected_locations() -> None:
    ommatidia_id_map = np.array(
        [
            [1, 1, 2, 2],
            [3, 3, 4, 4],
        ],
        dtype=int,
    )
    geometry = compute_retina_geometry(ommatidia_id_map)
    stimuli = build_body_side_stimuli(geometry, baseline_value=1.0, patch_value=0.0, side_fraction=0.49)

    assert stimuli["baseline_gray"].shape == (2, 4)
    assert np.all(stimuli["baseline_gray"] == 1.0)
    assert stimuli["body_left_dark"][0].tolist() == [0.0, 1.0, 0.0, 1.0]
    assert stimuli["body_left_dark"][1].tolist() == [1.0, 0.0, 1.0, 0.0]


def test_mirror_selectivity_scoring_prefers_sign_flipping_candidates() -> None:
    rows = [
        {
            "cell_type": "candidate_a",
            "body_left_left_eye_mean": 2.0,
            "body_left_right_eye_mean": 0.5,
            "body_right_left_eye_mean": 0.4,
            "body_right_right_eye_mean": 2.1,
            "body_center_abs_delta": 0.1,
        },
        {
            "cell_type": "candidate_b",
            "body_left_left_eye_mean": 1.0,
            "body_left_right_eye_mean": 0.9,
            "body_right_left_eye_mean": 0.8,
            "body_right_right_eye_mean": 0.7,
            "body_center_abs_delta": 0.1,
        },
    ]

    ranked = compute_mirror_selectivity_scores(rows)

    assert ranked[0]["cell_type"] == "candidate_a"
    assert ranked[0]["sign_flip_consistent"] is True
    assert ranked[0]["mirror_selectivity_score"] > ranked[1]["mirror_selectivity_score"]
