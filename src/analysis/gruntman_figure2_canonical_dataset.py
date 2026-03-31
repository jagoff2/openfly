from __future__ import annotations

import json
import tempfile
import zipfile
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

GRUNTMAN_FIGURE2_TRACE_LEN = 45_000
GRUNTMAN_FIGURE2_SAMPLING_RATE_HZ = 20_000.0
GRUNTMAN_FIGURE2_NEW_ZERO = int(np.floor(GRUNTMAN_FIGURE2_TRACE_LEN / 2.5))
GRUNTMAN_FIGURE2_DURATION_MS = {0: 40.0, 1: 160.0}


def _full_time_s() -> np.ndarray:
    samples = np.arange(1, GRUNTMAN_FIGURE2_TRACE_LEN + 1, dtype=np.float32)
    return ((samples - float(GRUNTMAN_FIGURE2_NEW_ZERO)) / GRUNTMAN_FIGURE2_SAMPLING_RATE_HZ).astype(np.float32)


def _extract_trace(handle: h5py.File, ref: h5py.Reference) -> np.ndarray | None:
    dataset = handle[ref]
    values = np.asarray(dataset, dtype=np.float32).reshape(-1)
    if values.size != GRUNTMAN_FIGURE2_TRACE_LEN:
        return None
    if np.isnan(values).all():
        return None
    return values


def export_gruntman_figure2_canonical_dataset(
    dataset_root: str | Path,
    *,
    output_dir: str | Path,
) -> dict[str, Any]:
    dataset_root = Path(dataset_root)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    zip_path = dataset_root / "figure2DataAndCode.zip"
    if not zip_path.exists():
        raise FileNotFoundError("Gruntman Figure 2 canonical export requires figure2DataAndCode.zip")

    full_time_s = _full_time_s()
    full_time_path = output_dir / "gruntman2019_figure2_time_s.npy"
    np.save(full_time_path, full_time_s)

    trials: list[CanonicalTrial] = []
    exported_rows: list[dict[str, Any]] = []
    skipped_conditions: list[dict[str, Any]] = []

    with zipfile.ZipFile(zip_path) as archive:
        with tempfile.TemporaryDirectory() as tmp_dir:
            mat_path = Path(tmp_dir) / "sourceDataPlottingFig2.mat"
            mat_path.write_bytes(archive.read("sourceDataPlottingFig2.mat"))
            with h5py.File(mat_path, "r") as handle:
                outer = handle["alignedSingleBarPerCell"]
                cell_count, duration_count, position_count, width_count = outer.shape
                for duration_index in range(duration_count):
                    for position_index in range(position_count):
                        for width_index in range(width_count):
                            traces: list[np.ndarray] = []
                            trace_defs: list[CanonicalNeuronTrace] = []
                            for cell_index in range(cell_count):
                                trace = _extract_trace(handle, outer[cell_index, duration_index, position_index, width_index])
                                if trace is None:
                                    continue
                                trace_index = len(traces)
                                traces.append(trace)
                                trace_defs.append(
                                    CanonicalNeuronTrace(
                                        trace_id=f"cell_{cell_index:02d}",
                                        recorded_entity_id=f"cell_{cell_index:02d}",
                                        recorded_entity_type="recorded_neuron",
                                        hemisphere=None,
                                        trace_index=trace_index,
                                        sampling_rate_hz=GRUNTMAN_FIGURE2_SAMPLING_RATE_HZ,
                                        units="mV",
                                        transform="public_raw_trace",
                                        values_path="",
                                        time_path=str(full_time_path),
                                        flywire_mapping_key=None,
                                        flywire_mapping_confidence="none",
                                        tags=("gruntman2019", "figure2", "single_bar_vm"),
                                    )
                                )
                            if not traces:
                                skipped_conditions.append(
                                    {
                                        "duration_index": duration_index,
                                        "position_index": position_index,
                                        "width_index": width_index,
                                        "reason": "no_valid_traces",
                                    }
                                )
                                continue

                            trial_id = (
                                f"gruntman2019_fig2_d{duration_index:02d}_"
                                f"p{position_index:02d}_w{width_index:02d}"
                            )
                            matrix_path = output_dir / f"{trial_id}_matrix.npy"
                            matrix = np.stack(traces, axis=0).astype(np.float32)
                            np.save(matrix_path, matrix)
                            trace_defs = tuple(
                                CanonicalNeuronTrace(
                                    trace_id=trace_def.trace_id,
                                    recorded_entity_id=trace_def.recorded_entity_id,
                                    recorded_entity_type=trace_def.recorded_entity_type,
                                    hemisphere=trace_def.hemisphere,
                                    trace_index=trace_def.trace_index,
                                    sampling_rate_hz=trace_def.sampling_rate_hz,
                                    units=trace_def.units,
                                    transform=trace_def.transform,
                                    values_path=str(matrix_path),
                                    time_path=trace_def.time_path,
                                    flywire_mapping_key=trace_def.flywire_mapping_key,
                                    flywire_mapping_confidence=trace_def.flywire_mapping_confidence,
                                    tags=trace_def.tags,
                                )
                                for trace_def in trace_defs
                            )
                            stimulus = CanonicalStimulus(
                                stimulus_family="single_bar_motion",
                                stimulus_name="gruntman2019_figure2_single_bar",
                                units="seconds",
                                parameters={
                                    "duration_index_h5": duration_index,
                                    "duration_ms_from_script": GRUNTMAN_FIGURE2_DURATION_MS.get(duration_index),
                                    "position_index_h5": position_index,
                                    "width_index_h5": width_index,
                                    "stimulus_onset_s": 0.0,
                                },
                            )
                            trial = CanonicalTrial(
                                trial_id=trial_id,
                                split="train",
                                behavior_context="single_bar_vm",
                                stimulus=stimulus,
                                timebase_path=str(full_time_path),
                                traces=trace_defs,
                                behavior_paths={},
                                metadata={
                                    "source_dataset": "gruntman2019_janelia",
                                    "figure": "figure2",
                                    "cell_count_h5": cell_count,
                                    "valid_trace_count": int(matrix.shape[0]),
                                    "trace_len": int(matrix.shape[1]),
                                    "h5_axis_order": ["cell", "duration", "position", "width"],
                                },
                            )
                            trials.append(trial)
                            exported_rows.append(
                                {
                                    "trial_id": trial_id,
                                    "duration_index_h5": duration_index,
                                    "duration_ms_from_script": GRUNTMAN_FIGURE2_DURATION_MS.get(duration_index),
                                    "position_index_h5": position_index,
                                    "width_index_h5": width_index,
                                    "valid_trace_count": int(matrix.shape[0]),
                                }
                            )

    bundle = CanonicalDatasetBundle(
        dataset_key="gruntman2019_janelia_figure2",
        citation_label="Gruntman et al. 2019 Janelia Figure 2",
        modality="single_neuron_membrane_potential",
        normalization={
            "trace_transform": "public_raw_trace",
            "sampling_rate_hz": GRUNTMAN_FIGURE2_SAMPLING_RATE_HZ,
            "time_alignment": "script_newZero_centered",
        },
        identity_strategy={
            "primary": "recorded_neuron_local_index",
            "fallback": "recorded_neuron_local_index",
            "notes": "Figure 2 exports recorded-cell traces by local index only. No FlyWire identity map is provided.",
        },
        trials=tuple(trials),
    )
    bundle_path = output_dir / "gruntman2019_figure2_canonical_bundle.json"
    bundle_path.write_text(json.dumps(bundle.to_dict(), indent=2), encoding="utf-8")

    summary = {
        "dataset_key": "gruntman2019_janelia_figure2",
        "dataset_root": str(dataset_root),
        "bundle_path": str(bundle_path),
        "trial_count": len(trials),
        "exported_rows": exported_rows,
        "skipped_condition_count": len(skipped_conditions),
        "skipped_conditions_preview": skipped_conditions[:50],
    }
    summary_path = output_dir / "gruntman2019_figure2_canonical_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
