from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from body.interfaces import BodyObservation
from brain.flywire_annotations import (
    build_overlap_groups,
    build_spatial_grid_overlap_groups,
    build_spatial_overlap_groups,
    find_exact_cell_type_overlap,
    load_flywire_annotation_table,
)
from vision.feature_extractor import _normalize_cell_type


@dataclass(frozen=True)
class FlyVisConnectomeCache:
    node_types: np.ndarray
    node_u: np.ndarray
    node_v: np.ndarray

    @classmethod
    def from_connectome(cls, connectome: Any) -> "FlyVisConnectomeCache":
        node_types = np.asarray([_normalize_cell_type(value) for value in np.asarray(connectome.nodes.type[:]).reshape(-1)], dtype=object)
        node_u = np.asarray(connectome.nodes.u[:], dtype=float).reshape(-1)
        node_v = np.asarray(connectome.nodes.v[:], dtype=float).reshape(-1)
        return cls(node_types=node_types, node_u=node_u, node_v=node_v)


@dataclass
class VisualSpliceConfig:
    enabled: bool = False
    annotation_path: str = "outputs/cache/flywire_annotation_supplement.tsv"
    spatial_mode: str = "axis1d"
    spatial_bins: int = 4
    spatial_u_bins: int = 2
    spatial_v_bins: int = 2
    spatial_swap_uv: bool = False
    spatial_flip_u: bool = False
    spatial_flip_v: bool = False
    spatial_mirror_u_by_side: bool = False
    min_roots_per_side: int = 50
    min_roots_per_bin: int = 20
    value_scale: float = 101.94613788960949
    max_abs_current: float = 120.0
    baseline_update_alpha: float = 0.0

    @classmethod
    def from_mapping(cls, mapping: dict[str, Any] | None) -> "VisualSpliceConfig":
        mapping = mapping or {}
        return cls(
            enabled=bool(mapping.get("enabled", False)),
            annotation_path=str(mapping.get("annotation_path", "outputs/cache/flywire_annotation_supplement.tsv")),
            spatial_mode=str(mapping.get("spatial_mode", "axis1d")),
            spatial_bins=int(mapping.get("spatial_bins", 4)),
            spatial_u_bins=int(mapping.get("spatial_u_bins", 2)),
            spatial_v_bins=int(mapping.get("spatial_v_bins", 2)),
            spatial_swap_uv=bool(mapping.get("spatial_swap_uv", False)),
            spatial_flip_u=bool(mapping.get("spatial_flip_u", False)),
            spatial_flip_v=bool(mapping.get("spatial_flip_v", False)),
            spatial_mirror_u_by_side=bool(mapping.get("spatial_mirror_u_by_side", False)),
            min_roots_per_side=int(mapping.get("min_roots_per_side", 50)),
            min_roots_per_bin=int(mapping.get("min_roots_per_bin", 20)),
            value_scale=float(mapping.get("value_scale", 101.94613788960949)),
            max_abs_current=float(mapping.get("max_abs_current", 120.0)),
            baseline_update_alpha=float(mapping.get("baseline_update_alpha", 0.0)),
        )


class VisualSpliceInjector:
    def __init__(self, config: VisualSpliceConfig | None = None) -> None:
        self.config = config or VisualSpliceConfig()
        self.reset()

    def reset(self) -> None:
        self._ready = False
        self._baseline_by_key: dict[tuple[str, str, int], float] = {}
        self._group_roots_by_key: dict[tuple[str, str, int], tuple[int, ...]] = {}
        self._flyvis_bins_by_key: dict[tuple[str, str, int], np.ndarray] = {}

    def _quantile_labels(self, values: np.ndarray, num_bins: int) -> np.ndarray:
        order = np.argsort(values, kind="stable")
        labels = np.zeros(values.shape[0], dtype=int)
        for label, chunk in enumerate(np.array_split(order, int(num_bins))):
            labels[np.asarray(chunk, dtype=int)] = int(label)
        return labels

    def _build_type_indices(self, cache: FlyVisConnectomeCache, cell_types: list[str]) -> dict[str, np.ndarray]:
        return {cell_type: np.flatnonzero(cache.node_types == cell_type).astype(int) for cell_type in cell_types}

    def _build_flyvis_bins(self, cache: FlyVisConnectomeCache, cell_types: list[str]) -> dict[tuple[str, int], np.ndarray]:
        type_indices = self._build_type_indices(cache, cell_types)
        bins: dict[tuple[str, int], np.ndarray] = {}
        if self.config.spatial_mode == "uv_grid":
            for cell_type, indices in type_indices.items():
                if len(indices) == 0:
                    continue
                u_labels = self._quantile_labels(cache.node_u[indices], int(self.config.spatial_u_bins))
                v_labels = self._quantile_labels(cache.node_v[indices], int(self.config.spatial_v_bins))
                for u_bin in range(int(self.config.spatial_u_bins)):
                    for v_bin in range(int(self.config.spatial_v_bins)):
                        mask = (u_labels == int(u_bin)) & (v_labels == int(v_bin))
                        chunk = np.asarray(indices[mask], dtype=int)
                        if len(chunk) == 0:
                            continue
                        bins[(cell_type, int(u_bin * int(self.config.spatial_v_bins) + v_bin))] = chunk
            return bins
        num_bins = max(1, int(self.config.spatial_bins))
        for cell_type, indices in type_indices.items():
            if len(indices) == 0:
                continue
            order = np.argsort(cache.node_u[indices], kind="stable")
            sorted_indices = indices[order]
            for bin_index, chunk in enumerate(np.array_split(sorted_indices, num_bins)):
                chunk_arr = np.asarray(chunk, dtype=int)
                if len(chunk_arr) == 0:
                    continue
                bins[(cell_type, int(bin_index))] = chunk_arr
        return bins

    def _initialize(self, observation: BodyObservation) -> None:
        vision_cache = getattr(observation, "realistic_vision_splice_cache", None)
        if vision_cache is None:
            raise ValueError("visual splice requires observation.realistic_vision_splice_cache; use fast vision payload mode")
        annotation_table = load_flywire_annotation_table(Path(self.config.annotation_path))
        overlap_types = find_exact_cell_type_overlap(sorted(set(str(v) for v in vision_cache.node_types.tolist())), annotation_table)
        if self.config.spatial_mode == "uv_grid":
            overlap_groups = build_spatial_grid_overlap_groups(
                annotation_table,
                cell_types=overlap_types,
                num_u_bins=int(self.config.spatial_u_bins),
                num_v_bins=int(self.config.spatial_v_bins),
                swap_uv=bool(self.config.spatial_swap_uv),
                flip_u=bool(self.config.spatial_flip_u),
                flip_v=bool(self.config.spatial_flip_v),
                mirror_u_by_side=bool(self.config.spatial_mirror_u_by_side),
                min_roots_per_bin=int(self.config.min_roots_per_bin),
            )
        elif int(self.config.spatial_bins) > 1:
            overlap_groups = build_spatial_overlap_groups(
                annotation_table,
                cell_types=overlap_types,
                num_bins=int(self.config.spatial_bins),
                min_roots_per_bin=int(self.config.min_roots_per_bin),
            )
        else:
            base_groups = build_overlap_groups(
                annotation_table,
                cell_types=overlap_types,
                min_roots_per_side=int(self.config.min_roots_per_side),
            )

            @dataclass(frozen=True)
            class _WrappedGroup:
                cell_type: str
                side: str
                bin_index: int
                root_ids: tuple[int, ...]

            overlap_groups = [_WrappedGroup(group.cell_type, group.side, 0, group.root_ids) for group in base_groups]
        flyvis_bins = self._build_flyvis_bins(vision_cache, overlap_types)
        for group in overlap_groups:
            key = (group.cell_type, group.side, int(group.bin_index))
            flyvis_key = (group.cell_type, int(group.bin_index))
            if flyvis_key not in flyvis_bins:
                continue
            self._group_roots_by_key[key] = tuple(int(root_id) for root_id in group.root_ids)
            self._flyvis_bins_by_key[key] = flyvis_bins[flyvis_key]
        self._ready = True

    def _group_means(self, nn_activities_arr: Any) -> dict[tuple[str, str, int], float]:
        eye_major = np.asarray(nn_activities_arr, dtype=float)
        if eye_major.shape[0] != 2:
            raise ValueError(f"expected eye-major FlyVis array with shape [2, N], got {eye_major.shape}")
        means: dict[tuple[str, str, int], float] = {}
        for key, indices in self._flyvis_bins_by_key.items():
            _, side, _ = key
            eye_index = 0 if side == "left" else 1
            means[key] = float(eye_major[eye_index, indices].mean())
        return means

    def build(self, observation: BodyObservation) -> tuple[dict[int, float], dict[str, Any]]:
        if not self.config.enabled:
            return {}, {"enabled": False, "mode": "disabled"}
        nn_activities_arr = getattr(observation, "realistic_vision_array", None)
        if nn_activities_arr is None:
            return {}, {"enabled": False, "mode": "missing_payload"}
        if not self._ready:
            self._initialize(observation)
        current_by_key = self._group_means(nn_activities_arr)
        if not self._baseline_by_key:
            self._baseline_by_key = dict(current_by_key)
            return {}, {
                "enabled": True,
                "mode": self.config.spatial_mode,
                "initialized_baseline": True,
                "num_groups": len(self._group_roots_by_key),
                "nonzero_root_count": 0,
                "max_abs_delta": 0.0,
                "max_abs_current": 0.0,
            }
        alpha = float(np.clip(self.config.baseline_update_alpha, 0.0, 1.0))
        direct_current_by_id: dict[int, float] = {}
        max_abs_delta = 0.0
        max_abs_current = 0.0
        signed_current_sum = 0.0
        for key, current_value in current_by_key.items():
            baseline_value = float(self._baseline_by_key.get(key, current_value))
            delta = float(current_value - baseline_value)
            max_abs_delta = max(max_abs_delta, abs(delta))
            current = float(np.clip(delta * self.config.value_scale, -self.config.max_abs_current, self.config.max_abs_current))
            if not np.isclose(current, 0.0):
                roots = self._group_roots_by_key.get(key, ())
                for root_id in roots:
                    direct_current_by_id[int(root_id)] = current
                signed_current_sum += current * len(roots)
                max_abs_current = max(max_abs_current, abs(current))
            if alpha > 0.0:
                self._baseline_by_key[key] = (1.0 - alpha) * baseline_value + alpha * current_value
        return direct_current_by_id, {
            "enabled": True,
            "mode": self.config.spatial_mode,
            "initialized_baseline": False,
            "num_groups": len(self._group_roots_by_key),
            "nonzero_root_count": len(direct_current_by_id),
            "max_abs_delta": max_abs_delta,
            "max_abs_current": max_abs_current,
            "signed_current_sum": signed_current_sum,
        }
