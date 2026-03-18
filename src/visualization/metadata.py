from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd


_FLYWIRE_COORD_COLUMNS = (
    "root_id",
    "cell_type",
    "hemibrain_type",
    "side",
    "pos_x",
    "pos_y",
    "pos_z",
    "soma_x",
    "soma_y",
    "soma_z",
)


def _as_path(path: str | Path) -> Path:
    return path if isinstance(path, Path) else Path(path)


def _normalize_side(value: Any) -> str:
    text = str(value).strip().lower()
    if text in {"l", "left"}:
        return "left"
    if text in {"r", "right"}:
        return "right"
    return text


def _coerce_root_id_array(value: str | Path | Sequence[int] | pd.Index | np.ndarray) -> np.ndarray:
    if isinstance(value, (str, Path)):
        frame = pd.read_csv(_as_path(value), index_col=0)
        return frame.index.to_numpy(dtype=np.int64, copy=True)
    if isinstance(value, pd.Index):
        return value.to_numpy(dtype=np.int64, copy=True)
    return np.asarray(value, dtype=np.int64).reshape(-1).copy()


def _ensure_xyz_columns(frame: pd.DataFrame, *, preference: str) -> pd.DataFrame:
    resolved = frame.copy()
    preference = str(preference).strip().lower()
    if preference not in {"soma", "pos"}:
        raise ValueError("coordinate_preference must be `soma` or `pos`")

    primary_prefix = "soma" if preference == "soma" else "pos"
    fallback_prefix = "pos" if primary_prefix == "soma" else "soma"
    coord_source = np.full(len(resolved), primary_prefix, dtype=object)

    for axis in ("x", "y", "z"):
        primary = f"{primary_prefix}_{axis}"
        fallback = f"{fallback_prefix}_{axis}"
        if primary not in resolved.columns and fallback not in resolved.columns:
            resolved[axis] = np.nan
            coord_source[:] = ""
            continue
        if primary in resolved.columns:
            values = pd.to_numeric(resolved[primary], errors="coerce")
        else:
            values = pd.Series(np.nan, index=resolved.index, dtype=float)
        if fallback in resolved.columns:
            fallback_values = pd.to_numeric(resolved[fallback], errors="coerce")
            used_fallback = values.isna() & fallback_values.notna()
            if axis == "x":
                coord_source = np.where(used_fallback.to_numpy(), fallback_prefix, coord_source)
            values = values.fillna(fallback_values)
        resolved[axis] = values.astype(float)

    empty_mask = resolved[["x", "y", "z"]].isna().all(axis=1).to_numpy()
    coord_source = np.where(empty_mask, "", coord_source)
    resolved["coord_source"] = np.asarray(coord_source, dtype=object)
    return resolved


def load_flywire_annotation_coordinates(
    annotation_path: str | Path,
    *,
    coordinate_preference: str = "soma",
    drop_duplicate_roots: bool = True,
) -> pd.DataFrame:
    path = _as_path(annotation_path)
    frame = pd.read_csv(path, sep="\t", low_memory=False)
    available = [column for column in _FLYWIRE_COORD_COLUMNS if column in frame.columns]
    frame = frame[available].copy()
    if "root_id" not in frame.columns:
        raise KeyError(f"`root_id` column is required in {path}")

    frame = frame.dropna(subset=["root_id"]).copy()
    frame["root_id"] = pd.to_numeric(frame["root_id"], errors="coerce").astype("Int64")
    frame = frame.dropna(subset=["root_id"]).copy()
    frame["root_id"] = frame["root_id"].astype(np.int64)

    if "cell_type" not in frame.columns:
        frame["cell_type"] = ""
    else:
        frame["cell_type"] = frame["cell_type"].fillna("").astype(str)

    if "hemibrain_type" not in frame.columns:
        frame["hemibrain_type"] = ""
    else:
        frame["hemibrain_type"] = frame["hemibrain_type"].fillna("").astype(str)

    if "side" not in frame.columns:
        frame["side"] = ""
    frame["side"] = frame["side"].map(_normalize_side).fillna("").astype(str)

    if drop_duplicate_roots:
        frame = frame.sort_values("root_id").drop_duplicates(subset=["root_id"], keep="first")

    frame = _ensure_xyz_columns(frame, preference=coordinate_preference)
    return frame.reset_index(drop=True)


def align_flywire_coordinates_to_backend_order(
    annotation_path: str | Path,
    backend_root_id_order: str | Path | Sequence[int] | pd.Index | np.ndarray,
    *,
    coordinate_preference: str = "soma",
    fill_value: float = np.nan,
) -> pd.DataFrame:
    annotation_frame = load_flywire_annotation_coordinates(
        annotation_path,
        coordinate_preference=coordinate_preference,
    )
    root_id_order = _coerce_root_id_array(backend_root_id_order)
    aligned = pd.DataFrame(
        {
            "backend_index": np.arange(root_id_order.shape[0], dtype=np.int64),
            "root_id": root_id_order,
        }
    )
    aligned = aligned.merge(annotation_frame, how="left", on="root_id", sort=False, copy=False)
    aligned["annotation_found"] = aligned["coord_source"].notna() & (aligned["coord_source"].astype(str) != "")
    for axis in ("x", "y", "z"):
        aligned[axis] = pd.to_numeric(aligned[axis], errors="coerce").fillna(fill_value).astype(float)
    for column in ("cell_type", "hemibrain_type", "side", "coord_source"):
        aligned[column] = aligned[column].fillna("").astype(str)
    return aligned


def flywire_coordinate_arrays(
    annotation_path: str | Path,
    backend_root_id_order: str | Path | Sequence[int] | pd.Index | np.ndarray,
    *,
    coordinate_preference: str = "soma",
    fill_value: float = np.nan,
) -> dict[str, np.ndarray]:
    aligned = align_flywire_coordinates_to_backend_order(
        annotation_path,
        backend_root_id_order,
        coordinate_preference=coordinate_preference,
        fill_value=fill_value,
    )
    return {
        "backend_index": aligned["backend_index"].to_numpy(dtype=np.int64, copy=True),
        "root_id": aligned["root_id"].to_numpy(dtype=np.int64, copy=True),
        "x": aligned["x"].to_numpy(dtype=float, copy=True),
        "y": aligned["y"].to_numpy(dtype=float, copy=True),
        "z": aligned["z"].to_numpy(dtype=float, copy=True),
        "cell_type": aligned["cell_type"].to_numpy(dtype=object, copy=True),
        "hemibrain_type": aligned["hemibrain_type"].to_numpy(dtype=object, copy=True),
        "side": aligned["side"].to_numpy(dtype=object, copy=True),
        "coord_source": aligned["coord_source"].to_numpy(dtype=object, copy=True),
        "annotation_found": aligned["annotation_found"].to_numpy(dtype=bool, copy=True),
    }


def _xyz_triplet(value: Any) -> tuple[float, float, float]:
    if not isinstance(value, Sequence) or len(value) != 3:
        return (np.nan, np.nan, np.nan)
    return tuple(float(component) for component in value)


def load_descending_decoder_candidate_metadata(
    path: str | Path,
) -> pd.DataFrame:
    payload = json.loads(_as_path(path).read_text(encoding="utf-8"))
    items = payload.get("selected_paired_cell_types") if isinstance(payload, Mapping) else None
    if not isinstance(items, list):
        raise ValueError("descending decoder candidate payload must contain `selected_paired_cell_types`")

    rows: list[dict[str, Any]] = []
    for rank, item in enumerate(items):
        if not isinstance(item, Mapping):
            continue
        left_root_ids = tuple(int(root_id) for root_id in item.get("left_root_ids", []) or [])
        right_root_ids = tuple(int(root_id) for root_id in item.get("right_root_ids", []) or [])
        left_soma = _xyz_triplet(item.get("left_soma_xyz"))
        right_soma = _xyz_triplet(item.get("right_soma_xyz"))
        left_pos = _xyz_triplet(item.get("left_pos_xyz"))
        right_pos = _xyz_triplet(item.get("right_pos_xyz"))
        rows.append(
            {
                "rank": int(rank),
                "candidate_label": str(item.get("candidate_label", "")),
                "pair_score": float(item.get("pair_score", 0.0)),
                "left_root_ids": left_root_ids,
                "right_root_ids": right_root_ids,
                "left_primary_root_id": int(left_root_ids[0]) if left_root_ids else 0,
                "right_primary_root_id": int(right_root_ids[0]) if right_root_ids else 0,
                "left_num_roots": int(item.get("left_num_roots", len(left_root_ids))),
                "right_num_roots": int(item.get("right_num_roots", len(right_root_ids))),
                "left_total_from_relays": float(item.get("left_total_from_relays", 0.0)),
                "right_total_from_relays": float(item.get("right_total_from_relays", 0.0)),
                "left_cell_types": tuple(str(value) for value in item.get("left_cell_types", []) or []),
                "right_cell_types": tuple(str(value) for value in item.get("right_cell_types", []) or []),
                "left_hemibrain_types": tuple(str(value) for value in item.get("left_hemibrain_types", []) or []),
                "right_hemibrain_types": tuple(str(value) for value in item.get("right_hemibrain_types", []) or []),
                "left_super_classes": tuple(str(value) for value in item.get("left_super_classes", []) or []),
                "right_super_classes": tuple(str(value) for value in item.get("right_super_classes", []) or []),
                "left_flows": tuple(str(value) for value in item.get("left_flows", []) or []),
                "right_flows": tuple(str(value) for value in item.get("right_flows", []) or []),
                "left_soma_x": float(left_soma[0]),
                "left_soma_y": float(left_soma[1]),
                "left_soma_z": float(left_soma[2]),
                "right_soma_x": float(right_soma[0]),
                "right_soma_y": float(right_soma[1]),
                "right_soma_z": float(right_soma[2]),
                "left_pos_x": float(left_pos[0]),
                "left_pos_y": float(left_pos[1]),
                "left_pos_z": float(left_pos[2]),
                "right_pos_x": float(right_pos[0]),
                "right_pos_y": float(right_pos[1]),
                "right_pos_z": float(right_pos[2]),
            }
        )

    return pd.DataFrame(rows)


def descending_decoder_candidate_arrays(path: str | Path) -> dict[str, np.ndarray]:
    frame = load_descending_decoder_candidate_metadata(path)
    return {
        "rank": frame["rank"].to_numpy(dtype=np.int64, copy=True),
        "candidate_label": frame["candidate_label"].to_numpy(dtype=object, copy=True),
        "pair_score": frame["pair_score"].to_numpy(dtype=float, copy=True),
        "left_primary_root_id": frame["left_primary_root_id"].to_numpy(dtype=np.int64, copy=True),
        "right_primary_root_id": frame["right_primary_root_id"].to_numpy(dtype=np.int64, copy=True),
        "left_num_roots": frame["left_num_roots"].to_numpy(dtype=np.int64, copy=True),
        "right_num_roots": frame["right_num_roots"].to_numpy(dtype=np.int64, copy=True),
        "left_total_from_relays": frame["left_total_from_relays"].to_numpy(dtype=float, copy=True),
        "right_total_from_relays": frame["right_total_from_relays"].to_numpy(dtype=float, copy=True),
        "left_root_ids": frame["left_root_ids"].to_numpy(dtype=object, copy=True),
        "right_root_ids": frame["right_root_ids"].to_numpy(dtype=object, copy=True),
        "left_cell_types": frame["left_cell_types"].to_numpy(dtype=object, copy=True),
        "right_cell_types": frame["right_cell_types"].to_numpy(dtype=object, copy=True),
        "left_hemibrain_types": frame["left_hemibrain_types"].to_numpy(dtype=object, copy=True),
        "right_hemibrain_types": frame["right_hemibrain_types"].to_numpy(dtype=object, copy=True),
        "left_soma_xyz": frame[["left_soma_x", "left_soma_y", "left_soma_z"]].to_numpy(dtype=float, copy=True),
        "right_soma_xyz": frame[["right_soma_x", "right_soma_y", "right_soma_z"]].to_numpy(dtype=float, copy=True),
        "left_pos_xyz": frame[["left_pos_x", "left_pos_y", "left_pos_z"]].to_numpy(dtype=float, copy=True),
        "right_pos_xyz": frame[["right_pos_x", "right_pos_y", "right_pos_z"]].to_numpy(dtype=float, copy=True),
    }


def flyvis_runtime_cache_arrays(source: Any) -> dict[str, np.ndarray]:
    cache = source
    if isinstance(source, Mapping):
        cache = source.get("vision_splice_cache", source.get("realistic_vision_splice_cache"))
    elif hasattr(source, "realistic_vision_splice_cache"):
        cache = getattr(source, "realistic_vision_splice_cache")

    if cache is None:
        raise ValueError("FlyVis runtime cache is missing")

    if not hasattr(cache, "node_types") or not hasattr(cache, "node_u") or not hasattr(cache, "node_v"):
        raise TypeError("FlyVis runtime cache must expose `node_types`, `node_u`, and `node_v`")

    node_types = np.asarray(getattr(cache, "node_types"), dtype=object).reshape(-1).copy()
    node_u = np.asarray(getattr(cache, "node_u"), dtype=float).reshape(-1).copy()
    node_v = np.asarray(getattr(cache, "node_v"), dtype=float).reshape(-1).copy()
    if node_types.shape[0] != node_u.shape[0] or node_types.shape[0] != node_v.shape[0]:
        raise ValueError("FlyVis runtime cache arrays must have the same length")

    return {
        "node_index": np.arange(node_types.shape[0], dtype=np.int64),
        "node_type": node_types,
        "node_u": node_u,
        "node_v": node_v,
    }


__all__ = [
    "align_flywire_coordinates_to_backend_order",
    "descending_decoder_candidate_arrays",
    "flyvis_runtime_cache_arrays",
    "flywire_coordinate_arrays",
    "load_descending_decoder_candidate_metadata",
    "load_flywire_annotation_coordinates",
]
