# Spontaneous-State Backend Design

## Scope

This note documents the first backend-side spontaneous-state candidate in
`src/brain/pytorch_backend.py`.

This is not a claim that biologically complete spontaneous fly-brain dynamics
 are solved. It is a narrower claim:

- the old backend had an absorbing silent cold-start state
- the new candidate adds endogenous activity sources inside the brain backend
- the new sources are explicit, bounded, and measurable
- no decoder, body, or target-conditioned shortcut was added

## Why The Old Backend Cold-Started Dead

Before this work, the Torch backend reset to:

- `spikes = 0`
- `conductance = 0`
- `delay_buffer = 0`
- `v = vRest = v0 = -52 mV`

and only advanced from:

- public sensory Poisson input
- recurrent weighted spikes
- optional direct external current

With no external perturbation, all three terms were zero, so the model sat at an
absorbing silent fixed point.

## Candidate Mechanism

The current candidate stays entirely inside `WholeBrainTorchBackend`.

### 1. Sparse tonic occupancy

At reset, a sparse subset of neurons receives tonic background rates sampled
from a lognormal distribution.

Purpose:

- break the absorbing silent fixed point
- preserve heterogeneity instead of giving every neuron the same floor
- keep the background weak enough that it does not become a hidden locomotor
  policy

### 2. Low-rank slow latent fluctuations

The backend can also sample a small set of latent background modes. Each mode
projects signed loadings into a sparse subset of neurons and evolves with a
slow Ornstein-Uhlenbeck-like process.

Purpose:

- create slow structured fluctuations rather than iid white noise
- allow opposite-sign subpopulations instead of uniform excitation
- approximate the mixed-timescale residual dynamics seen in adult fly whole-brain
  imaging without inventing a specialized unpublished control circuit

### 3. Voltage heterogeneity at reset

The candidate can add a small reset-time membrane-voltage jitter.

Purpose:

- avoid exact membrane synchrony at reset
- make the first post-reset windows less pathologically identical

## Why This Is Biologically Stricter Than Existing Shortcuts

The candidate is stricter than:

- decoder idle drive
- body-side fallback
- `public_p9_context`
- target-conditioned startup forcing
- runtime-side hidden preroll loops

Those alternatives either inject control too close to the actuator boundary or
condition the startup logic on task context. The current candidate lives inside
the brain state itself and is applied equally before any target-specific event.

## Current Config Surface

The new experimental config surface under `brain.spontaneous_state` is:

- `mode`
- `active_fraction`
- `lognormal_mean_hz`
- `lognormal_sigma`
- `max_rate_hz`
- `voltage_jitter_std_mv`
- `latent_count`
- `latent_target_fraction`
- `latent_loading_std_hz`
- `latent_ou_tau_s`
- `latent_ou_sigma_hz`

These are all opt-in. The default claim configs remain unchanged.

## Current Best Candidate

The current best brain-only candidate is not the original random sparse latent
pilot. It is a more constrained central-family bilateral variant:

- bilateral families are built from the public FlyWire annotation supplement
- the family pool is restricted to:
  - `central`
  - `ascending`
  - `visual_projection`
  - `visual_centrifugal`
  - `endocrine`
- giant bilateral families are excluded with a maximum per-side family size cap
- tonic occupancy is sampled at the family level, then lifted into both sides
  with strong shared coupling
- slow latent modes are also family-structured, with a dominant shared
  bilateral component and only weak antisymmetric variance

This is the first candidate in the repo that simultaneously gives:

- non-dead ongoing state
- low spontaneous motor-side lateral bias
- positive homologous left/right family correlation
- retained pulse perturbability across multiple seeds

## Logging And Audit Support

The workstream now has explicit instrumentation:

- `WholeBrainTorchBackend.state_summary()`
- `brain_backend_state` in closed-loop logs via `src/bridge/controller.py`
- `scripts/run_spontaneous_state_audit.py`

The audit emits:

- per-window global state summaries
- per-window monitored-population summaries
- benchmark CSV rows
- plots for global traces and monitor heatmaps

## Rejected Mechanisms

The following remain outside the honesty boundary:

- any decoder-side idle drive
- any body-side locomotor seed
- any target-only spontaneous mode
- any default direct drive into `P9`, `DNa01`, `DNa02`, or other motor-facing
  readouts
- any hidden bridge preroll that advances the brain before the first logged
  control step

## Current Limits

The current candidate still has major biological limits:

- no explicit homologous left/right pairing in the latent modes
- no connectome-derived compartment-specific neuromodulatory model
- no specialized persistent internal-state subcircuit
- seed-to-seed sensitivity remains high
- spontaneous motor-side lateral bias still appears in some seeds
- no matched embodied `target` / `no_target` / `zero_brain` validation yet

So the correct current label is:

- brain-side endogenous-state pilot
- partial success on bounded ongoing activity
- not yet promotable as a production embodiment branch
