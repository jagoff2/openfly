# Multi GPU Evaluation

## Hardware Context

- GPU0: RTX 5060 Ti 16 GB
- GPU1: RTX 5060 Ti 16 GB
- Host driver: 581.29
- WSL sees both GPUs through CUDA

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

Result: single-GPU FlyVis execution in the production realistic-vision stack now works in WSL after upgrading to `cu128` and repairing the upstream FlyGym import-time device reset. Evidence: `outputs/profiling/flyvis_gpu_sm120_check.json`.

## Practical Verdict

- Brain-only GPU placement is practical on either host GPU.
- Concurrent offline jobs on separate GPUs are practical.
- A meaningful end-to-end dual-GPU split for the production realistic-vision closed loop is still unevaluated.
- There is still no honest basis to claim a validated brain-on-one-GPU and vision-on-the-other production run today.

## Recommended Next Experiment

Next, rerun:

- `scripts/check_cuda.sh`
- `benchmarks/run_vision_benchmarks.py --mode flygym`
- `benchmarks/run_fullstack_with_realistic_vision.py --mode flygym --durations 0.02 0.05 0.1`

with `force_cpu_vision: false`, then compare single-GPU and split-GPU placements directly.
