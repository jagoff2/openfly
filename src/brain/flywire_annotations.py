from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class FlywireOverlapGroup:
    cell_type: str
    side: str
    root_ids: tuple[int, ...]


@dataclass(frozen=True)
class FlywireSpatialOverlapGroup:
    cell_type: str
    side: str
    bin_index: int
    root_ids: tuple[int, ...]
    u_bin: int | None = None
    v_bin: int | None = None


@dataclass(frozen=True)
class FlywireSpatialTransform:
    swap_uv: bool = False
    flip_u: bool = False
    flip_v: bool = False
    mirror_u_by_side: bool = False
    u_permutation: tuple[int, ...] | None = None
    v_permutation: tuple[int, ...] | None = None


def _validate_bin_permutation(
    values: Sequence[int] | None,
    *,
    num_bins: int,
    label: str,
) -> tuple[int, ...] | None:
    if values is None:
        return None
    permutation = tuple(int(value) for value in values)
    if len(permutation) != int(num_bins):
        raise ValueError(f"{label} must contain exactly {int(num_bins)} entries")
    if tuple(sorted(permutation)) != tuple(range(int(num_bins))):
        raise ValueError(f"{label} must be a permutation of 0..{int(num_bins) - 1}")
    return permutation


def _coerce_spatial_transform(
    value: FlywireSpatialTransform | Mapping[str, object] | None,
    *,
    base: FlywireSpatialTransform,
    num_u_bins: int,
    num_v_bins: int,
) -> FlywireSpatialTransform:
    if value is None:
        return FlywireSpatialTransform(
            swap_uv=bool(base.swap_uv),
            flip_u=bool(base.flip_u),
            flip_v=bool(base.flip_v),
            mirror_u_by_side=bool(base.mirror_u_by_side),
            u_permutation=_validate_bin_permutation(base.u_permutation, num_bins=num_u_bins, label="u_permutation"),
            v_permutation=_validate_bin_permutation(base.v_permutation, num_bins=num_v_bins, label="v_permutation"),
        )
    if isinstance(value, FlywireSpatialTransform):
        return FlywireSpatialTransform(
            swap_uv=bool(value.swap_uv),
            flip_u=bool(value.flip_u),
            flip_v=bool(value.flip_v),
            mirror_u_by_side=bool(value.mirror_u_by_side),
            u_permutation=_validate_bin_permutation(value.u_permutation, num_bins=num_u_bins, label="u_permutation"),
            v_permutation=_validate_bin_permutation(value.v_permutation, num_bins=num_v_bins, label="v_permutation"),
        )
    if not isinstance(value, Mapping):
        raise TypeError("cell_type_transforms values must be mappings or FlywireSpatialTransform instances")
    return FlywireSpatialTransform(
        swap_uv=bool(value.get("swap_uv", base.swap_uv)),
        flip_u=bool(value.get("flip_u", base.flip_u)),
        flip_v=bool(value.get("flip_v", base.flip_v)),
        mirror_u_by_side=bool(value.get("mirror_u_by_side", base.mirror_u_by_side)),
        u_permutation=_validate_bin_permutation(
            value.get("u_permutation", base.u_permutation),
            num_bins=num_u_bins,
            label="u_permutation",
        ),
        v_permutation=_validate_bin_permutation(
            value.get("v_permutation", base.v_permutation),
            num_bins=num_v_bins,
            label="v_permutation",
        ),
    )


def load_flywire_annotation_table(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep="\t", low_memory=False)
    keep_columns = [
        "root_id",
        "cell_type",
        "side",
        "pos_x",
        "pos_y",
        "pos_z",
        "soma_x",
        "soma_y",
        "soma_z",
    ]
    available = [column for column in keep_columns if column in df.columns]
    df = df[available].copy()
    df = df.dropna(subset=["root_id", "cell_type", "side"])
    df["root_id"] = df["root_id"].astype("int64")
    df["cell_type"] = df["cell_type"].astype(str)
    df["side"] = df["side"].astype(str).str.lower()
    return df


def find_exact_cell_type_overlap(
    flyvis_cell_types: Iterable[str],
    annotation_table: pd.DataFrame,
) -> list[str]:
    flyvis_types = {str(cell_type) for cell_type in flyvis_cell_types}
    flywire_types = set(annotation_table["cell_type"].astype(str))
    return sorted(flyvis_types & flywire_types)


def build_overlap_groups(
    annotation_table: pd.DataFrame,
    *,
    cell_types: Sequence[str],
    sides: Sequence[str] = ("left", "right"),
    min_roots_per_side: int = 1,
) -> list[FlywireOverlapGroup]:
    groups: list[FlywireOverlapGroup] = []
    sub = annotation_table[annotation_table["cell_type"].isin(cell_types)].copy()
    for cell_type in sorted(set(cell_types)):
        for side in sides:
            root_ids = tuple(
                sorted(
                    int(root_id)
                    for root_id in sub.loc[
                        (sub["cell_type"] == cell_type) & (sub["side"] == side),
                        "root_id",
                    ].dropna().unique().tolist()
                )
            )
            if len(root_ids) < int(min_roots_per_side):
                continue
            groups.append(FlywireOverlapGroup(cell_type=cell_type, side=str(side), root_ids=root_ids))
    return groups


def summarize_overlap_groups(groups: Sequence[FlywireOverlapGroup]) -> dict[str, object]:
    grouped_counts: dict[str, dict[str, int]] = {}
    for group in groups:
        counts = grouped_counts.setdefault(group.cell_type, {})
        counts[group.side] = len(group.root_ids)
    complete_cell_types = sorted(
        cell_type
        for cell_type, counts in grouped_counts.items()
        if counts.get("left", 0) > 0 and counts.get("right", 0) > 0
    )
    return {
        "num_groups": len(groups),
        "num_complete_bilateral_cell_types": len(complete_cell_types),
        "complete_bilateral_cell_types": complete_cell_types,
        "counts_by_cell_type": grouped_counts,
    }


def build_spatial_overlap_groups(
    annotation_table: pd.DataFrame,
    *,
    cell_types: Sequence[str],
    num_bins: int,
    sides: Sequence[str] = ("left", "right"),
    min_roots_per_bin: int = 1,
) -> list[FlywireSpatialOverlapGroup]:
    if int(num_bins) < 1:
        raise ValueError("num_bins must be at least 1")
    use_soma = all(column in annotation_table.columns for column in ("soma_x", "soma_y", "soma_z"))
    use_pos = all(column in annotation_table.columns for column in ("pos_x", "pos_y", "pos_z"))
    if not use_soma and not use_pos:
        raise ValueError("annotation_table must include soma or position columns for spatial overlap groups")
    primary_columns = ["soma_x", "soma_y", "soma_z"] if use_soma else ["pos_x", "pos_y", "pos_z"]
    fallback_columns = ["pos_x", "pos_y", "pos_z"] if use_soma and use_pos else primary_columns

    def projection(sub_df: pd.DataFrame) -> np.ndarray:
        xyz = sub_df[primary_columns].copy()
        if xyz.isna().any(axis=None) and fallback_columns != primary_columns:
            fallback = sub_df[fallback_columns].to_numpy(dtype=float)
            xyz_arr = xyz.to_numpy(dtype=float)
            mask = np.isnan(xyz_arr)
            xyz_arr[mask] = fallback[mask]
            xyz = pd.DataFrame(xyz_arr, columns=primary_columns, index=sub_df.index)
        if xyz.isna().any(axis=None):
            xyz = xyz.fillna(xyz.mean())
        arr = xyz.to_numpy(dtype=float)
        centered = arr - arr.mean(axis=0, keepdims=True)
        if arr.shape[0] < 2 or np.allclose(centered.std(axis=0), 0.0):
            return np.arange(arr.shape[0], dtype=float)
        _, _, vh = np.linalg.svd(centered, full_matrices=False)
        axis = vh[0]
        return centered @ axis

    groups: list[FlywireSpatialOverlapGroup] = []
    sub = annotation_table[annotation_table["cell_type"].isin(cell_types)].copy()
    for cell_type in sorted(set(cell_types)):
        for side in sides:
            group_df = sub[(sub["cell_type"] == cell_type) & (sub["side"] == side)].copy()
            if group_df.empty:
                continue
            scores = projection(group_df)
            order = np.argsort(scores)
            ordered_root_ids = group_df.iloc[order]["root_id"].astype("int64").to_numpy()
            for bin_index, chunk in enumerate(np.array_split(ordered_root_ids, int(num_bins))):
                root_ids = tuple(sorted(int(root_id) for root_id in np.asarray(chunk).tolist()))
                if len(root_ids) < int(min_roots_per_bin):
                    continue
                groups.append(
                    FlywireSpatialOverlapGroup(
                        cell_type=cell_type,
                        side=str(side),
                        bin_index=int(bin_index),
                        root_ids=root_ids,
                    )
                )
    return groups


def build_spatial_grid_overlap_groups(
    annotation_table: pd.DataFrame,
    *,
    cell_types: Sequence[str],
    num_u_bins: int,
    num_v_bins: int,
    swap_uv: bool = False,
    flip_u: bool = False,
    flip_v: bool = False,
    mirror_u_by_side: bool = False,
    cell_type_transforms: Mapping[str, FlywireSpatialTransform | Mapping[str, object]] | None = None,
    sides: Sequence[str] = ("left", "right"),
    min_roots_per_bin: int = 1,
) -> list[FlywireSpatialOverlapGroup]:
    if int(num_u_bins) < 1 or int(num_v_bins) < 1:
        raise ValueError("num_u_bins and num_v_bins must be at least 1")
    use_soma = all(column in annotation_table.columns for column in ("soma_x", "soma_y", "soma_z"))
    use_pos = all(column in annotation_table.columns for column in ("pos_x", "pos_y", "pos_z"))
    if not use_soma and not use_pos:
        raise ValueError("annotation_table must include soma or position columns for spatial overlap groups")
    primary_columns = ["soma_x", "soma_y", "soma_z"] if use_soma else ["pos_x", "pos_y", "pos_z"]
    fallback_columns = ["pos_x", "pos_y", "pos_z"] if use_soma and use_pos else primary_columns

    def projection_2d(sub_df: pd.DataFrame) -> np.ndarray:
        xyz = sub_df[primary_columns].copy()
        if xyz.isna().any(axis=None) and fallback_columns != primary_columns:
            fallback = sub_df[fallback_columns].to_numpy(dtype=float)
            xyz_arr = xyz.to_numpy(dtype=float)
            mask = np.isnan(xyz_arr)
            xyz_arr[mask] = fallback[mask]
            xyz = pd.DataFrame(xyz_arr, columns=primary_columns, index=sub_df.index)
        if xyz.isna().any(axis=None):
            xyz = xyz.fillna(xyz.mean())
        arr = xyz.to_numpy(dtype=float)
        centered = arr - arr.mean(axis=0, keepdims=True)
        if arr.shape[0] < 2 or np.allclose(centered.std(axis=0), 0.0):
            return np.column_stack([np.arange(arr.shape[0], dtype=float), np.zeros(arr.shape[0], dtype=float)])
        _, _, vh = np.linalg.svd(centered, full_matrices=False)
        first_axis = vh[0]
        second_axis = vh[1] if vh.shape[0] > 1 else np.array([0.0, 1.0, 0.0], dtype=float)
        return np.column_stack([centered @ first_axis, centered @ second_axis])

    def quantile_labels(values: np.ndarray, num_bins: int) -> np.ndarray:
        order = np.argsort(values, kind="stable")
        labels = np.zeros(values.shape[0], dtype=int)
        for label, chunk in enumerate(np.array_split(order, int(num_bins))):
            labels[np.asarray(chunk, dtype=int)] = int(label)
        return labels

    groups: list[FlywireSpatialOverlapGroup] = []
    sub = annotation_table[annotation_table["cell_type"].isin(cell_types)].copy()
    base_transform = FlywireSpatialTransform(
        swap_uv=bool(swap_uv),
        flip_u=bool(flip_u),
        flip_v=bool(flip_v),
        mirror_u_by_side=bool(mirror_u_by_side),
    )
    for cell_type in sorted(set(cell_types)):
        transform = _coerce_spatial_transform(
            None if cell_type_transforms is None else cell_type_transforms.get(cell_type),
            base=base_transform,
            num_u_bins=int(num_u_bins),
            num_v_bins=int(num_v_bins),
        )
        for side in sides:
            group_df = sub[(sub["cell_type"] == cell_type) & (sub["side"] == side)].copy()
            if group_df.empty:
                continue
            coords = projection_2d(group_df)
            u_coords = coords[:, 1] if transform.swap_uv else coords[:, 0]
            v_coords = coords[:, 0] if transform.swap_uv else coords[:, 1]
            u_labels = quantile_labels(u_coords, int(num_u_bins))
            v_labels = quantile_labels(v_coords, int(num_v_bins))
            if transform.flip_u:
                u_labels = (int(num_u_bins) - 1) - u_labels
            if transform.flip_v:
                v_labels = (int(num_v_bins) - 1) - v_labels
            if transform.mirror_u_by_side and str(side).lower() == "right":
                u_labels = (int(num_u_bins) - 1) - u_labels
            if transform.u_permutation is not None:
                u_labels = np.asarray(transform.u_permutation, dtype=int)[u_labels]
            if transform.v_permutation is not None:
                v_labels = np.asarray(transform.v_permutation, dtype=int)[v_labels]
            root_ids_arr = group_df["root_id"].astype("int64").to_numpy()
            for u_bin in range(int(num_u_bins)):
                for v_bin in range(int(num_v_bins)):
                    mask = (u_labels == int(u_bin)) & (v_labels == int(v_bin))
                    root_ids = tuple(sorted(int(root_id) for root_id in root_ids_arr[mask].tolist()))
                    if len(root_ids) < int(min_roots_per_bin):
                        continue
                    groups.append(
                        FlywireSpatialOverlapGroup(
                            cell_type=cell_type,
                            side=str(side),
                            bin_index=int(u_bin * int(num_v_bins) + v_bin),
                            root_ids=root_ids,
                            u_bin=int(u_bin),
                            v_bin=int(v_bin),
                        )
                    )
    return groups
