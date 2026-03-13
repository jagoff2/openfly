# First Causal Descending Motor-Response Atlas

This document records the first **causal** neck-output experiment after:

- `docs/neck_output_mapping_strategy.md`
- `docs/descending_monitoring_atlas.md`

The goal here is not to guess what descending labels "should" do from their
names. The goal is to directly perturb those groups in the current
public-equivalent embodied stack and measure what the stack actually does.

This is the first concrete step toward replacing the current hand-authored
decoder with a fitted neck-output motor basis.

## Scope

This atlas is about the current stack:

- real FlyGym body runtime
- current public-equivalent whole-brain backend
- current decoder/body controller path
- no target fly
- no vision-driven splice input
- direct perturbation of selected descending groups

So the atlas is **not** claiming:

- a solved biological VNC or muscle mapping
- a final biological interpretation of each descending population

It is claiming:

- in the current embodied stack, these descending perturbations produce these
  body/controller effects

That is the right level of truth for the next decoder-fitting step.

## Implementation

Added:

- `scripts/run_descending_motor_atlas.py`
- `scripts/summarize_descending_motor_atlas.py`
- `tests/test_descending_motor_atlas.py`

The atlas script:

1. loads the current calibrated embodied branch
2. disables the target fly
3. resets the body and brain
4. directly injects current into selected descending roots
5. decodes the resulting brain activity with the current decoder
6. steps the embodied runtime
7. records body motion and command statistics

The summary script then compares every perturbation to a true no-stimulation
baseline.

## Validation

Validated locally:

```bash
python -m pytest tests/test_descending_motor_atlas.py tests/test_bridge_unit.py -q
python -m py_compile scripts/run_descending_motor_atlas.py scripts/summarize_descending_motor_atlas.py
```

Result:

- `12 passed`

## Main artifacts

Raw atlas:

- `outputs/metrics/descending_motor_atlas.csv`
- `outputs/metrics/descending_motor_atlas.json`

Summary:

- `outputs/metrics/descending_motor_atlas_summary.csv`
- `outputs/metrics/descending_motor_atlas_summary.json`

Mock smoke:

- `outputs/metrics/descending_motor_atlas_mock.csv`
- `outputs/metrics/descending_motor_atlas_mock.json`

## Conditions tested

Configuration:

- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated.yaml`

Runtime:

- `mode = flygym`
- `duration = 0.1 s`
- `stim_current = 40.0`

Baseline:

- no direct descending perturbation

Forward-oriented bilateral candidates:

- `DNg97`
- `DNp103`
- `DNp18`

Turn-oriented paired candidates:

- `DNp71`
- `DNpe040`
- `DNpe056`
- `DNpe031`

Target-conditioned / stop-turn candidates from the observational atlas:

- `DNpe016`
- `DNae002`

## Baseline matters

The new baseline row is important.

Without any direct descending stimulation, the body still shows a small passive
settling trajectory over `0.1 s`:

- `avg_forward_speed = 1.8788`
- `net_displacement = 0.0482`
- `mean_total_drive = 0.0`
- `end_yaw = 0.0021`

So any causal interpretation has to be made relative to that baseline, not
relative to zero movement.

This makes the summary script necessary, because several weak perturbations
look nonzero in absolute terms but are actually baseline-like.

## Main result

The first causal atlas cleanly splits the selected candidates into:

1. strong bilateral forward drivers
2. plausible turn drivers with mirrored effect
3. ambiguous or ineffective candidates

That is exactly what we needed before fitting a motor basis.

## Best forward candidates

From `outputs/metrics/descending_motor_atlas_summary.json`, ranked by
`delta_net_displacement_vs_baseline`:

1. `DNp103`
   - `delta_net_displacement_vs_baseline = +0.2971`
   - `delta_avg_forward_speed_vs_baseline = +3.9664`
   - `delta_mean_total_drive_vs_baseline = +1.0553`

2. `DNp18`
   - `+0.2844`
   - `+3.7944`
   - `+1.0005`

3. `DNg97`
   - `+0.2820`
   - `+3.7865`
   - `+1.0005`

Interpretation:

- these three remain the strongest current bilateral propulsion candidates in
  the present body/controller stack
- `DNp103` is the single strongest forward candidate in this first causal pass
- `DNg97` is still useful, but less clean because it carries a small asymmetry
  even under bilateral drive

## Best turn candidates

From `outputs/metrics/descending_motor_atlas_summary.json`, ranked by mirrored
sign and yaw effect:

1. `DNpe040`
   - mirrored left/right yaw sign: `true`
   - left `delta_end_yaw_vs_baseline = -0.0254`
   - right `delta_end_yaw_vs_baseline = +0.0122`
   - strong drive asymmetry on both sides

2. `DNpe056`
   - mirrored left/right yaw sign: `true`
   - left `-0.0099`
   - right `+0.0033`
   - weaker than `DNpe040`, but still directionally consistent

Interpretation:

- `DNpe040` is the strongest current turn-authority candidate in this first
  atlas
- `DNpe056` is a weaker but still plausible secondary turn component

## Important ambiguity: `DNp71`

`DNp71` is not behaving like a clean mirrored turn pair in the present stack.

It does produce:

- large drive asymmetry
- additional displacement above baseline

But it does **not** produce mirrored end-yaw sign:

- left `delta_end_yaw_vs_baseline = -0.0099`
- right `delta_end_yaw_vs_baseline = -0.0099`
- `mirror_yaw_sign = false`

Interpretation:

- `DNp71` is clearly active in the stack
- but its current body/controller effect is ambiguous
- this could reflect:
  - decoder semantics
  - controller symmetry limits
  - body-side sign loss
  - or a more complex role than a simple left/right turn driver

So `DNp71` should not be treated as a clean steering primitive yet.

## Inactive or weak candidates

### `DNpe031`

No measurable effect above baseline:

- `delta_net_displacement_vs_baseline = 0.0`
- `delta_avg_forward_speed_vs_baseline = 0.0`
- `delta_mean_total_drive_vs_baseline = 0.0`

### `DNae002`

Also effectively baseline-like in the current test:

- `delta_net_displacement_vs_baseline = 0.0`
- `delta_avg_forward_speed_vs_baseline = 0.0`
- `delta_mean_total_drive_vs_baseline = 0.0`

### `DNpe016`

Weak bilateral effect:

- `delta_net_displacement_vs_baseline = +0.0253`
- `delta_avg_forward_speed_vs_baseline = +0.8621`
- `delta_mean_total_drive_vs_baseline = +0.1848`

Interpretation:

- `DNpe016` may still be relevant as a weak gate or context signal
- but it is not a primary locomotor driver in the current stack
- `DNae002` did not show useful causal effect in this first pass

## What this means for the next decoder

This first causal atlas now gives us a cleaner starting point for a fitted
motor basis:

### Current forward basis candidates

- `DNp103`
- `DNp18`
- `DNg97`

### Current turn basis candidates

- `DNpe040`
- `DNpe056`

### Current ambiguous / hold-out candidates

- `DNp71`
- `DNpe016`
- `DNae002`
- `DNpe031`

The correct next move is **not** more name-based guesswork.

The correct next move is:

1. treat the strong causal groups as the seed motor basis
2. fit their contribution into the controller-facing latent space
3. keep the ambiguous groups available as optional residual terms

## Honest limitations

This atlas is still limited by the current stack:

- only `0.1 s` perturbation windows
- current decoder/body controller semantics
- no explicit VNC or muscle layer
- no direct leg-phase or adhesion-state summary yet

So this is a strong first causal step, but not the final motor mapping.

## Conclusion

The project now has:

- a broad observational neck-output atlas
- a first causal descending motor-response atlas

That is enough to begin `T094`:

- derive a fitted neck-output motor basis
- replace the current hand-authored multidrive mapping with one informed by
  measured causal structure
