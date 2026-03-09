# Performance Tuning

## Measurement Basis

- Full-stack profile: `outputs/profiling/fullstack_flygym_0p02.txt`
- Host GPU probe: `outputs/profiling/torch_device_probe.json`
- Benchmark CSVs: `outputs/benchmarks/*.csv`

## Current Findings

1. The full realistic-vision stack is dominated by FlyGym plus FlyVis runtime cost.
2. The `0.02 s` profile spent `44.97 s` total wall time.
3. The top cumulative hotspots in that profile were:
   - `src/body/flygym_runtime.py:step`: `23.87 s`
   - `flygym.simulation.step`: `23.55 s`
   - `flygym.examples.vision.realistic_vision._get_visual_nn_activities`: `23.27 s`
   - built-in `time.sleep`: `19.85 s`
   - `src/body/flygym_runtime.py:reset`: `8.98 s`
4. The in-repo bridge logic is not the main bottleneck.
5. For brain-only Torch benchmarking on the host, `cuda:1` was slightly faster than `cuda:0` for the tested workload.

## Best Current Configuration

- Brain-only Torch benchmark: host Python, `cuda:1` if available
- Production body plus vision plus closed loop: WSL `flysim-full`, `MUJOCO_GL=egl`, `force_cpu_vision: true`
- Benchmark and demo cadence: `body_timestep_s = 0.0001`, `control_interval_s = 0.002`, `video_stride = 5`

## Optimization Attempts Kept

- Cached weight matrices under `outputs/cache/`
- Separate `Brian2` env to avoid dependency churn in the production stack
- CPU vision fallback in WSL to keep FlyVis stable on this hardware with current public wheels

## Remaining Practical Optimizations

1. Rerun the WSL production path once a public PyTorch wheel supports RTX 5060 Ti `sm_120`.
2. Investigate whether FlyGym camera playback or render throttling can remove the `time.sleep` hotspot without breaking artifact capture.
3. Split benchmark mode from artifact-heavy demo mode more aggressively if a no-video performance-only path is needed.
4. Reuse initialized realistic-vision state across sweep runs when exact reset parity is not required.
