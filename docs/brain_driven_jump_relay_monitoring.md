# Brain-Driven Jump Relay Monitoring

## Purpose

This note records the first jump-perturbation run on the canonical calibrated
decoder with no steering promotion and no new controller-side heuristics. The
goal is to keep the branch brain-driven and use expanded relay monitoring only
to locate the next biologically plausible decode step.

Primary artifacts:

- [summary.json](/G:/flysim/outputs/requested_2s_calibrated_target_jump_brain_relay_monitored/flygym-demo-20260315-020918/summary.json)
- [activation_side_by_side.mp4](/G:/flysim/outputs/requested_2s_calibrated_target_jump_brain_relay_monitored/flygym-demo-20260315-020918/activation_side_by_side.mp4)
- [activation_overview.png](/G:/flysim/outputs/requested_2s_calibrated_target_jump_brain_relay_monitored/flygym-demo-20260315-020918/activation_overview.png)
- [run.jsonl](/G:/flysim/outputs/requested_2s_calibrated_target_jump_brain_relay_monitored/flygym-demo-20260315-020918/run.jsonl)
- [cycle summary](/G:/flysim/outputs/metrics/jump_brain_driven_relay_cycle_summary.json)

## Result

This branch is still not a solved refixation result, but it is materially
useful and stays inside the hard rule.

Key behavior metrics:

- `target_condition_turn_bearing_corr = 0.8813`
- `target_condition_fixation_fraction_20deg = 0.043`
- `target_perturbation_jump_turn_alignment_fraction_active = 1.0`
- `target_perturbation_jump_turn_bearing_corr = 0.3215`
- `target_perturbation_jump_bearing_recovery_fraction_2s = -0.8210`
- `target_perturbation_jump_refixation_latency_s = null`

Important comparison against the earlier promoted jump branch:

- the brain-driven monitored branch still does not achieve frontal refixation
- but its jump recovery is less bad than the promoted sign-fix branch
  (`-0.8210` versus `-1.3164`)
- it preserves strong signed steering without using steering-promotion logic

## Diagnosis

The remaining failure is not the absence of signed steering. The fly still
turns with the correct sign after the jump, but the target reaches the rear
field in about `0.386 s` and frontal refixation still never completes within
`2.0 s`.

That means the next acceptable step is not another controller intervention. The
next step is to decode the missing state upstream of the current descending
readout.

## New Relay Ranking

The first honest jump-monitor capture produced a new second-wave relay ranking.

Top new relay families for general target-bearing structure:

- `CB1136`
- `CB3641`
- `LAL026`
- `CB1100`
- `LHPV4a7a`
- `CB3359`
- `CB3306`
- `CB1334`
- `CB2184`
- `PLP034`

Top new relay families for turn-specific lateralized structure:

- `TmY14`
- `AVLP507`
- `PLP156`
- `PLP034`
- `PS187`
- `CB2566`
- `CB1069`
- `SAD094`
- `VES058`
- `CB3640`

Artifacts:

- [wave 1 candidates](/G:/flysim/outputs/metrics/jump_brain_driven_relay_monitor_candidates.json)
- [wave 2 candidates](/G:/flysim/outputs/metrics/jump_brain_driven_relay_monitor_candidates_wave2.json)
- [wave 2 config](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_jump_brain_relay_monitored_wave2.yaml)

## Current Interpretation

- The steering-promotion branch remains evidence about where useful relay
  structure exists, but it is no longer the acceptable architecture target.
- The canonical calibrated decoder plus relay-heavy monitoring is now the
  active honest perturbation-analysis path.
- The next real work is a decoder-internal brain-side latent that lives
  upstream of the current motor decoder.
- That seam is now documented in
  [brain_latent_turn_decoder.md](/G:/flysim/docs/brain_latent_turn_decoder.md).
- The first live result on that seam is now recorded in
  [brain_latent_turn_decoder.md](/G:/flysim/docs/brain_latent_turn_decoder.md)
  and [brain_latent_turn_live_comparison.json](/G:/flysim/outputs/metrics/brain_latent_turn_live_comparison.json).
