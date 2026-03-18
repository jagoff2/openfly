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
- I have not yet completed the â€œlongest stableâ€ real FlyGym parity run or updated the final parity report / README with these new measurements.

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

## 2026-03-18 - Living-branch mesoscale spontaneous-state validation

1. What I attempted
- Fixed the spontaneous-data validation seam on the living branch instead of treating mesoscale validation as a pure literature note.
- Added a public spontaneous-dataset registry plus a deterministic metadata fetch path for Aimon 2023 Dryad and related spontaneous-state anchors.
- Staged the Aimon 2023 `README.md` and `GoodICsdf.pkl` artifacts that were actually obtainable in this environment.
- Implemented a living-branch mesoscale validator over the spontaneous-refit `target` / `no_target` pair using run logs, activation captures, the FlyWire annotation supplement, and completeness ordering.
- Ran focused tests, metadata fetch, and the full validation script.

2. What succeeded
- The repo now has a real spontaneous-dataset source registry:
  - `src/brain/spontaneous_data_sources.py`
- The repo now has reusable public-dataset inspectors:
  - `src/analysis/public_spontaneous_dataset.py`
- The repo now fetches and records Aimon 2023 Dryad metadata and access status:
  - `scripts/fetch_spontaneous_public_data.py`
  - `external/spontaneous/aimon2023_dryad/spontaneous_public_dataset_aimon2023_dryad_manifest.json`
  - `external/spontaneous/aimon2023_dryad/spontaneous_public_dataset_aimon2023_dryad_access_report.json`
- The repo now stages the small Aimon 2023 artifacts already obtained:
  - `external/spontaneous/aimon2023_dryad/README.md`
  - `external/spontaneous/aimon2023_dryad/GoodICsdf.pkl`
- The first living-branch mesoscale validation bundle now exists:
  - `scripts/run_spontaneous_mesoscale_validation.py`
  - `src/analysis/spontaneous_mesoscale_validation.py`
  - `outputs/metrics/spontaneous_mesoscale_validation_summary.json`
  - `outputs/metrics/spontaneous_mesoscale_validation_components.csv`
  - `outputs/metrics/spontaneous_mesoscale_target_family_turn_table.csv`
  - `outputs/metrics/spontaneous_mesoscale_no_target_family_turn_table.csv`
  - `outputs/plots/spontaneous_mesoscale_onset_curves.png`
  - `outputs/plots/spontaneous_mesoscale_bilateral_corr_hist.png`
  - `outputs/plots/spontaneous_mesoscale_turn_family_corr.png`
- Current living-branch mesoscale result:
  - non-quiescent awake state: pass
  - matched living baseline: pass
  - walk-linked global modulation: pass
  - bilateral family coupling: pass
  - residual high-dimensional structure: pass
  - residual temporal structure: pass
  - turn-linked spatial heterogeneity: pass
  - forced-vs-spontaneous walk similarity: not yet evaluated
  - connectome-function correspondence: not yet evaluated
- Focused validation passed:
  - `18 passed` across the new spontaneous-data and mesoscale-validation tests plus the existing spontaneous-state and living-activation tests

3. What failed
- Dryad direct file API endpoints still return `401 Unauthorized` in scripted checks from this environment.
- The large Aimon 2023 bundles are still not staged locally:
  - `Walk_anatomical_regions.zip`
  - `Walk_components.zip`
  - `Additional_data.zip`
- So the current mesoscale pass is strong and useful, but it is still based on:
  - living-branch run outputs
  - public literature anchors
  - public Dryad metadata
  - small local Aimon 2023 metadata artifacts
  rather than the full public regional/component timeseries bundles.

4. Evidence paths
- `docs/spontaneous_mesoscale_validation.md`
- `external/spontaneous/aimon2023_dryad/local_dataset_summary.json`
- `external/spontaneous/aimon2023_dryad/spontaneous_public_dataset_aimon2023_dryad_manifest.json`
- `external/spontaneous/aimon2023_dryad/spontaneous_public_dataset_aimon2023_dryad_access_report.json`
- `outputs/metrics/spontaneous_mesoscale_validation_summary.json`
- `outputs/metrics/spontaneous_mesoscale_validation_components.csv`
- `outputs/plots/spontaneous_mesoscale_onset_curves.png`
- `outputs/plots/spontaneous_mesoscale_bilateral_corr_hist.png`
- `outputs/plots/spontaneous_mesoscale_turn_family_corr.png`

5. Next actions
- Add a forced-walk assay so the living branch can be judged against the Aimon 2023 spontaneous-vs-forced mesoscale comparison directly.
- Add a connectome-to-functional-coupling comparison layer for the living branch.
- Stage and ingest the full Aimon 2023 regional/component bundles when a deterministic public download path is made reliable enough for this repo.

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
  - lower smoothing (`alpha â‰ˆ 0.06`)
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

## 2026-03-11 - T086 started on the motor-interface bottleneck

1. What I attempted
- Reopened the current strongest calibrated UV-grid branch specifically at the output side.
- Reviewed:
  - `src/bridge/decoder.py`
  - `src/body/interfaces.py`
  - `src/body/flygym_runtime.py`
  - `src/body/brain_only_realistic_vision_fly.py`
  - `docs/near_term_multidrive_plan.md`
- Compared the current body interface against the original FlyGym `HybridTurningFly` controller semantics.

2. What succeeded
- Confirmed that the current strongest branch is still compressing all descending activity into only:
  - `left_drive`
  - `right_drive`
- Confirmed that this remains the largest structural mismatch to fuller embodiment:
  - the controller underneath already has richer internal state
  - but the repo still addresses it through a two-scalar throttle-like interface
- Confirmed that the most plausible near-term fix is still the one already outlined in:
  - `docs/near_term_multidrive_plan.md`
  - namely a hybrid motor-latent interface that modulates:
    - left/right CPG amplitude
    - left/right CPG frequency
    - correction-rule gains
    - reverse gating

3. What failed
- No new embodied claim is made in this checkpoint.
- This entry is only the start of the motor-interface expansion.

4. Evidence paths
- `docs/near_term_multidrive_plan.md`
- `src/bridge/decoder.py`
- `src/body/interfaces.py`
- `src/body/flygym_runtime.py`
- `src/body/brain_only_realistic_vision_fly.py`

5. Next actions
- Implement a richer command dataclass and a FlyGym-side controller that accepts motor latents rather than only two descending drives.
- Keep the visual splice fixed.
- Revalidate against matched `target`, `no_target`, and `zero_brain` controls.

## 2026-03-11 - T086 and T087 completed with the first hybrid motor-latent branch

1. What I attempted
- Implemented a richer controller-facing motor interface instead of the current two-drive bottleneck.
- Added matched embodied `target`, `no_target`, and `zero_brain` runs for the new branch.
- Compared the new branch directly against the current calibrated two-drive UV-grid baseline.

2. What succeeded
- Added:
  - `src/body/connectome_turning_fly.py`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_no_target.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_zero_brain.yaml`
  - `configs/mock_multidrive.yaml`
  - `docs/multidrive_decoder_validation.md`
- Updated:
  - `src/body/interfaces.py`
  - `src/bridge/decoder.py`
  - `src/body/flygym_runtime.py`
  - `src/body/fast_realistic_vision_fly.py`
  - `src/runtime/closed_loop.py`
  - `tests/test_bridge_unit.py`
  - `tests/test_closed_loop_smoke.py`
- Local validation passed:
  - `python -m pytest tests/test_bridge_unit.py tests/test_closed_loop_smoke.py tests/test_realistic_vision_path.py -q`
  - result: `22 passed`
- Real embodied artifacts now exist for the new branch:
  - target:
    - `outputs/requested_2s_splice_uvgrid_multidrive_target/flygym-demo-20260311-115625/demo.mp4`
  - no target:
    - `outputs/requested_2s_splice_uvgrid_multidrive_no_target/flygym-demo-20260311-121158/demo.mp4`
  - zero brain:
    - `outputs/requested_2s_splice_uvgrid_multidrive_zero_brain/flygym-demo-20260311-122402/demo.mp4`
- Summary artifacts:
  - `outputs/metrics/descending_uvgrid_multidrive_visual_drive_validation.json`
  - `outputs/metrics/descending_uvgrid_multidrive_comparison.json`

3. Key result
- The hybrid motor-latent branch is real and brain-driven:
  - `zero_brain nonzero_command_cycles = 0`
  - `zero_brain net_displacement = 0.016680726595983866`
- But the first calibration does not beat the current calibrated two-drive UV-grid branch overall.

Target-run comparison versus the current best two-drive branch:
- `avg_forward_speed`: `4.9241 -> 4.4153`
- `net_displacement`: `5.7583 -> 5.5463`
- `corr_drive_diff_vs_target_bearing`: `0.8810 -> 0.8481`
- `steer_sign_match_rate`: `0.8878 -> 0.9031`

So the new branch slightly improves steering sign match, but regresses on the broader target-run metrics.

4. Main failure mode
- The first motor-latent calibration strengthens no-target locomotion too much:
  - calibrated two-drive no-target `avg_forward_speed = 3.9070`
  - hybrid motor-latent no-target `avg_forward_speed = 4.6506`
- That means the richer controller is currently amplifying generic visually driven locomotion more than target-conditioned pursuit.

5. Honest conclusion
- The new branch is more plausible at the controller interface:
  - it modulates CPG amplitude
  - CPG frequency
  - correction gains
  - reverse gating
- But it is not yet the strongest embodied branch.
- The current production reference therefore stays:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated.yaml`
- The new hybrid motor-latent branch stays experimental until it is calibrated to improve target-vs-no-target modulation.

6. Next actions
- Calibrate the hybrid motor-latent branch specifically for:
  - stronger target-vs-no-target modulation
  - lower generic no-target drive
  - preserved or improved target-bearing steering correlation

## 2026-03-11 - Follow-up artifact review refined the multidrive interpretation

1. What I rechecked
- Re-read the matched multidrive target and no-target logs after visual review of the videos:
  - `outputs/requested_2s_splice_uvgrid_multidrive_target/flygym-demo-20260311-115625/run.jsonl`
  - `outputs/requested_2s_splice_uvgrid_multidrive_no_target/flygym-demo-20260311-121158/run.jsonl`
- Compared target-conditioned phases against no-target phases rather than relying only on whole-run averages.

2. What I found
- The user's qualitative read is supported by the logs.
- In the target run, when the target is frontal:
  - mean total drive is higher
  - mean forward speed is much higher
- When the target moves peripheral:
  - mean total drive drops
  - steering asymmetry rises
  - forward speed falls
- Concrete target-run conditioned numbers:
  - `abs(target_bearing) < 0.5`:
    - mean total drive `0.6257`
    - mean abs drive diff `0.1366`
    - mean forward speed `6.4098`
  - `abs(target_bearing) >= 0.5`:
    - mean total drive `0.4216`
    - mean abs drive diff `0.2526`
    - mean forward speed `3.7776`
- The target run also approaches the target before losing it:
  - start distance `9.99`
  - minimum distance `6.31`
  - end distance `11.50`

3. Revised interpretation
- The multidrive branch is likely doing something more specific than the previous aggregate metrics suggested:
  - approach when the target is frontal
  - then suppress forward progression and attempt to reorient when the target goes peripheral
- The likely remaining failure is not "no pursuit-like behavior".
- It is more specifically:
  - insufficient turn authority
  - or ineffective turn execution in the current controller/body mapping

4. Consequence for next work
- `T089` should now focus on:
  - stronger turn execution
  - less ineffective stop-turn behavior
  - preserving the approach phase
- Not on abandoning the multidrive path.

## 2026-03-11 - T090 documented the neck-output mapping strategy and reset the next phase

1. What I recorded
- Added a new explicit strategy document:
  - `docs/neck_output_mapping_strategy.md`
- Updated:
  - `TASKS.md`
  - `PROGRESS_LOG.md`

2. What that document preserves
- The current strongest branch is still the calibrated UV-grid two-drive branch.
- The first hybrid motor-latent branch is more plausible but not yet stronger overall.
- The main remaining bottleneck is now the *output semantics*:
  - broad descending / neck outputs
  - into controller/body action
- The correct near-term target is now an explicit **neck-output motor basis**.

3. What the doc makes explicit
- We should stop hand-authoring more and more tiny output subsets.
- We should first monitor a broad public descending/efferent population during embodied runs.
- Then build:
  - an observational atlas
  - a causal motor-response atlas
  - a fitted motor basis
- Only after that should we revisit calibrated body feedback into the brain.

4. Why this matters
- Conversation compaction is expected.
- This repo now has an explicit record that the next phase is not:
  - "just tune turn gain"
- It is:
  - "derive a broader, data-driven neck-output mapping layer"

5. Next actions
- `T091`: add monitoring-only support for a broad descending/efferent population
- `T092`: summarize the first observational neck-output atlas
- `T093`: build the first causal descending motor-response atlas

## 2026-03-11 - T091 and T092 completed: broad descending monitoring and first observational atlas

1. What I added
- Monitoring-only support for a broad descending/efferent population in the
  current strongest embodied branch:
  - `src/bridge/decoder.py`
- New monitored configs:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_monitored.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_monitored_no_target.yaml`
- New summarizer:
  - `scripts/summarize_descending_monitoring.py`
- New docs:
  - `docs/descending_monitoring_atlas.md`

2. Validation
- Ran:
  - `python -m pytest tests/test_bridge_unit.py tests/test_closed_loop_smoke.py -q`
  - `python -m py_compile src/bridge/decoder.py scripts/summarize_descending_monitoring.py`
- Result:
  - `18 passed`

3. Embodied monitored runs
- Target + monitored:
  - `outputs/requested_2s_splice_uvgrid_calibrated_monitored_target/flygym-demo-20260311-134126/run.jsonl`
- No target + monitored:
  - `outputs/requested_2s_splice_uvgrid_calibrated_monitored_no_target/flygym-demo-20260311-135635/run.jsonl`

4. Atlas outputs
- `outputs/metrics/descending_monitor_neck_output_atlas.csv`
- `outputs/metrics/descending_monitor_neck_output_atlas.json`

5. Main findings
- The current branch uses a distributed descending code, not one "pursuit neuron".
- Strongest current forward/frontal candidates:
  - `DNg97`
  - `DNp103`
  - `DNp18`
- Strongest current turn-sensitive candidates:
  - `DNp71`
  - `DNpe040`
  - `DNpe056`
- Strongest current target-conditioned weak-gate candidates:
  - `DNpe016`
  - `DNae002`

6. Consequence
- `T091` and `T092` are complete.
- The next correct step became `T093`: direct causal perturbation of those
  descending groups in the embodied stack.

## 2026-03-11 - T093 completed, then recovered after a local power outage

1. What happened
- I built and validated the first causal descending motor-response atlas tooling:
  - `scripts/run_descending_motor_atlas.py`
  - `tests/test_descending_motor_atlas.py`
- I ran a local mock smoke atlas.
- I then ran the real WSL embodied atlas and generated the first summary
  artifacts.
- After that, the local PC suffered a power outage and crashed.
- On recovery, I checked the repo state, verified that the atlas artifacts were
  still present on disk, and resumed from those surviving outputs instead of
  rerunning blindly.

2. Recovery evidence
- Surviving raw atlas:
  - `outputs/metrics/descending_motor_atlas.json`
  - `outputs/metrics/descending_motor_atlas.csv`
- Surviving summary:
  - `outputs/metrics/descending_motor_atlas_summary.json`
  - `outputs/metrics/descending_motor_atlas_summary.csv`

3. What I changed after recovery
- Expanded the atlas script so it now includes:
  - a true no-stimulation baseline row
  - the target-conditioned observational candidates:
    - `DNpe016`
    - `DNae002`
    - `DNpe031`
- Added:
  - `scripts/summarize_descending_motor_atlas.py`
  - `docs/descending_motor_atlas.md`
- Updated:
  - `docs/neck_output_mapping_strategy.md`
  - `docs/descending_monitoring_atlas.md`
  - `docs/visual_splice_strategy.md`
  - `docs/cold_start_visual_brain_plan.md`

4. Validation
- Ran:
  - `python -m pytest tests/test_descending_motor_atlas.py tests/test_bridge_unit.py -q`
  - `python -m py_compile scripts/run_descending_motor_atlas.py scripts/summarize_descending_motor_atlas.py`
- Result:
  - `12 passed`

5. Main causal findings
- Baseline is not zero-motion:
  - over `0.1 s`, the body still passively settles with
    - `net_displacement = 0.0482`
    - `avg_forward_speed = 1.8788`
    - `mean_total_drive = 0.0`
- Strongest bilateral forward drivers above baseline:
  - `DNp103`
    - `delta_net_displacement_vs_baseline = +0.2971`
    - `delta_avg_forward_speed_vs_baseline = +3.9664`
  - `DNp18`
    - `+0.2844`
    - `+3.7944`
  - `DNg97`
    - `+0.2820`
    - `+3.7865`
- Strongest mirrored turn driver:
  - `DNpe040`
    - left `delta_end_yaw_vs_baseline = -0.0254`
    - right `delta_end_yaw_vs_baseline = +0.0122`
- Secondary mirrored turn candidate:
  - `DNpe056`
    - left `-0.0099`
    - right `+0.0033`
- Ambiguous current role:
  - `DNp71`
    - large asymmetry, but left and right perturbations do not mirror in the
      current end-yaw metric
- No useful effect in the present stack:
  - `DNpe031`
  - `DNae002`
- Weak bilateral gate-like effect:
  - `DNpe016`

6. Consequence
- `T093` is now complete.
- The next active task is now clearly `T094`:
  - fit a neck-output motor basis from the observational + causal atlas
  - then replace the current hand-authored multidrive mapping with that fitted
    basis

## 2026-03-11 - T094 started: first fitted neck-output motor basis and real pilot

1. What I added
- Basis fitter:
  - `scripts/fit_neck_output_motor_basis.py`
- Generated basis:
  - `outputs/metrics/neck_output_motor_basis.json`
- Decoder support for fitted basis files:
  - `src/bridge/decoder.py`
- New fitted-basis configs:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_no_target.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_zero_brain.yaml`
- New doc:
  - `docs/neck_output_motor_basis.md`

2. Validation
- Ran:
  - `python -m pytest tests/test_descending_motor_atlas.py tests/test_bridge_unit.py -q`
  - `python -m py_compile scripts/fit_neck_output_motor_basis.py`
- Result:
  - `13 passed`

3. Fitted basis produced
- Forward weights:
  - `DNp103 = 1.0`
  - `DNp18 = 0.9501`
  - `DNg97 = 0.9483`
  - `DNpe016 = 0.1553`
- Turn weights:
  - `DNpe040 = 1.0`
  - `DNpe056 = 0.3910`
- Explicit exclusions for now:
  - ambiguous turn role:
    - `DNp71`
  - inactive in first causal pass:
    - `DNpe031`
    - `DNae002`

4. Smoke and first real pilot
- Local mock smoke completed:
  - `outputs/requested_0p05s_multidrive_fitted_basis_mock/mock-demo-20260311-145811`
- Real WSL `0.1 s` target pilot completed:
  - `outputs/requested_0p1s_splice_uvgrid_multidrive_fitted_basis_target/demos/flygym-demo-20260311-145836.mp4`
  - `outputs/requested_0p1s_splice_uvgrid_multidrive_fitted_basis_target/metrics/flygym-demo-20260311-145836.csv`
  - `outputs/benchmarks/fullstack_splice_uvgrid_multidrive_fitted_basis_target_0p1s.csv`

5. Preliminary result
- Old hand-authored multidrive `0.1 s` target pilot:
  - `net_displacement = 0.0584`
  - `displacement_efficiency = 0.1919`
  - `avg_forward_speed = 3.1059`
- New fitted-basis multidrive `0.1 s` target pilot:
  - `net_displacement = 0.0802`
  - `displacement_efficiency = 0.3202`
  - `avg_forward_speed = 2.5563`

6. Interpretation
- The fitted basis is changing the character of the motion in a plausible way:
  - less raw forward speed
  - more net displacement
  - better displacement efficiency in the short pilot
- That is not enough to declare it better yet.
- The remaining gate for `T094` is still matched:
  - longer-window `target`
  - longer-window `no_target`
  - longer-window `zero_brain`

## 2026-03-11 - T094 extended to matched `0.1 s` fitted-basis pilots after recovery

1. What I ran
- Real WSL no-target pilot:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_no_target.yaml`
- Real WSL zero-brain pilot:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_zero_brain.yaml`
- New summary script:
  - `scripts/summarize_fitted_basis_pilot.py`

2. New artifacts
- `outputs/benchmarks/fullstack_splice_uvgrid_multidrive_fitted_basis_no_target_0p1s.csv`
- `outputs/benchmarks/fullstack_splice_uvgrid_multidrive_fitted_basis_zero_brain_0p1s.csv`
- `outputs/requested_0p1s_splice_uvgrid_multidrive_fitted_basis_no_target/demos/flygym-demo-20260311-150139.mp4`
- `outputs/requested_0p1s_splice_uvgrid_multidrive_fitted_basis_zero_brain/demos/flygym-demo-20260311-150253.mp4`
- `outputs/metrics/neck_output_motor_basis_pilot_summary.json`

3. Matched `0.1 s` result
- target:
  - `net_displacement = 0.0802`
  - `avg_forward_speed = 2.5563`
  - `displacement_efficiency = 0.3202`
- no target:
  - `net_displacement = 0.0770`
  - `avg_forward_speed = 2.2348`
  - `displacement_efficiency = 0.3518`
- zero brain:
  - `net_displacement = 0.0343`
  - `avg_forward_speed = 1.8578`
  - `displacement_efficiency = 0.1883`

4. Interpretation
- The fitted-basis branch is still brain-driven over the short pilot:
  - target minus zero-brain net displacement `= +0.0459`
  - target minus zero-brain forward speed `= +0.6985`
- But target-vs-no-target separation is still weak at `0.1 s`:
  - target minus no-target net displacement `= +0.0032`
  - target minus no-target forward speed `= +0.3215`
  - target minus no-target displacement efficiency `= -0.0316`

5. Consequence
- `T094` remains `doing`, not `done`.
- The next clean step is longer-window matched validation for the fitted-basis
  branch before replacing the current hand-authored multidrive path.

## 2026-03-11 - Longer-window `1.0 s` fitted-basis validation completed

1. What I ran
- Real WSL fitted-basis `1.0 s` target run:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis.yaml`
- Real WSL fitted-basis `1.0 s` no-target run:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_no_target.yaml`
- Real WSL fitted-basis `1.0 s` zero-brain run:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_zero_brain.yaml`

2. Main artifacts
- target:
  - `outputs/requested_1s_splice_uvgrid_multidrive_fitted_basis_target/demos/flygym-demo-20260311-150809.mp4`
- no target:
  - `outputs/requested_1s_splice_uvgrid_multidrive_fitted_basis_no_target/demos/flygym-demo-20260311-151736.mp4`
- zero brain:
  - `outputs/requested_1s_splice_uvgrid_multidrive_fitted_basis_zero_brain/demos/flygym-demo-20260311-152440.mp4`
- summary:
  - `outputs/metrics/neck_output_motor_basis_1s_summary.json`

3. `1.0 s` result
- target:
  - `avg_forward_speed = 5.4864`
  - `net_displacement = 3.8608`
  - `displacement_efficiency = 0.7051`
- no target:
  - `avg_forward_speed = 6.5676`
  - `net_displacement = 4.6747`
  - `displacement_efficiency = 0.7132`
- zero brain:
  - `avg_forward_speed = 0.6968`
  - `net_displacement = 0.0153`
  - `displacement_efficiency = 0.0219`

4. Interpretation
- The fitted-basis branch is still clearly brain-driven over `1.0 s`:
  - target minus zero-brain net displacement `= +3.8455`
  - target minus zero-brain forward speed `= +4.7897`
- But it is still not target-conditioned in the way we need:
  - target minus no-target net displacement `= -0.8140`
  - target minus no-target forward speed `= -1.0812`
  - target minus no-target displacement efficiency `= -0.0081`

5. Consequence
- `T094` remains active but cannot be closed.
- Added `T095` as the next output-side refinement task:
  - use the new atlas evidence to improve target-conditioned behavior over
    no-target locomotion
  - likely by revisiting:
    - `DNpe016`
    - `DNp71`
    - and the mapping from the fitted basis into the controller latents

## 2026-03-11 - Target-tracking evaluation gap noted; rerunning a `2.0 s` fitted-basis target demo

1. Correction
- The user pointed out a real evaluation gap:
  - aggregate locomotion metrics alone are not sufficient
  - they can miss pursuit-like structure such as:
    - approach while the target is frontal
    - slowing or stopping while attempting to reacquire the target
    - partial turn attempts that look meaningful in the video but weak in scalar summaries

2. Consequence
- Added `T096` so the repo explicitly tracks this as an evaluation requirement.
- This means the fitted-basis branch should not be judged only by:
  - net displacement
  - average forward speed
  - displacement efficiency
- It also needs explicit target-tracking review.

3. Immediate action
- Rerun the fitted-basis target demo at `2.0 s`:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis.yaml`
- Save the video/log/metrics artifacts for scene-level review before making the next decoder/basis change.

4. Result
- The `2.0 s` fitted-basis target rerun completed successfully and produced:
  - video:
    - `outputs/requested_2s_splice_uvgrid_multidrive_fitted_basis_target/demos/flygym-demo-20260311-153237.mp4`
  - log:
    - `outputs/requested_2s_splice_uvgrid_multidrive_fitted_basis_target/logs/flygym-demo-20260311-153237.jsonl`
  - metrics:
    - `outputs/requested_2s_splice_uvgrid_multidrive_fitted_basis_target/metrics/flygym-demo-20260311-153237.csv`
  - benchmark row:
    - `outputs/benchmarks/fullstack_splice_uvgrid_multidrive_fitted_basis_target_2s.csv`

5. Headline numbers
- `sim_seconds = 2.0`
- `avg_forward_speed = 4.8866`
- `net_displacement = 6.1516`
- `displacement_efficiency = 0.6301`
- `real_time_factor = 0.002286`

6. Next use
- This rerun exists primarily for explicit scene-level target-tracking review, not
  only scalar comparison.

## 2026-03-11 - Started longer-window fitted-basis validation after the recovered `0.1 s` pilots

1. Why this next step is necessary
- The recovered matched `0.1 s` pilots established that the fitted-basis branch
  is still brain-driven.
- They did **not** establish strong target-vs-no-target separation.
- So the correct next gate is a longer-window matched run, not another decoder
  rewrite yet.

2. Active plan
- Run the fitted-basis branch sequentially in real WSL for:
  - `target`
  - `no_target`
  - `zero_brain`
- Use `1.0 s` simulated duration as the first longer-window checkpoint.

3. Why `1.0 s`
- It is materially longer than the current `0.1 s` pilots.
- It is still short enough to complete on this machine without turning into a
  many-hour branch sweep.
- It should be long enough for target-conditioned approach vs reorientation
  structure to separate more clearly if the fitted basis is actually helping.

## 2026-03-11 - Wrote a cold-start context handoff for clean-session recovery

1. What I attempted
- Wrote a repo-root `context.md` intended for a fresh Codex session with no
  prior chat history.
- The goal was to preserve the current understanding of the repo, the public
  science basis, the neuron-mapping boundary, the current best production
  branch, and the active unresolved gaps.

2. What succeeded
- Added `context.md` with an explicit cold-start reading order.
- Captured the project mission, upstream repos, paper context, architecture,
  public neuron anchors, visual splice evolution, descending readout findings,
  current best calibrated UV-grid branch, performance reality, active tracker
  state, and recommended future sub-agent decomposition.
- Logged the handoff in `TASKS.md` as `T097`.

3. What failed
- Nothing substantive failed. The only practical issue was that the initial
  attempt was too large for a single patch, so the document was added in smaller
  sections instead.

4. Evidence paths
- `context.md`
- `TASKS.md`
- `PROGRESS_LOG.md`

5. Why this matters
- The repo has accumulated enough architectural and scientific state that a
  clean session would otherwise waste time reconstructing known facts.
- This handoff should let the next session start from the current real
  bottlenecks: visual splice semantics and output decoding quality.

## 2026-03-12 - Started contextual fitted-basis refinement for target-conditioned gating and stronger peripheral reorientation

1. What I attempted
- Continued `T095` and `T096` from the current fitted-basis branch instead of reopening install or splice work.
- Used bounded parallel analysis only on docs, logs, and metrics to confirm the current failure shape before editing code.
- Implemented a new experimental contextual decoder path that uses:
  - `DNpe016` as a forward-context gate
  - `DNp71` as a turn-context boost
  - new turn-priority latent asymmetry gains for low-forward, high-turn states
- Created a separate config family rather than mutating the current fitted-basis baseline.

2. What succeeded
- Confirmed the current qualitative failure mode from the existing evidence:
  - the branch can approach while the target is frontal
  - when the target goes peripheral, total drive falls and turn asymmetry rises
  - but the resulting turn execution is still too weak to recover the target cleanly
- Added decoder support for turn-priority motor-latent asymmetry gains in `src/bridge/decoder.py`.
- Preserved and used the existing context hooks (`forward_context_*`, `turn_context_*`) for the first explicit contextual fitted-basis refinement.
- Added unit coverage for:
  - forward gating from context populations
  - stronger hybrid turn execution from the new turn-priority path
- Added new experimental configs:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual_no_target.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual_zero_brain.yaml`
  - `configs/mock_multidrive_fitted_basis_contextual.yaml`
- Validation passed:
  - `python -m py_compile src/bridge/decoder.py`
  - `python -m pytest tests/test_bridge_unit.py tests/test_closed_loop_smoke.py -q`
  - result: `24 passed`
- The dedicated mock smoke run completed and produced artifacts:
  - `outputs/requested_0p2s_mock_multidrive_fitted_basis_contextual/mock-demo-20260312-004708/demo.mp4`
  - `outputs/requested_0p2s_mock_multidrive_fitted_basis_contextual/mock-demo-20260312-004708/run.jsonl`
  - `outputs/requested_0p2s_mock_multidrive_fitted_basis_contextual/mock-demo-20260312-004708/metrics.csv`

3. What failed
- The production FlyGym contextual config does not boot under `mode = mock` with the UV-grid splice still enabled, because the mock body does not expose `realistic_vision_splice_cache`.
- That was handled by creating a dedicated mock smoke config instead of pretending the production embodied config should run on the mock body.
- `pytest` still emits the known Windows temp-directory cleanup warning on exit, but the actual test run passes.

4. Evidence paths
- `src/bridge/decoder.py`
- `tests/test_bridge_unit.py`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual_no_target.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual_zero_brain.yaml`
- `configs/mock_multidrive_fitted_basis_contextual.yaml`
- `outputs/requested_0p2s_mock_multidrive_fitted_basis_contextual/mock-demo-20260312-004708/run.jsonl`
- `outputs/requested_0p2s_mock_multidrive_fitted_basis_contextual/mock-demo-20260312-004708/metrics.csv`

5. Next actions
- Run the new contextual fitted-basis branch in real WSL for matched:
  - `target`
  - `no_target`
  - `zero_brain`
- Keep those embodied runs serialized so local compute paths do not contend.
- Judge the new branch on both:
  - scalar metrics
  - explicit scene-level target-tracking review
- If the contextual branch still fails, the next output-side lever remains the same family:
  - stronger target-conditioned gating
  - stronger effective turn execution
  - not a return to prosthetic brain-context hacks.
## 2026-03-12 - Contextual fitted-basis validation deferred to preserve serialized heavy runtime use

1. What I attempted
- Reviewed the active embodied output bottleneck with local code/artifact reads and independent read-only Codex sub-agents.
- Confirmed that the current repo already has a contextual fitted-basis refinement branch under the `contextual` config family.
- Verified that the contextual branch is wired through the decoder and covered by a mock-path smoke config and unit tests.

2. What succeeded
- Re-aligned this session to the repo's current output-side refinement branch instead of creating a parallel duplicate.
- Added a clean regression check in `tests/test_closed_loop_smoke.py` that asserts the contextual fitted-basis config really wires `DNpe016`, `DNp71`, and the turn-priority latent gains into the decoder.
- Re-ran focused validation:
  - `python -m pytest tests/test_bridge_unit.py tests/test_closed_loop_smoke.py -q`
  - result: `22 passed`

3. What failed or was blocked
- A separate long embodied WSL benchmark was already active on the machine when this session reached the next real validation step.
- To obey the serialized-heavy-compute rule, I did not continue with an overlapping contextual WSL pilot.

4. Evidence paths
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual_no_target.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual_zero_brain.yaml`
- `configs/mock_multidrive_fitted_basis_contextual.yaml`
- `tests/test_closed_loop_smoke.py`
- `docs/neck_output_motor_basis.md`

5. Next actions
- Wait for the currently running background WSL embodied job to clear.
- Then run serialized matched contextual pilots for:
  - `target`
  - `no_target`
  - `zero_brain`
- Judge the contextual branch using both scalar metrics and explicit scene-level target-tracking review before deciding whether it beats the current fitted-basis branch.

## 2026-03-12 - Validated the contextual fitted-basis branch locally and kept WSL heavy runs serialized

1. What I attempted
- Re-read the live decoder/runtime/test state and confirmed that the repo already contains a contextual fitted-basis branch using:
  - `DNpe016` as a forward context gate
  - `DNp71` as a turn-context boost
  - turn-priority latent asymmetry gains in the hybrid multidrive decoder
- Validated that branch locally with targeted compile/test checks.
- Ran a dedicated local mock smoke run for the contextual config.
- Verified the WSL `flysim-full` micromamba env and the core embodied imports.
- Tried to start a short real WSL contextual target pilot, then stopped treating it as the active next step after discovering an already-running heavy contextual `no_target` WSL job.

2. What succeeded
- Local validation passed:
  - `python -m py_compile src/bridge/decoder.py scripts/fit_neck_output_motor_basis.py src/runtime/closed_loop.py src/body/flygym_runtime.py`
  - `python -m pytest tests/test_bridge_unit.py tests/test_closed_loop_smoke.py -q`
  - result: `24 passed`
- The contextual mock smoke run completed and wrote artifacts:
  - `outputs/requested_0p2s_multidrive_fitted_basis_contextual_smoke/mock-demo-20260312-004945/demo.mp4`
  - `outputs/requested_0p2s_multidrive_fitted_basis_contextual_smoke/mock-demo-20260312-004945/run.jsonl`
  - `outputs/requested_0p2s_multidrive_fitted_basis_contextual_smoke/mock-demo-20260312-004945/metrics.csv`
- The WSL full-stack env exists and imports cleanly:
  - `wsl --cd /mnt/g/flysim /root/.local/bin/micromamba run -n flysim-full python -c "import numpy"`
  - `wsl --cd /mnt/g/flysim /root/.local/bin/micromamba run -n flysim-full python -c "import sys; sys.path.append('src'); from body.flygym_runtime import FlyGymRealisticVisionRuntime"`

3. What failed or was intentionally stopped
- A short real WSL contextual target pilot was started under:
  - `outputs/requested_0p2s_splice_uvgrid_multidrive_fitted_basis_contextual_target/flygym-demo-20260312-005136/run.jsonl`
- That pilot was not allowed to continue as the active heavy task because `wsl pgrep -af` showed an already-running contextual `no_target` FlyGym job on this machine:
  - config: `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_context_gate_no_target.yaml`
  - output root: `outputs/requested_0p2s_splice_uvgrid_multidrive_fitted_basis_context_gate_no_target`
- To respect the explicit no-concurrent-heavy-runs requirement, the newly launched target pilot was terminated after its first logged rows rather than competing with the existing WSL run.

4. Evidence paths
- `src/bridge/decoder.py`
- `tests/test_bridge_unit.py`
- `tests/test_closed_loop_smoke.py`
- `configs/mock_multidrive_fitted_basis_contextual.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual.yaml`
- `outputs/requested_0p2s_multidrive_fitted_basis_contextual_smoke/mock-demo-20260312-004945/run.jsonl`
- `outputs/requested_0p2s_multidrive_fitted_basis_contextual_smoke/mock-demo-20260312-004945/metrics.csv`
- `outputs/requested_0p2s_splice_uvgrid_multidrive_fitted_basis_contextual_target/flygym-demo-20260312-005136/run.jsonl`
- `TASKS.md`

5. Next actions
- Do not launch another heavy WSL embodied run until the existing contextual `no_target` job has finished or been explicitly triaged.
- Inspect that active `no_target` artifact first.
- Then run the contextual `target` and `zero_brain` pilots strictly one-at-a-time.
- Keep judging the branch on both:
  - scalar metrics
  - explicit scene-level target-tracking review

## 2026-03-12 - Ran the first serialized real `0.2 s` context-gate pilots and revalidated the merged output branch

1. What I attempted
- Kept the heavy embodied work strictly serialized.
- Ran two real WSL `0.2 s` FlyGym pilots for the simpler context-gate scaffold:
  - `target`
  - `no_target`
- Re-ran the local decoder/runtime smoke suite after the sub-agent edits landed so the merged worktree had a fresh validation result.

2. What succeeded
- The merged local validation now passes:
  - `python -m pytest tests/test_bridge_unit.py tests/test_closed_loop_smoke.py -q`
  - result: `24 passed`
- Syntax checks passed:
  - `python -m py_compile src/bridge/decoder.py src/runtime/closed_loop.py src/body/flygym_runtime.py scripts/fit_neck_output_motor_basis.py`
- The serialized real WSL `target` pilot completed:
  - `outputs/requested_0p2s_splice_uvgrid_multidrive_fitted_basis_context_gate_target/flygym-demo-20260312-004336/run.jsonl`
  - `outputs/requested_0p2s_splice_uvgrid_multidrive_fitted_basis_context_gate_target/flygym-demo-20260312-004336/metrics.csv`
- The serialized real WSL `no_target` pilot completed:
  - `outputs/requested_0p2s_splice_uvgrid_multidrive_fitted_basis_context_gate_no_target/flygym-demo-20260312-004902/run.jsonl`
  - `outputs/requested_0p2s_splice_uvgrid_multidrive_fitted_basis_context_gate_no_target/flygym-demo-20260312-004902/metrics.csv`

3. Preliminary result
- `target`:
  - `avg_forward_speed = 1.8433`
  - `net_displacement = 0.0964`
  - `displacement_efficiency = 0.2643`
- `no_target`:
  - `avg_forward_speed = 1.8681`
  - `net_displacement = 0.0912`
  - `displacement_efficiency = 0.2467`

Interpretation:

- the simpler context-gate scaffold does not yet create strong target-vs-no-target separation,
- but it does show a small target advantage on net displacement and displacement efficiency,
- so the output-side context idea remains plausible rather than being immediately falsified.

4. What failed or remains open
- The result is still too weak to promote.
- These pilots were run on the simpler `context_gate` scaffold, not the fuller `contextual` branch with turn-priority latent gains.
- So the actual next gate remains the matched real WSL validation of:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual_no_target.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual_zero_brain.yaml`

5. Notes
- The pytest run still emitted the same Windows temp-cleanup `PermissionError` on exit, but the actual test run succeeded.
- No overlapping heavy WSL jobs were run during this pass.

6. Next actions
- Use the `contextual` branch, not the simpler `context_gate` scaffold, for the next serialized real WSL trio.
- Run `target`, `no_target`, and `zero_brain` one-at-a-time.
- After those finish, compare:
  - scalar metrics
  - scene-level target-tracking behavior
  - and whether the contextual branch now beats the plain fitted-basis branch on target-vs-no-target separation.

## 2026-03-12 - Reassigned the contextual decoder using completed atlases plus primary descending-control literature

1. What I attempted
- Re-check the contextual branch against the completed monitored embodied atlas and the short causal descending motor atlas instead of relying on aborted contextual partial runs.
- Dispatch a literature-focused sub-agent and independently review primary sources on descending steering, locomotor modulation, and walking-linked versus flight-linked descending neurons.
- Convert that evidence into a decoder/config refinement before launching another serialized WSL embodied run.

2. What succeeded
- The literature review converged on a strong constraint: keep direct steering on canonical lateralized descending neurons such as `DNa01` / `DNa02`, and treat other candidate descending groups as gain/modulatory channels unless they have stronger walking-steering support.
- The local atlas evidence and literature together supported this new split:
  - `DNae002` plus `DNpe016` as target-conditioned forward/context gates,
  - `DNpe040` plus `DNpe056` as exploratory turn-support context channels,
  - `DNa01` / `DNa02` retained as the direct steering core.
- Implemented a new decoder option `turn_context_mode = aligned_asymmetry` in `src/bridge/decoder.py`.
- Rewired the contextual configs so turn support now boosts only when the contextual left-right asymmetry agrees with the turn direction already selected by the canonical steering readout.
- Updated local coverage:
  - `tests/test_bridge_unit.py`
  - `tests/test_closed_loop_smoke.py`
- Updated the current branch rationale in `docs/neck_output_motor_basis.md`.

3. What failed
- The earlier contextual partial WSL logs were not reliable evidence for decoder-observable activity because they ended before the relevant outputs were emitted.
- No real WSL embodied validation was launched in this step, by design, to avoid overlapping heavy tasks before the refined branch was ready.

4. Evidence
- Empirical repo evidence:
  - `outputs/metrics/descending_early_activity.csv`
  - `outputs/metrics/descending_monitor_neck_output_atlas.csv`
  - `outputs/metrics/descending_motor_atlas_summary.json`
  - `outputs/metrics/neck_output_motor_basis.json`
- Primary sources:
  - Rayshubskiy et al., eLife 2025, steering DNs: `https://elifesciences.org/articles/102230`
  - Braun et al., Cell 2024, fine-grained walking steering: `https://pmc.ncbi.nlm.nih.gov/articles/PMC12778575/`
  - Westeinde et al., Nature 2024, steering command vs gain control: `https://www.nature.com/articles/s41586-024-07039-2`
  - Schlegel et al., Nature 2024, descending networks and population motor control: `https://www.nature.com/articles/s41586-024-07523-9`
  - Lappalainen et al., Nature 2024, walking-linked `oDN1` / `DNg97`: `https://www.nature.com/articles/s41586-024-07939-3`
  - Ache et al., Nature 2019, visually elicited flight turns and `DNb01`: `https://www.nature.com/articles/s41586-019-1677-2`

5. Files changed
- `src/bridge/decoder.py`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual_no_target.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual_zero_brain.yaml`
- `configs/mock_multidrive_fitted_basis_contextual.yaml`
- `tests/test_bridge_unit.py`
- `tests/test_closed_loop_smoke.py`
- `docs/neck_output_motor_basis.md`
- `TASKS.md`

6. Next actions
- Run local validation on the updated decoder/config branch.
- If local validation passes, start the real WSL contextual `target` pilot first and keep the `no_target` and `zero_brain` pilots strictly serialized after it.
- Compare the refined contextual branch against the current fitted-basis and calibrated two-drive baselines on both scalar metrics and scene-level target-tracking.

## 2026-03-12 - Replaced the suppressive forward gate with an additive context boost and reran serialized embodied pilots

1. What I attempted
- Validate the first literature-informed contextual patch locally.
- Run a short real WSL `target` pilot on that patch.
- After observing locomotor suppression, change the forward context mechanism from multiplicative gate to additive boost and rerun serialized `target` / `no_target` pilots.

2. What succeeded
- Local validation passed twice as the branch evolved:
  - first after the asymmetry-aligned context patch: `25 passed`
  - then after adding the forward-context boost path: `26 passed`
- The first contextual `target` / `no_target` pair on the multiplicative forward gate showed a clear failure mode:
  - target: `avg_forward_speed 1.5598`, `net_displacement 0.0572`, `displacement_efficiency 0.1852`
  - no_target: `avg_forward_speed 1.7889`, `net_displacement 0.0988`, `displacement_efficiency 0.2791`
- Diagnosis from the logs showed the target-biased context signal existed but the multiplicative gate was suppressing both conditions too strongly relative to the modest target-vs-no-target separation.
- I then added `forward_context_mode = boost` plus `forward_context_boost` in `src/bridge/decoder.py`, rewired the contextual configs, and added unit coverage.
- The boosted target rerun recovered motion substantially:
  - boosted target: `avg_forward_speed 2.7756`, `net_displacement 0.1621`, `displacement_efficiency 0.2950`
- I then ran the matched boosted `no_target` pilot, still strictly serialized:
  - boosted no_target: `avg_forward_speed 2.9413`, `net_displacement 0.1811`, `displacement_efficiency 0.3109`

3. What failed
- The additive boost fixed the locomotor-collapse problem but did not fix target selectivity.
- In the live boosted pair, the supposedly target-conditioned forward context family was not actually target-selective:
  - `DNae002` bilateral mean was higher in boosted `no_target` than in boosted `target`
  - `DNpe016` remained silent in both boosted runs
- Because the branch is still not beating matched `no_target`, I did not spend another heavy pass on `zero_brain` for this specific refinement.

4. Evidence
- Multiplicative-gate pilots:
  - `outputs/requested_0p2s_splice_uvgrid_multidrive_fitted_basis_contextual_target_refined/metrics/flygym-demo-20260312-112938.csv`
  - `outputs/requested_0p2s_splice_uvgrid_multidrive_fitted_basis_contextual_no_target_refined/metrics/flygym-demo-20260312-113221.csv`
- Additive-boost pilots:
  - `outputs/requested_0p2s_splice_uvgrid_multidrive_fitted_basis_contextual_target_boosted/metrics/flygym-demo-20260312-113644.csv`
  - `outputs/requested_0p2s_splice_uvgrid_multidrive_fitted_basis_contextual_no_target_boosted/metrics/flygym-demo-20260312-113859.csv`
- Log-level diagnosis:
  - `outputs/requested_0p2s_splice_uvgrid_multidrive_fitted_basis_contextual_target_boosted/logs/flygym-demo-20260312-113644.jsonl`
  - `outputs/requested_0p2s_splice_uvgrid_multidrive_fitted_basis_contextual_no_target_boosted/logs/flygym-demo-20260312-113859.jsonl`

5. Files changed
- `src/bridge/decoder.py`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual_no_target.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual_zero_brain.yaml`
- `configs/mock_multidrive_fitted_basis_contextual.yaml`
- `tests/test_bridge_unit.py`
- `tests/test_closed_loop_smoke.py`
- `docs/neck_output_motor_basis.md`
- `TASKS.md`

6. Next actions
- Stop assuming `DNae002` is a reliable target-conditioned forward control signal in the live embodied branch.
- Identify a genuinely target-selective signal family for the next refinement, or shift the refinement back upstream into the visual-to-steering interface rather than continuing to retune the current decoder alone.
- Keep future embodied runs serialized and evidence-first, because the current failure mode is now specific enough to avoid blind parameter sweeps.

## 2026-03-12 - Started the explicit VNC-wide workstream with public-source registry, typed graph ingest, and first pathway scaffolding

1. What I attempted
- Start the VNC-wide plan as a real repo workstream instead of leaving it as a conceptual response.
- Reuse sub-agents extensively for three parallel tracks:
  - public VNC literature/data availability
  - codebase integration seams
  - experimental design / milestone discipline
- Add actual code under `src/vnc/` for source metadata, annotation-atlas building, typed node/edge ingest, and first pathway extraction.

2. What succeeded
- Added the first VNC package and docs:
  - `src/vnc/data_sources.py`
  - `src/vnc/annotation_atlas.py`
  - `src/vnc/ingest.py`
  - `src/vnc/pathways.py`
  - `scripts/build_vnc_annotation_atlas.py`
  - `scripts/build_vnc_pathway_inventory.py`
  - `docs/vnc_data_sources.md`
  - `docs/vnc_workstream_plan.md`
  - `docs/vnc_graph_model.md`
- Added local coverage:
  - `tests/test_vnc_annotation_atlas.py`
  - `tests/test_vnc_pathways.py`
- Validation passed:
  - `python -m pytest tests/test_vnc_annotation_atlas.py tests/test_vnc_pathways.py -q` -> `4 passed`
  - `python -m py_compile src/vnc/annotation_atlas.py src/vnc/ingest.py src/vnc/pathways.py scripts/build_vnc_annotation_atlas.py scripts/build_vnc_pathway_inventory.py` -> passed
- Produced first executable VNC artifacts:
  - `outputs/metrics/vnc_annotation_atlas_mock.json`
  - `outputs/metrics/vnc_annotation_atlas_mock.csv`
  - `outputs/metrics/vnc_pathway_inventory_mock.json`
- Hardened the CSV readers against UTF-8 BOM headers after the first CLI run exposed that common export problem.

3. What the sub-agents concluded
- Experimental-design scout:
  - do not jump straight to a full muscle-level or whole-VNC dynamical reconstruction
  - keep the current best production branch as the control
  - expand via observational atlas -> causal atlas -> fitted VNC basis
- Codebase-integration scout:
  - keep VNC work in a dedicated `src/vnc/` package rather than growing `src/brain` or `bridge.decoder`
  - the long-term seam should be `brain readout -> vnc emulator -> body command`
  - the body/runtime interfaces will need richer command and state channels before a true VNC emulator can sit in the loop cleanly
- The literature/data scout is still pending, but the official-source review already anchored the first public registry around:
  - MANC
  - FANC
  - BANC

4. Official-source grounding used in this step
- MANC:
  - `https://www.janelia.org/project-team/flyem/manc-connectome`
  - `https://www.janelia.org/news/janelia-scientists-and-collaborators-unveil-fruit-fly-nerve-cord-connectome`
- FANC:
  - `https://connectomics.hms.harvard.edu/adult-drosophila-vnc-tem-dataset-female-adult-nerve-cord-fanc`
  - `https://flyconnectome.github.io/fancr/`
- BANC:
  - `https://flyconnectome.github.io/bancr/`

5. What failed or remains open
- No real MANC / FANC / BANC annotation export has been ingested yet; the first CLI artifacts are intentionally mock fixtures proving the toolchain shape.
- The literature/data scout did not finish in time for this turn, so the first real export target is still being finalized under `T104`.
- None of this yet replaces the live sparse decoder. It creates the tested scaffolding required to do that honestly.

6. Next actions
- Finalize the first real public export target under `T104`, with preference for a public MANC annotation/metadata export or a BANC Codex annotation export.
- Add `src/vnc/emulator.py` design scaffolding only after the real graph ingest target is settled.
- Keep the current embodied decoder branch and the VNC workstream separate until the VNC pathway inventory is operating on real public data instead of fixtures.

## 2026-03-12 - Added the first structural VNC spec compiler, a pluggable VNC decoder path, and a more generic runtime seam

1. What I attempted
- Reuse sub-agents again, this time for:
  - exact first public ingest targets
  - the cleanest runtime insertion seam
  - the next highest-value low-compute implementation slice
- Convert the VNC workstream from:
  - source registry
  - annotation atlas
  - pathway inventory
  into:
  - a graph-derived structural spec
  - a pluggable decoder candidate
  - a more command-agnostic closed-loop seam

2. What succeeded
- The literature/data scout came back with concrete first-ingest targets:
  - `MANC body-annotations-male-cns-v0.9-minconf-0.5.feather`
  - then `MANC body-neurotransmitters-male-cns-v0.9.feather`
  - then `MANC connectome-weights-male-cns-v0.9-minconf-0.5.feather`
  - BANC supplementary tables and Dataverse exports after that
  - FANC public SWC reconstructions as the non-gated female comparison path
- I folded those findings into:
  - `src/vnc/data_sources.py`
  - `docs/vnc_data_sources.md`
- Added a structural spec compiler:
  - `src/vnc/spec_builder.py`
  - `scripts/build_vnc_structural_spec.py`
- Added a first pluggable broad decoder candidate:
  - `src/vnc/spec_decoder.py`
  - `src/bridge/decoder_factory.py`
- Updated the runtime/body seam so future decoders are not forced to pretend they are just legacy left/right scalars:
  - `src/body/interfaces.py`
  - `src/body/mock_body.py`
  - `src/body/flygym_runtime.py`
  - `src/runtime/closed_loop.py`
- Produced the first structural-spec artifacts:
  - `outputs/metrics/vnc_structural_spec_mock.json`
  - `outputs/metrics/vnc_structural_spec_mock.csv`
- Validation passed:
  - `python -m pytest tests/test_vnc_annotation_atlas.py tests/test_vnc_pathways.py tests/test_vnc_spec_decoder.py tests/test_closed_loop_smoke.py -q` -> `16 passed`
  - `python -m py_compile src/vnc/data_sources.py src/body/interfaces.py src/body/mock_body.py src/body/flygym_runtime.py src/bridge/controller.py src/runtime/closed_loop.py src/vnc/spec_builder.py src/vnc/spec_decoder.py src/bridge/decoder_factory.py scripts/build_vnc_structural_spec.py` -> passed

3. What the sub-agents concluded
- Literature/data scout:
  - the first ungated real ingest target should be the public MANC annotation feather, not a neuPrint query path
  - BANC paper supplement / Dataverse exports are the best ungated brain+VNC follow-up
  - FANC is still valuable, but the first non-gated path is published reconstructions rather than the latest protected segmentation tooling
- Runtime seam scout:
  - the cleanest long-term seam is still `brain readout -> VNC stage -> body command`
  - the immediate blocker was not the loop itself, but command and logging assumptions that still treated everything as legacy `left_drive/right_drive`
- Experimental-design scout:
  - the right next code slice was a deterministic structural spec compiler and a testable decoder candidate, not a new embodied sweep or a new pile of heuristics in `bridge.decoder`

4. What failed or remains open
- No real public VNC export has been ingested yet; the new spec artifacts are still fixture-backed.
- The new `VNCSpecDecoder` is structural, not dynamical. It broadens the output hypothesis, but it does not yet model local VNC recurrence, motor neurons, or muscles.
- I did not launch any new heavy WSL embodied runs in this slice. That was intentional to avoid mixing architectural work with expensive evaluation before a real public graph export exists.

5. Evidence
- New code:
  - `src/vnc/spec_builder.py`
  - `src/vnc/spec_decoder.py`
  - `src/bridge/decoder_factory.py`
  - `scripts/build_vnc_structural_spec.py`
- Updated seam:
  - `src/body/interfaces.py`
  - `src/body/mock_body.py`
  - `src/body/flygym_runtime.py`
  - `src/runtime/closed_loop.py`
- New docs:
  - `docs/vnc_spec_decoder.md`
  - `docs/vnc_data_sources.md`
  - `docs/vnc_workstream_plan.md`
- New artifacts:
  - `outputs/metrics/vnc_structural_spec_mock.json`
  - `outputs/metrics/vnc_structural_spec_mock.csv`

6. Next actions
- Implement `T108`: fetch or otherwise ingest the first real public MANC annotation export locally and normalize it through the existing atlas / graph / spec toolchain.
- Only after the first real public export is in hand, compare the structural VNC decoder candidate against the current sampled/fitted output path on cheap local diagnostics.
- Keep heavy embodied WSL work serialized and deferred until the real-data ingest step is complete.

## 2026-03-12 - Added Feather support so the VNC toolchain can ingest real MANC annotation exports

1. What I attempted
- Remove the format mismatch between the real first public ingest target and the repo's current VNC tooling.
- The concrete issue was simple: the first MANC annotation target is a `.feather` file, while the VNC loaders only supported CSV / TSV / JSON.

2. What succeeded
- Added `.feather` support to:
  - `src/vnc/annotation_atlas.py`
  - `src/vnc/ingest.py`
- Added local coverage for Feather-backed atlas and graph ingest:
  - `tests/test_vnc_annotation_atlas.py`
  - `tests/test_vnc_pathways.py`
- Validation passed:
  - `python -m pytest tests/test_vnc_annotation_atlas.py tests/test_vnc_pathways.py tests/test_vnc_spec_decoder.py tests/test_closed_loop_smoke.py -q` -> `18 passed`
  - `python -m py_compile src/vnc/annotation_atlas.py src/vnc/ingest.py tests/test_vnc_annotation_atlas.py tests/test_vnc_pathways.py` -> passed

3. What failed or remains open
- This still does not fetch the real MANC file. It only removes the parser blocker.
- The remaining open step is now explicit: acquire the real public export locally and run it through the atlas / graph / structural-spec pipeline.

4. Evidence
- Loader updates:
  - `src/vnc/annotation_atlas.py`
  - `src/vnc/ingest.py`
- Coverage:
  - `tests/test_vnc_annotation_atlas.py`
  - `tests/test_vnc_pathways.py`

5. Next actions
- Keep `T108` focused on the real public annotation ingest itself rather than adding more mock-format support.

## 2026-03-12 - Downloaded and normalized the first real public MANC annotation export

1. What I attempted
- Use the official Janelia MANC download page to fetch the first real public VNC annotation export locally.
- Run the existing repo atlas/node tooling on that real file instead of on fixtures.
- Fix the schema mismatch exposed by the real data.

2. What succeeded
- Downloaded:
  - `external/vnc/manc/body-annotations-male-cns-v0.9-minconf-0.5.feather`
- Confirmed the real MANC file schema includes fields such as:
  - `bodyId`
  - `superclass`
  - `type`
  - `class`
  - `rootSide`
  - `somaSide`
  - `somaNeuromere`
- Added a shared schema-normalization layer:
  - `src/vnc/schema.py`
- Updated:
  - `src/vnc/annotation_atlas.py`
  - `src/vnc/ingest.py`
  so the repo now understands MANC-native fields and not only generic mock columns.
- Produced real public-data artifacts:
  - `outputs/metrics/vnc_annotation_atlas_manc_v0p9.json`
  - `outputs/metrics/vnc_annotation_atlas_manc_v0p9.csv`
  - `outputs/metrics/vnc_manc_annotation_node_summary.json`
- Added a dedicated evidence doc:
  - `docs/manc_annotation_ingest.md`
- Local validation still passed:
  - `python -m pytest tests/test_vnc_annotation_atlas.py tests/test_vnc_pathways.py tests/test_vnc_spec_decoder.py tests/test_closed_loop_smoke.py -q` -> `18 passed`

3. What the real data showed
- The first real public annotation file is large enough to matter:
  - `211743` rows
- After canonical normalization, the top super-classes were:
  - `interneuron` `134722`
  - `sensory` `27153`
  - `ascending` `2392`
  - `descending` `1332`
  - `motor` `933`
- The top flow categories were:
  - `intrinsic` `134884`
  - `afferent` `29545`
  - `efferent` `2265`
- A large `<missing>` bucket remains. That is real and should stay visible rather than being hidden by over-aggressive normalization.

4. What failed or remains open
- This is still annotation-only. There is no real public edge file in the pipeline yet.
- The real public pathway inventory and real public structural spec are therefore still blocked on edge ingest.
- I did not attempt the full `connectome-weights` file in this slice because the right first step was to make the annotation ingest correct and explicit first.

5. Evidence
- Real source file:
  - `external/vnc/manc/body-annotations-male-cns-v0.9-minconf-0.5.feather`
- Real artifacts:
  - `outputs/metrics/vnc_annotation_atlas_manc_v0p9.json`
  - `outputs/metrics/vnc_annotation_atlas_manc_v0p9.csv`
  - `outputs/metrics/vnc_manc_annotation_node_summary.json`
- New normalization layer:
  - `src/vnc/schema.py`

6. Next actions
- Start `T109`: acquire the first real public edge export and replace the fixture-backed pathway/spec artifacts with real public graph evidence.
- Keep heavy embodied WSL work deferred until the real graph side exists.

## 2026-03-12 - Completed the first real public MANC edge slice and real-data pathway/spec pipeline

1. What I attempted
- Continue `T109` with sub-agents and move from real annotations to the real public MANC edge file.
- Download the official `connectome-weights` feather.
- Avoid pushing the full `151,871,794`-row graph directly through the small in-memory pathway code.
- Build a filtered first-pass real locomotor slice instead.

2. What succeeded
- Downloaded the real public edge file:
  - `external/vnc/manc/connectome-weights-male-cns-v0.9-minconf-0.5.feather`
- Confirmed the real public schema is exactly:
  - `body_pre`
  - `body_post`
  - `weight`
- Added edge aliases and a filtered feather edge loader in:
  - `src/vnc/schema.py`
  - `src/vnc/ingest.py`
- Added a real MANC thoracic locomotor slice builder in:
  - `src/vnc/manc_slice.py`
- Added a real artifact CLI in:
  - `scripts/build_manc_thoracic_vnc_artifacts.py`
- Added local coverage:
  - `tests/test_vnc_manc_slice.py`
- Real artifact build succeeded and produced:
  - `outputs/metrics/manc_thoracic_slice_summary.json`
  - `outputs/metrics/manc_thoracic_pathway_inventory.json`
  - `outputs/metrics/manc_thoracic_structural_spec.json`
  - `outputs/metrics/manc_thoracic_slice_nodes.csv`
  - `outputs/metrics/manc_thoracic_slice_edges.csv`
  - `outputs/metrics/manc_thoracic_spec_overlap.json`
- Local validation passed:
  - `python -m pytest tests/test_vnc_annotation_atlas.py tests/test_vnc_pathways.py tests/test_vnc_spec_decoder.py tests/test_vnc_manc_slice.py tests/test_closed_loop_smoke.py -q` -> `20 passed`

3. What the sub-agents concluded
- The data scout confirmed the official real public edge path is the bulk MANC `connectome-weights` feather and that MANC does not publish an explicit compact edge-column schema beyond the actual file contents and related docs.
- The codebase scout confirmed the correct move was to filter early in `src/vnc/ingest.py` and keep `pathways.py` and `spec_builder.py` largely unchanged.
- The experimental-design scout confirmed the first real slice should be thoracic locomotor, not full-graph and not another tiny DN subset.

4. What the real data produced
- First real thoracic slice summary:
  - descending seeds: `1316`
  - thoracic motors: `516`
  - promoted premotor candidates: `5474`
  - selected nodes: `7291`
  - selected edges: `228061`
  - `descending -> premotor` edges: `124181`
  - `premotor -> motor` edges: `90463`
  - `descending -> motor` edges: `13417`
  - two-step paths: `2440537`
- First real structural spec:
  - `1301` descending channels
- The real overlap artifact shows that many current repo locomotor names are present in the public MANC slice with thoracic motor reachability, including:
  - `DNg97`
  - `DNp103`
  - `DNp18`
  - `DNpe056`
  - `DNpe016`
  - `DNpe040`
  - `DNp71`
  - `DNa01`
  - `DNa02`
  - `MDN`

5. What failed or remains open
- MANC still does not hand us an explicit public `premotor` label in the annotation feather, so the first real slice promotes premotor candidates by structural rule.
- I did not run embodied WSL evaluation with this real spec yet. The next honest step is slice refinement and comparison, not immediate promotion into the production embodied branch.

6. Evidence
- Real edge source:
  - `external/vnc/manc/connectome-weights-male-cns-v0.9-minconf-0.5.feather`
- New code:
  - `src/vnc/manc_slice.py`
  - `scripts/build_manc_thoracic_vnc_artifacts.py`
- New docs:
  - `docs/manc_edge_slice.md`
- New real public artifacts:
  - `outputs/metrics/manc_thoracic_slice_summary.json`
  - `outputs/metrics/manc_thoracic_pathway_inventory.json`
  - `outputs/metrics/manc_thoracic_structural_spec.json`
  - `outputs/metrics/manc_thoracic_spec_overlap.json`

7. Next actions
- Start `T110`: compare stricter thoracic slice variants before using this real spec as a production decoder candidate.
- Keep heavy embodied WSL runs serialized and deferred until the real slice rules are judged stable enough to justify them.

## 2026-03-12 - Ran the first stricter real MANC slice comparison

1. What I attempted
- Take the first real thoracic locomotor slice and check whether it survives a stricter premotor-candidate rule.
- I reused the same real-data CLI and only tightened:
  - `min_premotor_total_weight`
  - `min_premotor_motor_targets`

2. What succeeded
- Built a stricter real slice with:
  - `min_premotor_total_weight = 200`
  - `min_premotor_motor_targets = 10`
- Produced:
  - `outputs/metrics/manc_thoracic_slice_summary_strict.json`
  - `outputs/metrics/manc_thoracic_pathway_inventory_strict.json`
  - `outputs/metrics/manc_thoracic_structural_spec_strict.json`
  - `outputs/metrics/manc_thoracic_slice_nodes_strict.csv`
  - `outputs/metrics/manc_thoracic_slice_edges_strict.csv`
  - `outputs/metrics/manc_thoracic_slice_comparison.json`

3. What the comparison showed
- Baseline:
  - premotor candidates: `5474`
  - selected nodes: `7291`
  - selected edges: `228061`
  - descending structural channels: `1301`
- Stricter slice:
  - premotor candidates: `2164`
  - selected nodes: `3977`
  - selected edges: `121268`
  - descending structural channels: `1297`

4. Interpretation
- The premotor pool shrank a lot.
- The descending structural channel count barely moved.
- That is a good sign for the first real MANC structural spec: it suggests the broad descending coverage is not collapsing under a tighter premotor rule.

5. Next actions
- Move the next refinement toward biological selectivity, not just numeric thresholding.
- The best next comparison is likely a leg-biased or nerve-filtered thoracic motor slice before any embodied decoder benchmark is attempted.

## 2026-03-12 - Completed `T110` with leg-subclass and exit-nerve real MANC slice variants

1. What I attempted
- Finish the real-data refinement loop for `T110` instead of stopping at a
  looser-vs-stricter threshold comparison.
- Use sub-agents for three separate inputs:
  - local annotation / literature review for biologically selective leg-motor
    endpoints
  - code-shape review for the smallest safe extension point
  - test / docs / tracker expectations for a completed selective-slice pass
- Add selective motor-target modes to the real MANC slicer, regenerate the real
  artifacts, and compare the variants quantitatively.

2. What succeeded
- Added explicit `entry_nerve` / `exit_nerve` preservation to the normalized
  VNC node model in:
  - `src/vnc/schema.py`
  - `src/vnc/ingest.py`
- Extended the real MANC slicer in `src/vnc/manc_slice.py` with two explicit
  selective motor-target modes:
  - `leg_subclass`
  - `exit_nerve`
- Extended the real artifact CLI in
  `scripts/build_manc_thoracic_vnc_artifacts.py` so the selective modes are
  configurable and the node CSV now writes `entry_nerve` / `exit_nerve`.
- Added local coverage:
  - `tests/test_vnc_manc_slice.py`
  - `tests/test_vnc_pathways.py`
- Local validation passed:
  - `python -m pytest tests/test_vnc_manc_slice.py tests/test_vnc_pathways.py tests/test_vnc_spec_decoder.py tests/test_closed_loop_smoke.py -q` -> `18 passed`
  - `python -m py_compile src/vnc/schema.py src/vnc/ingest.py src/vnc/manc_slice.py scripts/build_manc_thoracic_vnc_artifacts.py tests/test_vnc_manc_slice.py tests/test_vnc_pathways.py`

3. What the sub-agents concluded
- The literature/data scout recommended a core leg-motor endpoint keyed to the
  thoracic leg exit nerves `ProLN`, `MesoLN`, and `MetaLN`, with ambiguous T1
  branch nerves treated as an optional expansion rather than the default.
- The code-shape scout confirmed that a true nerve-filtered slice needed the
  normalized node model to preserve `exitNerve` explicitly instead of trying to
  smuggle it through the overloaded `region` field.
- The testing/docs scout confirmed that `T110` should not be treated as
  complete unless the selective rules, artifacts, and comparison outputs are
  explicit and auditable.

4. What the real selective comparison produced
- Broad leg-subclass slice:
  - motor targets: `381`
  - premotor candidates: `3607`
  - selected edges: `140223`
  - two-step paths: `1460577`
  - descending structural channels: `1240`
- Strict leg-subclass slice:
  - motor targets: `381`
  - premotor candidates: `1304`
  - selected edges: `68222`
  - two-step paths: `848280`
  - descending structural channels: `1168`
- Core exit-nerve slice:
  - motor targets: `319`
  - premotor candidates: `2850`
  - selected edges: `106154`
  - two-step paths: `1028420`
  - descending structural channels: `1232`
- Strict exit-nerve slice:
  - motor targets: `319`
  - premotor candidates: `910`
  - selected edges: `46554`
  - two-step paths: `550740`
  - descending structural channels: `1131`

5. Interpretation
- The exit-nerve slice is the strongest next candidate.
- It removes the ambiguous T1 branch outputs that survive the broad
  `leg_subclass` filter and keeps only:
  - `ProLN`
  - `MesoLN`
  - `MetaLN`
- The non-strict exit-nerve slice still preserves the full live locomotor
  shortlist overlap used in this repo:
  - overlap count `30`, same as baseline and broad subclass slice
- The strict exit-nerve slice is probably too aggressive for the default next
  benchmark because it drops one `DNpe040` overlap channel.
- The broad subclass slice remains useful as a reference, but it still admits
  non-core branch outputs:
  - `DProN`
  - `VProN`
  - `ProAN`
  - `AbN1`

6. Evidence
- New real selective comparison artifacts:
  - `outputs/metrics/manc_thoracic_variant_comparison.json`
  - `outputs/metrics/manc_thoracic_variant_overlap_comparison.json`
- New selective slice summaries:
  - `outputs/metrics/manc_thoracic_slice_summary_leg_subclass.json`
  - `outputs/metrics/manc_thoracic_slice_summary_leg_subclass_strict.json`
  - `outputs/metrics/manc_thoracic_slice_summary_exit_nerve.json`
  - `outputs/metrics/manc_thoracic_slice_summary_exit_nerve_strict.json`
- New selective structural specs:
  - `outputs/metrics/manc_thoracic_structural_spec_leg_subclass.json`
  - `outputs/metrics/manc_thoracic_structural_spec_leg_subclass_strict.json`
  - `outputs/metrics/manc_thoracic_structural_spec_exit_nerve.json`
  - `outputs/metrics/manc_thoracic_structural_spec_exit_nerve_strict.json`
- Overlap artifacts:
  - `outputs/metrics/manc_thoracic_spec_overlap_leg_subclass.json`
  - `outputs/metrics/manc_thoracic_spec_overlap_leg_subclass_strict.json`
  - `outputs/metrics/manc_thoracic_spec_overlap_exit_nerve.json`
  - `outputs/metrics/manc_thoracic_spec_overlap_exit_nerve_strict.json`
- Updated docs:
  - `docs/manc_edge_slice.md`
  - `docs/vnc_workstream_plan.md`

7. What remains open
- `T110` is now done as a real-slice comparison task, but it is still not an
  embodied performance claim.
- No heavy WSL embodied decoder benchmark was launched in this loop.
- The next honest step is `T111`: load the non-strict `exit_nerve` structural
  spec as the first real production `vnc_structural_spec` candidate and smoke
  it in the closed loop before attempting broader comparisons.

## 2026-03-12 - Completed `T111` and exposed the real MANC-to-FlyWire ID blocker

1. What I attempted
- Take the preferred non-strict `exit_nerve` structural spec from `T110` and
  benchmark it as the first production `vnc_structural_spec` decoder candidate.
- Keep the ladder honest:
  - config and decoder load test
  - runtime smoke for the VNC decoder seam
  - host mock-body benchmark with the real torch brain backend
  - short real WSL FlyGym benchmark
  - explicit ID-space audit instead of guessing about the zero-output failure

2. What succeeded
- Added reproducible configs:
  - `configs/mock_multidrive_torch.yaml`
  - `configs/mock_vnc_structural_spec_exit_nerve.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_vnc_structural_spec_exit_nerve.yaml`
- Added a cheap alignment audit:
  - `scripts/audit_decoder_id_alignment.py`
- Added coverage:
  - `tests/test_vnc_spec_decoder.py`
  - `tests/test_closed_loop_smoke.py`
- Local validation passed:
  - `python -m pytest tests/test_vnc_spec_decoder.py tests/test_closed_loop_smoke.py -q` -> `14 passed`
  - `python -m py_compile src/vnc/spec_decoder.py src/bridge/decoder_factory.py src/runtime/closed_loop.py tests/test_vnc_spec_decoder.py scripts/audit_decoder_id_alignment.py`
- Host mock benchmarks completed:
  - `outputs/benchmarks/fullstack_mock_multidrive_torch_0p4s.csv`
  - `outputs/benchmarks/fullstack_mock_vnc_structural_spec_exit_nerve_0p4s.csv`
- Short real WSL realistic-vision benchmarks completed:
  - `outputs/benchmarks/fullstack_vnc_structural_spec_exit_nerve_target_0p1s.csv`
  - `outputs/benchmarks/fullstack_splice_uvgrid_descending_calibrated_target_t111_0p1s.csv`
- Wrote the machine-readable T111 summary:
  - `outputs/metrics/t111_exit_nerve_decoder_summary.json`
- Wrote the explicit ID-alignment audit:
  - `outputs/metrics/t111_decoder_id_alignment_comparison.json`
- Wrote the bench note:
  - `docs/vnc_exit_nerve_decoder_validation.md`

3. What the sub-agents concluded
- The right comparison ladder was mock-body seam validation first, then one
  short real FlyGym run, not a large sweep.
- The structural decoder config seam was already present; the key missing work
  was not more decoder math but real config files and a clear runtime audit.
- The real risk was not only saturation. It was that the MANC structural spec
  and the FlyWire brain backend might live in different ID spaces.

4. What the benchmarks showed
- Host mock path:
  - both the sampled decoder and the structural decoder stayed at zero command
  - that is consistent with the earlier public-input motor-path weakness
- Short real WSL target run with the new structural decoder:
  - completed `50` cycles at `0.1 s`
  - real-time factor: `0.00237`
  - nonzero command cycles: `0`
- Matched short real WSL target run with the current calibrated sampled decoder:
  - completed `50` cycles at `0.1 s`
  - real-time factor: `0.00244`
  - nonzero command cycles: `43`

5. Decisive blocker
- The explicit alignment audit showed:
  - real exit-nerve structural decoder requested IDs: `736`
  - FlyWire backend matched IDs: `0`
  - current sampled decoder requested IDs: `42`
  - FlyWire backend matched IDs: `42`
- That means the real MANC structural decoder is currently a silent no-op
  against the FlyWire whole-brain backend.
- This is not primarily a gain-tuning problem.
- It is an ID-space mismatch between:
  - real MANC body IDs
  - the FlyWire IDs used by the current brain backend

6. Interpretation
- `T111` is complete as a benchmark and diagnosis task.
- The runtime seam for `vnc_structural_spec` works.
- The real config path works.
- The real short benchmark works.
- But the candidate is not promotable because it cannot currently read
  meaningful brain activity from the present FlyWire backend.

7. Next actions
- Start `T112`: resolve the MANC-to-FlyWire ID-space blocker.
- Do not waste time tuning `forward_scale_hz`, `turn_scale_hz`, or channel
  thresholds further until the decoder can actually monitor a matching ID space.

## 2026-03-12 - T112 public ID-bridge review

1. What I attempted
- Reviewed the local `T111` decoder-alignment evidence and the bundled MANC
  annotation export to determine whether the current blocker is a missing
  public cross-dataset neuron-ID bridge.
- Reviewed public primary/public resources for MANC/FlyWire/BANC cross-dataset
  matching, with emphasis on official annotation tooling and the neck-connective
  comparative connectomics work.

2. What succeeded
- Confirmed locally that the runtime blocker is an ID-space mismatch, not a
  gain-tuning issue: the real MANC exit-nerve decoder requested `736` IDs and
  matched `0` against the present FlyWire backend, while the sampled
  FlyWire-native decoder matched `42/42`.
- Confirmed locally that the public MANC annotation export already carries
  annotation-level bridge fields including `mancType`, `flywireType`, and
  `hemibrainType`, which is consistent with a public homolog/type bridge rather
  than an exact raw-ID crosswalk.
- Confirmed from public sources that the strongest published cross-dataset
  bridge is at the matched type/group/homolog level, especially for
  neck-connective DNs and ANs spanning FAFB-FlyWire, FANC, and MANC.

3. What failed
- Did not find a general public exact `MANC bodyid -> FlyWire root_id`
  crosswalk that would let the current real MANC structural decoder monitor
  arbitrary FlyWire neurons by direct ID substitution.
- Did not find evidence that BANC publishes a general exact `MANC <-> FlyWire`
  per-neuron raw-ID bridge either; the public bridge appears to remain
  type/group-level.

4. Evidence
- Local: `outputs/metrics/t111_decoder_id_alignment_comparison.json`
- Local: `external/vnc/manc/body-annotations-male-cns-v0.9-minconf-0.5.feather`
- Public: `https://www.nature.com/articles/s41586-025-08925-z`
- Public: `https://github.com/flyconnectome/2023neckconnective`
- Public: `https://natverse.org/malecns/`
- Public: `https://www.nature.com/articles/s41586-024-07686-5`
- Public: `https://www.janelia.org/project-team/flyem/manc-connectome`

5. Next actions
- Treat exact MANC-to-FlyWire neuron-ID substitution as unavailable in the
  public stack unless a narrower curated subset proves otherwise.
- Design the next decoder bridge around public `cell_type` / homolog-group /
  `side` metadata, prioritizing neck-connective DN classes where the
  comparative literature is strongest.

## 2026-03-12 - T112 completed with a FlyWire semantic monitor-space bridge

1. What I attempted
- Continue `T112` past the literature review and replace the zero-overlap
  decoder path with an explicit bridge from the real MANC `exit_nerve`
  structural spec into the FlyWire monitor space used by the current
  whole-brain backend.
- Use sub-agents for three parallel checks:
  - local seam review for the minimal honest implementation
  - public literature review on whether an exact raw-ID crosswalk exists
  - local annotation overlap review for exact shared `cell_type + side`
    coverage
- Keep heavy compute serialized and only run one short real WSL benchmark after
  the bridge and tests were in place.

2. What succeeded
- Implemented the semantic bridge tooling in:
  - `src/vnc/flywire_bridge.py`
  - `scripts/build_vnc_flywire_semantic_spec.py`
- Extended the decoder in:
  - `src/vnc/spec_decoder.py`
  so `vnc_structural_spec` channels can now monitor grouped FlyWire roots via
  `monitor_ids` and pool them with `monitor_reduce = mean`.
- Added real bridge configs:
  - `configs/mock_vnc_structural_spec_exit_nerve_flywire_semantic.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_vnc_structural_spec_exit_nerve_flywire_semantic.yaml`
- Added validation coverage:
  - `tests/test_vnc_flywire_bridge.py`
  - `tests/test_vnc_spec_decoder.py`
  - `tests/test_closed_loop_smoke.py`
- Materialized the bridged real-data artifact:
  - `outputs/metrics/manc_thoracic_structural_spec_exit_nerve_flywire_semantic.json`
- Bridge summary from that artifact:
  - source channels: `1232`
  - source semantic keys: `926`
  - bridged semantic channels: `847`
  - matched source channels: `1095`
  - unmatched source channels: `137`
  - FlyWire monitor IDs after completeness filtering: `1145`
  - match counts:
    - exact `cell_type`: `770`
    - `hemibrain_type` fallback: `77`
- Cleared the runtime ID blocker:
  - raw real MANC spec config requested `736` IDs and matched `0`
  - bridged semantic config requested `685` IDs and matched `685`
- Ran a short serialized real WSL benchmark with the bridged config:
  - `outputs/benchmarks/fullstack_vnc_structural_spec_exit_nerve_flywire_semantic_target_0p1s.csv`
  - `outputs/requested_0p1s_vnc_structural_spec_exit_nerve_flywire_semantic_target/*`
  - `outputs/metrics/t112_exit_nerve_flywire_semantic_summary.json`
- That real run is no longer silent:
  - completed `50` cycles at `0.1 s`
  - real-time factor: `0.00232`
  - nonzero command cycles: `43`
  - max forward / turn signals both reached `1.0`
  - both left and right drives clipped at `1.2`

3. What failed
- The first bridged run is not behaviorally calibrated yet.
- The bridge solves monitor-space compatibility, but the decoder is currently
  saturating under the first semantic-weight scaling choice.
- No public general exact `MANC bodyid -> FlyWire root_id` crosswalk emerged;
  the bridge remains annotation-level rather than exact neuron identity.

4. Evidence
- Code:
  - `src/vnc/flywire_bridge.py`
  - `src/vnc/spec_decoder.py`
  - `scripts/build_vnc_flywire_semantic_spec.py`
- Configs:
  - `configs/mock_vnc_structural_spec_exit_nerve_flywire_semantic.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_vnc_structural_spec_exit_nerve_flywire_semantic.yaml`
- Tests:
  - `tests/test_vnc_flywire_bridge.py`
  - `tests/test_vnc_spec_decoder.py`
  - `tests/test_closed_loop_smoke.py`
- Artifacts:
  - `outputs/metrics/manc_thoracic_structural_spec_exit_nerve_flywire_semantic.json`
  - `outputs/metrics/t112_decoder_id_alignment_comparison.json`
  - `outputs/metrics/t112_decoder_id_alignment_semantic.json`
  - `outputs/metrics/t112_exit_nerve_flywire_semantic_summary.json`
  - `outputs/benchmarks/fullstack_vnc_structural_spec_exit_nerve_flywire_semantic_target_0p1s.csv`
- Docs:
  - `docs/vnc_flywire_semantic_bridge.md`
  - `docs/vnc_spec_decoder.md`
  - `docs/vnc_workstream_plan.md`
  - `docs/vnc_exit_nerve_decoder_validation.md`

5. Validation
- `python -m pytest tests/test_flywire_annotations.py tests/test_vnc_flywire_bridge.py tests/test_vnc_spec_decoder.py tests/test_closed_loop_smoke.py -q` -> `25 passed`
- `python -m py_compile src/brain/flywire_annotations.py src/vnc/flywire_bridge.py src/vnc/spec_decoder.py scripts/build_vnc_flywire_semantic_spec.py tests/test_vnc_flywire_bridge.py tests/test_vnc_spec_decoder.py` -> passed

6. Next actions
- Mark `T112` done.
- Start `T113`: calibrate the FlyWire-semantic VNC structural decoder so the
  bridged path stops saturating and can be judged on real behavior rather than
  only on ID-space validity.

## 2026-03-12 - Started `T113` with decoder normalization and tracked-camera reruns

1. What I attempted
- Investigate the user's report that the `T112` semantic-VNC demo looked bad
  because the fly ran off screen.
- Separate the problem into:
  - camera framing
  - decoder saturation
- Fix the decoder math first instead of only moving the camera.

2. What succeeded
- Confirmed from the `2.0 s` semantic-VNC run log that the fly really was
  leaving the frame under the old branch:
  - `992 / 1000` nonzero command cycles
  - drives repeatedly clipping at `1.2`
  - final position about `x = 40.69`
- Confirmed the video framing issue was real and mechanical:
  - `src/body/flygym_runtime.py` used a fixed world-mounted bird's-eye camera
    at `pos = (5, 0, 35)`
- Patched the runtime so the semantic-VNC branch can use a tracked FlyGym
  camera:
  - `src/body/flygym_runtime.py`
  - `src/runtime/closed_loop.py`
  - `configs/flygym_realistic_vision_splice_uvgrid_vnc_structural_spec_exit_nerve_flywire_semantic.yaml`
- Patched the decoder math in `src/vnc/spec_decoder.py`:
  - old path: summed `rate * structural_weight` directly into forward/turn
  - new path: divides weighted left/right totals by the total left/right
    structural weight mass of the loaded channels, then computes forward/turn
    from those normalized weighted mean rates
- Updated semantic-VNC config scales/gains to match the normalized decoder:
  - `forward_scale_hz: 20.0`
  - `turn_scale_hz: 10.0`
  - `forward_gain: 0.75`
  - `turn_gain: 0.3`
- Added/updated tests:
  - `tests/test_vnc_spec_decoder.py`
  - `tests/test_closed_loop_smoke.py`
- Short real rerun after decoder fix:
  - `outputs/benchmarks/fullstack_vnc_structural_spec_exit_nerve_flywire_semantic_decoder_fixed_target_0p1s.csv`
  - result:
    - `45 / 50` nonzero command cycles
    - `max_left_drive = 0.529`
    - `max_right_drive = 0.932`
    - `max_forward_signal = 0.858`
    - `max_turn_signal = 0.963`
- Full `2.0 s` corrected rerun:
  - `outputs/benchmarks/fullstack_vnc_structural_spec_exit_nerve_flywire_semantic_decoder_fixed_follow_yaw_target_2s.csv`
  - `outputs/requested_2s_vnc_structural_spec_exit_nerve_flywire_semantic_decoder_fixed_follow_yaw_target/flygym-demo-20260312-184650/demo.mp4`
  - result:
    - `1000 / 1000` cycles completed
    - `995 / 1000` cycles nonzero
    - `max_left_drive = 0.867`
    - `max_right_drive = 0.957`
    - final position about `x = 7.02`, `y = 1.00`
    - stable final frame remained on screen under the follow camera
- Final corrected `2.0 s` metrics:
  - `avg_forward_speed = 4.7635`
  - `net_displacement = 7.0699`
  - `displacement_efficiency = 0.7428`
  - `real_time_factor = 0.00244`

3. What failed
- This is not yet a biologically tuned semantic-VNC controller.
- The corrected branch is much better behaved than the first `T112` demo, but
  it still needs behavioral tuning and scene-level review, not just scalar
  command checks.

4. Evidence
- Code:
  - `src/vnc/spec_decoder.py`
  - `src/body/flygym_runtime.py`
  - `src/runtime/closed_loop.py`
- Tests:
  - `tests/test_vnc_spec_decoder.py`
  - `tests/test_closed_loop_smoke.py`
- Artifacts:
  - `outputs/benchmarks/fullstack_vnc_structural_spec_exit_nerve_flywire_semantic_decoder_fixed_target_0p1s.csv`
  - `outputs/benchmarks/fullstack_vnc_structural_spec_exit_nerve_flywire_semantic_decoder_fixed_follow_yaw_target_2s.csv`
  - `outputs/requested_0p1s_vnc_structural_spec_exit_nerve_flywire_semantic_decoder_fixed_target/*`
  - `outputs/requested_2s_vnc_structural_spec_exit_nerve_flywire_semantic_decoder_fixed_follow_yaw_target/flygym-demo-20260312-184650/demo.mp4`
  - `outputs/screenshots/demo.png`

5. Validation
- `python -m pytest tests/test_vnc_spec_decoder.py tests/test_closed_loop_smoke.py -q` -> `18 passed`
- `python -m py_compile src/vnc/spec_decoder.py src/body/flygym_runtime.py src/runtime/closed_loop.py tests/test_vnc_spec_decoder.py tests/test_closed_loop_smoke.py` -> passed

6. Next actions
- Continue `T113` with scene-level review of the corrected `2.0 s` semantic-VNC
  demo.
- If the motion still looks implausible, tune channel filtering and gains from
  the normalized decoder rather than reverting to raw weight-mass sums.

## 2026-03-12 - Semantic-VNC branch frozen as failed parity branch

1. What I attempted
- Wrote the semantic-VNC branch up explicitly as a failed parity branch instead of leaving it in a vague "needs more tuning" state.
- Added a dedicated freeze note and artifact-lock manifest.
- Closed `T113` with a final branch verdict.

2. What succeeded
- Added the freeze writeup:
  - `docs/semantic_vnc_failed_parity_branch.md`
- Updated the main parity and gap reports so the semantic-VNC branch is not treated as a live parity candidate:
  - `REPRO_PARITY_REPORT.md`
  - `ASSUMPTIONS_AND_GAPS.md`
- Updated the task tracker to close `T113` with a failed-parity outcome:
  - `TASKS.md`
- Added the locked-artifact manifest:
  - `outputs/locks/semantic_vnc_failed_parity_branch_manifest.md`

3. What failed
- No new technical failure occurred in this slice.
- The branch failure itself is now the recorded result:
  - semantic ID alignment works
  - decoder saturation was fixed
  - framing was fixed
  - target tracking still fails

4. Evidence paths
- `docs/semantic_vnc_failed_parity_branch.md`
- `outputs/locks/semantic_vnc_failed_parity_branch_manifest.md`
- `outputs/metrics/t112_decoder_id_alignment_comparison.json`
- `outputs/metrics/t112_exit_nerve_flywire_semantic_summary.json`
- `outputs/requested_2s_vnc_structural_spec_exit_nerve_flywire_semantic_decoder_fixed_follow_yaw_target/flygym-demo-20260312-184650/demo.mp4`
- `outputs/requested_2s_vnc_structural_spec_exit_nerve_flywire_semantic_decoder_fixed_follow_yaw_target/flygym-demo-20260312-184650/metrics.csv`

5. Next actions
- None in this turn.
- The semantic-VNC branch is frozen and should not be mutated in place.

## 2026-03-12 - Current best branch activation visualization

1. What I attempted
- Built a dedicated capture/render pipeline for a synchronized activation view
  of the current best embodied branch.
- Kept the expensive work serialized in one WSL FlyGym run.
- Used the monitored-only extension of the calibrated branch so the artifact
  could show broad descending/efferent activity without changing the underlying
  splice branch.

2. What succeeded
- Added the visualization module and CLI:
  - `src/visualization/activation_viz.py`
  - `src/visualization/__init__.py`
  - `scripts/build_best_branch_activation_visualization.py`
- Added a renderer smoke test:
  - `tests/test_activation_viz.py`
- Host validation passed:
  - `python -m pytest tests/test_activation_viz.py -q` -> `1 passed`
  - `python -m py_compile src/visualization/activation_viz.py src/visualization/__init__.py scripts/build_best_branch_activation_visualization.py tests/test_activation_viz.py` -> passed
- Completed the real WSL artifact build:
  - `outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/activation_side_by_side.mp4`
  - `outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/overview.png`
  - `outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/capture_data.npz`
  - `outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/source_demo.mp4`
  - `outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/summary.json`
- Captured scope from `summary.json`:
  - `frame_count = 200`
  - `brain_neuron_count = 138639`
  - `flyvis_neuron_count = 45669`
  - `monitor_label_count = 16`
  - `controller_label_count = 8`

3. What failed
- The first real smoke attempt on host Python failed because the new script
  did not add `src` to `sys.path`.
- The first real FlyGym smoke attempt also failed on host because `flygym` is
  only validated in the WSL `flysim-full` environment.
- Both were corrected before the full run:
  - script import shim added
  - real run moved to WSL `micromamba run -n flysim-full`

4. Evidence paths
- `docs/current_best_branch_activation_visualization.md`
- `outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/activation_side_by_side.mp4`
- `outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/overview.png`
- `outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/capture_data.npz`
- `outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/run.jsonl`
- `outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/metrics.csv`

5. Next actions
- None in this turn.
- The requested activation visualization artifact now exists and is documented.

## 2026-03-12 - Whitepaper and README frontpage refresh

1. What I attempted
- Refreshed the main whitepaper so it reflects the newest repo state instead of stopping before the semantic-VNC freeze and the activation visualization artifact.
- Replaced the repo-home `README.md` with an actual front page derived from the whitepaper and parity docs.
- Prepared the docs-only update for commit and push.

2. What succeeded
- Updated the long-form whitepaper:
  - `docs/openfly_whitepaper.md`
- Rewrote the GitHub landing page:
  - `README.md`
- Added tracker coverage for the docs refresh:
  - `TASKS.md`
  - `PROGRESS_LOG.md`
- The whitepaper now explicitly includes:
  - the semantic-VNC `exit_nerve_flywire_semantic` branch as a frozen failed parity result
  - the synchronized current-best activation visualization as a first-class evidence artifact

3. What failed
- No code or runtime work was attempted in this slice.
- No tests were run because this was a documentation-only refresh.

4. Evidence paths
- `docs/openfly_whitepaper.md`
- `README.md`
- `TASKS.md`
- `PROGRESS_LOG.md`
- `REPRO_PARITY_REPORT.md`
- `docs/current_best_branch_activation_visualization.md`
- `docs/semantic_vnc_failed_parity_branch.md`

5. Next actions
- Commit and push the docs-only refresh to `origin/main`.

## 2026-03-13 - Best-branch end-to-end investigation for no-shortcuts embodiment

1. What I attempted
- Investigated the current best branch using only recorded artifacts rather than
  launching a new heavy embodied run.
- Analyzed the synchronized activation capture, matched behavior metrics, and
  monitor/controller traces together.
- Focused on learning what would plausibly advance embodiment without adding
  new shortcuts.

2. What succeeded
- Added a reusable analysis module and CLI:
  - `src/analysis/best_branch_investigation.py`
  - `scripts/analyze_best_branch_embodiment.py`
- Added a focused local test:
  - `tests/test_best_branch_investigation.py`
- Materialized investigation artifacts:
  - `outputs/metrics/best_branch_investigation_summary.json`
  - `outputs/metrics/best_branch_investigation_behavior_summary.csv`
  - `outputs/metrics/best_branch_investigation_family_correlations.csv`
  - `outputs/metrics/best_branch_investigation_monitor_correlations.csv`
  - `outputs/metrics/best_branch_investigation_unsampled_central_units.csv`
  - `outputs/metrics/best_branch_investigation_unsampled_central_spiking_units.csv`
  - `outputs/plots/best_branch_investigation_family_target_bearing_corr.png`
  - `outputs/plots/best_branch_investigation_monitor_target_bearing_corr.png`
- Wrote the interpretation note:
  - `docs/best_branch_e2e_investigation.md`

3. What failed
- No new runtime failure occurred.
- Sub-agent turnaround was unreliable in this slice, so the decisive technical
  findings came from the local reproducible analysis rather than waiting on the
  sidecar syntheses.

4. Evidence
- Tests:
  - `python -m pytest tests/test_best_branch_investigation.py -q` -> `3 passed`
- Analysis outputs:
  - `outputs/metrics/best_branch_investigation_summary.json`
  - `outputs/metrics/best_branch_investigation_family_correlations.csv`
  - `outputs/metrics/best_branch_investigation_monitor_correlations.csv`
  - `docs/best_branch_e2e_investigation.md`

5. Next actions
- Build matched monitored activation captures for `target`, `no_target`, and
  `zero_brain` under the same config.
- Expand monitoring to the strongest unsampled relay families before changing
  the splice or decoder again.

## 2026-03-13 - Spontaneous-state workstream framing

1. What I attempted
- Added a docs-only framing note for the spontaneous-state program so the next
  cold-start work is defined before anyone starts patching runtime logic.
- Tied the new note directly to the current best-branch investigation and the
  existing `zero_brain` / brain-control evidence.
- Added a tracked task for the spontaneous-state workstream.

2. What succeeded
- Added the workstream note:
  - `docs/spontaneous_state_program.md`
- Added a new tracked task:
  - `T117` in `TASKS.md`
- Recorded this docs-only milestone in:
  - `PROGRESS_LOG.md`
- The new note now states:
  - why the current cold-start is functionally dead at the body-control
    boundary even though the backend itself is not dead
  - what counts as biologically plausible endogenous activity in this repo
  - what validation gates must be passed before any spontaneous-state
    implementation can be treated as honest progress

3. What failed
- No code or runtime experiments were attempted in this slice.
- No tests were run because this update intentionally stayed within
  `docs/`, `TASKS.md`, and `PROGRESS_LOG.md`.

4. Evidence
- `docs/spontaneous_state_program.md`
- `TASKS.md`
- `PROGRESS_LOG.md`
- `docs/best_branch_e2e_investigation.md`
- `docs/brain_control_validation.md`

5. Next actions
- Use `T117` as the tracking root for matched startup-state diagnostics.
- Add matched `target`, `no_target`, and `zero_brain` activation/control
  captures before proposing any endogenous-state mechanism.
- Keep the spontaneous-state path inside the no-shortcuts boundary documented
  in `docs/spontaneous_state_program.md`.

## 2026-03-13 - Spontaneous-state backend pilot: sparse tonic occupancy plus slow latent fluctuations

1. What I attempted
- Audited the current Torch whole-brain backend and confirmed that the old
  reset path had an absorbing silent fixed point with no endogenous source of
  activity.
- Added an opt-in spontaneous-state path inside `WholeBrainTorchBackend`
  instead of touching the decoder or body controller.
- Implemented a first biologically stricter candidate: sparse lognormal tonic
  background plus low-rank slow latent fluctuations and reset voltage
  heterogeneity.
- Added a brain-only audit path and startup-state logging so the new branch can
  be judged from saved artifacts rather than from impressionistic demos.

2. What succeeded
- Wired the new backend config path:
  - `src/brain/pytorch_backend.py`
  - `src/runtime/closed_loop.py`
  - `benchmarks/run_brain_benchmarks.py`
  - `configs/brain_spontaneous_probe.yaml`
- Added tests and logging support:
  - `tests/test_spontaneous_state_unit.py`
  - `tests/test_closed_loop_smoke.py`
  - `src/bridge/controller.py`
- Added reproducible docs for the workstream:
  - `docs/spontaneous_state_backend_design.md`
  - `docs/spontaneous_state_validation_plan.md`
  - `docs/spontaneous_state_results.md`
- Added a reproducible brain-only audit:
  - `scripts/run_spontaneous_state_audit.py`
- Produced the first artifact-complete pilot bundle:
  - `outputs/metrics/spontaneous_state_pilot_summary.json`
  - `outputs/metrics/spontaneous_state_latent_pilot_summary.json`
  - `outputs/metrics/spontaneous_state_latent_seed0_summary.json`
  - `outputs/metrics/spontaneous_state_latent_seed1_summary.json`
  - `outputs/metrics/spontaneous_state_latent_seed2_summary.json`
  - matching CSV, PNG, and benchmark CSV outputs under `outputs/metrics/`,
    `outputs/plots/`, and `outputs/benchmarks/`
- The old cold-start condition stayed exactly silent.
- The latent pilot no longer stayed dead:
  - `candidate_ongoing.mean_spike_fraction ~= 3.14e-4`
  - `candidate_ongoing.background_mean_rate_hz ~= 0.254`
  - `candidate_ongoing.background_active_fraction ~= 0.147`
  - `candidate_ongoing.nonzero_window_fraction = 1.0`
  - structure ratio `~= 1.115`
  - pulse peak turn asymmetry `= 200 Hz` in the seed-0 pilot

3. What failed
- The first static sparse-tonic candidate was too weak; monitored structure was
  effectively absent and the monitored motor layer stayed near zero.
- The current latent candidate is not yet robust enough across seeds:
  - seed `0`: ongoing baseline turn bias `+20 Hz`, pulse peak `200 Hz`
  - seed `1`: ongoing baseline turn bias `-5 Hz`, pulse peak `0 Hz`
  - seed `2`: ongoing baseline turn bias `+17.5 Hz`, pulse peak `200 Hz`
- Spontaneous motor-side lateral bias under symmetric zero-input conditions is
  still too strong for promotion.
- No embodied `target` / `no_target` / `zero_brain` spontaneous-state runs were
  launched in this slice, so no embodied improvement claim is being made.

4. Evidence
- Tests:
  - `python -m pytest tests/test_closed_loop_smoke.py tests/test_brain_backend.py tests/test_spontaneous_state_unit.py -q` -> `21 passed`
- Brain-only pilot outputs:
  - `outputs/metrics/spontaneous_state_pilot_summary.json`
  - `outputs/metrics/spontaneous_state_latent_pilot_summary.json`
  - `outputs/metrics/spontaneous_state_latent_seed0_summary.json`
  - `outputs/metrics/spontaneous_state_latent_seed1_summary.json`
  - `outputs/metrics/spontaneous_state_latent_seed2_summary.json`
- Docs:
  - `docs/spontaneous_state_backend_design.md`
  - `docs/spontaneous_state_validation_plan.md`
  - `docs/spontaneous_state_results.md`

5. Next actions
- Reduce spontaneous left/right bias under symmetric control without falling
  back into a dead-cold state.
- Improve seed robustness of the latent candidate.
- Run short matched embodied `target` / `no_target` / `zero_brain` validations
  with the new `brain_backend_state` logging before promoting any spontaneous
  branch config.

## 2026-03-13 - Central-family bilateral spontaneous-state candidate clears the brain-only bar

1. What I attempted
- Iterated on the backend-only spontaneous-state candidate instead of moving to
  embodied validation too early.
- Replaced the earlier random neuron-level latent structure with a bilateral
  family-structured candidate built from the public FlyWire annotation
  supplement.
- Restricted the spontaneous family pool to central/integrative super-classes
  so the background state would stop being dominated by giant optic/sensory
  families.
- Added homologous-family metrics to the audit so the candidate could be judged
  against public whole-brain monitoring results rather than only against a few
  motor readouts.

2. What succeeded
- Updated the backend to support family-structured spontaneous modes:
  - `src/brain/pytorch_backend.py`
- Updated the audit tool to evaluate family-level bilateral structure:
  - `scripts/run_spontaneous_state_audit.py`
- Promoted the new best probe config:
  - `configs/brain_spontaneous_probe.yaml`
- Materialized the new best-candidate artifacts:
  - `outputs/metrics/spontaneous_state_best_candidate_summary.json`
  - `outputs/metrics/spontaneous_state_central_seed0_summary.json`
  - `outputs/metrics/spontaneous_state_central_seed1_summary.json`
  - `outputs/metrics/spontaneous_state_central_seed2_summary.json`
  - `outputs/metrics/spontaneous_state_central_seed_summary.json`
  - `outputs/metrics/spontaneous_state_central_seed_summary.csv`
- The new candidate now shows:
  - sparse bounded ongoing activity
  - low spontaneous turn bias under symmetric zero-input conditions
  - positive homologous-family coupling
  - retained pulse perturbability across all tested seeds

3. What failed
- The first bilateral family sweep was too weak and effectively silent:
  - `outputs/metrics/spontaneous_state_bilateral_a_summary.json`
- A stronger bilateral family sweep became active but had weak structure and no
  useful pulse expression:
  - `outputs/metrics/spontaneous_state_bilateral_b_summary.json`
- The family-level audit initially had a real bug: family monitor groups were
  registered with backend indices instead of FlyWire root IDs. That produced
  invalid homologous-family metrics until fixed.
- Embodied matched-control validation is still intentionally not done in this
  entry.

4. Evidence
- Tests:
  - `python -m pytest tests/test_closed_loop_smoke.py tests/test_brain_backend.py tests/test_spontaneous_state_unit.py -q` -> `21 passed`
- Best-candidate summaries:
  - `outputs/metrics/spontaneous_state_best_candidate_summary.json`
  - `outputs/metrics/spontaneous_state_central_seed_summary.json`
  - `docs/spontaneous_state_results.md`
- Updated mechanism/design notes:
  - `docs/spontaneous_state_backend_design.md`
  - `ASSUMPTIONS_AND_GAPS.md`

5. Next actions
- Use the central-family bilateral candidate as the baseline for the first
  embodied spontaneous-state validation.
- Run matched short `target` / `no_target` / `zero_brain` tests with
  `brain_backend_state` logging.
- Keep embodied promotion blocked until the new candidate improves startup
  readiness without collapsing control separation.

## 2026-03-13 - Default activation capture and iterative decoding workbench

1. What I attempted
- Moved the synchronized activation visualization out of its special-case
  rerun path and into the normal closed-loop run path.
- Added a repo-native decoding-cycle workbench so the activation artifact can
  drive a repeatable relay/monitor expansion loop instead of ad hoc neuron
  guessing.
- Reused sub-agent scouting to ground the design against the current repo seam
  and the public data layers that are actually available now.

2. What succeeded
- Added same-run activation capture/render support to the main runtime:
  - `src/runtime/closed_loop.py`
  - `src/visualization/session.py`
  - `src/visualization/activation_viz.py`
- Ensured non-monitored population configs still expose monitor-style traces by
  falling back to population groups when explicit monitor groups are absent:
  - `src/bridge/decoder.py`
- Added a synthetic splice-cache path for fast mock runs so the activation
  capture seam can be smoke-tested:
  - `src/body/mock_body.py`
- Relaxed the standalone visualization script so it discovers monitor labels
  from live motor-readout keys instead of requiring a hand-authored monitor
  list:
  - `scripts/build_best_branch_activation_visualization.py`
- Added the iterative decoding workbench and CLI:
  - `src/analysis/iterative_decoding.py`
  - `scripts/run_iterative_decoding_cycle.py`
  - `tests/test_iterative_decoding.py`
- Ran the first decoding cycle on the current best activation capture:
  - `outputs/metrics/iterative_decoding_cycle_summary.json`
  - `outputs/metrics/iterative_decoding_cycle_family_scores.csv`
  - `outputs/metrics/iterative_decoding_cycle_monitor_scores.csv`
  - `outputs/metrics/iterative_decoding_cycle_monitor_expansion.csv`
  - `outputs/metrics/iterative_decoding_cycle_relay_candidates.csv`
- Wrote the design record:
  - `docs/iterative_brain_decoding_system.md`

3. What failed
- Nothing failed in the code path after the final patch set, but the workbench
  result is still a planning/probing layer, not a solved full-brain decode.
- The first workbench output confirms the existing problem rather than solving
  it automatically: monitored DN labels are still weaker than upstream central
  / ascending / visual-projection families for target-bearing structure.

4. Evidence
- Tests:
  - `python -m pytest tests/test_iterative_decoding.py tests/test_bridge_unit.py tests/test_closed_loop_smoke.py tests/test_activation_viz.py -q` -> `34 passed`
- New workbench output:
  - `outputs/metrics/iterative_decoding_cycle_summary.json`
  - `docs/iterative_brain_decoding_system.md`
- Key first-cycle findings:
  - best monitored target-bearing label remains weak: `DNg97 = 0.2192`
  - recommended next relay families include `AVLP370a`, `AN_multi_67`,
    `LHAV3e6`, `AN_AVLP_16`, `CB1505`, and `LT57`

5. Next actions
- Generate matched activation captures for `target`, `no_target`, and
  `zero_brain` using the new default run path.
- Run those matched captures through the decoding-cycle workbench.
- Promote the resulting relay families only as monitoring-only checkpoints
  before changing any live control path.

## 2026-03-13 - First matched relay-monitor and shadow-VNC control loop

1. What I attempted
- Built a merged monitor candidate set from the current strict DN shortlist plus
  the first relay families ranked by the iterative decoding workbench.
- Added a shadow-decoder seam so the same embodied run can carry the live
  descending controller and a passive semantic-VNC decoder at the same time.
- Ran serialized real WSL `0.2 s` matched controls for:
  - `target`
  - `no_target`
  - `zero_brain`
- Ran the iterative decoding workbench on the `target` and `no_target`
  activation captures.

2. What succeeded
- Added monitor-family tooling and widened matched-control configs:
  - `scripts/build_family_monitor_candidates.py`
  - `outputs/metrics/iterative_monitor_candidates_merged.json`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_relay_monitored.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_relay_monitored_no_target.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_relay_monitored_zero_brain.yaml`
- Added the shadow-decoder seam and raw monitored-rate logging:
  - `src/bridge/controller.py`
  - `src/runtime/closed_loop.py`
- Extended capture/logging to preserve raw monitored voltage/spike state:
  - `src/visualization/session.py`
- Materialized the first matched-control artifacts:
  - `outputs/requested_0p2s_relay_monitored_target/flygym-demo-20260313-215135/*`
  - `outputs/requested_0p2s_relay_monitored_no_target/flygym-demo-20260313-215459/*`
  - `outputs/requested_0p2s_relay_monitored_zero_brain/flygym-demo-20260313-215725/*`
  - `outputs/metrics/relay_monitored_control_metrics_0p2s.csv`
  - `outputs/metrics/relay_monitored_shadow_control_summary_0p2s.csv`
  - `outputs/metrics/iterative_decoding_cycle_relay_target_summary.json`
  - `outputs/metrics/iterative_decoding_cycle_relay_no_target_summary.json`
- Wrote the result note:
  - `docs/relay_monitored_shadow_control_loop.md`

3. What failed
- The widened relay monitor and shadow-VNC loop did not make the behavior
  target-selective.
- `no_target` still beat `target` on displacement and forward speed at the
  matched `0.2 s` duration.
- The newly added relay families were much more visible in voltage space than
  in firing-rate space. In the first widened target and no-target runs, many of
  the added relay labels stayed at or near zero rate even when whole-family
  voltage correlations were strong.
- The `zero` backend does not expose brain-state tensors, so the zero-brain run
  honestly skipped the rendered activation artifact.

4. Evidence
- Tests:
  - `python -m pytest tests/test_family_monitor_candidates.py tests/test_closed_loop_smoke.py tests/test_bridge_unit.py tests/test_iterative_decoding.py -q` -> `38 passed`
- Behavioral control comparison:
  - `target`: `avg_forward_speed = 2.7087`, `net_displacement = 0.2248`
  - `no_target`: `3.3055`, `0.2972`
  - `zero_brain`: `1.7358`, `0.0162`
- Shadow VNC comparison:
  - `target`: `forward_mean = 0.01093`, `abs_turn_mean = 0.00842`
  - `no_target`: `0.01322`, `0.00881`
  - `zero_brain`: exact zero
- Ranked-family outputs:
  - `outputs/metrics/iterative_decoding_cycle_relay_target_family_scores.csv`
  - `outputs/metrics/iterative_decoding_cycle_relay_no_target_family_scores.csv`

5. Next actions
- Re-run the matched relay-control analysis using the new monitored-voltage
  logging path rather than relying on rate-only relay monitors.
- Compare target / no-target relay families in voltage space to find
  target-selective families that survive the controls.
- Keep the semantic-VNC branch in shadow mode until it separates `target` from
  `no_target` better than the live descending controller.

## 2026-03-13 - Target-engagement metric pivot for iterative decoding

1. What I attempted
- Replaced the decode-loop behavior diagnosis that had been leaning too heavily
  on speed/displacement with behavior metrics that separate:
  - target engagement / steering alignment
  - spontaneous locomotor richness
- Re-scored the existing matched relay-monitored `target`, `no_target`, and
  `zero_brain` runs without launching any new heavy embodied jobs.
- Ranked target-specific relay families against the `no_target` spontaneous
  baseline so the next monitor expansion is chosen for steering relevance
  rather than generic locomotor correlation.

2. What succeeded
- Added the new analysis layer:
  - `src/analysis/behavior_metrics.py`
  - `scripts/analyze_behavior_conditions.py`
- Integrated those metrics into the iterative decoding workbench:
  - `src/analysis/iterative_decoding.py`
- Added the target-specific relay ranking layer:
  - `src/analysis/relay_target_specificity.py`
  - `scripts/compare_relay_condition_scores.py`
- Added regression coverage:
  - `tests/test_behavior_metrics.py`
  - `tests/test_relay_target_specificity.py`
  - updated `tests/test_iterative_decoding.py`
- Materialized the new artifacts:
  - `outputs/metrics/relay_monitored_behavior_conditions_0p2s.csv`
  - `outputs/metrics/relay_monitored_behavior_conditions_0p2s.json`
  - `outputs/metrics/relay_target_specificity_0p2s_summary.json`
  - `outputs/metrics/relay_target_specificity_0p2s_families.csv`
  - `outputs/metrics/relay_target_specificity_0p2s_monitors.csv`
- Wrote the result notes:
  - `docs/target_engagement_metric_pivot.md`
  - updated `docs/relay_monitored_shadow_control_loop.md`
  - updated `docs/iterative_brain_decoding_system.md`

3. What failed
- The current relay branch still does not clear a target-engagement bar.
- The target run now looks clearly locomotor-rich, but the signed steering
  transfer is still wrong:
  - `turn_alignment_fraction_active = 0.467`
  - `turn_bearing_corr = -0.697`
  - `fixation_fraction_20deg = 0.0`
- Simple target-bearing reduction cannot be trusted by itself because the
  matched `zero_brain` control still gets passive bearing improvement.

4. Evidence
- Tests:
  - `python -m pytest tests/test_behavior_metrics.py tests/test_iterative_decoding.py tests/test_closed_loop_smoke.py -q` -> `20 passed`
  - `python -m pytest tests/test_behavior_metrics.py tests/test_iterative_decoding.py tests/test_relay_target_specificity.py -q` -> `4 passed`
- Target condition summary:
  - `locomotor_active_fraction = 0.96`
  - `controller_state_entropy = 0.583`
  - `bearing_reduction_rad = 0.250`
  - `turn_alignment_fraction_active = 0.467`
  - `turn_bearing_corr = -0.697`
- Zero-brain control:
  - `locomotor_active_fraction = 0.40`
  - `controller_state_entropy = 0.0`
  - `bearing_reduction_rad = 0.273`
- Target-specific relay shortlist after penalizing the no-target spontaneous
  baseline:
  - `MTe14`
  - `LTe62`
  - `VCH`
  - `CB0828`
  - `cL02c`
  - `CB1492`
  - `CB3516`
  - `LTe11`

5. Next actions
- Use signed target-engagement metrics rather than raw locomotion totals when
  judging the next relay-monitor iteration.
- Re-run the relay-monitor workstream with the new target-specific shortlist,
  using voltage-space relay diagnostics as the main guide.
- Keep the semantic-VNC path in shadow mode and keep spontaneous-state as a
  background condition rather than a motor floor.

## 2026-03-14 - Steering-aware turn-voltage decode iteration

1. What I attempted
- Extended the iterative decode workbench so it scores lateralized monitored
  voltages and family asymmetries against target-bearing and controller
  asymmetry, instead of relying mainly on bilateral mean activation.
- Re-ran the matched target-specific monitored target / no-target analysis with
  that steering-aware table set.
- Built the next turn-voltage monitor cohort from the new family ranking.
- Built and replayed voltage-driven shadow turn decoders from the ranked monitor
  labels to test whether the relay voltages carry a better steering signal than
  the live sampled descending turn scalar.

2. What succeeded
- Added steering-aware decode artifacts:
  - `outputs/metrics/iterative_decoding_cycle_target_specific_target_family_turn_scores.csv`
  - `outputs/metrics/iterative_decoding_cycle_target_specific_target_monitor_voltage_turn_scores.csv`
  - `outputs/metrics/iterative_decoding_cycle_target_specific_no_target_family_turn_scores.csv`
  - `outputs/metrics/iterative_decoding_cycle_target_specific_no_target_monitor_voltage_turn_scores.csv`
- Added target-vs-no-target steering-specific comparisons:
  - `outputs/metrics/target_specific_relay_turn_voltage_specificity_0p2s_families.csv`
  - `outputs/metrics/target_specific_relay_turn_voltage_specificity_0p2s_monitors.csv`
  - `outputs/metrics/target_specific_relay_turn_voltage_specificity_0p2s_summary.json`
- Built the next monitor cohort:
  - `outputs/metrics/relay_turn_voltage_monitor_candidates.json`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_turn_voltage_monitored.yaml`
  - matched `no_target` and `zero_brain` configs
- Added the shadow turn decoder seam:
  - `src/bridge/voltage_decoder.py`
  - `scripts/build_turn_voltage_signal_library.py`
  - `scripts/replay_voltage_turn_shadow_decoder.py`
- Built two shadow signal libraries:
  - broad central+visual:
    - `outputs/metrics/target_specific_turn_voltage_signal_library_0p2s.json`
  - stricter visual-only:
    - `outputs/metrics/target_specific_turn_voltage_signal_library_visual_only_0p2s.json`
- Replayed both against the recorded target run:
  - `outputs/metrics/target_specific_turn_voltage_shadow_replay_target_0p2s.json`
  - `outputs/metrics/target_specific_turn_voltage_shadow_replay_visual_only_target_0p2s.json`

3. What failed
- The live embodied controller is still unchanged and still steering-poor.
- This slice does not yet prove online embodied improvement; the new turn
  decoders were evaluated as shadow replays on existing logs.
- The broader library still mixes plausible visual relays with central-state
  families, so it is not the cleanest biological candidate even though it is
  slightly stronger numerically.

4. Evidence
- Steering-aware monitor comparison now highlights current monitored labels such
  as:
  - `IB015`
  - `CB1492`
  - `MTe14`
  - `VCH`
  - `LTe62`
  - `LT43`
  - `LTe11`
- Steering-aware family comparison now highlights turn-voltage families such as:
  - `LTe74`
  - `cL17`
  - `LC10d`
  - `LPT27`
  - `LPT51`
  - `LC36`
- Replay result on the recorded target run:
  - live sampled turn signal:
    - `live_turn_bearing_corr = -0.1663`
  - broad voltage shadow:
    - `shadow_turn_bearing_corr = -0.7276`
  - visual-only voltage shadow:
    - `shadow_turn_bearing_corr = -0.7114`
- Tests:
  - `python -m pytest tests/test_iterative_decoding.py tests/test_closed_loop_smoke.py -q` -> `22 passed`
  - `python -m pytest tests/test_voltage_turn_decoder.py tests/test_closed_loop_smoke.py -q` -> `22 passed`

5. Next actions
- Run the new `turn_voltage_monitored` matched target / no-target / zero-brain
  embodied cohort with the semantic-VNC shadow plus both voltage-turn shadows.
- Compare whether the visual-only shadow stays nearly as predictive online as
  the broader library.
- Do not mutate the live controller until the shadow decoders show stable
  online target-signed steering above the zero-brain baseline.

## 2026-03-14 - Online matched turn-voltage monitored cohort

1. What I attempted
- Ran the new `turn_voltage_monitored` target / no-target / zero-brain
  embodied cohort in real FlyGym with:
  - the unchanged live controller
  - the semantic-VNC shadow
  - the broad voltage-turn shadow
  - the visual-only voltage-turn shadow

2. What succeeded
- All three serialized `0.2 s` runs completed:
  - `outputs/requested_0p2s_turn_voltage_monitored_target/flygym-demo-20260314-093340`
  - `outputs/requested_0p2s_turn_voltage_monitored_no_target/flygym-demo-20260314-093552`
  - `outputs/requested_0p2s_turn_voltage_monitored_zero_brain/flygym-demo-20260314-093805`
- Same-run activation artifacts were generated for the target and no-target
  runs.
- The online shadow voltage-turn signals remained strongly target-signed in the
  fresh target run:
  - broad: `turn_bearing_corr = -0.9206`
  - visual-only: `turn_bearing_corr = -0.9147`
- Both voltage shadows collapsed to zero in the zero-brain control.

3. What failed
- The live controller still did not improve. Behavior remained effectively the
  same steering-poor branch:
  - `turn_alignment_fraction_active = 0.467`
  - `fixation_fraction_20deg = 0.0`
- So this slice still does not deliver embodied target tracking; it only proves
  that the monitored relay voltages contain a strong online steering signal.

4. Evidence
- Behavior conditions:
  - `outputs/metrics/turn_voltage_monitored_behavior_conditions_0p2s.json`
- Shadow summaries:
  - `outputs/metrics/turn_voltage_shadow_all_target_0p2s.json`
  - `outputs/metrics/turn_voltage_shadow_all_no_target_0p2s.json`
  - `outputs/metrics/turn_voltage_shadow_all_zero_brain_0p2s.json`
  - `outputs/metrics/turn_voltage_shadow_visual_target_0p2s.json`
  - `outputs/metrics/turn_voltage_shadow_visual_no_target_0p2s.json`
  - `outputs/metrics/turn_voltage_shadow_visual_zero_brain_0p2s.json`
- Target-run correlations:
  - live sampled turn: `-0.1663`
  - broad voltage shadow: `-0.9206`
  - visual-only voltage shadow: `-0.9147`
- Condition separation:
  - broad shadow abs-turn mean:
    - target `0.6078`
    - no-target `0.4944`
    - zero-brain `0.0`
  - visual-only shadow abs-turn mean:
    - target `0.6167`
    - no-target `0.4973`
    - zero-brain `0.0`

5. Next actions
- Design a bounded steering-only live promotion experiment using the visual-only
  voltage shadow first.
- Keep forward drive untouched.
- Re-run matched target / no-target / zero-brain controls after any promotion.

## 2026-03-14 10:35 - Recorded hard duration rule for future evaluation

1. What I attempted
- Added a repo-level rule clarifying which run durations count as benchmark
  evidence versus smoke-only diagnostics.

2. What succeeded
- The rule is now recorded in:
  - `TASKS.md`
  - `ASSUMPTIONS_AND_GAPS.md`
  - `PROGRESS_LOG.md`

3. Rule
- `>= 1.0 s` counts as benchmarking / real evaluation.
- `< 1.0 s` counts only as smoke test / sanity check.

4. Evidence
- `TASKS.md`
- `ASSUMPTIONS_AND_GAPS.md`
- `PROGRESS_LOG.md`

5. Next actions
- Apply this rule to future reporting and do not treat sub-`1.0 s` runs as
  benchmark evidence.

## 2026-03-14 13:10 - Resolved the bounded turn-voltage promotion failure with matched 2.0 s controls

1. What I attempted
- Investigated the failing promoted visual-core branch with local analysis plus
  multiple sub-agents.
- Proved the original `>500 ms` issue was not just “vision dropoff”:
  - first failure mode was live/shadow arbitration collapse
  - second failure mode was a deeper generic relay bias visible in matched
    no-target controls
- Iterated through three code fixes:
  - conflict-aware steering arbitration in `src/bridge/controller.py`
  - salience-gated conflict override in `src/bridge/controller.py`
  - bias-corrected visual-core shadow decoding plus silent-brain guards in
    `src/bridge/voltage_decoder.py`
- Revalidated each step with real serialized WSL `2.0 s` runs.

2. What succeeded
- The final bounded promotion branch now has matched `2.0 s` evidence across
  target / no-target / zero-brain.
- Final target branch:
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_conflict_gated_bias_target/flygym-demo-20260314-121624/summary.json`
  - `turn_alignment_fraction_active = 0.7973`
  - `aligned_turn_fraction = 0.704`
  - `turn_bearing_corr = 0.7626`
  - `mean_abs_bearing_rad = 0.9020`
  - `right_turn_dominant_fraction = 0.232`
  - `left_turn_dominant_fraction = 0.768`
- Final no-target branch:
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_conflict_gated_bias_no_target/flygym-demo-20260314-123350/summary.json`
  - `right_turn_dominant_fraction = 0.374`
  - `left_turn_dominant_fraction = 0.626`
  - `mean_turn_drive = -0.0385`
  - `turn_switch_rate_hz = 21.021`
  - the old generic one-sided right-turn lock is gone
- Final zero-brain integrity branch:
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_conflict_gated_bias_zero_brain_guarded_v3/flygym-demo-20260314-131053/summary.json`
  - `controller_summary_forward_nonzero_fraction = 0.0`
  - `controller_summary_turn_nonzero_fraction = 0.0`
  - `mean_turn_drive = 0.0`
  - `net_displacement = 0.0118`
- The production run path kept generating same-run activation artifacts for the
  target and no-target branches.

3. What failed
- The first conflict-aware promotion patch alone was not sufficient.
- A naive no-target baseline subtraction initially broke the zero-brain control
  because the shadow decoder interpreted missing or uniform rest-state voltage
  as real signal.
- That was fixed by adding explicit silent-brain guards to the voltage shadow
  decoder.

4. Evidence
- Final target benchmark:
  - `outputs/benchmarks/fullstack_turn_voltage_promoted_visual_core_conflict_gated_bias_target_2s.csv`
- Final no-target benchmark:
  - `outputs/benchmarks/fullstack_turn_voltage_promoted_visual_core_conflict_gated_bias_no_target_2s.csv`
- Final zero-brain benchmark:
  - `outputs/benchmarks/fullstack_turn_voltage_promoted_visual_core_conflict_gated_bias_zero_brain_guarded_v3_2s.csv`
- Updated workstream note:
  - `docs/turn_voltage_decode_iteration.md`
- Derived bias-corrected library:
  - `outputs/metrics/target_specific_turn_voltage_signal_library_visual_core_2s_bias_corrected.json`

5. Next actions
- Treat `T134` as complete.
- Keep this branch as the current best bounded steering-promotion result.
- Future work should widen biological motor semantics beyond steering-only
  promotion rather than re-opening the resolved no-target bias bug.

## 2026-03-14 18:05 - Grounded the behavior target set in real adult-fly literature

1. What I attempted
- Used sub-agents plus direct literature review to verify that the behaviors we
  are optimizing are real adult-fly behaviors rather than synthetic benchmark
  artifacts.
- Reviewed visually guided fixation / orientation / perturbation refixation,
  spontaneous locomotion and pauses, structured turning, short-timescale
  orientation memory, and walking-linked whole-brain state.
- Reviewed the current repo docs to decide where the canonical behavior target
  set and state-management consequences should live.

2. What succeeded
- Added the canonical grounded spec:
  - `docs/behavior_target_set.md`
- Threaded that spec into the main decode and state-management docs:
  - `docs/target_engagement_metric_pivot.md`
  - `docs/iterative_brain_decoding_system.md`
  - `docs/spontaneous_state_program.md`
  - `docs/spontaneous_state_validation_plan.md`
  - `ASSUMPTIONS_AND_GAPS.md`
- The repo now distinguishes:
  - real target behaviors we should optimize for:
    - spontaneous roaming
    - intermittent locomotion with pauses
    - structured turning / reorientation
    - landmark fixation / orientation
    - perturbation refixation
    - short-timescale orientation memory
  - real but out-of-scope or context-specific behaviors we should not treat as
    default acceptance targets yet:
    - odor-loss search
    - reward local search
    - hunger-state foraging
    - looming freeze / flee
    - courtship-specific pursuit
- The repo now explicitly rejects generic indefinite smooth pursuit of an
  arbitrary moving target as the default real-fly behavior claim.

3. What failed
- The repo still does not have a perturbation-specific `target_jump` or
  `target_removed_brief` evaluation path, so refixation and short-timescale
  persistence are grounded by literature but not yet directly scored in the
  live branch.
- Repo-level verdict docs still need to be re-scored against the new canonical
  behavior target set.

4. Evidence
- `docs/behavior_target_set.md`
- `docs/target_engagement_metric_pivot.md`
- `docs/iterative_brain_decoding_system.md`
- `docs/spontaneous_state_program.md`
- `docs/spontaneous_state_validation_plan.md`
- `ASSUMPTIONS_AND_GAPS.md`
- `TASKS.md`

5. Next actions
- Re-score the current best embodied branch against the new canonical behavior
  target set.
- Add perturbation-aware target assays so refixation and brief-loss persistence
  are measured directly instead of inferred from continuous-target runs.

## 2026-03-14 21:10 - Implemented and benchmarked the first grounded target perturbation assays

1. What I attempted
- Used sub-agents to confirm the clean implementation seam for a grounded
  visual perturbation assay:
  - perturb the target in the body runtime
  - log perturbation state through `target_state`
  - score refixation and brief-loss persistence in `behavior_metrics.py`
- Implemented runtime-side target scheduling with `jump` and `hide` events.
- Added perturbation-aware behavior metrics.
- Added runnable current-branch configs for:
  - `target_jump`
  - `target_removed_brief`
- Ran real serialized `2.0 s` embodied FlyGym assays with same-run activation
  visualization for both perturbation types.

2. What succeeded
- New runtime and metric seams are in place:
  - `src/body/target_schedule.py`
  - `src/body/flygym_runtime.py`
  - `src/runtime/closed_loop.py`
  - `src/analysis/behavior_metrics.py`
- Focused validation passed:
  - `python -m pytest tests/test_target_schedule.py tests/test_behavior_metrics.py tests/test_closed_loop_smoke.py -q`
  - `26 passed`
- First real jump assay completed with activation capture:
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_target_jump/flygym-demo-20260314-203328`
- First real brief-removal assay completed with activation capture:
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_target_removed_brief/flygym-demo-20260314-204945`
- The new assay doc is written:
  - `docs/target_perturbation_assay.md`

3. What failed
- The current best branch does not yet solve perturbation behavior.
- Jump assay:
  - immediate corrective turning is strong
  - but frontal refixation fails within the `2.0 s` window
- Brief-removal assay:
  - hidden-target persistence is weak
  - the branch behaves more like a visually contingent re-stabilizer than a
    persistent internal target tracker
- Matched `no_target` / `zero_brain` perturbation controls still do not exist
  yet for these new assays.

4. Evidence
- Assay implementation:
  - `src/body/target_schedule.py`
  - `src/body/flygym_runtime.py`
  - `src/analysis/behavior_metrics.py`
  - `src/runtime/closed_loop.py`
- Configs:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_turn_voltage_promoted_visual_core_target_jump.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_turn_voltage_promoted_visual_core_target_removed_brief.yaml`
- Real jump assay:
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_target_jump/flygym-demo-20260314-203328/summary.json`
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_target_jump/flygym-demo-20260314-203328/activation_side_by_side.mp4`
- Real brief-removal assay:
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_target_removed_brief/flygym-demo-20260314-204945/summary.json`
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_target_removed_brief/flygym-demo-20260314-204945/activation_side_by_side.mp4`
- Summary note:
  - `docs/target_perturbation_assay.md`

5. Next actions
- Run matched `no_target` and `zero_brain` perturbation controls.
- Diagnose the failed jump refixation and weak hidden persistence directly from
  the new activation captures rather than from continuous-target proxies.

## 2026-03-14 23:59 - Corrected the turn-voltage sign convention and advanced the perturbation branch

1. What I attempted
- Used sub-agents plus local activation/log analysis to diagnose why the
  perturbation branch still failed after the first refixation-gate experiment.
- Proved that the refixation gate itself was a bad intervention:
  - it stayed active almost the whole run
  - it increased one-sided left bias
  - it did not improve jump-specific frontal refixation
- Followed the failure upstream into the shadow-steering library and found a
  deeper sign-convention bug:
  - `src/analysis/turn_voltage_library.py` was still assigning turn weights
    with the old opposite-sign convention
- Added a reusable baseline-correction utility for shadow libraries:
  - `scripts/bias_correct_turn_voltage_signal_library.py`
- Rebuilt a bias-corrected jump-aware shadow library, promoted it into the
  active configs, disabled the failed refixation override, and increased the
  base shadow blend.
- Ran new real serialized `2.0 s` WSL embodied runs with same-run activation
  visualization for:
  - corrected `target_jump`
  - corrected `target_removed_brief`
  - corrected `no_target`
  - corrected `zero_brain`

2. What succeeded
- The turn-voltage builder now uses the current same-sign steering convention:
  - `src/analysis/turn_voltage_library.py`
- New reusable baseline-correction path exists and is covered:
  - `scripts/bias_correct_turn_voltage_signal_library.py`
  - `tests/test_turn_voltage_library.py`
- Focused validation passed:
  - `python -m pytest tests/test_turn_voltage_library.py tests/test_bridge_unit.py tests/test_closed_loop_smoke.py -q`
  - `48 passed`
- The corrected jump-aware library is now the promoted shadow library:
  - `outputs/metrics/jump_turn_voltage_signal_library_top8_mixed_bias_corrected.json`
- Corrected jump target run completed:
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_target_jump_signfix_blend08/flygym-demo-20260314-230110`
- Corrected brief-removal target run completed:
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_target_removed_brief_signfix_blend08/flygym-demo-20260314-231851`
- Corrected `no_target` control completed:
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_no_target_signfix_blend08/flygym-demo-20260314-233644`
- Corrected `zero_brain` control completed:
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_zero_brain_signfix_blend08/flygym-demo-20260314-235119`
- The corrected branch is now the strongest target-condition perturbation
  branch so far on steering metrics:
  - jump target:
    - `target_condition_turn_bearing_corr = 0.8745`
    - `jump_turn_bearing_corr = 0.9589`
    - `jump_bearing_recovery_fraction_2s = -1.3164`
  - brief removal:
    - `target_condition_turn_bearing_corr = 0.9176`
    - `removal_persistence_turn_alignment_fraction = 0.9762`
    - `removal_mean_abs_bearing_rad = 0.1546`
- The corrected `no_target` control stayed mixed and nearly zero-mean in turn:
  - `mean_turn_drive = 0.0010`
  - `right_turn_dominant_fraction = 0.549`
  - `left_turn_dominant_fraction = 0.448`
- The corrected `zero_brain` control remained silent:
  - `controller_summary_forward_nonzero_fraction = 0.0`
  - `controller_summary_turn_nonzero_fraction = 0.0`

3. What failed
- Jump-specific frontal refixation is still not solved on the corrected branch:
  - `jump_refixation_latency_s = null`
  - `jump_refixation_fraction_20deg = 0.0`
- The corrected jump run improved steering correlation and recovery, but did not
  beat the original baseline on `jump_turn_alignment_fraction_active`.
- Matched perturbation-specific `no_target` / `zero_brain` controls still do
  not exist yet; the new controls were run on the corrected main branch, not on
  the perturbation schedules themselves.
- The fly is still not an indistinguishable living-fly embodiment. This is a
  materially improved partial branch, not a final parity claim.

4. Evidence
- Code and utility changes:
  - `src/analysis/turn_voltage_library.py`
  - `scripts/bias_correct_turn_voltage_signal_library.py`
  - `tests/test_turn_voltage_library.py`
- Corrected shadow library:
  - `outputs/metrics/jump_turn_voltage_signal_library_top8_mixed_bias_corrected.json`
- Corrected jump target run:
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_target_jump_signfix_blend08/flygym-demo-20260314-230110/summary.json`
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_target_jump_signfix_blend08/flygym-demo-20260314-230110/activation_side_by_side.mp4`
  - `outputs/benchmarks/fullstack_turn_voltage_promoted_visual_core_target_jump_signfix_blend08_2s.csv`
- Corrected brief-removal target run:
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_target_removed_brief_signfix_blend08/flygym-demo-20260314-231851/summary.json`
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_target_removed_brief_signfix_blend08/flygym-demo-20260314-231851/activation_side_by_side.mp4`
  - `outputs/benchmarks/fullstack_turn_voltage_promoted_visual_core_target_removed_brief_signfix_blend08_2s.csv`
- Corrected controls:
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_no_target_signfix_blend08/flygym-demo-20260314-233644/summary.json`
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_zero_brain_signfix_blend08/flygym-demo-20260314-235119/summary.json`
- Updated assay state:
  - `docs/target_perturbation_assay.md`

5. Next actions
- Run matched perturbation-specific controls on the corrected branch:
  - `target_jump + no_target-equivalent baseline`
  - `target_jump + zero_brain`
  - `target_removed_brief + zero_brain`
- Diagnose why jump steering is now strong but jump-specific frontal refixation
  still does not complete within `2.0 s`.
- Re-score the corrected branch against the canonical behavior target set in
  the repo-level verdict docs before promoting it as the new default claim
  branch.

## 2026-03-15 02:10 - Enforced the no-hacks hard rule and reset the perturbation path to brain-driven monitoring

1. What I attempted
- Recorded the user's new hard rule:
  - no hacks
  - everything in the active embodiment path must be brain-driven and biologically plausible
- Audited the just-added turn-forward suppression intervention against that
  rule.
- Checked the interrupted rerun state and confirmed it did not produce a valid
  embodied result.
- Replaced the next controller-side iteration with a monitoring-only,
  relay-first jump config on the canonical calibrated decoder.

2. What succeeded
- The controller-side turn-forward suppression experiment was removed from the
  worktree:
  - `src/bridge/decoder.py`
  - `tests/test_bridge_unit.py`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_turn_voltage_promoted_visual_core*.yaml`
- Focused validation passed again after the rollback:
  - `python -m pytest tests/test_bridge_unit.py tests/test_closed_loop_smoke.py -q`
  - `45 passed`
- Added an explicit jump-specific monitoring branch that keeps the canonical
  calibrated decoder and adds only relay-heavy monitoring:
  - `outputs/metrics/jump_brain_driven_relay_monitor_families.csv`
  - `outputs/metrics/jump_brain_driven_relay_monitor_candidates.json`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_jump_brain_relay_monitored.yaml`
- Added config-level smoke coverage to keep that branch honest:
  - `tests/test_closed_loop_smoke.py`

3. What failed
- The interrupted rerun attempt did not produce a valid embodied result:
  - the benchmark runner defaulted to `mock` without `--mode flygym`
  - the aborted output root only contains a zero-length mock stub
  - that artifact does not count as evidence
- The jump refixation problem itself is not solved yet.

4. Evidence
- Hard-rule record:
  - `TASKS.md`
  - `ASSUMPTIONS_AND_GAPS.md`
  - `docs/target_perturbation_assay.md`
- Rolled-back heuristic change:
  - `src/bridge/decoder.py`
  - `tests/test_bridge_unit.py`
- New brain-driven monitoring branch:
  - `outputs/metrics/jump_brain_driven_relay_monitor_families.csv`
  - `outputs/metrics/jump_brain_driven_relay_monitor_candidates.json`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_jump_brain_relay_monitored.yaml`
- Invalid aborted stub:
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_target_jump_turnsuppress/mock-demo-20260315-015719/run.jsonl`

5. Next actions
- Run the new jump-specific brain-relay monitored branch in `flygym` mode with
  same-run activation capture.
- Use that capture to expand relay-state decoding upstream of the current
  descending readout, instead of adding new controller-side logic.

## 2026-03-15 02:45 - Ran the first honest jump-monitor capture and extracted a second-wave relay cohort

1. What I attempted
- Ran a real `2.0 s` `flygym` target-jump assay on the canonical calibrated
  decoder with no steering promotion and relay-heavy monitoring only:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_jump_brain_relay_monitored.yaml`
- Used the resulting activation capture and run log to execute a fresh decode
  cycle on the no-hacks branch.
- Built a second-wave relay monitor cohort directly from that honest capture.

2. What succeeded
- The embodied run completed with same-run activation visualization:
  - `outputs/requested_2s_calibrated_target_jump_brain_relay_monitored/flygym-demo-20260315-020918`
- Key metrics from the honest branch:
  - `target_condition_turn_bearing_corr = 0.8813`
  - `target_perturbation_jump_turn_alignment_fraction_active = 1.0`
  - `target_perturbation_jump_bearing_recovery_fraction_2s = -0.8210`
  - `target_perturbation_jump_refixation_latency_s = null`
- This branch still does not solve frontal refixation, but it improves jump
  recovery over the promoted sign-fix branch while staying inside the hard
  rule.
- The decode workbench produced a new relay ranking from the honest capture:
  - `outputs/metrics/jump_brain_driven_relay_cycle_summary.json`
- Built the second-wave candidate set:
  - `outputs/metrics/jump_brain_driven_relay_monitor_candidates_wave2.json`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_jump_brain_relay_monitored_wave2.yaml`
- Wrote the branch note:
  - `docs/brain_driven_jump_relay_monitoring.md`

3. What failed
- Frontal refixation is still not solved on the honest branch.
- The target still reaches the rear field in roughly `0.386 s` after the jump.
- No matched no-hacks `no_target` / `zero_brain` controls were run in this
  slice yet.

4. Evidence
- Honest jump run:
  - `outputs/requested_2s_calibrated_target_jump_brain_relay_monitored/flygym-demo-20260315-020918/summary.json`
  - `outputs/requested_2s_calibrated_target_jump_brain_relay_monitored/flygym-demo-20260315-020918/activation_side_by_side.mp4`
- Honest decode-cycle outputs:
  - `outputs/metrics/jump_brain_driven_relay_cycle_summary.json`
  - `outputs/metrics/jump_brain_driven_relay_cycle_monitor_turn_candidates.csv`
  - `outputs/metrics/jump_brain_driven_relay_cycle_relay_turn_candidates.csv`
- Wave-2 monitoring artifacts:
  - `outputs/metrics/jump_brain_driven_relay_monitor_candidates_wave2.json`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_jump_brain_relay_monitored_wave2.yaml`
- Writeup:
  - `docs/brain_driven_jump_relay_monitoring.md`

5. Next actions
- Run matched no-hacks controls on this relay-monitored path.
- Run the wave-2 jump-monitor capture.
- Use the matched relay state to design a brain-side latent upstream of the
  current motor decoder instead of adding new controller logic.

## 2026-03-15 06:55 - Integrated the first decoder-internal brain-latent turn branch and validated it on a live target / no-target / zero-brain trio

1. What I attempted
- Added a decoder-internal brain-state latent seam to the primary motor
  decoder:
  - `src/bridge/decoder.py`
  - `src/bridge/controller.py`
- Built a matched-condition turn-latent library from the honest `target` and
  `no_target` captures:
  - `scripts/build_brain_turn_latent_library.py`
  - `src/analysis/brain_latent_library.py`
- Replayed that latent offline, tightened the library to a stricter upstream
  subset, swept candidate weights, then promoted the bounded latent into the
  live canonical jump branch.
- Ran a full serialized live trio on the new branch:
  - `target`
  - `no_target`
  - `zero_brain`

2. What succeeded
- The decoder can now consume monitored brain voltage directly through the
  live decoder path instead of only through shadow decoders.
- Focused validation passed after the integration:
  - `python -m pytest tests/test_turn_voltage_library.py tests/test_bridge_unit.py tests/test_closed_loop_smoke.py -q`
  - `56 passed`
- Built the matched latent artifacts:
  - `outputs/metrics/jump_brain_driven_turn_latent_2s.json`
  - `outputs/metrics/jump_brain_driven_turn_latent_2s_ranked.csv`
  - `outputs/metrics/jump_brain_driven_turn_latent_2s_library.json`
  - `outputs/metrics/jump_brain_driven_turn_latent_2s_library_strict.json`
  - `outputs/metrics/jump_brain_driven_turn_latent_weight_sweep.csv`
- The bounded strict live branch completed with same-run activation
  visualization on both `target` and `no_target`:
  - `outputs/requested_2s_calibrated_target_jump_brain_latent_turn/flygym-demo-20260315-061819`
  - `outputs/requested_2s_calibrated_no_target_brain_latent_turn/flygym-demo-20260315-063511`
- The matched live trio comparison is now explicit:
  - `outputs/metrics/brain_latent_turn_live_comparison.json`
- Relative to the honest relay-monitored baseline:
  - `jump_bearing_recovery_fraction_2s` improved from `-0.8210` to `-0.5658`
  - `jump_turn_bearing_corr` improved from `0.3215` to `0.8177`
  - `fixation_fraction_20deg` improved from `0.043` to `0.059`
  - overall `target_condition_turn_bearing_corr` stayed essentially unchanged
    (`0.8813 -> 0.8806`)
- `no_target` remained behaviorally sane on the new branch:
  - `mean_turn_drive = 0.0054`
  - `mean_abs_turn_drive = 0.1634`
  - `right/left dominance = 0.552 / 0.448`
- `zero_brain` remained silent on the new decoder path:
  - `controller_summary_turn_nonzero_fraction = 0.0`
  - `mean_abs_turn_drive = 0.0`

3. What failed
- The branch still does not complete frontal jump refixation within `2.0 s`.
- This remains only a signed-steering-error latent, not yet a full
  heading / goal / steering-gain scaffold.
- The active branch is improved, but it is not yet an indistinguishable living
  fly.

4. Evidence
- Decoder / analysis code:
  - `src/bridge/decoder.py`
  - `src/bridge/controller.py`
  - `src/analysis/brain_latent_library.py`
  - `scripts/build_brain_turn_latent_library.py`
- Live configs:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_jump_brain_latent_turn.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_latent_turn.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_zero_brain_target_jump_brain_latent_turn.yaml`
- Target run:
  - `outputs/requested_2s_calibrated_target_jump_brain_latent_turn/flygym-demo-20260315-061819/summary.json`
  - `outputs/requested_2s_calibrated_target_jump_brain_latent_turn/flygym-demo-20260315-061819/activation_side_by_side.mp4`
- No-target run:
  - `outputs/requested_2s_calibrated_no_target_brain_latent_turn/flygym-demo-20260315-063511/summary.json`
  - `outputs/requested_2s_calibrated_no_target_brain_latent_turn/flygym-demo-20260315-063511/activation_side_by_side.mp4`
- Zero-brain run:
  - `outputs/requested_2s_calibrated_zero_brain_target_jump_brain_latent_turn/flygym-demo-20260315-065048/summary.json`
- Branch note:
  - `docs/brain_latent_turn_decoder.md`

5. Next actions
- Extend the decoder-internal brain latent beyond signed steering error toward a
  literature-grounded heading / goal / steering-gain scaffold.
- Re-test that richer latent on `jump` and `target_removed_brief` assays.
- Keep the hard rule in force:
  - no controller-side steering arbitration
  - no body-side shortcut logic

## 2026-03-15 09:40 - Rewrote the whitepaper as a publication-style manuscript around the current best honest branch

1. What I attempted
- Replaced the old project-summary whitepaper with a full manuscript-style
  document that reads like a real computational systems paper rather than a
  changelog.
- Re-centered the narrative on the actual branch progression:
  - strict public-anchor failure
  - body-free splice localization
  - descending-readout embodiment
  - semantic-VNC negative result
  - spontaneous-state pilot
  - decoder-internal brain-latent turn branch as the current best honest result
- Used sub-agent review to tighten the claim boundary, section structure, and
  publishable tone before rewriting the file.

2. What succeeded
- [openfly_whitepaper.md](/G:/flysim/docs/openfly_whitepaper.md) is now a
  complete journal-style manuscript with:
  - abstract
  - introduction
  - system overview
  - experimental program
  - results
  - discussion
  - limitations
  - methods
  - reproducibility section
  - references
- The manuscript now presents the repo as a reconstruction-and-falsification
  study instead of a simple parity narrative.
- The current best honest branch is now explicit:
  - `requested_2s_calibrated_target_jump_brain_latent_turn`
- The main quantitative claim boundary is explicit:
  - jump-linked steering improved materially
  - `zero_brain` remained silent
  - frontal jump refixation still failed within `2.0 s`

3. What failed
- No new experiments were run in this slice.
- The whitepaper rewrite does not by itself resolve the remaining scientific
  gaps around refixation, heading/goal state, or full biological motor output.

4. Evidence
- Manuscript:
  - `docs/openfly_whitepaper.md`
- Current best branch:
  - `outputs/requested_2s_calibrated_target_jump_brain_latent_turn/flygym-demo-20260315-061819/summary.json`
  - `outputs/requested_2s_calibrated_target_jump_brain_latent_turn/flygym-demo-20260315-061819/activation_side_by_side.mp4`
- Matched comparison:
  - `outputs/metrics/brain_latent_turn_live_comparison.json`
- Supporting branch notes:
  - `docs/brain_latent_turn_decoder.md`
  - `docs/spontaneous_state_results.md`
  - `docs/semantic_vnc_failed_parity_branch.md`

5. Next actions
- Keep the manuscript synchronized with the active branch as the heading / goal
  latent work proceeds.
- When branch verdict docs are updated later, reconcile the whitepaper,
  parity report, and README front-page language so they all reference the same
  leading branch and claim boundary.

## 2026-03-15 09:55 - Promoted the rewritten whitepaper to the repo front page and prepared a docs-only push

1. What I attempted
- Made `README.md` match the rewritten manuscript exactly so the GitHub landing
  page shows the paper rather than the older front-page summary.
- Kept the commit scoped to documentation/tracker files only because the
  worktree still contains unrelated in-flight code and artifact changes.

2. What succeeded
- `README.md` now mirrors:
  - `docs/openfly_whitepaper.md`
- Added the corresponding tracker row so the front-page sync is explicit in
  repo state.

3. What failed
- No code or experiment changes were included in this slice.
- The broader uncommitted worktree remains intentionally untouched.

4. Evidence
- `README.md`
- `docs/openfly_whitepaper.md`
- `TASKS.md`

5. Next actions
- Commit only the manuscript/front-page/tracker files.
- Push that docs-only commit without sweeping in the unrelated local changes.

## 2026-03-15 15:35 - Created `exp/spontaneous-brain-latent-turn` and ran the first honest embodied spontaneous-state fold-in on the brain-latent branch

1. What I attempted
- Created a new git experiment branch:
  - `exp/spontaneous-brain-latent-turn`
- Used sub-agents to audit:
  - the safest spontaneous-state parameter block to port
  - the minimal integration seam for the current best brain-latent branch
  - the clean run/tracker package for the new experiment
- Added a new config that keeps the current best target-jump brain-latent
  decoder/body path intact and only enables the current best backend
  spontaneous-state candidate:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_jump_brain_latent_turn_spontaneous.yaml`
- Added smoke coverage to prove the new config stays on the primary
  no-shortcuts path:
  - `tests/test_closed_loop_smoke.py`
- Ran the focused config smoke suite and the backend spontaneous-state unit
  suite.
- Ran one serialized real `2.0 s` FlyGym target-jump demo with same-run
  activation visualization.

2. What succeeded
- The experimental branch was created cleanly without disturbing the existing
  in-flight worktree:
  - `git switch -c exp/spontaneous-brain-latent-turn`
- The new config passed closed-loop smoke coverage:
  - `python -m pytest tests/test_closed_loop_smoke.py -q`
  - `28 passed`
- The backend spontaneous-state seam is still covered directly:
  - `python -m pytest tests/test_spontaneous_state_unit.py -q`
  - `6 passed`
- The real run completed and emitted the full activation bundle:
  - `outputs/requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous/flygym-demo-20260315-150545`
  - `activation_side_by_side.mp4`
  - `activation_capture.npz`
  - `activation_overview.png`
  - `summary.json`
  - `run.jsonl`
  - `metrics.csv`
- The backend was genuinely awake in the live run, not merely configured:
  - `background_mean_rate_hz_mean ~= 0.0314`
  - `background_latent_mean_abs_hz_mean ~= 0.9613`
  - baseline non-spontaneous branch had `background_mean_rate_hz_mean = 0.0`

3. What failed
- The spontaneous-state fold-in regressed behavior relative to the current best
  non-spontaneous brain-latent branch.
- Target metrics worsened:
  - `avg_forward_speed: 5.4296 -> 3.7541`
  - `net_displacement: 6.2632 -> 4.3757`
  - `target_condition_mean_abs_bearing_rad: 1.3842 -> 1.6519`
  - `target_condition_fixation_fraction_20deg: 0.059 -> 0.045`
  - `target_condition_turn_bearing_corr: 0.8806 -> 0.6964`
- Jump behavior degraded badly:
  - `jump_turn_bearing_corr: 0.8177 -> -0.7485`
  - `jump_bearing_recovery_fraction_2s: -0.5658 -> -1.5755`
  - `jump_turn_alignment_fraction_active: 0.6667 -> 0.152`
- Spontaneous locomotion looked more active in state-space terms, but the
  control signature shifted toward a new right-dominant bias:
  - `right_turn_dominant_fraction: 0.388 -> 0.642`
  - `left_turn_dominant_fraction: 0.612 -> 0.358`
- This is therefore not a promotable branch. It is a real negative result:
  backend wakefulness alone does not improve this target-jump latent branch and
  can actively destabilize the signed steering solution.

4. Evidence
- Branch and config:
  - `exp/spontaneous-brain-latent-turn`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_jump_brain_latent_turn_spontaneous.yaml`
- Tests:
  - `tests/test_closed_loop_smoke.py`
  - `tests/test_spontaneous_state_unit.py`
- Real run:
  - `outputs/requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous/flygym-demo-20260315-150545/summary.json`
  - `outputs/requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous/flygym-demo-20260315-150545/activation_side_by_side.mp4`
  - `outputs/benchmarks/fullstack_calibrated_target_jump_brain_latent_turn_spontaneous_2s.csv`
- Baseline comparison reference:
  - `outputs/requested_2s_calibrated_target_jump_brain_latent_turn/flygym-demo-20260315-061819/summary.json`

5. Next actions
- Do not promote spontaneous state directly into the current best latent branch.
- Treat this result as evidence for `T147`: the next required move is a richer
  heading / goal / steering-gain scaffold, not a naive wakefulness fold-in.
- Complete `T122` properly with matched spontaneous `no_target` and
  `zero_brain` controls before making any broader spontaneous-state embodiment
  claims.

## 2026-03-15 20:35 - Recorded the living-brain evaluation rule in the repo state docs

1. What I attempted
- Wrote down the evaluation clarification that became necessary after the first
  spontaneous activation visualization made it obvious that the awakened branch
  is operating in a different brain-state regime than the old cold-start line.

2. What succeeded
- The repo now records that the old quiescent branches are only regime-change
  baselines once endogenous spontaneous state is on.
- The active evaluation rule is now explicit in:
  - `TASKS.md`
  - `ASSUMPTIONS_AND_GAPS.md`
  - `docs/brain_latent_turn_decoder.md`

3. What failed
- No experiments were completed in this logging slice.

4. Evidence
- `TASKS.md`
- `ASSUMPTIONS_AND_GAPS.md`
- `docs/brain_latent_turn_decoder.md`

5. Next actions
- Keep living-brain evaluation centered on matched living `target`,
  `no_target`, perturbation, and `zero_brain` controls.
- Treat raw speed / displacement differences versus the old dead-brain regime
  only as secondary diagnostics.

## 2026-03-15 21:09 - Re-derived the brain-latent decoder inside the awakened regime and validated it on a living target/no-target pair

1. What I attempted
- Built the missing spontaneous-on `no_target` companion for the
  brain-latent branch.
- Extended the latent-library builder so it can penalize sign-unstable
  candidates across low/high spontaneous-state bins using
  `background_latent_mean_abs_hz`.
- Rebuilt the latent from matched awakened `target` / `no_target` captures
  instead of reusing the old cold-state library.
- Ran fresh `2.0 s` living `target` and living `no_target` demos on the refit
  library with same-run activation visualization.

2. What succeeded
- Focused validation passed after wiring the refit path:
  - `python -m pytest tests/test_turn_voltage_library.py tests/test_closed_loop_smoke.py -q`
  - `37 passed`
- The spontaneous-on matched builder completed:
  - `outputs/metrics/jump_brain_driven_turn_latent_2s_spontaneous_refit.json`
  - `outputs/metrics/jump_brain_driven_turn_latent_2s_spontaneous_refit_ranked.csv`
  - `outputs/metrics/jump_brain_driven_turn_latent_2s_spontaneous_refit_library.json`
  - `outputs/metrics/jump_brain_driven_turn_latent_2s_spontaneous_refit_target_state_bins.csv`
  - `outputs/metrics/jump_brain_driven_turn_latent_2s_spontaneous_refit_no_target_state_bins.csv`
- The rebuilt awakened latent selected a new group set:
  - `MeLp1`
  - `PVLP112b`
  - `cM15`
  - `CB0965`
  - `CL294`
  - `CB1916`
  - `cML02`
  - `AVLP091`
- The fresh living target run completed with same-run activation capture:
  - `outputs/requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-203010`
- The fresh living no-target run completed with same-run activation capture:
  - `outputs/requested_2s_calibrated_no_target_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-204719`
- Relative to the first spontaneous target run, the awakened refit repaired the
  major pathology:
  - `jump_turn_alignment_fraction_active: 0.1520 -> 0.7302`
  - `jump_turn_bearing_corr: -0.7485 -> 0.5644`
  - `jump_bearing_recovery_fraction_2s: -1.5755 -> -1.0482`
- The matched awakened no-target control remained near zero-mean in turn:
  - `mean_turn_drive = 0.0077`
  - `right/left dominance = 0.413 / 0.587`

3. What failed
- The branch still does not complete frontal jump refixation within `2.0 s`.
- Gross locomotion remains strong in both living `target` and living
  `no_target`, so raw movement totals are still not a clean target-conditioned
  separator in this regime.
- A fresh spontaneous zero-brain rerun was not collected in this slice.

4. Evidence
- Builder and analysis:
  - `src/analysis/brain_latent_library.py`
  - `scripts/build_brain_turn_latent_library.py`
  - `outputs/metrics/jump_brain_driven_turn_latent_2s_spontaneous_refit.json`
  - `outputs/metrics/jump_brain_driven_turn_latent_2s_spontaneous_refit_library.json`
- Live configs:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_latent_turn_spontaneous.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_jump_brain_latent_turn_spontaneous_refit.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_latent_turn_spontaneous_refit.yaml`
- Live artifacts:
  - `outputs/requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-203010/summary.json`
  - `outputs/requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-203010/activation_side_by_side.mp4`
  - `outputs/requested_2s_calibrated_no_target_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-204719/summary.json`
  - `outputs/requested_2s_calibrated_no_target_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-204719/activation_side_by_side.mp4`
  - `outputs/metrics/spontaneous_brain_latent_refit_comparison.json`

5. Next actions
- Keep treating this as a living-branch partial rather than as a solved branch.
- Use the repaired spontaneous-on latent as the new base if the next step is a
  richer heading / goal-memory / steering-gain scaffold.
- Collect a fresh spontaneous zero-brain rerun before making stronger control
  claims about the embodied spontaneous branch.

## 2026-03-15 22:28 - Living target/no-target activation analysis recorded

1. What I attempted
- Analyzed the matched living spontaneous-refit `target` and `no_target`
  activation captures as a pair, with sub-agents reviewing renderer semantics
  and future decoder implications in parallel.
- Converted the one-off inspection into a reproducible analysis path and
  persisted the findings into repo artifacts and docs.

2. What succeeded
- Added reusable analysis code:
  - `src/analysis/living_brain_activation_analysis.py`
  - `scripts/analyze_living_brain_activation_pair.py`
  - `tests/test_living_brain_activation_analysis.py`
- Validation passed:
  - `python -m pytest tests/test_living_brain_activation_analysis.py -q`
  - `2 passed`
  - `python -m py_compile src/analysis/living_brain_activation_analysis.py scripts/analyze_living_brain_activation_pair.py`
- Generated the recorded analysis bundle:
  - `outputs/metrics/living_brain_activation_pair_summary.json`
  - `outputs/metrics/living_brain_activation_pair_condition_summary.csv`
  - `outputs/metrics/living_brain_activation_pair_family_comparison.csv`
  - `outputs/metrics/living_brain_activation_pair_monitor_rate_comparison.csv`
  - `outputs/metrics/living_brain_activation_pair_central_units_target.csv`
  - `outputs/metrics/living_brain_activation_pair_central_units_no_target.csv`
  - `outputs/plots/living_brain_activation_pair_renderer_breakdown.png`
- Wrote the findings note:
  - `docs/living_brain_activation_analysis.md`
- Updated the living-branch decoder note:
  - `docs/brain_latent_turn_decoder.md`

3. What I learned
- The living `target` and living `no_target` runs are already in the same
  awakened backend regime; the spontaneous-state backbone statistics are
  effectively identical across the pair.
- The large brain cloud in the activation video is real state, but not a
  whole-brain spike storm. Real spike density remains sparse, around
  `221-230` spiking neurons per frame across `138,639` neurons, while the
  renderer fills the rest of the `6000` displayed points with non-spiking
  high-`|voltage|` units.
- The visually dominant unsampled families are mostly shared living-brain
  baseline occupancy:
  - `MeMe_e13`
  - `DNa03`
  - `Nod3`
  - `H2`
  - `T2`
  - `Am1`
  - `LHMB1`
  - `H1`
  - `Mi10`
  - `T4a`
- The genuinely spike-heavy unsampled families are different and much smaller:
  - target: `CT1`, `DM4_adPN`, `LHPV12a1`, `lLN2X03`, `LPi12`
  - no-target: `lLN2F_b`, `VM6_adPN`, `il3LN6`, `CT1`, `lLN1_a`
- The decoder-relevant target-conditioned signal is still subtler and more
  distributed than the bright cloud. Existing living-branch decode outputs
  continue to point toward upstream voltage-asymmetry families such as
  `LCe01`, `CL314`, `LLPC4`, `PLP230`, `AVLP417,AVLP438`, and `CB3014`.

4. What failed
- This was analysis only; no new embodied run or decoder promotion was attempted.
- The activation video alone is not enough to identify target structure by eye;
  the visible cloud is too dominated by shared awakened baseline occupancy.

5. Evidence
- Pair analysis:
  - `outputs/metrics/living_brain_activation_pair_summary.json`
  - `outputs/metrics/living_brain_activation_pair_condition_summary.csv`
  - `outputs/metrics/living_brain_activation_pair_family_comparison.csv`
  - `outputs/metrics/living_brain_activation_pair_monitor_rate_comparison.csv`
- Existing living-regime decode evidence:
  - `outputs/metrics/living_spontaneous_refit_target_cycle_summary.json`
  - `outputs/metrics/living_spontaneous_refit_target_vs_no_target_summary.json`
  - `outputs/metrics/living_spontaneous_refit_target_vs_no_target_families.csv`
  - `outputs/metrics/living_spontaneous_refit_target_vs_no_target_monitors.csv`
- Docs:
  - `docs/living_brain_activation_analysis.md`
  - `docs/brain_latent_turn_decoder.md`

6. Next actions
- Keep the living branch on the matched-regime evaluation path.
- Continue decoding from voltage-side asymmetry rather than from gross rates or
  the visually dominant cloud.
- Widen monitoring upstream into the target-specific unsampled relay families
  identified by the living-regime pair analysis before adding more motor-side
  complexity.

## 2026-03-15 23:06 - Full spontaneous-state physiological-validation audit

1. What I attempted
- Treated the user goal literally and audited whether the repo can honestly
  claim fully physiologically validated spontaneous adult fly-brain dynamics.
- Used primary-source literature plus repo inspection and sub-agent assistance
  to define the exact requirement boundary rather than silently weakening the
  claim.

2. What succeeded
- Wrote the explicit requirement and blocker note:
  - `docs/spontaneous_state_full_validation_requirements.md`
- Updated the spontaneous-state status docs:
  - `docs/spontaneous_state_results.md`
  - `ASSUMPTIONS_AND_GAPS.md`
- Updated task tracking:
  - `T153` done: feasibility/requirement audit
  - `T154` blocked: full physiological spontaneous-state validation

3. What I learned
- The field now has enough public evidence to support mesoscale spontaneous-state
  validation, not full physiological validation.
- Strong public resources now exist for:
  - whole-brain connectome and cell typing
  - spontaneous / behavior-linked whole-brain imaging
  - mesoscale structure-function comparisons
- The missing pieces for a full claim are still decisive:
  - stable alignment from spontaneous recordings to the full simulated
    connectome identity space
  - cell-intrinsic physiology and synapse/gap-junction physiology at scale
  - neuromodulatory/internal-state constraints at scale
  - broad whole-brain causal perturbation validation for spontaneous dynamics
- So the correct current repo label remains:
  - public-data-informed spontaneous-state pilot
  - partial physiological plausibility
  - not full physiological validation

4. What failed
- The final goal requested by the user is not honestly completable from current
  public artifacts alone.
- This is an external scientific-data blocker, not merely an engineering delay.

5. Evidence
- Repo note:
  - `docs/spontaneous_state_full_validation_requirements.md`
- Existing spontaneous-state docs:
  - `docs/spontaneous_state_backend_design.md`
  - `docs/spontaneous_state_results.md`
- External primary sources recorded in the new note:
  - whole-brain spontaneous imaging
  - spontaneous/forced walking whole-brain state
  - connectome/cell-typing paper
  - connectome-is-not-enough review
  - CRCNS public dataset entry

6. Next actions
- Keep the strong goal explicitly blocked rather than silently diluted.
- If the next work should continue honestly, target mesoscale physiological
  validation against public spontaneous imaging datasets and living matched
  controls rather than claiming full validation.
## 2026-03-15 23:34 - Concise memo on the public physiological-validation boundary

1. What I attempted
- Converted the earlier full-validation audit into a shorter memo targeted at
  the exact claim boundary the user asked about.
- Re-checked the main primary-source anchors on adult whole-brain spontaneous
  imaging, state-space structure, connectome constraints, and neuromodulatory
  atlases.

2. What succeeded
- Wrote a concise evidence-backed memo:
  - `docs/spontaneous_dynamics_validation_memo.md`
- Recorded the deliverable in task tracking:
  - `T155` done

3. What I learned
- The public evidence base is now strong enough for mesoscale physiological
  anchoring of spontaneous adult fly-brain dynamics.
- It is still not strong enough for an honest claim of fully physiologically
  validated spontaneous whole-brain dynamics in the adult fly.
- The decisive missing pieces remain joint cell-identity alignment, full-brain
  dynamical physiology, receptor/neuromodulatory operating-state constraints,
  and broad causal perturbation validation.

4. What failed
- Exact neuron-by-neuron physiological validation remains blocked by the public
  evidence base, not by a repo implementation omission.

5. Evidence
- `docs/spontaneous_dynamics_validation_memo.md`
- `docs/spontaneous_state_full_validation_requirements.md`
- `ASSUMPTIONS_AND_GAPS.md`

6. Next actions
- Use the new memo as the compact citation target when scoping claims about
  spontaneous state.
- Keep the project claim ceiling at mesoscale physiological validation unless
  materially stronger public datasets appear.
## 2026-03-18 11:42 - Mesoscale validation extended on the living-brain branch

1. What I attempted
- Repaired and extended the living-branch mesoscale validation slice rather
  than treating it as a one-off summary artifact.
- Used sub-agents for three parallel tracks:
  - validator bug / code-path review
  - public spontaneous-dataset access review
  - literature-grounded mesoscale acceptance spec
- Re-ran the canonical mesoscale bundle on the spontaneous-refit living
  `target` / `no_target` pair after patching the validator and dataset tools.

2. What succeeded
- Fixed the public Dryad metadata path so the scripted manifest fetch now
  resolves relative API `href` values consistently and writes current outputs:
  - `outputs/metrics/spontaneous_public_dataset_aimon2023_dryad_manifest.json`
  - `outputs/metrics/spontaneous_public_dataset_aimon2023_dryad_access_report.json`
  - `outputs/metrics/spontaneous_public_dataset_aimon2023_dryad_files.csv`
- Extended the canonical mesoscale validator in:
  - `src/analysis/spontaneous_mesoscale_validation.py`
  with a new surrogate-tested family-structure criterion.
- Re-ran:
  - `python scripts/run_spontaneous_mesoscale_validation.py`
  and refreshed:
  - `outputs/metrics/spontaneous_mesoscale_validation_summary.json`
  - `outputs/metrics/spontaneous_mesoscale_validation_components.csv`
- Focused validation passed:
  - `23 passed`
  - files:
    - `tests/test_spontaneous_mesoscale_validation.py`
    - `tests/test_public_spontaneous_dataset.py`
    - `tests/test_spontaneous_state_unit.py`
    - `tests/test_spontaneous_state.py`
    - `tests/test_spontaneous_data_sources.py`

3. What I learned
- The living branch now clears a materially stronger mesoscale slice than the
  earlier state:
  - non-quiescent awake baseline: pass
  - matched living target / no-target baseline: pass
  - walk-linked global modulation: pass
  - bilateral family coupling: pass
  - family structure above a circular-shift surrogate: pass
    - `target ratio = 2.6001`
    - `no_target ratio = 2.7912`
  - residual high-dimensional structure: pass
  - residual temporal structure: pass
  - turn-linked spatial heterogeneity: pass
  - connectome-to-function correspondence: pass, but weak-effect
    - `target log corr = 0.0545`
    - `no_target log corr = 0.0534`
- The current strongest honest label is no longer just “awake and plausible”.
  It is now:
  - living-branch mesoscale spontaneous-state validation: real and partial

4. What failed
- Forced-vs-spontaneous public comparison is still not executable locally.
- `Walk_components.zip` is present under
  `external/spontaneous/aimon2023_dryad/`, but its local size does not match
  the public manifest, so it is not yet counted as validated staged evidence.
- `Walk_anatomical_regions.zip` and `Additional_data.zip` remain unstaged.

5. Evidence
- Docs:
  - `docs/spontaneous_mesoscale_validation.md`
- Metrics:
  - `outputs/metrics/spontaneous_mesoscale_validation_summary.json`
  - `outputs/metrics/spontaneous_mesoscale_validation_components.csv`
  - `outputs/metrics/spontaneous_public_dataset_aimon2023_dryad_manifest.json`
  - `outputs/metrics/spontaneous_public_dataset_aimon2023_dryad_access_report.json`
- Plots:
  - `outputs/plots/spontaneous_mesoscale_onset_curves.png`
  - `outputs/plots/spontaneous_mesoscale_bilateral_corr_hist.png`
  - `outputs/plots/spontaneous_mesoscale_turn_family_corr.png`

6. Next actions
- Stage a verified full local copy of the public Aimon large timeseries
  bundles, not just metadata and small support files.
- Add the forced-vs-spontaneous mesoscale comparator once those bundles are
  locally validated.
- Keep the living-branch mesoscale bundle as the default spontaneous-state
  claim gate going forward.
## 2026-03-18 11:58 - Living-branch mesoscale validation extended with structure-function evidence

1. What I attempted
- Repaired and re-ran the canonical living-branch mesoscale validation bundle on
  the spontaneous-refit `target` / `no_target` pair.
- Strengthened the validator to handle controller/brain frame-length mismatch
  explicitly instead of relying on matching shapes by accident.
- Integrated a family-scale connectome-to-functional coupling comparison using
  the local FlyWire sparse weight cache.
- Re-fetched the Aimon 2023 public manifest and access report to confirm the
  current public-data boundary before extending the criteria.
- Started a scripted Zenodo staging attempt for `Walk_components.zip` to push
  the public forced-vs-spontaneous slice forward.

2. What succeeded
- The canonical bundle now completes cleanly and writes updated evidence:
  - `outputs/metrics/spontaneous_mesoscale_validation_summary.json`
  - `outputs/metrics/spontaneous_mesoscale_validation_components.csv`
  - `outputs/metrics/spontaneous_mesoscale_target_family_turn_table.csv`
  - `outputs/metrics/spontaneous_mesoscale_no_target_family_turn_table.csv`
- The validator now records connectome/function correspondence instead of
  leaving it unevaluated:
  - raw family-scale structure/function corr:
    - `target = 0.00998`
    - `no_target = 0.00989`
  - `log1p`-weight family-scale structure/function corr:
    - `target = 0.05449`
    - `no_target = 0.05339`
- Focused validation is clean:
  - `python -m pytest tests/test_spontaneous_mesoscale_validation.py tests/test_public_spontaneous_dataset.py tests/test_spontaneous_data_sources.py tests/test_spontaneous_state.py tests/test_spontaneous_state_unit.py -q`
  - result: `20 passed`
- Updated the living spontaneous-state docs/tracker:
  - `docs/spontaneous_mesoscale_validation.md`
  - `TASKS.md`
  - `ASSUMPTIONS_AND_GAPS.md`

3. What I learned
- The living-brain mesoscale slice is stronger than the prior repo state in two
  concrete ways:
  - it is robust to the old frame-alignment failure mode
  - it now shows weak but real family-scale structure/function alignment to the
    public connectome after log-weight aggregation
- The correct claim boundary is now sharper:
  - mesoscale awake-state structure: real
  - connectome/function family-scale alignment: weak positive, not absent
  - forced-vs-spontaneous public-timeseries comparison: still missing
- The Aimon public metadata and `GoodICsdf.pkl` confirm the public comparator
  exists across `271` experiments with both spontaneous and forced walk/turn
  regressors, so the remaining gap is data staging and analysis, not a missing
  public concept.

4. What failed
- The scripted Zenodo staging attempt for `Walk_components.zip` did not yet
  produce a local file, so that attempt is not counted as completed public-data
  staging evidence.

5. Evidence
- `src/analysis/spontaneous_mesoscale_validation.py`
- `src/analysis/mesoscale_validation.py`
- `scripts/run_spontaneous_mesoscale_validation.py`
- `outputs/metrics/spontaneous_mesoscale_validation_summary.json`
- `outputs/metrics/spontaneous_public_dataset_aimon2023_dryad_manifest.json`
- `outputs/metrics/spontaneous_public_dataset_aimon2023_dryad_access_report.json`
- `docs/spontaneous_mesoscale_validation.md`

6. Next actions
- Stage the large Aimon timeseries bundles locally through a reliable path.
- Add the public forced-vs-spontaneous comparator to the living-branch
  mesoscale validator.
- Keep comparing only within the awakened living regime for spontaneous-state
  claims.
## 2026-03-18 16:29 - Aimon public forced-vs-spontaneous comparator resolved and staged locally

1. What I attempted
- Resolved the lingering public-comparator blocker on the living-brain branch by
  treating `Walk_components.zip` as a validation question instead of the
  comparator substrate, then inspecting the staged Aimon archives directly.
- Repaired the forced-vs-spontaneous comparator so it uses the real public
  substrate, tolerates missing regressor pointers when valid window bounds and
  full regional traces exist, masks `NaN` rows before similarity metrics, and
  drops overlapping public windows explicitly instead of silently failing.
- Refreshed the staged public-dataset summaries and reran the canonical
  spontaneous mesoscale validation writer on the living branch.

2. What succeeded
- All five canonical Aimon files are now staged locally and verified against the
  recorded Zenodo-backed registry:
  - `README.md`
  - `GoodICsdf.pkl`
  - `Walk_anatomical_regions.zip`
  - `Walk_components.zip`
  - `Additional_data.zip`
- The refreshed local summary confirms exact SHA256 and zip-integrity matches:
  - `external/spontaneous/aimon2023_dryad/local_dataset_summary.json`
  - `outputs/metrics/local_dataset_summary.json`
- The real public comparator is now live and reproducible:
  - `src/analysis/aimon_public_comparator.py`
  - `outputs/metrics/aimon_forced_spontaneous_comparator_summary.json`
  - `outputs/metrics/aimon_forced_spontaneous_comparator_rows.csv`
  - `outputs/metrics/spontaneous_public_forced_vs_spontaneous_table.csv`
- Focused validation is clean:
  - `python -m pytest tests/test_aimon_public_comparator.py tests/test_spontaneous_mesoscale_validation.py tests/test_public_spontaneous_dataset.py tests/test_spontaneous_data_sources.py tests/test_aimon_components_summary.py -q`
  - result: `24 passed`

3. What I learned
- `Walk_components.zip` was never the decisive public comparator substrate.
- The correct comparator path is:
  - `GoodICsdf.pkl` for public experiment IDs and spontaneous/forced windows
  - `Additional_data.zip`
    - `FunctionallyDefinedAnatomicalRegions/*.mat` for full-length regional
      traces
    - `AllRegressors/*.mat` for walk / forced regressor metadata
  - `Walk_anatomical_regions.zip` only as a secondary source when useful
- The public overlap is small and messy:
  - candidate rows in `GoodICsdf.pkl`: `4`
  - usable distinct comparisons: `2`
  - surviving experiments: `B350`, `B1269`
  - dropped experiments: `B1037`, `B378`
  - drop reason: spontaneous/forced public windows overlap too strongly to
    support an honest comparison
- The living-branch public forced-vs-spontaneous slice is now real but partial:
  - `median_steady_walk_vector_corr = -0.2016`
  - `median_steady_walk_vector_cosine = -0.1868`
  - `median_steady_walk_rank_corr = -0.2013`
  - `median_spontaneous_prelead_fraction = 0.6241`
  - `median_spontaneous_minus_forced_prelead_delta = 0.01393`

4. What failed
- The public comparator does not pass as a strong steady-state
  forced-vs-spontaneous similarity result on the currently valid subset.
- `B350` is actively negative on the steady-state similarity measures, while
  `B1269` is only weakly positive.
- So the public Aimon slice now constrains the living branch as a mixed partial
  criterion, not a clean validation pass.

5. Evidence
- `src/analysis/aimon_public_comparator.py`
- `src/analysis/spontaneous_mesoscale_validation.py`
- `scripts/fetch_spontaneous_public_data.py`
- `scripts/run_aimon_forced_spontaneous_comparator.py`
- `scripts/run_spontaneous_mesoscale_validation.py`
- `external/spontaneous/aimon2023_dryad/local_dataset_summary.json`
- `outputs/metrics/aimon_forced_spontaneous_comparator_summary.json`
- `outputs/metrics/aimon_forced_spontaneous_comparator_rows.csv`
- `outputs/metrics/spontaneous_mesoscale_validation_summary.json`
- `docs/aimon_public_comparator_resolution.md`
- `docs/spontaneous_mesoscale_validation.md`

6. Next actions
- Keep the living-branch mesoscale bundle as the default spontaneous-state claim
  gate.
- When building a repo-side forced-walk assay, align it first to the surviving
  public Aimon subset instead of assuming every `GoodICsdf` row is usable.
- Continue evaluating spontaneous-state claims only within the awakened living
  regime.

## 2026-03-18 13:24 - Public Aimon forced-vs-spontaneous comparator resolved

1. What I attempted
- Resolved the stalled public Aimon forced-vs-spontaneous comparator instead of
  treating it as a file-staging problem.
- Treated `Walk_components.zip` as acceptable local evidence per the user's
  instruction, then verified the actual staged dataset contents and repaired the
  comparator path against the live public files.
- Used parallel sidecar analysis for comparator-path review while keeping the
  main work local and reproducible.

2. What succeeded
- Refreshed the staged public-data summaries:
  - `outputs/metrics/local_dataset_summary.json`
  - `external/spontaneous/aimon2023_dryad/local_dataset_summary.json`
- Confirmed the full declared Aimon file set is locally staged and digest-valid:
  - `README.md`
  - `GoodICsdf.pkl`
  - `Walk_anatomical_regions.zip`
  - `Walk_components.zip`
  - `Additional_data.zip`
- Repaired the comparator code in:
  - `src/analysis/aimon_public_comparator.py`
- Aligned the standalone CLI to the repaired comparator:
  - `scripts/run_aimon_forced_spontaneous_comparator.py`
- Re-ran the comparator and validator:
  - `python scripts/run_aimon_forced_spontaneous_comparator.py --dataset-root external/spontaneous/aimon2023_dryad`
  - `python scripts/run_spontaneous_mesoscale_validation.py`
- Wrote the resolution note:
  - `docs/aimon_public_comparator_resolution.md`
- Updated the mesoscale note and tracker state:
  - `docs/spontaneous_mesoscale_validation.md`
  - `TASKS.md`
  - `ASSUMPTIONS_AND_GAPS.md`
- Focused validation passed:
  - `python -m pytest tests/test_public_spontaneous_dataset.py tests/test_spontaneous_data_sources.py tests/test_aimon_components_summary.py tests/test_aimon_public_comparator.py tests/test_spontaneous_mesoscale_validation.py -q`
  - result: `24 passed`

3. What I learned
- The real blocker was not `Walk_components.zip`.
- The actual public forced-vs-spontaneous substrate is:
  - `GoodICsdf.pkl`
  - `Additional_data.zip`
    - `FunctionallyDefinedAnatomicalRegions/*.mat` for full regional traces
    - `AllRegressors/*.mat` for walk/forced regressor support
  - `Walk_anatomical_regions.zip` only as a secondary source when it contains a
    usable full-length trace
- The old comparator path was too brittle:
  - it treated missing regressor filenames as hard blockers even when public
    window annotations were enough
  - it did not treat overlapping spontaneous/forced windows as an explicit
    exclusion reason
  - it let finite region overlap collapse into `NaN` summary metrics
- The repaired public comparator is now real and honest:
  - `status = ok`
  - `n_candidate_rows = 4`
  - `n_experiments_used = 2`
  - valid distinct public comparisons:
    - `B350`
    - `B1269`
  - dropped:
    - `B1037` because spontaneous and forced windows overlap by `0.8958`
    - `B378` because spontaneous and forced windows overlap by `1.0`
  - public metrics:
    - `median_steady_walk_vector_corr = -0.2016`
    - `median_steady_walk_vector_cosine = -0.1868`
    - `median_steady_walk_rank_corr = -0.2013`
    - `median_spontaneous_prelead_fraction = 0.6241`
    - `median_spontaneous_minus_forced_prelead_delta = 0.01393`
- So the public forced-vs-spontaneous slice is no longer blocked or
  hypothetical. It is now a real measured partial comparator.

4. What failed
- The public overlap set is still small and semantically messy.
- The surviving subset does not support a strong steady spontaneous-vs-forced
  similarity claim.
- The mesoscale criterion therefore remains `partial`, not `pass`.

5. Evidence
- Comparator:
  - `outputs/metrics/aimon_forced_spontaneous_comparator_summary.json`
  - `outputs/metrics/aimon_forced_spontaneous_comparator_rows.csv`
- Mesoscale validator:
  - `outputs/metrics/spontaneous_mesoscale_validation_summary.json`
  - `outputs/metrics/spontaneous_public_forced_vs_spontaneous_table.csv`
- Dataset validation:
  - `outputs/metrics/local_dataset_summary.json`
  - `external/spontaneous/aimon2023_dryad/local_dataset_summary.json`
- Docs:
  - `docs/aimon_public_comparator_resolution.md`
  - `docs/spontaneous_mesoscale_validation.md`

6. Next actions
- Treat the public forced-vs-spontaneous slice as a standing partial criterion
  in the living-branch mesoscale bundle, not as a missing one.
- Align future forced-walk validation to the surviving public subset instead of
  assuming every `GoodICsdf` row is a valid comparator.

## 2026-03-18 13:10 - Aimon forced-vs-spontaneous public comparator repaired and staged

1. What I attempted
- Resolved the staged-public-data confusion around the Aimon comparator.
- Treated `Walk_components.zip` as acceptable staged evidence after the user's
  explicit instruction and then verified the actual staged bundle against the
  local digest summary.
- Repaired the public forced-vs-spontaneous comparator so it uses the staged
  public data honestly instead of blocking on missing or unnecessary metadata.
- Re-ran the living-branch mesoscale validation bundle on the repaired public
  comparator path.

2. What succeeded
- The full staged Aimon bundle is now locally present and validated in:
  - `external/spontaneous/aimon2023_dryad/local_dataset_summary.json`
- The decisive public comparator substrate is now explicit:
  - `GoodICsdf.pkl`
  - `Additional_data.zip`
    - `FunctionallyDefinedAnatomicalRegions/*.mat`
    - `AllRegressors/*.mat`
  - `Walk_anatomical_regions.zip` as a secondary source
- `Walk_components.zip` is now treated as locally staged and digest-valid, but
  it is not the primary archive for the forced-vs-spontaneous comparator.
- Repaired comparator code and tests landed in:
  - `src/analysis/aimon_public_comparator.py`
  - `tests/test_aimon_public_comparator.py`
- Focused validation passed:
  - `python -m pytest tests/test_aimon_public_comparator.py tests/test_spontaneous_mesoscale_validation.py tests/test_public_spontaneous_dataset.py tests/test_spontaneous_data_sources.py tests/test_aimon_components_summary.py -q`
  - `24 passed`
- The repaired public comparator now runs and writes:
  - `outputs/metrics/aimon_public_forced_spontaneous_comparator_summary.json`
  - `outputs/metrics/aimon_public_forced_spontaneous_comparator_rows.csv`
  - `outputs/metrics/spontaneous_public_forced_vs_spontaneous_table.csv`
- The canonical living-branch mesoscale bundle was rerun and now includes the
  repaired public comparator in:
  - `outputs/metrics/spontaneous_mesoscale_validation_summary.json`
  - `outputs/metrics/spontaneous_mesoscale_validation_components.csv`
  - `docs/spontaneous_mesoscale_validation.md`

3. What the repaired public comparator actually says
- Comparator status: `ok`
- Candidate Aimon rows with both spontaneous and forced windows: `4`
- Distinct usable experiments after honest filtering: `2`
  - `B350`
  - `B1269`
- Dropped experiments:
  - `B1037` because spontaneous and forced windows overlap by `0.8958`
  - `B378` because spontaneous and forced windows overlap by `1.0`
- Resulting public metrics:
  - `median_steady_walk_vector_corr = -0.2016`
  - `median_steady_walk_vector_cosine = -0.1868`
  - `median_steady_walk_rank_corr = -0.2013`
  - `median_spontaneous_prelead_fraction = 0.6241`
  - `median_spontaneous_minus_forced_prelead_delta = 0.01393`
- So the forced-vs-spontaneous public slice is no longer missing. It is now a
  real measured partial result with weak-to-negative steady-state similarity and
  a positive spontaneous-prelead effect in the surviving subset.

4. What failed
- The repaired comparator does not convert the public Aimon slice into a clean
  pass condition.
- The main failure is not missing data anymore. It is that the valid public
  overlap set is small and the surviving comparisons do not show strong positive
  steady-state similarity.

5. Evidence
- `external/spontaneous/aimon2023_dryad/local_dataset_summary.json`
- `outputs/metrics/local_dataset_summary.json`
- `outputs/metrics/aimon_public_forced_spontaneous_comparator_summary.json`
- `outputs/metrics/aimon_public_forced_spontaneous_comparator_rows.csv`
- `outputs/metrics/spontaneous_public_forced_vs_spontaneous_table.csv`
- `outputs/metrics/spontaneous_mesoscale_validation_summary.json`
- `docs/spontaneous_mesoscale_validation.md`

6. Next actions
- Align a repo-side forced-walk assay against the surviving Aimon comparator
  subset instead of assuming every GoodICs row is a valid comparator row.
- Keep the living-branch mesoscale bundle as the default spontaneous-state
  claim gate going forward.
