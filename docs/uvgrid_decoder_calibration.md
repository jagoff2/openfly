## UV-Grid Decoder Calibration

This document records `T084`:

- calibrate the embodied decoder / downstream gains specifically for the UV-grid descending branch

The starting point was:

- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout.yaml`

That branch had already shown:

- brain-driven movement under matched `zero_brain`
- but weaker target-bearing tracking and weaker target modulation than the simpler axis1d descending branch

So this task treated the splice as fixed and calibrated only the embodied decoder / downstream gains.

## Method

### 1. Offline decoder replay sweep

A reproducible replay sweep was added:

- `scripts/run_uvgrid_decoder_calibration.py`

It replays the saved UV-grid target and no-target logs while sweeping decoder-only parameters:

- `signal_smoothing_alpha`
- `forward_gain`
- `turn_gain`
- `population_forward_weight`
- `population_turn_weight`
- `forward_asymmetry_turn_gain`

Artifacts:

- `outputs/metrics/uvgrid_decoder_calibration.csv`
- `outputs/metrics/uvgrid_decoder_calibration.json`
- `outputs/metrics/uvgrid_decoder_calibration_best.json`

Best replay candidate:

- `signal_smoothing_alpha = 0.06`
- `forward_gain = 1.2`
- `turn_gain = 0.65`
- `population_forward_weight = 1.0`
- `population_turn_weight = 0.75`
- `forward_asymmetry_turn_gain = 0.3`

Compared with the old UV-grid decoder:

- old:
  - `signal_smoothing_alpha = 0.12`
  - `forward_gain = 1.0`
  - `turn_gain = 0.45`
  - `forward_asymmetry_turn_gain = 0.0`
- new:
  - lower smoothing
  - stronger forward output gain
  - stronger turn output gain
  - nonzero forward-asymmetry steering term

### 2. Embodied validation

Dedicated calibrated configs were added:

- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_zero_brain.yaml`

Matched embodied artifacts:

- target + real brain:
  - `outputs/requested_2s_splice_uvgrid_descending_calibrated_target/demos/flygym-demo-20260311-071452.mp4`
- no target + real brain:
  - `outputs/requested_2s_splice_uvgrid_descending_calibrated_no_target/demos/flygym-demo-20260311-073028.mp4`
- target + zero brain:
  - `outputs/requested_2s_splice_uvgrid_descending_calibrated_zero_brain/demos/flygym-demo-20260311-074301.mp4`

Matched summaries:

- `outputs/metrics/descending_uvgrid_calibrated_visual_drive_validation.json`
- `outputs/metrics/descending_uvgrid_calibration_comparison.json`

## Main result

The calibrated UV-grid branch now beats both:

- the old UV-grid branch
- the old axis1d descending branch

on the main target-run embodied metrics.

### Target run comparison

#### Old UV-grid

- `avg_forward_speed = 3.6651577683842382`
- `net_displacement = 4.2833517602036055`
- `corr_drive_diff_vs_target_bearing = 0.459042453179978`
- `steer_sign_match_rate = 0.6526639344262295`

#### Axis1d descending baseline

- `avg_forward_speed = 4.326325286840003`
- `net_displacement = 4.943851959931002`
- `corr_drive_diff_vs_target_bearing = 0.7228049533574713`
- `steer_sign_match_rate = 0.7476828012358393`

#### Calibrated UV-grid

- `avg_forward_speed = 4.924057440740504`
- `net_displacement = 5.758268822981613`
- `corr_drive_diff_vs_target_bearing = 0.8809889705757767`
- `steer_sign_match_rate = 0.8877551020408163`

### Improvement over old UV-grid

- forward speed: `+1.2588996723562658`
- net displacement: `+1.4749170627780073`
- target-bearing correlation: `+0.42194651739579875`
- steer-sign match: `+0.23509116761458682`

### Improvement over axis1d

- forward speed: `+0.5977321539005009`
- net displacement: `+0.814416863050611`
- target-bearing correlation: `+0.15818401721830544`
- steer-sign match: `+0.140072300804977`

## Control result

The calibrated `zero_brain` run remains unchanged in substance:

- `nonzero_command_cycles = 0`
- `net_displacement = 0.011823383234191902`
- `displacement_efficiency = 0.0320475393946615`

So the gain did not come from a reintroduced fallback.

## Target modulation

Within the calibrated UV-grid branch:

- target run:
  - `avg_forward_speed = 4.924057440740504`
  - `mean_total_drive = 0.495721255471884`
  - `mean_abs_drive_diff = 0.23135474418690488`
- no-target run:
  - `avg_forward_speed = 3.907028380353221`
  - `mean_total_drive = 0.4424820589556034`
  - `mean_abs_drive_diff = 0.10450359625365861`

So the calibrated branch restores strong target modulation:

- forward speed: about `+26.03%`
- mean total drive: about `+12.03%`
- steering asymmetry: about `+121.38%`

## Interpretation

This calibration result changes the embodied picture.

The earlier body-free conclusion still holds:

- the per-cell-type UV-grid splice fixed a real boundary problem

But the embodied failure was not inherent to the UV-grid splice itself.

It was largely a decoder/downstream calibration mismatch:

- too much smoothing
- not enough output gain
- no asymmetry-to-steering term tuned for the UV-grid signal statistics

With those adjusted, the UV-grid branch becomes the current strongest embodied branch in the repo.

## Current best embodied branch

The strongest current embodied config is now:

- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated.yaml`

It remains subject to the same big-picture limits:

- the motor interface is still a descending-population-to-two-drive abstraction
- the no-target branch still moves substantially, so locomotion is not pure target pursuit
- this is still not a full biological VNC / muscle pathway
