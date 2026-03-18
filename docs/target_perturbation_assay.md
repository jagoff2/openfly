# Target Perturbation Assay

## Purpose

The repo now includes a grounded perturbation assay for two real adult-fly
visual behaviors from the canonical target set:

- refixation after a target jump
- bounded persistence / re-stabilization after brief target disappearance

This replaces vague "reacquisition" language with explicit runtime-side visual
stimulus perturbations and explicit behavior metrics.

## Implementation

Runtime-side target perturbations are now implemented in:

- [target_schedule.py](/G:/flysim/src/body/target_schedule.py)
- [flygym_runtime.py](/G:/flysim/src/body/flygym_runtime.py)
- [closed_loop.py](/G:/flysim/src/runtime/closed_loop.py)

The body runtime now accepts `body.target_schedule`, which is applied entirely
inside the visual stimulus path. No privileged target metadata is used for
control.

Supported events:

- `jump`
  - instant target phase change at `time_s`
- `hide`
  - target disappearance from `start_s` for `duration_s`

Behavior analysis now reads those event markers from `target_state` and reports
perturbation-specific metrics in:

- [behavior_metrics.py](/G:/flysim/src/analysis/behavior_metrics.py)

New metric block:

- `target_perturbation_jump_event_count`
- `target_perturbation_first_jump_time_s`
- `target_perturbation_jump_turn_alignment_fraction_active`
- `target_perturbation_jump_turn_bearing_corr`
- `target_perturbation_jump_refixation_latency_s`
- `target_perturbation_jump_refixation_fraction_20deg`
- `target_perturbation_jump_bearing_recovery_fraction_2s`
- `target_perturbation_removal_event_count`
- `target_perturbation_first_removal_time_s`
- `target_perturbation_removal_persistence_duration_s`
- `target_perturbation_removal_persistence_turn_alignment_fraction`
- `target_perturbation_removal_mean_abs_bearing_rad`
- `target_perturbation_removal_post_return_refixation_latency_s`
- `target_perturbation_removal_post_return_fixation_fraction_20deg`

## Runnable Configs

- [target_jump](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_turn_voltage_promoted_visual_core_target_jump.yaml)
- [target_removed_brief](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_turn_voltage_promoted_visual_core_target_removed_brief.yaml)

Both are built on the current best bounded steering-promotion branch.

## Validation

Focused local validation:

- `python -m pytest tests/test_target_schedule.py tests/test_behavior_metrics.py tests/test_closed_loop_smoke.py -q`
  - `26 passed`
- `python -m py_compile src/body/target_schedule.py src/body/flygym_runtime.py src/analysis/behavior_metrics.py src/runtime/closed_loop.py`
  - passed

## First Real `2.0 s` Runs

### Jump Assay

Artifacts:

- [summary.json](/G:/flysim/outputs/requested_2s_turn_voltage_promoted_visual_core_target_jump/flygym-demo-20260314-203328/summary.json)
- [demo.mp4](/G:/flysim/outputs/requested_2s_turn_voltage_promoted_visual_core_target_jump/flygym-demo-20260314-203328/demo.mp4)
- [activation_side_by_side.mp4](/G:/flysim/outputs/requested_2s_turn_voltage_promoted_visual_core_target_jump/flygym-demo-20260314-203328/activation_side_by_side.mp4)
- [activation_overview.png](/G:/flysim/outputs/requested_2s_turn_voltage_promoted_visual_core_target_jump/flygym-demo-20260314-203328/activation_overview.png)
- [benchmark csv](/G:/flysim/outputs/benchmarks/fullstack_turn_voltage_promoted_visual_core_target_jump_2s.csv)

Key results:

- `jump_event_count = 1`
- `first_jump_time_s = 0.752`
- `jump_turn_alignment_fraction_active = 0.927`
- `jump_turn_bearing_corr = 0.401`
- `jump_refixation_latency_s = null`
- `jump_refixation_fraction_20deg = 0.0`
- `jump_bearing_recovery_fraction_2s = -1.562`

Interpretation:

- the branch produces strong target-signed corrective turning immediately after
  the jump
- but it does not complete frontal refixation within the `2.0 s` window
- this is a real failure, and it is now measured directly rather than inferred
  from the older continuous-target drift story

### Brief Removal Assay

Artifacts:

- [summary.json](/G:/flysim/outputs/requested_2s_turn_voltage_promoted_visual_core_target_removed_brief/flygym-demo-20260314-204945/summary.json)
- [demo.mp4](/G:/flysim/outputs/requested_2s_turn_voltage_promoted_visual_core_target_removed_brief/flygym-demo-20260314-204945/demo.mp4)
- [activation_side_by_side.mp4](/G:/flysim/outputs/requested_2s_turn_voltage_promoted_visual_core_target_removed_brief/flygym-demo-20260314-204945/activation_side_by_side.mp4)
- [activation_overview.png](/G:/flysim/outputs/requested_2s_turn_voltage_promoted_visual_core_target_removed_brief/flygym-demo-20260314-204945/activation_overview.png)
- [benchmark csv](/G:/flysim/outputs/benchmarks/fullstack_turn_voltage_promoted_visual_core_target_removed_brief_2s.csv)

Key results:

- `removal_event_count = 1`
- `first_removal_time_s = 0.752`
- `removal_persistence_duration_s = 0.300`
- `removal_persistence_turn_alignment_fraction = 0.101`
- `removal_mean_abs_bearing_rad = 0.199`
- `removal_post_return_refixation_latency_s = 0.0`
- `removal_post_return_fixation_fraction_20deg = 0.168`

Interpretation:

- hidden-target persistence is weak in turn-sign terms on the current branch
- but the branch re-stabilizes immediately when the target returns
- that means the branch currently behaves more like a visually contingent
  re-stabilizer than a persistent internal target tracker

## Honest Status

This assay is the right next step and it is now real and reproducible.

It does **not** mean the branch has solved perturbation refixation or target
memory:

- jump refixation currently fails
- brief disappearance currently shows weak hidden persistence
- matched `no_target` / `zero_brain` perturbation controls still need to be run
  before this should be treated as a parity claim branch

The main value of this step is that the repo now measures the right problem
directly.

## Update: 2026-03-14 corrected turn-voltage sign branch

The first correction attempt after the baseline assays was a failure.

- failed refixation-gate jump run:
  - [summary.json](/G:/flysim/outputs/requested_2s_turn_voltage_promoted_visual_core_target_jump_refixation_gate/flygym-demo-20260314-220744/summary.json)

That branch proved a real controller bug:

- the refixation gate stayed active for nearly the whole run
- it pushed the controller toward a stronger one-sided left bias
- it did not improve jump-specific frontal refixation

The actual deeper bug was then found in the turn-voltage library builder:

- [turn_voltage_library.py](/G:/flysim/src/analysis/turn_voltage_library.py)
- [bias_correct_turn_voltage_signal_library.py](/G:/flysim/scripts/bias_correct_turn_voltage_signal_library.py)

The builder was still assigning turn-weight signs using an older convention
that opposed body-frame target bearing, while the current behavior metrics and
controller semantics treat same-sign turn/bearing as aligned. That stale sign
convention made the shadow steering signal fight the live turn path.

The corrected branch now does three things:

- uses a jump-aware monitored shadow library:
  - [jump_turn_voltage_signal_library_top8_mixed_bias_corrected.json](/G:/flysim/outputs/metrics/jump_turn_voltage_signal_library_top8_mixed_bias_corrected.json)
- disables the failed always-on refixation override by zeroing the refixation
  gate scales in the active configs
- raises the base shadow blend to `0.8` so the corrected shadow signal actually
  influences steering

### Corrected Jump Assay

Artifacts:

- [summary.json](/G:/flysim/outputs/requested_2s_turn_voltage_promoted_visual_core_target_jump_signfix_blend08/flygym-demo-20260314-230110/summary.json)
- [demo.mp4](/G:/flysim/outputs/requested_2s_turn_voltage_promoted_visual_core_target_jump_signfix_blend08/flygym-demo-20260314-230110/demo.mp4)
- [activation_side_by_side.mp4](/G:/flysim/outputs/requested_2s_turn_voltage_promoted_visual_core_target_jump_signfix_blend08/flygym-demo-20260314-230110/activation_side_by_side.mp4)
- [activation_overview.png](/G:/flysim/outputs/requested_2s_turn_voltage_promoted_visual_core_target_jump_signfix_blend08/flygym-demo-20260314-230110/activation_overview.png)
- [benchmark csv](/G:/flysim/outputs/benchmarks/fullstack_turn_voltage_promoted_visual_core_target_jump_signfix_blend08_2s.csv)

Key corrected results:

- `target_condition_turn_bearing_corr = 0.8745`
- `target_condition_turn_alignment_fraction_active = 0.9013`
- `target_condition_fixation_fraction_20deg = 0.011`
- `target_condition_fixation_fraction_30deg = 0.058`
- `target_condition_fixation_latency_s = 0.728`
- `jump_turn_alignment_fraction_active = 0.7419`
- `jump_turn_bearing_corr = 0.9589`
- `jump_bearing_recovery_fraction_2s = -1.3164`
- `jump_refixation_latency_s = null`
- `jump_refixation_fraction_20deg = 0.0`

Interpretation:

- this is now the best jump-target branch so far on steering correlation and
  bearing recovery
- it beats both the original jump baseline and the failed refixation-gate run
  on `jump_turn_bearing_corr`
- it also produces the first nonzero overall `20 deg` fixation fraction on the
  corrected jump branch
- but jump-specific frontal refixation still does not complete within `2.0 s`

### Corrected Brief Removal Assay

Artifacts:

- [summary.json](/G:/flysim/outputs/requested_2s_turn_voltage_promoted_visual_core_target_removed_brief_signfix_blend08/flygym-demo-20260314-231851/summary.json)
- [demo.mp4](/G:/flysim/outputs/requested_2s_turn_voltage_promoted_visual_core_target_removed_brief_signfix_blend08/flygym-demo-20260314-231851/demo.mp4)
- [activation_side_by_side.mp4](/G:/flysim/outputs/requested_2s_turn_voltage_promoted_visual_core_target_removed_brief_signfix_blend08/flygym-demo-20260314-231851/activation_side_by_side.mp4)
- [activation_overview.png](/G:/flysim/outputs/requested_2s_turn_voltage_promoted_visual_core_target_removed_brief_signfix_blend08/flygym-demo-20260314-231851/activation_overview.png)
- [benchmark csv](/G:/flysim/outputs/benchmarks/fullstack_turn_voltage_promoted_visual_core_target_removed_brief_signfix_blend08_2s.csv)

Key corrected results:

- `target_condition_turn_bearing_corr = 0.9176`
- `target_condition_turn_alignment_fraction_active = 0.9222`
- `removal_persistence_duration_s = 0.3000`
- `removal_persistence_turn_alignment_fraction = 0.9762`
- `removal_mean_abs_bearing_rad = 0.1546`
- `removal_post_return_refixation_latency_s = 0.0`
- `removal_post_return_fixation_fraction_20deg = 0.0232`

Interpretation:

- hidden-target persistence improved materially
- the old branch had `removal_persistence_turn_alignment_fraction = 0.1014`
- the corrected branch now keeps turn alignment through the hidden interval
  instead of collapsing almost immediately
- post-return re-stabilization remains immediate

### Corrected Controls

Corrected `no_target` control:

- [summary.json](/G:/flysim/outputs/requested_2s_turn_voltage_promoted_visual_core_no_target_signfix_blend08/flygym-demo-20260314-233644/summary.json)
- `mean_turn_drive = 0.0010`
- `mean_abs_turn_drive = 0.0405`
- `right_turn_dominant_fraction = 0.549`
- `left_turn_dominant_fraction = 0.448`

Interpretation:

- the corrected branch remains awake and locomotor-rich without a target
- the stronger shadow blend does not reintroduce a one-sided exploratory turn
  bias

Corrected `zero_brain` control:

- [summary.json](/G:/flysim/outputs/requested_2s_turn_voltage_promoted_visual_core_zero_brain_signfix_blend08/flygym-demo-20260314-235119/summary.json)
- `controller_summary_forward_nonzero_fraction = 0.0`
- `controller_summary_turn_nonzero_fraction = 0.0`
- `mean_turn_drive = 0.0`
- `mean_abs_turn_drive = 0.0`
- `path_length = 0.3689`
- `net_displacement = 0.0118`

Interpretation:

- the corrected branch still goes silent when the brain is removed
- the residual motion is the same passive settling observed on the earlier
  guarded zero-brain branch
- activation visualization is skipped here because the zero-brain path records
  no renderable neural frames

### Current Verdict

This corrected branch is materially better than the original perturbation
branch, but it is still not a solved real-fly parity result.

True now:

- jump steering is much better grounded
- brief hidden-target persistence is much better grounded
- the corrected branch passes `target`, `no_target`, and `zero_brain` checks
  on the main embodied branch

Still false:

- jump-specific frontal refixation is not yet solved
- matched perturbation-specific `no_target` / `zero_brain` controls still do
  not exist
- this is still a partial parity branch, not an indistinguishable living fly

Hard-rule consequence:

- future fixes for this assay must move upstream into brain-driven relay /
  descending mechanisms rather than adding controller-side heuristics
