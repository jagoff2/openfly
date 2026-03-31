from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from torch import Tensor

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

import flyvis
from flygym.examples.vision import RealTimeVisionNetworkView, RetinaMapper
from flygym.vision import Retina

from brain.public_ids import DEFAULT_FLOW_CELLS, DEFAULT_TRACKING_CELLS
from vision.flyvis_compat import configure_flyvis_device
from vision.lateralized_probe import (
    build_body_side_mask,
    build_body_side_stimuli,
    compute_mirror_selectivity_scores,
    compute_retina_geometry,
)


def _condition_side(condition_name: str) -> str:
    if condition_name == "body_left_dark":
        return "left"
    if condition_name == "body_center_dark":
        return "center"
    if condition_name == "body_right_dark":
        return "right"
    raise ValueError(f"Unsupported condition name: {condition_name}")


def _build_layer_indices(network) -> dict[str, np.ndarray]:
    layer_indices: dict[str, np.ndarray] = {}
    for cell_type, indices in network.connectome.nodes.layer_index.items():
        name = cell_type.decode() if isinstance(cell_type, bytes) else str(cell_type)
        layer_indices[name] = np.asarray(indices[:], dtype=int)
    return layer_indices


def _prepare_network(vision_network_dir: str | None):
    configure_flyvis_device(force_cpu=False)
    retina = Retina()
    retina_mapper = RetinaMapper(retina=retina)
    if vision_network_dir is None:
        vision_network_dir = str(flyvis.results_dir / "flow/0000/000")
    network_view = RealTimeVisionNetworkView(vision_network_dir)
    network = network_view.init_network(chkpt="best_chkpt")
    return retina, retina_mapper, network


def _setup_step_simulation(network, retina_mapper: RetinaMapper, baseline_gray: np.ndarray, vision_refresh_rate: float):
    visual_input = retina_mapper.flygym_to_flyvis(baseline_gray)
    visual_input = Tensor(visual_input).to(flyvis.device)
    initial_state = network.fade_in_state(
        t_fade_in=1.0,
        dt=1.0 / vision_refresh_rate,
        initial_frames=visual_input.unsqueeze(1),
    )
    network.setup_step_by_step_simulation(
        dt=1.0 / vision_refresh_rate,
        initial_state=initial_state,
        as_states=False,
        num_samples=2,
    )


def _run_condition(
    network,
    retina_mapper: RetinaMapper,
    stimulus_gray: np.ndarray,
    *,
    baseline_gray: np.ndarray,
    vision_refresh_rate: float,
    steps: int,
    tail_steps: int,
) -> np.ndarray:
    _setup_step_simulation(network, retina_mapper, baseline_gray, vision_refresh_rate)
    visual_input = retina_mapper.flygym_to_flyvis(stimulus_gray)
    visual_input = Tensor(visual_input).to(flyvis.device)
    tail: list[np.ndarray] = []
    try:
        for _ in range(steps):
            nn_activities_arr = network.forward_one_step(visual_input)
            if hasattr(nn_activities_arr, "detach"):
                nn_activities_arr = nn_activities_arr.detach()
            if hasattr(nn_activities_arr, "cpu"):
                nn_activities_arr = nn_activities_arr.cpu().numpy()
            tail.append(np.asarray(nn_activities_arr, dtype=float))
            if len(tail) > tail_steps:
                tail.pop(0)
    finally:
        network.cleanup_step_by_step_simulation()
    return np.stack(tail, axis=0)


def _aggregate_patch_mean(
    activity_tail: np.ndarray,
    *,
    eye_index: int,
    cell_indices: np.ndarray,
    retina_mapper: RetinaMapper,
    mask: np.ndarray,
) -> float:
    values = []
    for frame in activity_tail:
        flyvis_values = frame[eye_index, cell_indices]
        if flyvis_values.size == 0:
            continue
        flygym_values = retina_mapper.flyvis_to_flygym(flyvis_values)
        values.append(float(np.mean(flygym_values[mask])))
    return float(np.mean(values)) if values else 0.0


def _make_stimulus_plot(retina: Retina, stimuli: dict[str, np.ndarray], output_path: Path) -> None:
    fig, axes = plt.subplots(len(stimuli), 2, figsize=(6, 2 * len(stimuli)), tight_layout=True)
    if len(stimuli) == 1:
        axes = np.asarray([axes])
    for row_index, (name, stimulus) in enumerate(stimuli.items()):
        for eye_index, eye_name in enumerate(("L", "R")):
            ax = axes[row_index, eye_index]
            human = retina.hex_pxls_to_human_readable(stimulus[eye_index], color_8bit=False)
            human[retina.ommatidia_id_map == 0] = np.nan
            ax.imshow(human, cmap="gray", vmin=0.0, vmax=1.0)
            ax.set_title(f"{name} {eye_name}")
            ax.axis("off")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe the real visual system model with crafted left/right stimuli to infer lateralized candidate cell types.")
    parser.add_argument("--vision-network-dir", default=None, help="Optional FlyVis checkpoint directory. Defaults to the packaged flow/0000/000 checkpoint.")
    parser.add_argument("--vision-refresh-rate", type=float, default=500.0)
    parser.add_argument("--steps", type=int, default=40, help="Number of closed-loop vision steps per condition.")
    parser.add_argument("--tail-steps", type=int, default=10, help="Number of trailing steps to average for each condition.")
    parser.add_argument("--baseline-value", type=float, default=1.0)
    parser.add_argument("--patch-value", type=float, default=0.0)
    parser.add_argument("--side-fraction", type=float, default=0.35)
    parser.add_argument("--csv-output", default="outputs/metrics/inferred_lateralized_visual_candidates.csv")
    parser.add_argument("--json-output", default="outputs/metrics/inferred_lateralized_visual_candidates.json")
    parser.add_argument("--stimulus-plot", default="outputs/plots/inferred_lateralized_visual_stimuli.png")
    args = parser.parse_args()

    retina, retina_mapper, network = _prepare_network(args.vision_network_dir)
    geometry = compute_retina_geometry(retina.ommatidia_id_map)
    stimuli = build_body_side_stimuli(
        geometry,
        baseline_value=args.baseline_value,
        patch_value=args.patch_value,
        side_fraction=args.side_fraction,
    )
    _make_stimulus_plot(
        retina,
        {key: stimuli[key] for key in ("baseline_gray", "body_left_dark", "body_center_dark", "body_right_dark")},
        Path(args.stimulus_plot),
    )

    condition_names = ("baseline_gray", "body_left_dark", "body_center_dark", "body_right_dark")
    condition_tails = {
        name: _run_condition(
            network,
            retina_mapper,
            stimuli[name],
            baseline_gray=stimuli["baseline_gray"],
            vision_refresh_rate=args.vision_refresh_rate,
            steps=args.steps,
            tail_steps=args.tail_steps,
        )
        for name in condition_names
    }

    layer_indices = _build_layer_indices(network)
    num_ommatidia = retina.num_ommatidia_per_eye
    valid_cell_types = {
        cell_type: indices
        for cell_type, indices in layer_indices.items()
        if len(indices) == num_ommatidia
    }

    mask_by_condition_and_eye = {}
    for condition_name in ("body_left_dark", "body_center_dark", "body_right_dark"):
        side = _condition_side(condition_name)
        mask_by_condition_and_eye[condition_name] = {
            eye_index: build_body_side_mask(geometry, eye_index, side, side_fraction=args.side_fraction)
            for eye_index in (0, 1)
        }

    rows = []
    for cell_type, indices in sorted(valid_cell_types.items()):
        baseline_body_left_left = _aggregate_patch_mean(
            condition_tails["baseline_gray"],
            eye_index=0,
            cell_indices=indices,
            retina_mapper=retina_mapper,
            mask=mask_by_condition_and_eye["body_left_dark"][0],
        )
        baseline_body_left_right = _aggregate_patch_mean(
            condition_tails["baseline_gray"],
            eye_index=1,
            cell_indices=indices,
            retina_mapper=retina_mapper,
            mask=mask_by_condition_and_eye["body_left_dark"][1],
        )
        baseline_body_right_left = _aggregate_patch_mean(
            condition_tails["baseline_gray"],
            eye_index=0,
            cell_indices=indices,
            retina_mapper=retina_mapper,
            mask=mask_by_condition_and_eye["body_right_dark"][0],
        )
        baseline_body_right_right = _aggregate_patch_mean(
            condition_tails["baseline_gray"],
            eye_index=1,
            cell_indices=indices,
            retina_mapper=retina_mapper,
            mask=mask_by_condition_and_eye["body_right_dark"][1],
        )
        baseline_body_center_left = _aggregate_patch_mean(
            condition_tails["baseline_gray"],
            eye_index=0,
            cell_indices=indices,
            retina_mapper=retina_mapper,
            mask=mask_by_condition_and_eye["body_center_dark"][0],
        )
        baseline_body_center_right = _aggregate_patch_mean(
            condition_tails["baseline_gray"],
            eye_index=1,
            cell_indices=indices,
            retina_mapper=retina_mapper,
            mask=mask_by_condition_and_eye["body_center_dark"][1],
        )

        body_left_left = _aggregate_patch_mean(
            condition_tails["body_left_dark"],
            eye_index=0,
            cell_indices=indices,
            retina_mapper=retina_mapper,
            mask=mask_by_condition_and_eye["body_left_dark"][0],
        ) - baseline_body_left_left
        body_left_right = _aggregate_patch_mean(
            condition_tails["body_left_dark"],
            eye_index=1,
            cell_indices=indices,
            retina_mapper=retina_mapper,
            mask=mask_by_condition_and_eye["body_left_dark"][1],
        ) - baseline_body_left_right
        body_right_left = _aggregate_patch_mean(
            condition_tails["body_right_dark"],
            eye_index=0,
            cell_indices=indices,
            retina_mapper=retina_mapper,
            mask=mask_by_condition_and_eye["body_right_dark"][0],
        ) - baseline_body_right_left
        body_right_right = _aggregate_patch_mean(
            condition_tails["body_right_dark"],
            eye_index=1,
            cell_indices=indices,
            retina_mapper=retina_mapper,
            mask=mask_by_condition_and_eye["body_right_dark"][1],
        ) - baseline_body_right_right
        body_center_left = _aggregate_patch_mean(
            condition_tails["body_center_dark"],
            eye_index=0,
            cell_indices=indices,
            retina_mapper=retina_mapper,
            mask=mask_by_condition_and_eye["body_center_dark"][0],
        ) - baseline_body_center_left
        body_center_right = _aggregate_patch_mean(
            condition_tails["body_center_dark"],
            eye_index=1,
            cell_indices=indices,
            retina_mapper=retina_mapper,
            mask=mask_by_condition_and_eye["body_center_dark"][1],
        ) - baseline_body_center_right

        rows.append(
            {
                "cell_type": cell_type,
                "body_left_left_eye_mean": body_left_left,
                "body_left_right_eye_mean": body_left_right,
                "body_right_left_eye_mean": body_right_left,
                "body_right_right_eye_mean": body_right_right,
                "body_center_abs_delta": float(0.5 * (abs(body_center_left) + abs(body_center_right))),
                "is_tracking_cell": cell_type in DEFAULT_TRACKING_CELLS,
                "is_flow_cell": cell_type in DEFAULT_FLOW_CELLS,
            }
        )

    ranked_rows = compute_mirror_selectivity_scores(rows)

    csv_output = Path(args.csv_output)
    csv_output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(ranked_rows[0].keys()) if ranked_rows else []
    with csv_output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ranked_rows)

    json_output = Path(args.json_output)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    top_sign_flip = [row for row in ranked_rows if row["sign_flip_consistent"]][:15]
    report = {
        "vision_network_dir": args.vision_network_dir or str(flyvis.results_dir / "flow/0000/000"),
        "vision_refresh_rate_hz": args.vision_refresh_rate,
        "steps": args.steps,
        "tail_steps": args.tail_steps,
        "baseline_value": args.baseline_value,
        "patch_value": args.patch_value,
        "side_fraction": args.side_fraction,
        "num_valid_cell_types": len(valid_cell_types),
        "stimulus_plot": str(Path(args.stimulus_plot)),
        "top_candidates_all": ranked_rows[:15],
        "top_candidates_sign_flip_consistent": top_sign_flip,
        "notes": [
            "These candidates are inferred from crafted visual stimuli through the real FlyVis model, not from explicit public left/right sensory annotations in the whole-brain notebook artifacts.",
            "The ranking favors cell types whose left-eye minus right-eye response flips when the crafted object moves from the fly's left field to the fly's right field.",
            "This artifact supports an inferred lateralized bridge, not a strictly public-grounded one.",
        ],
    }
    json_output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(csv_output)
    print(json_output)


if __name__ == "__main__":
    main()
