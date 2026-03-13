# VNC FlyWire Semantic Bridge

This document records `T112`: the fix for the real MANC-to-FlyWire decoder
ID-space mismatch exposed by `T111`.

## Problem

The first real MANC `exit_nerve` structural decoder was runnable but silent.

The reason was not runtime failure or gain tuning.

It was an ID-space mismatch:

- the real MANC structural spec used MANC `bodyId` values
- the current whole-brain backend monitors FlyWire `root_id` values from
  `external/fly-brain/data/2025_Completeness_783.csv`

`T111` measured that mismatch directly:

- raw MANC structural decoder requested `736` IDs
- current backend matched `0`

See:

- `docs/vnc_exit_nerve_decoder_validation.md`
- `outputs/metrics/t111_decoder_id_alignment_comparison.json`

## Public mapping conclusion

The literature/public-source review did not find a general public exact raw-ID
crosswalk of the form:

- `MANC bodyid -> FlyWire root_id`

for arbitrary neurons.

The strongest public bridge is annotation-level:

- `cell_type`
- homolog group / `hemibrain_type`
- `side`
- sometimes hemilineage

Important sources:

- neck-connective comparative matching across FAFB/FlyWire, FANC, and MANC:
  - `https://www.nature.com/articles/s41586-025-08925-z`
  - `https://github.com/flyconnectome/2023neckconnective`
- MANC annotation/tooling:
  - `https://natverse.org/malecns/`
  - `https://www.janelia.org/project-team/flyem/manc-connectome`
- FlyWire annotation / typing:
  - `https://www.nature.com/articles/s41586-024-07686-5`
  - `https://github.com/flyconnectome/flywire_annotations`

The honest next step was therefore a semantic bridge, not a fake direct ID
substitution.

## Implemented bridge

New implementation:

- `src/vnc/flywire_bridge.py`
- `scripts/build_vnc_flywire_semantic_spec.py`
- `src/vnc/spec_decoder.py`

New configs:

- `configs/mock_vnc_structural_spec_exit_nerve_flywire_semantic.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_vnc_structural_spec_exit_nerve_flywire_semantic.yaml`

New tests:

- `tests/test_vnc_flywire_bridge.py`
- `tests/test_vnc_spec_decoder.py`
- `tests/test_closed_loop_smoke.py`

### Bridge rule

The real MANC `exit_nerve` structural spec is now bridged into FlyWire monitor
space by:

1. grouping the MANC structural channels by exact `cell_type + side`
2. aggregating duplicated MANC channels conservatively with `mean` weights
3. resolving each semantic key into FlyWire monitor roots using:
   - exact FlyWire `cell_type + side` first
   - the same key in FlyWire `hemibrain_type + side` as fallback
4. filtering the resolved monitor roots to the live backend completeness space
   so the generated spec only requests IDs that the current backend can monitor

This produces a real same-monitor-space decoder without claiming exact
MANC-neuron identity inside the FlyWire brain.

## Artifact

The bridged spec is:

- `outputs/metrics/manc_thoracic_structural_spec_exit_nerve_flywire_semantic.json`

Top-level summary from that artifact:

- source channels: `1232`
- source semantic keys: `926`
- bridged semantic channels: `847`
- matched source channels: `1095`
- unmatched source channels: `137`
- FlyWire monitor IDs after completeness filtering: `1145`
- match breakdown:
  - exact FlyWire `cell_type`: `770`
  - FlyWire `hemibrain_type` fallback: `77`

## Runtime decoder result

The bridged runtime config still applies the decoder's `min_total_weight = 500`
filter, so the live decoder does not use every bridged semantic channel.

Under the live config, the decoder requests:

- `685` FlyWire monitor IDs

Alignment result:

- requested IDs: `685`
- matched backend IDs: `685`
- unmatched IDs: `0`

Artifacts:

- `outputs/metrics/t112_decoder_id_alignment_comparison.json`
- `outputs/metrics/t112_decoder_id_alignment_semantic.json`

This resolves the original ID-space blocker.

## Short real benchmark

Artifact set:

- `outputs/benchmarks/fullstack_vnc_structural_spec_exit_nerve_flywire_semantic_target_0p1s.csv`
- `outputs/requested_0p1s_vnc_structural_spec_exit_nerve_flywire_semantic_target/*`
- `outputs/metrics/t112_exit_nerve_flywire_semantic_summary.json`

Observed short real WSL run:

- completed cycles: `50`
- nonzero command cycles: `43`
- wall seconds: `43.0374`
- simulated seconds: `0.1`
- real-time factor: `0.00232`

This is the key change relative to `T111`.

The bridged decoder is no longer a silent zero-output no-op.

## Current limitation

The first bridged run is clearly overdriven.

Observed from `outputs/metrics/t112_exit_nerve_flywire_semantic_summary.json`:

- `max_forward_signal = 1.0`
- `max_turn_signal = 1.0`
- `max_left_drive = 1.2`
- `max_right_drive = 1.2`

So `T112` solves monitor-space compatibility, but it does not yet produce a
calibrated behavioral decoder.

That is now a separate task.

## Honest status

What is now true:

- the VNC structural decoder can read real activity from the current FlyWire
  backend
- the public data path is explicit and reproducible
- the bridge is grounded in public annotation labels rather than made-up ID
  substitution

What is still not true:

- this is not an exact neuron-identity MANC-to-FlyWire mapping
- this is not yet a tuned or behaviorally validated VNC structural controller
- this is not yet a full biological VNC emulator

## Next step

`T113` should tune the bridged decoder's channel filtering and scaling so the
semantic VNC path can be judged on behavior rather than only on successful
monitor-space alignment.
