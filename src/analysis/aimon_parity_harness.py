from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from analysis.public_neural_measurement_harness import aggregate_trace_scores, score_trace_pair


@dataclass(frozen=True)
class AimonCanonicalTrialData:
    trial_id: str
    split: str
    behavior_context: str
    matrix: np.ndarray
    timebase_s: np.ndarray
    stimulus: dict[str, Any]
    behavior_paths: dict[str, str]
    metadata: dict[str, Any]


def load_aimon_canonical_trial_data(bundle_path: str | Path) -> list[AimonCanonicalTrialData]:
    bundle_path = Path(bundle_path)
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    bundle_root = bundle_path.parent
    rows: list[AimonCanonicalTrialData] = []
    for trial in bundle["trials"]:
        trace_paths = {trace["values_path"] for trace in trial["traces"]}
        if len(trace_paths) != 1:
            raise ValueError(f"trial {trial['trial_id']} has inconsistent values_path entries")
        matrix_path = Path(next(iter(trace_paths)))
        if not matrix_path.is_absolute():
            matrix_path = (bundle_root / matrix_path).resolve()
        time_path = Path(trial["timebase_path"])
        if not time_path.is_absolute():
            time_path = (bundle_root / time_path).resolve()
        rows.append(
            AimonCanonicalTrialData(
                trial_id=str(trial["trial_id"]),
                split=str(trial.get("split", "train")),
                behavior_context=str(trial["behavior_context"]),
                matrix=np.asarray(np.load(matrix_path), dtype=np.float32),
                timebase_s=np.asarray(np.load(time_path), dtype=np.float32).reshape(-1),
                stimulus=dict(trial.get("stimulus", {})),
                behavior_paths={str(key): str(value) for key, value in dict(trial.get("behavior_paths", {})).items()},
                metadata=dict(trial.get("metadata", {})),
            )
        )
    return rows


def score_aimon_trial_matrix(
    observed_trial: AimonCanonicalTrialData,
    simulated_matrix: np.ndarray,
    *,
    simulated_timebase_s: np.ndarray | None = None,
    max_lag_steps: int = 0,
    max_lag_seconds: float | None = 0.5,
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
                max_lag_steps=max_lag_steps,
                max_lag_seconds=max_lag_seconds,
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
