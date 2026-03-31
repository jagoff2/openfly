# Public Neural Measurement Dataset Status

## Current staged-source status

Authoritative machine-readable status:

- [stage status JSON](/G:/flysim/outputs/metrics/public_neural_measurement_stage_status.json)
- [stage status CSV](/G:/flysim/outputs/metrics/public_neural_measurement_stage_status.csv)

Current staging summary:

- `aimon2023_dryad`
  - fully staged local raw source
  - `manifest_file_count = 5`
  - `staged_file_count = 5`
- `schaffer2023_figshare`
  - manifest staged
  - spreadsheet plus one real staged NWB session
  - `manifest_file_count = 48`
  - staged artifacts currently include:
    - `datasets_for_each_figure.xlsx`
    - `2022_01_08_fly1.nwb`
- `ketkar2022_zenodo`
  - record and manifest staged
  - raw `Data.zip` not staged yet
  - `manifest_file_count = 1`
  - `staged_file_count = 0`
- `gruntman2019_janelia`
  - manifest staged
  - Figure 2 raw zip staged
  - `manifest_file_count = 2`
  - `staged_file_count = 1`
- `shomar2025_dryad`
  - metadata and file inventory staged
  - raw downloads blocked
- `dallmann2025_dryad`
  - metadata and file inventory staged
  - raw downloads blocked

## Current canonical exports

### Aimon 2023

Evidence:

- [bundle summary](/G:/flysim/outputs/derived/aimon2023_canonical/aimon2023_canonical_summary.json)
- [bundle JSON](/G:/flysim/outputs/derived/aimon2023_canonical/aimon2023_canonical_bundle.json)

Current result:

- `exported_experiment_count = 2`
- `trial_count = 4`
- surviving public experiments:
  - `B350`
  - `B1269`
- dropped public experiments:
  - `B1037` overlapping walk/forced windows
  - `B378` overlapping walk/forced windows

Interpretation:

- This is the first real living-brain parity substrate in canonical matched
  format.
- It gives a direct public whole-brain window bundle for spontaneous and forced
  walking.
- The first Aimon-specific scoring harness is now in place:
  - [aimon_parity_harness.py](/G:/flysim/src/analysis/aimon_parity_harness.py)
  - [test_aimon_parity_harness.py](/G:/flysim/tests/test_aimon_parity_harness.py)
- The first spontaneous-brain replay/projection harness has now completed a
  real live pilot on this substrate:
  - [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py)
  - [run_aimon_spontaneous_fit.py](/G:/flysim/scripts/run_aimon_spontaneous_fit.py)
  - [pilot summary](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_b1269_pilot_v2/aimon_spontaneous_fit_summary.json)

Current live-fit result:

- same-dataset B1269 pair pilot
- `fit_trial_ids`:
  - `B1269_spontaneous_walk`
  - `B1269_forced_walk`
- aggregate:
  - `mean_pearson_r = 0.8909`
  - `mean_nrmse = 0.0661`
  - `mean_abs_error = 0.00173`
  - `mean_sign_agreement = 0.8571`

Held-out result:

- [held-out summary](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_train_to_test_v1/aimon_spontaneous_fit_summary.json)
- fit split:
  - `B350_spontaneous_walk`
  - `B350_forced_walk`
- held-out `test` mean:
  - `mean_pearson_r = 0.0564`
  - `mean_nrmse = 0.3328`
  - `mean_abs_error = 0.00856`
  - `mean_sign_agreement = 0.4689`

Interpretation:

- The parity lane is no longer metadata-only or schema-only.
- The spontaneous brain can now be replayed and projected into the public Aimon
  measurement space with real saved scores.
- The first same-dataset pilot was not enough. Held-out generalization is
  currently weak and now defines the active optimization boundary.
- The first three held-out comparison points are now explicit:
  - [variant comparison](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_variant_comparison.json)
  - `v1` baseline:
    - `test_mean_pearson_r = 0.0564`
    - `test_mean_nrmse = 0.3328`
    - `test_mean_abs_error = 0.00856`
    - `test_mean_sign_agreement = 0.4689`
  - `v2` reduced basis / no asymmetry:
    - `test_mean_pearson_r = 0.0122`
    - `test_mean_nrmse = 0.3310`
    - `test_mean_abs_error = 0.00849`
    - `test_mean_sign_agreement = 0.4605`
  - `v3` doubled mechanosensory forcing:
    - `test_mean_pearson_r = 0.0620`
    - `test_mean_nrmse = 0.3117`
    - `test_mean_abs_error = 0.00821`
    - `test_mean_sign_agreement = 0.4660`
  - `v4` contact2 / forward1:
    - `test_mean_pearson_r = 0.0385`
    - `test_mean_nrmse = 0.3293`
    - `test_mean_abs_error = 0.00853`
    - `test_mean_sign_agreement = 0.4644`
  - `v5` forward2 / contact1:
    - `test_mean_pearson_r = 0.0565`
    - `test_mean_nrmse = 0.3155`
    - `test_mean_abs_error = 0.00824`
    - `test_mean_sign_agreement = 0.4723`
- Current read:
  - reduced projection capacity is not the main fix
  - stronger mechanosensory forcing is the first real held-out improvement
  - contact-only forcing is not the reason `v3` improved
  - forward-dominant forcing recovers most of the useful gain and currently has
    the best held-out sign agreement
  - the weak slice that still needs work is held-out `B1269_forced_walk`

### Gruntman 2019 Figure 2

Evidence:

- [bundle summary](/G:/flysim/outputs/derived/gruntman2019_figure2_canonical/gruntman2019_figure2_canonical_summary.json)
- [bundle JSON](/G:/flysim/outputs/derived/gruntman2019_figure2_canonical/gruntman2019_figure2_canonical_bundle.json)

Current result:

- `trial_count = 514`
- `skipped_condition_count = 540`
- modality:
  - single-neuron membrane potential
  - `20 kHz` sampling
  - raw single-bar motion traces

Interpretation:

- This is the first identified-neuron / early-visual raw-trace canonical export
  in the parity program.
- It is useful for forcing early motion-channel temporal structure before
  downstream embodied decoding is revisited.

### Schaffer 2023 NWB

Evidence:

- [bundle summary](/G:/flysim/outputs/derived/schaffer2023_nwb_canonical/schaffer2023_nwb_canonical_summary.json)
- [bundle JSON](/G:/flysim/outputs/derived/schaffer2023_nwb_canonical/schaffer2023_nwb_canonical_bundle.json)
- [Schaffer parity harness](/G:/flysim/src/analysis/schaffer_parity_harness.py)

Current result:

- `staged_session_count = 3`
- `exported_session_count = 3`
- `trial_count = 9`
- current staged/exported sessions:
  - `2018_08_24_fly3_run1.nwb`
  - `2019_04_25_fly1.nwb`
  - `2022_01_08_fly1.nwb`
- per-session contents preserved in canonical form:
  - ROI `Df/F` traces
  - aligned treadmill ball-motion trace
  - aligned behavioral-state matrix
  - NWB trial intervals as canonical trials

Interpretation:

- The second public parity substrate is now online in canonical form.
- This gives the program a behaving-fly whole-brain NWB lane beyond Aimon.
- It is still partial, but it is no longer a one-session toy substrate.
- It is no longer export-only. The staged NWB interval bundle now has a direct
  matrix scoring harness for matched model-vs-public comparisons.
- A first backend-connected spontaneous-fit path now exists too:
  - [schaffer_spontaneous_fit.py](/G:/flysim/src/analysis/schaffer_spontaneous_fit.py)
  - [run_schaffer_spontaneous_fit.py](/G:/flysim/scripts/run_schaffer_spontaneous_fit.py)
  - focused validation on the Schaffer fit seam: `11 passed`
- Important structural constraint:
  - Schaffer sessions do not share one ROI output space
  - current ROI counts are `2170`, `1006`, and `2`
  - honest fitting therefore has to stay within one session unless a stronger
    cross-session mapping is built

## Main blockers

- Dryad raw-file delivery remains hostile here:
  - direct API download path returns `401`
  - direct `file_stream` path returns `403`
- Ketkar, Dallmann, and Shomar still need dataset-specific exporters.
- No spontaneous-brain replay/projection harness has yet been run on the
  Ketkar, Dallmann, or Shomar substrates.
- Schaffer cross-session fitting is currently blocked by unmatched ROI spaces,
  so the correct next step is within-session holdout rather than pooled
  cross-session fitting.

## Immediate next moves

1. Continue the held-out Aimon optimization sweep by separating
   `force_contact_force` from `force_forward_speed` after the first successful
   force-2 improvement.
   Current state:
   - `contact2/forward1` regressed versus `force2`
   - `forward2/contact1` is the next decisive comparison
2. Finish the first within-session Schaffer interval holdout on the rebuilt
   2022 session using explicit `fit_trial_id` selection.
3. Stage or export the next accessible raw source after Aimon/Gruntman/Schaffer:
   - otherwise Ketkar `Data.zip`
4. Start direct measurement-parity optimization on the spontaneous brain before
   returning to downstream decoder interpretation.

## March 30 systemic status update

The parity miss is now narrowed by two stronger digital mismatches that cut
across datasets.

### Session continuity mismatch

The 2022 Schaffer exported intervals are contiguous pieces of one session, but
the old replay path reset the spontaneous brain at each interval boundary. That
continuity mismatch is now patched in the live fit harness and is being measured
directly with a corrected within-session rerun.

### Imaging observation-model mismatch

Schaffer targets are explicit `dff`, and Aimon canonical traces are tagged
`dff_like`. The parity lane now has an optional causal imaging observation basis
so the fit no longer assumes an instantaneous voltage-to-imaging projection.

Current active probes:

- [schaffer_spontaneous_fit_2022_train4_test2_continuous](/G:/flysim/outputs/metrics/schaffer_spontaneous_fit_2022_train4_test2_continuous)
- [aimon_spontaneous_fit_train_to_test_v7_force2_obs0p5](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_train_to_test_v7_force2_obs0p5)
