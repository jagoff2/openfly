from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import numpy as np

from brain.public_ids import DEFAULT_FLOW_CELLS, DEFAULT_TRACKING_CELLS
from vision.inferred_lateralized import InferredLateralizedFeatureExtractor


def _normalize_cell_type(value: Any) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8")
    if isinstance(value, np.bytes_):
        return value.tobytes().decode("utf-8")
    return str(value)


@dataclass(frozen=True)
class VisionIndexCache:
    tracking_cells: tuple[str, ...]
    flow_cells: tuple[str, ...]
    tracking_indices: dict[str, np.ndarray]
    flow_indices: dict[str, np.ndarray]

    @classmethod
    def from_node_types(
        cls,
        node_types: np.ndarray,
        tracking_cells: Sequence[str] | None = None,
        flow_cells: Sequence[str] | None = None,
    ) -> "VisionIndexCache":
        normalized = np.asarray([_normalize_cell_type(value) for value in np.asarray(node_types).reshape(-1)], dtype=object)
        tracking = tuple(tracking_cells or DEFAULT_TRACKING_CELLS)
        flow = tuple(flow_cells or DEFAULT_FLOW_CELLS)
        required_cells = set(tracking) | set(flow)
        cell_indices = {cell: np.flatnonzero(normalized == cell).astype(int) for cell in required_cells}
        return cls(
            tracking_cells=tracking,
            flow_cells=flow,
            tracking_indices={cell: cell_indices[cell] for cell in tracking},
            flow_indices={cell: cell_indices[cell] for cell in flow},
        )


@dataclass
class VisionFeatures:
    salience_left: float
    salience_right: float
    flow_left: float
    flow_right: float
    inferred_left_evidence: float = 0.0
    inferred_right_evidence: float = 0.0
    inferred_turn_bias: float = 0.0
    inferred_turn_confidence: float = 0.0
    inferred_candidate_count: int = 0
    balance_velocity: float = 0.0
    forward_salience_velocity: float = 0.0
    looming_evidence: float = 0.0
    receding_evidence: float = 0.0

    @classmethod
    def from_dict(cls, values: Mapping[str, Any]) -> "VisionFeatures":
        return cls(
            salience_left=float(values.get("salience_left", 0.0)),
            salience_right=float(values.get("salience_right", 0.0)),
            flow_left=float(values.get("flow_left", 0.0)),
            flow_right=float(values.get("flow_right", 0.0)),
            inferred_left_evidence=float(values.get("inferred_left_evidence", 0.0)),
            inferred_right_evidence=float(values.get("inferred_right_evidence", 0.0)),
            inferred_turn_bias=float(values.get("inferred_turn_bias", 0.0)),
            inferred_turn_confidence=float(values.get("inferred_turn_confidence", 0.0)),
            inferred_candidate_count=int(values.get("inferred_candidate_count", 0)),
            balance_velocity=float(values.get("balance_velocity", 0.0)),
            forward_salience_velocity=float(values.get("forward_salience_velocity", 0.0)),
            looming_evidence=float(values.get("looming_evidence", 0.0)),
            receding_evidence=float(values.get("receding_evidence", 0.0)),
        )

    @property
    def balance(self) -> float:
        denom = self.salience_left + self.salience_right + 1e-6
        return (self.salience_right - self.salience_left) / denom

    @property
    def forward_salience(self) -> float:
        return 0.5 * (self.salience_left + self.salience_right)

    @property
    def flow_balance(self) -> float:
        return float(self.flow_right - self.flow_left)

    def to_dict(self) -> dict[str, float]:
        return {
            "salience_left": self.salience_left,
            "salience_right": self.salience_right,
            "flow_left": self.flow_left,
            "flow_right": self.flow_right,
            "balance": self.balance,
            "forward_salience": self.forward_salience,
            "flow_balance": self.flow_balance,
            "inferred_left_evidence": self.inferred_left_evidence,
            "inferred_right_evidence": self.inferred_right_evidence,
            "inferred_turn_bias": self.inferred_turn_bias,
            "inferred_turn_confidence": self.inferred_turn_confidence,
            "inferred_candidate_count": self.inferred_candidate_count,
            "balance_velocity": self.balance_velocity,
            "forward_salience_velocity": self.forward_salience_velocity,
            "looming_evidence": self.looming_evidence,
            "receding_evidence": self.receding_evidence,
        }

class RealisticVisionFeatureExtractor:
    def __init__(
        self,
        tracking_cells: Sequence[str] | None = None,
        flow_cells: Sequence[str] | None = None,
        inferred_turn_extractor: InferredLateralizedFeatureExtractor | None = None,
    ) -> None:
        self.tracking_cells = list(tracking_cells or DEFAULT_TRACKING_CELLS)
        self.flow_cells = list(flow_cells or DEFAULT_FLOW_CELLS)
        self.inferred_turn_extractor = inferred_turn_extractor
        self.reset()

    def reset(self) -> None:
        self._last_feature_snapshot: VisionFeatures | None = None
        self._last_sim_time: float | None = None

    @staticmethod
    def _bounded_velocity(delta: float, dt: float, *, scale_per_s: float = 0.02) -> float:
        if dt <= 1e-9:
            return 0.0
        return float(np.tanh((float(delta) / float(dt)) * float(scale_per_s)))

    def _with_temporal_features(self, features: VisionFeatures, sim_time: float | None) -> VisionFeatures:
        if sim_time is None or self._last_feature_snapshot is None or self._last_sim_time is None:
            enriched = VisionFeatures(
                salience_left=features.salience_left,
                salience_right=features.salience_right,
                flow_left=features.flow_left,
                flow_right=features.flow_right,
                inferred_left_evidence=features.inferred_left_evidence,
                inferred_right_evidence=features.inferred_right_evidence,
                inferred_turn_bias=features.inferred_turn_bias,
                inferred_turn_confidence=features.inferred_turn_confidence,
                inferred_candidate_count=features.inferred_candidate_count,
            )
        else:
            dt = max(0.0, float(sim_time) - float(self._last_sim_time))
            balance_velocity = self._bounded_velocity(features.balance - self._last_feature_snapshot.balance, dt)
            forward_salience_velocity = self._bounded_velocity(
                features.forward_salience - self._last_feature_snapshot.forward_salience,
                dt,
            )
            enriched = VisionFeatures(
                salience_left=features.salience_left,
                salience_right=features.salience_right,
                flow_left=features.flow_left,
                flow_right=features.flow_right,
                inferred_left_evidence=features.inferred_left_evidence,
                inferred_right_evidence=features.inferred_right_evidence,
                inferred_turn_bias=features.inferred_turn_bias,
                inferred_turn_confidence=features.inferred_turn_confidence,
                inferred_candidate_count=features.inferred_candidate_count,
                balance_velocity=balance_velocity,
                forward_salience_velocity=forward_salience_velocity,
                looming_evidence=max(0.0, forward_salience_velocity),
                receding_evidence=max(0.0, -forward_salience_velocity),
            )
        self._last_feature_snapshot = enriched
        self._last_sim_time = None if sim_time is None else float(sim_time)
        return enriched

    def build_index_cache(self, node_types: np.ndarray) -> VisionIndexCache:
        return VisionIndexCache.from_node_types(node_types, tracking_cells=self.tracking_cells, flow_cells=self.flow_cells)

    def _reduce_eye_values(self, value: Any) -> np.ndarray:
        arr = np.asarray(value, dtype=float)
        if arr.ndim == 0:
            return np.array([float(arr), float(arr)])
        if arr.ndim == 1:
            return arr.astype(float) if arr.shape[0] == 2 else np.array([float(arr.mean()), float(arr.mean())])
        return np.array([arr[0].mean(), arr[1].mean()], dtype=float)

    def _ensure_eye_major_array(self, value: Any) -> np.ndarray:
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

    def _aggregate(self, nn_activities: Mapping[str, Any], cells: Sequence[str], absolute: bool = True) -> np.ndarray:
        values = []
        for cell in cells:
            if cell in nn_activities:
                eye_values = self._reduce_eye_values(nn_activities[cell])
                values.append(np.abs(eye_values) if absolute else eye_values)
        if not values:
            return np.zeros(2, dtype=float)
        return np.vstack(values).mean(axis=0)

    def _aggregate_from_array(self, nn_activities_arr: Any, index_map: Mapping[str, np.ndarray], cell_order: Sequence[str], absolute: bool = True) -> np.ndarray:
        eye_major = self._ensure_eye_major_array(nn_activities_arr)
        values = []
        for cell in cell_order:
            indices = index_map.get(cell)
            if indices is None or len(indices) == 0:
                continue
            eye_values = eye_major[:, indices].mean(axis=1)
            values.append(np.abs(eye_values) if absolute else eye_values)
        if not values:
            return np.zeros(2, dtype=float)
        return np.vstack(values).mean(axis=0)

    def _extract_inferred_features_from_array(self, nn_activities_arr: Any, index_cache: VisionIndexCache) -> dict[str, float | int]:
        if self.inferred_turn_extractor is None:
            return {}
        candidate_index_map = {}
        candidate_index_map.update(index_cache.tracking_indices)
        candidate_index_map.update(index_cache.flow_indices)
        inferred = self.inferred_turn_extractor.extract_from_array(nn_activities_arr, candidate_index_map)
        return inferred.to_dict()

    def extract(self, nn_activities: Mapping[str, Any]) -> VisionFeatures:
        salience = self._aggregate(nn_activities, self.tracking_cells, absolute=True)
        flow = self._aggregate(nn_activities, self.flow_cells, absolute=False)
        return VisionFeatures(salience_left=float(salience[0]), salience_right=float(salience[1]), flow_left=float(flow[0]), flow_right=float(flow[1]))

    def extract_from_array(self, nn_activities_arr: Any, index_cache: VisionIndexCache) -> VisionFeatures:
        salience = self._aggregate_from_array(nn_activities_arr, index_cache.tracking_indices, index_cache.tracking_cells, absolute=True)
        flow = self._aggregate_from_array(nn_activities_arr, index_cache.flow_indices, index_cache.flow_cells, absolute=False)
        inferred = self._extract_inferred_features_from_array(nn_activities_arr, index_cache)
        return VisionFeatures(
            salience_left=float(salience[0]),
            salience_right=float(salience[1]),
            flow_left=float(flow[0]),
            flow_right=float(flow[1]),
            inferred_left_evidence=float(inferred.get("left_evidence", 0.0)),
            inferred_right_evidence=float(inferred.get("right_evidence", 0.0)),
            inferred_turn_bias=float(inferred.get("turn_bias", 0.0)),
            inferred_turn_confidence=float(inferred.get("confidence", 0.0)),
            inferred_candidate_count=int(inferred.get("active_candidate_count", 0)),
        )

    def extract_observation(self, observation: Any) -> VisionFeatures:
        precomputed = getattr(observation, "realistic_vision_features", None)
        vision_array = getattr(observation, "realistic_vision_array", None)
        index_cache = getattr(observation, "realistic_vision_index_cache", None)
        current_features: VisionFeatures
        if vision_array is not None and index_cache is not None:
            array_features = self.extract_from_array(vision_array, index_cache)
            if precomputed:
                merged = VisionFeatures.from_dict(precomputed).to_dict()
                merged.update(
                    {
                        "inferred_left_evidence": array_features.inferred_left_evidence,
                        "inferred_right_evidence": array_features.inferred_right_evidence,
                        "inferred_turn_bias": array_features.inferred_turn_bias,
                        "inferred_turn_confidence": array_features.inferred_turn_confidence,
                        "inferred_candidate_count": array_features.inferred_candidate_count,
                    }
                )
                current_features = VisionFeatures.from_dict(merged)
            else:
                current_features = array_features
        elif precomputed:
            current_features = VisionFeatures.from_dict(precomputed)
        else:
            realistic_vision = getattr(observation, "realistic_vision", {})
            current_features = self.extract(realistic_vision)
        return self._with_temporal_features(current_features, getattr(observation, "sim_time", None))
