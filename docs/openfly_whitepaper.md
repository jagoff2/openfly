# OpenFly: Reconstructing a Public-Equivalent Embodied Drosophila Brain-Body Stack from Open Artifacts

Author: Codex
Date: 2026-03-12

## Abstract

This whitepaper consolidates the engineering and scientific findings from `openfly`, a local reproduction effort targeting the public-equivalent embodied fruit-fly simulation stack implied by the public Eon demo context. The goal was not to claim access to private glue or unpublished parameters. The goal was to determine how far the public artifacts can be pushed on one workstation: Windows 11, WSL2, dual RTX 5060 Ti 16 GB GPUs, and 192 GB RAM.

The current stack combines four public subsystems: a whole-brain recurrent model derived from the FlyWire connectome, the FlyGym and NeuroMechFly v2 embodied simulation stack, FlyGym realistic vision with FlyVis-derived neural activity, and new in-repo bridge code that maintains persistent closed-loop control online rather than as offline batch analyses. The main result is that a realistic-vision, real-body, real-whole-brain closed loop now runs locally and produces brain-driven, visually driven embodied locomotion under matched controls.

The strongest current branch is `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated.yaml`. In the current `2 s` logged-target validation run, this branch yields `avg_forward_speed = 4.9241`, `net_displacement = 5.7583`, `displacement_efficiency = 0.5853`, `corr(right_drive - left_drive, target_bearing) = 0.8810`, and `steer_sign_match_rate = 0.8878`, while the matched `zero_brain` control still yields `nonzero_command_cycles = 0` and `net_displacement = 0.0118`. A no-target control still produces substantial locomotion, which means the branch is visually driven but not purely target-driven: optic flow and scene structure also contribute.

The project also produced negative results that matter. A minimal public-anchor bridge built from bilateral `LC4` and `JON` pools plus a tiny descending-neuron bottleneck does not produce useful locomotion once decoder-side and body-side fallbacks are removed. That failure is not explained by a dead backend. Instead, body-free splice experiments showed that the original scalar bridge destroyed lateralized visual structure already present in FlyVis, and that the output bottleneck was also too narrow. A calibrated splice using exact shared FlyVis/FlyWire `cell_type + side + bin` groups can preserve grouped boundary activity strongly and launch the correct downstream turn sign at `100 ms`, but downstream sign drifts by `500 ms`, and exact column alignment remains unresolved. A later semantic-VNC branch built from real MANC `exit_nerve` structure and a FlyWire semantic bridge proved that monitor-space alignment can be solved, but it still failed target-tracking parity and is now frozen as a negative result rather than promoted.

In addition to locomotion, the repo now includes grounded brain-only reproductions of the feeding and grooming tasks from Shiu et al. Feeding probes recover clear `MN9` responses to unilateral sugar GRN input, and grooming probes recover `aBN1` responses in short windows and weaker `aDN1_right` responses in longer windows. These tasks are now ready for later embodiment work. The repo also now includes a synchronized activation visualization of the best embodied branch, showing the embodied run, whole-brain point cloud, FlyVis nodes, monitored decoder populations, and controller channels side by side. The repo therefore meets the public-equivalent acceptance gate in `AGENTS.MD`, but final parity remains partial because the exact private Eon glue is unavailable, GPU FlyVis remains blocked in WSL by public `sm_120` wheel support, and the current motor interface is still a descending-population-to-two-drive abstraction rather than a full biological motor pathway.

## 1. Introduction

The public Eon fly demo context implies a demanding systems problem: a whole-brain connectome model, realistic vision, embodied physics, and persistent online control must all operate together in closed loop. Publicly, the relevant pieces exist, but they do not arrive as a turnkey, unified runtime. The principal open components are the FlyWire-derived computational brain model and associated `fly-brain` codebase, the FlyWire whole-brain connectome and annotation releases, the FlyGym and NeuroMechFly v2 embodied simulator, and FlyGym's realistic-vision path. What is not public is the exact integration glue, task-specific sensory and motor mapping, parameterization, and any proprietary control heuristics that may have been used in internal demos.

This project was therefore organized as a public-equivalent reconstruction rather than an attempt to claim private parity. The central question was: what can be reproduced honestly from public artifacts alone, on this machine, with explicit evidence at each step? The answer required both positive and negative results. Positive results establish what is now working. Negative results identify which apparently reasonable bridges fail, and why.

The work proceeded in phases mandated by `AGENTS.MD`: initial scouting, environment creation, standalone benchmarking, architecture design, bridge implementation, realistic-vision integration, optimization, parity demos, and hardening. At every step, the repo maintained an explicit task tracker in `TASKS.md` and a dated lab notebook in `PROGRESS_LOG.md`. This whitepaper synthesizes that engineering record into a single technical narrative.

## 2. Scope, Hardware, and Public Components

### 2.1 Hardware target

All work targeted one workstation:

| Component | Value |
| --- | --- |
| Host OS | Windows 11 |
| Linux runtime | WSL2, Ubuntu 24.04 |
| GPUs | 2x NVIDIA RTX 5060 Ti 16 GB |
| System RAM | 192 GB |
| Driver | 581.29 |

### 2.2 Public components used

| Subsystem | Public source | Role in this project |
| --- | --- | --- |
| Whole-brain model | `eonsystemspbc/fly-brain`; Shiu et al. computational brain model | recurrent brain backend and task notebooks |
| Whole-brain connectome | FlyWire adult female brain releases | neuron graph, synapse-weight proxy, annotations |
| Embodied body sim | `NeLy-EPFL/flygym` / NeuroMechFly v2 | body physics, realistic vision, environment |
| Realistic vision | FlyGym realistic vision + FlyVis path | neural visual frontend |

### 2.3 Public scope versus inferred glue

The whole-brain backend, body simulation, and realistic vision are public. The closed-loop online bridge was not available as a finished public subsystem and had to be implemented in-repo. That bridge includes both public-grounded and inferred components. Public-grounded components include use of the public FlyWire graph, direct notebook-derived task IDs for feeding and grooming, public descending and efferent annotations for expanded readouts, and exact shared `cell_type + side` overlap groups grounded by the official FlyWire annotation supplement. Inferred components include retinotopic binning between FlyVis and FlyWire groups, signed current scaling at the splice boundary, and the current descending-population decoder that reduces rich descending activity into `left_drive` and `right_drive`.
## 3. System Architecture

### 3.1 High-level architecture

The current closed-loop production path has five persistent subsystems:

1. `FlyGymRealisticVisionRuntime` provides a persistent FlyGym world, a body state, and visual-system activity from the realistic-vision path.
2. `VisualSplice` converts raw FlyVis activity into direct current injected into exact shared FlyWire groups.
3. `WholeBrainTorchBackend` maintains a persistent recurrent whole-brain state and steps the FlyWire-derived graph online.
4. `MotorDecoder` reads out selected descending and efferent populations and converts them into a compact body command.
5. `ClosedLoopRunner` synchronizes stepping, logging, metrics, and artifact generation.

Implementation lives in:

- `src/body/flygym_runtime.py`
- `src/bridge/visual_splice.py`
- `src/brain/pytorch_backend.py`
- `src/bridge/decoder.py`
- `src/runtime/closed_loop.py`

### 3.2 Brain backend

The current production backend is a persistent Torch implementation over a public FlyWire-derived graph:

- neurons: `138,639`
- weighted directed edges: `15,091,983`
- weight source: `Excitatory x Connectivity` from `external/fly-brain/data/2025_Connectivity_783.parquet`

The graph is not unweighted. It already contains a sparse signed structural weight matrix. What remains simplified is not whether weights exist, but how much physiology is collapsed into global parameters. The current public backend uses shared membrane and synapse time constants, shared thresholding, shared refractory behavior, and a global synaptic scale.

### 3.3 Body and realistic vision

The body runtime uses FlyGym and NeuroMechFly v2 for embodied physics and FlyGym's realistic-vision path for neural visual activity rather than trivial RGB frames. The current strongest embodied branch uses:

- real FlyGym body
- real FlyVis-derived neural visual activity
- real whole-brain recurrent stepping
- no decoder idle-drive fallback
- no body-side hidden locomotion fallback
- no prosthetic `P9` locomotor-context injection

### 3.4 Logging, controls, and artifacts

The runtime emits timestamped demo videos, JSONL logs with per-cycle state, metrics CSVs, trajectory and command plots, benchmark CSVs and plots, and profiler artifacts. Later iterations also added explicit target-state logging so that target-bearing analysis no longer depends on reconstructing `MovingFlyArena` kinematics from public formulas.

## 4. Methods

### 4.1 Environment strategy

The environment strategy had to be split. The modern FlyGym stack and the secondary Brian2 benchmark stack were not cleanly co-installable in one environment. The project therefore created a production environment for FlyGym, realistic vision, and the Torch brain backend, and a separate Brian2 CPU benchmark environment for secondary backend comparison.

Bootstrap and validation scripts were created early:

- `scripts/bootstrap_wsl.sh`
- `scripts/bootstrap_env.sh`
- `scripts/check_cuda.sh`
- `scripts/check_mujoco.sh`

### 4.2 Benchmarking methodology

Each benchmark records `wall_seconds`, `sim_seconds`, `real_time_factor`, backend, device, config, and commit hash when available. Standalone runners were created for brain-only, body-only, realistic vision, and full stack workloads.

### 4.3 Initial public-anchor bridge

The first bridge encoded visual and mechanosensory evidence into bilateral public input pools derived from checked public notebook IDs and decoded a very small set of descending readouts (`P9`, `oDN1`, `DNa01`, `DNa02`, `MDN`) into a two-scalar body command. This bridge had one engineering virtue: every input and output handle was easy to explain. It also had two critical flaws:

1. it collapsed rich visual structure into a few scalar pools
2. it compressed output through a readout set that was too narrow

That initial bridge was useful only because it failed clearly once hidden fallbacks were removed.

### 4.4 Fast realistic-vision path

Performance profiling showed that the realistic-vision runtime, not the in-repo bridge, dominated runtime. The initial path spent disproportionate time in the `LayerActivity` and `datamate` access path. A fast path was therefore added that consumes raw `nn_activities_arr` directly, caches cell-type indices, and avoids repeated construction of higher-overhead activity objects for the control-relevant path. That new path was not accepted until exact control-path equivalence was proven for the repo's actual control computations.

### 4.5 Body-free splice program

The decisive methodological change was to remove the body from the inner discovery loop and work directly on the FlyVis-to-whole-brain splice. This produced a much faster iteration cycle and a cleaner causal question: same visual stimulus in, compare teacher (FlyVis) and student (whole-brain overlap groups), determine whether left/right structure is preserved, and determine whether downstream motor-sign predictions emerge.

The splice program advanced through these steps:

1. exact shared `cell_type + side` overlap grounded by the official FlyWire annotation supplement
2. signed boundary injection instead of positive-only rate drive
3. coarse spatial binning to preserve more retinotopic structure
4. voltage and conductance readouts in addition to spike-rate summaries
5. calibration of current scale and spatial bins against boundary preservation and downstream sign
6. deeper relay and longer-window probes

### 4.6 Embodied descending-readout expansion

Once the splice was good enough to launch the correct downstream sign at `100 ms`, the bottleneck shifted to the output side. An invalid relay-to-body shortcut through optic-lobe populations was explicitly rejected. Instead, a strict descending-only readout expansion was mined from public annotations and the connectome using anatomical constraints:

- `super_class == descending`
- `flow == efferent`
- DN/oDN/MDN-like labels

The selected supplemental groups were:

- forward-biased: `DNp103`, `DNp06`, `DNp18`, `DNp35`
- turn-biased: `DNpe056`, `DNp71`, `DNpe040`

### 4.7 Controls and falsification logic

The current strongest claims rely on matched controls:

- `zero_brain` control: proves there is no hidden body fallback
- no-target control: proves that the target specifically modulates behavior beyond the rest of the visual scene
- controlled left/right target conditions: test whether short side-isolated pursuit behavior mirrors correctly

Earlier hack branches are now treated only as diagnostics, not as success targets.
## 5. Results

### 5.1 Module-level validation and performance

The repo satisfies the module-level acceptance gate: brain-only, body-only, realistic-vision, and full closed-loop benchmarks all run locally and save artifacts.

Measured performance:

| Workload | Device | Sim time | Wall time | Real-time factor |
| --- | --- | ---: | ---: | ---: |
| Brain only, Torch | `cuda:0` | `0.100 s` | `0.923 s` | `0.1083x` |
| Brain only, Brian2 CPU | `cpu` | `0.100 s` | `10.852 s` | `0.0092x` |
| Body only | `cpu` | `0.020 s` | `0.285 s` | `0.0701x` |
| Realistic vision only | `cpu` | `0.020 s` | `22.644 s` | `0.000883x` |
| Full legacy closed loop | `cpu` | `0.098 s` | `125.350 s` | `0.000782x` |

Two points follow immediately. First, the realistic-vision path dominates runtime. Second, the validated WSL production path remains CPU-only for FlyVis because public `cu126` wheels still do not support RTX 5060 Ti `sm_120`.

### 5.2 Exact fast-path equivalence

The fast realistic-vision path was proven exact for the control-relevant computations in this repo. For identical `nn_activities_arr` and connectome metadata, the legacy and fast paths yielded exact equality of extracted features, sensor pool rates, sensor metadata, downstream motor-rate summaries, and the final decoded body command. Evidence is in `outputs/metrics/vision_fast_equivalence.json` and `docs/vision_fast_equivalence.md`.

### 5.3 The strict minimal public bridge failed for structural reasons

Once decoder idle-drive fallback, fake left/right public splits, and hidden body locomotion fallback were removed, the strict public-anchor path did not produce meaningful locomotion. It produced sparse twitching or no useful monitored motor output under short real diagnostics. The motor-path audit showed that the bilateral public sensory inputs were weak for the monitored DN readouts, while direct `P9` stimulation remained a strong positive control.

### 5.4 The original visual bridge destroyed lateralized structure already present in FlyVis

Crafted visual probes showed that several strong left/right visual families were already present in the data stream being computed by FlyVis. The problem was not that the bridge omitted the relevant visual families. The problem was that it averaged away their signed and lateralized structure before the whole-brain backend saw them.

### 5.5 A grounded body-free splice is possible

Using the official FlyWire annotation supplement, the overlap between FlyVis and the whole-brain graph could be grounded by exact shared `cell_type + side`, not by fabricated hemisphere splits. The repo found:

- `49` exact shared visual cell types
- `98` type+side groups
- `392` groups after splitting into `4` coarse spatial bins

The key calibrated result was:

- `4` spatial bins
- signed current injection
- `max_abs_current = 120`

At that point, mean voltage-based boundary agreement was strong:

- mean voltage group correlation: `0.8709`
- mean voltage side-difference correlation: `0.8079`

and the correct downstream turn-sign flip appeared at `100 ms`:

- left-dark: `turn_right - turn_left = -10`
- right-dark: `turn_right - turn_left = +10`

### 5.6 The splice is not yet final

Two blockers remained after splice calibration.

First, downstream sign drifted by `500 ms`. The `100 ms` launch was correct, but longer windows failed:

- `100 ms` hold: correct sign
- `500 ms` hold: wrong sign
- `500 ms` with only a `25 ms` pulse: still wrong sign

Second, better two-dimensional boundary fit did not automatically yield better downstream sign. The `uv_grid` splice improved voltage-side agreement, but no tested orientation-only variant restored the correct left-versus-right downstream sign.

### 5.7 Output bottleneck was also fundamental

A real `2 s` embodied run using the new splice but the old tiny motor readout remained behaviorally poor. The splice was active on `999/1000` cycles and generated `982/1000` nonzero commands, but maximum decoded drives were only about `0.14`, net displacement was only `0.113`, and displacement efficiency was only `0.0519`.

The failure was therefore not that the brain was silent. It was that the current output abstraction was too small and too weak for the FlyGym locomotion controller.

### 5.8 Descending-only expanded readout produced the first convincing embodied traversal without locomotion prosthetics

The descending-only expanded readout transformed the embodied result.

Old splice-only readout:

- `net_displacement = 0.1132`
- `displacement_efficiency = 0.0519`

Descending-only expanded readout:

- `avg_forward_speed = 4.5638`
- `path_length = 9.1185`
- `net_displacement = 5.6330`
- `displacement_efficiency = 0.6178`

This was the first embodied branch in the repo to produce meaningful traversal with no optic-lobe-as-motor shortcut, no `P9` prosthetic locomotor-context mode, no decoder idle-drive fallback, and no body-side hidden locomotion fallback.
### 5.9 The strongest current embodied claim is supported by matched controls

The strongest current branch is now validated by matched controls with explicit target-state logging.

Target + real brain:

- `avg_forward_speed = 4.9241`
- `net_displacement = 5.7583`
- `displacement_efficiency = 0.5853`
- `nonzero_command_cycles = 993`

No target + real brain:

- `avg_forward_speed = 3.9070`
- `net_displacement = 5.2903`
- `displacement_efficiency = 0.6777`

Target + zero brain:

- `avg_forward_speed = 0.1847`
- `net_displacement = 0.0118`
- `nonzero_command_cycles = 0`

Three conclusions are justified.

First, there is no hidden locomotion fallback. The zero-brain control stays near zero and produces zero commands.

Second, the branch is visually driven. It moves with the real brain and the realistic visual scene.

Third, the target modulates behavior specifically. Compared with the no-target run, the target run increases:

- forward speed by about `26.0%`
- mean total drive by about `12.0%`
- mean steering asymmetry by about `121.4%`

In addition, steering tracks directly logged target bearing:

- `corr(right_drive - left_drive, target_bearing) = 0.8810`
- steer-sign match rate `= 0.8878`

and forward drive increases as the target becomes more frontal:

- `corr(total_drive, target_frontalness) = 0.4634`
- `corr(forward_speed, target_frontalness) = 0.1298`

### 5.10 What remains unresolved in locomotion

The no-target run still produces substantial locomotion. That is consistent with the visual scene, floor texture, and self-motion driving the system via optic flow. This means the current branch is not a pure target-pursuit-only controller. It is better understood as a visually driven locomotor policy whose steering and drive are modulated by the target.

The short isolated left/right target conditions are still mixed. Controlled left and right placements now work correctly and target bearings are logged directly, but the short `1 s` side-isolated conditions do not yet show a clean mirrored reflex.

### 5.11 Feeding and grooming brain tasks were added and reproduced as grounded brain probes

The repo now includes grounded reproductions of the Shiu et al. feeding and grooming tasks using public notebook IDs.

Feeding, `100 ms` sweep:

- `sugar_right @ 180 Hz -> mn9_left = 60 Hz, mn9_right = 40 Hz`
- `sugar_left` remained silent in the same short sweep

Grooming, `100 ms` sweep:

- `JON_CE` and `JON_all` activate `aBN1` up to `20 Hz`
- `aDN1` is silent in the same short window

Grooming, `500 ms` sweep:

- `jon_all @ 220 Hz -> aDN1_right = 6 Hz, aBN1 = 28 Hz`

These are biologically cleaner than the earlier locomotion prosthetic experiments because they use published sensory and output neuron groups from the public task notebooks. They are not yet embodied.

### 5.12 A real semantic-VNC structural decoder was built, but it failed as a parity branch

The repo did not stop at small sampled descending populations. It also compiled a real MANC-derived `exit_nerve` structural spec, resolved the raw ID-space mismatch with a FlyWire semantic bridge, and ran that path through the embodied closed loop.

This branch proved several things:

- the raw MANC-versus-FlyWire ID mismatch was a real blocker
- the semantic bridge solved monitor-space alignment rather than hiding it
- the first bridged decoder was not silent
- the first bridged decoder also had a real saturation bug

After the semantic bridge, the real decoder requested `685` IDs and matched `685`. The first short bridged embodied run was therefore no longer silent, but it saturated immediately. Later normalization in `src/vnc/spec_decoder.py` removed that obvious decoder failure, and later follow-camera support removed the separate framing problem.

The corrected `2.0 s` semantic-VNC rerun reached:

- `avg_forward_speed = 4.7635`
- `net_displacement = 7.0699`
- `displacement_efficiency = 0.7428`
- `stable = 1.0`

Those numbers matter because they show the branch was no longer failing for trivial reasons such as dead monitor alignment, raw drive clipping, or a broken camera. Even so, scene-level review showed that the branch still did not track the target credibly enough to count as parity.

The honest conclusion is therefore negative: structural semantic reachability was enough to build a working locomotor branch, but not enough to recover target-directed behavior. The semantic-VNC branch is now frozen as a failed parity branch rather than left in an ambiguous "needs tuning" state.

### 5.13 The current best branch now has a synchronized activation visualization

The repo now includes a dedicated visualization artifact for the monitored-only extension of the strongest current embodied branch. This artifact is not a new parity claim. It is a visibility artifact that shows, in one synchronized view, what the current best branch is doing at the embodied, whole-brain, FlyVis, decoder, and controller layers.

The captured run records:

- `200` synchronized frames
- `138,639` local FlyWire brain points
- `45,669` FlyVis nodes
- `16` monitored decoder labels
- `8` controller channels

and the monitored visualization run itself remained behaviorally consistent with the best branch:

- `avg_forward_speed = 4.8348`
- `net_displacement = 6.2200`
- `displacement_efficiency = 0.6439`
- `stable = 1.0`

This matters for two reasons. First, it gives the repo a direct inspection tool for activation flow rather than relying only on scalar summaries. Second, it makes the current state of the system legible: where visual activity lives, how monitored descending groups evolve across time, and what the controller channels are doing on the same cycles as the body and target.

## 6. Interpretation

### 6.1 What is now proven

The project now supports these claims with direct evidence:

1. A realistic-vision-enabled, whole-brain, embodied closed loop runs locally on this machine.
2. The strongest current embodied branch does not depend on hidden locomotion fallback.
3. The strongest current embodied branch is brain-driven.
4. The strongest current embodied branch is visually driven.
5. A moving target measurably modulates steering and forward drive.
6. The public whole-brain model can reproduce grounded non-locomotion sensorimotor brain tasks for feeding and grooming.

### 6.2 What is not yet proven

The project does not yet prove:

1. that the current visual splice is the final endogenous biological interface
2. that the current descending-population decoder is the true natural locomotor code
3. that the current system implements a full neck-connective, VNC, and muscle pathway
4. that short isolated left/right target stimuli produce a clean mirrored pursuit reflex
5. that a structurally grounded semantic-VNC decoder is already sufficient for target pursuit
6. exact parity with any private Eon integration stack

### 6.3 Why the discovery process mattered

The most important discoveries in this project were not only positive results. They were falsifications:

- simply connecting bilateral public sensory anchors to a tiny DN bottleneck does not work
- hiding locomotion behind decoder or body fallback creates misleading demo behavior
- optic-lobe relay cells must not be treated as motor output
- the visual bridge was too lossy even before the whole-brain backend saw the data
- improving the input side alone is not enough; the output bottleneck is also structural

## 7. Limitations

The current limitations are precise.

First, the validated WSL production path is CPU-only for FlyVis because public `sm_120` wheel support is still absent. This constrains runtime severely.

Second, the current motor interface remains compressed. The decoder maps descending and efferent population activity into `left_drive` and `right_drive`, and FlyGym then transforms those into gait. This is materially better than the older hacks, but it is still not a full biological motor pathway.

Third, the whole-brain backend already has structural edge weights, but much of the physiology remains globally parameterized. Better functional-weight estimation or richer cell-class physiology could change longer-window dynamics.

Fourth, the visual splice is still an inferred overlap splice. It is grounded more strongly than the original scalar bridge, but exact FlyVis-to-FlyWire neuron identity and fine retinotopic column alignment remain unresolved.

Fifth, the current strongest locomotion result is not pure target pursuit. The rest of the visual scene still drives locomotion substantially.

Sixth, the broader semantic-VNC replacement program is still incomplete. A real MANC-derived semantic-VNC branch now exists and is no longer blocked by raw ID mismatch, silent decoding, or off-screen framing, but it still fails target-tracking parity. That means broader structural coverage alone is not yet enough to replace the current sampled descending decoder.

## 8. Comparison With The Subsequent Eon Embodiment Update

After the work in this repo, Eon published a new embodiment update:

- `https://eon.systems/updates/embodied-brain-emulation`

The post is important because it narrows what their current public embodiment appears to be.

### 8.1 What the new Eon update now makes explicit

The post says, in substance:

- they are using the Shiu-style simplified LIF whole-brain model rather than disclosing a radically different full biological brain core
- they run a visual-system model and feed those activations into the brain model
- they synchronize brain and body every `15 ms`
- they use slightly modified existing NeuroMechFly controllers trained by imitation learning for walking
- they do not know the exact mapping from brain outputs to locomotion-controller inputs
- their current visual input is not yet significantly influencing the embodied behavior

This matters because it weakens any theory that the public demo must already have depended on a fully solved, biologically faithful, end-to-end controller hidden behind the scenes.

### 8.2 What the Eon update confirms from this repo

The new post largely confirms the central diagnosis reached here:

1. The hard problem is the interface.
- The unresolved system is the splice between vision, brain, and embodied control.
- That matches the findings in `docs/splice_probe_results.md`.

2. Existing locomotion controllers still matter.
- Their disclosed embodiment still uses modified NeuroMechFly controllers.
- This repo also still relies on FlyGym / NeuroMechFly control machinery underneath the body wrappers.

3. Output mapping is still heuristic.
- Their post now explicitly says they do not know the exact correspondence between brain outputs and controller inputs.
- That matches the current limitation here: `src/bridge/decoder.py` still compresses descending and efferent population activity into `left_drive` and `right_drive`.

### 8.3 Where this repo is currently stronger

This repo currently has stronger explicit evidence that the embodied branch is visually driven.

The strongest current branch:

- has a matched `zero_brain` control
- has a matched no-target control
- logs target state directly from simulation
- shows:
  - `corr(right_drive - left_drive, target_bearing) = 0.8810`
  - target-present runs increase drive and steering asymmetry relative to no-target runs

Those results are documented in:

- `docs/uvgrid_decoder_calibration.md`

By contrast, the Eon update explicitly says that their current visual input is not yet significantly influencing the embodied behavior.

### 8.4 Where the Eon path may still be ahead

The Eon post likely reflects a more polished controller-mediated embodiment layer.

In particular:

- they describe modified imitation-learning-based NeuroMechFly walking controllers
- this repo still uses a hand-built descending-population decoder into a two-drive interface

So the most likely tradeoff is:

- their disclosed embodiment may currently be smoother as a practical controller stack
- this repo is currently stronger on explicit visual-drive validation and falsification logic

### 8.5 Bottom line of the comparison

The subsequent Eon post does not invalidate the direction of this repo. It mostly confirms it.

The public evidence now supports this interpretation:

- the whole-brain core is only one part of the problem
- the real systems bottleneck is the interface between vision, brain dynamics, and embodied control
- the current public state of the art is still controller-mediated and heuristic at the body interface
- exact biologically grounded output semantics remain unresolved on both sides

## 9. Reproducibility

### 9.1 Core setup

From WSL:

```bash
bash scripts/bootstrap_wsl.sh
bash scripts/bootstrap_env.sh
~/.local/bin/micromamba run -n flysim-full bash scripts/check_cuda.sh
~/.local/bin/micromamba run -n flysim-full bash scripts/check_mujoco.sh
python -m pytest tests/test_imports.py tests/test_bridge_unit.py tests/test_closed_loop_smoke.py tests/test_realistic_vision_path.py tests/test_benchmark_output_format.py tests/test_artifact_generation.py
```

### 9.2 Reproduce the strongest current embodied claim

Run these from WSL:

```bash
export MUJOCO_GL=egl
~/.local/bin/micromamba run -n flysim-full python benchmarks/run_fullstack_with_realistic_vision.py --config configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated.yaml --mode flygym --duration 2.0 --output-root outputs/requested_2s_splice_uvgrid_descending_calibrated_target --output-csv outputs/benchmarks/fullstack_splice_uvgrid_descending_calibrated_target_2s.csv
~/.local/bin/micromamba run -n flysim-full python benchmarks/run_fullstack_with_realistic_vision.py --config configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target.yaml --mode flygym --duration 2.0 --output-root outputs/requested_2s_splice_uvgrid_descending_calibrated_no_target --output-csv outputs/benchmarks/fullstack_splice_uvgrid_descending_calibrated_no_target_2s.csv
~/.local/bin/micromamba run -n flysim-full python benchmarks/run_fullstack_with_realistic_vision.py --config configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_zero_brain.yaml --mode flygym --duration 2.0 --output-root outputs/requested_2s_splice_uvgrid_descending_calibrated_zero_brain --output-csv outputs/benchmarks/fullstack_splice_uvgrid_descending_calibrated_zero_brain_2s.csv
python scripts/summarize_descending_visual_drive.py --target-metrics outputs/requested_2s_splice_uvgrid_descending_calibrated_target/flygym-demo-20260311-071452/metrics.csv --target-log outputs/requested_2s_splice_uvgrid_descending_calibrated_target/flygym-demo-20260311-071452/run.jsonl --no-target-metrics outputs/requested_2s_splice_uvgrid_descending_calibrated_no_target/flygym-demo-20260311-073028/metrics.csv --no-target-log outputs/requested_2s_splice_uvgrid_descending_calibrated_no_target/flygym-demo-20260311-073028/run.jsonl --zero-brain-metrics outputs/requested_2s_splice_uvgrid_descending_calibrated_zero_brain/flygym-demo-20260311-074301/metrics.csv --zero-brain-log outputs/requested_2s_splice_uvgrid_descending_calibrated_zero_brain/flygym-demo-20260311-074301/run.jsonl --csv-output outputs/metrics/descending_uvgrid_calibrated_visual_drive_validation.csv --json-output outputs/metrics/descending_uvgrid_calibrated_visual_drive_validation.json
```

Expected summary artifacts:

- `outputs/metrics/descending_uvgrid_calibrated_visual_drive_validation.json`
- `docs/uvgrid_decoder_calibration.md`

### 9.3 Reproduce the body-free splice program

```bash
python scripts/run_splice_probe.py
python scripts/run_splice_calibration.py
python scripts/summarize_splice_calibration.py
python scripts/find_splice_relay_candidates.py
python scripts/run_splice_relay_probe.py
python scripts/summarize_relay_drift.py
```

### 9.4 Reproduce feeding and grooming brain tasks

```bash
python scripts/run_feeding_probe.py --config configs/default.yaml
python scripts/run_grooming_probe.py --config configs/default.yaml
```

### 9.5 Reproduce the synchronized activation visualization

From WSL:

```bash
export MUJOCO_GL=egl
~/.local/bin/micromamba run -n flysim-full python scripts/build_best_branch_activation_visualization.py --config configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_monitored.yaml --mode flygym --duration 2.0 --output-root outputs/visualizations/current_best_branch_activation
```

Expected summary artifact:

- `outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/summary.json`

## 10. Immediate Next Steps

The current next steps are already tracked in `TASKS.md`:

- `T063`: improve per-cell-type column alignment beyond the current coarse shared UV-grid
- `T064`: identify which downstream recurrent pathways or readout assumptions drive the `500 ms` sign collapse
- `T072`: clarify or stabilize the short side-isolated left/right pursuit response
- `T076`: embody the new feeding and grooming tasks using grounded body-side sensory and motor interfaces

The highest-value next loop remains body-free splice refinement plus descending-path analysis. That is still the shortest path to a more defensible embodied controller because it isolates interface failures before expensive body runs are reintroduced.

The semantic-VNC branch should not be the active parity path right now. It is preserved as a useful negative result and should only be revisited as a new branch with new output roots, not by mutating the frozen artifacts in place.

## 11. Conclusion

This project now provides a reproducible public-equivalent embodied fly stack that is materially stronger than a thin demo wrapper around public repos. It includes persistent online control, realistic vision, a recurrent whole-brain backend, benchmark and profiler evidence, negative-control logic, and a descending-only embodied branch whose movement disappears in a `zero_brain` control and is measurably modulated by a moving target under realistic vision. It also includes grounded feeding and grooming brain-task reproductions ready for later embodiment work.

The central scientific and engineering discovery is that the problem was never just to run the public components together. The crucial work was at the splice and the output abstraction. The original scalar bridge destroyed useful visual structure, and the original motor readout was too narrow. A calibrated, grounded splice and a broader descending-only readout jointly moved the system from misleading fallback-heavy behavior to evidence-backed brain-driven visuomotor locomotion.

That is meaningful progress, but not the end state. Exact biological motor semantics, finer visual alignment, longer-window recurrent stability, and full embodiment of additional tasks remain unresolved. The current parity verdict therefore remains partial.

## References

1. Shiu, P. K., Sterne, G. R., Spiller, N. et al. *A Drosophila computational brain model reveals sensorimotor processing*. Nature 634, 210-219 (2024). `https://www.nature.com/articles/s41586-024-07763-9`
2. Dorkenwald, S., McKellar, C., Macrina, T. et al. *Neuronal wiring diagram of an adult brain*. Nature 634, 124-138 (2024). `https://www.nature.com/articles/s41586-024-07558-y`
3. Schlegel, P., Bates, A. S., Stuerner, T. et al. *Whole-brain annotation and multi-connectome cell typing of Drosophila*. Nature 634, 153-163 (2024). `https://www.nature.com/articles/s41586-024-07686-5`
4. Eichler, K., Li, F., Litwin-Kumar, A. et al. *Network statistics of the whole-brain connectome of Drosophila*. Nature 634, 164-171 (2024). `https://www.nature.com/articles/s41586-024-07968-y`
5. Vaxenburg, R., Rockenfeller, B., Bidaye, S. S. et al. *NeuroMechFly v2: simulating embodied sensorimotor control in adult Drosophila*. Nature Methods 22 (2024). `https://www.nature.com/articles/s41592-024-02497-y`
6. `eonsystemspbc/fly-brain` public repository. `https://github.com/eonsystemspbc/fly-brain`
7. `NeLy-EPFL/flygym` public repository. `https://github.com/NeLy-EPFL/flygym`
