# Motor Path Audit

This document records the first strict-brain-only audit after removing the decoder idle drive, the minimum positive drive floor, the fabricated left/right split of bilateral public sensory anchors, and the upstream zero-drive locomotion leak.

## Reproduction

Run:

```bash
python scripts/audit_motor_path.py
```

Artifacts:

- `outputs/metrics/motor_path_audit.json`
- `outputs/metrics/motor_path_audit_sweeps.csv`

The default audit uses the short strict-production log:

- `outputs/brain_only_fastvision_test_v2/logs/flygym-demo-20260308-150052.jsonl`

## What Was Checked

1. The bilateral public input rates actually seen in the strict closed-loop production run.
2. Whether those observed bilateral public inputs produce any monitored motor output when held constant in the whole-brain backend.
3. Whether the public `LC4` and `JON` anchor pools have direct structural connectivity to the monitored locomotor descending-neuron readouts.
4. A positive control: direct public `P9` stimulation matching the public notebook's forward-walking setup.

## Key Findings

### 1. The strict production run is under-driving the monitored locomotor readouts

From `outputs/metrics/motor_path_audit.json`:

- observed strict bilateral vision input was about `77.7 Hz`
- observed strict bilateral mechanosensory input averaged about `14.7 Hz`
- in the first `20 ms` and `100 ms`, those inputs produced exactly `0` monitored motor output
- even when the same observed bilateral input is held for `1000 ms`, the response stays weak:
  - `forward_left = 0.0 Hz`
  - `forward_right = 0.0 Hz`
  - `turn_left = 7.0 Hz`
  - `turn_right = 1.5 Hz`
  - `reverse = 0.0 Hz`

That is consistent with the short real WSL strict diagnostics showing `nonzero_motor_cycles = 0`.

### 2. The backend is not dead; direct public locomotor drive works

The positive-control case in `outputs/metrics/motor_path_audit_sweeps.csv` is:

- `public_p9_direct_100hz_1000ms`

That direct public `P9` input produces robust monitored output:

- `forward_left = 33.0 Hz`
- `forward_right = 32.5 Hz`
- first forward spikes arrive at about `10-12 ms`

So the current blocker is not that the Torch whole-brain backend or the decoder is numerically broken. The blocker is the sensory-to-motor mapping being too weak or too mismatched under the strict public-input path.

### 3. The public notebook uses `P9` as the explicit forward-walking baseline

The checked-in public notebook at `external/fly-brain/code/paper-phil-drosophila/example.ipynb` does the following:

- first: `P9s_100Hz` to simulate forward walking
- then: `P9_LC4s`
- then: `P9_JO_CE_bilateral`

So the public examples are not showing `LC4`-only or `JON`-only sensory drive causing the locomotor behavior by themselves. They are showing sensory co-stimulation on top of an externally injected locomotor context.

This matters because the strict production path currently removes all non-brain locomotor scaffolding and also does not inject any public `P9` context.

### 4. The current public sensory pools do not connect directly to the monitored motor readouts

From `outputs/metrics/motor_path_audit.json`:

- `vision_bilateral` (`LC4`) has `0` direct edges to every monitored locomotor output group
- `mech_bilateral` (`JON`) also has `0` direct edges to every monitored locomotor output group

They only reach the monitored locomotor outputs by hop `2`.

That does not make the path invalid, but it does make it a weaker and longer route than a direct drive.

### 5. The current strict public-input path discards stimulus laterality before the whole-brain model

The production backend now correctly uses bilateral public anchor pools in `src/brain/public_ids.py`:

- `vision_bilateral`
- `mech_bilateral`

This is more faithful than the earlier fake midpoint left/right split. But it also means the whole-brain backend is no longer receiving any externally imposed left/right sensory asymmetry from those pools.

So:

- any turning asymmetry that appears now is an internal network asymmetry
- it is not a stimulus-locked left/right steering signal

This is a structural reason why visually guided turning parity is currently out of reach with the present public anchor set.

## Interpretation

The strict production blocker is now much clearer:

1. `LC4` and `JON` as currently used are weak bilateral public sensory proxies for this closed-loop task.
2. The monitored locomotor descending-neuron set can respond, but it responds strongly when given direct locomotor context such as public `P9` stimulation, not under the current short bilateral sensory-only closed loop.
3. The strict path is therefore honest but under-powered.

## Consequences For The Repo

The current strict production path should be interpreted as:

- real FlyGym realistic vision
- real public whole-brain backend
- brain-only motor semantics
- no meaningful locomotor output yet under the present public sensory-to-motor mapping

Earlier demo videos that showed persistent walking are no longer representative of the current default semantics.

## Recommended Next Work

1. Keep the strict brain-only default in place.
2. Do not restore decoder or body-side fallback locomotion.
3. Split future work into two clearly labeled tracks:
   - `strict_public_sensory`: only public bilateral sensory anchors, no injected locomotor context
   - `public_p9_context`: explicit public `P9` locomotor context injected on the brain side, documented as a public experiment analogue rather than an endogenous closed-loop result
4. Search for truly lateralized public sensory anchors before attempting visually guided turning again.

Both follow-up items now exist in the repo as:

- `docs/public_p9_context_mode.md`
- `docs/lateralized_public_anchors.md`
