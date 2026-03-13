# Exit-Nerve VNC Decoder Validation

This document records `T111`: the first runtime benchmark attempt for the real
MANC `exit_nerve` structural spec as a `vnc_structural_spec` decoder candidate.

## Goal

Do not treat the real exit-nerve MANC structural spec as a paper-only artifact.

Instead:

- wire it into the existing runtime seam
- run a cheap host smoke / benchmark first
- then run one short real FlyGym realistic-vision smoke benchmark
- compare it against the current calibrated sampled decoder

## New config and tooling

Configs:

- `configs/mock_multidrive_torch.yaml`
- `configs/mock_vnc_structural_spec_exit_nerve.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_vnc_structural_spec_exit_nerve.yaml`

Audit tool:

- `scripts/audit_decoder_id_alignment.py`

New runtime-seam coverage:

- `tests/test_vnc_spec_decoder.py`
- `tests/test_closed_loop_smoke.py`

## Validation ladder

Completed in this order:

1. config and decoder loading test
2. mock closed-loop smoke that proves VNC decoder fields appear in the log
3. host mock benchmark with the real torch backend
4. short WSL FlyGym realistic-vision benchmark
5. ID-alignment audit against the configured FlyWire brain backend

## Host benchmark result

Artifacts:

- `outputs/benchmarks/fullstack_mock_multidrive_torch_0p4s.csv`
- `outputs/benchmarks/fullstack_mock_vnc_structural_spec_exit_nerve_0p4s.csv`

Result:

- both the sampled decoder and the VNC structural decoder stayed at zero
  command on the host mock-body path

Interpretation:

- this is not a useful decoder comparison on its own
- it is consistent with the earlier motor-path audit: the public-only coarse
  sensory path does not meaningfully drive the monitored motor / descending
  outputs
- that is why `T111` had to continue to the realistic-vision production path

## Short real FlyGym benchmark

Artifacts:

- `outputs/benchmarks/fullstack_vnc_structural_spec_exit_nerve_target_0p1s.csv`
- `outputs/benchmarks/fullstack_splice_uvgrid_descending_calibrated_target_t111_0p1s.csv`
- `outputs/requested_0p1s_vnc_structural_spec_exit_nerve_target/*`
- `outputs/requested_0p1s_splice_uvgrid_descending_calibrated_target_t111/*`
- `outputs/metrics/t111_exit_nerve_decoder_summary.json`

Observed benchmark summary:

- real exit-nerve VNC structural decoder:
  - wall seconds: `42.1159`
  - simulated seconds: `0.1`
  - real-time factor: `0.00237`
  - completed cycles: `50`
  - nonzero command cycles: `0`
- current calibrated sampled decoder:
  - wall seconds: `40.9756`
  - simulated seconds: `0.1`
  - real-time factor: `0.00244`
  - completed cycles: `50`
  - nonzero command cycles: `43`

Important interpretation:

- the real exit-nerve benchmark completed without crashing
- but it produced zero body command on every logged cycle
- the sampled decoder produced nonzero body command on most cycles under the
  same short production-path run

So the real structural decoder did not fail because it was too slow.

It failed because it never received meaningful monitored firing rates.

## Decisive blocker: ID-space mismatch

Artifact:

- `outputs/metrics/t111_decoder_id_alignment_comparison.json`

Observed alignment:

- `configs/flygym_realistic_vision_splice_uvgrid_vnc_structural_spec_exit_nerve.yaml`
  - requested decoder IDs: `736`
  - matched backend IDs: `0`
  - unmatched IDs: `736`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated.yaml`
  - requested decoder IDs: `42`
  - matched backend IDs: `42`

This is the core reason the real exit-nerve decoder stayed silent.

The real MANC structural spec uses MANC body IDs.

The current whole-brain backend uses FlyWire IDs from:

- `external/fly-brain/data/2025_Completeness_783.csv`

So the runtime seam itself works, but the current brain backend cannot monitor
the real MANC structural channels directly.

This is not a gain-tuning problem.

It is an ID-space compatibility problem.

## Verdict

`T111` succeeded as a benchmark and diagnosis task.

It did not succeed as a usable decoder promotion.

Current status:

- runtime seam: working
- real config path: working
- real short benchmark: completed
- meaningful control: blocked by MANC-vs-FlyWire ID mismatch

## Next step

Do not spend more time tuning `forward_scale_hz`, `turn_scale_hz`, or other
decoder gains against the current FlyWire backend until the ID-space mismatch is
addressed.

The next honest task is to build an explicit bridge between:

- real MANC VNC structural channels
- the FlyWire whole-brain monitor space used by the current backend

or to derive a same-ID-space replacement decoder candidate from the current
brain model outputs.

## Follow-up after `T112`

That next step is now complete.

The raw MANC structural spec was not rescued by an exact raw-ID crosswalk.
Instead, the repo now uses an explicit semantic bridge into the FlyWire monitor
space.

See:

- `docs/vnc_flywire_semantic_bridge.md`
- `outputs/metrics/manc_thoracic_structural_spec_exit_nerve_flywire_semantic.json`
- `outputs/metrics/t112_decoder_id_alignment_comparison.json`

The `T112` bridge clears the monitor-space blocker:

- raw MANC structural config: `736` requested IDs, `0` matched
- bridged semantic config: `685` requested IDs, `685` matched

The first short real bridged run is no longer silent, but it is also not yet
calibrated. The next task is now decoder tuning rather than ID-space repair.
