## Descending UV-Grid Embodied Validation

Superseded result note:

- this document records the first embodied UV-grid attempt before decoder-specific calibration
- the calibrated follow-up is now in:
  - `docs/uvgrid_decoder_calibration.md`
- the uncalibrated conclusion here remains historically correct, but it is no longer the repo's current best UV-grid result

This document records the embodied follow-up for:

- `T082`
- `T083`

Goal:

- test the new per-cell-type UV-grid splice in the embodied descending-only branch
- compare it directly against the current axis1d descending baseline

This branch keeps the widened descending-only decoder and changes only the splice input side.

Tested config family:

- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_no_target.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_zero_brain.yaml`

These configs use:

- `spatial_mode: uv_grid`
- `spatial_u_bins: 2`
- `spatial_v_bins: 2`
- `spatial_flip_v: true`
- `spatial_mirror_u_by_side: true`
- `spatial_cell_type_transforms_path: outputs/metrics/splice_celltype_alignment_recommended.json`

They do not use:

- `P9` prosthetic context
- decoder idle locomotion fallback
- optic-lobe-as-motor shortcuts
- body-side locomotion fallback

## Matched runs

### 1. Target + real brain

- config: `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout.yaml`
- video: `outputs/requested_2s_splice_uvgrid_descending_target/demos/flygym-demo-20260311-062430.mp4`
- metrics: `outputs/requested_2s_splice_uvgrid_descending_target/metrics/flygym-demo-20260311-062430.csv`
- benchmark: `outputs/benchmarks/fullstack_splice_uvgrid_descending_target_2s.csv`

### 2. No target + real brain

- config: `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_no_target.yaml`
- video: `outputs/requested_2s_splice_uvgrid_descending_no_target/demos/flygym-demo-20260311-063926.mp4`
- metrics: `outputs/requested_2s_splice_uvgrid_descending_no_target/metrics/flygym-demo-20260311-063926.csv`
- benchmark: `outputs/benchmarks/fullstack_splice_uvgrid_descending_no_target_2s.csv`

### 3. Target + zero brain

- config: `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_zero_brain.yaml`
- video: `outputs/requested_2s_splice_uvgrid_descending_zero_brain/demos/flygym-demo-20260311-065432.mp4`
- metrics: `outputs/requested_2s_splice_uvgrid_descending_zero_brain/metrics/flygym-demo-20260311-065432.csv`
- benchmark: `outputs/benchmarks/fullstack_splice_uvgrid_descending_zero_brain_2s.csv`

Summary artifacts:

- `outputs/metrics/descending_uvgrid_visual_drive_validation.csv`
- `outputs/metrics/descending_uvgrid_visual_drive_validation.json`
- `outputs/metrics/descending_uvgrid_vs_axis1d_comparison.csv`
- `outputs/metrics/descending_uvgrid_vs_axis1d_comparison.json`

## Main results

### A. The branch is still brain-driven

The `zero_brain` ablation stays at:

- `nonzero_command_cycles = 0`
- `net_displacement = 0.011823383234191902`
- `displacement_efficiency = 0.0320475393946615`

So the UV-grid embodied branch still has no hidden locomotion fallback.

### B. The per-cell-type UV-grid splice did not improve embodied pursuit

Compared against the current axis1d descending baseline:

#### Target run

- axis1d:
  - `avg_forward_speed = 4.326325286840003`
  - `net_displacement = 4.943851959931002`
  - `corr_drive_diff_vs_target_bearing = 0.7228049533574713`
  - `steer_sign_match_rate = 0.7476828012358393`
- UV-grid:
  - `avg_forward_speed = 3.6651577683842382`
  - `net_displacement = 4.2833517602036055`
  - `corr_drive_diff_vs_target_bearing = 0.459042453179978`
  - `steer_sign_match_rate = 0.6526639344262295`

Delta:

- forward speed: `-0.6611675184557648`
- net displacement: `-0.6605001997273963`
- target-bearing correlation: `-0.2637625001774933`
- steer sign match: `-0.0950188668096098`

#### No-target run

- axis1d:
  - `avg_forward_speed = 3.6971077463080686`
  - `net_displacement = 4.938367142047433`
- UV-grid:
  - `avg_forward_speed = 3.6750986385881887`
  - `net_displacement = 4.446223025146955`

This is close, but still slightly worse than axis1d.

### C. Target modulation is weaker than in the axis1d branch

Within the UV-grid branch itself:

- target run:
  - `mean_total_drive = 0.4441768885740195`
  - `mean_abs_drive_diff = 0.1077707909923879`
  - `avg_forward_speed = 3.6651577683842382`
- no-target run:
  - `mean_total_drive = 0.4302983772685672`
  - `mean_abs_drive_diff = 0.10259877290385935`
  - `avg_forward_speed = 3.6750986385881887`

So in this embodied UV-grid branch:

- total drive is only slightly higher with the target
- steering asymmetry is only slightly higher with the target
- forward speed is slightly lower with the target than without it

That is much weaker target modulation than the axis1d branch showed.

## Interpretation

The body-free per-cell-type UV-grid splice fixed the downstream sign problem at the calibration boundary.

That improvement did not transfer into stronger embodied target pursuit.

The current evidence therefore supports:

- the body-free splice alignment problem is materially improved
- the embodied descending-only branch remains brain-driven
- but the per-cell-type UV-grid splice is not yet a better embodied production path than the simpler axis1d descending splice

The strongest current embodied branch therefore remains:

- `configs/flygym_realistic_vision_splice_axis1d_descending_readout.yaml`

## Historical bottom line

`T082` / `T083` answer:

- yes, the new per-cell-type UV-grid splice can be tested cleanly in embodiment
- no, it does not currently outperform the axis1d descending baseline
- zero-brain still cleanly ablates movement
- the per-cell-type UV-grid splice should remain an experimental branch until its embodied target modulation exceeds the axis1d baseline
