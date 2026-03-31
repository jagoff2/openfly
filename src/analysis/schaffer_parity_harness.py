from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from analysis.public_neural_measurement_harness import aggregate_trace_scores, score_trace_pair


@dataclass(frozen=True)
class SchafferCanonicalTrialData:
    trial_id: str
    split: str
    behavior_context: str
    matrix: np.ndarray
    timebase_s: np.ndarray
    stimulus: dict[str, Any]
    ball_motion: np.ndarray | None
    ball_motion_time_s: np.ndarray | None
    behavioral_state: np.ndarray | None
    behavioral_state_time_s: np.ndarray | None
    metadata: dict[str, Any]


def _resolve_bundle_path(bundle_root: Path, path_value: str | None) -> Path | None:
    if not path_value:
        return None
    path = Path(path_value)
    if path.is_absolute():
        return path
    return (bundle_root / path).resolve()


def _load_optional_array(path: Path | None, *, flatten: bool = False) -> np.ndarray | None:
    if path is None:
        return None
    array = np.asarray(np.load(path), dtype=np.float32)
    if flatten:
        return array.reshape(-1)
    return array


def load_schaffer_canonical_trial_data(bundle_path: str | Path) -> list[SchafferCanonicalTrialData]:
    bundle_path = Path(bundle_path)
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    bundle_root = bundle_path.parent
    rows: list[SchafferCanonicalTrialData] = []
    for trial in bundle["trials"]:
        trace_paths = {trace["values_path"] for trace in trial["traces"]}
        if len(trace_paths) != 1:
            raise ValueError(f"trial {trial['trial_id']} has inconsistent values_path entries")
        matrix_path = _resolve_bundle_path(bundle_root, str(next(iter(trace_paths))))
        time_path = _resolve_bundle_path(bundle_root, str(trial["timebase_path"]))
        if matrix_path is None or time_path is None:
            raise ValueError(f"trial {trial['trial_id']} is missing required matrix or timebase path")
        behavior_paths = dict(trial.get("behavior_paths", {}))
        rows.append(
            SchafferCanonicalTrialData(
                trial_id=str(trial["trial_id"]),
                split=str(trial.get("split", "train")),
                behavior_context=str(trial["behavior_context"]),
                matrix=np.asarray(np.load(matrix_path), dtype=np.float32),
                timebase_s=np.asarray(np.load(time_path), dtype=np.float32).reshape(-1),
                stimulus=dict(trial.get("stimulus", {})),
                ball_motion=_load_optional_array(
                    _resolve_bundle_path(bundle_root, behavior_paths.get("ball_motion_path")),
                    flatten=True,
                ),
                ball_motion_time_s=_load_optional_array(
                    _resolve_bundle_path(bundle_root, behavior_paths.get("ball_motion_time_path")),
                    flatten=True,
                ),
                behavioral_state=_load_optional_array(
                    _resolve_bundle_path(bundle_root, behavior_paths.get("behavioral_state_path"))
                ),
                behavioral_state_time_s=_load_optional_array(
                    _resolve_bundle_path(bundle_root, behavior_paths.get("behavioral_state_time_path")),
                    flatten=True,
                ),
                metadata=dict(trial.get("metadata", {})),
            )
        )
    return rows


def score_schaffer_trial_matrix(
    observed_trial: SchafferCanonicalTrialData,
    simulated_matrix: np.ndarray,
    *,
    simulated_timebase_s: np.ndarray | None = None,
) -> dict[str, Any]:
    simulated_matrix = np.asarray(simulated_matrix, dtype=np.float32)
    if simulated_matrix.shape[0] != observed_trial.matrix.shape[0]:
        raise ValueError("observed and simulated matrices must have the same trace count")
    scores = []
    for trace_index in range(observed_trial.matrix.shape[0]):
        scores.append(
            score_trace_pair(
                trace_id=f"{observed_trial.trial_id}_trace_{trace_index:03d}",
                observed_values=observed_trial.matrix[trace_index],
                simulated_values=simulated_matrix[trace_index],
                observed_timebase=observed_trial.timebase_s,
                simulated_timebase=simulated_timebase_s,
            )
        )
    return {
        "trial_id": observed_trial.trial_id,
        "split": observed_trial.split,
        "behavior_context": observed_trial.behavior_context,
        "trace_count": int(observed_trial.matrix.shape[0]),
        "time_count": int(observed_trial.matrix.shape[1]),
        "aggregate": aggregate_trace_scores(scores),
        "trace_scores": [score.to_dict() for score in scores],
    }
