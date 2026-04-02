# Timing Mismatch Root Cause

Date: 2026-04-01

## Current conclusion

The continued timing mismatch is not primarily explained by "the backend is still too simple."
There are multiple higher-leverage timing faults and invalid assumptions in the current public-parity lane.

The strongest causes found so far are:

1. **Aimon export timebase is fabricated at 100 Hz**
2. **Aimon behavior regressors are used raw, even though the paper says they were convolved with the GCaMP spike response and processed through the same `dF/F` pipeline as fluorescence**
3. **The public body-feedback derivative path is acausal and non-physical**
4. **The routed-only parity config contains a duplicated `encoder:` block, silently overriding intended gains**
5. **The public mechanosensory subgroup mapping is currently slice-based rather than explicitly identity-based**
6. **The backend's `modulatory_exafference_state` is not actually driven by exafferent sensory input**

These issues are sufficient to explain why repeated backend-only tuning has produced only tiny or misleading timing changes.

## Ranked findings

### 1. Aimon export hard-codes a fake 100 Hz timebase

Evidence:

- [aimon_canonical_dataset.py](/G:/flysim/src/analysis/aimon_canonical_dataset.py)
  - `export_aimon_canonical_dataset(..., sampling_rate_hz: float = 100.0, ...)`
  - `full_time = np.arange(region_matrix.shape[1], dtype=np.float32) / float(sampling_rate_hz)`

Why this matters:

- The Aimon paper states that whole-brain recording speed varied by experiment and preparation, starting at `2` or `5` Hz and increasing only when possible, up to `98` Hz.
- A fixed synthetic `100 Hz` timebase therefore distorts:
  - event timing
  - finite differences
  - observation low-pass behavior
  - train/test window boundaries in seconds

Implication:

- Current pointwise timing scores on Aimon are partially anchored to a fabricated time axis.

Primary source:

- Aimon et al. 2023 / PMC methods, lines around recording speed and behavior regression:
  - [PMC article]https://pmc.ncbi.nlm.nih.gov/articles/PMC10168698/

### 2. Aimon behavioral regressors are used raw instead of imaging-space transformed

Evidence:

- [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py)
  - `_trial_regressor_values(...)` loads the stored walk regressor, takes `abs(...)`, normalizes by `max_abs`, and uses that directly.
- [public_body_feedback.py](/G:/flysim/src/analysis/public_body_feedback.py)
  - `public_body_feedback_from_aimon_regressor(...)` builds body channels directly from this raw normalized regressor.

Why this matters:

- The Aimon paper explicitly states that behavioral time series were convolved with the single-spike response of the GCaMP variant used and subjected to the same `ΔF/F` procedure as the fluorescence time series before regression.
- The current harness does not do that.

Implication:

- We are comparing and injecting the wrong temporal object.
- Even a perfect recurrent backend will struggle to match calcium timing if its public forcing channels are still in raw behavior space.

Primary source:

- [PMC article]https://pmc.ncbi.nlm.nih.gov/articles/PMC10168698/

### 3. The public body-feedback derivative path is both acausal and non-physical

Evidence:

- [public_body_feedback.py](/G:/flysim/src/analysis/public_body_feedback.py)
  - `_finite_difference(...)` uses a centered difference for interior samples:
    - `values[i+1] - values[i-1]`
  - `public_body_feedback_from_aimon_regressor(...)` uses that derivative as `forward_accel`
- [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py)
  - `_sensor_pool_rates_from_regressor_value(...)` applies the public body feedback at the previous sample index during forward integration

Why this matters:

- For interior samples, centered difference uses a future point relative to the simulated interval. That is acausal leakage.
- The derivative is taken on a normalized regressor, not a physical speed signal.
- Measured magnitudes are large:
  - `B350` normalized-regressor `|accel|` percentiles: `p50=0.77`, `p90=10.40`, `p99=24.37`, `max=27.74`
  - `B1269` normalized-regressor `|accel|` percentiles: `p50=0.75`, `p90=2.95`, `p99=33.49`, `max=40.13`
- [encoder.py](/G:/flysim/src/bridge/encoder.py) then multiplies this with `accel_gain_hz`, producing unrealistically large mechanosensory pulses.

Implication:

- The body-feedback lane can easily improve amplitude or baseline while still corrupting timing.

### 4. The routed-only parity config has a real duplicate-key bug

Evidence:

- [brain_endogenous_public_parity_routed_only.yaml](/G:/flysim/configs/brain_endogenous_public_parity_routed_only.yaml)
  contains two top-level `encoder:` mappings.
- YAML loading keeps the last mapping and discards the first one.
- The loaded config therefore becomes:
  - `accel_gain_hz = 18.0`
  - `state_gain_hz = 18.0`
  - `transition_gain_hz = 22.0`
  - `stop_suppression_hz = 8.0`
  - `exafference_gain_hz` missing, therefore defaulting to `0.0`

Why this matters:

- The intended body-feedback experiment did not actually use the intended encoder gains.
- The nominal exafference term was disabled in the routed-only config.

Implication:

- At least part of the recent body-feedback interpretation is confounded by a config bug.

### 5. JON subgroup mapping is currently order-based, not identity-based

Evidence:

- [public_ids.py](/G:/flysim/src/brain/public_ids.py)
  - `JON_CE_IDS = JON_ALL_IDS[:70]`
  - `JON_F_IDS = JON_ALL_IDS[70:130]`
  - `JON_DM_IDS = JON_ALL_IDS[130:]`

Why this matters:

- Unless `JON_ALL_IDS` is already guaranteed to be concatenated in exact `CE`, `F`, `D_m` order from a verified public source, this is a fabricated split.
- The current code does not load subgroup membership from an explicit public annotation table.

Implication:

- The new mechanosensory subgroup routing may be targeting the wrong neurons, which can alter timing while still improving scale.

### 6. The backend's exafference state is not driven by exafferent sensory input

Evidence:

- [pytorch_backend.py](/G:/flysim/src/brain/pytorch_backend.py)
  - `_update_neuromodulatory_state(...)` updates both:
    - `modulatory_arousal_state`
    - `modulatory_exafference_state`
  - both are driven by the same internal `drive` computed from modulatory population activity
  - neither is directly driven by public body-feedback exafferent input

Why this matters:

- The code path named `exafference` is currently not an exafferent sensory regulator.
- It is an internally generated modulatory state.

Implication:

- The mechanism we expected to stabilize sustained forced/exafferent state is not actually wired to exafferent evidence.

## External constraint that is real but not the main excuse

The Aimon public trial structure is still thin for exact temporal forcing:

- [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py)
  uses only the public walk regressor for Aimon body feedback.
- That regressor can help identify walk state and coarse drive level.
- It does not supply rich per-leg or true proprioceptive timing.

This means:

- yes, public data scarcity is real
- but it does **not** explain away the code and evaluation faults above

## What the results now mean

The recent body-feedback result:

- [v4 body-feedback](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v4_bodyfeedback/aimon_spontaneous_fit_summary.json)

versus the prior routed continuity baseline:

- [v2 continuity](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v2_cont/aimon_spontaneous_fit_summary.json)

showed:

- better amplitude / scale control
- worse timing

That is now consistent with the code audit:

- body feedback is a real missing ingredient
- but the current body-feedback implementation has timing faults and configuration errors
- so the experiment was informative, but not yet mechanistically clean

## Current root-cause ranking

1. Fixed synthetic Aimon `100 Hz` timebase
2. Missing GCaMP-convolved / `dF/F`-matched behavior regressor transform
3. Acausal and non-physical derivative-driven body feedback
4. Duplicate-`encoder` config override bug
5. Fabricated or at least unverified JON subgroup split
6. Exafference state not actually tied to exafferent input
7. Only after those: remaining recurrent-core physiology limits

## Immediate next actions

1. Fix the routed-only parity config duplication and restore an explicit single encoder block.
2. Remove acausal centered differences from public body-feedback construction.
3. Replace normalized-regressor acceleration with a bounded causal transform.
4. Add dataset-side Aimon behavior-to-imaging transform support:
   - experiment-specific sampling rate when available
   - GCaMP-like causal kernel
   - `dF/F`-matched preprocessing for behavior regressors used in timing assays
5. Treat current JO subgroup mapping as provisional until replaced by explicit public subgroup membership evidence.
6. Wire exafferent backend state to actual exafferent sensory drive if that mechanism is to remain in the backend.
