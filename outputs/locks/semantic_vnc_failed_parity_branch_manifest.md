# Semantic-VNC Failed Parity Branch Lock Manifest

Frozen: `2026-03-12`

Verdict: `fail`

Reason:

- the semantic-VNC branch is monitor-space valid and can drive locomotion
- the corrected decoder no longer saturates immediately
- the corrected demo stays in frame
- the branch still does not track the target and is not a parity candidate

Locked output roots:

- `outputs/requested_0p1s_vnc_structural_spec_exit_nerve_flywire_semantic_target/`
- `outputs/requested_2s_vnc_structural_spec_exit_nerve_flywire_semantic_target/`
- `outputs/requested_0p1s_vnc_structural_spec_exit_nerve_flywire_semantic_decoder_fixed_target/`
- `outputs/requested_2s_vnc_structural_spec_exit_nerve_flywire_semantic_decoder_fixed_follow_yaw_target/`

Locked benchmark files:

- `outputs/benchmarks/fullstack_vnc_structural_spec_exit_nerve_flywire_semantic_target_0p1s.csv`
- `outputs/benchmarks/fullstack_vnc_structural_spec_exit_nerve_flywire_semantic_target_2s.csv`
- `outputs/benchmarks/fullstack_vnc_structural_spec_exit_nerve_flywire_semantic_decoder_fixed_target_0p1s.csv`
- `outputs/benchmarks/fullstack_vnc_structural_spec_exit_nerve_flywire_semantic_decoder_fixed_follow_yaw_target_2s.csv`

Locked plot files:

- `outputs/plots/fullstack_vnc_structural_spec_exit_nerve_flywire_semantic_target_0p1s.png`
- `outputs/plots/fullstack_vnc_structural_spec_exit_nerve_flywire_semantic_target_2s.png`
- `outputs/plots/fullstack_vnc_structural_spec_exit_nerve_flywire_semantic_decoder_fixed_target_0p1s.png`
- `outputs/plots/fullstack_vnc_structural_spec_exit_nerve_flywire_semantic_decoder_fixed_follow_yaw_target_2s.png`

Locked summary files:

- `outputs/metrics/manc_thoracic_structural_spec_exit_nerve_flywire_semantic.json`
- `outputs/metrics/t112_decoder_id_alignment_comparison.json`
- `outputs/metrics/t112_exit_nerve_flywire_semantic_summary.json`

Lock rule:

- these paths were frozen as the canonical semantic-VNC failed-parity record
- do not overwrite them in future runs
- if the branch is revisited, write new outputs under a new root
