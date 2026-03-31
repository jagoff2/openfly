# Public Neural Measurement Schema

This is the canonical matched-format schema for the public neural measurement
parity program.

It exists to force all public datasets and all spontaneous-brain replay/fitting
harnesses into one comparable representation before any parity claim is made.

## Design constraints

- must support whole-brain, identified-neuron, and treadmill-linked datasets
- must support raw public IDs when available
- must support group-level fallback when exact neuron IDs are absent
- must preserve stimulus definitions explicitly
- must preserve behavior state explicitly
- must preserve normalization choices explicitly
- must support exact train/validation/test splits

## Dataset-level fields

- `dataset_key`
- `citation_label`
- `modality`
  - examples: `calcium`, `voltage`, `nwb`, `component_timeseries`
- `normalization`
  - examples:
    - `trace_transform: dff`
    - `zscore_within_trial: true`
    - `baseline_window_s: [-1.0, 0.0]`
- `identity_strategy`
  - examples:
    - `primary: exact_neuron_id`
    - `fallback: cell_type`
    - `grouping: population_pool`
- `trials`

## Trial-level fields

- `trial_id`
- `split`
  - required values: `train`, `val`, `test`
- `behavior_context`
  - examples: `spontaneous_walk`, `forced_walk`, `optic_flow`, `gap_crossing`
- `stimulus`
- `timebase_path`
- `traces`
- `behavior_paths`
  - examples:
    - `forward_velocity_path`
    - `yaw_velocity_path`
    - `walk_state_path`
- `metadata`

## Stimulus-level fields

- `stimulus_family`
  - examples: `optic_flow`, `bar_motion`, `parallax`, `closed_loop_gain`
- `stimulus_name`
  - examples: `front_to_back`, `back_to_front`, `counterphase_flicker`
- `units`
- `parameters`
  - examples:
    - `speed_mm_s`
    - `temporal_frequency_hz`
    - `spatial_wavelength_deg`
    - `gain`

## Trace-level fields

- `trace_id`
- `recorded_entity_id`
- `recorded_entity_type`
  - preferred order:
    - `exact_neuron_id`
    - `cell_type`
    - `cell_family`
    - `region_component`
    - `population_pool`
- `hemisphere`
- `sampling_rate_hz`
- `units`
- `transform`
- `values_path`
- `time_path`
- `flywire_mapping_key`
- `flywire_mapping_confidence`
- `tags`

## Identity mapping policy

Priority order:

1. exact neuron identity
2. stable cell type
3. stable cell family
4. atlas region or component
5. explicit pooled population

When exact mapping is unavailable:

- keep the public identity intact
- record the mapping fallback explicitly
- never silently upcast a pooled public trace into a fake exact-neuron label

## Normalization policy

Every dataset adapter must declare:

- original public units
- in-repo transform used for fitting
- whether normalization is within-trial, within-session, or global

Accepted examples:

- raw `dF/F`
- session-z-scored `dF/F`
- rate-normalized spike proxy
- component score z-scaling

## Split policy

Every dataset adapter must emit exact splits.

Default policy when not given by the public source:

- split by session or fly, not by random frame
- keep all frames from a single session in one split
- use `train/val/test = 70/15/15` at session granularity unless the dataset is
  too small, in which case record the exception explicitly

## First harness implications

The first harness layer should target:

1. whole-brain spontaneous/walk state datasets
   - Aimon 2023
   - Schaffer 2023
2. identified early visual neuron datasets
   - Ketkar 2022
   - Gruntman 2019
3. treadmill/body-feedback datasets
   - Dallmann 2025
   - Shomar 2025

The corresponding code entry points are:

- [public_neural_measurement_sources.py](/G:/flysim/src/brain/public_neural_measurement_sources.py)
- [public_neural_measurement_dataset.py](/G:/flysim/src/analysis/public_neural_measurement_dataset.py)
- [public_neural_measurement_schema.py](/G:/flysim/src/analysis/public_neural_measurement_schema.py)
- [fetch_public_neural_measurements.py](/G:/flysim/scripts/fetch_public_neural_measurements.py)
