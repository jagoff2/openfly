## Hybrid Motor-Latent Decoder Validation

This document records the first embodied validation of a more biologically
plausible motor interface than the current two-drive decoder.

The starting point was the current strongest embodied branch:

- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated.yaml`

That branch already has:

- real FlyVis realistic vision
- grounded per-cell-type UV-grid splice
- real whole-brain recurrent backend
- widened descending/efferent readout
- matched `target`, `no_target`, and `zero_brain` evidence

But it still compresses all descending output to:

- `left_drive`
- `right_drive`

The purpose of this task was to replace that output bottleneck with a richer
controller-facing abstraction while keeping the visual splice fixed.

## Implemented motor interface

### 1. New command type

Added:

- `src/body/interfaces.py`

New command:

- `HybridDriveCommand`

Fields:

- `left_amp`
- `right_amp`
- `left_freq_scale`
- `right_freq_scale`
- `retraction_gain`
- `stumbling_gain`
- `reverse_gate`

For compatibility and logging, the command still carries:

- `left_drive`
- `right_drive`

as a projected legacy view.

### 2. New FlyGym-side controller

Added:

- `src/body/connectome_turning_fly.py`

This controller subclasses the realistic-vision fly and maps the new motor
latents into the existing `HybridTurningFly` internals:

- left/right CPG amplitude
- left/right CPG frequency scaling
- retraction correction gain
- stumbling correction gain
- reverse gating via CPG frequency sign

Important:

- zero motor latents still produce the planted neutral stance
- no hidden locomotor fallback was reintroduced

### 3. Runtime plumbing

Updated:

- `src/body/flygym_runtime.py`
- `src/runtime/closed_loop.py`
- `src/body/fast_realistic_vision_fly.py`

The runtime now supports:

- `runtime.control_mode: hybrid_multidrive`

and the JSONL logs now serialize the richer command fields directly.

### 4. Decoder branch

Updated:

- `src/bridge/decoder.py`

New mode:

- `decoder.command_mode: hybrid_multidrive`

This keeps the same descending readout groups, but maps them into the richer
motor latents instead of directly driving only `left_drive` / `right_drive`.

### 5. Tests

Added / updated:

- `tests/test_bridge_unit.py`
- `tests/test_closed_loop_smoke.py`

Validated locally:

```bash
python -m pytest tests/test_bridge_unit.py tests/test_closed_loop_smoke.py tests/test_realistic_vision_path.py -q
```

Result:

- `22 passed`

## Embodied configs

Added:

- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_no_target.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_zero_brain.yaml`

## Matched embodied runs

### Target + real brain

- `outputs/requested_2s_splice_uvgrid_multidrive_target/flygym-demo-20260311-115625/demo.mp4`
- `outputs/requested_2s_splice_uvgrid_multidrive_target/flygym-demo-20260311-115625/run.jsonl`
- `outputs/requested_2s_splice_uvgrid_multidrive_target/flygym-demo-20260311-115625/metrics.csv`

### No target + real brain

- `outputs/requested_2s_splice_uvgrid_multidrive_no_target/flygym-demo-20260311-121158/demo.mp4`
- `outputs/requested_2s_splice_uvgrid_multidrive_no_target/flygym-demo-20260311-121158/run.jsonl`
- `outputs/requested_2s_splice_uvgrid_multidrive_no_target/flygym-demo-20260311-121158/metrics.csv`

### Zero brain

- `outputs/requested_2s_splice_uvgrid_multidrive_zero_brain/flygym-demo-20260311-122402/demo.mp4`
- `outputs/requested_2s_splice_uvgrid_multidrive_zero_brain/flygym-demo-20260311-122402/run.jsonl`
- `outputs/requested_2s_splice_uvgrid_multidrive_zero_brain/flygym-demo-20260311-122402/metrics.csv`

Summaries:

- `outputs/metrics/descending_uvgrid_multidrive_visual_drive_validation.csv`
- `outputs/metrics/descending_uvgrid_multidrive_visual_drive_validation.json`
- `outputs/metrics/descending_uvgrid_multidrive_comparison.csv`
- `outputs/metrics/descending_uvgrid_multidrive_comparison.json`

## Main result

The hybrid motor-latent branch is real and brain-driven, but the first
calibration does **not** beat the current calibrated two-drive UV-grid branch
overall.

### Positive result

The branch is still genuinely brain-dependent:

- `zero_brain nonzero_command_cycles = 0`
- `zero_brain net_displacement = 0.016680726595983866`

So the richer controller did not reintroduce hidden locomotion.

### Tradeoff versus the current best two-drive branch

From `outputs/metrics/descending_uvgrid_multidrive_comparison.json`:

#### Target run

Current best two-drive baseline:

- `avg_forward_speed = 4.924057440740504`
- `net_displacement = 5.758268822981613`
- `corr_drive_diff_vs_target_bearing = 0.8809889705757767`
- `steer_sign_match_rate = 0.8877551020408163`

Hybrid motor-latent branch:

- `avg_forward_speed = 4.415297537302404`
- `net_displacement = 5.546298802012086`
- `corr_drive_diff_vs_target_bearing = 0.848057435148708`
- `steer_sign_match_rate = 0.9031281533804238`

So the first motor-latent branch:

- improves steer-sign match slightly
- improves displacement efficiency slightly
- but reduces target-run speed
- reduces target-run displacement
- reduces target-bearing correlation

#### No-target run

This is the main failure mode of the first motor-latent calibration.

Two-drive baseline:

- `avg_forward_speed = 3.907028380353221`
- `net_displacement = 5.29025073410087`

Hybrid motor-latent branch:

- `avg_forward_speed = 4.650604531957434`
- `net_displacement = 6.751026944282977`

That means the richer controller currently strengthens generic visually driven
locomotion more than it strengthens target-conditioned locomotion.

## Interpretation

This is still a useful result.

What it shows:

1. The richer controller interface is technically sound.
- It runs end-to-end in the embodied stack.
- It preserves the `zero_brain` ablation.

2. The output bottleneck is indeed separable from the visual splice.
- We changed the output abstraction while keeping the visual splice fixed.

3. The first motor-latent calibration is not yet the new production branch.
- It is more plausible anatomically and controller-wise.
- But it is not yet stronger behaviorally than the current calibrated two-drive UV-grid branch.

## Current decision

Keep the current production reference branch as:

- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated.yaml`

Keep the new motor-latent branch as:

- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive.yaml`

and treat it as the next experimental path, not the headline result.

## Next step

The next logical follow-up is to calibrate the motor-latent branch specifically
for:

- stronger target-vs-no-target modulation
- reduced generic no-target forward drive
- preserved or improved target-bearing steering correlation

without giving up the richer, more plausible controller-side semantics.
