# Progress Log



Ground truth source: `AGENTS.MD`



## 2026-03-08 - Phase 0 scouting and scaffold


1. What I attempted

- Read `AGENTS.MD` and extracted the required phase order, artifact list, and task-tracking rules.

- Inspected host and WSL capabilities.

- Verified public repo availability and cloned / checked out the candidate repos for the brain and body stacks.

- Inspected README, environment, benchmark, and example files to determine what already exists versus what must be built here.



2. What succeeded

- Confirmed WSL2 is present with `Ubuntu-24.04`.

- Confirmed dual RTX 5060 Ti GPUs are visible on the host and inside WSL.

- Cloned `eonsystemspbc/fly-brain` and `NeLy-EPFL/flygym`.

- Recovered a partial `philshiu/Drosophila_brain_model` clone by fetching and checking out `FETCH_HEAD`.

- Verified that `fly-brain` contains ready benchmark runners for Brian2 CPU, Brian2CUDA, PyTorch, and NEST GPU, but not an online body bridge.

- Verified that `flygym` contains realistic vision and closed-loop embodied controllers, but not a whole-brain bridge to the Shiu/Eon model.

- Identified public neuron IDs in the notebook artifacts for locomotor descending neurons (`P9`, `DNa01`, `DNa02`, `MDN`) and sensory proxy pools (`LC4`, `JON`).



3. What failed

- The initial clone of `external/Drosophila_brain_model` did not finish checkout cleanly; only `.git` was present.

- Resolved by running `git -C external/Drosophila_brain_model fetch --depth 1 origin main` followed by `git checkout FETCH_HEAD`.

- No full production environment has been provisioned yet, so FlyGym realistic-vision execution is not yet validated on this machine.



4. Evidence paths

- `external/fly-brain`

- `external/Drosophila_brain_model`

- `external/flygym`

- `docs/architecture_scout.md`

- `docs/dependency_matrix.md`

- `docs/repo_gap_analysis.md`



5. Next actions
- Implement bootstrap scripts and a split-environment strategy that keeps Brian2/Brian2CUDA benchmarks separate from the modern FlyGym full-stack runtime.
- Build the Torch whole-brain online backend and the mock/FlyGym body adapters.
- Write tests first for the bridge logic and a deterministic smoke closed loop.

## 2026-03-08 - Bridge, tests, and first runnable artifacts

1. What I attempted
- Implemented the in-repo bridge/runtime stack under `src/`.
- Added WSL/bootstrap/check scripts and environment requirement files.
- Wrote mock-path smoke/unit tests and standalone benchmark scripts.
- Ran the mock-path tests and both mock and real-Torch benchmark/demo commands.

2. What succeeded
- Added a persistent Torch whole-brain backend in `src/brain/pytorch_backend.py`.
- Added mock and FlyGym body adapters in `src/body/`.
- Added realistic-vision feature extraction plus sensory encoder and motor decoder.
- Added the closed-loop scheduler in `src/runtime/closed_loop.py`.
- Test suite passed:
  - `tests/test_imports.py`
  - `tests/test_bridge_unit.py`
  - `tests/test_closed_loop_smoke.py`
  - `tests/test_realistic_vision_path.py`
  - `tests/test_benchmark_output_format.py`
  - `tests/test_artifact_generation.py`
- Produced benchmark CSVs and plots:
  - `outputs/benchmarks/brain_benchmarks.csv`
  - `outputs/benchmarks/body_benchmarks.csv`
  - `outputs/benchmarks/vision_benchmarks.csv`
  - `outputs/benchmarks/fullstack_benchmarks.csv`
- Produced runnable mock demo artifacts including video:
  - `outputs/demos/mock-demo-20260308-110632/demo.mp4`
  - `outputs/demos/mock-demo-20260308-110632/run.jsonl`
  - `outputs/demos/mock-demo-20260308-110632/metrics.csv`

3. What failed
- I have not yet executed the real FlyGym realistic-vision runtime on this machine.
- I have not yet provisioned the separate Brian2/Brian2CUDA benchmark environment.
- I started an exploratory WSL `flygym[examples]` install in a throwaway venv, but stopped it before completion once it reached the very large Torch wheel download; there is still no validated WSL FlyGym result to report.
- Therefore the true production body/vision/full-stack parity gate remains open.

4. Evidence paths
- `src/brain/pytorch_backend.py`
- `src/body/mock_body.py`
- `src/body/flygym_runtime.py`
- `src/bridge/encoder.py`
- `src/bridge/decoder.py`
- `src/runtime/closed_loop.py`
- `outputs/benchmarks/brain_benchmarks.csv`
- `outputs/benchmarks/fullstack_benchmarks.csv`
- `outputs/demos/mock-demo-20260308-110632/summary.json`

5. Next actions
- Provision the WSL `flysim-full` and `flysim-brain-brian2` environments via the new scripts.
- Validate `scripts/check_cuda.sh` and `scripts/check_mujoco.sh` inside WSL.
- Run the real FlyGym realistic-vision path and capture the first non-mock demo artifacts.
- Add at least one secondary neural backend benchmark if the WSL env comes up cleanly.

## 2026-03-08 - WSL provisioning, real FlyGym validation, and second neural backend

1. What I attempted
- Normalized the shell scripts under `scripts/*.sh` to LF line endings after the first WSL bootstrap failed on `set -euo pipefail`.
- Ran `scripts/bootstrap_wsl.sh` and `scripts/bootstrap_env.sh` inside WSL from `/mnt/g/flysim`.
- Validated `scripts/check_cuda.sh` and `scripts/check_mujoco.sh` in the WSL `flysim-full` environment.
- Fixed missing public-environment glue for the realistic-vision stack:
  - added `cachetools` to `environment/requirements-full.txt`
  - added `flyvis download-pretrained` to `scripts/bootstrap_env.sh`
  - added a CPU-vision fallback flag in `src/body/flygym_runtime.py`
  - fixed a double-close bug in `src/body/flygym_runtime.py`
- Extended the benchmark scripts so they can exercise real WSL workloads:
  - `benchmarks/run_body_benchmarks.py --mode flygym`
  - `benchmarks/run_vision_benchmarks.py --mode flygym`
  - `benchmarks/run_brain_benchmarks.py --backend brian2cpu`
- Patched the checked-out public `external/fly-brain` copy for current Brian2 compatibility:
  - `external/fly-brain/code/run_brian2_cuda.py`
  - `external/fly-brain/code/benchmark.py`
- Ran real WSL production commands:
  - `python benchmarks/run_body_benchmarks.py --config configs/flygym_realistic_vision.yaml --mode flygym --durations 0.02 0.05`
  - `python benchmarks/run_vision_benchmarks.py --config configs/flygym_realistic_vision.yaml --mode flygym --duration 0.02`
  - `python benchmarks/run_fullstack_with_realistic_vision.py --config configs/flygym_realistic_vision.yaml --mode flygym --duration 0.02`
  - `python benchmarks/run_fullstack_with_realistic_vision.py --config configs/flygym_realistic_vision.yaml --mode flygym --duration 0.05`
  - `python benchmarks/run_brain_benchmarks.py --config configs/default.yaml --backend brian2cpu --durations 0.1`

2. What succeeded
- WSL bootstrap now completes end-to-end:
  - `scripts/bootstrap_wsl.sh`
  - `scripts/bootstrap_env.sh`
- The WSL full-stack environment now imports and runs:
  - `mujoco`
  - `dm_control`
  - `flygym`
  - FlyVis pretrained model download
- Real FlyGym realistic-vision runtime now resets, steps, and closes locally in WSL.
- Real FlyGym benchmark evidence now exists:
  - body benchmark: `outputs/benchmarks/body_benchmarks.csv`
  - realistic-vision benchmark: `outputs/benchmarks/vision_benchmarks.csv`
  - full-stack realistic-vision benchmark: `outputs/benchmarks/fullstack_benchmarks.csv`
- Real closed-loop demo artifacts now exist:
  - `outputs/demos/flygym-demo-20260308-115338.mp4`
  - `outputs/logs/flygym-demo-20260308-115338.jsonl`
  - `outputs/metrics/flygym-demo-20260308-115338.csv`
  - `outputs/demos/flygym-demo-20260308-115954.mp4`
  - `outputs/logs/flygym-demo-20260308-115954.jsonl`
  - `outputs/metrics/flygym-demo-20260308-115954.csv`
- The second neural backend requirement is now satisfied with a real Brian2 CPU benchmark in WSL.
- `outputs/benchmarks/brain_benchmarks.csv` now carries both:
  - Torch on `cuda:0`
  - Brian2 CPU on WSL

3. What failed
- The public WSL PyTorch `cu126` wheel in `flysim-full` does not support the local RTX 5060 Ti `sm_120` GPUs. `torch.cuda.is_available()` is true, but the wheel warns that the GPU architecture is unsupported.
- Because of that public wheel limitation, the realistic-vision WSL runs currently need a CPU-only visibility fallback (`force_cpu_vision: true` / `CUDA_VISIBLE_DEVICES=''`) to keep FlyVis stable.
- The first Brian2 env attempt failed because:
  - `brian2cuda==1.0a7` conflicted with `brian2==2.5.1`
  - newer `setuptools` in the env did not expose `pkg_resources`
  - the checked-out `external/fly-brain` Brian2 code needed a local patch for the current `CPPStandaloneDevice.run(...)` signature
- I have not yet completed the “longest stable” real FlyGym parity run or updated the final parity report / README with these new measurements.

4. Evidence paths
- `scripts/bootstrap_wsl.sh`
- `scripts/bootstrap_env.sh`
- `environment/requirements-full.txt`
- `environment/requirements-brain-brian2.txt`
- `configs/flygym_realistic_vision.yaml`
- `src/body/flygym_runtime.py`
- `benchmarks/run_body_benchmarks.py`
- `benchmarks/run_vision_benchmarks.py`
- `benchmarks/run_brain_benchmarks.py`
- `external/fly-brain/code/run_brian2_cuda.py`
- `external/fly-brain/code/benchmark.py`
- `outputs/benchmarks/brain_benchmarks.csv`
- `outputs/benchmarks/body_benchmarks.csv`
- `outputs/benchmarks/vision_benchmarks.csv`
- `outputs/benchmarks/fullstack_benchmarks.csv`
- `outputs/demos/flygym-demo-20260308-115338/summary.json`
- `outputs/demos/flygym-demo-20260308-115954/summary.json`

5. Next actions
- Run the longest stable real FlyGym realistic-vision demo that is still practical on this machine and save the resulting artifacts.
- Update `docs/install_report.md`, `docs/benchmark_summary.md`, `docs/perf_tuning.md`, `docs/multi_gpu_evaluation.md`, `ASSUMPTIONS_AND_GAPS.md`, and `REPRO_PARITY_REPORT.md` with the WSL findings.
- Harden `README.md` so the documented quick start matches the now-validated WSL workflow exactly.

## 2026-03-08 - Longest stable demo, profiling, and acceptance hardening

1. What I attempted
- Extended `benchmarks/run_fullstack_with_realistic_vision.py` so one command can sweep multiple durations and emit `outputs/plots/fullstack_benchmarks.png`.
- Added `benchmarks/profile_fullstack.py` and `benchmarks/summarize_demo_runs.py` to make profiling and parity summarization reproducible.
- Ran a real WSL realistic-vision benchmark and demo sweep for `0.02 s`, `0.05 s`, and `0.1 s` simulated durations.
- Profiled the real WSL full stack for `0.02 s` simulated time.
- Probed the host Torch whole-brain backend on both `cuda:0` and `cuda:1`.
- Patched the benchmark regression tests so they write into temporary paths instead of overwriting production benchmark artifacts.
- Updated the final docs and trackers required by `AGENTS.MD`.

2. What succeeded
- Real short, medium, and longest-stable FlyGym realistic-vision demos now exist:
  - `outputs/demos/flygym-demo-20260308-121237.mp4`
  - `outputs/demos/flygym-demo-20260308-121318.mp4`
  - `outputs/demos/flygym-demo-20260308-121432.mp4`
- `outputs/benchmarks/fullstack_benchmarks.csv` now contains three real production rows and `outputs/plots/fullstack_benchmarks.png` now exists.
- `outputs/metrics/parity_runs.csv` now summarizes the three real production demos.
- Profiling artifacts now exist:
  - `outputs/profiling/fullstack_flygym_0p02.prof`
  - `outputs/profiling/fullstack_flygym_0p02.txt`
  - `outputs/profiling/torch_device_probe.json`
- Screenshot artifacts now exist:
  - `outputs/screenshots/flygym-demo-20260308-121237.png`
  - `outputs/screenshots/flygym-demo-20260308-121318.png`
  - `outputs/screenshots/flygym-demo-20260308-121432.png`
- Production benchmark artifacts were restored after isolating the tests:
  - `outputs/benchmarks/body_benchmarks.csv`
  - `outputs/benchmarks/fullstack_benchmarks.csv`
  - `outputs/plots/body_benchmarks.png`
  - `outputs/plots/fullstack_benchmarks.png`
- The profile shows the production bottleneck is FlyGym plus FlyVis runtime, especially realistic-vision stepping and a large `time.sleep` component, not the in-repo bridge.
- The host Torch probe showed `cuda:1` slightly faster than `cuda:0` for the tested brain-only workload.
- Host smoke and regression tests now pass with the updated benchmark script shape: `7 passed`.
- `README.md`, `docs/install_report.md`, `docs/benchmark_summary.md`, `docs/perf_tuning.md`, `docs/multi_gpu_evaluation.md`, `docs/realistic_vision_integration.md`, `ASSUMPTIONS_AND_GAPS.md`, `REPRO_PARITY_REPORT.md`, and `TASKS.md` now match the validated workflow and current evidence.

3. What failed
- The public WSL PyTorch `cu126` wheel still does not support RTX 5060 Ti `sm_120`, so the realistic-vision production path remains CPU-only in WSL.
- Because of that wheel limitation, a meaningful end-to-end dual-GPU production split is still blocked.
- The final parity verdict remains `partial` rather than `pass` because the exact private Eon glue and telemetry are not public.

4. Evidence paths
- `outputs/benchmarks/fullstack_benchmarks.csv`
- `outputs/plots/fullstack_benchmarks.png`
- `outputs/metrics/parity_runs.csv`
- `outputs/profiling/fullstack_flygym_0p02.txt`
- `outputs/profiling/torch_device_probe.json`
- `outputs/screenshots/flygym-demo-20260308-121432.png`
- `outputs/demos/flygym-demo-20260308-121432/summary.json`
- `REPRO_PARITY_REPORT.md`
- `README.md`
- `TASKS.md`

5. Next actions
- Mandatory repo work is complete for the public-equivalent acceptance gate in `AGENTS.MD`.
- External follow-up once public support exists: rerun the WSL realistic-vision stack with GPU FlyVis enabled and repeat the same benchmark and parity scripts.
- Secondary follow-up: inspect the `time.sleep` hotspot in the FlyGym plus FlyVis path if higher local throughput becomes a priority.

## 2026-03-08 - User-requested 30 second real full-stack demo launch

1. What I attempted
- Launched a real `30 s` simulated-duration FlyGym realistic-vision full-stack run from WSL using the validated production config.
- Isolated the request outputs under `outputs/requested_30s/` so existing benchmark artifacts remain unchanged.

2. What succeeded
- The run was started successfully and is currently writing artifacts under:
  - `outputs/requested_30s/run-20260308-130111.log`
  - `outputs/requested_30s/flygym-demo-20260308-130114/`
- The live run directory already exists and has started writing `run.jsonl`.

3. What failed
- The final video artifact is not ready yet.
- Based on the current measured real-time factor for the validated full-stack path (`~0.00078x`), a true `30 s` simulated run is expected to take about `10.7 h` wall time on this machine with the present public WSL stack.

4. Evidence paths
- `outputs/requested_30s/run-20260308-130111.log`
- `outputs/requested_30s/flygym-demo-20260308-130114/run.jsonl`
- `TASKS.md`

5. Next actions
- Let the requested long run continue until completion.
- Once complete, inspect `outputs/requested_30s/demos/` for the video artifact and summarize the final paths.
- Separately, provide the requested concrete near-term implementation plan for richer-than-two-drive control.
- Wrote the requested concrete near-term multidrive implementation plan to `docs/near_term_multidrive_plan.md` and logged it in `TASKS.md` as `T020`.
- Wrote the requested vision fast-path plan to `docs/vision_perf_plan.md` and logged it in `TASKS.md` as `T021`.

## 2026-03-08 - Vision fast-path implementation slice 1

1. What I attempted
- Started implementing the first concrete tasks from `docs/vision_perf_plan.md`.
- Added an in-repo array-based realistic-vision extraction path so the bridge can consume either:
  - legacy `LayerActivity`-expanded mappings, or
  - fast raw-array / precomputed-feature payloads.
- Added a repo-local `FastRealisticVisionFly` wrapper and wired a config-controlled `runtime.vision_payload_mode` through the mock runtime, FlyGym runtime, bridge, and benchmark CLIs.
- Added local tests and mock-path benchmarks for the new fast payload mode.

2. What succeeded
- Added cached index extraction primitives:
  - `src/vision/feature_extractor.py`
  - `src/vision/flyvis_fast_path.py`
- Added the repo-local FlyGym wrapper:
  - `src/body/fast_realistic_vision_fly.py`
- Extended body observations and runtimes so fast payloads can flow without rebuilding per-cell dictionaries:
  - `src/body/interfaces.py`
  - `src/body/mock_body.py`
  - `src/body/flygym_runtime.py`
- Updated the bridge and closed-loop runner to prefer fast payloads when available:
  - `src/bridge/controller.py`
  - `src/runtime/closed_loop.py`
- Added benchmark toggles for `legacy|fast` vision payload modes:
  - `benchmarks/run_vision_benchmarks.py`
  - `benchmarks/run_fullstack_with_realistic_vision.py`
- Added local validation coverage:
  - `tests/test_imports.py`
  - `tests/test_realistic_vision_path.py`
  - `tests/test_closed_loop_smoke.py`
- Host validation now passes:
  - `python -m pytest tests/test_imports.py tests/test_bridge_unit.py tests/test_closed_loop_smoke.py tests/test_realistic_vision_path.py tests/test_benchmark_output_format.py tests/test_artifact_generation.py`
  - result: `10 passed`
- Mock fast-path benchmark evidence now exists:
  - `tests/.tmp/vision_fast.csv`
  - `tests/.tmp/fastvision-fullstack.csv`

3. What failed
- I temporarily overwrote `outputs/benchmarks/vision_benchmarks.csv` and `outputs/plots/vision_benchmarks.png` with a host-side mock fast-path benchmark while adding the new CLI toggles.
- I restored the production artifact paths immediately by rerunning the real WSL legacy vision benchmark:
  - `outputs/benchmarks/vision_benchmarks.csv`
  - `outputs/plots/vision_benchmarks.png`
- I have not yet validated the new `vision_payload_mode=fast` path against the real WSL FlyGym stack, so I cannot yet claim that the `LayerActivity` / `datamate` hotspot is removed in the real production profile.

4. Evidence paths
- `docs/vision_perf_plan.md`
- `src/vision/feature_extractor.py`
- `src/vision/flyvis_fast_path.py`
- `src/body/fast_realistic_vision_fly.py`
- `src/body/mock_body.py`
- `src/body/flygym_runtime.py`
- `src/bridge/controller.py`
- `src/runtime/closed_loop.py`
- `benchmarks/run_vision_benchmarks.py`
- `benchmarks/run_fullstack_with_realistic_vision.py`
- `tests/test_realistic_vision_path.py`
- `tests/test_closed_loop_smoke.py`
- `tests/.tmp/vision_fast.csv`
- `tests/.tmp/fastvision-fullstack.csv`
- `outputs/benchmarks/vision_benchmarks.csv`

5. Next actions
- Run the real WSL FlyGym stack with `runtime.vision_payload_mode=fast`.
- Re-profile the realistic-vision path and compare the hotspot table against `outputs/profiling/fullstack_flygym_0p02.txt`.
- If the fast path works in WSL, add side-by-side legacy vs fast benchmark rows and then update `docs/perf_tuning.md`.

## 2026-03-08 - Cancelled requested 30 second run and validated real fast-vision full stack

1. What I attempted
- Killed the still-running user-requested `30 s` WSL full-stack job.
- Ran a real WSL full-stack FlyGym realistic-vision benchmark using the new `vision_payload_mode=fast` path.

2. What succeeded
- The long-running `30 s` job is no longer running.
- The partial run directory and log remain available for inspection:
  - `outputs/requested_30s/run-20260308-130111.log`
  - `outputs/requested_30s/flygym-demo-20260308-130114/run.jsonl`
- The first real WSL fast-vision full-stack run completed successfully and produced artifacts:
  - `outputs/benchmarks/fullstack_fastvision_test.csv`
  - `outputs/plots/fullstack_fastvision_test.png`
  - `outputs/fastvision_test/demos/flygym-demo-20260308-134523.mp4`
  - `outputs/fastvision_test/logs/flygym-demo-20260308-134523.jsonl`
  - `outputs/fastvision_test/metrics/flygym-demo-20260308-134523.csv`
- The production run log confirms the real fast payload mode was active:
  - `outputs/fastvision_test/logs/flygym-demo-20260308-134523.jsonl`
- The initial measured fast-path full-stack row is:
  - `wall_seconds = 5.928991241999938`
  - `sim_seconds = 0.018000000000000002`
  - `real_time_factor = 0.0030359295983591857`
- Relative to the earlier real legacy full-stack result for the same short-run class (`~0.00078x`), this first fast-path validation is materially faster.

3. What failed
- The user-requested `30 s` artifact was intentionally not completed because the run was terminated at user request.
- I have not yet rerun the dedicated vision-only benchmark in WSL with `vision_payload_mode=fast`, nor captured an updated profiler comparison, so the `LayerActivity` / `datamate` hotspot removal is not fully proven yet.

4. Evidence paths
- `outputs/requested_30s/run-20260308-130111.log`
- `outputs/requested_30s/flygym-demo-20260308-130114/run.jsonl`
- `outputs/benchmarks/fullstack_fastvision_test.csv`
- `outputs/plots/fullstack_fastvision_test.png`
- `outputs/fastvision_test/demos/flygym-demo-20260308-134523.mp4`
- `outputs/fastvision_test/logs/flygym-demo-20260308-134523.jsonl`
- `outputs/fastvision_test/metrics/flygym-demo-20260308-134523.csv`
- `TASKS.md`

5. Next actions
- Run the real WSL vision-only benchmark with `vision_payload_mode=fast`.
- Re-profile the real full stack with the fast payload mode enabled.
- Update `docs/perf_tuning.md` with the before/after results if the profiler confirms the intended hotspot shift.

## 2026-03-08 - Exact equivalence proof for fast vision on the control path

1. What I attempted
- Tightened the local vision tests from tolerance-based checks to exact equality checks where the algebra should match exactly.
- Wrote a dedicated proof script, `scripts/prove_vision_fast_equivalence.py`, to compare:
  - legacy `LayerActivity` indexing,
  - fast cached indexing,
  - extracted vision features,
  - sensor pool rates,
  - sensor metadata,
  - downstream motor rates,
  - final decoded motor command,
  on the same exact `nn_activities_arr`.
- Ran that proof script inside the real WSL `flysim-full` environment against the installed FlyVis connectome and real production samples.

2. What succeeded
- Local exact-equality tests now pass:
  - `python -m pytest tests/test_realistic_vision_path.py tests/test_bridge_unit.py`
  - result: `5 passed`
- The WSL proof script completed and wrote:
  - `outputs/metrics/vision_fast_equivalence.json`
- The proof artifact shows:
  - `all_index_arrays_exact = true`
  - `all_samples_exact_feature_match = true`
  - `all_samples_exact_sensor_pool_match = true`
  - `all_samples_exact_sensor_metadata_match = true`
  - `all_samples_exact_motor_rate_match = true`
  - `all_samples_exact_command_match = true`
  - `max_feature_abs_diff = 0.0`
  - `max_command_abs_diff = 0.0`
- Checked real production samples:
  - `reset`
  - `step_1`
  - `step_2`
- Wrote a file-backed proof summary:
  - `docs/vision_fast_equivalence.md`

3. What failed
- I cannot honestly claim byte-for-byte equivalence of every runtime payload, because fast mode intentionally does not emit the legacy `info["nn_activities"]` `LayerActivity` object.
- What is proven exactly equivalent is the control-relevant path used by this repo: same input array -> same extracted features -> same bridge outputs -> same decoded command.

4. Evidence paths
- `scripts/prove_vision_fast_equivalence.py`
- `outputs/metrics/vision_fast_equivalence.json`
- `docs/vision_fast_equivalence.md`
- `tests/test_realistic_vision_path.py`
- `TASKS.md`

5. Next actions
- Finish `T024`: run side-by-side real WSL legacy vs fast vision-only and full-stack benchmarks.
- Re-profile the real fast path and update `docs/perf_tuning.md` with the hotspot comparison.

## 2026-03-08 - User-requested 5 second real fast-vision demo launch

1. What I attempted
- Launched a real `5 s` simulated-duration FlyGym realistic-vision full-stack run using the new fast vision payload mode.
- Isolated the request outputs under `outputs/requested_5s_fastvision/` so the existing benchmark artifacts remain unchanged.

2. What succeeded
- The run started successfully in WSL.
- Live evidence now exists at:
  - `outputs/requested_5s_fastvision/run-20260308-141141.log`
  - `outputs/requested_5s_fastvision/demos/flygym-demo-20260308-141145/run.jsonl`
- The WSL process is active and the run directory has been created.

3. What failed
- The final demo artifact is not ready yet.
- Based on the current measured fast full-stack real-time factor (`~0.00304x` from `outputs/benchmarks/fullstack_fastvision_test.csv`), a true `5 s` simulated run is expected to take about `27.4 min` wall time on this machine.

4. Evidence paths
- `outputs/requested_5s_fastvision/run-20260308-141141.log`
- `outputs/requested_5s_fastvision/demos/flygym-demo-20260308-141145/run.jsonl`
- `outputs/benchmarks/fullstack_fastvision_test.csv`
- `TASKS.md`

5. Next actions
- Let the requested `5 s` fast-vision run continue until completion.
- Once complete, inspect `outputs/requested_5s_fastvision/demos/`, `outputs/requested_5s_fastvision/logs/`, and `outputs/requested_5s_fastvision/metrics/` for the final artifact paths.

## 2026-03-08 - 5 second fast-vision demo dissection

1. What I attempted
- Inspected the completed `5 s` fast-vision demo artifacts after the user reported that one fly walked off screen and the other appeared to circle consistently.
- Analyzed the run log, metrics, trajectory plot, command plot, decoder code, and the FlyGym arena implementation.

2. What succeeded
- Confirmed the run completed and produced:
  - `outputs/requested_5s_fastvision/demos/flygym-demo-20260308-141145.mp4`
  - `outputs/requested_5s_fastvision/logs/flygym-demo-20260308-141145.jsonl`
  - `outputs/requested_5s_fastvision/metrics/flygym-demo-20260308-141145.csv`
- Confirmed the circling second fly is not connectome-controlled behavior; it is the arena's scripted leading fly in `external/flygym/flygym/examples/vision/arena.py`, where `MovingFlyArena` advances the stimulus fly on a fixed-radius circular path.
- Confirmed the controlled fly largely runs on the decoder's hard-coded idle drive:
  - `src/bridge/decoder.py` sets `idle_drive = 0.7`
  - in the `5 s` run, the motor readout was exactly all-zero on `2257 / 2500` cycles
  - on those silent cycles, the decoder still emits `left_drive = right_drive = 0.7`
- Confirmed the control bias is strongly one-sided when activity does appear:
  - `turn_right_hz` was zero on all `2500` cycles
  - `forward_right_hz` was zero on all `2500` cycles
  - only left-side readout groups fired, producing repeated `left_drive > right_drive` events
- Confirmed the logged visual asymmetry is very small and almost uncorrelated with the drive asymmetry:
  - mean absolute `vision_balance` was about `0.0081`
  - correlation between `vision_balance` and `(left_drive - right_drive)` was about `0.0045`
- The trajectory plot shows the controlled fly does not perform a stable pursuit behavior; it drifts on a long right-curving path and exits the fixed camera framing:
  - `outputs/requested_5s_fastvision/demos/flygym-demo-20260308-141145/trajectory.png`

3. What failed
- The `5 s` demo does not show convincing visually guided pursuit.
- The controlled behavior is still dominated by engineering fallback dynamics:
  - baseline locomotion from `idle_drive`
  - sparse, left-only neural readout bursts
- This means the current fast-vision run is useful as a performance and plumbing validation, but not as a strong parity demo.

4. Evidence paths
- `outputs/requested_5s_fastvision/logs/flygym-demo-20260308-141145.jsonl`
- `outputs/requested_5s_fastvision/metrics/flygym-demo-20260308-141145.csv`
- `outputs/requested_5s_fastvision/demos/flygym-demo-20260308-141145/trajectory.png`
- `outputs/requested_5s_fastvision/demos/flygym-demo-20260308-141145/commands.png`
- `src/bridge/decoder.py`
- `external/flygym/flygym/examples/vision/arena.py`
- `TASKS.md`

5. Next actions
- Remove or gate the decoder idle drive for diagnostic runs so silent-brain behavior is visible immediately.
- Audit the public left/right motor readout IDs and the current sensor-pool mapping, because the observed output is one-sided.
- Add a pursuit-quality metric comparing controlled-fly trajectory to the arena fly trajectory before claiming anything close to demo parity.

## 2026-03-08 - Strict brain-only motor enforcement and public-input cleanup

1. What I attempted
- Re-read `AGENTS.MD`, `TASKS.md`, and the current `PROGRESS_LOG.md` before changing the production path.
- Removed the in-repo motor fallback so zero monitored brain output no longer becomes locomotion by default.
- Audited the public sensory anchor mapping and removed the fabricated midpoint left/right split of the bilateral public `LC4` and `JON` ID lists.
- Added a repo-local realistic-vision wrapper to suppress upstream `HybridTurningFly` rule-based locomotion when the decoded descending drive is exactly zero.
- Re-ran host tests and short real WSL strict-production diagnostics for both `fast` and `legacy` realistic-vision payload modes.

2. What succeeded
- The production decoder is now brain-only in the narrow sense requested:
  - `src/bridge/decoder.py` now defaults to `idle_drive = 0.0` and `min_drive = 0.0`
  - `src/bridge/encoder.py` now defaults to zero sensory baselines
  - `src/brain/mock_backend.py` now also returns zero readout for zero sensor input so the test path matches the stricter production semantics
- The fabricated public sensory hemispheres are gone:
  - `src/brain/public_ids.py` now defines bilateral public input pools and a `collapse_sensor_pool_rates(...)` helper
  - `src/brain/pytorch_backend.py` now drives the public whole-brain core through those bilateral pools instead of arbitrary list-halves
- The upstream body-side hidden locomotion is suppressed when decoded drive is zero:
  - `src/body/brain_only_realistic_vision_fly.py`
  - `src/body/fast_realistic_vision_fly.py`
  - `src/body/flygym_runtime.py`
- Host validation still passes:
  - `python -m pytest tests/test_bridge_unit.py tests/test_closed_loop_smoke.py tests/test_realistic_vision_path.py tests/test_benchmark_output_format.py tests/test_artifact_generation.py tests/test_imports.py`
  - result: `13 passed`
- Real WSL strict-production diagnostics now show that the decoder and wrapper changes are actually taking effect:
  - fast path benchmark: `outputs/benchmarks/fullstack_brainonly_fastvision_test_v2.csv`
  - legacy path benchmark: `outputs/benchmarks/fullstack_brainonly_legacyvision_test.csv`
  - in both runs:
    - `nonzero_commands = 0`
    - `nonzero_motor_cycles = 0`
    - remaining path length is only `0.013563274021824296` over `0.018 s`

3. What failed
- The strict production path currently reveals a harder truth: with the decoder floor removed and the fake sensory split removed, the public whole-brain backend produced no monitored motor output in the short real WSL diagnostics.
- There is still small residual motion even with zero decoded command. After the new wrapper, this is down to passive body settling rather than controller locomotion, but it is not literally zero movement.
- So the stricter default production path is now more faithful, but it is behaviorally weaker than the earlier demo artifacts that relied on now-removed scaffolding.

4. Evidence paths
- `src/bridge/decoder.py`
- `src/bridge/encoder.py`
- `src/brain/public_ids.py`
- `src/brain/pytorch_backend.py`
- `src/body/brain_only_realistic_vision_fly.py`
- `src/body/fast_realistic_vision_fly.py`
- `src/body/flygym_runtime.py`
- `tests/test_bridge_unit.py`
- `outputs/benchmarks/fullstack_brainonly_fastvision_test_v2.csv`
- `outputs/brain_only_fastvision_test_v2/logs/flygym-demo-20260308-150052.jsonl`
- `outputs/benchmarks/fullstack_brainonly_legacyvision_test.csv`
- `outputs/brain_only_legacyvision_test/logs/flygym-demo-20260308-150149.jsonl`
- `REPRO_PARITY_REPORT.md`

5. Next actions
- Keep the stricter brain-only defaults in place; do not restore the removed fallback behaviors.
- Treat the absence of motor output as the current production blocker and debug it explicitly rather than hiding it with decoder or body-controller scaffolding.
- If higher fidelity remains the goal, the next work should focus on whether the current public input mapping and monitored descending-neuron set are sufficient to elicit motor output under the public whole-brain model.

## 2026-03-08 - Strict motor-path audit and public notebook comparison

1. What I attempted
- Audited the strict production blocker after the decoder/body-side scaffolding was removed.
- Compared the observed strict-production public input rates against standalone whole-brain backend sweeps.
- Added a reproducible audit script that measures:
  - observed bilateral public input statistics from a strict production log
  - direct graph connectivity from the public `LC4` / `JON` anchor pools into the monitored locomotor DN groups
  - hop reachability from those sensory pools to the monitored DN groups
  - positive-control cases using direct public `P9` stimulation
- Re-read the checked public notebook in `external/fly-brain/code/paper-phil-drosophila/example.ipynb` to verify how `P9`, `LC4`, and `JON` are actually used in the public examples.

2. What succeeded
- Added the reproducible audit entrypoint:
  - `scripts/audit_motor_path.py`
- Wrote the audit artifacts:
  - `outputs/metrics/motor_path_audit.json`
  - `outputs/metrics/motor_path_audit_sweeps.csv`
- Wrote the supporting summary doc:
  - `docs/motor_path_audit.md`
- Confirmed the strict short production input levels are low relative to the public experiment context:
  - observed bilateral vision input is about `77.7 Hz`
  - observed bilateral mechanosensory input averages about `14.7 Hz`
- Confirmed those observed bilateral inputs produce:
  - zero monitored motor output over `20 ms`
  - zero monitored motor output over `100 ms`
  - only weak turning-biased output after `1000 ms`
- Confirmed the whole-brain backend and monitored readout path are not dead:
  - direct public `P9` stimulation at `100 Hz` for `1000 ms` produces about `33.0 Hz` / `32.5 Hz` forward readout with first forward spikes at about `10-12 ms`
- Confirmed the current public sensory pools do not connect directly to the monitored DN groups:
  - `LC4` to monitored DNs: `0` direct edges
  - `JON` to monitored DNs: `0` direct edges
  - both reach the monitored DN groups by hop `2`
- Confirmed the checked public notebook uses `P9` as the explicit forward-walking baseline before adding `LC4` or `JON` co-stimulation.

3. What failed
- The audit did not recover a new faithful locomotor controller.
- The strict sensory-only production path remains behaviorally blocked: it is honest, but it still does not produce meaningful locomotor output from the current public bilateral sensory anchor mapping.
- The bilateral public sensory anchors still discard external left/right asymmetry before the whole-brain backend, so visually guided turning parity remains out of reach with the present public anchor set.

4. Evidence paths
- `scripts/audit_motor_path.py`
- `outputs/metrics/motor_path_audit.json`
- `outputs/metrics/motor_path_audit_sweeps.csv`
- `docs/motor_path_audit.md`
- `external/fly-brain/code/paper-phil-drosophila/example.ipynb`
- `README.md`
- `ASSUMPTIONS_AND_GAPS.md`
- `REPRO_PARITY_REPORT.md`

5. Next actions
- Keep the strict brain-only default and do not restore decoder/body-side fallback locomotion.
- If a more behaviorally active public-equivalent mode is desired, implement it as a clearly labeled brain-side experiment analogue rather than hidden decoder scaffolding.
- Search for truly lateralized public sensory anchors or additional public readout anchors before trying to claim visually guided turning behavior again.

## 2026-03-08 - Public P9 context mode and lateralized-anchor search

1. What I attempted
- Implemented the user-requested `public_p9_context` experiment mode so the repo can reproduce the public notebook's direct `P9` locomotor baseline without restoring decoder or body-side fallback behavior.
- Added runtime/config/CLI plumbing so this mode is explicit in config files and JSONL logs.
- Extended the mock-path tests to cover the new brain-side context injection.
- Ran a short real WSL fast-vision validation run using the new mode.
- Searched the checked public notebook artifacts for truly lateralized sensory anchors before attempting visual turning again.

2. What succeeded
- Added a new brain-side context injector:
  - `src/bridge/brain_context.py`
- Wired the mode through the bridge/runtime/backends:
  - `src/bridge/controller.py`
  - `src/brain/pytorch_backend.py`
  - `src/brain/mock_backend.py`
  - `src/runtime/closed_loop.py`
  - `benchmarks/run_fullstack_with_realistic_vision.py`
- Added an explicit real config:
  - `configs/flygym_realistic_vision_public_p9_context.yaml`
- Host validation passed:
  - `python -m pytest tests/test_imports.py tests/test_bridge_unit.py tests/test_closed_loop_smoke.py tests/test_realistic_vision_path.py tests/test_benchmark_output_format.py tests/test_artifact_generation.py`
  - result: `15 passed`
- Real WSL validation run completed:
  - benchmark CSV: `outputs/benchmarks/fullstack_public_p9_context_test.csv`
  - video: `outputs/public_p9_context_test/demos/flygym-demo-20260308-165839.mp4`
  - log: `outputs/public_p9_context_test/logs/flygym-demo-20260308-165839.jsonl`
  - metrics: `outputs/public_p9_context_test/metrics/flygym-demo-20260308-165839.csv`
- The real WSL validation log confirms the new mode is explicit and active:
  - `brain_context.mode = public_p9_context`
  - `P9_left = 100 Hz`
  - `P9_right = 100 Hz`
- The short real WSL run produced measurable brain-driven motion without decoder/body fallback restoration:
  - `real_time_factor = 0.003553746426609255`
  - `path_length = 0.15791582767030482`
  - `nonzero command cycles = 2 / 10`
  - `max_forward_left_hz = 249.99998474121094`
  - `max_forward_right_hz = 249.99998474121094`
- Added a reproducible public-anchor search:
  - `scripts/search_lateralized_public_anchors.py`
  - `outputs/metrics/lateralized_public_anchors.json`
  - `docs/lateralized_public_anchors.md`
- The checked public artifact search found:
  - `visual_lateralized_hits = 0`
  - `mechanosensory_lateralized_hits = 0`
  - `gustatory_lateralized_hits = 5`
  - no `LC4_left/right` or `JON_left/right`-style public anchors in the checked notebook artifacts

3. What failed
- The new `public_p9_context` mode is useful as a public experiment analogue, but it is not evidence that realistic vision alone is currently driving locomotion in the strict production path.
- The lateralized-anchor search did not recover a clean public left/right visual or mechanosensory sensory pool for turning, so visually guided turning parity remains blocked on the public-anchor side.

4. Evidence paths
- `src/bridge/brain_context.py`
- `configs/flygym_realistic_vision_public_p9_context.yaml`
- `docs/public_p9_context_mode.md`
- `outputs/benchmarks/fullstack_public_p9_context_test.csv`
- `outputs/public_p9_context_test/logs/flygym-demo-20260308-165839.jsonl`
- `outputs/public_p9_context_test/metrics/flygym-demo-20260308-165839.csv`
- `scripts/search_lateralized_public_anchors.py`
- `outputs/metrics/lateralized_public_anchors.json`
- `docs/lateralized_public_anchors.md`
- `README.md`
- `ASSUMPTIONS_AND_GAPS.md`
- `REPRO_PARITY_REPORT.md`

5. Next actions
- Keep `brain_context.mode: none` as the default faithful production mode.
- Use `public_p9_context` only when the experiment framing needs to match the public notebook's direct `P9` baseline explicitly.
- Do not claim honest public left/right visual steering input until a real public lateralized visual or mechanosensory anchor set is identified.

## 2026-03-08 - Inferred lateralized bridge probing kickoff

1. What I attempted
- Started the next fallback the user requested: probing the real visual model with crafted inputs to infer candidate left/right bridge channels.
- Re-inspected the current vision stack and the checked public FlyGym vision examples to decide whether to probe through:
  - the real FlyVis network directly, or
  - full embodied closed-loop runs
- Verified that the repo-local fast vision path already exposes the ingredients needed for a direct probe:
  - `nn_activities_arr`
  - connectome node types
  - retina / retina-mapper utilities

2. What succeeded
- Confirmed the technical path for a direct probe is available in the current code:
  - `src/body/fast_realistic_vision_fly.py`
  - `src/vision/feature_extractor.py`
  - `src/vision/flyvis_fast_path.py`
  - `external/flygym/flygym/examples/vision/vision_network.py`
- Confirmed the checked public FlyGym examples already use z-scored activity comparisons over tracked visual cell types for object following:
  - `external/flygym/flygym/examples/vision/follow_fly_closed_loop.py`
- Confirmed the checked public tutorial exposes the full per-eye activity tensor shape:
  - `external/flygym/doc/source/tutorials/advanced_vision.rst`
  - `all_cell_activities.shape == (num_timesteps, 2, 45669)`
- Created a new tracked task for this probing work:
  - `T035` in `TASKS.md`

3. What failed
- I have not yet completed the actual probing script or generated the inferred candidate artifact.
- A quick one-line WSL probe command failed because of quoting issues from PowerShell into WSL; no repo state was changed by that failure.

4. Evidence paths
- `TASKS.md`
- `src/body/fast_realistic_vision_fly.py`
- `src/vision/feature_extractor.py`
- `src/vision/flyvis_fast_path.py`
- `external/flygym/flygym/examples/vision/follow_fly_closed_loop.py`
- `external/flygym/doc/source/tutorials/advanced_vision.rst`

5. Next actions
- Implement `scripts/probe_lateralized_visual_candidates.py`.
- Generate a saved candidate ranking artifact from crafted left/right stimuli through the real vision model.
- Document the inferred candidate set separately from the public-grounded bridge.

## 2026-03-08 - Inferred lateralized visual probe completed and packaged

1. What I attempted
- Finished the real-FlyVis left/right probe that had been staged in the previous entry.
- Inspected the saved ranking artifacts to determine whether the current extractor was missing important visual cell families or just collapsing away their left/right structure.
- Added a reusable experimental helper that can load the inferred candidate artifact and turn live per-eye activity arrays into an inferred turn-bias signal.

2. What succeeded
- The real probe completed in WSL and wrote:
  - `outputs/metrics/inferred_lateralized_visual_candidates.csv`
  - `outputs/metrics/inferred_lateralized_visual_candidates.json`
  - `outputs/plots/inferred_lateralized_visual_stimuli.png`
- The top inferred tracking candidates were:
  - `TmY14`
  - `TmY15`
  - `TmY5a`
  - `TmY4`
  - `TmY18`
  - `TmY9`
- The top inferred flow candidates were:
  - `T5d`
  - `T5c`
  - `T4b`
  - `T5a`
- The main outcome is that the current extractor was not missing the relevant FlyVis families entirely. Many of the strongest inferred candidates were already in the production tracking/flow sets; the bigger loss was the left/right sign structure being averaged away and then collapsed back into bilateral public pools.
- Added reusable experimental code:
  - `src/vision/inferred_lateralized.py`
  - `tests/test_inferred_lateralized.py`
- Wrote a compact recommended candidate artifact:
  - `outputs/metrics/inferred_lateralized_visual_recommended.json`
- Documented the result:
  - `docs/inferred_lateralized_visual_candidates.md`
- Host validation passed:
  - `python -m pytest tests/test_inferred_lateralized.py tests/test_lateralized_probe.py tests/test_bridge_unit.py tests/test_closed_loop_smoke.py tests/test_realistic_vision_path.py`
  - result: `17 passed`

3. What failed
- This still does not recover a faithful public-grounded whole-brain neuron-ID mapping for left/right visual input.
- I have not yet wired the inferred `turn_bias` into a new closed-loop experiment mode, because that would be a new inferred bridge step and should stay clearly separated from the faithful default path.

4. Evidence paths
- `scripts/probe_lateralized_visual_candidates.py`
- `src/vision/lateralized_probe.py`
- `src/vision/inferred_lateralized.py`
- `tests/test_inferred_lateralized.py`
- `outputs/metrics/inferred_lateralized_visual_candidates.csv`
- `outputs/metrics/inferred_lateralized_visual_candidates.json`
- `outputs/metrics/inferred_lateralized_visual_recommended.json`
- `docs/inferred_lateralized_visual_candidates.md`

5. Next actions
- Decide whether to add a clearly labeled inferred visual-turn experiment mode that uses the new `turn_bias` helper without changing the faithful default bridge.
- If that experiment mode is added, keep it separate from public-grounded claims and benchmark it against the current strict default plus `public_p9_context`.

## 2026-03-08 - Inferred visual-turn remediation plan and first implementation slice

1. What I attempted
- Turned the recent visual-probe findings into a concrete remediation plan.
- Implemented the first code slice to preserve inferred left/right visual structure in the extracted features and bridge metadata without changing the faithful default path.
- Added a clearly labeled `inferred_visual_turn_context` brain-side experiment mode.
- Added tests, configs, and a local mock artifact run for the new mode.

2. What succeeded
- Wrote the concrete plan:
  - `docs/inferred_visual_turn_plan.md`
- Extended the extracted visual features to carry inferred experiment fields:
  - `src/vision/feature_extractor.py`
  - `src/bridge/encoder.py`
- Added a reusable inferred candidate path to the bridge build process:
  - `src/runtime/closed_loop.py`
- Added the new brain-side experiment mode:
  - `src/bridge/brain_context.py`
- Added experiment configs:
  - `configs/mock_inferred_visual_turn.yaml`
  - `configs/flygym_realistic_vision_inferred_visual_turn.yaml`
- Documented the new mode:
  - `docs/inferred_visual_turn_context_mode.md`
- Added test coverage:
  - `tests/test_realistic_vision_path.py`
  - `tests/test_bridge_unit.py`
  - `tests/test_closed_loop_smoke.py`
- Local validation passed:
  - `python -m pytest tests/test_inferred_lateralized.py tests/test_realistic_vision_path.py tests/test_bridge_unit.py tests/test_closed_loop_smoke.py`
  - result: `17 passed`
- Produced a mock artifact-complete run for the new experiment mode:
  - `outputs/inferred_visual_turn_mock_test/mock-demo-20260308-174921/demo.mp4`
  - `outputs/inferred_visual_turn_mock_test/mock-demo-20260308-174921/run.jsonl`
  - `outputs/inferred_visual_turn_mock_test/mock-demo-20260308-174921/metrics.csv`
- The mock run log now exposes the new inferred fields end-to-end:
  - `inferred_turn_bias`
  - `inferred_turn_confidence`
  - `inferred_candidate_count`

3. What failed
- I have not yet run the new inferred experiment mode through the real WSL FlyGym stack.
- So there is still no real-WSL evidence yet for whether the inferred visual-turn context materially improves turning behavior under the production body/vision runtime.

4. Evidence paths
- `docs/inferred_visual_turn_plan.md`
- `src/vision/feature_extractor.py`
- `src/bridge/encoder.py`
- `src/bridge/brain_context.py`
- `src/runtime/closed_loop.py`
- `docs/inferred_visual_turn_context_mode.md`
- `configs/mock_inferred_visual_turn.yaml`
- `configs/flygym_realistic_vision_inferred_visual_turn.yaml`
- `tests/test_realistic_vision_path.py`
- `tests/test_bridge_unit.py`
- `tests/test_closed_loop_smoke.py`
- `outputs/inferred_visual_turn_mock_test/mock-demo-20260308-174921/run.jsonl`

5. Next actions
- Run a short real WSL FlyGym validation with `configs/flygym_realistic_vision_inferred_visual_turn.yaml`.
- Compare that experiment mode against:
  - strict default
  - `public_p9_context`
- Keep any result explicitly labeled inferred, not public-grounded.

## 2026-03-08 - Started real `5 s` WSL comparison for inferred visual turn mode

1. What I attempted
- Started the user-requested real WSL comparison at `5 s` simulated runtime for:
  - strict default
  - `public_p9_context`
  - `inferred_visual_turn_context`
- Chose the fast vision payload for all three runs so the comparison isolates the brain-side mode differences rather than legacy-vs-fast vision overhead.

2. What succeeded
- Tracking updated:
  - `T041` set to `doing`
  - `T042` added as `doing`

3. What failed
- No runtime result yet at this point in the log; the actual WSL runs are still pending.

4. Evidence paths
- `TASKS.md`
- `configs/flygym_realistic_vision.yaml`
- `configs/flygym_realistic_vision_public_p9_context.yaml`
- `configs/flygym_realistic_vision_inferred_visual_turn.yaml`

5. Next actions
- Run the three `5 s` real WSL demos.
- Save outputs under separate comparison directories.
- Summarize metrics and log-level differences once all three runs finish.

## 2026-03-08 - Real `5 s` comparison hit a long-run Torch input-probability bug

1. What I attempted
- Started the first real WSL `5 s` comparison run for the strict default mode with fast vision:
  - `configs/flygym_realistic_vision.yaml`
  - `--vision-payload-mode fast`

2. What succeeded
- The run got far enough to confirm the real WSL stack still boots and enters the closed-loop path under the comparison command shape.

3. What failed
- The run aborted before completion with a Torch error inside the whole-brain Poisson spike generator:
  - `RuntimeError: Expected p_in >= 0 && p_in <= 1 to be true`
- Failure path:
  - `src/brain/pytorch_backend.py`
  - `PoissonSpikeGenerator.forward(...)`
- This exposes a long-run robustness bug: the current whole-brain input-rate path can produce values outside the valid Bernoulli probability range during real closed-loop execution.

4. Evidence paths
- `src/brain/pytorch_backend.py`
- `TASKS.md`

5. Next actions
- Patch the Poisson input path to clamp probabilities into `[0, 1]`.
- Add a local unit test for that clamp.
- Re-run the real `5 s` comparison after the backend is robust against this overflow.

## 2026-03-08 - Real `5 s` comparison completed for strict default, public `P9`, and inferred visual turn

1. What I attempted
- Patched the whole-brain Poisson generator so long real runs cannot feed invalid probabilities into `torch.bernoulli`.
- Added a unit test for that clamp.
- Re-ran the user-requested real WSL `5 s` comparison for:
  - strict default, fast vision
  - `public_p9_context`
  - `inferred_visual_turn_context`
- Added a reusable comparison script to summarize the resulting metrics and log-derived differences.

2. What succeeded
- Patched and tested the backend clamp:
  - `src/brain/pytorch_backend.py`
  - `tests/test_brain_backend.py`
- Host validation passed:
  - `python -m pytest tests/test_brain_backend.py tests/test_inferred_lateralized.py tests/test_realistic_vision_path.py tests/test_bridge_unit.py tests/test_closed_loop_smoke.py`
  - result: `19 passed`
- The new failure-tolerant runtime path now preserves partial metrics/logs/videos even when the body runtime crashes:
  - `src/runtime/closed_loop.py`
  - `tests/test_closed_loop_smoke.py`
- Real WSL strict-default run completed with partial artifact capture after a physics failure:
  - `outputs/compare_5s_strict_fast/flygym-demo-20260308-180228/demo.mp4`
  - `outputs/compare_5s_strict_fast/flygym-demo-20260308-180228/run.jsonl`
  - `outputs/compare_5s_strict_fast/flygym-demo-20260308-180228/metrics.csv`
- Real WSL `public_p9_context` run completed the full `5 s`:
  - `outputs/compare_5s_public_p9_fast/flygym-demo-20260308-180519/demo.mp4`
  - `outputs/compare_5s_public_p9_fast/flygym-demo-20260308-180519/run.jsonl`
  - `outputs/compare_5s_public_p9_fast/flygym-demo-20260308-180519/metrics.csv`
- Real WSL `inferred_visual_turn_context` run completed the full `5 s`:
  - `outputs/compare_5s_inferred_turn_fast/flygym-demo-20260308-182847/demo.mp4`
  - `outputs/compare_5s_inferred_turn_fast/flygym-demo-20260308-182847/run.jsonl`
  - `outputs/compare_5s_inferred_turn_fast/flygym-demo-20260308-182847/metrics.csv`
- Wrote a compact comparison artifact:
  - `scripts/compare_mode_runs.py`
  - `outputs/metrics/compare_5s_modes.csv`
  - `outputs/metrics/compare_5s_modes.json`

3. What failed
- The strict default fast-vision run did not complete the full `5 s`.
- It failed at about `0.57 s` simulated time with:
  - `PhysicsError`
  - `mjWARN_INERTIA`
- That instability is now reproducible and artifact-captured, but not yet fixed.

4. Evidence paths
- `src/brain/pytorch_backend.py`
- `tests/test_brain_backend.py`
- `src/runtime/closed_loop.py`
- `tests/test_closed_loop_smoke.py`
- `scripts/compare_mode_runs.py`
- `outputs/compare_5s_strict_fast/flygym-demo-20260308-180228/metrics.csv`
- `outputs/compare_5s_public_p9_fast/flygym-demo-20260308-180519/metrics.csv`
- `outputs/compare_5s_inferred_turn_fast/flygym-demo-20260308-182847/metrics.csv`
- `outputs/metrics/compare_5s_modes.csv`

5. Next actions
- Decide whether to investigate the strict-default body instability as a separate stabilization task.
- If the comparison result is good enough, use the new artifacts to discuss whether the inferred visual-turn context is materially better than `public_p9_context`.

## 2026-03-08 - Strict-default `backflip` / tumble diagnosis

1. What I attempted
- Inspected the strict-default `5 s` comparison log to explain the visible tumble / backflip-like behavior before the MuJoCo failure.

2. What succeeded
- Confirmed the strict default run is not showing an intentional connectome-driven acrobatic behavior.
- The log shows:
  - only `11` nonzero command cycles out of `285`
  - most cycles use exact zero decoded drive
  - late in the run, the body state drifts into very large yaw-rate / speed values even while commands are still zero
- The strongest sparse impulses were all-or-nothing DN spikes:
  - cycle `64`: symmetric forward pulse with `left_drive = right_drive = 0.311...`
  - cycle `243`: pure turn pulse with `left_drive = 0.298...`, `right_drive = -0.298...`
- The strict wrapper in `src/body/brain_only_realistic_vision_fly.py` uses a neutral low-level action whenever decoded drive is zero:
  - current joint positions copied through
  - `adhesion = 0` on all legs
- Current diagnosis: the strict mode is mostly leaving the body in that passive neutral-action path, not in an actively stabilized posture. Over a longer run that appears to let the fly drift/tumble, and the rare saturated DN spikes likely make the instability worse. The run eventually dies with `PhysicsError` / `mjWARN_INERTIA`.

3. What failed
- The log does not currently record pitch/roll directly, so I cannot claim a literal backflip angle from telemetry alone.
- The explanation is therefore a strong inference from:
  - the video appearance
  - the zero-drive neutral-action path
  - the sparse impulse-like commands
  - the MuJoCo invalid-state failure

4. Evidence paths
- `outputs/compare_5s_strict_fast/flygym-demo-20260308-180228/run.jsonl`
- `outputs/compare_5s_strict_fast/flygym-demo-20260308-180228/metrics.csv`
- `src/body/brain_only_realistic_vision_fly.py`
- `TASKS.md`

5. Next actions
- If strict-default stabilization matters, the next work should focus on a biologically honest non-locomoting posture path rather than the current passive zero-adhesion neutral action.

## 2026-03-08 - Strict-default stabilization via planted stance

1. What I attempted
- Replaced the unstable zero-drive passive body path with a planted stance path:
  - use the preprogrammed default pose when available
  - keep adhesion on for all legs during the zero-drive state
- Added a small unit test around that wrapper behavior.
- Re-ran the strict default real WSL `5 s` fast-vision run.

2. What succeeded
- Patched the zero-drive body path:
  - `src/body/brain_only_realistic_vision_fly.py`
- Added a unit test:
  - `tests/test_body_wrapper_unit.py`
- Host validation passed:
  - `python -m pytest tests/test_body_wrapper_unit.py tests/test_closed_loop_smoke.py tests/test_brain_backend.py`
  - result: `6 passed, 1 skipped`
- The strict default real WSL `5 s` run is now stable and completes the full duration:
  - `outputs/compare_5s_strict_fast_v2/flygym-demo-20260308-195012/demo.mp4`
  - `outputs/compare_5s_strict_fast_v2/flygym-demo-20260308-195012/run.jsonl`
  - `outputs/compare_5s_strict_fast_v2/flygym-demo-20260308-195012/metrics.csv`
- New strict-default metrics:
  - `sim_seconds = 5.0`
  - `stable = 1.0`
  - `completed_full_duration = 1.0`
  - `nonzero_command_cycles = 107`

3. What failed
- This does not yet prove that the observed strict-default motion is fully attributable to the real brain backend rather than residual passive drift between sparse command pulses.
- I added a zero-brain baseline backend and config to measure that next.

4. Evidence paths
- `src/body/brain_only_realistic_vision_fly.py`
- `tests/test_body_wrapper_unit.py`
- `outputs/compare_5s_strict_fast_v2/flygym-demo-20260308-195012/metrics.csv`
- `outputs/compare_5s_strict_fast_v2/flygym-demo-20260308-195012/run.jsonl`
- `src/brain/zero_backend.py`
- `configs/flygym_realistic_vision_zero_brain.yaml`

5. Next actions
- Run a real WSL `5 s` zero-brain baseline.
- Compare the stable strict-default real-brain run against that zero-brain baseline to measure how much motion is actually brain-driven.

## 2026-03-08 - Brain-driven motion proof via zero-brain baseline

1. What I attempted
- Added a zero-output whole-brain backend to create a clean body-fallback baseline.
- Ran a real WSL `5 s` zero-brain FlyGym baseline under the same strict production body path.
- Compared the stable strict-default real-brain run against that zero-brain baseline.

2. What succeeded
- Added the zero backend and config:
  - `src/brain/zero_backend.py`
  - `configs/flygym_realistic_vision_zero_brain.yaml`
- Added smoke coverage for the zero backend:
  - `tests/test_closed_loop_smoke.py`
- Host validation passed:
  - `python -m pytest tests/test_closed_loop_smoke.py tests/test_brain_backend.py`
  - result: `7 passed`
- Real WSL zero-brain run completed the full `5 s`:
  - `outputs/compare_5s_zero_brain_fast/flygym-demo-20260308-201434/demo.mp4`
  - `outputs/compare_5s_zero_brain_fast/flygym-demo-20260308-201434/run.jsonl`
  - `outputs/compare_5s_zero_brain_fast/flygym-demo-20260308-201434/metrics.csv`
- Wrote the direct comparison artifact:
  - `outputs/metrics/compare_5s_strict_vs_zero.csv`
  - `outputs/metrics/compare_5s_strict_vs_zero.json`
- Wrote the supporting validation doc:
  - `docs/brain_control_validation.md`
- The direct numbers are:
  - strict real brain:
    - `nonzero_command_cycles = 107`
    - `path_length = 10.810298593539402`
    - `avg_forward_speed = 2.1629248886633454`
  - zero brain:
    - `nonzero_command_cycles = 0`
    - `path_length = 0.3795886446352556`
    - `avg_forward_speed = 0.07594810817031923`

3. What failed
- This does not solve the remaining parity gaps by itself.
- It proves brain-driven motion under the strict default stack, but not final parity with the public demo.

4. Evidence paths
- `src/brain/zero_backend.py`
- `configs/flygym_realistic_vision_zero_brain.yaml`
- `outputs/compare_5s_strict_fast_v2/flygym-demo-20260308-195012/metrics.csv`
- `outputs/compare_5s_zero_brain_fast/flygym-demo-20260308-201434/metrics.csv`
- `outputs/metrics/compare_5s_strict_vs_zero.csv`
- `docs/brain_control_validation.md`

5. Next actions
- If stronger parity is still required, the next work should focus on making the strict real-brain locomotor policy less sparse rather than re-proving body-fallback removal.

## 2026-03-08 - Corrected interpretation of the strict-default `5 s` run

1. What I checked
- Re-opened the strict-default `5 s` artifact after the user challenged the interpretation:
  - `outputs/compare_5s_strict_fast_v2/flygym-demo-20260308-195012/demo.mp4`
  - `outputs/compare_5s_strict_fast_v2/flygym-demo-20260308-195012/trajectory.png`
  - `outputs/compare_5s_strict_fast_v2/flygym-demo-20260308-195012/commands.png`
- Compared it directly against:
  - `outputs/compare_5s_zero_brain_fast/flygym-demo-20260308-201434/trajectory.png`
  - `outputs/compare_5s_public_p9_fast/flygym-demo-20260308-180519/trajectory.png`
  - `outputs/compare_5s_inferred_turn_fast/flygym-demo-20260308-182847/trajectory.png`

2. What I found
- The prior claim was too strong.
- The strict-default run is stable and brain-modulated relative to the zero-brain baseline, but it is not convincing locomotion.
- Visual inspection shows mostly local twitching / jitter inside a small region, not sustained walking across the arena.
- The reason the previous numbers looked better than the video is that `path_length` accumulates every small oscillation, so it overstates local jitter as "movement."
- The command trace is also consistent with sparse impulse-like control rather than a sustained locomotor policy:
  - mean forward drive is only about `0.00436`
  - only `107 / 2500` cycles are nonzero
  - most nonzero commands are narrow spikes rather than a continuous drive profile

3. What failed
- `docs/brain_control_validation.md` is still useful for proving that hidden body fallback was removed, but it should not be read as proof of meaningful walking.
- The strict default stack therefore remains below the bar for "the fly moves under full brain control" in the ordinary behavioral sense.

4. Evidence paths
- `outputs/compare_5s_strict_fast_v2/flygym-demo-20260308-195012/demo.mp4`
- `outputs/compare_5s_strict_fast_v2/flygym-demo-20260308-195012/trajectory.png`
- `outputs/compare_5s_strict_fast_v2/flygym-demo-20260308-195012/commands.png`
- `outputs/compare_5s_zero_brain_fast/flygym-demo-20260308-201434/trajectory.png`
- `outputs/compare_5s_public_p9_fast/flygym-demo-20260308-180519/trajectory.png`
- `outputs/compare_5s_inferred_turn_fast/flygym-demo-20260308-182847/trajectory.png`

5. Next actions
- Add more honest movement-quality metrics such as net displacement and spatial extent.
- Treat the current strict-default result as sparse brain-driven twitching, not successful locomotion.
- Continue iterating on the strict bridge / readout path until the real-brain default produces sustained locomotion rather than impulses.

## 2026-03-08 - Corrective plan for a cold-startable vision-driven brain path

1. What I concluded from the failed strict-default interpretation
- The previous bridge is missing more than tuning.
- Two concrete systemic problems are now clear from the local evidence:
  - the mechanosensory public input pool was mapped to all JONs, even though the checked public notebook experiment is specifically `P9_JO_CE_bilateral`
  - the existing inferred turn experiment injects turning readouts directly, which is too close to forcing output rather than letting the brain use its public locomotor gate

2. What I verified
- The public notebook includes explicit subgroup definitions for:
  - `neu_JON_CE`
  - `neu_JON_F`
  - `neu_JON_D_m`
- The current repo only preserved one flat `JON_IDS` list and used all of them for `mech_bilateral`.
- The current inferred-turn run uses mean forward `P9` context of about `76 Hz`, but its turn-rate injection is very weak and it still bypasses the cleaner `P9_left` / `P9_right` route.

3. Corrective direction
- Replace the current broad JON pool with the public `JON_CE` subset as the default bilateral mechanosensory public input.
- Add a new stateful brain-context mode that:
  - cold-starts from zero
  - derives locomotor onset from visual forward evidence
  - drives only `P9_left` and `P9_right`
  - steers by asymmetric `P9` drive rather than direct DNa injection
- Add more honest movement metrics so local twitching cannot be misreported as locomotion again.

4. Evidence paths
- `external/fly-brain/code/paper-phil-drosophila/figures.ipynb`
- `external/fly-brain/code/paper-phil-drosophila/example.ipynb`
- `outputs/compare_5s_strict_fast_v2/flygym-demo-20260308-195012/commands.png`
- `outputs/metrics/motor_path_audit_sweeps.csv`
- `outputs/compare_5s_inferred_turn_fast/flygym-demo-20260308-182847/run.jsonl`

5. Next actions
- Implement the public JON subgroup definitions and switch the default mechanosensory public input to `JON_CE`.
- Implement the stateful visually gated asymmetric `P9` context mode.
- Extend the parity metrics with net displacement and spatial extent before the next claim about movement quality.

## 2026-03-08 - First corrective implementation slice for cold-start visual locomotion

1. What I changed
- Added honest movement metrics:
  - `net_displacement`
  - `displacement_efficiency`
  - `bbox_width`
  - `bbox_height`
  - `bbox_area`
- Preserved the public JON subgroup definitions in code and switched the default public mechanosensory input pool from all JONs to the public `JON_CE` subset:
  - `src/brain/public_ids.py`
- Made encoder / decoder settings load from config instead of silently ignoring config tuning:
  - `src/bridge/encoder.py`
  - `src/bridge/decoder.py`
  - `src/runtime/closed_loop.py`
- Added a new stateful brain-context mode:
  - `brain_context.mode: inferred_visual_p9_context`
  - it cold-starts from zero
  - low-pass gates locomotion from visual forward evidence
  - drives only `P9_left` and `P9_right`
  - uses asymmetric `P9` drive rather than direct DNa output forcing
- Added decoder-side temporal smoothing so sparse firing-rate spikes can produce a continuous descending command:
  - `src/bridge/decoder.py`
- Added configs and smoke coverage:
  - `configs/mock_inferred_visual_p9.yaml`
  - `configs/flygym_realistic_vision_inferred_visual_p9.yaml`
  - `tests/test_bridge_unit.py`
  - `tests/test_closed_loop_smoke.py`

2. What succeeded
- Host validation passed after the refactor:
  - `python -m pytest tests/test_bridge_unit.py tests/test_closed_loop_smoke.py tests/test_realistic_vision_path.py tests/test_brain_backend.py tests/test_benchmark_output_format.py`
  - result: `21 passed`
- The new mock mode now produces sustained traversal rather than local jitter:
  - `outputs/inferred_visual_p9_mock_test_v2/mock-demo-20260308-214620/demo.mp4`
  - `outputs/inferred_visual_p9_mock_test_v2/mock-demo-20260308-214620/trajectory.png`
  - `outputs/inferred_visual_p9_mock_test_v2/mock-demo-20260308-214620/metrics.csv`
- A short real WSL smoke run also improved materially versus the earlier spiky attempt:
  - `outputs/inferred_visual_p9_smoke_v2/flygym-demo-20260308-214635/demo.mp4`
  - `outputs/inferred_visual_p9_smoke_v2/flygym-demo-20260308-214635/trajectory.png`
  - `outputs/inferred_visual_p9_smoke_v2/flygym-demo-20260308-214635/commands.png`
  - `outputs/inferred_visual_p9_smoke_v2/flygym-demo-20260308-214635/metrics.csv`
- That real `0.2 s` smoke run now shows continuous low-amplitude drive and materially better displacement efficiency:
  - `path_length = 0.4318`
  - `net_displacement = 0.1517`
  - `displacement_efficiency = 0.3514`

3. What failed
- This is not yet a completed proof of a good `5 s` cold-start locomotor policy.
- The real `0.2 s` smoke run still shows a curving local path rather than a fully convincing long-horizon pursuit trajectory.

4. Evidence paths
- `src/brain/public_ids.py`
- `src/bridge/brain_context.py`
- `src/bridge/decoder.py`
- `src/runtime/closed_loop.py`
- `outputs/inferred_visual_p9_smoke_v2/flygym-demo-20260308-214635/trajectory.png`
- `outputs/inferred_visual_p9_smoke_v2/flygym-demo-20260308-214635/commands.png`
- `outputs/inferred_visual_p9_smoke_v2/flygym-demo-20260308-214635/metrics.csv`

5. Next actions
- Run a full real `5 s` WSL validation with `configs/flygym_realistic_vision_inferred_visual_p9.yaml`.
- Compare it against:
  - zero-brain baseline
  - a no-target / vision-ablated control
- Use the old strict / `public_p9_context` modes only as diagnostic failure references, not as targets for success.
- Decide from those absolute criteria whether the new bridge is genuinely good enough or still only a partial fix.

## 2026-03-08 - Splice-strategy reset after the inferred `P9` critique

1. What I clarified
- The new `inferred_visual_p9_context` mode is still not an acceptable final answer.
- In plain terms it is an inferred prosthetic input:
  - real FlyVis visual signals go in
  - bridge logic decides when and how strongly to stimulate `P9_left` / `P9_right`
  - the rest of the whole-brain backend then evolves from that externally applied brain input
- That is cleaner than body fallback or direct DNa forcing, but it is still not an endogenous sensory pathway.

2. What the user correctly pushed on
- The key failure is not just tuning.
- The current bridge compresses a rich visual state into a few scalar rates before the brain ever sees it.
- That scalar compression is almost certainly destroying the left/right, motion-direction, and cell-family-specific structure needed for a correct splice.
- If FlyVis and the whole-brain graph both already cover real visual circuitry, the right next move is not more body-loop tuning; it is a body-free splice workflow.

3. Current best interpretation
- This is now best framed as a splice-boundary and interface-identification problem.
- It is not enough to say "the whole brain has eyes" or "FlyVis is mapped":
  - both systems may be structurally valid
  - but the live interface between them is still undefined in this repo
- The next technically correct move is:
  - pick a visual splice boundary
  - preserve a wide visual representation instead of scalar summaries
  - use FlyVis as a teacher on the overlapping visual populations
  - fit or derive the mapping there
  - only then pass control to the rest of the whole-brain model

4. Important validation rule change
- Old broken modes are no longer acceptable comparison targets:
  - `strict_default`
  - `public_p9_context`
  - `inferred_visual_turn_context`
- They remain useful only as failure diagnostics.
- The next success criteria must be absolute and body-free where possible:
  - zero-brain baseline
  - no-target / vision-ablated baseline
  - direct FlyVis-to-brain overlap agreement under shared stimuli

5. Next actions
- Write the splice strategy out in a dedicated doc so the compacted context does not lose this reasoning.
- Start with body-free work:
  - inspect FlyVis metadata for overlap identities
  - build a FlyVis + whole-brain offline splice harness
  - postpone body-loop claims until the splice itself is grounded.

## 2026-03-09 - First grounded body-free FlyVis-to-whole-brain splice probe

1. What I changed
- Added a reusable FlyWire annotation helper:
  - `src/brain/flywire_annotations.py`
- Added a body-free splice probe runner:
  - `scripts/run_splice_probe.py`
- Added a small unit test file for the new annotation helpers:
  - `tests/test_flywire_annotations.py`
- Extended the Torch backend with a clean monitored-ID setter so the splice probe can observe arbitrary overlap groups:
  - `src/brain/pytorch_backend.py`
- Wrote the result doc:
  - `docs/splice_probe_results.md`

2. What I used as the new public grounding source
- Downloaded the official FlyWire annotation supplement to:
  - `outputs/cache/flywire_annotation_supplement.tsv`
- This table exposes:
  - `root_id`
  - `cell_type`
  - `side`
- That is the first public artifact in this repo that grounds the whole-brain side of the visual splice at exact shared type labels plus side instead of arbitrary inferred pools.

3. What I found about the overlap
- `scripts/inspect_flyvis_overlap.py` still stands: FlyVis metadata alone does not expose direct FlyWire root IDs.
- The official annotation supplement closes part of the gap.
- The repo now finds `49` exact shared FlyVis / whole-brain visual cell types.
- These shared types are bilateral and large enough to support a wide splice.
- Important detail: among the FlyVis `R*` classes, the exact shared photoreceptor overlap found in the annotation supplement is `R7` and `R8`, not `R1` to `R6`.

4. What the body-free splice probe does
- Runs real FlyVis on:
  - `baseline_gray`
  - `body_left_dark`
  - `body_center_dark`
  - `body_right_dark`
- Aggregates FlyVis teacher activity by exact shared `cell_type` + `side`
- Maps the positive activity delta above baseline into direct whole-brain external drive for the matching shared `cell_type` + `side` root-ID groups
- Runs the whole-brain backend body-free for a short response window
- Compares grouped teacher and student activity at that boundary

5. What succeeded
- The wide type-level splice is real and public-grounded at the boundary:
  - `outputs/metrics/splice_probe_summary.json`
  - `outputs/metrics/splice_probe_groups.csv`
  - `outputs/metrics/splice_probe_side_differences.csv`
- Grouped teacher/student boundary correlation is high:
  - about `0.9881` for `body_left_dark`
  - about `0.9885` for `body_center_dark`
  - about `0.9913` for `body_right_dark`
- This is the first local proof that the bridge can operate on a wide shared visual boundary instead of only a handful of scalar visual features.

6. What failed
- Left/right asymmetry is not yet preserved robustly:
  - `teacher_student_side_diff_correlation = 0.2099` for `body_left_dark`
  - `teacher_student_side_diff_correlation = null` for `body_center_dark`
  - `teacher_student_side_diff_correlation = 0.8819` for `body_right_dark`
- Short-window downstream motor readouts remain zero for all non-baseline probe conditions.
- The current backend external-drive interface is still nonnegative only, so the splice probe cannot represent inhibitory visual deviations. It only maps positive deltas above baseline.
- The current probe still broadcasts one rate per `cell_type` + `side`, so it discards retinotopic `u` / `v` structure within each group.

7. What this changes in the project understanding
- The visual splice is now much more concrete.
- The right first boundary is no longer:
  - scalar salience / flow summaries
- The right first boundary is now:
  - exact shared visual `cell_type`
  - exact `side`
- The remaining blockers are now more specific:
  - signed external input at the splice boundary
  - retinotopic structure inside the shared groups
  - downstream propagation beyond the boundary itself

8. Validation
- Host validation:
  - `python -m pytest tests/test_flywire_annotations.py tests/test_inferred_lateralized.py tests/test_lateralized_probe.py`
  - result: `8 passed`
- WSL body-free splice probe:
  - `outputs/metrics/splice_probe_summary.json`
  - `outputs/metrics/splice_probe_groups.csv`
  - `outputs/metrics/splice_probe_side_differences.csv`

9. Next actions
- Add signed splice inputs so the body-free probe can represent inhibitory deviations instead of only positive deltas.
- Add coarse retinotopic structure, likely `u` / `v` bins, instead of broadcasting one scalar per `cell_type` + `side`.
- Only return to embodied claims after the body-free splice can preserve asymmetry robustly and recruit meaningful downstream brain responses.

## 2026-03-09 - Signed + spatial body-free splice follow-up

1. What I changed
- Added experimental signed boundary input support to the Torch backend:
  - `src/brain/pytorch_backend.py`
- Kept interface compatibility by extending:
  - `src/brain/mock_backend.py`
  - `src/brain/zero_backend.py`
- Added a spatial-overlap helper based on public FlyWire positions:
  - `src/brain/flywire_annotations.py`
- Extended the body-free probe so it can run with:
  - `input_mode=current_signed`
  - `spatial_bins > 1`
- Added tests:
  - `tests/test_brain_backend.py`
  - `tests/test_flywire_annotations.py`

2. Validation
- Host validation:
  - `python -m pytest tests/test_brain_backend.py tests/test_flywire_annotations.py tests/test_inferred_lateralized.py tests/test_lateralized_probe.py`
  - result: `11 passed`
- Syntax validation:
  - `python -m py_compile scripts/run_splice_probe.py src/brain/flywire_annotations.py src/brain/pytorch_backend.py src/brain/mock_backend.py src/brain/zero_backend.py`

3. What the signed + spatial probe does
- Signed mode:
  - uses direct current at the boundary instead of positive-only Poisson rate drive
- Spatial mode:
  - splits each shared visual `cell_type` + `side` into `4` coarse bins
  - FlyVis side uses `u`-based bins
  - whole-brain side uses inferred bins from public FlyWire spatial coordinates

4. New artifacts
- `outputs/metrics/splice_probe_signed_bins4_summary.json`
- `outputs/metrics/splice_probe_signed_bins4_groups.csv`
- `outputs/metrics/splice_probe_signed_bins4_side_differences.csv`
- `outputs/metrics/splice_probe_signed_bins4_100ms_summary.json`
- `outputs/metrics/splice_probe_signed_bins4_100ms_groups.csv`
- `outputs/metrics/splice_probe_signed_bins4_100ms_side_differences.csv`

5. What succeeded
- The body-free splice no longer has to rely on positive-only boundary drive.
- The body-free splice no longer broadcasts one scalar across an entire `cell_type` + `side`.
- In the signed+spatial `20 ms` probe:
  - side-difference preservation improved relative to the earlier broad positive-only probe
  - nonzero downstream motor readouts now appear
- In the signed+spatial `100 ms` probe:
  - downstream motor readouts become clearly nonzero for all asymmetric conditions
  - the sign of the turn-bias difference flips between left-dark and right-dark stimuli:
    - `body_left_dark`: `turn_right - turn_left = -10`
    - `body_right_dark`: `turn_right - turn_left = +10`

6. What failed
- Grouped boundary correlation dropped relative to the first broad type-level probe:
  - now about `0.746` for left/right and `0.819` for center in the signed+spatial runs
- Several groups saturate at high spike rates in the current mapping, especially positive `Am` bins.
- Strongly negative teacher targets often still appear as zero student spike-rate delta because the measured student boundary signal is still spike-based and the baseline is near quiescent.
- So the new blockers are now:
  - state-readout blindness for inhibitory deviations
  - current-scale calibration
  - better spatial correspondence than the present inferred one-axis binning

7. What changed in the project understanding
- The splice problem is now narrower and more concrete.
- We have moved from:
  - "does any grounded splice exist at all?"
- to:
  - "how do we calibrate and observe a grounded signed spatial splice without saturation and without losing inhibitory structure?"

8. Next actions
- Add state-based boundary readouts such as voltage or conductance so negative signed drive is observable without requiring spikes.
- Calibrate the signed-current scale and the spatial-bin mapping before any new embodied claim.

## 2026-03-09 - State-based splice readouts and calibrated body-free splice ranking

1. What I changed
- Added state-aware monitoring to the public Torch backend:
  - `src/brain/pytorch_backend.py`
  - new `WholeBrainTorchBackend.step_with_state(...)`
- Extended the body-free probe so each matched overlap group now records:
  - spike-rate deltas
  - voltage deltas
  - conductance deltas
- Added calibration scripts:
  - `scripts/run_splice_calibration.py`
  - `scripts/summarize_splice_calibration.py`
- Added a focused negative-current unit test:
  - `tests/test_brain_backend.py`

2. Validation
- Host tests:
  - `python -m pytest tests/test_brain_backend.py tests/test_flywire_annotations.py tests/test_inferred_lateralized.py tests/test_lateralized_probe.py`
  - result: `12 passed`
- Syntax validation:
  - `python -m py_compile scripts/run_splice_probe.py scripts/run_splice_calibration.py scripts/summarize_splice_calibration.py src/brain/pytorch_backend.py`

3. New artifacts
- State-based probe:
  - `outputs/metrics/splice_probe_signed_bins4_100ms_state_summary.json`
  - `outputs/metrics/splice_probe_signed_bins4_100ms_state_groups.csv`
  - `outputs/metrics/splice_probe_signed_bins4_100ms_state_side_differences.csv`
- Targeted calibration runs:
  - `outputs/metrics/splice_probe_bins4_current20_summary.json`
  - `outputs/metrics/splice_probe_bins4_current40_summary.json`
  - `outputs/metrics/splice_probe_bins4_current80_summary.json`
  - `outputs/metrics/splice_probe_bins2_current80_summary.json`
- Curated calibration ranking:
  - `outputs/metrics/splice_probe_calibration_curated.csv`
  - `outputs/metrics/splice_probe_calibration_curated.json`

4. What succeeded
- The probe now shows that spike-only evaluation was hiding real signed boundary responses.
- In the calibrated bins=`4`, current=`120` body-free run:
  - mean voltage group correlation is about `0.8709`
  - mean voltage side-difference correlation is about `0.8079`
  - left-dark vs right-dark downstream turn bias flips correctly:
    - left-dark: `turn_right - turn_left = -10`
    - right-dark: `turn_right - turn_left = +10`
- The curated calibration ranking now identifies the current best tested splice point as:
  - `4` spatial bins
  - `max_abs_current = 120`
- This is the first calibrated body-free splice setting in the repo that simultaneously:
  - preserves left/right boundary structure strongly in a signed state readout
  - keeps measured spike-rate saturation low
  - reaches the monitored downstream turn readouts with the correct left/right sign flip

5. What failed
- The full scripted calibration sweep in `scripts/run_splice_calibration.py` was too expensive to finish across the entire initial grid in one pass, so I stopped the broad sweep after enough bins=`1` and bins=`2` points were collected and filled the remaining critical comparisons with targeted single-run probes.
- The calibrated splice is still not robust enough for embodied claims:
  - bins=`4` lower-current runs preserve boundary asymmetry but fail the downstream turn-sign check
  - bins=`1` preserves broad grouped fit well but loses too much left/right structure
  - bins=`2` preserves left/right structure well but the tested settings still fail the downstream turn-sign check
- The best tested point is therefore only a local calibration result, not a proof of a globally optimal splice.

6. What changed in the project understanding
- `T057` is now closed: state-based boundary readouts were the missing diagnostic piece.
- `T058` is now closed in the narrower engineering sense: the current tested grid has a defensible best point and the tradeoffs are explicit.
- The next blockers are now downstream of calibration:
  - better retinotopic correspondence than the current inferred binning
  - deeper central-target / longer-window validation before body reintegration

7. Next actions
- Probe deeper intermediate targets and longer windows using the calibrated body-free splice.
- Improve the spatial correspondence beyond the current one-axis inferred bin proxy before returning to embodied cold-start claims.

## 2026-03-09 - Deeper relay probe and 2D UV-grid follow-up

1. What I attempted
- Continued from the calibrated body-free splice instead of returning to the body loop.
- Added a relay-candidate finder to identify bilateral annotated intermediate targets that sit between the grounded visual overlap groups and the monitored motor readouts:
  - `scripts/find_splice_relay_candidates.py`
- Added a dedicated relay probe so the calibrated splice can be evaluated over longer windows and against deeper central groups, not just the final motor readouts:
  - `scripts/run_splice_relay_probe.py`
- Extended the grounded spatial helper so the splice can use a coarse two-dimensional grid instead of only a one-axis proxy:
  - `src/brain/flywire_annotations.py`
- Extended the body-free splice probe with:
  - `--spatial-mode uv_grid`
  - `--spatial-u-bins`
  - `--spatial-v-bins`
  - `--spatial-flip-u`
  - `--spatial-flip-v`
  - file: `scripts/run_splice_probe.py`
- Ran the new relay and UV-grid probes in WSL.
- I initially launched the relay and UV-grid probe runs in parallel. That made them look stalled because both jobs were CPU-heavy. I killed those parallel runs and reran the probes sequentially so the resulting artifacts reflect clean single-job measurements.

2. What succeeded
- Relay candidate discovery now exists as a reproducible script plus saved artifacts:
  - `outputs/metrics/splice_relay_candidates.json`
  - `outputs/metrics/splice_relay_candidates_pairs.csv`
  - `outputs/metrics/splice_relay_candidates_roots.csv`
- The strongest bilateral annotated relay candidates found from the overlap-to-motor intersection are:
  - `LC31a`
  - `LC31b`
  - `LC19`
  - `LCe06`
  - `LT82a`
  - `LCe04`
- The calibrated body-free splice now has direct intermediate-target evidence, not just final motor evidence:
  - `outputs/metrics/splice_relay_probe_summary.json`
  - `outputs/metrics/splice_relay_probe.csv`
  - `outputs/metrics/splice_relay_probe_pairs.csv`
- At `100 ms`, the relay probe preserves the expected downstream turn-sign flip:
  - left-dark: `turn_right - turn_left = -10`
  - right-dark: `turn_right - turn_left = +10`
- At that same `100 ms` window, several relay groups already carry structured lateralized state:
  - `LC31a` right-minus-left voltage is negative in both asymmetric conditions, about `-2.60 mV` for left-dark and about `-1.86 mV` for right-dark
  - `LCe06` right-minus-left rate flips sign with the condition, about `-6.33 Hz` for left-dark and about `+10.67 Hz` for right-dark
  - `LT82a` shows the strongest relay asymmetry in the tested set, about `-45 Hz` for left-dark and about `0 Hz` for right-dark
- The retinotopy work now goes beyond the original one-axis proxy:
  - `src/brain/flywire_annotations.py` can now build a grounded coarse `u/v` grid from public FlyWire positions
  - `scripts/run_splice_probe.py` can now test that grid against FlyVis native `u/v`
- The new `uv_grid` probe variants are saved and comparable:
  - `outputs/metrics/splice_probe_uvgrid_2x2_current120_summary.json`
  - `outputs/metrics/splice_probe_uvgrid_flipu_summary.json`
  - `outputs/metrics/splice_probe_uvgrid_flipuv_summary.json`
- The best tested `uv_grid` boundary fit so far is the `flip_u` variant:
  - mean voltage group correlation about `0.8764`
  - mean voltage side-difference correlation about `0.8466`
- That boundary fit is better than the previous calibrated axis1d splice:
  - axis1d mean voltage group correlation about `0.8709`
  - axis1d mean voltage side-difference correlation about `0.8079`
- Host validation still passes:
  - `python -m pytest tests/test_flywire_annotations.py tests/test_brain_backend.py`
  - result: `7 passed`
- Syntax validation also passed:
  - `python -m py_compile src/brain/flywire_annotations.py scripts/run_splice_probe.py scripts/find_splice_relay_candidates.py scripts/run_splice_relay_probe.py`

3. What failed
- The longer-window relay probe exposed a new downstream-stability failure:
  - at `500 ms`, the downstream turn sign no longer preserves the initial left-vs-right flip
  - left-dark: `turn_right - turn_left = -17`
  - right-dark: `turn_right - turn_left = -9`
- So the calibrated splice launches the expected downstream response, but the recurrent brain dynamics drift over longer windows.
- The new `uv_grid` splice improved boundary agreement, but it did not preserve the correct downstream sign:
  - unflipped `uv_grid`:
    - left-dark: `turn_right - turn_left = +35`
    - right-dark: `turn_right - turn_left = -15`
  - `flip_u` `uv_grid`:
    - left-dark: `turn_right - turn_left = +5`
    - right-dark: `turn_right - turn_left = -10`
  - `flip_u + flip_v` `uv_grid`:
    - left-dark: `turn_right - turn_left = +10`
    - right-dark: `turn_right - turn_left = +30`
- This narrows the next blocker:
  - the `uv_grid` splice is not "too rich"
  - it is still oriented incorrectly relative to the downstream circuit, or it still lacks exact column alignment

4. Evidence paths
- `src/brain/flywire_annotations.py`
- `tests/test_flywire_annotations.py`
- `scripts/run_splice_probe.py`
- `scripts/find_splice_relay_candidates.py`
- `scripts/run_splice_relay_probe.py`
- `outputs/metrics/splice_relay_candidates.json`
- `outputs/metrics/splice_relay_probe_summary.json`
- `outputs/metrics/splice_probe_uvgrid_2x2_current120_summary.json`
- `outputs/metrics/splice_probe_uvgrid_flipu_summary.json`
- `outputs/metrics/splice_probe_uvgrid_flipuv_summary.json`
- `docs/splice_probe_results.md`

5. Next actions
- Resolve UV-grid orientation / exact column alignment so the better two-dimensional boundary fit also preserves downstream turn sign.
- Explain or stabilize the longer-window downstream drift that erases the correct initial turn-sign flip by `500 ms`.
- Keep the next loop body-free until those two blockers are understood.

## 2026-03-09 - UV-grid targeted alignment follow-up and drift explanation

1. What I attempted
- Continued directly on `T061` and `T062`.
- Added richer spatial-alignment controls on the whole-brain side:
  - axis swap for the two PCA-based spatial axes
  - side-specific horizontal mirroring
  - files:
    - `src/brain/flywire_annotations.py`
    - `scripts/run_splice_probe.py`
- Added a targeted UV-grid summarizer:
  - `scripts/summarize_uvgrid_targeted.py`
- Added pulse-schedule support to the deeper relay probe:
  - `scripts/run_splice_relay_probe.py`
  - new `--input-pulse-ms`
- Added a compact relay-drift summarizer:
  - `scripts/summarize_relay_drift.py`
- Validated the new code locally, then ran targeted WSL body-free probes instead of returning to the body loop.

2. What succeeded
- Local validation passed after the new spatial-alignment helper and summarizer changes:
  - `python -m pytest tests/test_flywire_annotations.py tests/test_brain_backend.py`
  - result: `9 passed`
- The targeted UV-grid follow-up is now backed by compact comparison artifacts:
  - `outputs/metrics/splice_uvgrid_targeted_comparison.csv`
  - `outputs/metrics/splice_uvgrid_targeted_comparison.json`
- The targeted UV-grid runs now include side-specific horizontal mirroring:
  - `outputs/metrics/splice_probe_uvgrid_mirror_summary.json`
  - `outputs/metrics/splice_probe_uvgrid_flipu_mirror_summary.json`
  - `outputs/metrics/splice_probe_uvgrid_flipv_mirror_summary.json`
  - `outputs/metrics/splice_probe_uvgrid_swap_mirror_summary.json`
- The best targeted boundary-fit row is now:
  - `flip_v = true`
  - `mirror_u_by_side = true`
  - mean voltage group correlation about `0.8764`
  - mean voltage side-difference correlation about `0.8467`
- But even that best targeted row still fails the downstream sign test:
  - left-dark: `turn_right - turn_left = -15`
  - right-dark: `turn_right - turn_left = -5`
- This is now a stronger result than before:
  - plain global flips were not enough
  - side-specific horizontal mirroring was also not enough
  - so the remaining spatial blocker is no longer just axis-sign ambiguity
- The drift follow-up is also now backed by compact comparison artifacts:
  - `outputs/metrics/splice_relay_drift_comparison.csv`
  - `outputs/metrics/splice_relay_drift_comparison.json`
- The relay-drift comparison now shows three concrete reference points:
  - `100 ms` hold:
    - left-dark `-10`
    - right-dark `+10`
    - correct sign
  - `500 ms` hold:
    - left-dark `-17`
    - right-dark `-9`
    - sign collapsed
  - `500 ms` with only a `25 ms` pulse:
    - left-dark `0`
    - right-dark about `-6.32`
    - sign still not preserved

3. What failed
- The full `uv_grid` orientation brute-force search became too expensive once the side-specific mirror branch was added, so I stopped using the full brute-force loop and switched to a smaller targeted matrix around the most promising UV-grid families.
- The first targeted WSL batch also failed once because PowerShell ate the bash `$PY` variable; I reran it with the Python path inlined.
- The broad `500 ms` drift sweep was also too expensive when it monitored more state than needed, so I narrowed it to compact comparison artifacts instead of waiting on the larger sweep.
- Most importantly, neither `T061` nor `T062` produced a full fix:
  - `T061`: no tested UV-grid orientation or side-mirror variant restored the correct downstream left-vs-right motor sign
  - `T062`: even a very short `25 ms` pulse does not preserve the correct sign by `500 ms`

4. Evidence paths
- `src/brain/flywire_annotations.py`
- `scripts/run_splice_probe.py`
- `scripts/run_splice_relay_probe.py`
- `scripts/summarize_uvgrid_targeted.py`
- `scripts/summarize_relay_drift.py`
- `outputs/metrics/splice_uvgrid_targeted_comparison.csv`
- `outputs/metrics/splice_uvgrid_targeted_comparison.json`
- `outputs/metrics/splice_relay_drift_comparison.csv`
- `outputs/metrics/splice_relay_drift_comparison.json`
- `outputs/metrics/splice_relay_probe_500ms_pulse25_summary.json`
- `docs/splice_probe_results.md`

5. Next actions
- The next spatial task is no longer generic UV-grid orientation. It is finer or cell-type-specific column alignment.
- The next temporal task is no longer "is the drift caused by holding the input too long?" It is identifying which recurrent or readout mechanism causes the `500 ms` sign collapse after a correct `100 ms` launch.

## 2026-03-09 - Embodied splice path wired for a real demo

1. Why this new branch exists
- The newest visual splice work until now was body-free only.
- The user requested a real `2 s` demo using the newest splice, so I needed to carry the calibrated splice into the embodied runtime instead of falling back to any `P9` prosthetic or old scalar bridge.

2. What I changed
- Added a new explicit embodied visual-splice injector:
  - `src/bridge/visual_splice.py`
- Extended the fast FlyGym vision path to expose static FlyVis connectome metadata needed for online splice mapping:
  - `src/body/fast_realistic_vision_fly.py`
  - `src/body/interfaces.py`
  - `src/body/flygym_runtime.py`
- Extended the closed-loop bridge to pass signed direct-current splice injections into the real brain backend:
  - `src/bridge/controller.py`
  - `src/runtime/closed_loop.py`
- Added a focused embodied-splice config:
  - `configs/flygym_realistic_vision_splice_axis1d.yaml`
- Added a unit test covering baseline initialization and signed current emission:
  - `tests/test_visual_splice.py`

3. What the new embodied splice mode does
- It does not use `public_p9_context`.
- It does not use `inferred_visual_p9_context`.
- It does not restore decoder or body fallback locomotion.
- It takes the live `nn_activities_arr` from the real FlyVis path, groups that activity at the current best body-free splice boundary, subtracts a reset-frame baseline, and injects signed direct current into exact shared FlyWire `cell_type + side + bin` groups in the whole-brain model.
- The initial embodied mode is deliberately conservative:
  - `axis1d`
  - `4` spatial bins
  - `value_scale = 101.94613788960949`
  - `max_abs_current = 120`
- This is based on the current best body-free calibration result rather than the newer but still sign-broken `uv_grid` branch.

4. Validation before the real run
- Local targeted validation passed:
  - `python -m pytest tests/test_visual_splice.py tests/test_bridge_unit.py tests/test_closed_loop_smoke.py`
  - result: `14 passed`
- Syntax validation passed for the new embodied splice files:
  - `python -m py_compile src/bridge/visual_splice.py src/body/fast_realistic_vision_fly.py src/body/flygym_runtime.py src/bridge/controller.py src/runtime/closed_loop.py`

5. Immediate next action
- Run the real WSL `2 s` FlyGym demo with:
  - `configs/flygym_realistic_vision_splice_axis1d.yaml`
- Save the video, JSONL, and metrics as evidence for whether the embodied splice produces anything stronger than the previous strict twitching regime.

## 2026-03-09 - Real `2 s` embodied demo with the newest splice

1. Run details
- I ran the new embodied splice path in real WSL FlyGym using:
  - `configs/flygym_realistic_vision_splice_axis1d.yaml`
  - `vision_payload_mode: fast`
  - no `P9` prosthetics
  - no decoder or body fallback locomotion
- Command used:
  - `~/.local/bin/micromamba run -n flysim-full python benchmarks/run_fullstack_with_realistic_vision.py --config configs/flygym_realistic_vision_splice_axis1d.yaml --mode flygym --duration 2 --output-root outputs/requested_2s_splice --output-csv outputs/benchmarks/fullstack_splice_axis1d_2s.csv --plot-path outputs/plots/fullstack_splice_axis1d_2s.png`

2. New evidence
- Demo video:
  - `outputs/requested_2s_splice/demos/flygym-demo-20260309-100707.mp4`
- Run log:
  - `outputs/requested_2s_splice/logs/flygym-demo-20260309-100707.jsonl`
- Metrics:
  - `outputs/requested_2s_splice/metrics/flygym-demo-20260309-100707.csv`
- Benchmark CSV:
  - `outputs/benchmarks/fullstack_splice_axis1d_2s.csv`
- Plot:
  - `outputs/plots/fullstack_splice_axis1d_2s.png`

3. What the run shows
- The run completed the full `2.0 s` simulated duration without crashing.
- The embodied splice was active on `999 / 1000` control cycles.
- The decoder produced nonzero commands on `982 / 1000` control cycles.
- The splice never reached the calibrated ceiling:
  - max applied splice current about `25.86`
  - configured clip `120`
- So this was not a saturated all-or-nothing current blast. It was active but moderate.

4. Metrics that matter
- From `outputs/requested_2s_splice/flygym-demo-20260309-100707/summary.json`:
  - `sim_seconds = 2.0`
  - `wall_seconds = 857.132014504`
  - `real_time_factor = 0.0023333628497789155`
  - `avg_forward_speed = 1.0916253476635753`
  - `path_length = 2.1810674446318234`
  - `net_displacement = 0.11315538386569819`
  - `displacement_efficiency = 0.05188073580402254`
  - `stable = 1.0`
- This is the key honest reading:
  - the splice now clearly produces persistent brain-driven command activity in the embodied loop
  - but the resulting motion is still inefficient and locally dithering rather than strong purposeful traversal

5. Extra log summary
- Parsed from `outputs/requested_2s_splice/logs/flygym-demo-20260309-100707.jsonl`:
  - `nonzero_commands = 982`
  - `nonzero_splice_cycles = 999`
  - `mean_left_drive = 0.04577`
  - `mean_right_drive = 0.03830`
- Early cycles confirm the intended initialization:
  - cycle `0`: baseline initialization, zero splice current, zero command
  - cycle `1+`: direct current begins

6. Conclusion
- This is the first real embodied demo in the repo using the newest visual splice path itself rather than a `P9` prosthetic.
- It is a real step forward over strict twitch-only inactivity because the splice is now producing persistent nonzero commands in the embodied loop.
- It is still not a success on meaningful locomotor behavior:
  - net displacement remains very small relative to path length
  - the run is active, but not yet behaviorally correct

7. Next actions
- Compare this embodied splice run against the zero-brain baseline and the previous strict mode using displacement-efficiency, not only path length.
- Then continue `T063` and `T064`, because the remaining blockers still look like:
  - finer or cell-type-specific column alignment
  - downstream recurrent drift / readout mismatch over longer windows

## 2026-03-09 - Why the new embodied splice still fails to locomote

1. What I audited
- I reviewed:
  - `outputs/requested_2s_splice/logs/flygym-demo-20260309-100707.jsonl`
  - `outputs/requested_2s_splice/flygym-demo-20260309-100707/summary.json`
  - `src/bridge/decoder.py`
  - `external/flygym/doc/source/tutorials/vision_basics.rst`
  - `external/flygym/doc/source/tutorials/turning.rst`
  - `external/flygym/flygym/examples/locomotion/turning_fly.py`

2. What is definitely not the problem
- The splice is not dead:
  - `visual_splice.nonzero_root_count > 0` on `999 / 1000` cycles
  - `nonzero_commands = 982 / 1000`
- The software path from brain readout to body command is not disconnected:
  - command sums and asymmetries are driven by the monitored neural rates as expected by `src/bridge/decoder.py`
- So this is not another case of "nothing is wired through."

3. The critical quantitative failure
- The decoded descending drives are far too small for the FlyGym walking interface:
  - `max_left_drive = 0.13965930025907064`
  - `max_right_drive = 0.14243771313159515`
  - mean drives:
    - left `0.04577`
    - right `0.03830`
- FlyGym's own controller documentation says the descending amplitude should not go far beyond `1`, and the vision tutorial's hand-tuned controller uses a range of roughly `0.2` to `1.0`.
- So the new splice is producing real commands, but almost all of them live below the range that normally produces robust walking in `HybridTurningFly`.

4. Why the commands stay tiny
- The decoder reads only a very small DN set:
  - forward: `P9` and `oDN1`
  - turn: `DNa01` and `DNa02`
  - reverse: `MDN`
- Those are aggregated in `src/bridge/decoder.py`.
- In the `2 ms` control window, the monitored rates are sparse and quantized:
  - forward-both-sides active on only `8` cycles
  - forward-left-only on `27`
  - forward-right-only on `99`
  - turn-left-only on `113`
  - turn-right-only on `100`
  - turn-both-sides on `22`
- The decoder then:
  - divides by large scale constants
  - passes through `tanh`
  - low-pass filters with `signal_smoothing_alpha = 0.08`
- Reconstructing the decoder state from the log shows the actual body command never exceeds about `0.142`.
- So the model is not generating a sustained locomotor command. It is generating sparse DN bursts that get smoothed into tiny amplitudes.

5. Why the body barely moves even though commands are nonzero
- The body-level response is weakly aligned with the intended command channels:
  - correlation between drive asymmetry and yaw rate: about `0.033`
  - correlation between total drive and forward speed: about `-0.111`
- Meanwhile the trajectory metrics show local activity, not locomotion:
  - `path_length = 2.1810674446318234`
  - `net_displacement = 0.11315538386569819`
  - `displacement_efficiency = 0.05188073580402254`
  - tiny bounding box:
    - width `0.1385`
    - height `0.0438`
- So the fly is doing leg-level motion and body jitter, but it is not entering a stable translational gait.

6. The broader systems reason
- The current visual splice now reaches the whole brain.
- But the output side is still too compressed and too high-level:
  - thousands of visual neurons are being driven
  - only a handful of descending neurons are read out
  - those few readouts are interpreted as the final 2D FlyGym descending control
- That is likely the wrong abstraction level.
- In other words:
  - software wiring: yes
  - biological/control-semantic wiring: no
- The present output mapping skips the missing VNC / premotor structure and asks a few sparse brain readouts to serve as a full locomotor controller. The logs show that they do not.

7. Bottom line
- The real reason it "won't live" is not that the visual splice is dead.
- It is that the current motor interface is still wrong in practice:
  - wrong output abstraction
  - too few readout neurons
  - too weak and too bursty command amplitudes for the FlyGym walking controller
- So the current failure is more on the output/control side than on the input splice side.

8. Immediate next actions
- Treat `T064` as a motor-readout audit too, not only a recurrent-drift audit.
- Test whether the current DN set is an insufficient output bottleneck by monitoring and decoding a broader descending / relay population before attempting more body runs.

## 2026-03-09 - Expanded readout branch started before touching the splice again

1. Why this branch is next
- The last embodied audit showed the input splice is alive but the output side is too narrow:
  - the brain is active
  - the decoder emits commands
  - but those commands are tiny and do not translate into locomotion
- So I am holding the visual splice fixed and changing only the readout side.

2. What I implemented
- Broadened the decoder so it can consume relay candidates from the grounded splice work:
  - `src/bridge/decoder.py`
- The decoder can now load bilateral relay candidate roots from:
  - `outputs/metrics/splice_relay_candidates.json`
- Added a new experimental readout config:
  - `configs/flygym_realistic_vision_splice_axis1d_expanded_readout.yaml`
- Added a focused unit test for relay-backed decoding:
  - `tests/test_bridge_unit.py`
- Updated bridge construction so the brain backend monitors whatever neuron IDs the decoder now actually needs:
  - `src/runtime/closed_loop.py`

3. Experimental expanded readout choice
- I did not change the visual splice.
- I selected the new relay-backed readout groups from the existing grounded candidate artifact:
  - forward proxy groups:
    - `LC31b`
    - `LCe06`
    - `LT82a`
  - turn proxy group:
    - `LCe06`
- Reason:
  - these groups were already identified structurally as likely relays between the splice boundary and the old DN readout set
  - `LCe06` is the clearest stable left/right-signed candidate in the relay probe
  - `LC31b`, `LCe06`, and `LT82a` all show large sustained bilateral activation that can plausibly carry locomotor context stronger than the old `8`-neuron bottleneck

4. Local validation
- Passed:
  - `python -m pytest tests/test_bridge_unit.py tests/test_closed_loop_smoke.py tests/test_visual_splice.py`
  - result: `15 passed`
- Passed:
  - `python -m py_compile src/bridge/decoder.py src/bridge/controller.py src/runtime/closed_loop.py`

5. Immediate next action
- Run the real embodied `2 s` demo with:
  - `configs/flygym_realistic_vision_splice_axis1d_expanded_readout.yaml`
- Then inspect whether real locomotion emerges before changing the visual splice again.

## 2026-03-09 - Relay-as-motor branch rejected, replaced with strict descending-only readout mining

1. What changed conceptually
- The relay-expanded branch above was explicitly rejected as a final motor semantics branch.
- The user correctly pointed out that optic-lobe / visual relay populations must not be treated as motor outputs.
- I therefore killed the in-flight real WSL relay-expanded run and replaced that branch with a strict descending-only readout pipeline.

2. What I stopped
- Killed the invalid relay-expanded benchmark process in WSL:
  - `wsl bash -lc "pkill -f 'benchmarks/run_fullstack_with_realistic_vision.py --config configs/flygym_realistic_vision_splice_axis1d_expanded_readout.yaml' || true"`
- Kept the files only as diagnostic history:
  - `configs/flygym_realistic_vision_splice_axis1d_expanded_readout.yaml`
- Stopped treating those optic-lobe relay groups as acceptable final motor outputs.

3. What I implemented instead
- Fixed the generic population decoder loader so it accepts either:
  - `cell_type`
  - or `candidate_label`
  - file: `src/bridge/decoder.py`
- Tightened the candidate mining step so it can produce a strict descending-only candidate set:
  - file: `scripts/find_descending_readout_candidates.py`
  - added `--strict-descending-only`
- Re-ran the candidate miner with the strict filter and wrote:
  - `outputs/metrics/descending_readout_candidates_strict.json`
  - `outputs/metrics/descending_readout_candidates_strict_pairs.csv`
  - `outputs/metrics/descending_readout_candidates_strict_roots.csv`
- Added a reproducible selector for supplemental descending forward/turn groups:
  - `scripts/select_descending_readout_groups.py`
  - output: `outputs/metrics/descending_readout_recommended.json`
- Added a descending-only embodied config:
  - `configs/flygym_realistic_vision_splice_axis1d_descending_readout.yaml`
- Tightened the bridge unit coverage so the decoder test now loads `candidate_label` JSON:
  - `tests/test_bridge_unit.py`

4. What the strict public descending candidate set contains
- The strict filter is now:
  - `super_class == descending`
  - `flow == efferent`
  - DN/oDN/MDN-like labels only
- This excludes the earlier tempting but wrong `cL22*` / `VES015` / `VES026` visual-centrifugal cells.
- Highest-scoring bilateral strict descending pairs:
  - `DNp09`
  - `DNp35`
  - `DNp06`
  - `DNpe031`
  - `DNb01`
  - `DNp71`
  - `DNb09`
  - `DNp103`
  - `DNp43`
  - `DNg97`
  - `DNp18`
  - `DNpe056`
  - `DNae002`
  - `DNpe040`
  - `DNpe016`
  - `DNp69`

5. Body-free descending probe
- Ran the strict descending probe in WSL:
  - `scripts/run_descending_readout_probe.py`
- Outputs:
  - `outputs/metrics/descending_readout_probe_strict.csv`
  - `outputs/metrics/descending_readout_probe_strict_pairs.csv`
  - `outputs/metrics/descending_readout_probe_strict_summary.json`
- Important result:
  - the `100 ms` window is useful for selecting supplemental readout groups
  - the `500 ms` window still inherits the previously known recurrent drift problem, so it is not a safe selection window

6. Supplemental descending group selection
- The selector excludes labels already covered by the fixed decoder DN set:
  - `DNp09`
  - `DNg97`
  - `DNa02`
- Recommended supplemental forward groups from `outputs/metrics/descending_readout_recommended.json`:
  - `DNp103`
  - `DNp06`
  - `DNp18`
  - `DNp35`
- Recommended supplemental turn groups:
  - `DNpe056`
  - `DNp71`
  - `DNpe040`

7. Local validation
- Passed:
  - `python -m pytest tests/test_bridge_unit.py -q`
  - result: `7 passed`

## 2026-03-09 - Descending-only embodied readout run succeeded

1. What I ran
- Real WSL embodied run with the strict descending-only expanded readout:
  - `configs/flygym_realistic_vision_splice_axis1d_descending_readout.yaml`
  - command:
    - `python benchmarks/run_fullstack_with_realistic_vision.py --config configs/flygym_realistic_vision_splice_axis1d_descending_readout.yaml --mode flygym --duration 2 --output-root outputs/requested_2s_splice_descending --output-csv outputs/benchmarks/fullstack_splice_descending_2s.csv --plot-path outputs/plots/fullstack_splice_descending_2s.png`

2. Produced artifacts
- Benchmark:
  - `outputs/benchmarks/fullstack_splice_descending_2s.csv`
- Plot:
  - `outputs/plots/fullstack_splice_descending_2s.png`
- Embodied run:
  - `outputs/requested_2s_splice_descending/flygym-demo-20260309-115041/demo.mp4`
  - `outputs/requested_2s_splice_descending/flygym-demo-20260309-115041/run.jsonl`
  - `outputs/requested_2s_splice_descending/flygym-demo-20260309-115041/metrics.csv`
  - `outputs/requested_2s_splice_descending/flygym-demo-20260309-115041/summary.json`
- Comparison artifact versus the earlier splice-only embodied run:
  - `outputs/metrics/descending_readout_comparison.csv`
  - `outputs/metrics/descending_readout_comparison.json`
- Written summary doc:
  - `docs/descending_readout_expansion.md`

3. Quantitative result
- The descending-only run completed the full `2 s`:
  - `stable = 1.0`
  - `completed_full_duration = 1.0`
- It now produces real traversal instead of local dithering:
  - `avg_forward_speed = 4.563790532043783`
  - `path_length = 9.11845348302348`
  - `net_displacement = 5.633006914226428`
  - `displacement_efficiency = 0.6177590229213569`
- Compared with the earlier splice-only embodied run:
  - old `net_displacement = 0.11315538386569819`
  - new `net_displacement = 5.633006914226428`
  - old `displacement_efficiency = 0.05188073580402254`
  - new `displacement_efficiency = 0.6177590229213569`
- Command magnitudes also moved into a much more plausible range:
  - old mean drives:
    - left `0.04576752944365208`
    - right `0.038295875266585365`
  - new mean drives:
    - left `0.31380241125955`
    - right `0.19510758948955362`
  - old max drives:
    - left `0.13965930025907064`
    - right `0.14243771313159515`
  - new max drives:
    - left `0.6430851601651894`
    - right `0.6038926955914254`

4. Why this is materially different from the failed splice-only run
- The visual splice is unchanged.
- The difference is the broadened descending-only readout:
  - fixed DN readout still present
  - plus supplemental descending/efferent populations selected from the body-free descending probe
- The new log shows much stronger neural support on the output side:
  - supplemental forward and turn populations are active
  - body commands are larger and more persistent
  - the fly now traverses space instead of accumulating local jitter

5. What this still does not prove
- It does not prove final biological correctness of the chosen descending readout.
- It does not solve the known longer-window recurrent drift.
- It does not remove the need for a matched `zero_brain` / no-target control on this exact new descending-only branch.
- So this is a grounded improvement, not a final success declaration.

6. Immediate next action
- Add the matched ablation check for the descending-only embodied branch:
  - `T070`

## 2026-03-09 - Visual-drive validation for the descending-only embodied branch

1. What I implemented
- Added a target-free body option to the real FlyGym runtime:
  - `src/body/flygym_runtime.py`
  - `src/runtime/closed_loop.py`
- This allows the same embodied branch to be run either:
  - with the standard public `MovingFlyArena`
  - or on `FlatTerrain` with no target fly at all
- Added matched configs for the descending-only branch:
  - `configs/flygym_realistic_vision_splice_axis1d_descending_readout_zero_brain.yaml`
  - `configs/flygym_realistic_vision_splice_axis1d_descending_readout_no_target.yaml`

2. Validation on the code changes
- Passed:
  - `python -m py_compile src/body/flygym_runtime.py src/runtime/closed_loop.py`
- Passed:
  - `python -m pytest tests/test_bridge_unit.py -q`
  - result: `7 passed`

3. What I ran
- Matched zero-brain control:
  - `outputs/requested_2s_splice_descending_zero_brain/flygym-demo-20260309-122135/demo.mp4`
  - `outputs/requested_2s_splice_descending_zero_brain/flygym-demo-20260309-122135/metrics.csv`
- Matched no-target control:
  - `outputs/requested_2s_splice_descending_no_target/flygym-demo-20260309-122723/demo.mp4`
  - `outputs/requested_2s_splice_descending_no_target/flygym-demo-20260309-122723/metrics.csv`
- Comparison artifact:
  - `outputs/metrics/descending_visual_drive_validation.csv`
  - `outputs/metrics/descending_visual_drive_validation.json`
- Written summary:
  - `docs/descending_visual_drive_validation.md`

4. What the controls show

### Zero-brain control

- `nonzero_command_cycles = 0`
- `net_displacement = 0.011823383234191902`
- `displacement_efficiency = 0.0320475393946615`

This confirms again that the descending-only embodied branch has no hidden locomotor fallback.

### No-target control

- `avg_forward_speed = 3.6971077463080686`
- `net_displacement = 4.938367142047433`
- `displacement_efficiency = 0.6685375152288059`

This is important:
- removing the target does **not** collapse locomotion
- so the moving target is not the only visual source driving the branch
- realistic optic flow / scene structure from the floor and self-motion is enough to keep the branch active

### Target-present branch versus no-target branch

With the moving target present:

- `avg_forward_speed = 4.563790532043783`
- `mean_total_drive = 0.5089100007491035`
- `mean_abs_drive_diff = 0.16774428657780152`

Without the target:

- `avg_forward_speed = 3.6971077463080686`
- `mean_total_drive = 0.436327681959764`
- `mean_abs_drive_diff = 0.12627696034183364`

So the moving target increases:

- forward speed by about `23.44%`
- mean total drive by about `16.63%`
- mean steering asymmetry by about `32.84%`

5. Pursuit-specific analysis
- The current run log does not yet record the target fly state directly.
- But `MovingFlyArena` has a deterministic public trajectory:
  - radius `10`
  - angular speed `15 / 10 = 1.5`
- Using that public trajectory and the logged fly pose from:
  - `outputs/requested_2s_splice_descending/flygym-demo-20260309-115041/run.jsonl`
  I reconstructed target bearing over time and compared it to the steering command.

Results:

- `corr(right_drive - left_drive, target_bearing) = 0.7521880536563109`
- sign match rate between steering command and target bearing = `0.7270875763747454`
- sign opposition rate = `0.2535641547861507`
- `corr(total_drive, target_frontalness) = 0.4949172168385213`
- `corr(total_drive, -abs(target_bearing)) = 0.5246216094922695`

Interpretation:

- steering in the target-present branch is strongly aligned with target bearing
- total forward drive rises when the target becomes more frontal
- this is consistent with the user's observation that the fly accelerates when the target moves into both visual fields

6. Honest conclusion
- I can now support the following claim:
  - the new descending-only embodied branch is brain-driven and visually driven
  - the moving target measurably modulates steering and drive
- I cannot yet claim:
  - the branch is purely target-driven
  - or that the selected descending groups are already the final true biological locomotor code
- The no-target control shows that the branch also responds to the rest of the visual scene, especially self-motion and floor optic flow.

7. Immediate next action
- Add explicit target-state logging and controlled left/right target conditions so pursuit claims no longer depend on reconstructed public arena kinematics:
  - `T071`

## 2026-03-09 - Direct target-state logging and controlled target-condition validation

1. What I attempted
- Added explicit target-state logging to the embodied descending-only splice branch so pursuit claims no longer depend on reconstructing the public `MovingFlyArena` trajectory.
- Added runtime controls for target enable/disable, initial phase, and angular direction so the target can be placed on the left or right deterministically.
- Ran a logged-target rerun of the real `2 s` descending-only embodied branch and generated matched controlled left/right target-condition runs.
- Re-summarized the descending visual-drive evidence using the direct logged target state rather than reconstructed arena kinematics.

2. What succeeded
- The runtime now logs direct target state from simulation physics, including:
  - `target_state.position_x`
  - `target_state.position_y`
  - `target_state.yaw`
  - `target_state.distance`
  - `target_state.bearing_body`
- The following controlled configs now exist:
  - `configs/flygym_realistic_vision_splice_axis1d_descending_readout_zero_brain.yaml`
  - `configs/flygym_realistic_vision_splice_axis1d_descending_readout_no_target.yaml`
  - `configs/flygym_realistic_vision_splice_axis1d_descending_readout_target_left.yaml`
  - `configs/flygym_realistic_vision_splice_axis1d_descending_readout_target_right.yaml`
  - `configs/flygym_realistic_vision_splice_axis1d_descending_readout_stationary_left.yaml`
  - `configs/flygym_realistic_vision_splice_axis1d_descending_readout_stationary_right.yaml`
- The direct logged-target rerun completed and now anchors the pursuit analysis:
  - `outputs/requested_2s_splice_descending_logged_target/flygym-demo-20260309-142600/demo.mp4`
  - `outputs/requested_2s_splice_descending_logged_target/flygym-demo-20260309-142600/run.jsonl`
  - `outputs/requested_2s_splice_descending_logged_target/flygym-demo-20260309-142600/metrics.csv`
- Updated summary artifacts now exist:
  - `outputs/metrics/descending_visual_drive_validation.csv`
  - `outputs/metrics/descending_visual_drive_validation.json`
  - `outputs/metrics/descending_target_conditions.json`
  - `outputs/metrics/descending_stationary_target_conditions.json`
  - `docs/descending_visual_drive_validation.md`

3. What the direct logged-target rerun shows
- With target + real brain:
  - `avg_forward_speed = 4.326325286840003`
  - `net_displacement = 4.943851959931002`
  - `displacement_efficiency = 0.571940438198806`
  - `mean_total_drive = 0.48122784453026124`
  - `mean_abs_drive_diff = 0.18706207480312084`
- Against directly logged target state from the same run:
  - `corr(right_drive - left_drive, target_bearing) = 0.7228049533574713`
  - steer-sign match rate = `0.7476828012358393`
  - steer-sign opposition rate = `0.23274974253347064`
  - `corr(total_drive, target_frontalness) = 0.330852251649671`
  - `corr(forward_speed, target_frontalness) = 0.2452151723394304`
- This removes the old reconstruction dependency from the main pursuit-modulation claim.

4. What the controlled left/right conditions show
- Condition control itself is working:
  - moving-left initial target bearing = `+1.5697550741127948`
  - moving-right initial target bearing = `-1.5755194594138011`
  - stationary-left initial target bearing = `+1.5726071797408192`
  - stationary-right initial target bearing = `-1.5726715812462848`
- The short side-isolated steering result is still mixed:
  - moving-left early mean drive difference = `-0.05511041478293597`
  - moving-right early mean drive difference = `-0.021594800448792844`
  - stationary-left early mean drive difference = `-0.056939209407958435`
  - stationary-right early mean drive difference = `-0.017198015031286273`
- So the repo now has the right instrumentation and deterministic target controls, but the short isolated left/right pursuit reflex is not yet a clean mirrored result.

5. Honest conclusion
- The descending-only branch is still supported as brain-driven and visually driven.
- The continuous target-present run now has direct target-state evidence, not just reconstructed arena kinematics.
- The controlled left/right target placements are now explicit and reproducible.
- The remaining open issue is no longer instrumentation; it is behavioral interpretation, because the short side-isolated left/right steering response is still mixed.

6. Next actions
- Mark `T071` complete because explicit target-state logging and controlled target conditions are now implemented and run.
- Track the remaining side-isolated steering ambiguity separately as a new follow-up task.

## 2026-03-09 - GitHub publishing prep

1. What I attempted
- Audited the workspace for GitHub push blockers after the request to upload the repo.
- Checked whether the workspace was already a Git repository and whether GitHub CLI was available.
- Measured the largest files so the publishable tree could be filtered before initializing Git.

2. What succeeded
- Confirmed the workspace was not yet a Git repository.
- Confirmed `gh` is not installed on this machine, so GitHub repo creation/push must use plain `git` plus a remote URL.
- Added `.gitignore` to exclude content that should not go into normal GitHub history:
  - `external/`
  - `outputs/cache/`
  - generated `*.jsonl`, `*.prof`, `*.pkl`, `*.parquet`, `*.feather`
  - `tests/.tmp/`
- Added `GITHUB_UPLOAD_NOTES.md` documenting exactly what will and will not be pushed.

3. What failed or remains open
- The largest local assets are not pushable as-is to a normal GitHub repo, for example:
  - `outputs/cache/weight_csr.pkl` at about `303 MB`
  - `outputs/cache/weight_coo.pkl` at about `302 MB`
  - `external/fly-brain/data/2025_Connectivity_783.parquet` at about `101 MB`
- Because of that, a literal "upload everything" push is not the right move. The correct move is to push the reproducible repo and keep oversized downloaded/generated assets out of Git history unless the user explicitly wants Git LFS or releases.
- A remote GitHub URL is still needed before the final push command can be run.

4. Evidence paths
- `.gitignore`
- `GITHUB_UPLOAD_NOTES.md`

5. Next actions
- Initialize Git in the workspace.
- Stage the publishable tree under the new ignore rules.
- If the user provides a GitHub remote URL, add it and push the first commit.

## 2026-03-09 - GitHub remote added, local repo committed, push blocked by account mismatch

1. What I attempted
- Initialized Git in `G:\\flysim`, staged the publishable tree under the new ignore rules, and created the first local commit.
- Added the user-provided remote:
  - `https://github.com/jagoff412/openfly`
- Tried both HTTPS and SSH push paths.

2. What succeeded
- Local repo is now initialized and committed:
  - `29d14e5 Initial public flysim reproduction repo`
- The remote is configured and the working tree is clean.
- SSH authentication to GitHub itself works on this machine.

3. What failed
- HTTPS push failed because this machine does not have a usable interactive GitHub credential helper in this shell:
  - `git: 'credential-manager-core' is not a git command`
  - `fatal: could not read Username for 'https://github.com': terminal prompts disabled`
- SSH push also failed, but for a clearer reason:
  - the local SSH key authenticates as GitHub user `jagoff2`
  - the target repo is `jagoff412/openfly`
  - GitHub rejected the push with:
    - `ERROR: Permission to jagoff412/openfly.git denied to jagoff2.`

4. Evidence paths
- `.gitignore`
- `GITHUB_UPLOAD_NOTES.md`
- local commit:
  - `29d14e5`

5. Honest conclusion
- The repo is ready to push technically.
- The remaining blocker is account/auth ownership, not repo state.
- To finish the upload, the authenticated GitHub identity must have write access to `jagoff412/openfly`, or the remote must be changed to a repo owned by `jagoff2`.

## 2026-03-09 - GitHub upload completed

1. What I attempted
- Switched the remote from the mismatched `jagoff412/openfly` repo to the user-provided repo owned by the authenticated account:
  - `git@github.com:jagoff2/openfly.git`
- Retried the push over SSH.

2. What succeeded
- The push completed successfully.
- `main` now tracks `origin/main`.
- Current local commit history pushed:
  - `7098bfa Document GitHub push blocker`
  - `29d14e5 Initial public flysim reproduction repo`

3. Evidence paths
- Remote:
  - `git@github.com:jagoff2/openfly.git`
- Branch:
  - `main`

4. Honest conclusion
- The repo is now uploaded to GitHub.
- The current GitHub remote matches the authenticated account and no longer has the earlier ownership mismatch.

## 2026-03-09 - Public-facing docs refreshed for the current strongest branch

1. What I attempted
- Audited the public-facing docs after the README still described the old strict diagnostic as if it were the current main result.
- Updated the README to describe the actual strongest branch and added exact commands to reproduce the current target/no-target/zero-brain evidence.
- Updated the parity report so it no longer uses the old strict default diagnostic as the main embodied reference.

2. What succeeded
- `README.md` now:
  - states that the strongest current branch is `configs/flygym_realistic_vision_splice_axis1d_descending_readout.yaml`
  - points readers to the current strongest demo and control artifacts
  - documents exact reproduction commands for:
    - target + real brain
    - no target + real brain
    - target + zero brain
    - controlled target-side follow-ups
- `REPRO_PARITY_REPORT.md` now:
  - promotes the descending-only embodied splice branch into the main parity narrative
  - marks locomotion and reaction-to-visual-stimulus according to the current stronger evidence
  - keeps the remaining open issues focused on biological correctness and mixed short left/right side conditions

3. Honest conclusion
- The public-facing docs are now aligned with the current evidence instead of the older strict-only failure mode.
- The remaining open claims are still clearly limited:
  - current strongest branch is brain-driven and visually driven
  - but not yet a final proof of the exact biological motor code or a clean mirrored short side-specific pursuit reflex

## 2026-03-09 - Paper-grounded feeding and grooming brain tasks added

1. What I attempted
- Added the two public Shiu-paper sensorimotor tasks as runnable brain-only probes:
  - feeding
  - grooming
- Kept them grounded in the public notebook IDs already present in the checked-out `fly-brain` repo.
- Kept them explicitly brain-only so they are ready for later embodiment experiments without pretending the body-side interfaces already exist.

2. What succeeded
- Added grounded task ID definitions:
  - `src/brain/paper_task_ids.py`
- Added reusable probe logic:
  - `src/brain/paper_task_probes.py`
- Added runnable scripts:
  - `scripts/run_feeding_probe.py`
  - `scripts/run_grooming_probe.py`
- Added test coverage:
  - `tests/test_paper_task_ids.py`
- Added documentation:
  - `docs/feeding_and_grooming_brain_tasks.md`
- Generated initial local artifacts:
  - `outputs/metrics/feeding_probe.csv`
  - `outputs/metrics/feeding_probe_summary.json`
  - `outputs/plots/feeding_probe.png`
  - `outputs/metrics/grooming_probe.csv`
  - `outputs/metrics/grooming_probe_summary.json`
  - `outputs/plots/grooming_probe.png`
  - `outputs/metrics/grooming_probe_500ms.csv`
  - `outputs/metrics/grooming_probe_500ms_summary.json`
  - `outputs/plots/grooming_probe_500ms.png`

3. What the first local probe results show
- Feeding:
  - the right-hemisphere sugar GRN set produces a clear `MN9` response in the short `100 ms` sweep
  - strongest observed row:
    - `sugar_right @ 180 Hz`
    - `mn9_left = 60 Hz`
    - `mn9_right = 40 Hz`
    - `mn9_total = 100 Hz`
  - the left-hemisphere sugar set stayed silent in that same short window
- Grooming:
  - the short `100 ms` sweep shows `aBN1` activation under `JON_CE` and `JON_all`
  - the short `100 ms` sweep does not show `aDN1` spiking
  - the longer `500 ms` follow-up does show a weaker downstream grooming response:
    - `jon_all @ 220 Hz` gives `aDN1_right = 6 Hz` and `aBN1 = 28 Hz`

4. Honest conclusion
- These tasks are now added as grounded brain-side probes.
- They are useful and reproducible today.
- They are not yet embodied behaviors.
- The next embodiment step is now narrower and cleaner:
  - map body-side gustatory/contact state into the published sugar/JON inputs
  - then map `MN9` / `aDN1` / `aBN1` into actual proboscis or grooming actuation interfaces

## 2026-03-10 - Journal-style whitepaper draft added

1. What I attempted
- Consolidated the repo's architecture, benchmark evidence, negative findings, splice-discovery work, embodied validation, and feeding/grooming brain tasks into one long-form publication-style document.
- Kept the write-up aligned with `AGENTS.MD`: evidence-heavy, explicit about remaining gaps, and careful not to overclaim exact Eon parity.

2. What succeeded
- Added `docs/openfly_whitepaper.md`.
- The document includes:
  - abstract and scope
  - architecture and methods
  - benchmark and profiler results
  - failure analysis of the original scalar public-anchor bridge
  - body-free visual splice discovery and calibration results
  - descending-only embodied readout expansion
  - matched `zero_brain`, no-target, and logged-target validation results
  - feeding and grooming brain-task probe results
  - limitations, next steps, and exact reproduction commands

3. Honest conclusion
- The whitepaper does not claim that the repo has solved final biological motor semantics or exact private-demo parity.
- It does capture the strongest supported current claim:
  - the repo now has a realistic-vision, whole-brain, embodied closed loop whose strongest current branch is brain-driven and visually driven under matched controls.
- It also preserves the key negative findings that shaped the architecture, which are necessary for an honest technical record.

## 2026-03-10 - Whitepaper signed, README archived, and repo landing page replaced

1. What I attempted
- Added explicit authorship metadata to the new whitepaper.
- Archived the previous operational `README.md`.
- Replaced the repo root `README.md` with the whitepaper content as requested.
- Prepared the doc update for GitHub push.

2. What succeeded
- `docs/openfly_whitepaper.md` now carries explicit `Author: Codex` metadata.
- The prior operational README is preserved at:
  - `docs/README_legacy.md`
- `README.md` now mirrors the whitepaper so the GitHub landing page presents the full long-form technical write-up instead of the shorter operational README.

3. Honest conclusion
- This changes the public presentation layer, not the experimental evidence.
- The old operational README is still preserved in-repo, so replication instructions and prior structure are not lost.

## 2026-03-10 - Reviewed new Eon embodiment update against local results

1. What I attempted
- Reviewed the new Eon update at `https://eon.systems/updates/embodied-brain-emulation`.
- Followed the main method-bearing links from the post:
  - Shiu brain-model paper
  - whole-brain connectome and annotation papers
  - FlyVis paper
  - NeuroMechFly v2 paper
  - NeuroMechFly advanced-vision docs
  - NeuroMechFly controller docs
- Compared the disclosed Eon architecture to the current strongest local branch and wrote the result into the repo.

2. What succeeded
- Added `docs/eon_embodiment_update_review_2026-03-10.md`.
- Main comparison result:
  - the new Eon post largely confirms our later diagnosis that the hard problem is the interface between vision, brain, and embodied controllers
  - it also confirms that their current embodiment is still controller-mediated and heuristic
  - they explicitly state that visual input is not yet significantly influencing their current embodied behavior
  - our strongest current local branch still has stronger target-vs-control evidence for visual drive

3. Honest conclusion
- The new Eon post does not reveal a hidden fully biological end-to-end controller that would invalidate the local reconstruction strategy here.
- It instead supports the view that the public brain core is only one part of the problem and that the unresolved splice/output interface is the real systems bottleneck.

## 2026-03-10 - Eon comparison integrated into whitepaper and pushed

1. What I attempted
- Added the new Eon-update comparison into the main whitepaper so the repo has one long-form document that includes both the local results and the subsequent public Eon disclosure.
- Prepared the new review doc, updated trackers, and pushed the documentation update to GitHub.

2. What succeeded
- `docs/openfly_whitepaper.md` now has a dedicated section comparing this repo to the later Eon embodiment update.
- `docs/eon_embodiment_update_review_2026-03-10.md` remains as the standalone comparison note.
- The doc update was committed and pushed to `origin/main`.

3. Honest conclusion
- The comparison section does not claim the local repo exceeds Eon in every way.
- It makes the narrower supported point:
  - the later Eon post largely confirms that the unresolved interface between vision, brain, and embodied control is the real bottleneck, and that the current disclosed embodiment remains controller-mediated rather than a fully solved biological motor stack.

## 2026-03-10 - README synced again to the latest whitepaper

1. What I attempted
- Checked whether the repo-home `README.md` still matched `docs/openfly_whitepaper.md` after the Eon comparison section was added.
- Found that `README.md` was stale relative to the updated whitepaper.
- Re-synced the root README so the GitHub landing page reflects the latest whitepaper text.

2. What succeeded
- `README.md` now matches `docs/openfly_whitepaper.md`, including the Eon comparison section.

3. Honest conclusion
- This was a presentation-layer sync only.
- No experimental claims or artifacts changed.

## 2026-03-11 - T063 review and restart

1. What I attempted
- Re-read `TASKS.md`, `PROGRESS_LOG.md`, `docs/visual_splice_strategy.md`, `docs/cold_start_visual_brain_plan.md`, and `docs/splice_probe_results.md` after context compaction.
- Re-inspected the current alignment code in `src/brain/flywire_annotations.py` and the body-free splice harness in `scripts/run_splice_probe.py` before making changes.

2. What succeeded
- Reconstructed the current state accurately enough to resume `T063` on the right branch.
- Confirmed that the current `uv_grid` alignment only supports global axis swap / flip plus side-specific horizontal mirroring.
- Confirmed the current blocker: boundary agreement is already strong, but downstream sign remains wrong, so the next step has to be per-cell-type alignment rather than another global transform.

3. What failed
- No new alignment improvement has been implemented yet in this entry; this is the restart checkpoint before code changes.

4. Evidence paths
- `TASKS.md`
- `PROGRESS_LOG.md`
- `docs/visual_splice_strategy.md`
- `docs/cold_start_visual_brain_plan.md`
- `docs/splice_probe_results.md`
- `src/brain/flywire_annotations.py`
- `scripts/run_splice_probe.py`

5. Next actions
- Implement a per-cell-type spatial-alignment path beyond the shared coarse UV grid.
- Re-run targeted body-free splice probes and compare them against the current best targeted `uv_grid` summary.

## 2026-03-11 - T063 completed with per-cell-type UV-grid alignment

1. What I attempted
- Added a per-cell-type spatial-transform path on the whole-brain side so the `uv_grid` splice is no longer limited to one global transform plus optional right-side mirroring.
- Added a dedicated body-free search script to greedily test per-cell-type `swap_uv` / `flip_u` / `flip_v` / `mirror_u_by_side` overrides against the grounded FlyVis teacher response.
- Re-ran a canonical `run_splice_probe.py` body-free summary using the recommended per-cell-type transform file.

2. What succeeded
- Added per-cell-type transform support in:
  - `src/brain/flywire_annotations.py`
  - `src/bridge/visual_splice.py`
  - `scripts/run_splice_probe.py`
- Added the dedicated search harness:
  - `scripts/run_celltype_uvgrid_alignment_search.py`
- Added unit coverage for the new per-cell-type transform override path:
  - `tests/test_flywire_annotations.py`
- Host validation passed:
  - `python -m pytest tests/test_flywire_annotations.py tests/test_visual_splice.py -q`
  - result: `8 passed`
- The body-free search found a sign-correct per-cell-type alignment starting from the old best global UV-grid transform:
  - `outputs/metrics/splice_celltype_alignment_search.json`
  - `outputs/metrics/splice_celltype_alignment_recommended.json`
- Key search result:
  - old best global UV-grid:
    - left turn bias `-15`
    - right turn bias `-5`
    - `sign_match = false`
  - new per-cell-type alignment search best:
    - left turn bias `-50`
    - right turn bias `+60`
    - `sign_match = true`
- A canonical re-run with the recommended transform file also preserved the correct downstream sign:
  - `outputs/metrics/splice_probe_uvgrid_celltype_aligned_summary.json`
  - left turn bias `-30`
  - right turn bias `+45`

3. What failed
- The canonical re-run did not keep the exact same boundary-correlation numbers reported by the greedy search summary.
- It still fixed the downstream sign cleanly, but the averaged voltage correlations in the canonical summary were slightly lower than the search-internal best score.
- So `T063` is solved at the level it was asked:
  - per-cell-type alignment can resolve the coarse downstream sign error
- but the result still needs embodied validation and does not replace `T064`.

4. Evidence paths
- `src/brain/flywire_annotations.py`
- `src/bridge/visual_splice.py`
- `scripts/run_splice_probe.py`
- `scripts/run_celltype_uvgrid_alignment_search.py`
- `tests/test_flywire_annotations.py`
- `tests/test_visual_splice.py`
- `outputs/metrics/splice_celltype_alignment_search.json`
- `outputs/metrics/splice_celltype_alignment_recommended.json`
- `outputs/metrics/splice_probe_uvgrid_celltype_aligned_summary.json`
- `outputs/metrics/splice_celltype_alignment_comparison.json`

5. Next actions
- Keep `T064` active: explain the `500 ms` recurrent sign collapse now that the coarse spatial sign error is no longer the main blocker.
- Add an embodied follow-up using the new per-cell-type UV-grid transform file in the descending-only branch.

## 2026-03-11 - T064 restart after the per-cell-type splice fix

1. What I attempted
- Re-opened the existing drift evidence after closing `T063`:
  - `outputs/metrics/splice_relay_drift_comparison.json`
  - `outputs/metrics/splice_relay_probe_summary.json`
  - `outputs/metrics/splice_relay_probe_500ms_pulse25_summary.json`
- Re-inspected the current body-free relay probe implementation in `scripts/run_splice_relay_probe.py`.
- Re-checked the fixed motor readout definitions in `src/brain/public_ids.py` and the supplemental descending candidate file in `outputs/metrics/descending_readout_candidates_strict.json`.

2. What succeeded
- Confirmed the key structural gap in the old relay-drift probe:
  - it only reports endpoint windows
  - and it only watches the fixed tiny DN readout plus a small relay set
- Confirmed that `T064` now needs time-resolved evidence, especially after `T063` proved the coarse input-side sign error is fixable.
- Narrowed the mechanistic possibilities to:
  - fixed DN readout collapse while deeper relay or supplemental descending groups remain sign-correct
  - broader descending-path collapse
  - or a true recurrent attractor that erases asymmetry across all monitored groups

3. What failed
- No mechanistic explanation is claimed yet in this entry; this is the restart checkpoint before the new audit script lands.

4. Evidence paths
- `outputs/metrics/splice_relay_drift_comparison.json`
- `outputs/metrics/splice_relay_probe_summary.json`
- `outputs/metrics/splice_relay_probe_500ms_pulse25_summary.json`
- `outputs/metrics/splice_probe_uvgrid_celltype_aligned_summary.json`
- `scripts/run_splice_relay_probe.py`
- `src/brain/public_ids.py`
- `outputs/metrics/descending_readout_candidates_strict.json`

5. Next actions
- Add a time-resolved body-free drift audit that monitors:
  - relay groups
  - fixed motor DN groups
  - supplemental descending/efferent candidates
- Run that audit on the new sign-correct per-cell-type splice and use it to explain whether the `500 ms` collapse is mainly a readout issue or a broader recurrent drift.

## 2026-03-11 - T064 completed with a time-resolved body-free drift audit

1. What I attempted
- Added a new time-resolved body-free audit script:
  - `scripts/run_splice_drift_audit.py`
- Ran it in WSL on the sign-correct per-cell-type UV-grid splice:
  - `outputs/metrics/splice_celltype_alignment_recommended.json`
- Measured two schedules:
  - sustained `hold`
  - `pulse_25ms`
- Monitored:
  - relay groups from `outputs/metrics/splice_relay_candidates.json`
  - the fixed tiny DN readout from `src/brain/public_ids.py`
  - the broader strict descending/efferent groups from `outputs/metrics/descending_readout_candidates_strict.json`

2. What succeeded
- Generated the audit artifacts:
  - `outputs/metrics/splice_drift_audit_summary.json`
  - `outputs/metrics/splice_drift_audit_timeseries.csv`
  - `outputs/metrics/splice_drift_audit_key_findings.json`
  - `outputs/metrics/splice_drift_audit_key_findings.csv`
- Added the write-up:
  - `docs/splice_drift_audit.md`
- The audit gives a stronger mechanistic answer than the old endpoint-only relay probe:
  - under sustained input, relay asymmetry does **not** collapse by `500 ms`
  - several broader descending groups also remain asymmetric by `500 ms`
  - but the original tiny fixed DN turn readout equalizes to zero by `500 ms`
- Key sustained-input numbers:
  - fixed DN turn bias at `100 ms`:
    - left `-40`
    - right `+100`
  - fixed DN turn bias at `500 ms`:
    - left `0`
    - right `0`
- Key relay persistence examples under sustained input:
  - `LC31a` contrastive right-minus-left:
    - `100 ms`: `+14.53`
    - `500 ms`: `+13.81`
  - `LC31b`:
    - `100 ms`: `+24.44`
    - `500 ms`: `+22.63`
  - `LCe04`:
    - `100 ms`: `+5.88`
    - `500 ms`: `+5.90`
- Key pulse result:
  - after a `25 ms` pulse, both relay and descending contrastive signals decay essentially to zero by `500 ms`
  - so the current public dynamics do not maintain a strong self-sustaining visuomotor state after a brief launch pulse

3. Honest conclusion
- The old `500 ms` sign collapse was **not** a complete splice failure.
- It is better explained by two effects:
  1. the fixed tiny DN readout is too brittle and equalizes under sustained drive
  2. the current public recurrent dynamics do not preserve the launched asymmetry once the external input is removed
- So the remaining blocker is now narrower and more concrete:
  - not "the whole network loses asymmetry by `500 ms`"
  - but "the tiny DN readout is insufficient for long-window interpretation, and there is no strong self-sustaining state after a short pulse"

4. Evidence paths
- `scripts/run_splice_drift_audit.py`
- `outputs/metrics/splice_drift_audit_summary.json`
- `outputs/metrics/splice_drift_audit_timeseries.csv`
- `outputs/metrics/splice_drift_audit_key_findings.json`
- `docs/splice_drift_audit.md`

5. Next actions
- Test the new per-cell-type UV-grid splice directly in the embodied descending-only branch rather than through the old tiny DN set.
- Keep long-window state-conditioning questions separate from output-readout questions in future embodiment claims.

## 2026-03-11 - T083 started with matched embodied UV-grid descending configs

1. What I attempted
- Began the embodied follow-up after `T064`.
- Created a matched config set that swaps the old axis1d splice for the new per-cell-type UV-grid splice while keeping the widened descending-only decoder path fixed.

2. What succeeded
- Added:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_no_target.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_zero_brain.yaml`
- These configs use:
  - `spatial_mode: uv_grid`
  - `spatial_u_bins: 2`
  - `spatial_v_bins: 2`
  - `spatial_flip_v: true`
  - `spatial_mirror_u_by_side: true`
  - `spatial_cell_type_transforms_path: outputs/metrics/splice_celltype_alignment_recommended.json`
- They keep the widened descending-only decoder unchanged so the embodied comparison isolates the input-splice change as cleanly as possible.

3. What failed
- No embodied run result yet in this entry; this is the configuration checkpoint before the matched WSL runs.

4. Evidence paths
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_no_target.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_zero_brain.yaml`
- `outputs/metrics/splice_celltype_alignment_recommended.json`

5. Next actions
- Run the matched real WSL target, no-target, and zero-brain embodied UV-grid descending tests sequentially.
- Summarize them against the existing axis1d descending branch with the same visual-drive metrics.

## 2026-03-11 - T082 and T083 completed with matched embodied UV-grid descending runs

1. What I attempted
- Ran the matched embodied comparison for the new per-cell-type UV-grid splice using the widened descending-only decoder:
  - target + real brain
  - no target + real brain
  - target + zero brain
- Then summarized those runs with the same visual-drive metrics used for the current axis1d descending baseline.

2. What succeeded
- Completed all three embodied WSL runs:
  - `outputs/requested_2s_splice_uvgrid_descending_target/flygym-demo-20260311-062430/demo.mp4`
  - `outputs/requested_2s_splice_uvgrid_descending_no_target/flygym-demo-20260311-063926/demo.mp4`
  - `outputs/requested_2s_splice_uvgrid_descending_zero_brain/flygym-demo-20260311-065432/demo.mp4`
- Generated matched summaries:
  - `outputs/metrics/descending_uvgrid_visual_drive_validation.csv`
  - `outputs/metrics/descending_uvgrid_visual_drive_validation.json`
  - `outputs/metrics/descending_uvgrid_vs_axis1d_comparison.csv`
  - `outputs/metrics/descending_uvgrid_vs_axis1d_comparison.json`
- Wrote the embodied comparison doc:
  - `docs/descending_uvgrid_visual_drive_validation.md`

3. What failed
- The per-cell-type UV-grid splice did not improve the embodied branch over the current axis1d descending baseline.
- In the target condition, the UV-grid branch regressed on the most important embodied pursuit metrics:
  - target-bearing steering correlation dropped from `0.7228` to `0.4590`
  - steer-sign match dropped from `0.7477` to `0.6527`
  - average forward speed dropped from `4.3263` to `3.6652`
  - net displacement dropped from `4.9439` to `4.2834`
- Within the UV-grid branch itself, the moving target no longer improves forward speed over the no-target condition:
  - target `avg_forward_speed = 3.6652`
  - no-target `avg_forward_speed = 3.6751`

4. Evidence paths
- `outputs/metrics/descending_uvgrid_visual_drive_validation.json`
- `outputs/metrics/descending_uvgrid_vs_axis1d_comparison.json`
- `docs/descending_uvgrid_visual_drive_validation.md`
- `outputs/requested_2s_splice_uvgrid_descending_target/flygym-demo-20260311-062430/summary.json`
- `outputs/requested_2s_splice_uvgrid_descending_no_target/flygym-demo-20260311-063926/summary.json`
- `outputs/requested_2s_splice_uvgrid_descending_zero_brain/flygym-demo-20260311-065432/summary.json`

5. Honest conclusion
- The body-free per-cell-type UV-grid splice solved the sign problem at the splice boundary, but that improvement did not transfer into a stronger embodied descending-only controller.
- The embodied UV-grid branch is still brain-driven, because the zero-brain control remains near-zero.
- But the current best embodied production path is still the simpler axis1d descending splice, not the new per-cell-type UV-grid branch.

6. Next actions
- Keep the per-cell-type UV-grid splice as an experimental branch, not the default embodied path.
- Focus the next iteration on why the body-free splice gain does not survive embodiment:
  - likely downstream calibration, decoder weighting, or time-scale mismatch
- Use the axis1d descending branch as the current embodied reference until the UV-grid branch exceeds it on target-bearing correlation and target-vs-no-target modulation.

## 2026-03-11 - T084 started with UV-grid-specific decoder calibration

1. What I attempted
- Reopened the UV-grid embodied branch specifically at the decoder / downstream calibration layer instead of changing the splice again.
- Compared the current UV-grid target log against the axis1d target log to identify which signal statistics actually regressed.

2. What succeeded
- Confirmed that the main UV-grid regression is not total brain silence:
  - the branch still has `993` nonzero command cycles in the `2 s` target run
- Confirmed that the UV-grid branch is under-driving and under-steering relative to axis1d:
  - mean total drive dropped from about `0.4812` to about `0.4442`
  - mean absolute drive difference dropped from about `0.1871` to about `0.1078`
  - target-bearing correlation dropped from about `0.7228` to about `0.4590`
- Ran an offline replay sweep over decoder-only parameters using the saved UV-grid target and no-target logs.
- The first promising decoder candidate from that replay uses:
  - lower smoothing (`alpha ≈ 0.06`)
  - stronger output gains
  - nonzero `forward_asymmetry_turn_gain`

3. What failed
- Nothing new is claimed yet at the embodied level in this entry.
- This is the calibration setup checkpoint before the embodied rerun.

4. Evidence paths
- `outputs/requested_2s_splice_uvgrid_descending_target/flygym-demo-20260311-062430/run.jsonl`
- `outputs/requested_2s_splice_uvgrid_descending_no_target/flygym-demo-20260311-063926/run.jsonl`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout.yaml`

5. Next actions
- Preserve the offline decoder sweep as a reproducible script and artifact.
- Create a UV-grid-specific calibrated config.
- Rerun the embodied UV-grid target branch first, then matched no-target / zero-brain if the target rerun improves materially.

## 2026-03-11 - T084 completed with a calibrated UV-grid embodied branch

1. What I attempted
- Added a reproducible offline decoder replay sweep for the UV-grid target and no-target logs.
- Used that sweep to pick a UV-grid-specific decoder candidate.
- Ran matched embodied `target`, `no_target`, and `zero_brain` validations for the calibrated UV-grid branch.

2. What succeeded
- Added:
  - `scripts/run_uvgrid_decoder_calibration.py`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_zero_brain.yaml`
  - `docs/uvgrid_decoder_calibration.md`
- Added a decoder unit test for forward-asymmetry steering:
  - `tests/test_bridge_unit.py`
- Offline sweep artifacts:
  - `outputs/metrics/uvgrid_decoder_calibration.csv`
  - `outputs/metrics/uvgrid_decoder_calibration.json`
  - `outputs/metrics/uvgrid_decoder_calibration_best.json`
- Matched embodied artifacts:
  - `outputs/requested_2s_splice_uvgrid_descending_calibrated_target/flygym-demo-20260311-071452/demo.mp4`
  - `outputs/requested_2s_splice_uvgrid_descending_calibrated_no_target/flygym-demo-20260311-073028/demo.mp4`
  - `outputs/requested_2s_splice_uvgrid_descending_calibrated_zero_brain/flygym-demo-20260311-074301/demo.mp4`
- Matched summaries:
  - `outputs/metrics/descending_uvgrid_calibrated_visual_drive_validation.json`
  - `outputs/metrics/descending_uvgrid_calibration_comparison.json`

3. Key result
- The calibrated UV-grid branch is now stronger than both:
  - the old UV-grid branch
  - the old axis1d descending branch

Target-run gains versus the old UV-grid branch:
- `avg_forward_speed`: `3.6652 -> 4.9241`
- `net_displacement`: `4.2834 -> 5.7583`
- `corr_drive_diff_vs_target_bearing`: `0.4590 -> 0.8810`
- `steer_sign_match_rate`: `0.6527 -> 0.8878`

Target-run gains versus the old axis1d branch:
- `avg_forward_speed`: `4.3263 -> 4.9241`
- `net_displacement`: `4.9439 -> 5.7583`
- `corr_drive_diff_vs_target_bearing`: `0.7228 -> 0.8810`
- `steer_sign_match_rate`: `0.7477 -> 0.8878`

4. Control result
- The calibrated `zero_brain` branch remains near-zero:
  - `nonzero_command_cycles = 0`
  - `net_displacement = 0.011823383234191902`

5. Honest conclusion
- The earlier embodied UV-grid failure was not inherent to the per-cell-type splice.
- It was largely a decoder/downstream calibration mismatch.
- After UV-grid-specific calibration, the per-cell-type UV-grid branch becomes the strongest embodied branch currently in the repo.

6. Next actions
- Update the public-facing docs so they no longer name the old axis1d branch as the current strongest result.
- Keep the remaining biological caveats explicit:
  - still a descending-population-to-two-drive abstraction
  - still not pure target pursuit
  - still not a VNC / muscle-level motor pathway

## 2026-03-11 - T085 published the calibrated UV-grid branch to GitHub

1. What I attempted
- Prepared the repo for publish after the UV-grid calibration work.
- Verified whether `README.md` needed another manual sync from `docs/openfly_whitepaper.md`.

2. What succeeded
- Verified that `README.md` already matched `docs/openfly_whitepaper.md` byte-for-byte.
- Kept that synced state unchanged.
- Committed the calibrated UV-grid branch updates, docs, configs, scripts, and artifacts.
- Pushed the new state to `origin/main`.

3. What failed
- Nothing. The remote was already configured correctly and the push path was clean.

4. Evidence paths
- `README.md`
- `docs/openfly_whitepaper.md`
- `git remote -v`
- `git log --oneline -1`

5. Result
- The GitHub repo now reflects the calibrated UV-grid branch as the current strongest embodied result.
