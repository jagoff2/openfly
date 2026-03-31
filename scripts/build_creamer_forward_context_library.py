from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


def _load_population_groups(path: Path) -> dict[str, dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    groups: dict[str, dict[str, object]] = {}
    for item in payload.get("selected_paired_cell_types", []):
        label = str(item.get("cell_type") or item.get("candidate_label") or "").strip()
        if not label:
            continue
        groups[label] = {
            "left_root_ids": [int(root_id) for root_id in item.get("left_root_ids", [])],
            "right_root_ids": [int(root_id) for root_id in item.get("right_root_ids", [])],
        }
    return groups


def _baseline_bilateral_rates(path: Path, cell_types: set[str]) -> dict[str, float]:
    stationary_blocks = {"baseline_a", "baseline_b", "baseline_c", "baseline_d"}
    values: dict[str, list[float]] = defaultdict(list)
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            block_label = str((((row.get("body_metadata") or {}).get("visual_speed_state") or {}).get("block_label")) or "")
            if block_label not in stationary_blocks:
                continue
            motor_readout = row.get("motor_readout") or {}
            for cell_type in cell_types:
                key = f"monitor_{cell_type}_bilateral_hz"
                value = motor_readout.get(key)
                if value is not None:
                    values[cell_type].append(float(value))
    return {
        cell_type: float(sum(samples) / len(samples))
        for cell_type, samples in values.items()
        if samples
    }


def _parse_weight_scale_overrides(raw: str) -> dict[str, float]:
    overrides: dict[str, float] = {}
    for item in str(raw or "").split(","):
        item = item.strip()
        if not item:
            continue
        if "=" not in item:
            raise ValueError(f"invalid weight scale override '{item}', expected CELLTYPE=SCALE")
        label, raw_scale = item.split("=", 1)
        label = label.strip()
        if not label:
            raise ValueError(f"invalid weight scale override '{item}', missing cell type")
        overrides[label] = float(raw_scale)
    return overrides


def _parse_absolute_weight_overrides(raw: str) -> dict[str, float]:
    overrides: dict[str, float] = {}
    for item in str(raw or "").split(","):
        item = item.strip()
        if not item:
            continue
        if "=" not in item:
            raise ValueError(f"invalid absolute weight override '{item}', expected CELLTYPE=WEIGHT")
        label, raw_weight = item.split("=", 1)
        label = label.strip()
        if not label:
            raise ValueError(f"invalid absolute weight override '{item}', missing cell type")
        overrides[label] = float(raw_weight)
    return overrides


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a baseline-centered Creamer forward-context library from ranked candidates.")
    parser.add_argument("--candidate-csv", required=True)
    parser.add_argument("--baseline-run", required=True)
    parser.add_argument("--monitor-candidates-json", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--cell-types", default="")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--min-score", type=float, default=0.0)
    parser.add_argument(
        "--library-mode",
        choices=["signed_centered", "motion_energy", "positive_centered", "negative_centered"],
        default="signed_centered",
    )
    parser.add_argument("--threshold-scale", type=float, default=0.0)
    parser.add_argument("--weight-scale-overrides", default="")
    parser.add_argument("--absolute-weight-overrides", default="")
    args = parser.parse_args()

    requested = {value.strip() for value in str(args.cell_types).split(",") if value.strip()}
    weight_scale_overrides = _parse_weight_scale_overrides(str(args.weight_scale_overrides))
    absolute_weight_overrides = _parse_absolute_weight_overrides(str(args.absolute_weight_overrides))
    rows: list[dict[str, str]] = []
    with Path(args.candidate_csv).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(row)
    rows.sort(key=lambda row: float(row.get("candidate_score", 0.0)), reverse=True)
    if requested:
        selected_rows = [row for row in rows if str(row.get("cell_type", "")) in requested]
    else:
        selected_rows = [row for row in rows if float(row.get("candidate_score", 0.0)) >= float(args.min_score)][: max(1, int(args.top_k))]

    groups = _load_population_groups(Path(args.monitor_candidates_json))
    selected_types = {str(row["cell_type"]) for row in selected_rows}
    baselines = _baseline_bilateral_rates(Path(args.baseline_run), selected_types)

    selected_groups: list[dict[str, object]] = []
    for row in selected_rows:
        cell_type = str(row["cell_type"])
        group = groups.get(cell_type)
        if not group:
            continue
        if args.library_mode == "motion_energy":
            forward_weight = max(0.0, float(row.get("motion_specificity_hz", 0.0)))
        elif args.library_mode == "positive_centered":
            forward_weight = max(0.0, float(row.get("signed_ablation_component_hz", 0.0)))
        elif args.library_mode == "negative_centered":
            forward_weight = max(0.0, -float(row.get("signed_ablation_component_hz", 0.0)))
        else:
            forward_weight = float(
                row.get(
                    "signed_ablation_component_hz",
                    row.get("signed_motion_mean_delta_hz", row.get("ablation_component_hz", 0.0)),
                )
            )
        scale_override = float(weight_scale_overrides.get(cell_type, 1.0))
        if cell_type in absolute_weight_overrides:
            forward_weight = float(absolute_weight_overrides[cell_type])
        else:
            forward_weight = float(forward_weight) * scale_override
        motion_threshold_hz = max(0.0, float(args.threshold_scale) * abs(float(row.get("baseline_flicker_delta_hz", 0.0))))
        payload = {
            "label": cell_type,
            "left_root_ids": list(group["left_root_ids"]),
            "right_root_ids": list(group["right_root_ids"]),
            "forward_weight": float(forward_weight),
            "baseline_bilateral_hz": float(baselines.get(cell_type, 0.0)),
            "signal_mode": str(args.library_mode),
            "motion_threshold_hz": float(motion_threshold_hz),
            "baseline_ftb_mean_delta_hz": float(row.get("baseline_ftb_mean_delta_hz", 0.0)),
            "baseline_btf_mean_delta_hz": float(row.get("baseline_btf_mean_delta_hz", 0.0)),
            "baseline_flicker_delta_hz": float(row.get("baseline_flicker_delta_hz", 0.0)),
            "signed_motion_mean_delta_hz": float(row.get("signed_motion_mean_delta_hz", 0.0)),
            "signed_ablation_component_hz": float(row.get("signed_ablation_component_hz", 0.0)),
            "motion_specificity_hz": float(row.get("motion_specificity_hz", 0.0)),
            "candidate_score": float(row.get("candidate_score", 0.0)),
        }
        if cell_type in absolute_weight_overrides:
            payload["absolute_weight_override"] = float(absolute_weight_overrides[cell_type])
        elif scale_override != 1.0:
            payload["weight_scale_override"] = float(scale_override)
        selected_groups.append(payload)

    output = {
        "selected_groups": selected_groups,
        "forward_context_scale_hz": 5.0,
        "library_mode": str(args.library_mode),
        "threshold_scale": float(args.threshold_scale),
        "weight_scale_overrides": weight_scale_overrides,
        "absolute_weight_overrides": absolute_weight_overrides,
        "source_candidate_csv": str(args.candidate_csv),
        "source_baseline_run": str(args.baseline_run),
        "source_monitor_candidates_json": str(args.monitor_candidates_json),
    }
    output_path = Path(args.output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
