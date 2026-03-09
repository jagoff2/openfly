# Inferred Visual Turn Context Mode

This mode is an explicit experiment. It is not part of the faithful default path.

## Purpose

The strict default bridge currently discards most of the left/right structure recovered by the real FlyVis probe because:

- the visual features are heavily averaged
- the public sensory mapping collapses everything back into bilateral `LC4` / `JON` pools

`inferred_visual_turn_context` keeps the faithful default unchanged and adds a separate brain-side experiment path.

## How It Works

Config:
- `brain_context.mode: inferred_visual_turn_context`
- `inferred_visual.enabled: true`

Files:
- `src/vision/inferred_lateralized.py`
- `src/vision/feature_extractor.py`
- `src/bridge/brain_context.py`
- `src/runtime/closed_loop.py`

Behavior:
- load the ranked inferred visual candidates from `outputs/metrics/inferred_lateralized_visual_candidates.csv`
- compute an inferred left/right `turn_bias` from live per-eye visual activity
- compute a symmetric direct `P9` context from visual forward salience
- compute an asymmetric direct turning context to the public `DNa01` / `DNa02` groups from the inferred `turn_bias`

This stays brain-side:
- no decoder idle floor
- no body fallback
- no change to the faithful default config

## Current Status

Validated locally on the mock path:
- `configs/mock_inferred_visual_turn.yaml`
- `tests/test_bridge_unit.py`
- `tests/test_closed_loop_smoke.py`

Staged for real FlyGym validation:
- `configs/flygym_realistic_vision_inferred_visual_turn.yaml`

## Boundary

This mode is useful for testing whether the left/right structure recovered from FlyVis can drive turning through the brain-side path.

It does not claim:
- a public-grounded whole-brain sensory mapping
- a faithful biological left/right steering bridge

It should be interpreted as an inferred experiment only.
