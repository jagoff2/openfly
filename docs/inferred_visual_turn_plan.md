# Inferred Visual Turn Plan

This plan addresses the shortcomings exposed by the inferred visual probe without weakening the faithful default path.

## Problem Summary

The probe showed three distinct losses in the current production bridge:

1. The real FlyVis model already contains useful left/right structure in relevant visual cell families.
2. `src/vision/feature_extractor.py` compresses that structure too aggressively:
   - tracking responses are reduced with `abs(...)`
   - many candidate cell families are averaged together
3. `src/brain/public_ids.py` then collapses the engineered left/right visual rates back into bilateral public pools before the whole-brain backend sees them.

The faithful default path should remain unchanged because the checked public notebook artifacts still do not expose honest left/right whole-brain sensory anchors.

## Goal

Add a clearly labeled inferred experimental path that preserves and uses the recovered left/right visual structure, while keeping the default `brain_context.mode: none` path unchanged.

## Plan

### 1. Preserve inferred left/right visual structure end-to-end

Files:
- `src/vision/feature_extractor.py`
- `src/vision/inferred_lateralized.py`
- `src/bridge/controller.py`
- `src/bridge/encoder.py`

Changes:
- extend `VisionFeatures` to carry inferred left/right turn evidence and confidence
- load the ranked probe artifact from `outputs/metrics/inferred_lateralized_visual_candidates.csv`
- compute inferred turn evidence directly from the live per-eye `nn_activities_arr`
- thread those inferred fields through bridge metadata and logs

Acceptance:
- default production behavior unchanged when inferred mode is disabled
- logs expose the inferred left/right evidence when enabled

### 2. Stop dropping flow structure in the experimental path

Files:
- `src/vision/feature_extractor.py`
- `src/bridge/encoder.py`

Changes:
- preserve signed flow-family structure for the inferred experiment helper
- keep the faithful default salience-based public-pool path unchanged
- expose both the legacy summary and the inferred turn summary in metadata so they can be compared directly

Acceptance:
- tests prove the inferred helper responds with opposite sign to mirrored left/right synthetic inputs

### 3. Add a brain-side inferred turn experiment mode

Files:
- `src/bridge/brain_context.py`
- `src/runtime/closed_loop.py`
- `configs/`

Changes:
- add `brain_context.mode: inferred_visual_turn_context`
- use inferred `turn_bias` to apply asymmetric direct brain-side stimulation to the public turning readout groups
- optionally use visual forward salience to scale direct `P9` context rather than forcing a constant locomotor floor

Constraint:
- no decoder fallback
- no body fallback
- keep this mode explicitly experimental and inferred

Acceptance:
- mock-path tests show left/right inferred stimuli produce opposite turning commands through the brain-side path

### 4. Add validation and comparison artifacts

Files:
- `tests/test_bridge_unit.py`
- `tests/test_closed_loop_smoke.py`
- `benchmarks/run_fullstack_with_realistic_vision.py`
- `docs/`

Changes:
- add unit tests for inferred candidate extraction and experimental context injection
- add smoke coverage for the new mode
- add a dedicated config for the experiment
- benchmark and compare:
  - strict default
  - `public_p9_context`
  - `inferred_visual_turn_context`

Acceptance:
- tests pass locally
- the new mode is clearly separated in configs, logs, docs, and benchmark rows

## Recommended Execution Order

1. preserve inferred features in `VisionFeatures` and bridge logs
2. add the experimental brain-context mode
3. validate with mock tests
4. validate with a short real WSL run
5. decide whether the inferred mode is worth keeping as a documented experiment
