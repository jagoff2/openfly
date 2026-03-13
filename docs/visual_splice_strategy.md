# Visual Splice Strategy

## Why This Doc Exists

The previous bridge iterations proved three things:

1. The repo can run the real whole-brain backend online.
2. The repo can run real FlyGym realistic vision online.
3. A small scalar bridge between those systems is not good enough.

This document records the corrected understanding in detail so the work can continue correctly after context compaction.

## Corrected Diagnosis

### 1. The strict public bridge failed honestly

Once the hidden locomotor scaffolding was removed:

- no decoder idle-drive floor
- no fake left/right split of bilateral public sensory pools
- no body-side locomotor fallback

the strict production path did not yield convincing locomotion. It produced sparse local twitching, not sustained walking.

That means the public-equivalent bridge, as previously implemented, is missing something fundamental.

### 2. The inferred `P9` modes are still prosthetic

Both of these are experiments, not final answers:

- `public_p9_context`
- `inferred_visual_p9_context`

They can make the animal move, but they do so by externally stimulating locomotor-related neurons on the brain-input side. That is cleaner than hidden body fallback, but it is still a prosthetic intervention.

### 3. The compression step is one of the main failures

The previous production bridge compressed the rich FlyVis state into a very small number of scalars:

- left salience
- right salience
- left flow
- right flow

and then further collapsed those into bilateral public pools for the whole-brain backend.

That loses:

- left/right sign structure
- motion-direction structure
- cell-family-specific structure
- spatial structure

This is likely one of the main reasons the bridge failed.

## Why This Is A Splice Problem

At a high level, both sides cover real visual biology:

- FlyVis simulates a connectome-constrained fly visual system
- the whole-brain connectome contains real visual circuitry

So the right problem is not "make more scalar features" and it is not "force locomotion harder." The right problem is:

- pick a visual splice boundary
- preserve a much wider visual representation
- map that representation into the whole-brain model at the chosen boundary
- validate the overlap directly

## What "Use FlyVis As A Teacher" Means

For the overlapping visual populations:

1. present the same controlled stimulus to FlyVis
2. derive candidate brain-input activity from that stimulus
3. run the whole-brain model
4. compare overlapping population responses
5. fit or derive the mapping until the overlap behaves plausibly

This is a teacher-student workflow:

- FlyVis provides the richer, experimentally grounded visual target behavior
- the whole-brain backend must reproduce compatible activity at the splice boundary

## Why This Should Be Body-Free First

The user is correct: the next iteration loop should not include the FlyGym body.

The body makes iteration much slower and confounds the question. The next fast loop only needs:

- controlled visual stimuli
- FlyVis
- the whole-brain backend
- overlap-comparison metrics

This lets us ask the actual question:

- can we define a defensible visual splice?

before we ask the harder embodied question:

- does that splice drive behavior?

## Immediate Work Items

### 1. Inspect FlyVis metadata for identity grounding

We need to know whether FlyVis nodes expose enough identity information to support more than a cell-family splice:

- root IDs
- type names
- column IDs
- any direct correspondence to the whole-brain graph

If this exists, the splice can be much better grounded.

Status update:

- `scripts/inspect_flyvis_overlap.py` showed that FlyVis metadata alone does not expose direct FlyWire root IDs.
- The official FlyWire annotation supplement in `outputs/cache/flywire_annotation_supplement.tsv` does expose:
  - `root_id`
  - `cell_type`
  - `side`
- That is enough to ground the whole-brain side of the splice by exact public `cell_type` + `side`.
- It is not enough to ground the FlyVis side by exact neuron identity.

### 2. Build a wide visual payload

Stop reducing the visual state to a few scalars in the experimental branch.

The bridge should preserve:

- cell family
- eye
- and as much spatial structure as is practical

Status update:

- `scripts/run_splice_probe.py` now proves there are `49` exact shared visual cell types between FlyVis and the official FlyWire annotation supplement.
- The first body-free wide splice uses those exact shared `cell_type` labels plus `side`, not scalar salience summaries.
- See `docs/splice_probe_results.md`.

### 3. Build a body-free splice harness

Need a script that:

- feeds the same stimuli into FlyVis
- derives candidate mapped brain inputs
- runs the whole-brain backend
- measures agreement on the chosen overlap populations

Status update:

- `scripts/run_splice_probe.py` now exists and has been run in WSL.
- Results:
  - grouped teacher/student correlation is high: about `0.988` to `0.991`
  - side-difference preservation is mixed: weak for left/center, stronger for right
  - short-window motor readouts remain zero
- So the project now has a grounded body-free splice harness, but not yet a visual-to-motor proof.
- See:
  - `outputs/metrics/splice_probe_summary.json`
  - `outputs/metrics/splice_probe_groups.csv`
  - `outputs/metrics/splice_probe_side_differences.csv`
  - `docs/splice_probe_results.md`

Further status update:

- The probe now also supports:
  - signed direct current at the splice boundary
  - coarse spatial bins
- In the signed+spatial `100 ms` probe:
  - downstream motor readouts become nonzero
  - left vs right visual conditions produce opposite signed turn-bias differences
- This is still not an embodied proof, but it is the first body-free evidence that a grounded visual splice can reach downstream motor readouts without `P9` prosthetics.
- See:
  - `outputs/metrics/splice_probe_signed_bins4_summary.json`
  - `outputs/metrics/splice_probe_signed_bins4_100ms_summary.json`
  - `docs/splice_probe_results.md`

### 4. Use proper baselines

The acceptable baselines now are:

- zero-brain
- no-target / vision-ablated
- overlap-agreement under shared stimuli

Broken historical modes are diagnostics only and must not be used as success targets.

## What Not To Do

- do not treat `public_p9_context` as success
- do not treat `inferred_visual_p9_context` as success
- do not use old broken modes as acceptance baselines
- do not compress the visual state down to a handful of scalars in the experimental splice path
- do not return to body-loop tuning until the splice itself is grounded

## Current Conclusion

The project is now at a more precise stage:

- the body loop exists
- the vision model exists
- the whole-brain model exists
- the missing piece is the visual splice

That splice should now be attacked directly, offline, and with much richer signals than the previous bridge allowed.

The current best grounded splice boundary is:

- exact shared visual `cell_type`
- exact `side`

and the current best experimental refinement is:

- coarse spatial bins within each shared `cell_type` + `side`
- signed external current instead of positive-only Poisson drive

The next missing pieces are:

- better retinotopic correspondence beyond the current inferred spatial-bin proxy
- downstream validation beyond the boundary groups themselves

Update after the latest body-free probe work:

- state-based boundary readouts now exist in the probe
- voltage and conductance correlations are now the primary calibration metrics
- the current best tested splice point is:
  - `4` spatial bins
  - signed current with `max_abs_current = 120`
  - artifacts:
    - `outputs/metrics/splice_probe_signed_bins4_100ms_state_summary.json`
    - `outputs/metrics/splice_probe_calibration_curated.json`

Why that point matters:

- it preserves left/right boundary structure strongly in voltage space, about `0.808`
- it preserves broad grouped voltage structure well, about `0.871`
- it is the only tested configuration so far that also flips downstream turn bias in the expected left-vs-right direction

What is still unresolved:

- the spatial bins are still inferred, not exact retinotopic column identity
- the downstream motor recruitment is still weak and only appears in a narrow calibrated regime
- this is enough to justify the splice direction, not enough to claim embodied parity

Further update after the relay and `uv_grid` follow-up:

- the project now has a reproducible relay-target finder:
  - `scripts/find_splice_relay_candidates.py`
- the project now has a dedicated deeper relay probe:
  - `scripts/run_splice_relay_probe.py`
- the project now has an experimental two-dimensional spatial splice mode:
  - `scripts/run_splice_probe.py --spatial-mode uv_grid`

What that follow-up proved:

- the calibrated splice is not only reaching the monitored motor readouts
- it is also producing structured left/right state in deeper annotated relay groups such as:
  - `LC31a`
  - `LC31b`
  - `LC19`
  - `LCe06`
  - `LT82a`
  - `LCe04`
- at `100 ms`, the calibrated body-free splice still preserves the expected downstream turn-sign flip
- at `500 ms`, that downstream turn sign drifts, even though several intermediate relay groups still show asymmetric state

What the `uv_grid` work clarified:

- preserving both FlyVis visual axes improves boundary agreement beyond the earlier one-axis splice
- the best tested `uv_grid` variant so far is `flip_u`
- but the downstream turn sign is still mirrored or wrong

Further targeted update:

- the repo now also supports:
  - axis swap on the whole-brain side
  - side-specific horizontal mirroring on the whole-brain side
- targeted comparison artifacts:
  - `outputs/metrics/splice_uvgrid_targeted_comparison.csv`
  - `outputs/metrics/splice_uvgrid_targeted_comparison.json`

That follow-up narrows the spatial blocker further:

- boundary fit can stay very strong, about `0.876` group and about `0.847` side correlation
- but no tested targeted orientation + mirror variant restores the correct downstream sign
- so the remaining error is not just a global left/right mirror or PCA sign ambiguity
- it is now more likely exact column alignment, per-cell-type retinotopic mismatch, or a downstream transform beyond the coarse `2 x 2` grid

Further temporal update:

- the relay probe now supports pulsed input schedules via `--input-pulse-ms`
- comparison artifacts:
  - `outputs/metrics/splice_relay_drift_comparison.csv`
  - `outputs/metrics/splice_relay_drift_comparison.json`

That follow-up narrows the temporal blocker further:

- `100 ms` hold still launches the correct sign
- `500 ms` hold collapses the sign
- `500 ms` with only a `25 ms` pulse still fails to preserve the sign
- so the longer-window failure is not only "persistent external drive was left on too long"
- it now points more directly to recurrent downstream drift or missing state conditioning

So the next spatial problem is no longer:

- "do we need more than one spatial axis?"

It is now:

Further embodied update after the per-cell-type UV-grid follow-up:

- the per-cell-type UV-grid splice was tested directly in the embodied descending-only branch
- matched artifacts now exist for:
  - target + real brain
  - no target + real brain
  - zero brain
- summary artifacts:
  - `outputs/metrics/descending_uvgrid_visual_drive_validation.json`
  - `outputs/metrics/descending_uvgrid_vs_axis1d_comparison.json`

What that embodied follow-up showed:

- the branch remains brain-driven because the matched `zero_brain` run still collapses to zero commands and negligible displacement
- but the per-cell-type UV-grid splice does **not** beat the current axis1d descending baseline in embodiment
- target-bearing steering correlation regressed from about `0.723` to about `0.459`
- target-run net displacement regressed from about `4.94` to about `4.28`
- target-run forward speed regressed from about `4.33` to about `3.67`

So the body-free sign-correct splice is now a stronger experimental boundary result than it is an embodied production result.

Current embodied decision:

- keep `configs/flygym_realistic_vision_splice_axis1d_descending_readout.yaml` as the main embodied branch
- keep the per-cell-type UV-grid splice as an experimental branch until it exceeds the axis1d branch on target modulation and bearing tracking

Latest decoder-calibration update:

- that embodied limitation is now materially changed
- the repo now has a UV-grid-specific decoder calibration:
  - `scripts/run_uvgrid_decoder_calibration.py`
  - `outputs/metrics/uvgrid_decoder_calibration_best.json`
  - `docs/uvgrid_decoder_calibration.md`

What changed:

- the per-cell-type UV-grid splice itself was not the final embodied blocker
- the main embodied mismatch was downstream calibration
- after calibrating the decoder specifically for the UV-grid signal statistics, the UV-grid embodied branch now exceeds both:
  - the old UV-grid branch
  - the old axis1d descending branch

Current embodied decision is therefore now:

- use `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated.yaml` as the strongest embodied branch
- keep the older axis1d branch as the previous baseline, not the current best result

- "how do we orient and align the two-dimensional visual columns correctly relative to the downstream circuit?"

And the next temporal problem is no longer:

- "does any downstream signal appear?"

It is now:

- "why does the correct `100 ms` downstream sign collapse by `500 ms`?"

Further embodied update after the descending-only readout expansion:

- the embodied splice path is no longer limited to the original tiny DN readout bottleneck
- a strict descending/efferent supplemental readout is now available:
  - `configs/flygym_realistic_vision_splice_axis1d_descending_readout.yaml`
  - `docs/descending_readout_expansion.md`
- that branch keeps the visual splice fixed and changes only the output side
- result:
  - meaningful embodied traversal finally appears without optic-lobe-as-motor shortcuts
  - `net_displacement` improves from about `0.113` to about `5.633` over the matched `2 s` run
  - `displacement_efficiency` improves from about `0.052` to about `0.618`

So the splice problem is now narrower than before:

- the input splice was not the only blocker
- the output-side readout bottleneck was also fundamental
- the current remaining questions are now:
- whether the chosen descending-only supplemental readout is the right one biologically
- whether matched ablations still confirm the new traversal is brain-driven in this exact branch
- how much more of the remaining mismatch is still input-side versus downstream recurrent / motor-structure mismatch

Further body-free update after per-cell-type UV-grid alignment:

- the repo now supports per-cell-type UV-grid transform overrides on the whole-brain side:
  - `src/brain/flywire_annotations.py`
  - `src/bridge/visual_splice.py`
  - `scripts/run_splice_probe.py`
- a dedicated greedy body-free search now exists:
  - `scripts/run_celltype_uvgrid_alignment_search.py`

What that follow-up proved:

- the remaining UV-grid error was not purely downstream
- one shared global orientation transform was too blunt
- a per-cell-type alignment can recover the correct downstream left/right turn sign in the body-free splice probe

Evidence:

- `outputs/metrics/splice_celltype_alignment_search.json`
- `outputs/metrics/splice_celltype_alignment_recommended.json`
- `outputs/metrics/splice_probe_uvgrid_celltype_aligned_summary.json`

Why this matters:

- old best global UV-grid:
  - good boundary fit
  - wrong downstream sign
- new per-cell-type UV-grid:
  - still good boundary fit
  - correct downstream sign

So the next blocker is now narrower again:

- not "can any grounded UV-grid mapping launch the right sign?"
- now "why does that sign still drift over longer windows, and does the improved mapping help the embodied branch?"

Further update after the time-resolved drift audit:

- the repo now has a time-resolved body-free drift audit:
  - `scripts/run_splice_drift_audit.py`
  - `docs/splice_drift_audit.md`

What that audit proved:

- the old `500 ms` failure is not a complete collapse of relay asymmetry
- under sustained input, several relay groups keep strong left-vs-right contrast through `500 ms`
- several broader descending/efferent groups also remain asymmetric
- but the original tiny fixed DN motor readout equalizes by `500 ms`

What the pulse schedule proved:

- once the external input is removed after `25 ms`, both relay and descending asymmetry decay almost completely
- so the current public recurrent dynamics do not maintain a strong self-sustaining visuomotor state after a brief launch pulse

This narrows the long-window problem further:

- one part is a brittle fixed-readout problem
- the other part is missing persistent internal state after brief input

Further update after the first neck-output atlas phase:

- the repo now has both:
  - a broad observational descending/efferent atlas
  - a first causal descending motor-response atlas

Evidence:

- `docs/descending_monitoring_atlas.md`
- `docs/descending_motor_atlas.md`
- `outputs/metrics/descending_motor_atlas_summary.json`

Why this matters for splice interpretation:

- the grounded visual splice is no longer being evaluated only through the
  original tiny DN readout
- we now know that the embodied stack can translate selected descending groups
  into distinct body/controller effects

Current causal summary:

- strongest bilateral forward effects:
  - `DNp103`
  - `DNp18`
  - `DNg97`
- strongest mirrored turn effect:
  - `DNpe040`
- secondary mirrored turn effect:
  - `DNpe056`
- unresolved sign/body-mapping ambiguity:
  - `DNp71`

So the next bottleneck after the visual splice is now even clearer:

- fit a broader neck-output motor basis from the causal atlas
- then re-evaluate the embodied branch
