# Semantic-VNC Failed Parity Branch

Status: frozen

Verdict: fail for target-tracking parity

## Scope

This writeup freezes the semantic-VNC branch built from:

- the real MANC `exit_nerve` structural spec
- the FlyWire semantic bridge
- the `vnc_structural_spec` decoder path
- the follow-camera corrected `2.0 s` demo

Primary config:

- `configs/flygym_realistic_vision_splice_uvgrid_vnc_structural_spec_exit_nerve_flywire_semantic.yaml`

## What this branch proved

- The raw MANC-vs-FlyWire ID mismatch was solvable at the monitor-space level.
- The semantic bridge is real, not silent:
  - `outputs/metrics/t112_decoder_id_alignment_comparison.json`
  - bridged decoder requested `685` IDs and matched `685`
- The decoder can drive locomotor output through the live embodied stack.
- The first saturation bug in the semantic decoder was real and was removed by later normalization in `src/vnc/spec_decoder.py`.
- The old off-screen demo framing was a real camera issue and was removed by later follow-camera support in `src/body/flygym_runtime.py`.

## Why this branch fails parity

The branch moves the fly, but it does not track the target credibly enough to count as parity.

The decisive progression is:

1. The first semantic-VNC bridged run proved monitor-space compatibility but immediately saturated:
   - `outputs/metrics/t112_exit_nerve_flywire_semantic_summary.json`
   - `max_left_drive = 1.2`
   - `max_right_drive = 1.2`
   - `max_forward_signal = 1.0`
   - `max_turn_signal = 1.0`
2. The later normalization fix removed that obvious decoder failure:
   - `outputs/benchmarks/fullstack_vnc_structural_spec_exit_nerve_flywire_semantic_decoder_fixed_target_0p1s.csv`
3. The later `2.0 s` corrected demo also removed the framing problem and stayed stable:
   - `outputs/benchmarks/fullstack_vnc_structural_spec_exit_nerve_flywire_semantic_decoder_fixed_follow_yaw_target_2s.csv`
   - `outputs/requested_2s_vnc_structural_spec_exit_nerve_flywire_semantic_decoder_fixed_follow_yaw_target/flygym-demo-20260312-184650/demo.mp4`
   - `outputs/requested_2s_vnc_structural_spec_exit_nerve_flywire_semantic_decoder_fixed_follow_yaw_target/flygym-demo-20260312-184650/metrics.csv`
   - corrected `2.0 s` metrics:
     - `avg_forward_speed = 4.7635`
     - `net_displacement = 7.0699`
     - `displacement_efficiency = 0.7428`
     - `stable = 1.0`
4. Even after those corrections, the branch still does not visibly pursue the target.

That means the branch is no longer blocked by a silent decoder, a broken ID seam, or a bad camera. It is blocked by the deeper issue: the current semantic structural mapping is not sufficient to recover target-directed behavior.

## Interpretation

The honest interpretation is:

- anatomical structural reachability was enough to build a working semantic-VNC locomotor branch
- anatomical structural reachability was not enough to recover target-tracking control
- this branch should therefore be preserved as a useful negative result, not promoted as the parity path

## Frozen artifacts

Locked artifact manifest:

- `outputs/locks/semantic_vnc_failed_parity_branch_manifest.md`

The locked set includes:

- the semantic bridge metric summaries
- the original bridged saturation run artifacts
- the normalized short rerun artifacts
- the corrected `2.0 s` follow-camera rerun artifacts
- the corresponding benchmark CSV and plot files

## Freeze rule

Do not overwrite the locked artifact paths in the manifest.

If this line of work is revisited later, create a new output root and treat it as a new branch rather than mutating this failed one.
