# Creamer Recording Fit Targets

## Current blocker

The current Creamer miss is now narrowed more tightly than before.

The synced treadmill probe proved that the scene semantics can be made honest:

- stationary scored blocks can be held at `0.0 mm/s` retinal slip
- motion blocks can impose a true small signed perturbation like `-0.5 mm/s`

That means the remaining miss is no longer best explained by mislabeled scene
motion. The dominant blocker is now:

1. a **high-speed embodied treadmill attractor** in the current
   `hybrid_multidrive` operating point
2. a **weak / nonspecific bilateral speed-suppression signal** from the current
   `T5a`-only forward-context library

The strongest local evidence is:

- in the synced assay, `baseline_a` and `baseline_b` had `0.0 mm/s` retinal
  slip, while `motion_ftb_a` had `-0.5 mm/s` exactly
- the decoder-side signals still moved during that perturbation
- treadmill speed remained pinned near `645 mm/s`

So the remaining problem is now more honestly:

- embodied brain / decoder / body response
- not scene semantics

## Strongest falsification experiment

The cleanest next blocker test is a same-state forked replay.

Procedure:

1. Snapshot brain state, decoder state, and MuJoCo/body state at the start of
   `baseline_a` in the synced probe.
2. Fork short `250-500 ms` continuations from that identical state.
3. Replay:
   - the observed `baseline_a` latent stream
   - the observed `motion_ftb_a` latent stream
   - a stronger bilateral frequency-suppressed stream with amplitudes and turn
     terms held fixed

Decision rule:

- if treadmill speed stays pinned near the same high value in all forks, the
  embodied high-speed attractor hypothesis is supported
- if speed tracks the imposed frequency changes from the same starting state,
  the main blocker is upstream in the visual-to-forward decoder signal

## Ranked public fit targets

These are the highest-value public living-fly datasets and papers for fitting
the current branch rather than guessing gains.

### Tier 1: immediate fit targets

1. **Aimon et al. 2023, spontaneous and forced walking**
- Best public mesoscale fit target for the living branch
- Whole-brain light-field calcium data with spontaneous and forced walking
- Public Dryad data
- Use for:
  - spontaneous backbone calibration
  - walk-onset dynamics
  - forced-vs-spontaneous locomotor structure
- Sources:
  - https://elifesciences.org/articles/85202
  - https://doi.org/10.5061/dryad.3bk3j9kpb

2. **Schaffer et al. 2023, spatial and temporal structure across the fly brain**
- Best public whole-brain walking-state dataset with high-dimensional activity
- SCAPE whole-brain calcium imaging in behaving flies on spherical treadmill
- Public NWB / Figshare release
- Use for:
  - living-branch locomotor state structure
  - high-dimensional residual activity
  - walking / quiescence transition statistics
- Sources:
  - https://doi.org/10.1038/s41467-023-41261-2
  - https://doi.org/10.6084/m9.figshare.23749074

3. **Ketkar et al. 2022**
- Best public upstream fit target for `L1/L2/L3`
- Calcium recordings plus walking-ball behavior
- Public Zenodo data/code
- Use for:
  - lamina temporal filtering
  - luminance / contrast adaptation
  - locomotor-state visual preprocessing
- Sources:
  - https://elifesciences.org/articles/74937
  - https://doi.org/10.5281/zenodo.6335347

4. **Gruntman et al. 2019**
- Best public mechanistic fit target for `T5`
- In vivo whole-cell recordings under flashes, moving bars, drifting gratings
- Public Figshare data and model code
- Use for:
  - OFF-path temporal kernels
  - directional computation
  - TF-tuned motion-detector calibration
- Sources:
  - https://elifesciences.org/articles/50706
  - https://doi.org/10.25378/janelia.c.4771805.v1

5. **Shomar et al. 2025**
- Best public identified visual-to-locomotor neural dataset near the current
  problem
- LC15 imaging plus behavior under parallax / distance-estimation stimuli
- Public Dryad data
- Use for:
  - near-object / obstacle-related slowing channels
  - downstream visual-motion-to-locomotor fitting
- Sources:
  - https://pmc.ncbi.nlm.nih.gov/articles/PMC12652897/
  - https://doi.org/10.5061/dryad.kkwh70sgw

6. **Dallmann et al. 2025**
- Best public treadmill proprioception / ascending-feedback fit target
- Calcium imaging in behaving treadmill flies with forward/lateral/rotational
  velocity and joint variables
- Public Dryad parquet dataset
- Use for:
  - treadmill locomotor-state calibration
  - ascending feedback realism
  - body-to-brain coupling
- Source:
  - https://doi.org/10.5061/dryad.gqnk98t16

### Tier 2: translational-vs-rotational motion constraints

7. **Creamer, Mano, Clark 2018**
- Target behavioral phenomenon itself
- Strongest scorecard for:
  - real-motion slowing over flicker
  - FtB and BtF translational slowing
  - turning-vs-speed dissociation
- Public paper, but no clearly confirmed raw dataset found yet
- Sources:
  - https://pmc.ncbi.nlm.nih.gov/articles/PMC6405217/
  - https://pubmed.ncbi.nlm.nih.gov/30415994/

8. **Katsov and Clandinin 2008**
- Best public prior that translational and rotational motion streams diverge
  behaviorally
- Use for:
  - architectural prior that speed control should not collapse into optomotor
    turning
- Source:
  - https://pmc.ncbi.nlm.nih.gov/articles/PMC3391501/

9. **Cruz et al. 2021**
- Best public walking-VR visual-feedback constraint
- Use for:
  - self-motion visual stabilization under walking
  - avoiding collapse into pure turn reflexes
- Sources:
  - https://pmc.ncbi.nlm.nih.gov/articles/PMC8556163/

10. **Henning et al. 2022**
- Best public `T4/T5` population optic-flow basis
- Use for:
  - upstream motion basis fitting before downstream speed-vs-turn separation
- Source:
  - https://pmc.ncbi.nlm.nih.gov/articles/PMC8769539/

11. **Erginkaya et al. 2025**
- Best public downstream optic-flow circuit exclusion / comparator source
- Use for:
  - telling turn / optic-flow-selective downstream pathways apart from true
    translational speed pathways
- Sources:
  - https://www.nature.com/articles/s41593-025-01948-9
  - https://doi.org/10.5281/zenodo.14967806

12. **Clark et al. 2023**
- Best public turning comparator with public data
- Use for:
  - ensuring a future Creamer branch is not just another turn decoder
- Source:
  - https://pmc.ncbi.nlm.nih.gov/articles/PMC10522332/

## Practical fit program

The best near-term fit stack is:

1. Fit the living / spontaneous baseline against **Aimon 2023** and
   **Schaffer 2023**
2. Fit early motion preprocessing against **Ketkar 2022** and
   **Gruntman 2019**
3. Fit downstream visual-to-locomotor channels against **Shomar 2025**
4. Fit treadmill feedback realism against **Dallmann 2025**
5. Score translational speed behavior against **Creamer 2018**
6. Use **Katsov 2008**, **Cruz 2021**, **Henning 2022**, **Erginkaya 2025**,
   and **Clark 2023** as structural and comparator constraints

## Immediate recommendation

Do not keep sweeping Creamer gains blindly.

Next:

1. run the same-state replay falsifier for the high-speed treadmill attractor
2. start a real parameter-fit workstream on the public datasets above
3. use Creamer only as the behavioral acceptance target, not as the sole fit
   source
