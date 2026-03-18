# Relay-Monitored Shadow-Control Loop

## Scope

This is the first matched-control loop using:

- the calibrated live descending decoder
- widened relay monitoring built from the first iterative decoding cycle
- a shadow semantic-VNC decoder on the same brain activity
- same-run activation artifacts by default for the non-zero backends

Configs:

- [relay target](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_relay_monitored.yaml)
- [relay no-target](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_relay_monitored_no_target.yaml)
- [relay zero-brain](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_relay_monitored_zero_brain.yaml)

Key artifacts:

- [control metrics](/G:/flysim/outputs/metrics/relay_monitored_control_metrics_0p2s.csv)
- [shadow control summary](/G:/flysim/outputs/metrics/relay_monitored_shadow_control_summary_0p2s.csv)
- [target decode summary](/G:/flysim/outputs/metrics/iterative_decoding_cycle_relay_target_summary.json)
- [no-target decode summary](/G:/flysim/outputs/metrics/iterative_decoding_cycle_relay_no_target_summary.json)

## What Changed

The live controller did not change. The changes were observational:

- monitor set widened from the strict DN shortlist to a merged DN + relay group
  file:
  [iterative_monitor_candidates_merged.json](/G:/flysim/outputs/metrics/iterative_monitor_candidates_merged.json)
- same run now logs raw monitored rates and voltages
- same run now carries a shadow semantic-VNC decode in `run.jsonl`

Implementation seams:

- [controller.py](/G:/flysim/src/bridge/controller.py)
- [closed_loop.py](/G:/flysim/src/runtime/closed_loop.py)
- [session.py](/G:/flysim/src/visualization/session.py)

## Behavior Result

At `0.2 s`, the widened monitoring did not solve the behavior problem.

Control comparison:

- `target`: `avg_forward_speed = 2.7087`, `net_displacement = 0.2248`,
  `efficiency = 0.4191`
- `no_target`: `3.3055`, `0.2972`, `0.4541`
- `zero_brain`: `1.7358`, `0.0162`, `0.0471`

Interpretation:

- `zero_brain` still collapses displacement strongly, so the live branch is
  still brain-mediated.
- `no_target` still exceeds `target`, so the branch remains scene-driven rather
  than target-pure.
- but raw speed/displacement are now treated as secondary metrics, not the main
  judgment axis, because an awake fly should still locomote under `no_target`
  conditions.

Behavior-specific artifacts:

- [behavior conditions](/G:/flysim/outputs/metrics/relay_monitored_behavior_conditions_0p2s.json)
- [metric pivot note](/G:/flysim/docs/target_engagement_metric_pivot.md)

The target-side diagnosis is now:

- locomotion is already present: `locomotor_active_fraction = 0.96`
- controller richness is nontrivial: `controller_state_entropy = 0.583`
- target steering is still wrong:
  - `turn_alignment_fraction_active = 0.467`
  - `turn_bearing_corr = -0.697`
  - `fixation_fraction_20deg = 0.0`

Important control caveat:

- simple `bearing_reduction_rad` is not enough, because the `zero_brain`
  control still gets passive bearing improvement from target motion plus body
  drift. In this matched slice, `target` reduced bearing by `0.250 rad` while
  `zero_brain` still reduced it by `0.273 rad`.
- the next decode loop therefore has to optimize for signed steering alignment
  and fixation above the zero-brain baseline, not just for reduced bearing.

## Shadow VNC Result

The shadow semantic-VNC decoder is active on both `target` and `no_target`, and
it collapses to zero on `zero_brain`.

Shadow summary:

- `target`: `forward_mean = 0.01093`, `abs_turn_mean = 0.00842`
- `no_target`: `0.01322`, `0.00881`
- `zero_brain`: `0.00000`, `0.00000`

Interpretation:

- The structural VNC path is reading real brain-side signal.
- It still does not separate `target` from `no_target`.
- That means the current bottleneck is not just “VNC sees nothing.” It sees
  something, but the signal is not target-selective enough to justify live
  promotion.

## Relay Monitoring Result

The widened relay monitor layer also produced a real negative result:

- most newly added relay labels stayed near zero in firing-rate space over
  these short windows
- the families that ranked highly in the iterative decode workbench did so
  mainly in voltage space, not in firing-rate space

This is why the current monitored-heatmap view is still incomplete. The new
instrumentation now logs monitored voltages as well, because firing-rate-only
monitoring underestimates quiescent-but-structured relay families.

## Ranked Families

Target-side top voltage-ranked relay families from the first widened target run:

- `CB1259`
- `T2`
- `LTe56`
- `AN_AVLP_GNG_23`
- `C3`
- `MTe49`

No-target-side top forward-ranked families from the widened no-target run:

- `PVLP024`
- `SA_MDA_3`
- `AL-AST1`
- `JO-CM`
- `CB2588`
- `AN_FLA_GNG_1`

This mismatch is the current point of the workstream:

- `target` and `no_target` are selecting different upstream relay structure
- that means the next decode loop should compare relay voltage trajectories
  across matched controls before promoting any new family into control

After explicitly penalizing the no-target spontaneous baseline, the current
target-specific family shortlist becomes:

- `MTe14`
- `LTe62`
- `VCH`
- `CB0828`
- `cL02c`
- `CB1492`
- `CB3516`
- `LTe11`

Artifacts:

- [target-specific relay summary](/G:/flysim/outputs/metrics/relay_target_specificity_0p2s_summary.json)
- [target-specific family ranking](/G:/flysim/outputs/metrics/relay_target_specificity_0p2s_families.csv)

## Important Limitation

The zero backend does not expose brain-state tensors, so the zero-brain run does
not generate a rendered activation artifact. That is honest and expected:

- [zero-brain summary](/G:/flysim/outputs/requested_0p2s_relay_monitored_zero_brain/flygym-demo-20260313-215725/summary.json)

The run still logs scalar outputs and shadow decoder collapse, so it remains a
valid behavioral control.

## Next Decode Step

The next biologically strict step is not another controller tweak.

It is:

1. use the new monitored-voltage logging path
2. compare target / no-target relay families in voltage space and rate space
3. identify families that are target-selective under matched controls
4. promote only those families into monitoring-first relay checkpoints
5. keep the semantic-VNC path in shadow mode until it shows control-condition
   separation that the live descending decoder does not

This next step is now implemented and recorded in
[turn_voltage_decode_iteration.md](/G:/flysim/docs/turn_voltage_decode_iteration.md).
The important update is that the relay-monitor workstream has moved from
bilateral voltage ranking to explicit left-right turn-voltage analysis and now
has a shadow voltage-turn decoder that can be replayed against existing runs
without touching the live controller.
