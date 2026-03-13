# Context Handoff for OpenFly

Last updated: 2026-03-11

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

## Mission and standards that govern this repo

The repo was built under a strict reproduction brief:

- reproduce the public-equivalent embodied fly stack as closely as public
  artifacts allow,
- do not pretend private Eon glue is available if it is not,
- measure parity using observable outputs,
- keep everything local, scripted, benchmarked, and testable,
- maintain explicit task tracking and a dated lab notebook,
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
