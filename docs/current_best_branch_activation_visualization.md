# Current Best Branch Activation Visualization

This document records the synchronized visualization artifact for the current
best embodied branch.

## Goal

Show, side by side, the embodied run plus:

- a whole-brain snapshot over the available FlyWire brain coordinates
- raw FlyVis node activity for both eyes
- monitored decoder population activity across the run
- controller and decoder-channel state across the run

## Why the monitored config was used

The strict best-branch config is:

- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated.yaml`

For visualization, the run used the monitoring-only extension:

- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_monitored.yaml`

This keeps the same calibrated splice and decoder branch but adds broad
descending/efferent monitoring so the side-by-side neural panel can show more
than the tiny fixed DN readout.

## Command

Run in the validated WSL environment:

```bash
wsl --cd /mnt/g/flysim /root/.local/bin/micromamba run -n flysim-full env MUJOCO_GL=egl \
  python scripts/build_best_branch_activation_visualization.py \
  --config configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_monitored.yaml \
  --mode flygym \
  --duration 2.0 \
  --output-root outputs/visualizations/current_best_branch_activation
```

## Artifact Set

Run directory:

- `outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618`

Key outputs:

- composite side-by-side video:
  - `outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/activation_side_by_side.mp4`
- source demo video:
  - `outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/source_demo.mp4`
- overview frame:
  - `outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/overview.png`
- synchronized capture arrays:
  - `outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/capture_data.npz`
- raw run log:
  - `outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/run.jsonl`
- metrics:
  - `outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/metrics.csv`
- summary:
  - `outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/summary.json`

## Panel Semantics

Top-left:

- embodied FlyGym frame from the best branch
- current target bearing and target distance

Top-middle:

- whole-brain point-cloud projection from local FlyWire annotation coordinates
- all available brain points shown as a density background
- current high-activity / spiking subset overlaid
- fixed decoder anchors overlaid in cyan
- monitored descending population centers overlaid in yellow

Top-right:

- monitored descending/efferent population activity over all `1000` control
  cycles
- current frame cycle marked by a vertical cursor

Bottom-left and bottom-middle:

- raw FlyVis node activity for left and right eyes
- all FlyVis nodes shown as a density background
- current high-activation subset overlaid

Bottom-right:

- decoder/controller/behavior channels over all `1000` cycles
- current frame cycle marked by a vertical cursor

## Captured Scope

From `summary.json`:

- `frame_count = 200`
- `brain_neuron_count = 138639`
- `flyvis_neuron_count = 45669`
- `monitor_label_count = 16`
- `controller_label_count = 8`

## Run Metrics

From `metrics.csv`:

- `sim_seconds = 2.0`
- `avg_forward_speed = 4.8348`
- `net_displacement = 6.2200`
- `displacement_efficiency = 0.6439`
- `stable = 1.0`
- `wall_seconds = 797.0861`
- `real_time_factor = 0.002509`

## Interpretation

This artifact is not a claim of full biological correctness.

It is a visibility artifact: it lets the repo show, in one synchronized view,
what the current best branch is doing at the embodied, whole-brain, FlyVis,
decoder, and controller layers.
