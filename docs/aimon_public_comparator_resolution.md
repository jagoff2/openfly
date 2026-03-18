# Aimon Public Comparator Resolution

## Outcome

The public forced-vs-spontaneous comparator is now live and reproducible on the
staged Aimon 2023 dataset under:

- [external/spontaneous/aimon2023_dryad](/G:/flysim/external/spontaneous/aimon2023_dryad)
- [aimon_forced_spontaneous_comparator_summary.json](/G:/flysim/outputs/metrics/aimon_forced_spontaneous_comparator_summary.json)
- [aimon_forced_spontaneous_comparator_rows.csv](/G:/flysim/outputs/metrics/aimon_forced_spontaneous_comparator_rows.csv)

The comparator is integrated into the living-branch mesoscale validator through:

- [aimon_public_comparator.py](/G:/flysim/src/analysis/aimon_public_comparator.py)
- [spontaneous_mesoscale_validation.py](/G:/flysim/src/analysis/spontaneous_mesoscale_validation.py)
- [run_aimon_forced_spontaneous_comparator.py](/G:/flysim/scripts/run_aimon_forced_spontaneous_comparator.py)
- [run_spontaneous_mesoscale_validation.py](/G:/flysim/scripts/run_spontaneous_mesoscale_validation.py)

## What The Real Issue Was

The earlier blocker was misidentified.

- `Walk_components.zip` was not the decisive substrate for the public
  forced-vs-spontaneous mesoscale comparator.
- The actual required public substrate was `Additional_data.zip`, specifically:
  - `Additional_data/FunctionallyDefinedAnatomicalRegions/*.mat`
  - `Additional_data/AllRegressors/*.mat`
- `Walk_anatomical_regions.zip` is useful, but for the overlapping experiments
  it contains clipped walk segments rather than the full-length regional traces
  needed for honest spontaneous-vs-forced window comparison.

So the true comparator path is:

1. `GoodICsdf.pkl` for experiment metadata and walk/forced window bounds
2. `Additional_data.zip` for full-length functional-region traces and
   regressor files
3. optional `Walk_anatomical_regions.zip` as a secondary source or cross-check

## Walk Components Resolution

`Walk_components.zip` is now treated as resolved and validated staged evidence.

Local validation in the refreshed dataset summary shows:

- size: `186,935,529`
- expected size: `186,935,529`
- digest algorithm: `sha256`
- digest match: `true`
- zip validity: `true`

Evidence:

- [local_dataset_summary.json](/G:/flysim/outputs/metrics/local_dataset_summary.json)
- [dataset-local summary](/G:/flysim/external/spontaneous/aimon2023_dryad/local_dataset_summary.json)

## Comparator Behavior

The public comparator now produces an honest non-blocked result:

- `status = ok`
- `n_candidate_rows = 4`
- `n_experiments_used = 2`
- `n_valid_vector_corr = 2`
- `n_valid_prelead_fraction = 1`

Usable experiments:

- `B350`
- `B1269`

Dropped experiments:

- `B1037`
  - reason: `overlapping_walk_forced_windows`
  - overlap fraction: `0.8958`
- `B378`
  - reason: `overlapping_walk_forced_windows`
  - overlap fraction: `1.0`

This drop is correct. Those public walk and forced windows overlap too strongly
to support an honest forced-vs-spontaneous comparison.

## Current Comparator Result

The current public mesoscale forced-vs-spontaneous result is partial, not a
pass.

Median metrics on the usable public experiments are:

- steady walk vector correlation: `-0.2016`
- steady walk vector cosine: `-0.1868`
- steady walk rank correlation: `-0.2013`
- spontaneous prelead fraction: `0.6241`
- spontaneous minus forced prelead delta: `0.01393`

Interpretation:

- the public comparator is working
- spontaneous-leading onset structure is present
- but steady spontaneous-vs-forced regional similarity is weak/mixed in the
  currently usable public subset
- so this criterion is now an evidence-producing partial, not a missing slice

## Code-Level Fixes

The main fixes were:

- stop blocking on `Walk_anatomical_regions.zip`
  - it is now optional for the comparator path
- allow valid windowed comparison even when one of the public regressor file
  pointers is missing or unusable, as long as `GoodICsdf` provides valid window
  bounds into full-length regional traces
- filter `NaN` rows before correlation/cosine/rank calculations
- surface overlap-based drops explicitly instead of silently treating them as
  missing-data failures
- align the standalone comparator CLI to the same comparator used by the
  mesoscale validator

## Validation

Focused validation for the repaired public-data slice:

- `python -m pytest tests/test_public_spontaneous_dataset.py tests/test_spontaneous_data_sources.py tests/test_aimon_components_summary.py tests/test_aimon_public_comparator.py tests/test_spontaneous_mesoscale_validation.py -q`
- result: `24 passed`

The same recurring Windows pytest temp-dir cleanup warning still appears after
successful completion. It is unchanged and non-blocking.
