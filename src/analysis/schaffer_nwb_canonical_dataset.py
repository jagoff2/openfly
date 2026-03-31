from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import h5py
import numpy as np

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


def _median_sampling_rate_hz(timestamps_s: np.ndarray) -> float:
    if timestamps_s.size < 2:
        return 0.0
    diffs = np.diff(timestamps_s.astype(np.float64))
    diffs = diffs[np.isfinite(diffs) & (diffs > 1e-9)]
    if diffs.size == 0:
        return 0.0
    return float(1.0 / np.median(diffs))


def _trace_entries(
    *,
    matrix_path: Path,
    roi_ids: np.ndarray,
    sampling_rate_hz: float,
) -> tuple[CanonicalNeuronTrace, ...]:
    entries: list[CanonicalNeuronTrace] = []
    roi_ids = np.asarray(roi_ids).reshape(-1)
    for trace_index, roi_id in enumerate(roi_ids.tolist()):
        entries.append(
            CanonicalNeuronTrace(
                trace_id=f"trace_{trace_index:04d}",
                recorded_entity_id=f"roi_{int(roi_id)}",
                recorded_entity_type="roi",
                hemisphere=None,
                trace_index=int(trace_index),
                sampling_rate_hz=float(sampling_rate_hz),
                units="dff",
                transform="public_raw_interval",
                values_path=str(matrix_path),
                time_path=None,
                flywire_mapping_key=None,
                flywire_mapping_confidence="none",
                tags=("schaffer2023", "roi_dff", "nwb"),
            )
        )
    return tuple(entries)


def _load_roi_ids(handle: h5py.File, roi_count: int) -> np.ndarray:
    candidate_path = "/processing/ophys/ImageSegmentation/ImagingPlane/id"
    if candidate_path in handle:
        roi_ids = np.asarray(handle[candidate_path][...]).reshape(-1)
        if roi_ids.size == roi_count:
            return roi_ids.astype(np.int64, copy=False)
    return np.arange(roi_count, dtype=np.int64)


def export_schaffer_nwb_canonical_dataset(
    dataset_root: str | Path,
    *,
    output_dir: str | Path,
) -> dict[str, Any]:
    dataset_root = Path(dataset_root)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    nwb_paths = sorted(dataset_root.glob("*.nwb"))
    if not nwb_paths:
        raise FileNotFoundError(f"No staged NWB files found under {dataset_root}")

    trials: list[CanonicalTrial] = []
    exported_sessions: list[dict[str, Any]] = []
    skipped_sessions: list[dict[str, Any]] = []
    total_session_count = len(nwb_paths)

    for session_index, nwb_path in enumerate(nwb_paths):
        split = _assign_split(session_index, total_session_count)
        session_dir = output_dir / nwb_path.stem
        session_dir.mkdir(parents=True, exist_ok=True)
        try:
            with h5py.File(nwb_path, "r") as handle:
                roi_series = handle["/processing/ophys/DfOverF/RoiResponseSeries"]
                dff_matrix = np.asarray(roi_series["data"][...], dtype=np.float32)
                timestamps_s = np.asarray(roi_series["timestamps"][...], dtype=np.float32).reshape(-1)
                if dff_matrix.ndim != 2 or dff_matrix.shape[0] != timestamps_s.size:
                    raise ValueError("Unexpected Schaffer NWB DfOverF shape")
                ball_motion = np.asarray(handle["/processing/behavior/ball_motion/data"][...], dtype=np.float32).reshape(-1)
                state_matrix = np.asarray(
                    handle["/processing/behavioral state/behavioral state/data"][...],
                    dtype=np.float32,
                )
                state_timestamps_s = np.asarray(
                    handle["/processing/behavioral state/behavioral state/timestamps"][...],
                    dtype=np.float32,
                ).reshape(-1)
                if ball_motion.shape[0] != timestamps_s.size:
                    raise ValueError("Unexpected Schaffer NWB ball-motion shape")
                if state_matrix.ndim != 2 or state_matrix.shape[0] != state_timestamps_s.size:
                    raise ValueError("Unexpected Schaffer NWB behavioral-state shape")
                trial_starts = np.asarray(handle["/intervals/trials/start_time"][...], dtype=np.float32).reshape(-1)
                trial_stops = np.asarray(handle["/intervals/trials/stop_time"][...], dtype=np.float32).reshape(-1)
                trial_ids = np.asarray(handle["/intervals/trials/id"][...], dtype=np.int64).reshape(-1)
                if not (trial_starts.size == trial_stops.size == trial_ids.size):
                    raise ValueError("Unexpected Schaffer NWB interval trial shape")
                roi_ids = _load_roi_ids(handle, int(dff_matrix.shape[1]))
                sampling_rate_hz = _median_sampling_rate_hz(timestamps_s)

                exported_interval_count = 0
                for interval_index, (trial_id, start_s, stop_s) in enumerate(
                    zip(trial_ids.tolist(), trial_starts.tolist(), trial_stops.tolist())
                ):
                    mask = (timestamps_s >= float(start_s)) & (timestamps_s <= float(stop_s))
                    if not np.any(mask):
                        continue
                    state_mask = (state_timestamps_s >= float(start_s)) & (state_timestamps_s <= float(stop_s))
                    interval_time_s = timestamps_s[mask].astype(np.float32, copy=False)
                    interval_time_rel_s = (interval_time_s - float(interval_time_s[0])).astype(np.float32, copy=False)
                    interval_matrix = np.asarray(dff_matrix[mask].T, dtype=np.float32)
                    interval_ball_motion = np.asarray(ball_motion[mask], dtype=np.float32)
                    interval_state = np.asarray(state_matrix[state_mask].T, dtype=np.float32)
                    interval_state_time_s = np.asarray(state_timestamps_s[state_mask], dtype=np.float32)
                    if interval_state_time_s.size:
                        interval_state_time_s = (
                            interval_state_time_s - float(interval_state_time_s[0])
                        ).astype(np.float32, copy=False)

                    prefix = f"trial_{int(trial_id):03d}"
                    matrix_path = session_dir / f"{prefix}_matrix.npy"
                    time_path = session_dir / f"{prefix}_time_s.npy"
                    ball_path = session_dir / f"{prefix}_ball_motion.npy"
                    ball_time_path = session_dir / f"{prefix}_ball_motion_time_s.npy"
                    state_path = session_dir / f"{prefix}_behavioral_state.npy"
                    state_time_path = session_dir / f"{prefix}_behavioral_state_time_s.npy"
                    np.save(matrix_path, interval_matrix)
                    np.save(time_path, interval_time_rel_s)
                    np.save(ball_path, interval_ball_motion)
                    np.save(ball_time_path, interval_time_rel_s)
                    np.save(state_path, interval_state)
                    np.save(state_time_path, interval_state_time_s)

                    trials.append(
                        CanonicalTrial(
                            trial_id=f"{nwb_path.stem}_trial_{int(trial_id):03d}",
                            split=split,
                            behavior_context="behaving_imaging",
                            stimulus=CanonicalStimulus(
                                stimulus_family="session_interval",
                                stimulus_name="schaffer2023_behavior_interval",
                                units="seconds",
                                parameters={
                                    "session_file": nwb_path.name,
                                    "trial_id": int(trial_id),
                                    "start_time_s": float(start_s),
                                    "stop_time_s": float(stop_s),
                                },
                            ),
                            timebase_path=str(time_path),
                            traces=_trace_entries(
                                matrix_path=matrix_path,
                                roi_ids=roi_ids,
                                sampling_rate_hz=sampling_rate_hz,
                            ),
                            behavior_paths={
                                "ball_motion_path": str(ball_path),
                                "ball_motion_time_path": str(ball_time_path),
                                "behavioral_state_path": str(state_path),
                                "behavioral_state_time_path": str(state_time_path),
                            },
                            metadata={
                                "session_file": nwb_path.name,
                                "trial_id": int(trial_id),
                                "roi_count": int(interval_matrix.shape[0]),
                                "time_count": int(interval_matrix.shape[1]),
                                "behavioral_state_dim": int(interval_state.shape[0]) if interval_state.ndim == 2 else 0,
                                "sampling_rate_hz": float(sampling_rate_hz),
                            },
                        )
                    )
                    exported_interval_count += 1

                exported_sessions.append(
                    {
                        "session_file": nwb_path.name,
                        "split": split,
                        "roi_count": int(dff_matrix.shape[1]),
                        "time_count": int(dff_matrix.shape[0]),
                        "interval_count": int(exported_interval_count),
                        "behavioral_state_dim": int(state_matrix.shape[1]) if state_matrix.ndim == 2 else 0,
                        "sampling_rate_hz": float(sampling_rate_hz),
                    }
                )
        except Exception as exc:  # noqa: BLE001
            skipped_sessions.append(
                {
                    "session_file": nwb_path.name,
                    "reason": f"{type(exc).__name__}:{exc}",
                }
            )

    bundle = CanonicalDatasetBundle(
        dataset_key="schaffer2023_figshare_nwb",
        citation_label="Schaffer et al. 2023 Figshare",
        modality="roi_dff_timeseries",
        normalization={
            "trace_transform": "public_raw_interval",
            "timebase_policy": "relative_interval_seconds",
            "behavior_policy": "aligned_ball_motion_and_behavioral_state",
        },
        identity_strategy={
            "primary": "roi",
            "fallback": "roi",
            "notes": "Current Schaffer export preserves NWB ROI identities per staged session file, not FlyWire-aligned neurons.",
        },
        trials=tuple(trials),
    )
    bundle_path = output_dir / "schaffer2023_nwb_canonical_bundle.json"
    bundle_path.write_text(json.dumps(bundle.to_dict(), indent=2), encoding="utf-8")

    summary = {
        "dataset_key": "schaffer2023_figshare_nwb",
        "dataset_root": str(dataset_root),
        "bundle_path": str(bundle_path),
        "staged_session_count": len(nwb_paths),
        "exported_session_count": len(exported_sessions),
        "trial_count": len(trials),
        "exported_sessions": exported_sessions,
        "skipped_sessions": skipped_sessions,
    }
    summary_path = output_dir / "schaffer2023_nwb_canonical_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
