# Iterative Brain Decoding System

## Purpose

This repo does not have a solved full-brain decode. It now has a repeatable
system for getting there without smuggling in new decoder/body shortcuts.

The system has two parts:

1. every embodied run now emits the activation artifact from the same run
2. the activation artifact now feeds a decoding-cycle workbench that ranks
   relay candidates, monitor expansions, and structured signal families for the
   next iteration

This is a deliberate shift away from hand-picking a few neuron families based
only on intuition.

The canonical behavior target set for that decode loop is:

- [behavior_target_set.md](/G:/flysim/docs/behavior_target_set.md)

So the workbench should rank candidate signals against real adult-fly behavior
targets, not against synthetic continuous-pursuit expectations.

## Data Sources The System Is Allowed To Use

The decoding system is constrained to public artifacts that are already in the
repo or publicly accessible:

- FlyWire annotations and the local completeness-filtered brain ID space
- the public Shiu / `fly-brain` whole-brain backend
- FlyVis realistic-vision activity and the repo's splice cache metadata
- the repo's structural VNC tools built from MANC and semantic FlyWire bridges
- public whole-brain activity/state literature as validation priors, not as
  direct motor labels

This matters because exact neuron-identity FlyVis -> FlyWire mapping and exact
brain -> VNC raw-ID crosswalks are still not public.

## Default Activation Capture

The normal `run_closed_loop()` path now attempts to generate:

- `activation_side_by_side.mp4`
- `activation_overview.png`
- `activation_capture.npz`
- `activation_summary.json`

from the same embodied run directory.

Implementation:

- [closed_loop.py](/G:/flysim/src/runtime/closed_loop.py)
- [session.py](/G:/flysim/src/visualization/session.py)
- [activation_viz.py](/G:/flysim/src/visualization/activation_viz.py)

The capture is skipped only when the run does not expose the required data
shape, for example when realistic-vision arrays or brain state tensors are not
available.

## Decoding-Cycle Workbench

The workbench is implemented in:

- [iterative_decoding.py](/G:/flysim/src/analysis/iterative_decoding.py)
- [run_iterative_decoding_cycle.py](/G:/flysim/scripts/run_iterative_decoding_cycle.py)

It consumes:

- run config
- activation capture bundle
- run log
- FlyWire annotation table

It produces:

- family-level scores against target bearing, forward speed, and drive asymmetry
- behavior metrics that separate target engagement from spontaneous locomotor richness
- current monitor scores
- monitor-expansion recommendations
- relay-probe recommendations
- a structured-signal library for candidate families
- explicit guardrails so candidate families are first promoted as
  monitoring-only probes rather than directly into control

Generated artifacts:

- [iterative_decoding_cycle_summary.json](/G:/flysim/outputs/metrics/iterative_decoding_cycle_summary.json)
- [iterative_decoding_cycle_family_scores.csv](/G:/flysim/outputs/metrics/iterative_decoding_cycle_family_scores.csv)
- [iterative_decoding_cycle_monitor_scores.csv](/G:/flysim/outputs/metrics/iterative_decoding_cycle_monitor_scores.csv)
- [iterative_decoding_cycle_monitor_expansion.csv](/G:/flysim/outputs/metrics/iterative_decoding_cycle_monitor_expansion.csv)
- [iterative_decoding_cycle_relay_candidates.csv](/G:/flysim/outputs/metrics/iterative_decoding_cycle_relay_candidates.csv)

Matched-condition behavior artifacts:

- [relay_monitored_behavior_conditions_0p2s.csv](/G:/flysim/outputs/metrics/relay_monitored_behavior_conditions_0p2s.csv)
- [relay_monitored_behavior_conditions_0p2s.json](/G:/flysim/outputs/metrics/relay_monitored_behavior_conditions_0p2s.json)
- [relay_target_specificity_0p2s_summary.json](/G:/flysim/outputs/metrics/relay_target_specificity_0p2s_summary.json)
- [target_engagement_metric_pivot.md](/G:/flysim/docs/target_engagement_metric_pivot.md)

## First Concrete Output

Running the workbench and the new behavior analysis on matched relay-monitored
controls produced a cleaner diagnosis:

- the fly is already locomotor-rich in both `target` and `no_target`
- `zero_brain` still collapses controller richness
- the remaining failure is signed steering transfer and fixation, not pure
  locomotor recruitment

Current best monitored target-bearing correlation:

- `0.2192` for `DNg97`

Top recommended monitor / relay candidates from the first cycle:

- `AVLP370a`
- `AN_multi_67`
- `LHAV3e6`
- `AN_AVLP_16`
- `CB1505`
- `LT57`
- `AN_AVLP_PVLP_5`
- `AVLP047`

These are not promoted as motor effectors. They are promoted as structured
relay checkpoints. The newer target-specific comparison against the no-target
baseline further narrows the next relay shortlist to families like `MTe14`,
`LTe62`, `VCH`, `CB0828`, and `LT43`.

## Staged Decoding Plan

### 1. Monitoring First

Expand monitored relay families before changing control. The workbench-ranked
families should enter the run as monitoring-only groups with matched
`target` / `no_target` / `zero_brain` controls.

### 2. Decoder-Internal Brain Latent

Fit a richer brain-side latent basis from observed relay and descending state,
but keep it inside the primary decoder path. The correct seam is the decoder's
brain-state readout, not controller arbitration.

### 3. VNC Shadow Decode

Run the semantic/structural VNC layer in shadow mode against the same captured
brain activity. It should constrain or explain the descending basis before it
replaces it.

### 4. Embodied Promotion

Only promote a new relay, descending, or VNC layer into live control after it
improves the control-condition comparison without reintroducing shortcuts.

### 5. Spontaneous-State Validation

Treat spontaneous-state only as a background condition and startup-readiness
improvement. It must not become a disguised motor floor.

## Guardrails

The workbench hard-codes these constraints into its summary:

- keep decoder/body shortcuts disabled
- promote new families first as monitoring-only relay checkpoints
- require matched `target` / `no_target` / `zero_brain` controls before
  promotion into control
- treat spontaneous-state as a background condition, not a motor floor
- shadow-test VNC semantics against descending latents before actuator
  promotion
- reject candidate branches that only improve speed/displacement while
  worsening literature-grounded fixation / orientation behavior
- avoid promoting families based on behaviors that are real only in odor,
  reward, or threat contexts unless those contexts are actually present

## Honest Status

This is not a complete decoding of the fly brain. It is the first repo-native
system that turns recorded embodied runs into a repeatable decode cycle with
public-data guardrails.

The current next branch from this system is documented in
[turn_voltage_decode_iteration.md](/G:/flysim/docs/turn_voltage_decode_iteration.md):

- steering-relevant structure is much clearer in lateralized monitored voltages
  than in the current sampled descending firing-rate slice
- the next monitored cohort is therefore built from turn-voltage family
  asymmetry, not generic bilateral activation
- a shadow voltage-turn decoder already outperforms the live sampled turn
  signal on the recorded target run, but it remains shadow-only until it
  survives fresh online controls

The first decoder-internal promotion of that idea is now tracked in
[brain_latent_turn_decoder.md](/G:/flysim/docs/brain_latent_turn_decoder.md).

That branch now has a completed live `target` / `no_target` / `zero_brain`
trio and should be treated as the current honest perturbation-improvement
branch, not as final parity.
