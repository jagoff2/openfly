# Canonical Behavior Target Set

## Purpose

This repo should only optimize for behaviors that are grounded in real adult
`Drosophila melanogaster` behavior.

The current embodied target assay is useful, but a moving target in closed loop
is only a valid benchmark insofar as it overlaps with real fly behaviors such
as:

- spontaneous locomotion and pauses
- structured turning / reorientation
- landmark fixation and approach
- short-timescale refixation after perturbation
- short-timescale orientation memory

This document is the canonical behavior spec for future decoding, embodiment,
and parity work.

## Hard Rule

Behavior evaluation may use logged target state as analysis metadata.

Behavior control may not use logged target state as a direct control input.

If a branch improves because it reads privileged target metadata rather than
because the visual-brain-body loop produced the behavior, it fails this spec.

## Real Adult-Fly Behaviors We Should Target

| Behavior | What real flies actually do | Why it belongs in this repo | Grounding |
| --- | --- | --- | --- |
| Spontaneous roaming / exploration | Flies walk without an explicit target, show exploratory structure, and often interact strongly with arena boundaries and salient landmarks. | `no_target` should still look alive rather than silent. | Soibam et al. 2012: https://pubmed.ncbi.nlm.nih.gov/22574279/ ; Fox et al. 2006: https://pubmed.ncbi.nlm.nih.gov/17151232/ |
| Intermittent locomotion with pauses | Walking is not continuous drive; flies stop, restart, and switch modes. | The spontaneous-state branch should preserve pause / move transitions instead of forcing always-on locomotion. | Strauss & Heisenberg 1990: https://pubmed.ncbi.nlm.nih.gov/2121965/ ; Gattuso et al. 2025: https://pubmed.ncbi.nlm.nih.gov/40244663/ |
| Structured turning / saccadic reorientation | Walking heading changes are organized and often occur in brief turns rather than only smooth continuous curvature. | Steering evaluation should reward plausible reorientation structure, not just raw bearing reduction. | Geurten et al. 2014: https://pmc.ncbi.nlm.nih.gov/articles/PMC4205811/ ; Yang et al. 2024: https://pubmed.ncbi.nlm.nih.gov/37904997/ |
| Landmark fixation / approach | Flies orient toward and stabilize salient visual objects such as vertical dark bars or stripes. | The current target assay is valid when treated as a landmark-orientation benchmark. | Moore et al. 2014: https://pmc.ncbi.nlm.nih.gov/articles/PMC6605338/ ; Xiong et al. 2020: https://pmc.ncbi.nlm.nih.gov/articles/PMC7843020/ ; Maimon et al. 2008: https://pmc.ncbi.nlm.nih.gov/articles/PMC2861965/ |
| Refixation after perturbation | When a stabilized landmark or goal cue is displaced, flies can make corrective turns to recover the prior heading / goal relation. | This is the correct grounded form of "reacquisition" for the current vision-first branch and is closer to menotaxis-style cue recovery than to arbitrary moving-target pursuit. | de Bivort et al. 2020: https://pmc.ncbi.nlm.nih.gov/articles/PMC7703559/ ; Pires et al. 2024: https://www.nature.com/articles/s41586-023-07006-3 ; Clemens et al. 2025: https://pmc.ncbi.nlm.nih.gov/articles/PMC12212441/ |
| Short-timescale orientation memory | Flies can preserve orientation relative to a previously shown visual landmark for seconds after it disappears. | This supports bounded persistence after brief target loss, but not an unlimited pursuit memory claim. | Neuser et al. 2008: https://pubmed.ncbi.nlm.nih.gov/18509336/ ; Kuntz et al. 2012: https://pubmed.ncbi.nlm.nih.gov/22815538/ ; Kuo et al. 2019: https://pmc.ncbi.nlm.nih.gov/articles/PMC6754076/ |
| Walking-linked global brain state | Whole-brain activity changes with spontaneous walking and turning even without explicit target stimulus. | The spontaneous-state backend should create bounded, structured readiness rather than a silent cold start. | Aimon et al. 2023: https://elifesciences.org/articles/85202 ; Mann et al. 2024: https://pubmed.ncbi.nlm.nih.gov/38109544/ |

## Real Behaviors That Are Context-Specific Or Out Of Scope For The Current Vision-First Branch

These are real adult-fly behaviors, but they should not become default
acceptance targets for the current branch unless the matching context is added.

| Behavior | Status in this repo | Grounding |
| --- | --- | --- |
| Odor-loss local search | Real, but not a first-pass vision-only target. | Alvarez-Salvado et al. 2018: https://pubmed.ncbi.nlm.nih.gov/30129438/ ; Demir et al. 2020: https://pubmed.ncbi.nlm.nih.gov/33140723/ |
| Sugar-triggered local search / reward return | Real, but requires reward-state and search context. | Murata et al. 2018: https://pubmed.ncbi.nlm.nih.gov/30546299/ |
| Hunger-state foraging modulation | Real, but requires explicit internal-state and reward assumptions. | Landayan et al. 2018: https://pubmed.ncbi.nlm.nih.gov/29636522/ |
| Freeze / flee responses to looming threat | Real, but requires a threat stimulus and state-conditioned defensive pathway. | Zacarias et al. 2018: https://pubmed.ncbi.nlm.nih.gov/30209268/ ; Sen et al. 2024: https://www.nature.com/articles/s41586-024-07854-7 |
| Courtship-style pursuit of a moving conspecific | Real, but sex- and context-specific; not the default interpretation of the current generic target assay. | Clemens et al. 2025: https://pmc.ncbi.nlm.nih.gov/articles/PMC12212441/ |

## Behaviors We Must Not Treat As Canonical Defaults

- Generic indefinite smooth pursuit of an arbitrary moving target.
- Perfectly continuous curvature with no pauses or reorientation structure.
- Always-on locomotion under `no_target`.
- Search behavior claims that are only supported by odor, reward, or threat
  assays.
- Any "living fly" claim based purely on speed or displacement.

## Interpretation Of The Current Jump Assay

The current `target_jump` assay is informative, but it is stricter than the
best grounded central-complex perturbation papers.

- In the strongest grounding paper for allocentric-goal to egocentric-steering
  conversion, flies recover heading relative to a displaced visual cue during a
  menotaxis-style perturbation task.
- In this repo, after the jump the target continues moving tangentially in world
  space, so strict frontal refixation within `2.0 s` is a harsher criterion than
  simple recovery toward a prior heading / goal relation.
- Therefore a branch can show biologically plausible corrective steering after
  the jump even when it does not re-enter a `20 deg` frontal fixation cone.

This means jump evaluation should prioritize:

- corrective turn latency
- signed turn-bearing correlation after perturbation
- bearing-recovery fraction over time
- bounded heading / goal persistence

before treating strict frontal refixation as the only success signal.

## Condition Matrix

The canonical condition matrix is:

- `target`
- `no_target`
- `zero_brain`
- spontaneous-state `off`
- spontaneous-state `on`

When the target-perturbation assay is added, it should also include:

- `target_jump`
- `target_removed_brief`

## Phase Windows

Default analysis windows for the current landmark-orientation benchmark:

- acquisition: `0.0-0.5 s`
- consolidation: `0.5-1.0 s`
- sustained orientation: `1.0-2.0 s`

For perturbation / refixation assays, add:

- perturbation response: `0-250 ms` after jump
- refixation window: `0-2 s` after jump

These windows are analysis windows only. They do not justify direct controller
phase scripting.

## Acceptance Mapping To Repo Metrics

| Literature-grounded concept | Current repo metric(s) | Acceptance intent |
| --- | --- | --- |
| Awake spontaneous locomotion | `spontaneous_locomotion.locomotor_active_fraction`, bout counts/durations, `controller_state_entropy` | `no_target` should show life without collapsing into silence or constant forced drive. |
| Intermittent pause / move structure | locomotor bout counts/durations, turn bout counts/durations | Spontaneous-state should preserve switching rather than flattening behavior into one mode. |
| Structured turning / reorientation | `mean_abs_turn_drive`, `turn_switch_rate_hz`, `turn_alignment_fraction_active`, `turn_bearing_corr` | Turning should be target-signed when relevant, without generic one-sided bias. |
| Landmark fixation / orientation | `mean_abs_bearing_rad`, `fixation_fraction_20deg`, `fixation_fraction_30deg`, `aligned_turn_fraction`, `aligned_turn_latency_s` | The target assay should be judged as frontal-object stabilization, not only translational pursuit. |
| Refixation after perturbation | not yet implemented; future jump-response summary should report recovery latency and frontal refixation fraction | This is the grounded next-step replacement for vague "reacquisition" claims. |
| Short-timescale persistence after brief loss | current runs can only weakly approximate this; requires `target_removed_brief` or equivalent assay | Do not claim strong persistence from the current continuous-target assay alone. |
| Brain-side ongoing state | spontaneous-state audit metrics, homologous-family correlation, `zero_brain` integrity, matched target/no-target separation | Wakefulness is only valid if it preserves condition differences and does not leak control. |

## Rejection Criteria

A branch fails this behavior spec if it:

- improves speed or displacement while degrading fixation/orientation structure
- reintroduces a generic one-sided turn bias under `no_target`
- creates nonzero decoded commands under `zero_brain`
- turns spontaneous-state into a body-side motor floor
- claims search or pursuit persistence without a matching real-fly assay
- optimizes against a behavior that is real only in odor, reward, or threat
  contexts while the repo is still vision-only

## Immediate Consequence For The Current Branch

The current `target` benchmark should be interpreted as:

- a landmark-orientation / fixation benchmark
- with some evidence for bounded frontal acquisition
- but not yet as proof of real-fly-like continuous pursuit or robust
  reacquisition after target loss

That is a stricter and more biologically honest interpretation of the same
artifacts.
