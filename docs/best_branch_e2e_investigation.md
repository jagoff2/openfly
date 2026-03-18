# Best-Branch End-to-End Investigation

This document records the current investigation pass over the strongest
embodied branch using synchronized recorded artifacts rather than new runtime
experiments.

Primary analysis entry point:

- `scripts/analyze_best_branch_embodiment.py`

Primary outputs:

- `outputs/metrics/best_branch_investigation_summary.json`
- `outputs/metrics/best_branch_investigation_behavior_summary.csv`
- `outputs/metrics/best_branch_investigation_family_correlations.csv`
- `outputs/metrics/best_branch_investigation_monitor_correlations.csv`
- `outputs/metrics/best_branch_investigation_unsampled_central_units.csv`
- `outputs/metrics/best_branch_investigation_unsampled_central_spiking_units.csv`
- `outputs/plots/best_branch_investigation_family_target_bearing_corr.png`
- `outputs/plots/best_branch_investigation_monitor_target_bearing_corr.png`

## Goal

Use the recorded stimulus, neural activations, decoder outputs, and embodied
behavior together to learn what would most plausibly improve embodiment
without adding new shortcuts.

The target branch analyzed here is:

- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_monitored.yaml`

with behavior grounded against the matched strongest branch artifacts:

- target:
  - `outputs/requested_2s_splice_uvgrid_descending_calibrated_target/flygym-demo-20260311-071452/*`
- no target:
  - `outputs/requested_2s_splice_uvgrid_descending_calibrated_no_target/flygym-demo-20260311-073028/*`
- zero brain:
  - `outputs/requested_2s_splice_uvgrid_descending_calibrated_zero_brain/flygym-demo-20260311-074301/*`

## Main Findings

### 1. The branch is target-modulated, but not target-pure

From `outputs/metrics/best_branch_investigation_behavior_summary.csv`:

- target:
  - `avg_forward_speed = 4.9241`
  - `net_displacement = 5.7583`
  - `displacement_efficiency = 0.5853`
- no target:
  - `avg_forward_speed = 3.9070`
  - `net_displacement = 5.2903`
  - `displacement_efficiency = 0.6777`
- zero brain:
  - `avg_forward_speed = 0.1847`
  - `net_displacement = 0.0118`
  - `displacement_efficiency = 0.0320`

Interpretation:

- the branch is genuinely brain-driven, because `zero_brain` stays near zero
- the branch is genuinely target-modulated, because the target raises forward
  speed and the previously logged bearing alignment remains strong
- but the branch is still heavily scene / self-motion driven, because the
  no-target run still traverses substantially

So the current system is not missing all relevant visual structure. It is
failing to separate target-specific drive from the rest of the visual stream
cleanly enough.

### 2. The dominant unsampled central cloud is real, but it is mostly not spiking

The apparent central unsampled cluster in the whole-brain panel is dominated by
`T4a` optic neurons.

From `outputs/metrics/best_branch_investigation_unsampled_central_units.csv`:

- dominant family: `T4a`
- representative units are selected in `196-197 / 200` rendered frames
- the top central `T4a` units show `spike_frames = 0`
- many of those units sit at very negative mean voltage, often around
  `-333` to `-347`

Interpretation:

- the central unsampled cloud is not mainly "hidden motor neurons"
- it is mainly a persistently selected optic population
- the current visualization selection rule favors large absolute voltage
  excursions, so a strongly hyperpolarized optic family can look visually
  dominant even when it is not repeatedly spiking

This means the current activation movie is useful, but it must not be read as
"the brightest-looking central cluster is the motor answer."

### 3. Strong target-bearing structure is still much stronger upstream than in the monitored descending outputs

From `outputs/metrics/best_branch_investigation_family_correlations.csv`:

- `LT78`: `corr_target_bearing = 0.8908` (`n_roots = 8`)
- `T5b`: `corr_target_bearing = 0.8143` (`n_roots = 1520`)
- `T5c`: `corr_target_bearing = 0.6951` (`n_roots = 1529`)
- `T5a`: `corr_target_bearing = 0.6540` (`n_roots = 1482`)
- `T5d`: `corr_target_bearing = 0.4906` (`n_roots = 1467`)
- `T4a`: `corr_target_bearing = 0.4222` (`n_roots = 1463`)

By contrast, from `outputs/metrics/best_branch_investigation_monitor_correlations.csv`:

- best monitored label: `DNg97`
  - `corr_target_bearing = 0.2192`
- next monitored labels are weaker:
  - `DNp103 = 0.0990`
  - `DNpe040 = 0.0763`
  - `DNp18 = 0.0636`

Interpretation:

- the strongest target-bearing structure in the recorded run is still upstream
  in optic / visual-projection families
- the monitored descending readout carries some target-bearing signal, but much
  less of it
- the main current bottleneck is therefore not "the visual signal is absent"
- the main bottleneck is transfer / compression from upstream visual families
  into the downstream descending readout and then into the two-drive body
  interface

### 4. The smaller central spiking set is more useful than the large `T4a` cloud

From `outputs/metrics/best_branch_investigation_unsampled_central_spiking_units.csv`,
the more spike-active central unsampled groups include:

- `CT1`
- `LPi12`
- `LPT50`
- `JO-EVL`
- `JO-EDM`
- `JO-CM`
- `JO-EVP`
- `JO-EVM`
- `T5a`
- `T5c`
- `IB092`

These are more interesting than the non-spiking `T4a` cloud because they are
better candidates for:

- relay analysis
- mechanosensory / optic-flow context
- downstream transfer diagnostics

They are still not evidence that they should be decoded directly into motor
commands.

## What This Means For Plausible Embodiment

The most important conclusion from this investigation is:

- do not spend the next loop on more decoder-only gain tuning

The current recordings argue for a biologically stricter path:

1. add matched activation captures for `target`, `no_target`, and `zero_brain`
   under the same monitored config
2. expand monitoring around the strongest unsampled relay families instead of
   only around the current DN shortlist
3. treat those relay families as diagnostic transfer checkpoints, not as direct
   body-effectors
4. only after the relay path is characterized, revise the splice or
   descending-output path
5. do not revive the semantic-VNC path until descending / VNC state semantics
   are matched behaviorally rather than only structurally

## Ranked No-Shortcuts Next Steps

### 1. Build matched activation captures for the control conditions

The current synchronized activation artifact exists only for the target-present
run. Without matched no-target and zero-brain captures, the repo cannot cleanly
separate:

- target-selective relay families
- optic-flow / self-motion families
- generic scene-driven populations

This is the highest-value next investigation step.

### 2. Add a relay monitoring layer above the current DN shortlist

The current monitored decoder layer is too far downstream to explain where the
target-bearing structure is being lost.

The first relay monitoring expansion should explicitly include:

- `LT78`
- `T5a`
- `T5b`
- `T5c`
- `T5d`
- `T4a`
- `CT1`
- `LPi12`
- `LPT50`
- `JO-*` families that appear centrally in the recorded run

This should remain a monitoring-only layer at first.

### 3. Separate depolarized / spiking selection from hyperpolarized selection in the visualization path

Right now, a family like `T4a` can dominate the active point cloud because the
renderer selects large absolute voltages. That is useful for finding numerical
dominance, but it is not the same as finding functionally recruiting neurons.

The next visualization revision should split:

- depolarized / spiking units
- strongly hyperpolarized units

before making causal claims from the video.

### 4. Use the relay findings to constrain the splice, not to bypass it

The right use of these families is:

- identify where target-bearing structure is preserved
- identify where it collapses
- use that to constrain the next splice / bridge refinement

The wrong use would be:

- directly decoding upstream optic families into body control

That would just create a new shortcut.

### 5. Keep the semantic-VNC branch frozen until behaviorally grounded

The semantic-VNC branch already showed:

- structure can be mapped
- locomotion can be generated
- target tracking still fails

So the next biologically faithful path is not "replace the decoder with a
broader structural map and hope." It is to first recover more honest relay and
descending semantics, then revisit VNC embodiment with those constraints in
place.

## Bottom Line

The recorded evidence says the repo is not starved for visual signal. It is
starved for a biologically honest transfer path from visual / relay structure
into descending and embodied motor structure.

That means the next credible embodiment loop is:

- matched activation controls
- relay-first monitoring
- splice / transfer refinement
- only then downstream embodiment revision

not more blind gain tuning and not a new visual-to-controller shortcut.
