from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd


def rank_target_specific_signals(
    *,
    target_table: pd.DataFrame,
    baseline_table: pd.DataFrame,
    group_column: str,
    allowed_super_classes: Iterable[str] = ("central", "ascending", "visual_projection", "visual_centrifugal"),
) -> pd.DataFrame:
    if target_table.empty:
        return pd.DataFrame(
            columns=[
                group_column,
                "super_class",
                "target_bearing_abs",
                "baseline_drive_abs",
                "baseline_forward_abs",
                "sampled_fraction",
                "target_specificity_score",
            ]
        )

    baseline_columns = {column: f"baseline_{column}" for column in baseline_table.columns if column != group_column}
    merged = target_table.copy().rename(columns={"super_class": "target_super_class"})
    merged = merged.merge(
        baseline_table.rename(columns=baseline_columns),
        how="left",
        on=group_column,
    )

    if "target_super_class" in merged.columns:
        merged["super_class"] = merged["target_super_class"].fillna("unknown").astype(str)
        allowed_mask = merged["super_class"].str.lower().isin({item.lower() for item in allowed_super_classes})
        merged = merged[allowed_mask].copy()
        if merged.empty:
            return pd.DataFrame(
                columns=[
                    group_column,
                    "super_class",
                    "target_bearing_abs",
                    "baseline_drive_abs",
                    "baseline_forward_abs",
                    "sampled_fraction",
                    "target_specificity_score",
                ]
            )
    else:
        merged["super_class"] = "unknown"

    merged["target_bearing_abs"] = merged["corr_target_bearing"].abs()
    merged["baseline_drive_abs"] = merged.get("baseline_corr_drive_asymmetry", pd.Series(0.0, index=merged.index)).fillna(0.0).abs()
    merged["baseline_forward_abs"] = merged.get("baseline_corr_forward_speed", pd.Series(0.0, index=merged.index)).fillna(0.0).abs()
    merged["sampled_fraction"] = merged.get("sampled_fraction", pd.Series(0.0, index=merged.index)).fillna(0.0)
    merged["target_specificity_score"] = (
        merged["target_bearing_abs"]
        - 0.6 * merged["baseline_drive_abs"]
        - 0.4 * merged["baseline_forward_abs"]
        - 0.25 * merged["sampled_fraction"]
    )

    keep_columns = [
        group_column,
        "super_class",
        "target_bearing_abs",
        "baseline_drive_abs",
        "baseline_forward_abs",
        "sampled_fraction",
        "target_specificity_score",
    ]
    extra_columns = [
        column
        for column in (
            "corr_target_bearing",
            "corr_drive_asymmetry",
            "corr_forward_speed",
            "mean_selected_frames",
            "mean_spike_frames",
            "mean_voltage",
            "mean_spike_per_frame",
            "mean_rate_hz",
            "mean_voltage_mv",
        )
        if column in merged.columns
    ]
    keep_columns.extend(extra_columns)
    return merged[keep_columns].sort_values(
        ["target_specificity_score", "target_bearing_abs"],
        ascending=[False, False],
    ).reset_index(drop=True)
