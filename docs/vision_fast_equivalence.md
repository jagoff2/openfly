# Vision Fast-Path Equivalence

Grounded in `AGENTS.MD`.

## Claim

For the control-relevant vision path used by this repo, the new fast path is exactly equivalent to the original legacy path on the same input.

More precisely:

- same `nn_activities_arr`
- same FlyVis connectome
- same tracked / flow cell lists

implies:

- exactly the same `VisionFeatures`
- exactly the same sensory pool rates
- exactly the same sensor metadata
- exactly the same downstream motor readout
- exactly the same final `BodyCommand`

## Why This Is True

The legacy path does:

1. `LayerActivity(nn_activities_arr, connectome, ...)`
2. `nn_activities[cell_type] -> nn_activities_arr[..., layer_index[cell_type]]`
3. `RealisticVisionFeatureExtractor.extract(...)`

The fast path does:

1. build cached indices from `connectome.nodes.type[:]`
2. `nn_activities_arr[..., cached_index[cell_type]]`
3. `RealisticVisionFeatureExtractor.extract_from_array(...)`

In the installed FlyVis code, `LayerActivity` uses:

- `connectome.nodes.layer_index[cell_type][:]`

for each cell type.

In this repo, the fast path uses:

- `np.flatnonzero(connectome.nodes.type[:] == cell_type)`

for each tracked / flow cell type.

For the currently installed FlyVis connectome used by `configs/flygym_realistic_vision.yaml`, these index arrays are exactly equal for every tracked / flow cell family used by the bridge.

Once the index arrays are identical, both implementations compute the same sequence of reductions:

- mean over cells within each eye for a cell type
- optional absolute value for tracking cells
- mean across the configured cell types

So the extracted four control features are identical for any `nn_activities_arr`.

## Proof Artifact

Generated with:

```bash
wsl.exe bash -lc "cd /mnt/g/flysim && export MUJOCO_GL=egl && ~/.local/bin/micromamba run -n flysim-full python scripts/prove_vision_fast_equivalence.py --config configs/flygym_realistic_vision.yaml --output outputs/metrics/vision_fast_equivalence.json"
```

Artifact:

- `outputs/metrics/vision_fast_equivalence.json`

Key results:

- `all_index_arrays_exact = true`
- `all_samples_exact_feature_match = true`
- `all_samples_exact_sensor_pool_match = true`
- `all_samples_exact_sensor_metadata_match = true`
- `all_samples_exact_motor_rate_match = true`
- `all_samples_exact_command_match = true`
- `max_feature_abs_diff = 0.0`
- `max_command_abs_diff = 0.0`

Checked real WSL production samples:

- `reset`
- `step_1`
- `step_2`

## Test Coverage

Local exact-equality unit coverage:

- `tests/test_realistic_vision_path.py`

The unit tests check:

- exact equality between legacy and fast feature extraction on the same synthetic input
- exact equality of downstream control outputs on the same observation

## Scope

What is proven equivalent:

- the control-relevant vision behavior used by this repo
- same input array -> same control output

What is intentionally not identical:

- the legacy `info["nn_activities"]` `LayerActivity` payload is not emitted in fast mode
- fast mode emits compact summaries instead

So the proof is about behavioral equivalence of the closed-loop control path, not byte-for-byte equality of every debug payload in `info`.
