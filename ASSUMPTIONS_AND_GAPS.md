# Assumptions And Gaps

## Public vs Inferred Pieces

| Subsystem | Publicly Available | Current Substitute Or Glue | Confidence |
| --- | --- | --- | --- |
| Whole-brain core | yes, `fly-brain` and `Drosophila_brain_model` | persistent online wrapper around the public Torch backend | high |
| Embodied body runtime | yes, `flygym` | local adapter around `SingleFlySimulation` and `RealisticVisionFly` | high |
| Realistic vision | yes, `flygym` | currently exposes raw `nn_activities_arr`, but the production bridge still reduces that rich state into a small number of sensory rates before the whole-brain backend sees it | medium |
| Sensorimotor mapping | partial neuron IDs only | explicit encoder/decoder built from public `LC4`, `JON`, `P9`, `DNa01`, `DNa02`, and `MDN` anchors, with no scripted idle-drive fallback in production | low |
| Public `P9` context experiment mode | partial public notebook framing | direct `P9_left` / `P9_right` brain-side Poisson-rate injection with no decoder/body fallback | medium |
| Inferred `P9` cold-start experiment mode | no direct public grounding | visually gated asymmetric `P9_left` / `P9_right` stimulation from inferred FlyVis evidence | low |
| Exact Eon private glue | no | not reproducible from public artifacts; replaced with a public-equivalent bridge | low |
| Multi-GPU production split | no turnkey public path | currently blocked by public WSL wheel support for `sm_120` | medium |

## Current Assumptions

- The strongest public production backend on this machine is the `fly-brain` Torch implementation, not `Brian2` CPU.
- Realistic vision is mandatory for the production path; the mock path exists only for tests and fast smoke runs.
- Hard rule for the active embodiment path:
  - no controller-side or body-side shortcut heuristics
  - no motor-floor or behavior-floor patches outside the brain
  - primary-branch behavior changes must be brain-driven and biologically plausible
  - monitoring-only and explicitly rejected experimental branches may still exist for diagnosis, but they must stay clearly labeled as non-production
- Evaluation-duration rule:
  - `>= 1.0 s` runs count as benchmarking / real evaluation.
  - `< 1.0 s` runs count only as smoke tests / sanity checks.
- Living-brain evaluation rule:
  - once endogenous spontaneous state is enabled, the old cold-start / quiescent
    branches must not be treated as the primary behavioral comparator
  - cold-start branches remain valid only as regime-transition baselines showing
    that the brain is no longer silent
  - the living-brain line must instead be judged against matched living-brain
    `target`, `no_target`, perturbation, and `zero_brain` controls
  - raw speed / displacement differences versus the dead-brain regime are
    secondary diagnostics, not the main success criterion
- The current closed-loop moving-target assay should be interpreted primarily as
  a landmark-orientation / fixation benchmark unless stronger context-specific
  evidence is added. Generic indefinite pursuit of an arbitrary target is not
  yet treated as a canonical real-fly default behavior in this repo.
- The public body and brain repos do not provide the exact closed-loop bridge used in the public demo context, so the bridge in `src/bridge/` is an explicit engineering substitute.
- The public `LC4` and `JON` anchor lists are bilateral in the checked public notebook artifacts, so the production path now treats them as bilateral public input pools instead of inventing left/right halves.
- The public notebook examples checked in under `external/fly-brain/code/paper-phil-drosophila/example.ipynb` use direct `P9` stimulation as the explicit forward-walking baseline, then add `LC4` or `JON` co-stimulation on top of that baseline.
- The inferred `P9` cold-start mode is a diagnostic splice experiment only. It must not be treated as a faithful final sensory pathway.
- A split-environment strategy is required because the modern FlyGym stack and the secondary Brian2 benchmark stack are not cleanly co-installable.

## Validated Gaps

- The current public WSL PyTorch `cu126` wheel used by FlyVis does not support RTX 5060 Ti `sm_120`, so the validated realistic-vision production path is CPU-only in WSL.
- `Brian2CUDA` and `NEST GPU` were not validated locally.
- No public raw telemetry or parameter dump from the Eon demo is available, so exact side-by-side trace matching is impossible.
- This workspace is not itself a Git repository, so benchmark rows cannot carry a real commit hash.
- The production path is now stricter than the earlier parity demos: it no longer injects decoder idle drive, so any locomotion now has to come from connectome readout rather than a scripted motor floor.
- The current strict public sensory path under-drives the monitored locomotor readouts: `outputs/metrics/motor_path_audit_sweeps.csv` shows that the observed bilateral production inputs produce zero monitored output over `20-100 ms` and only weak turning-biased output after `1000 ms`.
- The current public `LC4` and `JON` pools have zero direct edges to the monitored `P9`, `DNa01`, `DNa02`, and `MDN` groups in `outputs/metrics/motor_path_audit.json`; they only reach those readouts by hop `2`.
- The checked public artifacts do not expose clearly lateralized visual or mechanosensory anchor pools for this bridge. `outputs/metrics/lateralized_public_anchors.json` finds lateralized gustatory examples, but no `LC4_left/right` or `JON_left/right`-style public anchors.
- The repo now includes an inferred left/right visual-candidate probe through the real FlyVis network:
  - `scripts/probe_lateralized_visual_candidates.py`
  - `outputs/metrics/inferred_lateralized_visual_candidates.csv`
  - `docs/inferred_lateralized_visual_candidates.md`
- That probe recovers strong mirror-consistent left/right structure in several FlyVis cell types, but it still does not provide a public whole-brain neuron-ID mapping. Any bridge built from those candidates must be labeled inferred, not public-grounded.
- The repo now includes an explicit inferred experiment mode based on those candidates:
  - `docs/inferred_visual_turn_context_mode.md`
  - `configs/flygym_realistic_vision_inferred_visual_turn.yaml`
- That mode is only locally validated on the mock path so far. Real WSL validation is still pending.
- The repo also now includes an inferred asymmetric `P9` cold-start mode:
  - `configs/flygym_realistic_vision_inferred_visual_p9.yaml`
  - `src/bridge/brain_context.py`
- This mode is still a prosthetic bridge: it uses real visual evidence to decide how strongly to stimulate `P9_left` / `P9_right`. It is useful for diagnostics, but it is not yet a biologically grounded splice.
- The current bridge problem is now best understood as a splice-boundary problem between FlyVis and the whole-brain backend, not just a decoder-tuning problem.
- The next fast iteration loop should be body-free:
  - run FlyVis on controlled visual stimuli
  - run the whole-brain backend on candidate mapped inputs
  - compare overlap populations directly before putting the body back in the loop
- The first grounded body-free splice boundary is now exact shared visual `cell_type` + `side`, using the official FlyWire annotation supplement in `outputs/cache/flywire_annotation_supplement.tsv`.
- That body-free splice is promising but incomplete:
  - grouped overlap amplitudes match well
  - side-difference preservation is still inconsistent
  - short-window motor recruitment was absent in the first positive-only probe
  - a later signed+spatial body-free probe does produce downstream motor readouts over `100 ms`
  - voltage and conductance readouts now show that inhibitory signed responses were real even when spike-rate deltas looked flat
  - the current best tested calibrated splice point is:
    - `4` spatial bins
    - signed current with `max_abs_current = 120`
    - evidence:
      - `outputs/metrics/splice_probe_signed_bins4_100ms_state_summary.json`
      - `outputs/metrics/splice_probe_calibration_curated.json`
  - that calibrated splice is still experimental:
    - spatial bins are inferred, not exact retinotopic column matches
    - downstream motor recruitment is still weak and only appears in a narrow tested regime
    - embodied claims are still premature
- The repo now also includes a deeper relay-target audit built on top of the calibrated splice:
  - `scripts/find_splice_relay_candidates.py`
  - `scripts/run_splice_relay_probe.py`
  - `outputs/metrics/splice_relay_candidates.json`
  - `outputs/metrics/splice_relay_probe_summary.json`
- That relay probe narrows the failure mode:
  - at `100 ms`, the calibrated splice still flips the downstream turn sign correctly
  - deeper relay groups such as `LC31a`, `LCe06`, and `LT82a` already carry structured lateralized state
  - at `500 ms`, the downstream turn sign drifts into the wrong regime
  - so the remaining issue is now longer-window downstream stability, not total absence of a brain response
- The repo now also includes an experimental two-dimensional `uv_grid` splice mode:
  - FlyVis side uses native `u/v`
  - whole-brain side uses two public spatial principal axes from FlyWire coordinates
  - evidence:
    - `outputs/metrics/splice_probe_uvgrid_2x2_current120_summary.json`
    - `outputs/metrics/splice_probe_uvgrid_flipu_summary.json`
- That `uv_grid` splice improves boundary agreement beyond the earlier one-axis splice, but the downstream turn sign remains wrong, so the spatial blocker is now more specific:
  - axis orientation and column alignment are still unresolved
- The repo now also includes targeted UV-grid follow-up with side-specific horizontal mirroring:
  - `outputs/metrics/splice_uvgrid_targeted_comparison.json`
- That follow-up rules out a simpler explanation:
  - global flips alone were not enough
  - side-specific horizontal mirroring was also not enough
  - so the remaining spatial blocker is likely finer column alignment or a per-cell-type transform, not just a global orientation mistake
- The repo now also includes pulsed-input relay comparisons:
  - `outputs/metrics/splice_relay_drift_comparison.json`
- That follow-up also narrows the temporal blocker:
  - the `500 ms` sign collapse is not just because the external drive was held on continuously
  - even a `25 ms` pulse fails to preserve the correct downstream sign by `500 ms`
  - so recurrent downstream drift or missing state conditioning is now the leading explanation
- The repo now also includes a strict descending-only expanded readout branch:
  - `docs/descending_readout_expansion.md`
  - `configs/flygym_realistic_vision_splice_axis1d_descending_readout.yaml`
  - `outputs/metrics/descending_readout_comparison.csv`
- That branch materially improves embodied traversal without optic-lobe-as-motor shortcuts, which means the old failure was not input-only; the output readout bottleneck was also fundamental.
- Remaining gap for that new branch:
  - it still needs matched `zero_brain` / no-target ablations before it should be treated as a strong closed-loop success claim
- Those matched ablations now exist in:
  - `docs/descending_visual_drive_validation.md`
  - `outputs/metrics/descending_visual_drive_validation.csv`
- Updated interpretation:
  - the descending-only branch is now supported as brain-driven and visually driven
  - but not purely target-driven, because the no-target control still shows substantial locomotion driven by the rest of the visual scene and self-motion
- The repo now logs explicit target state directly from the simulation for the descending-only branch, and controlled left/right target conditions now exist in `docs/descending_visual_drive_validation.md`.
- Remaining gap after that instrumentation upgrade:
  - the short side-isolated left/right target conditions are still mixed and do not yet show a clean mirrored pursuit reflex
- The stable strict-default path is now validated against a real zero-brain baseline:
  - `docs/brain_control_validation.md`
  - `outputs/metrics/compare_5s_strict_vs_zero.csv`
- This validates that the strict-default motion is brain-driven rather than coming from hidden body fallback, but it does not by itself prove final parity or final biological correctness of the bridge.
- The semantic-VNC `exit_nerve_flywire_semantic` branch is now frozen as a failed parity branch:
  - semantic monitor-space alignment is real
  - decoder saturation and camera framing were fixed
  - the corrected embodied run is stable
  - but the branch still does not track the target
  - current conclusion:
    - structural semantic VNC mapping alone is not enough to recover target-directed behavior in this repo
- The repo now includes an opt-in backend-side spontaneous-state pilot:
  - `docs/spontaneous_state_backend_design.md`
  - `docs/spontaneous_state_results.md`
  - `outputs/metrics/spontaneous_state_best_candidate_summary.json`
  - `outputs/metrics/spontaneous_state_central_seed_summary.json`
- Current honest status of that pilot:
  - it resolves the fully silent cold-start baseline in the brain-only audit
  - the current best candidate uses bilateral family-structured tonic occupancy and slow latent fluctuations over central/integrative super-classes rather than decoder/body fallback
  - it now clears a brain-only plausibility bar: sparse bounded ongoing activity, positive homologous family coupling, and retained perturbability across seeds
  - but it is not yet promotable as a production embodied branch because matched embodied `target` / `no_target` / `zero_brain` validation has not been run yet
- The repo now includes a default same-run activation capture path plus an
  iterative decoding workbench:
  - `src/visualization/session.py`
  - `docs/iterative_brain_decoding_system.md`
  - `outputs/metrics/iterative_decoding_cycle_summary.json`
- Current honest status of that decoding system:
  - it makes the relay/decoder search reproducible and data-driven
  - it can rank candidate relay families and structured signals from recorded
    activation captures
  - but it does not constitute a complete decode of the fly brain
  - exact neuron-identity sensory and VNC mappings remain inferential
  - live control promotion still requires matched behavioral controls and
    causal validation
- The repo now also includes a matched relay-monitor plus shadow semantic-VNC
  control loop:
  - `docs/relay_monitored_shadow_control_loop.md`
  - `outputs/metrics/relay_monitored_control_metrics_0p2s.csv`
  - `outputs/metrics/relay_monitored_shadow_control_summary_0p2s.csv`
- Current honest status of that loop:
  - it proves the shadow VNC decoder is reading real brain-side signal on the
    same run, because it is nonzero for `target` and `no_target` and collapses
    exactly on `zero_brain`
  - it does not solve target tracking or target selectivity
- many widened relay families are more informative in monitored voltage than
  in monitored firing rate, so the current rate-only relay heatmap is not a
  sufficient summary of upstream state
- the repo did not previously have one canonical literature-grounded behavior
  target set; behavior criteria were spread across branch notes and metric docs
  until `docs/behavior_target_set.md`
- the turn-voltage controller-promotion line is now useful mainly as an
  evidence path about where target-bearing relay structure lives; under the
  current hard rule it is not an acceptable final control architecture
- the current active perturbation-improvement branch is instead a
  decoder-internal relay-voltage turn latent:
  - `docs/brain_latent_turn_decoder.md`
  - confidence: moderate for improved signed steering / jump recovery
  - confidence: low for full biological parity
  - remaining gap:
    - no explicit heading / goal / steering-gain scaffold yet
    - frontal jump refixation still does not complete within `2.0 s`
- full physiologically validated spontaneous adult fly-brain dynamics are not
  currently achievable from public artifacts alone:
  - public whole-brain spontaneous imaging exists
  - public connectome and cell-type resources exist
  - but the field still lacks the combined neuron-identity alignment,
    cell-intrinsic physiology, synapse/gap-junction physiology,
    neuromodulatory-state coverage, and whole-brain causal perturbation atlas
    needed for an honest full-validation claim
  - current strongest honest target is mesoscale physiological validation of
    spontaneous state against public imaging literature and datasets
  - current living-branch mesoscale result:
    - matched living target / no-target baseline: achieved
    - walk-linked global modulation: achieved
    - bilateral family coupling: achieved
    - family-scale structure above a circular-shift surrogate: achieved
    - residual high-dimensional / temporal structure: achieved
    - weak positive family-scale connectome-to-functional correspondence after
      log-weight aggregation: achieved
    - forced-vs-spontaneous public timeseries comparison: achieved as a real
      partial comparator
      - the staged Aimon public comparator is now executable locally
      - the decisive substrate is `Additional_data.zip`
        `FunctionallyDefinedAnatomicalRegions/*.mat` plus
        `AllRegressors/*.mat`, with `Walk_anatomical_regions.zip` used as a
        secondary source when available
      - `Walk_components.zip` is locally staged and digest-valid, but it is not
        the primary archive for this comparator
      - only `B350` and `B1269` survive as distinct forced-vs-spontaneous
        comparisons
      - `B1037` and `B378` are dropped because the public GoodICs windows
        overlap between spontaneous and forced segments
      - the resulting public slice is honest but weak:
        `median_steady_walk_vector_corr = -0.2016`,
        `median_steady_walk_rank_corr = -0.2013`,
        `median_spontaneous_prelead_fraction = 0.6241`
  - evidence:
    - `docs/spontaneous_state_full_validation_requirements.md`
    - `docs/spontaneous_mesoscale_validation.md`

## Engineering Substitutes Used

- Persistent online stepping API for the public whole-brain model
- Sensory encoder from realistic-vision and body state into public sensory proxy pools
- Motor decoder from public descending-neuron readouts into FlyGym left/right drive
- Optional `public_p9_context` experiment mode that injects direct public `P9` drive on the brain side to match the public notebook framing more closely
- Benchmark, profiling, and parity-summary scripts missing from the public repos

## Residual Open Questions

- Whether a future public FlyVis wheel with `sm_120` support will make GPU vision practical in WSL on this hardware
- Whether additional public descending-neuron anchors or better public sensory anchors would materially improve visual turning fidelity
- Whether a clearly labeled `public_p9_context` brain-side mode is the best public-experiment analogue for recovering locomotor output without reintroducing decoder or body-side fallback behavior
- Whether the public Eon demo used unpublished downstream control heuristics beyond the whole-brain core
- Whether FlyVis nodes expose enough neuron-identity metadata to ground a direct overlap mapping into the whole-brain backend instead of only a cell-family-level splice
- How to orient the current `uv_grid` splice so the stronger two-dimensional boundary fit also preserves the correct downstream turn sign
- Why the calibrated splice preserves the correct downstream sign at `100 ms` but drifts by `500 ms`
