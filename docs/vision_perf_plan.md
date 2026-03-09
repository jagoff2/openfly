# Vision Performance Plan

Grounded in `AGENTS.MD` and scoped to the current repo.

## Goal

Remove the dominant realistic-vision overhead caused by `LayerActivity` construction and repeated `datamate` access, while keeping:

- real FlyGym realistic vision
- the current whole-brain backend
- the current benchmark and artifact pipeline
- a fallback-compatible legacy path for validation

This plan targets the current dominant bottleneck seen in `outputs/profiling/fullstack_flygym_0p02.txt`.

## Root Cause

Current hot path:

1. `flygym/examples/vision/realistic_vision.py:112-124`
   - runs `forward_one_step(...)`
   - converts the result to NumPy
   - immediately constructs `LayerActivity(...)`

2. `flyvis/utils/activity_utils.py:244-274`
   - `LayerActivity.__init__` reads connectome metadata repeatedly
   - builds per-cell-type indexing on every update
   - triggers heavy `datamate` HDF5-backed access

3. `datamate/io.py:87-97`
   - each `__getitem__` retry path includes `sleep(0.1)`
   - this is visible in the full-stack profile as a major wall-time sink

Current repo-side overhead that compounds this:

4. `src/body/flygym_runtime.py:80-88`
   - copies the `LayerActivity` object into a Python dictionary keyed by cell type on every step

5. `src/vision/feature_extractor.py`
   - then re-aggregates those copied values into the few features we actually use

In short:

- we pay to build a rich `LayerActivity`
- we pay again to copy it into a dict
- we then throw almost all of that structure away and keep only a few pooled features

## Performance Strategy

Do not materialize `LayerActivity` in the production path.

Instead:

- keep `nn_activities_arr` from `forward_one_step(...)`
- precompute the cell-type indices we care about exactly once
- aggregate the required tracking and motion cell families directly from the raw activity array
- pass only compact feature summaries or raw array + cached indices through the repo

This removes the `LayerActivity` / `datamate` hot path from the steady-state loop.

## Preferred Approach

Implement the fast path in-repo rather than patching installed site-packages directly.

Reason:

- reproducible in this repo
- safer than mutating `site-packages`
- easy to benchmark against the legacy path
- keeps a clean fallback path if upstream APIs shift

## Exact File-Level Changes

### 1. `src/vision/feature_extractor.py`

Expand the feature extractor to operate directly on the raw FlyVis activity array.

Required additions:

- add a `VisionIndexCache` dataclass that stores the precomputed indices needed for:
  - `DEFAULT_TRACKING_CELLS`
  - `DEFAULT_FLOW_CELLS`
- add a builder, for example:
  - `VisionIndexCache.from_node_types(node_types: np.ndarray, tracking_cells: Sequence[str], flow_cells: Sequence[str])`
- add a fast extraction method, for example:
  - `extract_from_array(nn_activities_arr: np.ndarray, index_cache: VisionIndexCache) -> VisionFeatures`

Implementation details:

- `nn_activities_arr` from FlyGym has shape `(2, num_cells_per_eye)`
- `VisionIndexCache` should store indices in that cell axis only
- aggregation should be a direct NumPy reduction over the cached indices
- do not build per-cell dictionaries in the fast path

Keep:

- the current mapping-based `extract(...)` path as a compatibility fallback

Acceptance checks:

- fast-path and legacy-path outputs should match within tolerance on the same saved sample arrays
- unit tests should cover empty-index and missing-cell cases

### 2. `src/vision/flyvis_fast_path.py` (new)

Create a small helper module for extracting and caching only the cell-type metadata we need.

Required functions:

- `load_node_types(connectome) -> np.ndarray`
- `build_required_cell_indices(connectome, tracking_cells, flow_cells) -> VisionIndexCache`

Implementation details:

- do one connectome read of `connectome.nodes.type[:]`
- compute indices with `np.nonzero(node_types == cell_type)` for only the required cell families
- do not iterate all unique cell types
- do not call `connectome.nodes.layer_index[cell_type][:]` in the hot loop

Reason:

- this reproduces only the subset of `LayerActivity` indexing we actually need
- it avoids the per-step `datamate` calls that dominate the current profile

### 3. `src/body/fast_realistic_vision_fly.py` (new)

Create an in-repo subclass of FlyGym's realistic-vision fly.

Preferred base class:

- subclass `flygym.examples.vision.RealisticVisionFly`

Required overrides:

- `__init__`:
  - keep the current FlyGym setup
  - initialize a cached `VisionIndexCache` holder to `None`
- `_initialize_vision_network(...)`:
  - call parent or inline current implementation
  - after the vision network is ready, build the `VisionIndexCache` once from `self.vision_network.connectome`
- `_get_visual_nn_activities(...)`:
  - run `forward_one_step(...)`
  - convert to NumPy
  - do not construct `LayerActivity`
  - optionally compute compact features immediately from the array + cached indices
  - return only the array and compact summary payload
- `post_step(...)` and `reset(...)`:
  - expose a fast payload in `info`, for example:
    - `info["nn_activities_arr"]`
    - `info["vision_features_fast"]`
    - `info["vision_index_cache_ready"]`
  - do not populate `info["nn_activities"]` in fast mode

Key line to eliminate from the steady-state path:

- `LayerActivity(...)` currently created in `flygym/examples/vision/realistic_vision.py:118-123`

Acceptance checks:

- reset and step behavior remain functionally identical for body physics and vision refresh timing
- production runs no longer spend time in `flyvis.utils.activity_utils.LayerActivity.__init__`

### 4. `src/body/flygym_runtime.py`

Switch the production runtime to use the fast vision wrapper.

Required changes:

- in `_setup_imports()`, import the new in-repo `FastRealisticVisionFly`
- in `_build_simulation()`, instantiate `FastRealisticVisionFly` instead of the stock `RealisticVisionFly`
- in `_make_observation(...)`, stop copying every cell type out of `info["nn_activities"]`
- instead, prefer:
  - `info.get("vision_features_fast")`
  - `obs.get("nn_activities_arr")` or `info.get("nn_activities_arr")`

Important removal:

- delete the per-step loop at `src/body/flygym_runtime.py:82-85` in fast mode

Acceptance checks:

- no production-path dependence remains on `LayerActivity.keys()` or per-cell dictionary expansion
- `BodyObservation` still contains enough information for the bridge and debug logs

### 5. `src/body/interfaces.py`

Extend `BodyObservation` to carry the fast vision payload explicitly.

Required additions:

- `realistic_vision_array: Any = None`
- `realistic_vision_features: dict[str, float] | None = None`
- optionally `vision_payload_mode: str = "legacy"`

Keep:

- existing `realistic_vision` mapping field for legacy compatibility

Acceptance checks:

- legacy tests continue to work unchanged
- fast path can avoid the mapping field entirely

### 6. `src/bridge/controller.py`

Teach the bridge to prefer precomputed fast vision features.

Required changes:

- if `BodyObservation.realistic_vision_features` is present, construct `VisionFeatures` directly from it or use it as-is
- else if `realistic_vision_array` is present with a cached index structure, call the new fast extractor
- else fall back to the current mapping-based extractor

Goal:

- the bridge should not force the body runtime to rebuild legacy structures

### 7. `src/runtime/closed_loop.py`

Add a config-controlled fast-vision mode.

Required changes:

- support a runtime/config flag such as:
  - `runtime.fast_vision_path: true`
- log which vision payload mode was active in the JSONL output
- preserve benchmark CSV schema

Acceptance checks:

- benchmark scripts can toggle legacy vs fast path cleanly
- artifact generation remains unchanged

### 8. `configs/flygym_realistic_vision.yaml`

After validation, add:

- `runtime.fast_vision_path: true`

Before flipping the validated default, benchmark both modes side by side.

### 9. `benchmarks/run_vision_benchmarks.py`

Add a switch to compare legacy and fast vision payload modes.

Required changes:

- add `--vision-payload-mode legacy|fast`
- emit separate rows in `outputs/benchmarks/vision_benchmarks.csv`
- keep plot output compatible

### 10. `benchmarks/run_fullstack_with_realistic_vision.py`

Add the same toggle to the full-stack benchmark and demo runner.

Required changes:

- add `--vision-payload-mode legacy|fast`
- emit separate benchmark rows
- keep artifact output isolated per run

### 11. `tests/test_realistic_vision_path.py`

Add a fast-path unit test.

Required test coverage:

- build a synthetic `nn_activities_arr`
- build a synthetic `VisionIndexCache`
- verify `extract_from_array(...)` matches the current mapping-based extractor on equivalent synthetic data

### 12. `tests/test_closed_loop_smoke.py`

Add a smoke test for the fast vision payload path.

Required coverage:

- short run using a synthetic or lightweight observation path
- assert no legacy mapping expansion is required
- assert feature summaries appear in the log output

### 13. `docs/perf_tuning.md`

After implementation, update the doc with:

- before/after profiling tables
- whether the `time.sleep` hotspot disappears from the dominant profile entries
- whether the bottleneck shifts to actual network forward, physics, or rendering

## Optional Patch Path

If the repo-local wrapper is not enough, add a reproducible patch artifact under:

- `patches/flygym_fast_vision.patch`

This patch would modify the installed `flygym/examples/vision/realistic_vision.py` logic to:

- stop constructing `LayerActivity`
- emit raw arrays and compact summaries directly

Use this only if subclassing cannot intercept the relevant code cleanly.

## Validation Plan

### A. Micro-level

1. Save one sample `nn_activities_arr` from the current path.
2. Compare:
   - legacy `LayerActivity` -> dict -> `RealisticVisionFeatureExtractor.extract(...)`
   - fast `VisionIndexCache` -> `extract_from_array(...)`
3. Require numeric agreement within a small tolerance.

### B. Vision-only benchmark

Run:

- legacy payload mode
- fast payload mode

Compare:

- wall seconds
- real-time factor
- profile top hotspots

Success condition:

- `LayerActivity.__init__`, `datamate.io.__getitem__`, and `time.sleep` no longer dominate the steady-state profile

### C. Full-stack benchmark

Run the same short/medium sweep currently used in the repo and compare:

- wall seconds
- real-time factor
- parity metrics
- video/log/metrics generation

Success condition:

- substantial wall-time reduction without changing control semantics materially

## Expected Outcome

What should improve immediately:

- removal of repeated `LayerActivity` construction
- removal of most `datamate` access from the steady-state loop
- removal of the large associated `time.sleep` overhead from retries

What will remain:

- FlyGym physics cost
- actual FlyVis network step cost
- rendering/video overhead
- WSL CPU-only limitation until `sm_120` GPU support is available publicly

## Execution Order

1. `src/vision/flyvis_fast_path.py`
2. `src/vision/feature_extractor.py`
3. `src/body/fast_realistic_vision_fly.py`
4. `src/body/interfaces.py`
5. `src/body/flygym_runtime.py`
6. `src/bridge/controller.py`
7. `src/runtime/closed_loop.py`
8. `benchmarks/run_vision_benchmarks.py`
9. `benchmarks/run_fullstack_with_realistic_vision.py`
10. `tests/test_realistic_vision_path.py`
11. `tests/test_closed_loop_smoke.py`
12. `docs/perf_tuning.md`
13. `TASKS.md` and `PROGRESS_LOG.md`

## Risks

1. FlyGym/FlyVis upstream objects may change shape or field naming across versions.
2. If any downstream code implicitly expects `info["nn_activities"]`, it must be updated or left behind a legacy flag.
3. If the current per-step behavior depends subtly on `LayerActivity` semantics beyond the features we use, the fast path must be validated carefully.
4. Even after this fix, full-stack throughput may still be limited by CPU-only FlyVis on WSL.
