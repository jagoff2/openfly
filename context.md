# Context Handoff for OpenFly

Last updated: 2026-04-04

## Purpose of this file

This file is a cold-start handoff for a fresh Codex session. It is written under
the assumption that the next session has **zero** usable chat context. The goal
is that a new session can read this one file, then immediately know:

- what this repository is trying to reproduce,
- what public science and public code it is built on,
- what has actually been implemented locally,
- which parts are grounded in exact public identifiers versus inferred bridges,
- which branch/configuration currently works best,
- which claims are supported by evidence,
- which gaps remain open,
- and how to split the remaining work into targeted sub-agent tasks.

This document is intentionally verbose. It is not only a summary. It is meant to
be a practical memory scaffold for re-entry.

## Executive summary

2026-04-04 addendum:

- The canonical whitepaper now includes a source-verified external comparison against `erojasoficial-byte/fly-brain`.
- The canonical reproduction commands now show the exact active parity invocation on this machine:
  - WSL2
  - `MUJOCO_GL=egl`
  - `PYTHONPATH=src`
  - `/root/.local/bin/micromamba run -n flysim-full`
  - full-parity endogenous routed configs only
- `main` and `exp/spontaneous-brain-latent-turn` were synchronized to the same parity commit before this addendum.

The repository at `G:\flysim` is a public-equivalent reconstruction of an
Eon-style embodied fruit-fly simulation stack. It combines:

- a persistent whole-brain FlyWire-based neural backend,
- a persistent embodied FlyGym / NeuroMechFly v2 body simulation,
- realistic vision rather than a trivial RGB-only control loop,
- an online bridge from sensory state into the brain,
- an online decoder from brain activity into body control,
- task tracking, benchmarks, tests, parity metrics, and documentation.

The repo is **past** the initial scouting/install stage. It already contains a
working closed-loop embodied stack, multiple bridge variants, multiple configs,
benchmark outputs, parity reports, and a substantial documentation trail.

The current strongest embodied branch is the calibrated UV-grid visual splice
plus a strict descending/efferent readout, configured by:

- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated.yaml`

That branch is the current best public-equivalent answer to the question:

"Can realistic vision from FlyGym / FlyVis be injected into the public whole
brain model in a way that produces closed-loop embodied motion with meaningful
target-conditioned steering?"

The honest answer is:

- **Yes, partially.**
- The stack is real, persistent, and embodied.
- It produces nontrivial visually driven locomotion and turn-sign behavior.
- It clearly outperforms zero-brain controls.
- It still falls short of a clean, exact, biologically faithful neuron-to-neuron
  visual mapping and still shows residual drift / excess locomotion over longer
  windows.

The key unresolved scientific/engineering issue is the interface between:

- the visual system representation available in FlyVis / realistic vision, and
- the exact neuron identities used by the FlyWire whole-brain model.

The key unresolved control issue is the output side:

- broad descending/efferent activity can drive the body,
- but the mapping from those outputs into high-quality target-conditioned motor
  commands remains the main bottleneck.

As of `2026-04-02`, one specific lawful target-interaction bottleneck has been
materially improved. The active routed target/no-target configs now carry a
stateful temporal sensory patch:

- stateful temporal visual features in
  `src/vision/feature_extractor.py`
- a small bilateral looming gain in `src/bridge/encoder.py`
- and, most importantly, a transient retinotopic motion term in
  `src/bridge/visual_splice.py`

This was done under the strict no-bypass rule:

- no target metadata into control
- no decoder/shadow promotion from visual-area activity into body control
- no controller-side shortcut heuristics

The active routed target/no-target configs are now also `splice-only` on the
visual encoder side:

- `encoder.visual_gain_hz = 0.0`
- `encoder.visual_looming_gain_hz = 0.0`

So target/object interaction in that branch is now driven only by:

- lawful realistic-vision feature extraction
- the retinotopic temporal visual splice
- brain dynamics
- descending outputs

The first parity-time embodied target retest on this lawful branch,
`outputs/requested_1p1s_endogenous_routed_target_parity_temporal/flygym-demo-20260401-235448`,
materially improved target clearance in the old failure window:

- old first-`1.1 s` slice from the exact `2.0 s` target run:
  - minimum target distance `0.5780 mm`
  - `119` cycles under `2.0 mm`
  - `86` cycles under `1.5 mm`
- new lawful temporal branch:
  - minimum target distance `2.4862 mm`
  - `0` cycles under `2.0 mm`
  - `0` cycles under `1.5 mm`

That result matters because it shows the object-response miss was not only a
decoder/output problem. A lawful sensory-path improvement alone was enough to
change the embodied target interaction materially. The full `2.0 s` retest on
the same branch has now completed on the stricter splice-only visual setting:

- `outputs/requested_2s_endogenous_routed_target_parity_temporal_splice_only/flygym-demo-20260402-003922`

That exact full `2.0 s` run removed the old overlap failure completely:

- old exact target run:
  - minimum target distance `0.5780 mm`
  - `86` cycles under `1.5 mm`
  - `119` cycles under `2.0 mm`
- new splice-only exact target run:
  - minimum target distance `3.0065 mm`
  - `0` cycles under `1.5 mm`
  - `0` cycles under `2.0 mm`
  - `0` cycles under `3.0 mm`

The remaining target-side problem is no longer catastrophic overlap. It is weak
target fixation / bearing improvement over the full run:

- `fixation_fraction_20deg = 0.076`
- `fixation_fraction_30deg = 0.113`
- `bearing_reduction_rad = -0.9223`

So the active lawful target branch is now materially safer, but still not
correct target-oriented behavior.

## Mission and standards that govern this repo

The repo was built under a strict reproduction brief:

- reproduce the public-equivalent embodied fly stack as closely as public
  artifacts allow,
- do not pretend private Eon glue is available if it is not,
- measure parity using observable outputs,
- keep everything local, scripted, benchmarked, and testable,
- maintain explicit task tracking and a dated lab notebook,
- no bypass, no faking, no laziness:
  - no target metadata shortcuts into control
  - no decoder-side or shadow-decoder-side promotion from visual-area activity directly into body control
  - visual/object effects on behavior must pass through lawful sensory pathways, brain dynamics, and descending outputs only
- and never hand-wave missing glue code.

The repo therefore includes:

- `TASKS.md` as the explicit task tracker,
- `PROGRESS_LOG.md` as the dated notebook / progress record,
- `REPRO_PARITY_REPORT.md` as the running parity verdict,
- `ASSUMPTIONS_AND_GAPS.md` for public-vs-inferred boundaries,
- `docs/` for subsystem writeups,
- `tests/` for smoke/unit/integration coverage,
- `benchmarks/` and `outputs/` for performance and artifacts.

## Cold-start reading order

If a fresh session needs to rebuild mental state quickly, read in this order:

1. `README.md`
2. `REPRO_PARITY_REPORT.md`
3. `TASKS.md`
4. `PROGRESS_LOG.md`
5. `docs/system_architecture.md`
6. `docs/sensory_motor_mapping.md`
7. `docs/realistic_vision_integration.md`
8. `docs/splice_probe_results.md`
9. `docs/descending_readout_expansion.md`
10. `docs/uvgrid_decoder_calibration.md`
11. `docs/neck_output_motor_basis.md`

If the fresh session is specifically about visual neuron mapping, add:

- `docs/inferred_lateralized_visual_candidates.md`
- `docs/visual_splice_strategy.md`
- `docs/splice_drift_audit.md`
- `outputs/metrics/flyvis_overlap_inventory.json`
- `outputs/metrics/splice_celltype_alignment_recommended.json`
- `outputs/metrics/inferred_lateralized_visual_recommended.json`

If the fresh session is specifically about motor/output semantics, add:

- `docs/descending_motor_atlas.md`

## April 1, 2026 harness repair patch

The parity loop changed materially on April 1, 2026 and this matters more than
the recent tiny metric deltas.

What was repaired:

- The Aimon replay path in
  [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py)
  was partially poisoned.
  - `spontaneous_walk` no longer hard-codes all-zero regressors.
  - `forced_walk` no longer takes `abs()` and per-trial max normalization.
  - invalid `window_start/window_stop` metadata no longer collapses replay to
    constants or tail-stretched covariates.
- The canonical exporter in
  [aimon_canonical_dataset.py](/G:/flysim/src/analysis/aimon_canonical_dataset.py)
  now writes trial-aligned regressor files instead of leaving the fitter to
  guess how to slice incompatible raw arrays.
- Both parity configs no longer contain duplicate top-level `encoder:` blocks:
  - [brain_endogenous_public_parity.yaml](/G:/flysim/configs/brain_endogenous_public_parity.yaml)
  - [brain_endogenous_public_parity_routed_only.yaml](/G:/flysim/configs/brain_endogenous_public_parity_routed_only.yaml)
- The scorer in
  [public_neural_measurement_harness.py](/G:/flysim/src/analysis/public_neural_measurement_harness.py)
  now reports lag-aware timing metrics in addition to strict zero-lag metrics.
- The Aimon body-feedback path no longer reuses transition-derived drive in
  multiple positive encoder channels:
  - [public_body_feedback.py](/G:/flysim/src/analysis/public_body_feedback.py)
  - [encoder.py](/G:/flysim/src/bridge/encoder.py)
- The fit head in
  [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py)
  now sees slow endogenous backend state directly:
  - conductance summaries
  - adaptation
  - intrinsic noise
  - graded release
  - intracellular calcium
  - distributed temporal state
  - synapse-class state
  - modulatory state
- The backend in
  [pytorch_backend.py](/G:/flysim/src/brain/pytorch_backend.py)
  now separates public exafference target tracking from internal arousal.
  `modulatory_exafference_state` is no longer just the same internal target as
  arousal with a different tau.

Validation state:

- Focused repair slice passed:
  - `51 passed, 1 warning`
- The Aimon canonical bundle was regenerated from:
  - [external/spontaneous/aimon2023_dryad](/G:/flysim/external/spontaneous/aimon2023_dryad)
- The first repaired short exact-identity retest is:
  - [aimon_b350_forced_window_routed_v5_replayfix](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v5_replayfix)

Operational consequence:

- Any Aimon timing conclusion from before the April 1 repair patch should be
  treated as provisional unless it is reconfirmed on the repaired path.
- The next admissible metric comparison is the repaired
  `B350_forced_walk` 4-window split against the old `v2 continuity` and `v4
  body-feedback` baselines.
- `docs/descending_monitoring_atlas.md`
- `docs/neck_output_mapping_strategy.md`
- `docs/neck_output_motor_basis.md`
- `outputs/metrics/descending_readout_recommended.json`
- `outputs/metrics/descending_monitor_neck_output_atlas.json`
- `outputs/metrics/descending_motor_atlas_summary.json`
- `outputs/metrics/neck_output_motor_basis_1s_summary.json`

## Hardware and execution environment

Target machine assumptions for this repo:

- Host OS: Windows 11
- Linux environment: WSL2 preferred
- GPUs: dual NVIDIA RTX 5060 Ti 16 GB
- RAM: 192 GB
- Local compute preferred

Important environment reality:

- WSL2 is the practical primary runtime for the serious embodied runs.
- The project has repeatedly treated "validated in real WSL on this machine" as
  a stronger milestone than mock or local pure-Python runs.
- GPU support for some public components is constrained by public wheel/build
  availability, not only by raw hardware capability.

## What this repository adds beyond upstream public code

This repo is **not** a direct copy of one upstream project. Its core value is
the glue and evaluation layer that the public codebases do not provide as a
single turnkey system.

What upstream public code gives:

- a whole-brain connectome model and related notebooks,
- an embodied fly body and realistic vision stack,
- benchmark backends,
- public connectome data and cell annotations.

What this repo adds:

- a persistent online closed-loop runtime,
- clean interfaces between body, brain, vision, and control,
- practical sensory encoding and motor decoding layers,
- bridge variants ranging from public anchor contexts to inferred visual splice
  modes,
- strict control comparisons including `zero_brain` and `no_target`,
- realistic-vision production paths,
- parity metrics,
- task tracking and research notes that preserve the reasoning trail.

## Public upstream components and what each one contributes

### 1. `external/fly-brain`

Role:

- engineering benchmark repo associated with the public Eon fly-brain context,
- provides multiple backend pathways,
- supplies packaged datasets and benchmarking structure,
- serves as the most practical systems-oriented public reference.

Why it matters here:

- it demonstrates realistic backend choices,
- it provides data assets used by the local Torch backend,
- it is the main benchmark-oriented public repo closest in spirit to the Eon
  demo engineering story.

### 2. `external/Drosophila_brain_model`

Role:

- Philip Shiu's public repository for the Nature 2024 whole-brain work,
- authoritative source for the original public model framing and task notebooks.

Why it matters here:

- it is the main science reference for public task anchors,
- it shows real public neuron IDs used in example sensorimotor tasks,
- it demonstrates the original batch-oriented Brian2-style workflow.

Important limitation:

- it is not already a drop-in persistent embodied online controller.

### 3. `external/flygym`

Role:

- embodied body simulation stack,
- NeuroMechFly v2 / FlyGym public code,
- MuJoCo-based physics and realistic embodiment,
- visual system integration and realistic sensory interfaces.

Why it matters here:

- it provides the body, the world, and the realistic vision path,
- it makes it possible to test whether neural control is genuinely embodied.

### 4. FlyWire / connectome publications and annotation ecosystem

Role:

- provides the actual adult female whole-brain connectome basis,
- provides cell annotations and structural truth used by the neural model.

Why it matters here:

- this is the biological graph that the whole-brain backend simulates,
- the repo's public neuron IDs and inferred bridge logic depend on these
  annotations being correct.

### 5. FlyVis / realistic visual modeling

Role:

- connectome-constrained visual system model used for realistic visual features.

Why it matters here:

- this is the mandatory realistic vision path,
- it is the production path that replaces simplistic camera-only baselines,
- it creates the main cross-model mapping challenge, because its representation
  does not align one-to-one with the FlyWire whole-brain neuron identity space.

## Scientific foundation that this repo assumes

This repo sits on several public papers and public codebases. The following is
the working scientific picture that should be carried forward.

### Whole-brain connectome and simulation

The public whole-brain model is based on the adult female *Drosophila*
connectome and related annotation work published in the October 2024 Nature
paper cluster. The important practical consequence is:

- the repo has access to a large-scale structural graph of neurons and
  connectivity,
- it can run a persistent neural simulation on that graph,
- and the graph is rich enough to support broad sensorimotor hypotheses,
  including descending pathways.

The core whole-brain public reference is the Shiu et al. Nature 2024 paper:

- `https://www.nature.com/articles/s41586-024-07763-9`

This is the key paper behind the public whole-brain simulation story. It is the
main source for the public task examples used here, such as locomotor and
feeding/grooming anchors.

Related connectome/annotation papers that form the broader foundation include:

- Dorkenwald et al. Nature 2024: `s41586-024-07558-y`
- Schlegel et al. Nature 2024: `s41586-024-07686-5`
- Eichler et al. Nature 2024: `s41586-024-07968-y`
- Lappalainen et al. Nature 2024: `s41586-024-07939-3`

These are not interchangeable, but together they establish the structural,
annotation, completeness, and neuropil-level context that makes the whole-brain
model credible.

### Embodiment and realistic sensing

The embodied side is grounded in NeuroMechFly v2 / FlyGym, especially the
Nature Methods 2024 paper:

- `https://www.nature.com/articles/s41592-024-02497-y`

The practical scientific implication is:

- the body simulation is not a toy kinematic shell,
- physics and leg/body actuation matter,
- and realistic sensory pathways can be attached to the body in a way that is
  materially closer to animal embodiment than static notebook experiments.

### Why neuron mapping is hard in this project

There is a crucial scientific boundary here:

- the whole-brain backend uses FlyWire-style neuron identity and annotation
  space,
- while the realistic vision side does not simply hand over exact FlyWire root
  IDs for every active visual unit.

That means the project cannot just do an exact identity-preserving join from
"visual neurons in FlyVis" to "visual neurons in the whole-brain model" using a
public built-in table. The repo therefore has to bridge between models.

That bridge is the main place where this project is both scientifically
interesting and scientifically constrained.

## Concrete data assets and annotation sources in this repo

Important data assets and caches include:

- `external/fly-brain/data/2025_Completeness_783.csv`
- `external/fly-brain/data/2025_Connectivity_783.parquet`
- `outputs/cache/flywire_annotation_supplement.tsv`

The supplement TSV is especially important because it is used to recover exact
annotation details such as:

- `root_id`
- `cell_type`
- `side`

Those fields are central to the visual splice approach because they provide a
stable grouping basis on the whole-brain side even when exact cross-model
identity is unavailable.

## Repo structure and where the important logic lives

Top-level directories that matter most:

- `src/brain/`
- `src/body/`
- `src/vision/`
- `src/bridge/`
- `src/runtime/`
- `src/metrics/`
- `configs/`
- `docs/`
- `outputs/metrics/`

### Brain layer

Important files:

- `src/brain/pytorch_backend.py`
- `src/brain/public_ids.py`
- `src/brain/paper_task_ids.py`
- `src/brain/paper_task_probes.py`
- `src/brain/flywire_annotations.py`
- `src/brain/zero_backend.py`
- `src/brain/mock_backend.py`

Responsibilities:

- loading/hosting the persistent whole-brain state,
- exposing public anchor neuron IDs,
- supporting probe/task logic,
- providing both real and control backends.

The `pytorch_backend.py` implementation is the main persistent whole-brain path.
It should be treated as the real production backend, not as a placeholder.

The `zero_backend.py` implementation is important because it provides a clean
negative control. It helps answer whether locomotion is actually being caused by
brain outputs or by hidden controller defaults.

### Body layer

Important files:

- `src/body/flygym_runtime.py`
- `src/body/fast_realistic_vision_fly.py`
- `src/body/brain_only_realistic_vision_fly.py`
- `src/body/connectome_turning_fly.py`
- `src/body/interfaces.py`
- `src/body/mock_body.py`

Responsibilities:

- managing embodied FlyGym runtime state,
- realistic vision stepping,
- body-specific wrappers and experimental fly variants,
- mock/test body support.

The body side is not just a renderer. It is the embodied plant being controlled.

### Vision layer

Important files:

- `src/vision/feature_extractor.py`
- `src/vision/flyvis_fast_path.py`
- `src/vision/inferred_lateralized.py`
- `src/vision/lateralized_probe.py`

Responsibilities:

- extracting usable visual features,
- supporting realistic vision fast paths,
- exploring laterality and inferred visual structure,
- probing candidate mappings between visual activity and turn-relevant signals.

### Bridge layer

Important files:

- `src/bridge/encoder.py`
- `src/bridge/brain_context.py`
- `src/bridge/visual_splice.py`
- `src/bridge/decoder.py`
- `src/bridge/controller.py`

Responsibilities:

- encoding body/sensory state into neural inputs,
- injecting known public context modes,
- injecting inferred or splice-based visual drives,
- decoding neural activity into motor commands,
- packaging control outputs for the runtime loop.

This layer is the actual heart of the repo. It is where the public components
become a single online controller.

### Runtime and metrics layers

Important files:

- `src/runtime/closed_loop.py`
- `src/runtime/logging_utils.py`
- `src/metrics/parity.py`
- `src/metrics/timing.py`

Responsibilities:

- running the persistent synchronized loop,
- logging structured outputs,
- computing timing and parity metrics,
- preserving enough evidence that claims can be checked later.

## High-level runtime architecture

The current architecture can be described plainly as:

1. The body simulation advances in a persistent embodied world.
2. Realistic vision and/or body state are observed.
3. The bridge transforms those observations into neural inputs or modulation.
4. The whole-brain backend advances while preserving state across steps.
5. The decoder reads selected neural outputs.
6. Those outputs are converted into body control commands.
7. The next body step occurs.
8. Metrics/logs are written throughout the run.

This is a true closed loop. It is not just:

- run a brain notebook once,
- save a CSV,
- then replay it in the body later.

The persistence of both brain state and body state is essential.

## Public neuron anchors that are explicitly preserved

The repo preserves several public neuron/task anchors rather than inventing
everything from scratch. These are defined across:

- `src/brain/public_ids.py`
- `src/brain/paper_task_ids.py`

Working anchor categories include:

- locomotor anchors such as `P9` and `P9_oDN1`,
- descending locomotor-related neurons such as `DNa01`, `DNa02`, and `MDN`,
- grooming/feeding/task readouts such as `MN9`, `aDN1`, and `aBN1`,
- visual and sensory anchors such as `LC4`,
- auditory/mechanosensory `JON` subgroups,
- sugar GRN groupings used for non-vision task probes.

Specific names that have been carried forward in repo reasoning include:

- `P9_left`
- `P9_right`
- `P9_oDN1_left`
- `P9_oDN1_right`
- `DNa01`
- `DNa02`
- `MDN_1`
- `MDN_2`
- `MDN_3`
- `MDN_4`
- `MN9_left`
- `MN9_right`
- `aDN1_left`
- `aDN1_right`
- `aBN1`
- `LC4`
- `JON_CE`
- `JON_F`
- `JON_D_m`
- `JON_all`

These matter because they anchor the project to publicly inspectable neurons
rather than an entirely synthetic control basis.

## The neuron-mapping problem: exact, inferred, and bridged parts

This section is critical. A fresh session should retain these distinctions
carefully.

### What is exact

On the whole-brain side, the repo has exact or near-exact grounding through
public annotations and public task IDs. It can point to actual annotated neuron
groups and actual cell types in FlyWire-derived resources.

That means statements like the following are on relatively solid ground:

- "these public locomotor/task anchors exist,"
- "these annotated descending groups exist,"
- "these cell types and sides are present in the public annotation supplement."

### What is not exact

On the visual system side, the realistic vision interface does **not** simply
provide a ready-made exact one-to-one table from every active visual unit to a
FlyWire root ID in the whole-brain model.

Instead, the accessible FlyVis-side representation exposes features such as:

- `type`
- `u`
- `v`
- `role`
- internal indices

That is useful, but it is not the same as:

- exact FlyWire root ID for each active visual unit.

### What the repo does about that

The repo builds a bridge that is exact on the whole-brain grouping side and
inferred across the model boundary.

The core strategy is:

1. recover exact annotated groupings on the whole-brain side using public
   annotation data,
2. find exact shared naming overlap at the `cell_type` level where possible,
3. preserve hemisphere with `cell_type + side`,
4. then add coarse spatial structure using binned visual fields,
5. and inject signed/lateralized current into corresponding whole-brain groups.

This is not claimed to be an exact neuron-identity reconstruction. It is a
publicly grounded, engineering-explicit bridge.

## Visual splice findings that currently matter

The visual splice work has gone through several generations. The progression is
important because it explains what failed and why the current branch looks the
way it does.

### Early weak approach: scalar pooled drives

The early/simple bridge forms collapsed too much structure. In particular, they
often reduced vision to scalar or overly compressed pooled signals. That caused
several problems:

- weak lateral specificity,
- poor preservation of where in the visual field activity occurred,
- insufficient asymmetry for turning,
- and poor correspondence between visual scene changes and downstream steering.

The broad lesson was:

- a scalar visual bridge is too destructive.

### Stronger approach: exact shared `cell_type + side`

The next major improvement was to join the two systems using exact shared cell
type names and side labels where that overlap actually exists.

Important derived quantities that have been preserved in reasoning:

- `49` exact shared visual cell types,
- `98` bilateral `cell_type + side` groups,
- `392` groups after splitting each side-specific type into `4` spatial bins.

Those numbers matter because they describe the actual granularity of the current
publicly grounded bridge.

### Important photoreceptor detail

One subtle but important discovery was that the exact overlap found here is not
the full photoreceptor set people might casually assume. The exact overlap
called out in prior work is:

- `R7`
- `R8`

not the full `R1-R6` stack.

That matters because it constrains how confidently one can talk about exact
retinal-to-whole-brain alignment in the current public setup.

### Signed injection and spatial bins

The next important improvements were:

- moving from unsigned pooled stimulation to signed current injection,
- preserving left/right structure,
- adding coarse spatial bins,
- allowing directional asymmetry to survive into the brain input.

This materially improved turn-sign behavior and early response quality.

### UV-grid and per-cell-type transforms

The current stronger branch adds a UV-grid-like visual organization with
per-cell-type transforms. This is a more expressive splice than the earlier
1D-axis style variants.

This matters because different visual cell types can now contribute with:

- different gain structure,
- different polarity/sign treatment,
- different coarse spatial organization.

The current best branch is therefore not "just more neurons." It is a better
structured interface.

## What the splice currently succeeds at, and what it does not

Current honest assessment:

- the splice can launch the correct downstream turn sign at short horizons,
- the short-latency behavior around roughly `100 ms` is meaningfully better than
  the early bridges,
- but longer windows still drift,
- and the system is not yet a clean pure target-pursuit controller.

The critical empirical story preserved in prior analysis is:

- around short windows, the bridge shows credible directional launch,
- by around `500 ms`, the dynamics are less stable and can deviate or overrun.

That is why the repo contains splice probe summaries, drift audits, UV-grid
comparison artifacts, and calibration documents. The challenge is not "can any
visual activity be injected at all?" The challenge is "can the injected visual
activity remain semantically correct over time?"

## Output-side findings: descending readout expansion

The output side turned out to be at least as important as the sensory splice.

### Early weak approach: tiny readout

A narrow readout using only a tiny set of output neurons was too weak and too
fragile. It did not provide enough effective control authority to generate good
embodied motion.

### Stronger approach: strict descending/efferent candidates

The repo then expanded the readout to a stricter and broader descending /
efferent candidate set. Important candidate names repeatedly surfaced in the
repo's findings, including:

- `DNp103`
- `DNp06`
- `DNp18`
- `DNp35`
- `DNpe056`
- `DNp71`
- `DNpe040`

The working practical interpretation has been:

- some groups correlate strongly with forward drive,
- some with mirrored turn drive,
- some are active but ambiguous in the present control/body stack,
- and the body/controller interface still compresses their true semantics.

### Neck-output monitoring and motor atlas work

The repo later added a broader monitoring-only path for descending/efferent
activity and built:

- an observational neck-output atlas,
- a causal perturbation atlas,
- and a first fitted neck-output motor basis.

Those artifacts are important because they mark a shift in strategy:

- from hand-authored motor guesses,
- toward measured output semantics from the embodied system itself.

However, that line of work is **not** yet promoted to the main production
branch, because it has not clearly beaten the current calibrated two-drive
baseline under matched controls.

## Current best embodied production branch

The strongest current branch for actual embodied target-conditioned locomotion is
the calibrated UV-grid descending two-drive branch:

- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated.yaml`

Relevant matched controls also exist, including:

- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_zero_brain.yaml`

These control configs matter because they help separate three questions:

1. does the system move at all,
2. does it still move without a target,
3. does it still move when the brain is disabled.

### Best remembered matched target-run metrics

The working remembered benchmark for the best matched `2 s` target run is
approximately:

- `avg_forward_speed = 4.9241`
- `path_length = 9.8383`
- `net_displacement = 5.7583`
- `displacement_efficiency = 0.5853`
- `corr(right_drive-left_drive, target_bearing) = 0.8810`
- `steer_sign_match_rate = 0.8878`
- `nonzero_command_cycles = 993`

These numbers should be treated as the current best concise evidence that the
stack is doing real visually coupled control rather than random motion.

### Control interpretation

The key control comparisons are:

- `zero_brain` produces zero commands and near-zero displacement,
- therefore there is no hidden locomotion fallback silently driving the body,
- `no_target` still often produces substantial motion,
- therefore the best branch is visually driven but not yet cleanly
  target-selective.

That last point is crucial. The repo does **not** claim full parity with an
ideal target-pursuit demo. The honest status is still partial parity.

## Why parity is currently "partial" rather than "pass"

The repo can already support several strong claims:

- there is a persistent embodied closed loop,
- realistic vision is actually integrated,
- the brain backend materially affects behavior,
- zero-brain controls are clean,
- target-conditioned steering signal exists,
- videos/logs/metrics/benchmarks are generated locally.

But it cannot yet honestly claim:

- exact published-neuron visual identity mapping end to end,
- stable target-faithful behavior over long windows,
- full output semantics equivalent to a detailed VNC/muscle pathway,
- or clean suppression of no-target locomotion in the current best branch.

That is why the parity verdict remains partial.

## Important configuration families and what they mean

There are several config families in `configs/` that encode the repo's history.

### Public anchor context modes

Examples:

- `configs/flygym_realistic_vision_public_p9_context.yaml`
- `configs/flygym_realistic_vision_inferred_visual_p9.yaml`
- `configs/flygym_realistic_vision_inferred_visual_turn.yaml`

These represent simpler or earlier control modes that inject public or inferred
task context into the brain.

### Axis-1D splice family

Examples:

- `configs/flygym_realistic_vision_splice_axis1d.yaml`
- `configs/flygym_realistic_vision_splice_axis1d_descending_readout.yaml`
- `configs/flygym_realistic_vision_splice_axis1d_descending_readout_target_left.yaml`
- `configs/flygym_realistic_vision_splice_axis1d_descending_readout_target_right.yaml`
- `configs/flygym_realistic_vision_splice_axis1d_descending_readout_no_target.yaml`
- `configs/flygym_realistic_vision_splice_axis1d_descending_readout_zero_brain.yaml`

These represent an important intermediate generation. They matter historically
and analytically, but they are not the current best production branch.

### UV-grid calibrated two-drive family

Examples:

- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_zero_brain.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_monitored.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_monitored_no_target.yaml`

This is the main production family.

### Multidrive and fitted-basis family

Examples:

- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_no_target.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_zero_brain.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_no_target.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_zero_brain.yaml`

These encode the newer output-side experimentation. They are promising, but they
have not yet surpassed the calibrated two-drive branch.

## Performance and machine-specific reality

The repo includes dedicated performance documents and profiling artifacts,
including:

- `docs/perf_tuning.md`
- `docs/multi_gpu_evaluation.md`
- `docs/vision_perf_plan.md`
- `outputs/profiling/README.md`

The performance picture that should be remembered is:

- the whole-brain Torch path is viable and useful,
- realistic vision is a major runtime cost,
- the realistic-vision path is the dominant practical bottleneck in many runs,
- and validated production FlyVis in WSL on this machine has remained CPU-bound
  because public binary/build support does not cleanly cover the RTX 5060 Ti
  `sm_120` target yet.

That last point is important. If a future session assumes "dual modern NVIDIA
GPUs means the whole stack should already be fully GPU-accelerated," it will
waste time. The current blocker is public compatibility, not lack of local
hardware.

## Tests and validation structure

The repo does not rely only on ad hoc demos. It contains smoke/unit/integration
tests for key subsystems. Important tests to remember include:

- `tests/test_imports.py`
- `tests/test_bridge_unit.py`
- `tests/test_closed_loop_smoke.py`
- `tests/test_realistic_vision_path.py`
- `tests/test_descending_motor_atlas.py`

There may be additional tests beyond these, but these are the important named
ones carried forward in current reasoning.

The testing philosophy has been:

- add or update a test before claiming a subsystem works,
- keep short deterministic smoke configs for expensive systems,
- save artifacts rather than relying on verbal claims.

## Important documents and what each one answers

This section is meant as a lookup table for a fresh session.

### Core architecture and install

- `docs/architecture_scout.md`
  Explains the initial inspection of candidate public repos and what each one
  contributes.

- `docs/dependency_matrix.md`
  Tracks dependency relationships and environment constraints.

- `docs/repo_gap_analysis.md`
  Explains what upstream public code already does versus what this repo had to
  implement as glue.

- `docs/system_architecture.md`
  High-level architecture for the online closed-loop system.

- `docs/timing_model.md`
  Timing, synchronization, and cadence assumptions across body/brain/control.

- `docs/install_report.md`
  What was installed and how the environment validated.

### Vision and splice reasoning

- `docs/realistic_vision_integration.md`
  Documents how the realistic vision path is used and why it is mandatory.

- `docs/visual_splice_strategy.md`
  Explains the splice philosophy from pooled drives toward structured mappings.

- `docs/splice_probe_results.md`
  Summarizes what splice probes showed.

- `docs/splice_drift_audit.md`
  Records the short-window-vs-longer-window stability issue.

- `docs/inferred_lateralized_visual_candidates.md`
  Candidate visual group reasoning for left/right turn structure.

- `docs/descending_visual_drive_validation.md`
  Early descending-output validation against visual drive.

- `docs/descending_uvgrid_visual_drive_validation.md`
  UV-grid visual-drive validation.

- `docs/uvgrid_decoder_calibration.md`
  Documents the calibration steps for the current best UV-grid branch.

### Output-side and motor semantics

- `docs/descending_readout_expansion.md`
  Why the decoder had to move beyond a tiny output set.

- `docs/descending_monitoring_atlas.md`
  Monitoring-only embodied atlas for broad descending/efferent groups.

- `docs/descending_motor_atlas.md`
  Causal perturbation atlas for motor relevance.

- `docs/neck_output_mapping_strategy.md`
  Strategic framing for moving from monitored outputs to fitted bases.

- `docs/neck_output_motor_basis.md`
  Current fitted-basis work, its evidence, and why it is not yet promoted.

- `docs/multidrive_decoder_validation.md`
  Validation notes for the multidrive branch.

### Broader status and narrative docs

- `docs/eon_embodiment_update_review_2026-03-10.md`
  Snapshot review of the embodiment effort near the current phase.

- `docs/openfly_whitepaper.md`
  Longer-form repo narrative.

- `REPRO_PARITY_REPORT.md`
  Current public-equivalent parity verdict and evidence framing.

## Important metrics and artifact files worth knowing by name

The `outputs/metrics/` directory contains many JSON artifacts. The most useful
named ones to remember are:

- `outputs/metrics/flyvis_overlap_inventory.json`
- `outputs/metrics/splice_celltype_alignment_recommended.json`
- `outputs/metrics/inferred_lateralized_visual_recommended.json`
- `outputs/metrics/splice_probe_summary.json`
- `outputs/metrics/splice_probe_signed_bins4_summary.json`
- `outputs/metrics/splice_probe_uvgrid_celltype_aligned_summary.json`
- `outputs/metrics/splice_drift_audit_key_findings.json`
- `outputs/metrics/descending_readout_recommended.json`
- `outputs/metrics/descending_visual_drive_validation.json`
- `outputs/metrics/descending_uvgrid_visual_drive_validation.json`
- `outputs/metrics/descending_uvgrid_calibrated_visual_drive_validation.json`
- `outputs/metrics/descending_monitor_neck_output_atlas.json`
- `outputs/metrics/descending_motor_atlas_summary.json`
- `outputs/metrics/neck_output_motor_basis.json`
- `outputs/metrics/neck_output_motor_basis_1s_summary.json`
- `outputs/metrics/uvgrid_decoder_calibration_best.json`

These artifacts collectively tell the story of:

- overlap inventory,
- splice candidate selection,
- short-window and drift behavior,
- output candidate selection,
- calibration,
- and the newer fitted-basis output work.

## Feeding and grooming work

The repo is not only about visual locomotion. It also includes brain-task work
for feeding and grooming probes, mainly through:

- `src/brain/paper_task_ids.py`
- `src/brain/paper_task_probes.py`
- related outputs such as `feeding_probe_summary.json` and
  `grooming_probe_summary.json`

This work matters because it confirms the repo is grounded in more than one
public task family. However, these probe paths are still mostly brain-only task
validation rather than fully embodied closed-loop behavior.

## What is currently true about the fitted-basis branch

A fresh session should not forget the current status of the newer output-side
branch.

The fitted neck-output motor basis work:

- exists,
- is wired into the decoder,
- passes matched real WSL runs,
- is clearly brain-driven versus `zero_brain`,
- but still does **not** cleanly separate `target` from `no_target` on the key
  locomotion/displacement metrics.

This is reflected in the active tracker state around:

- `T094`
- `T095`
- `T096`

Interpretation:

- the fitted-basis branch is promising,
- it is not dead,
- but it should not yet displace the calibrated two-drive production branch.

## Current task tracker state that matters most

At the time of writing, the latest visible tracker tail includes:

- `T089`: calibrate the hybrid motor-latent decoder so target-conditioned
  behavior improves without inflating no-target locomotion. Status: `todo`.

- `T090`: record the neck-output mapping strategy explicitly. Status: `done`.

- `T091`: add monitoring-only support for broad public descending/efferent
  populations. Status: `done`.

- `T092`: build the first observational neck-output atlas. Status: `done`.

- `T093`: build the first causal descending motor-response atlas. Status:
  `done`.

- `T094`: derive a fitted neck-output motor basis and replace the hand-authored
  multidrive mapping. Status: `doing`.

- `T095`: refine the fitted basis so target-conditioned behavior improves over
  no-target locomotion, not only over zero-brain. Status: `todo`.

- `T096`: add explicit target-tracking review to the fitted-basis evaluation
  loop and stop relying only on aggregate locomotion metrics. Status: `doing`.

The important meta-lesson is:

- the repo is no longer mostly blocked on install or scaffolding,
- it is now blocked on refinement of the visual-to-brain and brain-to-body
  semantics.

## Top unresolved gaps

These are the main unresolved gaps that should remain active in memory.

### 1. No exact FlyVis-to-FlyWire neuron identity map

This is the deepest scientific/engineering gap. The current splice is grounded
and useful, but it is not a proven exact one-to-one neuron identity map across
the public vision and whole-brain systems.

### 2. Long-window splice stability is still weaker than short-window launch

The system can produce the right turn sign and early directional response, but
it does not remain as semantically clean over longer windows.

### 3. Output semantics are still compressed

The present controller still compresses broad descending/efferent activity into
simple body-control latents such as left/right drive or a small number of motor
basis components. This is useful, but it is not the same as a full VNC/muscle
pathway.

### 4. No-target motion is still too strong

The best branch is brain-driven and visually influenced, but `no_target` still
produces too much locomotion to claim clean target selectivity.

### 5. Short isolated target conditions remain a necessary debugging tool

Target-left, target-right, no-target, and zero-brain matched conditions remain
important because they expose control asymmetry and drift more clearly than a
single aggregate demo.

### 6. Validated GPU FlyVis remains limited by public support

This is a practical performance gap rather than a conceptual one. The local
hardware is strong, but validated public support for the exact GPU stack has
lagged.

## Recommended sub-agent decomposition for future work

If a future session wants to delegate work efficiently, the cleanest partitions
are:

### 1. Runtime / control-loop agent

Ownership:

- `src/runtime/`
- `src/bridge/controller.py`
- logging/timing integration

Use this for:

- synchronization issues,
- run-loop robustness,
- logging schema changes,
- benchmark cadence instrumentation.

### 2. Visual splice / neuron-mapping agent

Ownership:

- `src/bridge/visual_splice.py`
- `src/vision/`
- overlap inventory and splice metrics docs

Use this for:

- FlyVis/FlyWire overlap analysis,
- better lateralization,
- better spatial binning,
- longer-window stability improvements,
- calibration search around visual transforms.

### 3. Output semantics / motor basis agent

Ownership:

- `src/bridge/decoder.py`
- output atlas scripts/docs
- multidrive and fitted-basis configs

Use this for:

- descending/efferent candidate selection,
- neck-output basis refinement,
- target-vs-no-target separation,
- broader output monitoring and control decoding.

### 4. Benchmark / profiling agent

Ownership:

- `benchmarks/`
- `outputs/metrics/`
- `outputs/profiling/`
- `docs/perf_tuning.md`
- `docs/multi_gpu_evaluation.md`

Use this for:

- speed comparisons,
- reproducibility checks,
- artifact summarization,
- machine-specific tuning evidence.

### 5. Paper-task embodiment agent

Ownership:

- `src/brain/paper_task_*`
- feeding/grooming probe logic
- corresponding docs/artifacts

Use this for:

- extending public task probes into embodied or semi-embodied loops,
- preserving paper-grounded neuron references,
- broadening beyond visual locomotion without losing scientific grounding.

## What a fresh session should believe immediately after reading this file

After reading this file, a new session should assume the following unless later
local evidence contradicts it:

- the repo already contains a real embodied closed-loop system,
- the strongest current production path is the calibrated UV-grid visual splice
  with strict descending two-drive readout,
- realistic vision is actually integrated and not merely claimed,
- the repo's main unsolved problem is the semantic quality of the interface,
  especially cross-model visual mapping and output decoding,
- the fitted-basis / multidrive output branch is promising but not yet good
  enough to replace the current baseline,
- zero-brain controls are clean and therefore useful for causal interpretation,
- and the next productive work should focus on targeted refinement rather than
  redoing Phase 0 or Phase 1.

## Practical re-entry instructions

If starting a clean session:

1. Read this file fully.
2. Read `README.md`, `REPRO_PARITY_REPORT.md`, `TASKS.md`, and `PROGRESS_LOG.md`.
3. Inspect the latest tasks `T094` through `T096`.
4. Decide whether the next task is primarily:
   runtime, visual splice, output semantics, profiling, or paper-task work.
5. Open the corresponding docs and metrics artifacts listed above.
6. Only then dispatch targeted sub-agents with explicit file ownership.

## Final state of understanding captured here

In plain language:

This repo is a serious public reconstruction of an embodied fruit-fly simulation
stack. It combines a public whole-brain FlyWire-derived model, a public embodied
FlyGym body, a realistic visual pathway, and custom glue that makes them run
together online. The public science basis is real. The implementation is real.
The results are real enough to show visually driven embodied behavior. The
remaining gaps are also real and should not be minimized.

The most important scientific distinction to carry forward is:

- public neuron/task anchors on the whole-brain side are grounded,
- realistic visual inputs are available,
- but exact identity-preserving visual-to-brain mapping remains unavailable in
  public form and therefore had to be inferred through structured grouping.

The most important engineering distinction to carry forward is:

- the stack already works end to end,
- but its quality now depends much more on better semantics than on mere
  installation or scaffolding.

The most important tactical distinction to carry forward is:

- keep the calibrated UV-grid descending branch as the current production
  baseline,
- continue investigating the fitted-basis branch as the main output-side
  refinement path,
- and do not lose the exact-vs-inferred neuron mapping boundary when reasoning
  about future improvements.

## March 29, 2026 priority override and compaction handoff

This section supersedes the older tactical guidance above for the immediate next
phase.

### New top-level priority

The repo's highest-priority work is now:

- **public neural measurement parity on the spontaneous / living brain**

That means:

- obtain public real-fly neural measurement datasets
- convert them into canonical matched format
- drive the spontaneous brain under the same public conditions
- force model outputs to match the public measurements as closely as possible

Until that program has real traction, downstream Creamer / decoder /
embodiment work should not be the primary focus.

### Latest critical findings to preserve

1. **Synced Creamer scene semantics are now correct**
- The treadmill scene can now sync to fly speed and apply only a small signed
  offset.
- In the latest synced probe:
  - `baseline_a`: speed `645.153 mm/s`, slip `0.0 mm/s`
  - `motion_ftb_a`: speed `645.287 mm/s`, slip `-0.5 mm/s`
  - `baseline_b`: speed `645.244 mm/s`, slip `0.0 mm/s`
- So the scene-validity ambiguity is materially reduced.

2. **The remaining Creamer blocker is now more likely embodied response**
- Even with honest `-0.5 mm/s` front-to-back retinal slip, the branch did not
  slow and the first delta was slightly wrong-sign (`+0.13418 mm/s`).
- Independent blocker reviews converged on:
  - high-speed embodied treadmill attractor
  - weak coupling between bilateral frequency-floor suppression and treadmill
    speed once the branch sits near `~645 mm/s`

3. **Best next blocker test already identified**
- Run same-state replay forks from the start of `baseline_a`:
  - observed baseline latent stream
  - observed motion latent stream
  - stronger bilateral frequency-suppressed latent stream
- This is the cleanest falsifier for whether the body is effectively ignoring
  those changes once it enters the fast locomotor regime.

4. **Public fit targets are now explicit**
- Highest-value dataset stack:
  - Aimon 2023 Dryad
  - Schaffer 2023 Figshare
  - Ketkar 2022 Zenodo
  - Gruntman 2019 Figshare
  - Shomar 2025 Dryad
  - Dallmann 2025 Dryad
- Creamer 2018 remains the behavioral scorecard, not the best raw fit source.

### Immediate file map for the next session

Read these first:

1. [public_neural_measurement_parity_program.md](/G:/flysim/docs/public_neural_measurement_parity_program.md)
2. [creamer_recording_fit_targets.md](/G:/flysim/docs/creamer_recording_fit_targets.md)
3. [creamer2018_visual_speed_control_note.md](/G:/flysim/docs/creamer2018_visual_speed_control_note.md)
4. [TASKS.md](/G:/flysim/TASKS.md)
5. [PROGRESS_LOG.md](/G:/flysim/PROGRESS_LOG.md)

### Immediate next tasks

- `T191`: obtain and stage the public datasets
- `T192`: define the canonical matched-format neural measurement schema
- `T193`: build targeted fitting harnesses
- `T194`: force spontaneous-brain parity against public measurements

## March 29, 2026 public neural measurement parity implementation state

The new top-priority program is no longer just a note. It now has code,
artifacts, and staged public metadata.

New code:

- `src/brain/public_neural_measurement_sources.py`
- `src/analysis/public_neural_measurement_dataset.py`
- `src/analysis/public_neural_measurement_schema.py`
- `src/analysis/public_neural_measurement_harness.py`
- `scripts/fetch_public_neural_measurements.py`
- `scripts/summarize_public_neural_measurement_status.py`

Focused tests now pass:

- `tests/test_public_neural_measurement_sources.py`
- `tests/test_public_neural_measurement_schema.py`
- `tests/test_public_neural_measurement_dataset.py`
- `tests/test_public_neural_measurement_harness.py`

Current staged status:

- Aimon 2023:
  - fully staged raw source under `external/spontaneous/aimon2023_dryad`
- Schaffer 2023:
  - article JSON, manifest, files table, and `datasets_for_each_figure.xlsx`
  - root: `external/neural_measurements/schaffer2023_figshare`
- Ketkar 2022:
  - Zenodo record JSON, manifest, files table
  - root: `external/neural_measurements/ketkar2022_zenodo`
- Dallmann 2025:
  - Dryad dataset metadata, versions, file inventory, manifest, files table
  - root: `external/neural_measurements/dallmann2025_dryad`
- Shomar 2025:
  - Dryad dataset metadata, versions, file inventory, manifest, files table
  - root: `external/neural_measurements/shomar2025_dryad`
- Gruntman 2019:
  - authoritative collection/article endpoints identified by sub-agent
  - local manifest artifact not staged yet

Canonical status artifact:

- `outputs/metrics/public_neural_measurement_stage_status.json`

Current blocker:

- hostile Dryad raw-file delivery still blocks scripted raw staging for Dallmann
  and Shomar:
  - direct API download path returns `401`
  - direct `file_stream` path returns `403`

Most important next actions:

1. stage Gruntman manifest plus first figure zip
2. build dataset-specific adapters for Aimon, Schaffer, Ketkar, Dallmann
3. build the first open-loop replay harnesses against the spontaneous brain

## March 29, 2026 first real canonical exports

The parity program is now past metadata-only staging.

Two real canonical matched-format exports now exist:

1. **Aimon 2023 canonical bundle**
- code:
  - `src/analysis/aimon_canonical_dataset.py`
  - `scripts/export_aimon_canonical_dataset.py`
  - `tests/test_aimon_canonical_dataset.py`
- artifacts:
  - `outputs/derived/aimon2023_canonical/aimon2023_canonical_summary.json`
  - `outputs/derived/aimon2023_canonical/aimon2023_canonical_bundle.json`
- current result:
  - `2` exported experiments
  - `4` trials
  - surviving public experiments are `B350` and `B1269`
  - overlapping public rows `B1037` and `B378` are dropped

2. **Gruntman 2019 Figure 2 canonical bundle**
- code:
  - `src/analysis/gruntman_figure2_canonical_dataset.py`
  - `scripts/export_gruntman_figure2_canonical_dataset.py`
  - `tests/test_gruntman_figure2_canonical_dataset.py`
- artifacts:
  - `outputs/derived/gruntman2019_figure2_canonical/gruntman2019_figure2_canonical_summary.json`
  - `outputs/derived/gruntman2019_figure2_canonical/gruntman2019_figure2_canonical_bundle.json`
- current result:
  - `514` trials
  - `540` skipped empty conditions
  - raw membrane-potential traces sampled at `20 kHz`

Updated staging status:

- `outputs/metrics/public_neural_measurement_stage_status.json`

Current next-action order is now:

1. build the first Aimon replay/fitting harness against the spontaneous brain
2. add the next dataset-specific exporter after Aimon/Gruntman
3. do not resume decoder/embodiment-first work until the parity program yields actual measurement-match results

### Additional March 29, 2026 harness state

The first dataset-specific scoring harness now exists:

- `src/analysis/aimon_parity_harness.py`
- `tests/test_aimon_parity_harness.py`

What it does:

- loads the canonical Aimon bundle
- loads canonical trial matrices and timebases
- scores a simulated trial matrix against an observed Aimon trial using the
  generic trace-parity metrics

What it does **not** do yet:

- it does not yet run the spontaneous brain itself
- it does not yet project brain activity into Aimon region-component space

So the immediate tactical gap is now narrower:

- not “build the first Aimon harness”
- but “connect spontaneous-brain replay/projection outputs into the now-existing
  Aimon harness and optimize against those scores”

## March 29, 2026 first real spontaneous-brain measurement fit

The public neural measurement parity lane is now producing real model-vs-public
measurement scores.

New code:

- `src/analysis/aimon_spontaneous_fit.py`
- `scripts/run_aimon_spontaneous_fit.py`
- `tests/test_aimon_spontaneous_fit.py`

Supporting updates:

- `src/analysis/aimon_parity_harness.py`
  - now preserves `split`, `stimulus`, and `behavior_paths`
- `src/analysis/public_neural_measurement_harness.py`
  - now masks non-finite samples before computing trace metrics

Real pilot artifact:

- `outputs/metrics/aimon_spontaneous_fit_b1269_pilot_v2/aimon_spontaneous_fit_summary.json`

What the pilot actually did:

- used the living spontaneous branch from
  `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_jump_brain_latent_turn_spontaneous_refit.yaml`
- replayed canonical Aimon trials against the backend
- used the bilateral family voltage basis from the spontaneous mesoscale
  validator
- used encoder-based symmetric mechanosensory forcing for `forced_walk`
- fit a reduced linear projection into Aimon trace space

Current result:

- same-dataset fit on:
  - `B1269_spontaneous_walk`
  - `B1269_forced_walk`
- aggregate:
  - `mean_pearson_r = 0.890881`
  - `mean_nrmse = 0.0660805`
  - `mean_abs_error = 0.00172981`
  - `mean_sign_agreement = 0.857058`

Important honesty boundary:

- this is not held-out parity yet
- it proves the spontaneous-brain replay/projection path is live on real public
  neural measurements
- the next honest boundary is held-out Aimon generalization on the canonical
  train/test split

Immediate next tasks after this state:

1. update trackers to move `T194` into active execution
2. run held-out Aimon fit
3. use that result to define the first forcing/basis/regularization sweep
4. then extend the same program to Schaffer, Ketkar, Dallmann, and Shomar

## March 29, 2026 held-out Aimon boundary and Schaffer NWB exporter

The next honest boundary after the B1269 same-dataset pilot is now crossed.

Held-out Aimon artifact:

- `outputs/metrics/aimon_spontaneous_fit_train_to_test_v1/aimon_spontaneous_fit_summary.json`

What it did:

- fit on canonical `train`:
  - `B350_spontaneous_walk`
  - `B350_forced_walk`
- scored on held-out canonical `test`:
  - `B1269_spontaneous_walk`
  - `B1269_forced_walk`

Current result:

- aggregate over all four trials:
  - `mean_pearson_r = 0.145559`
  - `mean_nrmse = 0.246243`
  - `mean_abs_error = 0.00607705`
  - `mean_sign_agreement = 0.527894`
- held-out `test` mean:
  - `mean_pearson_r = 0.0564316`
  - `mean_nrmse = 0.332844`
  - `mean_abs_error = 0.00856342`
  - `mean_sign_agreement = 0.468885`

Interpretation:

- the same-dataset B1269 pilot proved the path was live
- the held-out boundary proves current generalization is weak
- the next active work is targeted held-out optimization, not more
  same-dataset fitting

Second live substrate:

- staged first real Schaffer NWB:
  - `external/neural_measurements/schaffer2023_figshare/2022_01_08_fly1.nwb`
- added canonical exporter:
  - `src/analysis/schaffer_nwb_canonical_dataset.py`
  - `scripts/export_schaffer_nwb_canonical_dataset.py`
  - `tests/test_schaffer_nwb_canonical_dataset.py`
- exported first canonical Schaffer bundle:
  - `outputs/derived/schaffer2023_nwb_canonical/schaffer2023_nwb_canonical_summary.json`
  - result: `1` staged session, `6` interval trials, aligned ROI `Df/F`, ball
    motion, and `6`-channel behavioral state

Immediate next tasks from this state:

1. run first targeted held-out Aimon optimization sweep
2. expand Schaffer staging beyond one NWB file
3. keep downstream decoder and embodiment work subordinate

## March 29, 2026 first held-out Aimon sweep comparison and Schaffer score seam

The first three held-out Aimon sweep points are now real enough to change the
search strategy.

Evidence:

- `outputs/metrics/aimon_spontaneous_fit_train_to_test_v1/aimon_spontaneous_fit_summary.json`
- `outputs/metrics/aimon_spontaneous_fit_train_to_test_v2_basis16_ridge1e-2_noasym/aimon_spontaneous_fit_summary.json`
- `outputs/metrics/aimon_spontaneous_fit_train_to_test_v3_force2/aimon_spontaneous_fit_summary.json`
- `outputs/metrics/aimon_spontaneous_fit_variant_comparison.json`

Held-out `B1269_*` means:

- `v1` baseline:
  - `mean_pearson_r = 0.0564316`
  - `mean_nrmse = 0.332844`
  - `mean_abs_error = 0.00856342`
  - `mean_sign_agreement = 0.468885`
- `v2` reduced basis and no asymmetry basis:
  - `mean_pearson_r = 0.0122189`
  - `mean_nrmse = 0.330953`
  - `mean_abs_error = 0.00848732`
  - `mean_sign_agreement = 0.460513`
- `v3` doubled mechanosensory forcing:
  - `mean_pearson_r = 0.0620387`
  - `mean_nrmse = 0.311678`
  - `mean_abs_error = 0.00820677`
  - `mean_sign_agreement = 0.465980`

Interpretation:

- reduced projection capacity is not the main missing ingredient
- stronger mechanosensory forcing is the first change that improved held-out
  Aimon in a meaningful way
- the improvement is still small and does not solve the weak held-out forced
  walk slice
- next narrow Aimon axis is separating `force_contact_force` from
  `force_forward_speed`

Second substrate update:

- added `src/analysis/schaffer_parity_harness.py`
- added `tests/test_schaffer_parity_harness.py`
- focused validation passed: `6 passed`

Meaning:

- Schaffer is no longer only a canonical exporter
- there is now a direct matched-format score seam for staged NWB intervals

Active run at this state:

- `outputs/metrics/aimon_spontaneous_fit_train_to_test_v4_contact2_forward1`
- purpose: isolate contact-dominant mechanosensory forcing after the first
  useful force-2 result

## March 29, 2026 contact split negative result and first live Schaffer fit

The next Aimon split result is now known.

Artifact:

- `outputs/metrics/aimon_spontaneous_fit_train_to_test_v4_contact2_forward1/aimon_spontaneous_fit_summary.json`

Held-out `B1269_*` means:

- `mean_pearson_r = 0.0385278`
- `mean_nrmse = 0.329335`
- `mean_abs_error = 0.00853495`
- `mean_sign_agreement = 0.464421`

Interpretation:

- the useful `v3 force2` gain does not come from contact amplification alone
- contact-dominant forcing regressed against `v3`
- the decisive complementary Aimon run is now:
  - `outputs/metrics/aimon_spontaneous_fit_train_to_test_v5_forward2_contact1`

Second live substrate progress:

- added:
  - `src/analysis/schaffer_spontaneous_fit.py`
  - `scripts/run_schaffer_spontaneous_fit.py`
  - `tests/test_schaffer_spontaneous_fit.py`
- focused validation passed: `9 passed`
- first live Schaffer pilot now running at:
  - `outputs/metrics/schaffer_spontaneous_fit_pilot_trial000`

Immediate next reads after this state:

1. poll `v5 forward2/contact1`
2. poll `schaffer_spontaneous_fit_pilot_trial000`
3. update the Aimon variant comparison with `v4` and `v5`
4. decide whether forward-dominant forcing or a Schaffer-derived covariate path
   is the next highest-yield parity axis

## March 29, 2026 forward split result

The complementary Aimon forward split is now complete.

Artifact:

- `outputs/metrics/aimon_spontaneous_fit_train_to_test_v5_forward2_contact1/aimon_spontaneous_fit_summary.json`

Held-out `B1269_*` means:

- `mean_pearson_r = 0.0565402`
- `mean_nrmse = 0.315540`
- `mean_abs_error = 0.00824232`
- `mean_sign_agreement = 0.472305`

Current Aimon sweep interpretation:

- `v3 force2` remains best overall on correlation and error
- `v5 forward2/contact1` is nearly as good on error and best on held-out sign
  agreement
- `v4 contact2/forward1` was the clear negative result
- useful forcing contribution therefore leans more toward forward-speed drive
  than contact alone
- weak slice still concentrates in held-out `B1269_forced_walk`

Still active:

- `outputs/metrics/schaffer_spontaneous_fit_pilot_trial000`

## March 29, 2026 Schaffer expanded beyond one session

Schaffer is now materially more real as a parity substrate.

New staged files:

- `external/neural_measurements/schaffer2023_figshare/2018_08_24_fly3_run1.nwb`
- `external/neural_measurements/schaffer2023_figshare/2019_04_25_fly1.nwb`

Rebuilt canonical bundle:

- `outputs/derived/schaffer2023_nwb_canonical/schaffer2023_nwb_canonical_summary.json`
- current result:
  - `staged_session_count = 3`
  - `exported_session_count = 3`
  - `trial_count = 9`

Important constraint discovered:

- Schaffer sessions do not share one ROI output space
- current ROI counts:
  - `2018_08_24_fly3_run1.nwb`: `2170`
  - `2019_04_25_fly1.nwb`: `1006`
  - `2022_01_08_fly1.nwb`: `2`
- so honest fitting must stay within one session unless a cross-session ROI
  mapping is built

Code updates:

- `src/analysis/schaffer_spontaneous_fit.py`
  - explicit same-session trace-count guard
  - `fit_trial_id` support for within-session holdouts
- `tests/test_schaffer_spontaneous_fit.py`
  - focused validation now `11 passed`

First live Schaffer backend result:

- `outputs/metrics/schaffer_spontaneous_fit_pilot_trial000/schaffer_spontaneous_fit_summary.json`
- same-trial result:
  - `mean_pearson_r = 0.150623`
  - `mean_nrmse = 0.194200`
  - `mean_abs_error = 0.00181258`
  - `mean_sign_agreement = 0.563755`

Current active Schaffer run:

- `outputs/metrics/schaffer_spontaneous_fit_2022_train4_test2`
- fit:
  - `2022_01_08_fly1_trial_000`
  - `2022_01_08_fly1_trial_001`
  - `2022_01_08_fly1_trial_002`
  - `2022_01_08_fly1_trial_003`
- held out:
  - `2022_01_08_fly1_trial_004`
  - `2022_01_08_fly1_trial_005`

## March 30, 2026 spontaneous-state hard rule tightened

The repo's spontaneous-state acceptance bar is now explicit:

- the only acceptable spontaneous endogenous state is one that emerges from:
  - richer intrinsic cell dynamics
  - graded transmission
  - synaptic heterogeneity
  - neuromodulatory state

Consequences:

- the current structured background-drive / latent-drive spontaneous regime is
  still useful diagnostically
- but it is explicitly disqualified as the final spontaneous mechanism
- any parity progress achieved with that surrogate is diagnostic evidence only
- `T201` is mandatory replacement work, not optional cleanup

## March 30, 2026 exact endogenous replacement path defined

The exact path to the real goal is now fixed in:

- `docs/endogenous_spontaneous_replacement_plan.md`

Execution order:

1. freeze the current structured-drive spontaneous branch as diagnostic-only
2. implement a production backend with:
   - intrinsic cell dynamics
   - graded transmission
   - synaptic heterogeneity
   - neuromodulatory state
3. fit that backend against Aimon and Schaffer with a deliberately tiny
   readout so the backend, not the head, carries the score
4. only then return to decoder / Creamer / embodiment work

Tracked tasks:

- `T202` to `T207`

## March 30, 2026 systemic digital-real mismatch narrowed beyond simple eval bugs

Two stronger digital mismatches are now explicit.

1. **Session continuity mismatch**

- The exported Schaffer 2022 intervals are contiguous windows from one
  continuous session, not six independent trials:
  - `000 29.6815 -> 299.9877 s`
  - `001 299.9877 -> 599.9753 s`
  - `002 599.9753 -> 899.9630 s`
  - `003 899.9630 -> 1199.9507 s`
  - `004 1199.9507 -> 1499.9384 s`
  - `005 1499.9384 -> 1799.9260 s`
- The old Schaffer holdout harness reset the spontaneous brain between those
  contiguous intervals.
- This is now treated as a real digital mismatch, not a minor evaluator bug.
- The continuity-preserving replay seam is now in:
  - `src/analysis/schaffer_spontaneous_fit.py`
  - `scripts/run_schaffer_spontaneous_fit.py`
  - `tests/test_schaffer_spontaneous_fit.py`
- Corrected rerun path:
  - `outputs/metrics/schaffer_spontaneous_fit_2022_train4_test2_continuous`

2. **Imaging observation-model mismatch**

- Schaffer targets are `roi_dff_timeseries`.
- Aimon canonical traces are tagged `dff_like`.
- The old parity harness used an instantaneous linear projection from digital
  voltage features into imaging-space traces.
- That is now treated as a second systemic digital mismatch.
- The optional shared causal low-pass observation basis now exists in:
  - `src/analysis/imaging_observation_model.py`
- It is threaded into both parity lanes:
  - `src/analysis/aimon_spontaneous_fit.py`
  - `src/analysis/schaffer_spontaneous_fit.py`
  - `scripts/run_aimon_spontaneous_fit.py`
  - `scripts/run_schaffer_spontaneous_fit.py`
  - `tests/test_imaging_observation_model.py`
- Active held-out probe:
  - `outputs/metrics/aimon_spontaneous_fit_train_to_test_v7_force2_obs0p5`

Current read:

- the parity miss is no longer best described as "probably chemistry"
- the strongest concrete mismatches now under test are:
  - missing persistent hidden-state semantics
  - missing imaging measurement physics

Latest endogenous-backend state:

- The strict spontaneous-state rule is now hard: diagnostic surrogate drive is
  disqualified as a final spontaneous mechanism.
- Completed backend replacement slices:
  - grouped intrinsic-dynamics scaffolding and split diagnostic vs endogenous path
  - adaptation current and intrinsic filtered noise
  - graded release with `spiking` / `graded` / `mixed` modes
  - multi-class synaptic heterogeneity
  - internal arousal/exafference neuromodulatory states
- The first backend-first public-parity gate is `T207`: fit Aimon and Schaffer
  with a deliberately `tiny` readout so the backend, not a large head, carries
  the held-out score.

Important seam fixed on 2026-03-30:

- The first endogenous Aimon tiny-readout run was invalid.
- Root cause: `src/analysis/aimon_spontaneous_fit.py` instantiated
  `WholeBrainTorchBackend` without forwarding `brain.backend_dynamics`, so the
  supposed endogenous parity run was not actually using the new endogenous
  backend path.
- Fix:
  - `src/analysis/aimon_spontaneous_fit.py` now passes `backend_dynamics`
  - `tests/test_aimon_spontaneous_fit.py` asserts the endogenous path is
    selected under `configs/brain_endogenous_public_parity.yaml`
- The invalid live run was killed and relaunched correctly.

Current admissible live run:

- output root:
  - `outputs/metrics/schaffer_endogenous_tiny_v1_calcium`
- live artifacts already present:
  - `outputs/metrics/schaffer_endogenous_tiny_v1_calcium/fit_run_manifest.json`
  - `outputs/metrics/schaffer_endogenous_tiny_v1_calcium/fit_run_status.json`
- current live exec session:
  - `21983`

Latest Aimon temporal-structure read:

- First endogenous tiny backend result:
  - held-out `B1269_*` mean:
    - `pearson = -0.0754`
    - `nrmse = 0.2688`
    - `abs_error = 0.00750`
    - `sign = 0.4221`
- Calcium-memory endogenous rerun:
  - `outputs/metrics/aimon_endogenous_tiny_v2_calcium/aimon_spontaneous_fit_summary.json`
  - held-out `B1269_*` mean:
    - `pearson = -0.0516`
    - `nrmse = 0.2745`
    - `abs_error = 0.00761`
    - `sign = 0.4305`
- Interpretation:
  - intracellular slow memory modestly improved held-out correlation and sign
  - it did not solve the temporal-structure gap
  - next discriminant is Schaffer on the same calcium-memory backend

Latest harness fixes for temporal structure:

- Tiny-readout path is no longer arbitrary:
  - Aimon/Schaffer now choose bilateral family bases from the fit split by
    temporal energy, not by family ordering
  - selected bilateral families retain their observation-basis rows, not just
    raw rows
- Schaffer observation filtering is now session-continuous:
  - when `preserve_state_within_session` is enabled, feature rows are
    concatenated in absolute session time
  - causal low-pass observation basis is applied once on the stitched stream
  - rows are then split back into interval reports

Current admissible live run:

- output root:
  - `outputs/metrics/schaffer_endogenous_tiny_v1_calcium`
- live artifacts already present:
  - `outputs/metrics/schaffer_endogenous_tiny_v1_calcium/fit_run_manifest.json`
  - `outputs/metrics/schaffer_endogenous_tiny_v1_calcium/fit_run_status.json`
- current live exec session:
  - `7400`

## March 30, 2026 routed recurrent backend produced the first endogenous held-out Aimon improvement above zero correlation

Latest admissible endogenous Aimon progression on held-out `B1269_*`:

- `v1`:
  - `pearson = -0.0754`
  - `nrmse = 0.2688`
  - `abs_error = 0.00750`
  - `sign = 0.4221`
- `v2 calcium`:
  - `pearson = -0.0516`
  - `nrmse = 0.2745`
  - `abs_error = 0.00761`
  - `sign = 0.4305`
- `v3 routed`:
  - `pearson = +0.0065`
  - `nrmse = 0.2685`
  - `abs_error = 0.00750`
  - `sign = 0.4551`

Result:

- routed recurrent pathways are the first endogenous backend change that pushed
  held-out Aimon correlation back above zero
- the gain is still small, so temporal parity is not solved
- but this is the strongest evidence so far that the stubborn temporal miss is
  in the routed recurrent core, not just in readout amplitude scaling

Important implication:

- calcium-like intracellular memory helped, but only modestly
- the stronger win came after replacing pooled recurrent classes with:
  - spike-routed fast pathways
  - graded-release-routed slow pathways
  - separate slow modulatory routing
- that makes true routed slow-path dynamics the current highest-confidence
  no-hack mechanism direction

Next admissible run:

- rerun Schaffer on the routed backend with the corrected session-continuous
  observation harness
- recommended output root:
  - `outputs/metrics/schaffer_endogenous_tiny_v2_routed`

## March 31, 2026 routed Schaffer result landed and narrowed the remaining temporal miss

Routed Schaffer result:

- `outputs/metrics/schaffer_endogenous_tiny_v2_routed/schaffer_spontaneous_fit_summary.json`

Honest split using `fit_trial_ids = 000-003` and held-out trials `004-005`:

- routed fit mean:
  - `pearson = 0.1131`
  - `nrmse = 0.4517`
  - `abs_error = 0.004225`
  - `sign = 0.5581`
- routed held-out mean:
  - `pearson = -0.0140`
  - `nrmse = 1.2182`
  - `abs_error = 0.00986`
  - `sign = 0.4770`

Comparison with the earlier Schaffer holdout:

- prior held-out:
  - `pearson = -0.0011`
  - `nrmse = 1.3698`
  - `abs_error = 0.01098`
  - `sign = 0.5032`

Interpretation:

- routed recurrent pathways are a real backend gain for amplitude/error
- they did not fix temporal alignment on held-out late-session intervals
- Aimon and Schaffer now agree on the same pattern:
  - endogenous backend changes improve scale / magnitude first
  - temporal correlation remains the stubborn miss

Current strongest diagnosis:

- true routed slow pathways were necessary but not sufficient
- the remaining missing mechanism is likely richer distributed temporal state in
  the recurrent core, not just local intracellular memory and not just readout
  or observation modeling

## March 31, 2026 distributed temporal-state backend slice validated

New backend mechanism now added on top of routed recurrence:

- distributed slow context states inside the recurrent core for:
  - excitatory recurrence
  - inhibitory recurrence
  - modulatory recurrence
- group-specific time constants and gains live in:
  - `configs/brain_endogenous_public_parity.yaml`
- those states feed back only inside the brain backend through:
  - routed slow recurrent-class inputs
  - internal neuromodulatory state drive
  - backend state summaries

Important validation:

- focused backend/parity slice passed:
  - `python -m pytest tests/test_spontaneous_state_unit.py tests/test_brain_backend.py tests/test_aimon_spontaneous_fit.py -q`
  - `30 passed, 1 warning`

Important operational rule:

- full-session Schaffer parity reruns are too slow for normal iteration and are
  no longer admissible as the default retest loop
- future Schaffer retests must use explicit staged-trial subsets and record the
  subset in the run manifest

Next admissible result:

- held-out Aimon rerun on the new distributed-context backend
- then subset-only Schaffer retests if Aimon shows a real temporal gain

## March 31, 2026 distributed-context Aimon rerun regressed versus routed recurrence

The first distributed-context Aimon attempt failed numerically in the shared
reduced-projection fit:

- `outputs/metrics/aimon_endogenous_tiny_v4_context/fit_run_status.json`
- error:
  - `LinAlgError('SVD did not converge')`

That failure was not scientific evidence. The shared fitter was then hardened
with:

- finite-safe normalization
- SVD fallback to covariance eigendecomposition
- linear-solve fallback to `lstsq`
- finite-safe prediction path

The corrected rerun completed at:

- `outputs/metrics/aimon_endogenous_tiny_v4_context_retry/aimon_spontaneous_fit_summary.json`

Honest held-out `B1269_*` mean:

- `v1 endogenous tiny`:
  - `pearson = -0.0754`
  - `nrmse = 0.2688`
  - `abs_error = 0.00750`
  - `sign = 0.4221`
- `v2 calcium`:
  - `pearson = -0.0516`
  - `nrmse = 0.2745`
  - `abs_error = 0.00761`
  - `sign = 0.4305`
- `v3 routed`:
  - `pearson = +0.0065`
  - `nrmse = 0.2685`
  - `abs_error = 0.00750`
  - `sign = 0.4551`
- `v4 distributed context`:
  - `pearson = -0.0384`
  - `nrmse = 0.2716`
  - `abs_error = 0.00751`
  - `sign = 0.4385`

Interpretation:

- the current distributed-context formulation still beats `v1` and `v2`, so it
  is not useless
- but it regresses materially versus `v3 routed` on every held-out metric that
  matters
- current read:
  - routed recurrence remains the best endogenous temporal baseline
  - simple distributed context accumulation is not yet the right missing
    temporal mechanism

Operational rule remains:

- future Schaffer retests must use explicit staged-trial subsets only

## March 31, 2026 Aimon exact-parity mistake identified

Two important corrections now exist.

1. Scorer bug fixed:

- consolidated parity means had been counting traces with `n_samples = 0`
- the scorer now drops empty traces from means and reports:
  - `valid_trace_count`
  - `dropped_empty_trace_count`
  - `sample_count`
  - sample-weighted metrics

2. Bigger exact-parity mistake:

- the current Aimon canonical bundle is not exporting exact neurons
- it explicitly says:
  - modality: `region_component_timeseries`
  - `recorded_entity_id = region_component_*`
  - `flywire_mapping_key = null`
  - `flywire_mapping_confidence = none`
  - identity note: public region/component traces, not exact neurons

Implication:

- direct `B350 -> B1269` trace-index scoring is not admissible as exact 1:1
  neural parity evidence
- those cross-experiment Aimon results are still useful as coarse
  regime-transfer signals
- but exact temporal parity must prioritize:
  - within-experiment Aimon holdouts
  - same-session Schaffer subset retests

Current routed/context Aimon read after dropping empty traces:

- `v3 routed`, valid-only sample-weighted:
  - `pearson = 0.00084`
  - `nrmse = 0.28052`
  - `abs_error = 0.00777`
  - `sign = 0.46634`
- `v4 context`, valid-only sample-weighted:
  - `pearson = -0.04294`
  - `nrmse = 0.27987`
  - `abs_error = 0.00767`
  - `sign = 0.45034`

So the earlier broad conclusion survives:

- `v4` still does not beat `v3`
- but the current Aimon cross-experiment held-out KPI should no longer be read
  as an exact 1:1 parity target

## April 1, 2026 Aimon exact-parity loop moved to within-trial windowed assays

The exact-identity Aimon lane is now:

- within-experiment only
- windowed holdouts on the same trace identities
- short enough to iterate quickly

New runner and mechanism baseline:

- runner:
  - [run_aimon_windowed_fit.py](/G:/flysim/scripts/run_aimon_windowed_fit.py)
- explicit routed-only baseline config:
  - [brain_endogenous_public_parity_routed_only.yaml](/G:/flysim/configs/brain_endogenous_public_parity_routed_only.yaml)

Windowed-fit implementation details:

- trials are split into fixed windows while preserving:
  - trace identity
  - sliced timebase
  - sliced regressor values
- current exact-identity split:
  - `4` windows per trial
  - fit windows `0-1`
  - test windows `2-3`

Focused validation for the new path passed:

- `python -m pytest tests/test_aimon_spontaneous_fit.py tests/test_public_neural_measurement_harness.py -q`
- `13 passed, 1 warning`

First live exact-identity assays:

- [aimon_b350_spont_window_routed_v1](/G:/flysim/outputs/metrics/aimon_b350_spont_window_routed_v1)
- [aimon_b350_forced_window_routed_v1](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v1)

Those runs use:

- routed-only endogenous backend
- tiny readout
- `obs_tau = 0.5 s`
- spontaneous on `cuda:0`
- forced on `cuda:1`

Meaning:

- Aimon exact parity is no longer being iterated through invalid
  `B350 -> B1269` aggregate transfer
- the next real discriminator is whether the remaining temporal miss is worse in
  spontaneous or forced windows of the same experiment

## April 1, 2026 First exact-identity forced Aimon result

The first within-trial routed-only exact-identity result is now real:

- [aimon_b350_forced_window_routed_v1](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v1)

Setup:

- source trial: `B350_forced_walk`
- `4` windows total
- fit on windows `00-01`
- hold out windows `02-03`
- routed-only endogenous backend
- tiny readout
- `obs_tau = 0.5 s`

Result:

- train windows:
  - `win_00`: `pearson=0.6592`, `nrmse=0.1687`, `sign=0.7944`
  - `win_01`: `pearson=0.6950`, `nrmse=0.1538`, `sign=0.7883`
- held windows:
  - `win_02`: `pearson=-0.2139`, `nrmse=0.4988`, `sign=0.4419`
  - `win_03`: `pearson=0.0751`, `nrmse=0.5043`, `sign=0.5222`
- held mean:
  - `pearson=-0.0694`
  - `nrmse=0.5015`
  - `abs_error=0.00782`
  - `sign=0.4821`

Interpretation:

- the remaining temporal miss is real even when trace identity is exact
- the forced regime currently generalizes poorly across time within the same
  experiment

Operational follow-up:

- the original full `30 s` spontaneous `B350` window run was too expensive for
  the short loop and was interrupted
- it was replaced by a true short spontaneous assay that keeps only the first
  two `2.5 s` windows out of a `12`-window split:
  - [aimon_b350_spont_window_routed_v2_short](/G:/flysim/outputs/metrics/aimon_b350_spont_window_routed_v2_short)

## April 1, 2026 Second Aimon exact-parity harness bug: reset between contiguous windows

Another real evaluator problem was found after the first exact-identity forced
result.

Bug:

- the windowed Aimon runner was still resetting the brain between windows of the
  same source trial
- that is wrong for exact within-trial temporal parity, because those windows are
  contiguous segments of one recording

Fix:

- [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py)
  now has:
  - `TrialExecutionPlan`
  - `build_trial_execution_plan(...)`
  - `preserve_continuity_by_source_trial`
- [run_aimon_windowed_fit.py](/G:/flysim/scripts/run_aimon_windowed_fit.py)
  now requests continuity preservation for within-trial windowed fits
- contiguous windows from the same `source_trial_id` no longer reset the brain
  between segments

Implication:

- the first reset-based within-trial Aimon scores are only provisional
- the admissible exact-identity reruns are now:
  - [aimon_b350_forced_window_routed_v2_cont](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v2_cont)
  - [aimon_b350_spont_window_routed_v3_short_cont](/G:/flysim/outputs/metrics/aimon_b350_spont_window_routed_v3_short_cont)

## April 1, 2026 Corrected continuity-preserving B350 split

The first admissible within-trial forced-versus-spontaneous split is now on
disk.

Corrected `B350` held-out results:

- forced continuity holdout:
  - `pearson = 0.0848`
  - `nrmse = 0.9100`
  - `abs_error = 0.01438`
  - `sign = 0.5589`
- spontaneous continuity holdout:
  - `pearson = 0.1166`
  - `nrmse = 0.4182`
  - `abs_error = 0.00554`
  - `sign = 0.5474`

Meaning:

- spontaneous continuity is still imperfect, so the mismatch is not limited to
  one behavior regime
- but forced/exafferent windows are materially worse, especially on
  amplitude/baseline control
- continuity preservation recovered some forced timing/sign structure relative
  to the reset-based read, but it also exposed a stronger later-window state
  offset problem

Current leading diagnosis:

- the routed recurrent core plus continuity is still missing a mechanism for
  stable late forced-state regulation
- this looks more like forced/exafferent gain/baseline control than a pure
  "more temporal memory" problem

Next live discriminator:

- [aimon_b1269_forced_window_routed_v2_cont](/G:/flysim/outputs/metrics/aimon_b1269_forced_window_routed_v2_cont)

## April 1, 2026 Public-data answer on disembodiment / proprioception

The current exact Aimon parity lane is still too numb.

Current harness reality:

- [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py)
  constructs only a synthetic scalar body observation for public fitting:
  - fixed pose
  - fixed yaw
  - fixed yaw rate
  - scalar `forward_speed`
  - scalar `contact_force`
  - zero vision
- [encoder.py](/G:/flysim/src/bridge/encoder.py) then maps that only into
  coarse speed/contact/yaw pool rates

Public-data answer:

- enough public data exists for a grounded first-order reafferent /
  proprioceptive feedback lane
- not enough staged public data exists yet for full exact proprioceptor
  reconstruction

Best current public supports:

- Schaffer staged NWBs:
  - aligned treadmill ball motion
  - aligned behavioral-state matrices
- Dallmann 2025:
  - best public treadmill proprioceptive / joint-variable fit target
  - raw Dryad downloads still blocked locally

Meaning:

- disembodiment is a serious likely contributor to the remaining mismatch
- the next acceptable harness upgrade should add public-constrained body-derived
  feedback channels rather than invent a free-form feedback head

## April 1, 2026 First grounded body-feedback lane implemented

The first real public-constrained body-derived feedback upgrade is now in the
codebase.

What changed:

- [public_body_feedback.py](/G:/flysim/src/analysis/public_body_feedback.py)
  now includes explicit `exafferent_drive` in addition to speed, contact,
  acceleration, walk/stop, transition, and behavioral-state summaries.
- [interfaces.py](/G:/flysim/src/body/interfaces.py) now exposes
  `BodyObservation.exafferent_drive`.
- [encoder.py](/G:/flysim/src/bridge/encoder.py) now emits three grounded
  mechanosensory subgroup pools:
  - `mech_ce_bilateral`
  - `mech_f_bilateral`
  - `mech_dm_bilateral`
- [public_ids.py](/G:/flysim/src/brain/public_ids.py) maps those pools onto the
  already-preserved public `JON_CE`, `JON_F`, and `JON_DM` subgroup boundaries.
- The public input collapse path now preserves those subgroup pools without
  double-counting the legacy mechanosensory bucket.

Current status:

- Focused validation:
  - `58 passed, 1 warning`
- Immediate short evidence run:
  - [aimon_b350_forced_window_routed_v4_bodyfeedback](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v4_bodyfeedback)

Interpretation:

- The parity harness is no longer "just one scalar forward/contact cue".
- It is still only a first-order grounded reafferent lane, not full exact
  proprioceptor realism.
- The next read from the short `B350_forced_walk` rerun will tell us whether
  disembodiment was a large enough blocker to reduce the forced late-window
  amplitude / baseline drift with this change alone.

## April 1, 2026 Grounded body feedback improved scale but hurt timing

The first exact-identity forced-window rerun with grounded public body feedback
is now complete:

- [aimon_b350_forced_window_routed_v4_bodyfeedback](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v4_bodyfeedback/aimon_spontaneous_fit_summary.json)

Held-out comparison versus the previous routed continuity baseline:

- previous [v2 continuity baseline](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v2_cont/aimon_spontaneous_fit_summary.json):
  - `pearson = 0.0848`
  - `nrmse = 0.9100`
  - `abs_error = 0.01438`
  - `sign = 0.5589`
- new [v4 body-feedback rerun](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v4_bodyfeedback/aimon_spontaneous_fit_summary.json):
  - `pearson = -0.1967`
  - `nrmse = 0.7122`
  - `abs_error = 0.01187`
  - `sign = 0.4232`

Interpretation:

- grounded body feedback materially improved amplitude / baseline control in
  late forced windows
- but temporal alignment became worse
- therefore disembodiment was part of the problem, but the current public
  reafferent encoding or its routing into the recurrent core is still
  mechanistically wrong for timing under sustained forced drive

## April 1, 2026 Root-cause audit: most of the Aimon timing loop has been using wrong replay semantics

This is the biggest new finding from the timing investigation.

Verified code-level problems:

- In [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py),
  `_trial_regressor_values()` currently:
  - returns zeros for every `spontaneous_walk`
  - applies `abs()` and per-trial normalization to `forced_walk`
  - slices regressor files using stimulus `window_start/window_stop` values
    that are incompatible with the stored regressor-array lengths for `3/4`
    current Aimon trials

Current concrete outcomes:

- `B350_forced_walk` replay regressor is all ones
- `B350_spontaneous_walk` replay regressor is all zeros
- `B1269_forced_walk` only replays the last `58` samples stretched over the
  full `297`-sample trial

Implication:

- a large part of the Aimon temporal-mismatch loop has been contaminated before
  the brain even runs
- therefore recent Aimon timing failures cannot be interpreted purely as
  backend-dynamics failures

Other verified contributors:

- both parity YAMLs have duplicate top-level `encoder:` blocks, so the second
  silently overwrites the first and disables at least the intended
  `exafference_gain_hz` path
- the public parity scorer currently uses strict zero-lag pointwise correlation
  after resampling, which is too strict to be the only timing KPI for
  imaging-like traces
- the fit head still does not expose most of the slow endogenous backend state
  directly

Current conclusion:

- the continued timing mismatch has been partly real mechanism mismatch and
  partly evaluator / replay-semantics mismatch
- `T215` is now mandatory before drawing further temporal-mechanism conclusions

## April 1, 2026 Timing audit found real code and assumption faults

The continued timing mismatch is not explained only by "the backend is still too
simple." A focused audit found several higher-leverage timing faults:

- [aimon_canonical_dataset.py](/G:/flysim/src/analysis/aimon_canonical_dataset.py)
  still hard-codes a synthetic `100 Hz` timebase for Aimon exports.
- The Aimon paper methods report variable imaging speed by preparation and
  explicitly state that behavioral regressors were convolved with the GCaMP
  single-spike response and processed through the same `dF/F` pipeline as the
  fluorescence traces:
  - [PMC article]https://pmc.ncbi.nlm.nih.gov/articles/PMC10168698/
- [public_body_feedback.py](/G:/flysim/src/analysis/public_body_feedback.py)
  uses a centered finite difference, so public body-feedback derivatives are
  acausal for interior samples.
- Those derivatives are taken on normalized behavior regressors and can become
  very large, which then overdrives [encoder.py](/G:/flysim/src/bridge/encoder.py)
  acceleration channels.
- [brain_endogenous_public_parity_routed_only.yaml](/G:/flysim/configs/brain_endogenous_public_parity_routed_only.yaml)
  has a duplicate `encoder:` key, so the intended first block is silently
  overridden and `exafference_gain_hz` is lost.
- [public_ids.py](/G:/flysim/src/brain/public_ids.py) still assigns `JON_CE`,
  `JON_F`, and `JON_DM` by slicing one flat ID list rather than loading explicit
  subgroup membership.
- [pytorch_backend.py](/G:/flysim/src/brain/pytorch_backend.py) currently updates
  `modulatory_exafference_state` from internal modulatory activity rather than
  from exafferent sensory drive.

Current interpretation:

- recent tiny metric changes were not only a mechanism problem
- the timing path itself is still partially wrong
- further backend tuning is not cleanly interpretable until these timing-root
  faults are fixed

## April 1, 2026 Root-cause audit for the persistent timing mismatch

The current timing problem is not just "small gains" or "not enough backend
state".

The audit found several structural reasons that explain why timing has remained
stubborn:

- [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py)
  still reads out family-averaged voltage, not family spike / release /
  calcium observables, even though the public targets are calcium / `dff_like`
  traces.
- [imaging_observation_model.py](/G:/flysim/src/analysis/imaging_observation_model.py)
  only adds a post-hoc causal low-pass basis; it does not convert the observed
  family state into an interval-integrated calcium-like measurement.
- [brain_endogenous_public_parity_routed_only.yaml](/G:/flysim/configs/brain_endogenous_public_parity_routed_only.yaml)
  sets all distributed-context gains to zero, so the exact-identity routed-only
  Aimon loop was not actually testing the richer distributed temporal-state
  mechanism.
- Both parity configs contain duplicate top-level `encoder:` blocks, so the
  earlier block is silently overwritten at YAML load time. That means some
  intended body-feedback gains were not actually active in recent runs.
- [public_body_feedback.py](/G:/flysim/src/analysis/public_body_feedback.py)
  expands one mostly flat Aimon forced-walk regressor into many simultaneous
  tonic channels. That can help amplitude / baseline control, but it cannot add
  much temporal structure in held forced windows.
- The parity harness records end-of-interval feature snapshots instead of
  interval-integrated spike/release/calcium features, which is the wrong
  geometry for imaging targets.

The strongest current read is:

- the timing mismatch persists because the observation / parity harness is still
  structurally wrong in addition to the backend still being incomplete
- several recent exact-identity assays were not actually exercising the intended
  temporal mechanisms due config drift

## April 1, 2026 Timing audit: the mismatch is not just one backend problem

Root-cause audit now says the persistent timing failure is a mixture of
evaluation confounds, harness blind spots, and one real backend state-semantics
error.

Concrete findings:

- both public parity brain configs contain duplicate top-level `encoder:` keys,
  so the second one silently overwrites the first and disables intended gains
  like `exafference_gain_hz`
- the recent `v4 body-feedback` comparison against `v2 continuity` was not a
  clean A/B because `v4` ran with no observation low-pass basis while `v2` used
  `observation_taus_s = [0.5]`
- zero-lag scoring is overstating the remaining timing miss on Aimon:
  - `v2 B350_forced_walk win_02`: `0.215 -> 0.468` at best lag
  - `v2 B350_forced_walk win_03`: `-0.046 -> 0.419`
  - `v4 B350_forced_walk win_03`: `-0.159 -> 0.368`
- the parity fit head is still mostly voltage-only and does not directly expose
  graded release, intracellular calcium, distributed context, or modulatory
  state to the readout
- the first grounded body-feedback encoder double-counts transition drive and
  is therefore likely misphased
- inside the backend, `modulatory_arousal_state` and
  `modulatory_exafference_state` are currently driven by the same internal
  source and differ only by tau, so forced/exafferent regulation is not truly
  represented as a distinct state

Current interpretation:

- the continued timing mismatch is real
- but the repo has also been measuring it through partially invalid or
  confounded assays
- the next correct work is to remove those confounds and expose the slow
  endogenous state to the public fit before further backend mechanism claims

## April 1, 2026 repaired Aimon exact-identity baseline

The first short repaired exact-identity retest on `B350_forced_walk` completed
at
[aimon_b350_forced_window_routed_v5_replayfix](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v5_replayfix/aimon_spontaneous_fit_summary.json).

Important result:

- fixing replay semantics, aligned regressor export, parity-config overwrite,
  lag-aware temporal scoring, body-feedback phase handling, slow-state feature
  exposure, and distinct public exafference semantics changed the held-out
  baseline materially
- held `B350_forced_walk` windows improved from the old `v2 continuity`
  baseline:
  - `pearson 0.0848 -> 0.2315`
  - `nrmse 0.9100 -> 0.7011`
  - `abs_error 0.01438 -> 0.01027`
  - `sign 0.5589 -> 0.6040`
- lag-aware held timing is much stronger than zero-lag timing on the repaired
  path:
  - `lagged_pearson = 0.7311`
  - `lagged_sign = 0.8195`
  - `best_lag_seconds = 0.0254`

Interpretation:

- the old Aimon timing gap was substantially inflated by harness/evaluator
  errors
- backend temporal-state work still matters, but the corrected Aimon baseline
  is now much healthier than the earlier numbers implied
- next exact-identity checks must use the repaired path before drawing new
  backend conclusions

## April 1, 2026 short embodied demo on the repaired endogenous brain

The repaired endogenous routed brain is now wired into a real FlyGym embodied
demo config:

- [flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_endogenous_routed.yaml](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_endogenous_routed.yaml)

For an interactive `2.0 s` visualization artifact, a demo-only coarser
discretization variant was added:

- [flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_endogenous_routed_demo_fast.yaml](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_endogenous_routed_demo_fast.yaml)

That run completed at:

- [flygym-demo-20260401-221940](/G:/flysim/outputs/requested_2s_endogenous_routed_demo_fast/flygym-demo-20260401-221940)

Key read:

- full embodied FlyGym run completed `2.0 s` with realistic vision fast path,
  uv-grid splice, and the repaired endogenous routed backend
- output artifacts include:
  - [demo.mp4](/G:/flysim/outputs/requested_2s_endogenous_routed_demo_fast/flygym-demo-20260401-221940/demo.mp4)
  - [activation_side_by_side.mp4](/G:/flysim/outputs/requested_2s_endogenous_routed_demo_fast/flygym-demo-20260401-221940/activation_side_by_side.mp4)
  - [summary.json](/G:/flysim/outputs/requested_2s_endogenous_routed_demo_fast/flygym-demo-20260401-221940/summary.json)
- metrics:
  - `avg_forward_speed = 0.6911`
  - `path_length = 1.3753`
  - `net_displacement = 0.9778`
  - `trajectory_smoothness = 0.9030`
  - `wall_seconds = 215.8743`
  - `real_time_factor = 0.00926`

Interpretation:

- the repaired endogenous routed brain can now drive a real embodied 2 s FlyGym
  demo locally
- for user-visible demos, the parity-time integration settings are too slow and
  should not be used directly

## April 2, 2026 lawful `30 s` multi-target zoomed-out demo

The repo now has real multi-target ghost-fly scene support in the embodied
runtime:

- [flygym_runtime.py](/G:/flysim/src/body/flygym_runtime.py)

Important constraints preserved:

- no target metadata enters control
- no decoder-side visual bypass was added
- visual object interaction still flows through realistic vision, the
  retinotopic splice, the brain backend, and descending outputs only

The dedicated long-demo config is:

- [flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_brain_endogenous_routed_multitarget_demo_fast.yaml](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_brain_endogenous_routed_multitarget_demo_fast.yaml)

It uses:

- splice-only lawful visual target path
- one primary target plus `2` extra ghost targets
- a wide fixed overhead camera preset
- `capture_activation: false` to avoid paying activation-viz cost on long demos
- a demo scheduler of `brain.dt_ms = 2.0`, `body_timestep_s = 0.002`,
  `control_interval_s = 0.02`

Completed artifact:

- [flygym-demo-20260402-031051](/G:/flysim/outputs/requested_30s_endogenous_routed_multitarget_zoomout_demo/flygym-demo-20260402-031051)

Key read:

- full `30.0 s` run completed cleanly
- `avg_forward_speed = 0.8942`
- `path_length = 26.8092`
- `net_displacement = 9.1737`
- `trajectory_smoothness = 0.8734`
- `wall_seconds = 1965.92`
- `real_time_factor = 0.01526`
- `target_condition_bearing_reduction_rad = 1.3417`
- `target_condition_fixation_fraction_20deg = 0.1233`
- `target_condition_fixation_fraction_30deg = 0.2240`

Interpretation:

- the long lawful target branch is now stable enough for a real `30 s`
  multi-target artifact
- the zoomed-out camera requirement is met by the new fixed overhead preset
- target interaction quality is better than the earlier `2 s` splice-only run,
  but fixation is still partial rather than strong
## 2026-04-02 follow-camera `10 s` multi-target rerun clarification

- The corrected follow-camera activation rerun at [flygym-demo-20260402-100243](/G:/flysim/outputs/requested_10s_endogenous_routed_multitarget_followyaw_activation/flygym-demo-20260402-100243) did satisfy the requested simulated duration:
  - `sim_seconds = 10.000000000000009`
  - encoded [demo.mp4](/G:/flysim/outputs/requested_10s_endogenous_routed_multitarget_followyaw_activation/flygym-demo-20260402-100243/demo.mp4) duration `10.42 s`
  - encoded [activation_side_by_side.mp4](/G:/flysim/outputs/requested_10s_endogenous_routed_multitarget_followyaw_activation/flygym-demo-20260402-100243/activation_side_by_side.mp4) duration `10.42 s`
- The clip still feels too short / visually uninformative because the lawful controller is low-amplitude in this window:
  - `avg_forward_speed = 0.7499 mm/s`
  - `path_length = 7.4842 mm`
  - `net_displacement = 3.2084 mm`
- “Dead / dark” activations have two causes:
  - genuine inactivity in part of the monitored set:
    - `1 / 48` monitored population rows identically zero
    - `14 / 307` monitored rate rows identically zero
    - `29 / 307` monitored spike rows identically zero
  - renderer clipping in the whole-brain snapshot:
    - [activation_viz.py](/G:/flysim/src/visualization/activation_viz.py) colors voltage only over `[-55, -45] mV`
    - captured frames include large negative tails down to about `-26k mV`
    - about half of neurons per sampled frame fall below `-55 mV` and therefore render as black even when not literally silent

## 2026-04-02 active `10 s` parity multi-target camera mode

- The active full-parity multi-target `10 s` config remains [flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_brain_endogenous_routed_multitarget_followyaw_10s.yaml](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_brain_endogenous_routed_multitarget_followyaw_10s.yaml), but its active `runtime.camera_mode` is now `fixed_birdeye`, not `follow_yaw`.
- This was a camera-only correction. The enforced full-parity path remains:
  - `brain.dt_ms = 0.1`
  - `runtime.body_timestep_s = 0.0001`
  - `runtime.control_interval_s = 0.002`
  - `runtime.force_cpu_vision = true`
  - `visual_splice.enabled = true`
  - no coarse encoder visual drive

## 2026-04-02 generic fly object-interaction interpretation rule

- Generic target/object realism is not to be judged by permanent fixation or
  endless pursuit.
- `bearing_reduction` and `fixation_fraction_*` are diagnostic only. They are
  not the main biological target for ordinary fly-like behavior around moving
  objects.
- Main encounter criteria are:
  - transient lawful orientation or locomotor perturbation
  - minimum-distance regulation
  - low overlap / pass-through frequency
  - plausible pass-by, sidestep, inspection, or disengagement behavior
  - reacquisition after pass-by when it happens, without requiring indefinite
    lock-on
- Ongoing and future target-run analyses should therefore be framed around
  embodied encounter structure, not around "track forever" behavior.

## 2026-04-03 parity Creamer retry status

- Lawful treadmill visual-speed-control assays are now allowed on the full
  parity path. The earlier guard that rejected any
  `body.visual_speed_control.enabled` config was too broad and has been
  narrowed in [closed_loop.py](/G:/flysim/src/runtime/closed_loop.py).
- A reproducible shortest-possible parity Creamer runner now exists:
  - [creamer_parity_short.py](/G:/flysim/src/analysis/creamer_parity_short.py)
  - [run_creamer2018_parity_short.py](/G:/flysim/scripts/run_creamer2018_parity_short.py)
- Two synced shortest-parity probes were attempted:
  - `0.4 s` total: [run.jsonl](/G:/flysim/outputs/creamer2018_parity_short_synced/baseline/flygym-demo-20260403-092353/run.jsonl)
  - `0.2 s` total: [run.jsonl](/G:/flysim/outputs/creamer2018_parity_short_synced_0p05/baseline/flygym-demo-20260403-092721/run.jsonl)
- Neither completed a full matched baseline / `T4/T5`-ablated pair before wall
  time became unacceptable, so the retry is currently runtime-blocked rather
  than scientifically complete.
- Important partial read already obtained on the parity branch:
  - in the `0.4 s` probe, `baseline_a` reached true `0.0 mm/s` retinal slip
  - despite that, treadmill speed had already climbed back into the old
    high-speed attractor regime around `557 mm/s` by `sim_time = 0.128 s`
- So the parity endogenous brain does not automatically resolve the Creamer
  mismatch. The attractor-like treadmill operating point still appears before
  any scored front-to-back motion block is finished.

## 2026-04-03 active control-path correction

- The first parity-short Creamer retry was contaminated by an accidental active
  fallback onto the obsolete two-drive control path.
- That is now fixed at the source:
  - [decoder.py](/G:/flysim/src/bridge/decoder.py) defaults to
    `hybrid_multidrive`
  - [flygym_runtime.py](/G:/flysim/src/body/flygym_runtime.py) defaults to
    `hybrid_multidrive`
  - [closed_loop.py](/G:/flysim/src/runtime/closed_loop.py) full-parity
    validation explicitly requires both multidrive fields
  - the active routed parity configs and the Creamer parity-short builder now
    declare those fields explicitly
- Current interpretation:
  - the old parity-short treadmill evidence remains useful as a sign that the
    treadmill branch was badly wrong
  - but it is not clean evidence for the parity branch alone because the
    control path was not yet pinned to the current multidrive mode
  - the corrected shortest rerun is now the admissible parity-Creamer retry

## 2026-04-03 treadmill fix status

- A second concrete treadmill defect is now fixed in code:
  - treadmill ball speed is no longer written back into
    `BodyObservation.forward_speed` in [flygym_runtime.py](/G:/flysim/src/body/flygym_runtime.py)
  - the encoder in [encoder.py](/G:/flysim/src/bridge/encoder.py) now ignores
    treadmill ball speed for mechanosensory speed feedback and instead uses the
    explicitly separated `visual_speed_state.body_forward_speed_mm_s`
  - [visual_speed_control.py](/G:/flysim/src/body/visual_speed_control.py)
    now zeros treadmill joint `qvel` and `qacc` on reset
- Current confidence:
  - the direct runaway self-feedback path is removed
  - the full parity end-to-end confirmation is still pending because short
    parity treadmill reruns remain slow before first-cycle writeout

## 2026-04-03 parity-short treadmill warmup rule

- The shortest admissible full-parity Creamer assay is no longer allowed to
  start scoring immediately after treadmill spawn.
- [creamer_parity_short.py](/G:/flysim/src/analysis/creamer_parity_short.py)
  now hard-codes:
  - two synced warmup blocks before `baseline_a`
  - `treadmill_settle_time_s = 2 * block_duration_s`
- The purpose is specific:
  - do not let scored baseline evidence be contaminated by treadmill spawn
    transients
  - keep the assay short without pretending the first post-reset samples are
    mechanically meaningful
- [test_creamer_parity_short.py](/G:/flysim/tests/test_creamer_parity_short.py)
  now locks that structure so it cannot silently regress.

## 2026-04-03 treadmill settle mechanics tightened

- The treadmill settle logic now acts both before and after each physics step.
- [visual_speed_control.py](/G:/flysim/src/body/visual_speed_control.py)
  exposes `_zero_treadmill_joint_state()` and
  `stabilize_after_physics_step()`.
- [flygym_runtime.py](/G:/flysim/src/body/flygym_runtime.py) now calls that
  post-physics stabilizer inside the substep loop.
- Intended effect:
  - do not merely ignore measured speed during settle
  - also prevent the ball from accumulating contact-driven spin during the
    settle window itself
- Regression coverage now exists in
  [test_visual_speed_control.py](/G:/flysim/tests/test_visual_speed_control.py).

## 2026-04-03 treadmill settle validity is now explicit

- The treadmill metadata now explicitly says whether a sample is admissible:
  - `measurement_valid`
  - `in_settle_window`
  - `settle_remaining_s`
- The settle window boundary is now inclusive at the release sample:
  - [visual_speed_control.py](/G:/flysim/src/body/visual_speed_control.py)
    uses `<=` for the settle cutoff in both measurement and post-physics
    stabilizing paths
- There is now a real latest-runtime smoke in
  [test_closed_loop_smoke.py](/G:/flysim/tests/test_closed_loop_smoke.py)
  that resets the FlyGym treadmill path directly and verifies zero treadmill
  speed and zero virtual-track drift during settle under zero multidrive
  commands
- This means future treadmill analysis should not treat early samples as valid
  just because they exist in `run.jsonl`; `measurement_valid` must be true.

## 2026-04-03 parity treadmill review after the real 1.2 s Creamer run

- The current parity Creamer open-loop run is not failing because the brain or
  decoder is dead.
- Verified from
  [run.jsonl](/G:/flysim/outputs/creamer2018_parity_open_loop_1p2_treadmillfix_v1/baseline/flygym-demo-20260403-204123/run.jsonl):
  - motor commands are strong and nonzero after settle
  - monitored brain rates are active
  - but nested treadmill metadata stays pinned at:
    - `fly_forward_speed_mm_s_measured = 0.0`
    - `track_x_mm = 0.0`
    - `treadmill_forward_speed_mm_s = 0.0`
- So the remaining blocker is localized to the body/treadmill seam, not the
  neural output layer.
- Important correction:
  - top-level `contact_force` is not currently logged in
    [closed_loop.py](/G:/flysim/src/runtime/closed_loop.py)
  - any prior interpretation of top-level `None` as "no contact" was invalid
    because the field simply is not emitted there
- Additional setup bug:
  - [run_treadmill_hybrid_response_map.py](/G:/flysim/scripts/run_treadmill_hybrid_response_map.py)
    is stale on the current treadmill path because it still records
    `obs.forward_speed`
  - but treadmill mode now intentionally forces
    `BodyObservation.forward_speed = 0.0` in
    [flygym_runtime.py](/G:/flysim/src/body/flygym_runtime.py)
  - any future direct treadmill-response validation must read nested treadmill
    metadata instead
- Existing tests are insufficient:
  - they prove the treadmill stays quiet during settle
  - they do not prove the treadmill resumes nonzero ball motion after settle
  - that positive-response regression now needs to exist before future Creamer
    evidence is treated as admissible

## 2026-04-03 treadmill is not being zeroed every frame after settle

- This specific suspicion is now directly regression-tested.
- In [visual_speed_control.py](/G:/flysim/src/body/visual_speed_control.py),
  treadmill joint zeroing only happens when:
  - `curr_time <= _settle_until_s` inside `step()`
  - `curr_time <= _settle_until_s` inside `stabilize_after_physics_step()`
- [test_visual_speed_control.py](/G:/flysim/tests/test_visual_speed_control.py)
  now also proves the opposite case:
  - after settle, `step()` preserves the treadmill joint state and returns the
    measured speed
  - after settle, `stabilize_after_physics_step()` leaves the joint unchanged
- So the current pinned-zero parity treadmill bug is not explained by
  unconditional per-frame treadmill zeroing after settle.

## 2026-04-03 Creamer interpretation rule for the current parity locomotor stack

- The current parity FlyGym stack does not let the brain specify raw per-joint
  locomotion directly.
- The decoder emits final locomotor latents and signals, including:
  - `forward_signal`
  - `turn_signal`
  - `left/right_drive`
  - `left/right_amp`
  - `left/right_freq_scale`
  - `retraction_gain`
  - `stumbling_gain`
  - `reverse_gate`
- [ConnectomeTurningFly](/G:/flysim/src/body/connectome_turning_fly.py)
  then maps those latents into the canned hybrid locomotor controller that
  generates low-level joint and adhesion actions.
- Therefore, Creamer-style visual-response evidence on this stack should be
  scored primarily on visual modulation of those final locomotor outputs.
- Treadmill ball motion is still important, but it is a secondary embodied
  mechanics check, not the primary assay target while the tethered-ball seam is
  broken.
- The current treadmill failure is downstream of the decoder:
  - direct probes show strong leg-joint motion after settle
  - `treadmill_joint.qvel` stays `[0, 0, 0]`
  - a direct post-settle contact probe reported `ncon = 0`
  - so the active treadmill defect is consistent with the fly failing to make
    real treadmill contact / traction on the current tethered-ball setup

## 2026-04-03 Creamer sign rule

- The correct qualitative sign from Creamer 2018 was rechecked against the
  paper and should not be flipped again.
- Front-to-back translational motion is expected to slow walking, not increase
  it.
- Back-to-front translational motion also slows walking, with stronger slowing
  than front-to-back.
- Therefore the current parity baseline front-to-back command-side suppression
  is sign-consistent with Creamer, even though the treadmill ball seam remains
  broken.
- Future Creamer reports must separate:
  - sign correctness
  - effect magnitude
  - `T4/T5` ablation sensitivity
  - downstream treadmill mechanics status

## 2026-04-04 corrected parity Creamer pair result

- The corrected `2.0 s` parity open-loop pair completed at:
  - [pair summary](/G:/flysim/outputs/creamer2018_parity_open_loop_2p0_commandmetrics_v1/metrics/creamer2018_parity_open_loop_pair_summary.json)
  - [baseline summary](/G:/flysim/outputs/creamer2018_parity_open_loop_2p0_commandmetrics_v1/baseline/flygym-demo-20260403-223301/summary.json)
  - [ablated summary](/G:/flysim/outputs/creamer2018_parity_open_loop_2p0_commandmetrics_v1/t4t5_ablated/flygym-demo-20260403-230440/summary.json)
- Primary readout remains `command_forward_proxy`.
- Baseline front-to-back response:
  - `0.7100 -> 0.0886`
  - `fold_change 0.1248`
  - `delta -0.6214`
- `T4/T5`-ablated front-to-back response:
  - `0.6477 -> 0.1176`
  - `fold_change 0.1816`
  - `delta -0.5301`
- Therefore:
  - front-to-back suppression is real on the command side
  - the sign is consistent with Creamer
  - `T4/T5` ablation weakens the effect modestly but does not abolish it
- Treadmill ball motion remains pinned at zero in both conditions, so treadmill
  mechanics are still a separate downstream failure.
