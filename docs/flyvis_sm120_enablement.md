# FlyVis `sm_120` GPU Enablement

## Summary

FlyVis now runs on the local RTX 5060 Ti GPUs under WSL in the primary `flysim-full` environment.

This required two fixes:

1. Upgrade the WSL Torch stack from `cu126` to `cu128`.
2. Repair an upstream FlyGym import-time side effect that forced `flyvis.device` back to CPU and left already-loaded FlyVis modules in a mixed CPU/CUDA state.

## Root Cause

The original blocker was not only the old Torch wheel.

### 1. CUDA wheel mismatch

The prior environment used:

- `torch 2.10.0+cu126`
- `torchvision 0.25.0+cu126`

That stack exposed CUDA visibility, but it did not ship kernels for `sm_120`. A trivial CUDA tensor failed with:

- `CUDA error: no kernel image is available for execution on the device`

### 2. FlyGym vision import reset

After the wheel upgrade, the production FlyVis path still did not run correctly by default because importing `flygym.examples.vision` executed upstream code that:

- set `torch.set_default_device(cpu)`
- reset `flyvis.device` to CPU

At the same time, some FlyVis modules had already imported and cached `device` by value, especially:

- `flyvis.network.initialization`
- `flyvis.task.decoder`

That left the process in a mixed state where parts of FlyVis thought the device was CUDA and other parts thought it was CPU.

## Repo Fix

### Environment

- `environment/requirements-full.txt` now points at `https://download.pytorch.org/whl/cu128`

### Runtime compatibility layer

- `src/vision/flyvis_compat.py`

This helper:

- resolves the intended FlyVis device
- updates `flyvis.device`
- updates Torch's default device
- patches already-loaded FlyVis submodules that cache `device`

### Production wiring

- `src/body/flygym_runtime.py`
- `src/body/brain_only_realistic_vision_fly.py`

The runtime and realistic-vision fly wrapper now re-synchronize the FlyVis device after the upstream FlyGym vision import path has run.

### Script compatibility

The old analysis/probe scripts that had been hard-coded to CPU now use the same compatibility layer:

- `scripts/probe_lateralized_visual_candidates.py`
- `scripts/run_splice_probe.py`
- `scripts/inspect_flyvis_overlap.py`
- `scripts/inspect_flyvis_nodes.py`

## Evidence

Primary smoke artifact:

- `outputs/profiling/flyvis_gpu_sm120_check.json`

That artifact shows:

- `torch_version = 2.10.0+cu128`
- `torch_cuda_version = 12.8`
- `flyvis_device = cuda`
- `output_device = cuda:0`
- `output_shape = [2, 45669]`

It also includes a repo-runtime smoke section:

- `runtime_smoke.vision_parameter_device = cuda:0`
- `runtime_smoke.vision_payload_mode = fast`
- `runtime_smoke.has_nn_activities_arr = true`

## Current Scope

Resolved:

- single-GPU FlyVis execution in WSL on local `sm_120`
- production runtime using GPU FlyVis when `force_cpu_vision: false`

Not yet rerun:

- historical vision benchmark tables
- historical full-stack benchmark tables
- dual-GPU split experiments

So the correct current claim is:

- FlyVis GPU execution on `sm_120` is now working locally.
- The benchmark/perf documents still contain historical CPU-fallback numbers until those sweeps are rerun.
