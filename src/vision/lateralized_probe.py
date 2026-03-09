from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np


@dataclass(frozen=True)
class RetinaGeometry:
    ommatidia_centers: np.ndarray
    x_norm: np.ndarray
    y_norm: np.ndarray


def compute_retina_geometry(ommatidia_id_map: np.ndarray) -> RetinaGeometry:
    ommatidia_id_map = np.asarray(ommatidia_id_map)
    num_ommatidia = int(ommatidia_id_map.max())
    centers = np.empty((num_ommatidia, 2), dtype=float)
    for ommatidium_id in range(1, num_ommatidia + 1):
        mask = ommatidia_id_map == ommatidium_id
        rows, cols = np.where(mask)
        centers[ommatidium_id - 1, 0] = float(rows.mean())
        centers[ommatidium_id - 1, 1] = float(cols.mean())
    row_min, col_min = centers.min(axis=0)
    row_max, col_max = centers.max(axis=0)
    y_norm = (centers[:, 0] - row_min) / max(row_max - row_min, 1e-9)
    x_norm = (centers[:, 1] - col_min) / max(col_max - col_min, 1e-9)
    return RetinaGeometry(ommatidia_centers=centers, x_norm=x_norm, y_norm=y_norm)


def body_centered_lateral_coordinate(x_norm: np.ndarray, eye_index: int) -> np.ndarray:
    if eye_index == 0:
        return 1.0 - np.asarray(x_norm, dtype=float)
    if eye_index == 1:
        return np.asarray(x_norm, dtype=float)
    raise ValueError(f"Expected eye_index 0 or 1, got {eye_index}")


def build_body_side_mask(
    geometry: RetinaGeometry,
    eye_index: int,
    side: str,
    side_fraction: float = 0.35,
    center_half_width: float = 0.15,
) -> np.ndarray:
    body_x = body_centered_lateral_coordinate(geometry.x_norm, eye_index)
    if side == "left":
        return body_x >= (1.0 - side_fraction)
    if side == "right":
        return body_x <= side_fraction
    if side == "center":
        return np.abs(body_x - 0.5) <= center_half_width
    raise ValueError(f"Unsupported side: {side}")


def build_dark_patch_stimulus(
    num_ommatidia: int,
    *,
    left_eye_mask: np.ndarray,
    right_eye_mask: np.ndarray,
    baseline_value: float = 1.0,
    patch_value: float = 0.0,
) -> np.ndarray:
    stimulus = np.full((2, int(num_ommatidia)), float(baseline_value), dtype=float)
    stimulus[0, np.asarray(left_eye_mask, dtype=bool)] = float(patch_value)
    stimulus[1, np.asarray(right_eye_mask, dtype=bool)] = float(patch_value)
    return stimulus


def build_body_side_stimuli(
    geometry: RetinaGeometry,
    *,
    baseline_value: float = 1.0,
    patch_value: float = 0.0,
    side_fraction: float = 0.35,
) -> dict[str, np.ndarray]:
    num_ommatidia = geometry.ommatidia_centers.shape[0]
    left_masks = {
        side: build_body_side_mask(geometry, 0, side, side_fraction=side_fraction)
        for side in ("left", "center", "right")
    }
    right_masks = {
        side: build_body_side_mask(geometry, 1, side, side_fraction=side_fraction)
        for side in ("left", "center", "right")
    }
    return {
        "baseline_gray": np.full((2, num_ommatidia), float(baseline_value), dtype=float),
        "body_left_dark": build_dark_patch_stimulus(
            num_ommatidia,
            left_eye_mask=left_masks["left"],
            right_eye_mask=right_masks["left"],
            baseline_value=baseline_value,
            patch_value=patch_value,
        ),
        "body_center_dark": build_dark_patch_stimulus(
            num_ommatidia,
            left_eye_mask=left_masks["center"],
            right_eye_mask=right_masks["center"],
            baseline_value=baseline_value,
            patch_value=patch_value,
        ),
        "body_right_dark": build_dark_patch_stimulus(
            num_ommatidia,
            left_eye_mask=left_masks["right"],
            right_eye_mask=right_masks["right"],
            baseline_value=baseline_value,
            patch_value=patch_value,
        ),
    }


def compute_mirror_selectivity_scores(rows: list[Mapping[str, float]]) -> list[dict[str, float | str | bool]]:
    scored_rows: list[dict[str, float | str | bool]] = []
    for row in rows:
        body_left_eye_diff = float(row["body_left_left_eye_mean"] - row["body_left_right_eye_mean"])
        body_right_eye_diff = float(row["body_right_left_eye_mean"] - row["body_right_right_eye_mean"])
        mirror_score = abs(body_left_eye_diff - body_right_eye_diff)
        sign_flip = body_left_eye_diff * body_right_eye_diff < 0.0
        enriched = dict(row)
        enriched["body_left_eye_diff"] = body_left_eye_diff
        enriched["body_right_eye_diff"] = body_right_eye_diff
        enriched["mirror_selectivity_score"] = float(mirror_score)
        enriched["sign_flip_consistent"] = bool(sign_flip)
        scored_rows.append(enriched)
    return sorted(
        scored_rows,
        key=lambda item: (float(item["mirror_selectivity_score"]), float(item.get("body_center_abs_delta", 0.0))),
        reverse=True,
    )
