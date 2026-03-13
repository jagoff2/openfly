from __future__ import annotations

import argparse
import json
from pathlib import Path


def _normalize(weights: dict[str, float]) -> dict[str, float]:
    if not weights:
        return {}
    max_weight = max(abs(value) for value in weights.values()) or 1.0
    return {label: float(value) / max_weight for label, value in weights.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description="Fit a first neck-output motor basis from the observational and causal atlas artifacts.")
    parser.add_argument("--observational-json", default="outputs/metrics/descending_monitor_neck_output_atlas.json")
    parser.add_argument("--causal-json", default="outputs/metrics/descending_motor_atlas_summary.json")
    parser.add_argument("--output-json", default="outputs/metrics/neck_output_motor_basis.json")
    args = parser.parse_args()

    observational = json.loads(Path(args.observational_json).read_text(encoding="utf-8"))
    causal = json.loads(Path(args.causal_json).read_text(encoding="utf-8"))

    forward_weights: dict[str, float] = {}
    for row in causal.get("forward_ranked", []):
        delta_drive = float(row["delta_mean_total_drive_vs_baseline"])
        delta_disp = float(row["delta_net_displacement_vs_baseline"])
        if delta_drive <= 0.0 and delta_disp <= 0.0:
            continue
        forward_weights[str(row["label"])] = max(0.0, delta_drive) + max(0.0, delta_disp)

    turn_weights: dict[str, float] = {}
    for row in causal.get("turn_ranked", []):
        if not bool(row["mirror_yaw_sign"]):
            continue
        turn_weights[str(row["label"])] = max(
            abs(float(row["left_delta_end_yaw_vs_baseline"])),
            abs(float(row["right_delta_end_yaw_vs_baseline"])),
        )

    forward_weights = _normalize(forward_weights)
    turn_weights = _normalize(turn_weights)

    observational_target_conditioned = [
        item["label"] if isinstance(item, dict) else item
        for item in observational.get("top_target_conditioned_labels", [])
    ]
    observational_bearing_locked = [
        item["label"] if isinstance(item, dict) else item
        for item in observational.get("top_bearing_locked_labels", [])
    ]
    observational_forward_locked = [
        item["label"] if isinstance(item, dict) else item
        for item in observational.get("top_forward_locked_labels", [])
    ]

    result = {
        "source_observational_json": args.observational_json,
        "source_causal_json": args.causal_json,
        "forward_group_weights": forward_weights,
        "turn_group_weights": turn_weights,
        "excluded_or_ambiguous_labels": {
            "turn_ambiguous": ["DNp71"],
            "inactive_in_first_causal_pass": ["DNpe031", "DNae002"],
            "weak_gate_like": ["DNpe016"],
        },
        "seed_forward_labels": list(forward_weights.keys()),
        "seed_turn_labels": list(turn_weights.keys()),
        "observational_context": {
            "top_target_conditioned_labels": observational_target_conditioned,
            "top_bearing_locked_labels": observational_bearing_locked,
            "top_forward_locked_labels": observational_forward_locked,
        },
        "notes": [
            "This is a first fitted motor basis from the current public-equivalent stack, not a final biological VNC/muscle mapping.",
            "Forward weights are derived from bilateral causal drive + displacement above the no-stimulation baseline.",
            "Turn weights are derived only from causal pairs that produce mirrored left/right yaw sign.",
        ],
    }

    output_path = Path(args.output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
