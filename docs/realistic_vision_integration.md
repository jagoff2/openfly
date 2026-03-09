# Realistic Vision Integration

## Production Requirement

Per `AGENTS.MD`, toy camera-only vision is allowed only as an intermediate debug path. The production path must use realistic vision.

## Production Adapter

The production adapter is `src/body/flygym_runtime.py`.

It does all of the following:

- imports `RealisticVisionFly` from `flygym.examples.vision.realistic_vision`
- collects `info["nn_activities"]` from the FlyGym step loop
- forwards those activities into `vision.feature_extractor.RealisticVisionFeatureExtractor`
- exposes the resulting left/right salience and motion features to `bridge.encoder.SensoryEncoder`

## What Is Reused Directly From Public Artifacts

- FlyGym `RealisticVisionFly`
- FlyGym `MovingFlyArena`
- FlyGym 500 Hz realistic-vision refresh cadence
- Public tracking-cell and motion-cell families reused by the FlyGym examples

## What This Repo Adds

- a compact online feature extractor suitable for whole-brain stimulation
- a body-runtime adapter that exposes realistic-vision activity every control window
- a CLI benchmark and demo path that proves the realistic-vision production route is the one being exercised

## Validation Status

Validated locally in WSL with real artifact output:

- body plus vision benchmark: `outputs/benchmarks/vision_benchmarks.csv`
- full-stack benchmark sweep: `outputs/benchmarks/fullstack_benchmarks.csv`
- short real demo: `outputs/demos/flygym-demo-20260308-121237.mp4`
- medium real demo: `outputs/demos/flygym-demo-20260308-121318.mp4`
- longest stable real demo: `outputs/demos/flygym-demo-20260308-121432.mp4`

## Current Caveat

The realistic-vision path is validated, but the current public WSL PyTorch wheel used by FlyVis does not support RTX 5060 Ti `sm_120`. The validated production configuration therefore hides GPUs from FlyVis with `force_cpu_vision: true` in `configs/flygym_realistic_vision.yaml`.
