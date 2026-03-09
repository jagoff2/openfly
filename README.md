# FlySim

Public-equivalent local reproduction of the embodied fruit-fly stack described in `AGENTS.MD` on this Windows 11 + WSL2 workstation.

## Status

- The `AGENTS.MD` acceptance gate is met for the public-equivalent stack: the repo is runnable, tests pass, benchmark CSVs and plots exist, and realistic-vision closed-loop demos run locally.
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

## Demo Artifacts

Current real FlyGym realistic-vision demo artifacts:

- short: `outputs/demos/flygym-demo-20260308-121237.mp4`
- medium: `outputs/demos/flygym-demo-20260308-121318.mp4`
- longest stable: `outputs/demos/flygym-demo-20260308-121432.mp4`
- screenshots: `outputs/screenshots/flygym-demo-20260308-121237.png`, `outputs/screenshots/flygym-demo-20260308-121318.png`, `outputs/screenshots/flygym-demo-20260308-121432.png`
- parity summary CSV: `outputs/metrics/parity_runs.csv`
- benchmark summary: `docs/benchmark_summary.md`
- parity report: `REPRO_PARITY_REPORT.md`

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
- The production path now enforces brain-only motor output: the decoder idle-drive floor is removed and the public bilateral `LC4` / `JON` anchors are no longer split into fabricated left/right hemispheres.
- Under this stricter production path, short real diagnostics currently produce zero monitored motor cycles and only small passive body settling motion, so convincing brain-driven pursuit behavior is still not established.
- `docs/motor_path_audit.md` and `outputs/metrics/motor_path_audit.json` show why: the current strict bilateral public sensory inputs weakly reach the monitored locomotor DN set, while direct public `P9` stimulation remains a strong positive control.
- `docs/public_p9_context_mode.md` documents a clearly labeled public-experiment analogue that injects direct `P9` drive on the brain side without restoring decoder or body fallback locomotion.
- `docs/lateralized_public_anchors.md` and `outputs/metrics/lateralized_public_anchors.json` show that the checked public artifacts do not expose clearly lateralized visual or mechanosensory anchor pools, so the repo does not currently claim honest public left/right visual steering input.
- `Brian2CUDA` and `NEST GPU` were not validated locally; the second benchmarked neural backend is `Brian2` CPU.
- This workspace is not inside a Git repository, so benchmark CSVs record `commit_hash = not_a_git_repo`.
