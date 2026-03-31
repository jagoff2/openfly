# Creamer 2018 Visual Speed Control Note

Paper:
- Creamer, M. S., Mano, O., Clark, D. A. *Visual Control of Walking Speed in Drosophila*. Neuron 100, 1460-1473 (2018). DOI: `10.1016/j.neuron.2018.10.028`
- Local copy reviewed: [mmc4.pdf](/G:/flysim/mmc4.pdf)

## Core Findings In The Paper

The paper reports four directly relevant results:

1. Flies slow in response to visual motion and use that signal to stabilize
   walking speed.
2. The slowing response is tuned to the speed of visual motion, not simply to
   generic scene content.
3. In a closed-loop virtual environment, visual gain manipulations change
   walking speed, and flies slow near nearby objects in an hourglass-style
   corridor.
4. The behavior depends on `T4` / `T5` motion pathways, and the authors fit a
   simple multi-motion-detector model to explain the behavior.

## Does OpenFly Replicate This Today?

Short answer:

- **partially in architecture and qualitative overlap**
- **not yet in the paper's controlled experimental sense**

## Replication Matrix

| Paper claim | OpenFly status | Honest verdict | Why |
| --- | --- | --- | --- |
| Visual motion modulates walking speed | The embodied branch is visually modulated, and the vision path explicitly includes `flow_left` / `flow_right` from `T4` / `T5`-like cells. | `partial` | We have visual-motion-sensitive locomotor modulation, but not the paper's isolated speed-control assay. |
| Slowing is tuned to visual speed | Not directly measured. | `no` | We do not currently run open-loop drifting-grating speed sweeps or quantify walking-speed tuning curves against stimulus speed. |
| Closed-loop visual gain stabilizes walking speed | Not directly measured. | `no` | We do not currently run the paper's gain-manipulation experiment where stimulus velocity is yoked to the fly's walking speed. |
| Flies slow near nearby objects in hourglass corridor | Not directly measured. | `no` | We do not currently implement the paper's 1D hourglass virtual hallway assay. |
| Dependence on `T4` / `T5` | We use `T4` / `T5` families in the fast visual feature path and they appear prominently in activation analysis. | `partial` | This is overlap in mechanism and signal path, not a causal ablation result. We have not shown that silencing `T4` / `T5` removes the behavior. |
| Multi-motion-detector model explains the behavior | Not replicated. | `no` | We do not currently fit or compare the paper's hierarchical speed-control model. |

## What We Do Already Have

The current repo does contain the right raw ingredients for a future replication:

- realistic vision in the embodied loop
- explicit `flow_left` / `flow_right` features derived from `T4` / `T5`-family
  activity in [feature_extractor.py](/G:/flysim/src/vision/feature_extractor.py)
- a closed-loop embodied runtime where the visual environment can be scripted in
  [flygym_runtime.py](/G:/flysim/src/body/flygym_runtime.py)
- logging and behavior metrics that could support speed-control assays

So the paper is useful, but mostly as a **next validation target**, not as a
claim we have already achieved.

## Most Important Implication For OpenFly

This paper adds a biologically grounded translational-control benchmark that is
currently missing from the repo.

Right now, most of the active work is about:

- target fixation
- perturbation-linked reorientation
- spontaneous-state plausibility
- heading / goal / steering structure

Creamer 2018 says we also need a separate visual-speed-control program:

- open-loop motion-speed sweeps
- closed-loop gain stabilization
- nearby-object slowing / collision-avoidance style assay
- `T4` / `T5` causal ablation test

That would let the repo distinguish:

- steering control
- translational speed control

instead of treating locomotion as one blended output variable.

## Bottom Line

The paper informs the project meaningfully.

It does **not** show that OpenFly already replicates those findings.
It shows that OpenFly currently has:

- the right visual ingredients
- some qualitative overlap
- but no direct controlled replication yet

So the honest verdict is:

- **Can we replicate it?** Probably yes, with new assays and ablations.
- **Do we replicate it now?** Not yet.

## March 28, 2026 Creamer Pilot Update

The first embodied corridor pilot was useful, but it exposed a real assay
confound.

### What we tested

We added a scripted stripe-corridor arena and ran a matched `1.0 s`
open-loop-drift pair:

- baseline living pilot:
  [summary.json](/G:/flysim/outputs/creamer2018_pilot/flygym-demo-20260328-102823/summary.json)
- matched `T4` / `T5` ablation:
  [summary.json](/G:/flysim/outputs/creamer2018_pilot_t4t5_ablated/flygym-demo-20260328-113311/summary.json)

### What we learned

The initial visual-speed-control effect was **not yet an honest `T4` / `T5`
dependence result**.

`T4` / `T5` ablation correctly zeroed the fast visual `flow_left` /
`flow_right` features, but the behavioral effect barely moved:

- baseline `speed_fold_change = 0.9369`
- ablated `speed_fold_change = 0.9343`

That forced a causal diagnosis. The current first-pass Creamer pilot was still
using two strong non-paper routes:

1. the public sensory encoder drove the brain from generic visual salience, not
   from motion flow
2. the visual splice still injected very large non-motion current from many
   other visual cell types

So the original pilot was a **generic visual-load slowing assay**, not yet a
motion-specific Creamer replication.

### What changed in the repo

To fix that, the assay branch now has a motion-only configuration:

- [motion-only config](/G:/flysim/configs/flygym_visual_speed_control_living_motion_only.yaml)
- [motion-only ablated config](/G:/flysim/configs/flygym_visual_speed_control_living_motion_only_t4t5_ablated.yaml)

Key changes:

- the Creamer motion-only configs set `encoder.visual_gain_hz = 0.0`, so the
  generic salience-to-public-input route is disabled
- the visual splice now supports `include_cell_types` /
  `exclude_cell_types`, and the motion-only assay restricts splice input to
  `T4a/T4b/T4c/T4d/T5a/T5b/T5c/T5d`
- the corridor assay camera is pinned back to a fixed bird's-eye view

This makes the next baseline/ablation pair much cleaner: the brain can still be
driven by realistic vision, but the assay is no longer dominated by generic
object-salience channels.

### Current live state

The motion-only matched pair is now complete:

- baseline:
  [summary.json](/G:/flysim/outputs/creamer2018_motion_only/flygym-demo-20260328-115812/summary.json)
- matched `T4/T5` ablation:
  [summary.json](/G:/flysim/outputs/creamer2018_motion_only_t4t5_ablated/flygym-demo-20260328-120740/summary.json)

This pair is much cleaner than the original pilot because the generic public
salience route is truly off:

- `public_input_rates.vision_bilateral = 0.0` in the motion-only branch
- the ablated branch keeps `visual_splice.nonzero_root_count = 0`

### What the motion-only pair proved

It **still does not replicate the paper**.

The speed-control effect survives almost unchanged even after removing the
entire intended motion pathway:

- motion-only baseline `speed_fold_change = 0.9245`
- motion-only `T4/T5` ablation `speed_fold_change = 0.9340`

That is a much stronger falsification than the first confounded pilot. It says
the current corridor behavior is still not an honest motion-pathway result.

### Additional assay failure discovered

The embodied free-walking geometry is also invalid as a Creamer analogue in its
current form.

Across the full `1.0 s` motion-only runs:

- baseline corridor occupancy fraction: `0.28`
- ablated corridor occupancy fraction: `0.28`
- baseline final `|y|`: `21.12 mm`
- ablated final `|y|`: `21.37 mm`
- nominal corridor half-width: `6.0 mm`

So the fly spends most of the run **outside the intended corridor**. That means
the current assay is mixing:

- spontaneous turning bias
- unconstrained lateral drift
- time-varying locomotor state
- moving visual walls that are no longer the fly's dominant spatial context

In other words, the current free-walking corridor branch is not yet measuring
the same controlled variable as the paper.

### Runtime regression resolved

There was also a separate runtime bug during the Creamer probe work: the fly
body appeared briefly and then vanished from the demo. That turned out to be a
real physical failure, not only a video issue.

In the broken short probe:

- [broken run log](/G:/flysim/outputs/creamer2018_body_visibility_probe_fixed/flygym-demo-20260328-123946/run.jsonl)
- body `position_z` crossed below zero by cycle `5`
- final body `position_z = -499.112 mm`

So the fly was actually falling out of the world.

The root causes were:

- the Creamer corridor arena used a hand-rolled ground plane instead of
  FlyGym's proven flat-terrain floor contract
- the runtime claimed `camera_mode: fixed_birdeye`, but corridor runs still
  silently forced tracked overhead camera parameters

Both are now fixed:

- [flygym_runtime.py](/G:/flysim/src/body/flygym_runtime.py)
- [visual_speed_control.py](/G:/flysim/src/body/visual_speed_control.py)

The repaired short WSL probe is:

- [fixed run log](/G:/flysim/outputs/creamer2018_body_visibility_probe_fixed_floor/flygym-demo-20260328-124552/run.jsonl)

In the repaired probe:

- no negative Z values occurred
- body `position_z` stayed within `1.0498 .. 1.5862 mm`
- extracted frames remained available through the end of the short run:
  - [frame 1](/G:/flysim/outputs/creamer2018_body_visibility_probe_fixed_floor/flygym-demo-20260328-124552/framecheck/frame_01.png)
  - [frame 2](/G:/flysim/outputs/creamer2018_body_visibility_probe_fixed_floor/flygym-demo-20260328-124552/framecheck/frame_02.png)

That means the current blocker is back where it should be: assay validity, not
body disappearance.

## Updated Bottom Line

The Creamer workstream is now in a better scientific state than before, because
the current failures are explicit rather than hidden.

What is now established:

- the original pilot was confounded
- the motion-only pair still fails to show `T4/T5` dependence
- the free-walking corridor geometry itself is invalid for this assay because
  the fly rapidly leaves the corridor

So the next valid replication step is **not** another gain tweak. It is a
better assay geometry, likely treadmill-like or otherwise constrained, where
the fly remains in the visual corridor long enough for the stimulus variable to
be meaningfully controlled.

## March 28, 2026 Treadmill-Ball Redesign And Parity Verdict

The free-walking corridor is no longer the active Creamer assay geometry. The
current active assay is a tethered treadmill-ball branch intended to approximate
the paper's ball / virtual-environment regime more honestly.

### What changed

- added a treadmill-ball geometry in
  [visual_speed_control.py](/G:/flysim/src/body/visual_speed_control.py)
- switched the Creamer treadmill configs to:
  - `geometry: treadmill_ball`
  - `spawn_pos: [0.0, 0.0, 0.3]`
  - `fly_init_pose: tripod`
- changed treadmill speed measurement to preserve sign instead of taking
  absolute speed
- updated the Creamer runner default to the treadmill motion-only config in
  [run_creamer2018_replication.py](/G:/flysim/scripts/run_creamer2018_replication.py)

### What the treadmill branch establishes

The treadmill-ball geometry is mechanically valid enough to use as the
biologically plausible Creamer assay frame.

Short contact smoke:

- [summary.json](/G:/flysim/outputs/creamer2018_treadmill_contact_smoke_tripod/flygym-demo-20260328-132147/summary.json)
- `spontaneous_locomotion_mean_forward_speed = 195.33 mm/s`
- `visual_speed_control_pre_mean_forward_speed = 192.85 mm/s`
- run remained stable and produced the full activation bundle

Important interpretation note:

- on a treadmill-ball assay, world-frame displacement is not the primary speed
  variable
- the relevant observable is the treadmill-measured forward speed in
  `visual_speed_control_*`, not the near-zero world-frame `avg_forward_speed`

### Baseline And Ablation Results

Baseline treadmill run:

- [summary.json](/G:/flysim/outputs/creamer2018_treadmill_baseline_1p2s_tripod/flygym-demo-20260328-132636/summary.json)
- `pre_mean_forward_speed = 223.20 mm/s`
- `stimulus_mean_forward_speed = 243.48 mm/s`
- `speed_fold_change = 1.0909`
- `scene_speed_mean = -30.0 mm/s`

Matched `T4/T5` ablation:

- [summary.json](/G:/flysim/outputs/creamer2018_treadmill_ablation_1p2s_tripod/flygym-demo-20260328-133246/summary.json)
- `pre_mean_forward_speed = 223.24 mm/s`
- `stimulus_mean_forward_speed = 243.49 mm/s`
- `speed_fold_change = 1.0907`
- `scene_speed_mean = -30.0 mm/s`

Compact pair summary:

- [creamer2018_treadmill_tripod_pair_summary.json](/G:/flysim/outputs/metrics/creamer2018_treadmill_tripod_pair_summary.json)

### What This Means

The current biologically plausible treadmill regime still fails Creamer parity.

Failure 1, wrong sign:

- the fly speeds up under front-to-back scene motion instead of slowing
- baseline fold change is `1.0909`, not `< 1`

Failure 2, no causal `T4/T5` dependence:

- baseline mean nonzero splice root count was about `12217.6`
- ablated mean nonzero splice root count was `0.0`
- despite that, the speed effect barely changed:
  - baseline `speed_fold_change = 1.0908718`
  - ablated `speed_fold_change = 1.0907094`

So the present speed-up effect is not being carried by the intended `T4/T5`
motion pathway in any meaningful causal sense.

### Additional Confound: The Treadmill Ball Is Visually Textured

There is also a real visual confound in the current treadmill branch.

The active treadmill arena subclasses FlyGym's upstream
`flygym.arena.tethered.Ball`, and that class creates the ball with a visible
checker texture and material:

- upstream source:
  [tethered.py](/G:/flysim/external/flygym/flygym/arena/tethered.py)

In other words, the treadmill is not visually blank. The fly is standing over a
moving chequered sphere unless we explicitly neutralize or hide it in the
vision render path.

That matters because:

- it can add strong self-motion-linked optic flow unrelated to the paper's
  intended wall-motion stimulus
- it is not part of a clean Creamer-style visual scene
- it should be removed or visually neutralized before any future positive
  replication claim

But it is **not** sufficient to explain the current null causal result by
itself.

Why not:

- in the matched treadmill pair, the baseline run had large motion splice drive
  (`nonzero_root_count_mean ~ 12217.6`)
- the matched `T4/T5` ablation reduced that to exactly `0.0`
- yet the behavioral speed-up effect remained essentially unchanged

So the treadmill texture is a legitimate assay contaminant, but the current
wrong-sign, ablation-insensitive speed phenotype still points to a deeper
remaining non-Creamer control path or sign inversion in the living branch.

### March 28, 2026 Treadmill Texture Fix

The treadmill texture issue is now fixed in the assay code.

The fix is in
[visual_speed_control.py](/G:/flysim/src/body/visual_speed_control.py):

- `VisualSpeedBallTreadmillArena.pre_visual_render_hook(...)`
- `VisualSpeedBallTreadmillArena.post_visual_render_hook(...)`

Those hooks now hide the treadmill sphere only during the fly's own visual
render pass and restore it immediately afterward. That preserves the ball as a
mechanical support while removing it as an optic-flow contaminant for the fly's
realistic vision pipeline.

So the current Creamer treadmill branch no longer has to be interpreted as
"moving walls plus a visible chequered ball" from the fly's perspective.

Current status after the fix:

- treadmill texture confound: `resolved in code`
- focused regression slice:
  - `python -m pytest tests/test_visual_speed_control.py tests/test_closed_loop_smoke.py -q`
  - `50 passed`

Important boundary:

- this fixes a legitimate visual contaminant
- it does **not** by itself prove that the current branch now matches Creamer
- the next honest step is to rerun the treadmill baseline / ablation pair and
  see whether parity moves toward the paper once the ball is hidden from the
  fly's visual input

### March 28, 2026 Open-Loop Bug Fix And Parity-Mismatch Diagnosis

The treadmill texture was not the main cause of the Creamer failure. The next
diagnostic pass exposed a more important assay bug and then isolated the real
remaining mismatch.

#### Corrected treadmill open-loop semantics

The treadmill `open_loop_drift` implementation was incorrectly subtracting the
fly's own virtual track from the scene. That made the supposed open-loop
retinal slip dominated by treadmill walking speed instead of the imposed scene
motion.

That bug is now fixed in
[visual_speed_control.py](/G:/flysim/src/body/visual_speed_control.py):

- treadmill `open_loop_drift` no longer subtracts virtual-track motion from
  the scene
- motion-direction labels are now explicit `front_to_back` /
  `back_to_front`, replacing the ambiguous `ftb` / `btf`
- the metrics path now exposes `retinal_slip_*` explicitly in
  [visual_speed_control_metrics.py](/G:/flysim/src/analysis/visual_speed_control_metrics.py)

This matters because the old ball-hidden treadmill run had a nominal
`scene_speed_mean_mm_s = -30.0`, but a retinal slip of about
`-273.49 mm/s`, which was not a clean Creamer analogue:

- [old corrected-but-bugged summary.json](/G:/flysim/outputs/creamer2018_treadmill_baseline_1p2s_tripod_ballhidden_suite/open_loop/flygym-demo-20260328-173402/summary.json)

#### Slower corrected open-loop runs

After that semantic fix, the treadmill branch was rerun at much lower
front-to-back drift speeds:

- corrected `-8 mm/s`:
  [summary.json](/G:/flysim/outputs/creamer2018_treadmill_baseline_1p2s_tripod_ballhidden_slow_sweep/open_loop/flygym-demo-20260328-180808/summary.json)
- corrected `-4 mm/s`:
  [summary.json](/G:/flysim/outputs/creamer2018_treadmill_baseline_1p2s_tripod_ballhidden_slow_sweep/open_loop/flygym-demo-20260328-181336/summary.json)

Those runs now really are low-slip:

- `-8 mm/s` run: `retinal_slip_mean_mm_s = -8.0`
- `-4 mm/s` run: `retinal_slip_mean_mm_s = -4.0`

But the measured effect did **not** change:

- `-8 mm/s`: `speed_fold_change = 1.091058`
- `-4 mm/s`: `speed_fold_change = 1.091062`

So the old huge-slip bug was real, but fixing it did not change the parity
verdict.

#### Stationary control

The decisive control is a corrected open-loop run with **zero** imposed scene
motion:

- stationary `0 mm/s`:
  [summary.json](/G:/flysim/outputs/creamer2018_treadmill_stationary_control_1p2s/open_loop/flygym-demo-20260328-182539/summary.json)

That run still shows the same apparent "stimulus effect":

- `scene_speed_mean_mm_s = 0.0`
- `retinal_slip_mean_mm_s = 0.0`
- `speed_fold_change = 1.091078`

So the current assay reports the same speed-up even when there is no visual
motion at all.

#### Actual diagnosis

The Creamer parity mismatch is currently caused by an **endogenous treadmill
locomotor ramp** in the living branch, not by a true visual-speed-control
response.

The current `speed_fold_change` metric is computed as:

- `stimulus_mean_forward_speed / pre_mean_forward_speed`

In these living treadmill runs, that ratio is being driven by the branch's own
internal locomotor trajectory:

- the branch ramps up from about `223.21 mm/s` in the pre window to about
  `243.54 mm/s` in the later stimulus window
- it does that at `-30`, `-8`, `-4`, and `0 mm/s`
- it does that even after `T4/T5` ablation
- the controller also remains in a highly persistent one-sided turning state
  with essentially zero switch rate

So the current assay is not yet measuring Creamer-style visual speed control.
It is measuring the living branch's own treadmill locomotor time course, which
is stronger than the imposed visual perturbation.

Compact evidence bundle:

- [creamer2018_parity_mismatch_diagnosis.json](/G:/flysim/outputs/metrics/creamer2018_parity_mismatch_diagnosis.json)

#### Updated implication

The next valid Creamer step is **not** another baseline / ablation rerun on
the same simple pre-vs-stim fold metric. The next valid step is an assay
redesign that separates true visual-speed modulation from the branch's
endogenous treadmill locomotor ramp, for example via state-matched controls or
within-trial subtraction against a stationary-scene control.

### Honest Verdict

- assay geometry: `resolved`
- biologically plausible regime achieved: `yes`, mechanically
- Creamer behavioral parity: `no`
- Creamer causal parity (`T4/T5` dependence): `no`

The current stack can now be tested in a biologically plausible treadmill
regime, but it does not match the paper. The active next problem is no longer
geometry. It is diagnosing why the living brain/body branch produces a
wrong-sign, ablation-insensitive translational speed response under motion-only
drive.

That is also closer to the real paper setup. The core open-loop and gain
experiments were done with flies tethered above an air-supported ball while
visual stimuli were presented on a virtual cylinder, and the nearby-object test
used a narrowed virtual hallway on a one-dimensional track. So the current
fully free-walking corridor branch is not just underperforming. It is the wrong
geometry for the claim.

## March 29, 2026 Interleaved-Block Reassessment

The next matched rerun was completed with a better assay instead of another
simple pre-vs-stim fold. The treadmill branch now supports interleaved
stationary, motion, and counterphase-flicker blocks:

- [baseline blocks config](/G:/flysim/configs/flygym_visual_speed_control_living_motion_only_treadmill_blocks.yaml)
- [ablated blocks config](/G:/flysim/configs/flygym_visual_speed_control_living_motion_only_treadmill_blocks_t4t5_ablated.yaml)
- baseline run:
  [summary.json](/G:/flysim/outputs/creamer2018_interleaved_blocks_baseline/flygym-demo-20260328-234658/summary.json)
- ablated run:
  [summary.json](/G:/flysim/outputs/creamer2018_interleaved_blocks_t4t5_ablated/flygym-demo-20260328-235424/summary.json)

### What the new pair fixed

The old assay asked the wrong question:

- `stimulus_mean_forward_speed / pre_mean_forward_speed`

That was too easy for the living branch to fool because its treadmill speed was
still ramping during the assay window. The interleaved-block version instead
compares each stimulus block against the immediately preceding stationary block.

That fixed two real interpretation problems:

1. motion is no longer equivalent to flicker in the metrics
2. the matched `T4/T5` ablation is now visibly real at the splice level

The baseline run shows active motion splice drive throughout the block assay:

- mean `visual_splice.nonzero_root_count` about `12,238`
- mean `visual_splice.max_abs_current` about `7.1`

The ablated run zeroes that cleanly:

- mean `visual_splice.nonzero_root_count = 0`
- mean `visual_splice.max_abs_current = 0`

So the causal manipulation is now honest in the assay itself.

### What the new pair actually says

The interleaved metrics are:

Baseline:

- `front_to_back_delta_forward_speed_mean = +20.2946 mm/s`
- `counterphase_flicker_delta_forward_speed_mean = +0.0732 mm/s`
- `back_to_front_delta_forward_speed_mean = -0.0237 mm/s`

Ablated:

- `front_to_back_delta_forward_speed_mean = +20.3096 mm/s`
- `counterphase_flicker_delta_forward_speed_mean = +0.0058 mm/s`
- `back_to_front_delta_forward_speed_mean = -0.0008 mm/s`

So the better assay does reveal something real:

- front-to-back motion behaves differently from flicker
- flicker is near zero, which is directionally consistent with Creamer
- back-to-front is also near zero in this short schedule

But the matched ablation still leaves the main apparent front-to-back effect
essentially unchanged. That means the current positive `front_to_back`
residual is still not trustworthy as a `T4/T5`-dependent slowing result.

### Why the remaining false effect survives

The raw block means show the real problem directly.

Baseline:

- stationary block `baseline_a`: `205.607 mm/s`
- first front-to-back block `motion_ftb_a`: `244.221 mm/s`
- later stationary / flicker / motion blocks: all near `244.2 .. 244.3 mm/s`

Ablated:

- stationary block `baseline_a`: `205.611 mm/s`
- first front-to-back block `motion_ftb_a`: `244.263 mm/s`
- later stationary / flicker / motion blocks: all near `244.2 .. 244.3 mm/s`

So the big positive front-to-back residual is concentrated almost entirely in
the **first** motion block, immediately after startup. Once the branch reaches
its treadmill plateau, the later front-to-back block, the flicker block, the
back-to-front block, and the later stationary blocks all sit on essentially the
same speed level.

That means the remaining mismatch is now much narrower and better defined than
before:

- not a motion-sign bug
- not a treadmill-texture bug
- not a coarse-slip bug
- not a fake ablation

It is now primarily a **startup-state contamination** problem in a living
branch that ramps from about `205.6 mm/s` to `244.2 mm/s` over the first two
blocks.

### Honest current verdict

The interleaved-block reassessment is a real scientific improvement. It proves:

- the assay is now separating motion from flicker much better than before
- the `T4/T5` ablation really is removing motion splice drive

But it still does **not** prove Creamer parity, because the dominant apparent
front-to-back effect is still inherited from the startup ramp rather than from
a stable post-warmup motion response.

So the next valid Creamer step is now specific:

- add warmup stationary blocks
- repeat motion and flicker blocks after the locomotor plateau is reached
- score only the post-warmup repeated comparisons when judging `T4/T5`
  dependence and slowing parity

## March 29, 2026 Disconnected Brain Hot-Start Test

I also tested the more literal hot-start idea: warm the brain alone for several
seconds, then start the body/sim without resetting brain state.

That path is now implemented in:

- [closed_loop.py](/G:/flysim/src/runtime/closed_loop.py)
- [controller.py](/G:/flysim/src/bridge/controller.py)

with dedicated Creamer configs:

- [warmstart baseline config](/G:/flysim/configs/flygym_visual_speed_control_living_motion_only_treadmill_blocks_warmstart.yaml)
- [warmstart ablated config](/G:/flysim/configs/flygym_visual_speed_control_living_motion_only_treadmill_blocks_warmstart_t4t5_ablated.yaml)

The runtime behavior is:

1. reset brain once
2. step brain alone for `5.0 s` with no body and no sensory input
3. reset decoder / splice / context state
4. reset body
5. start the embodied run without resetting brain state again

### Honest result

This did **not** solve the Creamer mismatch.

Warmstarted baseline:

- [summary.json](/G:/flysim/outputs/creamer2018_interleaved_blocks_warmstart_baseline/flygym-demo-20260329-002146/summary.json)

Warmstarted `T4/T5` ablation:

- [summary.json](/G:/flysim/outputs/creamer2018_interleaved_blocks_warmstart_t4t5_ablated/flygym-demo-20260329-003000/summary.json)

Instead of removing the startup artifact, the hot-start pushed the whole branch
into a much faster treadmill locomotor regime.

Warmstarted baseline block means:

- `baseline_a`: `618.138 mm/s`
- `motion_ftb_a`: `732.887 mm/s`
- later stationary / flicker / motion blocks: all near `732.4 .. 732.6 mm/s`

Warmstarted ablated block means:

- `baseline_a`: `618.001 mm/s`
- `motion_ftb_a`: `732.793 mm/s`
- later stationary / flicker / motion blocks: all near `732.4 .. 732.5 mm/s`

So the same pattern survived, just at a much higher speed scale.

The matched warmstarted pair still failed causally:

- baseline `front_to_back_delta_forward_speed_mean = 57.8557 mm/s`
- ablated `front_to_back_delta_forward_speed_mean = 57.8194 mm/s`

The ablation itself remained real:

- warmstarted baseline mean `visual_splice.nonzero_root_count` about `12,238`
- warmstarted ablated mean `visual_splice.nonzero_root_count = 0`

### Interpretation

The disconnected warmup is useful diagnostically, because it narrows the
problem further.

What it implies:

- the old `205 -> 244 mm/s` first-block jump was not just a cold-start artifact
  of the brain sitting at its reset state
- hot-starting the brain alone is enough to push the embodied branch into a
  stronger locomotor attractor before the visual assay starts
- the current decoder/body stack is therefore reading the warmed spontaneous
  brain state as a strong treadmill locomotion command, independently of the
  Creamer stimulus and independently of `T4/T5`

So the next valid Creamer fix is still **embodied assay design**, not just
off-body brain warming. The assay needs scored post-warmup motion/flicker
comparisons inside the embodied run, after the locomotor state has already
settled.

## March 29, 2026 Check Against The Last Known-Good Non-Spontaneous Branch

To determine whether the Creamer mismatch was introduced by the living
spontaneous brain or whether it already existed in the older decoder/body path,
I reran the same interleaved-block treadmill assay on the last strong
non-spontaneous target branch:

- reference target branch:
  [target_jump_brain_latent_turn.yaml](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_jump_brain_latent_turn.yaml)
- reference target result:
  [summary.json](/G:/flysim/outputs/requested_2s_calibrated_target_jump_brain_latent_turn/flygym-demo-20260315-061819/summary.json)

The matched Creamer configs for that non-spontaneous regime are:

- [non-spont baseline config](/G:/flysim/configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks.yaml)
- [non-spont ablated config](/G:/flysim/configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_t4t5_ablated.yaml)

Completed runs:

- baseline:
  [summary.json](/G:/flysim/outputs/creamer2018_known_good_nonspont_baseline/flygym-demo-20260329-004611/summary.json)
- matched `T4/T5` ablation:
  [summary.json](/G:/flysim/outputs/creamer2018_known_good_nonspont_t4t5_ablated/flygym-demo-20260329-005447/summary.json)
- compact six-run comparison artifact:
  [creamer_systemic_branch_comparison.csv](/G:/flysim/outputs/metrics/creamer_systemic_branch_comparison.csv)

### What this resolves

The Creamer mismatch is **not** caused only by the spontaneous-state branch.

The non-spontaneous branch still fails the same translational-speed test:

- non-spont baseline `front_to_back_delta_forward_speed_mean = 12.0611 mm/s`
- non-spont ablated `front_to_back_delta_forward_speed_mean = 12.0887 mm/s`

So the false apparent front-to-back speed effect survives even when the living
spontaneous-state machinery is removed.

That means the deeper translational-speed mismatch already existed in the older
decoder/body mapping.

### What spontaneous state changes

Although it is not the sole cause, spontaneous state clearly makes the assay
worse.

Non-spontaneous branch:

- mean treadmill speed about `150.7 mm/s`
- front-to-back false residual about `12.1 mm/s`
- baseline turn switching stays high: `18.0 Hz`
- baseline turn dominance is mixed: right `0.736`, left `0.264`

Spontaneous branch without hot-start:

- mean treadmill speed about `239.4 mm/s`
- front-to-back false residual about `20.3 mm/s`
- turn switching collapses to `0.0 Hz`
- branch becomes fully one-sided left-turn dominant

Spontaneous branch with disconnected hot-start:

- mean treadmill speed about `718.3 mm/s`
- front-to-back false residual about `57.9 mm/s`
- branch still stays almost entirely left-turn dominant

So spontaneous state is not the origin of the Creamer parity failure, but it
**amplifies** it by pushing the current decoder/body system into a much stronger
locomotor attractor.

### What the non-spontaneous pair adds mechanistically

The non-spontaneous pair also shows that `T4/T5` is not irrelevant. The motion
splice still changes steering dynamics even though it fails to change
translational speed in the Creamer sense.

In the non-spontaneous regime:

- baseline turn switching is `18.0 Hz`
- ablated turn switching collapses to `0.0 Hz`
- baseline right-turn dominance is `0.736`
- ablated right-turn dominance becomes `1.0`

So the motion pathway is still influencing the branch, but mostly through
steering structure, not through a separate speed-control channel.

That is actually consistent with the paper's central claim: turning and walking
speed should not be treated as the same motion computation.

### Honest synthesis

The current evidence now points to **both** failure classes:

1. spontaneous-state methodology issue
   - the current living spontaneous regime can swamp the assay by injecting a
     large locomotor attractor before or during the visual block schedule

2. systemic decoder/body mapping issue
   - even the best non-spontaneous reference branch still lacks a proper
     `T4/T5`-dependent translational speed-control channel
   - the motion pathway is still affecting steering much more than speed

So the next correct conclusion is not "spontaneous state is bad" and not
"visual splice is broken."

It is:

- the spontaneous regime needs better embodied-state calibration so it does not
  immediately dominate treadmill speed
- the current descending decode/body mapping still does not implement the
  distinct translational speed computation required by Creamer 2018

## March 29, 2026 Decoder-Channel Diagnosis

I then checked whether the remaining Creamer failure is primarily a spontaneous
state problem, a descending decoder/body-mapping problem, or both.

Reproducible diagnosis artifacts:

- [non-spontaneous decoder diagnosis JSON](/G:/flysim/outputs/metrics/creamer_known_good_nonspont_decoder_diagnosis.json)
- [non-spontaneous decoder diagnosis CSV](/G:/flysim/outputs/metrics/creamer_known_good_nonspont_decoder_diagnosis.csv)
- [spontaneous decoder diagnosis JSON](/G:/flysim/outputs/metrics/creamer_spontaneous_decoder_diagnosis.json)
- [spontaneous decoder diagnosis CSV](/G:/flysim/outputs/metrics/creamer_spontaneous_decoder_diagnosis.csv)

### What the non-spontaneous branch shows

The strongest result is in the non-spontaneous reference branch. In the first
front-to-back motion block:

- treadmill forward-speed delta survives matched `T4/T5` ablation almost
  perfectly:
  - baseline `+23.4059 mm/s`
  - ablated `+23.4156 mm/s`
- but the decoder forward signal does **not** survive:
  - baseline `+0.0717`
  - ablated `-0.0151`
- meanwhile the steering-side voltage turn signal *does* show a motion-pathway
  effect:
  - baseline `-0.1681`
  - ablated `-0.00008`

That means the assay's apparent speed effect is not being carried by the
decoder's forward channel. The visual motion pathway is still entering the
system, but mainly through steering-side structure, not through a distinct
translational speed-control readout.

This is the clearest evidence so far that the deeper Creamer mismatch is in the
current descending decode/body mapping, not simply in the sensory splice.

### The concrete code seam causing this

The current Creamer configs are still running the decoder in its default legacy
`two_drive` mode, not in the richer `hybrid_multidrive` latent mode:

- decoder default:
  [decoder.py](/G:/flysim/src/bridge/decoder.py)
- Creamer non-spont config:
  [flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks.yaml](/G:/flysim/configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks.yaml)

In that legacy compatibility path, the body controller does **not** receive a
separate locomotor-frequency or correction-gain command. Instead,
[ConnectomeTurningFly](/G:/flysim/src/body/connectome_turning_fly.py) maps any
nonzero two-drive action into:

- `left_amp = abs(left_drive)`
- `right_amp = abs(right_drive)`
- `left_freq_scale = 1.0`
- `right_freq_scale = 1.0`
- `retraction_gain = 1.0`
- `stumbling_gain = 1.0`

So as soon as the decoder emits any active left/right drive, the body enters a
fixed-frequency locomotor regime. That is a structural reason the current
Creamer branch cannot express the paper's distinct visual speed-control
computation cleanly. Even before the spontaneous-state amplification, the motor
interface is still collapsing translational control back into a legacy
left/right drive abstraction.

### What the spontaneous branch adds

In the spontaneous branch, the same false speed delta still survives ablation:

- baseline `+38.6136 mm/s`
- ablated `+38.6525 mm/s`

But by that point the spontaneous branch is already locked into a strong
one-sided turn/locomotor attractor, and the motion-pathway-specific turn signal
structure has mostly collapsed:

- baseline turn-voltage delta `-0.00354`
- ablated turn-voltage delta `+0.00052`

So the spontaneous methodology does not create the Creamer failure, but it does
make the branch less diagnostically clean by drowning the remaining
motion-sensitive steering structure in a stronger endogenous locomotor regime.

### Sub-agent plausibility check on endogenous activations

The independent plausibility review came back consistent with the local
evidence:

- the current spontaneous regime is mesoscale-plausible and supported by the
  validation bundle in
  [spontaneous_mesoscale_validation.md](/G:/flysim/docs/spontaneous_mesoscale_validation.md)
- but the hot-start treadmill locomotor attractor is not biologically
  trustworthy in its current embodied interpretation
- the most likely split is that spontaneous brain state is being amplified too
  directly by the current decoder/body loop

So the correct synthesis is now explicit:

1. the spontaneous-state methodology has an embodied calibration problem
   because it amplifies a locomotor attractor strongly enough to swamp the
   Creamer assay
2. the deeper pre-existing failure is the descending decode/body mapping,
   because even the older non-spontaneous branch does not expose a distinct
   `T4/T5`-dependent translational speed-control channel

That is why the next Creamer-facing fix should target the motor readout/body
mapping, not just the spontaneous-state generator.

## March 29, 2026 Current Fix Direction Before Corrected Pair Completes

Current live state before the next corrected non-spontaneous pair finishes:

- active corrected baseline output root:
  [creamer2018_known_good_nonspont_multidrive_warm_baseline](/G:/flysim/outputs/creamer2018_known_good_nonspont_multidrive_warm_baseline)
- that run is intentionally being left untouched until completion

The current preserved fix direction is:

1. the Creamer treadmill-block configs were structurally wrong
   - they were still on decoder `command_mode: two_drive`
   - they needed to be moved onto:
     - `decoder.command_mode: hybrid_multidrive`
     - `runtime.control_mode: hybrid_multidrive`
2. the assay also needed embodied warmup, not just disconnected brain warmup
   - four stationary warmup blocks are now prepended before the scored motion
     blocks

Important sub-agent refinement that should not be lost:

- the repo already has stable `hybrid_multidrive` branches
- the repo's standard hybrid settings are still fairly turn-heavy
- the repo's more conservative VNC-style hybrid settings preserve locomotor
  frequency more cleanly and are likely a better Creamer fit if the default
  hybrid family still leaks too much steering into treadmill speed

Practical next-step rule after the current run finishes:

- evaluate the corrected multidrive+warmup pair first as-is
- only if residual steering contamination remains, retune toward the weaker-turn
  latent family next:
  - lower `turn_gain`
  - lower `latent_turn_amp_gain`
  - lower `latent_turn_freq_gain`
  - lower `forward_asymmetry_turn_gain`
  - preserve or slightly strengthen the forward locomotor-frequency channel

Hard requirement for this workstream:

- the target is not merely to remove the false positive or clean up the assay
- the target is to make the embodied fly show the Creamer-style visual
  speed-control phenotype in this same treadmill evaluation setup through the
  brain plus descending decoder path

## March 29, 2026 Signed Relay Forward Suppression Produced The First Partial Creamer Effect

The first signed relay-forward branch finally produced a real partial result in
the correct treadmill assay:

- baseline:
  [summary.json](/G:/flysim/outputs/creamer2018_known_good_nonspont_creamer_relay_forward_context_vnclite_baseline/flygym-demo-20260329-030703/summary.json)
- matched `T4/T5` ablation:
  [summary.json](/G:/flysim/outputs/creamer2018_known_good_nonspont_creamer_relay_forward_context_vnclite_t4t5_ablated/flygym-demo-20260329-032136/summary.json)

Key metrics:

- baseline `front_to_back_delta_forward_speed_mean = -0.4688 mm/s`
- ablated `front_to_back_delta_forward_speed_mean = +0.0271 mm/s`
- baseline `counterphase_flicker_delta_forward_speed_mean = +0.0367 mm/s`

So the branch finally demonstrated that a real `T4/T5`-dependent visual motion
signal can slow treadmill walking speed through the current brain and decoder
stack.

But the branch was still not publishable parity, because the body remained
trapped in a pathological high-speed regime:

- spontaneous locomotion mean forward speed `~679 mm/s`
- `back_to_front` still had the wrong sign and was nearly ablation-insensitive

That meant the branch was scientifically useful, but still dominated by the
wrong locomotor operating point.

## March 29, 2026 Treadmill Body Frequency Cliff Proven Directly

To determine whether the remaining failure was still mainly in the body path, I
measured treadmill speed directly as a function of the hybrid locomotor command
operating point:

- tiny direct probe:
  [treadmill_hybrid_response_map_tiny.json](/G:/flysim/outputs/metrics/treadmill_hybrid_response_map_tiny.json)
- zero-amplitude frequency sweep:
  [treadmill_hybrid_response_map_freqgate.json](/G:/flysim/outputs/metrics/treadmill_hybrid_response_map_freqgate.json)

The decisive result was:

- `amp = 0.0`, `freq = 0.9` -> `~693 mm/s`
- `amp = 0.0`, `freq = 0.7..0.85` -> `~226..248 mm/s`

So the body path has a hard locomotor-frequency cliff near `0.9`. That proves
the old high-speed Creamer branches were not simply “more sensitive” or “more
alive”. They were sitting on a pathological gait regime where treadmill forward
speed stayed huge even at effectively zero locomotor amplitude.

This was the cleanest direct evidence so far that the next Creamer iteration had
to stay below that cliff.

## March 29, 2026 Safe Frequency-Gated Motion-Energy Branch

I then added a more biologically defensible translational-speed readout form:

- `motion_energy` forward-context groups in
  [decoder.py](/G:/flysim/src/bridge/decoder.py)
- optional adaptive group baselines so the signal is measured relative to the
  current stationary regime rather than a fixed old baseline

Artifacts:

- library:
  [creamer_relay_motion_energy_library_v1.json](/G:/flysim/outputs/metrics/creamer_relay_motion_energy_library_v1.json)
- high-speed first pass:
  [summary.json](/G:/flysim/outputs/creamer2018_known_good_nonspont_creamer_motion_energy_mid_baseline/flygym-demo-20260329-033539/summary.json)
- safe-regime frequency-gated pass:
  [summary.json](/G:/flysim/outputs/creamer2018_known_good_nonspont_creamer_motion_energy_freqgate_baseline/flygym-demo-20260329-040936/summary.json)

The safe-regime branch succeeded at the one thing it was designed to prove:

- it kept the treadmill in a sane locomotor regime
- spontaneous locomotion mean forward speed fell to `225.3 mm/s`

But it also exposed the next blocker clearly:

- `front_to_back_delta_forward_speed_mean = -0.0068 mm/s`
- `counterphase_flicker_delta_forward_speed_mean = -0.0049 mm/s`
- `back_to_front_delta_forward_speed_mean = -0.0033 mm/s`

So once the body regime was fixed, the current motion-energy library became
nearly constant across stationary, flicker, and motion blocks. In other words:

- the signed relay branch proved a real motion-sensitive speed suppressor exists
- the body probe proved the safe locomotor operating region
- the safe-regime motion-energy branch proved the current library was learned
  from the wrong regime

That sets the next valid step unambiguously:

1. collect a matched safe-regime relay-monitored baseline / `T4/T5` ablation
   pair
2. rebuild the motion-energy forward-context library from those safe-regime
   logs
3. rerun the matched safe-regime pair using that rebuilt library

At this point the remaining Creamer work is no longer about gross assay bugs.
It is about learning the translational speed-control readout in the correct
body operating regime.

### Biological constraint on the next library

A read-only plausibility review against the Creamer paper context and the local
candidate tables converged on a narrow, more defensible motion-energy library:

- keep `L1`, `L3`, and then `L2` as assay and monitor constraints, not as the
  first direct forward-suppression weights
- treat `T4/T5` as the early motion basis set
- use `T5b`, `T5c`, and `LPT30` as the first direct bilateral speed-suppression
  core
- keep `T5a` only at small weight unless the safe-regime pair says otherwise
- treat `VCH` as biologically plausible but high-risk because it is the
  strongest local bilateral suppressor and also the most flicker-contaminated

The practical implication is that the next safe-regime library should **not**
blindly reuse `top_k` selection if it re-elevates `VCH` or steering-heavy relay
families. It should stay narrow and motion-first unless the matched safe-regime
ablation says the broader cohort is genuinely required.

## March 29, 2026 Decoder Seam Fix: Motion Suppression Must Hit the Frequency Floor

The next structural diagnosis was decisive. In the current
`hybrid_multidrive` body path, the Creamer forward-context signal was only
modulating the decoder's forward scalar, while the body was still driven by a
nonzero locomotor frequency floor:

- `forward_context_signal` could saturate near `1.0`
- that could drive `forward_signal` and `forward_state` toward or below zero
- but `base_freq_scale` still retained a floor through `latent_freq_bias`
- the body ignored `left_drive/right_drive` in hybrid mode and kept stepping
  through the nonzero CPG frequency scales

So the signal was real, but it was landing on the wrong control variable for a
Creamer-style slowing assay.

The minimal biologically plausible fix was therefore decoder-side, not
body-side:

- keep the bilateral motion-suppression signal in the brain/decoder path
- allow it to suppress the hybrid locomotor frequency floor directly
- keep the change optional and config-controlled so it does not silently rewrite
  the rest of the branch family

This is now implemented in:

- [decoder.py](/G:/flysim/src/bridge/decoder.py)

with focused coverage in:

- [test_bridge_unit.py](/G:/flysim/tests/test_bridge_unit.py)

## March 29, 2026 Narrow Safe-Regime Library Update

The read-only biological plausibility review also tightened the candidate set
further. In the current safe-regime table:

- `T5a` is the cleanest bilateral direct suppressor
- `VCH` is still real and useful, but it remains heavily flicker-contaminated
- `T5b`, `T5c`, and `LPT30` are more mixed than earlier tables suggested once
  the branch is held below the old treadmill frequency cliff

So the next first-wave no-hacks suppressor library was narrowed to:

- `T5a`
- `VCH` at a tiny capped contribution

Artifact:

- [creamer_relay_motion_energy_library_freqgate_safe_t5a_vch002.json](/G:/flysim/outputs/metrics/creamer_relay_motion_energy_library_freqgate_safe_t5a_vch002.json)

Matched configs now on the corrected seam:

- [baseline config](/G:/flysim/configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_creamer_motion_energy_freqgate_safe_t5a_vch002_speedsuppress.yaml)
- [ablated config](/G:/flysim/configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_creamer_motion_energy_freqgate_safe_t5a_vch002_speedsuppress_t4t5_ablated.yaml)

The baseline run is currently the active live test of this corrected branch:

- [run.jsonl](/G:/flysim/outputs/creamer2018_known_good_nonspont_creamer_motion_energy_freqgate_safe_t5a_vch002_speedsuppress_baseline/flygym-demo-20260329-054759/run.jsonl)

## March 29, 2026 First Narrow-Library Result: Safe But Still Wrong-Sign

The first full safe-regime baseline on the new decoder seam is now complete:

- [metrics.csv](/G:/flysim/outputs/creamer2018_known_good_nonspont_creamer_motion_energy_freqgate_safe_t5a_vch002_speedsuppress_baseline/flygym-demo-20260329-054759/metrics.csv)

It did **not** produce Creamer-style slowing.

Measured result:

- spontaneous locomotion stayed in a sane regime:
  - `mean_forward_speed = 335.2 mm/s`
- but the scored stimulus blocks still moved in the wrong direction:
  - `front_to_back_delta_forward_speed_mean = +0.0267 mm/s`
  - `counterphase_flicker_delta_forward_speed_mean = +0.0831 mm/s`
  - `back_to_front_delta_forward_speed_mean = +0.0920 mm/s`

So the narrow safe-regime branch is honest but still wrong-sign. It is not
worth a matched ablation run in its current state.

The likely remaining failure is not the absence of a bilateral suppressor
signal. It is still turn-to-speed coupling inside the hybrid operating point:

- `front_to_back_delta_abs_turn_signal_mean = -0.0400`
- spontaneous locomotion remained heavily left-turn-dominant

That means the next valid move is **not** another assay rewrite and **not**
another broad library expansion. The next valid move is to keep the same
bilateral speed library and decoder-side frequency-floor suppression seam, but
shift to the more conservative turn-lite hybrid settings that were already
flagged earlier as the cleaner locomotor operating point.

Prepared configs:

- [turn-lite baseline](/G:/flysim/configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_creamer_motion_energy_freqgate_safe_t5a_vch002_speedsuppress_turnlite.yaml)
- [turn-lite ablation](/G:/flysim/configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_creamer_motion_energy_freqgate_safe_t5a_vch002_speedsuppress_turnlite_t4t5_ablated.yaml)

## March 29, 2026 Turn-Lite `T5a + Tiny VCH` Safe Branch Still Failed

The prepared turn-lite safe baseline is now finished:

- [metrics.csv](/G:/flysim/outputs/creamer2018_known_good_nonspont_creamer_motion_energy_freqgate_safe_t5a_vch002_speedsuppress_turnlite_baseline/flygym-demo-20260329-060349/metrics.csv)

It stayed in a sane operating region:

- `pre_mean_forward_speed = 241.46 mm/s`
- `stimulus_mean_forward_speed = 270.77 mm/s`

but it still did **not** produce Creamer-style slowing:

- `front_to_back_delta_forward_speed_mean = +0.0209 mm/s`
- `counterphase_flicker_delta_forward_speed_mean = +0.0051 mm/s`
- `back_to_front_delta_forward_speed_mean = +0.0353 mm/s`

So the more conservative turn-lite hybrid settings were not enough by
themselves. The result is cleaner than the earlier `T5a + tiny VCH` safe branch
because flicker is now much smaller than before, but the branch is still
wrong-sign under both real-motion directions.

That narrows the remaining cause further:

- the decoder-side frequency-floor suppression seam is real
- the safe treadmill operating point is real
- the `VCH` contribution is still the most likely contaminant even at tiny
  weight

So this branch is **not** worth a matched ablation run.

The next strict no-hacks step is the already-prepared `T5a`-only turn-lite
branch:

- [baseline config](/G:/flysim/configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_creamer_motion_energy_freqgate_safe_t5a_only_speedsuppress_turnlite.yaml)
- [ablated config](/G:/flysim/configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_creamer_motion_energy_freqgate_safe_t5a_only_speedsuppress_turnlite_t4t5_ablated.yaml)

## March 29, 2026 Stale-Baseline Saturation Bug In The Forward-Context Seam

While preparing the `T5a`-only fallback, I checked the raw turn-lite
`T5a + tiny VCH` run at the motor-readout field level rather than only the
block summaries. That exposed a real decoder bug.

At `warmup_a` in the finished turn-lite run:

- `T5a_forward_context_bilateral_hz = 0.0`
- `VCH_forward_context_bilateral_hz = 0.0`
- `T5a_forward_context_baseline_hz = 68.1316`
- `VCH_forward_context_baseline_hz = 147.7956`
- `forward_context_library_signal ~= 1.0`

The cause is in [decoder.py](/G:/flysim/src/bridge/decoder.py):

- the motion-energy library starts from the learned safe-regime bilateral
  baseline from a previous run
- `motion_energy` uses `abs(centered_rate)`
- so when the live branch is still near zero spikes, “no spikes” is interpreted
  as a large deviation from baseline and therefore as maximal suppressive motion

That means the earlier turn-lite `T5a + tiny VCH` result is **not** a valid
final comparator. It is still useful as evidence that the old seam was wrong.

The seam is now fixed in a biologically cleaner way:

- allow the bilateral forward-context baseline to initialize from the current
  run instead of a stale learned rate
- let it adapt during the unscored warmup window
- freeze it before the scored Creamer blocks

Implemented in:

- [decoder.py](/G:/flysim/src/bridge/decoder.py)

with focused tests in:

- [test_bridge_unit.py](/G:/flysim/tests/test_bridge_unit.py)
- [test_closed_loop_smoke.py](/G:/flysim/tests/test_closed_loop_smoke.py)

The corrected `T5a`-only turn-lite configs now set:

- `forward_context_initial_baseline_mode: zero`
- `forward_context_baseline_alpha: 0.05`
- `forward_context_baseline_update_steps: 500`

so the bilateral suppressor baseline is established from the current run's
stationary warmup blocks rather than inherited from an incompatible older
operating regime.

## March 29, 2026 Corrected `T5a`-Only Baseline: Valid But Still Wrong

After the stale-baseline seam fix, I reran the strict `T5a`-only turn-lite
baseline on the same treadmill assay:

- [metrics.csv](/G:/flysim/outputs/creamer2018_known_good_nonspont_creamer_motion_energy_freqgate_safe_t5a_only_speedsuppress_turnlite_baseline_rerun/flygym-demo-20260329-062600/metrics.csv)

The seam fix was genuinely active in the live run. At `warmup_a`:

- `T5a_forward_context_baseline_hz = 0.0`
- `forward_context_signal = 0.0`

So this rerun is the first valid `T5a`-only comparator for this branch family.

Its scored result still fails Creamer:

- `front_to_back_delta_forward_speed_mean = -0.0033 mm/s`
- `counterphase_flicker_delta_forward_speed_mean = +0.0593 mm/s`
- `back_to_front_delta_forward_speed_mean = +0.4009 mm/s`

That means:

- front-to-back motion is effectively flat
- flicker is still positive
- back-to-front motion strongly speeds the fly up

So the problem is no longer a stale decoder baseline bug. It is now the actual
embodied regime.

The rerun also exposed the next blocker clearly:

- `pre_mean_forward_speed = 547.7 mm/s`
- `stimulus_mean_forward_speed = 564.1 mm/s`

So the fly is entering the scored blocks already moving too fast for a small
bilateral visual suppressor to carve out realistic slowing. In other words,
after fixing the decoder seam, the remaining miss is a combination of:

1. the embodied locomotor operating point is still too fast
2. a single early `T5a` subtype is still too shallow a source for the final
   Creamer-style speed signal

This matches the paper's logic better than the earlier branch family did:

- the early `T4/T5`-side diagnostic is useful
- but the final speed computation must still be built later

So the next valid no-hacks step is not another `T5a` rerun. It is:

- move the embodied treadmill baseline down into a sane locomotor operating
  point in the same evaluation setup
- then rebuild the bilateral suppressor library downstream of single `T5`
  subtypes, with `LPT30` now the leading next relay candidate

## March 29, 2026 Low-Forward `T5a` Baseline: Operating Point Fixed, Phenotype Still Null

I then ran the prepared low-forward version of the same corrected `T5a`-only
turn-lite branch:

- [run.jsonl](/G:/flysim/outputs/creamer2018_known_good_nonspont_creamer_motion_energy_freqgate_safe_t5a_only_speedsuppress_turnlite_lowforward_baseline/flygym-demo-20260329-064715/run.jsonl)

The benchmark process never finalized its normal `metrics.csv` and
`summary.json`, so the result was recovered directly from the raw block states
in `run.jsonl`.

### What changed correctly

The operating-point fix worked.

The branch now warms into a sane treadmill regime instead of the earlier
`~548 mm/s` baseline:

- `warmup_a = 150.45 mm/s`
- `warmup_b = 230.41 mm/s`
- `warmup_c = 230.41 mm/s`
- `warmup_d = 230.40 mm/s`
- scored baseline mean `= 230.40 mm/s`

So lowering:

- `forward_gain`
- `population_forward_weight`
- `latent_freq_bias`
- `latent_freq_gain`

really did remove the overfast decoder-driven locomotor plateau.

### What still failed

Even in that corrected embodied regime, the `T5a` suppressor still did **not**
produce Creamer-style slowing:

- `motion_ftb_a delta = +0.00010 mm/s`
- `motion_ftb_b delta = +0.01813 mm/s`
- `flicker delta = -0.01643 mm/s`
- `motion_btf delta = +0.02545 mm/s`

That means the locomotor operating point was necessary to fix, but not
sufficient. Once the body regime is sane, the current single-`T5a` bilateral
motion-energy readout is still too shallow to create the paper's translational
speed-control phenotype.

### Interpretation

This is an important negative result because it separates two failure classes:

1. the old `~548 mm/s` baseline really was an operating-point problem
2. the remaining null result is now a **signal-localization** problem

In other words:

- the decoder seam is now behaving correctly
- the body regime is now behaving correctly
- but the current early visual suppressor still does not carry enough of the
  final speed-control computation

That is exactly the point where the paper predicts a downstream construction.
`T4/T5` are necessary early motion channels, but the final speed-like signal
should emerge later by combining motion signals downstream.

### Next valid step

So the next no-hacks branch is no longer another `T5a` rerun and no longer a
mere operating-point tweak. The next valid step is to keep the corrected seam
and the sane low-forward treadmill regime, but move the bilateral suppressor
library downstream:

- prepared next branch:
  [LPT30 low-forward baseline config](/G:/flysim/configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_creamer_motion_energy_freqgate_safe_lpt30_only_speedsuppress_turnlite_lowforward.yaml)
- matched ablation config:
  [LPT30 low-forward ablation config](/G:/flysim/configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_creamer_motion_energy_freqgate_safe_lpt30_only_speedsuppress_turnlite_lowforward_t4t5_ablated.yaml)

That preserves the corrected embodied regime and asks the next mechanistic
question cleanly: whether a downstream relay like `LPT30` expresses a more
Creamer-like bilateral speed signal than single `T5a`.

## March 29, 2026 Low-Forward `LPT30` Failed Early, So The Next Honest Move Is A Multi-Channel `T5` Pool

I ran the prepared low-forward `LPT30` baseline in the same corrected treadmill
regime, but streamed the raw `run.jsonl` live instead of waiting for expensive
artifact finalization. That was enough to classify the branch.

### What the early scored blocks showed

From
[run.jsonl](/G:/flysim/outputs/creamer2018_known_good_nonspont_creamer_motion_energy_freqgate_safe_lpt30_only_speedsuppress_turnlite_lowforward_baseline/flygym-demo-20260329-070406/run.jsonl):

- `baseline_mean = 229.08 mm/s`
- `motion_ftb_a delta = +0.02577 mm/s`
- `flicker delta = +0.02398 mm/s`

So `LPT30` reached the same sane operating point as the corrected low-forward
`T5a` branch, but it was already wrong-sign and flicker-positive by the first
scored blocks. That made it an unpromotable suppressor library for this assay,
and there was no reason to waste a matched `T4/T5` ablation on it.

### What this changes mechanistically

At that point both sane-regime single-path suppressors were falsified:

- `T5a` alone is honest but null
- `LPT30` alone is early wrong-sign and flicker-positive

That pushes the branch much closer to the paper's own model logic. The final
Creamer-like speed code is probably not sitting in one early subtype and not in
one later relay either. It is more likely built by combining multiple
TF-tuned channels.

### Read-only plausibility review result

A read-only review of the local safe-regime table plus the paper logic
converged on a stricter next rule than the earlier `LPT30` pivot:

- do **not** keep trying lone suppressor families
- build the next forward suppressor as a pooled multi-channel `T5`
  motion-energy latent
- keep any later relay term tiny and secondary

The most biologically plausible first promoted pool is now:

- `T5a`
- `T5b`
- `T5c`
- optional tiny downstream gate only later, not as the backbone

That keeps the decoder aligned with the paper's core claim: a translational
speed signal can be constructed downstream from multiple TF-tuned motion
channels without requiring a single early detector to already be speed-tuned.

### Why a staged `T5a + T4c` branch still exists

I also staged a quick signed-combo library at
[creamer_relay_signed_combo_library_freqgate_safe_t5a_t4c.json](/G:/flysim/outputs/metrics/creamer_relay_signed_combo_library_freqgate_safe_t5a_t4c.json)
with matching configs:

- [baseline](/G:/flysim/configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_creamer_signed_combo_freqgate_safe_t5a_t4c_lowforward.yaml)
- [ablated](/G:/flysim/configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_creamer_signed_combo_freqgate_safe_t5a_t4c_lowforward_t4t5_ablated.yaml)

That branch is only a fast intermediate test because it is already wired to
cancel flicker mathematically in the corrected low-forward regime. But it is no
longer the main biological hypothesis. The stricter target is now a pooled,
rectified multi-channel `T5` motion-energy suppressor that stays entirely
inside the early TF-tuned motion basis before any tiny downstream refinement.

## March 29, 2026 The Multi-Channel `T5` Pool Revealed A Deeper Embodied Assay Instability

I then moved from single-path suppressors to an explicit multi-channel `T5`
pool, which is closer to the paper's claimed mechanism. The tooling is now in
place:

- builder support for explicit per-channel weights
- pooled `T5abc` config pair
- smoke coverage for the new pair

The first suppressive pooled library is recorded at
[creamer_relay_motion_energy_library_freqgate_safe_t5abc_pool_suppressive.json](/G:/flysim/outputs/metrics/creamer_relay_motion_energy_library_freqgate_safe_t5abc_pool_suppressive.json).

### What the live run comparison exposed

The first pooled branch still failed, but the important new result is that it
failed in a way that exposes a deeper problem than “bad library weights.”

At the same cycle index in two different low-forward runs:

- clean `T5a` low-forward run:
  - `speed = 232.05 mm/s`
  - `left/right_drive = 0.15933 / 0.15638`
  - `left/right_freq = 0.17827 / 0.17749`
- suppressive `T5abc` pooled run:
  - `speed = 655.83 mm/s`
  - `left/right_drive = 0.14769 / 0.14474`
  - `left/right_freq = 0.17819 / 0.17740`

So the decoder commands and latent frequency scales are nearly identical, but
the treadmill forward-speed readout differs by almost `3x`.

That is not a small relay-choice error. It is evidence that the embodied
treadmill state is still too unstable across runs for fine Creamer comparisons
to be trusted.

### Why this matters

Up to this point, the dominant story was:

- fix the operating point
- find the right bilateral speed-suppression library
- rerun baseline / ablation

Now there is an additional blocker:

- matched runs can land in very different treadmill-speed regimes even when the
  decoder-side command is nearly the same

That means the remaining Creamer problem is no longer only “find the right
visual relay.” It is also:

- stabilize the embodied gait / contact state before scored blocks
- only then trust small motion-versus-flicker speed differences

### Current honest state

At this point the Creamer workstream has three distinct unresolved pieces:

1. `T5a` alone is too constant and too weakly differential
2. `LPT30` alone is early wrong-sign and flicker-positive
3. pooled multi-channel branches are currently colliding with embodied
   treadmill-state instability before they can be judged cleanly

So the next valid work is dual:

- keep the decoder biologically plausible by staying inside multi-channel
  motion pooling rather than heuristics
- stabilize the embodied pre-scored treadmill state so the same decoder command
  does not produce wildly different speed measurements across nominally matched
  runs

## March 29, 2026 The Creamer Demo Visuals Still Fail A Human Sanity Check

There is now a second acceptance criterion beyond the numeric block metrics:
the rendered scene itself must look like a biologically plausible Creamer-style
stimulus.

Direct visual inspection of the recent demos shows that this criterion is still
being violated in some branches. Even when the nominal open-loop drift is only
`4 mm/s`, the striped wall pattern can still scream past the fly at an
obviously absurd scale. That observation is consistent with the measured
treadmill speeds:

- sane low-forward `T5a` branch: about `230 mm/s`
- unstable pooled `T5abc` branch: about `650 mm/s`

So the user-visible problem is real. It is not just irritation with the movie.
It means the current rendered scene is not a valid Creamer analogue in those
runs.

### New rule

From this point on, no Creamer run counts as evidence unless it passes both:

1. the numeric assay criteria
2. a rendered-scene validity check showing that the bar pattern and effective
   retinal slip remain in a biologically plausible range relative to fly scale
   and the paper setup

Any run that fails the human visual sanity check is inadmissible, even if its
summary metrics look superficially usable.

## March 29, 2026 Very-Slow Scene Probe: Better Sign, Still Invalid Retinal Slip

To test the user's objection directly, I took the current most stable Creamer
branch and slowed the imposed bar-scene drift from `±4.0 mm/s` to `±0.5 mm/s`:

- [config](/G:/flysim/configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_creamer_motion_energy_freqgate_safe_t5a_only_speedsuppress_turnlite_lowforward_veryslow.yaml)
- [summary](/G:/flysim/outputs/creamer2018_known_good_nonspont_creamer_motion_energy_freqgate_safe_t5a_only_speedsuppress_turnlite_lowforward_veryslow_baseline/flygym-demo-20260329-114620/summary.json)

### What improved

The branch stayed in the sane low-forward regime and the first front-to-back
effect became slightly negative instead of null:

- `front_to_back_delta_forward_speed_mean = -0.02275 mm/s`

So reducing the nominal scene drift did make the sign slightly more
Creamer-like.

### What did not improve

The real perceptual variable is still dominated by the fly's own treadmill
self-motion:

- `scene_speed_abs_mean_mm_s = 0.25`
- `effective_visual_speed_abs_mean_mm_s = 230.65`
- `retinal_slip_abs_mean_mm_s = 230.65`

So the slow-scene probe proves an important point:

- lowering the configured wall speed alone is **not** enough
- the fly still experiences enormous retinal slip because self-motion dominates
  the scene

That is why the demo can still look visually absurd even when the nominal bar
drift has been reduced to a very small number.

### Current interpretation

This probe is directionally useful, but it is not a valid Creamer replication:

- front-to-back became slightly negative
- flicker is still not cleanly separated (`+0.03806 mm/s`)
- the rendered/retinal scene remains invalid because effective visual speed is
  still huge relative to the imposed stimulus

So the next fix must target **effective retinal slip**, not just the nominal
scene drift parameter.

## March 29, 2026 Synced Scene Probe: Honest Retinal Slip, Same Behavioral Miss

The next requested step was stronger than merely lowering the configured scene
drift: first match the scene to the fly's own treadmill speed, then add only a
small signed offset, then score behavior.

I implemented that directly in
[visual_speed_control.py](/G:/flysim/src/body/visual_speed_control.py).
Interleaved blocks can now carry:

- `sync_to_fly_speed: true`
- `gain: 0.0`
- a small `scene_velocity_offset_mm_s`

That creates the intended treadmill Creamer semantics:

- stationary blocks can have true `0.0 mm/s` retinal slip
- motion blocks can impose only a small front-to-back or back-to-front
  perturbation on top of matched self-motion

The new probe config is:

- [synced low-forward `T5a` probe](/G:/flysim/configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_creamer_motion_energy_freqgate_safe_t5a_only_speedsuppress_turnlite_lowforward_synced_veryslow.yaml)

Focused tests for the new semantics passed:

- [test_visual_speed_control.py](/G:/flysim/tests/test_visual_speed_control.py)
- [test_closed_loop_smoke.py](/G:/flysim/tests/test_closed_loop_smoke.py)

The live run was allowed to proceed through the first scored front-to-back
block and then stopped, because that was enough to judge whether the requested
scene semantics were actually correct:

- [run.jsonl](/G:/flysim/outputs/creamer2018_known_good_nonspont_creamer_motion_energy_freqgate_safe_t5a_only_speedsuppress_turnlite_lowforward_synced_veryslow_baseline/flygym-demo-20260329-120615/run.jsonl)

Observed block means:

- `baseline_a`:
  - treadmill speed `645.153 mm/s`
  - retinal slip `0.0 mm/s`
  - scene world speed `645.151 mm/s`
- `motion_ftb_a`:
  - treadmill speed `645.287 mm/s`
  - retinal slip `-0.5 mm/s`
  - scene world speed `644.787 mm/s`
- `baseline_b`:
  - treadmill speed `645.244 mm/s`
  - retinal slip `0.0 mm/s`
  - scene world speed `645.244 mm/s`

This proves the requested semantics are now genuinely achieved. The assay is no
longer lying about what the fly saw in those scored blocks.

But the branch still does **not** show Creamer-like slowing in that corrected
assay. The first synced front-to-back delta is slightly wrong-sign:

- `motion_ftb_a - baseline_a = +0.13418 mm/s`

And the embodied locomotor regime is still extremely fast:

- about `645 mm/s` treadmill speed through `baseline_a`, `motion_ftb_a`, and
  `baseline_b`

So this probe changes the interpretation materially:

- the scene-validity bug is no longer the main excuse for the miss on this
  branch
- the remaining failure is now more plainly the embodied
  brain/decoder/body response itself

That is useful even though it is not a parity result. Future Creamer iterations
can now be judged on a true retinal-slip variable instead of a mislabeled
high-slip scene.

## March 29, 2026 Blocker Review After The Synced Probe

After the synced probe removed the scene-semantics ambiguity, I used multiple
independent code and artifact reviews to narrow the remaining failure more
precisely.

### Main blocker

The main blocker is now best described as a **high-speed embodied treadmill
attractor** in the current `hybrid_multidrive` operating point.

The current `T5a`-only motion-energy signal is also too weak and too
nonspecific, but that is no longer the whole story. In the synced probe:

- the scored stationary blocks had true `0.0 mm/s` retinal slip
- the scored front-to-back block had true `-0.5 mm/s` retinal slip
- decoder-side suppressive signals still changed
- treadmill speed stayed pinned near `645 mm/s`

So the remaining failure is not just “bad scene kinematics” and not just
“missing visual input.” It is now more plausibly:

- the body/controller already sitting in a fast locomotor regime
- weak coupling between bilateral frequency-floor suppression and treadmill
  speed once in that regime

### Strongest falsifier

The best next blocker test is now a **same-state replay fork**.

Starting from the same embodied state at the beginning of `baseline_a`, run
short continuations with:

1. the observed `baseline_a` latent stream
2. the observed `motion_ftb_a` latent stream
3. a stronger bilateral frequency-suppressed stream with amplitude and turn
   terms held fixed

Interpretation:

- if treadmill speed stays pinned across all forks, the embodied attractor
  hypothesis is supported
- if speed tracks the replayed frequency changes from the same starting state,
  the main blocker is upstream in the visual-to-forward signal

That experiment is now explicitly tracked in
[TASKS.md](/G:/flysim/TASKS.md) as `T188`.

## March 29, 2026 Public Recording Targets For Fitting

The Creamer workstream now has an explicit public-data fitting stack, because
further blind gain sweeps are low-value.

The highest-value public targets are summarized in
[creamer_recording_fit_targets.md](/G:/flysim/docs/creamer_recording_fit_targets.md).

### Best whole-branch fit targets

- **Aimon 2023 Dryad** for spontaneous / forced walking mesoscale structure
- **Schaffer 2023 Figshare** for whole-brain walking-state structure

### Best early motion-path fit targets

- **Ketkar 2022 Zenodo** for `L1/L2/L3`
- **Gruntman 2019 Figshare** for `T5`

### Best downstream locomotor fit targets

- **Shomar 2025 Dryad** for identified visual-to-locomotor channels
- **Dallmann 2025 Dryad** for treadmill proprioceptive / feedback realism

### Best behavioral / comparator targets

- **Creamer 2018** remains the main behavioral scorecard
- **Katsov and Clandinin 2008** remains the strongest public prior that
  translational and rotational motion computations should diverge
- **Cruz 2021**, **Henning 2022**, **Erginkaya 2025**, and **Clark 2023** are
  strong comparator and exclusion-set sources for separating true translational
  speed control from generic turning / optic-flow decoding

The fitting stack itself is now tracked in [TASKS.md](/G:/flysim/TASKS.md) as
`T189`.
