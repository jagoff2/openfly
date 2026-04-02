# OpenFly: Public-Equivalent Embodied Drosophila Brain-Body Reconstruction

Author: Codex  
Project: OpenFly Reconstruction  
Date: 2026-04-02

## Abstract

OpenFly is a local reconstruction of a public-equivalent embodied adult *Drosophila* simulation stack built from open components: a FlyWire-derived whole-brain recurrent model, FlyGym / NeuroMechFly v2 embodiment, realistic vision, a closed-loop bridge, and reproducible evaluation code. The repo does not claim access to unpublished Eon glue. It implements the missing public-equivalent integration layer, then treats every promoted result as a falsification problem rather than a demo-assembly problem.

The current system now supports five strong claims. First, a persistent realistic-vision, whole-brain, embodied closed loop runs locally on this machine and emits videos, logs, metrics, activation captures, tests, and benchmarks. Second, early public-anchor interfaces failed for identifiable structural reasons: they destroyed too much visual structure and compressed output too aggressively. Third, a calibrated retinotopic splice plus descending readout established the first credible brain-driven, visually modulated embodied locomotion branch. Fourth, the public neural-measurement parity program against Aimon 2023 and Schaffer 2023 exposed major evaluator and replay-semantics bugs; repairing those bugs changed the baseline materially and proved that part of the earlier timing gap was methodological rather than biological. Fifth, the active lawful target branch now uses a splice-only visual path with temporal retinotopic evidence and removes the previous catastrophic target overlap failure in the exact full `2.0 s` parity-time run.

The current strongest negative result is equally important. The branch is now safer, but still not behaviorally correct as target-oriented control. In the current exact `2.0 s` splice-only target run, the target never comes closer than `3.0065 mm`, with `0` cycles under `3.0 mm`, but fixation remains weak with `fixation_fraction_20deg = 0.076`, `fixation_fraction_30deg = 0.113`, and full-run `bearing_reduction_rad = -0.9223`. So the present state of the project is not "solved parity." It is a real, lawful, closed-loop embodied brain stack with meaningful progress, a repaired evaluation basis, and a much narrower residual control problem.

## Current Status

| Area | Status | Best current evidence |
| --- | --- | --- |
| Whole-brain backend | real and persistent | `src/brain/pytorch_backend.py` |
| Embodied body simulation | real and persistent | `src/body/flygym_runtime.py` |
| Realistic vision | enabled in production path | `src/vision/`, `src/bridge/visual_splice.py` |
| Closed-loop integration | real and online | `src/runtime/closed_loop.py` |
| Brain-driven behavior | yes, under matched controls | target / no-target / zero-brain artifacts and metrics |
| Public neural parity program | active and materially repaired | Aimon + Schaffer harnesses under `src/analysis/` |
| Exact target overlap failure | fixed on lawful branch | `outputs/requested_2s_endogenous_routed_target_parity_temporal_splice_only/flygym-demo-20260402-003922` |
| Robust target fixation | not yet | same run still shows weak fixation metrics |
| Exact neuron-to-neuron parity | not achieved | public identity gaps and residual control mismatch remain |

## Hard Rules

This repo is governed by an explicit honesty boundary.

- No target metadata shortcuts into control.
- No controller-side heuristics that directly enforce target pursuit or avoidance.
- No decoder-side or shadow-decoder-side promotion from visual-area activity directly into body control.
- No "fake" spontaneous state inserted downstream of the brain.
- Visual / object effects on behavior must flow through lawful sensory inputs, brain dynamics, and descending outputs only.

These rules are recorded in:

- `TASKS.md`
- `ASSUMPTIONS_AND_GAPS.md`
- `PROGRESS_LOG.md`
- `context.md`

## Hardware and Runtime

All reported work targets one local workstation:

| Component | Value |
| --- | --- |
| Host OS | Windows 11 |
| Linux runtime | WSL2 |
| GPUs | 2x NVIDIA RTX 5060 Ti 16 GB |
| RAM | 192 GB |
| Main orchestrator | Python |
| Main embodied runtime | FlyGym / MuJoCo |
| Main brain backend | Torch CUDA / CPU fallback |

Current embodied parity-time target runs are still CPU-dominated because realistic vision remains the dominant runtime cost in the production stack.

## System Overview

The production loop has five persistent subsystems:

1. `src/body/flygym_runtime.py`
   - live FlyGym world
   - embodied body state
   - realistic visual observations
2. `src/vision/feature_extractor.py`
   - stateful realistic-vision feature extraction
   - temporal salience / looming evidence
3. `src/bridge/visual_splice.py`
   - retinotopic current injection into the whole-brain model
   - now includes transient temporal-delta drive
4. `src/brain/pytorch_backend.py`
   - persistent FlyWire-scale recurrent backend
   - endogenous backend-dynamics path
5. `src/bridge/decoder.py` and `src/runtime/closed_loop.py`
   - descending readout
   - synchronized control loop
   - logging, metrics, activation capture, video output

The current backend carries `138,639` neurons over `15,091,983` weighted edges.

## Main Findings

### 1. The local public-equivalent stack is real

The repo now runs:

- brain-only benchmarks
- body-only benchmarks
- realistic-vision workloads
- full closed-loop embodied demos
- activation capture and synchronized side-by-side visualizations
- matched control conditions

This is not an offline notebook replay. It is a persistent closed loop with explicit run directories, JSONL logs, metrics CSVs, videos, and activation artifacts.

### 2. Early "clean public-anchor" interfaces were structurally wrong

The first plausible bridge hypotheses failed for two main reasons:

- input interfaces collapsed too much visual structure
- motor output was compressed through too small and too generic a descending readout

This was useful. It narrowed the real bottlenecks instead of hiding them behind superficially moving demos.

### 3. A body-free splice program and wider descending readout established the first credible embodied branch

Earlier work in this repo showed:

- a calibrated retinotopic splice can carry structured visual evidence into the whole-brain model
- a wider descending-only readout materially improves embodied traversal without optic-lobe-to-body shortcuts

That branch remains an important historical milestone because it proved the stack could be brain-driven and visually modulated without fake motor floors.

### 4. A decoder-internal brain-latent branch improved perturbation-linked steering on the honest non-spontaneous path

The strongest older perturbation result remains the decoder-internal brain-latent turn branch. In a matched `2.0 s` jump assay, it improved:

| Metric | Honest baseline | Brain-latent branch |
| --- | ---: | ---: |
| Jump turn-bearing correlation | `0.3215` | `0.8177` |
| Jump bearing-recovery fraction | `-0.8210` | `-0.5658` |
| Fixation fraction at `20 deg` | `0.043` | `0.059` |

The matched `zero_brain` control stayed silent, which matters because it keeps the interpretation honest: the steering structure came from brain-side state, not a controller prosthetic.

### 5. The spontaneous public-parity program found real bugs before it found biology

The Aimon and Schaffer parity program was initially showing stubbornly weak timing results. That was not just "the model is still wrong." The harness itself had real faults.

The main repaired issues were:

- poisoned Aimon replay semantics
- invalid regressor slicing
- duplicate top-level `encoder:` config blocks silently overwriting gains
- zero-lag-only timing scoring
- misphased body-feedback channels
- fit-head blindness to slow endogenous backend state
- exafference and arousal sharing the same internal drive

Those fixes live in:

- `src/analysis/aimon_canonical_dataset.py`
- `src/analysis/aimon_spontaneous_fit.py`
- `src/analysis/public_neural_measurement_harness.py`
- `src/analysis/public_body_feedback.py`
- `src/bridge/encoder.py`
- `src/brain/pytorch_backend.py`

### 6. Repaired Aimon exact-identity assays changed the baseline materially

The most honest Aimon target is no longer cross-experiment `B350 -> B1269`. That setup is not an exact neuron-identity comparison because the public export exposes region-component traces rather than exact matched neurons.

The corrected exact-identity lane is now within-trial windowed replay. The repaired `B350_forced_walk` held-out result at:

- `outputs/metrics/aimon_b350_forced_window_routed_v5_replayfix/aimon_spontaneous_fit_summary.json`

produced:

| Metric | Held-out mean |
| --- | ---: |
| `pearson` | `0.2315` |
| `nrmse` | `0.7011` |
| `abs_error` | `0.01027` |
| `sign` | `0.6040` |
| `lagged_pearson` | `0.7311` |
| `lagged_sign` | `0.8195` |
| `best_lag_seconds` | `0.0254` |

Meaning:

- the old timing miss was substantially inflated by harness bugs
- the model is producing the right broad pattern much more often than earlier numbers implied
- exact waveform and timing are still not solved

### 7. The lawful temporal visual patch fixed the catastrophic target-overlap failure

The key recent control improvement was not a decoder trick. It was a lawful sensory-path fix:

- temporal visual features in `src/vision/feature_extractor.py`
- retinotopic temporal-delta current in `src/bridge/visual_splice.py`
- reset-safe visual state in `src/bridge/controller.py`

The active routed target/no-target configs are now splice-only on the visual encoder side:

- `encoder.visual_gain_hz = 0.0`
- `encoder.visual_looming_gain_hz = 0.0`

So target interaction is now driven only by:

- realistic visual input
- retinotopic temporal splice
- whole-brain dynamics
- descending output

## Exact Target Result: Old Failure vs Current Lawful Splice-Only Branch

Old exact `2.0 s` target run:

- local artifact: `outputs/requested_2s_endogenous_routed_target_parity/flygym-demo-20260401-223021`
- minimum target distance: `0.5780 mm`
- cycles under `1.5 mm`: `86`
- cycles under `2.0 mm`: `119`

Current exact `2.0 s` splice-only lawful run:

- local artifact: `outputs/requested_2s_endogenous_routed_target_parity_temporal_splice_only/flygym-demo-20260402-003922`
- minimum target distance: `3.0065 mm`
- cycles under `1.5 mm`: `0`
- cycles under `2.0 mm`: `0`
- cycles under `3.0 mm`: `0`

This is the most important recent embodied result. The previous "target effectively walks through the fly" failure is gone.

## What the Current Exact `2.0 s` Target Run Means

From `outputs/requested_2s_endogenous_routed_target_parity_temporal_splice_only/flygym-demo-20260402-003922/summary.json`:

| Metric | Value |
| --- | ---: |
| `sim_seconds` | `2.0` |
| `avg_forward_speed` | `8.5699 mm/s` |
| `path_length` | `17.1226 mm` |
| `net_displacement` | `12.4068 mm` |
| `trajectory_smoothness` | `0.3161` |
| `mean_target_distance` | `6.8912 mm` |
| `fixation_fraction_20deg` | `0.076` |
| `fixation_fraction_30deg` | `0.113` |
| `turn_alignment_fraction_all` | `0.6065` |
| `bearing_reduction_rad` | `-0.9223` |

Interpretation:

- The branch is materially safer.
- It is still not correct target-oriented behavior.
- The remaining problem is no longer catastrophic overlap.
- The remaining problem is weak fixation and weak full-run bearing improvement.

In plain terms: the fly no longer lets the target get on top of it, but it still does not robustly lock onto the target and steer around it the way the final system should.

## Public Neural Measurement Findings

### Aimon 2023

What is real now:

- full staged public source
- canonical export
- exact-identity within-trial windowed harness
- repaired replay semantics
- lag-aware scoring

What is not admissible:

- reading cross-experiment `B350 -> B1269` as exact 1:1 neural parity

Why:

- the public canonical target is region-component space
- identity confidence is not exact FlyWire neuron mapping

### Schaffer 2023

What is real now:

- staged NWB sessions
- canonical exporter
- same-session scoring harness
- explicit continuity-preserving fit path

What is limited:

- different sessions do not share one ROI space
- full-session retests are too slow for the normal iteration loop
- future retests must be subset-only

### Net scientific takeaway

The public parity program still matters, but its role is now narrower and more honest:

- Aimon is good for within-trial and regime-structure checks once the harness is repaired
- Schaffer is good for same-session continuity and timing checks on explicit subsets
- neither dataset currently justifies a strong exact-neuron parity claim

## Strongest Current Claims

The strongest claims now supported by evidence are:

1. A realistic-vision, real-body, whole-brain closed loop runs locally and reproducibly.
2. The stack produces brain-driven behavior under matched controls.
3. The public neural-parity harnesses are real and materially repaired.
4. The active lawful splice-only target branch removes the previous catastrophic overlap failure without target metadata or decoder/controller shortcuts.
5. The remaining embodied target problem is now a narrower fixation / target-bearing control problem, not generic sensory collapse.

## Strongest Current Non-Claims

This repo does **not** currently justify the following claims:

- exact parity with private Eon internals
- exact neuron-to-neuron visual mapping
- robust biologically correct target pursuit / fixation
- exact public-neural measurement parity
- a final solved living-fly spontaneous-state mechanism

## Reproduction Commands

Environment bootstrap and checks:

```bash
bash scripts/bootstrap_wsl.sh
bash scripts/bootstrap_env.sh
bash scripts/check_cuda.sh
bash scripts/check_mujoco.sh
python -m pytest tests/test_imports.py -q
```

Benchmarks:

```bash
python benchmarks/run_brain_benchmarks.py
python benchmarks/run_body_benchmarks.py
python benchmarks/run_vision_benchmarks.py
```

Main embodied production run:

```bash
python -m runtime.closed_loop --config configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_brain_endogenous_routed.yaml --mode flygym --duration 2.0
```

Short exact-identity Aimon replay:

```bash
python scripts/run_aimon_windowed_fit.py --help
```

## Repo Reading Order

For a technical operator re-entering cold:

1. `README.md`
2. `REPRO_PARITY_REPORT.md`
3. `TASKS.md`
4. `PROGRESS_LOG.md`
5. `ASSUMPTIONS_AND_GAPS.md`
6. `context.md`
7. `docs/timing_mismatch_root_cause.md`
8. `docs/public_neural_measurement_parity_program.md`

## Key Local Artifacts

Current exact splice-only target run:

- `outputs/requested_2s_endogenous_routed_target_parity_temporal_splice_only/flygym-demo-20260402-003922/demo.mp4`
- `outputs/requested_2s_endogenous_routed_target_parity_temporal_splice_only/flygym-demo-20260402-003922/summary.json`
- `outputs/requested_2s_endogenous_routed_target_parity_temporal_splice_only/flygym-demo-20260402-003922/run.jsonl`

Earlier lawful temporal retest:

- `outputs/requested_1p1s_endogenous_routed_target_parity_temporal/flygym-demo-20260401-235448/summary.json`

Old overlap failure reference:

- `outputs/requested_2s_endogenous_routed_target_parity/flygym-demo-20260401-223021/summary.json`
- `outputs/requested_2s_endogenous_routed_target_parity/flygym-demo-20260401-223021/run.jsonl`

Repaired Aimon exact-identity baseline:

- `outputs/metrics/aimon_b350_forced_window_routed_v5_replayfix/aimon_spontaneous_fit_summary.json`

## Final Verdict

OpenFly is now a real, local, lawful, public-equivalent embodied fly brain-body stack with significant positive results and equally significant falsifications. The system no longer deserves the older simplistic reading that "nothing works" or that all remaining mismatches are purely biological. Major harness and replay faults were repaired. The exact catastrophic target-overlap failure was removed. The active target branch is now lawful, splice-only on the visual side, and materially better.

The remaining unsolved problem is not whether the stack can run or whether the target can be kept from crossing directly through the fly. The remaining unsolved problem is how to convert lawful visual object evidence, through the public brain and descending interface, into strong, stable fixation and target-oriented control without introducing any bypass.
