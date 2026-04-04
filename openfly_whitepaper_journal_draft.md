# OpenFly: Public-Equivalent Embodied Drosophila Reconstruction

This manuscript draft mirrors `README.md` so the journal draft and the
operator-facing whitepaper stay synchronized.

This repository is a local, public-equivalent reconstruction of an Eon-style embodied adult fly stack built from public components and explicit glue code:

- FlyWire-derived whole-brain simulation
- FlyGym / NeuroMechFly v2 embodiment
- realistic vision
- persistent online closed loop
- parity harnesses against public neural and behavioral datasets

## Claim Boundary

OpenFly has achieved these things:

- a real persistent whole-brain plus body plus realistic-vision closed loop on this machine
- lawful brain-driven behavior under matched `target`, `no_target`, and `zero_brain` controls
- repaired public-neural parity harnesses that changed the baseline materially
- a lawful splice-only parity target branch that removed the earlier catastrophic target-overlap failure
- a corrected Creamer-style parity assay that now measures command-side locomotor modulation on the active parity brain

OpenFly has not achieved these things:

- exact parity with any private Eon internal stack
- exact neuron-to-neuron visual identity continuity
- robust biologically correct target fixation or close-range regulation
- a working treadmill-ball mechanics seam on the active parity Creamer path
- full biological motor equivalence

## Current Canonical Replication Paths

### 1. Embodied parity path

Canonical embodied configs:

- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_brain_endogenous_routed.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_endogenous_routed.yaml`

This is the active parity brain and control path. It is not the older non-spontaneous jump branch.

Key enforced properties:

- brain backend: `torch`
- brain dynamics: `grouped_glif_scaffold`
- spontaneous source: `endogenous`
- parity timing:
  - `brain.dt_ms = 0.1`
  - `runtime.body_timestep_s = 0.0001`
  - `runtime.control_interval_s = 0.002`
- parity enforcement:
  - `runtime.parity_path.required = true`
  - `runtime.parity_path.profile = flygym_full_parity_v1`
- visual path:
  - realistic vision enabled
  - retinotopic `uv_grid` splice enabled
  - `visual_splice.temporal_delta_scale = 2.0`
  - coarse encoder visual drive disabled:
    - `encoder.visual_gain_hz = 0.0`
    - `encoder.visual_looming_gain_hz = 0.0`
- control path:
  - `decoder.command_mode = hybrid_multidrive`
  - `runtime.control_mode = hybrid_multidrive`
- latest latent turn code is active through:
  - `decoder.turn_voltage_signal_library_json = outputs/metrics/jump_brain_driven_turn_latent_2s_spontaneous_refit_library.json`

The parity guard lives in `src/runtime/closed_loop.py` and blocks non-parity `flygym` runs unless a call site opts into diagnostic non-parity use explicitly.

### 2. Creamer parity path

Canonical Creamer runner:

- `scripts/run_creamer2018_parity_open_loop.py`

Builder source:

- `src/analysis/creamer_parity_open_loop.py`
- `src/analysis/creamer_parity_short.py`

Important point: the Creamer parity builders inherit from the same active no-target endogenous routed parity config:

- `BASE_PARITY_CONFIG_PATH = configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_endogenous_routed.yaml`

So the Creamer parity assays use the same active brain family, the same endogenous backend, the same splice-only visual path, the same latest latent turn library, and the same enforced `hybrid_multidrive` parity path. Only the scene geometry and open-loop treadmill stimulus differ.

### 3. Historical but non-canonical branch

The older decoder-internal brain-latent turn branch is still an important historical result for jump perturbation recovery, but it is not the current canonical replication path. It remains useful as historical evidence that brain-side latent state improved non-spontaneous perturbation recovery without a control bypass.

## Comparison with Related Public Work: `erojasoficial-byte/fly-brain`

As of the 2026-04-04 review of the public repo, OpenFly and `erojasoficial-byte/fly-brain` should be read as emphasizing different strengths. OpenFly is narrower in scope and more conservative in claim boundary. `erojasoficial-byte/fly-brain` presents a broader public feature surface and a more turnkey packaged demo.

### Architecture

OpenFly is narrower, more modular, and more falsification-oriented. The canonical path is explicitly constrained to parity-enforced configs, splice-only visual input, `hybrid_multidrive`, matched controls, and named evidence artifacts. `erojasoficial-byte/fly-brain` presents a broader bundled system with multimodal modules, two-fly experiments, plasticity, and bundled paper regeneration, which is a wider public feature surface than OpenFly currently claims.

The key architectural caveat is the actual bridge. In `brain_body_bridge.py`, the public motor seam is explicitly a DN firing-rate decoder feeding `[left_drive, right_drive]` into FlyGym's `HybridTurningController`, with behavior routed through bridge-level mode logic rather than a richer descending-control substrate. OpenFly is more limited, but its active bridge is also described more narrowly and more precisely.

### Honesty Boundary

OpenFly states its unresolved gaps directly: no private Eon glue, no exact neuron-identity visual continuity, no solved close-range target regulation, no solved treadmill-ball mechanics seam, and no full biological motor equivalence. That makes its claim boundary comparatively conservative.

By comparison, the README language in `erojasoficial-byte/fly-brain` is broader than some of the currently exposed bridge implementation. `brain_body_bridge.py` contains explicit thresholded mode selection with the stated priority `escape > grooming > feeding > walking`, bridge-level tactile / bitter / olfactory escape backups, and direct sound / olfactory turning gains. `fly_embodied.py` also adds a manual proboscis hinge because the stock body lacks one, and directly overwrites the free-joint quaternion and angular velocity during flight stabilization. Those are legitimate engineering scaffolds, but they should be interpreted as scaffolding rather than as evidence of a fully lawful end-to-end closed-loop path.

### Reproducibility

`erojasoficial-byte/fly-brain` is easier to rerun as the authors' packaged story because it bundles sessions, figures, PDFs, and one-shot regeneration scripts. OpenFly is easier to audit because it exposes canonical configs, focused tests, matched controls, named artifact paths, and preserved negative results instead of only packaging the showcase path.

### Likely Biological Fidelity

Both repos are still far from real fly. OpenFly's main weakness is that it openly does not yet know the full lawful sensor-to-brain-to-descending mapping, so it keeps its claim surface narrow. `erojasoficial-byte/fly-brain` aims at broader biological richness, but `visual_system.py` explicitly injects firing rates into the early visual pathway because of a scale mismatch, and its bridge-level behavior routing is more synthetic than the broadest README language implies. The practical consequence is that OpenFly is more conservative for the specific causal claims it currently makes, while `erojasoficial-byte/fly-brain` is better read as an ambitious embodied connectome demo platform.

### Vision Pipeline Comparison

The clearest technical contrast between the two repos is the visual pathway from scene input to motor consequence.

OpenFly's active parity path uses FlyGym realistic vision as the production sensor source, then advances the FlyVis visual network step-by-step on that payload. The active embodied parity configs explicitly force coarse visual encoder gains to zero, keep `brain_context.mode = none`, and require `visual_splice.enabled = true`, so visual influence reaches the brain only through the retinotopic splice path rather than through a bilateral salience shortcut.

`erojasoficial-byte/fly-brain` also starts from FlyGym compound-eye observations, but the public code converts those observations into hand-computed visual firing rates. In `visual_system.py`, the early visual stack is described as a manually computed brightness and contrast pipeline spanning photoreceptor, lamina, medulla, and T2 layers. The same file also states that the early visual system cannot be propagated faithfully through the public connectome model because of a scale mismatch, and therefore firing rates are injected manually.

The early-processing consequence is important. OpenFly preserves a full FlyVis activity field each cycle through `retina_mapper.flygym_to_flyvis(...)` and `vision_network.forward_one_step(...)`, then derives both coarse diagnostics and retinotopic splice currents from that internal activity tensor. `erojasoficial-byte/fly-brain` instead computes visual rates directly from brightness or contrast rules. In the current public path, `process_visual_layers()` effectively narrows live injection to T2 contrast-driven rates because wider early-layer injection produced excessive network noise. That makes the public vision path pragmatic and functional, but more synthetic than a full lawful visual cascade.

The injection seam also differs. OpenFly uses a retinotopic inferred splice between FlyVis node groups and FlyWire annotation groups. `VisualSpliceInjector` builds exact cell-type overlaps, bins them spatially in `uv_grid`, tracks baseline and temporal deltas, and injects direct current by FlyWire root id. That seam is still inferred rather than exact neuron-identity continuity, but it remains spatially structured and tied to the active visual activity field. `erojasoficial-byte/fly-brain` uses direct rate injection into selected visual layers, which is a more explicit engineering surrogate for the unavailable early visual dynamics.

OpenFly also carries more explicit temporal visual structure in the active parity path. The feature extractor tracks `balance_velocity`, `forward_salience_velocity`, `looming_evidence`, and `receding_evidence`, and the splice itself adds a temporal term through `temporal_delta_scale`. In the active parity configs, the splice-side temporal current is the operative visual path because the coarse visual encoder is disabled. By contrast, the public `erojasoficial-byte/fly-brain` visual code is primarily framewise brightness and contrast transformation, so temporal structure must arise later from downstream connectome dynamics or bridge logic rather than from a richer internal visual-state pipeline.

Finally, the motor consequence is different in granularity. OpenFly routes visual consequences through the whole-brain backend and then into `HybridDriveCommand`, which carries left and right gait amplitude, left and right frequency scaling, correction gains, and a reverse gate before `ConnectomeTurningFly` maps those latents into the hybrid locomotor controller. `erojasoficial-byte/fly-brain` routes descending activity through DN firing-rate decoding into `[left_drive, right_drive]`, then into FlyGym's `HybridTurningController`. That is a simpler and coarser motor seam.

For that reason, the two repos should be interpreted differently. `erojasoficial-byte/fly-brain` currently offers the broader visual-behavior demo surface. OpenFly currently offers the narrower but more internally constrained visual path from realistic visual input through internal visual activity, retinotopic brain injection, whole-brain integration, and richer locomotor latents.

### Comparative Summary

- More impressive public scope and packaging: `erojasoficial-byte/fly-brain`
- Stronger audit artifact and stricter claim boundary: OpenFly
- More conservative causal interpretation of current public results: OpenFly

Sources reviewed for this comparison:

- [`erojasoficial-byte/fly-brain` repo README](https://github.com/erojasoficial-byte/fly-brain)
- [`brain_body_bridge.py`](https://raw.githubusercontent.com/erojasoficial-byte/fly-brain/main/brain_body_bridge.py)
- [`fly_embodied.py`](https://raw.githubusercontent.com/erojasoficial-byte/fly-brain/main/fly_embodied.py)
- [`visual_system.py`](https://raw.githubusercontent.com/erojasoficial-byte/fly-brain/main/visual_system.py)

## Current Best-Supported Findings

### A. The stack is real

The project now has:

- persistent whole-brain state
- persistent embodied FlyGym state
- realistic vision in the production path
- structured logging, plots, videos, metrics, and activation captures
- matched target, no-target, zero-brain, and ablation controls

Core production code:

- `src/brain/pytorch_backend.py`
- `src/body/flygym_runtime.py`
- `src/bridge/visual_splice.py`
- `src/bridge/decoder.py`
- `src/runtime/closed_loop.py`

### B. The Aimon parity baseline changed after the harness was repaired

Artifact:

- `outputs/metrics/aimon_b350_forced_window_routed_v5_replayfix/aimon_spontaneous_fit_summary.json`

Corrected held-out exact-identity within-trial result:

| Metric | Value |
| --- | ---: |
| `pearson` | `0.2315` |
| `nrmse` | `0.7011` |
| `abs_error` | `0.01027` |
| `sign` | `0.6040` |
| `lagged_pearson` | `0.7311` |
| `lagged_sign` | `0.8195` |
| `best_lag_seconds` | `0.0254` |

Meaning:

- the old timing miss was materially inflated by harness and replay bugs
- the repaired baseline is healthier than the older continuity/body-feedback runs implied
- exact waveform parity is still not solved

### C. The lawful splice-only target branch removed the old overlap failure

Clean exact comparison:

- old run:
  - `outputs/requested_2s_endogenous_routed_target_parity/flygym-demo-20260401-223021`
- corrected run:
  - `outputs/requested_2s_endogenous_routed_target_parity_temporal_splice_only/flygym-demo-20260402-003922`

Old exact `2.0 s` target run:

- minimum target distance: `0.5780 mm`
- cycles under `1.5 mm`: `86`
- cycles under `2.0 mm`: `119`

Current exact `2.0 s` splice-only parity run:

- minimum target distance: `3.0065 mm`
- cycles under `1.5 mm`: `0`
- cycles under `2.0 mm`: `0`
- cycles under `3.0 mm`: `0`

That failure mode is fixed.

### D. The remaining target defect is now close-range encounter regulation, not generic blindness

The cleaner `2.0 s` splice-only run above is safer, but still weak on fixation:

- `fixation_fraction_20deg = 0.076`
- `fixation_fraction_30deg = 0.113`
- `bearing_reduction_rad = -0.9223`

The later full-parity `10.0 s` multi-target run makes the remaining defect sharper:

- artifact:
  - `outputs/requested_10s_endogenous_routed_multitarget_birdeye_activation_parity/flygym-demo-20260402-104437`
- it completed stably for `10.0 s`
- it moved strongly:
  - `avg_forward_speed = 19.3977 mm/s`
  - `path_length = 193.9386 mm`
- but the encounter geometry is still wrong:
  - minimum distance `0.4423 mm` at `1.998 s`
  - minimum absolute bearing `0.0053 rad` at `1.968 s`
  - exactly one close encounter episode under `5 mm`, lasting about `0.632 s`
  - final target distance `69.58 mm`

Current interpretation under the repo's encounter-realism rule:

- the fly is object-responsive
- it does not need to track forever
- but it still closes too hard and then loses the interaction
- the remaining defect is underdamped close-pass regulation

### E. The corrected Creamer result is now command-side, sign-correct, and partial

Primary artifact:

- `outputs/creamer2018_parity_open_loop_2p0_commandmetrics_v1/metrics/creamer2018_parity_open_loop_pair_summary.json`

The current assay interpretation is explicit:

- primary readout: `command_forward_proxy`
- treadmill ball speed: secondary embodied mechanics check only

Reason:

- on this stack the brain does not drive raw leg joints directly
- it drives final locomotor latents through the hybrid locomotor controller
- so command-side locomotor modulation is the right primary Creamer observable for the current parity controller

Corrected front-to-back result:

| Condition | Pre | Stimulus | Fold change | Delta |
| --- | ---: | ---: | ---: | ---: |
| Baseline `command_forward_proxy` | `0.7100` | `0.0886` | `0.1248` | `-0.6214` |
| `T4/T5` ablated `command_forward_proxy` | `0.6477` | `0.1176` | `0.1816` | `-0.5301` |

Interpretation:

- front-to-back motion suppresses locomotor output on the active parity brain
- that sign is consistent with Creamer 2018
- `T4/T5` ablation weakens the effect modestly but does not abolish it

The treadmill seam remains broken and should be treated separately:

- both baseline and ablated runs have `forward_speed = 0.0` throughout the scored valid rows
- direct probes showed strong leg motion but zero raw treadmill qvel and `ncon = 0`, consistent with a downstream contact or traction failure on the tethered-ball path

## Historical Negative Results That Still Matter

These remain important and should not be rewritten as successes:

- strict public anchors alone were too weak to drive useful embodied locomotion
- richer visual splice fidelity did not automatically transfer to better embodiment
- semantic VNC bridging was technically real but remained a behavioral parity failure
- controller-side or decoder-side steering promotion from visual areas was explicitly rejected as cheating and is not part of the active path

## What This Repo Does Not Claim

- exact MANC-to-FlyWire neuron identity continuity
- exact neuron-to-neuron parity against Aimon or Schaffer
- correct treadmill-ball mechanics on the active parity Creamer path
- solved spontaneous-state physiology
- solved target fixation, pursuit, or close-range social interaction

## Hard Rules

- No target metadata shortcuts into control.
- No controller-side heuristics that directly enforce pursuit or avoidance.
- No decoder-side or shadow-decoder-side promotion from visual-area activity into body control.
- No hidden motor floors outside the lawful brain-to-descending path.
- Active embodied runs must use the full parity path and `hybrid_multidrive`.

These rules are enforced in code and continuity files:

- `src/runtime/closed_loop.py`
- `TASKS.md`
- `PROGRESS_LOG.md`
- `ASSUMPTIONS_AND_GAPS.md`
- `context.md`

## Quick Start

Environment bootstrap:

```bash
bash scripts/bootstrap_wsl.sh
bash scripts/bootstrap_env.sh
bash scripts/check_cuda.sh
bash scripts/check_mujoco.sh
python -m pytest tests/test_imports.py -q
```

Focused parity-path validation:

```bash
python -m pytest tests/test_closed_loop_smoke.py tests/test_bridge_unit.py tests/test_vnc_spec_decoder.py -q
python -m pytest tests/test_visual_speed_control_metrics.py tests/test_creamer_parity_open_loop.py -q
```

## Reproduction Commands

Canonical production runs on this machine use WSL2, `MUJOCO_GL=egl`, `PYTHONPATH=src`, and the `flysim-full` micromamba environment. The commands below are the exact active parity invocations, not shortened host-side approximations.

### Canonical embodied parity target run

```bash
wsl.exe --cd /mnt/g/flysim bash -lc "
  export MUJOCO_GL=egl
  export PYTHONPATH=src
  /root/.local/bin/micromamba run -n flysim-full \
    python -m runtime.closed_loop \
    --config configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_brain_endogenous_routed.yaml \
    --mode flygym \
    --duration 2.0
"
```

### Canonical no-target parity run

```bash
wsl.exe --cd /mnt/g/flysim bash -lc "
  export MUJOCO_GL=egl
  export PYTHONPATH=src
  /root/.local/bin/micromamba run -n flysim-full \
    python -m runtime.closed_loop \
    --config configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_endogenous_routed.yaml \
    --mode flygym \
    --duration 2.0
"
```

### Canonical command-side Creamer parity pair

```bash
wsl.exe --cd /mnt/g/flysim bash -lc "
  export MUJOCO_GL=egl
  export PYTHONPATH=src
  /root/.local/bin/micromamba run -n flysim-full \
    python scripts/run_creamer2018_parity_open_loop.py \
    --mode flygym \
    --output-root outputs/creamer2018_parity_open_loop_2p0_commandmetrics_v1 \
    --duration 2.0 \
    --stimulus-start 0.5 \
    --stimulus-end 2.0 \
    --scene-velocity -30.0 \
    --treadmill-settle-time 0.2
"
```

### Benchmarks

```bash
python benchmarks/run_brain_benchmarks.py
python benchmarks/run_body_benchmarks.py
python benchmarks/run_vision_benchmarks.py
```

## Key Evidence Paths

- Active target parity config:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_brain_endogenous_routed.yaml`
- Active no-target parity config:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_endogenous_routed.yaml`
- Parity guard:
  - `src/runtime/closed_loop.py`
- Active decoder:
  - `src/bridge/decoder.py`
- Corrected Aimon exact-identity result:
  - `outputs/metrics/aimon_b350_forced_window_routed_v5_replayfix/aimon_spontaneous_fit_summary.json`
- Exact splice-only target result:
  - `outputs/requested_2s_endogenous_routed_target_parity_temporal_splice_only/flygym-demo-20260402-003922/summary.json`
- Full-parity `10 s` multi-target target artifact:
  - `outputs/requested_10s_endogenous_routed_multitarget_birdeye_activation_parity/flygym-demo-20260402-104437/summary.json`
- Corrected Creamer pair:
  - `outputs/creamer2018_parity_open_loop_2p0_commandmetrics_v1/metrics/creamer2018_parity_open_loop_pair_summary.json`

## Known Limitations

- The full parity embodied path is slow and presently CPU-bound.
- The treadmill-ball seam is still mechanically broken on the active parity Creamer path.
- The active target branch still shows underdamped close-pass behavior.
- Exact neuron-identity visual mapping remains unavailable from public artifacts.
- The repo contains many historical outputs and experimental branches. Only the parity-enforced endogenous routed configs and the corrected Creamer open-loop runner should be treated as current canonical replication paths.

## Bottom Line

OpenFly is no longer just a demo scaffold or a negative result map. It is a real public-equivalent whole-brain embodied fly stack with:

- a lawful parity-enforced embodied brain path
- materially repaired public-neural evaluation
- a corrected command-side Creamer assay on the active brain
- and a much narrower remaining target-control problem

The strongest honest current statement is:

> OpenFly now reproduces a lawful public-equivalent embodied fly stack that is visually responsive, brain-driven, and partially parity-consistent on public neural and behavioral assays, but it still fails on close-range target regulation, exact neural identity continuity, and treadmill-ball mechanics.
