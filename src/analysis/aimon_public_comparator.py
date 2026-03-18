from __future__ import annotations

import io
import math
import re
import zipfile
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


EXP_ID_PATTERN = re.compile(r"(B\d{3,6}|\d{3,6})", re.IGNORECASE)
REGION_KIND_PATTERN = re.compile(r"(.+?)_(Regions|LargeRegions|RegionNames|Walk|Left|Right)$", re.IGNORECASE)


def _normalize_token(value: str | Path | None) -> str:
    text = Path(str(value or "")).stem.lower()
    return re.sub(r"[^a-z0-9]+", "", text)


def _extract_exp_id(value: str | Path | None) -> str | None:
    text = Path(str(value or "")).stem
    match = EXP_ID_PATTERN.search(text)
    if not match:
        return None
    return str(match.group(1))


def index_aimon_archive_members(path: str | Path) -> pd.DataFrame:
    archive_path = Path(path)
    rows: list[dict[str, Any]] = []
    with zipfile.ZipFile(archive_path) as archive:
        for member_name in archive.namelist():
            if member_name.endswith("/"):
                continue
            member_path = Path(member_name)
            stem = member_path.stem
            suffix = member_path.suffix.lower()
            region_match = REGION_KIND_PATTERN.match(stem)
            rows.append(
                {
                    "member_name": member_name,
                    "stem": stem,
                    "normalized_stem": _normalize_token(stem),
                    "exp_id": _extract_exp_id(stem),
                    "suffix": suffix,
                    "region_kind": str(region_match.group(2)) if region_match else "",
                    "top_dir": member_path.parts[0] if member_path.parts else "",
                }
            )
    return pd.DataFrame(rows)


def _load_archive_array(archive: zipfile.ZipFile, member_name: str) -> np.ndarray:
    suffix = Path(member_name).suffix.lower()
    payload = archive.read(member_name)
    if suffix == ".npy":
        return np.asarray(np.load(io.BytesIO(payload), allow_pickle=True))
    if suffix == ".mat":
        try:
            from scipy.io import loadmat  # type: ignore
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"scipy is required to load MAT file {member_name}") from exc
        data = loadmat(io.BytesIO(payload))
        preferred_keys = ("Rkd", "Leftkd", "Rightkd", "Straightkd", "Ronkd", "Roffkd")
        for key in preferred_keys:
            if key in data:
                return np.asarray(data[key]).squeeze()
        for key, value in data.items():
            if key.startswith("__"):
                continue
            array = np.asarray(value)
            if array.size > 0:
                return array.squeeze()
        raise KeyError(f"No numeric variable found in MAT file {member_name}")
    raise ValueError(f"Unsupported archive member suffix for {member_name}")


def _select_region_member(region_index: pd.DataFrame, exp_id: str) -> str | None:
    if region_index.empty:
        return None
    subset = region_index[region_index["exp_id"].fillna("").str.lower() == str(exp_id).lower()].copy()
    if subset.empty:
        return None
    for preferred_kind in ("Regions", "LargeRegions"):
        preferred = subset[subset["region_kind"].str.lower() == preferred_kind.lower()]
        if not preferred.empty:
            return str(preferred.iloc[0]["member_name"])
    return str(subset.iloc[0]["member_name"])


def _candidate_additional_region_members(index_table: pd.DataFrame, exp_id: str) -> list[str]:
    if index_table.empty:
        return []
    subset = index_table[index_table["exp_id"].fillna("").str.lower() == str(exp_id).lower()].copy()
    if subset.empty:
        return []
    disallowed = (
        subset["member_name"]
        .astype(str)
        .str.lower()
        .str.contains(r"allregressors|walk|forced|left|right|dir|turn|rbinkd|rkd|ron|roff", regex=True)
    )
    subset = subset[~disallowed].copy()
    subset = subset[subset["suffix"].isin([".npy", ".mat"])].copy()
    return subset["member_name"].astype(str).tolist()


def _match_member_by_source(index_table: pd.DataFrame, source_value: str | float | int | None) -> str | None:
    if index_table.empty:
        return None
    if source_value is None or (isinstance(source_value, float) and math.isnan(source_value)):
        return None
    token = _normalize_token(str(source_value))
    if not token:
        return None
    exact = index_table[index_table["normalized_stem"] == token]
    if not exact.empty:
        return str(exact.iloc[0]["member_name"])
    contains = index_table[index_table["normalized_stem"].astype(str).str.contains(token, regex=False)]
    if not contains.empty:
        return str(contains.iloc[0]["member_name"])
    basename = _normalize_token(Path(str(source_value)).name)
    if basename and basename != token:
        exact = index_table[index_table["normalized_stem"] == basename]
        if not exact.empty:
            return str(exact.iloc[0]["member_name"])
        contains = index_table[index_table["normalized_stem"].astype(str).str.contains(basename, regex=False)]
        if not contains.empty:
            return str(contains.iloc[0]["member_name"])
    return None


def _orient_region_matrix(matrix: np.ndarray, *, expected_time_len: int) -> np.ndarray | None:
    array = np.asarray(matrix)
    if array.ndim != 2:
        return None
    rows, cols = int(array.shape[0]), int(array.shape[1])
    row_ok = rows >= expected_time_len
    col_ok = cols >= expected_time_len
    if col_ok and not row_ok:
        return array.astype(np.float32, copy=False)
    if row_ok and not col_ok:
        return array.T.astype(np.float32, copy=False)
    if col_ok and row_ok:
        return (array if cols >= rows else array.T).astype(np.float32, copy=False)
    return None


def _load_best_region_matrix(
    *,
    exp_id: str,
    expected_time_len: int,
    region_member: str | None,
    region_archive: zipfile.ZipFile | None,
    region_index: pd.DataFrame,
    additional_archive: zipfile.ZipFile,
    additional_index: pd.DataFrame,
) -> tuple[np.ndarray | None, str | None, str | None]:
    candidates: list[tuple[str, str]] = []
    if region_member and region_archive is not None:
        candidates.append(("walk_anatomical_regions", region_member))
    for member_name in _candidate_additional_region_members(additional_index, exp_id):
        candidates.append(("additional_data", member_name))
    best_matrix: np.ndarray | None = None
    best_member: str | None = None
    best_source: str | None = None
    best_score: tuple[int, int, int] | None = None
    for source_name, member_name in candidates:
        try:
            archive = region_archive if source_name == "walk_anatomical_regions" else additional_archive
            if archive is None:
                continue
            matrix_raw = _load_archive_array(archive, member_name)
            matrix = _orient_region_matrix(matrix_raw, expected_time_len=expected_time_len)
        except Exception:  # noqa: BLE001
            continue
        if matrix is None or matrix.shape[1] < expected_time_len:
            continue
        is_functional_regions = "FunctionallyDefinedAnatomicalRegions" in member_name
        is_additional_region = "AdditionalRegionalTimeSeries" in member_name
        source_priority = 2 if is_functional_regions else 1 if is_additional_region else 0
        score = (source_priority, int(matrix.shape[1]), int(matrix.shape[0]))
        if best_score is None or score > best_score:
            best_matrix = matrix
            best_member = member_name
            best_source = source_name
            best_score = score
    return best_matrix, best_member, best_source


def _paired_finite(left: np.ndarray, right: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    left_arr = np.asarray(left, dtype=np.float32).reshape(-1)
    right_arr = np.asarray(right, dtype=np.float32).reshape(-1)
    if left_arr.size == 0 or right_arr.size == 0 or left_arr.size != right_arr.size:
        return np.asarray([], dtype=np.float32), np.asarray([], dtype=np.float32)
    finite = np.isfinite(left_arr) & np.isfinite(right_arr)
    if not np.any(finite):
        return np.asarray([], dtype=np.float32), np.asarray([], dtype=np.float32)
    return left_arr[finite], right_arr[finite]


def _nanmean_rows(array: np.ndarray) -> np.ndarray:
    values = np.asarray(array, dtype=np.float32)
    if values.ndim != 2:
        raise ValueError("Expected a 2D array for row-wise nanmean")
    finite = np.isfinite(values)
    counts = finite.sum(axis=1)
    sums = np.where(finite, values, 0.0).sum(axis=1, dtype=np.float64)
    result = np.full(values.shape[0], np.nan, dtype=np.float32)
    valid = counts > 0
    if np.any(valid):
        result[valid] = (sums[valid] / counts[valid]).astype(np.float32)
    return result


def _window_slice(start_value: Any, stop_value: Any, *, length: int) -> slice | None:
    if pd.isna(start_value) or pd.isna(stop_value):
        return None
    start = max(0, int(round(float(start_value))) - 1)
    stop = min(length, int(round(float(stop_value))))
    if stop <= start:
        return None
    return slice(start, stop)


def _safe_pearson(left: np.ndarray, right: np.ndarray) -> float:
    left_finite, right_finite = _paired_finite(left, right)
    if left_finite.size < 2:
        return float("nan")
    if np.allclose(left_finite, left_finite[0]) or np.allclose(right_finite, right_finite[0]):
        return float("nan")
    return float(np.corrcoef(left_finite, right_finite)[0, 1])


def _safe_cosine(left: np.ndarray, right: np.ndarray) -> float:
    left_finite, right_finite = _paired_finite(left, right)
    if left_finite.size < 2:
        return float("nan")
    left_norm = float(np.linalg.norm(left_finite))
    right_norm = float(np.linalg.norm(right_finite))
    if left_norm <= 0.0 or right_norm <= 0.0:
        return float("nan")
    return float(np.dot(left_finite, right_finite) / (left_norm * right_norm))


def _safe_spearman(left: np.ndarray, right: np.ndarray) -> float:
    left_finite, right_finite = _paired_finite(left, right)
    if left_finite.size < 2:
        return float("nan")
    left_rank = pd.Series(left_finite).rank(method="average").to_numpy(dtype=np.float32)
    right_rank = pd.Series(right_finite).rank(method="average").to_numpy(dtype=np.float32)
    return _safe_pearson(left_rank, right_rank)


def _slice_overlap_fraction(left: slice, right: slice) -> float:
    left_len = int(left.stop - left.start)
    right_len = int(right.stop - right.start)
    if left_len <= 0 or right_len <= 0:
        return float("nan")
    overlap = max(0, min(int(left.stop), int(right.stop)) - max(int(left.start), int(right.start)))
    return float(overlap / min(left_len, right_len))


def _spontaneous_prelead_metrics(
    region_matrix: np.ndarray,
    walk_slice: slice,
    forced_slice: slice,
) -> dict[str, float]:
    walk_len = int(walk_slice.stop - walk_slice.start)
    forced_len = int(forced_slice.stop - forced_slice.start)
    pre_width = min(100, walk_len, forced_len, int(walk_slice.start) // 2, int(forced_slice.start) // 2)
    if pre_width < 5:
        return {
            "spontaneous_prelead_fraction": float("nan"),
            "spontaneous_minus_forced_prelead_delta": float("nan"),
            "prelead_width_frames": int(pre_width),
            "prelead_valid_region_count": 0,
        }
    spont_baseline = _nanmean_rows(region_matrix[:, walk_slice.start - 2 * pre_width : walk_slice.start - pre_width])
    spont_pre = _nanmean_rows(region_matrix[:, walk_slice.start - pre_width : walk_slice.start])
    forced_baseline = _nanmean_rows(
        region_matrix[:, forced_slice.start - 2 * pre_width : forced_slice.start - pre_width]
    )
    forced_pre = _nanmean_rows(region_matrix[:, forced_slice.start - pre_width : forced_slice.start])
    spont_delta = spont_pre - spont_baseline
    forced_delta = forced_pre - forced_baseline
    valid = np.isfinite(spont_delta) & np.isfinite(forced_delta)
    if int(np.sum(valid)) < 3:
        return {
            "spontaneous_prelead_fraction": float("nan"),
            "spontaneous_minus_forced_prelead_delta": float("nan"),
            "prelead_width_frames": int(pre_width),
            "prelead_valid_region_count": int(np.sum(valid)),
        }
    spontaneous_leading = (spont_delta[valid] > 0.0) & (forced_delta[valid] <= 0.0)
    return {
        "spontaneous_prelead_fraction": float(np.mean(spontaneous_leading.astype(np.float32))),
        "spontaneous_minus_forced_prelead_delta": float(np.median(spont_delta[valid] - forced_delta[valid])),
        "prelead_width_frames": int(pre_width),
        "prelead_valid_region_count": int(np.sum(valid)),
    }


def _nanmedian_series(table: pd.DataFrame, column: str) -> float:
    if column not in table.columns:
        return float("nan")
    values = pd.to_numeric(table[column], errors="coerce").to_numpy(dtype=np.float64)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return float("nan")
    return float(np.median(values))


def _filter_candidate_rows(goodics: pd.DataFrame) -> pd.DataFrame:
    required = ["TSlowlimForced", "TShighlimForced", "TSlowlimWalk", "TShighlimWalk", "expID"]
    mask = np.ones(len(goodics), dtype=bool)
    for column in required:
        mask &= goodics[column].notna().to_numpy()
    return goodics.loc[mask].copy()


def summarize_public_forced_vs_spontaneous_walk(dataset_root: str | Path) -> dict[str, Any]:
    dataset_root = Path(dataset_root)
    goodics_path = dataset_root / "GoodICsdf.pkl"
    additional_path = dataset_root / "Additional_data.zip"
    regions_path = dataset_root / "Walk_anatomical_regions.zip"
    missing = [path.name for path in (goodics_path, additional_path) if not path.exists()]
    if missing:
        return {
            "status": "blocked_missing_files",
            "dataset_root": str(dataset_root),
            "missing_files": missing,
            "n_candidate_rows": 0,
            "n_experiments_used": 0,
            "dropped_experiments": [],
            "per_experiment_rows": [],
        }

    goodics = pd.read_pickle(goodics_path)
    candidates = _filter_candidate_rows(goodics)
    use_regions_archive = regions_path.exists()
    region_index = index_aimon_archive_members(regions_path) if use_regions_archive else pd.DataFrame()
    additional_index = index_aimon_archive_members(additional_path)
    region_member_names = set(region_index["member_name"].astype(str).tolist()) if "member_name" in region_index.columns else set()
    per_experiment_rows: list[dict[str, Any]] = []
    dropped: list[dict[str, str]] = []

    with zipfile.ZipFile(additional_path) as additional_archive:
        regions_archive_ctx = zipfile.ZipFile(regions_path) if use_regions_archive else None
        try:
            regions_archive = regions_archive_ctx
            for _, row in candidates.iterrows():
                exp_id = str(row["expID"])
                region_member = _select_region_member(region_index, exp_id)
                walk_regressor_member = _match_member_by_source(additional_index, row.get("WalkRegressor"))
                if not walk_regressor_member and use_regions_archive:
                    walk_match = region_index[
                        (region_index["exp_id"].fillna("").str.lower() == exp_id.lower())
                        & (region_index["region_kind"].str.lower() == "walk")
                    ]
                    if not walk_match.empty:
                        walk_regressor_member = str(walk_match.iloc[0]["member_name"])
                forced_walk_member = _match_member_by_source(additional_index, row.get("ForcedWalkRegressor"))
                walk_high = int(round(float(row["TShighlimWalk"])))
                forced_high = int(round(float(row["TShighlimForced"])))
                expected_time_len = max(walk_high, forced_high)
                walk_regressor: np.ndarray | None = None
                forced_regressor: np.ndarray | None = None
                if walk_regressor_member:
                    try:
                        walk_archive = regions_archive if walk_regressor_member in region_member_names else additional_archive
                        walk_regressor = np.asarray(_load_archive_array(walk_archive, walk_regressor_member)).squeeze()
                        expected_time_len = max(expected_time_len, int(walk_regressor.size))
                    except Exception as exc:  # noqa: BLE001
                        dropped.append({"exp_id": exp_id, "reason": f"walk_regressor_load_failed:{type(exc).__name__}"})
                        continue
                if forced_walk_member:
                    try:
                        forced_regressor = np.asarray(_load_archive_array(additional_archive, forced_walk_member)).squeeze()
                        expected_time_len = max(expected_time_len, int(forced_regressor.size))
                    except Exception as exc:  # noqa: BLE001
                        dropped.append({"exp_id": exp_id, "reason": f"forced_regressor_load_failed:{type(exc).__name__}"})
                        continue
                region_matrix, region_member_used, region_source = _load_best_region_matrix(
                    exp_id=exp_id,
                    expected_time_len=expected_time_len,
                    region_member=region_member,
                    region_archive=regions_archive,
                    region_index=region_index,
                    additional_archive=additional_archive,
                    additional_index=additional_index,
                )
                if region_matrix is None or not region_member_used or not region_source:
                    dropped.append({"exp_id": exp_id, "reason": "missing_full_length_region_trace"})
                    continue
                walk_slice = _window_slice(row["TSlowlimWalk"], row["TShighlimWalk"], length=region_matrix.shape[1])
                forced_slice = _window_slice(row["TSlowlimForced"], row["TShighlimForced"], length=region_matrix.shape[1])
                if walk_slice is None or forced_slice is None:
                    dropped.append({"exp_id": exp_id, "reason": "invalid_window_bounds"})
                    continue
                overlap_fraction = _slice_overlap_fraction(walk_slice, forced_slice)
                if math.isfinite(overlap_fraction) and overlap_fraction > 0.0:
                    dropped.append(
                        {
                            "exp_id": exp_id,
                            "reason": "overlapping_walk_forced_windows",
                            "window_overlap_fraction": float(overlap_fraction),
                        }
                    )
                    continue
                spontaneous_vector = _nanmean_rows(region_matrix[:, walk_slice])
                forced_vector = _nanmean_rows(region_matrix[:, forced_slice])
                valid_vector_mask = np.isfinite(spontaneous_vector) & np.isfinite(forced_vector)
                prelead = _spontaneous_prelead_metrics(region_matrix, walk_slice, forced_slice)
                per_experiment_rows.append(
                    {
                        "exp_id": exp_id,
                        "region_member": region_member_used,
                        "region_source": region_source,
                        "spontaneous_walk_regressor_member": walk_regressor_member,
                        "forced_walk_regressor_member": forced_walk_member,
                        "region_count": int(region_matrix.shape[0]),
                        "time_count": int(region_matrix.shape[1]),
                        "walk_window_frames": int(walk_slice.stop - walk_slice.start),
                        "forced_window_frames": int(forced_slice.stop - forced_slice.start),
                        "window_overlap_fraction": float(overlap_fraction),
                        "valid_vector_region_count": int(np.sum(valid_vector_mask)),
                        "steady_walk_vector_corr": _safe_pearson(spontaneous_vector, forced_vector),
                        "steady_walk_vector_cosine": _safe_cosine(spontaneous_vector, forced_vector),
                        "steady_walk_rank_corr": _safe_spearman(spontaneous_vector, forced_vector),
                        **prelead,
                    }
                )
        finally:
            if regions_archive_ctx is not None:
                regions_archive_ctx.close()

    table = pd.DataFrame(per_experiment_rows)
    if table.empty:
        return {
            "status": "blocked_no_matches",
            "dataset_root": str(dataset_root),
            "missing_files": [],
            "n_candidate_rows": int(len(candidates)),
            "n_experiments_used": 0,
            "dropped_experiments": dropped,
            "per_experiment_rows": [],
        }

    status = "ok" if len(table) >= 2 else "partial_low_match_count"
    return {
        "status": status,
        "dataset_root": str(dataset_root),
        "missing_files": [],
        "n_candidate_rows": int(len(candidates)),
        "n_experiments_used": int(len(table)),
        "n_valid_vector_corr": int(np.isfinite(pd.to_numeric(table["steady_walk_vector_corr"], errors="coerce")).sum()),
        "n_valid_rank_corr": int(np.isfinite(pd.to_numeric(table["steady_walk_rank_corr"], errors="coerce")).sum()),
        "n_valid_prelead_fraction": int(
            np.isfinite(pd.to_numeric(table["spontaneous_prelead_fraction"], errors="coerce")).sum()
        ),
        "median_steady_walk_vector_corr": _nanmedian_series(table, "steady_walk_vector_corr"),
        "median_steady_walk_vector_cosine": _nanmedian_series(table, "steady_walk_vector_cosine"),
        "median_steady_walk_rank_corr": _nanmedian_series(table, "steady_walk_rank_corr"),
        "median_spontaneous_prelead_fraction": _nanmedian_series(table, "spontaneous_prelead_fraction"),
        "median_spontaneous_minus_forced_prelead_delta": _nanmedian_series(
            table, "spontaneous_minus_forced_prelead_delta"
        ),
        "dropped_experiments": dropped,
        "per_experiment_rows": table.to_dict(orient="records"),
    }
