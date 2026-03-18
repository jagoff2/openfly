# Living-Brain Activation Analysis

## Scope

This note compares the matched living-brain spontaneous-refit runs:

- target:
  - [activation_capture.npz](/G:/flysim/outputs/requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-203010/activation_capture.npz)
  - [run.jsonl](/G:/flysim/outputs/requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-203010/run.jsonl)
  - [activation_side_by_side.mp4](/G:/flysim/outputs/requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-203010/activation_side_by_side.mp4)
- no-target:
  - [activation_capture.npz](/G:/flysim/outputs/requested_2s_calibrated_no_target_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-204719/activation_capture.npz)
  - [run.jsonl](/G:/flysim/outputs/requested_2s_calibrated_no_target_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-204719/run.jsonl)
  - [activation_side_by_side.mp4](/G:/flysim/outputs/requested_2s_calibrated_no_target_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-204719/activation_side_by_side.mp4)

Recorded outputs from this analysis pass:

- [summary.json](/G:/flysim/outputs/metrics/living_brain_activation_pair_summary.json)
- [condition_summary.csv](/G:/flysim/outputs/metrics/living_brain_activation_pair_condition_summary.csv)
- [monitor_rate_comparison.csv](/G:/flysim/outputs/metrics/living_brain_activation_pair_monitor_rate_comparison.csv)
- [family_comparison.csv](/G:/flysim/outputs/metrics/living_brain_activation_pair_family_comparison.csv)
- [central_units_target.csv](/G:/flysim/outputs/metrics/living_brain_activation_pair_central_units_target.csv)
- [central_units_no_target.csv](/G:/flysim/outputs/metrics/living_brain_activation_pair_central_units_no_target.csv)
- [central_families_target.csv](/G:/flysim/outputs/metrics/living_brain_activation_pair_central_families_target.csv)
- [central_families_no_target.csv](/G:/flysim/outputs/metrics/living_brain_activation_pair_central_families_no_target.csv)
- [renderer_breakdown.png](/G:/flysim/outputs/plots/living_brain_activation_pair_renderer_breakdown.png)
- [top_central_families.png](/G:/flysim/outputs/plots/living_brain_activation_pair_top_central_families.png)

The analysis code is:

- [living_brain_activation_analysis.py](/G:/flysim/src/analysis/living_brain_activation_analysis.py)
- [analyze_living_brain_activation_pair.py](/G:/flysim/scripts/analyze_living_brain_activation_pair.py)

## Main Findings

### 1. Target and no-target are already in the same awakened regime

The matched living runs have effectively identical spontaneous-state backbone
statistics:

- `background_mean_rate_hz_mean = 0.0314`
- `background_active_fraction_mean = 0.0242`
- `background_latent_mean_abs_hz_mean = 0.9613`
- `background_latent_std_hz_mean = 1.1026`

This matters because it means target-conditioned differences are not coming from
one run being "more awake." They are smaller structured differences on top of
the same living baseline.

Implication:

- future fitting must keep using matched living `no_target` baselines
- awake-state bins keyed to `background_latent_mean_abs_hz` remain justified
- raw comparisons against dead-brain branches are not the primary evaluation for
  this line

### 2. The bright cloud is real state, but it is not a whole-brain spike storm

The activation renderer in [activation_viz.py](/G:/flysim/src/visualization/activation_viz.py)
shows:

- all spiking neurons first
- then fills the rest of the displayed `6000` brain points with the highest
  `abs(voltage)` non-spiking neurons

So the video is a mix of true spikes and high-|voltage| occupancy.

Measured from the captures:

- target:
  - `221.0` spiking neurons per frame on average across `138,639` neurons
  - `global_spike_fraction_mean = 0.00161`
  - about `5779` displayed points per frame are non-spiking high-|voltage|`
    selections
- no-target:
  - `229.7` spiking neurons per frame on average
  - `global_spike_fraction_mean = 0.00167`
  - about `5770` displayed points per frame are non-spiking high-|voltage|`
    selections

Interpretation:

- the living branch is genuinely awake
- the video overstates "how many spikes" there are
- the dense visible cloud is mostly distributed membrane-state occupancy, not a
  synchronous spike avalanche

### 3. The visually dominant families are not the same as the spike-heavy families

The most visible unsampled families are largely shared between target and
no-target:

- `MeMe_e13`
- `DNa03`
- `Nod3`
- `H2`
- `T2`
- `Am1`
- `LHMB1`
- `H1`
- `Mi10`
- `T4a`
- `TmY18`
- `Mi4`

These families have very high `mean_selected_frames` in
[family_comparison.csv](/G:/flysim/outputs/metrics/living_brain_activation_pair_family_comparison.csv),
but many of them have `0` or near-zero `mean_spike_frames`. They look like
shared living-brain baseline occupancy, not strong target-specific spike
drivers.

The truly spike-heavy unsampled families are a different, smaller set:

- target:
  - `CT1`
  - `DM4_adPN`
  - `LHPV12a1`
  - `lLN2X03`
  - `LPi12`
  - `CRE011`
  - `DC1_adPN`
  - `LHCENT2`
- no-target:
  - `lLN2F_b`
  - `VM6_adPN`
  - `il3LN6`
  - `CT1`
  - `lLN1_a`
  - `APL`
  - `DP1m_adPN`
  - `DPM`

These families spike intermittently. They are not the same populations that
dominate the brightest persistent cloud.

### 4. The current monitored rate layer is not where most living-brain structure sits

The top monitored bilateral rate labels are almost the same in target and
no-target:

- `CB0197`
- `DNp18`
- `LHAV2g2`
- `DNpe040`
- `DNb09`
- `DNpe031`

That is why gross monitored-rate magnitude is not the right signal for decoding
the living branch.

The more informative signal remains voltage-side and asymmetry-side. This is
consistent with the spontaneous-refit decode artifacts:

- [living_spontaneous_refit_target_cycle_summary.json](/G:/flysim/outputs/metrics/living_spontaneous_refit_target_cycle_summary.json)
- [jump_brain_driven_turn_latent_2s_spontaneous_refit_library.json](/G:/flysim/outputs/metrics/jump_brain_driven_turn_latent_2s_spontaneous_refit_library.json)

Those files already show:

- best monitor rate target-bearing correlation is weak
- best monitor voltage target-bearing correlation is strong
- the selected awakened latent is mostly a voltage-asymmetry scaffold

### 5. The target-conditioned signal is subtle and distributed

The living branch does not appear to encode target presence as a gross global
increase in spikes or visible occupancy. Instead, the target-conditioned
structure is carried by weaker distributed families that are not the brightest
part of the movie.

Existing target-vs-no-target decode outputs already point to the next upstream
families to probe:

- general target-bearing candidates:
  - `LCe01`
  - `CL314`
  - `LLPC4`
  - `PLP230`
  - `AVLP417,AVLP438`
  - `CB3014`
- lateralized turn candidates:
  - `PLP013`
  - `MTe50`
  - `LC12`
  - `CB3640`
  - `CB3516`
  - `CB2566`

Evidence:

- [living_spontaneous_refit_target_vs_no_target_summary.json](/G:/flysim/outputs/metrics/living_spontaneous_refit_target_vs_no_target_summary.json)
- [living_spontaneous_refit_target_vs_no_target_families.csv](/G:/flysim/outputs/metrics/living_spontaneous_refit_target_vs_no_target_families.csv)
- [living_spontaneous_refit_target_vs_no_target_monitors.csv](/G:/flysim/outputs/metrics/living_spontaneous_refit_target_vs_no_target_monitors.csv)

These are better next decode targets than the most visually dominant central
cloud.

## What This Means For Future Work

The living branch has already crossed an important line: it is no longer a
mostly silent stimulus-locked machine. But that changes the decoding problem.

What the current analysis supports:

- keep the spontaneous-state backbone on for living-branch work
- fit against matched living `target` / `no_target`, not against dead-brain
  baselines
- stay voltage-first and asymmetry-first
- treat the large shared visible cloud as awake-state baseline structure unless
  proven otherwise
- widen monitoring upstream into target-specific unsampled relay families before
  adding more downstream motor complexity

What the current analysis rejects:

- using the brightest visible cluster as if it were automatically the most
  informative motor or target signal
- using gross spike count or gross locomotion as the main metric for living
  target vs no-target separation
- assuming the monitored descending-rate layer already captures most of the
  living-brain signal

## Current Best Read

The living branch is doing more real brain-like internal work than the
quiescent branches, but much of that work is shared awakened baseline traffic.
The useful target-conditioned signal appears to be smaller, distributed,
voltage-based, and still only partially sampled by the current decoder and
monitoring set.

That means future progress should come from:

1. matched living control comparisons
2. upstream relay-family monitoring expansion
3. voltage-asymmetry latent fitting
4. later movement toward heading / goal / steering-gain state

Not from chasing the visually loudest spike cloud.
