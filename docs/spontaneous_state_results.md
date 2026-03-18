# Spontaneous-State Results

## Current Pilot Matrix

The first pilot used:

- `dead_cold_start`
- `candidate_ongoing`
- `candidate_pulse_release`

Artifacts:

- `outputs/metrics/spontaneous_state_pilot_summary.json`
- `outputs/metrics/spontaneous_state_latent_pilot_summary.json`
- `outputs/metrics/spontaneous_state_latent_seed0_summary.json`
- `outputs/metrics/spontaneous_state_latent_seed1_summary.json`
- `outputs/metrics/spontaneous_state_latent_seed2_summary.json`
- matching CSV and plot artifacts under `outputs/metrics/`, `outputs/plots/`,
  and `outputs/benchmarks/`

## Result 1: The old cold-start really was silent

`dead_cold_start` stayed at:

- `mean_spike_fraction = 0.0`
- `mean_voltage = -52.0`
- `mean_conductance = 0.0`
- `background_mean_rate_hz = 0.0`

So the old backend did not have any endogenous startup occupancy.

## Result 2: Static sparse tonic drive alone was too weak

The first static pilot produced only a tiny nonzero state:

- `mean_spike_fraction ~= 4e-6`
- structure metrics were effectively undefined at the monitored level
- monitored motor outputs stayed near zero

That was enough to prove the seam worked, but not enough to count as a useful
ongoing state.

## Result 3: Sparse tonic occupancy plus slow latent fluctuations produced a real ongoing state

The current latent pilot improved the picture materially.

Representative seed-0 brain-only results:

- `candidate_ongoing.mean_spike_fraction = 3.14e-4`
- `candidate_ongoing.background_mean_rate_hz = 0.254`
- `candidate_ongoing.background_active_fraction = 0.147`
- `candidate_ongoing.nonzero_window_fraction = 1.0`
- structure ratio `= 1.115`
- pulse peak turn asymmetry `= 200 Hz`

This is still weak compared with a rich biological spontaneous state, but it is
no longer a dead silent backend.

## Result 4: The pilot is bounded, but not yet clean

What passed:

- no numerical runaway was observed in the short audit windows
- background activity remained finite and bounded by the configured rate cap
- the candidate was perturbable by a lateralized visual pulse
- sample-neuron traces showed real ongoing nonzero activity

What failed or remains open:

- seed-to-seed robustness is not good enough yet
- spontaneous motor-side lateral bias appears in some seeds under symmetric
  zero-input conditions
- at least one tested seed showed much weaker perturbation/readout expression
- no embodied matched-control validation has been run yet

Example seed spread with the current latent pilot:

- seed `0`: ongoing baseline turn bias `+20 Hz`, pulse peak `200 Hz`
- seed `1`: ongoing baseline turn bias `-5 Hz`, pulse peak `0 Hz`
- seed `2`: ongoing baseline turn bias `+17.5 Hz`, pulse peak `200 Hz`

That is too unstable to promote.

## Result 5: A central-family bilateral candidate clears the brain-only bar

The earlier random latent pilot has now been superseded by a more constrained
candidate:

- config:
  - `configs/brain_spontaneous_probe.yaml`
- seed-0 main audit:
  - `outputs/metrics/spontaneous_state_best_candidate_summary.json`
- seed summary:
  - `outputs/metrics/spontaneous_state_central_seed_summary.json`
  - `outputs/metrics/spontaneous_state_central_seed_summary.csv`

What changed:

- spontaneous modes are now built over real bilateral annotation families
  instead of random neuron-level sparse masks
- the family pool is restricted to:
  - `central`
  - `ascending`
  - `visual_projection`
  - `visual_centrifugal`
  - `endocrine`
- large bilateral families are capped out of the spontaneous pool
- bilateral shared coupling is strong and antisymmetric latent variance is weak

Seed-level outcome for the current best candidate:

- ongoing spontaneous turn bias:
  - seed `0`: `+2.5 Hz`
  - seed `1`: `+10.0 Hz`
  - seed `2`: `+12.5 Hz`
- pulse peak turn asymmetry:
  - all three seeds: `100 Hz`
- homologous family rate correlation:
  - seed `0`: `0.205`
  - seed `1`: `-0.017`
  - seed `2`: `0.095`
- homologous family voltage correlation:
  - seed `0`: `0.001`
  - seed `1`: `0.657`
  - seed `2`: `0.606`

Interpretation:

- the candidate is no longer dead
- spontaneous lateral bias is much smaller and no longer flips into large
  persistent one-sided domination
- homologous bilateral structure is now measurable in the family-level
  readouts, especially in voltage-space
- the pulse response is retained consistently across seeds

This is strong enough to treat the central-family bilateral candidate as the
new best brain-only spontaneous-state candidate in the repo.

## Current Verdict

Verdict: `brain-only pass / full workstream partial`

The spontaneous-state program has now cleared the brain-only gate:

- the backend supports bounded ongoing activity without decoder/body hacks
- the current best candidate is sparse, bilateral, and perturbable in a way
  that is materially closer to public adult whole-brain monitoring than the old
  absorbing silent reset

The full workstream is still partial because:

- there is not yet matched embodied evidence showing better startup readiness
  without collapsing `target` / `no_target` / `zero_brain`

## Result 6: First honest embodied fold-in regressed the current best target-jump latent branch

The first real embodied spontaneous-state fold-in is now recorded at:

- config:
  - [target_jump_brain_latent_turn_spontaneous.yaml](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_jump_brain_latent_turn_spontaneous.yaml)
- run:
  - [summary.json](/G:/flysim/outputs/requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous/flygym-demo-20260315-150545/summary.json)
  - [activation_side_by_side.mp4](/G:/flysim/outputs/requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous/flygym-demo-20260315-150545/activation_side_by_side.mp4)

What passed:

- the backend was genuinely awake in the live embodied run
- same-run activation capture completed
- the body/decoder path remained the same primary branch path with no new
  controller/body shortcut logic

What failed:

- the spontaneous fold-in regressed the behavior of the current best
  non-spontaneous brain-latent target-jump branch
- target metrics worsened:
  - `avg_forward_speed: 5.4296 -> 3.7541`
  - `net_displacement: 6.2632 -> 4.3757`
  - `target_condition_turn_bearing_corr: 0.8806 -> 0.6964`
- jump behavior degraded sharply:
  - `jump_turn_bearing_corr: 0.8177 -> -0.7485`
  - `jump_bearing_recovery_fraction_2s: -0.5658 -> -1.5755`

Interpretation:

- backend wakefulness alone is not sufficient to improve the current
  target-jump latent branch
- the current spontaneous-state candidate is still useful and valid as a
  brain-only result
- but naive direct promotion into the best embodied branch is not justified
  and is now an explicit negative result

## Next Required Work

1. run matched short embodied `target` / `no_target` / `zero_brain` tests with
   `brain_backend_state` logging
2. confirm that the new candidate improves startup readiness without erasing
   target-conditioned control separation
3. only then decide whether a spontaneous-state config deserves a real embodied
   branch

## Result 7: Spontaneous-on matched latent refit repaired the jump-sign failure inside the living regime

The spontaneous-state branch no longer relies on the old cold-state latent
library.

Artifacts:

- matched awakened no-target capture:
  - [summary.json](/G:/flysim/outputs/requested_2s_calibrated_no_target_brain_latent_turn_spontaneous/flygym-demo-20260315-200558/summary.json)
- spontaneous-on refit builder:
  - [jump_brain_driven_turn_latent_2s_spontaneous_refit.json](/G:/flysim/outputs/metrics/jump_brain_driven_turn_latent_2s_spontaneous_refit.json)
  - [jump_brain_driven_turn_latent_2s_spontaneous_refit_library.json](/G:/flysim/outputs/metrics/jump_brain_driven_turn_latent_2s_spontaneous_refit_library.json)
  - [jump_brain_driven_turn_latent_2s_spontaneous_refit_ranked.csv](/G:/flysim/outputs/metrics/jump_brain_driven_turn_latent_2s_spontaneous_refit_ranked.csv)
  - [spontaneous refit comparison](/G:/flysim/outputs/metrics/spontaneous_brain_latent_refit_comparison.json)
- live refit runs:
  - [target summary](/G:/flysim/outputs/requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-203010/summary.json)
  - [no-target summary](/G:/flysim/outputs/requested_2s_calibrated_no_target_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-204719/summary.json)

What changed:

- the latent was rebuilt from matched awakened `target` / `no_target` captures
  instead of reusing the earlier cold-state library
- the builder now rejects sign-unstable candidates across low/high spontaneous
  state bins using `background_latent_mean_abs_hz`
- the awakened refit selected a different eight-group latent and then validated
  it live on a matched awakened pair

What improved relative to the first spontaneous target run:

- `avg_forward_speed: 3.7541 -> 4.1828`
- `net_displacement: 4.3757 -> 5.0591`
- `target_condition_mean_abs_bearing_rad: 1.6519 -> 1.5551`
- `jump_turn_alignment_fraction_active: 0.1520 -> 0.7302`
- `jump_turn_bearing_corr: -0.7485 -> 0.5644`
- `jump_bearing_recovery_fraction_2s: -1.5755 -> -1.0482`

Control-side outcome:

- the awakened no-target refit stayed near zero-mean in turn:
  - `mean_turn_drive = 0.0077`
- right/left dominance remained roughly balanced:
  - `0.413 / 0.587`

Interpretation:

- the spontaneous-state program is compatible with a better target-jump latent
  than the first naive fold-in suggested
- the main lesson is structural:
  - an awakened brain requires an awakened-regime decoder
  - the cold-state latent could not simply be transplanted
- this remains a partial living-fly result because:
  - frontal refixation still fails within `2.0 s`
  - a fresh spontaneous zero-brain rerun has not yet been collected in this
    slice

## Full Validation Boundary

The current repo should still not claim fully physiologically validated
spontaneous fly-brain dynamics.

That stronger claim would require public evidence that does not yet exist in
one aligned package:

- whole-brain spontaneous recordings with the right coverage
- stable alignment from those recordings to the simulated connectome identities
- cell-intrinsic and synaptic physiological constraints at scale
- a broad causal perturbation atlas for spontaneous-state dynamics

The full requirement and current blocker are recorded in:

- [spontaneous_state_full_validation_requirements.md](/G:/flysim/docs/spontaneous_state_full_validation_requirements.md)

So the correct current label remains:

- public-data-informed spontaneous-state pilot
- partial physiological plausibility
- not full physiological validation
