# Endogenous Spontaneous Replacement Plan

## Goal

Replace the current structured-background spontaneous surrogate with a
production spontaneous mechanism that is acceptable under the repo hard rule.

Accepted sources of spontaneous endogenous state:

- richer intrinsic cell dynamics
- graded transmission
- synaptic heterogeneity
- neuromodulatory state

Disallowed as final mechanism:

- structured external background drive
- latent OU background forcing
- reset-time voltage jitter used as the source of ongoing activity
- any other backend-internal surrogate prior that injects ongoing state from
  outside the actual neuron/synapse dynamics

## Current blocker in code

The current spontaneous mechanism is still implemented as an input prior in
[pytorch_backend.py](/G:/flysim/src/brain/pytorch_backend.py):

- `reset()` samples tonic background rates and latent OU state
- `_refresh_background_rates()` constructs `background_rates`
- `_build_inputs()` injects them through `self.rates += self.background_rates`

That makes the current mechanism diagnostic-only, not promotable.

## Shortest honest path

1. Freeze the current surrogate spontaneous branch as diagnostic-only.
2. Build a new production backend that generates ongoing state internally.
3. Fit that backend to public neural measurements with a tiny readout so the
   mechanism, not the head, carries the score.
4. Only after neural parity improves, resume downstream decoder and embodiment
   work.

## Production backend target

The minimum acceptable replacement is a mixed-mode generalized LIF backend with
the following endogenous state sources:

### 1. Intrinsic cell dynamics

Add per-neuron or per-cell-group:

- membrane time-constant heterogeneity
- threshold / reset heterogeneity
- spike-triggered or voltage-coupled adaptation current `w`
- intrinsic filtered membrane-noise state `eta`

Purpose:

- remove the absorbing silent fixed point without injecting a rate floor
- generate bounded spontaneous occupancy from neuron dynamics themselves

### 2. Graded transmission

Add a graded release state `z` for selected cell groups:

- `spiking` neurons emit spike events only
- `graded` neurons emit a filtered voltage-dependent release variable
- `mixed` neurons can do both

Purpose:

- stop forcing the fly brain into a spike-only recurrence model
- recover continuous signaling structure that imaging-space recordings can
  plausibly reflect

### 3. Synaptic heterogeneity

Replace the current single filtered synapse state with at least:

- fast excitatory
- slow excitatory
- fast inhibitory
- slow inhibitory
- modulatory

Each class needs its own:

- time constant
- reversal potential or equivalent effective sign/gain semantics
- class- or group-specific gain scale

Purpose:

- create real endogenous temporal diversity
- move spontaneous-state generation into network dynamics rather than input
  forcing

### 4. Neuromodulatory state

Add one or more internal slow modulatory states driven by designated
modulatory-population activity, not by external latent forcing.

Minimum useful set:

- walk/arousal-like state
- exafference / forced-walk-like state

Those states may modulate:

- membrane time constants
- thresholds
- release gain
- synaptic gain
- adaptation strength

Purpose:

- create slow internally generated state transitions
- explain spontaneous-vs-forced regime differences without OU latent forcing

## Code-level implementation order

### Stage A: scaffolding

Files:

- [src/brain/pytorch_backend.py](/G:/flysim/src/brain/pytorch_backend.py)
- new backend config section in relevant `configs/*.yaml`
- new tests under [tests/](/G:/flysim/tests)

Work:

- split the old global `MODEL_PARAMS` into grouped parameter tables
- add a new production backend mode, separate from the old diagnostic surrogate
- preserve the current surrogate path only under an explicitly disqualified
  diagnostic flag

Acceptance:

- no behavior work yet
- import and smoke tests green

### Stage B: intrinsic dynamics

Work:

- add adaptation current `w`
- add intrinsic filtered noise state `eta`
- add grouped membrane / threshold heterogeneity

Acceptance:

- with zero sensory input and zero surrogate background forcing, the brain can
  sustain bounded non-silent activity for `>= 10 s`
- no runaway excitation
- no collapse to the old silent fixed point

### Stage C: graded transmission

Work:

- add graded release state `z`
- add group-level `spiking` / `graded` / `mixed` mode assignment
- add recurrence paths for both spike events and graded release

Acceptance:

- continuous state statistics materially change relative to the spike-only path
- public-imaging fit improves with a tiny readout, not just with a rich head

### Stage D: synaptic heterogeneity

Work:

- replace the single synaptic low-pass with multi-class synaptic states
- add class-wise kinetics and sign semantics

Acceptance:

- spontaneous mesoscale temporal structure and held-out public parity both
  improve relative to the intrinsic-only stage

### Stage E: neuromodulatory state

Work:

- add one or two slow internal modulatory states driven by designated
  modulatory populations
- let those states gate excitability / adaptation / release / synaptic gain

Acceptance:

- spontaneous-vs-forced Aimon comparator improves without reintroducing
  external latent forcing
- Schaffer continuous-session carryover improves

## Public-data fitting strategy

The mechanism fit must be backend-first, not head-first.

### Datasets

- Aimon 2023:
  - primary for spontaneous-vs-forced walk state transitions and slow regime
    structure
- Schaffer 2023:
  - primary for continuous-session persistence, dF/F observation realism, and
    behavior-linked residual structure

### What gets optimized first

Optimize backend mechanism parameters first:

- intrinsic noise timescales and amplitudes
- adaptation parameters
- graded transmission mixture coefficients
- synapse-class time constants and gains
- modulatory-state time constants and coupling
- grouped heterogeneity scales by super-class / family

Keep the readout deliberately tiny during this stage:

- per-trace affine terms
- very low-rank linear map only

Do not let a rich readout head absorb the mismatch.

### Objective stack

Use a weighted combination of:

- Aimon held-out public-trace fit
- Aimon spontaneous-vs-forced comparator metrics
- Schaffer within-session continuous holdout metrics
- existing spontaneous mesoscale validation metrics

### Current target gates

Mechanism gate:

- no surrogate background forcing
- bounded ongoing activity for `>= 10 s`

Neural-parity gate:

- Aimon held-out `mean_pearson_r > 0.10`
- Aimon held-out `mean_nrmse < 0.30`
- Schaffer within-session holdout `mean_pearson_r > 0.20`
- Schaffer within-session holdout `mean_nrmse < 0.30`

Mesoscale gate:

- bilateral family coupling remains in the current validated living band
- structure ratio remains `> 2.0`
- residual lag-1 temporal structure remains high
- walk-linked global modulation remains real

Head-dominance gate:

- switching from the tiny readout to the richer current reduced projection must
  improve held-out metrics by less than `15%` relative
- if the larger head yields a much larger jump, the backend mechanism is still
  underfit

## What stays frozen until this passes

Do not prioritize any of these until the endogenous replacement clears the
neural-parity gates:

- Creamer parity tuning
- target-jump / refixation tuning
- new decoder-promotion work
- new body-control operating-point work
- any branch that claims spontaneous realism from the current surrogate

## Final criterion

The real goal is met only when:

- the production spontaneous state is generated by endogenous neuron/synapse
  dynamics under the hard rule
- public neural-measurement parity improves on held-out data with a small
  readout
- the current surrogate path is no longer carrying the scientific claim
