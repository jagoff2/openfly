# Sensory Motor Mapping

## Public Anchors Used

Inputs:

- bilateral `LC4` pool from the public notebook as the visual proxy pool
- bilateral `JON` pool from the public figure notebook as the mechanosensory proxy pool

Outputs:

- `P9_oDN1` and `P9` for forward drive
- `DNa01` and `DNa02` for turning bias
- `MDN` for reverse

## Encoding

`vision.feature_extractor.RealisticVisionFeatureExtractor` computes:

- left/right visual salience from the public tracking-cell set used in FlyGym's connectome-constrained vision examples
- left/right flow from T4/T5 motion-sensitive cells

`bridge.encoder.SensoryEncoder` converts that plus body state into four pool rates:

- `vision_left`
- `vision_right`
- `mech_left`
- `mech_right`

These left/right rates are still an inferred engineering substitute, not a published biological mapping.

`brain.public_ids.collapse_sensor_pool_rates(...)` then collapses those four engineered rates into the two bilateral public input groups actually supported by the public neuron-ID anchors:

- `vision_bilateral`
- `mech_bilateral`

This replaced an earlier unfaithful midpoint split of the public `LC4` and `JON` ID lists into fake left/right hemispheres.

## Decoding

`bridge.decoder.MotorDecoder` computes:

- forward signal = tanh(mean(`P9_oDN1`, `P9`) / scale)
- turn signal = tanh((right DNa mean - left DNa mean) / scale)
- reverse signal = tanh(mean(`MDN`) / scale)

These signals are converted into the two-element descending drive expected by FlyGym's hybrid turning controller family.
The production decoder no longer adds a scripted idle locomotion floor: zero monitored motor output now yields exactly zero body command.

See `docs/motor_path_audit.md` for the current blocker under the strict production path: the bilateral public sensory anchors are a weak route into the monitored locomotor DN set, and the checked public notebook examples use direct `P9` stimulation as the explicit forward-walking baseline before adding `LC4` or `JON` co-stimulation.

## Descending-Only Expanded Readout

The repo now also includes an embodied experimental mode that keeps the calibrated visual splice fixed and broadens only the motor readout using public descending/efferent candidates:

- config: `configs/flygym_realistic_vision_splice_axis1d_descending_readout.yaml`
- detailed write-up: `docs/descending_readout_expansion.md`

In that branch, the decoder still keeps the fixed DN groups above, but adds supplemental descending populations mined from the public annotation supplement and selected by the body-free descending probe:

- supplemental forward groups:
  - `DNp103`
  - `DNp06`
  - `DNp18`
  - `DNp35`
- supplemental turn groups:
  - `DNpe056`
  - `DNp71`
  - `DNpe040`

Important boundary:

- these are all public `descending` + `efferent` annotations
- they are not optic-lobe relay cells
- they are still an experimentally selected readout, not a final claim that this is the one true biological motor interface

## Public P9 Context Mode

The repo now also supports an explicit experiment mode:

- `brain_context.mode: public_p9_context`

This injects direct public `P9_left` and `P9_right` drive on the brain side, matching the public notebook framing more closely than hidden decoder or body fallback.

See:

- `docs/public_p9_context_mode.md`

## Lateralized Sensory Anchor Status

The checked public artifacts currently support:

- bilateral `LC4`
- bilateral or subtype-grouped `JO` / `JON`

They do not expose a clean public `left` / `right` visual or mechanosensory anchor pool for turning.

See:

- `docs/lateralized_public_anchors.md`

## Inferred Lateralized Fallback

The repo now also has an explicitly inferred visual-side fallback:

- `scripts/probe_lateralized_visual_candidates.py`
- `docs/inferred_lateralized_visual_candidates.md`
- `src/vision/inferred_lateralized.py`

That probe found mirror-consistent left/right structure in several of the same visual cell families already used by the current extractor, especially:

- tracking-like: `TmY14`, `TmY15`, `TmY5a`, `TmY4`, `TmY18`, `TmY9`
- flow-like: `T5d`, `T5c`, `T4b`, `T5a`

This means the current extractor is not missing the relevant FlyVis families entirely. The main loss is that the current production path averages and collapses those responses back into bilateral public pools.

The new experimental helper in `src/vision/inferred_lateralized.py` can turn those per-eye candidate responses into an inferred `turn_bias`, but that helper does not yet define a faithful whole-brain neuron-ID mapping and is not part of the default production bridge.

## Inferred Visual Turn Experiment

The repo now also includes a separate brain-side experiment mode:

- `brain_context.mode: inferred_visual_turn_context`

See:

- `docs/inferred_visual_turn_plan.md`
- `docs/inferred_visual_turn_context_mode.md`

This mode uses the inferred per-eye visual `turn_bias` to drive asymmetric brain-side turning context while keeping the faithful default path unchanged.
