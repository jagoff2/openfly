# Target-Engagement Metric Pivot

## Why this pivot is necessary

Raw speed and displacement are not the right primary metric for an awake fly
brain.

If the brain is genuinely active and the body/controller interface is capable of
walking, then `no_target` should still contain substantial locomotion. Public
whole-brain and behavior work supports that framing:

- spontaneous and forced walking recruit broad brain activity rather than a
  silent baseline:
  https://elifesciences.org/articles/85202
- steering-relevant descending populations are best evaluated against turning
  variables, not only forward displacement:
  https://elifesciences.org/reviewed-preprints/102230v1
- visually guided object/bar tracking is naturally described in terms of
  bearing, fixation, and saccadic orientation, not just translational speed:
  https://elifesciences.org/articles/83656

So the decode loop should ask two separate questions:

1. Is the fly awake and locomotor-rich even without a target?
2. Does the target change steering/alignment in a brain-specific way?

This note is now rationale only. The canonical grounded behavior spec is:

- [behavior_target_set.md](/G:/flysim/docs/behavior_target_set.md)

That matters because the repo should optimize for real adult-fly behaviors such
as spontaneous roaming, structured turning, landmark fixation, and perturbation
refixation, not for a synthetic idea of indefinite smooth pursuit.

## New behavior metrics

The repo now computes two behavior blocks directly from `run.jsonl`:

- `target_condition`
  - `mean_abs_bearing_rad`
  - `bearing_reduction_rad`
  - `fixation_fraction_20deg`
  - `fixation_fraction_30deg`
  - `approach_fraction`
  - `bearing_improvement_fraction`
  - `turn_alignment_fraction_active`
  - `turn_alignment_fraction_all`
  - `turn_bearing_corr`
  - `yaw_bearing_corr`
  - `aligned_turn_latency_s`
- `spontaneous_locomotion`
  - `locomotor_active_fraction`
  - `turn_active_fraction`
  - locomotor / turn bout counts and durations
  - `controller_state_entropy`
  - `mean_abs_turn_drive`
  - `turn_switch_rate_hz`

Implementation:

- [behavior_metrics.py](/G:/flysim/src/analysis/behavior_metrics.py)
- [iterative_decoding.py](/G:/flysim/src/analysis/iterative_decoding.py)
- [analyze_behavior_conditions.py](/G:/flysim/scripts/analyze_behavior_conditions.py)

## Current matched-control result

Artifacts:

- [relay_monitored_behavior_conditions_0p2s.csv](/G:/flysim/outputs/metrics/relay_monitored_behavior_conditions_0p2s.csv)
- [relay_monitored_behavior_conditions_0p2s.json](/G:/flysim/outputs/metrics/relay_monitored_behavior_conditions_0p2s.json)
- [iterative_decoding_cycle_relay_target_summary.json](/G:/flysim/outputs/metrics/iterative_decoding_cycle_relay_target_summary.json)
- [iterative_decoding_cycle_relay_no_target_summary.json](/G:/flysim/outputs/metrics/iterative_decoding_cycle_relay_no_target_summary.json)

The key result is:

- `target` is already locomotor-rich:
  - `locomotor_active_fraction = 0.96`
  - `controller_state_entropy = 0.583`
- `no_target` is also locomotor-rich:
  - `locomotor_active_fraction = 0.96`
  - `controller_state_entropy = 0.445`
- `zero_brain` collapses into sparse passive/body-side drift:
  - `locomotor_active_fraction = 0.40`
  - `controller_state_entropy = 0.0`

That means the current problem is not simply “the fly does not walk without the
target.”

The current problem is steering transfer:

- `target turn_alignment_fraction_active = 0.467`
- `zero_brain turn_alignment_fraction_active = 0.0`
- `target turn_bearing_corr = -0.697`
- `target fixation_fraction_20deg = 0.0`
- `target bearing_reduction_rad = 0.250`
- `zero_brain bearing_reduction_rad = 0.273`

The negative `turn_bearing_corr` is the important failure. The fly is turning,
but the signed turn response is not cleanly aligned with the target-bearing
signal. Also, simple bearing reduction alone is not trustworthy, because the
`zero_brain` control gets comparable passive bearing reduction from target
motion plus body drift.

## Decode consequence

The next decode loop should not optimize for more locomotion. It should optimize
for:

- positive signed turn alignment with target bearing
- fixation fraction above the zero-brain baseline
- target-specific steering structure beyond the no-target spontaneous baseline

This is a relay-to-descending steering transfer problem, not a wakefulness
problem.

## Current target-specific relay shortlist

I also ranked target relay families against the `no_target` spontaneous
baseline so the next monitor expansion is not just generic locomotor drive.

Artifacts:

- [relay_target_specificity_0p2s_families.csv](/G:/flysim/outputs/metrics/relay_target_specificity_0p2s_families.csv)
- [relay_target_specificity_0p2s_monitors.csv](/G:/flysim/outputs/metrics/relay_target_specificity_0p2s_monitors.csv)
- [relay_target_specificity_0p2s_summary.json](/G:/flysim/outputs/metrics/relay_target_specificity_0p2s_summary.json)

Current top family candidates after penalizing no-target locomotor correlation:

- `MTe14`
- `LTe62`
- `VCH`
- `CB0828`
- `cL02c`
- `CB1492`
- `CB3516`
- `LTe11`
- `IB015`
- `CB1108`
- `LT43`
- `LCe03`

These are still monitoring/probe candidates only. They are not promoted into
live control.
