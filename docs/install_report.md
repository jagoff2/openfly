# Install Report

## Validated Environment Plan

- Primary production environment: WSL2 Ubuntu 24.04, `micromamba` env `flysim-full`
- Secondary benchmark environment: WSL2 Ubuntu 24.04, `micromamba` env `flysim-brain-brian2`
- Host-side lightweight validation path: Windows Python 3.10.11 for smoke tests and Torch brain benchmarking

## Validated Commands

Run from WSL at `/mnt/g/flysim`:

- `bash scripts/bootstrap_wsl.sh`
- `bash scripts/bootstrap_env.sh`
- `~/.local/bin/micromamba run -n flysim-full bash scripts/check_cuda.sh`
- `~/.local/bin/micromamba run -n flysim-full bash scripts/check_mujoco.sh`

Run from the Windows host at `G:\flysim`:

- `python -m pytest tests/test_imports.py tests/test_bridge_unit.py tests/test_closed_loop_smoke.py tests/test_realistic_vision_path.py tests/test_benchmark_output_format.py tests/test_artifact_generation.py`

## What Had To Be Fixed

1. WSL bootstrap scripts initially failed because the shell files had CRLF line endings. They were normalized to LF.
2. The public FlyGym realistic-vision stack needed `cachetools` in `environment/requirements-full.txt`.
3. The public FlyVis model weights were not present after package install, so `scripts/bootstrap_env.sh` now runs `flyvis download-pretrained`.
4. The Brian2 comparison env needed `setuptools<81` because the public code still imports `pkg_resources`.
5. The checked-out public `external/fly-brain` code needed local compatibility patches for the current Brian2 API and benchmark CSV column naming.
6. The production WSL config needed CPU vision fallback because the public WSL PyTorch wheel does not support local `sm_120` GPUs.

## Validated Outcomes

- `scripts/bootstrap_wsl.sh` completes successfully.
- `scripts/bootstrap_env.sh` creates both required environments successfully.
- `scripts/check_cuda.sh` in `flysim-full` reports that CUDA is visible in WSL, but the installed public wheel warns that RTX 5060 Ti `sm_120` is unsupported.
- `scripts/check_mujoco.sh` in `flysim-full` imports `mujoco`, `dm_control`, and `flygym` successfully.
- Real FlyGym realistic-vision runs now work locally in WSL with `force_cpu_vision: true`.
- Host smoke tests pass.

## Current Production Limitation

The validated production path is:

- WSL `flysim-full`
- `MUJOCO_GL=egl`
- `configs/flygym_realistic_vision.yaml`
- `runtime.force_cpu_vision: true`

This is required because the current public WSL PyTorch wheel for FlyVis does not provide support for RTX 5060 Ti `sm_120`. Once a public wheel supports that architecture, the first follow-up experiment should be a true GPU vision rerun with the same benchmark scripts.
