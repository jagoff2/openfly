# Spontaneous Mesoscale Validation On The Living-Brain Branch

## Goal

This note records the first explicit **mesoscale physiological validation**
slice for the living-brain line on `exp/spontaneous-brain-latent-turn`.

The target claim is deliberately limited:

- validate the living branch against public whole-brain spontaneous-state
  observables at the level of global modes, bilateral family structure,
  residual dynamics, and turn-linked heterogeneity
- do **not** claim full physiological validation

That boundary remains documented in:

- [spontaneous_state_full_validation_requirements.md](/G:/flysim/docs/spontaneous_state_full_validation_requirements.md)
- [spontaneous_dynamics_validation_memo.md](/G:/flysim/docs/spontaneous_dynamics_validation_memo.md)

## Public Anchors Used

Primary public sources for this slice:

- Aimon et al. 2023 eLife / Dryad:
  - walk-linked global state change
  - spontaneous vs forced walk comparison
  - turning-related spatial heterogeneity
- Mann et al. 2017:
  - intrinsic functional-network and bilateral mesoscale structure
- Schaffer et al. 2023:
  - residual high-dimensional, temporally structured activity after regressing
    behavior
- Turner et al. 2021:
  - structure-function correspondence as a mesoscale target for the living
    branch

Repo-side public dataset registry and access artifacts:

- [spontaneous_data_sources.py](/G:/flysim/src/brain/spontaneous_data_sources.py)
- [fetch_spontaneous_public_data.py](/G:/flysim/scripts/fetch_spontaneous_public_data.py)
- [public_spontaneous_dataset.py](/G:/flysim/src/analysis/public_spontaneous_dataset.py)
- [outputs manifest](/G:/flysim/outputs/metrics/spontaneous_public_dataset_aimon2023_dryad_manifest.json)
- [outputs access report](/G:/flysim/outputs/metrics/spontaneous_public_dataset_aimon2023_dryad_access_report.json)
- [Dryad local summary](/G:/flysim/external/spontaneous/aimon2023_dryad/local_dataset_summary.json)
- [Dryad manifest](/G:/flysim/external/spontaneous/aimon2023_dryad/spontaneous_public_dataset_aimon2023_dryad_manifest.json)
- [Dryad access report](/G:/flysim/external/spontaneous/aimon2023_dryad/spontaneous_public_dataset_aimon2023_dryad_access_report.json)

Important access note:

- public Dryad metadata is script-accessible
- Dryad direct file API endpoints return `401 Unauthorized`
- in this environment, browser-assisted and Zenodo-backed download succeeded for
  the full staged bundle:
  - [README.md](/G:/flysim/external/spontaneous/aimon2023_dryad/README.md)
  - [GoodICsdf.pkl](/G:/flysim/external/spontaneous/aimon2023_dryad/GoodICsdf.pkl)
  - `Walk_components.zip`
  - `Walk_anatomical_regions.zip`
  - `Additional_data.zip`
- the current local summary and digest checks are now aligned with the staged
  dataset root:
  - [outputs local summary](/G:/flysim/outputs/metrics/local_dataset_summary.json)
  - [dataset-root local summary](/G:/flysim/external/spontaneous/aimon2023_dryad/local_dataset_summary.json)
- `Walk_components.zip` is now treated as locally validated staged evidence
- the forced-vs-spontaneous public-timeseries comparison is no longer pending;
  it now runs as a real partial comparator

## Living-Branch Inputs

Matched living runs used here:

- target:
  - [summary.json](/G:/flysim/outputs/requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-203010/summary.json)
  - [run.jsonl](/G:/flysim/outputs/requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-203010/run.jsonl)
  - [activation_capture.npz](/G:/flysim/outputs/requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-203010/activation_capture.npz)
- no-target:
  - [summary.json](/G:/flysim/outputs/requested_2s_calibrated_no_target_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-204719/summary.json)
  - [run.jsonl](/G:/flysim/outputs/requested_2s_calibrated_no_target_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-204719/run.jsonl)
  - [activation_capture.npz](/G:/flysim/outputs/requested_2s_calibrated_no_target_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-204719/activation_capture.npz)

Validation code:

- [spontaneous_mesoscale_validation.py](/G:/flysim/src/analysis/spontaneous_mesoscale_validation.py)
- [run_spontaneous_mesoscale_validation.py](/G:/flysim/scripts/run_spontaneous_mesoscale_validation.py)
- tests:
  - [test_spontaneous_mesoscale_validation.py](/G:/flysim/tests/test_spontaneous_mesoscale_validation.py)
  - [test_public_spontaneous_dataset.py](/G:/flysim/tests/test_public_spontaneous_dataset.py)
  - [test_spontaneous_data_sources.py](/G:/flysim/tests/test_spontaneous_data_sources.py)

Recorded outputs:

- [summary.json](/G:/flysim/outputs/metrics/spontaneous_mesoscale_validation_summary.json)
- [components.csv](/G:/flysim/outputs/metrics/spontaneous_mesoscale_validation_components.csv)
- [target family table](/G:/flysim/outputs/metrics/spontaneous_mesoscale_target_family_turn_table.csv)
- [no-target family table](/G:/flysim/outputs/metrics/spontaneous_mesoscale_no_target_family_turn_table.csv)
- plots:
  - [onset curves](/G:/flysim/outputs/plots/spontaneous_mesoscale_onset_curves.png)
  - [bilateral corr histogram](/G:/flysim/outputs/plots/spontaneous_mesoscale_bilateral_corr_hist.png)
  - [turn-family correlations](/G:/flysim/outputs/plots/spontaneous_mesoscale_turn_family_corr.png)

## What Was Measured

### 1. Non-quiescent awake state

Check:

- living `target` and living `no_target` must both show nonzero spontaneous
  background rate and nonzero whole-brain spike fraction

Result:

- `target background_mean_rate_hz_mean = 0.03136`
- `no_target background_mean_rate_hz_mean = 0.03136`
- `target global_spike_fraction_mean = 0.001607`
- `no_target global_spike_fraction_mean = 0.001666`

Verdict:

- `pass`

### 2. Matched living baseline

Check:

- `target` and `no_target` must occupy the same spontaneous backbone, so target
  effects are not confounded with different awake-state regimes

Result:

- `background_mean_rate_hz_delta = 0.0`
- `background_active_fraction_delta = 0.0`
- `background_latent_mean_abs_hz_delta = 0.0`
- `global_spike_fraction_delta = -5.93e-05`

Verdict:

- `pass`

Interpretation:

- this confirms the comparison rule already recorded in the repo:
  living-vs-dead is a regime transition baseline, while living `target` vs
  living `no_target` is the correct mesoscale comparator

### 3. Walk-linked global modulation

Check:

- global activity should covary with locomotion and rise around locomotor onset,
  which is the main Aimon 2023 mesoscale anchor

Result:

- target:
  - `speed_voltage_std_corr = 0.2745`
  - `onset_voltage_std_delta = 0.9492`
  - `locomotor_onset_count = 2`
- no-target:
  - `speed_voltage_std_corr = 0.0185`
  - `onset_voltage_std_delta = 0.0`
  - `locomotor_onset_count = 0`

Verdict:

- `pass`

Interpretation:

- the living target condition shows a real walk-linked global state shift
- the no-target run is almost continuously locomotor-active, so it is a weak
  locomotor-onset assay in this slice rather than a negative result

### 4. Bilateral family coupling

Check:

- homologous left/right family voltages should remain positively coupled across
  the living regime, consistent with intrinsic-network mesoscale structure

Result:

- target:
  - `family_pair_count = 2947`
  - `mean_bilateral_voltage_corr = 0.3605`
- no-target:
  - `family_pair_count = 2947`
  - `mean_bilateral_voltage_corr = 0.3890`

Verdict:

- `pass`

### 5. Family structure exceeds a shift surrogate

Check:

- family-level functional structure should exceed a circular-shift surrogate,
  which preserves per-family autocorrelation while destroying shared alignment

Result:

- target:
  - observed mean abs pairwise corr = `0.3435`
  - shifted-surrogate mean abs pairwise corr = `0.1321`
  - structure ratio = `2.6001`
- no-target:
  - observed mean abs pairwise corr = `0.3601`
  - shifted-surrogate mean abs pairwise corr = `0.1290`
  - structure ratio = `2.7912`

Verdict:

- `pass`

Interpretation:

- the family-scale organization is not just smooth per-family dynamics
- shared mesoscale alignment remains well above a matched circular-shift null

### 6. Residual high-dimensional structure

Check:

- after regressing controller-linked covariates from monitored voltages,
  residual activity should retain nontrivial dimensionality rather than
  collapsing into one global mode

Result:

- target:
  - raw `pc1 = 0.3066`
  - residual `pc1 = 0.2150`
  - residual participation ratio = `4.7609`
- no-target:
  - raw `pc1 = 0.3035`
  - residual `pc1 = 0.2656`
  - residual participation ratio = `4.2650`

Verdict:

- `pass`

Interpretation:

- this is a real positive result against the Schaffer-style residual-structure
  criterion
- the residual is not giant, but it is clearly not gone

### 7. Residual temporal structure

Check:

- residual activity should remain temporally structured, not white-noise-like

Result:

- target residual lag-1 autocorrelation = `0.9153`
- no-target residual lag-1 autocorrelation = `0.9170`

Verdict:

- `pass`

### 8. Turn-linked spatial heterogeneity

Check:

- family asymmetries should not all move together; different families should
  show materially different relationships to turn drive

Result:

- target:
  - `turn_corr_std = 0.2528`
  - `turn_corr_abs_p90 = 0.4708`
- no-target:
  - `turn_corr_std = 0.2780`
  - `turn_corr_abs_p90 = 0.4451`

Strong positive target families in this slice include:

- `PLP013`
- `LTe01`
- `LC26`
- `IbSpsP`
- `LC13`
- `MTe50`

Strong negative target families include:

- `SMP429`
- `PVLP112b`
- `CB2804`
- `CB2453`
- `CB2635`
- `LTe33`

Verdict:

- `pass`

### 9. Connectome-to-functional family correspondence

Check:

- family-scale functional coupling should show at least weak positive
  correspondence to connectome-predicted coupling when both are aggregated at
  the same family scale
- because structural weights are extremely heavy-tailed, both raw-weight and
  `log1p`-weight summaries are recorded, but the `log1p` summary is the more
  interpretable mesoscale criterion

Result:

- raw structural-weight correlation:
  - target: `0.00998`
  - no-target: `0.00989`
- `log1p` structural-weight correlation:
  - target: `0.05449`
  - no-target: `0.05339`
- compared family-pair count:
  - target: `4,340,931`
  - no-target: `4,340,931`

Verdict:

- `pass`, but weak-effect

Interpretation:

- the old repo state was weaker here because this criterion was not evaluated
  at all
- the current living branch does show positive mesoscale structure-function
  correspondence, but only weakly
- that is still useful, because it means the awakened family-scale dynamics are
  not arbitrary with respect to the public connectome, but it is not yet strong
  enough to support a more ambitious claim than weak mesoscale alignment

## Public Forced vs Spontaneous Comparator

This slice now includes a real public forced-vs-spontaneous comparator built
from the staged Aimon dataset:

- [public comparator summary](/G:/flysim/outputs/metrics/aimon_forced_spontaneous_comparator_summary.json)
- [public comparator rows](/G:/flysim/outputs/metrics/aimon_forced_spontaneous_comparator_rows.csv)
- [mesoscale comparator rows](/G:/flysim/outputs/metrics/spontaneous_public_forced_vs_spontaneous_table.csv)
- [resolution note](/G:/flysim/docs/aimon_public_comparator_resolution.md)

Mechanistically, the correct public substrate turned out to be:

- `GoodICsdf.pkl` for experiment-level spontaneous and forced windows
- `Additional_data.zip`
  - `FunctionallyDefinedAnatomicalRegions/*.mat` for full regional traces
  - `AllRegressors/*.mat` for supporting walk/forced regressor metadata
- `Walk_anatomical_regions.zip` as a secondary source when a usable full-length
  trace exists there

It is not primarily a `Walk_components.zip` problem. `Walk_components.zip` is
now locally staged and digest-valid, but the decisive comparator seam is the
functional-region data in `Additional_data.zip`.

Honest comparator outcome:

- raw comparator status: `ok`
- mesoscale criterion status: `partial`
- candidate rows from public `GoodICsdf.pkl`: `4`
- usable distinct experiments: `2`
- valid distinct experiments:
  - `B350`
  - `B1269`
- dropped experiments:
  - `B1037` because spontaneous and forced windows overlap by `0.8958`
  - `B378` because spontaneous and forced windows overlap by `1.0`
- resulting public metrics:
  - `median_steady_walk_vector_corr = -0.2016`
  - `median_steady_walk_vector_cosine = -0.1868`
  - `median_steady_walk_rank_corr = -0.2013`
  - `median_spontaneous_prelead_fraction = 0.6241`
  - `median_spontaneous_minus_forced_prelead_delta = 0.01393`

Interpretation:

- the public comparator is now real, not missing
- the public overlap set is small and semantically messy
- the spontaneous-prelead side is directionally present
- the steady-state forced-vs-spontaneous regional similarity in the surviving
  subset is weak-to-negative, so this criterion remains partial rather than a
  clean pass

## Honest Verdict

This slice pushes the living branch to a real mesoscale validation milestone.

What is now supportable:

- the living branch is non-quiescent
- target and no-target live on the same awakened spontaneous backbone
- the branch shows locomotion-linked global modulation
- bilateral family coupling is positive at large scale
- family-level structure exceeds a circular-shift surrogate by about `2.6x` to
  `2.8x`
- residual monitored dynamics remain high-dimensional and temporally structured
- turn-linked activity is spatially heterogeneous across family asymmetries
- family-scale structure-function correspondence is weakly positive after
  log-weight aggregation against the public connectome

What is **not** yet supportable:

- full physiological validation
- neuron-identity physiological validation
- strong forced-vs-spontaneous walk parity
- strong connectome-predicted FC parity

So the strongest honest label now is:

- **living-branch mesoscale spontaneous-state validation: real, partial, and materially stronger than the earlier slice**

## Immediate Consequence For Future Work

The living branch is now strong enough that future spontaneous-state work should
be judged against these mesoscale criteria by default.

That changes the next-stage decoder work:

1. keep spontaneous state on
2. keep matched living `target` / `no_target` controls
3. do not regress to dead-brain comparators as the primary benchmark
4. add a forced-walk assay
5. align the repo’s forced-walk assay against the surviving public Aimon
   comparator subset instead of assuming every GoodICs row is usable
6. only then escalate claims beyond the current mesoscale boundary
