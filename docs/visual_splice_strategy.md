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
