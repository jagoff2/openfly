# Spontaneous-State Program

## Purpose

This note frames the spontaneous-state workstream that follows the current
best-branch investigation in `docs/best_branch_e2e_investigation.md`.

The point is not to pretend the public stack already contains the exact
internal state logic used in any private demo. The point is to define a
public-equivalent, biologically plausible endogenous-activity program that can
be tested honestly inside this repo.

## What "Cold-Starts Dead" Means Here

The current brain backend is not numerically dead.

Existing evidence already shows:

- the strict real-brain run can drive motion while `zero_brain` collapses to
  zero commands:
  - `docs/brain_control_validation.md`
- the strongest current branch is target-modulated under realistic vision:
  - `docs/best_branch_e2e_investigation.md`

But the current stack still tends to cold-start into a functionally quiescent
state when it begins from a neutral reset and does not receive enough immediate
downstream recruitment.

In this document, "cold-starts dead" means:

- the run begins from a near-neutral internal state
- pre-motor and descending activity is too weak or too sparse to sustain an
  embodied control policy
- the body-control boundary sees little useful drive until strong external
  structure happens to recruit it

This is a transfer/readiness problem, not proof that the recurrent brain model
is disconnected or fake.

## Why The Current Cold-Start Fails

The current evidence points to four concrete causes.

### 1. The runtime reset is too empty

The embodied runs currently start from a clean reset rather than from a
biologically occupied ongoing brain state. That makes the first control cycles
depend almost entirely on immediate sensory drive plus whatever recurrent
activity the model can bootstrap from near zero.

### 2. Target-bearing structure is stronger upstream than downstream

`docs/best_branch_e2e_investigation.md` shows that strong target-bearing
structure exists in upstream visual and relay families, while the monitored
descending readout carries much weaker target-bearing signal.

So the current problem is not "the visual system sees nothing." The problem is
that enough structured activity is not reaching the embodied decoder early and
reliably enough.

### 3. The embodied decoder is evaluated at the narrowest point in the chain

The body only moves when the monitored downstream population crosses the
decoder's effective action threshold. If the state starts too quiet, the whole
closed loop can remain below useful control magnitude even when upstream brain
activity is present.

### 4. The existing controls already rule out the easy false explanations

The current evidence already rules out several simpler stories:

- not hidden body fallback:
  - `zero_brain` stays near zero
- not "the backend is dead":
  - real-brain runs can produce sustained commands
- not total absence of visual structure:
  - no-target and target runs both show strong scene-driven recruitment

That leaves endogenous state and state-dependent transfer as the next honest
gap to address.

## What Biologically Plausible Endogenous Activity Means In This Repo

For this project, endogenous activity means ongoing internal neural state that:

- exists before the first salient target event
- is expressed on the brain side, not as body-side scripted locomotion
- is distributed and bounded rather than a single hard-coded locomotor pulse
- can change sensory-to-descending gain or readiness
- remains present in matched `target`, `no_target`, and blank-control runs

Acceptable mechanisms may include:

- structured nonzero initial conditions
- bounded recurrent baseline drive
- slow state variables or gain terms that operate inside the brain/bridge state
- stochastic or quasi-stochastic neural perturbations if they are applied as
  brain-state perturbations rather than motor commands

This workstream does **not** count any of the following as endogenous activity:

- direct actuator commands
- decoder-side idle drive
- target-conditioned steering pulses
- injecting specific locomotor outputs as a startup prosthetic
- any state mechanism that only exists in the target-present condition

The standard is: if the mechanism would be better described as "controller
assist" than as "ongoing neural state," it does not qualify.

## What The Program Must Explain

The spontaneous-state program is only successful if it explains all three of
these at once:

1. why the current reset remains too quiet at the embodied output boundary
2. what endogenous state should exist before stimulus-driven recruitment
3. how that state improves closed-loop readiness without becoming a shortcut

Any proposal that improves behavior but cannot answer those three questions is
not yet good enough.

## Validation Criteria

We will judge the spontaneous-state program against four validation gates.

### Gate 1: Anti-shortcut integrity

The same endogenous-state mechanism must be enabled consistently across matched
conditions:

- `target`
- `no_target`
- blank / symmetric-vision control when available
- `zero_brain` ablation of the whole brain path

It must not inject body commands directly, and it must not depend on target
presence to exist.

### Gate 2: Neural-state plausibility

Before strong target recruitment, the brain-side logs should show:

- nonzero but bounded baseline activity
- repeatable state statistics across seeds/config repeats
- no runaway saturation
- no large persistent left/right bias under symmetric control conditions
- evidence that the state reaches relay and/or descending populations more
  effectively than the dead-cold-start baseline

The goal is not pure noise. The goal is structured readiness.

### Gate 3: Behavioral honesty

The spontaneous-state branch must improve cold-start behavior in ways that are
useful but not suspicious.

Required qualitative outcomes:

- shorter time from reset to first meaningful command
- less "dead air" at run start
- stronger sustained control than the dead-cold-start baseline
- no fake target tracking in `no_target` or blank controls
- no replacement of visual guidance with generic always-on locomotion
- preserved pause / move structure and structured turning in spontaneous runs,
  consistent with [behavior_target_set.md](/G:/flysim/docs/behavior_target_set.md)

Required quantitative comparisons should include at least:

- `completed_full_duration`
- `nonzero_command_cycles`
- `avg_forward_speed`
- `net_displacement`
- `turn_response_latency`
- `steer_sign_match_rate`
- pre-stimulus neural variance or analogous baseline-state summary

The endogenous-state branch should beat the dead-cold-start branch on startup
readiness while preserving the existing negative-control logic.

### Gate 4: Control-condition separation

A biologically plausible spontaneous state should increase readiness, not erase
condition differences.

So after adding endogenous activity, the repo should still show:

- `zero_brain` near zero at the body-command boundary
- stronger target-bearing modulation in `target` than `no_target`
- near-symmetric baseline commands under blank or symmetric visual conditions
- trajectory diversity across seeds without collapsing into random thrashing
- no collapse of the branch into synthetic continuous pursuit expectations that
  are not part of the canonical real-fly target set

If the state simply makes every condition walk hard in the same way, it has
failed the program even if displacement numbers improve.

## Required Evidence Artifacts

This workstream should not be judged from a single demo video.

The minimum evidence set is:

- matched `target`, `no_target`, and `zero_brain` runs
- matched activation captures for those runs
- saved logs and metrics for startup latency and baseline-state statistics
- a comparison note that states whether the endogenous mechanism improved
  readiness, symmetry, and target-modulated control simultaneously

## Public Gap And Honesty Boundary

There is no public evidence in this repo that the exact Eon-demo spontaneous
state implementation is available. We therefore should not claim exact
mechanistic parity.

What we can claim, if the work succeeds, is narrower and honest:

- the public-equivalent stack no longer cold-starts into an unrealistically
  dead control boundary
- the improvement came from a brain-side endogenous-state mechanism rather than
  a controller shortcut
- matched controls show the mechanism preserves target-modulated behavior and
  negative-control integrity

## Immediate Next Actions

The first spontaneous-state steps should stay diagnostic:

1. add matched activation captures for `target`, `no_target`, and `zero_brain`
2. add baseline-state summaries for the first control window after reset
3. test whether the current dead-cold-start problem is primarily:
   - missing baseline occupancy
   - weak relay transfer
   - or overly silent descending recruitment
4. only after that, evaluate candidate endogenous-state mechanisms

This keeps the workstream aligned with the no-shortcuts boundary established in
`docs/best_branch_e2e_investigation.md`.
