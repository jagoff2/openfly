# OpenFly

Public-equivalent reconstruction of an embodied Drosophila brain-body stack from open artifacts.

Status: complete with partial parity verdict.

This repo runs a real closed loop locally on one Windows 11 workstation with WSL2, dual RTX 5060 Ti 16 GB GPUs, and 192 GB RAM. The production path combines a persistent FlyWire-derived whole-brain backend, FlyGym / NeuroMechFly v2 embodiment, FlyGym realistic vision with FlyVis-derived activity, and in-repo bridge code for online control. It is not a claim that the private Eon glue or unpublished parameters were recovered exactly.

The strongest current branch is [configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated.yaml](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated.yaml). In the current `2.0 s` target run it reaches `avg_forward_speed = 4.9241`, `net_displacement = 5.7583`, `displacement_efficiency = 0.5853`, and `corr(right_drive - left_drive, target_bearing) = 0.8810`. The matched `zero_brain` control stays near zero with `nonzero_command_cycles = 0`, which is the strongest evidence that the embodied motion is coming from the brain-driven branch rather than a hidden locomotion fallback.

**What Runs Today**

- Real FlyGym body and realistic vision in the production path, not toy RGB-only input.
- Persistent Torch whole-brain backend over the local FlyWire-derived graph.
- Closed-loop body -> vision/splice -> brain -> decoder -> body runtime.
- Benchmark, demo, plot, JSONL, CSV, and video artifacts saved locally.
- A synchronized activation visualization showing the current best branch at the body, whole-brain, FlyVis, decoder, and controller layers.

**What This Is And Is Not**

- This is a public-equivalent reconstruction from open repositories and papers.
- The bridge layer is in-repo engineering glue because the public repos do not ship a turnkey persistent embodied controller.
- The best current result is visually driven embodied locomotion with partial parity, not a claim of full biological motor-path fidelity.
- The semantic-VNC structural decoder line was tested and frozen as a failed parity branch after it moved the fly but still failed target tracking.

**Current Best Evidence**

- Best production config: [configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated.yaml](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated.yaml)
- Target run: [demo.mp4](/G:/flysim/outputs/requested_2s_splice_uvgrid_descending_calibrated_target/flygym-demo-20260311-071452/demo.mp4)
- Target metrics: [metrics.csv](/G:/flysim/outputs/requested_2s_splice_uvgrid_descending_calibrated_target/flygym-demo-20260311-071452/metrics.csv)
- No-target control: [demo.mp4](/G:/flysim/outputs/requested_2s_splice_uvgrid_descending_calibrated_no_target/flygym-demo-20260311-073028/demo.mp4)
- Zero-brain control: [demo.mp4](/G:/flysim/outputs/requested_2s_splice_uvgrid_descending_calibrated_zero_brain/flygym-demo-20260311-074301/demo.mp4)
- Validation summary: [uvgrid_decoder_calibration.md](/G:/flysim/docs/uvgrid_decoder_calibration.md)

**Activation Visualization**

The best branch now has a synchronized side-by-side activation artifact:

- Composite video: [activation_side_by_side.mp4](/G:/flysim/outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/activation_side_by_side.mp4)
- Overview frame: [overview.png](/G:/flysim/outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/overview.png)
- Capture bundle: [capture_data.npz](/G:/flysim/outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/capture_data.npz)
- Writeup: [current_best_branch_activation_visualization.md](/G:/flysim/docs/current_best_branch_activation_visualization.md)

That artifact captures `200` synchronized frames across `138639` local FlyWire brain points, `45669` FlyVis nodes, `16` monitored decoder labels, and `8` controller channels. It is a visibility artifact, not a new parity claim.

**Quick Start**

From WSL:

```bash
bash scripts/bootstrap_wsl.sh
bash scripts/bootstrap_env.sh
~/.local/bin/micromamba run -n flysim-full bash scripts/check_cuda.sh
~/.local/bin/micromamba run -n flysim-full bash scripts/check_mujoco.sh
```

Run the strongest current embodied branch:

```bash
export MUJOCO_GL=egl
~/.local/bin/micromamba run -n flysim-full python benchmarks/run_fullstack_with_realistic_vision.py \
  --config configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated.yaml \
  --mode flygym \
  --duration 2.0 \
  --output-root outputs/requested_2s_splice_uvgrid_descending_calibrated_target \
  --output-csv outputs/benchmarks/fullstack_splice_uvgrid_descending_calibrated_target_2s.csv
```

Build the side-by-side activation visualization:

```bash
export MUJOCO_GL=egl
~/.local/bin/micromamba run -n flysim-full python scripts/build_best_branch_activation_visualization.py \
  --config configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_monitored.yaml \
  --mode flygym \
  --duration 2.0 \
  --output-root outputs/visualizations/current_best_branch_activation
```

Run focused tests:

```bash
python -m pytest tests/test_bridge_unit.py tests/test_closed_loop_smoke.py tests/test_activation_viz.py -q
```

**Architecture At A Glance**

`FlyGym body + realistic vision -> visual splice / encoder -> persistent whole-brain backend -> descending/efferent decoder -> FlyGym controller`

Implementation spine:

- [flygym_runtime.py](/G:/flysim/src/body/flygym_runtime.py)
- [visual_splice.py](/G:/flysim/src/bridge/visual_splice.py)
- [pytorch_backend.py](/G:/flysim/src/brain/pytorch_backend.py)
- [decoder.py](/G:/flysim/src/bridge/decoder.py)
- [closed_loop.py](/G:/flysim/src/runtime/closed_loop.py)

**Performance Snapshot**

| Workload | Device | Sim time | Wall time | Real-time factor |
| --- | --- | ---: | ---: | ---: |
| Brain only, Torch | `cuda:0` | `0.100 s` | `0.923 s` | `0.1083x` |
| Brain only, Brian2 CPU | `cpu` | `0.100 s` | `10.852 s` | `0.0092x` |
| Body only | `cpu` | `0.020 s` | `0.285 s` | `0.0701x` |
| Realistic vision only | `cpu` | `0.020 s` | `22.644 s` | `0.000883x` |
| Full legacy closed loop | `cpu` | `0.098 s` | `125.350 s` | `0.000782x` |

**Ground-Truth Docs**

- Whitepaper: [openfly_whitepaper.md](/G:/flysim/docs/openfly_whitepaper.md)
- Parity report: [REPRO_PARITY_REPORT.md](/G:/flysim/REPRO_PARITY_REPORT.md)
- Assumptions and gaps: [ASSUMPTIONS_AND_GAPS.md](/G:/flysim/ASSUMPTIONS_AND_GAPS.md)
- Task tracker: [TASKS.md](/G:/flysim/TASKS.md)
- Lab notebook: [PROGRESS_LOG.md](/G:/flysim/PROGRESS_LOG.md)

**Known Limits**

- Exact private Eon glue is unavailable, so parity is measured against public observables rather than claimed internal equivalence.
- The validated WSL production path is still CPU-only for FlyVis on this hardware because public wheels do not support RTX 5060 Ti `sm_120`.
- The visual splice is still an inferred FlyVis-to-FlyWire interface.
- The motor interface is still a compressed descending/efferent-to-controller abstraction, not a full biological VNC-to-muscle pathway.
- The semantic-VNC structural decoder branch is frozen as a failed parity line: [semantic_vnc_failed_parity_branch.md](/G:/flysim/docs/semantic_vnc_failed_parity_branch.md).

**Repo Layout**

- `src/`: brain, body, bridge, runtime, visualization, and VNC code
- `configs/`: runnable production, control, and experimental configs
- `benchmarks/`: reproducible benchmark runners
- `scripts/`: setup, probe, summary, and artifact-build scripts
- `tests/`: unit, smoke, integration, and artifact tests
- `outputs/`: demos, metrics, plots, logs, profiling, and visualization artifacts
- `docs/`: whitepaper, parity report support, and detailed technical notes
