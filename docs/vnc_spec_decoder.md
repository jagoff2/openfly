# VNC Structural Spec Decoder

This document records the first executable decoder candidate that uses a
graph-derived VNC structural specification instead of the repo's existing small
hand-picked descending sample.

## What this is

The current implementation adds three pieces:

- `src/vnc/spec_builder.py`
- `src/vnc/spec_decoder.py`
- `src/bridge/decoder_factory.py`

The builder takes a typed VNC graph slice and produces a structural spec JSON.
That spec contains one channel per descending node with side-specific motor
weights derived from:

- direct descending -> motor edges
- descending -> premotor -> motor two-step paths

The decoder then consumes that JSON and projects monitored descending firing
rates into:

- weighted left motor drive
- weighted right motor drive
- a forward signal
- a turn signal
- the current `HybridDriveCommand` body interface

## What this is not

This is not a full biological VNC emulator.

It does not yet model:

- local VNC dynamics
- recurrent premotor state
- motor neuron spike generation
- muscles or biomechanics beyond the existing FlyGym controller

It is still an experimental structural decoder.

The value of this slice is narrower and honest:

- it removes the requirement to pick only a tiny handful of descending groups
- it makes the broader VNC hypothesis executable and testable
- it preserves a clean config/runtime seam for future VNC work

## Decoder seam

The runtime now selects the motor decoder through:

- `src/bridge/decoder_factory.py`

That lets the closed loop swap between:

- the existing sampled descending decoder
- the new `vnc_structural_spec` decoder path

without rewriting:

- `src/runtime/closed_loop.py`
- `src/bridge/controller.py`

The future intended seam remains:

- brain readout -> VNC structural/emulator stage -> body command

This slice does not finish that architecture, but it removes the old assumption
that the only supported decoder is the hard-coded sampled one.

## Structural spec contents

The builder currently emits, per descending channel:

- `root_id`
- `cell_type`
- `side`
- `region`
- `left_direct_weight`
- `right_direct_weight`
- `left_premotor_path_weight`
- `right_premotor_path_weight`
- `left_total_weight`
- `right_total_weight`
- `total_motor_weight`
- `motor_target_count`

That is enough to test a broad structural readout before any richer dynamical
model exists.

## Validation in this slice

Local validation for this first decoder candidate is intentionally cheap:

- unit tests for structural-spec building
- unit tests for the decoder itself
- factory wiring tests
- mock JSON and CSV artifacts built from fixture graph slices

Heavy embodied WSL runs are intentionally deferred until a real public graph
export is ingested and the spec is no longer fixture-only.

## Current real-data status

That real-data gate has now been crossed, and the first real benchmark exposed
an additional blocker:

- the real MANC structural spec uses MANC body IDs
- the current whole-brain backend monitors FlyWire IDs

So the real `exit_nerve` structural spec could be loaded through the runtime
seam, but it could not read meaningful brain activity from the current backend
without an explicit ID-space bridge.

See:

- `docs/vnc_exit_nerve_decoder_validation.md`
- `outputs/metrics/t111_decoder_id_alignment_comparison.json`

## Current bridge status after `T112`

That blocker is now resolved by an explicit semantic bridge, not by pretending
that MANC `bodyId` values are FlyWire `root_id` values.

The new bridge:

- groups the real MANC structural channels by `cell_type + side`
- resolves those semantic channels into FlyWire monitor roots using exact
  `cell_type + side` plus key-level `hemibrain_type` fallback
- filters the final monitor roots to the live v783 backend completeness space

Artifacts:

- `src/vnc/flywire_bridge.py`
- `scripts/build_vnc_flywire_semantic_spec.py`
- `outputs/metrics/manc_thoracic_structural_spec_exit_nerve_flywire_semantic.json`
- `docs/vnc_flywire_semantic_bridge.md`

Runtime result:

- raw real MANC spec: `736` requested IDs, `0` backend matches
- bridged semantic spec: `685` requested IDs, `685` backend matches under the
  live config

The first short real run with the bridged spec is no longer silent. It produced
nonzero commands on `43 / 50` cycles.

What remains unresolved is calibration: the first bridged run saturates, so the
next task is behavioral tuning rather than more ID-space work.
