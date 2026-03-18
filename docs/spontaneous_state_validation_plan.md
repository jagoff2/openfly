# Spontaneous-State Validation Plan

## Questions

The spontaneous-state workstream is testing four questions:

1. can the whole-brain backend avoid a dead cold start without external drive
2. is the resulting activity bounded rather than runaway
3. does the resulting activity show structure beyond white noise
4. can that state be perturbed into behaviorally relevant trajectories without
   turning into a motor shortcut

The relevant behavior target set is:

- [behavior_target_set.md](/G:/flysim/docs/behavior_target_set.md)

## Conditions

The minimum condition matrix is:

- `dead_cold_start`
- `candidate_ongoing`
- `candidate_pulse_release`
- later embodied follow-on:
  - `target`
  - `no_target`
  - `zero_brain`

## Metrics

### Brain-only startup metrics

- `global_spike_fraction`
- `global_mean_voltage`
- `global_voltage_std`
- `global_mean_conductance`
- `global_conductance_std`
- `background_mean_rate_hz`
- `background_active_fraction`
- `background_latent_mean_abs_hz`
- `background_latent_std_hz`

### Structure metrics

- mean absolute pairwise correlation across monitored relay/descending/sample
  traces
- shuffled-surrogate correlation
- structure ratio = real / shuffled
- lag-1 autocorrelation
- mean homologous-family rate correlation
- mean homologous-family voltage correlation

### Perturbation metrics

- peak turn-asymmetry response during pulse
- residual turn asymmetry after pulse release
- comparison against dead-cold-start baseline

### Embodied follow-on metrics

- `completed_full_duration`
- `nonzero_command_cycles`
- `spontaneous_locomotion.locomotor_active_fraction`
- bout counts / durations
- `controller_state_entropy`
- `target_condition.fixation_fraction_20deg`
- `target_condition.fixation_fraction_30deg`
- `target_condition.turn_alignment_fraction_active`
- `target_condition.turn_bearing_corr`
- startup-state summaries from `brain_backend_state`

## Anti-Shortcut Rejection Criteria

The spontaneous-state branch fails immediately if it:

- injects control through the decoder or body
- depends on target presence to exist
- makes `zero_brain` nonzero
- erases the `target` vs `no_target` distinction
- creates obvious always-on locomotor drive under symmetric blank conditions
- improves only raw displacement while degrading the canonical behavior targets

## Current Threshold For Promotion

The spontaneous-state branch should not become a default or claim branch until
all of the following hold:

- bounded nonzero startup activity exists across multiple seeds
- structure metrics remain above shuffle/noise controls
- spontaneous lateral bias is acceptably small under symmetric control
- short embodied runs improve readiness without collapsing negative controls

Until then, it stays experimental.
