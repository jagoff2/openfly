from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from zipfile import ZipFile

import numpy as np
import pandas as pd
import scipy.io as sio


REGION_COUNT_SMALL = 75


@dataclass(frozen=True)
class RegionTraceRecord:
    exp_norm: str
    stem: str
    archive_path: str
    entry_name: str
    source_kind: str


def _clean_path_string(value: Any) -> str:
    text = str(value or "").strip()
    if not text or text.lower() == "nan":
        return ""
    return text


def normalize_exp_id(value: Any) -> str:
    text = _clean_path_string(value).upper()
    if text.startswith("B") and len(text) > 1:
        return text[1:]
    return text


def basename_or_empty(value: Any) -> str:
    text = _clean_path_string(value)
    return Path(text).name if text else ""


def _region_stem_from_entry_name(entry_name: str) -> str | None:
    name = Path(entry_name).name
    for suffix in ("_Regions.npy", "_LargeRegions.npy", "_Walk.npy", "_Left.npy", "_Right.npy"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return None


def _orient_region_matrix(array: np.ndarray) -> np.ndarray:
    matrix = np.asarray(array)
    if matrix.ndim != 2:
        raise ValueError(f"expected 2D region matrix, got shape {matrix.shape}")
    if matrix.shape[0] == REGION_COUNT_SMALL:
        return matrix.astype(np.float32, copy=False)
    if matrix.shape[1] == REGION_COUNT_SMALL:
        return matrix.T.astype(np.float32, copy=False)
    if matrix.shape[0] < matrix.shape[1]:
        return matrix.astype(np.float32, copy=False)
    return matrix.T.astype(np.float32, copy=False)


def _load_npy_from_zip(archive_path: str | Path, entry_name: str) -> np.ndarray:
    with ZipFile(Path(archive_path)) as archive:
        payload = archive.read(entry_name)
    return np.load(io.BytesIO(payload), allow_pickle=True)


def _load_mat_from_zip(archive_path: str | Path, entry_name: str) -> dict[str, Any]:
    with ZipFile(Path(archive_path)) as archive:
        payload = archive.read(entry_name)
    return sio.loadmat(io.BytesIO(payload))


def build_region_trace_inventory(
    *,
    walk_archive_path: str | Path,
    additional_archive_path: str | Path,
) -> dict[str, list[RegionTraceRecord]]:
    inventory: dict[str, list[RegionTraceRecord]] = {}
    archive_specs = [
        (Path(walk_archive_path), "walk_archive", "Walk_anatomical_regions/"),
        (Path(additional_archive_path), "additional_archive", "AdditionalRegionalTimeSeries/"),
    ]
    for archive_path, source_kind, folder_prefix in archive_specs:
        with ZipFile(archive_path) as archive:
            for entry_name in archive.namelist():
                if folder_prefix not in entry_name or not entry_name.endswith("_Regions.npy"):
                    continue
                stem = _region_stem_from_entry_name(entry_name)
                if not stem:
                    continue
                exp_norm = normalize_exp_id(stem.split("_")[-1])
                inventory.setdefault(exp_norm, []).append(
                    RegionTraceRecord(
                        exp_norm=exp_norm,
                        stem=stem,
                        archive_path=str(archive_path),
                        entry_name=entry_name,
                        source_kind=source_kind,
                    )
                )
    return inventory


def build_additional_regressor_inventory(additional_archive_path: str | Path) -> set[str]:
    with ZipFile(Path(additional_archive_path)) as archive:
        return {
            Path(entry_name).name
            for entry_name in archive.namelist()
            if "AllRegressors/" in entry_name and not entry_name.endswith("/")
        }


def build_goodics_table(goodics_path: str | Path) -> pd.DataFrame:
    table = pd.read_pickle(Path(goodics_path)).copy()
    for column in ("WalkRegressor", "TurnRegressor", "ForcedWalkRegressor", "ForcedTurnRegressor"):
        table[f"{column}_base"] = table[column].map(basename_or_empty) if column in table.columns else ""
    table["exp_norm"] = table["expID"].map(normalize_exp_id)
    table["GAL4"] = table.get("GAL4", "").fillna("").astype(str)
    table["UAS"] = table.get("UAS", "").fillna("").astype(str)
    table["WalkSubstrate"] = table.get("WalkSubstrate", "").fillna("").astype(str)
    return table


def _load_region_trace(record: RegionTraceRecord) -> np.ndarray:
    return _orient_region_matrix(_load_npy_from_zip(record.archive_path, record.entry_name))


def _load_walk_regressor_from_walk_archive(record: RegionTraceRecord) -> np.ndarray | None:
    walk_entry = f"{Path(record.entry_name).parent.as_posix()}/{record.stem}_Walk.npy"
    try:
        array = _load_npy_from_zip(record.archive_path, walk_entry)
    except KeyError:
        return None
    return np.asarray(array, dtype=np.float32).reshape(-1)


def _load_rkd_regressor(additional_archive_path: str | Path, base_name: str) -> np.ndarray | None:
    if not base_name:
        return None
    entry_name = f"Additional_data/AllRegressors/{base_name}"
    try:
        payload = _load_mat_from_zip(additional_archive_path, entry_name)
    except KeyError:
        return None
    array = payload.get("Rkd")
    if array is None:
        return None
    return np.asarray(array, dtype=np.float32).reshape(-1)


def _candidate_window_bounds(low: Any, high: Any, frame_count: int, target_len: int) -> tuple[int, int]:
    full = (0, frame_count)
    low_val = _clean_path_string(low)
    high_val = _clean_path_string(high)
    if not low_val or not high_val:
        return full
    try:
        low_i = int(float(low_val))
        high_i = int(float(high_val))
    except ValueError:
        return full
    candidates: list[tuple[int, int]] = []
    for start in (low_i, max(low_i - 1, 0)):
        for end in (high_i, high_i + 1):
            if start < 0 or end <= start:
                continue
            bounded = (max(0, start), min(frame_count, end))
            if bounded[1] > bounded[0]:
                candidates.append(bounded)
    for start, end in candidates:
        if end - start == target_len:
            return (start, end)
    if candidates:
        return min(candidates, key=lambda bounds: abs((bounds[1] - bounds[0]) - target_len))
    return full


def _align_region_segment(region_matrix: np.ndarray, regressor: np.ndarray, low: Any, high: Any) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    frames = int(region_matrix.shape[1])
    regressor_1d = np.asarray(regressor, dtype=np.float32).reshape(-1)
    start, end = _candidate_window_bounds(low, high, frames, int(regressor_1d.size))
    region_segment = region_matrix[:, start:end]
    regressor_segment = regressor_1d
    exact = region_segment.shape[1] == regressor_segment.size
    if not exact:
        trim = min(int(region_segment.shape[1]), int(regressor_segment.size))
        region_segment = region_segment[:, :trim]
        regressor_segment = regressor_segment[:trim]
    return region_segment, regressor_segment, {
        "window_start": int(start),
        "window_end": int(start + region_segment.shape[1]),
        "full_frame_count": frames,
        "regressor_length": int(regressor_1d.size),
        "aligned_length": int(region_segment.shape[1]),
        "exact_window_match": bool(exact),
    }


def _corr_profile(region_segment: np.ndarray, regressor_segment: np.ndarray) -> np.ndarray:
    regions = np.asarray(region_segment, dtype=np.float32)
    reg = np.asarray(regressor_segment, dtype=np.float32).reshape(1, -1)
    if regions.ndim != 2 or reg.shape[1] < 3:
        raise ValueError("insufficient aligned samples for correlation profile")
    regions = regions - regions.mean(axis=1, keepdims=True)
    reg = reg - reg.mean(axis=1, keepdims=True)
    denom = np.linalg.norm(regions, axis=1) * np.linalg.norm(reg, axis=1)[0]
    numer = np.sum(regions * reg, axis=1)
    profile = np.divide(numer, denom, out=np.zeros_like(numer), where=denom > 1e-8)
    return profile.astype(np.float32, copy=False)


def _profile_correlation(left: np.ndarray, right: np.ndarray) -> float:
    left_vec = np.asarray(left, dtype=np.float32).reshape(-1)
    right_vec = np.asarray(right, dtype=np.float32).reshape(-1)
    if left_vec.size != right_vec.size or left_vec.size < 3:
        return float("nan")
    left_centered = left_vec - left_vec.mean()
    right_centered = right_vec - right_vec.mean()
    denom = float(np.linalg.norm(left_centered) * np.linalg.norm(right_centered))
    if denom <= 1e-8:
        return float("nan")
    return float(np.dot(left_centered, right_centered) / denom)


def _build_spontaneous_profiles(
    table: pd.DataFrame,
    *,
    region_inventory: dict[str, list[RegionTraceRecord]],
    additional_archive_path: str | Path,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, record in table.iterrows():
        walk_base = str(record.get("WalkRegressor_base", ""))
        exp_norm = str(record.get("exp_norm", ""))
        if not walk_base or exp_norm not in region_inventory:
            continue
        regressor = _load_rkd_regressor(additional_archive_path, walk_base)
        if regressor is None:
            continue
        for region_record in region_inventory[exp_norm]:
            region_matrix = _load_region_trace(region_record)
            region_segment, regressor_segment, align_summary = _align_region_segment(
                region_matrix,
                regressor,
                record.get("TSlowlimWalk", ""),
                record.get("TShighlimWalk", ""),
            )
            if region_segment.shape[1] < 3:
                continue
            profile = _corr_profile(region_segment, regressor_segment)
            rows.append(
                {
                    "expID": str(record.get("expID", "")),
                    "exp_norm": exp_norm,
                    "GAL4": str(record.get("GAL4", "")),
                    "UAS": str(record.get("UAS", "")),
                    "FR": float(record.get("FR")) if pd.notna(record.get("FR")) else float("nan"),
                    "WalkSubstrate": str(record.get("WalkSubstrate", "")),
                    "region_source": region_record.source_kind,
                    "region_stem": region_record.stem,
                    "walk_regressor_base": walk_base,
                    "profile": profile,
                    **align_summary,
                }
            )
    return pd.DataFrame(rows)


def _build_forced_profiles(
    table: pd.DataFrame,
    *,
    region_inventory: dict[str, list[RegionTraceRecord]],
    additional_archive_path: str | Path,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, record in table.iterrows():
        forced_base = str(record.get("ForcedWalkRegressor_base", ""))
        exp_norm = str(record.get("exp_norm", ""))
        if not forced_base or exp_norm not in region_inventory:
            continue
        regressor = _load_rkd_regressor(additional_archive_path, forced_base)
        if regressor is None:
            continue
        for region_record in region_inventory[exp_norm]:
            region_matrix = _load_region_trace(region_record)
            region_segment, regressor_segment, align_summary = _align_region_segment(
                region_matrix,
                regressor,
                record.get("TSlowlimForced", ""),
                record.get("TShighlimForced", ""),
            )
            if region_segment.shape[1] < 3:
                continue
            profile = _corr_profile(region_segment, regressor_segment)
            rows.append(
                {
                    "expID": str(record.get("expID", "")),
                    "exp_norm": exp_norm,
                    "GAL4": str(record.get("GAL4", "")),
                    "UAS": str(record.get("UAS", "")),
                    "FR": float(record.get("FR")) if pd.notna(record.get("FR")) else float("nan"),
                    "WalkSubstrate": str(record.get("WalkSubstrate", "")),
                    "region_source": region_record.source_kind,
                    "region_stem": region_record.stem,
                    "forced_walk_regressor_base": forced_base,
                    "forced_turn_regressor_base": str(record.get("ForcedTurnRegressor_base", "")),
                    "profile": profile,
                    **align_summary,
                }
            )
    return pd.DataFrame(rows)


def _match_tier(
    forced_row: pd.Series,
    spontaneous_profiles: pd.DataFrame,
) -> tuple[str, pd.DataFrame]:
    same_exp = spontaneous_profiles[spontaneous_profiles["exp_norm"] == forced_row["exp_norm"]]
    if not same_exp.empty:
        return ("same_experiment", same_exp)
    tiers = [
        ("same_line_indicator_frame_substrate", ["GAL4", "UAS", "FR", "WalkSubstrate"]),
        ("same_line_indicator_frame", ["GAL4", "UAS", "FR"]),
        ("same_line_indicator", ["GAL4", "UAS"]),
    ]
    for tier_name, columns in tiers:
        mask = pd.Series(True, index=spontaneous_profiles.index)
        for column in columns:
            value = forced_row[column]
            if pd.isna(value):
                mask &= spontaneous_profiles[column].isna()
            else:
                mask &= spontaneous_profiles[column] == value
        matched = spontaneous_profiles[mask]
        if not matched.empty:
            return (tier_name, matched)
    return ("unmatched", spontaneous_profiles.iloc[0:0])


def compute_aimon_forced_spontaneous_comparator(
    *,
    goodics_path: str | Path,
    walk_archive_path: str | Path,
    additional_archive_path: str | Path,
) -> tuple[dict[str, Any], pd.DataFrame]:
    goodics = build_goodics_table(goodics_path)
    region_inventory = build_region_trace_inventory(
        walk_archive_path=walk_archive_path,
        additional_archive_path=additional_archive_path,
    )
    spontaneous_profiles = _build_spontaneous_profiles(
        goodics,
        region_inventory=region_inventory,
        additional_archive_path=additional_archive_path,
    )
    forced_profiles = _build_forced_profiles(
        goodics,
        region_inventory=region_inventory,
        additional_archive_path=additional_archive_path,
    )
    rows: list[dict[str, Any]] = []
    if forced_profiles.empty:
        summary = {
            "status": "no_forced_profiles",
            "forced_profile_count": 0,
            "spontaneous_profile_count": int(len(spontaneous_profiles)),
            "comparator_count": 0,
        }
        return summary, pd.DataFrame(rows)

    for _, forced_row in forced_profiles.iterrows():
        tier_name, matched = _match_tier(forced_row, spontaneous_profiles)
        if matched.empty:
            rows.append(
                {
                    "expID": forced_row["expID"],
                    "exp_norm": forced_row["exp_norm"],
                    "GAL4": forced_row["GAL4"],
                    "UAS": forced_row["UAS"],
                    "FR": forced_row["FR"],
                    "WalkSubstrate": forced_row["WalkSubstrate"],
                    "region_source": forced_row["region_source"],
                    "region_stem": forced_row["region_stem"],
                    "forced_walk_regressor_base": forced_row["forced_walk_regressor_base"],
                    "match_tier": tier_name,
                    "matched_spontaneous_count": 0,
                    "region_profile_corr": float("nan"),
                    "forced_aligned_length": int(forced_row["aligned_length"]),
                }
            )
            continue
        spontaneous_stack = np.stack(matched["profile"].to_list(), axis=0)
        spontaneous_mean = spontaneous_stack.mean(axis=0)
        similarity = _profile_correlation(np.asarray(forced_row["profile"]), spontaneous_mean)
        rows.append(
            {
                "expID": forced_row["expID"],
                "exp_norm": forced_row["exp_norm"],
                "GAL4": forced_row["GAL4"],
                "UAS": forced_row["UAS"],
                "FR": forced_row["FR"],
                "WalkSubstrate": forced_row["WalkSubstrate"],
                "region_source": forced_row["region_source"],
                "region_stem": forced_row["region_stem"],
                "forced_walk_regressor_base": forced_row["forced_walk_regressor_base"],
                "forced_turn_regressor_base": forced_row["forced_turn_regressor_base"],
                "match_tier": tier_name,
                "matched_spontaneous_count": int(len(matched)),
                "matched_spontaneous_exp_ids": ",".join(sorted(set(matched["expID"].astype(str).tolist()))),
                "region_profile_corr": similarity,
                "forced_aligned_length": int(forced_row["aligned_length"]),
                "spontaneous_aligned_length_mean": float(np.nanmean(matched["aligned_length"].to_numpy(dtype=np.float32))),
            }
        )

    table = pd.DataFrame(rows).sort_values(["match_tier", "expID"], kind="stable").reset_index(drop=True)
    valid = table["region_profile_corr"].dropna().to_numpy(dtype=np.float32) if not table.empty else np.asarray([], dtype=np.float32)
    tier_counts = (
        table["match_tier"].value_counts(dropna=False).to_dict()
        if not table.empty
        else {}
    )
    summary = {
        "status": "ok" if valid.size else "no_matches",
        "forced_profile_count": int(len(forced_profiles)),
        "spontaneous_profile_count": int(len(spontaneous_profiles)),
        "comparator_count": int(len(table)),
        "valid_similarity_count": int(valid.size),
        "region_profile_corr_mean": float(valid.mean()) if valid.size else float("nan"),
        "region_profile_corr_median": float(np.median(valid)) if valid.size else float("nan"),
        "region_profile_corr_min": float(valid.min()) if valid.size else float("nan"),
        "region_profile_corr_max": float(valid.max()) if valid.size else float("nan"),
        "positive_similarity_fraction": float(np.mean(valid > 0.0)) if valid.size else float("nan"),
        "match_tier_counts": {str(key): int(value) for key, value in tier_counts.items()},
        "same_experiment_count": int((table["match_tier"] == "same_experiment").sum()) if not table.empty else 0,
    }
    return summary, table

