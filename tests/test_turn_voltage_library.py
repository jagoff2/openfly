from __future__ import annotations

import pandas as pd
import numpy as np

from analysis.brain_latent_library import (
    apply_state_binned_ranking_adjustments,
    build_matched_turn_latent_ranking,
    build_state_binned_turn_metrics,
)
from analysis.turn_voltage_library import (
    apply_baseline_asymmetry_from_voltage_matrix,
    build_turn_voltage_signal_library,
)


def test_build_turn_voltage_signal_library_can_prune_and_reweight_groups() -> None:
    ranked = pd.DataFrame(
        [
            {
                "label": "RelayA",
                "target_specificity_score": 0.9,
                "corr_target_bearing": 0.8,
                "corr_drive_asymmetry": -0.4,
            },
            {
                "label": "RelayB",
                "target_specificity_score": 0.8,
                "corr_target_bearing": -0.7,
                "corr_drive_asymmetry": 0.5,
            },
            {
                "label": "RelayC",
                "target_specificity_score": 0.7,
                "corr_target_bearing": 0.6,
                "corr_drive_asymmetry": -0.2,
            },
        ]
    )
    metadata = {
        "RelayA": {"left_root_ids": [1], "right_root_ids": [2], "super_class": "visual_projection"},
        "RelayB": {"left_root_ids": [3], "right_root_ids": [4], "super_class": "visual_projection"},
        "RelayC": {"left_root_ids": [5], "right_root_ids": [6], "super_class": "visual_projection"},
    }
    target_turn = pd.DataFrame(
        [
            {"label": "RelayA", "mean_abs_asymmetry_voltage_mv": 1.0},
            {"label": "RelayB", "mean_abs_asymmetry_voltage_mv": 100.0},
            {"label": "RelayC", "mean_abs_asymmetry_voltage_mv": 4.0},
        ]
    ).set_index("label")

    library = build_turn_voltage_signal_library(
        ranked,
        metadata,
        top_k=3,
        target_turn=target_turn,
        include_labels=["RelayA", "RelayB", "RelayC"],
        exclude_labels=["RelayB"],
        weight_mode="score_over_sqrt_asym",
        downweight_labels={"RelayC": 0.5},
    )

    groups = {item["label"]: item for item in library["selected_groups"]}
    assert set(groups) == {"RelayA", "RelayC"}
    assert groups["RelayA"]["turn_weight"] > 0.0
    assert groups["RelayC"]["turn_weight"] > 0.0
    assert abs(groups["RelayA"]["turn_weight"]) > abs(groups["RelayC"]["turn_weight"])


def test_build_turn_voltage_signal_library_accepts_turn_specificity_score() -> None:
    ranked = pd.DataFrame(
        [
            {
                "label": "RelayA",
                "turn_specificity_score": 1.2,
                "corr_target_bearing": 0.75,
                "corr_drive_asymmetry": -0.25,
            },
            {
                "label": "RelayB",
                "turn_specificity_score": 0.6,
                "corr_target_bearing": -0.5,
                "corr_drive_asymmetry": 0.2,
            },
        ]
    )
    metadata = {
        "RelayA": {"left_root_ids": [1], "right_root_ids": [2], "super_class": "visual_projection"},
        "RelayB": {"left_root_ids": [3], "right_root_ids": [4], "super_class": "visual_projection"},
    }

    library = build_turn_voltage_signal_library(ranked, metadata, top_k=2)
    groups = {item["label"]: item for item in library["selected_groups"]}

    assert groups["RelayA"]["target_specificity_score"] == 1.2
    assert groups["RelayB"]["target_specificity_score"] == 0.6
    assert abs(groups["RelayA"]["turn_weight"]) > abs(groups["RelayB"]["turn_weight"])
    assert groups["RelayA"]["turn_weight"] > 0.0
    assert groups["RelayB"]["turn_weight"] < 0.0


def test_apply_baseline_asymmetry_from_voltage_matrix_adds_group_baselines() -> None:
    signal_library = {
        "selected_groups": [
            {
                "label": "RelayA",
                "left_root_ids": [1],
                "right_root_ids": [2],
            },
            {
                "label": "RelayB",
                "left_root_ids": [3],
                "right_root_ids": [4],
            },
        ]
    }
    monitored_root_ids = np.asarray([1, 2, 3, 4], dtype=np.int64)
    monitored_voltage_matrix = np.asarray(
        [
            [-50.0, -49.0],
            [-47.0, -46.0],
            [-60.0, -61.0],
            [-61.5, -62.5],
        ],
        dtype=np.float32,
    )

    corrected = apply_baseline_asymmetry_from_voltage_matrix(
        signal_library,
        monitored_root_ids,
        monitored_voltage_matrix,
    )
    groups = {item["label"]: item for item in corrected["selected_groups"]}

    assert groups["RelayA"]["baseline_asymmetry_mv"] == 3.0
    assert groups["RelayB"]["baseline_asymmetry_mv"] == -1.5


def test_build_matched_turn_latent_ranking_prefers_target_specific_over_generic_bias() -> None:
    target_turn = pd.DataFrame(
        [
            {
                "label": "RelayTarget",
                "corr_target_bearing": 0.9,
                "corr_drive_asymmetry": 0.6,
                "corr_forward_speed": 0.1,
                "mean_voltage_mv": -50.0,
                "mean_abs_asymmetry_voltage_mv": 2.0,
            },
            {
                "label": "RelayBiased",
                "corr_target_bearing": 0.85,
                "corr_drive_asymmetry": 0.55,
                "corr_forward_speed": 0.05,
                "mean_voltage_mv": -49.0,
                "mean_abs_asymmetry_voltage_mv": 2.0,
            },
        ]
    )
    no_target_turn = pd.DataFrame(
        [
            {
                "label": "RelayTarget",
                "corr_target_bearing": 0.0,
                "corr_drive_asymmetry": 0.05,
                "corr_forward_speed": 0.0,
                "mean_voltage_mv": -50.0,
                "mean_abs_asymmetry_voltage_mv": 0.3,
            },
            {
                "label": "RelayBiased",
                "corr_target_bearing": 0.0,
                "corr_drive_asymmetry": 0.7,
                "corr_forward_speed": 0.0,
                "mean_voltage_mv": -49.0,
                "mean_abs_asymmetry_voltage_mv": 1.9,
            },
        ]
    )

    ranked = build_matched_turn_latent_ranking(
        target_turn_table=target_turn,
        no_target_turn_table=no_target_turn,
        min_target_corr=0.1,
    )

    assert list(ranked["label"]) == ["RelayTarget", "RelayBiased"]
    assert float(ranked.iloc[0]["target_specificity_score"]) > float(ranked.iloc[1]["target_specificity_score"])
    assert float(ranked.iloc[0]["generic_turn_bias_penalty"]) < float(ranked.iloc[1]["generic_turn_bias_penalty"])


def test_build_state_binned_turn_metrics_reports_low_high_bin_correlations() -> None:
    capture = {
        "monitored_root_ids": np.asarray([1, 2], dtype=np.int64),
        "monitored_voltage_matrix": np.asarray(
            [
                [-52.0, -52.0, -52.0, -52.0],
                [-51.0, -50.0, -51.0, -50.0],
            ],
            dtype=np.float32,
        ),
        "controller_labels": np.asarray(["left_drive", "right_drive", "forward_speed"]),
        "controller_matrix": np.asarray(
            [
                [0.0, 0.0, 0.0, 0.0],
                [1.0, 2.0, 1.0, 2.0],
                [0.2, 0.2, 0.2, 0.2],
            ],
            dtype=np.float32,
        ),
        "frame_cycles": np.asarray([0, 1, 2, 3], dtype=np.int64),
        "frame_target_bearing_body": np.asarray([1.0, 2.0, 1.0, 2.0], dtype=np.float32),
    }
    metrics = build_state_binned_turn_metrics(
        capture=capture,
        monitor_groups={"RelayA_left": [1], "RelayA_right": [2]},
        frame_state_values=np.asarray([0.1, 0.2, 0.9, 1.0], dtype=np.float32),
        min_bin_frames=2,
    )

    assert list(metrics["label"]) == ["RelayA"]
    row = metrics.iloc[0]
    assert row["low_frame_count"] == 2
    assert row["high_frame_count"] == 2
    assert np.isclose(float(row["corr_target_bearing_low"]), 1.0)
    assert np.isclose(float(row["corr_target_bearing_high"]), 1.0)
    assert np.isclose(float(row["corr_drive_asymmetry_low"]), 1.0)
    assert np.isclose(float(row["corr_drive_asymmetry_high"]), 1.0)


def test_apply_state_binned_ranking_adjustments_penalizes_state_flip_and_bias() -> None:
    ranked = pd.DataFrame(
        [
            {
                "label": "RelayStable",
                "target_specificity_score": 0.8,
                "corr_target_bearing": 0.7,
                "corr_drive_asymmetry": 0.5,
                "mean_abs_asymmetry_voltage_mv": 2.0,
            },
            {
                "label": "RelayFlip",
                "target_specificity_score": 0.9,
                "corr_target_bearing": 0.7,
                "corr_drive_asymmetry": 0.6,
                "mean_abs_asymmetry_voltage_mv": 2.0,
            },
        ]
    )
    target_state_metrics = pd.DataFrame(
        [
            {
                "label": "RelayStable",
                "corr_target_bearing_low": 0.6,
                "corr_target_bearing_high": 0.5,
                "corr_drive_asymmetry_low": 0.4,
                "corr_drive_asymmetry_high": 0.3,
                "mean_abs_asymmetry_voltage_mv_low": 0.6,
                "mean_abs_asymmetry_voltage_mv_high": 0.8,
            },
            {
                "label": "RelayFlip",
                "corr_target_bearing_low": 0.7,
                "corr_target_bearing_high": -0.6,
                "corr_drive_asymmetry_low": 0.4,
                "corr_drive_asymmetry_high": -0.5,
                "mean_abs_asymmetry_voltage_mv_low": 0.8,
                "mean_abs_asymmetry_voltage_mv_high": 0.9,
            },
        ]
    )
    no_target_state_metrics = pd.DataFrame(
        [
            {
                "label": "RelayStable",
                "corr_target_bearing_low": np.nan,
                "corr_target_bearing_high": np.nan,
                "corr_drive_asymmetry_low": 0.05,
                "corr_drive_asymmetry_high": 0.04,
                "mean_abs_asymmetry_voltage_mv_low": 0.2,
                "mean_abs_asymmetry_voltage_mv_high": 0.25,
            },
            {
                "label": "RelayFlip",
                "corr_target_bearing_low": np.nan,
                "corr_target_bearing_high": np.nan,
                "corr_drive_asymmetry_low": 0.55,
                "corr_drive_asymmetry_high": 0.65,
                "mean_abs_asymmetry_voltage_mv_low": 1.2,
                "mean_abs_asymmetry_voltage_mv_high": 1.3,
            },
        ]
    )

    adjusted = apply_state_binned_ranking_adjustments(
        ranked,
        target_state_metrics=target_state_metrics,
        no_target_state_metrics=no_target_state_metrics,
        require_consistent_sign=False,
    )
    filtered = apply_state_binned_ranking_adjustments(
        ranked,
        target_state_metrics=target_state_metrics,
        no_target_state_metrics=no_target_state_metrics,
        require_consistent_sign=True,
    )

    assert list(adjusted["label"]) == ["RelayStable", "RelayFlip"]
    assert float(adjusted.iloc[0]["target_state_sign_flip_penalty"]) == 0.0
    assert float(adjusted.iloc[1]["target_state_sign_flip_penalty"]) == 1.0
    assert list(filtered["label"]) == ["RelayStable"]
