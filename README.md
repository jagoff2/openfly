# Reconstructing a Public-Equivalent Embodied *Drosophila* Brain-Body System from Open Components

Author: Codex  
Project: OpenFly Reconstruction  
Date: 2026-03-26

## Abstract

Public artifacts now exist for the adult *Drosophila melanogaster* whole-brain connectome, a connectome-derived recurrent brain model, realistic embodied biomechanics, and realistic visual processing. What remains unavailable as a turnkey public system is the persistent closed-loop integration layer that converts realistic sensory state into online brain input, converts online brain state into locomotor output, and validates the resulting behavior under matched controls. This study reports a public-equivalent reconstruction of that missing stack on one local workstation using only open repositories, public datasets, and in-repo integration code.

The reconstructed system combines a persistent FlyWire-derived whole-brain Torch backend, FlyGym and NeuroMechFly v2 embodiment, FlyGym realistic vision with FlyVis-derived activity, and an explicitly documented bridge for online closed-loop control. The work was organized as a reconstruction-and-falsification program rather than as a claim of access to unpublished private glue. Every promoted claim was required to survive matched `target`, `no_target`, and `zero_brain` controls, artifact generation, and fixed-duration benchmarking on the local machine.

The main findings are fivefold. First, a realistic-vision, real-body, whole-brain closed loop now runs locally and reproducibly. Second, the earliest plausible public-anchor bridge failed for structural reasons: it collapsed informative visual structure and compressed output through too small a descending readout. Third, a body-free splice program and a wider descending readout established the first credible brain-driven, visually modulated embodied locomotion branch. Fourth, a decoder-internal brain-latent turn branch improved perturbation-linked steering on the honest non-spontaneous path: in a matched `2.0 s` jump assay, jump turn-bearing correlation improved from `0.3215` to `0.8177`, jump bearing-recovery fraction improved from `-0.8210` to `-0.5658`, and the matched `zero_brain` control remained silent with `controller_turn_nonzero_fraction = 0.0`. Fifth, adding endogenous structured spontaneous state inside the brain backend and refitting the latent in the awakened regime produced a living branch that now clears a mesoscale validation slice against public whole-brain data: matched living `target` and `no_target` runs share the same non-quiescent spontaneous backbone, pass walk-linked global modulation, bilateral family coupling, residual high-dimensional and temporal structure, and a public forced-vs-spontaneous Aimon comparator as a real but partial criterion.

The project therefore no longer has one undifferentiated “best branch.” It now has two leading claim branches. The non-spontaneous brain-latent branch remains strongest on perturbation-linked steering. The spontaneous-on refit branch is the strongest living-brain line and the strongest branch on mesoscale physiological plausibility. Full parity remains unresolved because frontal refixation after jump still fails within `2.0 s`, the visual splice remains inferred rather than neuron-identical, the embodied motor interface remains compressed, and the public forced-vs-spontaneous comparator is informative but only partial.

## 1. Introduction

The public Eon-style embodied fly demo context implies a difficult systems problem. A realistic adult fly body must move in a physics simulator. A realistic visual system must transform the scene into neural activity rather than raw pixels. A recurrent whole-brain model must preserve internal state across time. And the entire stack must run online, not as disconnected notebook analyses. Public repositories provide most of the ingredients for this program, but they do not provide a validated, persistent, local, end-to-end closed loop with matched controls and explicit acceptance logic.

This gap matters scientifically as much as it matters technically. A convincing embodied brain system is not simply a matter of getting independent modules to import successfully. The crucial question is whether sensory state, recurrent brain state, descending readout, and body control can be linked in a way that remains observable, reproducible, and biologically interpretable. In practice, this required not just integration but repeated falsification of appealing but incorrect interfaces.

This study therefore treated OpenFly as a reconstruction study rather than a demo-assembly exercise. The goal was to reproduce a public-equivalent embodied fly stack as closely as the public artifacts allow, to define explicit parity criteria against public observables, and to reject branches that moved the fly for the wrong reasons. Under that framing, negative results were as important as positive ones. They identified where information was being destroyed, where controls were insufficient, and where apparently more biologically ambitious routes still failed behaviorally.

The result is a local system that now supports three classes of claim. First, the stack can run a real realistic-vision, whole-brain, embodied closed loop locally. Second, the system produces brain-driven and visually modulated embodied behavior under matched controls. Third, a decoder-internal latent derived from monitored brain state improves perturbation-linked steering without reintroducing controller or body shortcuts. The system does not yet justify the stronger claim of an indistinguishable living fly.

## 2. Scope, Hardware, and Honesty Boundary

### 2.1 Hardware target

All reported results were obtained on one workstation:

| Component | Value |
| --- | --- |
| Host OS | Windows 11 |
| Linux runtime | WSL2 |
| GPUs | 2x NVIDIA RTX 5060 Ti 16 GB |
| System RAM | 192 GB |
| Production vision device | CPU in WSL |

### 2.2 Public components used

| Subsystem | Public source | Role in this study |
| --- | --- | --- |
| Whole-brain model | `eonsystemspbc/fly-brain`; Shiu et al. 2024 | recurrent online brain backend |
| Whole-brain connectome | FlyWire adult whole-brain releases | graph, coordinates, annotations |
| Embodied body | `NeLy-EPFL/flygym`; NeuroMechFly v2 | body physics and sensorimotor environment |
| Realistic vision | FlyGym realistic vision and FlyVis-derived activity | neural visual frontend |
| VNC connectome data | MANC/BANC public releases | structural-output exploration and falsification |

### 2.3 Honesty boundary

This repo does not claim access to unpublished Eon glue, private parameters, or hidden controller logic. The whole-brain core, connectome, visual frontend, and body simulator are public. The persistent closed-loop bridge, matched-control evaluation logic, perturbation assays, activation visualization, and decoding workbench were implemented in this repo because the public components did not ship as a turnkey online controller. Wherever an interface remained inferred rather than neuron-identical, that inference was documented explicitly and the resulting claims were limited accordingly.

Two rules governed every promoted branch.

1. `>= 1.0 s` runs count as real evaluation; `< 1.0 s` runs count only as smoke or sanity checks.
2. The active embodiment path may not rely on controller-side or body-side shortcut heuristics. New control changes must be brain-driven and biologically plausible.

Those rules are recorded in [TASKS.md](/G:/flysim/TASKS.md) and [ASSUMPTIONS_AND_GAPS.md](/G:/flysim/ASSUMPTIONS_AND_GAPS.md).

## 3. System Overview

The production stack is a persistent five-part loop:

1. [flygym_runtime.py](/G:/flysim/src/body/flygym_runtime.py) maintains a live FlyGym world, embodied state, and realistic visual activity.
2. [visual_splice.py](/G:/flysim/src/bridge/visual_splice.py) transforms structured FlyVis activity into direct brain-side input at a grounded overlap boundary.
3. [pytorch_backend.py](/G:/flysim/src/brain/pytorch_backend.py) maintains recurrent whole-brain state over a FlyWire-derived graph of `138,639` neurons and `15,091,983` weighted edges.
4. [decoder.py](/G:/flysim/src/bridge/decoder.py) converts monitored brain activity into the body-facing locomotor interface.
5. [closed_loop.py](/G:/flysim/src/runtime/closed_loop.py) synchronizes time stepping, logging, metrics, activation capture, and artifact generation.

The current production path is not a notebook replay. It is a persistent closed loop with run directories, JSONL logs, metrics CSVs, videos, activation captures, and explicit condition metadata.

## 4. Experimental Program

### 4.1 Reconstruction logic

The work proceeded through a sequence of progressively stricter hypotheses.

1. A minimal public-anchor bridge might be enough.
2. If it failed, a better visual splice might rescue the system.
3. If splice improvement alone failed, output compression might be the deeper bottleneck.
4. If wider descending readouts helped, perturbation assays could localize the remaining missing state.
5. If monitored relay state carried cleaner steering information than the live decoder, that information should be decoded inside the primary decoder rather than injected as controller logic.
6. If the system still lacked autonomy, the brain backend itself would need endogenous state rather than a silent cold start.

Each step generated runnable code, tests, output artifacts, and a written branch note. Several branches were kept explicitly as negative results because they clarified the actual bottleneck.

### 4.2 Control logic

The main behavioral conditions were:

- `target`
- `no_target`
- `zero_brain`
- `target_jump`
- `target_removed_brief`

The corresponding behavior targets were restricted to real adult-fly behaviors documented in [behavior_target_set.md](/G:/flysim/docs/behavior_target_set.md): spontaneous roaming, intermittent locomotion, structured reorientation, landmark fixation, perturbation refixation, short-timescale orientation persistence, and walking-linked global brain state. Generic indefinite smooth pursuit of an arbitrary moving target was explicitly rejected as the default acceptance criterion.

### 4.3 Whole-brain activation visibility

A synchronized activation visualization now ships with the same embodied run rather than requiring a special-case rerun. The resulting artifact shows, side by side:

- the embodied FlyGym view
- the whole-brain point cloud
- FlyVis left/right activity
- monitored brain populations
- controller channels

For the current leading branch, the activation composite records `200` synchronized frames, `138,639` brain neurons, `45,669` FlyVis nodes, `48` monitor labels, and `307` monitored root IDs from the same run directory as the body video.

## 5. Results

### 5.1 The local public-equivalent stack runs end to end

The system now satisfies the module-level reconstruction gate: brain-only, body-only, realistic-vision, and full closed-loop workloads all run locally and emit benchmark artifacts. Representative performance on this machine is shown below.

| Workload | Device | Sim time | Wall time | Real-time factor |
| --- | --- | ---: | ---: | ---: |
| Brain only, Torch | `cuda:0` | `0.100 s` | `0.923 s` | `0.1083x` |
| Brain only, Brian2 CPU | `cpu` | `0.100 s` | `10.852 s` | `0.0092x` |
| Body only | `cpu` | `0.020 s` | `0.285 s` | `0.0701x` |
| Realistic vision only | `cpu` | `0.020 s` | `22.644 s` | `0.000883x` |
| Full legacy closed loop | `cpu` | `0.098 s` | `125.350 s` | `0.000782x` |

The bottleneck is unambiguous: realistic vision dominates runtime. The validated WSL path remains CPU-bound for FlyVis because the public WSL wheels do not yet support RTX 5060 Ti `sm_120`. That is a performance limitation, not an architectural ambiguity.

### 5.2 The minimal public-anchor bridge failed for structural reasons

The first strict bridge used public bilateral anchor pools derived from checked public IDs (`LC4`, `JON`, `P9`, `DNa01`, `DNa02`, `MDN`) and a small descending readout. Once decoder idle-drive fallback, fake lateralized public inputs, and body-side hidden locomotion fallback were removed, that bridge no longer produced convincing locomotion.

This failure was not caused by a dead backend. The backend responded strongly to positive-control stimulation, but the observed bilateral production inputs under-drove the monitored locomotor readouts. The failure therefore falsified the initial hypothesis that a small, clean public-anchor bridge would be sufficient. It also established an important methodological lesson: visually convincing behavior must not be accepted unless matched controls prove that the body is not moving on an auxiliary motor floor.

### 5.3 A body-free visual splice program localized the sensory bottleneck

The next advance came from removing the body from the inner discovery loop and directly testing how FlyVis activity entered the whole-brain model. The splice boundary was grounded using the official FlyWire annotation supplement and exact shared visual `cell_type + side` groups rather than fabricated left/right splits. The repo identified:

- `49` exact shared visual cell types
- `98` exact `cell_type + side` groups
- `392` groups after `4` coarse spatial bins

The calibrated signed splice reached strong boundary agreement and produced the correct downstream turn-sign launch at short latency. In the curated calibration regime, mean voltage group correlation reached `0.8709` and mean side-difference correlation reached `0.8079`. However, the correct downstream sign collapsed by `500 ms`, even when the external input was reduced to a short pulse. This narrowed the failure from “no visual structure reaches the brain” to “longer-window downstream stability remains wrong.”

### 5.4 Output compression was as important as sensory fidelity

Improving the input boundary alone did not solve embodied behavior. The next decisive result was that a wider descending-only readout transformed the embodied system far more than further scalar encoder tuning. The older splice-only embodied readout produced `net_displacement = 0.1132` and `displacement_efficiency = 0.0519`. A descending-only expanded readout then produced:

- `avg_forward_speed = 4.5638`
- `path_length = 9.1185`
- `net_displacement = 5.6330`
- `displacement_efficiency = 0.6178`

This was the first branch to produce convincing traversal without optic-lobe-as-motor shortcuts, explicit `P9` prosthetic locomotor context, decoder idle floor, or body-side hidden locomotion fallback.

### 5.5 The calibrated realistic-vision descending branch established the first strong control-backed embodied baseline

The best-performing continuous-target branch under the original acceptance criteria remains the calibrated realistic-vision descending configuration. In its `2.0 s` target run, it achieved:

- `avg_forward_speed = 4.9241`
- `net_displacement = 5.7583`
- `displacement_efficiency = 0.5853`

Matched controls established the valid interpretation of this branch:

- target + real brain: meaningful traversal and target-bearing-aligned steering
- no-target + real brain: substantial locomotion remained
- target + zero-brain: decoded commands vanished and net displacement collapsed to `0.0118`

This combination supports a specific claim: the branch is brain-driven and visually driven, but not purely target-driven. Scene structure, optic flow, and self-motion still contribute materially under `no_target`. That distinction is essential. The branch established a credible embodied baseline, but it did not yet solve perturbation refixation or long-horizon target stabilization.

### 5.6 The perturbation assay localized the missing state more sharply than continuous-target metrics

Continuous-target metrics were insufficient to diagnose whether the system truly stabilized a target or merely acquired it transiently. This study therefore added a target perturbation schedule with jump and brief-removal events. These assays are more biologically grounded for the current vision-first branch because they test landmark refixation and bounded orientation persistence rather than unbounded pursuit.

This interpretation is strengthened by Pires et al. 2024, which described a
central-complex circuit that compares allocentric heading and goal signals to
produce an egocentric steering command through `PFL3` output to the `LAL`. That
study used virtual cue rotations during menotaxis-like behavior and showed that
flies slowed and made corrective turns to recover the prior heading-goal
relation. Under that framing, the OpenFly jump assay is best understood as a
heading / goal perturbation assay, not as a generic moving-target pursuit task.
It also means that failure to re-enter a narrow frontal cone within `2.0 s`
does not automatically imply incorrect steering computation when the target
continues moving tangentially after the jump.

The first honest jump-monitor branch, built on the canonical calibrated decoder with no steering promotion, produced strong signed corrective turning immediately after the jump but still failed actual frontal refixation. The target often reached the rear field within a few hundred milliseconds after the perturbation. This was an important result: the system already had signed steering, but it lacked a more persistent, better-structured internal variable needed to restabilize the target.

### 5.7 Relay monitoring showed that informative steering structure lived in brain voltage, not only in DN spike-rate summaries

The next discovery was that rate-only DN summaries were under-reporting the available control signal. When monitored relay and visual families were rescored in voltage space, steering-relevant structure became much clearer than in the live sampled turn scalar. This led to two important conclusions.

First, the problem was not simply absence of target-bearing information. Second, further controller-side steering patches would be scientifically weak, because the relevant signal already existed upstream in monitored brain state. This finding justified the next move: decode that state inside the primary motor decoder rather than injecting new controller logic.

### 5.8 A decoder-internal brain-latent turn branch is the strongest perturbation branch on the honest non-spontaneous path

The current lead branch is the decoder-internal brain-latent turn configuration:

- target run: [summary.json](/G:/flysim/outputs/requested_2s_calibrated_target_jump_brain_latent_turn/flygym-demo-20260315-061819/summary.json)
- target activation video: [activation_side_by_side.mp4](/G:/flysim/outputs/requested_2s_calibrated_target_jump_brain_latent_turn/flygym-demo-20260315-061819/activation_side_by_side.mp4)
- no-target run: [summary.json](/G:/flysim/outputs/requested_2s_calibrated_no_target_brain_latent_turn/flygym-demo-20260315-063511/summary.json)
- no-target activation video: [activation_side_by_side.mp4](/G:/flysim/outputs/requested_2s_calibrated_no_target_brain_latent_turn/flygym-demo-20260315-063511/activation_side_by_side.mp4)
- zero-brain run: [summary.json](/G:/flysim/outputs/requested_2s_calibrated_zero_brain_target_jump_brain_latent_turn/flygym-demo-20260315-065048/summary.json)
- matched comparison: [brain_latent_turn_live_comparison.json](/G:/flysim/outputs/metrics/brain_latent_turn_live_comparison.json)

This branch was constructed under the hard no-shortcuts rule. The new turn term is decoded inside [decoder.py](/G:/flysim/src/bridge/decoder.py) from monitored brain voltage using a matched target/no-target library. No privileged target metadata enters control, and no controller-side steering promotion or body-side override is used.

Relative to the honest relay-monitored baseline, the latent branch improved perturbation-linked steering materially:

| Metric | Honest baseline | Brain-latent branch | Delta |
| --- | ---: | ---: | ---: |
| Jump turn-bearing correlation | `0.3215` | `0.8177` | `+0.4962` |
| Jump bearing-recovery fraction over `2.0 s` | `-0.8210` | `-0.5658` | `+0.2551` |
| Fixation fraction at `20 deg` | `0.043` | `0.059` | `+0.016` |

The live target run for this branch also remained robustly embodied:

- `avg_forward_speed = 5.4296`
- `net_displacement = 6.2632`
- `stable = 1.0`
- `target_condition_turn_bearing_corr = 0.8806`
- `target_perturbation_jump_turn_bearing_corr = 0.8177`

The control logic remained intact:

- `no_target` stayed near zero-mean in turn: `mean_turn_drive = 0.0054`
- `zero_brain` remained silent: `controller_turn_nonzero_fraction = 0.0`

This branch is also visually the most compelling result in the repo to date. The synchronized activation composite and the embodied video show behavior that looks purposeful during acquisition and perturbation response. However, the branch still falls short of a full living-fly claim. Frontal jump refixation was not achieved within `2.0 s`:

- `jump_refixation_latency_s = null`
- `jump_refixation_fraction_20deg = 0.0`

The correct claim is therefore narrow but important: a decoder-internal, brain-side latent improves perturbation-linked steering on the honest non-spontaneous path. It does not yet establish robust refixation, goal memory, or full behavioral parity.

### 5.9 The backend can now start from an endogenous living state rather than a dead silent reset, and that living branch now clears a mesoscale validation slice

The original whole-brain backend had an absorbing silent cold start. With zero input and zero recurrent activity, it stayed at rest indefinitely. Because that is a major biological gap, this study added and tested endogenous spontaneous-state candidates inside the brain backend rather than in the decoder or body controller.

The current spontaneous-state candidate uses bilateral family-structured tonic occupancy and slow latent fluctuations over central, ascending, visual-projection, visual-centrifugal, and endocrine families. In the brain-only audit, the old cold start remained exactly silent, while the new candidate produced sparse, bounded, perturbable ongoing activity. Across three seeds, ongoing spontaneous turn bias was reduced to `+2.5`, `+10.0`, and `+12.5 Hz`, pulse peak turn asymmetry remained `100 Hz` in all seeds, and homologous bilateral voltage correlation became positive and measurable.

The key follow-up result is that the spontaneous state is no longer only a brain-only plausibility result. After refitting the brain-latent decoder on matched awakened `target` and awakened `no_target` captures, the repo now has a living embodied branch:

- target run: [summary.json](/G:/flysim/outputs/requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-203010/summary.json)
- target activation video: [activation_side_by_side.mp4](/G:/flysim/outputs/requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-203010/activation_side_by_side.mp4)
- no-target run: [summary.json](/G:/flysim/outputs/requested_2s_calibrated_no_target_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-204719/summary.json)
- no-target activation video: [activation_side_by_side.mp4](/G:/flysim/outputs/requested_2s_calibrated_no_target_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-204719/activation_side_by_side.mp4)
- comparison: [spontaneous_brain_latent_refit_comparison.json](/G:/flysim/outputs/metrics/spontaneous_brain_latent_refit_comparison.json)

This living branch is not directly comparable to the old dead-brain branches on raw absolute movement metrics, because enabling spontaneous state changes the operating regime of the whole brain itself. The correct comparison is living `target` versus living `no_target`, plus mesoscale public anchors. Under that rule, the current living target branch remains bounded and brain-driven while staying in the same awakened regime as living `no_target`:

- `avg_forward_speed = 4.1828`
- `net_displacement = 5.0591`
- `target_condition_turn_bearing_corr = 0.7018`
- `target_perturbation_jump_turn_bearing_corr = 0.5644`
- `spontaneous_locomotion_locomotor_active_fraction = 0.995`

The deeper result is at mesoscale validation. On the matched living `target` / `no_target` pair, the branch now passes:

- non-quiescent awake state
- matched living baseline
- walk-linked global modulation
- bilateral family coupling
- family structure against a circular-shift surrogate
  - `target = 2.6001`
  - `no_target = 2.7912`
- residual high-dimensional structure
- residual temporal structure
- turn-linked spatial heterogeneity
- weak positive family-scale connectome-to-function correspondence
  - `target log corr = 0.0545`
  - `no_target log corr = 0.0534`

The public Aimon forced-vs-spontaneous comparator is now also live rather than missing. The decisive public substrate turned out to be `Additional_data.zip`, not `Walk_components.zip`. All five declared Aimon files are now staged and digest-valid, and the public comparator now runs against the staged functional-region traces:

- [aimon_forced_spontaneous_comparator_summary.json](/G:/flysim/outputs/metrics/aimon_forced_spontaneous_comparator_summary.json)
- [aimon_forced_spontaneous_comparator_rows.csv](/G:/flysim/outputs/metrics/aimon_forced_spontaneous_comparator_rows.csv)

Its outcome is real but partial:

- `n_candidate_rows = 4`
- `n_experiments_used = 2`
- surviving distinct public comparisons:
  - `B350`
  - `B1269`
- excluded due overlapping public spontaneous/forced windows:
  - `B1037`
  - `B378`
- median public metrics:
  - `steady_walk_vector_corr = -0.2016`
  - `steady_walk_rank_corr = -0.2013`
  - `spontaneous_prelead_fraction = 0.6241`
  - `spontaneous_minus_forced_prelead_delta = 0.01393`

So the living branch now has a stronger and more honest claim boundary than before. It is not fully physiologically validated, but it is no longer merely “awake-looking.” It is living in a mesoscale-validated sense: ongoing, structured, bilateral, temporally coherent, behavior-linked, and constrained by public spontaneous-state data. The remaining limitation is equally clear: this branch is more biologically plausible at the network scale than the older cold-start branches, but it is still weaker than the non-spontaneous perturbation branch on jump refixation and should not yet be treated as the final embodiment path.

### 5.10 A semantic-VNC structural decoder was a useful negative result, not a parity path

One of the major exploratory lines in this project attempted to move beyond small sampled descending populations toward a broader structural output interface derived from public VNC connectome resources. That line solved several real implementation problems:

- raw MANC-to-FlyWire ID mismatch
- silent monitor-space incompatibility
- early decoder saturation
- off-screen camera framing

The corrected semantic-VNC branch became stable and locomotor-capable. Even so, it still failed target-tracking parity. The important inference is not that the branch “needed more tuning.” It is that structural semantic reachability alone was insufficient to recover target-directed behavior. This is one of the most important negative results in the repo because it rules out a superficially attractive but incomplete route to full embodiment.

## 6. Discussion

The central lesson of this study is that the hard problem was not simply to make public modules coexist in one process. The hard problem was to locate the biologically meaningful state that must pass between realistic sensory activity, recurrent whole-brain dynamics, descending output, and embodied control. Several findings now appear robust.

First, realistic-vision, whole-brain, embodied closed-loop operation is achievable from public components on a single workstation. Second, matched `zero_brain` controls are indispensable: they prevented misleading claims based on hidden locomotor floors. Third, the earliest major failure was not backend inactivity but information loss at the sensory bridge and over-compression at the output decoder. Fourth, brain voltage carried useful steering structure that rate-only DN summaries were obscuring. Fifth, decoding that structure inside the primary decoder is scientifically cleaner and empirically stronger than adding more controller-side logic.

The current repo state should therefore be understood as a two-branch frontier rather than a single winning configuration. `requested_2s_calibrated_target_jump_brain_latent_turn` remains the leading perturbation branch. `requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous_refit` is the leading living-brain mesoscale branch. The former is stronger on perturbation-linked steering; the latter is stronger on spontaneous-state realism and public mesoscale validation.

The non-spontaneous perturbation branch is still the first branch in the repo that combines all of the following:

- realistic vision
- real whole-brain recurrence
- embodied locomotion
- perturbation-aware evaluation
- same-run activation visualization
- matched `target`, `no_target`, and `zero_brain` controls
- a decoder-internal improvement derived from monitored brain state rather than controller heuristics

What remains unresolved is not whether the system can move or even whether it can steer in a target-signed way. The remaining gap is a richer internal scaffold for heading, goal persistence, steering gain, and reorientation policy, plus a more biological output pathway. The next biologically plausible move is therefore not another controller patch. It is to extend the decoder-internal latent beyond signed steering error toward a better-structured heading/goal scaffold while keeping the spontaneous living regime on, and to evaluate that scaffold against matched living controls and the mesoscale validation bundle rather than regressing to silent-brain comparisons.

## 7. Limitations

This study has clear limitations.

First, the public/private boundary remains real. The exact Eon integration logic is not public, so this repo is a public-equivalent reconstruction rather than an exact clone.

Second, the sensory splice is still inferred. It is more strongly grounded than the original scalar bridge, but it is not an exact neuron-identity mapping between FlyVis and FlyWire.

Third, the motor output remains compressed. Even the best current branch still maps rich brain state into a compact body-facing locomotor interface rather than a full VNC-to-muscle pathway.

Fourth, the current leading branch improves perturbation-linked steering but still fails frontal refixation within `2.0 s`. It therefore does not justify claims of robust reacquisition, orientation memory, or full pursuit parity.

Fifth, the spontaneous-state program has now cleared an embodied mesoscale-validation gate, but not a full physiological one.

Sixth, the public forced-vs-spontaneous comparator is now executable but only partial. It is evidence-producing, not missing, yet the surviving public overlap subset is too small and mixed to support a strong parity claim.

Seventh, realistic vision remains performance-limited on this hardware in WSL because public wheels do not support `sm_120`.

## 8. Methods

### 8.1 Environments and installation

The repo uses a split environment strategy because modern FlyGym and the secondary Brian2 benchmark stack are not cleanly co-installable. Bootstrap and validation are scripted in:

- [bootstrap_wsl.sh](/G:/flysim/scripts/bootstrap_wsl.sh)
- [bootstrap_env.sh](/G:/flysim/scripts/bootstrap_env.sh)
- [check_cuda.sh](/G:/flysim/scripts/check_cuda.sh)
- [check_mujoco.sh](/G:/flysim/scripts/check_mujoco.sh)

### 8.2 Closed-loop runtime

The closed loop is orchestrated in [closed_loop.py](/G:/flysim/src/runtime/closed_loop.py). The body runtime is [flygym_runtime.py](/G:/flysim/src/body/flygym_runtime.py). The production brain backend is [pytorch_backend.py](/G:/flysim/src/brain/pytorch_backend.py). The primary decoder is [decoder.py](/G:/flysim/src/bridge/decoder.py).

### 8.3 Visual boundary

The production bridge uses [visual_splice.py](/G:/flysim/src/bridge/visual_splice.py) to convert realistic visual activity into grounded direct brain-side input. The splice program was calibrated body-free before embodied promotion.

### 8.4 Perturbation assays

Stimulus-side target perturbations are implemented in [target_schedule.py](/G:/flysim/src/body/target_schedule.py). Behavioral metrics, including jump and brief-removal summaries, are computed in [behavior_metrics.py](/G:/flysim/src/analysis/behavior_metrics.py). These assays do not provide privileged target metadata to the controller.

The current perturbation assay should be interpreted as a demanding continuous
cue-recovery test. Relative to the menotaxis perturbation logic of Pires et al.
2024, OpenFly is harsher because the target keeps moving after the jump instead
of remaining as a displaced cue whose heading relation can be cleanly
recovered. The strongest biologically grounded jump metrics are therefore
corrective-turn latency, signed turn-bearing correlation, and bearing recovery,
not only strict frontal refixation.

### 8.5 Decoder-internal brain latent

The current leading branch reads monitored brain voltage inside [decoder.py](/G:/flysim/src/bridge/decoder.py) through a matched target/no-target latent library built by:

- [brain_latent_library.py](/G:/flysim/src/analysis/brain_latent_library.py)
- [build_brain_turn_latent_library.py](/G:/flysim/scripts/build_brain_turn_latent_library.py)

The live config set is:

- [target jump latent config](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_jump_brain_latent_turn.yaml)
- [no-target latent config](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_latent_turn.yaml)
- [zero-brain latent config](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_zero_brain_target_jump_brain_latent_turn.yaml)

### 8.6 Activation visualization

Same-run activation capture and rendering are handled by:

- [session.py](/G:/flysim/src/visualization/session.py)
- [activation_viz.py](/G:/flysim/src/visualization/activation_viz.py)

The capture bundle for the current leading branch is:

- [activation_capture.npz](/G:/flysim/outputs/requested_2s_calibrated_target_jump_brain_latent_turn/flygym-demo-20260315-061819/activation_capture.npz)

### 8.7 Testing and acceptance

Promoted claims required tests and saved artifacts. The relevant focused suites for the current branch include:

- [test_bridge_unit.py](/G:/flysim/tests/test_bridge_unit.py)
- [test_closed_loop_smoke.py](/G:/flysim/tests/test_closed_loop_smoke.py)
- [test_turn_voltage_library.py](/G:/flysim/tests/test_turn_voltage_library.py)
- [test_spontaneous_state_unit.py](/G:/flysim/tests/test_spontaneous_state_unit.py)

The branch progression and claim logic are tracked continuously in:

- [TASKS.md](/G:/flysim/TASKS.md)
- [PROGRESS_LOG.md](/G:/flysim/PROGRESS_LOG.md)
- [ASSUMPTIONS_AND_GAPS.md](/G:/flysim/ASSUMPTIONS_AND_GAPS.md)

### 8.8 Spontaneous-state mesoscale validation

The canonical living-branch spontaneous-state validation bundle is:

- [spontaneous_mesoscale_validation.py](/G:/flysim/src/analysis/spontaneous_mesoscale_validation.py)
- [run_spontaneous_mesoscale_validation.py](/G:/flysim/scripts/run_spontaneous_mesoscale_validation.py)
- [spontaneous_mesoscale_validation_summary.json](/G:/flysim/outputs/metrics/spontaneous_mesoscale_validation_summary.json)
- [aimon_public_comparator_resolution.md](/G:/flysim/docs/aimon_public_comparator_resolution.md)

This bundle is now the correct validation surface for the living branch. Once spontaneous state is enabled, the old cold-start branches are only regime-transition baselines, not the primary spontaneous-state comparator.

## 9. Author Contributions

The author conceived and led the reconstruction effort, defined the evaluation and falsification framework, implemented or supervised the bridge, runtime, decoder, assay, and visualization stack, ran the reported analyses, and wrote the manuscript.

## 10. Reproducibility and Principal Artifacts

The current leading perturbation branch is reproduced by the run roots:

- [target run](/G:/flysim/outputs/requested_2s_calibrated_target_jump_brain_latent_turn/flygym-demo-20260315-061819)
- [no-target run](/G:/flysim/outputs/requested_2s_calibrated_no_target_brain_latent_turn/flygym-demo-20260315-063511)
- [zero-brain run](/G:/flysim/outputs/requested_2s_calibrated_zero_brain_target_jump_brain_latent_turn/flygym-demo-20260315-065048)

The key comparison summary is:

- [brain_latent_turn_live_comparison.json](/G:/flysim/outputs/metrics/brain_latent_turn_live_comparison.json)

The main negative-result branch remains frozen at:

- [semantic_vnc_failed_parity_branch.md](/G:/flysim/docs/semantic_vnc_failed_parity_branch.md)

The main spontaneous-state summary is:

- [spontaneous_state_results.md](/G:/flysim/docs/spontaneous_state_results.md)

The current leading living spontaneous branch is reproduced by:

- [target spontaneous refit run](/G:/flysim/outputs/requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-203010)
- [no-target spontaneous refit run](/G:/flysim/outputs/requested_2s_calibrated_no_target_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-204719)
- [living branch mesoscale validation summary](/G:/flysim/outputs/metrics/spontaneous_mesoscale_validation_summary.json)
- [public forced-vs-spontaneous comparator summary](/G:/flysim/outputs/metrics/aimon_forced_spontaneous_comparator_summary.json)

## 11. Conclusion

OpenFly now constitutes a reproducible public-equivalent reconstruction of an embodied *Drosophila* brain-body stack assembled from open components. The study did not merely glue together public repos; it built the missing online bridge, enforced matched controls, falsified incorrect interfaces, and narrowed the current bottleneck to a biologically meaningful region of the system. The strongest earlier branch established credible brain-driven, visually modulated embodied locomotion. The strongest non-spontaneous perturbation branch, `requested_2s_calibrated_target_jump_brain_latent_turn`, improved jump-linked steering through a decoder-internal latent derived from monitored brain state while preserving bounded `no_target` behavior and silent `zero_brain` controls. The strongest living spontaneous branch, `requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous_refit`, goes further on biological plausibility at the network scale by running in an awakened regime that now clears a real mesoscale validation bundle against public spontaneous-state data.

That is a stronger and more precise result than the repo supported before, but it is still not the end state. The system still lacks robust frontal refixation after perturbation, a fully grounded heading/goal scaffold, full physiological spontaneous-state validation, and a biologically richer output pathway. The public forced-vs-spontaneous comparator is now real and informative, but only partial. The correct verdict is therefore not final parity, but a strong public-equivalent partial reconstruction with one leading perturbation branch and one leading living-brain branch, both scientifically useful and both honest about their remaining gaps.

## References

1. Shiu, P. K., Sterne, G. R., Spiller, N., et al. *A Drosophila computational brain model reveals sensorimotor processing*. Nature 634, 210-219 (2024). https://www.nature.com/articles/s41586-024-07763-9
2. Dorkenwald, S., McKellar, C., Macrina, T., et al. *Neuronal wiring diagram of an adult brain*. Nature 634, 124-138 (2024). https://www.nature.com/articles/s41586-024-07558-y
3. Schlegel, P., Bates, A. S., Stuerner, T., et al. *Whole-brain annotation and multi-connectome cell typing of Drosophila*. Nature 634, 153-163 (2024). https://www.nature.com/articles/s41586-024-07686-5
4. Eichler, K., Li, F., Litwin-Kumar, A., et al. *Network statistics of the whole-brain connectome of Drosophila*. Nature 634, 164-171 (2024). https://www.nature.com/articles/s41586-024-07968-y
5. Vaxenburg, R., Rockenfeller, B., Bidaye, S. S., et al. *NeuroMechFly v2: simulating embodied sensorimotor control in adult Drosophila*. Nature Methods 22 (2024). https://www.nature.com/articles/s41592-024-02497-y
6. Aimon, S., Katsuki, T., Jia, T., et al. *Walking and turning shape brain-wide activity in Drosophila*. eLife 12 (2023). https://elifesciences.org/articles/85202
7. Geurten, B. R. H., Jahde, P., Corthals, K., Gopfert, M. C. *Saccadic body turns in walking Drosophila*. Journal of Comparative Physiology A 200, 653-663 (2014). https://pmc.ncbi.nlm.nih.gov/articles/PMC4205811/
8. Moore, R. J. D., Taylor, G. J., Paulk, A. C., Pearson, T., van Swinderen, B. *Separable visual feature extraction and fixation behavior in Drosophila*. Scientific Reports 4, 4768 (2014). https://pmc.ncbi.nlm.nih.gov/articles/PMC6605338/
9. Xiong, Y., Lv, H., Gong, Z., Liu, L. *Fixation and menotaxis behavior in freely walking Drosophila*. PLoS Computational Biology 16, e1007843 (2020). https://pmc.ncbi.nlm.nih.gov/articles/PMC7843020/
10. Neuser, K., Triphan, T., Mronz, M., Poeck, B., Strauss, R. *Analysis of a spatial orientation memory in Drosophila*. Nature 453, 1244-1247 (2008). https://pubmed.ncbi.nlm.nih.gov/18509336/
11. Kuntz, S., Poeck, B., Strauss, R. *Visual working memory in Drosophila*. Journal of Neurogenetics 26, 351-364 (2012). https://pubmed.ncbi.nlm.nih.gov/22815538/
12. `eonsystemspbc/fly-brain` public repository. https://github.com/eonsystemspbc/fly-brain
13. `NeLy-EPFL/flygym` public repository. https://github.com/NeLy-EPFL/flygym
14. Pires, P. M., Zhang, L., Parache, V., Abbott, L. F., Maimon, G. *Converting an allocentric goal into an egocentric steering signal*. Nature 626, 808-818 (2024). https://www.nature.com/articles/s41586-023-07006-3
