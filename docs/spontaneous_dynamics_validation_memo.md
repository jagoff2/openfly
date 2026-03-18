# Memo: What Would Be Required To Claim "Fully Physiologically Validated" Spontaneous Adult Fly-Brain Dynamics?

## Bottom Line

The strongest honest conclusion from current public evidence is:

- **not currently publicly possible**

Public resources are now strong enough to support **mesoscale physiological
anchoring** of spontaneous adult fly-brain dynamics. They are not strong enough
to support a neuron-complete claim of **fully physiologically validated
spontaneous dynamics** for the adult *Drosophila* brain.

## What Primary Sources Already Establish

### 1. Public whole-brain spontaneous physiology exists, but mostly at mesoscale

- **Mann et al. 2017, Current Biology**
  https://pmc.ncbi.nlm.nih.gov/articles/PMC5967399/
  - Adult whole-brain calcium imaging during spontaneous activity revealed an
    intrinsic functional network with reproducible region-level functional
    structure across flies.
  - Validation value: region-level resting/spontaneous functional connectivity.
  - Limitation: this is not neuron-by-neuron validation of the full adult brain.

- **Aimon et al. 2019, PLOS Biology**
  https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.2006732
  - Near-whole-brain calcium and voltage imaging in behaving adult flies was
    performed at up to `200 Hz`.
  - The paper reports global walk-linked activity increases, identifies
    turning-related components, and reports spontaneous voltage patterns.
  - Public dataset:
    https://crcns.org/data-sets/ia/fly-1/about-fly-1
  - Validation value: high-speed spontaneous and behavior-linked whole-brain
    observables with released data.
  - Limitation: light-field data trades spatial precision for coverage/speed.

- **Aimon et al. 2023, eLife**
  https://elifesciences.org/articles/85202
  - Fast whole-brain light-field imaging showed that a global activity change is
    tightly correlated with spontaneous walking.
  - The same study reports that spontaneous and forced walk produce similar
    activity in most brain regions, while some components precede spontaneous
    walk onset and some serotonergic neurons are inhibited during walk.
  - Public dataset:
    https://datadryad.org/dataset/doi:10.5061/dryad.3bk3j9kpb
  - Validation value: spontaneous-state transitions, onset timing, and
    transmitter-class-specific walk effects.
  - Limitation: still not cell-complete physiology across the whole adult brain.

### 2. Public state-space analyses show that spontaneous dynamics are not just one global mode

- **Schaffer et al. 2023, Nature Neuroscience**
  https://pubmed.ncbi.nlm.nih.gov/37696814/
  - Cellular-resolution imaging over a large dorsal-brain volume during
    spontaneous behavior found that much activity is explained by running or
    flailing, but residual activity remains high-dimensional, temporally rich,
    spatially sparse, and organized into small clusters, including genetically
    defined cell types.
  - Validation value: any serious claim must match both the global
    behavior-linked mode and the residual clustered state-space structure after
    regressing behavior.
  - Limitation: this is not whole-brain coverage.

- **Turner et al. 2021, Current Biology**
  https://pubmed.ncbi.nlm.nih.gov/33770490/
  - The connectome explains over half the variance in resting-state functional
    connectivity across the fly brain.
  - Validation value: structural connectivity is a real constraint on
    spontaneous functional coupling.
  - Limitation: "over half" is not "all"; physiology is not determined by
    anatomy alone.

### 3. Public connectome resources are now excellent structural constraints, not full physiological constraints

- **Dorkenwald et al. 2024, Nature**
  https://pubmed.ncbi.nlm.nih.gov/39358518/
  - The adult female whole-brain wiring diagram contains about `5 x 10^7`
    chemical synapses among `139,255` neurons and includes neurotransmitter
    identity predictions.
  - Validation value: whole-brain structural scaffold for simulation.
  - Limitation: structure plus transmitter prediction is still not enough to fix
    intrinsic dynamics, synaptic kinetics, or neuromodulator state.

- **Schlegel et al. 2024, Nature**
  https://www.nature.com/articles/s41586-024-07686-5
  - Whole-brain annotation and multi-connectome cell typing provide a strong
    cell-type and anatomical reference frame for adult fly simulations.
  - Validation value: lets a model be judged against identified cell classes,
    not only anonymous graph nodes.
  - Limitation: public spontaneous whole-brain recordings are still not aligned
    one-to-one to this full connectome identity space.

- **Eckstein et al. 2024, Cell**
  https://www.sciencedirect.com/science/article/pii/S0092867424003076
  - Electron-microscopy images at synaptic sites can be used to classify fast
    neurotransmitter identity across the fly brain.
  - Validation value: stronger sign/transmitter constraints than anatomy alone.
  - Limitation: this is not a dynamic map of receptor occupancy, modulatory
    state, synaptic kinetics, or slow neuromodulation.

### 4. Public molecular atlases constrain neuromodulation, but do not validate spontaneous dynamics directly

- **Croset et al. 2018, eLife**
  https://elifesciences.org/articles/34550
  - Single-cell transcriptomics of the fly midbrain showed that neurons can be
    typed by transmitter/neuromodulator gene expression and that receptor-subunit
    expression is complex.
  - Validation value: receptor and neuromodulator expression constraints exist
    at cell-type level.
  - Limitation: transcriptomic identity is not the same as dynamic physiological
    state.

- **Li et al. 2022, Science / Fly Cell Atlas**
  https://pubmed.ncbi.nlm.nih.gov/35239393/
  - The adult fly atlas sampled more than `580,000` cells across the animal and
    provides broad molecular context, including brain cell classes.
  - Validation value: strong molecular prior for neuromodulatory and receptor
    expression.
  - Limitation: not simultaneous whole-brain spontaneous physiology.

## Required Dataset Stack For An Honest Full-Validation Claim

To honestly claim **fully physiologically validated spontaneous adult
fly-brain dynamics**, a model would need all of the following, jointly:

1. **Whole-brain spontaneous recordings with broad coverage**
   - Adult behaving flies.
   - Repeated recordings across animals.
   - Brain-wide coverage during rest, walk, turn, grooming, and other internal
     states.
   - Ideally voltage or very fast calcium with enough resolution to compare
     both global modes and local residual structure.

2. **Cell-identity alignment between physiology and connectome**
   - The recorded spontaneous activity must be mappable to the cell types, and
     ideally the individual cells, used in the simulation.
   - Matching only anonymous latent statistics is not enough for a
     connectome-scale physiological-validation claim.

3. **Whole-brain transmitter and neuromodulator constraints**
   - Fast-transmitter identity.
   - Receptor-expression constraints.
   - Neuromodulatory-cell coverage.
   - Preferably direct measurements or perturbation-calibrated surrogates for
     modulatory state, not only static transcriptomic annotation.

4. **Cell-intrinsic and synaptic dynamical constraints**
   - Membrane-time-scale, threshold, tonic-drive, and non-spiking versus
     spiking behavior where relevant.
   - Synaptic sign and effective kinetics.
   - Gap-junction contribution where important.

5. **Whole-brain causal validation**
   - The spontaneous-state model must survive perturbation tests, not only
     correlation tests.
   - A whole-brain or broad cell-type perturbation atlas during spontaneous
     state would be needed to rule out mechanistically wrong models that merely
     reproduce summary statistics.

## Minimum Validation Criteria

A model should not be called "fully physiologically validated" unless it matches
held-out data on all of these axes:

1. **Region and cell-class spontaneous functional connectivity**
   - Resting/spontaneous correlation matrices and their cross-animal stability.

2. **Behavior-linked global state transitions**
   - Walk onset timing, spontaneous versus forced walk similarity, and
     turn-linked asymmetries.

3. **Residual state-space structure after regressing behavior**
   - Dimensionality, temporal spectra, sparse clustered residual structure, and
     cell-type enrichment.

4. **Structure-function correspondence**
   - Functional coupling should be predictable from the connectome to at least
     the level seen in the real data, without claiming anatomy alone is
     sufficient.

5. **Neuromodulatory class signatures**
   - The model should reproduce cell-class-specific spontaneous effects, not
     only pan-neuronal averages.

6. **Causal response profiles**
   - Perturbing identified neurons or classes should shift spontaneous dynamics
     in simulation the same way it does in vivo.

Inference:
- Because the cited studies already show strong dependence on behavior and
  transmitter class, a "full" claim should also generalize across internal-state
  conditions such as arousal and motivational state. Current public adult
  whole-brain datasets do not cover that space sufficiently.

## Strongest Honest Statement Today

### Publicly supportable now

- A model can be claimed to be **connectome-constrained and partially
  physiologically anchored** to adult fly spontaneous dynamics.
- It can be validated at **mesoscale** against:
  - resting/spontaneous functional connectivity,
  - walk-linked global state changes,
  - turn-linked asymmetries,
  - clustered residual dynamics,
  - transmitter-class-specific signatures where public data exists.

### Not publicly supportable now

- A claim of **fully physiologically validated spontaneous adult fly-brain
  dynamics**.
- A claim of **neuron-by-neuron validated spontaneous whole-brain dynamics**.
- A claim that the public evidence already fixes the required synaptic,
  intrinsic, receptor-level, and neuromodulatory parameters for the full adult
  brain.

## Repo-Relevant Consequence

This matches the existing project boundary in:

- `docs/spontaneous_state_full_validation_requirements.md`
- `ASSUMPTIONS_AND_GAPS.md`

The highest honest target from current public evidence remains:

- **mesoscale physiological validation of spontaneous state**

not full physiological validation.
