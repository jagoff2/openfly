# Brain-Latent Turn Decoder

## Purpose

This branch adds the first decoder-internal brain-state latent on the honest
path.

Hard rule:

- no controller-side steering promotion
- no body-side shortcut heuristic
- any new control signal must be read from brain state and decoded inside the
  primary decoder path

The implementation seam is:

- [decoder.py](/G:/flysim/src/bridge/decoder.py)
- [controller.py](/G:/flysim/src/bridge/controller.py)

The live decoder can now consume monitored brain voltage directly through
`MotorDecoder.decode_state(...)`, which keeps the body-facing map unchanged and
adds the new latent upstream of `_command_from_states(...)`.

## Biological Target

This is not yet a full heading / goal / memory model.

It is a bounded first step toward the literature-grounded latent scaffold:

- `heading`
- `goal / target memory`
- `signed steering error`
- `steering gain`

For the current jump-refixation problem, the first justified latent is the
signed steering-error dimension.

The implementation therefore starts with a turn latent derived from bilateral
relay asymmetry in monitored brain voltage, rather than another controller
override.

## Matched-Condition Build

Artifacts:

- [target capture](/G:/flysim/outputs/requested_2s_calibrated_target_jump_brain_relay_monitored/flygym-demo-20260315-020918/activation_capture.npz)
- [no-target capture](/G:/flysim/outputs/requested_2s_calibrated_no_target_brain_relay_monitored/flygym-demo-20260315-054144/activation_capture.npz)
- [matched builder summary](/G:/flysim/outputs/metrics/jump_brain_driven_turn_latent_2s.json)
- [ranked table](/G:/flysim/outputs/metrics/jump_brain_driven_turn_latent_2s_ranked.csv)
- [strict library](/G:/flysim/outputs/metrics/jump_brain_driven_turn_latent_2s_library_strict.json)
- [weight sweep](/G:/flysim/outputs/metrics/jump_brain_driven_turn_latent_weight_sweep.csv)

The first matched library was too active in `no_target`, so the strict library
was reduced to the lowest-bias upstream subset:

- `AVLP370a`
- `LT59`
- `AVLP096,AVLP256`

These groups stay upstream of the current descending/motor readout and are
baseline-corrected with the matched `no_target` capture.

## Offline Replay

Strict-library shadow replay:

- [target replay summary](/G:/flysim/outputs/metrics/jump_brain_driven_turn_latent_2s_replay_target_strict_v2.json)
- [no-target replay summary](/G:/flysim/outputs/metrics/jump_brain_driven_turn_latent_2s_replay_no_target_strict_v2.json)
- [zero-brain replay summary](/G:/flysim/outputs/metrics/jump_brain_driven_turn_latent_2s_replay_zero_brain_strict_v2.json)

Key facts before live promotion:

- the strict latent still carries nontrivial spontaneous turning in `no_target`
- but it is materially cleaner than the first unfiltered matched library
- `zero_brain` remains silent

The offline composite sweep selected `turn_voltage_weight = 0.3` as the first
bounded live trial because it improved target-side turn correlation without
creating a large mean turn bias in `no_target`.

## Current Status

This is a decoder-internal latent seam, not yet a solved refixation branch.

The next criterion is not speed or displacement. It is whether the live
brain-latent branch improves jump recovery / refixation while preserving sane
`no_target` spontaneous behavior and silent `zero_brain` controls.

Important comparison rule:

- the older cold-start / quiescent branches are valid only as regime-change
  baselines
- once the backend is awake, the living-brain line must be judged primarily
  against matched living-brain controls and perturbation assays
- raw movement totals versus the dead-brain regime are not the main success
  criterion for this branch
- the relevant questions are whether the awakened branch shows structured
  ongoing activity, plausible spontaneous roaming, target-conditioned
  orientation / refixation, and separation from matched living `no_target` and
  `zero_brain` controls

## Live Result

Matched `2.0 s` live trio:

- [target summary](/G:/flysim/outputs/requested_2s_calibrated_target_jump_brain_latent_turn/flygym-demo-20260315-061819/summary.json)
- [target activation video](/G:/flysim/outputs/requested_2s_calibrated_target_jump_brain_latent_turn/flygym-demo-20260315-061819/activation_side_by_side.mp4)
- [no-target summary](/G:/flysim/outputs/requested_2s_calibrated_no_target_brain_latent_turn/flygym-demo-20260315-063511/summary.json)
- [no-target activation video](/G:/flysim/outputs/requested_2s_calibrated_no_target_brain_latent_turn/flygym-demo-20260315-063511/activation_side_by_side.mp4)
- [zero-brain summary](/G:/flysim/outputs/requested_2s_calibrated_zero_brain_target_jump_brain_latent_turn/flygym-demo-20260315-065048/summary.json)
- [comparison summary](/G:/flysim/outputs/metrics/brain_latent_turn_live_comparison.json)

Relative to the honest relay-monitored baseline:

- jump recovery improved from `-0.8210` to `-0.5658`
- jump turn-bearing correlation improved from `0.3215` to `0.8177`
- fixation at `20 deg` improved from `0.043` to `0.059`
- overall target turn-bearing correlation stayed essentially unchanged
  (`0.8813 -> 0.8806`)

Control integrity:

- `no_target` stayed near zero-mean in turn
  (`mean_turn_drive = 0.0054`, `right/left dominance = 0.552 / 0.448`)
- `zero_brain` remained silent
  (`controller_summary_turn_nonzero_fraction = 0.0`)

So this branch is a real improvement on the honest path, but it is still not a
complete living-fly result because jump-specific frontal refixation still does
not complete within `2.0 s`.

## Spontaneous-State Fold-In

The first honest attempt to fold the backend spontaneous-state candidate into
this branch is now recorded at:

- config:
  - [target_jump_brain_latent_turn_spontaneous.yaml](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_jump_brain_latent_turn_spontaneous.yaml)
- run:
  - [summary.json](/G:/flysim/outputs/requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous/flygym-demo-20260315-150545/summary.json)
  - [activation_side_by_side.mp4](/G:/flysim/outputs/requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous/flygym-demo-20260315-150545/activation_side_by_side.mp4)

This run proved that the backend was awake in the embodied branch, but it did
not help behavior. Relative to the non-spontaneous branch:

- `avg_forward_speed` dropped from `5.4296` to `3.7541`
- `target_condition_turn_bearing_corr` dropped from `0.8806` to `0.6964`
- `jump_turn_bearing_corr` flipped from `+0.8177` to `-0.7485`
- `jump_bearing_recovery_fraction_2s` worsened from `-0.5658` to `-1.5755`

So the current spontaneous-state candidate should not be promoted directly into
this branch. The result strengthens the current interpretation of `T147`: the
next missing variable is not mere wakefulness, but a richer heading / goal /
steering-gain scaffold upstream of the motor map.

## Spontaneous-On Matched Refit

The next step was not to reuse the old latent library, but to rebuild the
latent inside the awakened regime itself.

Artifacts:

- spontaneous-on matched no-target capture:
  - [summary.json](/G:/flysim/outputs/requested_2s_calibrated_no_target_brain_latent_turn_spontaneous/flygym-demo-20260315-200558/summary.json)
  - [activation_side_by_side.mp4](/G:/flysim/outputs/requested_2s_calibrated_no_target_brain_latent_turn_spontaneous/flygym-demo-20260315-200558/activation_side_by_side.mp4)
- spontaneous-on matched builder summary:
  - [jump_brain_driven_turn_latent_2s_spontaneous_refit.json](/G:/flysim/outputs/metrics/jump_brain_driven_turn_latent_2s_spontaneous_refit.json)
  - [ranked table](/G:/flysim/outputs/metrics/jump_brain_driven_turn_latent_2s_spontaneous_refit_ranked.csv)
  - [library](/G:/flysim/outputs/metrics/jump_brain_driven_turn_latent_2s_spontaneous_refit_library.json)
  - [target replay](/G:/flysim/outputs/metrics/jump_brain_driven_turn_latent_2s_spontaneous_refit_replay_target.json)
  - [no-target replay](/G:/flysim/outputs/metrics/jump_brain_driven_turn_latent_2s_spontaneous_refit_replay_no_target.json)
- live refit configs:
  - [target_jump_brain_latent_turn_spontaneous_refit.yaml](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_jump_brain_latent_turn_spontaneous_refit.yaml)
  - [no_target_brain_latent_turn_spontaneous_refit.yaml](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_latent_turn_spontaneous_refit.yaml)
- live refit runs:
  - [target summary](/G:/flysim/outputs/requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-203010/summary.json)
  - [target activation video](/G:/flysim/outputs/requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-203010/activation_side_by_side.mp4)
  - [no-target summary](/G:/flysim/outputs/requested_2s_calibrated_no_target_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-204719/summary.json)
  - [no-target activation video](/G:/flysim/outputs/requested_2s_calibrated_no_target_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-204719/activation_side_by_side.mp4)
  - [comparison summary](/G:/flysim/outputs/metrics/spontaneous_brain_latent_refit_comparison.json)

What changed:

- a matched spontaneous-on `no_target` capture was collected instead of relying
  on the earlier cold-state control
- the builder now supports state-bin consistency filtering against the live
  backend state variable `background_latent_mean_abs_hz`
- the refit latent selected a different group set inside the awakened regime:
  - `MeLp1`
  - `PVLP112b`
  - `cM15`
  - `CB0965`
  - `CL294`
  - `CB1916`
  - `cML02`
  - `AVLP091`

Living-branch outcome:

- target-side jump steering repaired relative to the first spontaneous run:
  - `jump_turn_alignment_fraction_active: 0.1520 -> 0.7302`
  - `jump_turn_bearing_corr: -0.7485 -> 0.5644`
  - `jump_bearing_recovery_fraction_2s: -1.5755 -> -1.0482`
- broader target behavior also improved modestly:
  - `avg_forward_speed: 3.7541 -> 4.1828`
  - `net_displacement: 4.3757 -> 5.0591`
  - `target_condition_mean_abs_bearing_rad: 1.6519 -> 1.5551`
- the matched awakened no-target control remained balanced in sign:
  - `mean_turn_drive = 0.0077`
  - `right/left dominance = 0.413 / 0.587`

Current interpretation:

- the spontaneous-on latent does need to be rebuilt inside the awakened regime;
  reusing the cold-state library was the wrong move
- the matched refit repaired the most obvious pathology, namely the jump-sign
  inversion
- this is still not a full solution:
  - frontal refixation still does not complete within `2.0 s`
  - gross locomotion remains strong in both living `target` and living
    `no_target`, so target-conditioned structure must still be read mainly from
    the perturbation and orientation metrics rather than from raw movement
    totals

## Living Activation Read

The dedicated pair analysis is recorded in
[living_brain_activation_analysis.md](/G:/flysim/docs/living_brain_activation_analysis.md).

The important decoder-side consequence is:

- the large living-brain central cloud is mostly shared awakened baseline
  occupancy, not the main target-conditioned signal
- the informative target-conditioned structure remains subtler, more
  distributed, and more voltage-side than rate-side
- future decoder expansion should therefore widen upstream relay-family
  monitoring and keep the refit latent voltage-asymmetry-first
