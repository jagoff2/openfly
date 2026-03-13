# First Fitted Neck-Output Motor Basis

This document records the start of `T094`:

- use the observational + causal neck-output atlas
- derive a first fitted motor basis
- replace the current hand-authored multidrive input set with that basis

This is not the final motor decoder. It is the first data-driven version.

## Inputs used

Observational atlas:

- `outputs/metrics/descending_monitor_neck_output_atlas.json`

Causal atlas:

- `outputs/metrics/descending_motor_atlas_summary.json`

These are the two evidence sources the repo now has for the output side:

- what groups correlate with pursuit-like behavior
- what groups causally move the current body/controller stack

## Implementation

Added:

- `scripts/fit_neck_output_motor_basis.py`
- `outputs/metrics/neck_output_motor_basis.json`

Decoder support added:

- `src/bridge/decoder.py`

New config support:

- `decoder.motor_basis_json`

New fitted-basis configs:

- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_no_target.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_zero_brain.yaml`

## Fitted basis produced

From `outputs/metrics/neck_output_motor_basis.json`:

### Forward group weights

- `DNp103 = 1.0`
- `DNp18 = 0.9501`
- `DNg97 = 0.9483`
- `DNpe016 = 0.1553`

### Turn group weights

- `DNpe040 = 1.0`
- `DNpe056 = 0.3910`

### Explicit exclusions

- ambiguous turn role:
  - `DNp71`
- inactive in first causal pass:
  - `DNpe031`
  - `DNae002`
- weak gate-like only:
  - `DNpe016`

So the current first fitted basis says:

- propulsion is mainly the `DNp103` / `DNp18` / `DNg97` subspace
- turning is mainly the `DNpe040` / `DNpe056` subspace
- weak or ambiguous groups stay out of the main turn basis until the next pass

## Validation

Validated locally:

```bash
python -m pytest tests/test_descending_motor_atlas.py tests/test_bridge_unit.py -q
python -m py_compile scripts/fit_neck_output_motor_basis.py
python scripts/fit_neck_output_motor_basis.py --observational-json outputs/metrics/descending_monitor_neck_output_atlas.json --causal-json outputs/metrics/descending_motor_atlas_summary.json --output-json outputs/metrics/neck_output_motor_basis.json
```

Result:

- `13 passed`

## First smoke run

Local mock smoke:

- `outputs/requested_0p05s_multidrive_fitted_basis_mock/mock-demo-20260311-145811`

This confirms the new basis file and decoder path boot cleanly.

## First real WSL pilot

Ran:

- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis.yaml`
- `mode = flygym`
- `duration = 0.1 s`

Artifacts:

- benchmark:
  - `outputs/benchmarks/fullstack_splice_uvgrid_multidrive_fitted_basis_target_0p1s.csv`
- plot:
  - `outputs/plots/fullstack_splice_uvgrid_multidrive_fitted_basis_target_0p1s.png`
- demo:
  - `outputs/requested_0p1s_splice_uvgrid_multidrive_fitted_basis_target/demos/flygym-demo-20260311-145836.mp4`
- metrics:
  - `outputs/requested_0p1s_splice_uvgrid_multidrive_fitted_basis_target/metrics/flygym-demo-20260311-145836.csv`

## Preliminary comparison vs the old multidrive target pilot

Old hand-authored multidrive `0.1 s` target pilot:

- `net_displacement = 0.0584`
- `displacement_efficiency = 0.1919`
- `avg_forward_speed = 3.1059`

New fitted-basis multidrive `0.1 s` target pilot:

- `net_displacement = 0.0802`
- `displacement_efficiency = 0.3202`
- `avg_forward_speed = 2.5563`

Interpretation:

- the new fitted basis is already changing the character of the motion
- it is not simply "more forward speed"
- it appears to trade raw speed for more net displacement and better
  displacement efficiency over the short pilot window

That is a plausible direction for a more purposeful embodied motor code, but it
is still only a pilot.

## Matched `0.1 s` pilot controls

Additional WSL pilot runs now exist for:

- no target:
  - `outputs/requested_0p1s_splice_uvgrid_multidrive_fitted_basis_no_target/demos/flygym-demo-20260311-150139.mp4`
- zero brain:
  - `outputs/requested_0p1s_splice_uvgrid_multidrive_fitted_basis_zero_brain/demos/flygym-demo-20260311-150253.mp4`

Summary:

- `outputs/metrics/neck_output_motor_basis_pilot_summary.json`

Pilot comparison:

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

Interpretation:

- the fitted-basis branch is still brain-driven in the short pilot window:
  - target minus zero-brain net displacement `= +0.0459`
  - target minus zero-brain forward speed `= +0.6985`
- but target-vs-no-target separation is still weak over `0.1 s`:
  - target minus no-target net displacement `= +0.0032`
  - target minus no-target forward speed `= +0.3215`
  - target minus no-target displacement efficiency `= -0.0316`

So the new basis is promising, but not yet strong enough to claim a clear
target-conditioned improvement.

## What is not done yet

`T094` is not complete yet.

Still missing:

- longer-window matched validation beyond this document's first fitted-basis
  pass
- a more decisive target-vs-no-target separation
- promotion to the main embodied branch only if that separation survives the
  standard ablation criteria

Without those, the repo cannot yet claim that the fitted basis is better than
the hand-authored multidrive branch under the same ablation standards.

## `1.0 s` matched validation

That longer-window validation has now been run once for the fitted-basis branch.

Artifacts:

- target:
  - `outputs/requested_1s_splice_uvgrid_multidrive_fitted_basis_target/demos/flygym-demo-20260311-150809.mp4`
- no target:
  - `outputs/requested_1s_splice_uvgrid_multidrive_fitted_basis_no_target/demos/flygym-demo-20260311-151736.mp4`
- zero brain:
  - `outputs/requested_1s_splice_uvgrid_multidrive_fitted_basis_zero_brain/demos/flygym-demo-20260311-152440.mp4`
- summary:
  - `outputs/metrics/neck_output_motor_basis_1s_summary.json`

### `1.0 s` result

Target:

- `avg_forward_speed = 5.4864`
- `net_displacement = 3.8608`
- `displacement_efficiency = 0.7051`

No target:

- `avg_forward_speed = 6.5676`
- `net_displacement = 4.6747`
- `displacement_efficiency = 0.7132`

Zero brain:

- `avg_forward_speed = 0.6968`
- `net_displacement = 0.0153`
- `displacement_efficiency = 0.0219`

### Interpretation

The fitted-basis branch remains clearly brain-driven:

- target minus zero-brain net displacement `= +3.8455`
- target minus zero-brain forward speed `= +4.7897`
- target minus zero-brain displacement efficiency `= +0.6832`

But the longer-window target-vs-no-target result is not yet acceptable:

- target minus no-target net displacement `= -0.8140`
- target minus no-target forward speed `= -1.0812`
- target minus no-target displacement efficiency `= -0.0081`

So the first fitted basis solves the output mapping problem only partially:

- it gives a real brain-driven branch
- but it does not yet improve target-conditioned behavior over free locomotion

That means the next iteration is not "derive a basis from scratch again."

It is more specifically:

- refine the basis so target-conditioned groups influence motor state more
  selectively than they do now
- likely by revisiting:
  - weak gate/context groups like `DNpe016`
  - ambiguous groups like `DNp71`
  - and the mapping from the fitted basis into the controller-facing latents

## Current conclusion

The project now has a first fitted neck-output motor basis, and it is wired
into the decoder.

That basis is grounded by:

- the observational neck-output atlas
- the causal descending motor-response atlas

The next step is straightforward:

- run matched embodied controls on the fitted-basis branch
- then decide whether it is strong enough to replace the current hand-authored
  multidrive mapping
## Context-gated refinement scaffold

The decoder already had context-channel support before this refinement pass:

- `forward_context_cell_types`
- `forward_context_blend`
- `turn_context_cell_types`
- `turn_context_boost`

The contextual fitted-basis branch is the current output-side refinement path:

- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual_no_target.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual_zero_brain.yaml`

Current wiring:

- forward context/boost groups: `DNae002` plus `DNpe016`
- turn-context support groups: `DNpe040` plus `DNpe056`
- `turn_context_mode = aligned_asymmetry`, so contextual support only amplifies the same turn direction already selected by the canonical steering readout
- additional turn-priority latent gains to preserve reorientation when forward drive is suppressed

Current rationale:

- `DNae002` is one of the earliest target-biased monitored groups in the calibrated embodied branch, but it is weak as a direct causal propulsion primitive, so it fits better as a target-conditioned locomotor boost signal than as a primary drive basis weight.
- `DNpe016` remains a sustained target-conditioned bilateral group with weak direct motor leverage, so it complements `DNae002` as a slower forward-context component instead of a primary propulsion neuron class.
- `DNpe040` and `DNpe056` are still exploratory rather than fully literature-validated walking steering classes, but in the current repo they are the cleanest causal turn-support population; using their asymmetry as a multiplicative support signal is safer than treating them as replacement direct steering commands.
- `DNp71` stays monitored, but the first causal atlas did not show a clean mirrored left-right steering phenotype from it in the present body/controller stack.
- The direct steering core remains `DNa01` / `DNa02`. The contextual branch is now explicitly layered around that canonical steering readout rather than substituting for it.

Primary-source constraints folded into this refinement:

- Rayshubskiy et al., eLife 2025 supports keeping direct walking steering on lateralized descending signals such as `DNa01` and `DNa02`, with distinct sustained versus transient steering roles.
- Braun et al., Cell 2024 argues that walking steering is assembled from specific steering gestures rather than generic locomotor activation, which is another reason to keep the canonical steering pair privileged.
- Namiki et al., eLife 2018 supports treating many descending neurons as locomotor activators or modulators rather than full motor-pattern encoders.
- Lappalainen et al., Nature 2024 links `DNg97` / `oDN1` to walking promotion, which is one reason the repo keeps `DNg97` in the main forward motor basis instead of reusing it as a separate context gate.
- Ache et al., Nature 2019 links `DNb01` to visually elicited flight turns, which is why `DNb01` is not being promoted as the default walking context gate.

Unit validation:

- `python -m pytest tests/test_bridge_unit.py tests/test_closed_loop_smoke.py -q`
- Result: `26 passed`

Embodied validation status:

- A separate long WSL embodied benchmark was already active when this session reached the next heavy validation step.
- No additional contextual WSL run was allowed to continue in parallel.
- Resume the matched `target` / `no_target` / `zero_brain` contextual pilots only after the current WSL runtime is clear.
