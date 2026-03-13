# Neck-Output Mapping Strategy

This document records the next major direction after the current calibrated
UV-grid embodied branch and after the first hybrid motor-latent experiment.

It is intentionally explicit because this repo is being developed under
`AGENTS.md` with conversation-history compaction expected. The point of this
document is to preserve the real state of the project and the exact logic for
what should happen next.

## 1. Current state of the project

The current strongest embodied branch is still:

- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated.yaml`

That branch already demonstrates:

- real FlyGym body
- real FlyVis realistic vision
- a grounded visual splice based on shared `cell_type + side + bin`
- a real recurrent whole-brain backend
- descending/efferent output readout rather than optic-lobe-as-motor shortcuts
- matched `target`, `no_target`, and `zero_brain` controls

The most recent hybrid motor-latent branch:

- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive.yaml`

is more plausible at the controller interface, because it does not treat the
body as only a left/right throttle. It modulates:

- left/right CPG amplitude
- left/right CPG frequency
- sensory correction gains
- reverse gating

But the first calibration still does not beat the current two-drive production
branch overall.

What matters here is the interpretation:

- the project is no longer blocked mainly on the visual splice
- it is now blocked mainly on the *motor semantics* of the output side

## 2. What is wrong with the current output path

Even after the descending-only expansion and the UV-grid splice calibration,
the repo still mostly does this:

1. observe a large recurrent descending population
2. collapse it into a small number of hand-authored signals
3. project that into a controller abstraction

The strongest current branch still compresses descending output into:

- `left_drive`
- `right_drive`

The first hybrid motor-latent branch improved that to:

- `left_amp`
- `right_amp`
- `left_freq_scale`
- `right_freq_scale`
- `retraction_gain`
- `stumbling_gain`
- `reverse_gate`

That is better, but the mapping is still hand-authored.

So the remaining problem is not simply:

- "tune turn gain harder"

The remaining problem is:

- "infer what the descending / neck-output population collectively wants the body to do"

## 3. Correct target: a neck-output motor basis

The correct near-term target is *not* full muscles yet.

The public stack does not give us a clean end-to-end:

- brain
- neck connective
- VNC
- motor neuron
- muscle
- biomechanics

mapping that can simply be switched on.

So the correct target is:

- a **neck-output motor basis**

Meaning:

1. monitor a broad, public-grounded descending/efferent population
2. learn what body-level actions those outputs collectively imply
3. map them into a small controller-facing latent space
4. keep that latent space explicit, testable, and replaceable later

This is the honest substitute for the currently missing full public VNC /
muscle pathway.

## 4. Why this is the right next step

This direction is supported by the current evidence:

### 4.1 The visual side is already alive

The current embodied branch already shows:

- `zero_brain` collapses movement
- target-bearing steering correlation is strong
- target presence modulates the descending branch

So the project is not mainly blocked on "is the brain seeing anything?"

### 4.2 The remaining visible failure looks motor-side

In the new hybrid motor-latent artifacts, visual review suggests:

- the fly approaches the target
- then reduces forward progression
- then appears to try to reorient when the target leaves the frontal field
- but the turn execution is weak or ineffective

That is a motor-interface failure mode more than an input failure mode.

### 4.3 Hand-picking a tiny output subset is no longer good enough

The output side should stop depending primarily on:

- a tiny fixed DN set
- plus a small manually chosen supplemental list

Those sets were useful as bridge-building scaffolding, but they are now the
main remaining abstraction bottleneck.

## 5. What we should do next

This section is the operative plan.

### 5.1 Monitor the full public descending/efferent population

Stop treating a tiny hand-picked subset as the whole neck output.

Instead:

- monitor a broad, anatomically grounded public descending/efferent set
- log those outputs during real embodied runs
- compare them under:
  - `target`
  - `no_target`
  - `zero_brain`
  - later: controlled left/right target conditions

What this gives us:

- a *population-level observational atlas*
- which descending groups track:
  - target bearing
  - frontal target acquisition
  - forward progression
  - yaw / turn episodes
  - stop / reverse episodes

This is the first step because it removes a major blind spot in the current
repo. Right now we know too much about a tiny selected output slice and not
enough about the broader neck-output population.

### 5.2 Build a causal motor-response atlas

Once the broader outputs are monitored, we need causal evidence.

That means:

- stimulate descending pairs or groups one at a time
- measure what the current body/controller stack actually does

At minimum measure:

- forward velocity
- yaw rate
- net displacement
- body rotation
- if possible:
  - leg phase shifts
  - stance timing
  - adhesion timing
  - correction-rule activation

This produces a *response atlas*:

- descending group -> body/controller effect

Important:

- this atlas is not "the biological truth"
- it is the truth of the current public-equivalent embodied stack

That is exactly what we need in order to stop guessing about what groups should
do.

### 5.3 Factor that atlas into motor primitives

After observational + causal data exist, derive a small motor basis.

Likely primitives:

- propulsion / walk-enable
- left turn
- right turn
- stop / reverse
- stance stabilization / posture

These should be *fit from data*, not guessed from names.

This basis is the clean replacement for the current manually authored decoder.

### 5.4 Decode the broad descending population into that motor basis

Once the basis exists:

- decode the broader descending vector into the latent basis
- then map that latent basis into the FlyGym controller

This is still an abstraction, but it is much cleaner than:

- directly forcing a few DN names into a two-number throttle

### 5.5 Only then add calibrated body feedback into the brain

The user is correct that a full solution likely needs calibrated body feedback.

But the clean order is:

1. output-side mapping first
2. feedback-side calibration second

Why:

- right now the output interface is still the dominant uncertainty
- adding feedback before cleaning up the output side would mix two unknowns at once

The likely later feedback channels are:

- joint state
- contact / load
- stance or slip proxies
- controller correction-state proxies

Those should map into:

- ascending or mechanosensory brain inputs

but only after the output side is less ad hoc.

## 6. What we should not do

Do not:

- go back to `P9` prosthetic modes as a primary solution
- keep tuning scalar visual summaries
- treat optic-lobe or relay classes as motor outputs
- assume that a slightly better turn gain solves the whole problem
- assume the current two-drive branch is the final output abstraction

## 7. Why direct neck-output-to-leg mapping is still hard

The user is right to push for:

- a clean mapping from neck outputs to the legs

But the missing public piece is still large.

The public stack does not give us a directly validated live chain from:

- broad descending outputs
to
- VNC circuitry
to
- motor neurons
to
- muscles
to
- joint torques

So a direct, clean, biologically complete mapping is still a
"draw-the-rest-of-the-owl" problem.

The correct response is not to pretend that problem is solved.

The correct response is:

- make the surrogate layer explicit
- derive it from data rather than hand-picking it
- keep it narrow enough to test
- keep it documented so it can later be replaced by a better public chain

## 8. Immediate repo tasks implied by this strategy

### Task A. Broad descending monitoring

Add monitoring-only support so the repo can log a wide descending/efferent
population during the current strongest embodied runs without yet using all of
those groups for control.

Deliverables:

- config support for monitoring-only populations
- logs containing broader descending group rates
- summary scripts correlating those rates with target-bearing and motion

### Task B. First observational neck-output atlas

Run the strongest embodied branch again with broad descending monitoring.

Deliverables:

- target + monitored run
- no-target + monitored run
- zero-brain monitored baseline if needed
- summary tables:
  - group activity vs target bearing
  - group activity vs frontalness
  - group activity vs forward speed
  - group asymmetry vs yaw

### Task C. First causal motor-response atlas

Create a script that perturbs descending groups or pairs and measures body
response under the current controller.

Deliverables:

- reproducible perturbation script
- response CSV / JSON
- summary doc

### Task D. Data-driven motor-basis decoder

Replace the current hand-authored multidrive mapping with one informed by the
atlas.

This is the first place where a truly better motor decoder is likely to emerge.

## 10. Update After T091-T093

The first three steps of this strategy are now materially in place.

### T091 completed

Broad descending/efferent monitoring was added to the current strongest
embodied branch.

Evidence:

- `src/bridge/decoder.py`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_monitored.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_monitored_no_target.yaml`

### T092 completed

The first observational atlas now exists.

Evidence:

- `docs/descending_monitoring_atlas.md`
- `outputs/metrics/descending_monitor_neck_output_atlas.csv`
- `outputs/metrics/descending_monitor_neck_output_atlas.json`

Main takeaway:

- the current branch is using a distributed descending code
- likely forward candidates:
  - `DNg97`
  - `DNp103`
  - `DNp18`
- likely turn-sensitive candidates:
  - `DNp71`
  - `DNpe040`
  - `DNpe056`
- likely target-conditioned weak gate candidates:
  - `DNpe016`
  - `DNae002`

### T093 completed

The first causal descending motor-response atlas now exists.

Evidence:

- `docs/descending_motor_atlas.md`
- `outputs/metrics/descending_motor_atlas.csv`
- `outputs/metrics/descending_motor_atlas.json`
- `outputs/metrics/descending_motor_atlas_summary.csv`
- `outputs/metrics/descending_motor_atlas_summary.json`

Main takeaway:

- strongest current forward drivers:
  - `DNp103`
  - `DNp18`
  - `DNg97`
- strongest current mirrored turn driver:
  - `DNpe040`
- weaker mirrored turn candidate:
  - `DNpe056`
- ambiguous current role:
  - `DNp71`
- little or no causal effect in the present stack:
  - `DNpe031`
  - `DNae002`

### Consequence

The project now has enough output-side evidence to stop hand-authoring the next
motor decoder from names alone.

The next active task is now clearly:

- `T094`: derive a fitted neck-output motor basis

## 9. Current conclusion

The next logical step is no longer to keep hand-tuning the visual splice.

It is to build an explicit, data-driven neck-output mapping layer:

- first observationally
- then causally
- then as a fitted motor basis

That is the shortest honest path toward:

- fuller embodiment
- less hand-authored motor semantics
- and eventually better body feedback back into the brain
