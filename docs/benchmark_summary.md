# Benchmark Summary

## Evidence Files

- `outputs/benchmarks/brain_benchmarks.csv`
- `outputs/benchmarks/body_benchmarks.csv`
- `outputs/benchmarks/vision_benchmarks.csv`
- `outputs/benchmarks/fullstack_benchmarks.csv`
- `outputs/plots/brain_benchmarks.png`
- `outputs/plots/body_benchmarks.png`
- `outputs/plots/vision_benchmarks.png`
- `outputs/plots/fullstack_benchmarks.png`
- `outputs/profiling/torch_device_probe.json`
- `outputs/profiling/fullstack_flygym_0p02.txt`

## Measured Results

### Brain only

| Backend | Device | Sim Seconds | Wall Seconds | Real-Time Factor | Evidence |
| --- | --- | ---: | ---: | ---: | --- |
| Torch | `cuda:0` | 0.100 | 0.923 | 0.1083x | `outputs/benchmarks/brain_benchmarks.csv` |
| Brian2 CPU | `cpu` | 0.100 | 10.852 | 0.0092x | `outputs/benchmarks/brain_benchmarks.csv` |
| Torch device probe | `cuda:1` | 0.100 | 0.886 | 0.1129x | `outputs/profiling/torch_device_probe.json` |

### Body only

| Backend | Device | Sim Seconds | Wall Seconds | Real-Time Factor |
| --- | --- | ---: | ---: | ---: |
| FlyGym body | `cpu` | 0.020 | 0.285 | 0.0701x |
| FlyGym body | `cpu` | 0.050 | 0.732 | 0.0683x |

### Realistic vision representative workload

| Backend | Device | Sim Seconds | Wall Seconds | Real-Time Factor |
| --- | --- | ---: | ---: | ---: |
| FlyGym realistic vision | `cpu` | 0.020 | 22.644 | 0.000883x |

### Full closed-loop stack with realistic vision

| Run | Device | Sim Seconds | Wall Seconds | Real-Time Factor |
| --- | --- | ---: | ---: | ---: |
| short | `cpu` | 0.018 | 24.479 | 0.000735x |
| medium | `cpu` | 0.048 | 61.660 | 0.000778x |
| longest stable | `cpu` | 0.098 | 125.350 | 0.000782x |

## Interpretation

- The production bottleneck is the FlyGym plus FlyVis runtime, not the in-repo bridge logic.
- Body-only performance is roughly `0.068x` to `0.070x` real time on the validated WSL path.
- Adding realistic vision drops the representative workload to roughly `0.000883x` real time.
- The full realistic-vision closed loop remains in the same range as the vision-only workload, which matches the profile evidence that FlyVis dominates runtime.
- On the host, the Torch whole-brain backend runs slightly faster on `cuda:1` than on `cuda:0` for the tested 0.1 s workload.
- `Brian2` CPU is a valid secondary backend for comparison, but it is much slower than the Torch GPU path and is not the production choice.
