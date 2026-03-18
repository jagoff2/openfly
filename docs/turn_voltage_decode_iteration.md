# Turn-Voltage Decode Iteration

## Scope

This iteration moved the decode workbench from bilateral activation ranking to
steering-aware lateralized voltage analysis, then used those results to build
the next relay-monitor cohort and the first voltage-driven shadow turn
decoders. No live controller gains or body shortcuts were changed.

The canonical real-fly behavior target set for interpreting this branch is:

- [behavior_target_set.md](/G:/flysim/docs/behavior_target_set.md)

That means this branch should be read as a landmark-orientation / fixation
improvement with stronger target-signed steering, not as proof of generic
continuous pursuit of an arbitrary moving target.

## Inputs

- Target monitored run:
  - `outputs/requested_0p2s_target_specific_monitored_target/flygym-demo-20260314-090534/activation_capture.npz`
  - `outputs/requested_0p2s_target_specific_monitored_target/flygym-demo-20260314-090534/run.jsonl`
- No-target monitored run:
  - `outputs/requested_0p2s_target_specific_monitored_no_target/flygym-demo-20260314-090747/activation_capture.npz`
  - `outputs/requested_0p2s_target_specific_monitored_no_target/flygym-demo-20260314-090747/run.jsonl`
- Zero-brain control:
  - `outputs/requested_0p2s_target_specific_monitored_zero_brain/flygym-demo-20260314-090929/run.jsonl`

## What Changed

- `src/analysis/iterative_decoding.py`
  - added monitor-level turn-voltage tables based on `right_minus_left`
    monitored voltage rather than bilateral mean alone
  - added family-level turn-voltage tables and turn-specific ranking
  - kept the original bilateral tables for global activation / wakefulness
    diagnosis
- `scripts/run_iterative_decoding_cycle.py`
  - now emits:
    - `*_family_turn_scores.csv`
    - `*_monitor_voltage_turn_scores.csv`
    - `*_relay_turn_candidates.csv`
    - `*_monitor_turn_candidates.csv`
- `outputs/metrics/target_specific_relay_turn_voltage_specificity_0p2s_*.csv`
  - target-vs-no-target steering-specific ranking artifacts
- `outputs/metrics/relay_turn_voltage_monitor_candidates.json`
  - next monitoring cohort built from the new turn-voltage family ranking
- `src/bridge/voltage_decoder.py`
  - new shadow-only voltage-turn decoder
- `scripts/build_turn_voltage_signal_library.py`
  - builds shadow-decoder signal libraries from ranked monitor comparisons
- `scripts/replay_voltage_turn_shadow_decoder.py`
  - replays a voltage-turn shadow decoder against an existing run log

## Main Findings

### 1. Steering information is much cleaner in lateralized monitored voltages

The strongest monitor-level turn-voltage candidates from the target-vs-no-target
comparison are in:

- `outputs/metrics/target_specific_relay_turn_voltage_specificity_0p2s_monitors.csv`

Top current monitored labels:

- `IB015`
- `CB1492`
- `MTe14`
- `VCH`
- `LTe62`
- `CB0828`
- `CB1108`
- `DNp06`
- `DNp35`
- `LT43`
- `CB3516`
- `LTe11`

Among the currently monitored visual families, the most biologically plausible
steering/feedback subset remains:

- `MTe14`
- `VCH`
- `LTe62`
- `LT43`
- `LTe11`
- `LCe03`

That subset matches the higher-confidence local annotation review better than
the raw numeric top list, which also contains broad central-state families.

### 2. The next family expansion should be driven by turn-voltage structure

The steering-specific family ranking is in:

- `outputs/metrics/target_specific_relay_turn_voltage_specificity_0p2s_families.csv`

Top family-level turn-voltage candidates:

- `LTe74`
- `CB1856`
- `cL17`
- `AVLP014`
- `AVLP448`
- `CB3417`
- `LC10d`
- `CB2783`
- `LPT27`
- `ALIN5`
- `LPT51`
- `LC36`

The next monitoring cohort built from that ranking is:

- `outputs/metrics/relay_turn_voltage_monitor_candidates.json`

and is wired into:

- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_turn_voltage_monitored.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_turn_voltage_monitored_no_target.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_turn_voltage_monitored_zero_brain.yaml`

### 3. A voltage-driven shadow turn decoder beats the live sampled turn signal on the recorded target run

Two shadow libraries were built:

- broad central+visual library:
  - `outputs/metrics/target_specific_turn_voltage_signal_library_0p2s.json`
- stricter visual-only library:
  - `outputs/metrics/target_specific_turn_voltage_signal_library_visual_only_0p2s.json`

The replay summaries are:

- `outputs/metrics/target_specific_turn_voltage_shadow_replay_target_0p2s.json`
- `outputs/metrics/target_specific_turn_voltage_shadow_replay_visual_only_target_0p2s.json`

Results on the same target run:

- live sampled turn signal:
  - `live_turn_bearing_corr = -0.1663`
- broad voltage shadow:
  - `shadow_turn_bearing_corr = -0.7276`
- visual-only voltage shadow:
  - `shadow_turn_bearing_corr = -0.7114`

Interpretation:

- the monitored relay voltages already contain a much stronger target-signed
  steering signal than the current sampled descending turn scalar
- the stricter visual-only subset retains nearly all of that steering signal,
  which is better for biological plausibility than leaning immediately on the
  broader central-state set

### 4. The voltage-turn shadows survive online in a fresh matched embodied cohort

The next monitored cohort was run online with the live controller still
unchanged:

- target:
  - `outputs/requested_0p2s_turn_voltage_monitored_target/flygym-demo-20260314-093340/summary.json`
- no-target:
  - `outputs/requested_0p2s_turn_voltage_monitored_no_target/flygym-demo-20260314-093552/summary.json`
- zero-brain:
  - `outputs/requested_0p2s_turn_voltage_monitored_zero_brain/flygym-demo-20260314-093805/summary.json`

Key online results:

- live controller behavior remained unchanged and still steering-poor:
  - `turn_alignment_fraction_active = 0.467`
  - `fixation_fraction_20deg = 0.0`
- online shadow turn summaries:
  - broad:
    - `outputs/metrics/turn_voltage_shadow_all_target_0p2s.json`
    - `outputs/metrics/turn_voltage_shadow_all_no_target_0p2s.json`
    - `outputs/metrics/turn_voltage_shadow_all_zero_brain_0p2s.json`
  - visual-only:
    - `outputs/metrics/turn_voltage_shadow_visual_target_0p2s.json`
    - `outputs/metrics/turn_voltage_shadow_visual_no_target_0p2s.json`
    - `outputs/metrics/turn_voltage_shadow_visual_zero_brain_0p2s.json`

Online target-bearing correlations from the fresh target run:

- live sampled turn signal:
  - `-0.1663`
- broad voltage shadow:
  - `-0.9206`
- visual-only voltage shadow:
  - `-0.9147`

Condition separation stayed honest:

- target broad shadow `abs_turn_mean = 0.6078`
- no-target broad shadow `abs_turn_mean = 0.4944`
- zero-brain broad shadow `abs_turn_mean = 0.0`
- target visual-only shadow `abs_turn_mean = 0.6167`
- no-target visual-only shadow `abs_turn_mean = 0.4973`
- zero-brain visual-only shadow `abs_turn_mean = 0.0`

Interpretation:

- the monitored relay voltages carry a robust online steering signal
- the visual-only subset remains nearly as strong as the broader central+visual
  library
- that makes the visual-only subset the better candidate for any future bounded
  live-controller promotion step

## Limits

- This is still shadow-only. The live embodied controller was not changed.
- The replayed shadow turn decoder was evaluated offline on an existing log,
  not in a fresh embodied closed-loop run.
- The shadow decoder currently models turn only. It does not solve forward
  recruitment or full motor/VNC embodiment.

## Next Step

Design a bounded live-controller promotion experiment using the visual-only
shadow library first, not the broader central+visual set.

Promotion rules:

- keep the existing live controller intact as the baseline branch
- promote only steering, not forward drive
- keep the promoted path reversible and explicitly labeled experimental
- require matched target / no-target / zero-brain controls again

## Update: 2026-03-14 bounded live promotion, bias correction, and matched 2.0 s controls

The bounded steering-only promotion path is now real and revalidated at
benchmark duration.

### 5. What the failure actually was

The original `2.0 s` promoted visual-core branch failed in two layers:

- first, a `>500 ms` arbitration problem:
  - the live sampled turn path and the relay-voltage shadow diverged in sign
  - the old promoted branch lost useful steering after the first fixation window
- second, a deeper generic relay bias:
  - matched `2.0 s` no-target controls showed the same one-sided right-turn lock
  - so the old branch was not doing clean target-conditioned steering

Evidence for the old generic bias:

- old no-target control:
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_conflict_no_target/flygym-demo-20260314-114017/summary.json`
  - `right_turn_dominant_fraction = 0.946`
  - `mean_turn_drive = 0.301`
  - `turn_switch_rate_hz = 2.50`

### 6. What was changed

Two fixes were required.

1. Conflict override is now gated by current-frame visual evidence in
   `src/bridge/controller.py`.

- the override no longer jumps blindly from `turn_blend` to
  `conflict_turn_blend`
- it now scales that jump by the current salience asymmetry magnitude
- this directly attacks the long-horizon live/shadow arbitration failure

2. The visual-core shadow decoder is now bias-corrected in
   `src/bridge/voltage_decoder.py`.

- the new library is:
  - `outputs/metrics/target_specific_turn_voltage_signal_library_visual_core_2s_bias_corrected.json`
- it stores matched `2.0 s` no-target baseline asymmetries per visual-core group
- the decoder subtracts those baselines before computing the turn signal
- the decoder now also guards against decoding motion from no monitored
  activity or a silent uniform rest-voltage field

### 7. Sign convention

For the target-engagement metrics in `src/analysis/behavior_metrics.py`,
positive `turn_bearing_corr` means the turn drive sign matches the target
bearing sign and is counted as aligned. Earlier negative values in this
workstream were bad, not good.

### 8. Final matched 2.0 s results on the fixed branch

Target:

- `outputs/requested_2s_turn_voltage_promoted_visual_core_conflict_gated_bias_target/flygym-demo-20260314-121624/summary.json`
- `outputs/requested_2s_turn_voltage_promoted_visual_core_conflict_gated_bias_target/flygym-demo-20260314-121624/activation_side_by_side.mp4`
- `outputs/requested_2s_turn_voltage_promoted_visual_core_conflict_gated_bias_target/flygym-demo-20260314-121624/activation_overview.png`

Key target metrics:

- `mean_abs_bearing_rad = 0.9020`
- `initial_abs_bearing_rad = 1.4411`
- `final_abs_bearing_rad = 1.5673`
- `turn_alignment_fraction_active = 0.7973`
- `aligned_turn_fraction = 0.704`
- `turn_bearing_corr = 0.7626`
- `right_turn_dominant_fraction = 0.232`
- `left_turn_dominant_fraction = 0.768`
- `turn_switch_rate_hz = 9.009`

Interpretation:

- the old one-sided right-turn lock is gone
- the promoted branch is now strongly target-aligned over `2.0 s`
- the controller still walks continuously, but steering is no longer pinned to a
  single sign

No-target:

- `outputs/requested_2s_turn_voltage_promoted_visual_core_conflict_gated_bias_no_target/flygym-demo-20260314-123350/summary.json`
- `outputs/requested_2s_turn_voltage_promoted_visual_core_conflict_gated_bias_no_target/flygym-demo-20260314-123350/activation_side_by_side.mp4`

Key no-target metrics:

- `right_turn_dominant_fraction = 0.374`
- `left_turn_dominant_fraction = 0.626`
- `mean_turn_drive = -0.0385`
- `mean_abs_turn_drive = 0.1015`
- `turn_switch_rate_hz = 21.021`
- `controller_state_entropy = 0.5037`

Interpretation:

- the old generic one-sided right-turn bias is removed
- locomotion stays awake, but turning is now exploratory and mixed rather than
  pinned to one sign

Zero-brain:

- `outputs/requested_2s_turn_voltage_promoted_visual_core_conflict_gated_bias_zero_brain_guarded_v3/flygym-demo-20260314-131053/summary.json`

Key zero-brain metrics:

- `controller_summary_forward_nonzero_fraction = 0.0`
- `controller_summary_turn_nonzero_fraction = 0.0`
- `mean_turn_drive = 0.0`
- `mean_abs_turn_drive = 0.0`
- `net_displacement = 0.0118`
- `path_length = 0.3689`

Interpretation:

- the bias-corrected shadow no longer invents motion from a silent brain
- the remaining tiny body motion is passive settling, not decoded control

### 9. Result

This closes the bounded promotion task honestly:

- the old `>500 ms` arbitration failure is resolved
- the generic no-target controller bias is resolved
- the zero-brain integrity check is restored

This is still not a full biological motor stack. It is a corrected
steering-only promotion path on top of the existing locomotor interface. But it
is materially better grounded than the earlier promoted branch and is now
supported by matched `2.0 s` target / no-target / zero-brain evidence.
