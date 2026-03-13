## Broad Descending Monitoring And First Observational Neck-Output Atlas

This document records the first concrete step after `docs/neck_output_mapping_strategy.md`:

- add monitoring-only support for a broad descending/efferent population
- run the current strongest embodied branch again
- summarize which descending groups track target bearing, frontal acquisition, and forward progression

This is **observational**, not yet causal.

## Why this was necessary

Up to this point, the embodied branch was being interpreted mainly through:

- a small fixed DN readout
- plus a small manually selected supplemental descending set

That was enough to get the current strongest branch running, but not enough to
answer the next question cleanly:

- what is the broader neck-output population actually doing during approach,
  pursuit, loss of target, and reorientation?

So the first step was to widen monitoring without widening control.

## Implementation

### Decoder-side monitoring support

Updated:

- `src/bridge/decoder.py`

New capability:

- monitor a broad population set for logging only
- without yet using all monitored populations for control

Config fields:

- `monitor_candidates_json`
- `monitor_cell_types`

For each monitored label, the decoder now logs:

- `monitor_<label>_left_hz`
- `monitor_<label>_right_hz`
- `monitor_<label>_bilateral_hz`
- `monitor_<label>_right_minus_left_hz`

### Configs

Added:

- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_monitored.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_monitored_no_target.yaml`

These keep the current strongest control branch fixed and only widen
monitoring.

### Summary script

Added:

- `scripts/summarize_descending_monitoring.py`

This script computes, for each monitored label:

- target vs no-target bilateral-rate change
- target vs no-target asymmetry change
- correlation of bilateral rate with:
  - target frontalness
  - forward speed
  - total drive
- correlation of asymmetry with:
  - target bearing
  - yaw rate

## Validation

Local validation:

```bash
python -m pytest tests/test_bridge_unit.py tests/test_closed_loop_smoke.py -q
python -m py_compile src/bridge/decoder.py scripts/summarize_descending_monitoring.py
```

Result:

- `18 passed`

## Matched embodied runs

### Target + real brain

- `outputs/requested_2s_splice_uvgrid_calibrated_monitored_target/flygym-demo-20260311-134126/demo.mp4`
- `outputs/requested_2s_splice_uvgrid_calibrated_monitored_target/flygym-demo-20260311-134126/run.jsonl`

### No target + real brain

- `outputs/requested_2s_splice_uvgrid_calibrated_monitored_no_target/flygym-demo-20260311-135635/demo.mp4`
- `outputs/requested_2s_splice_uvgrid_calibrated_monitored_no_target/flygym-demo-20260311-135635/run.jsonl`

Summary artifacts:

- `outputs/metrics/descending_monitor_neck_output_atlas.csv`
- `outputs/metrics/descending_monitor_neck_output_atlas.json`

## Main result

The first broad monitoring pass supports a distributed, not single-neuron,
interpretation of the neck-output side.

There is no single label that cleanly explains everything.

Instead, different labels appear to contribute to different aspects of the
behavior:

- target-conditioned activation
- bearing/asymmetry locking
- forward/frontal locking

## Top target-conditioned labels

From `outputs/metrics/descending_monitor_neck_output_atlas.json`:

Top labels by bilateral target-minus-no-target increase:

1. `DNpe016`
   - delta bilateral: `+7.75 Hz`
2. `DNae002`
   - delta bilateral: `+5.75 Hz`
3. `DNp71`
   - delta bilateral: `+4.50 Hz`
4. `DNpe040`
   - delta bilateral: `+2.75 Hz`
5. `DNpe056`
   - delta bilateral: `+2.00 Hz`
6. `DNg97`
   - delta bilateral: `+1.25 Hz`

Interpretation:

- some descending groups are clearly more active with a moving target than
  without one
- that means the current branch is using a wider neck-output population than
  the small fixed decoder readout would suggest

## Top bearing-locked labels

Top labels by asymmetry correlation with target bearing:

1. `DNp71`
   - `corr(asym, target_bearing) = 0.1611`
2. `DNpe040`
   - `0.1435`
3. `DNpe056`
   - `0.1001`
4. `DNg97`
   - `0.0920`
5. `DNpe031`
   - `0.0693`

Interpretation:

- `DNp71`, `DNpe040`, and `DNpe056` are the clearest current candidates for
  target-side-sensitive turning structure in the broader descending population
- these correlations are not huge, which reinforces that the code is
  distributed and the current `2 s` run is still short

## Top forward/frontal-locked labels

Top labels by bilateral correlation with forward speed:

1. `DNg97`
   - `corr(bilateral, forward_speed) = 0.0547`
   - `corr(bilateral, frontalness) = 0.0770`
2. `DNp103`
   - `0.0516`
   - `0.0655`
3. `DNp18`
   - `0.0442`
   - `0.1520`

Interpretation:

- `DNg97`, `DNp103`, and `DNp18` remain plausible forward/propulsion-linked
  components in the current branch
- `DNp18` is especially interesting because its bilateral rate tracks target
  frontalness more strongly than the others in this first pass

## Important limitation

These correlations are modest.

That matters.

The correct interpretation is not:

- "we found the one true pursuit neuron"

The correct interpretation is:

- the current branch appears to use a distributed descending code
- some groups are more target-conditioned
- some groups are more side/bearing locked
- some groups are more frontal/forward locked

That is exactly why the next step should be a causal atlas rather than more
manual guesswork.

## Why this is still useful

This first monitoring pass already narrows the next causal work:

### Good first candidates for turn-oriented perturbation

- `DNp71`
- `DNpe040`
- `DNpe056`
- `DNpe031`

### Good first candidates for forward-oriented perturbation

- `DNg97`
- `DNp103`
- `DNp18`

### Good first candidates for target-conditioned gating / stop-turn behavior

- `DNpe016`
- `DNae002`

These are now the right groups to prioritize in the first causal motor atlas.

## Honest conclusion

This first observational atlas does not solve the neck-output mapping.

What it does do is:

- widen the project's view from a tiny selected output subset
- show that the current branch is using a broader descending code
- identify the first concrete group candidates for causal perturbation

That is enough to justify the next phase:

- build the first causal descending motor-response atlas

## Update After The First Causal Atlas

That next phase is now complete.

See:

- `docs/descending_motor_atlas.md`

The observational atlas predictions were partially confirmed:

- forward candidates `DNg97`, `DNp103`, and `DNp18` do produce the strongest
  bilateral locomotor effects in the present stack
- turn candidates `DNpe040` and `DNpe056` do produce mirrored yaw effects

They were also partially corrected:

- `DNp71` is active but not a clean mirrored turn driver in the present stack
- `DNae002` and `DNpe031` did not produce useful causal effects in this first
  pass

So the observational atlas was useful as a narrowing step, but it was not
enough on its own. The causal atlas is now the stronger basis for the next
decoder-fitting phase.
