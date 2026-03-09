# Multi GPU Evaluation

## Hardware Context

- GPU0: RTX 5060 Ti 16 GB
- GPU1: RTX 5060 Ti 16 GB
- Host driver: 581.29
- WSL sees both GPUs through CUDA, but public wheel support is the limiting factor

## What Was Tested

### Host Torch device probe

Evidence: `outputs/profiling/torch_device_probe.json`

| Device | Sim Seconds | Wall Seconds | Real-Time Factor |
| --- | ---: | ---: | ---: |
| `cuda:0` | 0.100 | 0.928 | 0.1078x |
| `cuda:1` | 0.100 | 0.886 | 0.1129x |

Result: the brain-only Torch backend can be pinned to either GPU, and `cuda:1` was slightly faster in the measured run.

### WSL production full stack

Evidence: `scripts/check_cuda.sh`, `docs/install_report.md`, `outputs/benchmarks/fullstack_benchmarks.csv`

Result: the production realistic-vision stack in WSL cannot currently use the local GPUs safely because the public WSL PyTorch `cu126` wheel used by FlyVis does not support RTX 5060 Ti `sm_120`. The validated workaround is `force_cpu_vision: true`.

## Practical Verdict

- Brain-only GPU placement is practical on either host GPU.
- Concurrent offline jobs on separate GPUs are practical.
- A meaningful end-to-end dual-GPU split for the production realistic-vision closed loop is currently blocked by the public WSL wheel limitation.
- Because of that blocker, there is no honest basis to claim a validated brain-on-one-GPU and vision-on-the-other production run today.

## Recommended Next Experiment

Once a public WSL wheel supports `sm_120`, rerun:

- `scripts/check_cuda.sh`
- `benchmarks/run_vision_benchmarks.py --mode flygym`
- `benchmarks/run_fullstack_with_realistic_vision.py --mode flygym --durations 0.02 0.05 0.1`

with `force_cpu_vision: false`, then compare single-GPU and split-GPU placements directly.
