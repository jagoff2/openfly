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
6. FlyVis on `sm_120` needed two fixes before GPU execution worked in WSL:
   - upgrade the Torch stack from `cu126` to `cu128`
   - repair the upstream FlyGym vision import path that reset `flyvis.device` back to CPU

## Validated Outcomes

- `scripts/bootstrap_wsl.sh` completes successfully.
- `scripts/bootstrap_env.sh` creates both required environments successfully.
- `scripts/check_cuda.sh` in `flysim-full` reports CUDA visibility, compute capability, and a successful CUDA tensor smoke on the RTX 5060 Ti.
- `scripts/check_mujoco.sh` in `flysim-full` imports `mujoco`, `dm_control`, and `flygym` successfully.
- `scripts/check_flyvis_gpu.py` proves that both the pretrained FlyVis network and the repo's `FlyGymRealisticVisionRuntime` use `cuda:0` when `force_cpu_vision: false`.
- Real FlyGym realistic-vision runs now work locally in WSL without the old forced CPU fallback.
- Host smoke tests pass.

## Current Production Path

The validated production path is:

- WSL `flysim-full`
- `MUJOCO_GL=egl`
- `configs/flygym_realistic_vision.yaml`
- `runtime.force_cpu_vision: false`

The remaining limitation is not basic GPU compatibility anymore. The remaining limitation is that the historical realistic-vision benchmark tables were gathered under the old CPU fallback and still need to be rerun under the new GPU-capable path.
