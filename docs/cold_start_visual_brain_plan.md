# Cold-Start Visual Brain Plan

## Objective

Replace the failed sparse-twitch strict bridge with a cold-startable, vision-driven path that still uses:

- the real FlyGym realistic-vision input path
- the real public whole-brain backend
- the real brain decoder output path

without restoring hidden body fallback or direct turning-output forcing.

This document now sits below the broader splice reset in:

- `docs/visual_splice_strategy.md`

The `inferred_visual_p9_context` work is still diagnostic only. The next substantive iteration should be body-free and should focus on the visual splice itself.

Current body-free splice status:

- `docs/splice_probe_results.md`

The first body-free splice probe now shows that the project can ground a wide visual splice by exact shared `cell_type` + `side` using the official FlyWire annotation supplement. That is a better boundary than the old scalar bridge.

It also shows that:

- grouped boundary amplitudes can be matched well
- left/right asymmetry is not yet preserved robustly
- short-window downstream motor recruitment is still absent

Follow-up body-free probe status:

- signed boundary input is now implemented
- coarse spatial bins are now implemented
- a `100 ms` body-free signed+spatial probe now produces condition-dependent downstream motor asymmetry
- state-based boundary readouts are now implemented
- the current best tested body-free splice point is:
  - `4` spatial bins
  - signed current with `max_abs_current = 120`
  - see `outputs/metrics/splice_probe_calibration_curated.json`

Further follow-up body-free status:

- deeper relay targets are now probed explicitly:
  - `outputs/metrics/splice_relay_candidates.json`
  - `outputs/metrics/splice_relay_probe_summary.json`
- at `100 ms`, the calibrated splice still produces the expected downstream turn-sign flip and already recruits structured intermediate relay asymmetry
- at `500 ms`, the downstream turn sign drifts even though some intermediate relays still carry asymmetric state
- a two-dimensional `uv_grid` splice now exists:
  - `outputs/metrics/splice_probe_uvgrid_2x2_current120_summary.json`
  - `outputs/metrics/splice_probe_uvgrid_flipu_summary.json`
- that `uv_grid` splice improves boundary agreement beyond the earlier one-axis splice, but the downstream turn sign is still wrong

So the current body-free blockers are now narrower:

1. resolve `uv_grid` orientation / column alignment
2. explain or stabilize the `100 ms -> 500 ms` downstream drift

Those two blockers now take priority over further embodied cold-start claims.

Latest narrowing:

- global UV-grid flips were not enough
- side-specific horizontal mirroring was also not enough
- the best targeted mirrored UV-grid variants still fail the downstream sign test even while preserving strong boundary agreement
- a `500 ms` probe with only a `25 ms` pulse also fails to preserve the correct downstream sign

So the next immediate body-free tasks are now:

1. finer or cell-type-specific column alignment
2. mechanistic audit of the recurrent downstream drift after a correct `100 ms` launch

See:

- `docs/splice_probe_results.md`

So the plan in this file remains relevant, but it is now downstream of the splice work rather than the next immediate loop.

## Problems To Fix

1. `path_length` overstates local twitching as locomotion.
2. `mech_bilateral` currently targets all `JON` neurons, but the checked public notebook experiment is `P9_JO_CE_bilateral`, not `P9_JON_all`.
3. `inferred_visual_turn_context` injects turning readouts directly. That is useful diagnostically, but it is weaker and less faithful than asymmetric `P9_left` / `P9_right` locomotor context.

## Corrective Changes

### 1. Honest movement metrics

File:
- `src/metrics/parity.py`

Add:
- `net_displacement`
- `displacement_efficiency`
- `bbox_width`
- `bbox_height`
- `bbox_area`

These must become the primary screen against reporting twitching as walking.

### 2. Public JON subgroup definitions

File:
- `src/brain/public_ids.py`

Add:
- `JON_CE_IDS`
- `JON_F_IDS`
- `JON_DM_IDS`
- `JON_ALL_IDS`

Change the default public mechanosensory bridge:
- `mech_bilateral -> JON_CE_IDS`

Reason:
- that matches the checked public `P9_JO_CE_bilateral` framing better than the current all-JON pool.

### 3. Stateful visually gated asymmetric P9 mode

Files:
- `src/bridge/brain_context.py`
- `src/bridge/controller.py`
- `src/runtime/closed_loop.py`

Add new mode:
- `brain_context.mode: inferred_visual_p9_context`

Behavior:
- starts from zero state
- computes a locomotor gate from visual forward evidence
- low-pass filters that gate over time
- injects only `P9_left` and `P9_right`
- applies asymmetry between `P9_left` and `P9_right` from inferred turn bias
- does not inject `DNa01` / `DNa02` directly

### 4. Configs and smoke tests

Files:
- `configs/mock_inferred_visual_p9.yaml`
- `configs/flygym_realistic_vision_inferred_visual_p9.yaml`
- `tests/test_bridge_unit.py`
- `tests/test_closed_loop_smoke.py`

Need tests for:
- cold-start zero state
- visual evidence turning the gate on
- asymmetric P9 drive on left/right bias
- zero-vision case remaining off

## Acceptance Criteria

For the next real `5 s` run:

1. `completed_full_duration = 1`
2. `nonzero_command_cycles` is sustained, not just sparse impulses
3. `net_displacement` is materially above the zero-brain baseline
4. `displacement_efficiency` is materially above the strict-twitch baseline
5. video and trajectory show traversal, not local jitter

Until those are met, the bridge is still not good enough.

## Update After The Descending-Only Readout Expansion

The specific `inferred_visual_p9_context` plan above remains historically useful, but it is no longer the leading path.

What changed:

- the repo now has a body-free grounded visual splice
- the first embodied splice-only run proved the input path was alive but still produced mostly local dithering
- the next successful improvement came from the output side, not from another locomotor prosthetic:
  - strict descending/efferent supplemental readout
  - no optic-lobe-as-motor shortcut
  - no `P9` prosthetic mode

Evidence:

- `docs/descending_readout_expansion.md`
- `outputs/metrics/descending_readout_comparison.csv`

Key result:

- embodied `2 s` splice-only baseline:
  - `net_displacement = 0.11315538386569819`
  - `displacement_efficiency = 0.05188073580402254`
- embodied `2 s` with descending-only expanded readout:
  - `net_displacement = 5.633006914226428`
  - `displacement_efficiency = 0.6177590229213569`

So the current project understanding is:

- cold-start visual control was blocked by both:
  - the input splice boundary
  - and the overly narrow output readout
- the next strongest path is now:
  - keep the grounded splice
  - keep the descending-only expanded readout
  - validate it against matched ablations before making a stronger closed-loop claim
