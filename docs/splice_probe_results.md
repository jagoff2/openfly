# Splice Probe Results

## Scope

This is the first body-free FlyVis-to-whole-brain splice probe. It does not use the FlyGym body. It only asks:

1. what overlap between FlyVis and the whole-brain graph can be grounded from public artifacts
2. whether a wide visual splice can be driven into the whole-brain backend without collapsing everything to a few scalar pools
3. whether that splice preserves left/right structure well enough to be a credible next boundary

Artifacts:

- `outputs/cache/flywire_annotation_supplement.tsv`
- `outputs/metrics/flyvis_overlap_inventory.json`
- `outputs/metrics/splice_probe_summary.json`
- `outputs/metrics/splice_probe_groups.csv`
- `outputs/metrics/splice_probe_side_differences.csv`
- `outputs/metrics/splice_probe_signed_bins4_summary.json`
- `outputs/metrics/splice_probe_signed_bins4_groups.csv`
- `outputs/metrics/splice_probe_signed_bins4_side_differences.csv`
- `outputs/metrics/splice_probe_signed_bins4_100ms_summary.json`
- `outputs/metrics/splice_probe_signed_bins4_100ms_groups.csv`
- `outputs/metrics/splice_probe_signed_bins4_100ms_side_differences.csv`

## Grounded overlap

### 1. FlyVis metadata alone was not enough

`scripts/inspect_flyvis_overlap.py` showed that the accessible FlyVis connectome metadata exposes:

- `type`
- `role`
- `u`
- `v`
- `index`

but no direct FlyWire neuron identity field such as a root ID.

So the splice cannot currently be grounded at the level of:

- FlyVis node identity -> exact whole-brain root ID

from FlyVis metadata alone.

### 2. The official FlyWire annotation supplement fixes part of that problem

The official annotation supplement written to:

- `outputs/cache/flywire_annotation_supplement.tsv`

contains:

- `root_id`
- `cell_type`
- `side`

That lets the repo ground the whole-brain side of the splice by exact public:

- cell type
- hemisphere side

instead of by fabricated left/right splits of arbitrary ID lists.

### 3. Exact shared cell types exist in large numbers

Using the official annotation supplement plus the FlyVis node `type` labels, the repo found:

- `49` exact shared cell types
- `98` type+side groups

The complete bilateral overlap set is:

- `Am`
- `C2`
- `C3`
- `L1`
- `L2`
- `L3`
- `L4`
- `L5`
- `Lawf1`
- `Lawf2`
- `Mi1`
- `Mi10`
- `Mi13`
- `Mi14`
- `Mi15`
- `Mi2`
- `Mi4`
- `Mi9`
- `R7`
- `R8`
- `T1`
- `T2`
- `T2a`
- `T3`
- `T4a`
- `T4b`
- `T4c`
- `T4d`
- `T5a`
- `T5b`
- `T5c`
- `T5d`
- `Tm1`
- `Tm16`
- `Tm2`
- `Tm20`
- `Tm3`
- `Tm4`
- `Tm5Y`
- `Tm5a`
- `Tm5c`
- `Tm9`
- `TmY14`
- `TmY15`
- `TmY18`
- `TmY3`
- `TmY4`
- `TmY5a`
- `TmY9`

Important detail:

- among the FlyVis `R*` photoreceptor classes, the exact overlap found in the whole-brain annotation supplement is `R7` and `R8`
- not `R1` to `R6`

So the public overlap is real, but it is not the full photoreceptor stack.

## Probe design

`scripts/run_splice_probe.py` does the following:

1. runs real FlyVis on body-free crafted visual stimuli:
   - `baseline_gray`
   - `body_left_dark`
   - `body_center_dark`
   - `body_right_dark`
2. computes per-cell-type, per-eye FlyVis activity
3. uses the official annotation supplement to gather the exact whole-brain root IDs for the same:
   - `cell_type`
   - `side`
4. builds a wide direct-input mapping:
   - each whole-brain neuron in a matched `cell_type` + `side` group receives a rate proportional to the positive FlyVis delta above baseline for that same group
5. runs the whole-brain backend body-free for a short response window
6. compares teacher and student responses at that type+side boundary

This is still a first-pass splice. It is intentionally simple:

- exact type match
- exact left/right side match
- no fabricated hemisphere splits
- no body

## Results

### 1. Wide type-level overlap is viable

From `outputs/metrics/splice_probe_summary.json`:

- `num_overlap_cell_types = 49`
- `num_complete_bilateral_cell_types = 49`

For the three non-baseline stimuli:

- `body_left_dark`
  - `teacher_student_group_correlation = 0.9881`
- `body_center_dark`
  - `teacher_student_group_correlation = 0.9885`
- `body_right_dark`
  - `teacher_student_group_correlation = 0.9913`

Interpretation:

- if the splice boundary is defined as exact `cell_type` + `side` groups
- and FlyVis teacher activity is broadcast into the matched whole-brain groups
- the whole-brain backend can preserve the broad grouped amplitude pattern very well

This is the first concrete proof in the repo that the bridge does not have to collapse down to four scalar vision features.

### 2. Left/right structure is only partially preserved

The stricter metric is the side-difference correlation:

- `body_left_dark`
  - `teacher_student_side_diff_correlation = 0.2099`
- `body_center_dark`
  - `teacher_student_side_diff_correlation = null`
- `body_right_dark`
  - `teacher_student_side_diff_correlation = 0.8819`

Interpretation:

- the broad grouped response magnitude is easy to preserve
- the left/right asymmetry is much harder
- right-side stimuli retained side structure much better than left-side or centered stimuli in this first probe

Concrete examples from `outputs/metrics/splice_probe_side_differences.csv`:

- `TmY14` under `body_right_dark`
  - teacher `right-left = -0.0753`
  - student `right-left = -12.4324`
- `T5a` under `body_left_dark`
  - teacher `right-left = 0.0471`
  - student `right-left = 4.6248`

So the sign is sometimes preserved, but the magnitude is not calibrated and the asymmetry is not stable across conditions.

### 3. The splice does not yet recruit motor output

For all three non-baseline stimuli:

- `forward_left = 0`
- `forward_right = 0`
- `turn_left = 0`
- `turn_right = 0`
- `reverse = 0`

in the short `20 ms` body-free probe window.

That means:

- a wide visually grounded type-level splice is now demonstrated
- but it still does not prove a working visual-to-motor path

## Signed + Spatial Follow-Up

The next two missing pieces from the first probe were:

1. signed external input
2. coarse retinotopic structure instead of one scalar per `cell_type` + `side`

Those are now implemented in:

- `src/brain/pytorch_backend.py`
- `src/brain/flywire_annotations.py`
- `scripts/run_splice_probe.py`

### What changed

1. The body-free probe can now run in:
   - `input_mode=current_signed`

   This uses signed direct current at the splice boundary instead of only nonnegative Poisson-rate drive.

2. The probe can now use:
   - `spatial_bins > 1`

   In the current runs that means:
   - `4` coarse bins per shared `cell_type` + `side`

   The whole-brain bins are inferred from public FlyWire spatial coordinates.
   The FlyVis bins are inferred from public FlyVis `u` coordinates.

This is still inferred retinotopy, not exact column identity matching.

### Results: signed current + 4 spatial bins, `20 ms`

Artifact:

- `outputs/metrics/splice_probe_signed_bins4_summary.json`

Key numbers:

- `body_left_dark`
  - `teacher_student_group_correlation = 0.7458`
  - `teacher_student_side_diff_correlation = 0.4132`
- `body_center_dark`
  - `teacher_student_group_correlation = 0.8186`
  - `teacher_student_side_diff_correlation = null`
- `body_right_dark`
  - `teacher_student_group_correlation = 0.7455`
  - `teacher_student_side_diff_correlation = 0.4130`

Interpretation:

- grouped fit got worse than the first broad type-level probe
- but side-difference preservation improved on the hard left/right stimuli
- and the probe is now at least capable of nonzero motor readout in the short window

Short-window motor readout:

- `body_left_dark`
  - `forward_right = 25`
  - `turn_left = 25`
- `body_right_dark`
  - `turn_left = 50`
  - `turn_right = 25`

This is still weak and not yet cleanly directional, but it is no longer a total visual-to-motor dead end.

### Results: signed current + 4 spatial bins, `100 ms`

Artifact:

- `outputs/metrics/splice_probe_signed_bins4_100ms_summary.json`

Key numbers:

- `body_left_dark`
  - `teacher_student_group_correlation = 0.7457`
  - `teacher_student_side_diff_correlation = 0.4203`
- `body_center_dark`
  - `teacher_student_group_correlation = 0.8190`
  - `teacher_student_side_diff_correlation = null`
- `body_right_dark`
  - `teacher_student_group_correlation = 0.7455`
  - `teacher_student_side_diff_correlation = 0.4188`

Motor readout over `100 ms`:

- `body_left_dark`
  - `forward_left = 35`
  - `forward_right = 45`
  - `turn_left = 35`
  - `turn_right = 25`
  - `reverse = 7.5`
- `body_right_dark`
  - `forward_left = 10`
  - `forward_right = 45`
  - `turn_left = 35`
  - `turn_right = 45`
  - `reverse = 32.5`

Important directional detail:

- the signed turn bias flips in the expected direction between left-dark and right-dark
  - left-dark: `turn_right - turn_left = -10`
  - right-dark: `turn_right - turn_left = +10`

That is not yet enough to claim a correct visual-to-motor policy.
But it is the first local body-free evidence that a more grounded splice can produce condition-dependent downstream motor asymmetry without body fallback and without direct `P9` prosthetics.

## State-Based Readouts and Calibration

The next blocker after the signed+spatial `100 ms` probe was that spike-rate deltas were still a bad calibration target for inhibitory conditions.

Negative signed drive was often real at the boundary, but looked like `0 Hz` when the monitored group was already near a quiescent baseline.

That is now fixed in the probe:

- `src/brain/pytorch_backend.py`
  - `WholeBrainTorchBackend.step_with_state(...)`
- `scripts/run_splice_probe.py`
  - now records:
    - `student_raw_voltage_mv`
    - `student_delta_voltage_mv`
    - `student_raw_conductance`
    - `student_delta_conductance`
- `scripts/run_splice_calibration.py`
  - scripted parameter sweeps for current scale and spatial bins
- `scripts/summarize_splice_calibration.py`
  - reproducible ranking over completed calibration artifacts

New artifacts:

- `outputs/metrics/splice_probe_signed_bins4_100ms_state_summary.json`
- `outputs/metrics/splice_probe_signed_bins4_100ms_state_groups.csv`
- `outputs/metrics/splice_probe_signed_bins4_100ms_state_side_differences.csv`
- `outputs/metrics/splice_probe_bins4_current20_summary.json`
- `outputs/metrics/splice_probe_bins4_current40_summary.json`
- `outputs/metrics/splice_probe_bins4_current80_summary.json`
- `outputs/metrics/splice_probe_bins2_current80_summary.json`
- `outputs/metrics/splice_probe_calibration_curated.csv`
- `outputs/metrics/splice_probe_calibration_curated.json`

### What the state readouts changed

For the current best bins=`4`, current=`120` run in:

- `outputs/metrics/splice_probe_signed_bins4_100ms_state_summary.json`

the boundary fit is much clearer in voltage/conductance than in spike rate.

Mean non-baseline correlation:

- spike-rate grouped fit: `0.7701`
- spike-rate side-difference fit: `0.4195`
- voltage grouped fit: `0.8709`
- voltage side-difference fit: `0.8079`
- conductance grouped fit: `0.8775`
- conductance side-difference fit: `0.8125`

Interpretation:

- the earlier spike-only probe was under-reporting real signed boundary responses
- inhibitory structure is now visible
- voltage and conductance are the correct primary calibration targets for this body-free splice stage

### What the calibration sweep found

The curated calibration ranking in:

- `outputs/metrics/splice_probe_calibration_curated.csv`
- `outputs/metrics/splice_probe_calibration_curated.json`

used these rules:

1. prioritize voltage-based boundary agreement
2. weight left/right side-difference preservation more heavily than broad amplitude preservation
3. reward only runs where left-dark and right-dark produce opposite signed downstream turn biases
4. penalize spike-rate saturation

Within the evaluated grid, the best compromise is:

- spatial bins: `4`
- signed-current scale: `max_abs_current = 120`
- artifact: `outputs/metrics/splice_probe_signed_bins4_100ms_state_summary.json`

Why this won:

- it preserves left/right voltage structure strongly:
  - mean voltage side-difference correlation `0.8079`
- it keeps broad grouped voltage fit high:
  - mean voltage group correlation `0.8709`
- it produces the correct downstream turn-bias flip:
  - left-dark: `turn_right - turn_left = -10`
  - right-dark: `turn_right - turn_left = +10`
- its measured spike-rate saturation fraction is still low enough to tolerate in this grid search:
  - about `1.02%`

### Why the lower-current runs did not win

The bins=`4` lower-current runs at:

- `20`
- `40`
- `80`

all preserved left/right voltage structure almost as well:

- mean voltage side-difference correlation stayed around `0.806` to `0.808`

but they failed the downstream sign check:

- `20`: left `-30`, right `-15`
- `40`: left `+10`, right `-20`
- `80`: left `-30`, right `-15`

So they still did not recruit the downstream motor readouts in a directionally correct way.

The bins=`1` and bins=`2` runs clarified the tradeoff:

- bins=`1`
  - highest broad grouped fit
  - much weaker side structure, around `0.64`
- bins=`2`
  - strong side structure around `0.81`
  - but the tested current settings still did not produce the correct downstream left/right flip

So the present calibration result is:

- coarse spatial structure is necessary
- signed current must be strong enough to push through to downstream readouts
- the best tested point is bins=`4` plus current=`120`

This is still an experimental splice calibration, not a final biological claim.

## Deeper Relay Targets and Longer Windows

After the calibrated boundary existed, the next question was whether the downstream brain response stayed coherent beyond the first motor readout window.

That is now probed by:

- `scripts/find_splice_relay_candidates.py`
- `scripts/run_splice_relay_probe.py`

New artifacts:

- `outputs/metrics/splice_relay_candidates_roots.csv`
- `outputs/metrics/splice_relay_candidates_pairs.csv`
- `outputs/metrics/splice_relay_candidates.json`
- `outputs/metrics/splice_relay_probe.csv`
- `outputs/metrics/splice_relay_probe_pairs.csv`
- `outputs/metrics/splice_relay_probe_summary.json`

### Relay candidates

The relay candidates are inferred structurally:

1. take the grounded overlap boundary roots
2. find neurons receiving strong summed input from that boundary
3. intersect with neurons that also send strong summed output to the monitored motor readout set
4. exclude the overlap cell types themselves and exclude the motor readout neurons themselves
5. keep only annotated bilateral cell types

Top paired annotated relay candidates found this way are:

- `LC31a`
- `LC31b`
- `LC19`
- `LCe06`
- `LT82a`
- `LCe04`

### Relay results at `100 ms`

Using the current calibrated splice:

- axis1d bins=`4`
- signed current=`120`

the relay probe confirms that deeper groups already carry structured left/right state before embodiment.

Examples from `outputs/metrics/splice_relay_probe_summary.json`:

- `LC31a`
  - right-minus-left voltage is negative in both asymmetric conditions
  - left-dark: about `-2.60 mV`
  - right-dark: about `-1.86 mV`
- `LCe06`
  - right-minus-left rate changes sign with the visual condition
  - left-dark: about `-6.33 Hz`
  - right-dark: about `+10.67 Hz`
- `LT82a`
  - shows the largest lateralized relay effect in this set
  - left-dark: right-minus-left rate about `-45 Hz`
  - right-dark: right-minus-left rate about `0 Hz`

At the same `100 ms` window the downstream motor turn bias still flips correctly:

- left-dark: `turn_right - turn_left = -10`
- right-dark: `turn_right - turn_left = +10`

So the calibrated splice is not only reaching the motor readouts.
It is also producing structured intermediate-target state in several plausible relay groups.

### Relay results at `500 ms`

The longer window is more revealing.

At `500 ms`:

- relay asymmetry is still present in several groups
- but the motor turn bias is no longer stable

From `outputs/metrics/splice_relay_probe_summary.json`:

- left-dark: `turn_right - turn_left = -17`
- right-dark: `turn_right - turn_left = -9`

So by `500 ms` both asymmetric conditions drift into a left-turn-biased downstream state.

Interpretation:

- the calibrated splice can launch the downstream brain response in the expected direction
- but the recurrent whole-brain dynamics do not yet preserve the sign robustly over longer windows

That is an important narrowing of the problem.
The remaining failure is no longer "visual splice is dead."
It is "initial asymmetry exists, intermediate relays respond, but the downstream policy drifts over time."

### Drift follow-up with pulsed inputs

The next question was whether the `500 ms` sign collapse was merely caused by holding the external current on for the entire observation window.

To test that, I added pulse-schedule support to the relay probe:

- `scripts/run_splice_relay_probe.py`
- `--input-pulse-ms`

I then compared:

- existing `100 ms` hold from `outputs/metrics/splice_relay_probe_summary.json`
- existing `500 ms` hold from `outputs/metrics/splice_relay_probe_summary.json`
- new `500 ms` with only a `25 ms` input pulse from `outputs/metrics/splice_relay_probe_500ms_pulse25_summary.json`

Compact comparison artifacts:

- `outputs/metrics/splice_relay_drift_comparison.csv`
- `outputs/metrics/splice_relay_drift_comparison.json`
- `scripts/summarize_relay_drift.py`

Results:

- `100 ms` hold:
  - left-dark: `-10`
  - right-dark: `+10`
  - sign preserved
- `500 ms` hold:
  - left-dark: `-17`
  - right-dark: `-9`
  - sign collapsed
- `500 ms` with only a `25 ms` pulse:
  - left-dark: `0`
  - right-dark: about `-6.32`
  - sign still not preserved

Interpretation:

- the `500 ms` failure is not just "you drove the boundary too long"
- even when the external input is cut after `25 ms`, the downstream state still fails to preserve the correct sign by `500 ms`
- that makes the remaining problem look more like recurrent downstream dynamics, readout choice, or missing normalization / state-conditioning inside the whole-brain model

## 2D UV-Grid Follow-Up

The original coarse spatial splice used:

- one inferred spatial axis on the FlyWire side
- one `u` axis on the FlyVis side

That was better than scalar pooling, but still a one-axis proxy.

To push past that, the probe now supports a `uv_grid` mode:

- FlyVis side:
  - native `u` and `v`
- whole-brain side:
  - first two public spatial principal axes from the annotation coordinates

Code:

- `src/brain/flywire_annotations.py`
- `scripts/run_splice_probe.py`

New artifacts:

- `outputs/metrics/splice_probe_uvgrid_2x2_current120_summary.json`
- `outputs/metrics/splice_probe_uvgrid_flipu_summary.json`
- `outputs/metrics/splice_probe_uvgrid_flipuv_summary.json`

### Raw 2D grid

For the unflipped `2 x 2` UV grid at current=`120`:

- mean voltage group correlation: about `0.8714`
- mean voltage side-difference correlation: about `0.8233`

This is slightly better than the calibrated axis1d splice on the boundary metrics:

- axis1d mean voltage group correlation: about `0.8709`
- axis1d mean voltage side-difference correlation: about `0.8079`

But the downstream sign is wrong:

- left-dark: `turn_right - turn_left = +35`
- right-dark: `turn_right - turn_left = -15`

So the two-dimensional boundary fit improved, but the motor sign became mirrored.

### U-flipped 2D grid

Because the whole-brain principal axes are sign-ambiguous, the probe now also supports explicit axis flips.

The best tested UV-grid variant so far is:

- `u` flipped
- `v` unchanged

Artifact:

- `outputs/metrics/splice_probe_uvgrid_flipu_summary.json`

Its boundary agreement is the strongest tested UV-grid result:

- mean voltage group correlation: about `0.8764`
- mean voltage side-difference correlation: about `0.8466`

That is better than the axis1d calibrated splice on boundary structure.

But the downstream turn sign is still not correct:

- left-dark: `turn_right - turn_left = +5`
- right-dark: `turn_right - turn_left = -10`

### Interpretation of the UV-grid result

The 2D grid work is still valuable even though it is not yet the new best overall splice.

It shows:

1. the boundary correspondence really does improve when both visual axes are preserved
2. principal-axis sign and orientation are still unresolved on the whole-brain side
3. the remaining error is not just "more dimensions are bad"
4. the remaining error is "the 2D mapping is not yet oriented correctly relative to the downstream circuit"

So the next spatial problem is now precise:

- resolve UV-grid orientation / exact column alignment, not just "add more bins"

### Targeted side-mirror follow-up

The first UV-grid follow-up still used one shared orientation transform for both hemispheres.

That was incomplete.
Because the left and right visual hemispheres are mirror-related, I next added:

- axis swap support on the whole-brain side
- side-specific horizontal mirroring on the whole-brain side

Code:

- `src/brain/flywire_annotations.py`
- `scripts/run_splice_probe.py`
- `scripts/summarize_uvgrid_targeted.py`

Artifacts:

- `outputs/metrics/splice_probe_uvgrid_mirror_summary.json`
- `outputs/metrics/splice_probe_uvgrid_flipu_mirror_summary.json`
- `outputs/metrics/splice_probe_uvgrid_flipv_mirror_summary.json`
- `outputs/metrics/splice_probe_uvgrid_swap_mirror_summary.json`
- `outputs/metrics/splice_uvgrid_targeted_comparison.csv`
- `outputs/metrics/splice_uvgrid_targeted_comparison.json`

What changed:

- boundary agreement stayed strong or improved further
- but no tested targeted side-mirror variant restored the correct downstream left-vs-right motor sign

Best targeted boundary-fit row from `outputs/metrics/splice_uvgrid_targeted_comparison.json`:

- `flip_v = true`
- `mirror_u_by_side = true`
- mean voltage group correlation: about `0.8764`
- mean voltage side-difference correlation: about `0.8467`

But its downstream turn sign is still wrong:

- left-dark: `turn_right - turn_left = -15`
- right-dark: `turn_right - turn_left = -5`

Other targeted mirror variants also fail:

- mirror only:
  - left-dark: `+20`
  - right-dark: `-20`
- `flip_u + mirror`:
  - left-dark: `+35`
  - right-dark: `0`
- `swap_uv + mirror`:
  - left-dark: `+15`
  - right-dark: `-25`

Interpretation:

- the UV-grid orientation problem is now narrower than before
- plain global flips were not enough
- side-specific horizontal mirroring was also not enough
- so the remaining blocker is not just axis sign ambiguity
- it is more likely exact column alignment, per-cell-type retinotopic mismatch, or a downstream transform beyond the coarse `2 x 2` grid

## Updated interpretation

The current best reading is:

1. exact shared `cell_type` + `side` is the right first grounded boundary
2. signed input matters
3. some coarse spatial structure matters
4. state-based readouts are required to see inhibitory boundary responses honestly
5. deeper relay targets already show structured responses under the calibrated splice
6. the current signed/spatial mapping is still crude and only calibrated within a small tested grid
7. two-dimensional UV-grid correspondence improves boundary agreement but still has an unresolved orientation/sign problem

Concrete evidence of that saturation:

- in `outputs/metrics/splice_probe_signed_bins4_groups.csv`, several `Am` bins saturate at `350 Hz`
- in the calibrated state-based run, saturation is much lower overall, but spike-rate summaries still understate negative responses

So the next blocker is no longer "does any grounded splice exist?"

It is:

- how to improve retinotopic correspondence and downstream recruitment beyond the current coarse calibrated splice

## Per-cell-type UV-grid alignment follow-up

The earlier UV-grid work established a narrower problem:

- one global transform plus optional right-side mirroring was not enough
- boundary agreement could be strong while downstream turn sign was still wrong

That left two live possibilities:

1. exact column alignment differs by cell type
2. the whole problem is purely downstream and no better spatial mapping exists

To separate those, I added per-cell-type transform support on the whole-brain side.

Code:

- `src/brain/flywire_annotations.py`
- `src/bridge/visual_splice.py`
- `scripts/run_splice_probe.py`
- `scripts/run_celltype_uvgrid_alignment_search.py`

The new path keeps the same grounded overlap:

- exact shared FlyVis / FlyWire `cell_type`
- exact `side`
- same coarse `2 x 2` UV grid

but it no longer forces every cell type to share one orientation transform.

### Search method

The new search script:

- `scripts/run_celltype_uvgrid_alignment_search.py`

does the following:

1. starts from the old best global UV-grid transform:
   - `flip_v = true`
   - `mirror_u_by_side = true`
2. ranks cell types by teacher left-vs-right asymmetry magnitude under the body-left and body-right stimuli
3. greedily tests per-cell-type overrides chosen from:
   - `swap_uv`
   - `flip_u`
   - `flip_v`
   - `mirror_u_by_side`
4. keeps any override that improves a combined score over:
   - voltage boundary agreement
   - downstream left/right turn-sign correctness

Artifacts:

- `outputs/metrics/splice_celltype_alignment_search.json`
- `outputs/metrics/splice_celltype_alignment_search.csv`
- `outputs/metrics/splice_celltype_alignment_recommended.json`

### What the search found

The strongest candidate cell types were:

- `Mi4`
- `Am`
- `T2`
- `Mi1`
- `TmY18`
- `Mi9`
- `Mi15`
- `Tm3`
- `R8`
- `T4a`
- `L2`
- `TmY14`

The selected override set is written to:

- `outputs/metrics/splice_celltype_alignment_recommended.json`

It keeps the old best global transform:

- `flip_v = true`
- `mirror_u_by_side = true`

but adds per-cell-type exceptions for a subset of visual classes, including:

- `Mi4`
- `Am`
- `T2`
- `Mi1`
- `TmY18`
- `Mi9`
- `Mi15`
- `Tm3`
- `R8`
- `T4a`
- `L2`

### Result

This is the first splice result in the repo where the coarse UV-grid sign problem is actually fixed without another prosthetic.

From `outputs/metrics/splice_celltype_alignment_search.json`:

- old best global UV-grid:
  - left turn bias: `-15`
  - right turn bias: `-5`
  - `sign_match = false`
- new per-cell-type search best:
  - left turn bias: `-50`
  - right turn bias: `+60`
  - `sign_match = true`

So the remaining blocker is not "no spatial alignment can recover the correct sign."

It is now narrower:

- coarse global alignment was too blunt
- at least part of the mismatch is genuinely cell-type-specific

### Canonical re-run

I also ran the standard body-free probe using the recommended transform file:

- `outputs/metrics/splice_probe_uvgrid_celltype_aligned_summary.json`
- `outputs/metrics/splice_probe_uvgrid_celltype_aligned_groups.csv`
- `outputs/metrics/splice_probe_uvgrid_celltype_aligned_side_differences.csv`

That canonical re-run still preserved the correct downstream sign:

- left-dark:
  - `turn_right - turn_left = -30`
- right-dark:
  - `turn_right - turn_left = +45`

So the sign correction is not only an internal search artifact.

### Comparison to the old best global UV-grid

Comparison artifact:

- `outputs/metrics/splice_celltype_alignment_comparison.json`
- `outputs/metrics/splice_celltype_alignment_comparison.csv`

What changed:

- old best global UV-grid:
  - strong boundary agreement
  - wrong downstream sign
- new per-cell-type alignment:
  - still strong boundary agreement
  - now correct downstream sign

The canonical re-run does show a modest drop in voltage boundary correlation relative to the search-internal best score.
That means the result is good enough to close the original coarse sign problem, but it does not remove the need for:

- longer-window drift analysis
- embodied validation

## Updated next splice steps

1. `T064`: explain the `500 ms` recurrent sign collapse now that the coarse spatial sign error is no longer the main blocker.
2. Test the new per-cell-type UV-grid splice in the embodied descending-only branch.

## Time-resolved drift audit after the per-cell-type splice fix

The per-cell-type UV-grid result solved the coarse sign error at `100 ms`, but it did not yet answer the long-window question.

To answer that, I added:

- `scripts/run_splice_drift_audit.py`

Artifacts:

- `outputs/metrics/splice_drift_audit_summary.json`
- `outputs/metrics/splice_drift_audit_timeseries.csv`
- `outputs/metrics/splice_drift_audit_key_findings.json`
- `docs/splice_drift_audit.md`

### What the audit tested

It used the sign-correct per-cell-type UV-grid splice:

- `outputs/metrics/splice_celltype_alignment_recommended.json`

and then compared two schedules:

1. sustained `hold`
2. `pulse_25ms`

while monitoring:

- relay groups
- the fixed tiny DN motor readout
- the broader strict descending/efferent candidate groups

### Main result

The long-window failure is **not** a total collapse of relay asymmetry.

Under sustained input:

- relay asymmetry persists through `500 ms`
- several broader descending groups still carry asymmetric rates at `500 ms`
- but the original fixed DN turn readout equalizes to zero by `500 ms`

Concrete examples:

- fixed DN turn bias:
  - `100 ms`
    - left: `-40`
    - right: `+100`
  - `500 ms`
    - left: `0`
    - right: `0`

- relay contrastive voltage:
  - `LC31a`
    - `100 ms`: `+14.53`
    - `500 ms`: `+13.81`
  - `LC31b`
    - `100 ms`: `+24.44`
    - `500 ms`: `+22.63`
  - `LCe04`
    - `100 ms`: `+5.88`
    - `500 ms`: `+5.90`

So the earlier "drift" is better understood as:

- a readout collapse in the tiny fixed DN set
- not a complete loss of asymmetric signal everywhere downstream

### What the pulse test adds

Under a `25 ms` pulse:

- relay contrastive signals decay to about zero by `500 ms`
- descending contrastive signals also decay to about zero

So the current public recurrent dynamics do **not** maintain a strong self-sustaining visuomotor state once the external splice input is removed.

### Updated interpretation

This narrows the remaining problem again:

1. `T063` showed that coarse global column alignment was too blunt
2. `T064` now shows that the old long-window failure was also partly a readout problem

So the next embodied step should not rely on the tiny fixed DN readout as the only long-window motor interpretation layer.

## What this means

### 1. We were too lossy before

The earlier scalar bridge threw away a real and publicly grounded overlap space.

This probe shows that the project can now work with:

- dozens of exact shared cell types
- explicit left/right side labels
- tens of thousands of mapped whole-brain neurons

instead of only:

- `vision_left`
- `vision_right`
- `flow_left`
- `flow_right`

### 2. This is a real splice boundary

The first credible splice boundary is now:

- exact shared visual `cell_type`
- exact `side`

not:

- scalar salience summaries
- fabricated LC4 left/right halves

### 3. The next problems are more specific

The remaining failures are now clearer:

1. the current spatial mapping is still only a coarse inferred proxy
   - even the newer UV-grid version does not yet match exact columns or exact neuron identity
2. downstream recruitment is still weak and only appears in a narrow calibrated regime
 - the splice is not yet robust enough for embodied claims
3. the current calibration grid is small
  - bins=`4`, current=`120` is only the best tested point so far, not a proven global optimum
4. longer-window downstream dynamics still drift
   - the relay probe shows that the initial asymmetry is present, but the downstream turn sign is not stable by `500 ms`

## Next splice steps

1. Improve retinotopy.
   - The probe now has both coarse one-axis bins and an experimental UV-grid splice.
   - The next issue is resolving the UV-grid orientation / exact column alignment so the improved boundary match also preserves downstream sign.

2. Probe deeper central targets.
   - The relay probe now identifies candidate intermediate groups and shows that several carry structured left/right state.
   - The next issue is understanding why the motor turn sign drifts over longer windows even though those deeper groups are active.

3. Only return to the body after the visual splice can both:
   - preserve asymmetry robustly
   - and drive a nontrivial downstream brain response

## Embodied follow-up

The body loop has now been re-entered with the calibrated splice held fixed and only the output side broadened.

Evidence:

- `docs/descending_readout_expansion.md`
- `outputs/metrics/descending_readout_comparison.csv`

What changed:

- no new prosthetic `P9` mode was added
- no optic-lobe-as-motor shortcut was used
- the only change was replacing the old tiny embodied output bottleneck with a strict descending/efferent supplemental readout selected from the body-free descending probe

What that proved:

- the body-free splice direction was not the main remaining problem by itself
- the embodied loop was also bottlenecked by the old descending readout choice
- once the embodied output side was widened using grounded descending/efferent candidates, the run moved from local dithering to meaningful traversal
