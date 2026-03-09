from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np


def _normalize_cell_type(value: Any) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8")
    if isinstance(value, np.bytes_):
        return value.tobytes().decode("utf-8")
    return str(value)


def _ensure_eye_major_array(value: Any) -> np.ndarray:
    arr = np.asarray(value, dtype=float)
    if arr.ndim == 0:
        return np.array([[float(arr)], [float(arr)]], dtype=float)
    if arr.ndim == 1:
        if arr.shape[0] == 2:
            return arr.reshape(2, 1)
        mean_value = float(arr.mean()) if arr.size else 0.0
        return np.array([[mean_value], [mean_value]], dtype=float)
    if arr.shape[0] == 2:
        return arr
    if arr.shape[-1] == 2:
        return np.moveaxis(arr, -1, 0)
    raise ValueError(f"Expected vision activity array with an eye axis of size 2, got shape {arr.shape}")


def _coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


@dataclass(frozen=True)
class InferredLateralizedCandidate:
    cell_type: str
    mirror_selectivity_score: float
    body_right_eye_diff: float
    right_side_polarity: float
    is_tracking_cell: bool
    is_flow_cell: bool


@dataclass(frozen=True)
class InferredLateralizedFeatures:
    left_evidence: float
    right_evidence: float
    turn_bias: float
    confidence: float
    active_candidate_count: int

    def to_dict(self) -> dict[str, float | int]:
        return {
            "left_evidence": self.left_evidence,
            "right_evidence": self.right_evidence,
            "turn_bias": self.turn_bias,
            "confidence": self.confidence,
            "active_candidate_count": self.active_candidate_count,
        }


def load_inferred_lateralized_candidates(
    path: str | Path,
    *,
    min_score: float = 0.0,
    require_sign_flip: bool = True,
) -> list[InferredLateralizedCandidate]:
    candidates: list[InferredLateralizedCandidate] = []
    with Path(path).open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            mirror_selectivity_score = float(row["mirror_selectivity_score"])
            if mirror_selectivity_score < float(min_score):
                continue
            sign_flip_consistent = _coerce_bool(row.get("sign_flip_consistent", True))
            if require_sign_flip and not sign_flip_consistent:
                continue
            body_right_eye_diff = float(row["body_right_eye_diff"])
            if body_right_eye_diff == 0.0:
                continue
            candidates.append(
                InferredLateralizedCandidate(
                    cell_type=str(row["cell_type"]),
                    mirror_selectivity_score=mirror_selectivity_score,
                    body_right_eye_diff=body_right_eye_diff,
                    right_side_polarity=float(np.sign(body_right_eye_diff)),
                    is_tracking_cell=_coerce_bool(row.get("is_tracking_cell", False)),
                    is_flow_cell=_coerce_bool(row.get("is_flow_cell", False)),
                )
            )
    return candidates


def select_recommended_candidates(
    candidates: Sequence[InferredLateralizedCandidate],
    *,
    tracking_limit: int = 6,
    flow_limit: int = 4,
) -> list[InferredLateralizedCandidate]:
    tracking = [candidate for candidate in candidates if candidate.is_tracking_cell][:tracking_limit]
    flow = [candidate for candidate in candidates if candidate.is_flow_cell][:flow_limit]
    selected = {candidate.cell_type: candidate for candidate in [*tracking, *flow]}
    return list(selected.values())


class InferredLateralizedFeatureExtractor:
    def __init__(self, candidates: Iterable[InferredLateralizedCandidate]) -> None:
        self.candidates = list(candidates)
        self.cell_types = tuple(candidate.cell_type for candidate in self.candidates)

    @classmethod
    def from_probe_csv(
        cls,
        path: str | Path,
        *,
        min_score: float = 0.0,
        tracking_limit: int = 6,
        flow_limit: int = 4,
    ) -> "InferredLateralizedFeatureExtractor":
        candidates = load_inferred_lateralized_candidates(path, min_score=min_score)
        return cls(
            select_recommended_candidates(
                candidates,
                tracking_limit=tracking_limit,
                flow_limit=flow_limit,
            )
        )

    def build_index_map(self, node_types: np.ndarray) -> dict[str, np.ndarray]:
        normalized = np.asarray([_normalize_cell_type(value) for value in np.asarray(node_types).reshape(-1)], dtype=object)
        return {
            cell_type: np.flatnonzero(normalized == cell_type).astype(int)
            for cell_type in self.cell_types
        }

    def extract_from_array(
        self,
        nn_activities_arr: Any,
        index_map: dict[str, np.ndarray],
    ) -> InferredLateralizedFeatures:
        eye_major = _ensure_eye_major_array(nn_activities_arr)
        weighted_signed_diffs = []
        active_weights = []
        active_candidate_count = 0
        for candidate in self.candidates:
            indices = index_map.get(candidate.cell_type)
            if indices is None or len(indices) == 0:
                continue
            eye_diff = float(eye_major[0, indices].mean() - eye_major[1, indices].mean())
            signed_right_evidence = candidate.right_side_polarity * eye_diff
            weighted_signed_diffs.append(candidate.mirror_selectivity_score * signed_right_evidence)
            active_weights.append(candidate.mirror_selectivity_score)
            active_candidate_count += 1
        if not weighted_signed_diffs:
            return InferredLateralizedFeatures(
                left_evidence=0.0,
                right_evidence=0.0,
                turn_bias=0.0,
                confidence=0.0,
                active_candidate_count=0,
            )
        total_weight = float(sum(active_weights)) if active_weights else float(len(weighted_signed_diffs))
        turn_bias = float(sum(weighted_signed_diffs) / total_weight)
        confidence = float(sum(abs(value) for value in weighted_signed_diffs) / total_weight)
        return InferredLateralizedFeatures(
            left_evidence=max(0.0, -turn_bias),
            right_evidence=max(0.0, turn_bias),
            turn_bias=turn_bias,
            confidence=confidence,
            active_candidate_count=active_candidate_count,
        )
