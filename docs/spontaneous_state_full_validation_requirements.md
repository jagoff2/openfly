# Full Physiological Validation Requirements For Spontaneous Fly-Brain Dynamics

## Goal

This note defines what would be required to honestly claim:

- fully physiologically validated spontaneous adult fly-brain dynamics

and then compares that requirement to what is currently public and what exists
in this repo.

## Honest Verdict

Verdict: **not currently achievable from public artifacts alone**

The field now has strong public resources for:

- whole-brain anatomical connectivity
- large-scale cell typing
- whole-brain spontaneous and behavior-linked imaging
- mesoscale structure-function comparisons

But that is still not enough to honestly claim full physiological validation of
spontaneous whole-brain dynamics at the level of an embodied simulation.

## What Full Physiological Validation Would Require

To make the strong claim, all of the following would need to be true.

### 1. Whole-brain spontaneous recordings with the right coverage

Required:

- adult behaving flies
- repeated spontaneous-state recordings
- sufficiently broad brain coverage to capture global and local residual state
- ideally single-cell or near-single-cell resolution
- across multiple animals and internal states

Why:

- spontaneous state is not a single scalar "awake" quantity
- the public literature shows both broad global components and smaller
  cell-cluster residual dynamics

Relevant public evidence:

- [Whole-Brain Calcium Imaging Reveals an Intrinsic Functional Network in Drosophila](https://pmc.ncbi.nlm.nih.gov/articles/PMC5967399/)
- [The spatial and temporal structure of neural activity across the fly brain](https://pubmed.ncbi.nlm.nih.gov/37696814/)
- [Global change in brain state during spontaneous and forced walk in Drosophila is composed of combined activity patterns of different neuron classes](https://elifesciences.org/articles/85202)

### 2. Stable mapping from recorded activity to connectome cell identity

Required:

- reliable correspondence from spontaneous activity measurements to the cells or
  cell types in the connectome used for simulation
- ideally a repeatable mapping across animals, not only within one recording

Why:

- physiological validation of a connectome-scale simulator is not just about
  matching anonymous activity statistics
- it requires knowing whether the simulated cells or families correspond to the
  recorded biological ones

Relevant public evidence:

- [Whole-brain annotation and multi-connectome cell typing of Drosophila](https://www.nature.com/articles/s41586-024-07686-5)

Current limitation:

- the public connectome/cell-type atlas is extremely strong anatomically, but
  public spontaneous whole-brain recordings are not currently aligned one-to-one
  to the full FlyWire root-ID space in a way that would support exact
  neuron-level physiological validation of this simulator

### 3. Cell-intrinsic physiology and synapse physiology

Required:

- resting states
- thresholds / time constants
- spiking vs non-spiking physiology where relevant
- synapse sign, strength, kinetics
- gap junction identity and strength
- neuromodulator receptors and operating regimes

Why:

- a connectome alone does not determine spontaneous dynamics
- many parameters that matter most for spontaneous state are not encoded in the
  synapse graph

Relevant public evidence:

- [A connectome is not enough – what is still needed to understand the brain of Drosophila?](https://journals.biologists.com/jeb/article/224/21/jeb242740/272599/A-connectome-is-not-enough-what-is-still-needed-to)

That review explicitly points out that current EM connectomes do not directly
give neurotransmitter receptor identities, connection sign/strength/time
constants, gap junction physiology, or the wider biochemical constraints needed
for full mechanistic understanding.

### 4. Causal perturbation validation

Required:

- perturb specific cells or cell types
- compare real and simulated recovery / state transitions
- validate not just correlation, but the direction of causal effects

Why:

- matching spontaneous summary statistics is not enough
- a model can look plausible while being mechanistically wrong

The current public literature provides important targeted perturbation results
for particular circuits, but not a whole-brain spontaneous perturbation atlas
rich enough to fully validate a connectome-scale spontaneous model.

### 5. Cross-animal and cross-state robustness

Required:

- validation across multiple animals
- validation across hunger, satiety, circadian, arousal, and behavioral context
- confidence that the target model is not just fit to one preparation

Why:

- spontaneous dynamics are state dependent
- an embodied "living fly" claim is stronger than a single-condition fit

## What Public Data Actually Supports Today

### Strong public resources we do have

1. Whole-brain connectome and cell typing

- [Whole-brain annotation and multi-connectome cell typing of Drosophila](https://www.nature.com/articles/s41586-024-07686-5)

This gives a strong anatomical and cell-type scaffold for simulation.

2. Public whole-brain spontaneous / behavior-linked imaging

- [Whole-Brain Calcium Imaging Reveals an Intrinsic Functional Network in Drosophila](https://pmc.ncbi.nlm.nih.gov/articles/PMC5967399/)
- [The connectome predicts resting-state functional connectivity across the Drosophila brain](https://pubmed.ncbi.nlm.nih.gov/33770490/)
- [The spatial and temporal structure of neural activity across the fly brain](https://pubmed.ncbi.nlm.nih.gov/37696814/)
- [Global change in brain state during spontaneous and forced walk in Drosophila is composed of combined activity patterns of different neuron classes](https://elifesciences.org/articles/85202)
- [CRCNS fly-1 dataset](https://crcns.org/data-sets/fly/fly-1/about-fly-1)

These support real validation of some mesoscale spontaneous-state properties.

3. Explicit warning from the field that the connectome is not sufficient

- [A connectome is not enough – what is still needed to understand the brain of Drosophila?](https://journals.biologists.com/jeb/article/224/21/jeb242740/272599/A-connectome-is-not-enough-what-is-still-needed-to)

This is the best single public statement of the current honesty boundary.

### What these resources support validating

They support validation of:

- non-dead spontaneous occupancy
- broad global state changes
- structured residual dynamics beyond white noise
- mesoscale structure-function correspondence
- family/region-level bilateral organization
- perturbability of selected pathways

### What they do not yet support validating

They do not support honest full validation of:

- exact neuron-by-neuron spontaneous dynamics over the whole brain
- full connectome-to-physiology parameterization
- all neurotransmitter / receptor / gap-junction operating regimes
- whole-brain spontaneous causal response atlas
- exact spontaneous embodied control loops across full internal-state space

## Current Repo Status Against This Bar

The current repo does **not** meet the full-validation bar.

Current honest label:

- public-data-informed spontaneous-state pilot
- partial physiological plausibility
- not fully physiologically validated spontaneous whole-brain dynamics

What the repo currently has:

- a backend-side spontaneous-state mechanism inside the brain model
- validation against boundedness / structure / perturbability in brain-only
  audits
- matched living `target` / `no_target` embodied runs
- living-regime activation analysis and decoder guidance

What it still lacks relative to full validation:

- public single-cell spontaneous physiological targets aligned to the simulated
  full-brain ID space
- validated cell-intrinsic and synaptic kinetics across the whole brain
- neuromodulatory and receptor-level constraints sufficient for a full
  spontaneous-state model
- whole-brain causal perturbation validation across spontaneous states

## Highest Honest Next Tier

The strongest achievable next tier from public data is:

- **mesoscale physiological validation of spontaneous state**

That means validating the simulator against public whole-brain imaging at the
level of:

- family / region / component occupancy
- bilateral coupling
- low-dimensional global state structure
- residual cluster structure
- behavior-linked state transitions
- perturbation/release profiles where public data exists

That is a meaningful target.

It is not the same as full physiological validation.

## Consequence For Project Claims

This repo should not claim:

- fully physiologically validated spontaneous fly-brain dynamics

unless the external evidence base changes substantially.

The strongest honest current claim is:

- a connectome-grounded, biologically constrained spontaneous-state model with
  partial validation against public whole-brain imaging literature and matched
  living control runs

That is still substantial progress.

It is not the final goal.
