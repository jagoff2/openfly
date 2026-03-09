# FlySim

Public-equivalent local reproduction of the embodied fruit-fly stack described in `AGENTS.MD` on this Windows 11 + WSL2 workstation.

## Status

- The `AGENTS.MD` acceptance gate is met for the public-equivalent stack: the repo is runnable, tests pass, benchmark CSVs and plots exist, and realistic-vision closed-loop demos run locally.
- The strongest current embodied branch is `configs/flygym_realistic_vision_splice_axis1d_descending_readout.yaml`: it uses the calibrated FlyVis-to-whole-brain splice plus a descending-only readout, and matched controls now support the claim that this branch is brain-driven and visually driven.
- The final parity verdict is still `partial`, not `pass`, because the exact private Eon glue is not public and the current public WSL PyTorch wheel does not support RTX 5060 Ti `sm_120` for FlyVis GPU execution.
- Ground-truth progress tracking lives in `TASKS.md` and `PROGRESS_LOG.md`.

## Hardware Used

- Host OS: Windows 11
- WSL: Ubuntu 24.04 on WSL2
- GPUs: 2x NVIDIA GeForce RTX 5060 Ti 16 GB
- Host driver: 581.29
- CUDA capability exposed by driver: 13.0
- RAM: 192 GB

## Quick Start

Run these from WSL unless noted otherwise.

1. Bootstrap WSL packages:
   - `bash scripts/bootstrap_wsl.sh`
2. Create the project environments:
   - `bash scripts/bootstrap_env.sh`
3. Validate CUDA and MuJoCo in the production env:
   - `~/.local/bin/micromamba run -n flysim-full bash scripts/check_cuda.sh`
   - `~/.local/bin/micromamba run -n flysim-full bash scripts/check_mujoco.sh`
4. Run the host smoke tests from the repo root:
   - `python -m pytest tests/test_imports.py tests/test_bridge_unit.py tests/test_closed_loop_smoke.py tests/test_realistic_vision_path.py tests/test_benchmark_output_format.py tests/test_artifact_generation.py`

## Benchmark Commands

Host Torch brain benchmark:
- `python benchmarks/run_brain_benchmarks.py --config configs/default.yaml --backend torch --durations 0.1`

WSL Brian2 CPU benchmark:
- `~/.local/bin/micromamba run -n flysim-brain-brian2 python benchmarks/run_brain_benchmarks.py --config configs/default.yaml --backend brian2cpu --durations 0.1`

WSL body-only benchmark:
- `export MUJOCO_GL=egl && ~/.local/bin/micromamba run -n flysim-full python benchmarks/run_body_benchmarks.py --config configs/flygym_realistic_vision.yaml --mode flygym --durations 0.02 0.05`

WSL realistic-vision benchmark:
- `export MUJOCO_GL=egl && ~/.local/bin/micromamba run -n flysim-full python benchmarks/run_vision_benchmarks.py --config configs/flygym_realistic_vision.yaml --mode flygym --duration 0.02`

WSL full-stack realistic-vision benchmark and demo sweep:
- `export MUJOCO_GL=egl && ~/.local/bin/micromamba run -n flysim-full python benchmarks/run_fullstack_with_realistic_vision.py --config configs/flygym_realistic_vision.yaml --mode flygym --durations 0.02 0.05 0.1`

WSL profiling run:
- `export MUJOCO_GL=egl && ~/.local/bin/micromamba run -n flysim-full python benchmarks/profile_fullstack.py --config configs/flygym_realistic_vision.yaml --mode flygym --duration 0.02 --output-prefix fullstack_flygym_0p02`

Host motor-path audit for the strict brain-only blocker:
- `python scripts/audit_motor_path.py`

WSL public `P9` context experiment benchmark:
- `export MUJOCO_GL=egl && ~/.local/bin/micromamba run -n flysim-full python benchmarks/run_fullstack_with_realistic_vision.py --config configs/flygym_realistic_vision_public_p9_context.yaml --mode flygym --duration 0.02 --output-root outputs/public_p9_context_test --output-csv outputs/benchmarks/fullstack_public_p9_context_test.csv --plot-path outputs/plots/fullstack_public_p9_context_test.png`

Host search for lateralized public sensory anchors:
- `python scripts/search_lateralized_public_anchors.py`

## Replicate Current Results

These are the exact runs behind the current strongest claim: the descending-only embodied splice branch is brain-driven and visually driven, and the moving target modulates steering and drive.

Run these from WSL:

1. Target + real brain:
   - `export MUJOCO_GL=egl && ~/.local/bin/micromamba run -n flysim-full python benchmarks/run_fullstack_with_realistic_vision.py --config configs/flygym_realistic_vision_splice_axis1d_descending_readout.yaml --mode flygym --duration 2.0 --output-root outputs/requested_2s_splice_descending_logged_target --output-csv outputs/benchmarks/fullstack_splice_descending_logged_target_2s.csv`
2. No target + real brain:
   - `export MUJOCO_GL=egl && ~/.local/bin/micromamba run -n flysim-full python benchmarks/run_fullstack_with_realistic_vision.py --config configs/flygym_realistic_vision_splice_axis1d_descending_readout_no_target.yaml --mode flygym --duration 2.0 --output-root outputs/requested_2s_splice_descending_no_target --output-csv outputs/benchmarks/fullstack_splice_descending_no_target_2s.csv`
3. Target + zero brain:
   - `export MUJOCO_GL=egl && ~/.local/bin/micromamba run -n flysim-full python benchmarks/run_fullstack_with_realistic_vision.py --config configs/flygym_realistic_vision_splice_axis1d_descending_readout_zero_brain.yaml --mode flygym --duration 2.0 --output-root outputs/requested_2s_splice_descending_zero_brain --output-csv outputs/benchmarks/fullstack_splice_descending_zero_brain_2s.csv`
4. Summarize the matched controls:
   - `python scripts/summarize_descending_visual_drive.py`
5. Optional controlled target-side checks:
   - `export MUJOCO_GL=egl && ~/.local/bin/micromamba run -n flysim-full python benchmarks/run_fullstack_with_realistic_vision.py --config configs/flygym_realistic_vision_splice_axis1d_descending_readout_target_left.yaml --mode flygym --duration 1.0 --output-root outputs/requested_1s_splice_descending_target_left --output-csv outputs/benchmarks/fullstack_splice_descending_target_left_1s.csv`
   - `export MUJOCO_GL=egl && ~/.local/bin/micromamba run -n flysim-full python benchmarks/run_fullstack_with_realistic_vision.py --config configs/flygym_realistic_vision_splice_axis1d_descending_readout_target_right.yaml --mode flygym --duration 1.0 --output-root outputs/requested_1s_splice_descending_target_right --output-csv outputs/benchmarks/fullstack_splice_descending_target_right_1s.csv`
   - `export MUJOCO_GL=egl && ~/.local/bin/micromamba run -n flysim-full python benchmarks/run_fullstack_with_realistic_vision.py --config configs/flygym_realistic_vision_splice_axis1d_descending_readout_stationary_left.yaml --mode flygym --duration 1.0 --output-root outputs/requested_1s_splice_descending_stationary_left --output-csv outputs/benchmarks/fullstack_splice_descending_stationary_left_1s.csv`
   - `export MUJOCO_GL=egl && ~/.local/bin/micromamba run -n flysim-full python benchmarks/run_fullstack_with_realistic_vision.py --config configs/flygym_realistic_vision_splice_axis1d_descending_readout_stationary_right.yaml --mode flygym --duration 1.0 --output-root outputs/requested_1s_splice_descending_stationary_right --output-csv outputs/benchmarks/fullstack_splice_descending_stationary_right_1s.csv`
   - `python scripts/summarize_descending_target_conditions.py`

Expected evidence after those runs:

- `outputs/metrics/descending_visual_drive_validation.json`
- `outputs/metrics/descending_target_conditions.json`
- `outputs/metrics/descending_stationary_target_conditions.json`
- `docs/descending_visual_drive_validation.md`

## Demo Artifacts

Current strongest real embodied splice artifacts:

- target + real brain: `outputs/requested_2s_splice_descending_logged_target/flygym-demo-20260309-142600/demo.mp4`
- no target + real brain: `outputs/requested_2s_splice_descending_no_target/flygym-demo-20260309-122723/demo.mp4`
- target + zero brain: `outputs/requested_2s_splice_descending_zero_brain/flygym-demo-20260309-122135/demo.mp4`
- visual-drive summary: `outputs/metrics/descending_visual_drive_validation.json`
- target-condition summary: `outputs/metrics/descending_target_conditions.json`
- benchmark summary: `docs/benchmark_summary.md`
- parity report: `REPRO_PARITY_REPORT.md`
- descending-branch validation: `docs/descending_visual_drive_validation.md`

## Repo Layout

- `src/brain/`: neural backends and public neuron ID anchors
- `src/body/`: mock and FlyGym runtime adapters
- `src/bridge/`: sensory encoder, motor decoder, closed-loop controller
- `src/runtime/`: scheduler, logging, artifact generation
- `benchmarks/`: benchmark, profiling, and run-summary scripts
- `tests/`: smoke, unit, and artifact regression tests
- `outputs/`: benchmark CSVs, plots, demos, logs, metrics, and profiling artifacts

## Known Limitations

- Exact private Eon glue is unavailable, so the bridge is an explicit public-equivalent substitute.
- The public WSL `cu126` PyTorch wheel used by FlyVis does not support RTX 5060 Ti `sm_120`; production WSL runs therefore use `force_cpu_vision: true` in `configs/flygym_realistic_vision.yaml`.
- The strict default public bilateral-anchor path is still weak: it was useful as a falsification step, but by itself it does not yet produce strong pursuit behavior. The repo's strongest current branch is the newer descending-only embodied splice path documented in `docs/descending_visual_drive_validation.md`.
- That stronger branch is not a hidden locomotion hack: matched `zero_brain` controls produce zero commands and negligible displacement, while target-present runs show stronger drive and steering than no-target runs.
- What is still not proven is final biological correctness of the motor interface. The current decoder still compresses descending/efferent population activity into `left_drive` / `right_drive`, so this is not yet a full neck-connective / VNC / muscle-level reconstruction.
- `docs/public_p9_context_mode.md` documents a clearly labeled public-experiment analogue that injects direct `P9` drive on the brain side without restoring decoder or body fallback locomotion.
- `docs/lateralized_public_anchors.md` and `outputs/metrics/lateralized_public_anchors.json` show that the checked public artifacts do not expose clearly lateralized visual or mechanosensory anchor pools, so the repo does not currently claim honest public left/right visual steering input.
- The short controlled left/right target conditions are still mixed rather than a clean mirrored pursuit reflex; see `outputs/metrics/descending_target_conditions.json`, `outputs/metrics/descending_stationary_target_conditions.json`, and `TASKS.md:T072`.
- `Brian2CUDA` and `NEST GPU` were not validated locally; the second benchmarked neural backend is `Brian2` CPU.
- The repo is now in Git and published on GitHub, but older benchmark CSVs created before Git initialization may still carry `commit_hash = not_a_git_repo`.
