# Review Of Eon Embodiment Update (2026-03-10)

Reviewed source:

- `https://eon.systems/updates/embodied-brain-emulation`

Reviewed linked sources relevant to implementation claims:

- Shiu et al. whole-brain model: `https://www.nature.com/articles/s41586-024-07763-9`
- adult fly brain connectome: `https://www.nature.com/articles/s41586-024-07558-y`
- whole-brain annotation paper: `https://www.nature.com/articles/s41586-024-07686-5`
- FlyVis / visual-system model: `https://www.nature.com/articles/s41586-024-07939-3`
- NeuroMechFly v2 paper: `https://www.nature.com/articles/s41592-024-02497-y`
- NeuroMechFly advanced vision docs: `https://neuromechfly.org/tutorials/advanced_vision.html`
- NeuroMechFly controller docs: `https://neuromechfly.org/api_ref/examples/controllers.html`

## Main disclosures in the Eon update

The new post materially narrows what their embodied stack appears to be.

1. Brain core
- They describe the brain model as the simplified Shiu et al. LIF model built from the adult fly connectome plus neurotransmitter/sign predictions, not as a fully new richly parameterized proprietary whole-brain dynamical model.

2. Visual input
- They describe taking rendered visual input, running a connectome-constrained visual system model, and piping the resulting activations into corresponding neurons in the LIF brain model.
- But they explicitly say that the current visual input is not yet significantly influencing the embodied behavior.

3. Brain/body sync
- They say the brain and body are synchronized every `15 ms` because of current speed limits.

4. Body controller
- They say the body uses slight modifications of existing NeuroMechFly controllers trained by imitation learning for walking.
- They also say they do not know the exact correspondence between brain outputs and the locomotion controller inputs, so they currently infer a low-dimensional interface from a small set of outputs.

5. Scope / biological plausibility
- They explicitly describe the current body setup as simplified and not fully biologically plausible, with a model fly chasing another fly in an empty environment.

## Comparison to this repo

## Where the new Eon post agrees with our findings

1. The hard problem is the interface, not just “run the public pieces”.
- This matches our conclusion from the failed scalar public-anchor bridge and the later body-free splice work in `docs/splice_probe_results.md`.

2. Vision-to-brain splice is necessary.
- This matches our current `VisualSplice` path in `src/bridge/visual_splice.py`.

3. Output mapping is still heuristic.
- Their post now explicitly says they do not know the exact brain-output to locomotion-controller mapping.
- That matches our current limitation that the decoder still compresses descending/efferent activity into `left_drive` and `right_drive` in `src/bridge/decoder.py`.

4. Existing embodied controllers are still doing important work.
- Their post uses modified NeuroMechFly controllers.
- Our repo also still sits on top of FlyGym / NeuroMechFly controller machinery via `RealisticVisionFly` / `HybridTurningFly` wrappers in `src/body/brain_only_realistic_vision_fly.py` and `src/body/fast_realistic_vision_fly.py`.

## Where this repo is currently stronger

1. Stronger evidence that behavior is visually driven.
- Our strongest current branch has matched `zero_brain` and no-target controls in `docs/descending_visual_drive_validation.md`.
- Current evidence:
  - `zero_brain`: zero commands, negligible displacement
  - target-present: higher drive and steering asymmetry than no-target
  - `corr(right_drive - left_drive, target_bearing) = 0.7228`
- The Eon post, by contrast, says their current visual input is not yet significantly influencing the embodied result.

2. Stronger written evidence for why the naive bridge failed.
- Our repo now has the body-free splice audit and calibration record:
  - `docs/splice_probe_results.md`
  - `outputs/metrics/splice_probe_calibration_curated.json`
- That work shows the original scalar bridge was too lossy and that the output bottleneck was also fundamental.

3. Stronger falsification discipline.
- We explicitly removed:
  - decoder idle locomotion fallback
  - fake left/right public splits
  - optic-lobe-as-motor shortcuts
- and then re-validated with controls.

## Where Eon’s disclosed path may be ahead

1. Their body controller path is likely more optimized for stable embodiment.
- They mention imitation-learning modifications to existing NeuroMechFly controllers.
- Our current body interface is still a hand-built descending-population decoder into `left_drive` / `right_drive`.

2. Their released embodiment may already have a cleaner practical closed loop even if it is still heuristic.
- The post suggests they already have a working chase behavior on top of their chosen low-dimensional interface.
- Our current strongest branch is brain-driven and visually driven, but the short side-isolated left/right conditions remain mixed, and the motor code is still explicitly provisional.

## What the post changes about our interpretation

The new post weakens the case for any theory that Eon already had a fully biologically faithful end-to-end fly controller hidden behind the demo.

What it instead supports is this:

- they appear to be using the same general public brain-model family
- a real visual-system model is in the loop
- but the embodiment layer is still heuristic and controller-mediated
- and the exact output mapping remains unresolved on their side too

That is important because it validates the direction of our later work:

- move away from pretending a tiny public-anchor bridge is enough
- work the splice explicitly
- treat the motor interface as an open systems problem
- use controls instead of visual impressions alone

## Bottom line

The new Eon post does not invalidate this repo’s conclusions. It mostly confirms them.

Most important confirmation:

- the missing piece really is the interface between public brain, public vision, and embodied controllers
- not a simple install failure
- and not a hidden proof that the public brain model should naturally produce a full cold-start locomotor policy on its own

Main remaining difference:

- their currently disclosed embodiment appears more controller-mediated and less visually validated than our strongest current branch
- our branch has stronger target-vs-control evidence, but still lacks a final biologically grounded motor code
