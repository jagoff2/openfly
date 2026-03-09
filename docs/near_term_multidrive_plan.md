# Near-Term Multidrive Implementation Plan

Grounded in `AGENTS.MD` and scoped to the current repo.

## Goal

Move the production control path from the current two-scalar descending interface to a richer but still tractable control interface, while keeping:

- real FlyGym physics
- real FlyGym realistic vision
- the public whole-brain backend
- the current closed-loop scheduler and artifact pipeline

This plan explicitly does not attempt a full biological connectome-to-muscle reconstruction. It targets better-than-two-drive control using the FlyGym locomotion stack that already expands high-level control into full joint trajectories.

## Current Baseline

Current production path:

- body runtime: `src/body/flygym_runtime.py`
- bridge: `src/bridge/controller.py`
- encoder: `src/bridge/encoder.py`
- decoder: `src/bridge/decoder.py`
- whole-brain backend: `src/brain/pytorch_backend.py`
- runtime scheduler: `src/runtime/closed_loop.py`
- production config: `configs/flygym_realistic_vision.yaml`

Current bottlenecks and limitations:

- realistic-vision runtime dominates wall time
- body command is only `left_drive` and `right_drive`
- mechanosensory encoding is compressed to four pooled rates
- monitored neural outputs are limited to a small DN readout set

## Near-Term Success Criteria

1. Production runs still use the real FlyGym realistic-vision path.
2. Production runs still use the public whole-brain backend.
3. Body control is no longer limited to two scalars.
4. Run logs expose multiple control channels that vary over time.
5. Realistic-vision multidrive demos remain stable and artifact-complete.
6. A/B benchmarks compare legacy two-drive vs multidrive control honestly.

## Design Choice

Use FlyGym's existing hybrid locomotion machinery as the low-level expansion layer.

Reason:

- `HybridTurningFly` already converts descending modulation into full joint and adhesion commands.
- Replacing that with direct muscle or raw joint control immediately would be a much larger project.
- A richer descending interface can be added now by subclassing the hybrid controller rather than discarding it.

## Proposed Command Space

Replace `BodyCommand(left_drive, right_drive)` with a richer command object in the production path.

Proposed fields:

- `left_amp`
- `right_amp`
- `left_freq_scale`
- `right_freq_scale`
- `left_stance_bias`
- `right_stance_bias`
- `retraction_gain`
- `stumbling_gain`
- `reverse_gate`

Interpretation:

- amplitude channels modulate stepping strength
- frequency channels modulate stepping cadence
- stance-bias channels modulate turn asymmetry more flexibly than one scalar per side
- correction gains modulate existing FlyGym retraction/stumbling logic
- reverse gate provides a stop/back-up control dimension without overloading turn channels

## File-Level Plan

### 1. `src/body/interfaces.py`

Add a new production command dataclass, for example `HybridDriveCommand`.

Required changes:

- keep the current `BodyCommand` for compatibility and tests
- add `HybridDriveCommand` with the fields listed above
- add a helper method or adapter for projecting `HybridDriveCommand` into the legacy two-drive form for baseline comparisons

Acceptance checks:

- legacy tests keep passing
- new command object is serializable in run logs

### 2. `src/body/connectome_turning_fly.py` (new)

Create a new FlyGym-side controller class that subclasses `HybridTurningFly`.

Required changes:

- accept the richer command vector instead of only shape `(2,)`
- map new channels into:
  - CPG amplitudes
  - CPG frequencies
  - left/right asymmetry terms
  - correction-rule gains
  - reverse/stop gating
- preserve adhesion and per-leg correction machinery from FlyGym

Implementation note:

- start by minimally overriding `pre_step(...)`
- do not fork the whole controller unless required
- keep the output action as FlyGym joint and adhesion signals

Acceptance checks:

- a smoke sim can step with the new controller
- the controller still emits valid joint commands for all actuated leg DoFs

### 3. `src/body/flygym_runtime.py`

Make runtime instantiation configurable between the current legacy path and the new multidrive path.

Required changes:

- add `control_mode` support, e.g. `legacy_2drive` and `hybrid_multidrive`
- if `hybrid_multidrive`, instantiate the new `ConnectomeTurningFly`
- preserve realistic vision exactly as today
- extend `BodyObservation` capture to include more proprioceptive/body state when available:
  - joint positions
  - joint velocities
  - per-leg contact summaries
  - adhesion state if exposed by info/obs

Acceptance checks:

- legacy config behavior remains unchanged
- new config resets, steps, closes, and renders successfully

### 4. `src/bridge/encoder.py`

Expand the mechanosensory side without trying to model the full periphery.

Required changes:

- keep current visual feature reduction path
- add tractable proprioceptive channels derived from FlyGym observations:
  - left/right stance load
  - fore/mid/hind contact load
  - average joint-phase proxy
  - stumble/slip proxy
- expose both the current four-pool encoding and an expanded encoding mode via config

Acceptance checks:

- encoder output remains deterministic for fixed input
- expanded encoder produces richer metadata logged to JSONL

### 5. `src/brain/public_ids.py`

Refactor monitored readout definitions into named groups.

Required changes:

- preserve current anchors:
  - `P9`
  - `oDN1`
  - `DNa01`
  - `DNa02`
  - `MDN`
- add grouped readout definitions intended for multidrive decoding
- document where groups are directly public and where they are engineering substitutes

Acceptance checks:

- old decoder path still resolves its groups correctly
- new decoder can request grouped outputs without hard-coding ad hoc logic

### 6. `src/brain/pytorch_backend.py`

Make readout monitoring more flexible.

Required changes:

- allow configurable monitored neuron IDs or monitored groups
- optionally return both raw neuron-rate dict and grouped summaries
- keep benchmark behavior unchanged for existing scripts

Acceptance checks:

- current brain benchmarks still run
- multidrive decoder can request the readouts it needs without patching backend internals again

### 7. `src/bridge/decoder.py`

Split the decoder into two explicit implementations.

Required changes:

- keep a `LegacyTwoDriveDecoder`
- add `HybridMultiDriveDecoder`
- new decoder maps grouped neural rates into the richer command channels
- add clipping, gains, and defaults via config
- expose all intermediate decoded signals for logging/debugging

Acceptance checks:

- unit tests cover saturation, asymmetry, reverse gating, and zero-input defaults
- logs show all multidrive channels

### 8. `src/bridge/controller.py`

Make the bridge decoder/encoder swappable by config.

Required changes:

- preserve current constructor defaults for legacy behavior
- allow multidrive encoder/decoder selection from runtime config
- keep existing `vision_extractor` integration unchanged

Acceptance checks:

- legacy closed-loop smoke tests remain unchanged
- multidrive bridge path returns the richer command object and structured debug info

### 9. `src/runtime/closed_loop.py`

Plumb control-mode selection and richer logging through the runtime.

Required changes:

- select legacy vs multidrive bridge/runtime behavior from config
- serialize the richer command fields into JSONL logs
- preserve benchmark summary generation and artifact writing

Acceptance checks:

- current production path still works with the old config
- multidrive runs produce complete artifacts and richer logs

### 10. `configs/flygym_realistic_vision_multidrive.yaml` (new)

Create a separate production config for the multidrive path.

Required changes:

- clone the validated realistic-vision config
- add:
  - `runtime.control_mode: hybrid_multidrive`
  - multidrive decoder gains/clipping
  - expanded encoder toggles
- keep `force_cpu_vision: true` for now because the WSL FlyVis GPU blocker still exists

Acceptance checks:

- this config can run end-to-end without affecting the existing validated baseline config

### 11. `tests/test_bridge_unit.py`

Add multidrive-specific unit tests.

Required changes:

- richer decoder clipping tests
- asymmetry tests
- reverse-gate tests
- deterministic zero-input tests

### 12. `tests/test_closed_loop_smoke.py`

Add a multidrive smoke run.

Required changes:

- short deterministic multidrive mock-body or lightweight body smoke test
- assert new command fields appear in the log/summary

### 13. `tests/test_realistic_vision_path.py`

Extend the production-path test.

Required changes:

- verify both legacy and multidrive configurations preserve realistic-vision feature extraction

### 14. `benchmarks/run_fullstack_with_realistic_vision.py`

Add explicit control-mode benchmarking.

Required changes:

- add `--control-mode`
- keep output schema unchanged
- run side-by-side legacy vs multidrive comparisons cleanly

### 15. `benchmarks/run_control_ablation.py` (new)

Create an A/B comparison script.

Metrics to compare:

- nonzero motor cycles
- command variance per channel
- turn response latency
- path length
- trajectory smoothness
- stability
- wall time and real-time factor

### 16. `docs/sensory_motor_mapping.md`

Update the mapping documentation.

Required changes:

- describe the new multidrive command space
- explain what is public-anchor-based vs inferred
- document how the new channels influence FlyGym locomotion internals

### 17. `docs/system_architecture.md`

Update the architecture doc.

Required changes:

- show the expanded command interface
- show richer proprioception channels
- keep the realistic-vision production path clearly marked

## Execution Order

1. `src/body/interfaces.py`
2. `src/body/connectome_turning_fly.py`
3. `src/body/flygym_runtime.py`
4. `src/bridge/decoder.py`
5. `src/bridge/encoder.py`
6. `src/bridge/controller.py`
7. `src/runtime/closed_loop.py`
8. `configs/flygym_realistic_vision_multidrive.yaml`
9. `tests/test_bridge_unit.py`
10. `tests/test_closed_loop_smoke.py`
11. `tests/test_realistic_vision_path.py`
12. `benchmarks/run_fullstack_with_realistic_vision.py`
13. `benchmarks/run_control_ablation.py`
14. `docs/sensory_motor_mapping.md`
15. `docs/system_architecture.md`
16. `TASKS.md` and `PROGRESS_LOG.md`

## Risks

1. Richer command space may not improve behavior if the monitored readout set stays too sparse.
2. It may increase runtime overhead slightly, though this should still be small relative to realistic vision.
3. FlyGym's existing hybrid controller may constrain how much behavioral richness can be expressed without moving to lower-level joint or muscle control.
4. The current WSL GPU blocker for FlyVis remains the dominant throughput issue regardless of control richness.

## Deliverables

- new multidrive production config
- richer FlyGym controller wrapper
- richer decoder and expanded encoder
- updated tests
- A/B benchmark script and output artifacts
- updated architecture and mapping docs
