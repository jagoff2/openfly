# Reproduction Parity Report

Status: complete with partial parity verdict

## Target Public Behavior Summary

The target is the public Eon-style demo context referenced in `AGENTS.MD`: a local embodied fly driven in closed loop by a whole-brain simulation, realistic vision, and body physics, with observable locomotion, turning, video capture, and timing evidence.

## Reproduced Behavior Summary

This repo now reproduces the public-equivalent stack locally with:

- a persistent closed-loop bridge between realistic vision, body state, and the public whole-brain backend
- real FlyGym realistic-vision runs in WSL
- short, medium, and longest-stable real demo artifacts
- strict brain-only motor diagnostics with the decoder idle floor removed and the fake left/right public sensory split removed
- a standalone motor-path audit that explains why the current strict public sensory path produces no meaningful locomotor output
- a clearly labeled `public_p9_context` experiment mode that reproduces the public notebook's direct `P9` locomotor baseline without restoring decoder or body fallback
- benchmark CSVs and plots for brain, body, vision, and full stack
- a second neural backend benchmark using `Brian2` CPU
- profiling evidence and an explicit assumptions-and-gaps register

## Parity Metrics

Evidence source for run-level metrics: `outputs/metrics/parity_runs.csv`

| Metric | Target | Current Result | Status |
| --- | --- | --- | --- |
| Persistent closed-loop runtime | yes | real bridge loop runs locally with `FlyGymRealisticVisionRuntime` and `WholeBrainTorchBackend` | pass |
| Realistic vision enabled in production path | yes | validated through `outputs/benchmarks/vision_benchmarks.csv` and real FlyGym demos | pass |
| Whole-brain backend integrated | yes | Torch backend participates in the real closed loop; secondary `Brian2` CPU benchmark also exists | pass |
| Walking / locomotion artifact | yes | pre-strict demos exist, but the current strict brain-only production diagnostic shows zero monitored motor cycles and only `0.0136` path length from passive settling over `0.018 s` | partial |
| Turning / orientation artifact | yes | pre-strict demos showed turn asymmetry, but the current strict brain-only production diagnostic shows zero decoded turning output | partial |
| Reaction to visual stimulus | yes | realistic vision reaches the bridge, but the current strict brain-only production diagnostic shows zero monitored motor cycles under both `fast` and `legacy` payload modes | fail |
| Stable demo video capture | yes | real videos exist for short, medium, and longest-stable runs | pass |
| Timing logs and metrics CSV | yes | JSONL logs and metrics CSVs exist for all real demo runs | pass |
| Sim-speed vs wall-time benchmarks | yes | benchmark CSVs and plots exist for brain, body, vision, and full stack | pass |
| Qualitative similarity to the public demo | approximate | public-equivalent behavior is present, but exact unpublished glue and parameters are unavailable | partial |

## Demo Artifacts

### Short real run

- video: `outputs/demos/flygym-demo-20260308-121237.mp4`
- screenshot: `outputs/screenshots/flygym-demo-20260308-121237.png`
- log: `outputs/logs/flygym-demo-20260308-121237.jsonl`
- metrics: `outputs/metrics/flygym-demo-20260308-121237.csv`
- trajectory: `outputs/demos/flygym-demo-20260308-121237/trajectory.png`

### Medium real run

- video: `outputs/demos/flygym-demo-20260308-121318.mp4`
- screenshot: `outputs/screenshots/flygym-demo-20260308-121318.png`
- log: `outputs/logs/flygym-demo-20260308-121318.jsonl`
- metrics: `outputs/metrics/flygym-demo-20260308-121318.csv`
- trajectory: `outputs/demos/flygym-demo-20260308-121318/trajectory.png`

### Longest stable real run

- video: `outputs/demos/flygym-demo-20260308-121432.mp4`
- screenshot: `outputs/screenshots/flygym-demo-20260308-121432.png`
- log: `outputs/logs/flygym-demo-20260308-121432.jsonl`
- metrics: `outputs/metrics/flygym-demo-20260308-121432.csv`
- trajectory: `outputs/demos/flygym-demo-20260308-121432/trajectory.png`

### Strict brain-only diagnostics

- fast vision benchmark: `outputs/benchmarks/fullstack_brainonly_fastvision_test_v2.csv`
- fast vision log: `outputs/brain_only_fastvision_test_v2/logs/flygym-demo-20260308-150052.jsonl`
- fast vision metrics: `outputs/brain_only_fastvision_test_v2/metrics/flygym-demo-20260308-150052.csv`
- legacy vision benchmark: `outputs/benchmarks/fullstack_brainonly_legacyvision_test.csv`
- legacy vision log: `outputs/brain_only_legacyvision_test/logs/flygym-demo-20260308-150149.jsonl`
- legacy vision metrics: `outputs/brain_only_legacyvision_test/metrics/flygym-demo-20260308-150149.csv`
- motor-path audit summary: `docs/motor_path_audit.md`
- motor-path audit JSON: `outputs/metrics/motor_path_audit.json`
- motor-path audit sweep CSV: `outputs/metrics/motor_path_audit_sweeps.csv`

### Public `P9` context experiment mode

- config: `configs/flygym_realistic_vision_public_p9_context.yaml`
- mode doc: `docs/public_p9_context_mode.md`
- benchmark CSV: `outputs/benchmarks/fullstack_public_p9_context_test.csv`
- video: `outputs/public_p9_context_test/demos/flygym-demo-20260308-165839.mp4`
- log: `outputs/public_p9_context_test/logs/flygym-demo-20260308-165839.jsonl`
- metrics: `outputs/public_p9_context_test/metrics/flygym-demo-20260308-165839.csv`

### Lateralized public-anchor search

- search doc: `docs/lateralized_public_anchors.md`
- search artifact: `outputs/metrics/lateralized_public_anchors.json`

### Inferred lateralized visual probe

- probe doc: `docs/inferred_lateralized_visual_candidates.md`
- probe CSV: `outputs/metrics/inferred_lateralized_visual_candidates.csv`
- probe JSON: `outputs/metrics/inferred_lateralized_visual_candidates.json`
- recommended set: `outputs/metrics/inferred_lateralized_visual_recommended.json`
- stimulus plot: `outputs/plots/inferred_lateralized_visual_stimuli.png`

### Inferred visual-turn experiment mode

- plan: `docs/inferred_visual_turn_plan.md`
- mode doc: `docs/inferred_visual_turn_context_mode.md`
- mock config: `configs/mock_inferred_visual_turn.yaml`
- staged FlyGym config: `configs/flygym_realistic_vision_inferred_visual_turn.yaml`
- local mock artifact: `outputs/inferred_visual_turn_mock_test/mock-demo-20260308-174921/demo.mp4`

### Inferred visual-`P9` cold-start experiment mode

- config: `configs/flygym_realistic_vision_inferred_visual_p9.yaml`
- mock config: `configs/mock_inferred_visual_p9.yaml`
- local mock artifact: `outputs/inferred_visual_p9_mock_test_v2/mock-demo-20260308-214620/demo.mp4`
- short real smoke artifact: `outputs/inferred_visual_p9_smoke_v2/flygym-demo-20260308-214635/demo.mp4`

### Body-free splice probe

- strategy doc: `docs/visual_splice_strategy.md`
- results doc: `docs/splice_probe_results.md`
- FlyVis metadata inventory: `outputs/metrics/flyvis_overlap_inventory.json`
- official annotation cache: `outputs/cache/flywire_annotation_supplement.tsv`
- grouped splice CSV: `outputs/metrics/splice_probe_groups.csv`
- side-difference CSV: `outputs/metrics/splice_probe_side_differences.csv`
- summary JSON: `outputs/metrics/splice_probe_summary.json`
- signed+spatial splice CSV: `outputs/metrics/splice_probe_signed_bins4_groups.csv`
- signed+spatial side CSV: `outputs/metrics/splice_probe_signed_bins4_side_differences.csv`
- signed+spatial summary JSON: `outputs/metrics/splice_probe_signed_bins4_summary.json`
- signed+spatial `100 ms` summary JSON: `outputs/metrics/splice_probe_signed_bins4_100ms_summary.json`
- state-based `100 ms` summary JSON: `outputs/metrics/splice_probe_signed_bins4_100ms_state_summary.json`
- calibrated comparison CSV: `outputs/metrics/splice_probe_calibration_curated.csv`
- calibrated comparison JSON: `outputs/metrics/splice_probe_calibration_curated.json`

### Brain-control validation

- validation doc: `docs/brain_control_validation.md`
- real-brain strict run: `outputs/compare_5s_strict_fast_v2/flygym-demo-20260308-195012/demo.mp4`
- zero-brain baseline: `outputs/compare_5s_zero_brain_fast/flygym-demo-20260308-201434/demo.mp4`
- comparison CSV: `outputs/metrics/compare_5s_strict_vs_zero.csv`

## Unresolved Deviations

- Exact private Eon glue code is unavailable, so the bridge logic is inferred from public artifacts.
- The validated WSL production run uses CPU-only FlyVis because the public WSL PyTorch wheel does not support RTX 5060 Ti `sm_120`.
- No public demo telemetry exists for exact trajectory or neural-trace alignment.
- `Brian2CUDA` and `NEST GPU` were not reproduced locally.
- The current strict production path removes the decoder idle-drive floor and the fabricated left/right split of the public `LC4` / `JON` anchor pools; under that stricter path the public whole-brain model currently produces no monitored motor output in the short real diagnostics.
- The new motor-path audit shows that the strict bilateral public sensory inputs are weak for the monitored locomotor DN set, while direct public `P9` stimulation remains a strong positive control. This indicates an input-mapping mismatch rather than a dead backend.
- The public notebook experiments use `P9` as the explicit forward-walking baseline before adding `LC4` or `JON` co-stimulation, so the current strict sensory-only closed loop is more demanding than the public experiment framing.
- The checked public artifacts do not expose clearly lateralized visual or mechanosensory anchor pools for this bridge, so the repo does not currently claim honest public left/right visual steering input.
- The inferred FlyVis probe recovers left/right structure in several visual cell families, but that evidence is experimental and does not yet supply a faithful public-grounded whole-brain input mapping.
- The new body-free splice probe now grounds a much better boundary at exact shared visual `cell_type` + `side` using the official FlyWire annotation supplement.
- The backend now has experimental signed external input plus state-based boundary readouts, and the body-free probe now has an experimental signed+spatial calibrated mode.
- Even with that signed+spatial mode, the splice is not final:
  - grouped spike-rate matching drops relative to the broad type-level probe
  - voltage-side preservation is strong only in the calibrated spatial modes
  - the current best tested setting is bins=`4`, current=`120`
  - downstream motor recruitment appears over `100 ms`, but it is still weak and not yet enough for embodied parity claims
- The body-free splice now also has a deeper relay-target audit:
  - `outputs/metrics/splice_relay_candidates.json`
  - `outputs/metrics/splice_relay_probe_summary.json`
- That relay audit shows a narrower failure mode:
  - the calibrated splice launches the expected downstream turn-sign at `100 ms`
  - several intermediate relay groups already carry structured left/right state
  - but the downstream turn sign drifts by `500 ms`
- The body-free splice also now has an experimental `uv_grid` mode:
  - `outputs/metrics/splice_probe_uvgrid_2x2_current120_summary.json`
  - `outputs/metrics/splice_probe_uvgrid_flipu_summary.json`
- That `uv_grid` mode improves boundary agreement beyond the earlier one-axis splice, but the downstream turn sign is still wrong, so exact spatial orientation / column alignment remains unresolved.
- The newer targeted UV-grid follow-up now rules out a simpler orientation-only explanation:
  - `outputs/metrics/splice_uvgrid_targeted_comparison.json`
  - even with axis swap and side-specific horizontal mirroring, no tested UV-grid variant restores the correct downstream sign
- The newer relay-drift follow-up now rules out a simpler "held the input too long" explanation:
  - `outputs/metrics/splice_relay_drift_comparison.json`
  - a correct `100 ms` launch collapses by `500 ms`, and a `500 ms` run with only a `25 ms` pulse still fails to preserve the correct sign
- The repo now also includes a strict descending-only expanded readout branch:
  - `docs/descending_readout_expansion.md`
  - `configs/flygym_realistic_vision_splice_axis1d_descending_readout.yaml`
  - `outputs/benchmarks/fullstack_splice_descending_2s.csv`
  - `outputs/metrics/descending_readout_comparison.csv`
- That branch is the first embodied splice path here to produce meaningful traversal without optic-lobe-as-motor shortcuts or `P9` prosthetic context.
- However, it is still not final parity:
  - the supplemental descending groups are selected from public anatomy plus the body-free probe, not from a proven final biological motor interface
  - the matched `zero_brain` / no-target ablations now exist in `docs/descending_visual_drive_validation.md`
  - those ablations support a stronger claim that this branch is brain-driven and visually driven
  - but they also show the branch is not purely target-driven, because the no-target control still produces substantial locomotion from the rest of the visual scene
  - explicit target-state logging is now in place for that branch, so the main target-bearing correlation no longer depends on reconstructing `MovingFlyArena` kinematics
  - controlled left/right moving and stationary target conditions now exist, but the short side-isolated conditions remain mixed rather than a clean mirrored pursuit reflex
- The new `inferred_visual_turn_context` mode and the newer `inferred_visual_p9_context` mode are both experimental only. They are useful diagnostics, but neither one should be treated as the final faithful splice.
- The current core blocker is now a splice issue between the FlyVis visual model and the whole-brain backend. The next iteration should focus on body-free FlyVis-to-brain overlap matching rather than more body-loop tuning.
- The strict default path is now stably runnable for `5 s` and the zero-brain comparison shows that its motion is brain-driven, but the resulting locomotor policy is still sparse and not yet a strong parity match to the public demo.

## Final Verdict

Final verdict: partial

Explanation: the local repo now satisfies the public-equivalent acceptance gate in `AGENTS.MD` with real realistic-vision demos, benchmark evidence, tests, and documentation. Exact parity with the public Eon demo cannot be claimed because the private glue is not public and the current public WSL wheel blocks GPU FlyVis on this hardware.
