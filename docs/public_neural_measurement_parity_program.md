# Public Neural Measurement Parity Program

## Priority

This is now the top-level max-urgent program for the repo.

Until this program reaches acceptable parity, no other downstream Creamer,
decoder, or embodiment work should take precedence.

The explicit objective is:

- obtain public real fly neural measurement datasets
- convert them into a canonical matched format
- drive the **spontaneous / living brain** under the same public conditions
- force the model outputs to match the public neural measurements as closely as
  possible, dataset by dataset

This is deliberately optimization-first rather than purity-first.

## Why this now takes precedence

The latest Creamer work clarified the dependency order.

The synced treadmill probe proved that scene semantics can be made honest:

- `baseline_a`: speed `645.153 mm/s`, retinal slip `0.0 mm/s`
- `motion_ftb_a`: speed `645.287 mm/s`, retinal slip `-0.5 mm/s`
- `baseline_b`: speed `645.244 mm/s`, retinal slip `0.0 mm/s`

So the scene-validity ambiguity is reduced. The remaining mismatch is now more
plainly the embodied brain / decoder / body response itself.

That makes a stronger upstream footing necessary:

- match public neural measurements first
- then re-examine the decoder and embodiment from that anchored brain state

## Current blocker summary preserved from the latest work

### Synced probe result

Evidence:

- [synced run log](/G:/flysim/outputs/creamer2018_known_good_nonspont_creamer_motion_energy_freqgate_safe_t5a_only_speedsuppress_turnlite_lowforward_synced_veryslow_baseline/flygym-demo-20260329-120615/run.jsonl)
- [Creamer note](/G:/flysim/docs/creamer2018_visual_speed_control_note.md)

What it proved:

- scored stationary blocks can now be true `0.0 mm/s` retinal slip
- scored motion blocks can now be true `-0.5 mm/s` retinal slip

What it did **not** fix:

- the branch still did not slow
- first synced front-to-back delta was slightly wrong-sign:
  - `+0.13418 mm/s`
- treadmill speed remained pinned near `645 mm/s`

### Strongest current blocker hypothesis

The dominant blocker is now a **high-speed embodied treadmill attractor** in the
current `hybrid_multidrive` operating point, combined with a weak / nonspecific
forward-context signal.

Independent blocker reviews converged on this:

- the decoder-side suppressive signal changes
- the body-side treadmill speed hardly responds once the branch sits in the
  very fast locomotor regime

See:

- [creamer_recording_fit_targets.md](/G:/flysim/docs/creamer_recording_fit_targets.md)
- [creamer2018_visual_speed_control_note.md](/G:/flysim/docs/creamer2018_visual_speed_control_note.md)

### Best falsifier already identified

Run a **same-state replay fork** from the start of `baseline_a`:

1. replay the observed baseline latent stream
2. replay the observed motion latent stream
3. replay a stronger bilateral frequency-suppressed latent stream with turn and
   amplitude fixed

Interpretation:

- if treadmill speed stays pinned across forks, the embodied attractor is real
- if speed tracks the replayed frequencies, the main blocker is upstream in the
  visual-to-forward signal

This is tracked as `T188`.

## Public datasets to obtain first

These are the highest-value targets identified so far.

### Whole-brain / locomotor state

1. **Aimon et al. 2023 Dryad**
- spontaneous and forced walking whole-brain light-field imaging
- use for spontaneous/living baseline fit
- https://doi.org/10.5061/dryad.3bk3j9kpb

2. **Schaffer et al. 2023 Figshare**
- whole-brain SCAPE in behaving flies on spherical treadmill
- use for locomotor-state structure and residual dynamics
- https://doi.org/10.6084/m9.figshare.23749074

### Early visual channels

3. **Ketkar et al. 2022 Zenodo**
- `L1/L2/L3`-relevant visual recordings plus walking-ball behavior
- use for lamina temporal and state-dependent preprocessing
- https://doi.org/10.5281/zenodo.6335347

4. **Gruntman et al. 2019 Figshare**
- mechanistic `T5` recordings under motion stimuli
- use for OFF-path temporal kernels and TF-tuned motion basis
- https://doi.org/10.25378/janelia.c.4771805.v1

### Downstream visual-to-locomotor / treadmill feedback

5. **Shomar et al. 2025 Dryad**
- identified visual-to-locomotor channel dataset
- use for downstream visual-motion-to-locomotor fitting
- https://doi.org/10.5061/dryad.kkwh70sgw

6. **Dallmann et al. 2025 Dryad**
- treadmill proprioceptive / ascending-feedback dataset
- use for treadmill/body-to-brain coupling realism
- https://doi.org/10.5061/dryad.gqnk98t16

### Behavioral scorecard / comparator set

7. **Creamer, Mano, Clark 2018**
- main behavioral acceptance target
- currently best treated as scorecard rather than primary raw fit source
- https://pmc.ncbi.nlm.nih.gov/articles/PMC6405217/

8. **Katsov and Clandinin 2008**
- translational-vs-rotational stream separation prior
- https://pmc.ncbi.nlm.nih.gov/articles/PMC3391501/

9. **Cruz et al. 2021**
- walking-VR visual feedback stabilization comparator
- https://pmc.ncbi.nlm.nih.gov/articles/PMC8556163/

10. **Henning et al. 2022**
- `T4/T5` population optic-flow basis
- https://pmc.ncbi.nlm.nih.gov/articles/PMC8769539/

11. **Erginkaya et al. 2025**
- downstream optic-flow circuit comparator
- https://www.nature.com/articles/s41593-025-01948-9

12. **Clark et al. 2023**
- turning comparator with public data
- https://pmc.ncbi.nlm.nih.gov/articles/PMC10522332/

## Canonical harness requirement

Every dataset must be converted into one matched schema:

- time base
- stimulus definition
- behavior state
- neural activity traces
- neuron identity or group identity
- units / normalization
- train/validation/test split

The spontaneous brain must then be driven under the same public conditions and
evaluated in that exact same schema.

## Current preserved tactical guidance

1. Use the **spontaneous / living brain** for this program.
2. Do not resume downstream decoder interpretation as the main priority until
   public neural measurement parity has real traction.
3. Preserve the current latest blocker findings:
   - synced-scene semantics are fixed
   - high-speed embodied attractor remains the main blocker in the Creamer path
   - whole-brain and identified-neuron public datasets now exist to constrain
     the model more directly

## Current staged status

Current stage artifact:

- [dataset status note](/G:/flysim/docs/public_neural_measurement_dataset_status.md)
- [stage status JSON](/G:/flysim/outputs/metrics/public_neural_measurement_stage_status.json)

What is real now:

- `aimon2023_dryad`
  - fully staged raw source
  - first real canonical export exists:
    - `outputs/derived/aimon2023_canonical/aimon2023_canonical_summary.json`
- `schaffer2023_figshare`
  - manifest and file inventory staged
  - spreadsheet plus one real staged NWB session
  - first real canonical export exists:
    - `outputs/derived/schaffer2023_nwb_canonical/schaffer2023_nwb_canonical_summary.json`
- `ketkar2022_zenodo`
  - record JSON, manifest, and file table staged
- `gruntman2019_janelia`
  - manifest and file inventory staged
  - Figure 2 raw zip staged
  - first real canonical export exists:
    - `outputs/derived/gruntman2019_figure2_canonical/gruntman2019_figure2_canonical_summary.json`
- `dallmann2025_dryad`
  - Dryad dataset metadata, versions, file inventory, and manifest staged
- `shomar2025_dryad`
  - Dryad dataset metadata, versions, file inventory, and manifest staged

Still blocked:

- Dryad raw file download remains hostile in this environment
  - direct API download path returns `401`
  - direct `file_stream` path returns `403`
- Schaffer, Ketkar, Dallmann, and Shomar still need dataset-specific canonical
  exporters before they can participate in matched replay/fitting

## First live parity result

The parity program now has its first real spontaneous-brain fit artifact, not
just staged datasets and canonical exports.

Evidence:

- [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py)
- [run_aimon_spontaneous_fit.py](/G:/flysim/scripts/run_aimon_spontaneous_fit.py)
- [pilot summary](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_b1269_pilot_v2/aimon_spontaneous_fit_summary.json)

What was done:

- used the living spontaneous branch as the backend
- used the canonical Aimon trial windows and score surface
- used the bilateral family voltage basis from the spontaneous mesoscale
  validator
- used symmetric mechanosensory forcing for `forced_walk`
- fit a reduced linear projection from spontaneous-brain state into the public
  Aimon trace space

Current result:

- same-dataset pilot on:
  - `B1269_spontaneous_walk`
  - `B1269_forced_walk`
- aggregate:
  - `mean_pearson_r = 0.8909`
  - `mean_nrmse = 0.0661`
  - `mean_abs_error = 0.00173`
  - `mean_sign_agreement = 0.8571`

Interpretation:

- This proves the parity lane is live.
- It does not yet prove held-out generalization.
- The next honest boundary is train-on-`B350`, score-on-`B1269`, then sweep
  forcing amplitude and basis choices from that held-out result.

## First held-out boundary

The first held-out Aimon spontaneous-brain fit is now complete.

Evidence:

- [held-out summary](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_train_to_test_v1/aimon_spontaneous_fit_summary.json)

What was done:

- fit on canonical `train`:
  - `B350_spontaneous_walk`
  - `B350_forced_walk`
- scored on all trials, including held-out canonical `test`:
  - `B1269_spontaneous_walk`
  - `B1269_forced_walk`

Current result:

- aggregate over all four trials:
  - `mean_pearson_r = 0.1456`
  - `mean_nrmse = 0.2462`
  - `mean_abs_error = 0.00608`
  - `mean_sign_agreement = 0.5279`
- held-out `test` mean:
  - `mean_pearson_r = 0.0564`
  - `mean_nrmse = 0.3328`
  - `mean_abs_error = 0.00856`
  - `mean_sign_agreement = 0.4689`

Interpretation:

- The same-dataset B1269 pilot was not enough.
- Generalization is currently weak.
- That is the first honest optimization boundary for the parity program.
- The next active work is not more architecture discussion. It is a targeted
  held-out optimization sweep.

## First held-out sweep comparison

The first three held-out Aimon optimization points are now complete enough to
show which direction is productive.

Evidence:

- [v1 baseline](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_train_to_test_v1/aimon_spontaneous_fit_summary.json)
- [v2 reduced basis / no asymmetry](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_train_to_test_v2_basis16_ridge1e-2_noasym/aimon_spontaneous_fit_summary.json)
- [v3 doubled mechanosensory forcing](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_train_to_test_v3_force2/aimon_spontaneous_fit_summary.json)
- [variant comparison](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_variant_comparison.json)

Held-out `test` mean on `B1269_*`:

- `v1` baseline:
  - `mean_pearson_r = 0.0564`
  - `mean_nrmse = 0.3328`
  - `mean_abs_error = 0.00856`
  - `mean_sign_agreement = 0.4689`
- `v2` reduced basis / no asymmetry:
  - `mean_pearson_r = 0.0122`
  - `mean_nrmse = 0.3310`
  - `mean_abs_error = 0.00849`
  - `mean_sign_agreement = 0.4605`
- `v3` doubled mechanosensory forcing:
  - `mean_pearson_r = 0.0620`
  - `mean_nrmse = 0.3117`
  - `mean_abs_error = 0.00821`
  - `mean_sign_agreement = 0.4660`
- `v4` contact2 / forward1:
  - `mean_pearson_r = 0.0385`
  - `mean_nrmse = 0.3293`
  - `mean_abs_error = 0.00853`
  - `mean_sign_agreement = 0.4644`
- `v5` forward2 / contact1:
  - `mean_pearson_r = 0.0565`
  - `mean_nrmse = 0.3155`
  - `mean_abs_error = 0.00824`
  - `mean_sign_agreement = 0.4723`

Interpretation:

- Reduced projection capacity is not the main missing ingredient.
- Stronger mechanosensory forcing is the first change that improved held-out
  Aimon in a meaningful way.
- The improvement is still small and not enough for parity.
- The weak slice still concentrates in held-out `B1269_forced_walk`, so the
  next narrow optimization axis is separating `force_contact_force` from
  `force_forward_speed`.
- Contact-only forcing was a negative result.
- Forward-dominant forcing recovered most of the useful `v3` gain and produced
  the best held-out sign agreement so far.

New split result:

- [v4 contact2/forward1](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_train_to_test_v4_contact2_forward1/aimon_spontaneous_fit_summary.json)
- held-out `test` mean:
  - `mean_pearson_r = 0.0385`
  - `mean_nrmse = 0.3293`
  - `mean_abs_error = 0.00853`
  - `mean_sign_agreement = 0.4644`

Interpretation:

- Contact amplification by itself is not the main reason `v3 force2` improved.
- The complementary forward split is now complete too:
  - [v5 forward2/contact1](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_train_to_test_v5_forward2_contact1/aimon_spontaneous_fit_summary.json)
- That result confirms the useful forcing contribution leans more toward
  forward-speed drive than contact alone, but still does not surpass `v3
  force2` overall.

## Second live substrate

The Schaffer NWB lane is now real as well.

Evidence:

- [Schaffer canonical summary](/G:/flysim/outputs/derived/schaffer2023_nwb_canonical/schaffer2023_nwb_canonical_summary.json)
- [schaffer_nwb_canonical_dataset.py](/G:/flysim/src/analysis/schaffer_nwb_canonical_dataset.py)
- [schaffer_parity_harness.py](/G:/flysim/src/analysis/schaffer_parity_harness.py)

Current result:

- one real staged NWB session:
  - `2022_01_08_fly1.nwb`
- one canonical export:
  - `6` interval trials
  - aligned ROI `Df/F`
  - aligned ball motion
  - aligned `6`-channel behavioral state

Interpretation:

- Aimon is no longer the only live parity substrate.
- Schaffer is still small and partial, but the exporter seam is now verified on
  real NWB structure.
- The staged NWB lane now has direct matched-format matrix scoring as well as
  canonical export, so it is ready for the first real spontaneous-brain scoring
  pass once the next bundle-level adapter is added.
- That next adapter now exists:
  - [schaffer_spontaneous_fit.py](/G:/flysim/src/analysis/schaffer_spontaneous_fit.py)
  - [run_schaffer_spontaneous_fit.py](/G:/flysim/scripts/run_schaffer_spontaneous_fit.py)
- The first one-trial live Schaffer pilot is complete:
  - [pilot summary](/G:/flysim/outputs/metrics/schaffer_spontaneous_fit_pilot_trial000/schaffer_spontaneous_fit_summary.json)
  - same-trial result:
    - `mean_pearson_r = 0.1506`
    - `mean_nrmse = 0.1942`
    - `mean_abs_error = 0.00181`
    - `mean_sign_agreement = 0.5638`
- Schaffer staging has also expanded:
  - `3` real NWB sessions
  - `9` canonical interval trials
- Critical honesty constraint:
  - those sessions do not share one ROI output space
  - current ROI counts are `2170`, `1006`, and `2`
  - so honest Schaffer fitting must stay within one session unless a stronger
    cross-session ROI mapping is built

## Immediate next steps

1. Continue the held-out Aimon optimization sweep with separated
   `force_contact_force` and `force_forward_speed`, because force-2 was the
   first real improvement and the remaining weakness sits in held-out
   `B1269_forced_walk`.
   Current narrow question:
   - `contact2/forward1` failed
   - `forward2/contact1` partially recovered the gain
   - next likely Aimon axis is forward-dominant refinement rather than more
     contact gain
2. Use the Schaffer parity harness to prepare the first spontaneous-brain
   matched scoring pass on the staged NWB interval bundle.
   Current state:
   - first one-trial live Schaffer spontaneous-fit pilot is done
   - first within-session 2022 interval holdout is now running
3. Expand the Schaffer NWB staging set beyond one file now that the exporter
   seam is proven on real data.
4. Promote dataset-specific adapters for:
   - Ketkar `Data.zip`
   - Dallmann treadmill parquet files
5. Fit the spontaneous brain to those measurements directly.
6. Only then return to downstream decoder / embodiment interpretation as the
   primary line.

## March 30 systemic mismatch update

Two stronger systemic mismatch hypotheses are now explicit in the codebase.

### 1. Missing persistent state semantics

The exported Schaffer 2022 intervals are not six independent trials. They are
contiguous windows cut from one continuous session:

- `trial_000 29.6815 -> 299.9877 s`
- `trial_001 299.9877 -> 599.9753 s`
- `trial_002 599.9753 -> 899.9630 s`
- `trial_003 899.9630 -> 1199.9507 s`
- `trial_004 1199.9507 -> 1499.9384 s`
- `trial_005 1499.9384 -> 1799.9260 s`

The old Schaffer holdout harness reset the spontaneous brain between those
intervals. That is now treated as a real digital mismatch rather than a minor
evaluator quirk.

The continuity-preserving replay seam is now implemented in:

- [schaffer_spontaneous_fit.py](/G:/flysim/src/analysis/schaffer_spontaneous_fit.py)
- [run_schaffer_spontaneous_fit.py](/G:/flysim/scripts/run_schaffer_spontaneous_fit.py)

A corrected within-session rerun is in progress at:

- [schaffer_spontaneous_fit_2022_train4_test2_continuous](/G:/flysim/outputs/metrics/schaffer_spontaneous_fit_2022_train4_test2_continuous)

### 2. Missing imaging measurement physics

Both main public parity targets are imaging-space outputs, not raw membrane
voltage:

- Schaffer canonical modality is `roi_dff_timeseries`
- Aimon canonical traces are tagged `dff_like`

The old parity lane projected digital voltage features directly into those
targets with an instantaneous linear map. That is now treated as a second
systemic digital mismatch.

The shared optional observation model now exists in:

- [imaging_observation_model.py](/G:/flysim/src/analysis/imaging_observation_model.py)

It adds causal low-pass observation bases and is threaded into both live parity
lanes:

- [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py)
- [schaffer_spontaneous_fit.py](/G:/flysim/src/analysis/schaffer_spontaneous_fit.py)

The first held-out Aimon rerun with this observation basis is in progress at:

- [aimon_spontaneous_fit_train_to_test_v7_force2_obs0p5](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_train_to_test_v7_force2_obs0p5)

Current interpretation:

- the parity miss is no longer being treated as "probably chemistry"
- the strongest concrete digital mismatches now under test are:
  - missing continuous hidden-state semantics
  - missing imaging readout physics

## March 30 spontaneous-state acceptance tightening

The repo's spontaneous-state acceptance bar is now explicit and strict.

The only acceptable spontaneous endogenous state is one that emerges from:

- richer intrinsic cell dynamics
- graded transmission
- synaptic heterogeneity
- neuromodulatory state

Implication for the current parity program:

- the existing structured-background spontaneous surrogate remains useful for
  diagnosis and mismatch localization
- but it is explicitly disqualified as the final spontaneous mechanism
- any public-recording parity reached with that surrogate is diagnostic
  evidence, not final acceptance evidence
- `T201` is therefore mandatory replacement work, not optional cleanup

## March 30 exact replacement path

The exact path to the real goal is now fixed in:

- [endogenous_spontaneous_replacement_plan.md](/G:/flysim/docs/endogenous_spontaneous_replacement_plan.md)

Summary:

1. keep the current structured-background branch diagnostic-only
2. build a production backend whose spontaneous state comes from:
   - intrinsic cell dynamics
   - graded transmission
   - synaptic heterogeneity
   - neuromodulatory state
3. fit that backend to Aimon and Schaffer with a deliberately tiny readout
4. only resume downstream decoder / embodiment work after the backend clears
   held-out neural-parity gates
