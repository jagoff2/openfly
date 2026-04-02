from __future__ import annotations

import json
import math
import zipfile
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from analysis.aimon_public_comparator import (
    _filter_candidate_rows,
    _load_archive_array,
    _load_best_region_matrix,
    _match_member_by_source,
    _select_region_member,
    _slice_overlap_fraction,
    _window_slice,
    index_aimon_archive_members,
)
from analysis.public_neural_measurement_schema import (
    CanonicalDatasetBundle,
    CanonicalNeuronTrace,
    CanonicalStimulus,
    CanonicalTrial,
)


def _assign_split(index: int, total: int) -> str:
    if total <= 1:
        return "train"
    if total == 2:
        return "train" if index == 0 else "test"
    mod = index % 3
    if mod == 0:
        return "train"
    if mod == 1:
        return "val"
    return "test"


def _trace_entries(
    *,
    matrix_path: Path,
    trace_count: int,
    sampling_rate_hz: float,
) -> tuple[CanonicalNeuronTrace, ...]:
    return tuple(
        CanonicalNeuronTrace(
            trace_id=f"trace_{trace_index:03d}",
            recorded_entity_id=f"region_component_{trace_index:03d}",
            recorded_entity_type="region_component",
            hemisphere=None,
            trace_index=trace_index,
            sampling_rate_hz=float(sampling_rate_hz),
            units="dff_like",
            transform="public_raw_window",
            values_path=str(matrix_path),
            time_path=None,
            flywire_mapping_key=None,
            flywire_mapping_confidence="none",
            tags=("aimon2023", "region_component"),
        )
        for trace_index in range(trace_count)
    )


def _row_window_overlap_fraction(row: pd.Series) -> float | None:
    if pd.isna(row["TSlowlimWalk"]) or pd.isna(row["TShighlimWalk"]):
        return None
    if pd.isna(row["TSlowlimForced"]) or pd.isna(row["TShighlimForced"]):
        return None
    walk_start = max(0, int(round(float(row["TSlowlimWalk"]))) - 1)
    walk_stop = int(round(float(row["TShighlimWalk"])))
    forced_start = max(0, int(round(float(row["TSlowlimForced"]))) - 1)
    forced_stop = int(round(float(row["TShighlimForced"])))
    walk_len = max(0, walk_stop - walk_start)
    forced_len = max(0, forced_stop - forced_start)
    if walk_len <= 0 or forced_len <= 0:
        return None
    overlap = max(0, min(walk_stop, forced_stop) - max(walk_start, forced_start))
    denom = float(min(walk_len, forced_len))
    if denom <= 0.0:
        return None
    return float(overlap) / denom


def _resample_array_to_length(values: np.ndarray, target_length: int) -> np.ndarray:
    values = np.asarray(values, dtype=np.float32).reshape(-1)
    target_length = max(0, int(target_length))
    if target_length == 0:
        return np.zeros((0,), dtype=np.float32)
    if values.size == 0:
        return np.zeros((target_length,), dtype=np.float32)
    if values.size == target_length:
        return values.astype(np.float32, copy=False)
    if values.size == 1:
        return np.full((target_length,), float(values[0]), dtype=np.float32)
    source_time = np.linspace(0.0, 1.0, values.size, dtype=np.float32)
    target_time = np.linspace(0.0, 1.0, target_length, dtype=np.float32)
    return np.interp(target_time, source_time, values).astype(np.float32)


def export_aimon_canonical_dataset(
    dataset_root: str | Path,
    *,
    output_dir: str | Path,
    sampling_rate_hz: float = 100.0,
    max_experiments: int | None = None,
) -> dict[str, Any]:
    dataset_root = Path(dataset_root)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    goodics_path = dataset_root / "GoodICsdf.pkl"
    additional_path = dataset_root / "Additional_data.zip"
    regions_path = dataset_root / "Walk_anatomical_regions.zip"
    if not goodics_path.exists() or not additional_path.exists():
        raise FileNotFoundError("Aimon canonical export requires GoodICsdf.pkl and Additional_data.zip")

    goodics = pd.read_pickle(goodics_path)
    raw_candidates = _filter_candidate_rows(goodics).copy()
    overlap_drops: list[dict[str, Any]] = []
    kept_rows: list[dict[str, Any]] = []
    for _, row in raw_candidates.iterrows():
        overlap_fraction = _row_window_overlap_fraction(row)
        if overlap_fraction is None:
            overlap_drops.append({"exp_id": str(row["expID"]), "reason": "invalid_window_bounds"})
            continue
        if math.isfinite(overlap_fraction) and overlap_fraction > 0.0:
            overlap_drops.append({"exp_id": str(row["expID"]), "reason": "overlapping_walk_forced_windows"})
            continue
        kept_rows.append(dict(row))
    candidates = pd.DataFrame(kept_rows)
    if max_experiments is not None:
        candidates = candidates.head(int(max_experiments)).copy()

    use_regions_archive = regions_path.exists()
    region_index = index_aimon_archive_members(regions_path) if use_regions_archive else pd.DataFrame()
    additional_index = index_aimon_archive_members(additional_path)
    region_member_names = set(region_index["member_name"].astype(str).tolist()) if "member_name" in region_index.columns else set()

    trials: list[CanonicalTrial] = []
    exported_rows: list[dict[str, Any]] = []
    dropped: list[dict[str, Any]] = list(overlap_drops)

    with zipfile.ZipFile(additional_path) as additional_archive:
        regions_archive_ctx = zipfile.ZipFile(regions_path) if use_regions_archive else None
        try:
            regions_archive = regions_archive_ctx
            for row_index, (_, row) in enumerate(candidates.iterrows()):
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
                exp_dir = output_dir / exp_id
                exp_dir.mkdir(parents=True, exist_ok=True)
                full_time = np.arange(region_matrix.shape[1], dtype=np.float32) / float(sampling_rate_hz)
                full_time_path = exp_dir / "full_time_s.npy"
                np.save(full_time_path, full_time)

                split = _assign_split(len(exported_rows), len(candidates))
                trial_specs = [
                    (
                        "spontaneous_walk",
                        walk_slice,
                        walk_regressor_member,
                        CanonicalStimulus(
                            stimulus_family="behavior_regressor",
                            stimulus_name="spontaneous_walk",
                            units="frames",
                            parameters={"window_start": int(walk_slice.start), "window_stop": int(walk_slice.stop)},
                        ),
                    ),
                    (
                        "forced_walk",
                        forced_slice,
                        forced_walk_member,
                        CanonicalStimulus(
                            stimulus_family="behavior_regressor",
                            stimulus_name="forced_walk",
                            units="frames",
                            parameters={"window_start": int(forced_slice.start), "window_stop": int(forced_slice.stop)},
                        ),
                    ),
                ]
                for label, current_slice, regressor_member, stimulus in trial_specs:
                    matrix = np.asarray(region_matrix[:, current_slice], dtype=np.float32)
                    matrix_path = exp_dir / f"{label}_matrix.npy"
                    time_path = exp_dir / f"{label}_time_s.npy"
                    np.save(matrix_path, matrix)
                    np.save(time_path, full_time[current_slice])
                    behavior_paths: dict[str, str] = {}
                    if regressor_member:
                        try:
                            archive = regions_archive if regressor_member in region_member_names else additional_archive
                            regressor = np.asarray(_load_archive_array(archive, regressor_member), dtype=np.float32).squeeze()
                            if regressor.ndim != 1:
                                regressor = regressor.reshape(-1)
                            if regressor.size == region_matrix.shape[1]:
                                aligned = regressor[current_slice]
                            elif current_slice.stop <= regressor.size:
                                aligned = regressor[current_slice]
                            else:
                                aligned = _resample_array_to_length(regressor, matrix.shape[1])
                            regressor_path = exp_dir / f"{label}_regressor.npy"
                            np.save(regressor_path, np.asarray(aligned, dtype=np.float32))
                            behavior_paths["walk_regressor_path"] = str(regressor_path)
                        except Exception:  # noqa: BLE001
                            pass
                    trial = CanonicalTrial(
                        trial_id=f"{exp_id}_{label}",
                        split=split,
                        behavior_context=label,
                        stimulus=stimulus,
                        timebase_path=str(time_path),
                        traces=_trace_entries(
                            matrix_path=matrix_path,
                            trace_count=int(matrix.shape[0]),
                            sampling_rate_hz=sampling_rate_hz,
                        ),
                        behavior_paths=behavior_paths,
                        metadata={
                            "exp_id": exp_id,
                            "region_member": region_member_used,
                            "region_source": region_source,
                            "trace_count": int(matrix.shape[0]),
                            "time_count": int(matrix.shape[1]),
                            "regressor_alignment": "trial_timebase" if behavior_paths else "missing",
                        },
                    )
                    trials.append(trial)
                exported_rows.append(
                    {
                        "exp_id": exp_id,
                        "split": split,
                        "region_member": region_member_used,
                        "region_source": region_source,
                        "trace_count": int(region_matrix.shape[0]),
                        "time_count": int(region_matrix.shape[1]),
                    }
                )
        finally:
            if regions_archive_ctx is not None:
                regions_archive_ctx.close()

    bundle = CanonicalDatasetBundle(
        dataset_key="aimon2023_dryad",
        citation_label="Aimon et al. 2023 eLife / Dryad",
        modality="region_component_timeseries",
        normalization={
            "trace_transform": "public_raw_window",
            "sampling_rate_hz": float(sampling_rate_hz),
            "window_policy": "goodics_walk_and_forced_windows",
        },
        identity_strategy={
            "primary": "region_component",
            "fallback": "region_component",
            "notes": "Aimon bundle currently exports public region/component-level traces, not exact neurons.",
        },
        trials=tuple(trials),
    )
    bundle_path = output_dir / "aimon2023_canonical_bundle.json"
    bundle_path.write_text(json.dumps(bundle.to_dict(), indent=2), encoding="utf-8")

    summary = {
        "dataset_key": "aimon2023_dryad",
        "dataset_root": str(dataset_root),
        "bundle_path": str(bundle_path),
        "exported_experiment_count": len(exported_rows),
        "trial_count": len(trials),
        "exported_rows": exported_rows,
        "dropped_experiments": dropped,
    }
    summary_path = output_dir / "aimon2023_canonical_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
