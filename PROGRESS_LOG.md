# Progress Log



Ground truth source: `AGENTS.MD`

## 2026-04-04 11:40 - Added a source-verified external comparison against `erojasoficial-byte/fly-brain` and tightened the canonical parity reproduction commands

1. What I did

- Reviewed the current public `erojasoficial-byte/fly-brain` repo against its repo root and three implementation files rather than trusting the README claim surface alone:
  - repo root README
  - `brain_body_bridge.py`
  - `fly_embodied.py`
  - `visual_system.py`
- Compared that public code against the current OpenFly canonical path and then added a new external-comparison section to:
  - [README.md](/G:/flysim/README.md)
  - [openfly_whitepaper_journal_draft.md](/G:/flysim/openfly_whitepaper_journal_draft.md)
- Tightened the canonical reproduction commands in both documents so they now show the exact active WSL parity invocation on this machine:
  - `wsl.exe --cd /mnt/g/flysim`
  - `MUJOCO_GL=egl`
  - `PYTHONPATH=src`
  - `/root/.local/bin/micromamba run -n flysim-full`
  - full-parity target / no-target configs
  - corrected command-side Creamer parity runner

2. What succeeded

- The whitepaper now states a balanced external verdict:
  - OpenFly is the stronger scientific audit artifact
  - `erojasoficial-byte/fly-brain` is the stronger scope/demo artifact
- The comparison is grounded in actual public code, not just README language:
  - `brain_body_bridge.py` really does collapse the motor seam to DN rate decoding into `[left_drive, right_drive]` plus explicit bridge-level mode selection and backup routing
  - `visual_system.py` really does state the early-visual scale mismatch and rate injection workaround
  - `fly_embodied.py` really does add a manual proboscis hinge and overwrite the free-joint quaternion during flight stabilization
- The canonical reproduction path is now more explicit than before and no longer leaves room to confuse generic host-side `python` invocations with the actual active parity run path.

3. What failed

- Nothing failed in this documentation pass.
- The live `2.0 s` parity target activation run that was already in flight before the doc edit is still separate from this change and still running on the exact active parity path.

4. Evidence

- [README.md](/G:/flysim/README.md)
- [openfly_whitepaper_journal_draft.md](/G:/flysim/openfly_whitepaper_journal_draft.md)
- External repo:
  - `https://github.com/erojasoficial-byte/fly-brain`
  - `https://raw.githubusercontent.com/erojasoficial-byte/fly-brain/main/brain_body_bridge.py`
  - `https://raw.githubusercontent.com/erojasoficial-byte/fly-brain/main/fly_embodied.py`
  - `https://raw.githubusercontent.com/erojasoficial-byte/fly-brain/main/visual_system.py`

5. Next actions

- Commit this documentation update on `main`.
- Push it to `origin/main`.
- Move `exp/spontaneous-brain-latent-turn` to the same commit so both branches stay synchronized.

## 2026-04-04 00:55 - Reviewed the journal draft, corrected stale claims, and synchronized the canonical whitepaper to the actual active parity path

1. What I did

- Reviewed the untracked manuscript draft at `openfly_whitepaper_journal_draft.md` against:
  - the active parity guard in [closed_loop.py](/G:/flysim/src/runtime/closed_loop.py)
  - the active decoder defaults in [decoder.py](/G:/flysim/src/bridge/decoder.py)
  - the active target/no-target endogenous routed parity configs
  - the corrected Creamer command-side pair result
  - the current long-form parity target artifact
- Rewrote [README.md](/G:/flysim/README.md) so it again serves as the canonical whitepaper and operator entrypoint, but now with the current evidence boundary rather than the older April 2 snapshot.
- Rewrote [openfly_whitepaper_journal_draft.md](/G:/flysim/openfly_whitepaper_journal_draft.md) into a synchronized mirror of the README so the journal draft cannot drift away from the live code and artifacts.
- Updated [docs/openfly_whitepaper.md](/G:/flysim/docs/openfly_whitepaper.md) to point at both the canonical README and the synchronized journal draft mirror.

2. What succeeded

- The whitepaper now reflects the actual current canonical replication path:
  - endogenous routed full-parity configs
  - explicit `runtime.parity_path.required = true`
  - explicit `decoder.command_mode = hybrid_multidrive`
  - explicit `runtime.control_mode = hybrid_multidrive`
  - splice-only encoder visual path
  - latest turn-voltage latent library in the active decoder config
- The older non-spontaneous brain-latent turn branch is no longer misrepresented as the active canonical branch. It is now clearly labeled as historical evidence only.
- The corrected Creamer pair is now represented accurately:
  - command-side primary readout
  - front-to-back suppression is sign-consistent with Creamer
  - `T4/T5` ablation weakens but does not abolish the effect
  - treadmill ball motion remains a separate downstream mechanics failure
- The later `10 s` full-parity target artifact is now incorporated as the sharper current behavioral boundary:
  - strong target response exists
  - close approach is still too aggressive
  - the remaining defect is close-range regulation rather than generic blindness

3. What failed

- No new scientific failure in the document-sync step itself.
- The underlying treadmill mechanics caveat remains unresolved and is preserved explicitly in the rewritten whitepaper rather than papered over.

4. Evidence

- [README.md](/G:/flysim/README.md)
- [openfly_whitepaper_journal_draft.md](/G:/flysim/openfly_whitepaper_journal_draft.md)
- [docs/openfly_whitepaper.md](/G:/flysim/docs/openfly_whitepaper.md)
- [creamer2018_parity_open_loop_pair_summary.json](/G:/flysim/outputs/creamer2018_parity_open_loop_2p0_commandmetrics_v1/metrics/creamer2018_parity_open_loop_pair_summary.json)
- [summary.json](/G:/flysim/outputs/requested_10s_endogenous_routed_multitarget_birdeye_activation_parity/flygym-demo-20260402-104437/summary.json)

5. Next actions

- Commit the synchronized whitepaper plus the pending parity-path config/default cleanup.
- Push the resulting README update to both `exp/spontaneous-brain-latent-turn` and `main`.

## 2026-04-02 01:49 - Rewrote the top-level whitepaper so README matches the current lawful branch and repaired findings

1. What I did

- Replaced the stale March 26 README paper with a current April 2 whitepaper in [README.md](/G:/flysim/README.md).
- Folded in the current branch state:
  - repaired Aimon / Schaffer parity harness findings
  - the explicit no-bypass rule
  - the splice-only lawful target branch
  - the exact `2.0 s` splice-only parity-time target rerun
  - the remaining fixation / bearing-reduction limitation
- Reduced [docs/openfly_whitepaper.md](/G:/flysim/docs/openfly_whitepaper.md) to a canonical pointer so the repo has one authoritative whitepaper entrypoint instead of two drifting copies.

2. What succeeded

- The top-level README is now the project whitepaper and current operator entrypoint.
- It now reflects the actual state of the branch instead of the older pre-repair picture.

3. What failed

- Nothing in the document rewrite itself.

4. Evidence

- [README.md](/G:/flysim/README.md)
- [docs/openfly_whitepaper.md](/G:/flysim/docs/openfly_whitepaper.md)

5. Next actions

- Commit and push the whitepaper rewrite.

## 2026-04-02 01:33 - Exact full `2.0 s` splice-only parity-time target rerun removed the old overlap failure

1. What I did

- Removed the legacy coarse visual encoder path from the active routed target/no-target configs by setting:
  - `encoder.visual_gain_hz = 0.0`
  - `encoder.visual_looming_gain_hz = 0.0`
- Locked that rule with focused smoke coverage in [test_closed_loop_smoke.py](/G:/flysim/tests/test_closed_loop_smoke.py).
- Ran the exact full `2.0 s` parity-time target assay on the corrected splice-only lawful branch:
  - [summary.json](/G:/flysim/outputs/requested_2s_endogenous_routed_target_parity_temporal_splice_only/flygym-demo-20260402-003922/summary.json)
  - [run.jsonl](/G:/flysim/outputs/requested_2s_endogenous_routed_target_parity_temporal_splice_only/flygym-demo-20260402-003922/run.jsonl)
  - [demo.mp4](/G:/flysim/outputs/requested_2s_endogenous_routed_target_parity_temporal_splice_only/flygym-demo-20260402-003922/demo.mp4)

2. What succeeded

- The exact old overlap failure is gone in the full `2.0 s` run.
- Old exact target run:
  - minimum target distance `0.5780 mm`
  - `86` cycles under `1.5 mm`
  - `119` cycles under `2.0 mm`
- New splice-only exact target run:
  - minimum target distance `3.0065 mm`
  - `0` cycles under `1.5 mm`
  - `0` cycles under `2.0 mm`
  - `0` cycles under `3.0 mm`
- The first `1.1 s` slice also improved over the earlier temporal retest:
  - earlier temporal retest minimum distance `2.4862 mm`
  - new splice-only run minimum distance by `1.1 s` is `3.1324 mm`
  - earlier temporal retest still spent `37` cycles under `3.0 mm`
  - new splice-only run spends `0` cycles under `3.0 mm` by `1.1 s`

3. What failed

- The branch is safer, but still not behaviorally correct as target-oriented control.
- Full-run fixation/targeting quality is still weak:
  - `target_condition_fixation_fraction_20deg = 0.076`
  - `target_condition_fixation_fraction_30deg = 0.113`
  - `target_condition_bearing_reduction_rad = -0.9223`
- So the fly now avoids the catastrophic near-overlap regime, but it still does not hold or improve target bearing robustly across the full run.

4. Evidence

- [summary.json](/G:/flysim/outputs/requested_2s_endogenous_routed_target_parity/flygym-demo-20260401-223021/summary.json)
- [run.jsonl](/G:/flysim/outputs/requested_2s_endogenous_routed_target_parity/flygym-demo-20260401-223021/run.jsonl)
- [summary.json](/G:/flysim/outputs/requested_1p1s_endogenous_routed_target_parity_temporal/flygym-demo-20260401-235448/summary.json)
- [run.jsonl](/G:/flysim/outputs/requested_1p1s_endogenous_routed_target_parity_temporal/flygym-demo-20260401-235448/run.jsonl)
- [summary.json](/G:/flysim/outputs/requested_2s_endogenous_routed_target_parity_temporal_splice_only/flygym-demo-20260402-003922/summary.json)
- [run.jsonl](/G:/flysim/outputs/requested_2s_endogenous_routed_target_parity_temporal_splice_only/flygym-demo-20260402-003922/run.jsonl)
- [test_closed_loop_smoke.py](/G:/flysim/tests/test_closed_loop_smoke.py)

5. Next actions

- Keep the active routed branch splice-only.
- Do not restore any coarse visual pool or any controller/decoder shortcut.
- Improve lawful target fixation by adjusting the sensory-to-brain temporal path only:
  - retinotopic transient weighting
  - sign/balance of bilateral temporal terms
  - splice/current timing relative to descending response
  - without using target metadata or any visual-area-to-body bypass

## 2026-04-02 00:33 - Removed the legacy coarse visual pool from the active routed branch and prepared the exact full target rerun

1. What I did

- Removed the last coarse encoder visual drive from the active routed target/no-target configs:
  - [flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_brain_endogenous_routed.yaml](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_brain_endogenous_routed.yaml)
  - [flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_endogenous_routed.yaml](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_endogenous_routed.yaml)
- Set the active routed branch to:
  - `encoder.visual_gain_hz = 0.0`
  - `encoder.visual_looming_gain_hz = 0.0`
- Kept the lawful retinotopic splice path active with `visual_splice.temporal_delta_scale = 2.0`.
- Added smoke coverage in [test_closed_loop_smoke.py](/G:/flysim/tests/test_closed_loop_smoke.py) to lock the splice-only rule for both active routed configs.
- Fixed two bad assertions in the new no-target smoke test that were checking unrelated config keys.

2. What succeeded

- The active routed target/no-target configs now drive visual object interaction solely through the retinotopic splice path.
- Focused validation passed:
  - `python -m pytest tests/test_closed_loop_smoke.py -k "endogenous_routed_config or turn_voltage_monitored_config" -q`
  - result: `3 passed`

3. What failed

- Nothing in the code/config slice after the smoke-test cleanup.

4. Evidence

- [test_closed_loop_smoke.py](/G:/flysim/tests/test_closed_loop_smoke.py)
- [flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_brain_endogenous_routed.yaml](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_brain_endogenous_routed.yaml)
- [flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_endogenous_routed.yaml](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_endogenous_routed.yaml)

5. Next actions

- Relaunch the exact `2.0 s` parity-time target run on the corrected splice-only routed config.
- Compare minimum target distance and close-pass occupancy against:
  - the old overlap run at `outputs/requested_2s_endogenous_routed_target_parity/flygym-demo-20260401-223021`
  - the lawful `1.1 s` temporal retest at `outputs/requested_1p1s_endogenous_routed_target_parity_temporal/flygym-demo-20260401-235448`

## 2026-04-02 00:16 - Added a lawful temporal sensory path and materially improved embodied target clearance without any bypass

1. What I did

- Traced the active routed target branch end to end and confirmed the key lawful bottleneck: public encoder vision collapses to a bilateral pool, so target-side structure was surviving mainly through the retinotopic `visual_splice` path, but that splice was still mostly static baseline-delta current with weak explicit temporal evidence.
- Patched the lawful sensory side only:
  - [feature_extractor.py](/G:/flysim/src/vision/feature_extractor.py)
    - added stateful temporal visual terms:
      - `balance_velocity`
      - `forward_salience_velocity`
      - `looming_evidence`
      - `receding_evidence`
    - added `reset()` so history does not leak across runs
  - [encoder.py](/G:/flysim/src/bridge/encoder.py)
    - added a small bilateral `visual_looming_gain_hz` path
    - exposed the new temporal visual terms in sensor metadata
  - [controller.py](/G:/flysim/src/bridge/controller.py)
    - now resets the vision extractor together with the rest of the bridge state
  - [visual_splice.py](/G:/flysim/src/bridge/visual_splice.py)
    - added a lawful `temporal_delta_scale` term so the retinotopic splice can inject transient motion evidence from the real vision array, not just static baseline differences
- Enabled the new sensory path in the active routed configs:
  - [flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_brain_endogenous_routed.yaml](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_brain_endogenous_routed.yaml)
  - [flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_endogenous_routed.yaml](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_endogenous_routed.yaml)
- Added focused coverage:
  - [test_realistic_vision_path.py](/G:/flysim/tests/test_realistic_vision_path.py)
  - [test_visual_splice.py](/G:/flysim/tests/test_visual_splice.py)
- Ran the first admissible embodied target retest on the exact routed parity-time stack, but shortened to `1.1 s` because the old failure window happened around `1.03 s`:
  - [summary.json](/G:/flysim/outputs/requested_1p1s_endogenous_routed_target_parity_temporal/flygym-demo-20260401-235448/summary.json)
  - [run.jsonl](/G:/flysim/outputs/requested_1p1s_endogenous_routed_target_parity_temporal/flygym-demo-20260401-235448/run.jsonl)

2. What succeeded

- Focused validation passed on the edited sensory slice:
  - `python -m pytest tests/test_realistic_vision_path.py tests/test_visual_splice.py tests/test_bridge_unit.py tests/test_closed_loop_smoke.py -k "brain_endogenous_routed or turn_voltage_monitored_config or realistic_vision or visual_splice or bridge" -q`
  - `43 passed`
- The new sensory path is live on the real embodied target run. The live `run.jsonl` now carries the new lawful temporal visual fields in `vision_features` and `sensor_metadata`.
- Most important: the new lawful branch materially improved target clearance in the old failure window.
  - Old exact target run, first `1.1 s` slice from [run.jsonl](/G:/flysim/outputs/requested_2s_endogenous_routed_target_parity/flygym-demo-20260401-223021/run.jsonl):
    - minimum target distance: `0.5780 mm`
    - cycles with target distance `< 2.0 mm`: `119`
    - cycles with target distance `< 1.5 mm`: `86`
  - New lawful temporal retest, [run.jsonl](/G:/flysim/outputs/requested_1p1s_endogenous_routed_target_parity_temporal/flygym-demo-20260401-235448/run.jsonl):
    - minimum target distance: `2.4862 mm`
    - cycles with target distance `< 2.0 mm`: `0`
    - cycles with target distance `< 1.5 mm`: `0`
- The closest-pass window in the new retest never entered overlap territory:
  - cycle `545`: distance `2.5089`, bearing `0.2975`, forward speed `4.5430`
  - cycle `546`: distance `2.5024`, bearing `0.2890`, forward speed `4.1321`
  - cycle `547`: distance `2.4956`, bearing `0.2798`, forward speed `3.0116`
  - cycle `548`: distance `2.4904`, bearing `0.2710`, forward speed `1.3306`
  - cycle `549`: distance `2.4862`, bearing `0.2614`, forward speed `0.4582`
- Summary metrics for the new `1.1 s` run from [summary.json](/G:/flysim/outputs/requested_1p1s_endogenous_routed_target_parity_temporal/flygym-demo-20260401-235448/summary.json):
  - `avg_forward_speed = 10.2249 mm/s`
  - `net_displacement = 7.5190 mm`
  - `displacement_efficiency = 0.6697`
  - `target_condition_bearing_reduction_rad = 0.9302`
  - `target_condition_mean_target_distance = 6.7756 mm`

3. What failed

- This is not a full end-to-end parity claim yet.
- The `1.1 s` run proves the new lawful sensory path materially changes target interaction, but it does not prove the full `2.0 s` target branch is fully fixed.
- The branch still does not show a strong explicit fixation policy. In the new `1.1 s` summary:
  - `target_condition_fixation_fraction_20deg = 0.0182`
  - `target_condition_fixation_fraction_30deg = 0.0473`
- The run is also still very slow on CPU:
  - `wall_seconds = 1105.80`
  - `real_time_factor = 0.000995`

4. Why this matters

- The recent target failure was not only a missing policy or a decoder issue.
- A lawful sensory-path change alone, with no target metadata and no visual-core steering shortcut, was enough to materially reduce the overlap failure.
- That means the object-response problem really was bottlenecked on the sensory-to-brain path, not just on body control or readout semantics.

5. Next actions

- Re-run the exact full `2.0 s` parity-time target assay on the same lawful temporal branch.
- Compare its closest-pass statistics directly against:
  - [run.jsonl](/G:/flysim/outputs/requested_2s_endogenous_routed_target_parity/flygym-demo-20260401-223021/run.jsonl)
- If the full `2.0 s` run also avoids the old overlap window, keep the new sensory path and then tune only remaining lawful gaps in target fixation / interception dynamics.

## 2026-04-01 22:55 - Reasserted and recorded the strict no-bypass rule after catching a disallowed visual-core steering idea

1. What I did

- Re-read the active target embodiment path against the user’s strict rule.
- Confirmed that the just-attempted idea of promoting steering from monitored visual-core voltage groups would violate the rule, because it would let visual-area activity drive the body through a decoder-side promotion path rather than through lawful descending structure.
- Reverted that attempted config-level promotion from the active routed target/no-target configs:
  - [flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_brain_endogenous_routed.yaml](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_brain_endogenous_routed.yaml)
  - [flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_endogenous_routed.yaml](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_endogenous_routed.yaml)
- Removed the temporary smoke assertions that would have normalized that promotion path:
  - [test_closed_loop_smoke.py](/G:/flysim/tests/test_closed_loop_smoke.py)
- Recorded the rule explicitly in:
  - [TASKS.md](/G:/flysim/TASKS.md)
  - [ASSUMPTIONS_AND_GAPS.md](/G:/flysim/ASSUMPTIONS_AND_GAPS.md)
  - [context.md](/G:/flysim/context.md)

2. What succeeded

- The active embodied routed target branch is back on a descending-only control path.
- The repo now states the production rule in unambiguous terms:
  - no bypass
  - no faking
  - no decoder/shadow promotion from visual-area activity into body control
  - no target metadata shortcuts into control
- Sanity validation after the revert passed:
  - `python -m pytest tests/test_closed_loop_smoke.py -k "turn_voltage_monitored_config" -q`
  - `1 passed`
  - prior bridge conflict/refixation coverage remained green:
  - `python -m pytest tests/test_bridge_unit.py -k "conflict_blend or refixation or shadow" -q`
  - `6 passed`

3. What failed

- The attempted visual-core promotion idea itself is disallowed for production and cannot be used to solve target interaction on the main branch.

4. Consequence

- Any future fix for target/object interaction must come from lawful sensory encoding, lawful recurrent/descending dynamics, or lawful descending readout structure.
- Visual-core monitors may still be used for diagnosis and analysis, but not as a direct body-driving promotion path.

## 2026-04-01 19:35 - Repaired the poisoned Aimon timing harness and launched the first repaired exact-identity retest

1. What I did

- Patched the shared trace scorer in:
  - [public_neural_measurement_harness.py](/G:/flysim/src/analysis/public_neural_measurement_harness.py)
- Patched both parity harnesses to record lag-aware timing metrics while preserving the old zero-lag metrics:
  - [aimon_parity_harness.py](/G:/flysim/src/analysis/aimon_parity_harness.py)
  - [schaffer_parity_harness.py](/G:/flysim/src/analysis/schaffer_parity_harness.py)
- Repaired Aimon replay semantics in:
  - [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py)
- Repaired canonical regressor export so each Aimon trial now carries a trial-aligned regressor file instead of an incompatible raw array:
  - [aimon_canonical_dataset.py](/G:/flysim/src/analysis/aimon_canonical_dataset.py)
- Repaired the public body-feedback phase path:
  - [public_body_feedback.py](/G:/flysim/src/analysis/public_body_feedback.py)
  - [encoder.py](/G:/flysim/src/bridge/encoder.py)
- Repaired the endogenous backend state semantics so exafference is now driven by public mechanosensory input rather than sharing the same internal target as arousal:
  - [pytorch_backend.py](/G:/flysim/src/brain/pytorch_backend.py)
- Removed the duplicate top-level `encoder:` overwrite in:
  - [brain_endogenous_public_parity.yaml](/G:/flysim/configs/brain_endogenous_public_parity.yaml)
  - [brain_endogenous_public_parity_routed_only.yaml](/G:/flysim/configs/brain_endogenous_public_parity_routed_only.yaml)
- Expanded the fit-head global feature seam so the parity head can now see slow endogenous backend state directly instead of only coarse voltage/global background summaries.

2. What succeeded

- The poisoned Aimon replay path is gone:
  - spontaneous trials no longer hard-code all-zero regressors
  - forced trials no longer apply `abs()` or per-trial max normalization
  - invalid `window_start/window_stop` metadata no longer collapses trials to constants or tail-stretched covariates
- The scorer is no longer zero-lag-only. It now reports both strict zero-lag metrics and best local lag metrics for imaging-like traces.
- The first-order phase bug in the public body-feedback lane is fixed:
  - Aimon no longer duplicates transition-derived drive into multiple positive channels
  - state and transition drives are now separated in the encoder
- The endogenous backend now has distinct public exafference target tracking in addition to internal arousal dynamics.
- Focused validation passed:
  - `python -m pytest tests/test_public_neural_measurement_harness.py tests/test_aimon_canonical_dataset.py tests/test_public_body_feedback.py tests/test_aimon_spontaneous_fit.py tests/test_spontaneous_state_unit.py tests/test_aimon_parity_harness.py tests/test_schaffer_parity_harness.py -q`
  - `51 passed, 1 warning`
- The Aimon canonical bundle was regenerated from the staged public dataset:
  - [aimon2023_canonical_bundle.json](/G:/flysim/outputs/derived/aimon2023_canonical/aimon2023_canonical_bundle.json)
  - [aimon2023_canonical_summary.json](/G:/flysim/outputs/derived/aimon2023_canonical/aimon2023_canonical_summary.json)
- The first repaired short exact-identity forced retest is live:
  - [aimon_b350_forced_window_routed_v5_replayfix](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v5_replayfix)

3. What failed

- No scientific retest result exists yet from the repaired path in this log entry.
- The live `B350_forced_walk` rerun has not written its final summary yet, so there is no post-fix timing verdict here.

4. Evidence

- [public_neural_measurement_harness.py](/G:/flysim/src/analysis/public_neural_measurement_harness.py)
- [aimon_parity_harness.py](/G:/flysim/src/analysis/aimon_parity_harness.py)
- [schaffer_parity_harness.py](/G:/flysim/src/analysis/schaffer_parity_harness.py)
- [aimon_canonical_dataset.py](/G:/flysim/src/analysis/aimon_canonical_dataset.py)
- [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py)
- [public_body_feedback.py](/G:/flysim/src/analysis/public_body_feedback.py)
- [encoder.py](/G:/flysim/src/bridge/encoder.py)
- [pytorch_backend.py](/G:/flysim/src/brain/pytorch_backend.py)
- [brain_endogenous_public_parity.yaml](/G:/flysim/configs/brain_endogenous_public_parity.yaml)
- [brain_endogenous_public_parity_routed_only.yaml](/G:/flysim/configs/brain_endogenous_public_parity_routed_only.yaml)

5. Next actions

- Wait for the repaired `B350_forced_walk` retest to finish:
  - [aimon_b350_forced_window_routed_v5_replayfix](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v5_replayfix)
- Compare it directly against:
  - [aimon_b350_forced_window_routed_v2_cont](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v2_cont/aimon_spontaneous_fit_summary.json)
  - [aimon_b350_forced_window_routed_v4_bodyfeedback](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v4_bodyfeedback/aimon_spontaneous_fit_summary.json)
- Use the repaired run to decide whether the remaining miss is still backend temporal state, forced/exafferent regulation, or the public body-feedback encoding itself.

## 2026-04-01 - Added grounded public reafferent channels to the parity harness

1. What I did

- Implemented a new shared public body-feedback helper:
  - [public_body_feedback.py](/G:/flysim/src/analysis/public_body_feedback.py)
- Extended [BodyObservation](/G:/flysim/src/body/interfaces.py) with grounded
  reafferent fields that can be derived from staged public data without
  inventing new sensor IDs:
  - `forward_accel`
  - `walk_state`
  - `stop_state`
  - `transition_on`
  - `transition_off`
  - `behavioral_state_level`
  - `behavioral_state_transition`
- Upgraded [encoder.py](/G:/flysim/src/bridge/encoder.py) so those channels now
  contribute to the existing public mechanosensory seam and its subgroup pools:
  - `mech_ce_bilateral`
  - `mech_f_bilateral`
  - `mech_dm_bilateral`
- Patched both parity harnesses to use grounded reafferent observations instead
  of only a numb scalar speed/contact proxy:
  - [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py)
  - [schaffer_spontaneous_fit.py](/G:/flysim/src/analysis/schaffer_spontaneous_fit.py)
- Added parity-config encoder gains in:
  - [brain_endogenous_public_parity.yaml](/G:/flysim/configs/brain_endogenous_public_parity.yaml)
  - [brain_endogenous_public_parity_routed_only.yaml](/G:/flysim/configs/brain_endogenous_public_parity_routed_only.yaml)
- Added focused regression coverage:
  - [test_public_body_feedback.py](/G:/flysim/tests/test_public_body_feedback.py)
  - [test_aimon_spontaneous_fit.py](/G:/flysim/tests/test_aimon_spontaneous_fit.py)
  - [test_schaffer_spontaneous_fit.py](/G:/flysim/tests/test_schaffer_spontaneous_fit.py)
  - [test_bridge_unit.py](/G:/flysim/tests/test_bridge_unit.py)

2. What succeeded

- The public-parity harness is no longer limited to:
  - scalar `forward_speed`
  - scalar `contact_force`
  - fixed pose / zero yaw / zero richer state
- Aimon reafference is now derived from the staged walk regressor itself, which
  means spontaneous windows are no longer forced through a completely numb body
  path.
- Schaffer reafference is now derived from staged ball-motion and behavioral
  state arrays rather than only a single scalar motion regressor.
- Focused validation passed:
  - `python -m pytest tests/test_public_body_feedback.py tests/test_aimon_spontaneous_fit.py tests/test_schaffer_spontaneous_fit.py tests/test_bridge_unit.py -q`
  - `56 passed, 1 warning`

3. Evidence

- [public_body_feedback.py](/G:/flysim/src/analysis/public_body_feedback.py)
- [interfaces.py](/G:/flysim/src/body/interfaces.py)
- [encoder.py](/G:/flysim/src/bridge/encoder.py)
- [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py)
- [schaffer_spontaneous_fit.py](/G:/flysim/src/analysis/schaffer_spontaneous_fit.py)
- [brain_endogenous_public_parity.yaml](/G:/flysim/configs/brain_endogenous_public_parity.yaml)
- [brain_endogenous_public_parity_routed_only.yaml](/G:/flysim/configs/brain_endogenous_public_parity_routed_only.yaml)

4. Next actions

- Wait for the live exact-identity routed-only Aimon reruns to finish:
  - [aimon_b350_spont_window_routed_v4_reafferent](/G:/flysim/outputs/metrics/aimon_b350_spont_window_routed_v4_reafferent)
  - [aimon_b350_forced_window_routed_v3_reafferent](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v3_reafferent)
- Use those two runs to decide whether grounded reafference materially reduces
  the spontaneous/forced gap or whether the next backend change has to target
  explicit exafferent late-state regulation.

## 2026-03-30 - Killed active WSL Schaffer job and completed T202/T203 endogenous backend slices

1. What I did

- Killed the active WSL/host Schaffer continuity fit job so the workspace was
  no longer carrying a stale parity run:
  - host process `2504`
  - command: `scripts/run_schaffer_spontaneous_fit.py ... --output-dir outputs/metrics/schaffer_spontaneous_fit_2022_train4_test2_continuous`
- Implemented `T202` in the production backend:
  - added `backend_dynamics` config parsing and grouped parameter scaffolding
  - split the old diagnostic surrogate from the new endogenous path
- Implemented `T203`:
  - added backend-internal adaptation current
  - added backend-internal filtered intrinsic noise state
  - wired both only into the `endogenous` spontaneous path

2. What succeeded

- The old spontaneous surrogate is now cleanly separable in code. It is no
  longer silently tied to the future endogenous production path.
- The endogenous path now has its first real internal state sources:
  - `adaptation_current`
  - `intrinsic_noise_state`
- Focused validation passed:
  - `python -m pytest tests/test_spontaneous_state_unit.py tests/test_brain_backend.py -q`
  - `17 passed`

3. Evidence

- [pytorch_backend.py](/G:/flysim/src/brain/pytorch_backend.py)
- [closed_loop.py](/G:/flysim/src/runtime/closed_loop.py)
- [test_spontaneous_state_unit.py](/G:/flysim/tests/test_spontaneous_state_unit.py)
- [test_brain_backend.py](/G:/flysim/tests/test_brain_backend.py)
- [endogenous_spontaneous_replacement_plan.md](/G:/flysim/docs/endogenous_spontaneous_replacement_plan.md)

4. Notes

- `T202` is now done.
- `T203` is now done.
- `T204` is now the active next slice.
- The endogenous path is still incomplete. It now avoids dependence on
  `background_rates`, but it is still spike-only in recurrence until graded
  release lands.

## 2026-03-30 - Completed T204 graded-release slice

1. What I did

- Added grouped graded-release state to the endogenous backend path.
- Added `spiking` / `graded` / `mixed` release modes to grouped backend
  dynamics.
- Added endogenous graded recurrent current on top of the existing spike
  recurrence.

2. What succeeded

- The endogenous backend now has a continuous signaling substrate beyond pure
  spike-only recurrence.
- Nonspiking release modes now produce a real graded release state under
  depolarization, while pure spiking mode keeps that state at zero.
- Focused validation passed:
  - `python -m pytest tests/test_spontaneous_state_unit.py tests/test_brain_backend.py -q`
  - `18 passed`

3. Evidence

- [pytorch_backend.py](/G:/flysim/src/brain/pytorch_backend.py)
- [test_spontaneous_state_unit.py](/G:/flysim/tests/test_spontaneous_state_unit.py)
- [test_brain_backend.py](/G:/flysim/tests/test_brain_backend.py)

4. Next actions

- Move to `T205`: multi-class synaptic heterogeneity in the production backend.

## 2026-03-30 - Completed T205 and first T206 slice, then opened T207 tiny-readout mode

1. What I did

- Replaced the old single synaptic low-pass assumption in the production
  backend with explicit synapse classes:
  - `fast_exc`
  - `slow_exc`
  - `fast_inh`
  - `slow_inh`
  - `modulatory`
- Added internal slow neuromodulatory state variables:
  - `modulatory_arousal_state`
  - `modulatory_exafference_state`
- Wired those states to gate:
  - endogenous current / excitability
  - adaptation
  - release and synaptic gain
- Opened `T207` by adding a real `tiny` readout mode to both Aimon and
  Schaffer parity lanes.

2. What succeeded

- The production backend now has multi-class synaptic heterogeneity rather than
  one undifferentiated filtered recurrence path.
- The endogenous path now has internal neuromodulatory state instead of relying
  only on intrinsic noise, adaptation, and graded release.
- The parity harness can now run with a deliberately tiny readout that keeps:
  - globals
  - covariates
  - a capped number of bilateral features
- Focused validation passed:
  - `python -m pytest tests/test_aimon_spontaneous_fit.py tests/test_spontaneous_state_unit.py tests/test_brain_backend.py -q`
  - `23 passed`

3. Evidence

- [pytorch_backend.py](/G:/flysim/src/brain/pytorch_backend.py)
- [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py)
- [schaffer_spontaneous_fit.py](/G:/flysim/src/analysis/schaffer_spontaneous_fit.py)
- [test_aimon_spontaneous_fit.py](/G:/flysim/tests/test_aimon_spontaneous_fit.py)
- [test_spontaneous_state_unit.py](/G:/flysim/tests/test_spontaneous_state_unit.py)
- [test_brain_backend.py](/G:/flysim/tests/test_brain_backend.py)

4. Next actions

- Run Aimon and Schaffer with the endogenous backend plus `tiny` readout mode.
- Compare tiny-readout held-out fit against the richer readout to see whether
  the backend is starting to carry the score.

## 2026-03-30 - Exact endogenous replacement plan defined under the strict spontaneous-state rule

1. What I did

- Used sub-agent review plus local code inspection to define the exact
  production path for replacing the current spontaneous-state surrogate.
- Wrote the concrete replacement plan into a dedicated design note and split it
  into new tracked execution tasks.

2. What succeeded

- The repo now has one explicit answer to "how do we meet the real goal under
  the strict rule?":
  - freeze the current surrogate as diagnostic-only
  - replace it with an endogenous production backend built from:
    - intrinsic cell dynamics
    - graded transmission
    - synaptic heterogeneity
    - neuromodulatory state
  - fit that backend to Aimon and Schaffer with a deliberately tiny readout
  - only then resume downstream decoder / embodiment work
- The exact production target and gates are now recorded in:
  - [endogenous_spontaneous_replacement_plan.md](/G:/flysim/docs/endogenous_spontaneous_replacement_plan.md)
- New tracked implementation tasks were added:
  - `T202` to `T207`

3. Key code-level finding

- The current spontaneous surrogate is conclusively an input prior, not an
  endogenous mechanism, because [pytorch_backend.py](/G:/flysim/src/brain/pytorch_backend.py)
  still advances spontaneous state through `background_rates` and then injects
  it via `_build_inputs()` into `self.rates`.

4. Sub-agent synthesis

- backend architecture review:
  - minimum acceptable replacement is a mixed-mode generalized LIF backend with
    adaptation, intrinsic filtered noise, graded release, multi-class synapses,
    and internal modulatory states
- data-identifiability review:
  - Aimon and Schaffer are enough to constrain a mesoscale endogenous mechanism
    if the head is kept tiny and the backend carries the fit
- shortest-honest-path review:
  - freeze all new downstream decoder / Creamer / embodiment tuning until the
    endogenous backend clears neural-parity gates

5. Evidence

- [endogenous_spontaneous_replacement_plan.md](/G:/flysim/docs/endogenous_spontaneous_replacement_plan.md)
- [TASKS.md](/G:/flysim/TASKS.md)
- [pytorch_backend.py](/G:/flysim/src/brain/pytorch_backend.py)

6. Next actions

- Start `T202` in the production backend.
- Keep the current surrogate branch diagnostic-only.

## 2026-03-30 - Spontaneous-state acceptance bar made strict

1. What I changed

- Tightened the repo rule for spontaneous state so there is no ambiguity left.
- Updated the task tracker and design/result docs to explicitly disqualify the
  current structured-drive spontaneous regime as a final mechanism.

2. What succeeded

- The repo now states the hard constraint directly:
  - acceptable spontaneous endogenous state must emerge from richer intrinsic
    cell dynamics, graded transmission, synaptic heterogeneity, or
    neuromodulatory state
- The current structured background-drive / latent-drive regime is now labeled
  diagnostic-only rather than merely "not yet ideal".
- `T201` now reflects mandatory replacement work, not optional tightening.

3. What failed or remains open

- The current spontaneous backend still uses structured background drive, so it
  remains outside the final acceptance set.
- No replacement richer-endogenous spontaneous mechanism has been implemented
  yet.

4. Evidence

- [TASKS.md](/G:/flysim/TASKS.md)
- [spontaneous_state_backend_design.md](/G:/flysim/docs/spontaneous_state_backend_design.md)
- [spontaneous_state_results.md](/G:/flysim/docs/spontaneous_state_results.md)
- [ASSUMPTIONS_AND_GAPS.md](/G:/flysim/ASSUMPTIONS_AND_GAPS.md)
- [public_neural_measurement_parity_program.md](/G:/flysim/docs/public_neural_measurement_parity_program.md)

5. Next actions

- Keep using the existing surrogate only for diagnosis while parity work
  continues.
- Treat final spontaneous-state acceptance as blocked on a richer endogenous
  backend mechanism.

## 2026-03-30 - Systemic parity mismatch narrowed to session continuity and imaging readout physics

1. What I attempted

- Reframed the parity problem away from one-off evaluator bugs and toward the systemic digital mismatch between the spontaneous model and living recordings.
- Audited the Schaffer 2022 canonical timing structure instead of treating its exported intervals as independent trials.
- Patched the Schaffer spontaneous-fit harness so one session can replay as one persistent neural state.
- Added an optional shared imaging observation basis so Aimon and Schaffer fits no longer assume raw voltage projects instantaneously into `dff` / `dff_like` traces.

2. What succeeded

- Verified the Schaffer 2022 interval structure is exactly contiguous:
  - `trial_000 29.6815 -> 299.9877 s`
  - `trial_001 299.9877 -> 599.9753 s`
  - `trial_002 599.9753 -> 899.9630 s`
  - `trial_003 899.9630 -> 1199.9507 s`
  - `trial_004 1199.9507 -> 1499.9384 s`
  - `trial_005 1499.9384 -> 1799.9260 s`
- This exposed a real digital mismatch in the old parity harness: it reset the spontaneous brain between intervals that are actually one continuous recording session.
- Patched `src/analysis/schaffer_spontaneous_fit.py` and `scripts/run_schaffer_spontaneous_fit.py` to support continuity-preserving replay, including explicit session-key ordering, inter-interval gap stepping, and a `--no-preserve-session-state` control path.
- Added test coverage for the continuity seam and kept the focused Schaffer suite green:
  - `11 passed`
- Confirmed a second systemic mismatch:
  - Schaffer canonical modality is `roi_dff_timeseries`
  - Aimon canonical traces are tagged `dff_like`
  - the old fit path used an instantaneous linear voltage projection with no measurement model
- Added a shared optional causal low-pass imaging observation basis:
  - `src/analysis/imaging_observation_model.py`
  - threaded into both Aimon and Schaffer replay scripts
- Focused observation-model coverage passed:
  - `12 passed`

3. What failed

- The corrected continuous Schaffer holdout is still running, so the size of the continuity effect is not known yet.
- The first Aimon held-out rerun with the new imaging observation basis is also still running, so the size of the measurement-physics effect is not known yet.
- Therefore the systemic root cause is narrowed but not yet fully ranked.

4. Evidence paths

- `outputs/derived/schaffer2023_nwb_canonical/schaffer2023_nwb_canonical_bundle.json`
- `outputs/metrics/schaffer_spontaneous_fit_2022_train4_test2/schaffer_spontaneous_fit_summary.json`
- `src/analysis/schaffer_spontaneous_fit.py`
- `scripts/run_schaffer_spontaneous_fit.py`
- `tests/test_schaffer_spontaneous_fit.py`
- `src/analysis/imaging_observation_model.py`
- `src/analysis/aimon_spontaneous_fit.py`
- `tests/test_imaging_observation_model.py`

5. Next actions

- Finish the corrected continuity-preserving Schaffer holdout and compare it directly against the old broken-reset result.
- Finish the Aimon held-out rerun with the imaging observation basis and compare it against `v3 force2`.
- Rank the two systemic effects:
  - missing persistent hidden-state semantics
  - missing imaging measurement physics
- Only after that, decide whether the remaining delta is mostly intrinsic dynamics, observation mapping, or both.

## 2026-03-30 - LIF ceiling clarified and spontaneous-state honesty boundary tightened

1. What I attempted

- Assessed whether the current whole-brain LIF model itself is the main root
  cause of the parity miss.
- Audited the current spontaneous-state implementation against the repo's
  no-hacks rule.

2. What succeeded

- Confirmed the production backend is an alpha-filtered, delayed, refractory
  point-neuron LIF network with globally shared parameters rather than richer
  graded or conductance-based physiology.
- Recorded the current best verdict:
  - LIF is a real ceiling for exact imaging-space physiological parity
  - LIF does not currently look like the strongest blocker for the repo's
    present parity failures
- Recorded the stronger honesty clarification for spontaneous state:
  - it is not a decoder-side hack
  - it is not a body-side hack
  - but it **is** still a backend-internal surrogate prior implemented as
    structured background drive rather than emergent intrinsic physiology
- Added the new follow-up task `T201` so this does not get silently normalized
  as the final answer.

3. What failed

- I cannot honestly defend the current spontaneous-state mechanism as fully
  clearing the strongest possible interpretation of the repo's no-hacks rule.
- If that rule is taken to forbid exogenous brain priors, the current
  spontaneous-state mechanism remains provisional and non-final.

4. Evidence paths

- `src/brain/pytorch_backend.py`
- `docs/spontaneous_state_backend_design.md`
- `ASSUMPTIONS_AND_GAPS.md`
- `TASKS.md`

5. Next actions

- Keep testing the stronger current systemic mismatch candidates first:
  - continuity
  - imaging observation model
- If those do not collapse the parity gap enough, replace or sharply constrain
  the current spontaneous-state surrogate instead of pretending it is the final
  physiological mechanism.



## 2026-03-08 - Phase 0 scouting and scaffold


1. What I attempted

- Read `AGENTS.MD` and extracted the required phase order, artifact list, and task-tracking rules.

- Inspected host and WSL capabilities.

- Verified public repo availability and cloned / checked out the candidate repos for the brain and body stacks.

- Inspected README, environment, benchmark, and example files to determine what already exists versus what must be built here.



2. What succeeded

- Confirmed WSL2 is present with `Ubuntu-24.04`.

- Confirmed dual RTX 5060 Ti GPUs are visible on the host and inside WSL.

- Cloned `eonsystemspbc/fly-brain` and `NeLy-EPFL/flygym`.

- Recovered a partial `philshiu/Drosophila_brain_model` clone by fetching and checking out `FETCH_HEAD`.

- Verified that `fly-brain` contains ready benchmark runners for Brian2 CPU, Brian2CUDA, PyTorch, and NEST GPU, but not an online body bridge.

- Verified that `flygym` contains realistic vision and closed-loop embodied controllers, but not a whole-brain bridge to the Shiu/Eon model.

- Identified public neuron IDs in the notebook artifacts for locomotor descending neurons (`P9`, `DNa01`, `DNa02`, `MDN`) and sensory proxy pools (`LC4`, `JON`).



3. What failed

- The initial clone of `external/Drosophila_brain_model` did not finish checkout cleanly; only `.git` was present.

- Resolved by running `git -C external/Drosophila_brain_model fetch --depth 1 origin main` followed by `git checkout FETCH_HEAD`.

- No full production environment has been provisioned yet, so FlyGym realistic-vision execution is not yet validated on this machine.



4. Evidence paths

- `external/fly-brain`

- `external/Drosophila_brain_model`

- `external/flygym`

- `docs/architecture_scout.md`

- `docs/dependency_matrix.md`

- `docs/repo_gap_analysis.md`



5. Next actions
- Implement bootstrap scripts and a split-environment strategy that keeps Brian2/Brian2CUDA benchmarks separate from the modern FlyGym full-stack runtime.
- Build the Torch whole-brain online backend and the mock/FlyGym body adapters.
- Write tests first for the bridge logic and a deterministic smoke closed loop.

## 2026-03-26 - Pires 2024 steering-circuit review and integration

1. What I attempted
- Read the Nature paper `s41586-023-07006-3` on allocentric-goal to egocentric-steering conversion in `Drosophila`.
- Checked whether its claims directly constrain the current OpenFly steering and perturbation work.
- Integrated the resulting interpretation into the canonical behavior spec and manuscript.

2. What succeeded
- Confirmed the paper is directly relevant to the current jump-target / steering problem.
- Recorded a focused literature note at `docs/pires2024_allocentric_goal_to_steering_note.md`.
- Updated `docs/behavior_target_set.md` so perturbation recovery is framed more explicitly as heading / goal recovery rather than generic moving-target pursuit.
- Updated `docs/openfly_whitepaper.md` to connect the current perturbation assay to the paper's central-complex steering circuit and to state that strict frontal refixation is harsher than the cited cue-jump paradigm when the target keeps moving tangentially.
- Marked the literature-integration task complete in `TASKS.md`.

3. What failed
- The paper does not supply a turnkey implementation path for our whole-brain model.
- It does not resolve FlyWire-root identity mapping for all relevant steering neurons.
- It therefore sharpens the biological target but does not by itself complete the steering decode problem.

4. Evidence paths
- `docs/pires2024_allocentric_goal_to_steering_note.md`
- `docs/behavior_target_set.md`
- `docs/openfly_whitepaper.md`
- `https://www.nature.com/articles/s41586-023-07006-3`

5. Next actions
- Use the paper's `EPG -> FC2 -> PFL3 -> LAL` scaffold to define a more explicit brain-side heading / goal / steering latent for future embodied steering work.
- Add a less punitive cue-jump assay that separates correct corrective steering from the physical difficulty of recapturing a continuously moving tangential target.

## 2026-03-28 - Creamer 2018 visual speed-control review

1. What I attempted
- Read the local PDF `mmc4.pdf`.
- Identified the paper and extracted its actual claims.
- Compared those claims against the current living-branch architecture and repo artifacts.

2. What succeeded
- Confirmed `mmc4.pdf` is Creamer, Mano, Clark 2018, *Visual Control of Walking Speed in Drosophila*.
- Wrote a claim-by-claim replication note at `docs/creamer2018_visual_speed_control_note.md`.
- Added visual speed regulation / slowing near nearby objects to the canonical behavior target set in `docs/behavior_target_set.md`.
- Recorded the verdict in `TASKS.md`.

3. What failed
- The current repo does not yet replicate the paper's controlled findings.
- We do not yet run:
  - open-loop visual speed-tuning sweeps
  - the closed-loop gain-manipulation assay
  - the hourglass nearby-object slowing assay
  - `T4` / `T5` causal ablations
  - the paper's multi-motion-detector model fit

4. Evidence paths
- `mmc4.pdf`
- `docs/creamer2018_visual_speed_control_note.md`
- `docs/behavior_target_set.md`

5. Next actions
- Treat visual translational-speed control as a separate grounded benchmark from steering / fixation.
- Build the paper-style gain-stabilization and nearby-object slowing assays on top of the existing realistic-vision loop.
- Add a `T4` / `T5` ablation path so the repo can test causal dependence rather than only architectural overlap.

## 2026-03-29 - Public neural measurement parity registry, schema, and first staging lane

1. What I attempted
- Promoted the new top-level priority program from note-only status into code and staged artifacts.
- Generalized the old Aimon-only spontaneous-data path into a broader public neural measurement registry.
- Added a canonical matched-format schema and a first generic trace-parity harness.
- Staged the first public metadata/manifests for Aimon, Schaffer, Ketkar, Dallmann, and Shomar.
- Used all six available sub-agent slots for disjoint source research and harness prioritization.

2. What succeeded
- Added the source registry:
  - `src/brain/public_neural_measurement_sources.py`
- Added the generic manifest/staging layer:
  - `src/analysis/public_neural_measurement_dataset.py`
  - `scripts/fetch_public_neural_measurements.py`
- Added the canonical schema:
  - `src/analysis/public_neural_measurement_schema.py`
  - `docs/public_neural_measurement_schema.md`
- Added the first generic parity harness:
  - `src/analysis/public_neural_measurement_harness.py`
- Added the stage-status summarizer:
  - `scripts/summarize_public_neural_measurement_status.py`
- Focused coverage passed:
  - `9 passed` on the new public-neural-measurement source/schema/dataset/harness slice.
- Real staging artifacts now exist:
  - Aimon full staging under `external/spontaneous/aimon2023_dryad`
  - Schaffer article JSON, manifest, files table, and `datasets_for_each_figure.xlsx`
  - Ketkar record JSON, manifest, and files table
  - Dallmann Dryad dataset/versions/files metadata plus manifest/files table
  - Shomar Dryad dataset/versions/files metadata plus manifest/files table
- Canonical status output now exists:
  - `outputs/metrics/public_neural_measurement_stage_status.json`
  - `outputs/metrics/public_neural_measurement_stage_status.csv`

3. What failed
- The direct scripted Dryad raw-file path remains blocked for the new program:
  - API download URLs return `401`
  - direct `file_stream` URLs return `403`
- Gruntman 2019 authoritative endpoints are identified, but the local manifest artifact is not staged yet.
- The generic Python fetch path against some large external hosts was slower/less reliable than direct `curl`, so part of the staging work used explicit record-JSON pulls and local normalization rather than only the new fetch script.

4. Evidence paths
- `docs/public_neural_measurement_parity_program.md`
- `docs/public_neural_measurement_schema.md`
- `docs/public_neural_measurement_dataset_status.md`
- `outputs/metrics/public_neural_measurement_stage_status.json`
- `outputs/metrics/public_neural_measurement_aimon2023_dryad_manifest.json`
- `outputs/metrics/public_neural_measurement_schaffer2023_figshare_manifest.json`
- `outputs/metrics/public_neural_measurement_ketkar2022_zenodo_manifest.json`
- `outputs/metrics/public_neural_measurement_dallmann2025_dryad_manifest.json`
- `outputs/metrics/public_neural_measurement_shomar2025_dryad_manifest.json`

5. Next actions
- Stage the Gruntman 2019 collection/article manifests and the first figure zip.
- Promote dataset-specific adapters for Aimon, Schaffer, Ketkar, and Dallmann.
- Build the first open-loop replay harnesses against the spontaneous brain before returning to downstream decoder interpretation.

## 2026-03-29 - First real canonical exports: Aimon whole-brain windows and Gruntman Figure 2 traces

1. What I attempted
- Validated and hardened the first Aimon canonical exporter against the already staged local Aimon source.
- Fixed the exporter so `--max-experiments` counts surviving canonical experiments rather than stopping on invalid overlapping rows.
- Added the first direct raw-trace adapter for Gruntman 2019 Figure 2 using the locally staged Janelia zip.
- Exported both datasets into the canonical matched-format schema.

2. What succeeded
- Aimon canonical exporter is now real and test-covered:
  - `src/analysis/aimon_canonical_dataset.py`
  - `scripts/export_aimon_canonical_dataset.py`
  - `tests/test_aimon_canonical_dataset.py`
- Real Aimon canonical export now exists:
  - `outputs/derived/aimon2023_canonical/aimon2023_canonical_summary.json`
  - `outputs/derived/aimon2023_canonical/aimon2023_canonical_bundle.json`
- Aimon result:
  - `exported_experiment_count = 2`
  - `trial_count = 4`
  - surviving public experiments: `B350`, `B1269`
- Gruntman Figure 2 canonical exporter is now real and test-covered:
  - `src/analysis/gruntman_figure2_canonical_dataset.py`
  - `scripts/export_gruntman_figure2_canonical_dataset.py`
  - `tests/test_gruntman_figure2_canonical_dataset.py`
- Real Gruntman Figure 2 canonical export now exists:
  - `outputs/derived/gruntman2019_figure2_canonical/gruntman2019_figure2_canonical_summary.json`
  - `outputs/derived/gruntman2019_figure2_canonical/gruntman2019_figure2_canonical_bundle.json`
- Gruntman result:
  - `trial_count = 514`
  - `skipped_condition_count = 540`
  - raw membrane-potential traces at `20 kHz`
- Focused coverage passed:
  - `4 passed` on the Aimon exporter/schema slice
  - `3 passed` on the Gruntman exporter/schema slice
- The stage-status artifact was refreshed after Gruntman staging:
  - `outputs/metrics/public_neural_measurement_stage_status.json`

3. What failed
- Dryad raw-file delivery remains blocked for Dallmann and Shomar.
- Schaffer and Ketkar still have staged metadata but not canonical exporters yet.
- No spontaneous-brain replay/fitting run has been executed on the new canonical bundles yet.

4. Evidence paths
- `docs/public_neural_measurement_dataset_status.md`
- `outputs/derived/aimon2023_canonical/aimon2023_canonical_summary.json`
- `outputs/derived/gruntman2019_figure2_canonical/gruntman2019_figure2_canonical_summary.json`
- `outputs/metrics/public_neural_measurement_stage_status.json`

5. Next actions
- Build the first Aimon replay/fitting harness against the spontaneous brain.
- Add the next dataset-specific exporter after Aimon and Gruntman.
- Keep downstream decoder/embodiment work frozen until the parity program starts producing measurement-match results.

## 2026-03-29 - First targeted Aimon scoring harness

1. What I attempted
- Built the first dataset-specific scoring harness on top of the canonical Aimon export instead of stopping at file conversion.
- Used the already-exported canonical bundle as the observed side and added a direct trial-matrix scoring path for future spontaneous-brain replay output.

2. What succeeded
- Added:
  - `src/analysis/aimon_parity_harness.py`
  - `tests/test_aimon_parity_harness.py`
- Focused coverage passed:
  - `4 passed` on the Aimon harness plus canonical-export regression slice
- The parity program now has:
  - staged public source
  - canonical Aimon bundle
  - trial-matrix scoring surface

3. What failed
- The spontaneous brain has not been connected into this harness yet, so there are still no real measurement-match scores from live simulated traces.

4. Evidence paths
- `src/analysis/aimon_parity_harness.py`
- `tests/test_aimon_parity_harness.py`
- `outputs/derived/aimon2023_canonical/aimon2023_canonical_bundle.json`

5. Next actions
- Connect spontaneous-brain replay/projection output into the Aimon harness.
- Use that as the first real dataset-by-dataset parity optimization loop.

## 2026-03-08 - Bridge, tests, and first runnable artifacts

1. What I attempted
- Implemented the in-repo bridge/runtime stack under `src/`.
- Added WSL/bootstrap/check scripts and environment requirement files.
- Wrote mock-path smoke/unit tests and standalone benchmark scripts.
- Ran the mock-path tests and both mock and real-Torch benchmark/demo commands.

2. What succeeded
- Added a persistent Torch whole-brain backend in `src/brain/pytorch_backend.py`.
- Added mock and FlyGym body adapters in `src/body/`.
- Added realistic-vision feature extraction plus sensory encoder and motor decoder.
- Added the closed-loop scheduler in `src/runtime/closed_loop.py`.
- Test suite passed:
  - `tests/test_imports.py`
  - `tests/test_bridge_unit.py`
  - `tests/test_closed_loop_smoke.py`
  - `tests/test_realistic_vision_path.py`
  - `tests/test_benchmark_output_format.py`
  - `tests/test_artifact_generation.py`
- Produced benchmark CSVs and plots:
  - `outputs/benchmarks/brain_benchmarks.csv`
  - `outputs/benchmarks/body_benchmarks.csv`
  - `outputs/benchmarks/vision_benchmarks.csv`
  - `outputs/benchmarks/fullstack_benchmarks.csv`
- Produced runnable mock demo artifacts including video:
  - `outputs/demos/mock-demo-20260308-110632/demo.mp4`
  - `outputs/demos/mock-demo-20260308-110632/run.jsonl`
  - `outputs/demos/mock-demo-20260308-110632/metrics.csv`

3. What failed
- I have not yet executed the real FlyGym realistic-vision runtime on this machine.
- I have not yet provisioned the separate Brian2/Brian2CUDA benchmark environment.
- I started an exploratory WSL `flygym[examples]` install in a throwaway venv, but stopped it before completion once it reached the very large Torch wheel download; there is still no validated WSL FlyGym result to report.
- Therefore the true production body/vision/full-stack parity gate remains open.

4. Evidence paths
- `src/brain/pytorch_backend.py`
- `src/body/mock_body.py`
- `src/body/flygym_runtime.py`
- `src/bridge/encoder.py`
- `src/bridge/decoder.py`
- `src/runtime/closed_loop.py`
- `outputs/benchmarks/brain_benchmarks.csv`
- `outputs/benchmarks/fullstack_benchmarks.csv`
- `outputs/demos/mock-demo-20260308-110632/summary.json`

5. Next actions
- Provision the WSL `flysim-full` and `flysim-brain-brian2` environments via the new scripts.
- Validate `scripts/check_cuda.sh` and `scripts/check_mujoco.sh` inside WSL.
- Run the real FlyGym realistic-vision path and capture the first non-mock demo artifacts.
- Add at least one secondary neural backend benchmark if the WSL env comes up cleanly.

## 2026-03-08 - WSL provisioning, real FlyGym validation, and second neural backend

1. What I attempted
- Normalized the shell scripts under `scripts/*.sh` to LF line endings after the first WSL bootstrap failed on `set -euo pipefail`.
- Ran `scripts/bootstrap_wsl.sh` and `scripts/bootstrap_env.sh` inside WSL from `/mnt/g/flysim`.
- Validated `scripts/check_cuda.sh` and `scripts/check_mujoco.sh` in the WSL `flysim-full` environment.
- Fixed missing public-environment glue for the realistic-vision stack:
  - added `cachetools` to `environment/requirements-full.txt`
  - added `flyvis download-pretrained` to `scripts/bootstrap_env.sh`
  - added a CPU-vision fallback flag in `src/body/flygym_runtime.py`
  - fixed a double-close bug in `src/body/flygym_runtime.py`
- Extended the benchmark scripts so they can exercise real WSL workloads:
  - `benchmarks/run_body_benchmarks.py --mode flygym`
  - `benchmarks/run_vision_benchmarks.py --mode flygym`
  - `benchmarks/run_brain_benchmarks.py --backend brian2cpu`
- Patched the checked-out public `external/fly-brain` copy for current Brian2 compatibility:
  - `external/fly-brain/code/run_brian2_cuda.py`
  - `external/fly-brain/code/benchmark.py`
- Ran real WSL production commands:
  - `python benchmarks/run_body_benchmarks.py --config configs/flygym_realistic_vision.yaml --mode flygym --durations 0.02 0.05`
  - `python benchmarks/run_vision_benchmarks.py --config configs/flygym_realistic_vision.yaml --mode flygym --duration 0.02`
  - `python benchmarks/run_fullstack_with_realistic_vision.py --config configs/flygym_realistic_vision.yaml --mode flygym --duration 0.02`
  - `python benchmarks/run_fullstack_with_realistic_vision.py --config configs/flygym_realistic_vision.yaml --mode flygym --duration 0.05`
  - `python benchmarks/run_brain_benchmarks.py --config configs/default.yaml --backend brian2cpu --durations 0.1`

2. What succeeded
- WSL bootstrap now completes end-to-end:
  - `scripts/bootstrap_wsl.sh`
  - `scripts/bootstrap_env.sh`
- The WSL full-stack environment now imports and runs:
  - `mujoco`
  - `dm_control`
  - `flygym`
  - FlyVis pretrained model download
- Real FlyGym realistic-vision runtime now resets, steps, and closes locally in WSL.
- Real FlyGym benchmark evidence now exists:
  - body benchmark: `outputs/benchmarks/body_benchmarks.csv`
  - realistic-vision benchmark: `outputs/benchmarks/vision_benchmarks.csv`
  - full-stack realistic-vision benchmark: `outputs/benchmarks/fullstack_benchmarks.csv`
- Real closed-loop demo artifacts now exist:
  - `outputs/demos/flygym-demo-20260308-115338.mp4`
  - `outputs/logs/flygym-demo-20260308-115338.jsonl`
  - `outputs/metrics/flygym-demo-20260308-115338.csv`
  - `outputs/demos/flygym-demo-20260308-115954.mp4`
  - `outputs/logs/flygym-demo-20260308-115954.jsonl`
  - `outputs/metrics/flygym-demo-20260308-115954.csv`
- The second neural backend requirement is now satisfied with a real Brian2 CPU benchmark in WSL.
- `outputs/benchmarks/brain_benchmarks.csv` now carries both:
  - Torch on `cuda:0`
  - Brian2 CPU on WSL

3. What failed
- The public WSL PyTorch `cu126` wheel in `flysim-full` does not support the local RTX 5060 Ti `sm_120` GPUs. `torch.cuda.is_available()` is true, but the wheel warns that the GPU architecture is unsupported.
- Because of that public wheel limitation, the realistic-vision WSL runs currently need a CPU-only visibility fallback (`force_cpu_vision: true` / `CUDA_VISIBLE_DEVICES=''`) to keep FlyVis stable.
- The first Brian2 env attempt failed because:
  - `brian2cuda==1.0a7` conflicted with `brian2==2.5.1`
  - newer `setuptools` in the env did not expose `pkg_resources`
  - the checked-out `external/fly-brain` Brian2 code needed a local patch for the current `CPPStandaloneDevice.run(...)` signature
- I have not yet completed the â€œlongest stableâ€ real FlyGym parity run or updated the final parity report / README with these new measurements.

4. Evidence paths
- `scripts/bootstrap_wsl.sh`
- `scripts/bootstrap_env.sh`
- `environment/requirements-full.txt`
- `environment/requirements-brain-brian2.txt`
- `configs/flygym_realistic_vision.yaml`
- `src/body/flygym_runtime.py`
- `benchmarks/run_body_benchmarks.py`
- `benchmarks/run_vision_benchmarks.py`
- `benchmarks/run_brain_benchmarks.py`
- `external/fly-brain/code/run_brian2_cuda.py`
- `external/fly-brain/code/benchmark.py`
- `outputs/benchmarks/brain_benchmarks.csv`
- `outputs/benchmarks/body_benchmarks.csv`
- `outputs/benchmarks/vision_benchmarks.csv`
- `outputs/benchmarks/fullstack_benchmarks.csv`
- `outputs/demos/flygym-demo-20260308-115338/summary.json`
- `outputs/demos/flygym-demo-20260308-115954/summary.json`

5. Next actions
- Run the longest stable real FlyGym realistic-vision demo that is still practical on this machine and save the resulting artifacts.
- Update `docs/install_report.md`, `docs/benchmark_summary.md`, `docs/perf_tuning.md`, `docs/multi_gpu_evaluation.md`, `ASSUMPTIONS_AND_GAPS.md`, and `REPRO_PARITY_REPORT.md` with the WSL findings.
- Harden `README.md` so the documented quick start matches the now-validated WSL workflow exactly.

## 2026-03-18 - Living-branch mesoscale spontaneous-state validation

1. What I attempted
- Fixed the spontaneous-data validation seam on the living branch instead of treating mesoscale validation as a pure literature note.
- Added a public spontaneous-dataset registry plus a deterministic metadata fetch path for Aimon 2023 Dryad and related spontaneous-state anchors.
- Staged the Aimon 2023 `README.md` and `GoodICsdf.pkl` artifacts that were actually obtainable in this environment.
- Implemented a living-branch mesoscale validator over the spontaneous-refit `target` / `no_target` pair using run logs, activation captures, the FlyWire annotation supplement, and completeness ordering.
- Ran focused tests, metadata fetch, and the full validation script.

2. What succeeded
- The repo now has a real spontaneous-dataset source registry:
  - `src/brain/spontaneous_data_sources.py`
- The repo now has reusable public-dataset inspectors:
  - `src/analysis/public_spontaneous_dataset.py`
- The repo now fetches and records Aimon 2023 Dryad metadata and access status:
  - `scripts/fetch_spontaneous_public_data.py`
  - `external/spontaneous/aimon2023_dryad/spontaneous_public_dataset_aimon2023_dryad_manifest.json`
  - `external/spontaneous/aimon2023_dryad/spontaneous_public_dataset_aimon2023_dryad_access_report.json`
- The repo now stages the small Aimon 2023 artifacts already obtained:
  - `external/spontaneous/aimon2023_dryad/README.md`
  - `external/spontaneous/aimon2023_dryad/GoodICsdf.pkl`
- The first living-branch mesoscale validation bundle now exists:
  - `scripts/run_spontaneous_mesoscale_validation.py`
  - `src/analysis/spontaneous_mesoscale_validation.py`
  - `outputs/metrics/spontaneous_mesoscale_validation_summary.json`
  - `outputs/metrics/spontaneous_mesoscale_validation_components.csv`
  - `outputs/metrics/spontaneous_mesoscale_target_family_turn_table.csv`
  - `outputs/metrics/spontaneous_mesoscale_no_target_family_turn_table.csv`
  - `outputs/plots/spontaneous_mesoscale_onset_curves.png`
  - `outputs/plots/spontaneous_mesoscale_bilateral_corr_hist.png`
  - `outputs/plots/spontaneous_mesoscale_turn_family_corr.png`
- Current living-branch mesoscale result:
  - non-quiescent awake state: pass
  - matched living baseline: pass
  - walk-linked global modulation: pass
  - bilateral family coupling: pass
  - residual high-dimensional structure: pass
  - residual temporal structure: pass
  - turn-linked spatial heterogeneity: pass
  - forced-vs-spontaneous walk similarity: not yet evaluated
  - connectome-function correspondence: not yet evaluated
- Focused validation passed:
  - `18 passed` across the new spontaneous-data and mesoscale-validation tests plus the existing spontaneous-state and living-activation tests

3. What failed
- Dryad direct file API endpoints still return `401 Unauthorized` in scripted checks from this environment.
- The large Aimon 2023 bundles are still not staged locally:
  - `Walk_anatomical_regions.zip`
  - `Walk_components.zip`
  - `Additional_data.zip`
- So the current mesoscale pass is strong and useful, but it is still based on:
  - living-branch run outputs
  - public literature anchors
  - public Dryad metadata
  - small local Aimon 2023 metadata artifacts
  rather than the full public regional/component timeseries bundles.

4. Evidence paths
- `docs/spontaneous_mesoscale_validation.md`
- `external/spontaneous/aimon2023_dryad/local_dataset_summary.json`
- `external/spontaneous/aimon2023_dryad/spontaneous_public_dataset_aimon2023_dryad_manifest.json`
- `external/spontaneous/aimon2023_dryad/spontaneous_public_dataset_aimon2023_dryad_access_report.json`
- `outputs/metrics/spontaneous_mesoscale_validation_summary.json`
- `outputs/metrics/spontaneous_mesoscale_validation_components.csv`
- `outputs/plots/spontaneous_mesoscale_onset_curves.png`
- `outputs/plots/spontaneous_mesoscale_bilateral_corr_hist.png`
- `outputs/plots/spontaneous_mesoscale_turn_family_corr.png`

5. Next actions
- Add a forced-walk assay so the living branch can be judged against the Aimon 2023 spontaneous-vs-forced mesoscale comparison directly.
- Add a connectome-to-functional-coupling comparison layer for the living branch.
- Stage and ingest the full Aimon 2023 regional/component bundles when a deterministic public download path is made reliable enough for this repo.

## 2026-03-08 - Longest stable demo, profiling, and acceptance hardening

1. What I attempted
- Extended `benchmarks/run_fullstack_with_realistic_vision.py` so one command can sweep multiple durations and emit `outputs/plots/fullstack_benchmarks.png`.
- Added `benchmarks/profile_fullstack.py` and `benchmarks/summarize_demo_runs.py` to make profiling and parity summarization reproducible.
- Ran a real WSL realistic-vision benchmark and demo sweep for `0.02 s`, `0.05 s`, and `0.1 s` simulated durations.
- Profiled the real WSL full stack for `0.02 s` simulated time.
- Probed the host Torch whole-brain backend on both `cuda:0` and `cuda:1`.
- Patched the benchmark regression tests so they write into temporary paths instead of overwriting production benchmark artifacts.
- Updated the final docs and trackers required by `AGENTS.MD`.

2. What succeeded
- Real short, medium, and longest-stable FlyGym realistic-vision demos now exist:
  - `outputs/demos/flygym-demo-20260308-121237.mp4`
  - `outputs/demos/flygym-demo-20260308-121318.mp4`
  - `outputs/demos/flygym-demo-20260308-121432.mp4`
- `outputs/benchmarks/fullstack_benchmarks.csv` now contains three real production rows and `outputs/plots/fullstack_benchmarks.png` now exists.
- `outputs/metrics/parity_runs.csv` now summarizes the three real production demos.
- Profiling artifacts now exist:
  - `outputs/profiling/fullstack_flygym_0p02.prof`
  - `outputs/profiling/fullstack_flygym_0p02.txt`
  - `outputs/profiling/torch_device_probe.json`
- Screenshot artifacts now exist:
  - `outputs/screenshots/flygym-demo-20260308-121237.png`
  - `outputs/screenshots/flygym-demo-20260308-121318.png`
  - `outputs/screenshots/flygym-demo-20260308-121432.png`
- Production benchmark artifacts were restored after isolating the tests:
  - `outputs/benchmarks/body_benchmarks.csv`
  - `outputs/benchmarks/fullstack_benchmarks.csv`
  - `outputs/plots/body_benchmarks.png`
  - `outputs/plots/fullstack_benchmarks.png`
- The profile shows the production bottleneck is FlyGym plus FlyVis runtime, especially realistic-vision stepping and a large `time.sleep` component, not the in-repo bridge.
- The host Torch probe showed `cuda:1` slightly faster than `cuda:0` for the tested brain-only workload.
- Host smoke and regression tests now pass with the updated benchmark script shape: `7 passed`.
- `README.md`, `docs/install_report.md`, `docs/benchmark_summary.md`, `docs/perf_tuning.md`, `docs/multi_gpu_evaluation.md`, `docs/realistic_vision_integration.md`, `ASSUMPTIONS_AND_GAPS.md`, `REPRO_PARITY_REPORT.md`, and `TASKS.md` now match the validated workflow and current evidence.

3. What failed
- The public WSL PyTorch `cu126` wheel still does not support RTX 5060 Ti `sm_120`, so the realistic-vision production path remains CPU-only in WSL.
- Because of that wheel limitation, a meaningful end-to-end dual-GPU production split is still blocked.
- The final parity verdict remains `partial` rather than `pass` because the exact private Eon glue and telemetry are not public.

4. Evidence paths
- `outputs/benchmarks/fullstack_benchmarks.csv`
- `outputs/plots/fullstack_benchmarks.png`
- `outputs/metrics/parity_runs.csv`
- `outputs/profiling/fullstack_flygym_0p02.txt`
- `outputs/profiling/torch_device_probe.json`
- `outputs/screenshots/flygym-demo-20260308-121432.png`
- `outputs/demos/flygym-demo-20260308-121432/summary.json`
- `REPRO_PARITY_REPORT.md`
- `README.md`
- `TASKS.md`

5. Next actions
- Mandatory repo work is complete for the public-equivalent acceptance gate in `AGENTS.MD`.
- External follow-up once public support exists: rerun the WSL realistic-vision stack with GPU FlyVis enabled and repeat the same benchmark and parity scripts.
- Secondary follow-up: inspect the `time.sleep` hotspot in the FlyGym plus FlyVis path if higher local throughput becomes a priority.

## 2026-03-08 - User-requested 30 second real full-stack demo launch

1. What I attempted
- Launched a real `30 s` simulated-duration FlyGym realistic-vision full-stack run from WSL using the validated production config.
- Isolated the request outputs under `outputs/requested_30s/` so existing benchmark artifacts remain unchanged.

2. What succeeded
- The run was started successfully and is currently writing artifacts under:
  - `outputs/requested_30s/run-20260308-130111.log`
  - `outputs/requested_30s/flygym-demo-20260308-130114/`
- The live run directory already exists and has started writing `run.jsonl`.

3. What failed
- The final video artifact is not ready yet.
- Based on the current measured real-time factor for the validated full-stack path (`~0.00078x`), a true `30 s` simulated run is expected to take about `10.7 h` wall time on this machine with the present public WSL stack.

4. Evidence paths
- `outputs/requested_30s/run-20260308-130111.log`
- `outputs/requested_30s/flygym-demo-20260308-130114/run.jsonl`
- `TASKS.md`

5. Next actions
- Let the requested long run continue until completion.
- Once complete, inspect `outputs/requested_30s/demos/` for the video artifact and summarize the final paths.
- Separately, provide the requested concrete near-term implementation plan for richer-than-two-drive control.
- Wrote the requested concrete near-term multidrive implementation plan to `docs/near_term_multidrive_plan.md` and logged it in `TASKS.md` as `T020`.
- Wrote the requested vision fast-path plan to `docs/vision_perf_plan.md` and logged it in `TASKS.md` as `T021`.

## 2026-03-08 - Vision fast-path implementation slice 1

1. What I attempted
- Started implementing the first concrete tasks from `docs/vision_perf_plan.md`.
- Added an in-repo array-based realistic-vision extraction path so the bridge can consume either:
  - legacy `LayerActivity`-expanded mappings, or
  - fast raw-array / precomputed-feature payloads.
- Added a repo-local `FastRealisticVisionFly` wrapper and wired a config-controlled `runtime.vision_payload_mode` through the mock runtime, FlyGym runtime, bridge, and benchmark CLIs.
- Added local tests and mock-path benchmarks for the new fast payload mode.

2. What succeeded
- Added cached index extraction primitives:
  - `src/vision/feature_extractor.py`
  - `src/vision/flyvis_fast_path.py`
- Added the repo-local FlyGym wrapper:
  - `src/body/fast_realistic_vision_fly.py`
- Extended body observations and runtimes so fast payloads can flow without rebuilding per-cell dictionaries:
  - `src/body/interfaces.py`
  - `src/body/mock_body.py`
  - `src/body/flygym_runtime.py`
- Updated the bridge and closed-loop runner to prefer fast payloads when available:
  - `src/bridge/controller.py`
  - `src/runtime/closed_loop.py`
- Added benchmark toggles for `legacy|fast` vision payload modes:
  - `benchmarks/run_vision_benchmarks.py`
  - `benchmarks/run_fullstack_with_realistic_vision.py`
- Added local validation coverage:
  - `tests/test_imports.py`
  - `tests/test_realistic_vision_path.py`
  - `tests/test_closed_loop_smoke.py`
- Host validation now passes:
  - `python -m pytest tests/test_imports.py tests/test_bridge_unit.py tests/test_closed_loop_smoke.py tests/test_realistic_vision_path.py tests/test_benchmark_output_format.py tests/test_artifact_generation.py`
  - result: `10 passed`
- Mock fast-path benchmark evidence now exists:
  - `tests/.tmp/vision_fast.csv`
  - `tests/.tmp/fastvision-fullstack.csv`

3. What failed
- I temporarily overwrote `outputs/benchmarks/vision_benchmarks.csv` and `outputs/plots/vision_benchmarks.png` with a host-side mock fast-path benchmark while adding the new CLI toggles.
- I restored the production artifact paths immediately by rerunning the real WSL legacy vision benchmark:
  - `outputs/benchmarks/vision_benchmarks.csv`
  - `outputs/plots/vision_benchmarks.png`
- I have not yet validated the new `vision_payload_mode=fast` path against the real WSL FlyGym stack, so I cannot yet claim that the `LayerActivity` / `datamate` hotspot is removed in the real production profile.

4. Evidence paths
- `docs/vision_perf_plan.md`
- `src/vision/feature_extractor.py`
- `src/vision/flyvis_fast_path.py`
- `src/body/fast_realistic_vision_fly.py`
- `src/body/mock_body.py`
- `src/body/flygym_runtime.py`
- `src/bridge/controller.py`
- `src/runtime/closed_loop.py`
- `benchmarks/run_vision_benchmarks.py`
- `benchmarks/run_fullstack_with_realistic_vision.py`
- `tests/test_realistic_vision_path.py`
- `tests/test_closed_loop_smoke.py`
- `tests/.tmp/vision_fast.csv`
- `tests/.tmp/fastvision-fullstack.csv`
- `outputs/benchmarks/vision_benchmarks.csv`

5. Next actions
- Run the real WSL FlyGym stack with `runtime.vision_payload_mode=fast`.
- Re-profile the realistic-vision path and compare the hotspot table against `outputs/profiling/fullstack_flygym_0p02.txt`.
- If the fast path works in WSL, add side-by-side legacy vs fast benchmark rows and then update `docs/perf_tuning.md`.

## 2026-03-08 - Cancelled requested 30 second run and validated real fast-vision full stack

1. What I attempted
- Killed the still-running user-requested `30 s` WSL full-stack job.
- Ran a real WSL full-stack FlyGym realistic-vision benchmark using the new `vision_payload_mode=fast` path.

2. What succeeded
- The long-running `30 s` job is no longer running.
- The partial run directory and log remain available for inspection:
  - `outputs/requested_30s/run-20260308-130111.log`
  - `outputs/requested_30s/flygym-demo-20260308-130114/run.jsonl`
- The first real WSL fast-vision full-stack run completed successfully and produced artifacts:
  - `outputs/benchmarks/fullstack_fastvision_test.csv`
  - `outputs/plots/fullstack_fastvision_test.png`
  - `outputs/fastvision_test/demos/flygym-demo-20260308-134523.mp4`
  - `outputs/fastvision_test/logs/flygym-demo-20260308-134523.jsonl`
  - `outputs/fastvision_test/metrics/flygym-demo-20260308-134523.csv`
- The production run log confirms the real fast payload mode was active:
  - `outputs/fastvision_test/logs/flygym-demo-20260308-134523.jsonl`
- The initial measured fast-path full-stack row is:
  - `wall_seconds = 5.928991241999938`
  - `sim_seconds = 0.018000000000000002`
  - `real_time_factor = 0.0030359295983591857`
- Relative to the earlier real legacy full-stack result for the same short-run class (`~0.00078x`), this first fast-path validation is materially faster.

3. What failed
- The user-requested `30 s` artifact was intentionally not completed because the run was terminated at user request.
- I have not yet rerun the dedicated vision-only benchmark in WSL with `vision_payload_mode=fast`, nor captured an updated profiler comparison, so the `LayerActivity` / `datamate` hotspot removal is not fully proven yet.

4. Evidence paths
- `outputs/requested_30s/run-20260308-130111.log`
- `outputs/requested_30s/flygym-demo-20260308-130114/run.jsonl`
- `outputs/benchmarks/fullstack_fastvision_test.csv`
- `outputs/plots/fullstack_fastvision_test.png`
- `outputs/fastvision_test/demos/flygym-demo-20260308-134523.mp4`
- `outputs/fastvision_test/logs/flygym-demo-20260308-134523.jsonl`
- `outputs/fastvision_test/metrics/flygym-demo-20260308-134523.csv`
- `TASKS.md`

5. Next actions
- Run the real WSL vision-only benchmark with `vision_payload_mode=fast`.
- Re-profile the real full stack with the fast payload mode enabled.
- Update `docs/perf_tuning.md` with the before/after results if the profiler confirms the intended hotspot shift.

## 2026-03-08 - Exact equivalence proof for fast vision on the control path

1. What I attempted
- Tightened the local vision tests from tolerance-based checks to exact equality checks where the algebra should match exactly.
- Wrote a dedicated proof script, `scripts/prove_vision_fast_equivalence.py`, to compare:
  - legacy `LayerActivity` indexing,
  - fast cached indexing,
  - extracted vision features,
  - sensor pool rates,
  - sensor metadata,
  - downstream motor rates,
  - final decoded motor command,
  on the same exact `nn_activities_arr`.
- Ran that proof script inside the real WSL `flysim-full` environment against the installed FlyVis connectome and real production samples.

2. What succeeded
- Local exact-equality tests now pass:
  - `python -m pytest tests/test_realistic_vision_path.py tests/test_bridge_unit.py`
  - result: `5 passed`
- The WSL proof script completed and wrote:
  - `outputs/metrics/vision_fast_equivalence.json`
- The proof artifact shows:
  - `all_index_arrays_exact = true`
  - `all_samples_exact_feature_match = true`
  - `all_samples_exact_sensor_pool_match = true`
  - `all_samples_exact_sensor_metadata_match = true`
  - `all_samples_exact_motor_rate_match = true`
  - `all_samples_exact_command_match = true`
  - `max_feature_abs_diff = 0.0`
  - `max_command_abs_diff = 0.0`
- Checked real production samples:
  - `reset`
  - `step_1`
  - `step_2`
- Wrote a file-backed proof summary:
  - `docs/vision_fast_equivalence.md`

3. What failed
- I cannot honestly claim byte-for-byte equivalence of every runtime payload, because fast mode intentionally does not emit the legacy `info["nn_activities"]` `LayerActivity` object.
- What is proven exactly equivalent is the control-relevant path used by this repo: same input array -> same extracted features -> same bridge outputs -> same decoded command.

4. Evidence paths
- `scripts/prove_vision_fast_equivalence.py`
- `outputs/metrics/vision_fast_equivalence.json`
- `docs/vision_fast_equivalence.md`
- `tests/test_realistic_vision_path.py`
- `TASKS.md`

5. Next actions
- Finish `T024`: run side-by-side real WSL legacy vs fast vision-only and full-stack benchmarks.
- Re-profile the real fast path and update `docs/perf_tuning.md` with the hotspot comparison.

## 2026-03-08 - User-requested 5 second real fast-vision demo launch

1. What I attempted
- Launched a real `5 s` simulated-duration FlyGym realistic-vision full-stack run using the new fast vision payload mode.
- Isolated the request outputs under `outputs/requested_5s_fastvision/` so the existing benchmark artifacts remain unchanged.

2. What succeeded
- The run started successfully in WSL.
- Live evidence now exists at:
  - `outputs/requested_5s_fastvision/run-20260308-141141.log`
  - `outputs/requested_5s_fastvision/demos/flygym-demo-20260308-141145/run.jsonl`
- The WSL process is active and the run directory has been created.

3. What failed
- The final demo artifact is not ready yet.
- Based on the current measured fast full-stack real-time factor (`~0.00304x` from `outputs/benchmarks/fullstack_fastvision_test.csv`), a true `5 s` simulated run is expected to take about `27.4 min` wall time on this machine.

4. Evidence paths
- `outputs/requested_5s_fastvision/run-20260308-141141.log`
- `outputs/requested_5s_fastvision/demos/flygym-demo-20260308-141145/run.jsonl`
- `outputs/benchmarks/fullstack_fastvision_test.csv`
- `TASKS.md`

5. Next actions
- Let the requested `5 s` fast-vision run continue until completion.
- Once complete, inspect `outputs/requested_5s_fastvision/demos/`, `outputs/requested_5s_fastvision/logs/`, and `outputs/requested_5s_fastvision/metrics/` for the final artifact paths.

## 2026-03-08 - 5 second fast-vision demo dissection

1. What I attempted
- Inspected the completed `5 s` fast-vision demo artifacts after the user reported that one fly walked off screen and the other appeared to circle consistently.
- Analyzed the run log, metrics, trajectory plot, command plot, decoder code, and the FlyGym arena implementation.

2. What succeeded
- Confirmed the run completed and produced:
  - `outputs/requested_5s_fastvision/demos/flygym-demo-20260308-141145.mp4`
  - `outputs/requested_5s_fastvision/logs/flygym-demo-20260308-141145.jsonl`
  - `outputs/requested_5s_fastvision/metrics/flygym-demo-20260308-141145.csv`
- Confirmed the circling second fly is not connectome-controlled behavior; it is the arena's scripted leading fly in `external/flygym/flygym/examples/vision/arena.py`, where `MovingFlyArena` advances the stimulus fly on a fixed-radius circular path.
- Confirmed the controlled fly largely runs on the decoder's hard-coded idle drive:
  - `src/bridge/decoder.py` sets `idle_drive = 0.7`
  - in the `5 s` run, the motor readout was exactly all-zero on `2257 / 2500` cycles
  - on those silent cycles, the decoder still emits `left_drive = right_drive = 0.7`
- Confirmed the control bias is strongly one-sided when activity does appear:
  - `turn_right_hz` was zero on all `2500` cycles
  - `forward_right_hz` was zero on all `2500` cycles
  - only left-side readout groups fired, producing repeated `left_drive > right_drive` events
- Confirmed the logged visual asymmetry is very small and almost uncorrelated with the drive asymmetry:
  - mean absolute `vision_balance` was about `0.0081`
  - correlation between `vision_balance` and `(left_drive - right_drive)` was about `0.0045`
- The trajectory plot shows the controlled fly does not perform a stable pursuit behavior; it drifts on a long right-curving path and exits the fixed camera framing:
  - `outputs/requested_5s_fastvision/demos/flygym-demo-20260308-141145/trajectory.png`

3. What failed
- The `5 s` demo does not show convincing visually guided pursuit.
- The controlled behavior is still dominated by engineering fallback dynamics:
  - baseline locomotion from `idle_drive`
  - sparse, left-only neural readout bursts
- This means the current fast-vision run is useful as a performance and plumbing validation, but not as a strong parity demo.

4. Evidence paths
- `outputs/requested_5s_fastvision/logs/flygym-demo-20260308-141145.jsonl`
- `outputs/requested_5s_fastvision/metrics/flygym-demo-20260308-141145.csv`
- `outputs/requested_5s_fastvision/demos/flygym-demo-20260308-141145/trajectory.png`
- `outputs/requested_5s_fastvision/demos/flygym-demo-20260308-141145/commands.png`
- `src/bridge/decoder.py`
- `external/flygym/flygym/examples/vision/arena.py`
- `TASKS.md`

5. Next actions
- Remove or gate the decoder idle drive for diagnostic runs so silent-brain behavior is visible immediately.
- Audit the public left/right motor readout IDs and the current sensor-pool mapping, because the observed output is one-sided.
- Add a pursuit-quality metric comparing controlled-fly trajectory to the arena fly trajectory before claiming anything close to demo parity.

## 2026-03-08 - Strict brain-only motor enforcement and public-input cleanup

1. What I attempted
- Re-read `AGENTS.MD`, `TASKS.md`, and the current `PROGRESS_LOG.md` before changing the production path.
- Removed the in-repo motor fallback so zero monitored brain output no longer becomes locomotion by default.
- Audited the public sensory anchor mapping and removed the fabricated midpoint left/right split of the bilateral public `LC4` and `JON` ID lists.
- Added a repo-local realistic-vision wrapper to suppress upstream `HybridTurningFly` rule-based locomotion when the decoded descending drive is exactly zero.
- Re-ran host tests and short real WSL strict-production diagnostics for both `fast` and `legacy` realistic-vision payload modes.

2. What succeeded
- The production decoder is now brain-only in the narrow sense requested:
  - `src/bridge/decoder.py` now defaults to `idle_drive = 0.0` and `min_drive = 0.0`
  - `src/bridge/encoder.py` now defaults to zero sensory baselines
  - `src/brain/mock_backend.py` now also returns zero readout for zero sensor input so the test path matches the stricter production semantics
- The fabricated public sensory hemispheres are gone:
  - `src/brain/public_ids.py` now defines bilateral public input pools and a `collapse_sensor_pool_rates(...)` helper
  - `src/brain/pytorch_backend.py` now drives the public whole-brain core through those bilateral pools instead of arbitrary list-halves
- The upstream body-side hidden locomotion is suppressed when decoded drive is zero:
  - `src/body/brain_only_realistic_vision_fly.py`
  - `src/body/fast_realistic_vision_fly.py`
  - `src/body/flygym_runtime.py`
- Host validation still passes:
  - `python -m pytest tests/test_bridge_unit.py tests/test_closed_loop_smoke.py tests/test_realistic_vision_path.py tests/test_benchmark_output_format.py tests/test_artifact_generation.py tests/test_imports.py`
  - result: `13 passed`
- Real WSL strict-production diagnostics now show that the decoder and wrapper changes are actually taking effect:
  - fast path benchmark: `outputs/benchmarks/fullstack_brainonly_fastvision_test_v2.csv`
  - legacy path benchmark: `outputs/benchmarks/fullstack_brainonly_legacyvision_test.csv`
  - in both runs:
    - `nonzero_commands = 0`
    - `nonzero_motor_cycles = 0`
    - remaining path length is only `0.013563274021824296` over `0.018 s`

3. What failed
- The strict production path currently reveals a harder truth: with the decoder floor removed and the fake sensory split removed, the public whole-brain backend produced no monitored motor output in the short real WSL diagnostics.
- There is still small residual motion even with zero decoded command. After the new wrapper, this is down to passive body settling rather than controller locomotion, but it is not literally zero movement.
- So the stricter default production path is now more faithful, but it is behaviorally weaker than the earlier demo artifacts that relied on now-removed scaffolding.

4. Evidence paths
- `src/bridge/decoder.py`
- `src/bridge/encoder.py`
- `src/brain/public_ids.py`
- `src/brain/pytorch_backend.py`
- `src/body/brain_only_realistic_vision_fly.py`
- `src/body/fast_realistic_vision_fly.py`
- `src/body/flygym_runtime.py`
- `tests/test_bridge_unit.py`
- `outputs/benchmarks/fullstack_brainonly_fastvision_test_v2.csv`
- `outputs/brain_only_fastvision_test_v2/logs/flygym-demo-20260308-150052.jsonl`
- `outputs/benchmarks/fullstack_brainonly_legacyvision_test.csv`
- `outputs/brain_only_legacyvision_test/logs/flygym-demo-20260308-150149.jsonl`
- `REPRO_PARITY_REPORT.md`

5. Next actions
- Keep the stricter brain-only defaults in place; do not restore the removed fallback behaviors.
- Treat the absence of motor output as the current production blocker and debug it explicitly rather than hiding it with decoder or body-controller scaffolding.
- If higher fidelity remains the goal, the next work should focus on whether the current public input mapping and monitored descending-neuron set are sufficient to elicit motor output under the public whole-brain model.

## 2026-03-08 - Strict motor-path audit and public notebook comparison

1. What I attempted
- Audited the strict production blocker after the decoder/body-side scaffolding was removed.
- Compared the observed strict-production public input rates against standalone whole-brain backend sweeps.
- Added a reproducible audit script that measures:
  - observed bilateral public input statistics from a strict production log
  - direct graph connectivity from the public `LC4` / `JON` anchor pools into the monitored locomotor DN groups
  - hop reachability from those sensory pools to the monitored DN groups
  - positive-control cases using direct public `P9` stimulation
- Re-read the checked public notebook in `external/fly-brain/code/paper-phil-drosophila/example.ipynb` to verify how `P9`, `LC4`, and `JON` are actually used in the public examples.

2. What succeeded
- Added the reproducible audit entrypoint:
  - `scripts/audit_motor_path.py`
- Wrote the audit artifacts:
  - `outputs/metrics/motor_path_audit.json`
  - `outputs/metrics/motor_path_audit_sweeps.csv`
- Wrote the supporting summary doc:
  - `docs/motor_path_audit.md`
- Confirmed the strict short production input levels are low relative to the public experiment context:
  - observed bilateral vision input is about `77.7 Hz`
  - observed bilateral mechanosensory input averages about `14.7 Hz`
- Confirmed those observed bilateral inputs produce:
  - zero monitored motor output over `20 ms`
  - zero monitored motor output over `100 ms`
  - only weak turning-biased output after `1000 ms`
- Confirmed the whole-brain backend and monitored readout path are not dead:
  - direct public `P9` stimulation at `100 Hz` for `1000 ms` produces about `33.0 Hz` / `32.5 Hz` forward readout with first forward spikes at about `10-12 ms`
- Confirmed the current public sensory pools do not connect directly to the monitored DN groups:
  - `LC4` to monitored DNs: `0` direct edges
  - `JON` to monitored DNs: `0` direct edges
  - both reach the monitored DN groups by hop `2`
- Confirmed the checked public notebook uses `P9` as the explicit forward-walking baseline before adding `LC4` or `JON` co-stimulation.

3. What failed
- The audit did not recover a new faithful locomotor controller.
- The strict sensory-only production path remains behaviorally blocked: it is honest, but it still does not produce meaningful locomotor output from the current public bilateral sensory anchor mapping.
- The bilateral public sensory anchors still discard external left/right asymmetry before the whole-brain backend, so visually guided turning parity remains out of reach with the present public anchor set.

4. Evidence paths
- `scripts/audit_motor_path.py`
- `outputs/metrics/motor_path_audit.json`
- `outputs/metrics/motor_path_audit_sweeps.csv`
- `docs/motor_path_audit.md`
- `external/fly-brain/code/paper-phil-drosophila/example.ipynb`
- `README.md`
- `ASSUMPTIONS_AND_GAPS.md`
- `REPRO_PARITY_REPORT.md`

5. Next actions
- Keep the strict brain-only default and do not restore decoder/body-side fallback locomotion.
- If a more behaviorally active public-equivalent mode is desired, implement it as a clearly labeled brain-side experiment analogue rather than hidden decoder scaffolding.
- Search for truly lateralized public sensory anchors or additional public readout anchors before trying to claim visually guided turning behavior again.

## 2026-03-08 - Public P9 context mode and lateralized-anchor search

1. What I attempted
- Implemented the user-requested `public_p9_context` experiment mode so the repo can reproduce the public notebook's direct `P9` locomotor baseline without restoring decoder or body-side fallback behavior.
- Added runtime/config/CLI plumbing so this mode is explicit in config files and JSONL logs.
- Extended the mock-path tests to cover the new brain-side context injection.
- Ran a short real WSL fast-vision validation run using the new mode.
- Searched the checked public notebook artifacts for truly lateralized sensory anchors before attempting visual turning again.

2. What succeeded
- Added a new brain-side context injector:
  - `src/bridge/brain_context.py`
- Wired the mode through the bridge/runtime/backends:
  - `src/bridge/controller.py`
  - `src/brain/pytorch_backend.py`
  - `src/brain/mock_backend.py`
  - `src/runtime/closed_loop.py`
  - `benchmarks/run_fullstack_with_realistic_vision.py`
- Added an explicit real config:
  - `configs/flygym_realistic_vision_public_p9_context.yaml`
- Host validation passed:
  - `python -m pytest tests/test_imports.py tests/test_bridge_unit.py tests/test_closed_loop_smoke.py tests/test_realistic_vision_path.py tests/test_benchmark_output_format.py tests/test_artifact_generation.py`
  - result: `15 passed`
- Real WSL validation run completed:
  - benchmark CSV: `outputs/benchmarks/fullstack_public_p9_context_test.csv`
  - video: `outputs/public_p9_context_test/demos/flygym-demo-20260308-165839.mp4`
  - log: `outputs/public_p9_context_test/logs/flygym-demo-20260308-165839.jsonl`
  - metrics: `outputs/public_p9_context_test/metrics/flygym-demo-20260308-165839.csv`
- The real WSL validation log confirms the new mode is explicit and active:
  - `brain_context.mode = public_p9_context`
  - `P9_left = 100 Hz`
  - `P9_right = 100 Hz`
- The short real WSL run produced measurable brain-driven motion without decoder/body fallback restoration:
  - `real_time_factor = 0.003553746426609255`
  - `path_length = 0.15791582767030482`
  - `nonzero command cycles = 2 / 10`
  - `max_forward_left_hz = 249.99998474121094`
  - `max_forward_right_hz = 249.99998474121094`
- Added a reproducible public-anchor search:
  - `scripts/search_lateralized_public_anchors.py`
  - `outputs/metrics/lateralized_public_anchors.json`
  - `docs/lateralized_public_anchors.md`
- The checked public artifact search found:
  - `visual_lateralized_hits = 0`
  - `mechanosensory_lateralized_hits = 0`
  - `gustatory_lateralized_hits = 5`
  - no `LC4_left/right` or `JON_left/right`-style public anchors in the checked notebook artifacts

3. What failed
- The new `public_p9_context` mode is useful as a public experiment analogue, but it is not evidence that realistic vision alone is currently driving locomotion in the strict production path.
- The lateralized-anchor search did not recover a clean public left/right visual or mechanosensory sensory pool for turning, so visually guided turning parity remains blocked on the public-anchor side.

4. Evidence paths
- `src/bridge/brain_context.py`
- `configs/flygym_realistic_vision_public_p9_context.yaml`
- `docs/public_p9_context_mode.md`
- `outputs/benchmarks/fullstack_public_p9_context_test.csv`
- `outputs/public_p9_context_test/logs/flygym-demo-20260308-165839.jsonl`
- `outputs/public_p9_context_test/metrics/flygym-demo-20260308-165839.csv`
- `scripts/search_lateralized_public_anchors.py`
- `outputs/metrics/lateralized_public_anchors.json`
- `docs/lateralized_public_anchors.md`
- `README.md`
- `ASSUMPTIONS_AND_GAPS.md`
- `REPRO_PARITY_REPORT.md`

5. Next actions
- Keep `brain_context.mode: none` as the default faithful production mode.
- Use `public_p9_context` only when the experiment framing needs to match the public notebook's direct `P9` baseline explicitly.
- Do not claim honest public left/right visual steering input until a real public lateralized visual or mechanosensory anchor set is identified.

## 2026-03-08 - Inferred lateralized bridge probing kickoff

1. What I attempted
- Started the next fallback the user requested: probing the real visual model with crafted inputs to infer candidate left/right bridge channels.
- Re-inspected the current vision stack and the checked public FlyGym vision examples to decide whether to probe through:
  - the real FlyVis network directly, or
  - full embodied closed-loop runs
- Verified that the repo-local fast vision path already exposes the ingredients needed for a direct probe:
  - `nn_activities_arr`
  - connectome node types
  - retina / retina-mapper utilities

2. What succeeded
- Confirmed the technical path for a direct probe is available in the current code:
  - `src/body/fast_realistic_vision_fly.py`
  - `src/vision/feature_extractor.py`
  - `src/vision/flyvis_fast_path.py`
  - `external/flygym/flygym/examples/vision/vision_network.py`
- Confirmed the checked public FlyGym examples already use z-scored activity comparisons over tracked visual cell types for object following:
  - `external/flygym/flygym/examples/vision/follow_fly_closed_loop.py`
- Confirmed the checked public tutorial exposes the full per-eye activity tensor shape:
  - `external/flygym/doc/source/tutorials/advanced_vision.rst`
  - `all_cell_activities.shape == (num_timesteps, 2, 45669)`
- Created a new tracked task for this probing work:
  - `T035` in `TASKS.md`

3. What failed
- I have not yet completed the actual probing script or generated the inferred candidate artifact.
- A quick one-line WSL probe command failed because of quoting issues from PowerShell into WSL; no repo state was changed by that failure.

4. Evidence paths
- `TASKS.md`
- `src/body/fast_realistic_vision_fly.py`
- `src/vision/feature_extractor.py`
- `src/vision/flyvis_fast_path.py`
- `external/flygym/flygym/examples/vision/follow_fly_closed_loop.py`
- `external/flygym/doc/source/tutorials/advanced_vision.rst`

5. Next actions
- Implement `scripts/probe_lateralized_visual_candidates.py`.
- Generate a saved candidate ranking artifact from crafted left/right stimuli through the real vision model.
- Document the inferred candidate set separately from the public-grounded bridge.

## 2026-03-08 - Inferred lateralized visual probe completed and packaged

1. What I attempted
- Finished the real-FlyVis left/right probe that had been staged in the previous entry.
- Inspected the saved ranking artifacts to determine whether the current extractor was missing important visual cell families or just collapsing away their left/right structure.
- Added a reusable experimental helper that can load the inferred candidate artifact and turn live per-eye activity arrays into an inferred turn-bias signal.

2. What succeeded
- The real probe completed in WSL and wrote:
  - `outputs/metrics/inferred_lateralized_visual_candidates.csv`
  - `outputs/metrics/inferred_lateralized_visual_candidates.json`
  - `outputs/plots/inferred_lateralized_visual_stimuli.png`
- The top inferred tracking candidates were:
  - `TmY14`
  - `TmY15`
  - `TmY5a`
  - `TmY4`
  - `TmY18`
  - `TmY9`
- The top inferred flow candidates were:
  - `T5d`
  - `T5c`
  - `T4b`
  - `T5a`
- The main outcome is that the current extractor was not missing the relevant FlyVis families entirely. Many of the strongest inferred candidates were already in the production tracking/flow sets; the bigger loss was the left/right sign structure being averaged away and then collapsed back into bilateral public pools.
- Added reusable experimental code:
  - `src/vision/inferred_lateralized.py`
  - `tests/test_inferred_lateralized.py`
- Wrote a compact recommended candidate artifact:
  - `outputs/metrics/inferred_lateralized_visual_recommended.json`
- Documented the result:
  - `docs/inferred_lateralized_visual_candidates.md`
- Host validation passed:
  - `python -m pytest tests/test_inferred_lateralized.py tests/test_lateralized_probe.py tests/test_bridge_unit.py tests/test_closed_loop_smoke.py tests/test_realistic_vision_path.py`
  - result: `17 passed`

3. What failed
- This still does not recover a faithful public-grounded whole-brain neuron-ID mapping for left/right visual input.
- I have not yet wired the inferred `turn_bias` into a new closed-loop experiment mode, because that would be a new inferred bridge step and should stay clearly separated from the faithful default path.

4. Evidence paths
- `scripts/probe_lateralized_visual_candidates.py`
- `src/vision/lateralized_probe.py`
- `src/vision/inferred_lateralized.py`
- `tests/test_inferred_lateralized.py`
- `outputs/metrics/inferred_lateralized_visual_candidates.csv`
- `outputs/metrics/inferred_lateralized_visual_candidates.json`
- `outputs/metrics/inferred_lateralized_visual_recommended.json`
- `docs/inferred_lateralized_visual_candidates.md`

5. Next actions
- Decide whether to add a clearly labeled inferred visual-turn experiment mode that uses the new `turn_bias` helper without changing the faithful default bridge.
- If that experiment mode is added, keep it separate from public-grounded claims and benchmark it against the current strict default plus `public_p9_context`.

## 2026-03-08 - Inferred visual-turn remediation plan and first implementation slice

1. What I attempted
- Turned the recent visual-probe findings into a concrete remediation plan.
- Implemented the first code slice to preserve inferred left/right visual structure in the extracted features and bridge metadata without changing the faithful default path.
- Added a clearly labeled `inferred_visual_turn_context` brain-side experiment mode.
- Added tests, configs, and a local mock artifact run for the new mode.

2. What succeeded
- Wrote the concrete plan:
  - `docs/inferred_visual_turn_plan.md`
- Extended the extracted visual features to carry inferred experiment fields:
  - `src/vision/feature_extractor.py`
  - `src/bridge/encoder.py`
- Added a reusable inferred candidate path to the bridge build process:
  - `src/runtime/closed_loop.py`
- Added the new brain-side experiment mode:
  - `src/bridge/brain_context.py`
- Added experiment configs:
  - `configs/mock_inferred_visual_turn.yaml`
  - `configs/flygym_realistic_vision_inferred_visual_turn.yaml`
- Documented the new mode:
  - `docs/inferred_visual_turn_context_mode.md`
- Added test coverage:
  - `tests/test_realistic_vision_path.py`
  - `tests/test_bridge_unit.py`
  - `tests/test_closed_loop_smoke.py`
- Local validation passed:
  - `python -m pytest tests/test_inferred_lateralized.py tests/test_realistic_vision_path.py tests/test_bridge_unit.py tests/test_closed_loop_smoke.py`
  - result: `17 passed`
- Produced a mock artifact-complete run for the new experiment mode:
  - `outputs/inferred_visual_turn_mock_test/mock-demo-20260308-174921/demo.mp4`
  - `outputs/inferred_visual_turn_mock_test/mock-demo-20260308-174921/run.jsonl`
  - `outputs/inferred_visual_turn_mock_test/mock-demo-20260308-174921/metrics.csv`
- The mock run log now exposes the new inferred fields end-to-end:
  - `inferred_turn_bias`
  - `inferred_turn_confidence`
  - `inferred_candidate_count`

3. What failed
- I have not yet run the new inferred experiment mode through the real WSL FlyGym stack.
- So there is still no real-WSL evidence yet for whether the inferred visual-turn context materially improves turning behavior under the production body/vision runtime.

4. Evidence paths
- `docs/inferred_visual_turn_plan.md`
- `src/vision/feature_extractor.py`
- `src/bridge/encoder.py`
- `src/bridge/brain_context.py`
- `src/runtime/closed_loop.py`
- `docs/inferred_visual_turn_context_mode.md`
- `configs/mock_inferred_visual_turn.yaml`
- `configs/flygym_realistic_vision_inferred_visual_turn.yaml`
- `tests/test_realistic_vision_path.py`
- `tests/test_bridge_unit.py`
- `tests/test_closed_loop_smoke.py`
- `outputs/inferred_visual_turn_mock_test/mock-demo-20260308-174921/run.jsonl`

5. Next actions
- Run a short real WSL FlyGym validation with `configs/flygym_realistic_vision_inferred_visual_turn.yaml`.
- Compare that experiment mode against:
  - strict default
  - `public_p9_context`
- Keep any result explicitly labeled inferred, not public-grounded.

## 2026-03-08 - Started real `5 s` WSL comparison for inferred visual turn mode

1. What I attempted
- Started the user-requested real WSL comparison at `5 s` simulated runtime for:
  - strict default
  - `public_p9_context`
  - `inferred_visual_turn_context`
- Chose the fast vision payload for all three runs so the comparison isolates the brain-side mode differences rather than legacy-vs-fast vision overhead.

2. What succeeded
- Tracking updated:
  - `T041` set to `doing`
  - `T042` added as `doing`

3. What failed
- No runtime result yet at this point in the log; the actual WSL runs are still pending.

4. Evidence paths
- `TASKS.md`
- `configs/flygym_realistic_vision.yaml`
- `configs/flygym_realistic_vision_public_p9_context.yaml`
- `configs/flygym_realistic_vision_inferred_visual_turn.yaml`

5. Next actions
- Run the three `5 s` real WSL demos.
- Save outputs under separate comparison directories.
- Summarize metrics and log-level differences once all three runs finish.

## 2026-03-08 - Real `5 s` comparison hit a long-run Torch input-probability bug

1. What I attempted
- Started the first real WSL `5 s` comparison run for the strict default mode with fast vision:
  - `configs/flygym_realistic_vision.yaml`
  - `--vision-payload-mode fast`

2. What succeeded
- The run got far enough to confirm the real WSL stack still boots and enters the closed-loop path under the comparison command shape.

3. What failed
- The run aborted before completion with a Torch error inside the whole-brain Poisson spike generator:
  - `RuntimeError: Expected p_in >= 0 && p_in <= 1 to be true`
- Failure path:
  - `src/brain/pytorch_backend.py`
  - `PoissonSpikeGenerator.forward(...)`
- This exposes a long-run robustness bug: the current whole-brain input-rate path can produce values outside the valid Bernoulli probability range during real closed-loop execution.

4. Evidence paths
- `src/brain/pytorch_backend.py`
- `TASKS.md`

5. Next actions
- Patch the Poisson input path to clamp probabilities into `[0, 1]`.
- Add a local unit test for that clamp.
- Re-run the real `5 s` comparison after the backend is robust against this overflow.

## 2026-03-08 - Real `5 s` comparison completed for strict default, public `P9`, and inferred visual turn

1. What I attempted
- Patched the whole-brain Poisson generator so long real runs cannot feed invalid probabilities into `torch.bernoulli`.
- Added a unit test for that clamp.
- Re-ran the user-requested real WSL `5 s` comparison for:
  - strict default, fast vision
  - `public_p9_context`
  - `inferred_visual_turn_context`
- Added a reusable comparison script to summarize the resulting metrics and log-derived differences.

2. What succeeded
- Patched and tested the backend clamp:
  - `src/brain/pytorch_backend.py`
  - `tests/test_brain_backend.py`
- Host validation passed:
  - `python -m pytest tests/test_brain_backend.py tests/test_inferred_lateralized.py tests/test_realistic_vision_path.py tests/test_bridge_unit.py tests/test_closed_loop_smoke.py`
  - result: `19 passed`
- The new failure-tolerant runtime path now preserves partial metrics/logs/videos even when the body runtime crashes:
  - `src/runtime/closed_loop.py`
  - `tests/test_closed_loop_smoke.py`
- Real WSL strict-default run completed with partial artifact capture after a physics failure:
  - `outputs/compare_5s_strict_fast/flygym-demo-20260308-180228/demo.mp4`
  - `outputs/compare_5s_strict_fast/flygym-demo-20260308-180228/run.jsonl`
  - `outputs/compare_5s_strict_fast/flygym-demo-20260308-180228/metrics.csv`
- Real WSL `public_p9_context` run completed the full `5 s`:
  - `outputs/compare_5s_public_p9_fast/flygym-demo-20260308-180519/demo.mp4`
  - `outputs/compare_5s_public_p9_fast/flygym-demo-20260308-180519/run.jsonl`
  - `outputs/compare_5s_public_p9_fast/flygym-demo-20260308-180519/metrics.csv`
- Real WSL `inferred_visual_turn_context` run completed the full `5 s`:
  - `outputs/compare_5s_inferred_turn_fast/flygym-demo-20260308-182847/demo.mp4`
  - `outputs/compare_5s_inferred_turn_fast/flygym-demo-20260308-182847/run.jsonl`
  - `outputs/compare_5s_inferred_turn_fast/flygym-demo-20260308-182847/metrics.csv`
- Wrote a compact comparison artifact:
  - `scripts/compare_mode_runs.py`
  - `outputs/metrics/compare_5s_modes.csv`
  - `outputs/metrics/compare_5s_modes.json`

3. What failed
- The strict default fast-vision run did not complete the full `5 s`.
- It failed at about `0.57 s` simulated time with:
  - `PhysicsError`
  - `mjWARN_INERTIA`
- That instability is now reproducible and artifact-captured, but not yet fixed.

4. Evidence paths
- `src/brain/pytorch_backend.py`
- `tests/test_brain_backend.py`
- `src/runtime/closed_loop.py`
- `tests/test_closed_loop_smoke.py`
- `scripts/compare_mode_runs.py`
- `outputs/compare_5s_strict_fast/flygym-demo-20260308-180228/metrics.csv`
- `outputs/compare_5s_public_p9_fast/flygym-demo-20260308-180519/metrics.csv`
- `outputs/compare_5s_inferred_turn_fast/flygym-demo-20260308-182847/metrics.csv`
- `outputs/metrics/compare_5s_modes.csv`

5. Next actions
- Decide whether to investigate the strict-default body instability as a separate stabilization task.
- If the comparison result is good enough, use the new artifacts to discuss whether the inferred visual-turn context is materially better than `public_p9_context`.

## 2026-03-08 - Strict-default `backflip` / tumble diagnosis

1. What I attempted
- Inspected the strict-default `5 s` comparison log to explain the visible tumble / backflip-like behavior before the MuJoCo failure.

2. What succeeded
- Confirmed the strict default run is not showing an intentional connectome-driven acrobatic behavior.
- The log shows:
  - only `11` nonzero command cycles out of `285`
  - most cycles use exact zero decoded drive
  - late in the run, the body state drifts into very large yaw-rate / speed values even while commands are still zero
- The strongest sparse impulses were all-or-nothing DN spikes:
  - cycle `64`: symmetric forward pulse with `left_drive = right_drive = 0.311...`
  - cycle `243`: pure turn pulse with `left_drive = 0.298...`, `right_drive = -0.298...`
- The strict wrapper in `src/body/brain_only_realistic_vision_fly.py` uses a neutral low-level action whenever decoded drive is zero:
  - current joint positions copied through
  - `adhesion = 0` on all legs
- Current diagnosis: the strict mode is mostly leaving the body in that passive neutral-action path, not in an actively stabilized posture. Over a longer run that appears to let the fly drift/tumble, and the rare saturated DN spikes likely make the instability worse. The run eventually dies with `PhysicsError` / `mjWARN_INERTIA`.

3. What failed
- The log does not currently record pitch/roll directly, so I cannot claim a literal backflip angle from telemetry alone.
- The explanation is therefore a strong inference from:
  - the video appearance
  - the zero-drive neutral-action path
  - the sparse impulse-like commands
  - the MuJoCo invalid-state failure

4. Evidence paths
- `outputs/compare_5s_strict_fast/flygym-demo-20260308-180228/run.jsonl`
- `outputs/compare_5s_strict_fast/flygym-demo-20260308-180228/metrics.csv`
- `src/body/brain_only_realistic_vision_fly.py`
- `TASKS.md`

5. Next actions
- If strict-default stabilization matters, the next work should focus on a biologically honest non-locomoting posture path rather than the current passive zero-adhesion neutral action.

## 2026-03-08 - Strict-default stabilization via planted stance

1. What I attempted
- Replaced the unstable zero-drive passive body path with a planted stance path:
  - use the preprogrammed default pose when available
  - keep adhesion on for all legs during the zero-drive state
- Added a small unit test around that wrapper behavior.
- Re-ran the strict default real WSL `5 s` fast-vision run.

2. What succeeded
- Patched the zero-drive body path:
  - `src/body/brain_only_realistic_vision_fly.py`
- Added a unit test:
  - `tests/test_body_wrapper_unit.py`
- Host validation passed:
  - `python -m pytest tests/test_body_wrapper_unit.py tests/test_closed_loop_smoke.py tests/test_brain_backend.py`
  - result: `6 passed, 1 skipped`
- The strict default real WSL `5 s` run is now stable and completes the full duration:
  - `outputs/compare_5s_strict_fast_v2/flygym-demo-20260308-195012/demo.mp4`
  - `outputs/compare_5s_strict_fast_v2/flygym-demo-20260308-195012/run.jsonl`
  - `outputs/compare_5s_strict_fast_v2/flygym-demo-20260308-195012/metrics.csv`
- New strict-default metrics:
  - `sim_seconds = 5.0`
  - `stable = 1.0`
  - `completed_full_duration = 1.0`
  - `nonzero_command_cycles = 107`

3. What failed
- This does not yet prove that the observed strict-default motion is fully attributable to the real brain backend rather than residual passive drift between sparse command pulses.
- I added a zero-brain baseline backend and config to measure that next.

4. Evidence paths
- `src/body/brain_only_realistic_vision_fly.py`
- `tests/test_body_wrapper_unit.py`
- `outputs/compare_5s_strict_fast_v2/flygym-demo-20260308-195012/metrics.csv`
- `outputs/compare_5s_strict_fast_v2/flygym-demo-20260308-195012/run.jsonl`
- `src/brain/zero_backend.py`
- `configs/flygym_realistic_vision_zero_brain.yaml`

5. Next actions
- Run a real WSL `5 s` zero-brain baseline.
- Compare the stable strict-default real-brain run against that zero-brain baseline to measure how much motion is actually brain-driven.

## 2026-03-08 - Brain-driven motion proof via zero-brain baseline

1. What I attempted
- Added a zero-output whole-brain backend to create a clean body-fallback baseline.
- Ran a real WSL `5 s` zero-brain FlyGym baseline under the same strict production body path.
- Compared the stable strict-default real-brain run against that zero-brain baseline.

2. What succeeded
- Added the zero backend and config:
  - `src/brain/zero_backend.py`
  - `configs/flygym_realistic_vision_zero_brain.yaml`
- Added smoke coverage for the zero backend:
  - `tests/test_closed_loop_smoke.py`
- Host validation passed:
  - `python -m pytest tests/test_closed_loop_smoke.py tests/test_brain_backend.py`
  - result: `7 passed`
- Real WSL zero-brain run completed the full `5 s`:
  - `outputs/compare_5s_zero_brain_fast/flygym-demo-20260308-201434/demo.mp4`
  - `outputs/compare_5s_zero_brain_fast/flygym-demo-20260308-201434/run.jsonl`
  - `outputs/compare_5s_zero_brain_fast/flygym-demo-20260308-201434/metrics.csv`
- Wrote the direct comparison artifact:
  - `outputs/metrics/compare_5s_strict_vs_zero.csv`
  - `outputs/metrics/compare_5s_strict_vs_zero.json`
- Wrote the supporting validation doc:
  - `docs/brain_control_validation.md`
- The direct numbers are:
  - strict real brain:
    - `nonzero_command_cycles = 107`
    - `path_length = 10.810298593539402`
    - `avg_forward_speed = 2.1629248886633454`
  - zero brain:
    - `nonzero_command_cycles = 0`
    - `path_length = 0.3795886446352556`
    - `avg_forward_speed = 0.07594810817031923`

3. What failed
- This does not solve the remaining parity gaps by itself.
- It proves brain-driven motion under the strict default stack, but not final parity with the public demo.

4. Evidence paths
- `src/brain/zero_backend.py`
- `configs/flygym_realistic_vision_zero_brain.yaml`
- `outputs/compare_5s_strict_fast_v2/flygym-demo-20260308-195012/metrics.csv`
- `outputs/compare_5s_zero_brain_fast/flygym-demo-20260308-201434/metrics.csv`
- `outputs/metrics/compare_5s_strict_vs_zero.csv`
- `docs/brain_control_validation.md`

5. Next actions
- If stronger parity is still required, the next work should focus on making the strict real-brain locomotor policy less sparse rather than re-proving body-fallback removal.

## 2026-03-08 - Corrected interpretation of the strict-default `5 s` run

1. What I checked
- Re-opened the strict-default `5 s` artifact after the user challenged the interpretation:
  - `outputs/compare_5s_strict_fast_v2/flygym-demo-20260308-195012/demo.mp4`
  - `outputs/compare_5s_strict_fast_v2/flygym-demo-20260308-195012/trajectory.png`
  - `outputs/compare_5s_strict_fast_v2/flygym-demo-20260308-195012/commands.png`
- Compared it directly against:
  - `outputs/compare_5s_zero_brain_fast/flygym-demo-20260308-201434/trajectory.png`
  - `outputs/compare_5s_public_p9_fast/flygym-demo-20260308-180519/trajectory.png`
  - `outputs/compare_5s_inferred_turn_fast/flygym-demo-20260308-182847/trajectory.png`

2. What I found
- The prior claim was too strong.
- The strict-default run is stable and brain-modulated relative to the zero-brain baseline, but it is not convincing locomotion.
- Visual inspection shows mostly local twitching / jitter inside a small region, not sustained walking across the arena.
- The reason the previous numbers looked better than the video is that `path_length` accumulates every small oscillation, so it overstates local jitter as "movement."
- The command trace is also consistent with sparse impulse-like control rather than a sustained locomotor policy:
  - mean forward drive is only about `0.00436`
  - only `107 / 2500` cycles are nonzero
  - most nonzero commands are narrow spikes rather than a continuous drive profile

3. What failed
- `docs/brain_control_validation.md` is still useful for proving that hidden body fallback was removed, but it should not be read as proof of meaningful walking.
- The strict default stack therefore remains below the bar for "the fly moves under full brain control" in the ordinary behavioral sense.

4. Evidence paths
- `outputs/compare_5s_strict_fast_v2/flygym-demo-20260308-195012/demo.mp4`
- `outputs/compare_5s_strict_fast_v2/flygym-demo-20260308-195012/trajectory.png`
- `outputs/compare_5s_strict_fast_v2/flygym-demo-20260308-195012/commands.png`
- `outputs/compare_5s_zero_brain_fast/flygym-demo-20260308-201434/trajectory.png`
- `outputs/compare_5s_public_p9_fast/flygym-demo-20260308-180519/trajectory.png`
- `outputs/compare_5s_inferred_turn_fast/flygym-demo-20260308-182847/trajectory.png`

5. Next actions
- Add more honest movement-quality metrics such as net displacement and spatial extent.
- Treat the current strict-default result as sparse brain-driven twitching, not successful locomotion.
- Continue iterating on the strict bridge / readout path until the real-brain default produces sustained locomotion rather than impulses.

## 2026-03-08 - Corrective plan for a cold-startable vision-driven brain path

1. What I concluded from the failed strict-default interpretation
- The previous bridge is missing more than tuning.
- Two concrete systemic problems are now clear from the local evidence:
  - the mechanosensory public input pool was mapped to all JONs, even though the checked public notebook experiment is specifically `P9_JO_CE_bilateral`
  - the existing inferred turn experiment injects turning readouts directly, which is too close to forcing output rather than letting the brain use its public locomotor gate

2. What I verified
- The public notebook includes explicit subgroup definitions for:
  - `neu_JON_CE`
  - `neu_JON_F`
  - `neu_JON_D_m`
- The current repo only preserved one flat `JON_IDS` list and used all of them for `mech_bilateral`.
- The current inferred-turn run uses mean forward `P9` context of about `76 Hz`, but its turn-rate injection is very weak and it still bypasses the cleaner `P9_left` / `P9_right` route.

3. Corrective direction
- Replace the current broad JON pool with the public `JON_CE` subset as the default bilateral mechanosensory public input.
- Add a new stateful brain-context mode that:
  - cold-starts from zero
  - derives locomotor onset from visual forward evidence
  - drives only `P9_left` and `P9_right`
  - steers by asymmetric `P9` drive rather than direct DNa injection
- Add more honest movement metrics so local twitching cannot be misreported as locomotion again.

4. Evidence paths
- `external/fly-brain/code/paper-phil-drosophila/figures.ipynb`
- `external/fly-brain/code/paper-phil-drosophila/example.ipynb`
- `outputs/compare_5s_strict_fast_v2/flygym-demo-20260308-195012/commands.png`
- `outputs/metrics/motor_path_audit_sweeps.csv`
- `outputs/compare_5s_inferred_turn_fast/flygym-demo-20260308-182847/run.jsonl`

5. Next actions
- Implement the public JON subgroup definitions and switch the default mechanosensory public input to `JON_CE`.
- Implement the stateful visually gated asymmetric `P9` context mode.
- Extend the parity metrics with net displacement and spatial extent before the next claim about movement quality.

## 2026-03-08 - First corrective implementation slice for cold-start visual locomotion

1. What I changed
- Added honest movement metrics:
  - `net_displacement`
  - `displacement_efficiency`
  - `bbox_width`
  - `bbox_height`
  - `bbox_area`
- Preserved the public JON subgroup definitions in code and switched the default public mechanosensory input pool from all JONs to the public `JON_CE` subset:
  - `src/brain/public_ids.py`
- Made encoder / decoder settings load from config instead of silently ignoring config tuning:
  - `src/bridge/encoder.py`
  - `src/bridge/decoder.py`
  - `src/runtime/closed_loop.py`
- Added a new stateful brain-context mode:
  - `brain_context.mode: inferred_visual_p9_context`
  - it cold-starts from zero
  - low-pass gates locomotion from visual forward evidence
  - drives only `P9_left` and `P9_right`
  - uses asymmetric `P9` drive rather than direct DNa output forcing
- Added decoder-side temporal smoothing so sparse firing-rate spikes can produce a continuous descending command:
  - `src/bridge/decoder.py`
- Added configs and smoke coverage:
  - `configs/mock_inferred_visual_p9.yaml`
  - `configs/flygym_realistic_vision_inferred_visual_p9.yaml`
  - `tests/test_bridge_unit.py`
  - `tests/test_closed_loop_smoke.py`

2. What succeeded
- Host validation passed after the refactor:
  - `python -m pytest tests/test_bridge_unit.py tests/test_closed_loop_smoke.py tests/test_realistic_vision_path.py tests/test_brain_backend.py tests/test_benchmark_output_format.py`
  - result: `21 passed`
- The new mock mode now produces sustained traversal rather than local jitter:
  - `outputs/inferred_visual_p9_mock_test_v2/mock-demo-20260308-214620/demo.mp4`
  - `outputs/inferred_visual_p9_mock_test_v2/mock-demo-20260308-214620/trajectory.png`
  - `outputs/inferred_visual_p9_mock_test_v2/mock-demo-20260308-214620/metrics.csv`
- A short real WSL smoke run also improved materially versus the earlier spiky attempt:
  - `outputs/inferred_visual_p9_smoke_v2/flygym-demo-20260308-214635/demo.mp4`
  - `outputs/inferred_visual_p9_smoke_v2/flygym-demo-20260308-214635/trajectory.png`
  - `outputs/inferred_visual_p9_smoke_v2/flygym-demo-20260308-214635/commands.png`
  - `outputs/inferred_visual_p9_smoke_v2/flygym-demo-20260308-214635/metrics.csv`
- That real `0.2 s` smoke run now shows continuous low-amplitude drive and materially better displacement efficiency:
  - `path_length = 0.4318`
  - `net_displacement = 0.1517`
  - `displacement_efficiency = 0.3514`

3. What failed
- This is not yet a completed proof of a good `5 s` cold-start locomotor policy.
- The real `0.2 s` smoke run still shows a curving local path rather than a fully convincing long-horizon pursuit trajectory.

4. Evidence paths
- `src/brain/public_ids.py`
- `src/bridge/brain_context.py`
- `src/bridge/decoder.py`
- `src/runtime/closed_loop.py`
- `outputs/inferred_visual_p9_smoke_v2/flygym-demo-20260308-214635/trajectory.png`
- `outputs/inferred_visual_p9_smoke_v2/flygym-demo-20260308-214635/commands.png`
- `outputs/inferred_visual_p9_smoke_v2/flygym-demo-20260308-214635/metrics.csv`

5. Next actions
- Run a full real `5 s` WSL validation with `configs/flygym_realistic_vision_inferred_visual_p9.yaml`.
- Compare it against:
  - zero-brain baseline
  - a no-target / vision-ablated control
- Use the old strict / `public_p9_context` modes only as diagnostic failure references, not as targets for success.
- Decide from those absolute criteria whether the new bridge is genuinely good enough or still only a partial fix.

## 2026-03-08 - Splice-strategy reset after the inferred `P9` critique

1. What I clarified
- The new `inferred_visual_p9_context` mode is still not an acceptable final answer.
- In plain terms it is an inferred prosthetic input:
  - real FlyVis visual signals go in
  - bridge logic decides when and how strongly to stimulate `P9_left` / `P9_right`
  - the rest of the whole-brain backend then evolves from that externally applied brain input
- That is cleaner than body fallback or direct DNa forcing, but it is still not an endogenous sensory pathway.

2. What the user correctly pushed on
- The key failure is not just tuning.
- The current bridge compresses a rich visual state into a few scalar rates before the brain ever sees it.
- That scalar compression is almost certainly destroying the left/right, motion-direction, and cell-family-specific structure needed for a correct splice.
- If FlyVis and the whole-brain graph both already cover real visual circuitry, the right next move is not more body-loop tuning; it is a body-free splice workflow.

3. Current best interpretation
- This is now best framed as a splice-boundary and interface-identification problem.
- It is not enough to say "the whole brain has eyes" or "FlyVis is mapped":
  - both systems may be structurally valid
  - but the live interface between them is still undefined in this repo
- The next technically correct move is:
  - pick a visual splice boundary
  - preserve a wide visual representation instead of scalar summaries
  - use FlyVis as a teacher on the overlapping visual populations
  - fit or derive the mapping there
  - only then pass control to the rest of the whole-brain model

4. Important validation rule change
- Old broken modes are no longer acceptable comparison targets:
  - `strict_default`
  - `public_p9_context`
  - `inferred_visual_turn_context`
- They remain useful only as failure diagnostics.
- The next success criteria must be absolute and body-free where possible:
  - zero-brain baseline
  - no-target / vision-ablated baseline
  - direct FlyVis-to-brain overlap agreement under shared stimuli

5. Next actions
- Write the splice strategy out in a dedicated doc so the compacted context does not lose this reasoning.
- Start with body-free work:
  - inspect FlyVis metadata for overlap identities
  - build a FlyVis + whole-brain offline splice harness
  - postpone body-loop claims until the splice itself is grounded.

## 2026-03-09 - First grounded body-free FlyVis-to-whole-brain splice probe

1. What I changed
- Added a reusable FlyWire annotation helper:
  - `src/brain/flywire_annotations.py`
- Added a body-free splice probe runner:
  - `scripts/run_splice_probe.py`
- Added a small unit test file for the new annotation helpers:
  - `tests/test_flywire_annotations.py`
- Extended the Torch backend with a clean monitored-ID setter so the splice probe can observe arbitrary overlap groups:
  - `src/brain/pytorch_backend.py`
- Wrote the result doc:
  - `docs/splice_probe_results.md`

2. What I used as the new public grounding source
- Downloaded the official FlyWire annotation supplement to:
  - `outputs/cache/flywire_annotation_supplement.tsv`
- This table exposes:
  - `root_id`
  - `cell_type`
  - `side`
- That is the first public artifact in this repo that grounds the whole-brain side of the visual splice at exact shared type labels plus side instead of arbitrary inferred pools.

3. What I found about the overlap
- `scripts/inspect_flyvis_overlap.py` still stands: FlyVis metadata alone does not expose direct FlyWire root IDs.
- The official annotation supplement closes part of the gap.
- The repo now finds `49` exact shared FlyVis / whole-brain visual cell types.
- These shared types are bilateral and large enough to support a wide splice.
- Important detail: among the FlyVis `R*` classes, the exact shared photoreceptor overlap found in the annotation supplement is `R7` and `R8`, not `R1` to `R6`.

4. What the body-free splice probe does
- Runs real FlyVis on:
  - `baseline_gray`
  - `body_left_dark`
  - `body_center_dark`
  - `body_right_dark`
- Aggregates FlyVis teacher activity by exact shared `cell_type` + `side`
- Maps the positive activity delta above baseline into direct whole-brain external drive for the matching shared `cell_type` + `side` root-ID groups
- Runs the whole-brain backend body-free for a short response window
- Compares grouped teacher and student activity at that boundary

5. What succeeded
- The wide type-level splice is real and public-grounded at the boundary:
  - `outputs/metrics/splice_probe_summary.json`
  - `outputs/metrics/splice_probe_groups.csv`
  - `outputs/metrics/splice_probe_side_differences.csv`
- Grouped teacher/student boundary correlation is high:
  - about `0.9881` for `body_left_dark`
  - about `0.9885` for `body_center_dark`
  - about `0.9913` for `body_right_dark`
- This is the first local proof that the bridge can operate on a wide shared visual boundary instead of only a handful of scalar visual features.

6. What failed
- Left/right asymmetry is not yet preserved robustly:
  - `teacher_student_side_diff_correlation = 0.2099` for `body_left_dark`
  - `teacher_student_side_diff_correlation = null` for `body_center_dark`
  - `teacher_student_side_diff_correlation = 0.8819` for `body_right_dark`
- Short-window downstream motor readouts remain zero for all non-baseline probe conditions.
- The current backend external-drive interface is still nonnegative only, so the splice probe cannot represent inhibitory visual deviations. It only maps positive deltas above baseline.
- The current probe still broadcasts one rate per `cell_type` + `side`, so it discards retinotopic `u` / `v` structure within each group.

7. What this changes in the project understanding
- The visual splice is now much more concrete.
- The right first boundary is no longer:
  - scalar salience / flow summaries
- The right first boundary is now:
  - exact shared visual `cell_type`
  - exact `side`
- The remaining blockers are now more specific:
  - signed external input at the splice boundary
  - retinotopic structure inside the shared groups
  - downstream propagation beyond the boundary itself

8. Validation
- Host validation:
  - `python -m pytest tests/test_flywire_annotations.py tests/test_inferred_lateralized.py tests/test_lateralized_probe.py`
  - result: `8 passed`
- WSL body-free splice probe:
  - `outputs/metrics/splice_probe_summary.json`
  - `outputs/metrics/splice_probe_groups.csv`
  - `outputs/metrics/splice_probe_side_differences.csv`

9. Next actions
- Add signed splice inputs so the body-free probe can represent inhibitory deviations instead of only positive deltas.
- Add coarse retinotopic structure, likely `u` / `v` bins, instead of broadcasting one scalar per `cell_type` + `side`.
- Only return to embodied claims after the body-free splice can preserve asymmetry robustly and recruit meaningful downstream brain responses.

## 2026-03-09 - Signed + spatial body-free splice follow-up

1. What I changed
- Added experimental signed boundary input support to the Torch backend:
  - `src/brain/pytorch_backend.py`
- Kept interface compatibility by extending:
  - `src/brain/mock_backend.py`
  - `src/brain/zero_backend.py`
- Added a spatial-overlap helper based on public FlyWire positions:
  - `src/brain/flywire_annotations.py`
- Extended the body-free probe so it can run with:
  - `input_mode=current_signed`
  - `spatial_bins > 1`
- Added tests:
  - `tests/test_brain_backend.py`
  - `tests/test_flywire_annotations.py`

2. Validation
- Host validation:
  - `python -m pytest tests/test_brain_backend.py tests/test_flywire_annotations.py tests/test_inferred_lateralized.py tests/test_lateralized_probe.py`
  - result: `11 passed`
- Syntax validation:
  - `python -m py_compile scripts/run_splice_probe.py src/brain/flywire_annotations.py src/brain/pytorch_backend.py src/brain/mock_backend.py src/brain/zero_backend.py`

3. What the signed + spatial probe does
- Signed mode:
  - uses direct current at the boundary instead of positive-only Poisson rate drive
- Spatial mode:
  - splits each shared visual `cell_type` + `side` into `4` coarse bins
  - FlyVis side uses `u`-based bins
  - whole-brain side uses inferred bins from public FlyWire spatial coordinates

4. New artifacts
- `outputs/metrics/splice_probe_signed_bins4_summary.json`
- `outputs/metrics/splice_probe_signed_bins4_groups.csv`
- `outputs/metrics/splice_probe_signed_bins4_side_differences.csv`
- `outputs/metrics/splice_probe_signed_bins4_100ms_summary.json`
- `outputs/metrics/splice_probe_signed_bins4_100ms_groups.csv`
- `outputs/metrics/splice_probe_signed_bins4_100ms_side_differences.csv`

5. What succeeded
- The body-free splice no longer has to rely on positive-only boundary drive.
- The body-free splice no longer broadcasts one scalar across an entire `cell_type` + `side`.
- In the signed+spatial `20 ms` probe:
  - side-difference preservation improved relative to the earlier broad positive-only probe
  - nonzero downstream motor readouts now appear
- In the signed+spatial `100 ms` probe:
  - downstream motor readouts become clearly nonzero for all asymmetric conditions
  - the sign of the turn-bias difference flips between left-dark and right-dark stimuli:
    - `body_left_dark`: `turn_right - turn_left = -10`
    - `body_right_dark`: `turn_right - turn_left = +10`

6. What failed
- Grouped boundary correlation dropped relative to the first broad type-level probe:
  - now about `0.746` for left/right and `0.819` for center in the signed+spatial runs
- Several groups saturate at high spike rates in the current mapping, especially positive `Am` bins.
- Strongly negative teacher targets often still appear as zero student spike-rate delta because the measured student boundary signal is still spike-based and the baseline is near quiescent.
- So the new blockers are now:
  - state-readout blindness for inhibitory deviations
  - current-scale calibration
  - better spatial correspondence than the present inferred one-axis binning

7. What changed in the project understanding
- The splice problem is now narrower and more concrete.
- We have moved from:
  - "does any grounded splice exist at all?"
- to:
  - "how do we calibrate and observe a grounded signed spatial splice without saturation and without losing inhibitory structure?"

8. Next actions
- Add state-based boundary readouts such as voltage or conductance so negative signed drive is observable without requiring spikes.
- Calibrate the signed-current scale and the spatial-bin mapping before any new embodied claim.

## 2026-03-09 - State-based splice readouts and calibrated body-free splice ranking

1. What I changed
- Added state-aware monitoring to the public Torch backend:
  - `src/brain/pytorch_backend.py`
  - new `WholeBrainTorchBackend.step_with_state(...)`
- Extended the body-free probe so each matched overlap group now records:
  - spike-rate deltas
  - voltage deltas
  - conductance deltas
- Added calibration scripts:
  - `scripts/run_splice_calibration.py`
  - `scripts/summarize_splice_calibration.py`
- Added a focused negative-current unit test:
  - `tests/test_brain_backend.py`

2. Validation
- Host tests:
  - `python -m pytest tests/test_brain_backend.py tests/test_flywire_annotations.py tests/test_inferred_lateralized.py tests/test_lateralized_probe.py`
  - result: `12 passed`
- Syntax validation:
  - `python -m py_compile scripts/run_splice_probe.py scripts/run_splice_calibration.py scripts/summarize_splice_calibration.py src/brain/pytorch_backend.py`

3. New artifacts
- State-based probe:
  - `outputs/metrics/splice_probe_signed_bins4_100ms_state_summary.json`
  - `outputs/metrics/splice_probe_signed_bins4_100ms_state_groups.csv`
  - `outputs/metrics/splice_probe_signed_bins4_100ms_state_side_differences.csv`
- Targeted calibration runs:
  - `outputs/metrics/splice_probe_bins4_current20_summary.json`
  - `outputs/metrics/splice_probe_bins4_current40_summary.json`
  - `outputs/metrics/splice_probe_bins4_current80_summary.json`
  - `outputs/metrics/splice_probe_bins2_current80_summary.json`
- Curated calibration ranking:
  - `outputs/metrics/splice_probe_calibration_curated.csv`
  - `outputs/metrics/splice_probe_calibration_curated.json`

4. What succeeded
- The probe now shows that spike-only evaluation was hiding real signed boundary responses.
- In the calibrated bins=`4`, current=`120` body-free run:
  - mean voltage group correlation is about `0.8709`
  - mean voltage side-difference correlation is about `0.8079`
  - left-dark vs right-dark downstream turn bias flips correctly:
    - left-dark: `turn_right - turn_left = -10`
    - right-dark: `turn_right - turn_left = +10`
- The curated calibration ranking now identifies the current best tested splice point as:
  - `4` spatial bins
  - `max_abs_current = 120`
- This is the first calibrated body-free splice setting in the repo that simultaneously:
  - preserves left/right boundary structure strongly in a signed state readout
  - keeps measured spike-rate saturation low
  - reaches the monitored downstream turn readouts with the correct left/right sign flip

5. What failed
- The full scripted calibration sweep in `scripts/run_splice_calibration.py` was too expensive to finish across the entire initial grid in one pass, so I stopped the broad sweep after enough bins=`1` and bins=`2` points were collected and filled the remaining critical comparisons with targeted single-run probes.
- The calibrated splice is still not robust enough for embodied claims:
  - bins=`4` lower-current runs preserve boundary asymmetry but fail the downstream turn-sign check
  - bins=`1` preserves broad grouped fit well but loses too much left/right structure
  - bins=`2` preserves left/right structure well but the tested settings still fail the downstream turn-sign check
- The best tested point is therefore only a local calibration result, not a proof of a globally optimal splice.

6. What changed in the project understanding
- `T057` is now closed: state-based boundary readouts were the missing diagnostic piece.
- `T058` is now closed in the narrower engineering sense: the current tested grid has a defensible best point and the tradeoffs are explicit.
- The next blockers are now downstream of calibration:
  - better retinotopic correspondence than the current inferred binning
  - deeper central-target / longer-window validation before body reintegration

7. Next actions
- Probe deeper intermediate targets and longer windows using the calibrated body-free splice.
- Improve the spatial correspondence beyond the current one-axis inferred bin proxy before returning to embodied cold-start claims.

## 2026-03-09 - Deeper relay probe and 2D UV-grid follow-up

1. What I attempted
- Continued from the calibrated body-free splice instead of returning to the body loop.
- Added a relay-candidate finder to identify bilateral annotated intermediate targets that sit between the grounded visual overlap groups and the monitored motor readouts:
  - `scripts/find_splice_relay_candidates.py`
- Added a dedicated relay probe so the calibrated splice can be evaluated over longer windows and against deeper central groups, not just the final motor readouts:
  - `scripts/run_splice_relay_probe.py`
- Extended the grounded spatial helper so the splice can use a coarse two-dimensional grid instead of only a one-axis proxy:
  - `src/brain/flywire_annotations.py`
- Extended the body-free splice probe with:
  - `--spatial-mode uv_grid`
  - `--spatial-u-bins`
  - `--spatial-v-bins`
  - `--spatial-flip-u`
  - `--spatial-flip-v`
  - file: `scripts/run_splice_probe.py`
- Ran the new relay and UV-grid probes in WSL.
- I initially launched the relay and UV-grid probe runs in parallel. That made them look stalled because both jobs were CPU-heavy. I killed those parallel runs and reran the probes sequentially so the resulting artifacts reflect clean single-job measurements.

2. What succeeded
- Relay candidate discovery now exists as a reproducible script plus saved artifacts:
  - `outputs/metrics/splice_relay_candidates.json`
  - `outputs/metrics/splice_relay_candidates_pairs.csv`
  - `outputs/metrics/splice_relay_candidates_roots.csv`
- The strongest bilateral annotated relay candidates found from the overlap-to-motor intersection are:
  - `LC31a`
  - `LC31b`
  - `LC19`
  - `LCe06`
  - `LT82a`
  - `LCe04`
- The calibrated body-free splice now has direct intermediate-target evidence, not just final motor evidence:
  - `outputs/metrics/splice_relay_probe_summary.json`
  - `outputs/metrics/splice_relay_probe.csv`
  - `outputs/metrics/splice_relay_probe_pairs.csv`
- At `100 ms`, the relay probe preserves the expected downstream turn-sign flip:
  - left-dark: `turn_right - turn_left = -10`
  - right-dark: `turn_right - turn_left = +10`
- At that same `100 ms` window, several relay groups already carry structured lateralized state:
  - `LC31a` right-minus-left voltage is negative in both asymmetric conditions, about `-2.60 mV` for left-dark and about `-1.86 mV` for right-dark
  - `LCe06` right-minus-left rate flips sign with the condition, about `-6.33 Hz` for left-dark and about `+10.67 Hz` for right-dark
  - `LT82a` shows the strongest relay asymmetry in the tested set, about `-45 Hz` for left-dark and about `0 Hz` for right-dark
- The retinotopy work now goes beyond the original one-axis proxy:
  - `src/brain/flywire_annotations.py` can now build a grounded coarse `u/v` grid from public FlyWire positions
  - `scripts/run_splice_probe.py` can now test that grid against FlyVis native `u/v`
- The new `uv_grid` probe variants are saved and comparable:
  - `outputs/metrics/splice_probe_uvgrid_2x2_current120_summary.json`
  - `outputs/metrics/splice_probe_uvgrid_flipu_summary.json`
  - `outputs/metrics/splice_probe_uvgrid_flipuv_summary.json`
- The best tested `uv_grid` boundary fit so far is the `flip_u` variant:
  - mean voltage group correlation about `0.8764`
  - mean voltage side-difference correlation about `0.8466`
- That boundary fit is better than the previous calibrated axis1d splice:
  - axis1d mean voltage group correlation about `0.8709`
  - axis1d mean voltage side-difference correlation about `0.8079`
- Host validation still passes:
  - `python -m pytest tests/test_flywire_annotations.py tests/test_brain_backend.py`
  - result: `7 passed`
- Syntax validation also passed:
  - `python -m py_compile src/brain/flywire_annotations.py scripts/run_splice_probe.py scripts/find_splice_relay_candidates.py scripts/run_splice_relay_probe.py`

3. What failed
- The longer-window relay probe exposed a new downstream-stability failure:
  - at `500 ms`, the downstream turn sign no longer preserves the initial left-vs-right flip
  - left-dark: `turn_right - turn_left = -17`
  - right-dark: `turn_right - turn_left = -9`
- So the calibrated splice launches the expected downstream response, but the recurrent brain dynamics drift over longer windows.
- The new `uv_grid` splice improved boundary agreement, but it did not preserve the correct downstream sign:
  - unflipped `uv_grid`:
    - left-dark: `turn_right - turn_left = +35`
    - right-dark: `turn_right - turn_left = -15`
  - `flip_u` `uv_grid`:
    - left-dark: `turn_right - turn_left = +5`
    - right-dark: `turn_right - turn_left = -10`
  - `flip_u + flip_v` `uv_grid`:
    - left-dark: `turn_right - turn_left = +10`
    - right-dark: `turn_right - turn_left = +30`
- This narrows the next blocker:
  - the `uv_grid` splice is not "too rich"
  - it is still oriented incorrectly relative to the downstream circuit, or it still lacks exact column alignment

4. Evidence paths
- `src/brain/flywire_annotations.py`
- `tests/test_flywire_annotations.py`
- `scripts/run_splice_probe.py`
- `scripts/find_splice_relay_candidates.py`
- `scripts/run_splice_relay_probe.py`
- `outputs/metrics/splice_relay_candidates.json`
- `outputs/metrics/splice_relay_probe_summary.json`
- `outputs/metrics/splice_probe_uvgrid_2x2_current120_summary.json`
- `outputs/metrics/splice_probe_uvgrid_flipu_summary.json`
- `outputs/metrics/splice_probe_uvgrid_flipuv_summary.json`
- `docs/splice_probe_results.md`

5. Next actions
- Resolve UV-grid orientation / exact column alignment so the better two-dimensional boundary fit also preserves downstream turn sign.
- Explain or stabilize the longer-window downstream drift that erases the correct initial turn-sign flip by `500 ms`.
- Keep the next loop body-free until those two blockers are understood.

## 2026-03-09 - UV-grid targeted alignment follow-up and drift explanation

1. What I attempted
- Continued directly on `T061` and `T062`.
- Added richer spatial-alignment controls on the whole-brain side:
  - axis swap for the two PCA-based spatial axes
  - side-specific horizontal mirroring
  - files:
    - `src/brain/flywire_annotations.py`
    - `scripts/run_splice_probe.py`
- Added a targeted UV-grid summarizer:
  - `scripts/summarize_uvgrid_targeted.py`
- Added pulse-schedule support to the deeper relay probe:
  - `scripts/run_splice_relay_probe.py`
  - new `--input-pulse-ms`
- Added a compact relay-drift summarizer:
  - `scripts/summarize_relay_drift.py`
- Validated the new code locally, then ran targeted WSL body-free probes instead of returning to the body loop.

2. What succeeded
- Local validation passed after the new spatial-alignment helper and summarizer changes:
  - `python -m pytest tests/test_flywire_annotations.py tests/test_brain_backend.py`
  - result: `9 passed`
- The targeted UV-grid follow-up is now backed by compact comparison artifacts:
  - `outputs/metrics/splice_uvgrid_targeted_comparison.csv`
  - `outputs/metrics/splice_uvgrid_targeted_comparison.json`
- The targeted UV-grid runs now include side-specific horizontal mirroring:
  - `outputs/metrics/splice_probe_uvgrid_mirror_summary.json`
  - `outputs/metrics/splice_probe_uvgrid_flipu_mirror_summary.json`
  - `outputs/metrics/splice_probe_uvgrid_flipv_mirror_summary.json`
  - `outputs/metrics/splice_probe_uvgrid_swap_mirror_summary.json`
- The best targeted boundary-fit row is now:
  - `flip_v = true`
  - `mirror_u_by_side = true`
  - mean voltage group correlation about `0.8764`
  - mean voltage side-difference correlation about `0.8467`
- But even that best targeted row still fails the downstream sign test:
  - left-dark: `turn_right - turn_left = -15`
  - right-dark: `turn_right - turn_left = -5`
- This is now a stronger result than before:
  - plain global flips were not enough
  - side-specific horizontal mirroring was also not enough
  - so the remaining spatial blocker is no longer just axis-sign ambiguity
- The drift follow-up is also now backed by compact comparison artifacts:
  - `outputs/metrics/splice_relay_drift_comparison.csv`
  - `outputs/metrics/splice_relay_drift_comparison.json`
- The relay-drift comparison now shows three concrete reference points:
  - `100 ms` hold:
    - left-dark `-10`
    - right-dark `+10`
    - correct sign
  - `500 ms` hold:
    - left-dark `-17`
    - right-dark `-9`
    - sign collapsed
  - `500 ms` with only a `25 ms` pulse:
    - left-dark `0`
    - right-dark about `-6.32`
    - sign still not preserved

3. What failed
- The full `uv_grid` orientation brute-force search became too expensive once the side-specific mirror branch was added, so I stopped using the full brute-force loop and switched to a smaller targeted matrix around the most promising UV-grid families.
- The first targeted WSL batch also failed once because PowerShell ate the bash `$PY` variable; I reran it with the Python path inlined.
- The broad `500 ms` drift sweep was also too expensive when it monitored more state than needed, so I narrowed it to compact comparison artifacts instead of waiting on the larger sweep.
- Most importantly, neither `T061` nor `T062` produced a full fix:
  - `T061`: no tested UV-grid orientation or side-mirror variant restored the correct downstream left-vs-right motor sign
  - `T062`: even a very short `25 ms` pulse does not preserve the correct sign by `500 ms`

4. Evidence paths
- `src/brain/flywire_annotations.py`
- `scripts/run_splice_probe.py`
- `scripts/run_splice_relay_probe.py`
- `scripts/summarize_uvgrid_targeted.py`
- `scripts/summarize_relay_drift.py`
- `outputs/metrics/splice_uvgrid_targeted_comparison.csv`
- `outputs/metrics/splice_uvgrid_targeted_comparison.json`
- `outputs/metrics/splice_relay_drift_comparison.csv`
- `outputs/metrics/splice_relay_drift_comparison.json`
- `outputs/metrics/splice_relay_probe_500ms_pulse25_summary.json`
- `docs/splice_probe_results.md`

5. Next actions
- The next spatial task is no longer generic UV-grid orientation. It is finer or cell-type-specific column alignment.
- The next temporal task is no longer "is the drift caused by holding the input too long?" It is identifying which recurrent or readout mechanism causes the `500 ms` sign collapse after a correct `100 ms` launch.

## 2026-03-09 - Embodied splice path wired for a real demo

1. Why this new branch exists
- The newest visual splice work until now was body-free only.
- The user requested a real `2 s` demo using the newest splice, so I needed to carry the calibrated splice into the embodied runtime instead of falling back to any `P9` prosthetic or old scalar bridge.

2. What I changed
- Added a new explicit embodied visual-splice injector:
  - `src/bridge/visual_splice.py`
- Extended the fast FlyGym vision path to expose static FlyVis connectome metadata needed for online splice mapping:
  - `src/body/fast_realistic_vision_fly.py`
  - `src/body/interfaces.py`
  - `src/body/flygym_runtime.py`
- Extended the closed-loop bridge to pass signed direct-current splice injections into the real brain backend:
  - `src/bridge/controller.py`
  - `src/runtime/closed_loop.py`
- Added a focused embodied-splice config:
  - `configs/flygym_realistic_vision_splice_axis1d.yaml`
- Added a unit test covering baseline initialization and signed current emission:
  - `tests/test_visual_splice.py`

3. What the new embodied splice mode does
- It does not use `public_p9_context`.
- It does not use `inferred_visual_p9_context`.
- It does not restore decoder or body fallback locomotion.
- It takes the live `nn_activities_arr` from the real FlyVis path, groups that activity at the current best body-free splice boundary, subtracts a reset-frame baseline, and injects signed direct current into exact shared FlyWire `cell_type + side + bin` groups in the whole-brain model.
- The initial embodied mode is deliberately conservative:
  - `axis1d`
  - `4` spatial bins
  - `value_scale = 101.94613788960949`
  - `max_abs_current = 120`
- This is based on the current best body-free calibration result rather than the newer but still sign-broken `uv_grid` branch.

4. Validation before the real run
- Local targeted validation passed:
  - `python -m pytest tests/test_visual_splice.py tests/test_bridge_unit.py tests/test_closed_loop_smoke.py`
  - result: `14 passed`
- Syntax validation passed for the new embodied splice files:
  - `python -m py_compile src/bridge/visual_splice.py src/body/fast_realistic_vision_fly.py src/body/flygym_runtime.py src/bridge/controller.py src/runtime/closed_loop.py`

5. Immediate next action
- Run the real WSL `2 s` FlyGym demo with:
  - `configs/flygym_realistic_vision_splice_axis1d.yaml`
- Save the video, JSONL, and metrics as evidence for whether the embodied splice produces anything stronger than the previous strict twitching regime.

## 2026-03-09 - Real `2 s` embodied demo with the newest splice

1. Run details
- I ran the new embodied splice path in real WSL FlyGym using:
  - `configs/flygym_realistic_vision_splice_axis1d.yaml`
  - `vision_payload_mode: fast`
  - no `P9` prosthetics
  - no decoder or body fallback locomotion
- Command used:
  - `~/.local/bin/micromamba run -n flysim-full python benchmarks/run_fullstack_with_realistic_vision.py --config configs/flygym_realistic_vision_splice_axis1d.yaml --mode flygym --duration 2 --output-root outputs/requested_2s_splice --output-csv outputs/benchmarks/fullstack_splice_axis1d_2s.csv --plot-path outputs/plots/fullstack_splice_axis1d_2s.png`

2. New evidence
- Demo video:
  - `outputs/requested_2s_splice/demos/flygym-demo-20260309-100707.mp4`
- Run log:
  - `outputs/requested_2s_splice/logs/flygym-demo-20260309-100707.jsonl`
- Metrics:
  - `outputs/requested_2s_splice/metrics/flygym-demo-20260309-100707.csv`
- Benchmark CSV:
  - `outputs/benchmarks/fullstack_splice_axis1d_2s.csv`
- Plot:
  - `outputs/plots/fullstack_splice_axis1d_2s.png`

3. What the run shows
- The run completed the full `2.0 s` simulated duration without crashing.
- The embodied splice was active on `999 / 1000` control cycles.
- The decoder produced nonzero commands on `982 / 1000` control cycles.
- The splice never reached the calibrated ceiling:
  - max applied splice current about `25.86`
  - configured clip `120`
- So this was not a saturated all-or-nothing current blast. It was active but moderate.

4. Metrics that matter
- From `outputs/requested_2s_splice/flygym-demo-20260309-100707/summary.json`:
  - `sim_seconds = 2.0`
  - `wall_seconds = 857.132014504`
  - `real_time_factor = 0.0023333628497789155`
  - `avg_forward_speed = 1.0916253476635753`
  - `path_length = 2.1810674446318234`
  - `net_displacement = 0.11315538386569819`
  - `displacement_efficiency = 0.05188073580402254`
  - `stable = 1.0`
- This is the key honest reading:
  - the splice now clearly produces persistent brain-driven command activity in the embodied loop
  - but the resulting motion is still inefficient and locally dithering rather than strong purposeful traversal

5. Extra log summary
- Parsed from `outputs/requested_2s_splice/logs/flygym-demo-20260309-100707.jsonl`:
  - `nonzero_commands = 982`
  - `nonzero_splice_cycles = 999`
  - `mean_left_drive = 0.04577`
  - `mean_right_drive = 0.03830`
- Early cycles confirm the intended initialization:
  - cycle `0`: baseline initialization, zero splice current, zero command
  - cycle `1+`: direct current begins

6. Conclusion
- This is the first real embodied demo in the repo using the newest visual splice path itself rather than a `P9` prosthetic.
- It is a real step forward over strict twitch-only inactivity because the splice is now producing persistent nonzero commands in the embodied loop.
- It is still not a success on meaningful locomotor behavior:
  - net displacement remains very small relative to path length
  - the run is active, but not yet behaviorally correct

7. Next actions
- Compare this embodied splice run against the zero-brain baseline and the previous strict mode using displacement-efficiency, not only path length.
- Then continue `T063` and `T064`, because the remaining blockers still look like:
  - finer or cell-type-specific column alignment
  - downstream recurrent drift / readout mismatch over longer windows

## 2026-03-09 - Why the new embodied splice still fails to locomote

1. What I audited
- I reviewed:
  - `outputs/requested_2s_splice/logs/flygym-demo-20260309-100707.jsonl`
  - `outputs/requested_2s_splice/flygym-demo-20260309-100707/summary.json`
  - `src/bridge/decoder.py`
  - `external/flygym/doc/source/tutorials/vision_basics.rst`
  - `external/flygym/doc/source/tutorials/turning.rst`
  - `external/flygym/flygym/examples/locomotion/turning_fly.py`

2. What is definitely not the problem
- The splice is not dead:
  - `visual_splice.nonzero_root_count > 0` on `999 / 1000` cycles
  - `nonzero_commands = 982 / 1000`
- The software path from brain readout to body command is not disconnected:
  - command sums and asymmetries are driven by the monitored neural rates as expected by `src/bridge/decoder.py`
- So this is not another case of "nothing is wired through."

3. The critical quantitative failure
- The decoded descending drives are far too small for the FlyGym walking interface:
  - `max_left_drive = 0.13965930025907064`
  - `max_right_drive = 0.14243771313159515`
  - mean drives:
    - left `0.04577`
    - right `0.03830`
- FlyGym's own controller documentation says the descending amplitude should not go far beyond `1`, and the vision tutorial's hand-tuned controller uses a range of roughly `0.2` to `1.0`.
- So the new splice is producing real commands, but almost all of them live below the range that normally produces robust walking in `HybridTurningFly`.

4. Why the commands stay tiny
- The decoder reads only a very small DN set:
  - forward: `P9` and `oDN1`
  - turn: `DNa01` and `DNa02`
  - reverse: `MDN`
- Those are aggregated in `src/bridge/decoder.py`.
- In the `2 ms` control window, the monitored rates are sparse and quantized:
  - forward-both-sides active on only `8` cycles
  - forward-left-only on `27`
  - forward-right-only on `99`
  - turn-left-only on `113`
  - turn-right-only on `100`
  - turn-both-sides on `22`
- The decoder then:
  - divides by large scale constants
  - passes through `tanh`
  - low-pass filters with `signal_smoothing_alpha = 0.08`
- Reconstructing the decoder state from the log shows the actual body command never exceeds about `0.142`.
- So the model is not generating a sustained locomotor command. It is generating sparse DN bursts that get smoothed into tiny amplitudes.

5. Why the body barely moves even though commands are nonzero
- The body-level response is weakly aligned with the intended command channels:
  - correlation between drive asymmetry and yaw rate: about `0.033`
  - correlation between total drive and forward speed: about `-0.111`
- Meanwhile the trajectory metrics show local activity, not locomotion:
  - `path_length = 2.1810674446318234`
  - `net_displacement = 0.11315538386569819`
  - `displacement_efficiency = 0.05188073580402254`
  - tiny bounding box:
    - width `0.1385`
    - height `0.0438`
- So the fly is doing leg-level motion and body jitter, but it is not entering a stable translational gait.

6. The broader systems reason
- The current visual splice now reaches the whole brain.
- But the output side is still too compressed and too high-level:
  - thousands of visual neurons are being driven
  - only a handful of descending neurons are read out
  - those few readouts are interpreted as the final 2D FlyGym descending control
- That is likely the wrong abstraction level.
- In other words:
  - software wiring: yes
  - biological/control-semantic wiring: no
- The present output mapping skips the missing VNC / premotor structure and asks a few sparse brain readouts to serve as a full locomotor controller. The logs show that they do not.

7. Bottom line
- The real reason it "won't live" is not that the visual splice is dead.
- It is that the current motor interface is still wrong in practice:
  - wrong output abstraction
  - too few readout neurons
  - too weak and too bursty command amplitudes for the FlyGym walking controller
- So the current failure is more on the output/control side than on the input splice side.

8. Immediate next actions
- Treat `T064` as a motor-readout audit too, not only a recurrent-drift audit.
- Test whether the current DN set is an insufficient output bottleneck by monitoring and decoding a broader descending / relay population before attempting more body runs.

## 2026-03-09 - Expanded readout branch started before touching the splice again

1. Why this branch is next
- The last embodied audit showed the input splice is alive but the output side is too narrow:
  - the brain is active
  - the decoder emits commands
  - but those commands are tiny and do not translate into locomotion
- So I am holding the visual splice fixed and changing only the readout side.

2. What I implemented
- Broadened the decoder so it can consume relay candidates from the grounded splice work:
  - `src/bridge/decoder.py`
- The decoder can now load bilateral relay candidate roots from:
  - `outputs/metrics/splice_relay_candidates.json`
- Added a new experimental readout config:
  - `configs/flygym_realistic_vision_splice_axis1d_expanded_readout.yaml`
- Added a focused unit test for relay-backed decoding:
  - `tests/test_bridge_unit.py`
- Updated bridge construction so the brain backend monitors whatever neuron IDs the decoder now actually needs:
  - `src/runtime/closed_loop.py`

3. Experimental expanded readout choice
- I did not change the visual splice.
- I selected the new relay-backed readout groups from the existing grounded candidate artifact:
  - forward proxy groups:
    - `LC31b`
    - `LCe06`
    - `LT82a`
  - turn proxy group:
    - `LCe06`
- Reason:
  - these groups were already identified structurally as likely relays between the splice boundary and the old DN readout set
  - `LCe06` is the clearest stable left/right-signed candidate in the relay probe
  - `LC31b`, `LCe06`, and `LT82a` all show large sustained bilateral activation that can plausibly carry locomotor context stronger than the old `8`-neuron bottleneck

4. Local validation
- Passed:
  - `python -m pytest tests/test_bridge_unit.py tests/test_closed_loop_smoke.py tests/test_visual_splice.py`
  - result: `15 passed`
- Passed:
  - `python -m py_compile src/bridge/decoder.py src/bridge/controller.py src/runtime/closed_loop.py`

5. Immediate next action
- Run the real embodied `2 s` demo with:
  - `configs/flygym_realistic_vision_splice_axis1d_expanded_readout.yaml`
- Then inspect whether real locomotion emerges before changing the visual splice again.

## 2026-03-09 - Relay-as-motor branch rejected, replaced with strict descending-only readout mining

1. What changed conceptually
- The relay-expanded branch above was explicitly rejected as a final motor semantics branch.
- The user correctly pointed out that optic-lobe / visual relay populations must not be treated as motor outputs.
- I therefore killed the in-flight real WSL relay-expanded run and replaced that branch with a strict descending-only readout pipeline.

2. What I stopped
- Killed the invalid relay-expanded benchmark process in WSL:
  - `wsl bash -lc "pkill -f 'benchmarks/run_fullstack_with_realistic_vision.py --config configs/flygym_realistic_vision_splice_axis1d_expanded_readout.yaml' || true"`
- Kept the files only as diagnostic history:
  - `configs/flygym_realistic_vision_splice_axis1d_expanded_readout.yaml`
- Stopped treating those optic-lobe relay groups as acceptable final motor outputs.

3. What I implemented instead
- Fixed the generic population decoder loader so it accepts either:
  - `cell_type`
  - or `candidate_label`
  - file: `src/bridge/decoder.py`
- Tightened the candidate mining step so it can produce a strict descending-only candidate set:
  - file: `scripts/find_descending_readout_candidates.py`
  - added `--strict-descending-only`
- Re-ran the candidate miner with the strict filter and wrote:
  - `outputs/metrics/descending_readout_candidates_strict.json`
  - `outputs/metrics/descending_readout_candidates_strict_pairs.csv`
  - `outputs/metrics/descending_readout_candidates_strict_roots.csv`
- Added a reproducible selector for supplemental descending forward/turn groups:
  - `scripts/select_descending_readout_groups.py`
  - output: `outputs/metrics/descending_readout_recommended.json`
- Added a descending-only embodied config:
  - `configs/flygym_realistic_vision_splice_axis1d_descending_readout.yaml`
- Tightened the bridge unit coverage so the decoder test now loads `candidate_label` JSON:
  - `tests/test_bridge_unit.py`

4. What the strict public descending candidate set contains
- The strict filter is now:
  - `super_class == descending`
  - `flow == efferent`
  - DN/oDN/MDN-like labels only
- This excludes the earlier tempting but wrong `cL22*` / `VES015` / `VES026` visual-centrifugal cells.
- Highest-scoring bilateral strict descending pairs:
  - `DNp09`
  - `DNp35`
  - `DNp06`
  - `DNpe031`
  - `DNb01`
  - `DNp71`
  - `DNb09`
  - `DNp103`
  - `DNp43`
  - `DNg97`
  - `DNp18`
  - `DNpe056`
  - `DNae002`
  - `DNpe040`
  - `DNpe016`
  - `DNp69`

5. Body-free descending probe
- Ran the strict descending probe in WSL:
  - `scripts/run_descending_readout_probe.py`
- Outputs:
  - `outputs/metrics/descending_readout_probe_strict.csv`
  - `outputs/metrics/descending_readout_probe_strict_pairs.csv`
  - `outputs/metrics/descending_readout_probe_strict_summary.json`
- Important result:
  - the `100 ms` window is useful for selecting supplemental readout groups
  - the `500 ms` window still inherits the previously known recurrent drift problem, so it is not a safe selection window

6. Supplemental descending group selection
- The selector excludes labels already covered by the fixed decoder DN set:
  - `DNp09`
  - `DNg97`
  - `DNa02`
- Recommended supplemental forward groups from `outputs/metrics/descending_readout_recommended.json`:
  - `DNp103`
  - `DNp06`
  - `DNp18`
  - `DNp35`
- Recommended supplemental turn groups:
  - `DNpe056`
  - `DNp71`
  - `DNpe040`

7. Local validation
- Passed:
  - `python -m pytest tests/test_bridge_unit.py -q`
  - result: `7 passed`

## 2026-03-09 - Descending-only embodied readout run succeeded

1. What I ran
- Real WSL embodied run with the strict descending-only expanded readout:
  - `configs/flygym_realistic_vision_splice_axis1d_descending_readout.yaml`
  - command:
    - `python benchmarks/run_fullstack_with_realistic_vision.py --config configs/flygym_realistic_vision_splice_axis1d_descending_readout.yaml --mode flygym --duration 2 --output-root outputs/requested_2s_splice_descending --output-csv outputs/benchmarks/fullstack_splice_descending_2s.csv --plot-path outputs/plots/fullstack_splice_descending_2s.png`

2. Produced artifacts
- Benchmark:
  - `outputs/benchmarks/fullstack_splice_descending_2s.csv`
- Plot:
  - `outputs/plots/fullstack_splice_descending_2s.png`
- Embodied run:
  - `outputs/requested_2s_splice_descending/flygym-demo-20260309-115041/demo.mp4`
  - `outputs/requested_2s_splice_descending/flygym-demo-20260309-115041/run.jsonl`
  - `outputs/requested_2s_splice_descending/flygym-demo-20260309-115041/metrics.csv`
  - `outputs/requested_2s_splice_descending/flygym-demo-20260309-115041/summary.json`
- Comparison artifact versus the earlier splice-only embodied run:
  - `outputs/metrics/descending_readout_comparison.csv`
  - `outputs/metrics/descending_readout_comparison.json`
- Written summary doc:
  - `docs/descending_readout_expansion.md`

3. Quantitative result
- The descending-only run completed the full `2 s`:
  - `stable = 1.0`
  - `completed_full_duration = 1.0`
- It now produces real traversal instead of local dithering:
  - `avg_forward_speed = 4.563790532043783`
  - `path_length = 9.11845348302348`
  - `net_displacement = 5.633006914226428`
  - `displacement_efficiency = 0.6177590229213569`
- Compared with the earlier splice-only embodied run:
  - old `net_displacement = 0.11315538386569819`
  - new `net_displacement = 5.633006914226428`
  - old `displacement_efficiency = 0.05188073580402254`
  - new `displacement_efficiency = 0.6177590229213569`
- Command magnitudes also moved into a much more plausible range:
  - old mean drives:
    - left `0.04576752944365208`
    - right `0.038295875266585365`
  - new mean drives:
    - left `0.31380241125955`
    - right `0.19510758948955362`
  - old max drives:
    - left `0.13965930025907064`
    - right `0.14243771313159515`
  - new max drives:
    - left `0.6430851601651894`
    - right `0.6038926955914254`

4. Why this is materially different from the failed splice-only run
- The visual splice is unchanged.
- The difference is the broadened descending-only readout:
  - fixed DN readout still present
  - plus supplemental descending/efferent populations selected from the body-free descending probe
- The new log shows much stronger neural support on the output side:
  - supplemental forward and turn populations are active
  - body commands are larger and more persistent
  - the fly now traverses space instead of accumulating local jitter

5. What this still does not prove
- It does not prove final biological correctness of the chosen descending readout.
- It does not solve the known longer-window recurrent drift.
- It does not remove the need for a matched `zero_brain` / no-target control on this exact new descending-only branch.
- So this is a grounded improvement, not a final success declaration.

6. Immediate next action
- Add the matched ablation check for the descending-only embodied branch:
  - `T070`

## 2026-03-09 - Visual-drive validation for the descending-only embodied branch

1. What I implemented
- Added a target-free body option to the real FlyGym runtime:
  - `src/body/flygym_runtime.py`
  - `src/runtime/closed_loop.py`
- This allows the same embodied branch to be run either:
  - with the standard public `MovingFlyArena`
  - or on `FlatTerrain` with no target fly at all
- Added matched configs for the descending-only branch:
  - `configs/flygym_realistic_vision_splice_axis1d_descending_readout_zero_brain.yaml`
  - `configs/flygym_realistic_vision_splice_axis1d_descending_readout_no_target.yaml`

2. Validation on the code changes
- Passed:
  - `python -m py_compile src/body/flygym_runtime.py src/runtime/closed_loop.py`
- Passed:
  - `python -m pytest tests/test_bridge_unit.py -q`
  - result: `7 passed`

3. What I ran
- Matched zero-brain control:
  - `outputs/requested_2s_splice_descending_zero_brain/flygym-demo-20260309-122135/demo.mp4`
  - `outputs/requested_2s_splice_descending_zero_brain/flygym-demo-20260309-122135/metrics.csv`
- Matched no-target control:
  - `outputs/requested_2s_splice_descending_no_target/flygym-demo-20260309-122723/demo.mp4`
  - `outputs/requested_2s_splice_descending_no_target/flygym-demo-20260309-122723/metrics.csv`
- Comparison artifact:
  - `outputs/metrics/descending_visual_drive_validation.csv`
  - `outputs/metrics/descending_visual_drive_validation.json`
- Written summary:
  - `docs/descending_visual_drive_validation.md`

4. What the controls show

### Zero-brain control

- `nonzero_command_cycles = 0`
- `net_displacement = 0.011823383234191902`
- `displacement_efficiency = 0.0320475393946615`

This confirms again that the descending-only embodied branch has no hidden locomotor fallback.

### No-target control

- `avg_forward_speed = 3.6971077463080686`
- `net_displacement = 4.938367142047433`
- `displacement_efficiency = 0.6685375152288059`

This is important:
- removing the target does **not** collapse locomotion
- so the moving target is not the only visual source driving the branch
- realistic optic flow / scene structure from the floor and self-motion is enough to keep the branch active

### Target-present branch versus no-target branch

With the moving target present:

- `avg_forward_speed = 4.563790532043783`
- `mean_total_drive = 0.5089100007491035`
- `mean_abs_drive_diff = 0.16774428657780152`

Without the target:

- `avg_forward_speed = 3.6971077463080686`
- `mean_total_drive = 0.436327681959764`
- `mean_abs_drive_diff = 0.12627696034183364`

So the moving target increases:

- forward speed by about `23.44%`
- mean total drive by about `16.63%`
- mean steering asymmetry by about `32.84%`

5. Pursuit-specific analysis
- The current run log does not yet record the target fly state directly.
- But `MovingFlyArena` has a deterministic public trajectory:
  - radius `10`
  - angular speed `15 / 10 = 1.5`
- Using that public trajectory and the logged fly pose from:
  - `outputs/requested_2s_splice_descending/flygym-demo-20260309-115041/run.jsonl`
  I reconstructed target bearing over time and compared it to the steering command.

Results:

- `corr(right_drive - left_drive, target_bearing) = 0.7521880536563109`
- sign match rate between steering command and target bearing = `0.7270875763747454`
- sign opposition rate = `0.2535641547861507`
- `corr(total_drive, target_frontalness) = 0.4949172168385213`
- `corr(total_drive, -abs(target_bearing)) = 0.5246216094922695`

Interpretation:

- steering in the target-present branch is strongly aligned with target bearing
- total forward drive rises when the target becomes more frontal
- this is consistent with the user's observation that the fly accelerates when the target moves into both visual fields

6. Honest conclusion
- I can now support the following claim:
  - the new descending-only embodied branch is brain-driven and visually driven
  - the moving target measurably modulates steering and drive
- I cannot yet claim:
  - the branch is purely target-driven
  - or that the selected descending groups are already the final true biological locomotor code
- The no-target control shows that the branch also responds to the rest of the visual scene, especially self-motion and floor optic flow.

7. Immediate next action
- Add explicit target-state logging and controlled left/right target conditions so pursuit claims no longer depend on reconstructed public arena kinematics:
  - `T071`

## 2026-03-09 - Direct target-state logging and controlled target-condition validation

1. What I attempted
- Added explicit target-state logging to the embodied descending-only splice branch so pursuit claims no longer depend on reconstructing the public `MovingFlyArena` trajectory.
- Added runtime controls for target enable/disable, initial phase, and angular direction so the target can be placed on the left or right deterministically.
- Ran a logged-target rerun of the real `2 s` descending-only embodied branch and generated matched controlled left/right target-condition runs.
- Re-summarized the descending visual-drive evidence using the direct logged target state rather than reconstructed arena kinematics.

2. What succeeded
- The runtime now logs direct target state from simulation physics, including:
  - `target_state.position_x`
  - `target_state.position_y`
  - `target_state.yaw`
  - `target_state.distance`
  - `target_state.bearing_body`
- The following controlled configs now exist:
  - `configs/flygym_realistic_vision_splice_axis1d_descending_readout_zero_brain.yaml`
  - `configs/flygym_realistic_vision_splice_axis1d_descending_readout_no_target.yaml`
  - `configs/flygym_realistic_vision_splice_axis1d_descending_readout_target_left.yaml`
  - `configs/flygym_realistic_vision_splice_axis1d_descending_readout_target_right.yaml`
  - `configs/flygym_realistic_vision_splice_axis1d_descending_readout_stationary_left.yaml`
  - `configs/flygym_realistic_vision_splice_axis1d_descending_readout_stationary_right.yaml`
- The direct logged-target rerun completed and now anchors the pursuit analysis:
  - `outputs/requested_2s_splice_descending_logged_target/flygym-demo-20260309-142600/demo.mp4`
  - `outputs/requested_2s_splice_descending_logged_target/flygym-demo-20260309-142600/run.jsonl`
  - `outputs/requested_2s_splice_descending_logged_target/flygym-demo-20260309-142600/metrics.csv`
- Updated summary artifacts now exist:
  - `outputs/metrics/descending_visual_drive_validation.csv`
  - `outputs/metrics/descending_visual_drive_validation.json`
  - `outputs/metrics/descending_target_conditions.json`
  - `outputs/metrics/descending_stationary_target_conditions.json`
  - `docs/descending_visual_drive_validation.md`

3. What the direct logged-target rerun shows
- With target + real brain:
  - `avg_forward_speed = 4.326325286840003`
  - `net_displacement = 4.943851959931002`
  - `displacement_efficiency = 0.571940438198806`
  - `mean_total_drive = 0.48122784453026124`
  - `mean_abs_drive_diff = 0.18706207480312084`
- Against directly logged target state from the same run:
  - `corr(right_drive - left_drive, target_bearing) = 0.7228049533574713`
  - steer-sign match rate = `0.7476828012358393`
  - steer-sign opposition rate = `0.23274974253347064`
  - `corr(total_drive, target_frontalness) = 0.330852251649671`
  - `corr(forward_speed, target_frontalness) = 0.2452151723394304`
- This removes the old reconstruction dependency from the main pursuit-modulation claim.

4. What the controlled left/right conditions show
- Condition control itself is working:
  - moving-left initial target bearing = `+1.5697550741127948`
  - moving-right initial target bearing = `-1.5755194594138011`
  - stationary-left initial target bearing = `+1.5726071797408192`
  - stationary-right initial target bearing = `-1.5726715812462848`
- The short side-isolated steering result is still mixed:
  - moving-left early mean drive difference = `-0.05511041478293597`
  - moving-right early mean drive difference = `-0.021594800448792844`
  - stationary-left early mean drive difference = `-0.056939209407958435`
  - stationary-right early mean drive difference = `-0.017198015031286273`
- So the repo now has the right instrumentation and deterministic target controls, but the short isolated left/right pursuit reflex is not yet a clean mirrored result.

5. Honest conclusion
- The descending-only branch is still supported as brain-driven and visually driven.
- The continuous target-present run now has direct target-state evidence, not just reconstructed arena kinematics.
- The controlled left/right target placements are now explicit and reproducible.
- The remaining open issue is no longer instrumentation; it is behavioral interpretation, because the short side-isolated left/right steering response is still mixed.

6. Next actions
- Mark `T071` complete because explicit target-state logging and controlled target conditions are now implemented and run.
- Track the remaining side-isolated steering ambiguity separately as a new follow-up task.

## 2026-03-09 - GitHub publishing prep

1. What I attempted
- Audited the workspace for GitHub push blockers after the request to upload the repo.
- Checked whether the workspace was already a Git repository and whether GitHub CLI was available.
- Measured the largest files so the publishable tree could be filtered before initializing Git.

2. What succeeded
- Confirmed the workspace was not yet a Git repository.
- Confirmed `gh` is not installed on this machine, so GitHub repo creation/push must use plain `git` plus a remote URL.
- Added `.gitignore` to exclude content that should not go into normal GitHub history:
  - `external/`
  - `outputs/cache/`
  - generated `*.jsonl`, `*.prof`, `*.pkl`, `*.parquet`, `*.feather`
  - `tests/.tmp/`
- Added `GITHUB_UPLOAD_NOTES.md` documenting exactly what will and will not be pushed.

3. What failed or remains open
- The largest local assets are not pushable as-is to a normal GitHub repo, for example:
  - `outputs/cache/weight_csr.pkl` at about `303 MB`
  - `outputs/cache/weight_coo.pkl` at about `302 MB`
  - `external/fly-brain/data/2025_Connectivity_783.parquet` at about `101 MB`
- Because of that, a literal "upload everything" push is not the right move. The correct move is to push the reproducible repo and keep oversized downloaded/generated assets out of Git history unless the user explicitly wants Git LFS or releases.
- A remote GitHub URL is still needed before the final push command can be run.

4. Evidence paths
- `.gitignore`
- `GITHUB_UPLOAD_NOTES.md`

5. Next actions
- Initialize Git in the workspace.
- Stage the publishable tree under the new ignore rules.
- If the user provides a GitHub remote URL, add it and push the first commit.

## 2026-03-09 - GitHub remote added, local repo committed, push blocked by account mismatch

1. What I attempted
- Initialized Git in `G:\\flysim`, staged the publishable tree under the new ignore rules, and created the first local commit.
- Added the user-provided remote:
  - `https://github.com/jagoff412/openfly`
- Tried both HTTPS and SSH push paths.

2. What succeeded
- Local repo is now initialized and committed:
  - `29d14e5 Initial public flysim reproduction repo`
- The remote is configured and the working tree is clean.
- SSH authentication to GitHub itself works on this machine.

3. What failed
- HTTPS push failed because this machine does not have a usable interactive GitHub credential helper in this shell:
  - `git: 'credential-manager-core' is not a git command`
  - `fatal: could not read Username for 'https://github.com': terminal prompts disabled`
- SSH push also failed, but for a clearer reason:
  - the local SSH key authenticates as GitHub user `jagoff2`
  - the target repo is `jagoff412/openfly`
  - GitHub rejected the push with:
    - `ERROR: Permission to jagoff412/openfly.git denied to jagoff2.`

4. Evidence paths
- `.gitignore`
- `GITHUB_UPLOAD_NOTES.md`
- local commit:
  - `29d14e5`

5. Honest conclusion
- The repo is ready to push technically.
- The remaining blocker is account/auth ownership, not repo state.
- To finish the upload, the authenticated GitHub identity must have write access to `jagoff412/openfly`, or the remote must be changed to a repo owned by `jagoff2`.

## 2026-03-09 - GitHub upload completed

1. What I attempted
- Switched the remote from the mismatched `jagoff412/openfly` repo to the user-provided repo owned by the authenticated account:
  - `git@github.com:jagoff2/openfly.git`
- Retried the push over SSH.

2. What succeeded
- The push completed successfully.
- `main` now tracks `origin/main`.
- Current local commit history pushed:
  - `7098bfa Document GitHub push blocker`
  - `29d14e5 Initial public flysim reproduction repo`

3. Evidence paths
- Remote:
  - `git@github.com:jagoff2/openfly.git`
- Branch:
  - `main`

4. Honest conclusion
- The repo is now uploaded to GitHub.
- The current GitHub remote matches the authenticated account and no longer has the earlier ownership mismatch.

## 2026-03-09 - Public-facing docs refreshed for the current strongest branch

1. What I attempted
- Audited the public-facing docs after the README still described the old strict diagnostic as if it were the current main result.
- Updated the README to describe the actual strongest branch and added exact commands to reproduce the current target/no-target/zero-brain evidence.
- Updated the parity report so it no longer uses the old strict default diagnostic as the main embodied reference.

2. What succeeded
- `README.md` now:
  - states that the strongest current branch is `configs/flygym_realistic_vision_splice_axis1d_descending_readout.yaml`
  - points readers to the current strongest demo and control artifacts
  - documents exact reproduction commands for:
    - target + real brain
    - no target + real brain
    - target + zero brain
    - controlled target-side follow-ups
- `REPRO_PARITY_REPORT.md` now:
  - promotes the descending-only embodied splice branch into the main parity narrative
  - marks locomotion and reaction-to-visual-stimulus according to the current stronger evidence
  - keeps the remaining open issues focused on biological correctness and mixed short left/right side conditions

3. Honest conclusion
- The public-facing docs are now aligned with the current evidence instead of the older strict-only failure mode.
- The remaining open claims are still clearly limited:
  - current strongest branch is brain-driven and visually driven
  - but not yet a final proof of the exact biological motor code or a clean mirrored short side-specific pursuit reflex

## 2026-03-09 - Paper-grounded feeding and grooming brain tasks added

1. What I attempted
- Added the two public Shiu-paper sensorimotor tasks as runnable brain-only probes:
  - feeding
  - grooming
- Kept them grounded in the public notebook IDs already present in the checked-out `fly-brain` repo.
- Kept them explicitly brain-only so they are ready for later embodiment experiments without pretending the body-side interfaces already exist.

2. What succeeded
- Added grounded task ID definitions:
  - `src/brain/paper_task_ids.py`
- Added reusable probe logic:
  - `src/brain/paper_task_probes.py`
- Added runnable scripts:
  - `scripts/run_feeding_probe.py`
  - `scripts/run_grooming_probe.py`
- Added test coverage:
  - `tests/test_paper_task_ids.py`
- Added documentation:
  - `docs/feeding_and_grooming_brain_tasks.md`
- Generated initial local artifacts:
  - `outputs/metrics/feeding_probe.csv`
  - `outputs/metrics/feeding_probe_summary.json`
  - `outputs/plots/feeding_probe.png`
  - `outputs/metrics/grooming_probe.csv`
  - `outputs/metrics/grooming_probe_summary.json`
  - `outputs/plots/grooming_probe.png`
  - `outputs/metrics/grooming_probe_500ms.csv`
  - `outputs/metrics/grooming_probe_500ms_summary.json`
  - `outputs/plots/grooming_probe_500ms.png`

3. What the first local probe results show
- Feeding:
  - the right-hemisphere sugar GRN set produces a clear `MN9` response in the short `100 ms` sweep
  - strongest observed row:
    - `sugar_right @ 180 Hz`
    - `mn9_left = 60 Hz`
    - `mn9_right = 40 Hz`
    - `mn9_total = 100 Hz`
  - the left-hemisphere sugar set stayed silent in that same short window
- Grooming:
  - the short `100 ms` sweep shows `aBN1` activation under `JON_CE` and `JON_all`
  - the short `100 ms` sweep does not show `aDN1` spiking
  - the longer `500 ms` follow-up does show a weaker downstream grooming response:
    - `jon_all @ 220 Hz` gives `aDN1_right = 6 Hz` and `aBN1 = 28 Hz`

4. Honest conclusion
- These tasks are now added as grounded brain-side probes.
- They are useful and reproducible today.
- They are not yet embodied behaviors.
- The next embodiment step is now narrower and cleaner:
  - map body-side gustatory/contact state into the published sugar/JON inputs
  - then map `MN9` / `aDN1` / `aBN1` into actual proboscis or grooming actuation interfaces

## 2026-03-10 - Journal-style whitepaper draft added

1. What I attempted
- Consolidated the repo's architecture, benchmark evidence, negative findings, splice-discovery work, embodied validation, and feeding/grooming brain tasks into one long-form publication-style document.
- Kept the write-up aligned with `AGENTS.MD`: evidence-heavy, explicit about remaining gaps, and careful not to overclaim exact Eon parity.

2. What succeeded
- Added `docs/openfly_whitepaper.md`.
- The document includes:
  - abstract and scope
  - architecture and methods
  - benchmark and profiler results
  - failure analysis of the original scalar public-anchor bridge
  - body-free visual splice discovery and calibration results
  - descending-only embodied readout expansion
  - matched `zero_brain`, no-target, and logged-target validation results
  - feeding and grooming brain-task probe results
  - limitations, next steps, and exact reproduction commands

3. Honest conclusion
- The whitepaper does not claim that the repo has solved final biological motor semantics or exact private-demo parity.
- It does capture the strongest supported current claim:
  - the repo now has a realistic-vision, whole-brain, embodied closed loop whose strongest current branch is brain-driven and visually driven under matched controls.
- It also preserves the key negative findings that shaped the architecture, which are necessary for an honest technical record.

## 2026-03-10 - Whitepaper signed, README archived, and repo landing page replaced

1. What I attempted
- Added explicit authorship metadata to the new whitepaper.
- Archived the previous operational `README.md`.
- Replaced the repo root `README.md` with the whitepaper content as requested.
- Prepared the doc update for GitHub push.

2. What succeeded
- `docs/openfly_whitepaper.md` now carries explicit `Author: Codex` metadata.
- The prior operational README is preserved at:
  - `docs/README_legacy.md`
- `README.md` now mirrors the whitepaper so the GitHub landing page presents the full long-form technical write-up instead of the shorter operational README.

3. Honest conclusion
- This changes the public presentation layer, not the experimental evidence.
- The old operational README is still preserved in-repo, so replication instructions and prior structure are not lost.

## 2026-03-10 - Reviewed new Eon embodiment update against local results

1. What I attempted
- Reviewed the new Eon update at `https://eon.systems/updates/embodied-brain-emulation`.
- Followed the main method-bearing links from the post:
  - Shiu brain-model paper
  - whole-brain connectome and annotation papers
  - FlyVis paper
  - NeuroMechFly v2 paper
  - NeuroMechFly advanced-vision docs
  - NeuroMechFly controller docs
- Compared the disclosed Eon architecture to the current strongest local branch and wrote the result into the repo.

2. What succeeded
- Added `docs/eon_embodiment_update_review_2026-03-10.md`.
- Main comparison result:
  - the new Eon post largely confirms our later diagnosis that the hard problem is the interface between vision, brain, and embodied controllers
  - it also confirms that their current embodiment is still controller-mediated and heuristic
  - they explicitly state that visual input is not yet significantly influencing their current embodied behavior
  - our strongest current local branch still has stronger target-vs-control evidence for visual drive

3. Honest conclusion
- The new Eon post does not reveal a hidden fully biological end-to-end controller that would invalidate the local reconstruction strategy here.
- It instead supports the view that the public brain core is only one part of the problem and that the unresolved splice/output interface is the real systems bottleneck.

## 2026-03-10 - Eon comparison integrated into whitepaper and pushed

1. What I attempted
- Added the new Eon-update comparison into the main whitepaper so the repo has one long-form document that includes both the local results and the subsequent public Eon disclosure.
- Prepared the new review doc, updated trackers, and pushed the documentation update to GitHub.

2. What succeeded
- `docs/openfly_whitepaper.md` now has a dedicated section comparing this repo to the later Eon embodiment update.
- `docs/eon_embodiment_update_review_2026-03-10.md` remains as the standalone comparison note.
- The doc update was committed and pushed to `origin/main`.

3. Honest conclusion
- The comparison section does not claim the local repo exceeds Eon in every way.
- It makes the narrower supported point:
  - the later Eon post largely confirms that the unresolved interface between vision, brain, and embodied control is the real bottleneck, and that the current disclosed embodiment remains controller-mediated rather than a fully solved biological motor stack.

## 2026-03-10 - README synced again to the latest whitepaper

1. What I attempted
- Checked whether the repo-home `README.md` still matched `docs/openfly_whitepaper.md` after the Eon comparison section was added.
- Found that `README.md` was stale relative to the updated whitepaper.
- Re-synced the root README so the GitHub landing page reflects the latest whitepaper text.

2. What succeeded
- `README.md` now matches `docs/openfly_whitepaper.md`, including the Eon comparison section.

3. Honest conclusion
- This was a presentation-layer sync only.
- No experimental claims or artifacts changed.

## 2026-03-11 - T063 review and restart

1. What I attempted
- Re-read `TASKS.md`, `PROGRESS_LOG.md`, `docs/visual_splice_strategy.md`, `docs/cold_start_visual_brain_plan.md`, and `docs/splice_probe_results.md` after context compaction.
- Re-inspected the current alignment code in `src/brain/flywire_annotations.py` and the body-free splice harness in `scripts/run_splice_probe.py` before making changes.

2. What succeeded
- Reconstructed the current state accurately enough to resume `T063` on the right branch.
- Confirmed that the current `uv_grid` alignment only supports global axis swap / flip plus side-specific horizontal mirroring.
- Confirmed the current blocker: boundary agreement is already strong, but downstream sign remains wrong, so the next step has to be per-cell-type alignment rather than another global transform.

3. What failed
- No new alignment improvement has been implemented yet in this entry; this is the restart checkpoint before code changes.

4. Evidence paths
- `TASKS.md`
- `PROGRESS_LOG.md`
- `docs/visual_splice_strategy.md`
- `docs/cold_start_visual_brain_plan.md`
- `docs/splice_probe_results.md`
- `src/brain/flywire_annotations.py`
- `scripts/run_splice_probe.py`

5. Next actions
- Implement a per-cell-type spatial-alignment path beyond the shared coarse UV grid.
- Re-run targeted body-free splice probes and compare them against the current best targeted `uv_grid` summary.

## 2026-03-11 - T063 completed with per-cell-type UV-grid alignment

1. What I attempted
- Added a per-cell-type spatial-transform path on the whole-brain side so the `uv_grid` splice is no longer limited to one global transform plus optional right-side mirroring.
- Added a dedicated body-free search script to greedily test per-cell-type `swap_uv` / `flip_u` / `flip_v` / `mirror_u_by_side` overrides against the grounded FlyVis teacher response.
- Re-ran a canonical `run_splice_probe.py` body-free summary using the recommended per-cell-type transform file.

2. What succeeded
- Added per-cell-type transform support in:
  - `src/brain/flywire_annotations.py`
  - `src/bridge/visual_splice.py`
  - `scripts/run_splice_probe.py`
- Added the dedicated search harness:
  - `scripts/run_celltype_uvgrid_alignment_search.py`
- Added unit coverage for the new per-cell-type transform override path:
  - `tests/test_flywire_annotations.py`
- Host validation passed:
  - `python -m pytest tests/test_flywire_annotations.py tests/test_visual_splice.py -q`
  - result: `8 passed`
- The body-free search found a sign-correct per-cell-type alignment starting from the old best global UV-grid transform:
  - `outputs/metrics/splice_celltype_alignment_search.json`
  - `outputs/metrics/splice_celltype_alignment_recommended.json`
- Key search result:
  - old best global UV-grid:
    - left turn bias `-15`
    - right turn bias `-5`
    - `sign_match = false`
  - new per-cell-type alignment search best:
    - left turn bias `-50`
    - right turn bias `+60`
    - `sign_match = true`
- A canonical re-run with the recommended transform file also preserved the correct downstream sign:
  - `outputs/metrics/splice_probe_uvgrid_celltype_aligned_summary.json`
  - left turn bias `-30`
  - right turn bias `+45`

3. What failed
- The canonical re-run did not keep the exact same boundary-correlation numbers reported by the greedy search summary.
- It still fixed the downstream sign cleanly, but the averaged voltage correlations in the canonical summary were slightly lower than the search-internal best score.
- So `T063` is solved at the level it was asked:
  - per-cell-type alignment can resolve the coarse downstream sign error
- but the result still needs embodied validation and does not replace `T064`.

4. Evidence paths
- `src/brain/flywire_annotations.py`
- `src/bridge/visual_splice.py`
- `scripts/run_splice_probe.py`
- `scripts/run_celltype_uvgrid_alignment_search.py`
- `tests/test_flywire_annotations.py`
- `tests/test_visual_splice.py`
- `outputs/metrics/splice_celltype_alignment_search.json`
- `outputs/metrics/splice_celltype_alignment_recommended.json`
- `outputs/metrics/splice_probe_uvgrid_celltype_aligned_summary.json`
- `outputs/metrics/splice_celltype_alignment_comparison.json`

5. Next actions
- Keep `T064` active: explain the `500 ms` recurrent sign collapse now that the coarse spatial sign error is no longer the main blocker.
- Add an embodied follow-up using the new per-cell-type UV-grid transform file in the descending-only branch.

## 2026-03-11 - T064 restart after the per-cell-type splice fix

1. What I attempted
- Re-opened the existing drift evidence after closing `T063`:
  - `outputs/metrics/splice_relay_drift_comparison.json`
  - `outputs/metrics/splice_relay_probe_summary.json`
  - `outputs/metrics/splice_relay_probe_500ms_pulse25_summary.json`
- Re-inspected the current body-free relay probe implementation in `scripts/run_splice_relay_probe.py`.
- Re-checked the fixed motor readout definitions in `src/brain/public_ids.py` and the supplemental descending candidate file in `outputs/metrics/descending_readout_candidates_strict.json`.

2. What succeeded
- Confirmed the key structural gap in the old relay-drift probe:
  - it only reports endpoint windows
  - and it only watches the fixed tiny DN readout plus a small relay set
- Confirmed that `T064` now needs time-resolved evidence, especially after `T063` proved the coarse input-side sign error is fixable.
- Narrowed the mechanistic possibilities to:
  - fixed DN readout collapse while deeper relay or supplemental descending groups remain sign-correct
  - broader descending-path collapse
  - or a true recurrent attractor that erases asymmetry across all monitored groups

3. What failed
- No mechanistic explanation is claimed yet in this entry; this is the restart checkpoint before the new audit script lands.

4. Evidence paths
- `outputs/metrics/splice_relay_drift_comparison.json`
- `outputs/metrics/splice_relay_probe_summary.json`
- `outputs/metrics/splice_relay_probe_500ms_pulse25_summary.json`
- `outputs/metrics/splice_probe_uvgrid_celltype_aligned_summary.json`
- `scripts/run_splice_relay_probe.py`
- `src/brain/public_ids.py`
- `outputs/metrics/descending_readout_candidates_strict.json`

5. Next actions
- Add a time-resolved body-free drift audit that monitors:
  - relay groups
  - fixed motor DN groups
  - supplemental descending/efferent candidates
- Run that audit on the new sign-correct per-cell-type splice and use it to explain whether the `500 ms` collapse is mainly a readout issue or a broader recurrent drift.

## 2026-03-11 - T064 completed with a time-resolved body-free drift audit

1. What I attempted
- Added a new time-resolved body-free audit script:
  - `scripts/run_splice_drift_audit.py`
- Ran it in WSL on the sign-correct per-cell-type UV-grid splice:
  - `outputs/metrics/splice_celltype_alignment_recommended.json`
- Measured two schedules:
  - sustained `hold`
  - `pulse_25ms`
- Monitored:
  - relay groups from `outputs/metrics/splice_relay_candidates.json`
  - the fixed tiny DN readout from `src/brain/public_ids.py`
  - the broader strict descending/efferent groups from `outputs/metrics/descending_readout_candidates_strict.json`

2. What succeeded
- Generated the audit artifacts:
  - `outputs/metrics/splice_drift_audit_summary.json`
  - `outputs/metrics/splice_drift_audit_timeseries.csv`
  - `outputs/metrics/splice_drift_audit_key_findings.json`
  - `outputs/metrics/splice_drift_audit_key_findings.csv`
- Added the write-up:
  - `docs/splice_drift_audit.md`
- The audit gives a stronger mechanistic answer than the old endpoint-only relay probe:
  - under sustained input, relay asymmetry does **not** collapse by `500 ms`
  - several broader descending groups also remain asymmetric by `500 ms`
  - but the original tiny fixed DN turn readout equalizes to zero by `500 ms`
- Key sustained-input numbers:
  - fixed DN turn bias at `100 ms`:
    - left `-40`
    - right `+100`
  - fixed DN turn bias at `500 ms`:
    - left `0`
    - right `0`
- Key relay persistence examples under sustained input:
  - `LC31a` contrastive right-minus-left:
    - `100 ms`: `+14.53`
    - `500 ms`: `+13.81`
  - `LC31b`:
    - `100 ms`: `+24.44`
    - `500 ms`: `+22.63`
  - `LCe04`:
    - `100 ms`: `+5.88`
    - `500 ms`: `+5.90`
- Key pulse result:
  - after a `25 ms` pulse, both relay and descending contrastive signals decay essentially to zero by `500 ms`
  - so the current public dynamics do not maintain a strong self-sustaining visuomotor state after a brief launch pulse

3. Honest conclusion
- The old `500 ms` sign collapse was **not** a complete splice failure.
- It is better explained by two effects:
  1. the fixed tiny DN readout is too brittle and equalizes under sustained drive
  2. the current public recurrent dynamics do not preserve the launched asymmetry once the external input is removed
- So the remaining blocker is now narrower and more concrete:
  - not "the whole network loses asymmetry by `500 ms`"
  - but "the tiny DN readout is insufficient for long-window interpretation, and there is no strong self-sustaining state after a short pulse"

4. Evidence paths
- `scripts/run_splice_drift_audit.py`
- `outputs/metrics/splice_drift_audit_summary.json`
- `outputs/metrics/splice_drift_audit_timeseries.csv`
- `outputs/metrics/splice_drift_audit_key_findings.json`
- `docs/splice_drift_audit.md`

5. Next actions
- Test the new per-cell-type UV-grid splice directly in the embodied descending-only branch rather than through the old tiny DN set.
- Keep long-window state-conditioning questions separate from output-readout questions in future embodiment claims.

## 2026-03-11 - T083 started with matched embodied UV-grid descending configs

1. What I attempted
- Began the embodied follow-up after `T064`.
- Created a matched config set that swaps the old axis1d splice for the new per-cell-type UV-grid splice while keeping the widened descending-only decoder path fixed.

2. What succeeded
- Added:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_no_target.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_zero_brain.yaml`
- These configs use:
  - `spatial_mode: uv_grid`
  - `spatial_u_bins: 2`
  - `spatial_v_bins: 2`
  - `spatial_flip_v: true`
  - `spatial_mirror_u_by_side: true`
  - `spatial_cell_type_transforms_path: outputs/metrics/splice_celltype_alignment_recommended.json`
- They keep the widened descending-only decoder unchanged so the embodied comparison isolates the input-splice change as cleanly as possible.

3. What failed
- No embodied run result yet in this entry; this is the configuration checkpoint before the matched WSL runs.

4. Evidence paths
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_no_target.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_zero_brain.yaml`
- `outputs/metrics/splice_celltype_alignment_recommended.json`

5. Next actions
- Run the matched real WSL target, no-target, and zero-brain embodied UV-grid descending tests sequentially.
- Summarize them against the existing axis1d descending branch with the same visual-drive metrics.

## 2026-03-11 - T082 and T083 completed with matched embodied UV-grid descending runs

1. What I attempted
- Ran the matched embodied comparison for the new per-cell-type UV-grid splice using the widened descending-only decoder:
  - target + real brain
  - no target + real brain
  - target + zero brain
- Then summarized those runs with the same visual-drive metrics used for the current axis1d descending baseline.

2. What succeeded
- Completed all three embodied WSL runs:
  - `outputs/requested_2s_splice_uvgrid_descending_target/flygym-demo-20260311-062430/demo.mp4`
  - `outputs/requested_2s_splice_uvgrid_descending_no_target/flygym-demo-20260311-063926/demo.mp4`
  - `outputs/requested_2s_splice_uvgrid_descending_zero_brain/flygym-demo-20260311-065432/demo.mp4`
- Generated matched summaries:
  - `outputs/metrics/descending_uvgrid_visual_drive_validation.csv`
  - `outputs/metrics/descending_uvgrid_visual_drive_validation.json`
  - `outputs/metrics/descending_uvgrid_vs_axis1d_comparison.csv`
  - `outputs/metrics/descending_uvgrid_vs_axis1d_comparison.json`
- Wrote the embodied comparison doc:
  - `docs/descending_uvgrid_visual_drive_validation.md`

3. What failed
- The per-cell-type UV-grid splice did not improve the embodied branch over the current axis1d descending baseline.
- In the target condition, the UV-grid branch regressed on the most important embodied pursuit metrics:
  - target-bearing steering correlation dropped from `0.7228` to `0.4590`
  - steer-sign match dropped from `0.7477` to `0.6527`
  - average forward speed dropped from `4.3263` to `3.6652`
  - net displacement dropped from `4.9439` to `4.2834`
- Within the UV-grid branch itself, the moving target no longer improves forward speed over the no-target condition:
  - target `avg_forward_speed = 3.6652`
  - no-target `avg_forward_speed = 3.6751`

4. Evidence paths
- `outputs/metrics/descending_uvgrid_visual_drive_validation.json`
- `outputs/metrics/descending_uvgrid_vs_axis1d_comparison.json`
- `docs/descending_uvgrid_visual_drive_validation.md`
- `outputs/requested_2s_splice_uvgrid_descending_target/flygym-demo-20260311-062430/summary.json`
- `outputs/requested_2s_splice_uvgrid_descending_no_target/flygym-demo-20260311-063926/summary.json`
- `outputs/requested_2s_splice_uvgrid_descending_zero_brain/flygym-demo-20260311-065432/summary.json`

5. Honest conclusion
- The body-free per-cell-type UV-grid splice solved the sign problem at the splice boundary, but that improvement did not transfer into a stronger embodied descending-only controller.
- The embodied UV-grid branch is still brain-driven, because the zero-brain control remains near-zero.
- But the current best embodied production path is still the simpler axis1d descending splice, not the new per-cell-type UV-grid branch.

6. Next actions
- Keep the per-cell-type UV-grid splice as an experimental branch, not the default embodied path.
- Focus the next iteration on why the body-free splice gain does not survive embodiment:
  - likely downstream calibration, decoder weighting, or time-scale mismatch
- Use the axis1d descending branch as the current embodied reference until the UV-grid branch exceeds it on target-bearing correlation and target-vs-no-target modulation.

## 2026-03-11 - T084 started with UV-grid-specific decoder calibration

1. What I attempted
- Reopened the UV-grid embodied branch specifically at the decoder / downstream calibration layer instead of changing the splice again.
- Compared the current UV-grid target log against the axis1d target log to identify which signal statistics actually regressed.

2. What succeeded
- Confirmed that the main UV-grid regression is not total brain silence:
  - the branch still has `993` nonzero command cycles in the `2 s` target run
- Confirmed that the UV-grid branch is under-driving and under-steering relative to axis1d:
  - mean total drive dropped from about `0.4812` to about `0.4442`
  - mean absolute drive difference dropped from about `0.1871` to about `0.1078`
  - target-bearing correlation dropped from about `0.7228` to about `0.4590`
- Ran an offline replay sweep over decoder-only parameters using the saved UV-grid target and no-target logs.
- The first promising decoder candidate from that replay uses:
  - lower smoothing (`alpha â‰ˆ 0.06`)
  - stronger output gains
  - nonzero `forward_asymmetry_turn_gain`

3. What failed
- Nothing new is claimed yet at the embodied level in this entry.
- This is the calibration setup checkpoint before the embodied rerun.

4. Evidence paths
- `outputs/requested_2s_splice_uvgrid_descending_target/flygym-demo-20260311-062430/run.jsonl`
- `outputs/requested_2s_splice_uvgrid_descending_no_target/flygym-demo-20260311-063926/run.jsonl`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout.yaml`

5. Next actions
- Preserve the offline decoder sweep as a reproducible script and artifact.
- Create a UV-grid-specific calibrated config.
- Rerun the embodied UV-grid target branch first, then matched no-target / zero-brain if the target rerun improves materially.

## 2026-03-11 - T084 completed with a calibrated UV-grid embodied branch

1. What I attempted
- Added a reproducible offline decoder replay sweep for the UV-grid target and no-target logs.
- Used that sweep to pick a UV-grid-specific decoder candidate.
- Ran matched embodied `target`, `no_target`, and `zero_brain` validations for the calibrated UV-grid branch.

2. What succeeded
- Added:
  - `scripts/run_uvgrid_decoder_calibration.py`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_zero_brain.yaml`
  - `docs/uvgrid_decoder_calibration.md`
- Added a decoder unit test for forward-asymmetry steering:
  - `tests/test_bridge_unit.py`
- Offline sweep artifacts:
  - `outputs/metrics/uvgrid_decoder_calibration.csv`
  - `outputs/metrics/uvgrid_decoder_calibration.json`
  - `outputs/metrics/uvgrid_decoder_calibration_best.json`
- Matched embodied artifacts:
  - `outputs/requested_2s_splice_uvgrid_descending_calibrated_target/flygym-demo-20260311-071452/demo.mp4`
  - `outputs/requested_2s_splice_uvgrid_descending_calibrated_no_target/flygym-demo-20260311-073028/demo.mp4`
  - `outputs/requested_2s_splice_uvgrid_descending_calibrated_zero_brain/flygym-demo-20260311-074301/demo.mp4`
- Matched summaries:
  - `outputs/metrics/descending_uvgrid_calibrated_visual_drive_validation.json`
  - `outputs/metrics/descending_uvgrid_calibration_comparison.json`

3. Key result
- The calibrated UV-grid branch is now stronger than both:
  - the old UV-grid branch
  - the old axis1d descending branch

Target-run gains versus the old UV-grid branch:
- `avg_forward_speed`: `3.6652 -> 4.9241`
- `net_displacement`: `4.2834 -> 5.7583`
- `corr_drive_diff_vs_target_bearing`: `0.4590 -> 0.8810`
- `steer_sign_match_rate`: `0.6527 -> 0.8878`

Target-run gains versus the old axis1d branch:
- `avg_forward_speed`: `4.3263 -> 4.9241`
- `net_displacement`: `4.9439 -> 5.7583`
- `corr_drive_diff_vs_target_bearing`: `0.7228 -> 0.8810`
- `steer_sign_match_rate`: `0.7477 -> 0.8878`

4. Control result
- The calibrated `zero_brain` branch remains near-zero:
  - `nonzero_command_cycles = 0`
  - `net_displacement = 0.011823383234191902`

5. Honest conclusion
- The earlier embodied UV-grid failure was not inherent to the per-cell-type splice.
- It was largely a decoder/downstream calibration mismatch.
- After UV-grid-specific calibration, the per-cell-type UV-grid branch becomes the strongest embodied branch currently in the repo.

6. Next actions
- Update the public-facing docs so they no longer name the old axis1d branch as the current strongest result.
- Keep the remaining biological caveats explicit:
  - still a descending-population-to-two-drive abstraction
  - still not pure target pursuit
  - still not a VNC / muscle-level motor pathway

## 2026-03-11 - T085 published the calibrated UV-grid branch to GitHub

1. What I attempted
- Prepared the repo for publish after the UV-grid calibration work.
- Verified whether `README.md` needed another manual sync from `docs/openfly_whitepaper.md`.

2. What succeeded
- Verified that `README.md` already matched `docs/openfly_whitepaper.md` byte-for-byte.
- Kept that synced state unchanged.
- Committed the calibrated UV-grid branch updates, docs, configs, scripts, and artifacts.
- Pushed the new state to `origin/main`.

3. What failed
- Nothing. The remote was already configured correctly and the push path was clean.

4. Evidence paths
- `README.md`
- `docs/openfly_whitepaper.md`
- `git remote -v`
- `git log --oneline -1`

5. Result
- The GitHub repo now reflects the calibrated UV-grid branch as the current strongest embodied result.

## 2026-03-11 - T086 started on the motor-interface bottleneck

1. What I attempted
- Reopened the current strongest calibrated UV-grid branch specifically at the output side.
- Reviewed:
  - `src/bridge/decoder.py`
  - `src/body/interfaces.py`
  - `src/body/flygym_runtime.py`
  - `src/body/brain_only_realistic_vision_fly.py`
  - `docs/near_term_multidrive_plan.md`
- Compared the current body interface against the original FlyGym `HybridTurningFly` controller semantics.

2. What succeeded
- Confirmed that the current strongest branch is still compressing all descending activity into only:
  - `left_drive`
  - `right_drive`
- Confirmed that this remains the largest structural mismatch to fuller embodiment:
  - the controller underneath already has richer internal state
  - but the repo still addresses it through a two-scalar throttle-like interface
- Confirmed that the most plausible near-term fix is still the one already outlined in:
  - `docs/near_term_multidrive_plan.md`
  - namely a hybrid motor-latent interface that modulates:
    - left/right CPG amplitude
    - left/right CPG frequency
    - correction-rule gains
    - reverse gating

3. What failed
- No new embodied claim is made in this checkpoint.
- This entry is only the start of the motor-interface expansion.

4. Evidence paths
- `docs/near_term_multidrive_plan.md`
- `src/bridge/decoder.py`
- `src/body/interfaces.py`
- `src/body/flygym_runtime.py`
- `src/body/brain_only_realistic_vision_fly.py`

5. Next actions
- Implement a richer command dataclass and a FlyGym-side controller that accepts motor latents rather than only two descending drives.
- Keep the visual splice fixed.
- Revalidate against matched `target`, `no_target`, and `zero_brain` controls.

## 2026-03-11 - T086 and T087 completed with the first hybrid motor-latent branch

1. What I attempted
- Implemented a richer controller-facing motor interface instead of the current two-drive bottleneck.
- Added matched embodied `target`, `no_target`, and `zero_brain` runs for the new branch.
- Compared the new branch directly against the current calibrated two-drive UV-grid baseline.

2. What succeeded
- Added:
  - `src/body/connectome_turning_fly.py`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_no_target.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_zero_brain.yaml`
  - `configs/mock_multidrive.yaml`
  - `docs/multidrive_decoder_validation.md`
- Updated:
  - `src/body/interfaces.py`
  - `src/bridge/decoder.py`
  - `src/body/flygym_runtime.py`
  - `src/body/fast_realistic_vision_fly.py`
  - `src/runtime/closed_loop.py`
  - `tests/test_bridge_unit.py`
  - `tests/test_closed_loop_smoke.py`
- Local validation passed:
  - `python -m pytest tests/test_bridge_unit.py tests/test_closed_loop_smoke.py tests/test_realistic_vision_path.py -q`
  - result: `22 passed`
- Real embodied artifacts now exist for the new branch:
  - target:
    - `outputs/requested_2s_splice_uvgrid_multidrive_target/flygym-demo-20260311-115625/demo.mp4`
  - no target:
    - `outputs/requested_2s_splice_uvgrid_multidrive_no_target/flygym-demo-20260311-121158/demo.mp4`
  - zero brain:
    - `outputs/requested_2s_splice_uvgrid_multidrive_zero_brain/flygym-demo-20260311-122402/demo.mp4`
- Summary artifacts:
  - `outputs/metrics/descending_uvgrid_multidrive_visual_drive_validation.json`
  - `outputs/metrics/descending_uvgrid_multidrive_comparison.json`

3. Key result
- The hybrid motor-latent branch is real and brain-driven:
  - `zero_brain nonzero_command_cycles = 0`
  - `zero_brain net_displacement = 0.016680726595983866`
- But the first calibration does not beat the current calibrated two-drive UV-grid branch overall.

Target-run comparison versus the current best two-drive branch:
- `avg_forward_speed`: `4.9241 -> 4.4153`
- `net_displacement`: `5.7583 -> 5.5463`
- `corr_drive_diff_vs_target_bearing`: `0.8810 -> 0.8481`
- `steer_sign_match_rate`: `0.8878 -> 0.9031`

So the new branch slightly improves steering sign match, but regresses on the broader target-run metrics.

4. Main failure mode
- The first motor-latent calibration strengthens no-target locomotion too much:
  - calibrated two-drive no-target `avg_forward_speed = 3.9070`
  - hybrid motor-latent no-target `avg_forward_speed = 4.6506`
- That means the richer controller is currently amplifying generic visually driven locomotion more than target-conditioned pursuit.

5. Honest conclusion
- The new branch is more plausible at the controller interface:
  - it modulates CPG amplitude
  - CPG frequency
  - correction gains
  - reverse gating
- But it is not yet the strongest embodied branch.
- The current production reference therefore stays:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated.yaml`
- The new hybrid motor-latent branch stays experimental until it is calibrated to improve target-vs-no-target modulation.

6. Next actions
- Calibrate the hybrid motor-latent branch specifically for:
  - stronger target-vs-no-target modulation
  - lower generic no-target drive
  - preserved or improved target-bearing steering correlation

## 2026-03-11 - Follow-up artifact review refined the multidrive interpretation

1. What I rechecked
- Re-read the matched multidrive target and no-target logs after visual review of the videos:
  - `outputs/requested_2s_splice_uvgrid_multidrive_target/flygym-demo-20260311-115625/run.jsonl`
  - `outputs/requested_2s_splice_uvgrid_multidrive_no_target/flygym-demo-20260311-121158/run.jsonl`
- Compared target-conditioned phases against no-target phases rather than relying only on whole-run averages.

2. What I found
- The user's qualitative read is supported by the logs.
- In the target run, when the target is frontal:
  - mean total drive is higher
  - mean forward speed is much higher
- When the target moves peripheral:
  - mean total drive drops
  - steering asymmetry rises
  - forward speed falls
- Concrete target-run conditioned numbers:
  - `abs(target_bearing) < 0.5`:
    - mean total drive `0.6257`
    - mean abs drive diff `0.1366`
    - mean forward speed `6.4098`
  - `abs(target_bearing) >= 0.5`:
    - mean total drive `0.4216`
    - mean abs drive diff `0.2526`
    - mean forward speed `3.7776`
- The target run also approaches the target before losing it:
  - start distance `9.99`
  - minimum distance `6.31`
  - end distance `11.50`

3. Revised interpretation
- The multidrive branch is likely doing something more specific than the previous aggregate metrics suggested:
  - approach when the target is frontal
  - then suppress forward progression and attempt to reorient when the target goes peripheral
- The likely remaining failure is not "no pursuit-like behavior".
- It is more specifically:
  - insufficient turn authority
  - or ineffective turn execution in the current controller/body mapping

4. Consequence for next work
- `T089` should now focus on:
  - stronger turn execution
  - less ineffective stop-turn behavior
  - preserving the approach phase
- Not on abandoning the multidrive path.

## 2026-03-11 - T090 documented the neck-output mapping strategy and reset the next phase

1. What I recorded
- Added a new explicit strategy document:
  - `docs/neck_output_mapping_strategy.md`
- Updated:
  - `TASKS.md`
  - `PROGRESS_LOG.md`

2. What that document preserves
- The current strongest branch is still the calibrated UV-grid two-drive branch.
- The first hybrid motor-latent branch is more plausible but not yet stronger overall.
- The main remaining bottleneck is now the *output semantics*:
  - broad descending / neck outputs
  - into controller/body action
- The correct near-term target is now an explicit **neck-output motor basis**.

3. What the doc makes explicit
- We should stop hand-authoring more and more tiny output subsets.
- We should first monitor a broad public descending/efferent population during embodied runs.
- Then build:
  - an observational atlas
  - a causal motor-response atlas
  - a fitted motor basis
- Only after that should we revisit calibrated body feedback into the brain.

4. Why this matters
- Conversation compaction is expected.
- This repo now has an explicit record that the next phase is not:
  - "just tune turn gain"
- It is:
  - "derive a broader, data-driven neck-output mapping layer"

5. Next actions
- `T091`: add monitoring-only support for a broad descending/efferent population
- `T092`: summarize the first observational neck-output atlas
- `T093`: build the first causal descending motor-response atlas

## 2026-03-11 - T091 and T092 completed: broad descending monitoring and first observational atlas

1. What I added
- Monitoring-only support for a broad descending/efferent population in the
  current strongest embodied branch:
  - `src/bridge/decoder.py`
- New monitored configs:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_monitored.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_monitored_no_target.yaml`
- New summarizer:
  - `scripts/summarize_descending_monitoring.py`
- New docs:
  - `docs/descending_monitoring_atlas.md`

2. Validation
- Ran:
  - `python -m pytest tests/test_bridge_unit.py tests/test_closed_loop_smoke.py -q`
  - `python -m py_compile src/bridge/decoder.py scripts/summarize_descending_monitoring.py`
- Result:
  - `18 passed`

3. Embodied monitored runs
- Target + monitored:
  - `outputs/requested_2s_splice_uvgrid_calibrated_monitored_target/flygym-demo-20260311-134126/run.jsonl`
- No target + monitored:
  - `outputs/requested_2s_splice_uvgrid_calibrated_monitored_no_target/flygym-demo-20260311-135635/run.jsonl`

4. Atlas outputs
- `outputs/metrics/descending_monitor_neck_output_atlas.csv`
- `outputs/metrics/descending_monitor_neck_output_atlas.json`

5. Main findings
- The current branch uses a distributed descending code, not one "pursuit neuron".
- Strongest current forward/frontal candidates:
  - `DNg97`
  - `DNp103`
  - `DNp18`
- Strongest current turn-sensitive candidates:
  - `DNp71`
  - `DNpe040`
  - `DNpe056`
- Strongest current target-conditioned weak-gate candidates:
  - `DNpe016`
  - `DNae002`

6. Consequence
- `T091` and `T092` are complete.
- The next correct step became `T093`: direct causal perturbation of those
  descending groups in the embodied stack.

## 2026-03-11 - T093 completed, then recovered after a local power outage

1. What happened
- I built and validated the first causal descending motor-response atlas tooling:
  - `scripts/run_descending_motor_atlas.py`
  - `tests/test_descending_motor_atlas.py`
- I ran a local mock smoke atlas.
- I then ran the real WSL embodied atlas and generated the first summary
  artifacts.
- After that, the local PC suffered a power outage and crashed.
- On recovery, I checked the repo state, verified that the atlas artifacts were
  still present on disk, and resumed from those surviving outputs instead of
  rerunning blindly.

2. Recovery evidence
- Surviving raw atlas:
  - `outputs/metrics/descending_motor_atlas.json`
  - `outputs/metrics/descending_motor_atlas.csv`
- Surviving summary:
  - `outputs/metrics/descending_motor_atlas_summary.json`
  - `outputs/metrics/descending_motor_atlas_summary.csv`

3. What I changed after recovery
- Expanded the atlas script so it now includes:
  - a true no-stimulation baseline row
  - the target-conditioned observational candidates:
    - `DNpe016`
    - `DNae002`
    - `DNpe031`
- Added:
  - `scripts/summarize_descending_motor_atlas.py`
  - `docs/descending_motor_atlas.md`
- Updated:
  - `docs/neck_output_mapping_strategy.md`
  - `docs/descending_monitoring_atlas.md`
  - `docs/visual_splice_strategy.md`
  - `docs/cold_start_visual_brain_plan.md`

4. Validation
- Ran:
  - `python -m pytest tests/test_descending_motor_atlas.py tests/test_bridge_unit.py -q`
  - `python -m py_compile scripts/run_descending_motor_atlas.py scripts/summarize_descending_motor_atlas.py`
- Result:
  - `12 passed`

5. Main causal findings
- Baseline is not zero-motion:
  - over `0.1 s`, the body still passively settles with
    - `net_displacement = 0.0482`
    - `avg_forward_speed = 1.8788`
    - `mean_total_drive = 0.0`
- Strongest bilateral forward drivers above baseline:
  - `DNp103`
    - `delta_net_displacement_vs_baseline = +0.2971`
    - `delta_avg_forward_speed_vs_baseline = +3.9664`
  - `DNp18`
    - `+0.2844`
    - `+3.7944`
  - `DNg97`
    - `+0.2820`
    - `+3.7865`
- Strongest mirrored turn driver:
  - `DNpe040`
    - left `delta_end_yaw_vs_baseline = -0.0254`
    - right `delta_end_yaw_vs_baseline = +0.0122`
- Secondary mirrored turn candidate:
  - `DNpe056`
    - left `-0.0099`
    - right `+0.0033`
- Ambiguous current role:
  - `DNp71`
    - large asymmetry, but left and right perturbations do not mirror in the
      current end-yaw metric
- No useful effect in the present stack:
  - `DNpe031`
  - `DNae002`
- Weak bilateral gate-like effect:
  - `DNpe016`

6. Consequence
- `T093` is now complete.
- The next active task is now clearly `T094`:
  - fit a neck-output motor basis from the observational + causal atlas
  - then replace the current hand-authored multidrive mapping with that fitted
    basis

## 2026-03-11 - T094 started: first fitted neck-output motor basis and real pilot

1. What I added
- Basis fitter:
  - `scripts/fit_neck_output_motor_basis.py`
- Generated basis:
  - `outputs/metrics/neck_output_motor_basis.json`
- Decoder support for fitted basis files:
  - `src/bridge/decoder.py`
- New fitted-basis configs:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_no_target.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_zero_brain.yaml`
- New doc:
  - `docs/neck_output_motor_basis.md`

2. Validation
- Ran:
  - `python -m pytest tests/test_descending_motor_atlas.py tests/test_bridge_unit.py -q`
  - `python -m py_compile scripts/fit_neck_output_motor_basis.py`
- Result:
  - `13 passed`

3. Fitted basis produced
- Forward weights:
  - `DNp103 = 1.0`
  - `DNp18 = 0.9501`
  - `DNg97 = 0.9483`
  - `DNpe016 = 0.1553`
- Turn weights:
  - `DNpe040 = 1.0`
  - `DNpe056 = 0.3910`
- Explicit exclusions for now:
  - ambiguous turn role:
    - `DNp71`
  - inactive in first causal pass:
    - `DNpe031`
    - `DNae002`

4. Smoke and first real pilot
- Local mock smoke completed:
  - `outputs/requested_0p05s_multidrive_fitted_basis_mock/mock-demo-20260311-145811`
- Real WSL `0.1 s` target pilot completed:
  - `outputs/requested_0p1s_splice_uvgrid_multidrive_fitted_basis_target/demos/flygym-demo-20260311-145836.mp4`
  - `outputs/requested_0p1s_splice_uvgrid_multidrive_fitted_basis_target/metrics/flygym-demo-20260311-145836.csv`
  - `outputs/benchmarks/fullstack_splice_uvgrid_multidrive_fitted_basis_target_0p1s.csv`

5. Preliminary result
- Old hand-authored multidrive `0.1 s` target pilot:
  - `net_displacement = 0.0584`
  - `displacement_efficiency = 0.1919`
  - `avg_forward_speed = 3.1059`
- New fitted-basis multidrive `0.1 s` target pilot:
  - `net_displacement = 0.0802`
  - `displacement_efficiency = 0.3202`
  - `avg_forward_speed = 2.5563`

6. Interpretation
- The fitted basis is changing the character of the motion in a plausible way:
  - less raw forward speed
  - more net displacement
  - better displacement efficiency in the short pilot
- That is not enough to declare it better yet.
- The remaining gate for `T094` is still matched:
  - longer-window `target`
  - longer-window `no_target`
  - longer-window `zero_brain`

## 2026-03-11 - T094 extended to matched `0.1 s` fitted-basis pilots after recovery

1. What I ran
- Real WSL no-target pilot:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_no_target.yaml`
- Real WSL zero-brain pilot:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_zero_brain.yaml`
- New summary script:
  - `scripts/summarize_fitted_basis_pilot.py`

2. New artifacts
- `outputs/benchmarks/fullstack_splice_uvgrid_multidrive_fitted_basis_no_target_0p1s.csv`
- `outputs/benchmarks/fullstack_splice_uvgrid_multidrive_fitted_basis_zero_brain_0p1s.csv`
- `outputs/requested_0p1s_splice_uvgrid_multidrive_fitted_basis_no_target/demos/flygym-demo-20260311-150139.mp4`
- `outputs/requested_0p1s_splice_uvgrid_multidrive_fitted_basis_zero_brain/demos/flygym-demo-20260311-150253.mp4`
- `outputs/metrics/neck_output_motor_basis_pilot_summary.json`

3. Matched `0.1 s` result
- target:
  - `net_displacement = 0.0802`
  - `avg_forward_speed = 2.5563`
  - `displacement_efficiency = 0.3202`
- no target:
  - `net_displacement = 0.0770`
  - `avg_forward_speed = 2.2348`
  - `displacement_efficiency = 0.3518`
- zero brain:
  - `net_displacement = 0.0343`
  - `avg_forward_speed = 1.8578`
  - `displacement_efficiency = 0.1883`

4. Interpretation
- The fitted-basis branch is still brain-driven over the short pilot:
  - target minus zero-brain net displacement `= +0.0459`
  - target minus zero-brain forward speed `= +0.6985`
- But target-vs-no-target separation is still weak at `0.1 s`:
  - target minus no-target net displacement `= +0.0032`
  - target minus no-target forward speed `= +0.3215`
  - target minus no-target displacement efficiency `= -0.0316`

5. Consequence
- `T094` remains `doing`, not `done`.
- The next clean step is longer-window matched validation for the fitted-basis
  branch before replacing the current hand-authored multidrive path.

## 2026-03-11 - Longer-window `1.0 s` fitted-basis validation completed

1. What I ran
- Real WSL fitted-basis `1.0 s` target run:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis.yaml`
- Real WSL fitted-basis `1.0 s` no-target run:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_no_target.yaml`
- Real WSL fitted-basis `1.0 s` zero-brain run:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_zero_brain.yaml`

2. Main artifacts
- target:
  - `outputs/requested_1s_splice_uvgrid_multidrive_fitted_basis_target/demos/flygym-demo-20260311-150809.mp4`
- no target:
  - `outputs/requested_1s_splice_uvgrid_multidrive_fitted_basis_no_target/demos/flygym-demo-20260311-151736.mp4`
- zero brain:
  - `outputs/requested_1s_splice_uvgrid_multidrive_fitted_basis_zero_brain/demos/flygym-demo-20260311-152440.mp4`
- summary:
  - `outputs/metrics/neck_output_motor_basis_1s_summary.json`

3. `1.0 s` result
- target:
  - `avg_forward_speed = 5.4864`
  - `net_displacement = 3.8608`
  - `displacement_efficiency = 0.7051`
- no target:
  - `avg_forward_speed = 6.5676`
  - `net_displacement = 4.6747`
  - `displacement_efficiency = 0.7132`
- zero brain:
  - `avg_forward_speed = 0.6968`
  - `net_displacement = 0.0153`
  - `displacement_efficiency = 0.0219`

4. Interpretation
- The fitted-basis branch is still clearly brain-driven over `1.0 s`:
  - target minus zero-brain net displacement `= +3.8455`
  - target minus zero-brain forward speed `= +4.7897`
- But it is still not target-conditioned in the way we need:
  - target minus no-target net displacement `= -0.8140`
  - target minus no-target forward speed `= -1.0812`
  - target minus no-target displacement efficiency `= -0.0081`

5. Consequence
- `T094` remains active but cannot be closed.
- Added `T095` as the next output-side refinement task:
  - use the new atlas evidence to improve target-conditioned behavior over
    no-target locomotion
  - likely by revisiting:
    - `DNpe016`
    - `DNp71`
    - and the mapping from the fitted basis into the controller latents

## 2026-03-11 - Target-tracking evaluation gap noted; rerunning a `2.0 s` fitted-basis target demo

1. Correction
- The user pointed out a real evaluation gap:
  - aggregate locomotion metrics alone are not sufficient
  - they can miss pursuit-like structure such as:
    - approach while the target is frontal
    - slowing or stopping while attempting to reacquire the target
    - partial turn attempts that look meaningful in the video but weak in scalar summaries

2. Consequence
- Added `T096` so the repo explicitly tracks this as an evaluation requirement.
- This means the fitted-basis branch should not be judged only by:
  - net displacement
  - average forward speed
  - displacement efficiency
- It also needs explicit target-tracking review.

3. Immediate action
- Rerun the fitted-basis target demo at `2.0 s`:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis.yaml`
- Save the video/log/metrics artifacts for scene-level review before making the next decoder/basis change.

4. Result
- The `2.0 s` fitted-basis target rerun completed successfully and produced:
  - video:
    - `outputs/requested_2s_splice_uvgrid_multidrive_fitted_basis_target/demos/flygym-demo-20260311-153237.mp4`
  - log:
    - `outputs/requested_2s_splice_uvgrid_multidrive_fitted_basis_target/logs/flygym-demo-20260311-153237.jsonl`
  - metrics:
    - `outputs/requested_2s_splice_uvgrid_multidrive_fitted_basis_target/metrics/flygym-demo-20260311-153237.csv`
  - benchmark row:
    - `outputs/benchmarks/fullstack_splice_uvgrid_multidrive_fitted_basis_target_2s.csv`

5. Headline numbers
- `sim_seconds = 2.0`
- `avg_forward_speed = 4.8866`
- `net_displacement = 6.1516`
- `displacement_efficiency = 0.6301`
- `real_time_factor = 0.002286`

6. Next use
- This rerun exists primarily for explicit scene-level target-tracking review, not
  only scalar comparison.

## 2026-03-11 - Started longer-window fitted-basis validation after the recovered `0.1 s` pilots

1. Why this next step is necessary
- The recovered matched `0.1 s` pilots established that the fitted-basis branch
  is still brain-driven.
- They did **not** establish strong target-vs-no-target separation.
- So the correct next gate is a longer-window matched run, not another decoder
  rewrite yet.

2. Active plan
- Run the fitted-basis branch sequentially in real WSL for:
  - `target`
  - `no_target`
  - `zero_brain`
- Use `1.0 s` simulated duration as the first longer-window checkpoint.

3. Why `1.0 s`
- It is materially longer than the current `0.1 s` pilots.
- It is still short enough to complete on this machine without turning into a
  many-hour branch sweep.
- It should be long enough for target-conditioned approach vs reorientation
  structure to separate more clearly if the fitted basis is actually helping.

## 2026-03-11 - Wrote a cold-start context handoff for clean-session recovery

1. What I attempted
- Wrote a repo-root `context.md` intended for a fresh Codex session with no
  prior chat history.
- The goal was to preserve the current understanding of the repo, the public
  science basis, the neuron-mapping boundary, the current best production
  branch, and the active unresolved gaps.

2. What succeeded
- Added `context.md` with an explicit cold-start reading order.
- Captured the project mission, upstream repos, paper context, architecture,
  public neuron anchors, visual splice evolution, descending readout findings,
  current best calibrated UV-grid branch, performance reality, active tracker
  state, and recommended future sub-agent decomposition.
- Logged the handoff in `TASKS.md` as `T097`.

3. What failed
- Nothing substantive failed. The only practical issue was that the initial
  attempt was too large for a single patch, so the document was added in smaller
  sections instead.

4. Evidence paths
- `context.md`
- `TASKS.md`
- `PROGRESS_LOG.md`

5. Why this matters
- The repo has accumulated enough architectural and scientific state that a
  clean session would otherwise waste time reconstructing known facts.
- This handoff should let the next session start from the current real
  bottlenecks: visual splice semantics and output decoding quality.

## 2026-03-12 - Started contextual fitted-basis refinement for target-conditioned gating and stronger peripheral reorientation

1. What I attempted
- Continued `T095` and `T096` from the current fitted-basis branch instead of reopening install or splice work.
- Used bounded parallel analysis only on docs, logs, and metrics to confirm the current failure shape before editing code.
- Implemented a new experimental contextual decoder path that uses:
  - `DNpe016` as a forward-context gate
  - `DNp71` as a turn-context boost
  - new turn-priority latent asymmetry gains for low-forward, high-turn states
- Created a separate config family rather than mutating the current fitted-basis baseline.

2. What succeeded
- Confirmed the current qualitative failure mode from the existing evidence:
  - the branch can approach while the target is frontal
  - when the target goes peripheral, total drive falls and turn asymmetry rises
  - but the resulting turn execution is still too weak to recover the target cleanly
- Added decoder support for turn-priority motor-latent asymmetry gains in `src/bridge/decoder.py`.
- Preserved and used the existing context hooks (`forward_context_*`, `turn_context_*`) for the first explicit contextual fitted-basis refinement.
- Added unit coverage for:
  - forward gating from context populations
  - stronger hybrid turn execution from the new turn-priority path
- Added new experimental configs:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual_no_target.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual_zero_brain.yaml`
  - `configs/mock_multidrive_fitted_basis_contextual.yaml`
- Validation passed:
  - `python -m py_compile src/bridge/decoder.py`
  - `python -m pytest tests/test_bridge_unit.py tests/test_closed_loop_smoke.py -q`
  - result: `24 passed`
- The dedicated mock smoke run completed and produced artifacts:
  - `outputs/requested_0p2s_mock_multidrive_fitted_basis_contextual/mock-demo-20260312-004708/demo.mp4`
  - `outputs/requested_0p2s_mock_multidrive_fitted_basis_contextual/mock-demo-20260312-004708/run.jsonl`
  - `outputs/requested_0p2s_mock_multidrive_fitted_basis_contextual/mock-demo-20260312-004708/metrics.csv`

3. What failed
- The production FlyGym contextual config does not boot under `mode = mock` with the UV-grid splice still enabled, because the mock body does not expose `realistic_vision_splice_cache`.
- That was handled by creating a dedicated mock smoke config instead of pretending the production embodied config should run on the mock body.
- `pytest` still emits the known Windows temp-directory cleanup warning on exit, but the actual test run passes.

4. Evidence paths
- `src/bridge/decoder.py`
- `tests/test_bridge_unit.py`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual_no_target.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual_zero_brain.yaml`
- `configs/mock_multidrive_fitted_basis_contextual.yaml`
- `outputs/requested_0p2s_mock_multidrive_fitted_basis_contextual/mock-demo-20260312-004708/run.jsonl`
- `outputs/requested_0p2s_mock_multidrive_fitted_basis_contextual/mock-demo-20260312-004708/metrics.csv`

5. Next actions
- Run the new contextual fitted-basis branch in real WSL for matched:
  - `target`
  - `no_target`
  - `zero_brain`
- Keep those embodied runs serialized so local compute paths do not contend.
- Judge the new branch on both:
  - scalar metrics
  - explicit scene-level target-tracking review
- If the contextual branch still fails, the next output-side lever remains the same family:
  - stronger target-conditioned gating
  - stronger effective turn execution
  - not a return to prosthetic brain-context hacks.
## 2026-03-12 - Contextual fitted-basis validation deferred to preserve serialized heavy runtime use

1. What I attempted
- Reviewed the active embodied output bottleneck with local code/artifact reads and independent read-only Codex sub-agents.
- Confirmed that the current repo already has a contextual fitted-basis refinement branch under the `contextual` config family.
- Verified that the contextual branch is wired through the decoder and covered by a mock-path smoke config and unit tests.

2. What succeeded
- Re-aligned this session to the repo's current output-side refinement branch instead of creating a parallel duplicate.
- Added a clean regression check in `tests/test_closed_loop_smoke.py` that asserts the contextual fitted-basis config really wires `DNpe016`, `DNp71`, and the turn-priority latent gains into the decoder.
- Re-ran focused validation:
  - `python -m pytest tests/test_bridge_unit.py tests/test_closed_loop_smoke.py -q`
  - result: `22 passed`

3. What failed or was blocked
- A separate long embodied WSL benchmark was already active on the machine when this session reached the next real validation step.
- To obey the serialized-heavy-compute rule, I did not continue with an overlapping contextual WSL pilot.

4. Evidence paths
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual_no_target.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual_zero_brain.yaml`
- `configs/mock_multidrive_fitted_basis_contextual.yaml`
- `tests/test_closed_loop_smoke.py`
- `docs/neck_output_motor_basis.md`

5. Next actions
- Wait for the currently running background WSL embodied job to clear.
- Then run serialized matched contextual pilots for:
  - `target`
  - `no_target`
  - `zero_brain`
- Judge the contextual branch using both scalar metrics and explicit scene-level target-tracking review before deciding whether it beats the current fitted-basis branch.

## 2026-03-12 - Validated the contextual fitted-basis branch locally and kept WSL heavy runs serialized

1. What I attempted
- Re-read the live decoder/runtime/test state and confirmed that the repo already contains a contextual fitted-basis branch using:
  - `DNpe016` as a forward context gate
  - `DNp71` as a turn-context boost
  - turn-priority latent asymmetry gains in the hybrid multidrive decoder
- Validated that branch locally with targeted compile/test checks.
- Ran a dedicated local mock smoke run for the contextual config.
- Verified the WSL `flysim-full` micromamba env and the core embodied imports.
- Tried to start a short real WSL contextual target pilot, then stopped treating it as the active next step after discovering an already-running heavy contextual `no_target` WSL job.

2. What succeeded
- Local validation passed:
  - `python -m py_compile src/bridge/decoder.py scripts/fit_neck_output_motor_basis.py src/runtime/closed_loop.py src/body/flygym_runtime.py`
  - `python -m pytest tests/test_bridge_unit.py tests/test_closed_loop_smoke.py -q`
  - result: `24 passed`
- The contextual mock smoke run completed and wrote artifacts:
  - `outputs/requested_0p2s_multidrive_fitted_basis_contextual_smoke/mock-demo-20260312-004945/demo.mp4`
  - `outputs/requested_0p2s_multidrive_fitted_basis_contextual_smoke/mock-demo-20260312-004945/run.jsonl`
  - `outputs/requested_0p2s_multidrive_fitted_basis_contextual_smoke/mock-demo-20260312-004945/metrics.csv`
- The WSL full-stack env exists and imports cleanly:
  - `wsl --cd /mnt/g/flysim /root/.local/bin/micromamba run -n flysim-full python -c "import numpy"`
  - `wsl --cd /mnt/g/flysim /root/.local/bin/micromamba run -n flysim-full python -c "import sys; sys.path.append('src'); from body.flygym_runtime import FlyGymRealisticVisionRuntime"`

3. What failed or was intentionally stopped
- A short real WSL contextual target pilot was started under:
  - `outputs/requested_0p2s_splice_uvgrid_multidrive_fitted_basis_contextual_target/flygym-demo-20260312-005136/run.jsonl`
- That pilot was not allowed to continue as the active heavy task because `wsl pgrep -af` showed an already-running contextual `no_target` FlyGym job on this machine:
  - config: `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_context_gate_no_target.yaml`
  - output root: `outputs/requested_0p2s_splice_uvgrid_multidrive_fitted_basis_context_gate_no_target`
- To respect the explicit no-concurrent-heavy-runs requirement, the newly launched target pilot was terminated after its first logged rows rather than competing with the existing WSL run.

4. Evidence paths
- `src/bridge/decoder.py`
- `tests/test_bridge_unit.py`
- `tests/test_closed_loop_smoke.py`
- `configs/mock_multidrive_fitted_basis_contextual.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual.yaml`
- `outputs/requested_0p2s_multidrive_fitted_basis_contextual_smoke/mock-demo-20260312-004945/run.jsonl`
- `outputs/requested_0p2s_multidrive_fitted_basis_contextual_smoke/mock-demo-20260312-004945/metrics.csv`
- `outputs/requested_0p2s_splice_uvgrid_multidrive_fitted_basis_contextual_target/flygym-demo-20260312-005136/run.jsonl`
- `TASKS.md`

5. Next actions
- Do not launch another heavy WSL embodied run until the existing contextual `no_target` job has finished or been explicitly triaged.
- Inspect that active `no_target` artifact first.
- Then run the contextual `target` and `zero_brain` pilots strictly one-at-a-time.
- Keep judging the branch on both:
  - scalar metrics
  - explicit scene-level target-tracking review

## 2026-03-12 - Ran the first serialized real `0.2 s` context-gate pilots and revalidated the merged output branch

1. What I attempted
- Kept the heavy embodied work strictly serialized.
- Ran two real WSL `0.2 s` FlyGym pilots for the simpler context-gate scaffold:
  - `target`
  - `no_target`
- Re-ran the local decoder/runtime smoke suite after the sub-agent edits landed so the merged worktree had a fresh validation result.

2. What succeeded
- The merged local validation now passes:
  - `python -m pytest tests/test_bridge_unit.py tests/test_closed_loop_smoke.py -q`
  - result: `24 passed`
- Syntax checks passed:
  - `python -m py_compile src/bridge/decoder.py src/runtime/closed_loop.py src/body/flygym_runtime.py scripts/fit_neck_output_motor_basis.py`
- The serialized real WSL `target` pilot completed:
  - `outputs/requested_0p2s_splice_uvgrid_multidrive_fitted_basis_context_gate_target/flygym-demo-20260312-004336/run.jsonl`
  - `outputs/requested_0p2s_splice_uvgrid_multidrive_fitted_basis_context_gate_target/flygym-demo-20260312-004336/metrics.csv`
- The serialized real WSL `no_target` pilot completed:
  - `outputs/requested_0p2s_splice_uvgrid_multidrive_fitted_basis_context_gate_no_target/flygym-demo-20260312-004902/run.jsonl`
  - `outputs/requested_0p2s_splice_uvgrid_multidrive_fitted_basis_context_gate_no_target/flygym-demo-20260312-004902/metrics.csv`

3. Preliminary result
- `target`:
  - `avg_forward_speed = 1.8433`
  - `net_displacement = 0.0964`
  - `displacement_efficiency = 0.2643`
- `no_target`:
  - `avg_forward_speed = 1.8681`
  - `net_displacement = 0.0912`
  - `displacement_efficiency = 0.2467`

Interpretation:

- the simpler context-gate scaffold does not yet create strong target-vs-no-target separation,
- but it does show a small target advantage on net displacement and displacement efficiency,
- so the output-side context idea remains plausible rather than being immediately falsified.

4. What failed or remains open
- The result is still too weak to promote.
- These pilots were run on the simpler `context_gate` scaffold, not the fuller `contextual` branch with turn-priority latent gains.
- So the actual next gate remains the matched real WSL validation of:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual_no_target.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual_zero_brain.yaml`

5. Notes
- The pytest run still emitted the same Windows temp-cleanup `PermissionError` on exit, but the actual test run succeeded.
- No overlapping heavy WSL jobs were run during this pass.

6. Next actions
- Use the `contextual` branch, not the simpler `context_gate` scaffold, for the next serialized real WSL trio.
- Run `target`, `no_target`, and `zero_brain` one-at-a-time.
- After those finish, compare:
  - scalar metrics
  - scene-level target-tracking behavior
  - and whether the contextual branch now beats the plain fitted-basis branch on target-vs-no-target separation.

## 2026-03-12 - Reassigned the contextual decoder using completed atlases plus primary descending-control literature

1. What I attempted
- Re-check the contextual branch against the completed monitored embodied atlas and the short causal descending motor atlas instead of relying on aborted contextual partial runs.
- Dispatch a literature-focused sub-agent and independently review primary sources on descending steering, locomotor modulation, and walking-linked versus flight-linked descending neurons.
- Convert that evidence into a decoder/config refinement before launching another serialized WSL embodied run.

2. What succeeded
- The literature review converged on a strong constraint: keep direct steering on canonical lateralized descending neurons such as `DNa01` / `DNa02`, and treat other candidate descending groups as gain/modulatory channels unless they have stronger walking-steering support.
- The local atlas evidence and literature together supported this new split:
  - `DNae002` plus `DNpe016` as target-conditioned forward/context gates,
  - `DNpe040` plus `DNpe056` as exploratory turn-support context channels,
  - `DNa01` / `DNa02` retained as the direct steering core.
- Implemented a new decoder option `turn_context_mode = aligned_asymmetry` in `src/bridge/decoder.py`.
- Rewired the contextual configs so turn support now boosts only when the contextual left-right asymmetry agrees with the turn direction already selected by the canonical steering readout.
- Updated local coverage:
  - `tests/test_bridge_unit.py`
  - `tests/test_closed_loop_smoke.py`
- Updated the current branch rationale in `docs/neck_output_motor_basis.md`.

3. What failed
- The earlier contextual partial WSL logs were not reliable evidence for decoder-observable activity because they ended before the relevant outputs were emitted.
- No real WSL embodied validation was launched in this step, by design, to avoid overlapping heavy tasks before the refined branch was ready.

4. Evidence
- Empirical repo evidence:
  - `outputs/metrics/descending_early_activity.csv`
  - `outputs/metrics/descending_monitor_neck_output_atlas.csv`
  - `outputs/metrics/descending_motor_atlas_summary.json`
  - `outputs/metrics/neck_output_motor_basis.json`
- Primary sources:
  - Rayshubskiy et al., eLife 2025, steering DNs: `https://elifesciences.org/articles/102230`
  - Braun et al., Cell 2024, fine-grained walking steering: `https://pmc.ncbi.nlm.nih.gov/articles/PMC12778575/`
  - Westeinde et al., Nature 2024, steering command vs gain control: `https://www.nature.com/articles/s41586-024-07039-2`
  - Schlegel et al., Nature 2024, descending networks and population motor control: `https://www.nature.com/articles/s41586-024-07523-9`
  - Lappalainen et al., Nature 2024, walking-linked `oDN1` / `DNg97`: `https://www.nature.com/articles/s41586-024-07939-3`
  - Ache et al., Nature 2019, visually elicited flight turns and `DNb01`: `https://www.nature.com/articles/s41586-019-1677-2`

5. Files changed
- `src/bridge/decoder.py`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual_no_target.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual_zero_brain.yaml`
- `configs/mock_multidrive_fitted_basis_contextual.yaml`
- `tests/test_bridge_unit.py`
- `tests/test_closed_loop_smoke.py`
- `docs/neck_output_motor_basis.md`
- `TASKS.md`

6. Next actions
- Run local validation on the updated decoder/config branch.
- If local validation passes, start the real WSL contextual `target` pilot first and keep the `no_target` and `zero_brain` pilots strictly serialized after it.
- Compare the refined contextual branch against the current fitted-basis and calibrated two-drive baselines on both scalar metrics and scene-level target-tracking.

## 2026-03-12 - Replaced the suppressive forward gate with an additive context boost and reran serialized embodied pilots

1. What I attempted
- Validate the first literature-informed contextual patch locally.
- Run a short real WSL `target` pilot on that patch.
- After observing locomotor suppression, change the forward context mechanism from multiplicative gate to additive boost and rerun serialized `target` / `no_target` pilots.

2. What succeeded
- Local validation passed twice as the branch evolved:
  - first after the asymmetry-aligned context patch: `25 passed`
  - then after adding the forward-context boost path: `26 passed`
- The first contextual `target` / `no_target` pair on the multiplicative forward gate showed a clear failure mode:
  - target: `avg_forward_speed 1.5598`, `net_displacement 0.0572`, `displacement_efficiency 0.1852`
  - no_target: `avg_forward_speed 1.7889`, `net_displacement 0.0988`, `displacement_efficiency 0.2791`
- Diagnosis from the logs showed the target-biased context signal existed but the multiplicative gate was suppressing both conditions too strongly relative to the modest target-vs-no-target separation.
- I then added `forward_context_mode = boost` plus `forward_context_boost` in `src/bridge/decoder.py`, rewired the contextual configs, and added unit coverage.
- The boosted target rerun recovered motion substantially:
  - boosted target: `avg_forward_speed 2.7756`, `net_displacement 0.1621`, `displacement_efficiency 0.2950`
- I then ran the matched boosted `no_target` pilot, still strictly serialized:
  - boosted no_target: `avg_forward_speed 2.9413`, `net_displacement 0.1811`, `displacement_efficiency 0.3109`

3. What failed
- The additive boost fixed the locomotor-collapse problem but did not fix target selectivity.
- In the live boosted pair, the supposedly target-conditioned forward context family was not actually target-selective:
  - `DNae002` bilateral mean was higher in boosted `no_target` than in boosted `target`
  - `DNpe016` remained silent in both boosted runs
- Because the branch is still not beating matched `no_target`, I did not spend another heavy pass on `zero_brain` for this specific refinement.

4. Evidence
- Multiplicative-gate pilots:
  - `outputs/requested_0p2s_splice_uvgrid_multidrive_fitted_basis_contextual_target_refined/metrics/flygym-demo-20260312-112938.csv`
  - `outputs/requested_0p2s_splice_uvgrid_multidrive_fitted_basis_contextual_no_target_refined/metrics/flygym-demo-20260312-113221.csv`
- Additive-boost pilots:
  - `outputs/requested_0p2s_splice_uvgrid_multidrive_fitted_basis_contextual_target_boosted/metrics/flygym-demo-20260312-113644.csv`
  - `outputs/requested_0p2s_splice_uvgrid_multidrive_fitted_basis_contextual_no_target_boosted/metrics/flygym-demo-20260312-113859.csv`
- Log-level diagnosis:
  - `outputs/requested_0p2s_splice_uvgrid_multidrive_fitted_basis_contextual_target_boosted/logs/flygym-demo-20260312-113644.jsonl`
  - `outputs/requested_0p2s_splice_uvgrid_multidrive_fitted_basis_contextual_no_target_boosted/logs/flygym-demo-20260312-113859.jsonl`

5. Files changed
- `src/bridge/decoder.py`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual_no_target.yaml`
- `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual_zero_brain.yaml`
- `configs/mock_multidrive_fitted_basis_contextual.yaml`
- `tests/test_bridge_unit.py`
- `tests/test_closed_loop_smoke.py`
- `docs/neck_output_motor_basis.md`
- `TASKS.md`

6. Next actions
- Stop assuming `DNae002` is a reliable target-conditioned forward control signal in the live embodied branch.
- Identify a genuinely target-selective signal family for the next refinement, or shift the refinement back upstream into the visual-to-steering interface rather than continuing to retune the current decoder alone.
- Keep future embodied runs serialized and evidence-first, because the current failure mode is now specific enough to avoid blind parameter sweeps.

## 2026-03-12 - Started the explicit VNC-wide workstream with public-source registry, typed graph ingest, and first pathway scaffolding

1. What I attempted
- Start the VNC-wide plan as a real repo workstream instead of leaving it as a conceptual response.
- Reuse sub-agents extensively for three parallel tracks:
  - public VNC literature/data availability
  - codebase integration seams
  - experimental design / milestone discipline
- Add actual code under `src/vnc/` for source metadata, annotation-atlas building, typed node/edge ingest, and first pathway extraction.

2. What succeeded
- Added the first VNC package and docs:
  - `src/vnc/data_sources.py`
  - `src/vnc/annotation_atlas.py`
  - `src/vnc/ingest.py`
  - `src/vnc/pathways.py`
  - `scripts/build_vnc_annotation_atlas.py`
  - `scripts/build_vnc_pathway_inventory.py`
  - `docs/vnc_data_sources.md`
  - `docs/vnc_workstream_plan.md`
  - `docs/vnc_graph_model.md`
- Added local coverage:
  - `tests/test_vnc_annotation_atlas.py`
  - `tests/test_vnc_pathways.py`
- Validation passed:
  - `python -m pytest tests/test_vnc_annotation_atlas.py tests/test_vnc_pathways.py -q` -> `4 passed`
  - `python -m py_compile src/vnc/annotation_atlas.py src/vnc/ingest.py src/vnc/pathways.py scripts/build_vnc_annotation_atlas.py scripts/build_vnc_pathway_inventory.py` -> passed
- Produced first executable VNC artifacts:
  - `outputs/metrics/vnc_annotation_atlas_mock.json`
  - `outputs/metrics/vnc_annotation_atlas_mock.csv`
  - `outputs/metrics/vnc_pathway_inventory_mock.json`
- Hardened the CSV readers against UTF-8 BOM headers after the first CLI run exposed that common export problem.

3. What the sub-agents concluded
- Experimental-design scout:
  - do not jump straight to a full muscle-level or whole-VNC dynamical reconstruction
  - keep the current best production branch as the control
  - expand via observational atlas -> causal atlas -> fitted VNC basis
- Codebase-integration scout:
  - keep VNC work in a dedicated `src/vnc/` package rather than growing `src/brain` or `bridge.decoder`
  - the long-term seam should be `brain readout -> vnc emulator -> body command`
  - the body/runtime interfaces will need richer command and state channels before a true VNC emulator can sit in the loop cleanly
- The literature/data scout is still pending, but the official-source review already anchored the first public registry around:
  - MANC
  - FANC
  - BANC

4. Official-source grounding used in this step
- MANC:
  - `https://www.janelia.org/project-team/flyem/manc-connectome`
  - `https://www.janelia.org/news/janelia-scientists-and-collaborators-unveil-fruit-fly-nerve-cord-connectome`
- FANC:
  - `https://connectomics.hms.harvard.edu/adult-drosophila-vnc-tem-dataset-female-adult-nerve-cord-fanc`
  - `https://flyconnectome.github.io/fancr/`
- BANC:
  - `https://flyconnectome.github.io/bancr/`

5. What failed or remains open
- No real MANC / FANC / BANC annotation export has been ingested yet; the first CLI artifacts are intentionally mock fixtures proving the toolchain shape.
- The literature/data scout did not finish in time for this turn, so the first real export target is still being finalized under `T104`.
- None of this yet replaces the live sparse decoder. It creates the tested scaffolding required to do that honestly.

6. Next actions
- Finalize the first real public export target under `T104`, with preference for a public MANC annotation/metadata export or a BANC Codex annotation export.
- Add `src/vnc/emulator.py` design scaffolding only after the real graph ingest target is settled.
- Keep the current embodied decoder branch and the VNC workstream separate until the VNC pathway inventory is operating on real public data instead of fixtures.

## 2026-03-12 - Added the first structural VNC spec compiler, a pluggable VNC decoder path, and a more generic runtime seam

1. What I attempted
- Reuse sub-agents again, this time for:
  - exact first public ingest targets
  - the cleanest runtime insertion seam
  - the next highest-value low-compute implementation slice
- Convert the VNC workstream from:
  - source registry
  - annotation atlas
  - pathway inventory
  into:
  - a graph-derived structural spec
  - a pluggable decoder candidate
  - a more command-agnostic closed-loop seam

2. What succeeded
- The literature/data scout came back with concrete first-ingest targets:
  - `MANC body-annotations-male-cns-v0.9-minconf-0.5.feather`
  - then `MANC body-neurotransmitters-male-cns-v0.9.feather`
  - then `MANC connectome-weights-male-cns-v0.9-minconf-0.5.feather`
  - BANC supplementary tables and Dataverse exports after that
  - FANC public SWC reconstructions as the non-gated female comparison path
- I folded those findings into:
  - `src/vnc/data_sources.py`
  - `docs/vnc_data_sources.md`
- Added a structural spec compiler:
  - `src/vnc/spec_builder.py`
  - `scripts/build_vnc_structural_spec.py`
- Added a first pluggable broad decoder candidate:
  - `src/vnc/spec_decoder.py`
  - `src/bridge/decoder_factory.py`
- Updated the runtime/body seam so future decoders are not forced to pretend they are just legacy left/right scalars:
  - `src/body/interfaces.py`
  - `src/body/mock_body.py`
  - `src/body/flygym_runtime.py`
  - `src/runtime/closed_loop.py`
- Produced the first structural-spec artifacts:
  - `outputs/metrics/vnc_structural_spec_mock.json`
  - `outputs/metrics/vnc_structural_spec_mock.csv`
- Validation passed:
  - `python -m pytest tests/test_vnc_annotation_atlas.py tests/test_vnc_pathways.py tests/test_vnc_spec_decoder.py tests/test_closed_loop_smoke.py -q` -> `16 passed`
  - `python -m py_compile src/vnc/data_sources.py src/body/interfaces.py src/body/mock_body.py src/body/flygym_runtime.py src/bridge/controller.py src/runtime/closed_loop.py src/vnc/spec_builder.py src/vnc/spec_decoder.py src/bridge/decoder_factory.py scripts/build_vnc_structural_spec.py` -> passed

3. What the sub-agents concluded
- Literature/data scout:
  - the first ungated real ingest target should be the public MANC annotation feather, not a neuPrint query path
  - BANC paper supplement / Dataverse exports are the best ungated brain+VNC follow-up
  - FANC is still valuable, but the first non-gated path is published reconstructions rather than the latest protected segmentation tooling
- Runtime seam scout:
  - the cleanest long-term seam is still `brain readout -> VNC stage -> body command`
  - the immediate blocker was not the loop itself, but command and logging assumptions that still treated everything as legacy `left_drive/right_drive`
- Experimental-design scout:
  - the right next code slice was a deterministic structural spec compiler and a testable decoder candidate, not a new embodied sweep or a new pile of heuristics in `bridge.decoder`

4. What failed or remains open
- No real public VNC export has been ingested yet; the new spec artifacts are still fixture-backed.
- The new `VNCSpecDecoder` is structural, not dynamical. It broadens the output hypothesis, but it does not yet model local VNC recurrence, motor neurons, or muscles.
- I did not launch any new heavy WSL embodied runs in this slice. That was intentional to avoid mixing architectural work with expensive evaluation before a real public graph export exists.

5. Evidence
- New code:
  - `src/vnc/spec_builder.py`
  - `src/vnc/spec_decoder.py`
  - `src/bridge/decoder_factory.py`
  - `scripts/build_vnc_structural_spec.py`
- Updated seam:
  - `src/body/interfaces.py`
  - `src/body/mock_body.py`
  - `src/body/flygym_runtime.py`
  - `src/runtime/closed_loop.py`
- New docs:
  - `docs/vnc_spec_decoder.md`
  - `docs/vnc_data_sources.md`
  - `docs/vnc_workstream_plan.md`
- New artifacts:
  - `outputs/metrics/vnc_structural_spec_mock.json`
  - `outputs/metrics/vnc_structural_spec_mock.csv`

6. Next actions
- Implement `T108`: fetch or otherwise ingest the first real public MANC annotation export locally and normalize it through the existing atlas / graph / spec toolchain.
- Only after the first real public export is in hand, compare the structural VNC decoder candidate against the current sampled/fitted output path on cheap local diagnostics.
- Keep heavy embodied WSL work serialized and deferred until the real-data ingest step is complete.

## 2026-03-12 - Added Feather support so the VNC toolchain can ingest real MANC annotation exports

1. What I attempted
- Remove the format mismatch between the real first public ingest target and the repo's current VNC tooling.
- The concrete issue was simple: the first MANC annotation target is a `.feather` file, while the VNC loaders only supported CSV / TSV / JSON.

2. What succeeded
- Added `.feather` support to:
  - `src/vnc/annotation_atlas.py`
  - `src/vnc/ingest.py`
- Added local coverage for Feather-backed atlas and graph ingest:
  - `tests/test_vnc_annotation_atlas.py`
  - `tests/test_vnc_pathways.py`
- Validation passed:
  - `python -m pytest tests/test_vnc_annotation_atlas.py tests/test_vnc_pathways.py tests/test_vnc_spec_decoder.py tests/test_closed_loop_smoke.py -q` -> `18 passed`
  - `python -m py_compile src/vnc/annotation_atlas.py src/vnc/ingest.py tests/test_vnc_annotation_atlas.py tests/test_vnc_pathways.py` -> passed

3. What failed or remains open
- This still does not fetch the real MANC file. It only removes the parser blocker.
- The remaining open step is now explicit: acquire the real public export locally and run it through the atlas / graph / structural-spec pipeline.

4. Evidence
- Loader updates:
  - `src/vnc/annotation_atlas.py`
  - `src/vnc/ingest.py`
- Coverage:
  - `tests/test_vnc_annotation_atlas.py`
  - `tests/test_vnc_pathways.py`

5. Next actions
- Keep `T108` focused on the real public annotation ingest itself rather than adding more mock-format support.

## 2026-03-12 - Downloaded and normalized the first real public MANC annotation export

1. What I attempted
- Use the official Janelia MANC download page to fetch the first real public VNC annotation export locally.
- Run the existing repo atlas/node tooling on that real file instead of on fixtures.
- Fix the schema mismatch exposed by the real data.

2. What succeeded
- Downloaded:
  - `external/vnc/manc/body-annotations-male-cns-v0.9-minconf-0.5.feather`
- Confirmed the real MANC file schema includes fields such as:
  - `bodyId`
  - `superclass`
  - `type`
  - `class`
  - `rootSide`
  - `somaSide`
  - `somaNeuromere`
- Added a shared schema-normalization layer:
  - `src/vnc/schema.py`
- Updated:
  - `src/vnc/annotation_atlas.py`
  - `src/vnc/ingest.py`
  so the repo now understands MANC-native fields and not only generic mock columns.
- Produced real public-data artifacts:
  - `outputs/metrics/vnc_annotation_atlas_manc_v0p9.json`
  - `outputs/metrics/vnc_annotation_atlas_manc_v0p9.csv`
  - `outputs/metrics/vnc_manc_annotation_node_summary.json`
- Added a dedicated evidence doc:
  - `docs/manc_annotation_ingest.md`
- Local validation still passed:
  - `python -m pytest tests/test_vnc_annotation_atlas.py tests/test_vnc_pathways.py tests/test_vnc_spec_decoder.py tests/test_closed_loop_smoke.py -q` -> `18 passed`

3. What the real data showed
- The first real public annotation file is large enough to matter:
  - `211743` rows
- After canonical normalization, the top super-classes were:
  - `interneuron` `134722`
  - `sensory` `27153`
  - `ascending` `2392`
  - `descending` `1332`
  - `motor` `933`
- The top flow categories were:
  - `intrinsic` `134884`
  - `afferent` `29545`
  - `efferent` `2265`
- A large `<missing>` bucket remains. That is real and should stay visible rather than being hidden by over-aggressive normalization.

4. What failed or remains open
- This is still annotation-only. There is no real public edge file in the pipeline yet.
- The real public pathway inventory and real public structural spec are therefore still blocked on edge ingest.
- I did not attempt the full `connectome-weights` file in this slice because the right first step was to make the annotation ingest correct and explicit first.

5. Evidence
- Real source file:
  - `external/vnc/manc/body-annotations-male-cns-v0.9-minconf-0.5.feather`
- Real artifacts:
  - `outputs/metrics/vnc_annotation_atlas_manc_v0p9.json`
  - `outputs/metrics/vnc_annotation_atlas_manc_v0p9.csv`
  - `outputs/metrics/vnc_manc_annotation_node_summary.json`
- New normalization layer:
  - `src/vnc/schema.py`

6. Next actions
- Start `T109`: acquire the first real public edge export and replace the fixture-backed pathway/spec artifacts with real public graph evidence.
- Keep heavy embodied WSL work deferred until the real graph side exists.

## 2026-03-12 - Completed the first real public MANC edge slice and real-data pathway/spec pipeline

1. What I attempted
- Continue `T109` with sub-agents and move from real annotations to the real public MANC edge file.
- Download the official `connectome-weights` feather.
- Avoid pushing the full `151,871,794`-row graph directly through the small in-memory pathway code.
- Build a filtered first-pass real locomotor slice instead.

2. What succeeded
- Downloaded the real public edge file:
  - `external/vnc/manc/connectome-weights-male-cns-v0.9-minconf-0.5.feather`
- Confirmed the real public schema is exactly:
  - `body_pre`
  - `body_post`
  - `weight`
- Added edge aliases and a filtered feather edge loader in:
  - `src/vnc/schema.py`
  - `src/vnc/ingest.py`
- Added a real MANC thoracic locomotor slice builder in:
  - `src/vnc/manc_slice.py`
- Added a real artifact CLI in:
  - `scripts/build_manc_thoracic_vnc_artifacts.py`
- Added local coverage:
  - `tests/test_vnc_manc_slice.py`
- Real artifact build succeeded and produced:
  - `outputs/metrics/manc_thoracic_slice_summary.json`
  - `outputs/metrics/manc_thoracic_pathway_inventory.json`
  - `outputs/metrics/manc_thoracic_structural_spec.json`
  - `outputs/metrics/manc_thoracic_slice_nodes.csv`
  - `outputs/metrics/manc_thoracic_slice_edges.csv`
  - `outputs/metrics/manc_thoracic_spec_overlap.json`
- Local validation passed:
  - `python -m pytest tests/test_vnc_annotation_atlas.py tests/test_vnc_pathways.py tests/test_vnc_spec_decoder.py tests/test_vnc_manc_slice.py tests/test_closed_loop_smoke.py -q` -> `20 passed`

3. What the sub-agents concluded
- The data scout confirmed the official real public edge path is the bulk MANC `connectome-weights` feather and that MANC does not publish an explicit compact edge-column schema beyond the actual file contents and related docs.
- The codebase scout confirmed the correct move was to filter early in `src/vnc/ingest.py` and keep `pathways.py` and `spec_builder.py` largely unchanged.
- The experimental-design scout confirmed the first real slice should be thoracic locomotor, not full-graph and not another tiny DN subset.

4. What the real data produced
- First real thoracic slice summary:
  - descending seeds: `1316`
  - thoracic motors: `516`
  - promoted premotor candidates: `5474`
  - selected nodes: `7291`
  - selected edges: `228061`
  - `descending -> premotor` edges: `124181`
  - `premotor -> motor` edges: `90463`
  - `descending -> motor` edges: `13417`
  - two-step paths: `2440537`
- First real structural spec:
  - `1301` descending channels
- The real overlap artifact shows that many current repo locomotor names are present in the public MANC slice with thoracic motor reachability, including:
  - `DNg97`
  - `DNp103`
  - `DNp18`
  - `DNpe056`
  - `DNpe016`
  - `DNpe040`
  - `DNp71`
  - `DNa01`
  - `DNa02`
  - `MDN`

5. What failed or remains open
- MANC still does not hand us an explicit public `premotor` label in the annotation feather, so the first real slice promotes premotor candidates by structural rule.
- I did not run embodied WSL evaluation with this real spec yet. The next honest step is slice refinement and comparison, not immediate promotion into the production embodied branch.

6. Evidence
- Real edge source:
  - `external/vnc/manc/connectome-weights-male-cns-v0.9-minconf-0.5.feather`
- New code:
  - `src/vnc/manc_slice.py`
  - `scripts/build_manc_thoracic_vnc_artifacts.py`
- New docs:
  - `docs/manc_edge_slice.md`
- New real public artifacts:
  - `outputs/metrics/manc_thoracic_slice_summary.json`
  - `outputs/metrics/manc_thoracic_pathway_inventory.json`
  - `outputs/metrics/manc_thoracic_structural_spec.json`
  - `outputs/metrics/manc_thoracic_spec_overlap.json`

7. Next actions
- Start `T110`: compare stricter thoracic slice variants before using this real spec as a production decoder candidate.
- Keep heavy embodied WSL runs serialized and deferred until the real slice rules are judged stable enough to justify them.

## 2026-03-12 - Ran the first stricter real MANC slice comparison

1. What I attempted
- Take the first real thoracic locomotor slice and check whether it survives a stricter premotor-candidate rule.
- I reused the same real-data CLI and only tightened:
  - `min_premotor_total_weight`
  - `min_premotor_motor_targets`

2. What succeeded
- Built a stricter real slice with:
  - `min_premotor_total_weight = 200`
  - `min_premotor_motor_targets = 10`
- Produced:
  - `outputs/metrics/manc_thoracic_slice_summary_strict.json`
  - `outputs/metrics/manc_thoracic_pathway_inventory_strict.json`
  - `outputs/metrics/manc_thoracic_structural_spec_strict.json`
  - `outputs/metrics/manc_thoracic_slice_nodes_strict.csv`
  - `outputs/metrics/manc_thoracic_slice_edges_strict.csv`
  - `outputs/metrics/manc_thoracic_slice_comparison.json`

3. What the comparison showed
- Baseline:
  - premotor candidates: `5474`
  - selected nodes: `7291`
  - selected edges: `228061`
  - descending structural channels: `1301`
- Stricter slice:
  - premotor candidates: `2164`
  - selected nodes: `3977`
  - selected edges: `121268`
  - descending structural channels: `1297`

4. Interpretation
- The premotor pool shrank a lot.
- The descending structural channel count barely moved.
- That is a good sign for the first real MANC structural spec: it suggests the broad descending coverage is not collapsing under a tighter premotor rule.

5. Next actions
- Move the next refinement toward biological selectivity, not just numeric thresholding.
- The best next comparison is likely a leg-biased or nerve-filtered thoracic motor slice before any embodied decoder benchmark is attempted.

## 2026-03-12 - Completed `T110` with leg-subclass and exit-nerve real MANC slice variants

1. What I attempted
- Finish the real-data refinement loop for `T110` instead of stopping at a
  looser-vs-stricter threshold comparison.
- Use sub-agents for three separate inputs:
  - local annotation / literature review for biologically selective leg-motor
    endpoints
  - code-shape review for the smallest safe extension point
  - test / docs / tracker expectations for a completed selective-slice pass
- Add selective motor-target modes to the real MANC slicer, regenerate the real
  artifacts, and compare the variants quantitatively.

2. What succeeded
- Added explicit `entry_nerve` / `exit_nerve` preservation to the normalized
  VNC node model in:
  - `src/vnc/schema.py`
  - `src/vnc/ingest.py`
- Extended the real MANC slicer in `src/vnc/manc_slice.py` with two explicit
  selective motor-target modes:
  - `leg_subclass`
  - `exit_nerve`
- Extended the real artifact CLI in
  `scripts/build_manc_thoracic_vnc_artifacts.py` so the selective modes are
  configurable and the node CSV now writes `entry_nerve` / `exit_nerve`.
- Added local coverage:
  - `tests/test_vnc_manc_slice.py`
  - `tests/test_vnc_pathways.py`
- Local validation passed:
  - `python -m pytest tests/test_vnc_manc_slice.py tests/test_vnc_pathways.py tests/test_vnc_spec_decoder.py tests/test_closed_loop_smoke.py -q` -> `18 passed`
  - `python -m py_compile src/vnc/schema.py src/vnc/ingest.py src/vnc/manc_slice.py scripts/build_manc_thoracic_vnc_artifacts.py tests/test_vnc_manc_slice.py tests/test_vnc_pathways.py`

3. What the sub-agents concluded
- The literature/data scout recommended a core leg-motor endpoint keyed to the
  thoracic leg exit nerves `ProLN`, `MesoLN`, and `MetaLN`, with ambiguous T1
  branch nerves treated as an optional expansion rather than the default.
- The code-shape scout confirmed that a true nerve-filtered slice needed the
  normalized node model to preserve `exitNerve` explicitly instead of trying to
  smuggle it through the overloaded `region` field.
- The testing/docs scout confirmed that `T110` should not be treated as
  complete unless the selective rules, artifacts, and comparison outputs are
  explicit and auditable.

4. What the real selective comparison produced
- Broad leg-subclass slice:
  - motor targets: `381`
  - premotor candidates: `3607`
  - selected edges: `140223`
  - two-step paths: `1460577`
  - descending structural channels: `1240`
- Strict leg-subclass slice:
  - motor targets: `381`
  - premotor candidates: `1304`
  - selected edges: `68222`
  - two-step paths: `848280`
  - descending structural channels: `1168`
- Core exit-nerve slice:
  - motor targets: `319`
  - premotor candidates: `2850`
  - selected edges: `106154`
  - two-step paths: `1028420`
  - descending structural channels: `1232`
- Strict exit-nerve slice:
  - motor targets: `319`
  - premotor candidates: `910`
  - selected edges: `46554`
  - two-step paths: `550740`
  - descending structural channels: `1131`

5. Interpretation
- The exit-nerve slice is the strongest next candidate.
- It removes the ambiguous T1 branch outputs that survive the broad
  `leg_subclass` filter and keeps only:
  - `ProLN`
  - `MesoLN`
  - `MetaLN`
- The non-strict exit-nerve slice still preserves the full live locomotor
  shortlist overlap used in this repo:
  - overlap count `30`, same as baseline and broad subclass slice
- The strict exit-nerve slice is probably too aggressive for the default next
  benchmark because it drops one `DNpe040` overlap channel.
- The broad subclass slice remains useful as a reference, but it still admits
  non-core branch outputs:
  - `DProN`
  - `VProN`
  - `ProAN`
  - `AbN1`

6. Evidence
- New real selective comparison artifacts:
  - `outputs/metrics/manc_thoracic_variant_comparison.json`
  - `outputs/metrics/manc_thoracic_variant_overlap_comparison.json`
- New selective slice summaries:
  - `outputs/metrics/manc_thoracic_slice_summary_leg_subclass.json`
  - `outputs/metrics/manc_thoracic_slice_summary_leg_subclass_strict.json`
  - `outputs/metrics/manc_thoracic_slice_summary_exit_nerve.json`
  - `outputs/metrics/manc_thoracic_slice_summary_exit_nerve_strict.json`
- New selective structural specs:
  - `outputs/metrics/manc_thoracic_structural_spec_leg_subclass.json`
  - `outputs/metrics/manc_thoracic_structural_spec_leg_subclass_strict.json`
  - `outputs/metrics/manc_thoracic_structural_spec_exit_nerve.json`
  - `outputs/metrics/manc_thoracic_structural_spec_exit_nerve_strict.json`
- Overlap artifacts:
  - `outputs/metrics/manc_thoracic_spec_overlap_leg_subclass.json`
  - `outputs/metrics/manc_thoracic_spec_overlap_leg_subclass_strict.json`
  - `outputs/metrics/manc_thoracic_spec_overlap_exit_nerve.json`
  - `outputs/metrics/manc_thoracic_spec_overlap_exit_nerve_strict.json`
- Updated docs:
  - `docs/manc_edge_slice.md`
  - `docs/vnc_workstream_plan.md`

7. What remains open
- `T110` is now done as a real-slice comparison task, but it is still not an
  embodied performance claim.
- No heavy WSL embodied decoder benchmark was launched in this loop.
- The next honest step is `T111`: load the non-strict `exit_nerve` structural
  spec as the first real production `vnc_structural_spec` candidate and smoke
  it in the closed loop before attempting broader comparisons.

## 2026-03-12 - Completed `T111` and exposed the real MANC-to-FlyWire ID blocker

1. What I attempted
- Take the preferred non-strict `exit_nerve` structural spec from `T110` and
  benchmark it as the first production `vnc_structural_spec` decoder candidate.
- Keep the ladder honest:
  - config and decoder load test
  - runtime smoke for the VNC decoder seam
  - host mock-body benchmark with the real torch brain backend
  - short real WSL FlyGym benchmark
  - explicit ID-space audit instead of guessing about the zero-output failure

2. What succeeded
- Added reproducible configs:
  - `configs/mock_multidrive_torch.yaml`
  - `configs/mock_vnc_structural_spec_exit_nerve.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_vnc_structural_spec_exit_nerve.yaml`
- Added a cheap alignment audit:
  - `scripts/audit_decoder_id_alignment.py`
- Added coverage:
  - `tests/test_vnc_spec_decoder.py`
  - `tests/test_closed_loop_smoke.py`
- Local validation passed:
  - `python -m pytest tests/test_vnc_spec_decoder.py tests/test_closed_loop_smoke.py -q` -> `14 passed`
  - `python -m py_compile src/vnc/spec_decoder.py src/bridge/decoder_factory.py src/runtime/closed_loop.py tests/test_vnc_spec_decoder.py scripts/audit_decoder_id_alignment.py`
- Host mock benchmarks completed:
  - `outputs/benchmarks/fullstack_mock_multidrive_torch_0p4s.csv`
  - `outputs/benchmarks/fullstack_mock_vnc_structural_spec_exit_nerve_0p4s.csv`
- Short real WSL realistic-vision benchmarks completed:
  - `outputs/benchmarks/fullstack_vnc_structural_spec_exit_nerve_target_0p1s.csv`
  - `outputs/benchmarks/fullstack_splice_uvgrid_descending_calibrated_target_t111_0p1s.csv`
- Wrote the machine-readable T111 summary:
  - `outputs/metrics/t111_exit_nerve_decoder_summary.json`
- Wrote the explicit ID-alignment audit:
  - `outputs/metrics/t111_decoder_id_alignment_comparison.json`
- Wrote the bench note:
  - `docs/vnc_exit_nerve_decoder_validation.md`

3. What the sub-agents concluded
- The right comparison ladder was mock-body seam validation first, then one
  short real FlyGym run, not a large sweep.
- The structural decoder config seam was already present; the key missing work
  was not more decoder math but real config files and a clear runtime audit.
- The real risk was not only saturation. It was that the MANC structural spec
  and the FlyWire brain backend might live in different ID spaces.

4. What the benchmarks showed
- Host mock path:
  - both the sampled decoder and the structural decoder stayed at zero command
  - that is consistent with the earlier public-input motor-path weakness
- Short real WSL target run with the new structural decoder:
  - completed `50` cycles at `0.1 s`
  - real-time factor: `0.00237`
  - nonzero command cycles: `0`
- Matched short real WSL target run with the current calibrated sampled decoder:
  - completed `50` cycles at `0.1 s`
  - real-time factor: `0.00244`
  - nonzero command cycles: `43`

5. Decisive blocker
- The explicit alignment audit showed:
  - real exit-nerve structural decoder requested IDs: `736`
  - FlyWire backend matched IDs: `0`
  - current sampled decoder requested IDs: `42`
  - FlyWire backend matched IDs: `42`
- That means the real MANC structural decoder is currently a silent no-op
  against the FlyWire whole-brain backend.
- This is not primarily a gain-tuning problem.
- It is an ID-space mismatch between:
  - real MANC body IDs
  - the FlyWire IDs used by the current brain backend

6. Interpretation
- `T111` is complete as a benchmark and diagnosis task.
- The runtime seam for `vnc_structural_spec` works.
- The real config path works.
- The real short benchmark works.
- But the candidate is not promotable because it cannot currently read
  meaningful brain activity from the present FlyWire backend.

7. Next actions
- Start `T112`: resolve the MANC-to-FlyWire ID-space blocker.
- Do not waste time tuning `forward_scale_hz`, `turn_scale_hz`, or channel
  thresholds further until the decoder can actually monitor a matching ID space.

## 2026-03-12 - T112 public ID-bridge review

1. What I attempted
- Reviewed the local `T111` decoder-alignment evidence and the bundled MANC
  annotation export to determine whether the current blocker is a missing
  public cross-dataset neuron-ID bridge.
- Reviewed public primary/public resources for MANC/FlyWire/BANC cross-dataset
  matching, with emphasis on official annotation tooling and the neck-connective
  comparative connectomics work.

2. What succeeded
- Confirmed locally that the runtime blocker is an ID-space mismatch, not a
  gain-tuning issue: the real MANC exit-nerve decoder requested `736` IDs and
  matched `0` against the present FlyWire backend, while the sampled
  FlyWire-native decoder matched `42/42`.
- Confirmed locally that the public MANC annotation export already carries
  annotation-level bridge fields including `mancType`, `flywireType`, and
  `hemibrainType`, which is consistent with a public homolog/type bridge rather
  than an exact raw-ID crosswalk.
- Confirmed from public sources that the strongest published cross-dataset
  bridge is at the matched type/group/homolog level, especially for
  neck-connective DNs and ANs spanning FAFB-FlyWire, FANC, and MANC.

3. What failed
- Did not find a general public exact `MANC bodyid -> FlyWire root_id`
  crosswalk that would let the current real MANC structural decoder monitor
  arbitrary FlyWire neurons by direct ID substitution.
- Did not find evidence that BANC publishes a general exact `MANC <-> FlyWire`
  per-neuron raw-ID bridge either; the public bridge appears to remain
  type/group-level.

4. Evidence
- Local: `outputs/metrics/t111_decoder_id_alignment_comparison.json`
- Local: `external/vnc/manc/body-annotations-male-cns-v0.9-minconf-0.5.feather`
- Public: `https://www.nature.com/articles/s41586-025-08925-z`
- Public: `https://github.com/flyconnectome/2023neckconnective`
- Public: `https://natverse.org/malecns/`
- Public: `https://www.nature.com/articles/s41586-024-07686-5`
- Public: `https://www.janelia.org/project-team/flyem/manc-connectome`

5. Next actions
- Treat exact MANC-to-FlyWire neuron-ID substitution as unavailable in the
  public stack unless a narrower curated subset proves otherwise.
- Design the next decoder bridge around public `cell_type` / homolog-group /
  `side` metadata, prioritizing neck-connective DN classes where the
  comparative literature is strongest.

## 2026-03-12 - T112 completed with a FlyWire semantic monitor-space bridge

1. What I attempted
- Continue `T112` past the literature review and replace the zero-overlap
  decoder path with an explicit bridge from the real MANC `exit_nerve`
  structural spec into the FlyWire monitor space used by the current
  whole-brain backend.
- Use sub-agents for three parallel checks:
  - local seam review for the minimal honest implementation
  - public literature review on whether an exact raw-ID crosswalk exists
  - local annotation overlap review for exact shared `cell_type + side`
    coverage
- Keep heavy compute serialized and only run one short real WSL benchmark after
  the bridge and tests were in place.

2. What succeeded
- Implemented the semantic bridge tooling in:
  - `src/vnc/flywire_bridge.py`
  - `scripts/build_vnc_flywire_semantic_spec.py`
- Extended the decoder in:
  - `src/vnc/spec_decoder.py`
  so `vnc_structural_spec` channels can now monitor grouped FlyWire roots via
  `monitor_ids` and pool them with `monitor_reduce = mean`.
- Added real bridge configs:
  - `configs/mock_vnc_structural_spec_exit_nerve_flywire_semantic.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_vnc_structural_spec_exit_nerve_flywire_semantic.yaml`
- Added validation coverage:
  - `tests/test_vnc_flywire_bridge.py`
  - `tests/test_vnc_spec_decoder.py`
  - `tests/test_closed_loop_smoke.py`
- Materialized the bridged real-data artifact:
  - `outputs/metrics/manc_thoracic_structural_spec_exit_nerve_flywire_semantic.json`
- Bridge summary from that artifact:
  - source channels: `1232`
  - source semantic keys: `926`
  - bridged semantic channels: `847`
  - matched source channels: `1095`
  - unmatched source channels: `137`
  - FlyWire monitor IDs after completeness filtering: `1145`
  - match counts:
    - exact `cell_type`: `770`
    - `hemibrain_type` fallback: `77`
- Cleared the runtime ID blocker:
  - raw real MANC spec config requested `736` IDs and matched `0`
  - bridged semantic config requested `685` IDs and matched `685`
- Ran a short serialized real WSL benchmark with the bridged config:
  - `outputs/benchmarks/fullstack_vnc_structural_spec_exit_nerve_flywire_semantic_target_0p1s.csv`
  - `outputs/requested_0p1s_vnc_structural_spec_exit_nerve_flywire_semantic_target/*`
  - `outputs/metrics/t112_exit_nerve_flywire_semantic_summary.json`
- That real run is no longer silent:
  - completed `50` cycles at `0.1 s`
  - real-time factor: `0.00232`
  - nonzero command cycles: `43`
  - max forward / turn signals both reached `1.0`
  - both left and right drives clipped at `1.2`

3. What failed
- The first bridged run is not behaviorally calibrated yet.
- The bridge solves monitor-space compatibility, but the decoder is currently
  saturating under the first semantic-weight scaling choice.
- No public general exact `MANC bodyid -> FlyWire root_id` crosswalk emerged;
  the bridge remains annotation-level rather than exact neuron identity.

4. Evidence
- Code:
  - `src/vnc/flywire_bridge.py`
  - `src/vnc/spec_decoder.py`
  - `scripts/build_vnc_flywire_semantic_spec.py`
- Configs:
  - `configs/mock_vnc_structural_spec_exit_nerve_flywire_semantic.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_vnc_structural_spec_exit_nerve_flywire_semantic.yaml`
- Tests:
  - `tests/test_vnc_flywire_bridge.py`
  - `tests/test_vnc_spec_decoder.py`
  - `tests/test_closed_loop_smoke.py`
- Artifacts:
  - `outputs/metrics/manc_thoracic_structural_spec_exit_nerve_flywire_semantic.json`
  - `outputs/metrics/t112_decoder_id_alignment_comparison.json`
  - `outputs/metrics/t112_decoder_id_alignment_semantic.json`
  - `outputs/metrics/t112_exit_nerve_flywire_semantic_summary.json`
  - `outputs/benchmarks/fullstack_vnc_structural_spec_exit_nerve_flywire_semantic_target_0p1s.csv`
- Docs:
  - `docs/vnc_flywire_semantic_bridge.md`
  - `docs/vnc_spec_decoder.md`
  - `docs/vnc_workstream_plan.md`
  - `docs/vnc_exit_nerve_decoder_validation.md`

5. Validation
- `python -m pytest tests/test_flywire_annotations.py tests/test_vnc_flywire_bridge.py tests/test_vnc_spec_decoder.py tests/test_closed_loop_smoke.py -q` -> `25 passed`
- `python -m py_compile src/brain/flywire_annotations.py src/vnc/flywire_bridge.py src/vnc/spec_decoder.py scripts/build_vnc_flywire_semantic_spec.py tests/test_vnc_flywire_bridge.py tests/test_vnc_spec_decoder.py` -> passed

6. Next actions
- Mark `T112` done.
- Start `T113`: calibrate the FlyWire-semantic VNC structural decoder so the
  bridged path stops saturating and can be judged on real behavior rather than
  only on ID-space validity.

## 2026-03-12 - Started `T113` with decoder normalization and tracked-camera reruns

1. What I attempted
- Investigate the user's report that the `T112` semantic-VNC demo looked bad
  because the fly ran off screen.
- Separate the problem into:
  - camera framing
  - decoder saturation
- Fix the decoder math first instead of only moving the camera.

2. What succeeded
- Confirmed from the `2.0 s` semantic-VNC run log that the fly really was
  leaving the frame under the old branch:
  - `992 / 1000` nonzero command cycles
  - drives repeatedly clipping at `1.2`
  - final position about `x = 40.69`
- Confirmed the video framing issue was real and mechanical:
  - `src/body/flygym_runtime.py` used a fixed world-mounted bird's-eye camera
    at `pos = (5, 0, 35)`
- Patched the runtime so the semantic-VNC branch can use a tracked FlyGym
  camera:
  - `src/body/flygym_runtime.py`
  - `src/runtime/closed_loop.py`
  - `configs/flygym_realistic_vision_splice_uvgrid_vnc_structural_spec_exit_nerve_flywire_semantic.yaml`
- Patched the decoder math in `src/vnc/spec_decoder.py`:
  - old path: summed `rate * structural_weight` directly into forward/turn
  - new path: divides weighted left/right totals by the total left/right
    structural weight mass of the loaded channels, then computes forward/turn
    from those normalized weighted mean rates
- Updated semantic-VNC config scales/gains to match the normalized decoder:
  - `forward_scale_hz: 20.0`
  - `turn_scale_hz: 10.0`
  - `forward_gain: 0.75`
  - `turn_gain: 0.3`
- Added/updated tests:
  - `tests/test_vnc_spec_decoder.py`
  - `tests/test_closed_loop_smoke.py`
- Short real rerun after decoder fix:
  - `outputs/benchmarks/fullstack_vnc_structural_spec_exit_nerve_flywire_semantic_decoder_fixed_target_0p1s.csv`
  - result:
    - `45 / 50` nonzero command cycles
    - `max_left_drive = 0.529`
    - `max_right_drive = 0.932`
    - `max_forward_signal = 0.858`
    - `max_turn_signal = 0.963`
- Full `2.0 s` corrected rerun:
  - `outputs/benchmarks/fullstack_vnc_structural_spec_exit_nerve_flywire_semantic_decoder_fixed_follow_yaw_target_2s.csv`
  - `outputs/requested_2s_vnc_structural_spec_exit_nerve_flywire_semantic_decoder_fixed_follow_yaw_target/flygym-demo-20260312-184650/demo.mp4`
  - result:
    - `1000 / 1000` cycles completed
    - `995 / 1000` cycles nonzero
    - `max_left_drive = 0.867`
    - `max_right_drive = 0.957`
    - final position about `x = 7.02`, `y = 1.00`
    - stable final frame remained on screen under the follow camera
- Final corrected `2.0 s` metrics:
  - `avg_forward_speed = 4.7635`
  - `net_displacement = 7.0699`
  - `displacement_efficiency = 0.7428`
  - `real_time_factor = 0.00244`

3. What failed
- This is not yet a biologically tuned semantic-VNC controller.
- The corrected branch is much better behaved than the first `T112` demo, but
  it still needs behavioral tuning and scene-level review, not just scalar
  command checks.

4. Evidence
- Code:
  - `src/vnc/spec_decoder.py`
  - `src/body/flygym_runtime.py`
  - `src/runtime/closed_loop.py`
- Tests:
  - `tests/test_vnc_spec_decoder.py`
  - `tests/test_closed_loop_smoke.py`
- Artifacts:
  - `outputs/benchmarks/fullstack_vnc_structural_spec_exit_nerve_flywire_semantic_decoder_fixed_target_0p1s.csv`
  - `outputs/benchmarks/fullstack_vnc_structural_spec_exit_nerve_flywire_semantic_decoder_fixed_follow_yaw_target_2s.csv`
  - `outputs/requested_0p1s_vnc_structural_spec_exit_nerve_flywire_semantic_decoder_fixed_target/*`
  - `outputs/requested_2s_vnc_structural_spec_exit_nerve_flywire_semantic_decoder_fixed_follow_yaw_target/flygym-demo-20260312-184650/demo.mp4`
  - `outputs/screenshots/demo.png`

5. Validation
- `python -m pytest tests/test_vnc_spec_decoder.py tests/test_closed_loop_smoke.py -q` -> `18 passed`
- `python -m py_compile src/vnc/spec_decoder.py src/body/flygym_runtime.py src/runtime/closed_loop.py tests/test_vnc_spec_decoder.py tests/test_closed_loop_smoke.py` -> passed

6. Next actions
- Continue `T113` with scene-level review of the corrected `2.0 s` semantic-VNC
  demo.
- If the motion still looks implausible, tune channel filtering and gains from
  the normalized decoder rather than reverting to raw weight-mass sums.

## 2026-03-12 - Semantic-VNC branch frozen as failed parity branch

1. What I attempted
- Wrote the semantic-VNC branch up explicitly as a failed parity branch instead of leaving it in a vague "needs more tuning" state.
- Added a dedicated freeze note and artifact-lock manifest.
- Closed `T113` with a final branch verdict.

2. What succeeded
- Added the freeze writeup:
  - `docs/semantic_vnc_failed_parity_branch.md`
- Updated the main parity and gap reports so the semantic-VNC branch is not treated as a live parity candidate:
  - `REPRO_PARITY_REPORT.md`
  - `ASSUMPTIONS_AND_GAPS.md`
- Updated the task tracker to close `T113` with a failed-parity outcome:
  - `TASKS.md`
- Added the locked-artifact manifest:
  - `outputs/locks/semantic_vnc_failed_parity_branch_manifest.md`

3. What failed
- No new technical failure occurred in this slice.
- The branch failure itself is now the recorded result:
  - semantic ID alignment works
  - decoder saturation was fixed
  - framing was fixed
  - target tracking still fails

4. Evidence paths
- `docs/semantic_vnc_failed_parity_branch.md`
- `outputs/locks/semantic_vnc_failed_parity_branch_manifest.md`
- `outputs/metrics/t112_decoder_id_alignment_comparison.json`
- `outputs/metrics/t112_exit_nerve_flywire_semantic_summary.json`
- `outputs/requested_2s_vnc_structural_spec_exit_nerve_flywire_semantic_decoder_fixed_follow_yaw_target/flygym-demo-20260312-184650/demo.mp4`
- `outputs/requested_2s_vnc_structural_spec_exit_nerve_flywire_semantic_decoder_fixed_follow_yaw_target/flygym-demo-20260312-184650/metrics.csv`

5. Next actions
- None in this turn.
- The semantic-VNC branch is frozen and should not be mutated in place.

## 2026-03-12 - Current best branch activation visualization

1. What I attempted
- Built a dedicated capture/render pipeline for a synchronized activation view
  of the current best embodied branch.
- Kept the expensive work serialized in one WSL FlyGym run.
- Used the monitored-only extension of the calibrated branch so the artifact
  could show broad descending/efferent activity without changing the underlying
  splice branch.

2. What succeeded
- Added the visualization module and CLI:
  - `src/visualization/activation_viz.py`
  - `src/visualization/__init__.py`
  - `scripts/build_best_branch_activation_visualization.py`
- Added a renderer smoke test:
  - `tests/test_activation_viz.py`
- Host validation passed:
  - `python -m pytest tests/test_activation_viz.py -q` -> `1 passed`
  - `python -m py_compile src/visualization/activation_viz.py src/visualization/__init__.py scripts/build_best_branch_activation_visualization.py tests/test_activation_viz.py` -> passed
- Completed the real WSL artifact build:
  - `outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/activation_side_by_side.mp4`
  - `outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/overview.png`
  - `outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/capture_data.npz`
  - `outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/source_demo.mp4`
  - `outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/summary.json`
- Captured scope from `summary.json`:
  - `frame_count = 200`
  - `brain_neuron_count = 138639`
  - `flyvis_neuron_count = 45669`
  - `monitor_label_count = 16`
  - `controller_label_count = 8`

3. What failed
- The first real smoke attempt on host Python failed because the new script
  did not add `src` to `sys.path`.
- The first real FlyGym smoke attempt also failed on host because `flygym` is
  only validated in the WSL `flysim-full` environment.
- Both were corrected before the full run:
  - script import shim added
  - real run moved to WSL `micromamba run -n flysim-full`

4. Evidence paths
- `docs/current_best_branch_activation_visualization.md`
- `outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/activation_side_by_side.mp4`
- `outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/overview.png`
- `outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/capture_data.npz`
- `outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/run.jsonl`
- `outputs/visualizations/current_best_branch_activation/activation-viz-20260312-202618/metrics.csv`

5. Next actions
- None in this turn.
- The requested activation visualization artifact now exists and is documented.

## 2026-03-12 - Whitepaper and README frontpage refresh

1. What I attempted
- Refreshed the main whitepaper so it reflects the newest repo state instead of stopping before the semantic-VNC freeze and the activation visualization artifact.
- Replaced the repo-home `README.md` with an actual front page derived from the whitepaper and parity docs.
- Prepared the docs-only update for commit and push.

2. What succeeded
- Updated the long-form whitepaper:
  - `docs/openfly_whitepaper.md`
- Rewrote the GitHub landing page:
  - `README.md`
- Added tracker coverage for the docs refresh:
  - `TASKS.md`
  - `PROGRESS_LOG.md`
- The whitepaper now explicitly includes:
  - the semantic-VNC `exit_nerve_flywire_semantic` branch as a frozen failed parity result
  - the synchronized current-best activation visualization as a first-class evidence artifact

3. What failed
- No code or runtime work was attempted in this slice.
- No tests were run because this was a documentation-only refresh.

4. Evidence paths
- `docs/openfly_whitepaper.md`
- `README.md`
- `TASKS.md`
- `PROGRESS_LOG.md`
- `REPRO_PARITY_REPORT.md`
- `docs/current_best_branch_activation_visualization.md`
- `docs/semantic_vnc_failed_parity_branch.md`

5. Next actions
- Commit and push the docs-only refresh to `origin/main`.

## 2026-03-13 - Best-branch end-to-end investigation for no-shortcuts embodiment

1. What I attempted
- Investigated the current best branch using only recorded artifacts rather than
  launching a new heavy embodied run.
- Analyzed the synchronized activation capture, matched behavior metrics, and
  monitor/controller traces together.
- Focused on learning what would plausibly advance embodiment without adding
  new shortcuts.

2. What succeeded
- Added a reusable analysis module and CLI:
  - `src/analysis/best_branch_investigation.py`
  - `scripts/analyze_best_branch_embodiment.py`
- Added a focused local test:
  - `tests/test_best_branch_investigation.py`
- Materialized investigation artifacts:
  - `outputs/metrics/best_branch_investigation_summary.json`
  - `outputs/metrics/best_branch_investigation_behavior_summary.csv`
  - `outputs/metrics/best_branch_investigation_family_correlations.csv`
  - `outputs/metrics/best_branch_investigation_monitor_correlations.csv`
  - `outputs/metrics/best_branch_investigation_unsampled_central_units.csv`
  - `outputs/metrics/best_branch_investigation_unsampled_central_spiking_units.csv`
  - `outputs/plots/best_branch_investigation_family_target_bearing_corr.png`
  - `outputs/plots/best_branch_investigation_monitor_target_bearing_corr.png`
- Wrote the interpretation note:
  - `docs/best_branch_e2e_investigation.md`

3. What failed
- No new runtime failure occurred.
- Sub-agent turnaround was unreliable in this slice, so the decisive technical
  findings came from the local reproducible analysis rather than waiting on the
  sidecar syntheses.

4. Evidence
- Tests:
  - `python -m pytest tests/test_best_branch_investigation.py -q` -> `3 passed`
- Analysis outputs:
  - `outputs/metrics/best_branch_investigation_summary.json`
  - `outputs/metrics/best_branch_investigation_family_correlations.csv`
  - `outputs/metrics/best_branch_investigation_monitor_correlations.csv`
  - `docs/best_branch_e2e_investigation.md`

5. Next actions
- Build matched monitored activation captures for `target`, `no_target`, and
  `zero_brain` under the same config.
- Expand monitoring to the strongest unsampled relay families before changing
  the splice or decoder again.

## 2026-03-13 - Spontaneous-state workstream framing

1. What I attempted
- Added a docs-only framing note for the spontaneous-state program so the next
  cold-start work is defined before anyone starts patching runtime logic.
- Tied the new note directly to the current best-branch investigation and the
  existing `zero_brain` / brain-control evidence.
- Added a tracked task for the spontaneous-state workstream.

2. What succeeded
- Added the workstream note:
  - `docs/spontaneous_state_program.md`
- Added a new tracked task:
  - `T117` in `TASKS.md`
- Recorded this docs-only milestone in:
  - `PROGRESS_LOG.md`
- The new note now states:
  - why the current cold-start is functionally dead at the body-control
    boundary even though the backend itself is not dead
  - what counts as biologically plausible endogenous activity in this repo
  - what validation gates must be passed before any spontaneous-state
    implementation can be treated as honest progress

3. What failed
- No code or runtime experiments were attempted in this slice.
- No tests were run because this update intentionally stayed within
  `docs/`, `TASKS.md`, and `PROGRESS_LOG.md`.

4. Evidence
- `docs/spontaneous_state_program.md`
- `TASKS.md`
- `PROGRESS_LOG.md`
- `docs/best_branch_e2e_investigation.md`
- `docs/brain_control_validation.md`

5. Next actions
- Use `T117` as the tracking root for matched startup-state diagnostics.
- Add matched `target`, `no_target`, and `zero_brain` activation/control
  captures before proposing any endogenous-state mechanism.
- Keep the spontaneous-state path inside the no-shortcuts boundary documented
  in `docs/spontaneous_state_program.md`.

## 2026-03-13 - Spontaneous-state backend pilot: sparse tonic occupancy plus slow latent fluctuations

1. What I attempted
- Audited the current Torch whole-brain backend and confirmed that the old
  reset path had an absorbing silent fixed point with no endogenous source of
  activity.
- Added an opt-in spontaneous-state path inside `WholeBrainTorchBackend`
  instead of touching the decoder or body controller.
- Implemented a first biologically stricter candidate: sparse lognormal tonic
  background plus low-rank slow latent fluctuations and reset voltage
  heterogeneity.
- Added a brain-only audit path and startup-state logging so the new branch can
  be judged from saved artifacts rather than from impressionistic demos.

2. What succeeded
- Wired the new backend config path:
  - `src/brain/pytorch_backend.py`
  - `src/runtime/closed_loop.py`
  - `benchmarks/run_brain_benchmarks.py`
  - `configs/brain_spontaneous_probe.yaml`
- Added tests and logging support:
  - `tests/test_spontaneous_state_unit.py`
  - `tests/test_closed_loop_smoke.py`
  - `src/bridge/controller.py`
- Added reproducible docs for the workstream:
  - `docs/spontaneous_state_backend_design.md`
  - `docs/spontaneous_state_validation_plan.md`
  - `docs/spontaneous_state_results.md`
- Added a reproducible brain-only audit:
  - `scripts/run_spontaneous_state_audit.py`
- Produced the first artifact-complete pilot bundle:
  - `outputs/metrics/spontaneous_state_pilot_summary.json`
  - `outputs/metrics/spontaneous_state_latent_pilot_summary.json`
  - `outputs/metrics/spontaneous_state_latent_seed0_summary.json`
  - `outputs/metrics/spontaneous_state_latent_seed1_summary.json`
  - `outputs/metrics/spontaneous_state_latent_seed2_summary.json`
  - matching CSV, PNG, and benchmark CSV outputs under `outputs/metrics/`,
    `outputs/plots/`, and `outputs/benchmarks/`
- The old cold-start condition stayed exactly silent.
- The latent pilot no longer stayed dead:
  - `candidate_ongoing.mean_spike_fraction ~= 3.14e-4`
  - `candidate_ongoing.background_mean_rate_hz ~= 0.254`
  - `candidate_ongoing.background_active_fraction ~= 0.147`
  - `candidate_ongoing.nonzero_window_fraction = 1.0`
  - structure ratio `~= 1.115`
  - pulse peak turn asymmetry `= 200 Hz` in the seed-0 pilot

3. What failed
- The first static sparse-tonic candidate was too weak; monitored structure was
  effectively absent and the monitored motor layer stayed near zero.
- The current latent candidate is not yet robust enough across seeds:
  - seed `0`: ongoing baseline turn bias `+20 Hz`, pulse peak `200 Hz`
  - seed `1`: ongoing baseline turn bias `-5 Hz`, pulse peak `0 Hz`
  - seed `2`: ongoing baseline turn bias `+17.5 Hz`, pulse peak `200 Hz`
- Spontaneous motor-side lateral bias under symmetric zero-input conditions is
  still too strong for promotion.
- No embodied `target` / `no_target` / `zero_brain` spontaneous-state runs were
  launched in this slice, so no embodied improvement claim is being made.

4. Evidence
- Tests:
  - `python -m pytest tests/test_closed_loop_smoke.py tests/test_brain_backend.py tests/test_spontaneous_state_unit.py -q` -> `21 passed`
- Brain-only pilot outputs:
  - `outputs/metrics/spontaneous_state_pilot_summary.json`
  - `outputs/metrics/spontaneous_state_latent_pilot_summary.json`
  - `outputs/metrics/spontaneous_state_latent_seed0_summary.json`
  - `outputs/metrics/spontaneous_state_latent_seed1_summary.json`
  - `outputs/metrics/spontaneous_state_latent_seed2_summary.json`
- Docs:
  - `docs/spontaneous_state_backend_design.md`
  - `docs/spontaneous_state_validation_plan.md`
  - `docs/spontaneous_state_results.md`

5. Next actions
- Reduce spontaneous left/right bias under symmetric control without falling
  back into a dead-cold state.
- Improve seed robustness of the latent candidate.
- Run short matched embodied `target` / `no_target` / `zero_brain` validations
  with the new `brain_backend_state` logging before promoting any spontaneous
  branch config.

## 2026-03-13 - Central-family bilateral spontaneous-state candidate clears the brain-only bar

1. What I attempted
- Iterated on the backend-only spontaneous-state candidate instead of moving to
  embodied validation too early.
- Replaced the earlier random neuron-level latent structure with a bilateral
  family-structured candidate built from the public FlyWire annotation
  supplement.
- Restricted the spontaneous family pool to central/integrative super-classes
  so the background state would stop being dominated by giant optic/sensory
  families.
- Added homologous-family metrics to the audit so the candidate could be judged
  against public whole-brain monitoring results rather than only against a few
  motor readouts.

2. What succeeded
- Updated the backend to support family-structured spontaneous modes:
  - `src/brain/pytorch_backend.py`
- Updated the audit tool to evaluate family-level bilateral structure:
  - `scripts/run_spontaneous_state_audit.py`
- Promoted the new best probe config:
  - `configs/brain_spontaneous_probe.yaml`
- Materialized the new best-candidate artifacts:
  - `outputs/metrics/spontaneous_state_best_candidate_summary.json`
  - `outputs/metrics/spontaneous_state_central_seed0_summary.json`
  - `outputs/metrics/spontaneous_state_central_seed1_summary.json`
  - `outputs/metrics/spontaneous_state_central_seed2_summary.json`
  - `outputs/metrics/spontaneous_state_central_seed_summary.json`
  - `outputs/metrics/spontaneous_state_central_seed_summary.csv`
- The new candidate now shows:
  - sparse bounded ongoing activity
  - low spontaneous turn bias under symmetric zero-input conditions
  - positive homologous-family coupling
  - retained pulse perturbability across all tested seeds

3. What failed
- The first bilateral family sweep was too weak and effectively silent:
  - `outputs/metrics/spontaneous_state_bilateral_a_summary.json`
- A stronger bilateral family sweep became active but had weak structure and no
  useful pulse expression:
  - `outputs/metrics/spontaneous_state_bilateral_b_summary.json`
- The family-level audit initially had a real bug: family monitor groups were
  registered with backend indices instead of FlyWire root IDs. That produced
  invalid homologous-family metrics until fixed.
- Embodied matched-control validation is still intentionally not done in this
  entry.

4. Evidence
- Tests:
  - `python -m pytest tests/test_closed_loop_smoke.py tests/test_brain_backend.py tests/test_spontaneous_state_unit.py -q` -> `21 passed`
- Best-candidate summaries:
  - `outputs/metrics/spontaneous_state_best_candidate_summary.json`
  - `outputs/metrics/spontaneous_state_central_seed_summary.json`
  - `docs/spontaneous_state_results.md`
- Updated mechanism/design notes:
  - `docs/spontaneous_state_backend_design.md`
  - `ASSUMPTIONS_AND_GAPS.md`

5. Next actions
- Use the central-family bilateral candidate as the baseline for the first
  embodied spontaneous-state validation.
- Run matched short `target` / `no_target` / `zero_brain` tests with
  `brain_backend_state` logging.
- Keep embodied promotion blocked until the new candidate improves startup
  readiness without collapsing control separation.

## 2026-03-13 - Default activation capture and iterative decoding workbench

1. What I attempted
- Moved the synchronized activation visualization out of its special-case
  rerun path and into the normal closed-loop run path.
- Added a repo-native decoding-cycle workbench so the activation artifact can
  drive a repeatable relay/monitor expansion loop instead of ad hoc neuron
  guessing.
- Reused sub-agent scouting to ground the design against the current repo seam
  and the public data layers that are actually available now.

2. What succeeded
- Added same-run activation capture/render support to the main runtime:
  - `src/runtime/closed_loop.py`
  - `src/visualization/session.py`
  - `src/visualization/activation_viz.py`
- Ensured non-monitored population configs still expose monitor-style traces by
  falling back to population groups when explicit monitor groups are absent:
  - `src/bridge/decoder.py`
- Added a synthetic splice-cache path for fast mock runs so the activation
  capture seam can be smoke-tested:
  - `src/body/mock_body.py`
- Relaxed the standalone visualization script so it discovers monitor labels
  from live motor-readout keys instead of requiring a hand-authored monitor
  list:
  - `scripts/build_best_branch_activation_visualization.py`
- Added the iterative decoding workbench and CLI:
  - `src/analysis/iterative_decoding.py`
  - `scripts/run_iterative_decoding_cycle.py`
  - `tests/test_iterative_decoding.py`
- Ran the first decoding cycle on the current best activation capture:
  - `outputs/metrics/iterative_decoding_cycle_summary.json`
  - `outputs/metrics/iterative_decoding_cycle_family_scores.csv`
  - `outputs/metrics/iterative_decoding_cycle_monitor_scores.csv`
  - `outputs/metrics/iterative_decoding_cycle_monitor_expansion.csv`
  - `outputs/metrics/iterative_decoding_cycle_relay_candidates.csv`
- Wrote the design record:
  - `docs/iterative_brain_decoding_system.md`

3. What failed
- Nothing failed in the code path after the final patch set, but the workbench
  result is still a planning/probing layer, not a solved full-brain decode.
- The first workbench output confirms the existing problem rather than solving
  it automatically: monitored DN labels are still weaker than upstream central
  / ascending / visual-projection families for target-bearing structure.

4. Evidence
- Tests:
  - `python -m pytest tests/test_iterative_decoding.py tests/test_bridge_unit.py tests/test_closed_loop_smoke.py tests/test_activation_viz.py -q` -> `34 passed`
- New workbench output:
  - `outputs/metrics/iterative_decoding_cycle_summary.json`
  - `docs/iterative_brain_decoding_system.md`
- Key first-cycle findings:
  - best monitored target-bearing label remains weak: `DNg97 = 0.2192`
  - recommended next relay families include `AVLP370a`, `AN_multi_67`,
    `LHAV3e6`, `AN_AVLP_16`, `CB1505`, and `LT57`

5. Next actions
- Generate matched activation captures for `target`, `no_target`, and
  `zero_brain` using the new default run path.
- Run those matched captures through the decoding-cycle workbench.
- Promote the resulting relay families only as monitoring-only checkpoints
  before changing any live control path.

## 2026-03-13 - First matched relay-monitor and shadow-VNC control loop

1. What I attempted
- Built a merged monitor candidate set from the current strict DN shortlist plus
  the first relay families ranked by the iterative decoding workbench.
- Added a shadow-decoder seam so the same embodied run can carry the live
  descending controller and a passive semantic-VNC decoder at the same time.
- Ran serialized real WSL `0.2 s` matched controls for:
  - `target`
  - `no_target`
  - `zero_brain`
- Ran the iterative decoding workbench on the `target` and `no_target`
  activation captures.

2. What succeeded
- Added monitor-family tooling and widened matched-control configs:
  - `scripts/build_family_monitor_candidates.py`
  - `outputs/metrics/iterative_monitor_candidates_merged.json`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_relay_monitored.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_relay_monitored_no_target.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_relay_monitored_zero_brain.yaml`
- Added the shadow-decoder seam and raw monitored-rate logging:
  - `src/bridge/controller.py`
  - `src/runtime/closed_loop.py`
- Extended capture/logging to preserve raw monitored voltage/spike state:
  - `src/visualization/session.py`
- Materialized the first matched-control artifacts:
  - `outputs/requested_0p2s_relay_monitored_target/flygym-demo-20260313-215135/*`
  - `outputs/requested_0p2s_relay_monitored_no_target/flygym-demo-20260313-215459/*`
  - `outputs/requested_0p2s_relay_monitored_zero_brain/flygym-demo-20260313-215725/*`
  - `outputs/metrics/relay_monitored_control_metrics_0p2s.csv`
  - `outputs/metrics/relay_monitored_shadow_control_summary_0p2s.csv`
  - `outputs/metrics/iterative_decoding_cycle_relay_target_summary.json`
  - `outputs/metrics/iterative_decoding_cycle_relay_no_target_summary.json`
- Wrote the result note:
  - `docs/relay_monitored_shadow_control_loop.md`

3. What failed
- The widened relay monitor and shadow-VNC loop did not make the behavior
  target-selective.
- `no_target` still beat `target` on displacement and forward speed at the
  matched `0.2 s` duration.
- The newly added relay families were much more visible in voltage space than
  in firing-rate space. In the first widened target and no-target runs, many of
  the added relay labels stayed at or near zero rate even when whole-family
  voltage correlations were strong.
- The `zero` backend does not expose brain-state tensors, so the zero-brain run
  honestly skipped the rendered activation artifact.

4. Evidence
- Tests:
  - `python -m pytest tests/test_family_monitor_candidates.py tests/test_closed_loop_smoke.py tests/test_bridge_unit.py tests/test_iterative_decoding.py -q` -> `38 passed`
- Behavioral control comparison:
  - `target`: `avg_forward_speed = 2.7087`, `net_displacement = 0.2248`
  - `no_target`: `3.3055`, `0.2972`
  - `zero_brain`: `1.7358`, `0.0162`
- Shadow VNC comparison:
  - `target`: `forward_mean = 0.01093`, `abs_turn_mean = 0.00842`
  - `no_target`: `0.01322`, `0.00881`
  - `zero_brain`: exact zero
- Ranked-family outputs:
  - `outputs/metrics/iterative_decoding_cycle_relay_target_family_scores.csv`
  - `outputs/metrics/iterative_decoding_cycle_relay_no_target_family_scores.csv`

5. Next actions
- Re-run the matched relay-control analysis using the new monitored-voltage
  logging path rather than relying on rate-only relay monitors.
- Compare target / no-target relay families in voltage space to find
  target-selective families that survive the controls.
- Keep the semantic-VNC branch in shadow mode until it separates `target` from
  `no_target` better than the live descending controller.

## 2026-03-13 - Target-engagement metric pivot for iterative decoding

1. What I attempted
- Replaced the decode-loop behavior diagnosis that had been leaning too heavily
  on speed/displacement with behavior metrics that separate:
  - target engagement / steering alignment
  - spontaneous locomotor richness
- Re-scored the existing matched relay-monitored `target`, `no_target`, and
  `zero_brain` runs without launching any new heavy embodied jobs.
- Ranked target-specific relay families against the `no_target` spontaneous
  baseline so the next monitor expansion is chosen for steering relevance
  rather than generic locomotor correlation.

2. What succeeded
- Added the new analysis layer:
  - `src/analysis/behavior_metrics.py`
  - `scripts/analyze_behavior_conditions.py`
- Integrated those metrics into the iterative decoding workbench:
  - `src/analysis/iterative_decoding.py`
- Added the target-specific relay ranking layer:
  - `src/analysis/relay_target_specificity.py`
  - `scripts/compare_relay_condition_scores.py`
- Added regression coverage:
  - `tests/test_behavior_metrics.py`
  - `tests/test_relay_target_specificity.py`
  - updated `tests/test_iterative_decoding.py`
- Materialized the new artifacts:
  - `outputs/metrics/relay_monitored_behavior_conditions_0p2s.csv`
  - `outputs/metrics/relay_monitored_behavior_conditions_0p2s.json`
  - `outputs/metrics/relay_target_specificity_0p2s_summary.json`
  - `outputs/metrics/relay_target_specificity_0p2s_families.csv`
  - `outputs/metrics/relay_target_specificity_0p2s_monitors.csv`
- Wrote the result notes:
  - `docs/target_engagement_metric_pivot.md`
  - updated `docs/relay_monitored_shadow_control_loop.md`
  - updated `docs/iterative_brain_decoding_system.md`

3. What failed
- The current relay branch still does not clear a target-engagement bar.
- The target run now looks clearly locomotor-rich, but the signed steering
  transfer is still wrong:
  - `turn_alignment_fraction_active = 0.467`
  - `turn_bearing_corr = -0.697`
  - `fixation_fraction_20deg = 0.0`
- Simple target-bearing reduction cannot be trusted by itself because the
  matched `zero_brain` control still gets passive bearing improvement.

4. Evidence
- Tests:
  - `python -m pytest tests/test_behavior_metrics.py tests/test_iterative_decoding.py tests/test_closed_loop_smoke.py -q` -> `20 passed`
  - `python -m pytest tests/test_behavior_metrics.py tests/test_iterative_decoding.py tests/test_relay_target_specificity.py -q` -> `4 passed`
- Target condition summary:
  - `locomotor_active_fraction = 0.96`
  - `controller_state_entropy = 0.583`
  - `bearing_reduction_rad = 0.250`
  - `turn_alignment_fraction_active = 0.467`
  - `turn_bearing_corr = -0.697`
- Zero-brain control:
  - `locomotor_active_fraction = 0.40`
  - `controller_state_entropy = 0.0`
  - `bearing_reduction_rad = 0.273`
- Target-specific relay shortlist after penalizing the no-target spontaneous
  baseline:
  - `MTe14`
  - `LTe62`
  - `VCH`
  - `CB0828`
  - `cL02c`
  - `CB1492`
  - `CB3516`
  - `LTe11`

5. Next actions
- Use signed target-engagement metrics rather than raw locomotion totals when
  judging the next relay-monitor iteration.
- Re-run the relay-monitor workstream with the new target-specific shortlist,
  using voltage-space relay diagnostics as the main guide.
- Keep the semantic-VNC path in shadow mode and keep spontaneous-state as a
  background condition rather than a motor floor.

## 2026-03-14 - Steering-aware turn-voltage decode iteration

1. What I attempted
- Extended the iterative decode workbench so it scores lateralized monitored
  voltages and family asymmetries against target-bearing and controller
  asymmetry, instead of relying mainly on bilateral mean activation.
- Re-ran the matched target-specific monitored target / no-target analysis with
  that steering-aware table set.
- Built the next turn-voltage monitor cohort from the new family ranking.
- Built and replayed voltage-driven shadow turn decoders from the ranked monitor
  labels to test whether the relay voltages carry a better steering signal than
  the live sampled descending turn scalar.

2. What succeeded
- Added steering-aware decode artifacts:
  - `outputs/metrics/iterative_decoding_cycle_target_specific_target_family_turn_scores.csv`
  - `outputs/metrics/iterative_decoding_cycle_target_specific_target_monitor_voltage_turn_scores.csv`
  - `outputs/metrics/iterative_decoding_cycle_target_specific_no_target_family_turn_scores.csv`
  - `outputs/metrics/iterative_decoding_cycle_target_specific_no_target_monitor_voltage_turn_scores.csv`
- Added target-vs-no-target steering-specific comparisons:
  - `outputs/metrics/target_specific_relay_turn_voltage_specificity_0p2s_families.csv`
  - `outputs/metrics/target_specific_relay_turn_voltage_specificity_0p2s_monitors.csv`
  - `outputs/metrics/target_specific_relay_turn_voltage_specificity_0p2s_summary.json`
- Built the next monitor cohort:
  - `outputs/metrics/relay_turn_voltage_monitor_candidates.json`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_turn_voltage_monitored.yaml`
  - matched `no_target` and `zero_brain` configs
- Added the shadow turn decoder seam:
  - `src/bridge/voltage_decoder.py`
  - `scripts/build_turn_voltage_signal_library.py`
  - `scripts/replay_voltage_turn_shadow_decoder.py`
- Built two shadow signal libraries:
  - broad central+visual:
    - `outputs/metrics/target_specific_turn_voltage_signal_library_0p2s.json`
  - stricter visual-only:
    - `outputs/metrics/target_specific_turn_voltage_signal_library_visual_only_0p2s.json`
- Replayed both against the recorded target run:
  - `outputs/metrics/target_specific_turn_voltage_shadow_replay_target_0p2s.json`
  - `outputs/metrics/target_specific_turn_voltage_shadow_replay_visual_only_target_0p2s.json`

3. What failed
- The live embodied controller is still unchanged and still steering-poor.
- This slice does not yet prove online embodied improvement; the new turn
  decoders were evaluated as shadow replays on existing logs.
- The broader library still mixes plausible visual relays with central-state
  families, so it is not the cleanest biological candidate even though it is
  slightly stronger numerically.

4. Evidence
- Steering-aware monitor comparison now highlights current monitored labels such
  as:
  - `IB015`
  - `CB1492`
  - `MTe14`
  - `VCH`
  - `LTe62`
  - `LT43`
  - `LTe11`
- Steering-aware family comparison now highlights turn-voltage families such as:
  - `LTe74`
  - `cL17`
  - `LC10d`
  - `LPT27`
  - `LPT51`
  - `LC36`
- Replay result on the recorded target run:
  - live sampled turn signal:
    - `live_turn_bearing_corr = -0.1663`
  - broad voltage shadow:
    - `shadow_turn_bearing_corr = -0.7276`
  - visual-only voltage shadow:
    - `shadow_turn_bearing_corr = -0.7114`
- Tests:
  - `python -m pytest tests/test_iterative_decoding.py tests/test_closed_loop_smoke.py -q` -> `22 passed`
  - `python -m pytest tests/test_voltage_turn_decoder.py tests/test_closed_loop_smoke.py -q` -> `22 passed`

5. Next actions
- Run the new `turn_voltage_monitored` matched target / no-target / zero-brain
  embodied cohort with the semantic-VNC shadow plus both voltage-turn shadows.
- Compare whether the visual-only shadow stays nearly as predictive online as
  the broader library.
- Do not mutate the live controller until the shadow decoders show stable
  online target-signed steering above the zero-brain baseline.

## 2026-03-14 - Online matched turn-voltage monitored cohort

1. What I attempted
- Ran the new `turn_voltage_monitored` target / no-target / zero-brain
  embodied cohort in real FlyGym with:
  - the unchanged live controller
  - the semantic-VNC shadow
  - the broad voltage-turn shadow
  - the visual-only voltage-turn shadow

2. What succeeded
- All three serialized `0.2 s` runs completed:
  - `outputs/requested_0p2s_turn_voltage_monitored_target/flygym-demo-20260314-093340`
  - `outputs/requested_0p2s_turn_voltage_monitored_no_target/flygym-demo-20260314-093552`
  - `outputs/requested_0p2s_turn_voltage_monitored_zero_brain/flygym-demo-20260314-093805`
- Same-run activation artifacts were generated for the target and no-target
  runs.
- The online shadow voltage-turn signals remained strongly target-signed in the
  fresh target run:
  - broad: `turn_bearing_corr = -0.9206`
  - visual-only: `turn_bearing_corr = -0.9147`
- Both voltage shadows collapsed to zero in the zero-brain control.

3. What failed
- The live controller still did not improve. Behavior remained effectively the
  same steering-poor branch:
  - `turn_alignment_fraction_active = 0.467`
  - `fixation_fraction_20deg = 0.0`
- So this slice still does not deliver embodied target tracking; it only proves
  that the monitored relay voltages contain a strong online steering signal.

4. Evidence
- Behavior conditions:
  - `outputs/metrics/turn_voltage_monitored_behavior_conditions_0p2s.json`
- Shadow summaries:
  - `outputs/metrics/turn_voltage_shadow_all_target_0p2s.json`
  - `outputs/metrics/turn_voltage_shadow_all_no_target_0p2s.json`
  - `outputs/metrics/turn_voltage_shadow_all_zero_brain_0p2s.json`
  - `outputs/metrics/turn_voltage_shadow_visual_target_0p2s.json`
  - `outputs/metrics/turn_voltage_shadow_visual_no_target_0p2s.json`
  - `outputs/metrics/turn_voltage_shadow_visual_zero_brain_0p2s.json`
- Target-run correlations:
  - live sampled turn: `-0.1663`
  - broad voltage shadow: `-0.9206`
  - visual-only voltage shadow: `-0.9147`
- Condition separation:
  - broad shadow abs-turn mean:
    - target `0.6078`
    - no-target `0.4944`
    - zero-brain `0.0`
  - visual-only shadow abs-turn mean:
    - target `0.6167`
    - no-target `0.4973`
    - zero-brain `0.0`

5. Next actions
- Design a bounded steering-only live promotion experiment using the visual-only
  voltage shadow first.
- Keep forward drive untouched.
- Re-run matched target / no-target / zero-brain controls after any promotion.

## 2026-03-14 10:35 - Recorded hard duration rule for future evaluation

1. What I attempted
- Added a repo-level rule clarifying which run durations count as benchmark
  evidence versus smoke-only diagnostics.

2. What succeeded
- The rule is now recorded in:
  - `TASKS.md`
  - `ASSUMPTIONS_AND_GAPS.md`
  - `PROGRESS_LOG.md`

3. Rule
- `>= 1.0 s` counts as benchmarking / real evaluation.
- `< 1.0 s` counts only as smoke test / sanity check.

4. Evidence
- `TASKS.md`
- `ASSUMPTIONS_AND_GAPS.md`
- `PROGRESS_LOG.md`

5. Next actions
- Apply this rule to future reporting and do not treat sub-`1.0 s` runs as
  benchmark evidence.

## 2026-03-14 13:10 - Resolved the bounded turn-voltage promotion failure with matched 2.0 s controls

1. What I attempted
- Investigated the failing promoted visual-core branch with local analysis plus
  multiple sub-agents.
- Proved the original `>500 ms` issue was not just “vision dropoff”:
  - first failure mode was live/shadow arbitration collapse
  - second failure mode was a deeper generic relay bias visible in matched
    no-target controls
- Iterated through three code fixes:
  - conflict-aware steering arbitration in `src/bridge/controller.py`
  - salience-gated conflict override in `src/bridge/controller.py`
  - bias-corrected visual-core shadow decoding plus silent-brain guards in
    `src/bridge/voltage_decoder.py`
- Revalidated each step with real serialized WSL `2.0 s` runs.

2. What succeeded
- The final bounded promotion branch now has matched `2.0 s` evidence across
  target / no-target / zero-brain.
- Final target branch:
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_conflict_gated_bias_target/flygym-demo-20260314-121624/summary.json`
  - `turn_alignment_fraction_active = 0.7973`
  - `aligned_turn_fraction = 0.704`
  - `turn_bearing_corr = 0.7626`
  - `mean_abs_bearing_rad = 0.9020`
  - `right_turn_dominant_fraction = 0.232`
  - `left_turn_dominant_fraction = 0.768`
- Final no-target branch:
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_conflict_gated_bias_no_target/flygym-demo-20260314-123350/summary.json`
  - `right_turn_dominant_fraction = 0.374`
  - `left_turn_dominant_fraction = 0.626`
  - `mean_turn_drive = -0.0385`
  - `turn_switch_rate_hz = 21.021`
  - the old generic one-sided right-turn lock is gone
- Final zero-brain integrity branch:
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_conflict_gated_bias_zero_brain_guarded_v3/flygym-demo-20260314-131053/summary.json`
  - `controller_summary_forward_nonzero_fraction = 0.0`
  - `controller_summary_turn_nonzero_fraction = 0.0`
  - `mean_turn_drive = 0.0`
  - `net_displacement = 0.0118`
- The production run path kept generating same-run activation artifacts for the
  target and no-target branches.

3. What failed
- The first conflict-aware promotion patch alone was not sufficient.
- A naive no-target baseline subtraction initially broke the zero-brain control
  because the shadow decoder interpreted missing or uniform rest-state voltage
  as real signal.
- That was fixed by adding explicit silent-brain guards to the voltage shadow
  decoder.

4. Evidence
- Final target benchmark:
  - `outputs/benchmarks/fullstack_turn_voltage_promoted_visual_core_conflict_gated_bias_target_2s.csv`
- Final no-target benchmark:
  - `outputs/benchmarks/fullstack_turn_voltage_promoted_visual_core_conflict_gated_bias_no_target_2s.csv`
- Final zero-brain benchmark:
  - `outputs/benchmarks/fullstack_turn_voltage_promoted_visual_core_conflict_gated_bias_zero_brain_guarded_v3_2s.csv`
- Updated workstream note:
  - `docs/turn_voltage_decode_iteration.md`
- Derived bias-corrected library:
  - `outputs/metrics/target_specific_turn_voltage_signal_library_visual_core_2s_bias_corrected.json`

5. Next actions
- Treat `T134` as complete.
- Keep this branch as the current best bounded steering-promotion result.
- Future work should widen biological motor semantics beyond steering-only
  promotion rather than re-opening the resolved no-target bias bug.

## 2026-03-14 18:05 - Grounded the behavior target set in real adult-fly literature

1. What I attempted
- Used sub-agents plus direct literature review to verify that the behaviors we
  are optimizing are real adult-fly behaviors rather than synthetic benchmark
  artifacts.
- Reviewed visually guided fixation / orientation / perturbation refixation,
  spontaneous locomotion and pauses, structured turning, short-timescale
  orientation memory, and walking-linked whole-brain state.
- Reviewed the current repo docs to decide where the canonical behavior target
  set and state-management consequences should live.

2. What succeeded
- Added the canonical grounded spec:
  - `docs/behavior_target_set.md`
- Threaded that spec into the main decode and state-management docs:
  - `docs/target_engagement_metric_pivot.md`
  - `docs/iterative_brain_decoding_system.md`
  - `docs/spontaneous_state_program.md`
  - `docs/spontaneous_state_validation_plan.md`
  - `ASSUMPTIONS_AND_GAPS.md`
- The repo now distinguishes:
  - real target behaviors we should optimize for:
    - spontaneous roaming
    - intermittent locomotion with pauses
    - structured turning / reorientation
    - landmark fixation / orientation
    - perturbation refixation
    - short-timescale orientation memory
  - real but out-of-scope or context-specific behaviors we should not treat as
    default acceptance targets yet:
    - odor-loss search
    - reward local search
    - hunger-state foraging
    - looming freeze / flee
    - courtship-specific pursuit
- The repo now explicitly rejects generic indefinite smooth pursuit of an
  arbitrary moving target as the default real-fly behavior claim.

3. What failed
- The repo still does not have a perturbation-specific `target_jump` or
  `target_removed_brief` evaluation path, so refixation and short-timescale
  persistence are grounded by literature but not yet directly scored in the
  live branch.
- Repo-level verdict docs still need to be re-scored against the new canonical
  behavior target set.

4. Evidence
- `docs/behavior_target_set.md`
- `docs/target_engagement_metric_pivot.md`
- `docs/iterative_brain_decoding_system.md`
- `docs/spontaneous_state_program.md`
- `docs/spontaneous_state_validation_plan.md`
- `ASSUMPTIONS_AND_GAPS.md`
- `TASKS.md`

5. Next actions
- Re-score the current best embodied branch against the new canonical behavior
  target set.
- Add perturbation-aware target assays so refixation and brief-loss persistence
  are measured directly instead of inferred from continuous-target runs.

## 2026-03-14 21:10 - Implemented and benchmarked the first grounded target perturbation assays

1. What I attempted
- Used sub-agents to confirm the clean implementation seam for a grounded
  visual perturbation assay:
  - perturb the target in the body runtime
  - log perturbation state through `target_state`
  - score refixation and brief-loss persistence in `behavior_metrics.py`
- Implemented runtime-side target scheduling with `jump` and `hide` events.
- Added perturbation-aware behavior metrics.
- Added runnable current-branch configs for:
  - `target_jump`
  - `target_removed_brief`
- Ran real serialized `2.0 s` embodied FlyGym assays with same-run activation
  visualization for both perturbation types.

2. What succeeded
- New runtime and metric seams are in place:
  - `src/body/target_schedule.py`
  - `src/body/flygym_runtime.py`
  - `src/runtime/closed_loop.py`
  - `src/analysis/behavior_metrics.py`
- Focused validation passed:
  - `python -m pytest tests/test_target_schedule.py tests/test_behavior_metrics.py tests/test_closed_loop_smoke.py -q`
  - `26 passed`
- First real jump assay completed with activation capture:
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_target_jump/flygym-demo-20260314-203328`
- First real brief-removal assay completed with activation capture:
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_target_removed_brief/flygym-demo-20260314-204945`
- The new assay doc is written:
  - `docs/target_perturbation_assay.md`

3. What failed
- The current best branch does not yet solve perturbation behavior.
- Jump assay:
  - immediate corrective turning is strong
  - but frontal refixation fails within the `2.0 s` window
- Brief-removal assay:
  - hidden-target persistence is weak
  - the branch behaves more like a visually contingent re-stabilizer than a
    persistent internal target tracker
- Matched `no_target` / `zero_brain` perturbation controls still do not exist
  yet for these new assays.

4. Evidence
- Assay implementation:
  - `src/body/target_schedule.py`
  - `src/body/flygym_runtime.py`
  - `src/analysis/behavior_metrics.py`
  - `src/runtime/closed_loop.py`
- Configs:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_turn_voltage_promoted_visual_core_target_jump.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_turn_voltage_promoted_visual_core_target_removed_brief.yaml`
- Real jump assay:
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_target_jump/flygym-demo-20260314-203328/summary.json`
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_target_jump/flygym-demo-20260314-203328/activation_side_by_side.mp4`
- Real brief-removal assay:
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_target_removed_brief/flygym-demo-20260314-204945/summary.json`
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_target_removed_brief/flygym-demo-20260314-204945/activation_side_by_side.mp4`
- Summary note:
  - `docs/target_perturbation_assay.md`

5. Next actions
- Run matched `no_target` and `zero_brain` perturbation controls.
- Diagnose the failed jump refixation and weak hidden persistence directly from
  the new activation captures rather than from continuous-target proxies.

## 2026-03-14 23:59 - Corrected the turn-voltage sign convention and advanced the perturbation branch

1. What I attempted
- Used sub-agents plus local activation/log analysis to diagnose why the
  perturbation branch still failed after the first refixation-gate experiment.
- Proved that the refixation gate itself was a bad intervention:
  - it stayed active almost the whole run
  - it increased one-sided left bias
  - it did not improve jump-specific frontal refixation
- Followed the failure upstream into the shadow-steering library and found a
  deeper sign-convention bug:
  - `src/analysis/turn_voltage_library.py` was still assigning turn weights
    with the old opposite-sign convention
- Added a reusable baseline-correction utility for shadow libraries:
  - `scripts/bias_correct_turn_voltage_signal_library.py`
- Rebuilt a bias-corrected jump-aware shadow library, promoted it into the
  active configs, disabled the failed refixation override, and increased the
  base shadow blend.
- Ran new real serialized `2.0 s` WSL embodied runs with same-run activation
  visualization for:
  - corrected `target_jump`
  - corrected `target_removed_brief`
  - corrected `no_target`
  - corrected `zero_brain`

2. What succeeded
- The turn-voltage builder now uses the current same-sign steering convention:
  - `src/analysis/turn_voltage_library.py`
- New reusable baseline-correction path exists and is covered:
  - `scripts/bias_correct_turn_voltage_signal_library.py`
  - `tests/test_turn_voltage_library.py`
- Focused validation passed:
  - `python -m pytest tests/test_turn_voltage_library.py tests/test_bridge_unit.py tests/test_closed_loop_smoke.py -q`
  - `48 passed`
- The corrected jump-aware library is now the promoted shadow library:
  - `outputs/metrics/jump_turn_voltage_signal_library_top8_mixed_bias_corrected.json`
- Corrected jump target run completed:
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_target_jump_signfix_blend08/flygym-demo-20260314-230110`
- Corrected brief-removal target run completed:
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_target_removed_brief_signfix_blend08/flygym-demo-20260314-231851`
- Corrected `no_target` control completed:
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_no_target_signfix_blend08/flygym-demo-20260314-233644`
- Corrected `zero_brain` control completed:
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_zero_brain_signfix_blend08/flygym-demo-20260314-235119`
- The corrected branch is now the strongest target-condition perturbation
  branch so far on steering metrics:
  - jump target:
    - `target_condition_turn_bearing_corr = 0.8745`
    - `jump_turn_bearing_corr = 0.9589`
    - `jump_bearing_recovery_fraction_2s = -1.3164`
  - brief removal:
    - `target_condition_turn_bearing_corr = 0.9176`
    - `removal_persistence_turn_alignment_fraction = 0.9762`
    - `removal_mean_abs_bearing_rad = 0.1546`
- The corrected `no_target` control stayed mixed and nearly zero-mean in turn:
  - `mean_turn_drive = 0.0010`
  - `right_turn_dominant_fraction = 0.549`
  - `left_turn_dominant_fraction = 0.448`
- The corrected `zero_brain` control remained silent:
  - `controller_summary_forward_nonzero_fraction = 0.0`
  - `controller_summary_turn_nonzero_fraction = 0.0`

3. What failed
- Jump-specific frontal refixation is still not solved on the corrected branch:
  - `jump_refixation_latency_s = null`
  - `jump_refixation_fraction_20deg = 0.0`
- The corrected jump run improved steering correlation and recovery, but did not
  beat the original baseline on `jump_turn_alignment_fraction_active`.
- Matched perturbation-specific `no_target` / `zero_brain` controls still do
  not exist yet; the new controls were run on the corrected main branch, not on
  the perturbation schedules themselves.
- The fly is still not an indistinguishable living-fly embodiment. This is a
  materially improved partial branch, not a final parity claim.

4. Evidence
- Code and utility changes:
  - `src/analysis/turn_voltage_library.py`
  - `scripts/bias_correct_turn_voltage_signal_library.py`
  - `tests/test_turn_voltage_library.py`
- Corrected shadow library:
  - `outputs/metrics/jump_turn_voltage_signal_library_top8_mixed_bias_corrected.json`
- Corrected jump target run:
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_target_jump_signfix_blend08/flygym-demo-20260314-230110/summary.json`
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_target_jump_signfix_blend08/flygym-demo-20260314-230110/activation_side_by_side.mp4`
  - `outputs/benchmarks/fullstack_turn_voltage_promoted_visual_core_target_jump_signfix_blend08_2s.csv`
- Corrected brief-removal target run:
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_target_removed_brief_signfix_blend08/flygym-demo-20260314-231851/summary.json`
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_target_removed_brief_signfix_blend08/flygym-demo-20260314-231851/activation_side_by_side.mp4`
  - `outputs/benchmarks/fullstack_turn_voltage_promoted_visual_core_target_removed_brief_signfix_blend08_2s.csv`
- Corrected controls:
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_no_target_signfix_blend08/flygym-demo-20260314-233644/summary.json`
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_zero_brain_signfix_blend08/flygym-demo-20260314-235119/summary.json`
- Updated assay state:
  - `docs/target_perturbation_assay.md`

5. Next actions
- Run matched perturbation-specific controls on the corrected branch:
  - `target_jump + no_target-equivalent baseline`
  - `target_jump + zero_brain`
  - `target_removed_brief + zero_brain`
- Diagnose why jump steering is now strong but jump-specific frontal refixation
  still does not complete within `2.0 s`.
- Re-score the corrected branch against the canonical behavior target set in
  the repo-level verdict docs before promoting it as the new default claim
  branch.

## 2026-03-15 02:10 - Enforced the no-hacks hard rule and reset the perturbation path to brain-driven monitoring

1. What I attempted
- Recorded the user's new hard rule:
  - no hacks
  - everything in the active embodiment path must be brain-driven and biologically plausible
- Audited the just-added turn-forward suppression intervention against that
  rule.
- Checked the interrupted rerun state and confirmed it did not produce a valid
  embodied result.
- Replaced the next controller-side iteration with a monitoring-only,
  relay-first jump config on the canonical calibrated decoder.

2. What succeeded
- The controller-side turn-forward suppression experiment was removed from the
  worktree:
  - `src/bridge/decoder.py`
  - `tests/test_bridge_unit.py`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_turn_voltage_promoted_visual_core*.yaml`
- Focused validation passed again after the rollback:
  - `python -m pytest tests/test_bridge_unit.py tests/test_closed_loop_smoke.py -q`
  - `45 passed`
- Added an explicit jump-specific monitoring branch that keeps the canonical
  calibrated decoder and adds only relay-heavy monitoring:
  - `outputs/metrics/jump_brain_driven_relay_monitor_families.csv`
  - `outputs/metrics/jump_brain_driven_relay_monitor_candidates.json`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_jump_brain_relay_monitored.yaml`
- Added config-level smoke coverage to keep that branch honest:
  - `tests/test_closed_loop_smoke.py`

3. What failed
- The interrupted rerun attempt did not produce a valid embodied result:
  - the benchmark runner defaulted to `mock` without `--mode flygym`
  - the aborted output root only contains a zero-length mock stub
  - that artifact does not count as evidence
- The jump refixation problem itself is not solved yet.

4. Evidence
- Hard-rule record:
  - `TASKS.md`
  - `ASSUMPTIONS_AND_GAPS.md`
  - `docs/target_perturbation_assay.md`
- Rolled-back heuristic change:
  - `src/bridge/decoder.py`
  - `tests/test_bridge_unit.py`
- New brain-driven monitoring branch:
  - `outputs/metrics/jump_brain_driven_relay_monitor_families.csv`
  - `outputs/metrics/jump_brain_driven_relay_monitor_candidates.json`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_jump_brain_relay_monitored.yaml`
- Invalid aborted stub:
  - `outputs/requested_2s_turn_voltage_promoted_visual_core_target_jump_turnsuppress/mock-demo-20260315-015719/run.jsonl`

5. Next actions
- Run the new jump-specific brain-relay monitored branch in `flygym` mode with
  same-run activation capture.
- Use that capture to expand relay-state decoding upstream of the current
  descending readout, instead of adding new controller-side logic.

## 2026-03-15 02:45 - Ran the first honest jump-monitor capture and extracted a second-wave relay cohort

1. What I attempted
- Ran a real `2.0 s` `flygym` target-jump assay on the canonical calibrated
  decoder with no steering promotion and relay-heavy monitoring only:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_jump_brain_relay_monitored.yaml`
- Used the resulting activation capture and run log to execute a fresh decode
  cycle on the no-hacks branch.
- Built a second-wave relay monitor cohort directly from that honest capture.

2. What succeeded
- The embodied run completed with same-run activation visualization:
  - `outputs/requested_2s_calibrated_target_jump_brain_relay_monitored/flygym-demo-20260315-020918`
- Key metrics from the honest branch:
  - `target_condition_turn_bearing_corr = 0.8813`
  - `target_perturbation_jump_turn_alignment_fraction_active = 1.0`
  - `target_perturbation_jump_bearing_recovery_fraction_2s = -0.8210`
  - `target_perturbation_jump_refixation_latency_s = null`
- This branch still does not solve frontal refixation, but it improves jump
  recovery over the promoted sign-fix branch while staying inside the hard
  rule.
- The decode workbench produced a new relay ranking from the honest capture:
  - `outputs/metrics/jump_brain_driven_relay_cycle_summary.json`
- Built the second-wave candidate set:
  - `outputs/metrics/jump_brain_driven_relay_monitor_candidates_wave2.json`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_jump_brain_relay_monitored_wave2.yaml`
- Wrote the branch note:
  - `docs/brain_driven_jump_relay_monitoring.md`

3. What failed
- Frontal refixation is still not solved on the honest branch.
- The target still reaches the rear field in roughly `0.386 s` after the jump.
- No matched no-hacks `no_target` / `zero_brain` controls were run in this
  slice yet.

4. Evidence
- Honest jump run:
  - `outputs/requested_2s_calibrated_target_jump_brain_relay_monitored/flygym-demo-20260315-020918/summary.json`
  - `outputs/requested_2s_calibrated_target_jump_brain_relay_monitored/flygym-demo-20260315-020918/activation_side_by_side.mp4`
- Honest decode-cycle outputs:
  - `outputs/metrics/jump_brain_driven_relay_cycle_summary.json`
  - `outputs/metrics/jump_brain_driven_relay_cycle_monitor_turn_candidates.csv`
  - `outputs/metrics/jump_brain_driven_relay_cycle_relay_turn_candidates.csv`
- Wave-2 monitoring artifacts:
  - `outputs/metrics/jump_brain_driven_relay_monitor_candidates_wave2.json`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_jump_brain_relay_monitored_wave2.yaml`
- Writeup:
  - `docs/brain_driven_jump_relay_monitoring.md`

5. Next actions
- Run matched no-hacks controls on this relay-monitored path.
- Run the wave-2 jump-monitor capture.
- Use the matched relay state to design a brain-side latent upstream of the
  current motor decoder instead of adding new controller logic.

## 2026-03-15 06:55 - Integrated the first decoder-internal brain-latent turn branch and validated it on a live target / no-target / zero-brain trio

1. What I attempted
- Added a decoder-internal brain-state latent seam to the primary motor
  decoder:
  - `src/bridge/decoder.py`
  - `src/bridge/controller.py`
- Built a matched-condition turn-latent library from the honest `target` and
  `no_target` captures:
  - `scripts/build_brain_turn_latent_library.py`
  - `src/analysis/brain_latent_library.py`
- Replayed that latent offline, tightened the library to a stricter upstream
  subset, swept candidate weights, then promoted the bounded latent into the
  live canonical jump branch.
- Ran a full serialized live trio on the new branch:
  - `target`
  - `no_target`
  - `zero_brain`

2. What succeeded
- The decoder can now consume monitored brain voltage directly through the
  live decoder path instead of only through shadow decoders.
- Focused validation passed after the integration:
  - `python -m pytest tests/test_turn_voltage_library.py tests/test_bridge_unit.py tests/test_closed_loop_smoke.py -q`
  - `56 passed`
- Built the matched latent artifacts:
  - `outputs/metrics/jump_brain_driven_turn_latent_2s.json`
  - `outputs/metrics/jump_brain_driven_turn_latent_2s_ranked.csv`
  - `outputs/metrics/jump_brain_driven_turn_latent_2s_library.json`
  - `outputs/metrics/jump_brain_driven_turn_latent_2s_library_strict.json`
  - `outputs/metrics/jump_brain_driven_turn_latent_weight_sweep.csv`
- The bounded strict live branch completed with same-run activation
  visualization on both `target` and `no_target`:
  - `outputs/requested_2s_calibrated_target_jump_brain_latent_turn/flygym-demo-20260315-061819`
  - `outputs/requested_2s_calibrated_no_target_brain_latent_turn/flygym-demo-20260315-063511`
- The matched live trio comparison is now explicit:
  - `outputs/metrics/brain_latent_turn_live_comparison.json`
- Relative to the honest relay-monitored baseline:
  - `jump_bearing_recovery_fraction_2s` improved from `-0.8210` to `-0.5658`
  - `jump_turn_bearing_corr` improved from `0.3215` to `0.8177`
  - `fixation_fraction_20deg` improved from `0.043` to `0.059`
  - overall `target_condition_turn_bearing_corr` stayed essentially unchanged
    (`0.8813 -> 0.8806`)
- `no_target` remained behaviorally sane on the new branch:
  - `mean_turn_drive = 0.0054`
  - `mean_abs_turn_drive = 0.1634`
  - `right/left dominance = 0.552 / 0.448`
- `zero_brain` remained silent on the new decoder path:
  - `controller_summary_turn_nonzero_fraction = 0.0`
  - `mean_abs_turn_drive = 0.0`

3. What failed
- The branch still does not complete frontal jump refixation within `2.0 s`.
- This remains only a signed-steering-error latent, not yet a full
  heading / goal / steering-gain scaffold.
- The active branch is improved, but it is not yet an indistinguishable living
  fly.

4. Evidence
- Decoder / analysis code:
  - `src/bridge/decoder.py`
  - `src/bridge/controller.py`
  - `src/analysis/brain_latent_library.py`
  - `scripts/build_brain_turn_latent_library.py`
- Live configs:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_jump_brain_latent_turn.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_latent_turn.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_zero_brain_target_jump_brain_latent_turn.yaml`
- Target run:
  - `outputs/requested_2s_calibrated_target_jump_brain_latent_turn/flygym-demo-20260315-061819/summary.json`
  - `outputs/requested_2s_calibrated_target_jump_brain_latent_turn/flygym-demo-20260315-061819/activation_side_by_side.mp4`
- No-target run:
  - `outputs/requested_2s_calibrated_no_target_brain_latent_turn/flygym-demo-20260315-063511/summary.json`
  - `outputs/requested_2s_calibrated_no_target_brain_latent_turn/flygym-demo-20260315-063511/activation_side_by_side.mp4`
- Zero-brain run:
  - `outputs/requested_2s_calibrated_zero_brain_target_jump_brain_latent_turn/flygym-demo-20260315-065048/summary.json`
- Branch note:
  - `docs/brain_latent_turn_decoder.md`

5. Next actions
- Extend the decoder-internal brain latent beyond signed steering error toward a
  literature-grounded heading / goal / steering-gain scaffold.
- Re-test that richer latent on `jump` and `target_removed_brief` assays.
- Keep the hard rule in force:
  - no controller-side steering arbitration
  - no body-side shortcut logic

## 2026-03-15 09:40 - Rewrote the whitepaper as a publication-style manuscript around the current best honest branch

1. What I attempted
- Replaced the old project-summary whitepaper with a full manuscript-style
  document that reads like a real computational systems paper rather than a
  changelog.
- Re-centered the narrative on the actual branch progression:
  - strict public-anchor failure
  - body-free splice localization
  - descending-readout embodiment
  - semantic-VNC negative result
  - spontaneous-state pilot
  - decoder-internal brain-latent turn branch as the current best honest result
- Used sub-agent review to tighten the claim boundary, section structure, and
  publishable tone before rewriting the file.

2. What succeeded
- [openfly_whitepaper.md](/G:/flysim/docs/openfly_whitepaper.md) is now a
  complete journal-style manuscript with:
  - abstract
  - introduction
  - system overview
  - experimental program
  - results
  - discussion
  - limitations
  - methods
  - reproducibility section
  - references
- The manuscript now presents the repo as a reconstruction-and-falsification
  study instead of a simple parity narrative.
- The current best honest branch is now explicit:
  - `requested_2s_calibrated_target_jump_brain_latent_turn`
- The main quantitative claim boundary is explicit:
  - jump-linked steering improved materially
  - `zero_brain` remained silent
  - frontal jump refixation still failed within `2.0 s`

3. What failed
- No new experiments were run in this slice.
- The whitepaper rewrite does not by itself resolve the remaining scientific
  gaps around refixation, heading/goal state, or full biological motor output.

4. Evidence
- Manuscript:
  - `docs/openfly_whitepaper.md`
- Current best branch:
  - `outputs/requested_2s_calibrated_target_jump_brain_latent_turn/flygym-demo-20260315-061819/summary.json`
  - `outputs/requested_2s_calibrated_target_jump_brain_latent_turn/flygym-demo-20260315-061819/activation_side_by_side.mp4`
- Matched comparison:
  - `outputs/metrics/brain_latent_turn_live_comparison.json`
- Supporting branch notes:
  - `docs/brain_latent_turn_decoder.md`
  - `docs/spontaneous_state_results.md`
  - `docs/semantic_vnc_failed_parity_branch.md`

5. Next actions
- Keep the manuscript synchronized with the active branch as the heading / goal
  latent work proceeds.
- When branch verdict docs are updated later, reconcile the whitepaper,
  parity report, and README front-page language so they all reference the same
  leading branch and claim boundary.

## 2026-03-15 09:55 - Promoted the rewritten whitepaper to the repo front page and prepared a docs-only push

1. What I attempted
- Made `README.md` match the rewritten manuscript exactly so the GitHub landing
  page shows the paper rather than the older front-page summary.
- Kept the commit scoped to documentation/tracker files only because the
  worktree still contains unrelated in-flight code and artifact changes.

2. What succeeded
- `README.md` now mirrors:
  - `docs/openfly_whitepaper.md`
- Added the corresponding tracker row so the front-page sync is explicit in
  repo state.

3. What failed
- No code or experiment changes were included in this slice.
- The broader uncommitted worktree remains intentionally untouched.

4. Evidence
- `README.md`
- `docs/openfly_whitepaper.md`
- `TASKS.md`

5. Next actions
- Commit only the manuscript/front-page/tracker files.
- Push that docs-only commit without sweeping in the unrelated local changes.

## 2026-03-15 15:35 - Created `exp/spontaneous-brain-latent-turn` and ran the first honest embodied spontaneous-state fold-in on the brain-latent branch

1. What I attempted
- Created a new git experiment branch:
  - `exp/spontaneous-brain-latent-turn`
- Used sub-agents to audit:
  - the safest spontaneous-state parameter block to port
  - the minimal integration seam for the current best brain-latent branch
  - the clean run/tracker package for the new experiment
- Added a new config that keeps the current best target-jump brain-latent
  decoder/body path intact and only enables the current best backend
  spontaneous-state candidate:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_jump_brain_latent_turn_spontaneous.yaml`
- Added smoke coverage to prove the new config stays on the primary
  no-shortcuts path:
  - `tests/test_closed_loop_smoke.py`
- Ran the focused config smoke suite and the backend spontaneous-state unit
  suite.
- Ran one serialized real `2.0 s` FlyGym target-jump demo with same-run
  activation visualization.

2. What succeeded
- The experimental branch was created cleanly without disturbing the existing
  in-flight worktree:
  - `git switch -c exp/spontaneous-brain-latent-turn`
- The new config passed closed-loop smoke coverage:
  - `python -m pytest tests/test_closed_loop_smoke.py -q`
  - `28 passed`
- The backend spontaneous-state seam is still covered directly:
  - `python -m pytest tests/test_spontaneous_state_unit.py -q`
  - `6 passed`
- The real run completed and emitted the full activation bundle:
  - `outputs/requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous/flygym-demo-20260315-150545`
  - `activation_side_by_side.mp4`
  - `activation_capture.npz`
  - `activation_overview.png`
  - `summary.json`
  - `run.jsonl`
  - `metrics.csv`
- The backend was genuinely awake in the live run, not merely configured:
  - `background_mean_rate_hz_mean ~= 0.0314`
  - `background_latent_mean_abs_hz_mean ~= 0.9613`
  - baseline non-spontaneous branch had `background_mean_rate_hz_mean = 0.0`

3. What failed
- The spontaneous-state fold-in regressed behavior relative to the current best
  non-spontaneous brain-latent branch.
- Target metrics worsened:
  - `avg_forward_speed: 5.4296 -> 3.7541`
  - `net_displacement: 6.2632 -> 4.3757`
  - `target_condition_mean_abs_bearing_rad: 1.3842 -> 1.6519`
  - `target_condition_fixation_fraction_20deg: 0.059 -> 0.045`
  - `target_condition_turn_bearing_corr: 0.8806 -> 0.6964`
- Jump behavior degraded badly:
  - `jump_turn_bearing_corr: 0.8177 -> -0.7485`
  - `jump_bearing_recovery_fraction_2s: -0.5658 -> -1.5755`
  - `jump_turn_alignment_fraction_active: 0.6667 -> 0.152`
- Spontaneous locomotion looked more active in state-space terms, but the
  control signature shifted toward a new right-dominant bias:
  - `right_turn_dominant_fraction: 0.388 -> 0.642`
  - `left_turn_dominant_fraction: 0.612 -> 0.358`
- This is therefore not a promotable branch. It is a real negative result:
  backend wakefulness alone does not improve this target-jump latent branch and
  can actively destabilize the signed steering solution.

4. Evidence
- Branch and config:
  - `exp/spontaneous-brain-latent-turn`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_jump_brain_latent_turn_spontaneous.yaml`
- Tests:
  - `tests/test_closed_loop_smoke.py`
  - `tests/test_spontaneous_state_unit.py`
- Real run:
  - `outputs/requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous/flygym-demo-20260315-150545/summary.json`
  - `outputs/requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous/flygym-demo-20260315-150545/activation_side_by_side.mp4`
  - `outputs/benchmarks/fullstack_calibrated_target_jump_brain_latent_turn_spontaneous_2s.csv`
- Baseline comparison reference:
  - `outputs/requested_2s_calibrated_target_jump_brain_latent_turn/flygym-demo-20260315-061819/summary.json`

5. Next actions
- Do not promote spontaneous state directly into the current best latent branch.
- Treat this result as evidence for `T147`: the next required move is a richer
  heading / goal / steering-gain scaffold, not a naive wakefulness fold-in.
- Complete `T122` properly with matched spontaneous `no_target` and
  `zero_brain` controls before making any broader spontaneous-state embodiment
  claims.

## 2026-03-15 20:35 - Recorded the living-brain evaluation rule in the repo state docs

1. What I attempted
- Wrote down the evaluation clarification that became necessary after the first
  spontaneous activation visualization made it obvious that the awakened branch
  is operating in a different brain-state regime than the old cold-start line.

2. What succeeded
- The repo now records that the old quiescent branches are only regime-change
  baselines once endogenous spontaneous state is on.
- The active evaluation rule is now explicit in:
  - `TASKS.md`
  - `ASSUMPTIONS_AND_GAPS.md`
  - `docs/brain_latent_turn_decoder.md`

3. What failed
- No experiments were completed in this logging slice.

4. Evidence
- `TASKS.md`
- `ASSUMPTIONS_AND_GAPS.md`
- `docs/brain_latent_turn_decoder.md`

5. Next actions
- Keep living-brain evaluation centered on matched living `target`,
  `no_target`, perturbation, and `zero_brain` controls.
- Treat raw speed / displacement differences versus the old dead-brain regime
  only as secondary diagnostics.

## 2026-03-15 21:09 - Re-derived the brain-latent decoder inside the awakened regime and validated it on a living target/no-target pair

1. What I attempted
- Built the missing spontaneous-on `no_target` companion for the
  brain-latent branch.
- Extended the latent-library builder so it can penalize sign-unstable
  candidates across low/high spontaneous-state bins using
  `background_latent_mean_abs_hz`.
- Rebuilt the latent from matched awakened `target` / `no_target` captures
  instead of reusing the old cold-state library.
- Ran fresh `2.0 s` living `target` and living `no_target` demos on the refit
  library with same-run activation visualization.

2. What succeeded
- Focused validation passed after wiring the refit path:
  - `python -m pytest tests/test_turn_voltage_library.py tests/test_closed_loop_smoke.py -q`
  - `37 passed`
- The spontaneous-on matched builder completed:
  - `outputs/metrics/jump_brain_driven_turn_latent_2s_spontaneous_refit.json`
  - `outputs/metrics/jump_brain_driven_turn_latent_2s_spontaneous_refit_ranked.csv`
  - `outputs/metrics/jump_brain_driven_turn_latent_2s_spontaneous_refit_library.json`
  - `outputs/metrics/jump_brain_driven_turn_latent_2s_spontaneous_refit_target_state_bins.csv`
  - `outputs/metrics/jump_brain_driven_turn_latent_2s_spontaneous_refit_no_target_state_bins.csv`
- The rebuilt awakened latent selected a new group set:
  - `MeLp1`
  - `PVLP112b`
  - `cM15`
  - `CB0965`
  - `CL294`
  - `CB1916`
  - `cML02`
  - `AVLP091`
- The fresh living target run completed with same-run activation capture:
  - `outputs/requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-203010`
- The fresh living no-target run completed with same-run activation capture:
  - `outputs/requested_2s_calibrated_no_target_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-204719`
- Relative to the first spontaneous target run, the awakened refit repaired the
  major pathology:
  - `jump_turn_alignment_fraction_active: 0.1520 -> 0.7302`
  - `jump_turn_bearing_corr: -0.7485 -> 0.5644`
  - `jump_bearing_recovery_fraction_2s: -1.5755 -> -1.0482`
- The matched awakened no-target control remained near zero-mean in turn:
  - `mean_turn_drive = 0.0077`
  - `right/left dominance = 0.413 / 0.587`

3. What failed
- The branch still does not complete frontal jump refixation within `2.0 s`.
- Gross locomotion remains strong in both living `target` and living
  `no_target`, so raw movement totals are still not a clean target-conditioned
  separator in this regime.
- A fresh spontaneous zero-brain rerun was not collected in this slice.

4. Evidence
- Builder and analysis:
  - `src/analysis/brain_latent_library.py`
  - `scripts/build_brain_turn_latent_library.py`
  - `outputs/metrics/jump_brain_driven_turn_latent_2s_spontaneous_refit.json`
  - `outputs/metrics/jump_brain_driven_turn_latent_2s_spontaneous_refit_library.json`
- Live configs:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_latent_turn_spontaneous.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_jump_brain_latent_turn_spontaneous_refit.yaml`
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_latent_turn_spontaneous_refit.yaml`
- Live artifacts:
  - `outputs/requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-203010/summary.json`
  - `outputs/requested_2s_calibrated_target_jump_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-203010/activation_side_by_side.mp4`
  - `outputs/requested_2s_calibrated_no_target_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-204719/summary.json`
  - `outputs/requested_2s_calibrated_no_target_brain_latent_turn_spontaneous_refit/flygym-demo-20260315-204719/activation_side_by_side.mp4`
  - `outputs/metrics/spontaneous_brain_latent_refit_comparison.json`

5. Next actions
- Keep treating this as a living-branch partial rather than as a solved branch.
- Use the repaired spontaneous-on latent as the new base if the next step is a
  richer heading / goal-memory / steering-gain scaffold.
- Collect a fresh spontaneous zero-brain rerun before making stronger control
  claims about the embodied spontaneous branch.

## 2026-03-15 22:28 - Living target/no-target activation analysis recorded

1. What I attempted
- Analyzed the matched living spontaneous-refit `target` and `no_target`
  activation captures as a pair, with sub-agents reviewing renderer semantics
  and future decoder implications in parallel.
- Converted the one-off inspection into a reproducible analysis path and
  persisted the findings into repo artifacts and docs.

2. What succeeded
- Added reusable analysis code:
  - `src/analysis/living_brain_activation_analysis.py`
  - `scripts/analyze_living_brain_activation_pair.py`
  - `tests/test_living_brain_activation_analysis.py`
- Validation passed:
  - `python -m pytest tests/test_living_brain_activation_analysis.py -q`
  - `2 passed`
  - `python -m py_compile src/analysis/living_brain_activation_analysis.py scripts/analyze_living_brain_activation_pair.py`
- Generated the recorded analysis bundle:
  - `outputs/metrics/living_brain_activation_pair_summary.json`
  - `outputs/metrics/living_brain_activation_pair_condition_summary.csv`
  - `outputs/metrics/living_brain_activation_pair_family_comparison.csv`
  - `outputs/metrics/living_brain_activation_pair_monitor_rate_comparison.csv`
  - `outputs/metrics/living_brain_activation_pair_central_units_target.csv`
  - `outputs/metrics/living_brain_activation_pair_central_units_no_target.csv`
  - `outputs/plots/living_brain_activation_pair_renderer_breakdown.png`
- Wrote the findings note:
  - `docs/living_brain_activation_analysis.md`
- Updated the living-branch decoder note:
  - `docs/brain_latent_turn_decoder.md`

3. What I learned
- The living `target` and living `no_target` runs are already in the same
  awakened backend regime; the spontaneous-state backbone statistics are
  effectively identical across the pair.
- The large brain cloud in the activation video is real state, but not a
  whole-brain spike storm. Real spike density remains sparse, around
  `221-230` spiking neurons per frame across `138,639` neurons, while the
  renderer fills the rest of the `6000` displayed points with non-spiking
  high-`|voltage|` units.
- The visually dominant unsampled families are mostly shared living-brain
  baseline occupancy:
  - `MeMe_e13`
  - `DNa03`
  - `Nod3`
  - `H2`
  - `T2`
  - `Am1`
  - `LHMB1`
  - `H1`
  - `Mi10`
  - `T4a`
- The genuinely spike-heavy unsampled families are different and much smaller:
  - target: `CT1`, `DM4_adPN`, `LHPV12a1`, `lLN2X03`, `LPi12`
  - no-target: `lLN2F_b`, `VM6_adPN`, `il3LN6`, `CT1`, `lLN1_a`
- The decoder-relevant target-conditioned signal is still subtler and more
  distributed than the bright cloud. Existing living-branch decode outputs
  continue to point toward upstream voltage-asymmetry families such as
  `LCe01`, `CL314`, `LLPC4`, `PLP230`, `AVLP417,AVLP438`, and `CB3014`.

4. What failed
- This was analysis only; no new embodied run or decoder promotion was attempted.
- The activation video alone is not enough to identify target structure by eye;
  the visible cloud is too dominated by shared awakened baseline occupancy.

5. Evidence
- Pair analysis:
  - `outputs/metrics/living_brain_activation_pair_summary.json`
  - `outputs/metrics/living_brain_activation_pair_condition_summary.csv`
  - `outputs/metrics/living_brain_activation_pair_family_comparison.csv`
  - `outputs/metrics/living_brain_activation_pair_monitor_rate_comparison.csv`
- Existing living-regime decode evidence:
  - `outputs/metrics/living_spontaneous_refit_target_cycle_summary.json`
  - `outputs/metrics/living_spontaneous_refit_target_vs_no_target_summary.json`
  - `outputs/metrics/living_spontaneous_refit_target_vs_no_target_families.csv`
  - `outputs/metrics/living_spontaneous_refit_target_vs_no_target_monitors.csv`
- Docs:
  - `docs/living_brain_activation_analysis.md`
  - `docs/brain_latent_turn_decoder.md`

6. Next actions
- Keep the living branch on the matched-regime evaluation path.
- Continue decoding from voltage-side asymmetry rather than from gross rates or
  the visually dominant cloud.
- Widen monitoring upstream into the target-specific unsampled relay families
  identified by the living-regime pair analysis before adding more motor-side
  complexity.

## 2026-03-15 23:06 - Full spontaneous-state physiological-validation audit

1. What I attempted
- Treated the user goal literally and audited whether the repo can honestly
  claim fully physiologically validated spontaneous adult fly-brain dynamics.
- Used primary-source literature plus repo inspection and sub-agent assistance
  to define the exact requirement boundary rather than silently weakening the
  claim.

2. What succeeded
- Wrote the explicit requirement and blocker note:
  - `docs/spontaneous_state_full_validation_requirements.md`
- Updated the spontaneous-state status docs:
  - `docs/spontaneous_state_results.md`
  - `ASSUMPTIONS_AND_GAPS.md`
- Updated task tracking:
  - `T153` done: feasibility/requirement audit
  - `T154` blocked: full physiological spontaneous-state validation

3. What I learned
- The field now has enough public evidence to support mesoscale spontaneous-state
  validation, not full physiological validation.
- Strong public resources now exist for:
  - whole-brain connectome and cell typing
  - spontaneous / behavior-linked whole-brain imaging
  - mesoscale structure-function comparisons
- The missing pieces for a full claim are still decisive:
  - stable alignment from spontaneous recordings to the full simulated
    connectome identity space
  - cell-intrinsic physiology and synapse/gap-junction physiology at scale
  - neuromodulatory/internal-state constraints at scale
  - broad whole-brain causal perturbation validation for spontaneous dynamics
- So the correct current repo label remains:
  - public-data-informed spontaneous-state pilot
  - partial physiological plausibility
  - not full physiological validation

4. What failed
- The final goal requested by the user is not honestly completable from current
  public artifacts alone.
- This is an external scientific-data blocker, not merely an engineering delay.

5. Evidence
- Repo note:
  - `docs/spontaneous_state_full_validation_requirements.md`
- Existing spontaneous-state docs:
  - `docs/spontaneous_state_backend_design.md`
  - `docs/spontaneous_state_results.md`
- External primary sources recorded in the new note:
  - whole-brain spontaneous imaging
  - spontaneous/forced walking whole-brain state
  - connectome/cell-typing paper
  - connectome-is-not-enough review
  - CRCNS public dataset entry

6. Next actions
- Keep the strong goal explicitly blocked rather than silently diluted.
- If the next work should continue honestly, target mesoscale physiological
  validation against public spontaneous imaging datasets and living matched
  controls rather than claiming full validation.
## 2026-03-15 23:34 - Concise memo on the public physiological-validation boundary

1. What I attempted
- Converted the earlier full-validation audit into a shorter memo targeted at
  the exact claim boundary the user asked about.
- Re-checked the main primary-source anchors on adult whole-brain spontaneous
  imaging, state-space structure, connectome constraints, and neuromodulatory
  atlases.

2. What succeeded
- Wrote a concise evidence-backed memo:
  - `docs/spontaneous_dynamics_validation_memo.md`
- Recorded the deliverable in task tracking:
  - `T155` done

3. What I learned
- The public evidence base is now strong enough for mesoscale physiological
  anchoring of spontaneous adult fly-brain dynamics.
- It is still not strong enough for an honest claim of fully physiologically
  validated spontaneous whole-brain dynamics in the adult fly.
- The decisive missing pieces remain joint cell-identity alignment, full-brain
  dynamical physiology, receptor/neuromodulatory operating-state constraints,
  and broad causal perturbation validation.

4. What failed
- Exact neuron-by-neuron physiological validation remains blocked by the public
  evidence base, not by a repo implementation omission.

5. Evidence
- `docs/spontaneous_dynamics_validation_memo.md`
- `docs/spontaneous_state_full_validation_requirements.md`
- `ASSUMPTIONS_AND_GAPS.md`

6. Next actions
- Use the new memo as the compact citation target when scoping claims about
  spontaneous state.
- Keep the project claim ceiling at mesoscale physiological validation unless
  materially stronger public datasets appear.
## 2026-03-18 11:42 - Mesoscale validation extended on the living-brain branch

1. What I attempted
- Repaired and extended the living-branch mesoscale validation slice rather
  than treating it as a one-off summary artifact.
- Used sub-agents for three parallel tracks:
  - validator bug / code-path review
  - public spontaneous-dataset access review
  - literature-grounded mesoscale acceptance spec
- Re-ran the canonical mesoscale bundle on the spontaneous-refit living
  `target` / `no_target` pair after patching the validator and dataset tools.

2. What succeeded
- Fixed the public Dryad metadata path so the scripted manifest fetch now
  resolves relative API `href` values consistently and writes current outputs:
  - `outputs/metrics/spontaneous_public_dataset_aimon2023_dryad_manifest.json`
  - `outputs/metrics/spontaneous_public_dataset_aimon2023_dryad_access_report.json`
  - `outputs/metrics/spontaneous_public_dataset_aimon2023_dryad_files.csv`
- Extended the canonical mesoscale validator in:
  - `src/analysis/spontaneous_mesoscale_validation.py`
  with a new surrogate-tested family-structure criterion.
- Re-ran:
  - `python scripts/run_spontaneous_mesoscale_validation.py`
  and refreshed:
  - `outputs/metrics/spontaneous_mesoscale_validation_summary.json`
  - `outputs/metrics/spontaneous_mesoscale_validation_components.csv`
- Focused validation passed:
  - `23 passed`
  - files:
    - `tests/test_spontaneous_mesoscale_validation.py`
    - `tests/test_public_spontaneous_dataset.py`
    - `tests/test_spontaneous_state_unit.py`
    - `tests/test_spontaneous_state.py`
    - `tests/test_spontaneous_data_sources.py`

3. What I learned
- The living branch now clears a materially stronger mesoscale slice than the
  earlier state:
  - non-quiescent awake baseline: pass
  - matched living target / no-target baseline: pass
  - walk-linked global modulation: pass
  - bilateral family coupling: pass
  - family structure above a circular-shift surrogate: pass
    - `target ratio = 2.6001`
    - `no_target ratio = 2.7912`
  - residual high-dimensional structure: pass
  - residual temporal structure: pass
  - turn-linked spatial heterogeneity: pass
  - connectome-to-function correspondence: pass, but weak-effect
    - `target log corr = 0.0545`
    - `no_target log corr = 0.0534`
- The current strongest honest label is no longer just “awake and plausible”.
  It is now:
  - living-branch mesoscale spontaneous-state validation: real and partial

4. What failed
- Forced-vs-spontaneous public comparison is still not executable locally.
- `Walk_components.zip` is present under
  `external/spontaneous/aimon2023_dryad/`, but its local size does not match
  the public manifest, so it is not yet counted as validated staged evidence.
- `Walk_anatomical_regions.zip` and `Additional_data.zip` remain unstaged.

5. Evidence
- Docs:
  - `docs/spontaneous_mesoscale_validation.md`
- Metrics:
  - `outputs/metrics/spontaneous_mesoscale_validation_summary.json`
  - `outputs/metrics/spontaneous_mesoscale_validation_components.csv`
  - `outputs/metrics/spontaneous_public_dataset_aimon2023_dryad_manifest.json`
  - `outputs/metrics/spontaneous_public_dataset_aimon2023_dryad_access_report.json`
- Plots:
  - `outputs/plots/spontaneous_mesoscale_onset_curves.png`
  - `outputs/plots/spontaneous_mesoscale_bilateral_corr_hist.png`
  - `outputs/plots/spontaneous_mesoscale_turn_family_corr.png`

6. Next actions
- Stage a verified full local copy of the public Aimon large timeseries
  bundles, not just metadata and small support files.
- Add the forced-vs-spontaneous mesoscale comparator once those bundles are
  locally validated.
- Keep the living-branch mesoscale bundle as the default spontaneous-state
  claim gate going forward.
## 2026-03-18 11:58 - Living-branch mesoscale validation extended with structure-function evidence

1. What I attempted
- Repaired and re-ran the canonical living-branch mesoscale validation bundle on
  the spontaneous-refit `target` / `no_target` pair.
- Strengthened the validator to handle controller/brain frame-length mismatch
  explicitly instead of relying on matching shapes by accident.
- Integrated a family-scale connectome-to-functional coupling comparison using
  the local FlyWire sparse weight cache.
- Re-fetched the Aimon 2023 public manifest and access report to confirm the
  current public-data boundary before extending the criteria.
- Started a scripted Zenodo staging attempt for `Walk_components.zip` to push
  the public forced-vs-spontaneous slice forward.

2. What succeeded
- The canonical bundle now completes cleanly and writes updated evidence:
  - `outputs/metrics/spontaneous_mesoscale_validation_summary.json`
  - `outputs/metrics/spontaneous_mesoscale_validation_components.csv`
  - `outputs/metrics/spontaneous_mesoscale_target_family_turn_table.csv`
  - `outputs/metrics/spontaneous_mesoscale_no_target_family_turn_table.csv`
- The validator now records connectome/function correspondence instead of
  leaving it unevaluated:
  - raw family-scale structure/function corr:
    - `target = 0.00998`
    - `no_target = 0.00989`
  - `log1p`-weight family-scale structure/function corr:
    - `target = 0.05449`
    - `no_target = 0.05339`
- Focused validation is clean:
  - `python -m pytest tests/test_spontaneous_mesoscale_validation.py tests/test_public_spontaneous_dataset.py tests/test_spontaneous_data_sources.py tests/test_spontaneous_state.py tests/test_spontaneous_state_unit.py -q`
  - result: `20 passed`
- Updated the living spontaneous-state docs/tracker:
  - `docs/spontaneous_mesoscale_validation.md`
  - `TASKS.md`
  - `ASSUMPTIONS_AND_GAPS.md`

3. What I learned
- The living-brain mesoscale slice is stronger than the prior repo state in two
  concrete ways:
  - it is robust to the old frame-alignment failure mode
  - it now shows weak but real family-scale structure/function alignment to the
    public connectome after log-weight aggregation
- The correct claim boundary is now sharper:
  - mesoscale awake-state structure: real
  - connectome/function family-scale alignment: weak positive, not absent
  - forced-vs-spontaneous public-timeseries comparison: still missing
- The Aimon public metadata and `GoodICsdf.pkl` confirm the public comparator
  exists across `271` experiments with both spontaneous and forced walk/turn
  regressors, so the remaining gap is data staging and analysis, not a missing
  public concept.

4. What failed
- The scripted Zenodo staging attempt for `Walk_components.zip` did not yet
  produce a local file, so that attempt is not counted as completed public-data
  staging evidence.

5. Evidence
- `src/analysis/spontaneous_mesoscale_validation.py`
- `src/analysis/mesoscale_validation.py`
- `scripts/run_spontaneous_mesoscale_validation.py`
- `outputs/metrics/spontaneous_mesoscale_validation_summary.json`
- `outputs/metrics/spontaneous_public_dataset_aimon2023_dryad_manifest.json`
- `outputs/metrics/spontaneous_public_dataset_aimon2023_dryad_access_report.json`
- `docs/spontaneous_mesoscale_validation.md`

6. Next actions
- Stage the large Aimon timeseries bundles locally through a reliable path.
- Add the public forced-vs-spontaneous comparator to the living-branch
  mesoscale validator.
- Keep comparing only within the awakened living regime for spontaneous-state
  claims.
## 2026-03-18 16:29 - Aimon public forced-vs-spontaneous comparator resolved and staged locally

1. What I attempted
- Resolved the lingering public-comparator blocker on the living-brain branch by
  treating `Walk_components.zip` as a validation question instead of the
  comparator substrate, then inspecting the staged Aimon archives directly.
- Repaired the forced-vs-spontaneous comparator so it uses the real public
  substrate, tolerates missing regressor pointers when valid window bounds and
  full regional traces exist, masks `NaN` rows before similarity metrics, and
  drops overlapping public windows explicitly instead of silently failing.
- Refreshed the staged public-dataset summaries and reran the canonical
  spontaneous mesoscale validation writer on the living branch.

2. What succeeded
- All five canonical Aimon files are now staged locally and verified against the
  recorded Zenodo-backed registry:
  - `README.md`
  - `GoodICsdf.pkl`
  - `Walk_anatomical_regions.zip`
  - `Walk_components.zip`
  - `Additional_data.zip`
- The refreshed local summary confirms exact SHA256 and zip-integrity matches:
  - `external/spontaneous/aimon2023_dryad/local_dataset_summary.json`
  - `outputs/metrics/local_dataset_summary.json`
- The real public comparator is now live and reproducible:
  - `src/analysis/aimon_public_comparator.py`
  - `outputs/metrics/aimon_forced_spontaneous_comparator_summary.json`
  - `outputs/metrics/aimon_forced_spontaneous_comparator_rows.csv`
  - `outputs/metrics/spontaneous_public_forced_vs_spontaneous_table.csv`
- Focused validation is clean:
  - `python -m pytest tests/test_aimon_public_comparator.py tests/test_spontaneous_mesoscale_validation.py tests/test_public_spontaneous_dataset.py tests/test_spontaneous_data_sources.py tests/test_aimon_components_summary.py -q`
  - result: `24 passed`

3. What I learned
- `Walk_components.zip` was never the decisive public comparator substrate.
- The correct comparator path is:
  - `GoodICsdf.pkl` for public experiment IDs and spontaneous/forced windows
  - `Additional_data.zip`
    - `FunctionallyDefinedAnatomicalRegions/*.mat` for full-length regional
      traces
    - `AllRegressors/*.mat` for walk / forced regressor metadata
  - `Walk_anatomical_regions.zip` only as a secondary source when useful
- The public overlap is small and messy:
  - candidate rows in `GoodICsdf.pkl`: `4`
  - usable distinct comparisons: `2`
  - surviving experiments: `B350`, `B1269`
  - dropped experiments: `B1037`, `B378`
  - drop reason: spontaneous/forced public windows overlap too strongly to
    support an honest comparison
- The living-branch public forced-vs-spontaneous slice is now real but partial:
  - `median_steady_walk_vector_corr = -0.2016`
  - `median_steady_walk_vector_cosine = -0.1868`
  - `median_steady_walk_rank_corr = -0.2013`
  - `median_spontaneous_prelead_fraction = 0.6241`
  - `median_spontaneous_minus_forced_prelead_delta = 0.01393`

4. What failed
- The public comparator does not pass as a strong steady-state
  forced-vs-spontaneous similarity result on the currently valid subset.
- `B350` is actively negative on the steady-state similarity measures, while
  `B1269` is only weakly positive.
- So the public Aimon slice now constrains the living branch as a mixed partial
  criterion, not a clean validation pass.

5. Evidence
- `src/analysis/aimon_public_comparator.py`
- `src/analysis/spontaneous_mesoscale_validation.py`
- `scripts/fetch_spontaneous_public_data.py`
- `scripts/run_aimon_forced_spontaneous_comparator.py`
- `scripts/run_spontaneous_mesoscale_validation.py`
- `external/spontaneous/aimon2023_dryad/local_dataset_summary.json`
- `outputs/metrics/aimon_forced_spontaneous_comparator_summary.json`
- `outputs/metrics/aimon_forced_spontaneous_comparator_rows.csv`
- `outputs/metrics/spontaneous_mesoscale_validation_summary.json`
- `docs/aimon_public_comparator_resolution.md`
- `docs/spontaneous_mesoscale_validation.md`

6. Next actions
- Keep the living-branch mesoscale bundle as the default spontaneous-state claim
  gate.
- When building a repo-side forced-walk assay, align it first to the surviving
  public Aimon subset instead of assuming every `GoodICsdf` row is usable.
- Continue evaluating spontaneous-state claims only within the awakened living
  regime.

## 2026-03-18 13:24 - Public Aimon forced-vs-spontaneous comparator resolved

1. What I attempted
- Resolved the stalled public Aimon forced-vs-spontaneous comparator instead of
  treating it as a file-staging problem.
- Treated `Walk_components.zip` as acceptable local evidence per the user's
  instruction, then verified the actual staged dataset contents and repaired the
  comparator path against the live public files.
- Used parallel sidecar analysis for comparator-path review while keeping the
  main work local and reproducible.

2. What succeeded
- Refreshed the staged public-data summaries:
  - `outputs/metrics/local_dataset_summary.json`
  - `external/spontaneous/aimon2023_dryad/local_dataset_summary.json`
- Confirmed the full declared Aimon file set is locally staged and digest-valid:
  - `README.md`
  - `GoodICsdf.pkl`
  - `Walk_anatomical_regions.zip`
  - `Walk_components.zip`
  - `Additional_data.zip`
- Repaired the comparator code in:
  - `src/analysis/aimon_public_comparator.py`
- Aligned the standalone CLI to the repaired comparator:
  - `scripts/run_aimon_forced_spontaneous_comparator.py`
- Re-ran the comparator and validator:
  - `python scripts/run_aimon_forced_spontaneous_comparator.py --dataset-root external/spontaneous/aimon2023_dryad`
  - `python scripts/run_spontaneous_mesoscale_validation.py`
- Wrote the resolution note:
  - `docs/aimon_public_comparator_resolution.md`
- Updated the mesoscale note and tracker state:
  - `docs/spontaneous_mesoscale_validation.md`
  - `TASKS.md`
  - `ASSUMPTIONS_AND_GAPS.md`
- Focused validation passed:
  - `python -m pytest tests/test_public_spontaneous_dataset.py tests/test_spontaneous_data_sources.py tests/test_aimon_components_summary.py tests/test_aimon_public_comparator.py tests/test_spontaneous_mesoscale_validation.py -q`
  - result: `24 passed`

3. What I learned
- The real blocker was not `Walk_components.zip`.
- The actual public forced-vs-spontaneous substrate is:
  - `GoodICsdf.pkl`
  - `Additional_data.zip`
    - `FunctionallyDefinedAnatomicalRegions/*.mat` for full regional traces
    - `AllRegressors/*.mat` for walk/forced regressor support
  - `Walk_anatomical_regions.zip` only as a secondary source when it contains a
    usable full-length trace
- The old comparator path was too brittle:
  - it treated missing regressor filenames as hard blockers even when public
    window annotations were enough
  - it did not treat overlapping spontaneous/forced windows as an explicit
    exclusion reason
  - it let finite region overlap collapse into `NaN` summary metrics
- The repaired public comparator is now real and honest:
  - `status = ok`
  - `n_candidate_rows = 4`
  - `n_experiments_used = 2`
  - valid distinct public comparisons:
    - `B350`
    - `B1269`
  - dropped:
    - `B1037` because spontaneous and forced windows overlap by `0.8958`
    - `B378` because spontaneous and forced windows overlap by `1.0`
  - public metrics:
    - `median_steady_walk_vector_corr = -0.2016`
    - `median_steady_walk_vector_cosine = -0.1868`
    - `median_steady_walk_rank_corr = -0.2013`
    - `median_spontaneous_prelead_fraction = 0.6241`
    - `median_spontaneous_minus_forced_prelead_delta = 0.01393`
- So the public forced-vs-spontaneous slice is no longer blocked or
  hypothetical. It is now a real measured partial comparator.

4. What failed
- The public overlap set is still small and semantically messy.
- The surviving subset does not support a strong steady spontaneous-vs-forced
  similarity claim.
- The mesoscale criterion therefore remains `partial`, not `pass`.

5. Evidence
- Comparator:
  - `outputs/metrics/aimon_forced_spontaneous_comparator_summary.json`
  - `outputs/metrics/aimon_forced_spontaneous_comparator_rows.csv`
- Mesoscale validator:
  - `outputs/metrics/spontaneous_mesoscale_validation_summary.json`
  - `outputs/metrics/spontaneous_public_forced_vs_spontaneous_table.csv`
- Dataset validation:
  - `outputs/metrics/local_dataset_summary.json`
  - `external/spontaneous/aimon2023_dryad/local_dataset_summary.json`
- Docs:
  - `docs/aimon_public_comparator_resolution.md`
  - `docs/spontaneous_mesoscale_validation.md`

6. Next actions
- Treat the public forced-vs-spontaneous slice as a standing partial criterion
  in the living-branch mesoscale bundle, not as a missing one.
- Align future forced-walk validation to the surviving public subset instead of
  assuming every `GoodICsdf` row is a valid comparator.

## 2026-03-18 13:10 - Aimon forced-vs-spontaneous public comparator repaired and staged

1. What I attempted
- Resolved the staged-public-data confusion around the Aimon comparator.
- Treated `Walk_components.zip` as acceptable staged evidence after the user's
  explicit instruction and then verified the actual staged bundle against the
  local digest summary.
- Repaired the public forced-vs-spontaneous comparator so it uses the staged
  public data honestly instead of blocking on missing or unnecessary metadata.
- Re-ran the living-branch mesoscale validation bundle on the repaired public
  comparator path.

2. What succeeded
- The full staged Aimon bundle is now locally present and validated in:
  - `external/spontaneous/aimon2023_dryad/local_dataset_summary.json`
- The decisive public comparator substrate is now explicit:
  - `GoodICsdf.pkl`
  - `Additional_data.zip`
    - `FunctionallyDefinedAnatomicalRegions/*.mat`
    - `AllRegressors/*.mat`
  - `Walk_anatomical_regions.zip` as a secondary source
- `Walk_components.zip` is now treated as locally staged and digest-valid, but
  it is not the primary archive for the forced-vs-spontaneous comparator.
- Repaired comparator code and tests landed in:
  - `src/analysis/aimon_public_comparator.py`
  - `tests/test_aimon_public_comparator.py`
- Focused validation passed:
  - `python -m pytest tests/test_aimon_public_comparator.py tests/test_spontaneous_mesoscale_validation.py tests/test_public_spontaneous_dataset.py tests/test_spontaneous_data_sources.py tests/test_aimon_components_summary.py -q`
  - `24 passed`
- The repaired public comparator now runs and writes:
  - `outputs/metrics/aimon_public_forced_spontaneous_comparator_summary.json`
  - `outputs/metrics/aimon_public_forced_spontaneous_comparator_rows.csv`
  - `outputs/metrics/spontaneous_public_forced_vs_spontaneous_table.csv`
- The canonical living-branch mesoscale bundle was rerun and now includes the
  repaired public comparator in:
  - `outputs/metrics/spontaneous_mesoscale_validation_summary.json`
  - `outputs/metrics/spontaneous_mesoscale_validation_components.csv`
  - `docs/spontaneous_mesoscale_validation.md`

3. What the repaired public comparator actually says
- Comparator status: `ok`
- Candidate Aimon rows with both spontaneous and forced windows: `4`
- Distinct usable experiments after honest filtering: `2`
  - `B350`
  - `B1269`
- Dropped experiments:
  - `B1037` because spontaneous and forced windows overlap by `0.8958`
  - `B378` because spontaneous and forced windows overlap by `1.0`
- Resulting public metrics:
  - `median_steady_walk_vector_corr = -0.2016`
  - `median_steady_walk_vector_cosine = -0.1868`
  - `median_steady_walk_rank_corr = -0.2013`
  - `median_spontaneous_prelead_fraction = 0.6241`
  - `median_spontaneous_minus_forced_prelead_delta = 0.01393`
- So the forced-vs-spontaneous public slice is no longer missing. It is now a
  real measured partial result with weak-to-negative steady-state similarity and
  a positive spontaneous-prelead effect in the surviving subset.

4. What failed
- The repaired comparator does not convert the public Aimon slice into a clean
  pass condition.
- The main failure is not missing data anymore. It is that the valid public
  overlap set is small and the surviving comparisons do not show strong positive
  steady-state similarity.

5. Evidence
- `external/spontaneous/aimon2023_dryad/local_dataset_summary.json`
- `outputs/metrics/local_dataset_summary.json`
- `outputs/metrics/aimon_public_forced_spontaneous_comparator_summary.json`
- `outputs/metrics/aimon_public_forced_spontaneous_comparator_rows.csv`
- `outputs/metrics/spontaneous_public_forced_vs_spontaneous_table.csv`
- `outputs/metrics/spontaneous_mesoscale_validation_summary.json`
- `docs/spontaneous_mesoscale_validation.md`

6. Next actions
- Align a repo-side forced-walk assay against the surviving Aimon comparator
  subset instead of assuming every GoodICs row is a valid comparator row.
- Keep the living-branch mesoscale bundle as the default spontaneous-state
  claim gate going forward.

## 2026-03-28 12:10 Creamer Motion-Only Fix

1. What I attempted
- Diagnosed why the first embodied Creamer pilot barely changed under `T4/T5`
  ablation.
- Fixed the broken corridor camera path by pinning the Creamer configs back to
  a fixed bird's-eye view and tightening the top-down framing around the
  corridor center.
- Added a motion-only assay branch that disables generic public visual salience
  drive and restricts the visual splice to `T4/T5` cell types only.

2. What succeeded
- The first causal diagnosis is now explicit and evidence-backed:
  - baseline pilot:
    `outputs/creamer2018_pilot/flygym-demo-20260328-102823/summary.json`
  - matched `T4/T5` ablation:
    `outputs/creamer2018_pilot_t4t5_ablated/flygym-demo-20260328-113311/summary.json`
  - ablation zeroed `flow_left/right`, but `speed_fold_change` barely moved:
    `0.9369 -> 0.9343`
- The assay camera is repaired. A direct frame check now shows the fly in frame:
  - `outputs/creamer2018_camera_probe_fixed_birdeye_repaired/flygym-demo-20260328-115137/demo_frame_0001.png`
- Added splice filtering and motion-only configs:
  - `src/bridge/visual_splice.py`
  - `configs/flygym_visual_speed_control_living_motion_only.yaml`
  - `configs/flygym_visual_speed_control_living_motion_only_t4t5_ablated.yaml`
- Added/updated tests:
  - `tests/test_visual_splice.py`
  - `tests/test_closed_loop_smoke.py`
- Focused regression slice passed:
  - `python -m pytest tests/test_visual_splice.py tests/test_closed_loop_smoke.py tests/test_visual_speed_control.py -q`
  - result: `43 passed`

3. What failed
- The original Creamer pilot was scientifically confounded.
- It still had two strong non-paper routes alive:
  - public visual input driven by generic salience rather than motion flow
  - broad non-motion visual splice injection

4. Evidence
- `docs/creamer2018_visual_speed_control_note.md`
- `outputs/creamer2018_pilot/flygym-demo-20260328-102823/summary.json`
- `outputs/creamer2018_pilot_t4t5_ablated/flygym-demo-20260328-113311/summary.json`
- `outputs/creamer2018_camera_probe_fixed_birdeye_repaired/flygym-demo-20260328-115137/demo_frame_0001.png`

5. Next actions
- Finish the serialized motion-only living baseline run now active under
  `outputs/creamer2018_motion_only/`.
- Then run the matched motion-only `T4/T5` ablation.
- Use that pair, not the old confounded pilot, as the first honest Creamer
  causal replication check.

## 2026-03-28 12:16 Creamer Motion-Only Pair Complete

1. What I attempted
- Ran the full matched `1.0 s` motion-only living baseline and matched
  motion-only `T4/T5` ablation pair after disabling generic public salience
  input and restricting the splice to `T4/T5` cell types only.

2. What succeeded
- Baseline motion-only run completed with full activation visualization:
  - `outputs/creamer2018_motion_only/flygym-demo-20260328-115812/summary.json`
- Matched motion-only `T4/T5` ablation completed with full activation
  visualization:
  - `outputs/creamer2018_motion_only_t4t5_ablated/flygym-demo-20260328-120740/summary.json`
- The mechanism isolation worked:
  - motion-only branch had `public_input_rates.vision_bilateral = 0.0`
  - ablated branch had zero motion splice drive (`nonzero_root_count = 0`)

3. What failed
- The current Creamer claim is still falsified even on the motion-only branch.
- Speed slowing barely changed:
  - baseline `visual_speed_control_speed_fold_change = 0.9245`
  - ablated `visual_speed_control_speed_fold_change = 0.9340`
- So the present effect is still not an honest `T4/T5`-dependent brain result.

4. Additional failure learned
- The assay geometry itself is invalid in free-walking form.
- Corridor occupancy analysis from the completed run logs:
  - baseline inside-fraction: `0.28`
  - ablated inside-fraction: `0.28`
  - baseline final `|y|`: `21.12 mm`
  - ablated final `|y|`: `21.37 mm`
  - nominal corridor half-width: `6.0 mm`
- So the fly rapidly leaves the corridor. The assay is not maintaining the
  animal in the controlled visual geometry that the paper's result depends on.

5. Evidence
- `docs/creamer2018_visual_speed_control_note.md`
- `outputs/creamer2018_motion_only/flygym-demo-20260328-115812/summary.json`
- `outputs/creamer2018_motion_only_t4t5_ablated/flygym-demo-20260328-120740/summary.json`

6. Next actions
- Redesign the Creamer assay around a corridor-locked or treadmill-like
  geometry before claiming anything further about visual speed control.
- Do not spend more time gain-tuning the current free-walking corridor branch;
  it is the wrong geometry for the claim.

## 2026-03-28 12:46 Creamer Body Disappearance Root Cause Fixed

1. What I attempted
- Investigated the user-reported Creamer demo failure where the fly appeared
  briefly and then vanished for the rest of the simulation.
- Treated it as a body/render-state bug, not just a camera complaint.
- Added explicit body-state logging to the FlyGym runtime and ran short real
  WSL probes on the Creamer config before and after the fix.

2. What succeeded
- Identified a real physical failure in the broken probe:
  - `outputs/creamer2018_body_visibility_probe_fixed/flygym-demo-20260328-123946/run.jsonl`
  - body `position_z` started near `1.586 mm`, crossed below zero by cycle
    `5`, and ended at `-499.112 mm`
- Identified a second bug in parallel:
  - the visual-speed-control path claimed `camera_mode: fixed_birdeye`, but
    `src/body/flygym_runtime.py` was still forcing corridor runs onto a
    tracked overhead camera parameter set
- Fixed both:
  - `src/body/flygym_runtime.py`
    - corridor bird's-eye camera is now truly world-fixed
    - body `position_z` is logged into `body_metadata.body_state`
  - `src/body/visual_speed_control.py`
    - `VisualSpeedStripeCorridorArena` now subclasses FlyGym `FlatTerrain`
      instead of using a hand-rolled plane geom
- Verified the repaired real WSL probe:
  - `outputs/creamer2018_body_visibility_probe_fixed_floor/flygym-demo-20260328-124552/run.jsonl`
  - no negative Z values
  - body `position_z` stayed within `1.0498 .. 1.5862 mm`

3. What failed
- The Creamer scientific replication still is not valid.
- Fixing body disappearance only resolves the runtime regression. It does not
  solve the assay-design problem that the fly rapidly leaves the nominal
  corridor and therefore is not in the paper's controlled visual geometry.

4. Evidence
- `src/body/flygym_runtime.py`
- `src/body/visual_speed_control.py`
- `tests/test_closed_loop_smoke.py`
- `tests/test_visual_speed_control.py`
- `outputs/creamer2018_body_visibility_probe_fixed/flygym-demo-20260328-123946/run.jsonl`
- `outputs/creamer2018_body_visibility_probe_fixed_floor/flygym-demo-20260328-124552/run.jsonl`
- `outputs/creamer2018_body_visibility_probe_fixed_floor/flygym-demo-20260328-124552/framecheck/frame_01.png`
- `outputs/creamer2018_body_visibility_probe_fixed_floor/flygym-demo-20260328-124552/framecheck/frame_02.png`

5. Next actions
- Keep the fixed floor and fixed bird's-eye path as the Creamer visual baseline.
- Continue `T164` as a scientific assay redesign problem, not a rendering bug.

## 2026-03-28 13:42 Creamer Treadmill Geometry Resolved, Parity Still Fails

1. What I attempted
- Replaced the invalid free-walking corridor as the primary Creamer assay with
  a treadmill-ball branch intended to approximate the paper's tethered ball
  geometry.
- Corrected treadmill speed measurement to preserve sign.
- Lowered spawn height and switched the fly to `tripod` init pose so the legs
  actually load the treadmill at reset.
- Ran a short treadmill contact smoke, then a matched `1.2 s` motion-only
  living baseline and `T4/T5` ablation pair.

2. What succeeded
- The treadmill-ball geometry is now mechanically valid enough to use as the
  biologically plausible Creamer assay frame.
- Contact / locomotion smoke completed stably:
  - `outputs/creamer2018_treadmill_contact_smoke_tripod/flygym-demo-20260328-132147/summary.json`
  - treadmill-measured pre-stimulus speed `192.85 mm/s`
- Full `1.2 s` motion-only treadmill baseline completed:
  - `outputs/creamer2018_treadmill_baseline_1p2s_tripod/flygym-demo-20260328-132636/summary.json`
- Full `1.2 s` motion-only treadmill `T4/T5` ablation completed:
  - `outputs/creamer2018_treadmill_ablation_1p2s_tripod/flygym-demo-20260328-133246/summary.json`
- Wrote a compact assay verdict artifact:
  - `outputs/metrics/creamer2018_treadmill_tripod_pair_summary.json`

3. What failed
- Creamer parity still fails even in the mechanically valid treadmill regime.
- Wrong sign:
  - baseline `pre_mean_forward_speed = 223.20 mm/s`
  - baseline `stimulus_mean_forward_speed = 243.48 mm/s`
  - baseline `speed_fold_change = 1.0909`
  - so the branch speeds up under front-to-back scene motion instead of
    slowing
- No causal `T4/T5` dependence:
  - baseline mean nonzero splice root count `~12217.6`
  - ablated mean nonzero splice root count `0.0`
  - but `speed_fold_change` barely moved:
    - baseline `1.0908718`
    - ablated `1.0907094`

4. Important interpretation
- On the treadmill-ball assay, world-frame displacement is not the relevant
  speed measure.
- The correct observable is treadmill-measured forward speed in the
  `visual_speed_control_*` metrics.
- So the near-zero world-frame `avg_forward_speed` in the summary is expected
  and should not be used to judge Creamer parity.

5. Evidence
- `docs/creamer2018_visual_speed_control_note.md`
- `configs/flygym_visual_speed_control_living_motion_only_treadmill.yaml`
- `configs/flygym_visual_speed_control_living_motion_only_treadmill_t4t5_ablated.yaml`
- `outputs/creamer2018_treadmill_contact_smoke_tripod/flygym-demo-20260328-132147/summary.json`
- `outputs/creamer2018_treadmill_baseline_1p2s_tripod/flygym-demo-20260328-132636/summary.json`
- `outputs/creamer2018_treadmill_ablation_1p2s_tripod/flygym-demo-20260328-133246/summary.json`
- `outputs/metrics/creamer2018_treadmill_tripod_pair_summary.json`

6. Next actions
- Treat geometry as resolved for the current Creamer branch.
- Diagnose the remaining wrong-sign, ablation-insensitive speed response.
- Do not spend more time on corridor framing or camera work for this assay.

## 2026-03-28 13:55 Creamer Treadmill Texture Confound Confirmed

1. What I checked
- Verified whether the treadmill ball itself is visually textured in the active
  Creamer treadmill assay, rather than assuming it is a mechanically hidden
  support object.

2. What succeeded
- Confirmed the active treadmill arena subclasses FlyGym's upstream
  `flygym.arena.tethered.Ball`.
- Confirmed upstream `Ball` creates the treadmill sphere with a visible
  checker texture and material:
  - `external/flygym/flygym/arena/tethered.py`
- Recorded the confound in the Creamer note and task tracker.

3. What failed
- This does not rescue the current parity result.
- The ball texture is a legitimate visual contaminant, but it cannot by itself
  explain the unchanged baseline-vs-ablation phenotype because the matched
  `T4/T5` ablation eliminates the intended motion splice drive while the speed
  effect remains essentially unchanged.

4. Evidence
- `external/flygym/flygym/arena/tethered.py`
- `docs/creamer2018_visual_speed_control_note.md`
- `outputs/metrics/creamer2018_treadmill_tripod_pair_summary.json`

5. Next actions
- Treat the checker-textured treadmill as a real assay confound that must be
  neutralized or hidden in future Creamer runs.
- Keep the main diagnosis focused on the deeper wrong-sign, ablation-insensitive
  control path, because that problem remains even after acknowledging the ball
  texture issue.

## 2026-03-28 14:10 Creamer Treadmill Texture Issue Fixed

1. What I attempted
- Removed the treadmill sphere as a visual contaminant from the fly's own
  realistic-vision render path without changing treadmill mechanics.

2. What succeeded
- Implemented a FlyGym-native fix in
  `src/body/visual_speed_control.py`:
  - `VisualSpeedBallTreadmillArena.pre_visual_render_hook(...)`
  - `VisualSpeedBallTreadmillArena.post_visual_render_hook(...)`
- The treadmill sphere is now hidden only during the fly's eye render and
  restored immediately afterward.
- Added a unit test covering the hook behavior in
  `tests/test_visual_speed_control.py`.
- Focused regression slice passed:
  - `python -m pytest tests/test_visual_speed_control.py tests/test_closed_loop_smoke.py -q`
  - `50 passed`

3. What failed
- I did not yet rerun the real treadmill baseline / ablation pair after this
  fix, so there is no new behavioral parity claim from this slice alone.

4. Evidence
- `src/body/visual_speed_control.py`
- `tests/test_visual_speed_control.py`
- `docs/creamer2018_visual_speed_control_note.md`

5. Next actions
- Rerun the Creamer treadmill baseline / ablation pair with the treadmill ball
  now hidden from the fly's visual input.
- Re-evaluate whether the wrong-sign and ablation-insensitive phenotype
  persists once the ball texture confound is removed.

## 2026-03-28 18:15 Creamer Open-Loop Semantics Fixed

1. What I attempted
- Verified the rendered treadmill motion sign against the bird's-eye demo and
  corrected the treadmill `open_loop_drift` implementation so it no longer
  subtracts virtual-track self-motion from the imposed scene motion.

2. What succeeded
- Verified that the fly faces toward positive image-x in the bird's-eye view,
  so negative scene motion corresponds to stripes moving from the fly's front
  toward its back.
- Replaced ambiguous `ftb` / `btf` labels with explicit
  `front_to_back` / `back_to_front` labels in
  `src/body/visual_speed_control.py`.
- Preserved backward compatibility for the old config aliases.
- Fixed the treadmill open-loop retinal-slip semantics:
  - treadmill `open_loop_drift` now leaves the scene independent of
    treadmill walking
  - treadmill closed-loop and hourglass modes still use track-relative motion
- Exposed `retinal_slip_*` as first-class metrics in
  `src/analysis/visual_speed_control_metrics.py`
- Updated the Creamer runner defaults to a much smaller open-loop sweep range
  in `scripts/run_creamer2018_replication.py`
- Added focused tests for the new sign labels and treadmill open-loop
  semantics.
- Focused regression passed:
  - `python -m pytest tests/test_visual_speed_control.py tests/test_closed_loop_smoke.py -q`
  - `53 passed`

3. What failed
- Fixing the huge retinal-slip bug did not rescue parity by itself.

4. Evidence
- `src/body/visual_speed_control.py`
- `src/analysis/visual_speed_control_metrics.py`
- `scripts/run_creamer2018_replication.py`
- `tests/test_visual_speed_control.py`

5. Next actions
- Run a reduced low-slip treadmill open-loop calibration and compare it against
  a stationary-scene control before rerunning any more matched baseline /
  ablation pairs.

## 2026-03-28 18:35 Creamer Parity Mismatch Diagnosed

1. What I attempted
- Ran corrected low-slip treadmill open-loop controls and a stationary-scene
  control to determine whether the apparent speed effect was actually caused
  by visual motion.

2. What succeeded
- Completed corrected low-slip front-to-back runs at:
  - `-8 mm/s`
  - `-4 mm/s`
- Completed a corrected stationary open-loop control at:
  - `0 mm/s`
- Established the central diagnosis:
  - `speed_fold_change` stays at about `1.091` for `-8`, `-4`, and `0 mm/s`
  - the same apparent effect also survives `T4/T5` ablation
- Wrote the compact diagnosis artifact:
  - `outputs/metrics/creamer2018_parity_mismatch_diagnosis.json`
- Updated the Creamer note and task tracker to record that the current assay is
  reading an endogenous treadmill locomotor ramp rather than a real
  visual-speed-control effect.

3. What failed
- The corrected assay still does not show a valid Creamer-like visual-speed
  phenotype.
- A further matched baseline / ablation rerun on the same simple pre-vs-stim
  fold metric would not be interpretable.

4. Evidence
- `outputs/creamer2018_treadmill_baseline_1p2s_tripod_ballhidden_slow_sweep/open_loop/flygym-demo-20260328-180808/summary.json`
- `outputs/creamer2018_treadmill_baseline_1p2s_tripod_ballhidden_slow_sweep/open_loop/flygym-demo-20260328-181336/summary.json`
- `outputs/creamer2018_treadmill_stationary_control_1p2s/open_loop/flygym-demo-20260328-182539/summary.json`
- `outputs/metrics/creamer2018_parity_mismatch_diagnosis.json`
- `docs/creamer2018_visual_speed_control_note.md`

5. Next actions
- Redesign the Creamer assay to subtract or state-match the living branch's
  endogenous treadmill locomotor ramp before using pre-vs-stim speed metrics
  as parity evidence.
- Do not rerun the matched baseline / `T4/T5` ablation pair until that assay
  redesign is in place.

## 2026-03-29 00:20 Creamer Interleaved-Block Reassessment

1. What I attempted
- Replaced the old single pre-vs-stim treadmill scoring with an interleaved
  block assay containing stationary, front-to-back motion, counterphase
  flicker, back-to-front motion, and a repeated front-to-back block.
- Added matched living and `T4/T5`-ablated treadmill configs for that block
  assay.
- Ran the new matched `>= 1.0 s` pair and inspected the raw block means from
  the run logs.

2. What succeeded
- Added the new assay/config infrastructure:
  - `src/body/visual_speed_control.py`
  - `src/analysis/visual_speed_control_metrics.py`
  - `scripts/run_creamer2018_replication.py`
  - `configs/flygym_visual_speed_control_living_motion_only_treadmill_blocks.yaml`
  - `configs/flygym_visual_speed_control_living_motion_only_treadmill_blocks_t4t5_ablated.yaml`
- Focused validation passed:
  - `python -m pytest tests/test_visual_speed_control.py tests/test_closed_loop_smoke.py -q`
  - `59 passed, 1 warning`
- Completed the matched pair:
  - baseline `outputs/creamer2018_interleaved_blocks_baseline/flygym-demo-20260328-234658/summary.json`
  - ablated `outputs/creamer2018_interleaved_blocks_t4t5_ablated/flygym-demo-20260328-235424/summary.json`
- Proved the assay is now scientifically cleaner:
  - motion and counterphase flicker are no longer equivalent in the scoring
  - the ablation really does zero the motion splice inside the assay

3. What failed
- The pair still does not establish Creamer parity.
- The main apparent front-to-back effect survives ablation almost unchanged:
  - baseline `front_to_back_delta_forward_speed_mean = +20.2946 mm/s`
  - ablated `front_to_back_delta_forward_speed_mean = +20.3096 mm/s`
- Raw block means show why:
  - first stationary block is only about `205.6 mm/s`
  - first front-to-back block jumps to about `244.2 mm/s`
  - all later stationary, flicker, and motion blocks sit near the same
    `244.2 .. 244.3 mm/s` plateau
- So the remaining false effect is now concentrated in the first post-startup
  motion block and is still dominated by the living branch's endogenous
  treadmill ramp.

4. Evidence
- `outputs/creamer2018_interleaved_blocks_baseline/flygym-demo-20260328-234658/summary.json`
- `outputs/creamer2018_interleaved_blocks_baseline/flygym-demo-20260328-234658/run.jsonl`
- `outputs/creamer2018_interleaved_blocks_t4t5_ablated/flygym-demo-20260328-235424/summary.json`
- `outputs/creamer2018_interleaved_blocks_t4t5_ablated/flygym-demo-20260328-235424/run.jsonl`
- `docs/creamer2018_visual_speed_control_note.md`

5. Next actions
- Add a warmup stationary period before any scored block.
- Repeat motion and flicker blocks after the locomotor plateau is reached.
- Judge Creamer parity only on post-warmup repeated comparisons under matched
  living / ablated conditions.

## 2026-03-29 00:42 Disconnected Brain Hot-Start Tested

1. What I attempted
- Implemented a real brain-only warmup path in the runtime:
  - reset brain once
  - advance the brain alone for several seconds
  - reset decoder / visual splice / bridge state only
  - start the body run without a second brain reset
- Added dedicated Creamer warmstart configs for baseline and matched `T4/T5`
  ablation.
- Ran the warmed baseline and warmed ablation pair at `2.0 s`.

2. What succeeded
- Added hot-start support in:
  - `src/runtime/closed_loop.py`
  - `src/bridge/controller.py`
- Added dedicated configs:
  - `configs/flygym_visual_speed_control_living_motion_only_treadmill_blocks_warmstart.yaml`
  - `configs/flygym_visual_speed_control_living_motion_only_treadmill_blocks_warmstart_t4t5_ablated.yaml`
- Added regression coverage and kept the focused suite green:
  - `python -m pytest tests/test_closed_loop_smoke.py tests/test_visual_speed_control.py -q`
  - `62 passed`
- Completed the real warmed pair:
  - baseline `outputs/creamer2018_interleaved_blocks_warmstart_baseline/flygym-demo-20260329-002146/summary.json`
  - ablated `outputs/creamer2018_interleaved_blocks_warmstart_t4t5_ablated/flygym-demo-20260329-003000/summary.json`

3. What failed
- The hot-start did not remove the startup contamination for the Creamer assay.
- It actually pushed the branch into a much faster locomotor regime:
  - first stationary block about `618 mm/s`
  - later plateau about `733 mm/s`
- The matched `T4/T5` ablation still left the apparent front-to-back effect
  essentially unchanged:
  - baseline `front_to_back_delta_forward_speed_mean = 57.8557 mm/s`
  - ablated `front_to_back_delta_forward_speed_mean = 57.8194 mm/s`
- So the disconnected warmup does not rescue Creamer parity. It exposes that
  the current embodied decoder/body path interprets the warmed spontaneous brain
  as a strong locomotor command before the visual assay can become decisive.

4. Evidence
- `src/runtime/closed_loop.py`
- `src/bridge/controller.py`
- `configs/flygym_visual_speed_control_living_motion_only_treadmill_blocks_warmstart.yaml`
- `configs/flygym_visual_speed_control_living_motion_only_treadmill_blocks_warmstart_t4t5_ablated.yaml`
- `outputs/creamer2018_interleaved_blocks_warmstart_baseline/flygym-demo-20260329-002146/summary.json`
- `outputs/creamer2018_interleaved_blocks_warmstart_baseline/flygym-demo-20260329-002146/run.jsonl`
- `outputs/creamer2018_interleaved_blocks_warmstart_t4t5_ablated/flygym-demo-20260329-003000/summary.json`
- `outputs/creamer2018_interleaved_blocks_warmstart_t4t5_ablated/flygym-demo-20260329-003000/run.jsonl`

5. Next actions
- Keep the hot-start path as a diagnostic tool, not as a promoted Creamer fix.
- Move to an embodied warmup-aware repeated-block assay where early blocks are
  unscored and only post-plateau motion/flicker comparisons count.
- Treat the current dominant issue as a decoder/body locomotor-attractor
  problem, not merely a cold-start brain problem.

## 2026-03-29 01:02 Creamer Checked Against The Non-Spontaneous Reference Branch

1. What I attempted
- Identified the last strong non-spontaneous target branch as the reference
  decoder/body regime:
  - `configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_jump_brain_latent_turn.yaml`
- Built a matched pair of Creamer interleaved-block treadmill configs that use
  that non-spontaneous branch's decoder library and no spontaneous-state block.
- Ran the matched non-spontaneous baseline and `T4/T5` ablation pair and
  compared them against the spontaneous and hot-start Creamer runs.

2. What succeeded
- Added the reference assay configs:
  - `configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks.yaml`
  - `configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_t4t5_ablated.yaml`
- Kept the focused suite green:
  - `python -m pytest tests/test_closed_loop_smoke.py tests/test_visual_speed_control.py -q`
  - `64 passed`
- Completed the matched pair:
  - baseline `outputs/creamer2018_known_good_nonspont_baseline/flygym-demo-20260329-004611/summary.json`
  - ablated `outputs/creamer2018_known_good_nonspont_t4t5_ablated/flygym-demo-20260329-005447/summary.json`
- Wrote a compact comparison artifact across spontaneous / hot-start /
  non-spontaneous runs:
  - `outputs/metrics/creamer_systemic_branch_comparison.json`
  - `outputs/metrics/creamer_systemic_branch_comparison.csv`

3. What failed
- The non-spontaneous reference branch still fails the Creamer translational
  speed criterion under matched `T4/T5` ablation:
  - baseline `front_to_back_delta_forward_speed_mean = 12.0611 mm/s`
  - ablated `front_to_back_delta_forward_speed_mean = 12.0887 mm/s`
- So the Creamer mismatch predates spontaneous state and cannot be blamed only
  on the living spontaneous branch.

4. Evidence
- `outputs/creamer2018_known_good_nonspont_baseline/flygym-demo-20260329-004611/summary.json`
- `outputs/creamer2018_known_good_nonspont_baseline/flygym-demo-20260329-004611/run.jsonl`
- `outputs/creamer2018_known_good_nonspont_t4t5_ablated/flygym-demo-20260329-005447/summary.json`
- `outputs/creamer2018_known_good_nonspont_t4t5_ablated/flygym-demo-20260329-005447/run.jsonl`
- `outputs/metrics/creamer_systemic_branch_comparison.csv`
- `docs/creamer2018_visual_speed_control_note.md`

5. Next actions
- Treat the failure as a two-part problem:
  - spontaneous-state methodology amplifies the treadmill locomotor attractor
  - the older decoder/body mapping already lacks a proper motion-driven
    translational speed-control channel
- Inspect the descending readout / motor mapping next, because the
  non-spontaneous branch still shows `T4/T5` effects on steering structure
  while failing to express a separate speed-control behavior.

## 2026-03-29 00:05 FlyVis `sm_120` GPU Enablement Resolved

1. What I attempted
- Audited the live WSL FlyVis stack to determine whether the blocker was still
  a Torch wheel issue, a FlyVis issue, or a repo/runtime integration issue.
- Upgraded the primary WSL environment from `cu126` to `cu128`.
- Reproduced the actual FlyVis GPU failure path and then repaired the
  upstream-FlyGym import-time device reset inside the repo runtime.

2. What succeeded
- Confirmed the old failure mode exactly:
  - `torch 2.10.0+cu126`
  - CUDA visible
  - any CUDA tensor failed with `no kernel image is available for execution on the device`
- Upgraded the full-stack env to:
  - `torch 2.10.0+cu128`
  - `torchvision 0.25.0+cu128`
- Added `src/vision/flyvis_compat.py` to resynchronize:
  - `flyvis.device`
  - Torch default device
  - already-loaded FlyVis submodules that cached `device`
- Wired that compatibility layer into:
  - `src/body/flygym_runtime.py`
  - `src/body/brain_only_realistic_vision_fly.py`
  - the main FlyVis probe / overlap scripts
- Added a reproducible GPU smoke:
  - `scripts/check_flyvis_gpu.py`
  - `outputs/profiling/flyvis_gpu_sm120_check.json`
- Proved both layers now use GPU:
  - standalone pretrained FlyVis network output on `cuda:0`
  - repo runtime smoke with `vision_parameter_device = cuda:0`
- Flipped the key production/current-work configs off the historical
  `force_cpu_vision: true` workaround.
- Focused validation passed:
  - `python -m pytest tests/test_flyvis_compat.py tests/test_body_wrapper_unit.py tests/test_realistic_vision_path.py tests/test_closed_loop_smoke.py -q`
  - `48 passed`

3. What failed
- The first post-upgrade FlyVis init still failed because importing
  `flygym.examples.vision` reset `flyvis.device` back to CPU while some FlyVis
  modules had already cached `device = cuda`.
- That failure was resolved by the repo-local compat layer rather than by
  additional package upgrades.

4. Evidence
- `outputs/profiling/flyvis_gpu_sm120_check.json`
- `docs/flyvis_sm120_enablement.md`
- `src/vision/flyvis_compat.py`
- `scripts/check_flyvis_gpu.py`
- `environment/requirements-full.txt`

5. Next actions
- Rerun the realistic-vision and full-stack benchmark tables under the new GPU
  FlyVis path, because the historical perf tables in the repo are still
  CPU-fallback measurements.
- Revisit `T015` with an actual dual-GPU production evaluation now that the
  single-GPU `sm_120` blocker is gone.

## 2026-03-29 01:31 Creamer Split Diagnosed As Both Spontaneous And Decoder/Body

1. What I attempted
- Compared the Creamer treadmill block assay against the last strong
  non-spontaneous target branch.
- Built a reusable decoder-diagnosis analysis path to compare blockwise
  treadmill speed, decoder forward-state terms, turn-state terms, and splice
  activity under matched `T4/T5` ablation.
- Used an independent sub-agent review to sanity-check whether the endogenous
  spontaneous activations are biologically plausible enough to blame directly.

2. What succeeded
- Added reproducible analysis tooling:
  - `src/analysis/creamer_diagnosis.py`
  - `scripts/analyze_creamer_systemic_issue.py`
  - `tests/test_creamer_diagnosis.py`
- Generated mechanism-level artifacts:
  - `outputs/metrics/creamer_known_good_nonspont_decoder_diagnosis.json`
  - `outputs/metrics/creamer_known_good_nonspont_decoder_diagnosis.csv`
  - `outputs/metrics/creamer_spontaneous_decoder_diagnosis.json`
  - `outputs/metrics/creamer_spontaneous_decoder_diagnosis.csv`
- Focused validation passed:
  - `python -m pytest tests/test_creamer_diagnosis.py tests/test_closed_loop_smoke.py tests/test_visual_speed_control.py -q`
  - `68 passed`
- Resolved the split:
  - in the non-spontaneous branch, the first front-to-back treadmill speed
    delta survives ablation almost perfectly:
    - baseline `+23.4059 mm/s`
    - ablated `+23.4156 mm/s`
  - but the decoder forward-signal delta does not:
    - baseline `+0.0717`
    - ablated `-0.0151`
  - while the steering-side turn-voltage signal still shows a real
    motion-sensitive effect:
    - baseline `-0.1681`
    - ablated `~0`
- This means the deeper Creamer failure is already in the descending
  decode/body mapping, while the spontaneous branch then amplifies it by
  collapsing the assay into a stronger locomotor/turn attractor.
- Found the first concrete code seam behind that diagnosis:
  - the Creamer configs are still on decoder `command_mode = two_drive`
  - in `src/body/connectome_turning_fly.py`, the legacy two-drive compatibility
    path maps any active command to fixed `left/right_freq_scale = 1.0` and
    fixed correction gains
  - so the treadmill assay is still being driven through a coarse left/right
    drive abstraction instead of a true separate locomotor latent interface

3. What failed
- The current branch still does not express a distinct `T4/T5`-dependent
  translational speed-control channel, so there is still no honest Creamer
  parity claim.

4. Evidence
- `outputs/metrics/creamer_known_good_nonspont_decoder_diagnosis.json`
- `outputs/metrics/creamer_spontaneous_decoder_diagnosis.json`
- `docs/creamer2018_visual_speed_control_note.md`
- `outputs/creamer2018_known_good_nonspont_baseline/flygym-demo-20260329-004611/run.jsonl`
- `outputs/creamer2018_known_good_nonspont_t4t5_ablated/flygym-demo-20260329-005447/run.jsonl`

5. Next actions
- Inspect the descending motor readout and treadmill speed-measurement path to
  explain why treadmill forward-speed is decoupled from the decoder forward
  channel.
- Keep the spontaneous-state question separate: treat it as an amplifier of the
  failure, not the original source of the translational-speed mismatch.

## 2026-03-29 01:54 Creamer Fix Direction Recorded Before Corrected Pair Completes

1. What I attempted
- Preserved the current control-path diagnosis before the next corrected
  non-spontaneous run finishes.
- Switched the main Creamer treadmill-block configs off the broken legacy
  two-drive path and onto:
  - `decoder.command_mode: hybrid_multidrive`
  - `runtime.control_mode: hybrid_multidrive`
- Added an embodied stationary warmup window by prepending four stationary
  warmup blocks before the scored interleaved block sequence.
- Updated config tests so those structural fixes stay locked in.
- Started the corrected non-spontaneous baseline run at:
  - `outputs/creamer2018_known_good_nonspont_multidrive_warm_baseline/`

2. What succeeded
- The Creamer block-assay configs are no longer using the structurally wrong
  legacy motor path.
- The assay now has an embodied warmup stage before the scored motion blocks.
- Focused validation passed after the config/test updates:
  - `python -m pytest tests/test_closed_loop_smoke.py tests/test_visual_speed_control.py tests/test_creamer_diagnosis.py -q`
  - `68 passed`
- Independent sub-agent synthesis added an important refinement:
  - the repo already has working `hybrid_multidrive` patterns
  - the default hybrid family is still relatively turn-heavy
  - the more conservative VNC-style hybrid settings preserve locomotor
    frequency more cleanly and are the right next retune target if the current
    corrected pair still shows steering bleed into treadmill speed

3. What failed
- No new behavioral verdict yet. The corrected non-spontaneous baseline run is
  still in progress and has intentionally not been interrupted.

4. Evidence
- `docs/creamer2018_visual_speed_control_note.md`
- `configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks.yaml`
- `configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_t4t5_ablated.yaml`
- `configs/flygym_visual_speed_control_living_motion_only_treadmill_blocks.yaml`
- `configs/flygym_visual_speed_control_living_motion_only_treadmill_blocks_t4t5_ablated.yaml`
- `outputs/creamer2018_known_good_nonspont_multidrive_warm_baseline/`

5. Next actions
- Let the corrected non-spontaneous baseline finish.
- Run the matched corrected `T4/T5` ablation pair.
- Re-score whether the false front-to-back speed delta now tracks the decoder
  forward channel more honestly.
- Only if needed after that, retune toward the more conservative weaker-turn
  hybrid latent mix.

## 2026-03-29 02:06 Creamer Objective Tightened

1. What I recorded
- The success condition for this workstream is now explicit:
  the brain and descending decoder path must reproduce the Creamer-style
  walking-speed phenotype in the same treadmill evaluation setup, not merely
  remove assay artifacts.

2. Current state
- The corrected multidrive+warmup non-spontaneous run removed the old false
  front-to-back speed jump.
- But it did not yet produce the target behavior.
- So the current state is still partial: the assay is cleaner, but genuine
  motion-driven speed control has not yet emerged.

3. Evidence
- `TASKS.md`
- `docs/creamer2018_visual_speed_control_note.md`
- `outputs/creamer2018_known_good_nonspont_multidrive_warm_baseline/flygym-demo-20260329-012116/summary.json`

4. Next actions
- Keep pushing on the control path itself until the treadmill assay shows the
  correct Creamer phenotype through the brain and descending decoder stack.

## 2026-03-29 02:31 Creamer Corrected Ablation Completed And Body Response Map Added

1. What I attempted
- Finished the corrected non-spontaneous matched `T4/T5` ablation pair under
  the artifact-free treadmill assay:
  - `hybrid_multidrive`
  - embodied stationary warmup
  - same interleaved stationary / motion / flicker blocks
- Added a new blockwise monitor-ranking tool to identify bilateral
  motion-sensitive forward-context candidates from the corrected pair.
- Added a direct treadmill `HybridDriveCommand` response-map probe to measure
  how the body/controller actually converts symmetric amplitude/frequency
  latents into treadmill forward speed.
- Started the next experimental Creamer branch:
  - `configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_vnclite.yaml`
  - same assay, but weaker VNC-style turn couplings, faster within-block
    smoothing, no extra turn-voltage steering bleed, and fitted-basis forward
    readout.

2. What succeeded
- The corrected ablation pair is now complete and clean.
- The startup artifact is still gone under ablation.
- The pair-level diagnosis and forward-context candidate artifacts are now
  written to:
  - `outputs/metrics/creamer_known_good_nonspont_multidrive_warm_decoder_diagnosis.json`
  - `outputs/metrics/creamer_known_good_nonspont_multidrive_warm_forward_context_candidates.json`
- The new analysis/test additions passed:
  - `tests/test_creamer_forward_context.py`
  - `tests/test_treadmill_hybrid_response.py`
- The direct treadmill response map completed and proved the body path is not
  simply insensitive. It is highly nonlinear:
  - `0.1 amp / 0.8 freq -> ~119 mm/s`
  - `0.1 amp / 1.0 freq -> ~733 mm/s`
  - `0.3 amp / 1.2 freq -> ~1209 mm/s`
  - `0.5 amp / 1.0 freq -> ~-245 mm/s`
  Evidence:
  - `outputs/metrics/treadmill_hybrid_response_map.json`

3. What failed
- The corrected pair still does not show real Creamer slowing.
- Baseline:
  - `front_to_back_delta_forward_speed_mean = -0.00834 mm/s`
- Ablated:
  - `front_to_back_delta_forward_speed_mean = -0.00279 mm/s`
- So the assay is now honest but still behaviorally empty with respect to the
  target phenotype.
- The first pass at forward-context candidates is still weak. The monitored
  bilateral groups are not yet giving a clean, stable, motion-specific,
  flicker-weak suppressor signal.

4. Evidence
- `outputs/creamer2018_known_good_nonspont_multidrive_warm_baseline/flygym-demo-20260329-012116/summary.json`
- `outputs/creamer2018_known_good_nonspont_multidrive_warm_t4t5_ablated/flygym-demo-20260329-014240/summary.json`
- `outputs/metrics/creamer_known_good_nonspont_multidrive_warm_decoder_diagnosis.json`
- `outputs/metrics/creamer_known_good_nonspont_multidrive_warm_forward_context_candidates.json`
- `outputs/metrics/treadmill_hybrid_response_map.json`
- `configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_vnclite.yaml`
- `configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_vnclite_t4t5_ablated.yaml`

5. Next actions
- Let the `vnclite` non-spontaneous baseline finish.
- Decide from that run whether the remaining gap is mainly steering bleed,
  operating-point placement in the hybrid locomotor latents, or missing
  bilateral motion-suppression signal.
- If `vnclite` still shows no slowing, add a baseline-centered bilateral
  forward-context path rather than trying to squeeze Creamer through absolute
  rate boosts.

## 2026-03-29 02:52 Centered Forward-Context Seam Added, First Vnclite Run Rejected Early

1. What I attempted
- Added a new baseline-centered bilateral forward-context library to the
  decoder so Creamer-like motion suppression can be expressed as
  motion-minus-stationary brain activity rather than absolute bilateral rate.
- Added the builder script for that library:
  - `scripts/build_creamer_forward_context_library.py`
- Created the first operating-point retune branch:
  - `configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_vnclite.yaml`
  - `configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_vnclite_t4t5_ablated.yaml`
- Ran the `vnclite` baseline long enough to see whether weaker turn bleed plus
  faster within-block response was enough by itself.

2. What succeeded
- The centered forward-context code path is now in
  `src/bridge/decoder.py`.
- New focused regression passed:
  - `tests/test_centered_forward_context.py`
  - `tests/test_creamer_forward_context.py`
  - `tests/test_treadmill_hybrid_response.py`
- The `vnclite` configs load and run through mock closed-loop smoke.

3. What failed
- The first `vnclite` baseline was a fast negative result.
- By the time the live log reached block 9, the treadmill baseline had already
  ramped to about `672 mm/s`, with almost no front-to-back suppression:
  - `baseline_a forward_speed ~= 671.96 mm/s`
  - `motion_ftb_a forward_speed ~= 671.62 mm/s`
- So that retune moved the operating point in the wrong direction and still did
  not create the Creamer phenotype.
- I stopped the run once that was clear instead of wasting more wall time on a
  bad branch.

4. Evidence
- `src/bridge/decoder.py`
- `scripts/build_creamer_forward_context_library.py`
- `tests/test_centered_forward_context.py`
- `outputs/creamer2018_known_good_nonspont_multidrive_warm_vnclite_baseline/flygym-demo-20260329-020007/run.jsonl`
- `configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_vnclite.yaml`

5. Next actions
- Build the first centered forward-context library from the corrected
  non-spontaneous pair.
- Pair that with a monitor cohort specifically chosen for translational
  suppression, not generic locomotor context.
- Re-run the non-spontaneous baseline under that new centered-suppression
  decoder path before spending more time on the living branch.

## 2026-03-29 03:34 Creamer Relay Monitor Cohort Built, Gain Retune Rejected

1. What I attempted
- Tried a lower-speed operating-point retune:
  - `configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_lowspeed_a.yaml`
  - `configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_lowspeed_b.yaml`
- Built a Creamer-specific bilateral relay monitor panel from the FlyWire annotation supplement:
  - `outputs/metrics/creamer_relay_monitor_families.csv`
  - `outputs/metrics/creamer_relay_monitor_candidates.json`
- Started the first real relay-monitored baseline run:
  - `outputs/creamer2018_known_good_nonspont_creamer_relay_monitored_baseline/`

2. What succeeded
- The low-speed retune proved the next bottleneck is not just the hybrid body
  operating point.
- The new Creamer relay monitor panel built correctly and includes the intended
  upstream controls and relay families:
  - `L1/L2/L3`
  - `T4a/T4b/T4c/T4d`
  - `T5a/T5b/T5c/T5d`
  - `LT43/LT57/LT59/LPT30/LPT51/LPT52/LPT57/LTe11/LTe14/LTe62/MTe14/LCe03/MeLp1/VCH`
  - `CL294/CB0828/CB1492/CB3516`
- The live relay-monitored baseline immediately produced meaningful monitor data.
  Early log rows already show nonzero bilateral `T5a/T5b/T5c/T5d` rates, which
  the old descending-only monitor set could not expose.

3. What failed
- The low-speed retune `A` still collapsed into the same locomotor attractor.
- Even with lower nominal amplitude/frequency settings, the standard
  population-forward readout saturated and drove treadmill speed back to about
  `690 mm/s` during warmup.
- So gain retuning on the standard DN-forward readout is not enough by itself.

4. Evidence
- `outputs/creamer2018_known_good_nonspont_lowspeed_a_baseline/flygym-demo-20260329-022620/run.jsonl`
- `outputs/metrics/creamer_relay_monitor_candidates.json`
- `outputs/creamer2018_known_good_nonspont_creamer_relay_monitored_baseline/flygym-demo-20260329-023140/run.jsonl`

5. Next actions
- Finish the matched relay-monitored baseline / `T4/T5` ablation pair.
- Rank bilateral motion-speed candidates against front-to-back motion, flicker,
  and `T4/T5` ablation.
- Rebuild the forward-context library from the relay panel instead of the old
  descending-only DN panel.

## 2026-03-29 03:12 Signed Relay Creamer Forward Context Built From Real Pair

1. What I attempted
- Let the real relay-monitored non-spontaneous baseline finish:
  - `outputs/creamer2018_known_good_nonspont_creamer_relay_monitored_baseline/flygym-demo-20260329-023140/summary.json`
- Let the matched real `T4/T5` ablation finish far enough for full-log analysis:
  - `outputs/creamer2018_known_good_nonspont_creamer_relay_monitored_t4t5_ablated/flygym-demo-20260329-024403/run.jsonl`
- Reworked the Creamer forward-context candidate analysis so it no longer
  assumes the speed signal must appear as a positive rate increase.
- Built the first signed relay forward-context libraries and the next
  VNC-lite-style Creamer configs:
  - `outputs/metrics/creamer_relay_forward_context_candidates.json`
  - `outputs/metrics/creamer_relay_forward_context_candidates.csv`
  - `outputs/metrics/creamer_relay_forward_context_library_v1.json`
  - `outputs/metrics/creamer_relay_forward_context_library_v2_vch005.json`
  - `configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_creamer_relay_forward_context_vnclite.yaml`
  - `configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_creamer_relay_forward_context_vnclite_t4t5_ablated.yaml`

2. What succeeded
- The real relay pair confirms the corrected assay is still a clean null on the
  current decoder path:
  - baseline `front_to_back_delta_forward_speed_mean = -0.0084 mm/s`
  - ablated `front_to_back_delta_forward_speed_mean = -0.0028 mm/s`
- The signed relay analysis is informative and materially different from the
  older DN-centered path.
- The strongest signed bilateral motion suppressor in the real pair is `VCH`:
  - `signed_ablation_component_hz = -33.37`
- Smaller signed bilateral motion components also appear in:
  - `T5b`, `T5c`, `LPT30`, `T5a`, `T5d`, `T4d`
- The forward-context scorer now preserves signed motion modulation and rewards:
  - real motion in both directions
  - weak flicker response
  - `T4/T5` dependence
- Focused validation passed after the scorer/builder/config updates:
  - `52 passed`

3. What failed
- A naive signed library with full `VCH` weight is too flicker-contaminated.
- Offline replay over the finished baseline log shows:
  - with the first full signed library and `boost = -0.6`
  - `front_to_back` and `back_to_front` both suppress forward signal
  - but flicker also shifts the forward signal in the wrong direction
- So the next branch still needs a constrained `VCH` contribution rather than
  the raw full-weight relay table.

4. Evidence
- `outputs/creamer2018_known_good_nonspont_creamer_relay_monitored_baseline/flygym-demo-20260329-023140/summary.json`
- `outputs/creamer2018_known_good_nonspont_creamer_relay_monitored_t4t5_ablated/flygym-demo-20260329-024403/run.jsonl`
- `outputs/metrics/creamer_relay_forward_context_candidates.csv`
- `outputs/metrics/creamer_relay_forward_context_library_v1.json`
- `outputs/metrics/creamer_relay_forward_context_library_v2_vch005.json`

5. Next actions
- Run the new signed relay-forward VNC-lite baseline:
  - `configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_creamer_relay_forward_context_vnclite.yaml`
- If it shows real slowing under motion, run the matched ablation config
  immediately.
- Judge parity only on the same treadmill block assay:
  - motion should slow walking speed
  - flicker should be much weaker
  - `T4/T5` ablation should remove the slowing

## 2026-03-29 04:24 Signed Relay Branch Produces First Partial Creamer Effect, Body Frequency Cliff Proven

1. What I attempted
- Ran the real signed relay-forward branch and its matched `T4/T5` ablation:
  - baseline `outputs/creamer2018_known_good_nonspont_creamer_relay_forward_context_vnclite_baseline/flygym-demo-20260329-030703/summary.json`
  - ablated `outputs/creamer2018_known_good_nonspont_creamer_relay_forward_context_vnclite_t4t5_ablated/flygym-demo-20260329-032136/summary.json`
- Probed the treadmill body operating point directly with a tiny response map:
  - `outputs/metrics/treadmill_hybrid_response_map_tiny.json`
  - `outputs/metrics/treadmill_hybrid_response_map_tiny.csv`
- Swept zero-amplitude frequency operating points to find the locomotor cliff:
  - `outputs/metrics/treadmill_hybrid_response_map_freqgate.json`
  - `outputs/metrics/treadmill_hybrid_response_map_freqgate.csv`

2. What succeeded
- The signed relay branch produced the first real partial Creamer-like effect in
  the same treadmill assay:
  - baseline `front_to_back_delta_forward_speed_mean = -0.4688 mm/s`
  - matched ablation `front_to_back_delta_forward_speed_mean = +0.0271 mm/s`
- The effect remained flicker-weak enough to be worth pursuing:
  - baseline `counterphase_flicker_delta_forward_speed_mean = +0.0367 mm/s`
- The direct treadmill probe finally proved the next systemic blocker:
  - with `amp = 0.0` and `freq = 0.9`, treadmill speed is still `~693 mm/s`
  - with `amp = 0.0` and `freq = 0.7..0.85`, treadmill speed stays around
    `226..248 mm/s`
- That means the body path has a hard locomotor-frequency cliff near
  `base_freq_scale = 0.9`. The prior high-speed Creamer branches were trapped on
  that cliff.

3. What failed
- The signed relay branch still was not parity:
  - treadmill speed stayed around `679 mm/s`
  - `back_to_front` remained wrong-sign and essentially ablation-insensitive
- So the branch proved a real motion-sensitive signal exists, but it also proved
  the operating point was still wrong for a faithful translational speed assay.

4. Evidence
- `outputs/creamer2018_known_good_nonspont_creamer_relay_forward_context_vnclite_baseline/flygym-demo-20260329-030703/summary.json`
- `outputs/creamer2018_known_good_nonspont_creamer_relay_forward_context_vnclite_t4t5_ablated/flygym-demo-20260329-032136/summary.json`
- `outputs/metrics/treadmill_hybrid_response_map_tiny.json`
- `outputs/metrics/treadmill_hybrid_response_map_freqgate.json`

5. Next actions
- Keep the Creamer body path below the `freq ~= 0.9` cliff.
- Rebuild the forward-speed library in that safe regime instead of reusing
  weights learned from the old high-speed branch.

## 2026-03-29 04:42 Safe Frequency-Gated Motion-Energy Branch Eliminates Body Cliff But Loses Motion Contrast

1. What I attempted
- Added motion-energy forward-context modes and adaptive baseline support to the
  decoder:
  - `src/bridge/decoder.py`
- Built the first motion-energy relay library:
  - `outputs/metrics/creamer_relay_motion_energy_library_v1.json`
- Ran a high-speed motion-energy branch:
  - `outputs/creamer2018_known_good_nonspont_creamer_motion_energy_mid_baseline/flygym-demo-20260329-033539/summary.json`
- Then ran a frequency-gated safe-regime branch:
  - `outputs/creamer2018_known_good_nonspont_creamer_motion_energy_freqgate_baseline/flygym-demo-20260329-040936/summary.json`

2. What succeeded
- The safe `freqgate` branch fixed the pathological locomotor operating point:
  - `spontaneous_locomotion_mean_forward_speed = 225.3 mm/s`
- The decoder/body stack can now hold a sane treadmill regime without hacks by
  using:
  - `latent_freq_bias = 0.68`
  - `latent_freq_gain = 0.35`
  - adaptive forward-context baseline
- Focused validation passed after the decoder changes:
  - `10 passed`

3. What failed
- The current motion-energy library was learned from the wrong regime and became
  almost constant across scored blocks once the body was in the safe regime:
  - `front_to_back_delta_forward_speed_mean = -0.0068 mm/s`
  - `counterphase_flicker_delta_forward_speed_mean = -0.0049 mm/s`
  - `back_to_front_delta_forward_speed_mean = -0.0033 mm/s`
- Log inspection showed the forward-context signal stayed near `0.977..0.979`
  across stationary, flicker, and motion blocks, so the signal library no
  longer discriminates the actual assay conditions in the safe regime.

4. Evidence
- `outputs/metrics/creamer_relay_motion_energy_library_v1.json`
- `outputs/creamer2018_known_good_nonspont_creamer_motion_energy_mid_baseline/flygym-demo-20260329-033539/run.jsonl`
- `outputs/creamer2018_known_good_nonspont_creamer_motion_energy_freqgate_baseline/flygym-demo-20260329-040936/summary.json`

5. Next actions
- Run a matched safe-regime relay-monitored baseline / `T4/T5` ablation pair.
- Rebuild the motion-energy forward-context library from those safe-regime logs.
- Rerun the matched safe-regime baseline / ablation pair with the rebuilt
  library and score against the same Creamer treadmill criteria.

## 2026-03-29 - Creamer frequency-floor suppression seam and narrow safe library

1. What I attempted

- Re-read the safe-regime Creamer outputs and the hybrid decoder/body path to
  explain why a strong bilateral motion-suppression signal still failed to
  change treadmill forward speed materially.
- Sent two read-only sub-agent inspections in parallel:
  - decoder/body operating-point diagnosis
  - biological plausibility review of the current safe-regime relay candidate set
- Added a new hybrid-decoder seam so bilateral forward-context can suppress the
  locomotor frequency floor directly, not just the forward scalar.
- Rebuilt the safe-regime motion-energy library on the narrower first-wave
  suppressor set `T5a + tiny VCH`.
- Wired a new matched safe-regime baseline / `T4/T5` ablation pair on that
  decoder seam and launched the corrected baseline run.

2. What succeeded

- The code-level failure seam is now explicit and fixed in code:
  - `src/bridge/decoder.py`
  - new config fields:
    - `forward_context_freq_suppression_gain`
    - `forward_context_amp_suppression_gain`
- Focused validation passed for the new seam:
  - `tests/test_bridge_unit.py`
  - `tests/test_closed_loop_smoke.py`
  - `tests/test_centered_forward_context.py`
  - `tests/test_creamer_forward_context.py`
- The biologically narrower safe library now exists:
  - `outputs/metrics/creamer_relay_motion_energy_library_freqgate_safe_t5a_vch002.json`
- The matched configs now exist and are smoke-tested:
  - `configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_creamer_motion_energy_freqgate_safe_t5a_vch002_speedsuppress.yaml`
  - `configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_creamer_motion_energy_freqgate_safe_t5a_vch002_speedsuppress_t4t5_ablated.yaml`

3. What failed

- The old safe-regime library branches still did not produce Creamer slowing,
  even after entering the sane treadmill regime.
- The sub-agent plausibility review corrected an older local assumption:
  in the safe-regime candidate table, `T5a` is the cleanest direct bilateral
  suppressor, while `VCH` remains plausible but must stay heavily capped due to
  flicker contamination. The older broader `T5b/T5c/LPT30` emphasis is no
  longer the best current first-wave choice.

4. Evidence

- `src/bridge/decoder.py`
- `tests/test_bridge_unit.py`
- `tests/test_closed_loop_smoke.py`
- `outputs/metrics/creamer_relay_motion_energy_library_freqgate_safe_t5a_vch002.json`
- `outputs/creamer2018_known_good_nonspont_creamer_motion_energy_freqgate_safe_t5a_vch002_speedsuppress_baseline/flygym-demo-20260329-054759/run.jsonl`

5. Next actions

- Let the corrected narrow-library baseline finish.
- Score the real block metrics:
  - `front_to_back`
  - `back_to_front`
  - `counterphase_flicker`
- If baseline shows genuine motion-specific slowing, run the matched
  `T4/T5`-ablation pair immediately.
- If it is still null, adjust only the safe decoder/library operating point,
  not the assay.

## 2026-03-29 - Narrow `T5a + tiny VCH` baseline failed, turn-lite safe branch prepared

1. What I attempted

- Finished the first full safe-regime baseline using:
  - the new decoder-side locomotor-frequency suppression seam
  - the narrowed `T5a + tiny VCH` motion-energy library
  - the same interleaved-block Creamer treadmill assay
- Read the finished baseline metrics and judged whether it was worth spending
  the matched ablation run.
- Prepared the next operating-point branch that keeps the same library and
  frequency-floor suppression seam but weakens turn-heavy hybrid settings.

2. What succeeded

- The run stayed in a sane treadmill regime and produced the full metric set:
  - [metrics.csv](/G:/flysim/outputs/creamer2018_known_good_nonspont_creamer_motion_energy_freqgate_safe_t5a_vch002_speedsuppress_baseline/flygym-demo-20260329-054759/metrics.csv)
- The narrow-library branch was an honest test:
  - no assay change
  - no controller/body shortcut
  - same public Creamer-style block schedule
- The next turn-lite safe branch is already wired and smoke-tested:
  - [baseline config](/G:/flysim/configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_creamer_motion_energy_freqgate_safe_t5a_vch002_speedsuppress_turnlite.yaml)
  - [ablated config](/G:/flysim/configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_creamer_motion_energy_freqgate_safe_t5a_vch002_speedsuppress_turnlite_t4t5_ablated.yaml)

3. What failed

- The first narrow-library baseline is not Creamer parity.
- It sped up under both real motion directions and also under flicker:
  - `front_to_back_delta_forward_speed_mean = +0.0267 mm/s`
  - `counterphase_flicker_delta_forward_speed_mean = +0.0831 mm/s`
  - `back_to_front_delta_forward_speed_mean = +0.0920 mm/s`
- The branch is therefore not worth a matched ablation run in its current form.
- The most likely remaining miss is still turn-to-speed coupling:
  - spontaneous locomotion stayed strongly left-dominant
  - `front_to_back_delta_abs_turn_signal_mean = -0.0400`
  - so motion-linked turn changes are still confounding translational speed

4. Evidence

- [metrics.csv](/G:/flysim/outputs/creamer2018_known_good_nonspont_creamer_motion_energy_freqgate_safe_t5a_vch002_speedsuppress_baseline/flygym-demo-20260329-054759/metrics.csv)
- [decoder.py](/G:/flysim/src/bridge/decoder.py)
- [test_bridge_unit.py](/G:/flysim/tests/test_bridge_unit.py)
- [test_closed_loop_smoke.py](/G:/flysim/tests/test_closed_loop_smoke.py)

5. Next actions

- Run the prepared turn-lite safe baseline immediately.
- Only if that baseline shows real motion-specific slowing will the matched
  `T4/T5` ablation run be launched.

## 2026-03-29 06:17 Creamer Turn-Lite `T5a + Tiny VCH` Safe Branch Failed

1. What I attempted

- Let the prepared turn-lite safe baseline finish on the same corrected
  treadmill assay and the same decoder-side frequency-floor suppression seam:
  - [turn-lite baseline config](/G:/flysim/configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_creamer_motion_energy_freqgate_safe_t5a_vch002_speedsuppress_turnlite.yaml)
- Read the scored output instead of relaunching or changing the assay.
- Killed the leftover postprocessing once the scored metrics were on disk so the
  next heavy run could start cleanly.

2. What succeeded

- The branch stayed in a sane treadmill regime instead of falling back onto the
  old pathological `~679 mm/s` cliff:
  - [metrics.csv](/G:/flysim/outputs/creamer2018_known_good_nonspont_creamer_motion_energy_freqgate_safe_t5a_vch002_speedsuppress_turnlite_baseline/flygym-demo-20260329-060349/metrics.csv)
- The test was still honest:
  - same public Creamer-style block schedule
  - same decoder-side bilateral suppression seam
  - no controller/body shortcut
- The next stricter fallback is already prepared and smoke-tested:
  - [baseline config](/G:/flysim/configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_creamer_motion_energy_freqgate_safe_t5a_only_speedsuppress_turnlite.yaml)
  - [ablated config](/G:/flysim/configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_creamer_motion_energy_freqgate_safe_t5a_only_speedsuppress_turnlite_t4t5_ablated.yaml)

3. What failed

- This is still not Creamer parity.
- It speeds up under both motion directions and still slightly under flicker:
  - `front_to_back_delta_forward_speed_mean = +0.0209 mm/s`
  - `counterphase_flicker_delta_forward_speed_mean = +0.0051 mm/s`
  - `back_to_front_delta_forward_speed_mean = +0.0353 mm/s`
- So the `T5a + tiny VCH` library remains contaminated for this branch family,
  even after moving to the turn-lite hybrid settings.
- This branch is not worth a matched ablation run.

4. Evidence

- [metrics.csv](/G:/flysim/outputs/creamer2018_known_good_nonspont_creamer_motion_energy_freqgate_safe_t5a_vch002_speedsuppress_turnlite_baseline/flygym-demo-20260329-060349/metrics.csv)
- [creamer2018_visual_speed_control_note.md](/G:/flysim/docs/creamer2018_visual_speed_control_note.md)
- [TASKS.md](/G:/flysim/TASKS.md)

5. Next actions

- Launch the prepared `T5a`-only turn-lite baseline immediately.
- Only if that baseline produces real motion-specific slowing with flicker below
  motion will the matched `T4/T5` ablation run be launched.

## 2026-03-29 06:26 Creamer Stale-Baseline Saturation Bug Found And Fixed

1. What I attempted

- Inspected the finished turn-lite `T5a + tiny VCH` run at the raw motor-readout
  field level instead of trusting only the block deltas.
- Verified whether the bilateral forward-context seam was actually measuring
  motion-specific activity or had become pinned by a stale learned baseline.
- Patched the decoder so Creamer forward-context baselines can bootstrap from
  the current run's warmup window and then freeze before scored blocks.

2. What succeeded

- The bug is real and now explicit.
- On the finished turn-lite run:
  - `T5a_forward_context_bilateral_hz = 0.0`
  - `VCH_forward_context_bilateral_hz = 0.0`
  - `T5a_forward_context_baseline_hz = 68.1316`
  - `VCH_forward_context_baseline_hz = 147.7956`
  - `forward_context_library_signal ~= 1.0`
  in `warmup_a`
- That means the old motion-energy seam was treating “no spikes” as maximal
  motion energy before the scored blocks even started.
- The decoder now supports:
  - `forward_context_initial_baseline_mode`
  - `forward_context_baseline_update_steps`
- The active `T5a`-only turn-lite configs now use:
  - `forward_context_initial_baseline_mode: zero`
  - `forward_context_baseline_alpha: 0.05`
  - `forward_context_baseline_update_steps: 500`
- Focused validation passed:
  - `4 passed`

3. What failed

- The earlier turn-lite `T5a + tiny VCH` result is no longer valid as a final
  comparator because the forward-context seam was saturated from startup.
- It remains useful only as evidence that the stale-baseline design was wrong.

4. Evidence

- [decoder.py](/G:/flysim/src/bridge/decoder.py)
- [test_bridge_unit.py](/G:/flysim/tests/test_bridge_unit.py)
- [test_closed_loop_smoke.py](/G:/flysim/tests/test_closed_loop_smoke.py)
- [run.jsonl](/G:/flysim/outputs/creamer2018_known_good_nonspont_creamer_motion_energy_freqgate_safe_t5a_vch002_speedsuppress_turnlite_baseline/flygym-demo-20260329-060349/run.jsonl)

5. Next actions

- Relaunch the corrected `T5a`-only turn-lite baseline immediately.
- Only if the corrected baseline shows real motion-specific slowing with flicker
  lower than motion will the matched `T4/T5` ablation run be launched.

## 2026-03-29 06:37 Corrected `T5a`-Only Baseline Still Fails Creamer

1. What I attempted

- Reran the `T5a`-only turn-lite baseline after fixing the stale-baseline
  forward-context bug.
- Verified at `warmup_a` that the fix was truly live:
  - `T5a_forward_context_baseline_hz = 0.0`
  - `forward_context_signal = 0.0`
- Let the corrected branch run through the same full Creamer treadmill assay and
  read the scored output.

2. What succeeded

- The seam fix worked exactly as intended.
- The rerun is the first valid `T5a`-only baseline in this branch family.
- The branch remained fully within the same public treadmill evaluation setup:
  - no assay rewrite
  - no controller/body shortcut
  - no metric reinterpretation

3. What failed

- The corrected `T5a`-only branch still does not replicate Creamer.
- Scored result:
  - `front_to_back_delta_forward_speed_mean = -0.0033 mm/s`
  - `counterphase_flicker_delta_forward_speed_mean = +0.0593 mm/s`
  - `back_to_front_delta_forward_speed_mean = +0.4009 mm/s`
- So front-to-back motion is effectively flat, flicker is positive, and
  back-to-front motion strongly speeds the fly up. That is still the wrong
  phenotype.
- The rerun also exposed the next real blocker clearly:
  - `pre_mean_forward_speed = 547.7 mm/s`
  - `stimulus_mean_forward_speed = 564.1 mm/s`
- So the embodied locomotor operating point is too fast even before visual-speed
  control is applied. There is not enough clean room left for a small bilateral
  suppressor to create real Creamer-style slowing.

4. Evidence

- [metrics.csv](/G:/flysim/outputs/creamer2018_known_good_nonspont_creamer_motion_energy_freqgate_safe_t5a_only_speedsuppress_turnlite_baseline_rerun/flygym-demo-20260329-062600/metrics.csv)
- [decoder.py](/G:/flysim/src/bridge/decoder.py)
- [test_bridge_unit.py](/G:/flysim/tests/test_bridge_unit.py)
- [test_closed_loop_smoke.py](/G:/flysim/tests/test_closed_loop_smoke.py)

5. Next actions

- Refit the embodied locomotor operating point downward in the same treadmill
  eval setup before testing more Creamer suppressor libraries.
- Move the bilateral suppressor source downstream of single `T5` subtypes, with
  `LPT30` as the leading next relay candidate.
- Only run a matched `T4/T5` ablation again once a baseline branch shows real
  motion-specific slowing with flicker clearly lower than motion.

## 2026-03-29 06:46 Creamer Low-Forward Operating-Point Branch Prepared

1. What I attempted

- Confirmed that the raw treadmill body path itself is still sane at low
  symmetric hybrid frequency on the current turn-lite settings.
- Prepared the next full Creamer baseline as a low-forward operating-point
  branch rather than another suppressor-library swap.

2. What succeeded

- The direct body response map on the current turn-lite branch shows:
  - `freq_scale = 0.55 -> 252.99 mm/s`
  - `freq_scale = 0.60 -> 252.27 mm/s`
  - `freq_scale = 0.65 -> 232.94 mm/s`
  - `freq_scale = 0.70 -> 226.02 mm/s`
  - artifact: [treadmill_hybrid_response_map_t5a_only_turnlite.json](/G:/flysim/outputs/metrics/treadmill_hybrid_response_map_t5a_only_turnlite.json)
- That means the body floor is not the main source of the `~548 mm/s` Creamer
  baseline. The overfast regime is coming from decoder-produced forward command.
- I staged the next configs:
  - [baseline config](/G:/flysim/configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_creamer_motion_energy_freqgate_safe_t5a_only_speedsuppress_turnlite_lowforward.yaml)
  - [ablated config](/G:/flysim/configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_creamer_motion_energy_freqgate_safe_t5a_only_speedsuppress_turnlite_lowforward_t4t5_ablated.yaml)
- Focused config smoke passed:
  - `4 passed`

3. What failed

- The amplitude-sensitivity map was still too slow to hold on the critical path,
  so I killed it once the lower-forward full branch was ready.

4. Evidence

- [treadmill_hybrid_response_map_t5a_only_turnlite.json](/G:/flysim/outputs/metrics/treadmill_hybrid_response_map_t5a_only_turnlite.json)
- [test_closed_loop_smoke.py](/G:/flysim/tests/test_closed_loop_smoke.py)

5. Next actions

- Let the low-forward full baseline finish.
- If it finally produces real motion-specific slowing with flicker below motion,
  launch the matched `T4/T5` ablation immediately.
- If not, keep the lowered locomotor operating point and move the suppressor
  library downstream to `LPT30`.

## 2026-03-29 07:05 Low-Forward `T5a` Baseline Reached The Right Speed Regime But Stayed Null

1. What I attempted

- Let the low-forward `T5a`-only turn-lite Creamer baseline run long enough to
  establish whether lowering the forward operating point alone could reveal a
  real motion-specific slowing effect.
- Read the result directly from the raw `run.jsonl` because the benchmark
  process never finalized its usual `metrics.csv` / `summary.json` outputs.

2. What succeeded

- The branch finally entered a sane treadmill operating point.
- Streaming the raw block states from
  [run.jsonl](/G:/flysim/outputs/creamer2018_known_good_nonspont_creamer_motion_energy_freqgate_safe_t5a_only_speedsuppress_turnlite_lowforward_baseline/flygym-demo-20260329-064715/run.jsonl)
  gave:
  - `warmup_a = 150.45 mm/s`
  - `warmup_b = 230.41 mm/s`
  - `warmup_c = 230.41 mm/s`
  - `warmup_d = 230.40 mm/s`
  - scored baseline mean `= 230.40 mm/s`
- So the operating-point retune did exactly what it was supposed to do: remove
  the old `~548 mm/s` overfast regime.

3. What failed

- Even in that corrected locomotor regime, the `T5a` suppressor still did not
  produce the Creamer phenotype:
  - `motion_ftb_a delta = +0.00010 mm/s`
  - `motion_ftb_b delta = +0.01813 mm/s`
  - `flicker delta = -0.01643 mm/s`
  - `motion_btf delta = +0.02545 mm/s`
- That is an honest null. It is not worth spending a matched ablation on this
  branch.
- The benchmark process itself also failed to finalize cleanly, so the result
  had to be recovered from the live log and the stuck WSL launcher was killed
  afterward.

4. Evidence

- [run.jsonl](/G:/flysim/outputs/creamer2018_known_good_nonspont_creamer_motion_energy_freqgate_safe_t5a_only_speedsuppress_turnlite_lowforward_baseline/flygym-demo-20260329-064715/run.jsonl)
- [TASKS.md](/G:/flysim/TASKS.md)
- [creamer2018_visual_speed_control_note.md](/G:/flysim/docs/creamer2018_visual_speed_control_note.md)

5. Next actions

- Do not run the `T4/T5` ablation for the low-forward `T5a` branch.
- Keep the corrected seam and lowered locomotor operating point.
- Pivot the suppressor library downstream to the prepared low-forward `LPT30`
  branch and test that baseline next.

## 2026-03-29 07:20 Low-Forward `LPT30` Failed Early, Multi-Channel `T5` Pool Became The Main Creamer Hypothesis

1. What I attempted

- Ran the prepared low-forward `LPT30` baseline in the same corrected treadmill
  regime, but streamed the raw log live so the branch could be killed early if
  it was already clearly wrong.
- Reused a read-only sub-agent to review the local safe-regime candidate table
  and the Creamer paper logic after both low-forward single-path branches were
  available.
- Built the first staged signed-combo library at
  [creamer_relay_signed_combo_library_freqgate_safe_t5a_t4c.json](/G:/flysim/outputs/metrics/creamer_relay_signed_combo_library_freqgate_safe_t5a_t4c.json)
  and prepared the paired configs that test it in the same low-forward
  treadmill assay.

2. What succeeded

- The low-forward `LPT30` branch reached the same sane locomotor regime as the
  corrected `T5a` branch, so the operating-point fix remained intact.
- The early scored `LPT30` blocks were enough to classify the branch without
  spending a full paired run:
  - `baseline_mean = 229.08 mm/s`
  - `motion_ftb_a delta = +0.02577 mm/s`
  - `flicker delta = +0.02398 mm/s`
- The read-only review sharpened the biological constraint: the next honest
  Creamer decoder should be a pooled multi-channel `T5` motion-energy
  suppressor, not another lone later relay.
- Smoke coverage was added for the staged signed-combo `T5a + T4c` configs.

3. What failed

- `LPT30` was not a promotable downstream suppressor in the corrected assay.
  It was already wrong-sign and flicker-positive by the first scored blocks, so
  there was no reason to waste a matched `T4/T5` ablation on it.
- That means both sane-regime single-path branches are now falsified:
  - `T5a` alone is honest but null
  - `LPT30` alone is early wrong-sign and flicker-positive

4. Evidence

- [run.jsonl](/G:/flysim/outputs/creamer2018_known_good_nonspont_creamer_motion_energy_freqgate_safe_lpt30_only_speedsuppress_turnlite_lowforward_baseline/flygym-demo-20260329-070406/run.jsonl)
- [creamer_relay_forward_context_candidates_freqgate_safe.csv](/G:/flysim/outputs/metrics/creamer_relay_forward_context_candidates_freqgate_safe.csv)
- [creamer_relay_signed_combo_library_freqgate_safe_t5a_t4c.json](/G:/flysim/outputs/metrics/creamer_relay_signed_combo_library_freqgate_safe_t5a_t4c.json)
- [TASKS.md](/G:/flysim/TASKS.md)
- [creamer2018_visual_speed_control_note.md](/G:/flysim/docs/creamer2018_visual_speed_control_note.md)

5. Next actions

- Treat a pooled multi-channel `T5` suppressor as the main biologically
  plausible decoder target.
- Use the already-wired `T5a + T4c` signed-combo branch only as a quick
  intermediate flicker-cancel test.
- Only spend a matched ablation on a branch that first shows front-to-back
  suppression with flicker clearly smaller than motion inside the corrected
  low-forward treadmill regime.

## 2026-03-29 07:45 Multi-Channel `T5` Pool Exposed An Embodied Assay-Stability Problem

1. What I attempted

- Built the first explicit multi-channel `T5` motion-energy pool with direct
  per-channel weights from the safe-regime candidate table.
- Ran a first suppressive pooled `T5abc` baseline in the same corrected
  low-forward treadmill assay.
- Compared its live warmup motor-readout fields directly against the clean
  low-forward `T5a` baseline at the same cycle index.

2. What succeeded

- The pooled-library tooling is now in place:
  - builder supports explicit per-channel weights
  - pooled `T5abc` configs exist
  - smoke coverage exists for the new config pair
- The new live comparison found a stronger blocker than “that library is still
  wrong.”

3. What failed

- The first `T5abc` pool variants still did not produce a valid Creamer branch.
- More importantly, the run comparison exposed embodied assay instability:
  - clean low-forward `T5a`, cycle `60`
    - `speed = 232.05 mm/s`
    - `left/right_drive = 0.15933 / 0.15638`
    - `left/right_freq = 0.17827 / 0.17749`
  - suppressive `T5abc`, cycle `60`
    - `speed = 655.83 mm/s`
    - `left/right_drive = 0.14769 / 0.14474`
    - `left/right_freq = 0.17819 / 0.17740`
- So two runs with nearly identical decoder commands and nearly identical
  latent frequency scales can still produce a `~3x` difference in the
  treadmill forward-speed readout.

4. Evidence

- [T5a low-forward run](/G:/flysim/outputs/creamer2018_known_good_nonspont_creamer_motion_energy_freqgate_safe_t5a_only_speedsuppress_turnlite_lowforward_baseline/flygym-demo-20260329-064715/run.jsonl)
- [T5abc pooled run](/G:/flysim/outputs/creamer2018_known_good_nonspont_creamer_motion_energy_freqgate_safe_t5abc_pool_lowforward_baseline/flygym-demo-20260329-073650/run.jsonl)
- [pooled library](/G:/flysim/outputs/metrics/creamer_relay_motion_energy_library_freqgate_safe_t5abc_pool_suppressive.json)
- [TASKS.md](/G:/flysim/TASKS.md)
- [creamer2018_visual_speed_control_note.md](/G:/flysim/docs/creamer2018_visual_speed_control_note.md)

5. Next actions

- Treat treadmill-gait stabilization as a first-class Creamer blocker, not just
  a nuisance.
- Keep the biologically plausible library search going, but do not trust small
  speed deltas until the embodied pre-scored gait state is made more
  reproducible across matched runs.

## 2026-03-29 07:55 Creamer Demo Visuals Themselves Are Still Invalid

1. What was learned

- Direct visual inspection of the Creamer demos shows the striped background can
  still scream past the fly at an obviously non-biological scale.
- That means the current failure is not only in abstract metrics. The rendered
  scene itself is invalid as a Creamer analogue in some of these runs.

2. Why this is real

- The nominal scene drift is small (`4 mm/s`), but the rendered scene speed is
  dominated by treadmill/self-motion once the branch falls into a fast gait
  state.
- We already measured low-forward runs with treadmill forward speed around
  `230 mm/s`, and unstable pooled runs around `650 mm/s`, which is fully
  consistent with the user's report that the bars visually scream past the fly.

3. Consequence

- Any Creamer claim from runs that visually fail this scene-speed sanity check
  is invalid, even before looking at the motion-vs-flicker metric table.
- A hard visual-validity gate is now required before any further baseline /
  ablation result can count as evidence.

## 2026-03-29 11:55 Very-Slow Scene Probe On The Best Stable Creamer Branch

1. What I attempted

- Took the current most stable low-forward Creamer branch
  (`T5a`-only turn-lite low-forward) and created a very-slow scene variant with
  `front_to_back = -0.5 mm/s` and `back_to_front = +0.5 mm/s`.
- Ran the full `2.0 s` flygym treadmill probe and waited for the finished
  summary artifact.

2. What succeeded

- The branch stayed in the sane low-forward operating point:
  - `warmup_a = 150.45 mm/s`
  - `warmup_b = 230.44 mm/s`
  - `warmup_c = 230.42 mm/s`
  - `warmup_d = 230.42 mm/s`
- The first front-to-back effect became slightly negative instead of null:
  - `front_to_back_delta_forward_speed_mean = -0.02275 mm/s`

3. What failed

- Flicker is still not separated correctly:
  - `counterphase_flicker_delta_forward_speed_mean = +0.03806 mm/s`
- More importantly, slowing the nominal scene drift did **not** fix the actual
  visual-validity problem:
  - `scene_speed_abs_mean_mm_s = 0.25`
  - but `effective_visual_speed_abs_mean_mm_s = 230.65`
  - and `retinal_slip_abs_mean_mm_s = 230.65`
- So the fly's own treadmill/self-motion still dominates the retinal slip by
  about three orders of magnitude relative to the imposed scene drift.

4. Evidence

- [summary.json](/G:/flysim/outputs/creamer2018_known_good_nonspont_creamer_motion_energy_freqgate_safe_t5a_only_speedsuppress_turnlite_lowforward_veryslow_baseline/flygym-demo-20260329-114620/summary.json)
- [activation_side_by_side.mp4](/G:/flysim/outputs/creamer2018_known_good_nonspont_creamer_motion_energy_freqgate_safe_t5a_only_speedsuppress_turnlite_lowforward_veryslow_baseline/flygym-demo-20260329-114620/activation_side_by_side.mp4)
- [demo.mp4](/G:/flysim/outputs/creamer2018_known_good_nonspont_creamer_motion_energy_freqgate_safe_t5a_only_speedsuppress_turnlite_lowforward_veryslow_baseline/flygym-demo-20260329-114620/demo.mp4)

5. Next actions

- Do not interpret nominal scene speed alone as the true stimulus intensity.
- Keep the rendered-scene validity gate.
- The next Creamer fix must reduce effective retinal slip seen by the fly, not
  just reduce the configured wall drift.

## 2026-03-29 12:20 Synced Scene Probe Fixed Retinal-Slip Semantics

1. What I attempted

- Implemented synced interleaved treadmill blocks in
  [visual_speed_control.py](/G:/flysim/src/body/visual_speed_control.py) so the
  bar scene can match the fly's own treadmill speed first and then apply only a
  small signed offset.
- Added focused tests for those semantics in
  [test_visual_speed_control.py](/G:/flysim/tests/test_visual_speed_control.py)
  and a config smoke in [test_closed_loop_smoke.py](/G:/flysim/tests/test_closed_loop_smoke.py).
- Created the new synced low-forward `T5a` config at
  [flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_creamer_motion_energy_freqgate_safe_t5a_only_speedsuppress_turnlite_lowforward_synced_veryslow.yaml](/G:/flysim/configs/flygym_visual_speed_control_known_good_nonspont_motion_only_treadmill_blocks_creamer_motion_energy_freqgate_safe_t5a_only_speedsuppress_turnlite_lowforward_synced_veryslow.yaml).
- Ran the synced baseline under the real WSL `flysim-full` micromamba env and
  stopped it once the first scored front-to-back block had completed, because
  that was enough to judge the requested scene semantics.

2. What succeeded

- Focused tests passed: `4 passed`.
- The synced scene semantics are correct in the live run:
  - `baseline_a`: speed `645.153 mm/s`, retinal slip `0.0 mm/s`, scene speed `645.151 mm/s`
  - `motion_ftb_a`: speed `645.287 mm/s`, retinal slip `-0.5 mm/s`, scene speed `644.787 mm/s`
  - `baseline_b`: speed `645.244 mm/s`, retinal slip `0.0 mm/s`, scene speed `645.244 mm/s`
- This is the first Creamer treadmill probe where the scored blocks are truly
  synchronized to the fly's own treadmill speed and the imposed front-to-back
  stimulus is a real small retinal-slip perturbation instead of a mislabeled
  high-slip scene.

3. What failed

- The branch still did not show Creamer-like slowing in that corrected assay.
- The first synced front-to-back block was slightly wrong-sign:
  - `front_to_back_delta_forward_speed_mean = +0.13418 mm/s`
- The embodied locomotor regime remained extremely fast at about `645 mm/s`,
  so even after the retinal-slip semantics were fixed, the current
  brain/decoder/body path did not convert clean front-to-back motion into
  slowing.

4. Evidence

- [run.jsonl](/G:/flysim/outputs/creamer2018_known_good_nonspont_creamer_motion_energy_freqgate_safe_t5a_only_speedsuppress_turnlite_lowforward_synced_veryslow_baseline/flygym-demo-20260329-120615/run.jsonl)
- [visual_speed_control.py](/G:/flysim/src/body/visual_speed_control.py)
- [test_visual_speed_control.py](/G:/flysim/tests/test_visual_speed_control.py)
- [test_closed_loop_smoke.py](/G:/flysim/tests/test_closed_loop_smoke.py)

5. Next actions

- Treat the scene-synchronization request as resolved.
- Stop blaming scene semantics for the current Creamer miss on this branch.
- Push the next iteration into the actual remaining blocker:
  biologically plausible brain/decoder/body control that slows under clean
  front-to-back retinal motion in the same synced treadmill assay.

## 2026-03-29 12:45 Sub-Agent Blocker Review And Public Recording Fit Targets

1. What I attempted

- Used all six sub-agent slots in parallel for two jobs:
  - blocker diagnosis on the current Creamer branch
  - public living-fly recording / dataset search for fitting targets
- Kept the work read-only and used the results to build a concrete next-step
  plan rather than more blind gain sweeps.

2. What succeeded

- The blocker diagnosis converged cleanly across the code/artifact reviews:
  - the dominant blocker is the **high-speed embodied treadmill attractor**
    rather than scene semantics
  - the current `T5a` forward-context signal is weak and not specific enough,
    but the deeper problem is that once the branch sits near `~645 mm/s`, the
    body path responds only weakly to changes in the bilateral frequency-floor
    suppressor
- The strongest public recording targets are now explicit and ranked in
  [creamer_recording_fit_targets.md](/G:/flysim/docs/creamer_recording_fit_targets.md):
  - **Aimon 2023 Dryad** and **Schaffer 2023 Figshare** for living-brain /
    locomotor-state fitting
  - **Ketkar 2022 Zenodo** and **Gruntman 2019 Figshare** for early visual
    motion channels
  - **Shomar 2025 Dryad** for downstream visual-to-locomotor channels
  - **Dallmann 2025 Dryad** for treadmill proprioceptive / feedback realism
  - **Creamer 2018** remains the behavioral scorecard, not the best public raw
    fit source
- Added two new tracker tasks:
  - `T188`: same-state replay falsifier for the high-speed attractor
  - `T189`: public-data fitting stack for the living / Creamer workstream

3. What failed

- I still do **not** have evidence for a public raw trace repository directly
  attached to Creamer 2018 itself.
- So the fitting program has to use adjacent public recordings plus Creamer as
  the behavioral acceptance target.

4. Evidence

- [creamer_recording_fit_targets.md](/G:/flysim/docs/creamer_recording_fit_targets.md)
- [creamer2018_visual_speed_control_note.md](/G:/flysim/docs/creamer2018_visual_speed_control_note.md)
- [TASKS.md](/G:/flysim/TASKS.md)

5. Next actions

- Run `T188` before any further large Creamer sweep.
- Start `T189` so the living branch and motion pathway stop being tuned only by
  local assay outcomes.

## 2026-03-29 13:05 Priority Override To Public Neural Measurement Parity

1. What I attempted

- Recorded the user's new top-level directive as the repo priority:
  public neural measurement parity on the spontaneous brain now supersedes all
  downstream Creamer / decoder / embodiment work.
- Preserved the current chat state, including the latest synced-probe result,
  blocker diagnosis, and sub-agent dataset findings, in repo files intended to
  survive compaction.

2. What succeeded

- Added the priority override to [TASKS.md](/G:/flysim/TASKS.md).
- Created the new program note:
  [public_neural_measurement_parity_program.md](/G:/flysim/docs/public_neural_measurement_parity_program.md)
- Added new top-priority tasks:
  - `T190`: freeze downstream work and promote the parity program
  - `T191`: obtain and stage the public datasets
  - `T192`: define canonical matched-format schema
  - `T193`: build or reuse targeted fitting harnesses
  - `T194`: force the spontaneous brain to match public measurements dataset by
    dataset
- Preserved the latest blocker and dataset context in:
  - [public_neural_measurement_parity_program.md](/G:/flysim/docs/public_neural_measurement_parity_program.md)
  - [creamer_recording_fit_targets.md](/G:/flysim/docs/creamer_recording_fit_targets.md)
  - [creamer2018_visual_speed_control_note.md](/G:/flysim/docs/creamer2018_visual_speed_control_note.md)
  - [context.md](/G:/flysim/context.md) still needed an update at this point and remains part of the preserved-state set

3. What failed

- The datasets are not yet staged locally in this slice.
- This slice was for priority freeze and context preservation first, because
  the chat context was at risk of compaction.

4. Evidence

- [TASKS.md](/G:/flysim/TASKS.md)
- [public_neural_measurement_parity_program.md](/G:/flysim/docs/public_neural_measurement_parity_program.md)
- [creamer_recording_fit_targets.md](/G:/flysim/docs/creamer_recording_fit_targets.md)

5. Next actions

- Start `T191` immediately.
- Use the spontaneous brain only for this program unless a dataset-specific
  harness requires an isolated comparator branch.

## 2026-03-29 14:05 First Real Aimon Spontaneous-Brain Fit Pilot

1. What I attempted

- Implemented the first actual spontaneous-brain replay/projection harness
  against a public living-fly neural dataset rather than stopping at canonical
  export and generic scoring.
- Used the staged Aimon 2023 canonical bundle plus the living spontaneous
  branch to run a real B1269 pilot.

2. What succeeded

- Added the new replay/projection module:
  [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py)
- Added the CLI runner:
  [run_aimon_spontaneous_fit.py](/G:/flysim/scripts/run_aimon_spontaneous_fit.py)
- Extended the Aimon harness to preserve the metadata needed for replay:
  `split`, `stimulus`, and `behavior_paths`
- Fixed the generic trace scorer to ignore non-finite public samples instead of
  contaminating aggregate metrics with `NaN`
- Added focused tests:
  - [test_aimon_parity_harness.py](/G:/flysim/tests/test_aimon_parity_harness.py)
  - [test_aimon_spontaneous_fit.py](/G:/flysim/tests/test_aimon_spontaneous_fit.py)
- Completed the first real live fit artifact:
  [aimon_spontaneous_fit_summary.json](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_b1269_pilot_v2/aimon_spontaneous_fit_summary.json)
- Main same-dataset pilot result on `B1269_spontaneous_walk` and
  `B1269_forced_walk`:
  - `aggregate.mean_pearson_r = 0.8909`
  - `aggregate.mean_nrmse = 0.0661`
  - `aggregate.mean_abs_error = 0.00173`
  - `aggregate.mean_sign_agreement = 0.8571`

3. What failed

- This is not a held-out parity result yet.
- The first pilot fit and scored on the same short B1269 pair, so it proves the
  path is live but does not yet prove generalization.

4. Evidence

- [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py)
- [run_aimon_spontaneous_fit.py](/G:/flysim/scripts/run_aimon_spontaneous_fit.py)
- [aimon_spontaneous_fit_summary.json](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_b1269_pilot_v2/aimon_spontaneous_fit_summary.json)
- [test_aimon_spontaneous_fit.py](/G:/flysim/tests/test_aimon_spontaneous_fit.py)

5. Next actions

- Run the first held-out Aimon fit on the canonical train/test split.
- Use that result to define the first parameter sweep on mechanosensory forcing,
  basis options, and projection regularization.
- Keep all downstream decoder and embodiment interpretation subordinate to this
  parity lane.

## 2026-03-29 16:35 First Held-Out Aimon Boundary And First Schaffer NWB Canonical Export

1. What I attempted

- Ran the first honest held-out Aimon spontaneous-brain fit:
  - fit on canonical `train`
  - score on held-out canonical `test`
- Staged and inspected the first real Schaffer NWB session, then built a first
  canonical exporter around the actual NWB layout rather than metadata alone.

2. What succeeded

- Held-out Aimon run completed:
  [aimon_spontaneous_fit_train_to_test_v1](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_train_to_test_v1/aimon_spontaneous_fit_summary.json)
- The held-out result is now explicit:
  - fit trials:
    - `B350_spontaneous_walk`
    - `B350_forced_walk`
  - aggregate over all four trials:
    - `mean_pearson_r = 0.1456`
    - `mean_nrmse = 0.2462`
    - `mean_abs_error = 0.00608`
    - `mean_sign_agreement = 0.5279`
  - held-out `test` mean:
    - `mean_pearson_r = 0.0564`
    - `mean_nrmse = 0.3328`
    - `mean_abs_error = 0.00856`
    - `mean_sign_agreement = 0.4689`
- Added the first Schaffer NWB canonical exporter:
  - [schaffer_nwb_canonical_dataset.py](/G:/flysim/src/analysis/schaffer_nwb_canonical_dataset.py)
  - [export_schaffer_nwb_canonical_dataset.py](/G:/flysim/scripts/export_schaffer_nwb_canonical_dataset.py)
  - [test_schaffer_nwb_canonical_dataset.py](/G:/flysim/tests/test_schaffer_nwb_canonical_dataset.py)
- Staged the first real Schaffer NWB source:
  - [2022_01_08_fly1.nwb](/G:/flysim/external/neural_measurements/schaffer2023_figshare/2022_01_08_fly1.nwb)
- Exported the first real Schaffer canonical bundle:
  [schaffer2023_nwb_canonical_summary.json](/G:/flysim/outputs/derived/schaffer2023_nwb_canonical/schaffer2023_nwb_canonical_summary.json)
  - `staged_session_count = 1`
  - `trial_count = 6`
  - aligned ROI `Df/F`, ball motion, behavioral-state arrays

3. What failed

- The first held-out Aimon result is not close to parity.
- The same-dataset B1269 pilot was strong, but generalization to held-out
  `B1269` after fitting on `B350` is weak, especially for forced walk.

4. Evidence

- [aimon_spontaneous_fit_train_to_test_v1](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_train_to_test_v1/aimon_spontaneous_fit_summary.json)
- [aimon_spontaneous_fit_b1269_pilot_v2](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_b1269_pilot_v2/aimon_spontaneous_fit_summary.json)
- [schaffer_nwb_canonical_dataset.py](/G:/flysim/src/analysis/schaffer_nwb_canonical_dataset.py)
- [schaffer2023_nwb_canonical_summary.json](/G:/flysim/outputs/derived/schaffer2023_nwb_canonical/schaffer2023_nwb_canonical_summary.json)

5. Next actions

- Run the first targeted held-out Aimon optimization sweep.
- Keep the optimization target on held-out Aimon metrics, not same-dataset fit.
- Expand Schaffer staging beyond one NWB session once the exporter seam is
  confirmed stable.

## 2026-03-29 17:05 Aimon Held-Out Sweep Comparison And Schaffer Score Harness

1. What I attempted

- Ran two targeted held-out Aimon optimization variants after the first
  train-on-`B350`, test-on-`B1269` boundary:
  - reduced-capacity regularized variant without asymmetry basis
  - stronger mechanosensory forcing variant with both forcing channels doubled
- Added a direct Schaffer canonical parity harness so staged NWB intervals can be
  loaded and scored in the same style as Aimon.

2. What succeeded

- Completed the second and third held-out Aimon variants:
  - [v2 reduced basis no asymmetry](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_train_to_test_v2_basis16_ridge1e-2_noasym/aimon_spontaneous_fit_summary.json)
  - [v3 force2](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_train_to_test_v3_force2/aimon_spontaneous_fit_summary.json)
- Materialized a comparison artifact:
  - [aimon_spontaneous_fit_variant_comparison.json](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_variant_comparison.json)
- Held-out `B1269` means now compare as:
  - `v1`: `pearson_r = 0.0564`, `nrmse = 0.3328`, `abs_error = 0.00856`, `sign = 0.4689`
  - `v2`: `pearson_r = 0.0122`, `nrmse = 0.3310`, `abs_error = 0.00849`, `sign = 0.4605`
  - `v3`: `pearson_r = 0.0620`, `nrmse = 0.3117`, `abs_error = 0.00821`, `sign = 0.4660`
- Interpretation:
  - reduced capacity and no asymmetry did not solve held-out Aimon
  - stronger mechanosensory forcing is the first real held-out improvement
  - the weak slice remains held-out `B1269_forced_walk`, not spontaneous walk
- Added and validated the Schaffer score harness:
  - [schaffer_parity_harness.py](/G:/flysim/src/analysis/schaffer_parity_harness.py)
  - [test_schaffer_parity_harness.py](/G:/flysim/tests/test_schaffer_parity_harness.py)
  - focused validation: `6 passed`

3. What failed

- The improved `v3` Aimon result is still weak. It is an optimization step, not
  parity.
- Sign agreement on held-out `B1269` remains poor even when aggregate error
  improves.

4. Evidence

- [aimon_spontaneous_fit_train_to_test_v2_basis16_ridge1e-2_noasym](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_train_to_test_v2_basis16_ridge1e-2_noasym/aimon_spontaneous_fit_summary.json)
- [aimon_spontaneous_fit_train_to_test_v3_force2](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_train_to_test_v3_force2/aimon_spontaneous_fit_summary.json)
- [aimon_spontaneous_fit_variant_comparison.json](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_variant_comparison.json)
- [schaffer_parity_harness.py](/G:/flysim/src/analysis/schaffer_parity_harness.py)

5. Next actions

- Separate `force_contact_force` from `force_forward_speed` in the next held-out
  Aimon sweep point and target the weak forced-walk slice directly.
- Use the new Schaffer harness to prepare the first spontaneous-brain matched
  scoring run on the staged NWB interval bundle.

## 2026-03-29 17:25 Aimon Contact Split Falsified And First Live Schaffer Fit Started

1. What I attempted

- Continued the held-out Aimon forcing sweep by isolating the contact channel:
  - `force_contact_force = 2.0`
  - `force_forward_speed = 1.0`
- Added the first backend-connected Schaffer spontaneous-fit path and launched a
  one-trial pilot on the staged NWB bundle.

2. What succeeded

- Added the first live Schaffer spontaneous-fit code path:
  - [schaffer_spontaneous_fit.py](/G:/flysim/src/analysis/schaffer_spontaneous_fit.py)
  - [run_schaffer_spontaneous_fit.py](/G:/flysim/scripts/run_schaffer_spontaneous_fit.py)
  - [test_schaffer_spontaneous_fit.py](/G:/flysim/tests/test_schaffer_spontaneous_fit.py)
- Focused Schaffer validation passed:
  - `9 passed`
- The contact-dominant Aimon held-out run completed:
  - [v4 contact2/forward1](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_train_to_test_v4_contact2_forward1/aimon_spontaneous_fit_summary.json)
- Held-out `B1269_*` means for `v4`:
  - `mean_pearson_r = 0.0385`
  - `mean_nrmse = 0.3293`
  - `mean_abs_error = 0.00853`
  - `mean_sign_agreement = 0.4644`

3. What failed

- The contact-only gain split did not preserve the `v3 force2` improvement.
- That falsifies contact amplification by itself as the main reason `v3`
  improved held-out Aimon.

4. Evidence

- [v4 contact2/forward1](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_train_to_test_v4_contact2_forward1/aimon_spontaneous_fit_summary.json)
- [schaffer_spontaneous_fit.py](/G:/flysim/src/analysis/schaffer_spontaneous_fit.py)
- [run_schaffer_spontaneous_fit.py](/G:/flysim/scripts/run_schaffer_spontaneous_fit.py)

5. Next actions

- Finish the complementary `forward2/contact1` Aimon run, because it is now the
  decisive test of whether the useful `v3` gain came mainly from forward
  mechanosensory forcing.
- Finish the one-trial live Schaffer pilot and use it to decide whether the new
  NWB fit path is stable enough for larger interval sweeps.

## 2026-03-29 18:05 Aimon Forward Split Result

1. What I attempted

- Ran the complementary held-out Aimon forcing split:
  - `force_forward_speed = 2.0`
  - `force_contact_force = 1.0`

2. What succeeded

- Completed:
  - [v5 forward2/contact1](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_train_to_test_v5_forward2_contact1/aimon_spontaneous_fit_summary.json)
- Held-out `B1269_*` means for `v5`:
  - `mean_pearson_r = 0.0565`
  - `mean_nrmse = 0.3155`
  - `mean_abs_error = 0.00824`
  - `mean_sign_agreement = 0.4723`
- Current Aimon sweep read:
  - `v3 force2` remains best overall on correlation and error
  - `v5 forward2/contact1` is close on error and is now the best held-out sign
    agreement point
  - `v4 contact2/forward1` was the clear negative result

3. What failed

- The forward-only split did not beat `v3 force2` outright.
- So the current gain is not explained by pure forward forcing alone either.

4. Evidence

- [v3 force2](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_train_to_test_v3_force2/aimon_spontaneous_fit_summary.json)
- [v4 contact2/forward1](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_train_to_test_v4_contact2_forward1/aimon_spontaneous_fit_summary.json)
- [v5 forward2/contact1](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_train_to_test_v5_forward2_contact1/aimon_spontaneous_fit_summary.json)
- [variant comparison](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_variant_comparison.json)

5. Next actions

- Keep the Aimon search centered on forward-dominant mechanosensory forcing,
  because contact-only was clearly wrong and forward-only recovered most of the
  useful gain.
- Finish the live Schaffer pilot and use it to open the second dataset-specific
  parity lane with a real backend run.

## 2026-03-29 20:35 Three-Session Schaffer Bundle And Aimon Interpolation Point

1. What I attempted

- Refreshed the Schaffer Figshare manifest through the real API path, then
  staged two additional NWB sessions:
  - `2018_08_24_fly3_run1.nwb`
  - `2019_04_25_fly1.nwb`
- Rebuilt the Schaffer canonical bundle from the staged NWBs.
- Ran one more Aimon interpolation point between `v3 force2` and
  `v5 forward2/contact1`.
- Added an explicit same-session guard and `fit_trial_id` support to the
  Schaffer fit path so interval holdouts can be run honestly.

2. What succeeded

- Schaffer staging succeeded with verified digests:
  - [2018_08_24_fly3_run1.nwb](/G:/flysim/external/neural_measurements/schaffer2023_figshare/2018_08_24_fly3_run1.nwb)
  - [2019_04_25_fly1.nwb](/G:/flysim/external/neural_measurements/schaffer2023_figshare/2019_04_25_fly1.nwb)
- Rebuilt Schaffer canonical bundle:
  - [schaffer2023_nwb_canonical_summary.json](/G:/flysim/outputs/derived/schaffer2023_nwb_canonical/schaffer2023_nwb_canonical_summary.json)
  - current result:
    - `staged_session_count = 3`
    - `exported_session_count = 3`
    - `trial_count = 9`
- Added the Schaffer same-session fit guard and explicit fit-trial selector:
  - [schaffer_spontaneous_fit.py](/G:/flysim/src/analysis/schaffer_spontaneous_fit.py)
  - [run_schaffer_spontaneous_fit.py](/G:/flysim/scripts/run_schaffer_spontaneous_fit.py)
  - focused validation: `11 passed`
- Completed Aimon `v6 forward2/contact1.5`:
  - [v6 summary](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_train_to_test_v6_forward2_contact1p5/aimon_spontaneous_fit_summary.json)
  - held-out `B1269_*` means:
    - `mean_pearson_r = 0.0563`
    - `mean_nrmse = 0.3144`
    - `mean_abs_error = 0.00824`
    - `mean_sign_agreement = 0.4665`

3. What failed

- `v6` did not beat `v3 force2` on error/correlation.
- `v6` did not beat `v5 forward2/contact1` on sign agreement.
- So it is an interpolation point, not a new frontier.

4. Evidence

- [public_neural_measurement_schaffer2023_figshare_manifest.json](/G:/flysim/outputs/metrics/public_neural_measurement_schaffer2023_figshare_manifest.json)
- [schaffer2023_nwb_canonical_summary.json](/G:/flysim/outputs/derived/schaffer2023_nwb_canonical/schaffer2023_nwb_canonical_summary.json)
- [v6 summary](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_train_to_test_v6_forward2_contact1p5/aimon_spontaneous_fit_summary.json)
- [variant comparison](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_variant_comparison.json)

5. Next actions

- Finish the first within-session Schaffer interval holdout on the rebuilt 2022
  session.
- Keep the Aimon forcing search forward-dominant, because the new interpolation
  point still supports that read.

## 2026-03-30 - Endogenous tiny-readout parity runner hardened

1. What I attempted

- Hardened the Aimon and Schaffer parity runners so they create their output
  directories and write immediate run-manifest / run-status artifacts at launch,
  instead of appearing dead until the fit summary is emitted at the end.
- Reused the existing live endogenous Aimon fit session instead of opening more
  long-lived shells, because the unified exec process ceiling is already tight.

2. What succeeded

- Patched:
  - [run_aimon_spontaneous_fit.py](/G:/flysim/scripts/run_aimon_spontaneous_fit.py)
  - [run_schaffer_spontaneous_fit.py](/G:/flysim/scripts/run_schaffer_spontaneous_fit.py)
- New behavior:
  - create `output_dir` immediately
  - write `fit_run_manifest.json`
  - write `fit_run_status.json` with `running`
  - update status to `completed` or `failed` at exit
- Added regression coverage:
  - [test_fit_runner_manifests.py](/G:/flysim/tests/test_fit_runner_manifests.py)
- Focused validation passed:
  - `python -m pytest tests/test_fit_runner_manifests.py tests/test_aimon_spontaneous_fit.py tests/test_schaffer_spontaneous_fit.py -q`
  - `12 passed in 1.77s`

3. What failed

- The currently running endogenous Aimon fit predates this runner hardening, so
  it still does not have an early manifest/status directory on disk.
- The live run is not hung, but it is still in long backend replay / fit work
  without intermediate writeout.

4. Evidence

- Live host process:
  - `PID 26508`
  - `CPU 236.61`
  - `WS_MB 1385.8`
- Existing live session:
  - unified exec session `54672`
- Patched runner files:
  - [run_aimon_spontaneous_fit.py](/G:/flysim/scripts/run_aimon_spontaneous_fit.py)
  - [run_schaffer_spontaneous_fit.py](/G:/flysim/scripts/run_schaffer_spontaneous_fit.py)
- New test:
  - [test_fit_runner_manifests.py](/G:/flysim/tests/test_fit_runner_manifests.py)

5. Next actions

- Keep polling the live endogenous Aimon fit until it writes
  [aimon_spontaneous_fit_summary.json](/G:/flysim/outputs/metrics/aimon_endogenous_tiny_v1/aimon_spontaneous_fit_summary.json)
  or fails.
- Once that result lands, compare it directly against the old surrogate-based
  Aimon fronts and then launch the matching endogenous tiny-readout Schaffer
  run with the hardened runner path.

## 2026-03-30 - Fixed endogenous parity harness seam and relaunched admissible Aimon run

1. What I attempted

- Audited the live endogenous Aimon tiny-readout run after the runner hardening.
- Traced the backend-construction seam inside
  [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py)
  and checked whether the parity harness was actually forwarding
  `brain.backend_dynamics` into [pytorch_backend.py](/G:/flysim/src/brain/pytorch_backend.py).

2. What succeeded

- Found a real blocking bug: the fit helper was instantiating
  [WholeBrainTorchBackend](/G:/flysim/src/brain/pytorch_backend.py) with
  `spontaneous_state`, but **not** with `backend_dynamics`.
- Patched [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py)
  so `build_backend_from_config()` now passes `brain.backend_dynamics`.
- Added regression coverage in
  [test_aimon_spontaneous_fit.py](/G:/flysim/tests/test_aimon_spontaneous_fit.py)
  asserting that [brain_endogenous_public_parity.yaml](/G:/flysim/configs/brain_endogenous_public_parity.yaml)
  actually selects the endogenous path and disables the diagnostic surrogate.
- Focused validation passed:
  - `python -m pytest tests/test_aimon_spontaneous_fit.py tests/test_fit_runner_manifests.py tests/test_schaffer_spontaneous_fit.py -q`
  - `13 passed, 1 warning in 2.60s`
- Killed the invalid live run:
  - host PID `26508`
- Relaunched the corrected admissible run:
  - unified exec session `37856`
  - live host PID `15472`
  - output root:
    [aimon_endogenous_tiny_v1](/G:/flysim/outputs/metrics/aimon_endogenous_tiny_v1)
- Verified immediate runner artifacts now exist:
  - [fit_run_manifest.json](/G:/flysim/outputs/metrics/aimon_endogenous_tiny_v1/fit_run_manifest.json)
  - [fit_run_status.json](/G:/flysim/outputs/metrics/aimon_endogenous_tiny_v1/fit_run_status.json)

3. What failed

- The first endogenous Aimon tiny-readout run was invalid and had to be discarded.
- It would have wasted more wall time if left alive, because it was not actually
  exercising the new endogenous production backend.

4. Evidence

- Fixed seam:
  - [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py)
- Regression:
  - [test_aimon_spontaneous_fit.py](/G:/flysim/tests/test_aimon_spontaneous_fit.py)
- Live corrected run artifacts:
  - [fit_run_manifest.json](/G:/flysim/outputs/metrics/aimon_endogenous_tiny_v1/fit_run_manifest.json)
  - [fit_run_status.json](/G:/flysim/outputs/metrics/aimon_endogenous_tiny_v1/fit_run_status.json)

5. Next actions

- Wait for the corrected endogenous Aimon run to finish and score it against the
  old surrogate-based Aimon frontier.
- Then launch the matching endogenous tiny-readout Schaffer run using the same
  hardened runner semantics.

## 2026-03-30 - Corrected endogenous Aimon tiny-readout result landed

1. What I attempted

- Waited for the corrected admissible endogenous Aimon tiny-readout run to
  finish after the `backend_dynamics` seam fix.
- Extracted the true held-out `B1269_*` trial aggregates and compared them
  directly against the prior surrogate-front Aimon runs.

2. What succeeded

- The corrected run completed cleanly:
  - [aimon_spontaneous_fit_summary.json](/G:/flysim/outputs/metrics/aimon_endogenous_tiny_v1/aimon_spontaneous_fit_summary.json)
- Aggregate over all four trials:
  - `mean_pearson_r = 0.02833`
  - `mean_nrmse = 0.21538`
  - `mean_abs_error = 0.00559`
  - `mean_sign_agreement = 0.48035`
- Per-trial highlights:
  - `B350_spontaneous_walk`: `pearson = 0.1420`, `nrmse = 0.1318`
  - `B350_forced_walk`: `pearson = 0.1221`, `nrmse = 0.1920`
  - `B1269_spontaneous_walk`: `pearson = -0.1395`, `nrmse = 0.2778`
  - `B1269_forced_walk`: `pearson = -0.01135`, `nrmse = 0.2599`
- True held-out `B1269_*` mean for the endogenous tiny backend:
  - `pearson = -0.0754`
  - `nrmse = 0.2688`
  - `abs_error = 0.00750`
  - `sign_agreement = 0.4221`

3. What failed

- The endogenous tiny backend did **not** beat the surrogate Aimon fronts on
  held-out correlation or sign agreement.
- Comparison against old held-out `B1269_*` means:
  - `v3 force2`: `pearson = 0.0620`, `nrmse = 0.3117`, `abs_error = 0.00821`, `sign = 0.4660`
  - `v7 force2 + obs_tau=0.5`: `pearson = 0.0410`, `nrmse = 0.2904`, `abs_error = 0.00778`, `sign = 0.4672`
  - `endogenous tiny v1`: `pearson = -0.0754`, `nrmse = 0.2688`, `abs_error = 0.00750`, `sign = 0.4221`
- So the new endogenous backend plus tiny readout improved amplitude/error but
  currently lost temporal alignment and sign consistency on held-out Aimon.

4. Evidence

- Corrected run result:
  - [aimon_spontaneous_fit_summary.json](/G:/flysim/outputs/metrics/aimon_endogenous_tiny_v1/aimon_spontaneous_fit_summary.json)
- Prior surrogate fronts:
  - [v3 force2](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_train_to_test_v3_force2/aimon_spontaneous_fit_summary.json)
  - [v7 force2 obs0p5](/G:/flysim/outputs/metrics/aimon_spontaneous_fit_train_to_test_v7_force2_obs0p5/aimon_spontaneous_fit_summary.json)

5. Next actions

- Launch the matching endogenous tiny-readout Schaffer run.
- Use the Aimon result to decide whether the next endogenous adjustment should
  target temporal structure / continuity rather than amplitude suppression.

## 2026-03-30 - Temporal structure promoted to top priority and calcium-memory slice added

1. What I attempted

- Treated the recurring parity miss as a temporal-structure failure, not an
  amplitude-fit failure.
- Added a new endogenous backend slice aimed specifically at slow internal
  memory with no surrogate forcing.

2. What succeeded

- Patched [pytorch_backend.py](/G:/flysim/src/brain/pytorch_backend.py) with a
  new intracellular calcium-like state:
  - `tau_calcium_ms`
  - `calcium_spike_gain`
  - `calcium_release_gain`
  - `calcium_adapt_gain`
  - `calcium_release_feedback_gain`
- The new state is driven only by:
  - spikes
  - graded release
- It now feeds back into:
  - endogenous adaptation current
  - graded recurrent release gain
  - modulatory drive readout
- Enabled nonzero calcium-memory parameters in
  [brain_endogenous_public_parity.yaml](/G:/flysim/configs/brain_endogenous_public_parity.yaml)
  with slower endocrine / central timescales and faster visual timescales.
- Added coverage in
  [test_spontaneous_state_unit.py](/G:/flysim/tests/test_spontaneous_state_unit.py)
  and kept the fit seam test green.
- Focused validation passed:
  - `python -m pytest tests/test_spontaneous_state_unit.py tests/test_brain_backend.py tests/test_aimon_spontaneous_fit.py -q`
  - `25 passed, 1 warning`

3. What failed

- Nothing failed at the implementation slice after the final test adjustment.
- The earlier endogenous Aimon result still stands as the baseline to beat:
  held-out `B1269_*` temporal correlation is still poor.

4. Evidence

- Backend:
  - [pytorch_backend.py](/G:/flysim/src/brain/pytorch_backend.py)
- Config:
  - [brain_endogenous_public_parity.yaml](/G:/flysim/configs/brain_endogenous_public_parity.yaml)
- Tests:
  - [test_spontaneous_state_unit.py](/G:/flysim/tests/test_spontaneous_state_unit.py)
  - [test_aimon_spontaneous_fit.py](/G:/flysim/tests/test_aimon_spontaneous_fit.py)

5. Next actions

- Rerun endogenous Aimon tiny-readout parity on the calcium-memory backend.
- Then run the matching endogenous Schaffer tiny-readout parity path.

## 2026-03-30 - Calcium-memory Aimon rerun completed and Schaffer temporal run launched

1. What I attempted

- Ran the first Aimon tiny-readout parity rerun on the calcium-memory endogenous
  backend.
- Immediately launched the matching Schaffer tiny-readout run on the same
  updated backend once the Aimon result landed.

2. What succeeded

- Aimon calcium-memory rerun completed:
  - [aimon_spontaneous_fit_summary.json](/G:/flysim/outputs/metrics/aimon_endogenous_tiny_v2_calcium/aimon_spontaneous_fit_summary.json)
- Aggregate over all four Aimon trials:
  - `mean_pearson_r = 0.04736`
  - `mean_nrmse = 0.21788`
  - `mean_abs_error = 0.00563`
  - `mean_sign_agreement = 0.49298`
- True held-out `B1269_*` mean:
  - `pearson = -0.05162`
  - `nrmse = 0.27447`
  - `abs_error = 0.00761`
  - `sign_agreement = 0.43051`
- Relative to the first endogenous tiny run:
  - `pearson`: `-0.0754 -> -0.0516` better
  - `sign_agreement`: `0.4221 -> 0.4305` better
  - `nrmse`: `0.2688 -> 0.2745` worse
  - `abs_error`: `0.00750 -> 0.00761` slightly worse
- Matching Schaffer run launched:
  - output root: [schaffer_endogenous_tiny_v1_calcium](/G:/flysim/outputs/metrics/schaffer_endogenous_tiny_v1_calcium)
  - live runner session: `21983`
  - immediate artifacts exist:
    - [fit_run_manifest.json](/G:/flysim/outputs/metrics/schaffer_endogenous_tiny_v1_calcium/fit_run_manifest.json)
    - [fit_run_status.json](/G:/flysim/outputs/metrics/schaffer_endogenous_tiny_v1_calcium/fit_run_status.json)

3. What failed

- The calcium-memory slice did not solve Aimon held-out temporal structure.
- It improved correlation/sign modestly but did not cross zero-mean held-out
  correlation and did not beat the surrogate observation-model frontier.

4. Evidence

- Aimon calcium-memory result:
  - [aimon_spontaneous_fit_summary.json](/G:/flysim/outputs/metrics/aimon_endogenous_tiny_v2_calcium/aimon_spontaneous_fit_summary.json)
- Prior endogenous baseline:
  - [aimon_spontaneous_fit_summary.json](/G:/flysim/outputs/metrics/aimon_endogenous_tiny_v1/aimon_spontaneous_fit_summary.json)
- Live Schaffer temporal run root:
  - [schaffer_endogenous_tiny_v1_calcium](/G:/flysim/outputs/metrics/schaffer_endogenous_tiny_v1_calcium)

5. Next actions

- Wait for the Schaffer calcium-memory run to finish.
- Use the Schaffer result to decide whether the next temporal slice should
  emphasize session-scale modulatory memory or recurrent slow inhibition.

## 2026-03-30 - Applied agent-guided temporal harness fixes and relaunched Schaffer

1. What I attempted

- Used the first completed sub-agent findings to patch the parity harness
  itself, not just the backend.
- Focused on two temporal bottlenecks:
  - tiny-readout temporal information loss
  - Schaffer interval-boundary observation reset

2. What succeeded

- Aimon/Schaffer tiny mode no longer keeps the first few bilateral families in
  alphabetical order. It now:
  - ranks bilateral family bases on the fit split by temporal energy
  - keeps the selected families' raw and observation-basis rows together
- Schaffer observation filtering is now session-continuous when
  `preserve_state_within_session` is enabled:
  - feature rows are concatenated in absolute session time
  - causal observation low-pass is applied once on the stitched stream
  - rows are then split back to interval reports
- New tests passed:
  - `python -m pytest tests/test_aimon_spontaneous_fit.py tests/test_schaffer_spontaneous_fit.py tests/test_fit_runner_manifests.py -q`
  - `15 passed, 1 warning in 2.76s`
- The stale Schaffer run launched before these fixes was killed:
  - `PID 21860`
- Relaunched corrected Schaffer temporal run:
  - session `7400`
  - output root:
    [schaffer_endogenous_tiny_v1_calcium](/G:/flysim/outputs/metrics/schaffer_endogenous_tiny_v1_calcium)

3. What failed

- Nothing failed in the harness patch slice after the final validation.
- The improved Aimon calcium-memory result still does not solve the held-out
  temporal miss by itself.

4. Evidence

- Harness code:
  - [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py)
  - [schaffer_spontaneous_fit.py](/G:/flysim/src/analysis/schaffer_spontaneous_fit.py)
- Tests:
  - [test_aimon_spontaneous_fit.py](/G:/flysim/tests/test_aimon_spontaneous_fit.py)
  - [test_schaffer_spontaneous_fit.py](/G:/flysim/tests/test_schaffer_spontaneous_fit.py)
- Live relaunched Schaffer run artifacts:
  - [fit_run_manifest.json](/G:/flysim/outputs/metrics/schaffer_endogenous_tiny_v1_calcium/fit_run_manifest.json)
  - [fit_run_status.json](/G:/flysim/outputs/metrics/schaffer_endogenous_tiny_v1_calcium/fit_run_status.json)

5. Next actions

- Let the corrected Schaffer run finish.
- Use that result to decide whether the next backend temporal step should be
  real routed slow synaptic pathways or stronger session-scale modulatory
  memory.

## 2026-03-30 - Implemented true routed recurrent pathways in the backend

1. What I attempted

- Treated the stubborn temporal miss as evidence that the recurrent core was
  still too collapsed.
- Replaced pooled recurrent class inputs with routed pathways inside
  [pytorch_backend.py](/G:/flysim/src/brain/pytorch_backend.py).

2. What succeeded

- Implemented true source-routed recurrent classes:
  - spikes now feed fast excitatory / inhibitory classes
  - graded release now feeds slow excitatory / inhibitory classes
  - modulatory populations now feed a separate slow modulatory class
  - routing is determined by source-group release modes and modulatory-group
    membership
- Added routed source masks and summary signals:
  - `routed_fast_source_fraction`
  - `routed_slow_source_fraction`
  - `routed_modulatory_source_fraction`
- Preserved the old model-forward path as a fallback, but the endogenous backend
  now uses explicit `class_inputs` built from routed sources.
- Added regression coverage:
  - [test_brain_backend.py](/G:/flysim/tests/test_brain_backend.py)
  - [test_spontaneous_state_unit.py](/G:/flysim/tests/test_spontaneous_state_unit.py)
- Focused validation passed:
  - `python -m pytest tests/test_brain_backend.py tests/test_spontaneous_state_unit.py tests/test_aimon_spontaneous_fit.py tests/test_schaffer_spontaneous_fit.py -q`
  - `36 passed, 1 warning in 12.91s`

3. What failed

- The Schaffer run that had been started before this backend routing change is
  no longer admissible for temporal diagnosis and was already stopped.

4. Evidence

- Backend:
  - [pytorch_backend.py](/G:/flysim/src/brain/pytorch_backend.py)
- Tests:
  - [test_brain_backend.py](/G:/flysim/tests/test_brain_backend.py)
  - [test_spontaneous_state_unit.py](/G:/flysim/tests/test_spontaneous_state_unit.py)

5. Next actions

- Rerun endogenous Aimon tiny-readout parity on the routed backend.
- Then rerun Schaffer on the routed backend after the new Aimon read lands.

## 2026-03-30 - Routed endogenous Aimon rerun completed and crossed back above zero correlation

1. What I attempted

- Finished the first Aimon parity rerun on the routed recurrent backend after:
  - intracellular calcium-like memory
  - fit-based tiny feature selection
  - session-continuous observation filtering
  - true source-routed recurrent classes

2. What succeeded

- The routed backend materially improved the held-out Aimon temporal read.
- Held-out `B1269_*` mean from
  [aimon_spontaneous_fit_summary.json](/G:/flysim/outputs/metrics/aimon_endogenous_tiny_v3_routed/aimon_spontaneous_fit_summary.json):
  - `pearson = +0.0065`
  - `nrmse = 0.2685`
  - `abs_error = 0.00750`
  - `sign = 0.4551`
- Relative to prior endogenous runs:
  - `v1`:
    - `pearson = -0.0754`
    - `nrmse = 0.2688`
    - `abs_error = 0.00750`
    - `sign = 0.4221`
  - `v2 calcium`:
    - `pearson = -0.0516`
    - `nrmse = 0.2745`
    - `abs_error = 0.00761`
    - `sign = 0.4305`
- This is the first endogenous Aimon run that gets held-out correlation back
  above zero without reintroducing surrogate drive.
- The routed/tiny fit now uses `22` features instead of `18`, which confirms the
  harness is preserving more of the temporal family structure instead of
  collapsing it away.

3. What failed

- Temporal parity is still not acceptable.
- The routed backend improved direction and sign consistency, but the held-out
  temporal correlation is still far too weak to count as a resolution.

4. Evidence

- Routed result:
  - [aimon_spontaneous_fit_summary.json](/G:/flysim/outputs/metrics/aimon_endogenous_tiny_v3_routed/aimon_spontaneous_fit_summary.json)
- Prior endogenous references:
  - [aimon_spontaneous_fit_summary.json](/G:/flysim/outputs/metrics/aimon_endogenous_tiny_v1/aimon_spontaneous_fit_summary.json)
  - [aimon_spontaneous_fit_summary.json](/G:/flysim/outputs/metrics/aimon_endogenous_tiny_v2_calcium/aimon_spontaneous_fit_summary.json)

5. Next actions

- Launch the matching routed Schaffer rerun on the corrected harness.
- Use Schaffer to decide whether routed recurrent classes are enough or whether
  the next no-hack temporal slice must add even richer distributed slow-path
  state inside the backend.

## 2026-03-31 - Routed endogenous Schaffer rerun completed

1. What I attempted

- Let the corrected routed Schaffer within-session holdout run finish on the
  same endogenous backend that produced the first positive held-out Aimon
  correlation.
- Compared it directly against the prior Schaffer holdout using the honest
  split:
  - fit trials `000-003`
  - held-out trials `004-005`

2. What succeeded

- The routed Schaffer run completed cleanly and wrote full artifacts:
  - [schaffer_spontaneous_fit_summary.json](/G:/flysim/outputs/metrics/schaffer_endogenous_tiny_v2_routed/schaffer_spontaneous_fit_summary.json)
  - per-trial predicted matrices
  - per-trial feature matrices
  - per-trial ball-motion and behavioral-state arrays
- Honest routed fit mean on trials `000-003`:
  - `pearson = 0.1131`
  - `nrmse = 0.4517`
  - `abs_error = 0.004225`
  - `sign = 0.5581`
- Honest routed held-out mean on trials `004-005`:
  - `pearson = -0.0140`
  - `nrmse = 1.2182`
  - `abs_error = 0.00986`
  - `sign = 0.4770`
- Compared with the earlier Schaffer holdout:
  - prior held-out:
    - `pearson = -0.0011`
    - `nrmse = 1.3698`
    - `abs_error = 0.01098`
    - `sign = 0.5032`
- So routed recurrence improved held-out amplitude/error:
  - `nrmse 1.3698 -> 1.2182`
  - `abs_error 0.01098 -> 0.00986`
- But temporal alignment did not improve:
  - `pearson -0.0011 -> -0.0140`
  - `sign 0.5032 -> 0.4770`

3. What failed

- The routed backend did not resolve the temporal-structure miss on Schaffer.
- The fit remains materially better than the holdout, and the held-out late
  intervals still drift into weak-to-negative temporal alignment.

4. Evidence

- Routed Schaffer result:
  - [schaffer_spontaneous_fit_summary.json](/G:/flysim/outputs/metrics/schaffer_endogenous_tiny_v2_routed/schaffer_spontaneous_fit_summary.json)
- Prior Schaffer reference:
  - [schaffer_spontaneous_fit_summary.json](/G:/flysim/outputs/metrics/schaffer_spontaneous_fit_2022_train4_test2/schaffer_spontaneous_fit_summary.json)

5. Next actions

- Treat routed slow-path recurrence as a real but incomplete mechanism win.
- The next no-hack temporal slice must add richer distributed temporal state
  inside the backend rather than more readout complexity.

## 2026-03-31 - Distributed temporal-state backend slice validated

1. What I attempted

- Added a richer distributed temporal-state mechanism inside the endogenous
  recurrent core instead of expanding the readout head.
- Specifically added distributed slow context states for:
  - excitatory recurrence
  - inhibitory recurrence
  - modulatory recurrence
- Wired those states into the routed recurrent-class inputs, internal
  neuromodulatory drive, and backend state summary.
- Tightened the new unit coverage so the distributed-state test isolates the
  integrator itself rather than accidentally asserting on live recurrent
  reverberation.

2. What succeeded

- Backend/config/test slice is now implemented and validated:
  - [pytorch_backend.py](/G:/flysim/src/brain/pytorch_backend.py)
  - [brain_endogenous_public_parity.yaml](/G:/flysim/configs/brain_endogenous_public_parity.yaml)
  - [test_spontaneous_state_unit.py](/G:/flysim/tests/test_spontaneous_state_unit.py)
- Focused validation passed:
  - `python -m pytest tests/test_spontaneous_state_unit.py tests/test_brain_backend.py tests/test_aimon_spontaneous_fit.py -q`
  - `30 passed, 1 warning`
- Added the operational rule that future Schaffer retests must use explicit
  staged-trial subsets. The full-session Schaffer loop is too slow for normal
  iteration and is no longer admissible as the default experimental path.

3. What failed

- No new fit metric landed yet in this slice. This was backend implementation
  and validation only.

4. Evidence

- Backend:
  - [pytorch_backend.py](/G:/flysim/src/brain/pytorch_backend.py)
- Config:
  - [brain_endogenous_public_parity.yaml](/G:/flysim/configs/brain_endogenous_public_parity.yaml)
- Tests:
  - [test_spontaneous_state_unit.py](/G:/flysim/tests/test_spontaneous_state_unit.py)
  - [test_brain_backend.py](/G:/flysim/tests/test_brain_backend.py)
  - [test_aimon_spontaneous_fit.py](/G:/flysim/tests/test_aimon_spontaneous_fit.py)

5. Next actions

- Launch a new held-out Aimon rerun on the distributed-context backend.
- Compare it directly against:
  - `v1 endogenous tiny`
  - `v2 calcium`
  - `v3 routed`
- Only after that, run subset-only Schaffer retests to see whether the new
  distributed context helps late-session temporal alignment without paying the
  old 20-hour wall-time cost.

## 2026-03-31 - Distributed-context Aimon rerun completed after fitter hardening

1. What I attempted

- Ran the first held-out Aimon rerun on the new distributed temporal-state
  backend.
- The first attempt failed numerically with:
  - `LinAlgError('SVD did not converge')`
- Hardened the shared reduced-projection fit path in
  [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py):
  - finite-safe normalization
  - SVD fallback to covariance eigendecomposition
  - linear-solve fallback to `lstsq`
  - finite-safe prediction path
- Added regression coverage for the fitter hardening.
- Reran the same distributed-context Aimon experiment cleanly.

2. What succeeded

- The shared fit path is now numerically harder to break and validated:
  - `python -m pytest tests/test_aimon_spontaneous_fit.py tests/test_spontaneous_state_unit.py tests/test_brain_backend.py -q`
  - `32 passed, 1 warning`
- The corrected rerun completed at:
  - [aimon_spontaneous_fit_summary.json](/G:/flysim/outputs/metrics/aimon_endogenous_tiny_v4_context_retry/aimon_spontaneous_fit_summary.json)
- Honest held-out `B1269_*` mean:
  - `pearson = -0.0384`
  - `nrmse = 0.2716`
  - `abs_error = 0.00751`
  - `sign = 0.4385`

3. What failed

- The distributed context slice did not beat the simpler routed recurrent
  backend on held-out Aimon.
- Comparison:
  - `v1 endogenous tiny`:
    - `pearson = -0.0754`
    - `nrmse = 0.2688`
    - `abs_error = 0.00750`
    - `sign = 0.4221`
  - `v2 calcium`:
    - `pearson = -0.0516`
    - `nrmse = 0.2745`
    - `abs_error = 0.00761`
    - `sign = 0.4305`
  - `v3 routed`:
    - `pearson = +0.0065`
    - `nrmse = 0.2685`
    - `abs_error = 0.00750`
    - `sign = 0.4551`
  - `v4 context`:
    - `pearson = -0.0384`
    - `nrmse = 0.2716`
    - `abs_error = 0.00751`
    - `sign = 0.4385`
- So `v4` still improves over `v1` and `v2` on temporal structure, but
  regresses materially versus `v3` on every held-out metric that matters.

4. Evidence

- Failed first attempt:
  - [fit_run_status.json](/G:/flysim/outputs/metrics/aimon_endogenous_tiny_v4_context/fit_run_status.json)
- Corrected completed rerun:
  - [aimon_spontaneous_fit_summary.json](/G:/flysim/outputs/metrics/aimon_endogenous_tiny_v4_context_retry/aimon_spontaneous_fit_summary.json)
- Prior endogenous references:
  - [aimon_spontaneous_fit_summary.json](/G:/flysim/outputs/metrics/aimon_endogenous_tiny_v1/aimon_spontaneous_fit_summary.json)
  - [aimon_spontaneous_fit_summary.json](/G:/flysim/outputs/metrics/aimon_endogenous_tiny_v2_calcium/aimon_spontaneous_fit_summary.json)
  - [aimon_spontaneous_fit_summary.json](/G:/flysim/outputs/metrics/aimon_endogenous_tiny_v3_routed/aimon_spontaneous_fit_summary.json)

5. Next actions

- Treat routed recurrence as the current best endogenous temporal baseline.
- Do not promote the current distributed-context formulation as-is.
- Next backend work should target a different distributed temporal mechanism
  instead of piling more static context accumulation on top of the routed core.
- Any Schaffer confirmation run must use an explicit staged-trial subset only.

## 2026-03-31 - Found a real Aimon evaluator flaw and a larger exact-parity mistake

1. What I attempted

- Audited why the consolidated Aimon metrics were still only moving by tiny
  amounts across `v1` to `v4`.
- Checked whether the held-out summaries were being distorted by empty traces or
  by an invalid identity assumption in the Aimon canonical export.

2. What succeeded

- Found a concrete scorer bug:
  - consolidated means were including traces with `n_samples = 0`
  - those rows are now dropped from summary means
  - the scorer now also reports:
    - `valid_trace_count`
    - `dropped_empty_trace_count`
    - `sample_count`
    - sample-weighted parity metrics
- Validated the scorer fix:
  - `python -m pytest tests/test_public_neural_measurement_harness.py tests/test_aimon_parity_harness.py tests/test_schaffer_parity_harness.py tests/test_aimon_spontaneous_fit.py -q`
  - `16 passed, 1 warning`
- Quantified the held-out effect of removing empty Aimon traces:
  - `v3 routed`, valid-only sample-weighted:
    - `pearson = 0.00084`
    - `nrmse = 0.28052`
    - `abs_error = 0.00777`
    - `sign = 0.46634`
  - `v4 context`, valid-only sample-weighted:
    - `pearson = -0.04294`
    - `nrmse = 0.27987`
    - `abs_error = 0.00767`
    - `sign = 0.45034`

3. What failed

- Found the bigger mistake: the current `B350 -> B1269` Aimon held-out setup is
  not a valid exact 1:1 identity test.
- The canonical Aimon bundle explicitly says:
  - modality is `region_component_timeseries`
  - `recorded_entity_id = region_component_*`
  - `flywire_mapping_key = null`
  - `flywire_mapping_confidence = none`
  - identity notes: exported public traces are region/components, not exact
    neurons
- So direct cross-experiment trace-index scoring is not admissible as exact
  neural parity evidence.

4. Evidence

- Aimon canonical identity note:
  - [aimon2023_canonical_bundle.json](/G:/flysim/outputs/derived/aimon2023_canonical/aimon2023_canonical_bundle.json)
- Scorer fix:
  - [public_neural_measurement_harness.py](/G:/flysim/src/analysis/public_neural_measurement_harness.py)
  - [test_public_neural_measurement_harness.py](/G:/flysim/tests/test_public_neural_measurement_harness.py)
- Current routed/context Aimon references:
  - [aimon_spontaneous_fit_summary.json](/G:/flysim/outputs/metrics/aimon_endogenous_tiny_v3_routed/aimon_spontaneous_fit_summary.json)
  - [aimon_spontaneous_fit_summary.json](/G:/flysim/outputs/metrics/aimon_endogenous_tiny_v4_context_retry/aimon_spontaneous_fit_summary.json)

5. Next actions

- Demote cross-experiment Aimon transfer to a coarse regime-transfer metric.
- Move exact Aimon temporal parity to within-experiment holdouts where trace
  identity is actually preserved.
- Keep same-session Schaffer subset retests as the main exact temporal parity
  discriminator while the Aimon evaluator is being corrected.

## 2026-04-01 13:53 - Aimon exact-parity lane switched to short within-trial windowed assays

1. What I attempted

- Finished the new identity-safe Aimon windowed-fit path and validated it.
- Made the best endogenous temporal baseline explicit as a standalone routed-only
  backend config instead of silently reusing the mutable parity config.
- Launched the first two short exact-identity Aimon temporal assays:
  - `B350_spontaneous_walk`
  - `B350_forced_walk`

2. What succeeded

- The new windowed Aimon path passed focused tests:
  - `python -m pytest tests/test_aimon_spontaneous_fit.py tests/test_public_neural_measurement_harness.py -q`
  - `13 passed, 1 warning`
- Added [run_aimon_windowed_fit.py](/G:/flysim/scripts/run_aimon_windowed_fit.py)
  as the reproducible within-experiment runner.
- Added explicit routed-only config
  [brain_endogenous_public_parity_routed_only.yaml](/G:/flysim/configs/brain_endogenous_public_parity_routed_only.yaml)
  by zeroing distributed-context gains while keeping the routed recurrent core,
  calcium memory, graded release, synaptic heterogeneity, and neuromodulation.
- Started the first two short identity-safe assays:
  - [aimon_b350_spont_window_routed_v1](/G:/flysim/outputs/metrics/aimon_b350_spont_window_routed_v1)
  - [aimon_b350_forced_window_routed_v1](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v1)
- Both manifests confirm:
  - `4` windows per trial
  - fit on windows `0-1`
  - hold out windows `2-3`
  - tiny readout
  - `obs_tau = 0.5 s`
  - routed-only endogenous backend
  - spontaneous on `cuda:0`, forced on `cuda:1`

3. What failed

- A quick one-line config instantiation check initially failed because it did not
  put `src/` on `sys.path`. That was only a shell-path issue, not a backend or
  config failure.

4. Evidence

- Runner:
  - [run_aimon_windowed_fit.py](/G:/flysim/scripts/run_aimon_windowed_fit.py)
- Windowed fit support:
  - [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py)
  - [test_aimon_spontaneous_fit.py](/G:/flysim/tests/test_aimon_spontaneous_fit.py)
- Routed-only config:
  - [brain_endogenous_public_parity_routed_only.yaml](/G:/flysim/configs/brain_endogenous_public_parity_routed_only.yaml)
- Live exact-identity assays:
  - [fit_run_manifest.json](/G:/flysim/outputs/metrics/aimon_b350_spont_window_routed_v1/fit_run_manifest.json)
  - [fit_run_manifest.json](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v1/fit_run_manifest.json)

5. Next actions

- Wait for the two `B350` windowed runs to finish.
- Compare spontaneous versus forced held-out window metrics on the same trace
  identities.
- Use that split to decide whether the next backend refinement should target:
  - spontaneous roaming memory
  - forced/exafferent transition dynamics
  - or both

## 2026-04-01 14:02 - First exact-identity forced Aimon window result landed

1. What I attempted

- Let the first two routed-only `B350` identity-safe windowed fits run:
  - `B350_forced_walk`, full `2.5 s`
  - `B350_spontaneous_walk`, originally full `30 s`
- After seeing the spontaneous source trial was `30 s`, patched the windowed
  runner so it can keep only selected windows and avoid replaying the whole
  spontaneous trace for a short-loop assay.

2. What succeeded

- Added subset-window support:
  - `split_aimon_trial_into_windows(..., include_window_indices=...)`
  - `run_aimon_windowed_fit.py --include-window-index`
- Focused validation passed:
  - `python -m pytest tests/test_aimon_spontaneous_fit.py -q`
  - `10 passed, 1 warning`
- The first exact-identity forced result is now complete:
  - [aimon_b350_forced_window_routed_v1](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v1)
- Forced `B350` routed-only window metrics:
  - train windows:
    - `win_00`: `pearson=0.6592`, `nrmse=0.1687`, `abs_error=0.00265`, `sign=0.7944`
    - `win_01`: `pearson=0.6950`, `nrmse=0.1538`, `abs_error=0.00222`, `sign=0.7883`
  - held-out windows:
    - `win_02`: `pearson=-0.2139`, `nrmse=0.4988`, `abs_error=0.00690`, `sign=0.4419`
    - `win_03`: `pearson=0.0751`, `nrmse=0.5043`, `abs_error=0.00874`, `sign=0.5222`
  - held mean:
    - `pearson=-0.0694`
    - `nrmse=0.5015`
    - `abs_error=0.00782`
    - `sign=0.4821`

3. What failed

- The first spontaneous `B350` windowed run was still too large for a short
  loop because it included all `4` windows of a `30 s` trial.
- I interrupted that full replay and replaced it with a true short spontaneous
  assay using only the first two `2.5 s` windows out of a `12`-window split.

4. Evidence

- Forced result:
  - [aimon_spontaneous_fit_summary.json](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v1/aimon_spontaneous_fit_summary.json)
- Short spontaneous live rerun:
  - [fit_run_manifest.json](/G:/flysim/outputs/metrics/aimon_b350_spont_window_routed_v2_short/fit_run_manifest.json)
- Window subset support:
  - [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py)
  - [run_aimon_windowed_fit.py](/G:/flysim/scripts/run_aimon_windowed_fit.py)
  - [test_aimon_spontaneous_fit.py](/G:/flysim/tests/test_aimon_spontaneous_fit.py)

5. Next actions

- Wait for the short spontaneous `B350` result.
- Compare it directly against the forced holdout failure.
- If spontaneous holds up better than forced, prioritize backend work on
  forced/exafferent transition dynamics over generic roaming memory.

## 2026-04-01 14:09 - Found and patched a second Aimon exact-parity harness bug: reset between contiguous windows

1. What I attempted

- Audited why the first exact-identity forced result looked like a late-window
  temporal collapse.
- Checked the actual replay semantics in
  [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py).

2. What succeeded

- Found the bug: `simulate_trial_feature_matrix()` was resetting the brain at
  the start of every window, even when those windows were contiguous slices from
  the same source trial.
- Patched the Aimon fit path to support continuity-preserving execution plans:
  - added `TrialExecutionPlan`
  - added `build_trial_execution_plan(...)`
  - added `preserve_continuity_by_source_trial`
  - contiguous windows from the same `source_trial_id` now reuse brain state and
    seed instead of resetting
- Updated the windowed runner so within-trial Aimon fits now always request
  continuity preservation.
- Added coverage:
  - contiguous windows from one source trial preserve continuity
  - gapped windows reset
- Focused validation passed:
  - `python -m pytest tests/test_aimon_spontaneous_fit.py -q`
  - `11 passed, 1 warning`
- Relaunched the two key admissible reruns:
  - [aimon_b350_forced_window_routed_v2_cont](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v2_cont)
  - [aimon_b350_spont_window_routed_v3_short_cont](/G:/flysim/outputs/metrics/aimon_b350_spont_window_routed_v3_short_cont)

3. What failed

- The first spontaneous continuity relaunch died immediately due to a CLI typo
  (`--max_basis_dim` instead of `--max-basis-dim`). That was corrected and
  relaunched cleanly.

4. Evidence

- Continuity patch:
  - [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py)
  - [run_aimon_windowed_fit.py](/G:/flysim/scripts/run_aimon_windowed_fit.py)
  - [test_aimon_spontaneous_fit.py](/G:/flysim/tests/test_aimon_spontaneous_fit.py)
- Live corrected reruns:
  - [fit_run_manifest.json](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v2_cont/fit_run_manifest.json)
  - [fit_run_manifest.json](/G:/flysim/outputs/metrics/aimon_b350_spont_window_routed_v3_short_cont/fit_run_manifest.json)

5. Next actions

- Treat the earlier reset-based within-trial Aimon scores as provisional only.
- Wait for the continuity-preserving reruns.
- Use those corrected forced versus spontaneous reads to decide whether the next
  backend work should target:
  - exafferent/forced transition dynamics
  - spontaneous continuity dynamics
  - or both

## 2026-04-01 14:17 - Corrected continuity-preserving Aimon split now localizes the remaining miss to forced dynamics

1. What I attempted

- Let the corrected continuity-preserving `B350` reruns finish:
  - `B350_forced_walk`, `4` windows, fit `00-01`, hold out `02-03`
  - `B350_spontaneous_walk`, short contiguous subset, fit `win_00`, hold out
    `win_01`

2. What succeeded

- Both corrected reruns completed:
  - [aimon_b350_forced_window_routed_v2_cont](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v2_cont)
  - [aimon_b350_spont_window_routed_v3_short_cont](/G:/flysim/outputs/metrics/aimon_b350_spont_window_routed_v3_short_cont)
- The corrected execution plans are now explicit in the summaries:
  - first window resets
  - later contiguous windows do not
- Corrected held-out `B350` read:
  - forced:
    - `pearson = 0.0848`
    - `nrmse = 0.9100`
    - `abs_error = 0.01438`
    - `sign = 0.5589`
  - spontaneous:
    - `pearson = 0.1166`
    - `nrmse = 0.4182`
    - `abs_error = 0.00554`
    - `sign = 0.5474`
- Interpretation:
  - spontaneous still degrades, so the temporal problem is not confined to
    forced data
  - but forced is materially worse, especially on amplitude / baseline control
- Continuity is a real missing piece:
  - compared with the reset-based forced run, held `pearson` improved from
    `-0.0694` to `+0.0848`
  - held `sign` improved from `0.4821` to `0.5589`
  - but held `nrmse` and `abs_error` became much worse, which means continuity
    exposed a later forced-window state-offset / amplitude problem instead of
    solving it

3. What failed

- The corrected forced result still does not generalize well in held windows.
- The remaining miss is no longer best described as just "timing is wrong". It
  is now:
  - some timing recovery with continuity
  - but poor late-window amplitude / baseline control in forced state

4. Evidence

- Corrected forced summary:
  - [aimon_spontaneous_fit_summary.json](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v2_cont/aimon_spontaneous_fit_summary.json)
- Corrected spontaneous summary:
  - [aimon_spontaneous_fit_summary.json](/G:/flysim/outputs/metrics/aimon_b350_spont_window_routed_v3_short_cont/aimon_spontaneous_fit_summary.json)

5. Next actions

- Run the corrected `B1269_forced_walk` continuity assay as the next small
  discriminator.
- If `B1269_forced_walk` repeats the same pattern, prioritize backend work on
  forced/exafferent state regulation:
  - late-state gain control
  - baseline stabilization under sustained forced drive
  - not a larger readout head

## 2026-04-01 14:24 - Public-data answer on body feedback / proprioception blocker

1. What I checked

- The exact Aimon parity harness seam in
  [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py)
- The current encoder surface in [encoder.py](/G:/flysim/src/bridge/encoder.py)
- The staged public dataset status and ranked fit-target notes in:
  - [public_neural_measurement_dataset_status.md](/G:/flysim/docs/public_neural_measurement_dataset_status.md)
  - [creamer_recording_fit_targets.md](/G:/flysim/docs/creamer_recording_fit_targets.md)

2. What is true

- The current Aimon public-parity runner is still strongly disembodied.
- It constructs a synthetic body observation with:
  - fixed position
  - fixed yaw
  - fixed yaw rate
  - only scalar `forward_speed`
  - only scalar `contact_force`
  - zero vision
- The encoder then maps that into only coarse speed/contact/yaw pool rates.

3. Public-data answer

- Yes, there is enough public data to add a grounded first-order reafferent /
  proprioceptive lane.
- No, there is not yet enough staged public data for a full exact
  neuron-by-neuron proprioceptor reconstruction.
- The strongest immediate public support already available is:
  - Schaffer staged NWBs with aligned treadmill ball motion and behavioral-state
    matrices
  - Dallmann 2025 as the best public treadmill proprioceptive / joint-variable
    fit target, though raw Dryad downloads are still blocked locally

4. Consequence

- This is now an explicit blocker task.
- The next acceptable feedback upgrade must use body-derived variables that are
  constrained by public data, not invented wholesale.

## 2026-04-01 15:12 - Added public-constrained body-derived channels and JO-subgroup routing

1. What I changed

- Extended [public_body_feedback.py](/G:/flysim/src/analysis/public_body_feedback.py)
  so the grounded public body-feedback surface now carries explicit
  `exafferent_drive` in addition to speed, contact, acceleration, walk/stop,
  transition, and behavioral-state summaries.
- Extended [interfaces.py](/G:/flysim/src/body/interfaces.py) so
  `BodyObservation` carries `exafferent_drive`.
- Extended [encoder.py](/G:/flysim/src/bridge/encoder.py) so the parity harness
  now emits three separate grounded mechanosensory subgroup pools:
  - `mech_ce_bilateral`
  - `mech_f_bilateral`
  - `mech_dm_bilateral`
- Extended [public_ids.py](/G:/flysim/src/brain/public_ids.py) so those pools
  map onto the existing preserved public `JON_CE`, `JON_F`, and `JON_DM`
  subgroup boundaries, and updated the collapse path so subgroup pools are not
  double-counted with the legacy mechanosensory bucket.
- Activated the new gains in:
  - [brain_endogenous_public_parity.yaml](/G:/flysim/configs/brain_endogenous_public_parity.yaml)
  - [brain_endogenous_public_parity_routed_only.yaml](/G:/flysim/configs/brain_endogenous_public_parity_routed_only.yaml)

2. Why this is acceptable

- This is still only a first-order reafferent lane.
- It uses only public covariates we currently stage:
  - Aimon forced-walk regressor
  - Schaffer ball-motion trace
  - Schaffer behavioral-state matrix
- It does not invent an unconstrained feedback head or claim exact
  proprioceptor realism.

3. Validation

- Focused validation passed:
  - `python -m pytest tests/test_bridge_unit.py tests/test_realistic_vision_path.py tests/test_aimon_spontaneous_fit.py tests/test_schaffer_spontaneous_fit.py -q`
  - `58 passed, 1 warning`

4. Immediate assay

- Started one short identity-safe Aimon forced-window rerun using the routed
  endogenous backend plus the new body-feedback lane:
  - [aimon_b350_forced_window_routed_v4_bodyfeedback](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v4_bodyfeedback)

5. Expected read

- If disembodiment is materially responsible for the current forced mismatch,
  this short rerun should improve late-window amplitude / baseline control
  before any new recurrent-core mechanism change.

## 2026-04-01 14:52 - Added public-constrained body-feedback channels to the parity harness

1. What I did

- Audited the current parity harness and confirmed the real gap: the worktree
  still had only a thin scalar body proxy in the public replay lanes.
- Hardened the already-started body-feedback patch instead of duplicating it.
- Added a dedicated public-feedback helper module:
  - [public_body_feedback.py](/G:/flysim/src/analysis/public_body_feedback.py)
- Wired both public replay lanes through that helper:
  - [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py)
  - [schaffer_spontaneous_fit.py](/G:/flysim/src/analysis/schaffer_spontaneous_fit.py)
- Extended [BodyObservation](/G:/flysim/src/body/interfaces.py) and
  [SensoryEncoder](/G:/flysim/src/bridge/encoder.py) so the brain now receives
  public-constrained body-derived summaries:
  - `forward_accel`
  - `walk_state`
  - `stop_state`
  - `transition_on`
  - `transition_off`
  - `exafferent_drive`
  - `behavioral_state_level`
  - `behavioral_state_transition`
- Routed those summaries into richer public mechanosensory subgroup pools:
  - `mech_ce_bilateral`
  - `mech_f_bilateral`
  - `mech_dm_bilateral`
- Added encoder gains for that path in:
  - [brain_endogenous_public_parity.yaml](/G:/flysim/configs/brain_endogenous_public_parity.yaml)
  - [brain_endogenous_public_parity_routed_only.yaml](/G:/flysim/configs/brain_endogenous_public_parity_routed_only.yaml)
- Added focused tests:
  - [test_public_body_feedback.py](/G:/flysim/tests/test_public_body_feedback.py)

2. What succeeded

- The public parity harness no longer feeds the brain only synthetic scalar
  `forward_speed` and `contact_force`.
- The new Aimon path derives body-like channels from the staged public walk
  regressor.
- The new Schaffer path derives body-like channels from staged public
  ball-motion plus behavioral-state covariates.
- The mechanosensory encoder now emits subgroup public JON pools rather than
  only one coarse bilateral mechanosensory scalar.
- Focused validation passed:
  - `python -m pytest tests/test_public_body_feedback.py tests/test_aimon_spontaneous_fit.py tests/test_schaffer_spontaneous_fit.py tests/test_bridge_unit.py -q`
  - `56 passed, 1 warning`

3. What is running

- Exact-identity Aimon forced-window re-test with the new body-feedback path:
  - [fit_run_manifest.json](/G:/flysim/outputs/metrics/aimon_b1269_forced_window_routed_v3_reafferent/fit_run_manifest.json)
  - [fit_run_status.json](/G:/flysim/outputs/metrics/aimon_b1269_forced_window_routed_v3_reafferent/fit_run_status.json)
- This is the direct comparator against the previous routed continuity baseline
  on the strongest weak slice: late held windows of `B1269_forced_walk`.

4. Current interpretation

- This is still public-constrained and not a made-up free-form feedback head.
- It is not a full proprioceptor reconstruction.
- It is the first honest step from "numb disembodied brain" toward a grounded
  reafferent lane using only currently staged public covariates.

## 2026-04-01 16:05 - First grounded body-feedback forced re-test completed

1. What finished

- The short exact-identity forced Aimon rerun with grounded body feedback
  completed:
  - [aimon_b350_forced_window_routed_v4_bodyfeedback](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v4_bodyfeedback)

2. Held-out comparison against the routed continuity baseline

- Previous routed continuity baseline:
  - [aimon_b350_forced_window_routed_v2_cont](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v2_cont/aimon_spontaneous_fit_summary.json)
  - held mean:
    - `pearson = 0.0848`
    - `nrmse = 0.9100`
    - `abs_error = 0.01438`
    - `sign = 0.5589`
- New grounded body-feedback rerun:
  - [aimon_b350_forced_window_routed_v4_bodyfeedback](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v4_bodyfeedback/aimon_spontaneous_fit_summary.json)
  - held mean:
    - `pearson = -0.1967`
    - `nrmse = 0.7122`
    - `abs_error = 0.01187`
    - `sign = 0.4232`

3. Meaning

- The grounded body-feedback lane improved late forced-window scale control:
  - lower `nrmse`
  - lower `abs_error`
- But it clearly hurt temporal agreement:
  - `pearson` flipped strongly negative
  - `sign_agreement` dropped
- So disembodiment was a real blocker for amplitude / baseline control, but it
  is not the whole systemic answer. The current public-feedback encoding or its
  coupling into the recurrent core is still temporally wrong under sustained
  forced drive.

## 2026-04-01 16:42 - Root-cause audit found the Aimon timing harness is partially poisoned

1. What I checked

- Used all six sub-agent slots for parallel audits, then verified the strongest
  claims locally in code and artifacts.
- Re-read the current parity runner, scorer, configs, canonical bundle, and
  exact-identity Aimon outputs:
  - [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py)
  - [public_neural_measurement_harness.py](/G:/flysim/src/analysis/public_neural_measurement_harness.py)
  - [public_body_feedback.py](/G:/flysim/src/analysis/public_body_feedback.py)
  - [brain_endogenous_public_parity.yaml](/G:/flysim/configs/brain_endogenous_public_parity.yaml)
  - [brain_endogenous_public_parity_routed_only.yaml](/G:/flysim/configs/brain_endogenous_public_parity_routed_only.yaml)
  - [aimon2023_canonical_bundle.json](/G:/flysim/outputs/derived/aimon2023_canonical/aimon2023_canonical_bundle.json)

2. Main new findings

- The Aimon exact-parity lane is currently replaying wrong covariates on most
  trials before the brain even runs.
- In [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py):
  - `_trial_regressor_values()` returns all zeros for every
    `spontaneous_walk`.
  - For `forced_walk`, it takes `abs()` and normalizes by per-trial max.
  - It slices regressor files using stimulus `window_start/window_stop` values
    that are incompatible with the stored regressor array lengths for 3 of the
    4 current Aimon trials.
- Verified current semantics:
  - `B350_forced_walk`: regressor replay becomes all ones
  - `B350_spontaneous_walk`: regressor replay becomes all zeros
  - `B1269_forced_walk`: only the tail `58` samples are stretched over the
    whole `297`-sample trial
- So much of the Aimon temporal-mismatch loop has been polluted by wrong public
  replay semantics, not just by missing backend dynamics.

3. Additional concrete issues

- Both parity YAMLs contain duplicate top-level `encoder:` blocks:
  - the second silently overwrites the first
  - `exafference_gain_hz` is therefore not actually live in the current parity
    configs
- The scorer in
  [public_neural_measurement_harness.py](/G:/flysim/src/analysis/public_neural_measurement_harness.py)
  uses strict zero-lag pointwise correlation after resampling. A small local
  lag scan on held `B350_forced_walk` windows improves correlation materially,
  especially on `win_03`, so zero-lag-only scoring is too strict to be the sole
  top-line temporal KPI for these imaging-like traces.
- The fit head is also still mostly blind to the slow endogenous states that
  were added. It reads family voltages plus a few coarse globals, but not
  graded release, intracellular calcium, distributed context, or modulatory
  states directly.

4. Current diagnosis

- The reason timing has stayed stubborn is not just "we have not invented the
  right slow recurrent mechanism yet."
- We have also been:
  - replaying wrong Aimon covariates,
  - silently disabling part of the intended body-feedback encoder via config
    overwrite,
  - over-penalizing plausible lags with zero-lag-only scoring,
  - and hiding most slow backend state from the fit head.

5. Immediate implication

- No more temporal-mechanism conclusions should be drawn from the current Aimon
  exact-parity lane until `T215` is fixed.

## 2026-04-01 16:42 - Root-cause audit found multiple timing faults beyond backend simplicity

1. What I checked

- Re-audited the exact Aimon timing path:
  - [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py)
  - [public_body_feedback.py](/G:/flysim/src/analysis/public_body_feedback.py)
  - [encoder.py](/G:/flysim/src/bridge/encoder.py)
  - [public_ids.py](/G:/flysim/src/brain/public_ids.py)
  - [aimon_canonical_dataset.py](/G:/flysim/src/analysis/aimon_canonical_dataset.py)
  - [brain_endogenous_public_parity_routed_only.yaml](/G:/flysim/configs/brain_endogenous_public_parity_routed_only.yaml)
- Cross-checked the Aimon paper methods for recording speed and behavior-regressor preprocessing:
  - [PMC article]https://pmc.ncbi.nlm.nih.gov/articles/PMC10168698/

2. What I found

- The current Aimon canonical export still fabricates a fixed `100 Hz` timebase.
- The current Aimon harness still uses raw normalized walk regressors, even
  though the paper says behavioral regressors were convolved with the GCaMP
  single-spike response and subjected to the same `dF/F` pipeline as the
  fluorescence traces.
- The public body-feedback derivative path is acausal:
  - centered difference in [public_body_feedback.py](/G:/flysim/src/analysis/public_body_feedback.py)
    uses future samples.
- That same derivative is non-physical in scale:
  - `B350` normalized-regressor `|accel|`: `p90=10.40`, `p99=24.37`, `max=27.74`
  - `B1269` normalized-regressor `|accel|`: `p90=2.95`, `p99=33.49`, `max=40.13`
- The routed-only parity config has a duplicate `encoder:` block, so the later
  block silently overrides the intended one and drops `exafference_gain_hz`.
- The current `JON_CE/F/DM` split in [public_ids.py](/G:/flysim/src/brain/public_ids.py)
  is still slice-based on one flat ID list rather than loaded from an explicit
  public subgroup-membership source.
- The backend's `modulatory_exafference_state` is not actually driven by
  exafferent sensory input. It currently uses the same internal modulatory drive
  used for arousal.

3. Meaning

- The continued timing mismatch is not just "the recurrent backend still needs
  better dynamics."
- We are still feeding the model and evaluating it through a timing path with
  real code and assumption faults.
- That makes the small gains from recent backend-only tuning partly
  uninterpretable.

4. Evidence

- [timing_mismatch_root_cause.md](/G:/flysim/docs/timing_mismatch_root_cause.md)

## 2026-04-01 17:10 - Timing mismatch audit found structural causes, not just weak gains

1. What I audited

- Aimon parity harness
- Schaffer parity harness
- imaging observation model
- endogenous backend configs
- exact-identity Aimon result artifacts

2. Strongest findings

- The readout is still trying to fit calcium / `dff_like` public recordings
  from mostly instantaneous family-averaged membrane voltage features:
  - [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py)
  - [imaging_observation_model.py](/G:/flysim/src/analysis/imaging_observation_model.py)
- The exact-identity routed-only loop was not exercising the richer distributed
  temporal-state mechanism because the routed-only config sets:
  - `context_exc_gain = 0.0`
  - `context_inh_gain = 0.0`
  - `context_mod_gain = 0.0`
  - [brain_endogenous_public_parity_routed_only.yaml](/G:/flysim/configs/brain_endogenous_public_parity_routed_only.yaml)
- Both parity configs contain duplicate top-level `encoder:` keys, so YAML load
  silently overwrites the earlier block. This means some intended reafferent
  gains, including `exafference_gain_hz`, were not actually active in recent
  runs:
  - [brain_endogenous_public_parity.yaml](/G:/flysim/configs/brain_endogenous_public_parity.yaml)
  - [brain_endogenous_public_parity_routed_only.yaml](/G:/flysim/configs/brain_endogenous_public_parity_routed_only.yaml)
- The Aimon public body-feedback lane cannot meaningfully repair timing inside
  held forced windows by construction, because it expands one mostly flat walk
  regressor into many simultaneous tonic channels:
  - [public_body_feedback.py](/G:/flysim/src/analysis/public_body_feedback.py)
  - [aimon_b350_forced_window_routed_v4_bodyfeedback](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v4_bodyfeedback/aimon_spontaneous_fit_summary.json)
- The harness records end-of-interval state snapshots rather than
  interval-integrated spike/release/calcium observables, which is the wrong
  observation geometry for imaging targets.

3. Consequence

- The persistent timing mismatch is not mainly "needs more tuning".
- Several recent assays were either testing the wrong observation basis or not
  actually enabling the intended temporal mechanism.
- The next admissible fixes must correct those structural issues before more
  gain sweeps.

## 2026-04-01 16:36 - Root-cause audit found multiple self-inflicted timing faults

1. Hard config bug

- Both public parity brain configs contain duplicate top-level `encoder:` keys:
  - [brain_endogenous_public_parity.yaml](/G:/flysim/configs/brain_endogenous_public_parity.yaml)
  - [brain_endogenous_public_parity_routed_only.yaml](/G:/flysim/configs/brain_endogenous_public_parity_routed_only.yaml)
- The second block silently overwrites the first under normal YAML loading.
- That means intended settings such as `exafference_gain_hz` were not actually
  active in the runs we thought were testing them.

2. Assay confound

- The recent `v4 body-feedback` run was not a clean body-feedback A/B against
  `v2 continuity`.
- [v2 continuity](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v2_cont/aimon_spontaneous_fit_summary.json)
  used `observation_taus_s = [0.5]`.
- [v4 body-feedback](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v4_bodyfeedback/aimon_spontaneous_fit_summary.json)
  used `observation_taus_s = []`.
- So we changed body feedback and observation lag handling at the same time.

3. Zero-lag scoring is hiding recoverable timing

- The public Aimon targets are `dff_like` region-component traces, but the
  current scorer uses strict zero-lag pointwise comparison.
- Short lag scans on held `B350_forced_walk` windows show large hidden timing:
  - `v2 win_02`: `0.215 -> 0.468` at best lag
  - `v2 win_03`: `-0.046 -> 0.419` at best lag
  - `v4 win_03`: `-0.159 -> 0.368` at best lag
- So part of the stubborn "timing mismatch" has been an observation/alignment
  mismatch, not only recurrent dynamics.

4. The fit head is blind to most slow endogenous state

- [aimon_spontaneous_fit.py](/G:/flysim/src/analysis/aimon_spontaneous_fit.py)
  still extracts family voltages plus a few coarse globals.
- It does not expose graded release, intracellular calcium, distributed
  context, or modulatory states to the parity fit.
- So several slow backend mechanisms added this week were barely visible to the
  fit head except indirectly through voltage.

5. Encoder/body-feedback timing is currently misphased

- [public_body_feedback.py](/G:/flysim/src/analysis/public_body_feedback.py)
  builds `transition_on`, `transition_off`, and
  `behavioral_state_transition` from the same finite-difference signal.
- [encoder.py](/G:/flysim/src/bridge/encoder.py) then uses transition drive in
  both `motion_mech` and `state_mech`, effectively double-counting it.
- Combined with the duplicate YAML overwrite, this means the body-feedback runs
  were not testing the intended timing structure.

6. Backend semantic bug

- [pytorch_backend.py](/G:/flysim/src/brain/pytorch_backend.py) currently
  advances `modulatory_arousal_state` and `modulatory_exafference_state` from
  the same internal drive and only changes the tau.
- So the backend does not yet represent exafferent forced-state regulation as a
  distinct state variable.

## 2026-04-01 20:05 - Repaired Aimon exact-identity retest completed and changed the baseline

Attempted

- completed the first short exact-identity `B350_forced_walk` retest on the
  repaired parity path at
  [aimon_b350_forced_window_routed_v5_replayfix](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v5_replayfix)
- extracted held-out window metrics from the finished summary and compared them
  against the previous `v2 continuity` and `v4 body-feedback` baselines

Succeeded

- the repaired run finished cleanly and produced
  [aimon_spontaneous_fit_summary.json](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v5_replayfix/aimon_spontaneous_fit_summary.json)
- held `B350_forced_walk` windows improved materially versus the old baseline:
  - `v2 continuity` held mean:
    - `pearson = 0.0848`
    - `nrmse = 0.9100`
    - `abs_error = 0.01438`
    - `sign = 0.5589`
  - `v5 repaired replay/scoring path` held mean:
    - `pearson = 0.2315`
    - `nrmse = 0.7011`
    - `abs_error = 0.01027`
    - `sign = 0.6040`
    - `lagged_pearson = 0.7311`
    - `lagged_sign = 0.8195`
    - `best_lag_seconds = 0.0254`
- per held window:
  - `win_02`: `pearson 0.2154 -> 0.3005`, `nrmse 1.0040 -> 0.5858`,
    `abs_error 0.01522 -> 0.00821`, `sign 0.6055 -> 0.6398`
  - `win_03`: `pearson -0.0459 -> 0.1625`, `nrmse 0.8161 -> 0.8165`,
    `abs_error 0.01353 -> 0.01233`, `sign 0.5124 -> 0.5682`

Failed

- nothing operational failed in this slice
- this does not yet prove the backend temporal problem is solved; it proves a
  large part of the old Aimon timing miss was coming from poisoned replay and
  scorer/harness semantics

Evidence

- [aimon_spontaneous_fit_summary.json](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v5_replayfix/aimon_spontaneous_fit_summary.json)
- [aimon_spontaneous_fit_summary.json](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v2_cont/aimon_spontaneous_fit_summary.json)
- [aimon_spontaneous_fit_summary.json](/G:/flysim/outputs/metrics/aimon_b350_forced_window_routed_v4_bodyfeedback/aimon_spontaneous_fit_summary.json)

Next actions

- re-baseline `B1269_forced_walk` on the repaired path
- rerun the body-feedback ablation on the repaired path with matched observation
  filtering so it becomes a clean A/B
- then port the repaired scoring/replay path into subset-only Schaffer assays

## 2026-04-01 22:24 - Ran a real 2 s embodied FlyGym demo on the repaired endogenous routed brain

Attempted

- built a merged full-stack config that swaps the old surrogate spontaneous
  branch out for the repaired endogenous routed backend while keeping the
  working realistic-vision fast path, uv-grid visual splice, and descending
  decoder
- first tried the parity-time version at
  [flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_endogenous_routed.yaml](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_endogenous_routed.yaml)
  under WSL `flysim-full`
- then created a demo-only faster discretization variant at
  [flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_endogenous_routed_demo_fast.yaml](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_endogenous_routed_demo_fast.yaml)
  after the parity-time run proved too slow for an interactive 2 s demo

Succeeded

- the demo-fast run completed the full `2.0 s` embodied FlyGym loop and wrote
  video, log, metrics, summary, and activation artifacts under
  [flygym-demo-20260401-221940](/G:/flysim/outputs/requested_2s_endogenous_routed_demo_fast/flygym-demo-20260401-221940)
- key artifacts:
  - [demo.mp4](/G:/flysim/outputs/requested_2s_endogenous_routed_demo_fast/flygym-demo-20260401-221940/demo.mp4)
  - [summary.json](/G:/flysim/outputs/requested_2s_endogenous_routed_demo_fast/flygym-demo-20260401-221940/summary.json)
  - [metrics.csv](/G:/flysim/outputs/requested_2s_endogenous_routed_demo_fast/flygym-demo-20260401-221940/metrics.csv)
  - [run.jsonl](/G:/flysim/outputs/requested_2s_endogenous_routed_demo_fast/flygym-demo-20260401-221940/run.jsonl)
  - [activation_side_by_side.mp4](/G:/flysim/outputs/requested_2s_endogenous_routed_demo_fast/flygym-demo-20260401-221940/activation_side_by_side.mp4)
- summary metrics:
  - `sim_seconds = 2.0`
  - `completed_full_duration = 1.0`
  - `avg_forward_speed = 0.6911`
  - `path_length = 1.3753`
  - `net_displacement = 0.9778`
  - `trajectory_smoothness = 0.9030`
  - `wall_seconds = 215.8743`
  - `real_time_factor = 0.00926`
  - `device = cpu`

Failed

- the first parity-time attempt was interrupted because it was still deep in the
  simulation loop with the original fine step sizes and was not appropriate for
  an interactive 2 s demo artifact

Evidence

- [flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_endogenous_routed.yaml](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_endogenous_routed.yaml)
- [flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_endogenous_routed_demo_fast.yaml](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_no_target_brain_endogenous_routed_demo_fast.yaml)
- [summary.json](/G:/flysim/outputs/requested_2s_endogenous_routed_demo_fast/flygym-demo-20260401-221940/summary.json)

Next actions

- keep the demo-fast config for short embodied visualization artifacts
- keep parity-time configs for neural-fit and assay evidence, not interactive
  demo requests

## 2026-04-02 03:44 - Completed a `30 s` lawful multi-target zoomed-out embodied demo

Attempted

- extended the FlyGym realistic-vision runtime to support multiple real ghost
  fly targets in the arena instead of just one upstream `MovingFlyArena`
  target
- added a wide fixed overhead camera preset so long demos can keep the fly on
  screen without a tracking-camera shortcut
- added a demo-only runtime flag to disable activation capture, since the
  activation side-by-side pass is unnecessary overhead for a long video request
- built and ran a dedicated lawful splice-only multi-target demo config at
  [flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_brain_endogenous_routed_multitarget_demo_fast.yaml](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_brain_endogenous_routed_multitarget_demo_fast.yaml)
  under WSL `flysim-full` with `MUJOCO_GL=egl`

Succeeded

- runtime changes landed in:
  - [flygym_runtime.py](/G:/flysim/src/body/flygym_runtime.py)
  - [closed_loop.py](/G:/flysim/src/runtime/closed_loop.py)
  - [test_closed_loop_smoke.py](/G:/flysim/tests/test_closed_loop_smoke.py)
- focused smoke coverage passed:
  - `5 passed`
- the final long run completed full duration at
  [flygym-demo-20260402-031051](/G:/flysim/outputs/requested_30s_endogenous_routed_multitarget_zoomout_demo/flygym-demo-20260402-031051)
- key artifacts:
  - [demo.mp4](/G:/flysim/outputs/requested_30s_endogenous_routed_multitarget_zoomout_demo/flygym-demo-20260402-031051/demo.mp4)
  - [summary.json](/G:/flysim/outputs/requested_30s_endogenous_routed_multitarget_zoomout_demo/flygym-demo-20260402-031051/summary.json)
  - [metrics.csv](/G:/flysim/outputs/requested_30s_endogenous_routed_multitarget_zoomout_demo/flygym-demo-20260402-031051/metrics.csv)
  - [run.jsonl](/G:/flysim/outputs/requested_30s_endogenous_routed_multitarget_zoomout_demo/flygym-demo-20260402-031051/run.jsonl)
- completed metrics:
  - `sim_seconds = 30.0`
  - `completed_full_duration = 1.0`
  - `avg_forward_speed = 0.8942`
  - `path_length = 26.8092`
  - `net_displacement = 9.1737`
  - `trajectory_smoothness = 0.8734`
  - `wall_seconds = 1965.92`
  - `real_time_factor = 0.01526`
  - `device = cuda:1`
  - `target_condition_bearing_reduction_rad = 1.3417`
  - `target_condition_fixation_fraction_20deg = 0.1233`
  - `target_condition_fixation_fraction_30deg = 0.2240`
- the scene used one primary target plus `2` extra ghost flies, confirmed in
  the live run log as `extra_target_count = 2`

Failed

- the first wide-camera smoke exceeded MuJoCo's offscreen framebuffer height
  because the new preset used `960 px` height; that was fixed by reducing the
  zoomed-out camera window to `960x720`
- an overly coarse `5 ms` demo scheduler made the fly nearly stationary; the
  final demo used the less aggressive `brain.dt_ms = 2.0`,
  `body_timestep_s = 0.002`, `control_interval_s = 0.02` compromise instead

Evidence

- [flygym_runtime.py](/G:/flysim/src/body/flygym_runtime.py)
- [closed_loop.py](/G:/flysim/src/runtime/closed_loop.py)
- [test_closed_loop_smoke.py](/G:/flysim/tests/test_closed_loop_smoke.py)
- [flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_brain_endogenous_routed_multitarget_demo_fast.yaml](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_brain_endogenous_routed_multitarget_demo_fast.yaml)
- [summary.json](/G:/flysim/outputs/requested_30s_endogenous_routed_multitarget_zoomout_demo/flygym-demo-20260402-031051/summary.json)
- [run.jsonl](/G:/flysim/outputs/requested_30s_endogenous_routed_multitarget_zoomout_demo/flygym-demo-20260402-031051/run.jsonl)

Next actions

- keep the new multi-target / zoomed-out arena support available for longer
  demo requests
- improve lawful target fixation quality further without restoring coarse visual
  pooling or target-metadata shortcuts
- add a demo-only flag for reduced log density if long artifact wall time
  becomes the next bottleneck

## 2026-04-02 10:16 - Re-ran the multi-target demo with a fly-locked camera and restored activations

Attempted

- built a corrected follow-camera config at
  [flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_brain_endogenous_routed_multitarget_followyaw_10s.yaml](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_brain_endogenous_routed_multitarget_followyaw_10s.yaml)
  after the `30 s` zoomed-out artifact proved visually unusable
- restored `capture_activation: true`
- kept the same lawful multi-target routed branch and the same `2` extra ghost
  flies
- ran a real WSL smoke first to confirm activation artifacts actually write

Succeeded

- focused config/test slice passed:
  - `3 passed`
- the real `0.2 s` smoke completed with activation artifacts at
  [flygym-demo-20260402-100134](/G:/flysim/outputs/requested_0p2s_endogenous_routed_multitarget_followyaw_activation_smoke/flygym-demo-20260402-100134)
- the final `10.0 s` run completed at
  [flygym-demo-20260402-100243](/G:/flysim/outputs/requested_10s_endogenous_routed_multitarget_followyaw_activation/flygym-demo-20260402-100243)
- key artifacts:
  - [demo.mp4](/G:/flysim/outputs/requested_10s_endogenous_routed_multitarget_followyaw_activation/flygym-demo-20260402-100243/demo.mp4)
  - [activation_side_by_side.mp4](/G:/flysim/outputs/requested_10s_endogenous_routed_multitarget_followyaw_activation/flygym-demo-20260402-100243/activation_side_by_side.mp4)
  - [activation_capture.npz](/G:/flysim/outputs/requested_10s_endogenous_routed_multitarget_followyaw_activation/flygym-demo-20260402-100243/activation_capture.npz)
  - [activation_overview.png](/G:/flysim/outputs/requested_10s_endogenous_routed_multitarget_followyaw_activation/flygym-demo-20260402-100243/activation_overview.png)
  - [summary.json](/G:/flysim/outputs/requested_10s_endogenous_routed_multitarget_followyaw_activation/flygym-demo-20260402-100243/summary.json)
  - [run.jsonl](/G:/flysim/outputs/requested_10s_endogenous_routed_multitarget_followyaw_activation/flygym-demo-20260402-100243/run.jsonl)
- summary metrics:
  - `sim_seconds = 10.0`
  - `completed_full_duration = 1.0`
  - `avg_forward_speed = 0.7499`
  - `path_length = 7.4842`
  - `net_displacement = 3.2084`
  - `trajectory_smoothness = 0.8991`
  - `wall_seconds = 693.27`
  - `real_time_factor = 0.01442`
  - `target_condition_bearing_reduction_rad = 0.5184`
  - `target_condition_fixation_fraction_20deg = 0.0`
  - `target_condition_fixation_fraction_30deg = 0.0`

Failed

- nothing crashed in the corrected rerun
- the only warning was `imageio` macro-block resizing when writing the
  activation side-by-side video because the rendered frame height was
  `1080 px`

Evidence

- [flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_brain_endogenous_routed_multitarget_followyaw_10s.yaml](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_brain_endogenous_routed_multitarget_followyaw_10s.yaml)
- [summary.json](/G:/flysim/outputs/requested_10s_endogenous_routed_multitarget_followyaw_activation/flygym-demo-20260402-100243/summary.json)
- [activation_summary.json](/G:/flysim/outputs/requested_10s_endogenous_routed_multitarget_followyaw_activation/flygym-demo-20260402-100243/activation_summary.json)

Next actions

- keep the fly-locked camera branch for any user-visible target demo requests
- if needed, trim activation video resolution or macro-block alignment to avoid
  ffmpeg resize warnings without removing activation capture
- continue improving lawful fixation quality rather than only late-run bearing
  reduction
## 2026-04-02 10:35 - Diagnosed the apparent shortness of the `10 s` follow-camera rerun and the dark activation panels

What I attempted:
- audited the completed `10 s` follow-camera multi-target activation rerun to determine whether the encoded video was actually shorter than the requested simulated duration
- inspected the activation-capture payload and renderer scaling to explain why some activation panels looked dead or excessively dark

What succeeded:
- verified the rerun did satisfy the request in fly time: [summary.json](/G:/flysim/outputs/requested_10s_endogenous_routed_multitarget_followyaw_activation/flygym-demo-20260402-100243/summary.json) reports `sim_seconds = 10.000000000000009`, and both [demo.mp4](/G:/flysim/outputs/requested_10s_endogenous_routed_multitarget_followyaw_activation/flygym-demo-20260402-100243/demo.mp4) and [activation_side_by_side.mp4](/G:/flysim/outputs/requested_10s_endogenous_routed_multitarget_followyaw_activation/flygym-demo-20260402-100243/activation_side_by_side.mp4) encode to `10.42 s` at `24 fps`
- established that the clip feels visually uninformative because the behavior is low-amplitude, not because ffmpeg truncated it: the fly only covered `7.48 mm` of path with `0.75 mm/s` mean forward speed and `3.21 mm` net displacement while the camera was locked to the body
- established that some dark activation panels are real inactivity:
  - `1 / 48` monitored population rows are identically zero
  - `14 / 307` monitored rate rows are identically zero
  - `29 / 307` monitored spike rows are identically zero
- established that much of the dark whole-brain snapshot is a renderer clipping issue, not true silence: [activation_viz.py](/G:/flysim/src/visualization/activation_viz.py) maps voltages only over `[-55, -45] mV`, while the captured brain frames contain large negative tails down to about `-26k mV`; roughly `49-53%` of neurons in representative frames are below `-55 mV` and therefore clip to black

What failed:
- the first explanatory response to the user did not make the distinction clear between simulated duration, encoded video duration, and visually analyzable behavioral amplitude

Evidence:
- [summary.json](/G:/flysim/outputs/requested_10s_endogenous_routed_multitarget_followyaw_activation/flygym-demo-20260402-100243/summary.json)
- [activation_summary.json](/G:/flysim/outputs/requested_10s_endogenous_routed_multitarget_followyaw_activation/flygym-demo-20260402-100243/activation_summary.json)
- [demo.mp4](/G:/flysim/outputs/requested_10s_endogenous_routed_multitarget_followyaw_activation/flygym-demo-20260402-100243/demo.mp4)
- [activation_side_by_side.mp4](/G:/flysim/outputs/requested_10s_endogenous_routed_multitarget_followyaw_activation/flygym-demo-20260402-100243/activation_side_by_side.mp4)
- [activation_viz.py](/G:/flysim/src/visualization/activation_viz.py)

Next actions:
- preserve the current activation artifacts but treat the rendering as diagnostically limited until the whole-brain color scaling is made percentile-robust instead of hard-clipped to a narrow fixed voltage window

## 2026-04-02 10:49 - Restored the active `10 s` full-parity multi-target config to bird's-eye view without changing the parity path

What I attempted:
- revert the active `10 s` multi-target config away from the follow camera and back to the standard bird's-eye view
- leave the full-parity runtime guard and timing invariants untouched

What succeeded:
- changed only `runtime.camera_mode` in [flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_brain_endogenous_routed_multitarget_followyaw_10s.yaml](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_brain_endogenous_routed_multitarget_followyaw_10s.yaml) from `follow_yaw` back to `fixed_birdeye`
- updated the smoke assertion in [test_closed_loop_smoke.py](/G:/flysim/tests/test_closed_loop_smoke.py) so the repo's active-camera expectation now matches the config

What failed:
- nothing in code; the filename still contains `followyaw` for continuity even though the active camera mode is bird's-eye again

Evidence:
- [flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_brain_endogenous_routed_multitarget_followyaw_10s.yaml](/G:/flysim/configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_calibrated_target_brain_endogenous_routed_multitarget_followyaw_10s.yaml)
- [test_closed_loop_smoke.py](/G:/flysim/tests/test_closed_loop_smoke.py)

Next actions:
- keep the active `10 s` multi-target config on the full parity path and treat camera framing as a presentation choice only, not a reason to relax parity timing

## 2026-04-02 11:09 - Locked the behavioral interpretation of target demos to transient encounter realism rather than permanent pursuit

What I attempted:
- convert the repo continuity docs from a pursuit-biased interpretation of
  target demos to an encounter-structure interpretation that matches the user's
  correction about ordinary fly behavior

What succeeded:
- recorded in [ASSUMPTIONS_AND_GAPS.md](/G:/flysim/ASSUMPTIONS_AND_GAPS.md)
  and [context.md](/G:/flysim/context.md) that generic object realism must not
  be judged by endless pursuit or permanent fixation
- demoted `bearing_reduction` and `fixation_fraction_*` to diagnostic-only
  status for generic fly realism
- promoted transient lawful response, minimum-distance regulation, low
  overlap/pass-through, plausible pass-by/disengagement, and reacquisition as
  the primary embodied encounter criteria

What failed:
- nothing in code or docs; the remaining work is to keep applying this rule to
  live-run analysis instead of slipping back into fixation-biased language

Evidence:
- [ASSUMPTIONS_AND_GAPS.md](/G:/flysim/ASSUMPTIONS_AND_GAPS.md)
- [context.md](/G:/flysim/context.md)

Next actions:
- analyze the active full-parity `10 s` run under this encounter-style
  criterion instead of using lock-on behavior as the default expectation

## 2026-04-03 09:35 - Retried the Creamer treadmill assay on the full parity endogenous brain with the shortest lawful synced block schedules and hit a runtime wall

What I attempted:
- narrowed the full-parity guard in [closed_loop.py](/G:/flysim/src/runtime/closed_loop.py) so lawful treadmill assays under `body.visual_speed_control` are allowed on the parity path instead of being rejected outright
- added a parity-short Creamer builder in [creamer_parity_short.py](/G:/flysim/src/analysis/creamer_parity_short.py), a reproducible runner in [run_creamer2018_parity_short.py](/G:/flysim/scripts/run_creamer2018_parity_short.py), and focused tests in [test_creamer_parity_short.py](/G:/flysim/tests/test_creamer_parity_short.py)
- launched two synced shortest-possible parity probes:
  - `0.4 s` total with `0.1 s` blocks at [run.jsonl](/G:/flysim/outputs/creamer2018_parity_short_synced/baseline/flygym-demo-20260403-092353/run.jsonl)
  - `0.2 s` total with `0.05 s` blocks at [run.jsonl](/G:/flysim/outputs/creamer2018_parity_short_synced_0p05/baseline/flygym-demo-20260403-092721/run.jsonl)

What succeeded:
- the parity-short configs do stay on the enforced full-parity path: `4 passed` across the focused config/validator slice
- the synced treadmill semantics are live on the parity branch:
  - stationary blocks report true `retinal_slip_mm_s = 0.0`
  - no coarse encoder visual gain is reintroduced
  - the assay uses the active endogenous routed parity brain with lawful T4/T5-only splice input
- the first `0.4 s` baseline probe already showed the important qualitative result before completion:
  - by `baseline_a` at `sim_time = 0.128 s`, the treadmill branch had already snapped back into the old high-speed attractor regime around `557 mm/s` while stationary retinal slip remained `0.0`

What failed:
- neither parity probe completed a full matched baseline/ablated pair before wall-time became unacceptable
- both probes had to be interrupted manually
- the compute hotspot was inside repeated routed recurrent updates in [pytorch_backend.py](/G:/flysim/src/brain/pytorch_backend.py), specifically the routed weighted-component path used by the endogenous backend

Evidence:
- [closed_loop.py](/G:/flysim/src/runtime/closed_loop.py)
- [creamer_parity_short.py](/G:/flysim/src/analysis/creamer_parity_short.py)
- [run_creamer2018_parity_short.py](/G:/flysim/scripts/run_creamer2018_parity_short.py)
- [test_creamer_parity_short.py](/G:/flysim/tests/test_creamer_parity_short.py)
- [run.jsonl](/G:/flysim/outputs/creamer2018_parity_short_synced/baseline/flygym-demo-20260403-092353/run.jsonl)
- [run.jsonl](/G:/flysim/outputs/creamer2018_parity_short_synced_0p05/baseline/flygym-demo-20260403-092721/run.jsonl)

Next actions:
- treat parity-Creamer as runtime-blocked for full pair scoring until the endogenous routed backend can be made cheaper in the treadmill loop or the assay can be converted into a same-state replay fork that avoids full embodied wall time
- keep the partial result: the parity brain did not magically remove the high-speed treadmill attractor during zero-slip baseline

## 2026-04-03 16:55 - Removed the accidental legacy two-drive fallback from the active parity and Creamer treadmill paths

What I attempted:
- verify whether the parity-short Creamer retry had silently fallen back onto
  the obsolete two-drive motor path instead of the current hybrid multidrive
  path
- if so, cut that fallback out of the active stack instead of only patching one
  assay config

What succeeded:
- confirmed the bug:
  - [creamer_parity_short.py](/G:/flysim/src/analysis/creamer_parity_short.py)
    was loading the active routed parity config but not setting
    `decoder.command_mode` or `runtime.control_mode`
  - [decoder.py](/G:/flysim/src/bridge/decoder.py) still defaulted
    `command_mode` to `two_drive`
  - [flygym_runtime.py](/G:/flysim/src/body/flygym_runtime.py) and
    [closed_loop.py](/G:/flysim/src/runtime/closed_loop.py) still defaulted the
    body-side control mode to `legacy_2drive`
- removed that fallback from the active/default path:
  - decoder default is now `hybrid_multidrive`
  - FlyGym runtime default control mode is now `hybrid_multidrive`
  - full-parity validation now explicitly requires both
    `decoder.command_mode = hybrid_multidrive` and
    `runtime.control_mode = hybrid_multidrive`
  - the active routed parity configs and the active `10 s` parity multi-target
    config now declare those fields explicitly
  - the Creamer parity-short builder now pins those fields explicitly too
- focused regression slice passed:
  - `7 passed, 117 deselected`

What failed:
- the corrected shortest parity Creamer rerun is still slow before first cycle
  writeout, so the remaining blocker is now runtime in the parity treadmill
  loop itself rather than an accidental fallback onto the obsolete control path

Evidence:
- [decoder.py](/G:/flysim/src/bridge/decoder.py)
- [flygym_runtime.py](/G:/flysim/src/body/flygym_runtime.py)
- [closed_loop.py](/G:/flysim/src/runtime/closed_loop.py)
- [creamer_parity_short.py](/G:/flysim/src/analysis/creamer_parity_short.py)
- [test_creamer_parity_short.py](/G:/flysim/tests/test_creamer_parity_short.py)
- [test_closed_loop_smoke.py](/G:/flysim/tests/test_closed_loop_smoke.py)
- [test_bridge_unit.py](/G:/flysim/tests/test_bridge_unit.py)
- [test_vnc_spec_decoder.py](/G:/flysim/tests/test_vnc_spec_decoder.py)

Next actions:
- let the corrected shortest parity Creamer rerun continue long enough to see
  whether the first logged treadmill speeds are materially lower than the old
  accidental-two-drive retry
- if it still explodes, move the treadmill investigation squarely onto the ball
  arena / embodied contact dynamics rather than decoder mode confusion

## 2026-04-03 17:20 - Added a first-pass treadmill stabilization fix instead of treating the ball-speed blowup as a decoder problem

What I attempted:
- fix the treadmill itself rather than keep arguing from the earlier broken
  parity-Creamer retries
- target the two specific treadmill-path feedback loops that remained after the
  multidrive correction:
  - ball reset/contact transients immediately registering as real speed
  - tether-root jitter being fed back into the brain as `forward_speed`

What succeeded:
- added a treadmill settle window in
  [visual_speed_control.py](/G:/flysim/src/body/visual_speed_control.py):
  - new config field `treadmill_settle_time_s`
  - treadmill joint `qvel` / `qacc` are zeroed on reset
  - during the settle window, measured treadmill speed is forced to `0.0`
    instead of being treated as locomotion
- the treadmill runtime already had the complementary body-side correction in
  [flygym_runtime.py](/G:/flysim/src/body/flygym_runtime.py):
  - treadmill-ball runs now set observation `forward_speed = 0.0`
  - raw tether-root jitter is preserved only as metadata
  - treadmill speed is preserved separately as assay metadata
- added focused unit coverage in
  [test_visual_speed_control.py](/G:/flysim/tests/test_visual_speed_control.py)
  for the settle-window suppression path
- focused validation passed:
  - `5 passed, 105 deselected`

What failed:
- the corrected shortest full-parity Creamer verification run is still slow
  before first writeout, so I do not yet have completed embodied evidence that
  the insane-speed treadmill regime is gone

Evidence:
- [visual_speed_control.py](/G:/flysim/src/body/visual_speed_control.py)
- [flygym_runtime.py](/G:/flysim/src/body/flygym_runtime.py)
- [test_visual_speed_control.py](/G:/flysim/tests/test_visual_speed_control.py)
- [creamer2018_parity_short_synced_0p05_multidrive_fix1](/G:/flysim/outputs/creamer2018_parity_short_synced_0p05_multidrive_fix1)

Next actions:
- wait for the corrected parity-Creamer baseline run to emit its first `jsonl`
  records and compare the first stationary samples against the old
  `-54.9 mm/s` and `419.7 mm/s` values
- if those values remain absurd, move the next fix into deeper treadmill
  contact/spawn geometry rather than decoder or parity control semantics

## 2026-04-03 17:20 - Broke the treadmill-ball speed feedback loop in the active code path

What I attempted:
- fix the specific treadmill defect where ball-derived speed was being written
  back into [BodyObservation.forward_speed](/G:/flysim/src/body/interfaces.py)
  and then amplified by the encoder as if it were genuine body translation
- also remove obvious ball-reset state contamination by zeroing the treadmill
  joint velocity buffers on reset

What succeeded:
- [flygym_runtime.py](/G:/flysim/src/body/flygym_runtime.py) now keeps
  treadmill ball speed in `body_metadata.visual_speed_state` and no longer
  overwrites the observation's body forward speed with the treadmill speed
- [encoder.py](/G:/flysim/src/bridge/encoder.py) now explicitly ignores
  treadmill-ball speed for mechanosensory forward-speed feedback and instead
  reads `visual_speed_state.body_forward_speed_mm_s`
- [visual_speed_control.py](/G:/flysim/src/body/visual_speed_control.py) now
  zeros treadmill joint `qvel` and `qacc` on arena reset
- focused regression coverage now exists for both pieces:
  - encoder treadmill feedback isolation
  - treadmill reset zeroing the joint velocity buffers
- passing slices:
  - `11 passed, 43 deselected`
  - `25 passed, 116 deselected`

What failed:
- the quick full-parity fixcheck rerun is still slow before first-cycle writeout
  because the endogenous parity backend remains expensive in the treadmill loop
- so I do not yet have a fresh parity artifact proving the speed numbers are now
  sane end to end

Evidence:
- [encoder.py](/G:/flysim/src/bridge/encoder.py)
- [flygym_runtime.py](/G:/flysim/src/body/flygym_runtime.py)
- [visual_speed_control.py](/G:/flysim/src/body/visual_speed_control.py)
- [test_bridge_unit.py](/G:/flysim/tests/test_bridge_unit.py)
- [test_visual_speed_control.py](/G:/flysim/tests/test_visual_speed_control.py)

Next actions:
- rerun the shortest admissible parity-Creamer baseline when wall time is
  acceptable and check whether the previous `300-400+ mm/s` treadmill speeds
  collapse now that the direct self-feedback loop is gone
- if speeds are still absurd, investigate the remaining embodied source in the
  treadmill ball / contact dynamics rather than the encoder path

## 2026-04-03 18:05 - Hardened the short parity Creamer builder against spawn transients

What I attempted:
- keep the parity-short Creamer assay as short as possible without letting the
  scored baseline start immediately after treadmill spawn
- make the warmup/settle rule explicit in code and tests instead of relying on
  memory or ad hoc operator caution

What succeeded:
- [creamer_parity_short.py](/G:/flysim/src/analysis/creamer_parity_short.py)
  now inserts two synced warmup blocks before `baseline_a`
- the same builder now sets
  `body.visual_speed_control.treadmill_settle_time_s = 2 * block_duration_s`
  so the treadmill and warmup schedule are matched structurally
- [test_creamer_parity_short.py](/G:/flysim/tests/test_creamer_parity_short.py)
  now locks that structure:
  - schedule labels include `warmup_a`, `warmup_b`, then `baseline_a`
  - `treadmill_settle_time_s` is asserted explicitly
  - total short-run duration updates from `0.4 s` to `0.5 s`
- focused regression slice passed:
  - `5 passed, 25 deselected`

What failed:
- the fresh corrected parity-short rerun has only just been relaunched and has
  not yet emitted admissible artifacts
- so the mechanical fix is stronger, but end-to-end scientific confirmation is
  still pending

Evidence:
- [creamer_parity_short.py](/G:/flysim/src/analysis/creamer_parity_short.py)
- [test_creamer_parity_short.py](/G:/flysim/tests/test_creamer_parity_short.py)
- [TASKS.md](/G:/flysim/TASKS.md)

Next actions:
- watch the new [creamer2018_parity_short_synced_0p05_treadmillfix_v2](/G:/flysim/outputs/creamer2018_parity_short_synced_0p05_treadmillfix_v2)
  rerun for its first `run.jsonl` output
- compare the first scored `baseline_a` samples against the old broken values
  and decide whether the remaining failure is still treadmill mechanics or has
  shifted upstream into the parity controller

## 2026-04-03 18:22 - Added a post-physics treadmill freeze during the settle window

What I attempted:
- close the remaining mechanical gap in the treadmill settle logic
- the previous code zeroed the ball joint only before each step, which still
  allowed contact impulses during the physics step itself

What succeeded:
- [visual_speed_control.py](/G:/flysim/src/body/visual_speed_control.py)
  now factors joint zeroing into `_zero_treadmill_joint_state()`
- the ball arena now exposes
  `stabilize_after_physics_step()` and uses the same zeroing path there
- [flygym_runtime.py](/G:/flysim/src/body/flygym_runtime.py) now calls that
  post-physics stabilizer on every substep when present
- added regression coverage in
  [test_visual_speed_control.py](/G:/flysim/tests/test_visual_speed_control.py)
- focused slice passed:
  - `6 passed, 25 deselected`

What failed:
- no fresh parity artifact yet, because the already-launched reruns predate
  this exact patch and the next admissible rerun still needs to start

Evidence:
- [visual_speed_control.py](/G:/flysim/src/body/visual_speed_control.py)
- [flygym_runtime.py](/G:/flysim/src/body/flygym_runtime.py)
- [test_visual_speed_control.py](/G:/flysim/tests/test_visual_speed_control.py)

Next actions:
- relaunch the shortest parity Creamer rerun on this exact code state
- inspect the first admissible stationary samples and compare them against the
  old `-54.9 mm/s` first-cycle and `~419.7 mm/s` early-baseline failures

## 2026-04-03 18:46 - Added explicit treadmill settle-validity metadata and a real latest-runtime smoke

What I attempted:
- tighten the treadmill settle boundary and add direct regression coverage
  against the exact failure mode the old Creamer artifact showed
- specifically, protect against treadmill spawn explosions reappearing in the
  real FlyGym runtime even if the fake-physics unit seam still passes

What succeeded:
- [visual_speed_control.py](/G:/flysim/src/body/visual_speed_control.py)
  now treats the settle window as `<=` the settle cutoff, not `<`, so the
  release sample is still frozen
- treadmill metadata now records:
  - `measurement_valid`
  - `in_settle_window`
  - `settle_remaining_s`
- added a real-runtime smoke in
  [test_closed_loop_smoke.py](/G:/flysim/tests/test_closed_loop_smoke.py)
  that resets the latest treadmill runtime, applies zero multidrive commands,
  and asserts:
  - no measured treadmill speed during settle
  - no filtered treadmill speed during settle
  - no virtual track drift during settle
- focused validation passed:
  - `23 passed, 1 skipped, 93 deselected`

What failed:
- the fresh end-to-end parity-short rerun still had not written files by the
  time this entry was recorded, so this entry is code-level and smoke-level
  evidence, not yet the final paired Creamer result

Evidence:
- [visual_speed_control.py](/G:/flysim/src/body/visual_speed_control.py)
- [test_visual_speed_control.py](/G:/flysim/tests/test_visual_speed_control.py)
- [test_closed_loop_smoke.py](/G:/flysim/tests/test_closed_loop_smoke.py)
- [creamer2018_parity_short_synced_0p05_treadmillfix_v4](/G:/flysim/outputs/creamer2018_parity_short_synced_0p05_treadmillfix_v4)

Next actions:
- watch the fresh `v4` parity-short rerun for its first `run.jsonl`
- compare the first post-settle samples against the old broken warmup values
- only then treat the treadmill fix as end-to-end confirmed

## 2026-04-03 22:10 - Reviewed the full parity treadmill setup after the real 1.2 s Creamer run stayed flat

What I attempted:
- review the entire parity treadmill path after the user correctly pointed out
  that the legs visibly move in the baseline video even though the scored
  treadmill speed stayed at zero
- separate a dead-brain / dead-decoder failure from a downstream body/treadmill
  mechanics failure
- compare the current parity run against older treadmill artifacts and the
  direct treadmill-response tooling already in the repo

What succeeded:
- confirmed from the real parity baseline log at
  [run.jsonl](/G:/flysim/outputs/creamer2018_parity_open_loop_1p2_treadmillfix_v1/baseline/flygym-demo-20260403-204123/run.jsonl)
  that the decoder is producing strong nonzero commands after settle:
  - pre-window means: `left_amp 0.9323`, `right_amp 0.6715`,
    `left_drive 1.0241`, `right_drive 0.5190`,
    `forward_signal 0.6074`, `turn_signal -0.4518`
  - valid-row maxima reach roughly:
    `left_amp 1.2074`, `right_amp 1.1749`,
    `left_freq_scale 1.5048`, `right_freq_scale 1.4487`,
    `forward_signal 1.0`, `|turn_signal| 1.0`
- confirmed the monitored brain slice is active, not silent:
  - pre-window monitored-rate mean about `21.74 Hz`
  - stimulus-window monitored-rate mean about `17.52 Hz`
- confirmed the treadmill/body seam is where the current failure lives:
  - for all `500` valid rows, nested treadmill metadata stays at
    `fly_forward_speed_mm_s_measured = 0.0`
  - `track_x_mm = 0.0`
  - `treadmill_forward_speed_mm_s = 0.0`
  - body XY motion is tiny but nonzero, and yaw-rate is nonzero
- confirmed the current logger shape was part of the confusion:
  - treadmill state is nested under `body_metadata.visual_speed_state`
    in [closed_loop.py](/G:/flysim/src/runtime/closed_loop.py)
  - top-level `contact_force` is not logged there, so my earlier
    top-level `None` interpretation was not valid evidence of missing contact
- identified a stale diagnostic seam:
  - [run_treadmill_hybrid_response_map.py](/G:/flysim/scripts/run_treadmill_hybrid_response_map.py)
    still records `obs.forward_speed`
  - but treadmill mode now intentionally writes
    `BodyObservation.forward_speed = 0.0` in
    [flygym_runtime.py](/G:/flysim/src/body/flygym_runtime.py)
    to keep ball motion out of proprioceptive body feedback
  - so that script can no longer validate current treadmill motion unless it
    is updated to read nested treadmill metadata instead
- compared historical treadmill artifacts and found the spawn height itself is
  not the leading new regression:
  - current parity tripod run sits around `position_z = 1.5814`
  - older treadmill tripod artifacts that did show nonzero ball speed used the
    same `position_z` scale

What failed:
- the current real parity Creamer assay still produced no locomotor ball-speed
  response, despite clear motor output
- there is still no regression that proves the treadmill resumes nonzero ball
  motion after the settle window; the current tests only prove suppression
  during settle and a bounded release sample

Evidence:
- [run.jsonl](/G:/flysim/outputs/creamer2018_parity_open_loop_1p2_treadmillfix_v1/baseline/flygym-demo-20260403-204123/run.jsonl)
- [summary.json](/G:/flysim/outputs/creamer2018_parity_open_loop_1p2_treadmillfix_v1/baseline/flygym-demo-20260403-204123/summary.json)
- [visual_speed_control.py](/G:/flysim/src/body/visual_speed_control.py)
- [flygym_runtime.py](/G:/flysim/src/body/flygym_runtime.py)
- [run_treadmill_hybrid_response_map.py](/G:/flysim/scripts/run_treadmill_hybrid_response_map.py)
- [treadmill_hybrid_response_map.csv](/G:/flysim/outputs/metrics/treadmill_hybrid_response_map.csv)
- [test_closed_loop_smoke.py](/G:/flysim/tests/test_closed_loop_smoke.py)
- [test_visual_speed_control.py](/G:/flysim/tests/test_visual_speed_control.py)

Next actions:
- add raw treadmill-joint and contact debug logging to the parity treadmill path
- update the direct treadmill-response script to read nested treadmill metadata
  instead of `obs.forward_speed`
- add a post-settle positive-response regression using a direct hybrid command,
  so the treadmill must prove nonzero measured ball motion after settle before
  any future Creamer run is accepted

## 2026-04-03 22:18 - Locked down the "ball gets reset every frame" suspicion with direct unit regressions

What I attempted:
- verify the specific user suspicion that the treadmill bug might simply be
  caused by zeroing the treadmill ball every frame rather than only during the
  settle window

What succeeded:
- added two explicit post-settle regressions in
  [test_visual_speed_control.py](/G:/flysim/tests/test_visual_speed_control.py)
  that prove:
  - `VisualSpeedBallTreadmillArena.step()` does not zero the treadmill joint
    once `curr_time > _settle_until_s`
  - `stabilize_after_physics_step()` also does not zero the treadmill joint
    after settle
- the focused settle/post-settle slice passed:
  - `4 passed`

What failed:
- this does not fix the pinned-zero treadmill regression itself
- it only rules out one concrete cause: unconditional per-frame treadmill reset

Evidence:
- [visual_speed_control.py](/G:/flysim/src/body/visual_speed_control.py)
- [test_visual_speed_control.py](/G:/flysim/tests/test_visual_speed_control.py)

Next actions:
- instrument raw treadmill-joint and contact state in the live parity run path
- add a positive-response regression that requires nonzero post-settle ball
  motion under a direct hybrid command

## 2026-04-03 22:44 - Split the Creamer assay into the right primary and secondary readouts

What I attempted:
- resolve the disagreement about whether a broken treadmill should block Creamer
  interpretation on the current parity stack
- directly inspect the current controller boundary and the live treadmill
  mechanics seam

What succeeded:
- verified from direct probes that the parity and legacy treadmill paths both
  show the same downstream mechanics failure:
  - leg joints move strongly after settle
  - `treadmill_joint.qvel` remains `[0, 0, 0]`
  - a direct post-settle contact probe reports `ncon = 0`
- that means the current treadmill failure is downstream of the brain and
  decoder, and more specifically consistent with the fly effectively stepping
  in air on the current tethered-ball setup
- corrected the Creamer assay framing:
  - on this stack, the brain drives a canned hybrid locomotor controller via
    final latents, not raw per-joint actuation
  - therefore the primary Creamer readout should be visual modulation of those
    final locomotor outputs:
    - `forward_signal`
    - `turn_signal`
    - `left/right_amp`
    - `left/right_freq_scale`
    - correction gains
    - `reverse_gate`
  - treadmill ball motion remains important, but as a secondary embodied
    mechanics check rather than the primary assay target
- updated the metric layer accordingly:
  - [visual_speed_control_metrics.py](/G:/flysim/src/analysis/visual_speed_control_metrics.py)
    now emits:
    - `primary_readout = command_forward_proxy`
    - `pre/stim/post_mean_command_forward_signal`
    - `pre/stim/post_mean_command_gait_drive`
    - `pre/stim/post_mean_command_forward_proxy`
    - command-side fold changes and deltas
  - [creamer_parity_open_loop.py](/G:/flysim/src/analysis/creamer_parity_open_loop.py)
    and [run_creamer2018_parity_open_loop.py](/G:/flysim/scripts/run_creamer2018_parity_open_loop.py)
    now promote those command-side metrics in the pair summary
- added regression coverage and passed the focused slice:
  - `6 passed`

What failed:
- the treadmill mechanics seam is still broken
- the open-loop Creamer pair has not yet been rerun on the updated scorer in
  this log entry

Evidence:
- [visual_speed_control_metrics.py](/G:/flysim/src/analysis/visual_speed_control_metrics.py)
- [creamer_parity_open_loop.py](/G:/flysim/src/analysis/creamer_parity_open_loop.py)
- [run_creamer2018_parity_open_loop.py](/G:/flysim/scripts/run_creamer2018_parity_open_loop.py)
- [test_visual_speed_control_metrics.py](/G:/flysim/tests/test_visual_speed_control_metrics.py)
- [test_creamer_parity_open_loop.py](/G:/flysim/tests/test_creamer_parity_open_loop.py)

Next actions:
- rerun exactly one parity open-loop Creamer baseline / T4/T5-ablated pair on
  the updated scorer
- report command-side visual-response modulation as the primary result
- keep treadmill ball motion in the report as a separate downstream mechanics
  status field

## 2026-04-03 23:09 - Locked the Creamer sign interpretation to the paper

What I attempted:
- recheck the qualitative sign expectation for front-to-back motion against the
  Creamer paper after noticing the current baseline command-side response was
  suppressive

What succeeded:
- confirmed the paper-consistent qualitative rule:
  - front-to-back translational motion slows walking
  - back-to-front translational motion also slows walking
  - back-to-front slowing is stronger
- recorded that rule into the continuity files so future analysis does not
  incorrectly treat front-to-back suppression as a sign failure

What failed:
- nothing technical failed in this step; this was an interpretation correction

Evidence:
- [ASSUMPTIONS_AND_GAPS.md](/G:/flysim/ASSUMPTIONS_AND_GAPS.md)
- [context.md](/G:/flysim/context.md)

Next actions:
- keep evaluating the current parity open-loop pair on:
  - suppressive sign
  - magnitude
  - `T4/T5` ablation sensitivity
  - treadmill seam status as a separate downstream issue

## 2026-04-04 00:14 - Corrected parity Creamer pair completed under command-side scoring

What I attempted:
- complete the updated `2.0 s` parity open-loop Creamer baseline / `T4/T5`
  ablated pair after rewriting the scorer around decoder / locomotor-latent
  outputs rather than treadmill ball speed

What succeeded:
- the pair completed at:
  - [pair summary](/G:/flysim/outputs/creamer2018_parity_open_loop_2p0_commandmetrics_v1/metrics/creamer2018_parity_open_loop_pair_summary.json)
  - [baseline summary](/G:/flysim/outputs/creamer2018_parity_open_loop_2p0_commandmetrics_v1/baseline/flygym-demo-20260403-223301/summary.json)
  - [ablated summary](/G:/flysim/outputs/creamer2018_parity_open_loop_2p0_commandmetrics_v1/t4t5_ablated/flygym-demo-20260403-230440/summary.json)
- the corrected assay is no longer flat
- both baseline and `T4/T5` ablated runs show the Creamer-consistent sign for
  front-to-back motion: suppressive slowing on the command-side locomotor
  readout
- baseline:
  - `pre_mean_command_forward_proxy = 0.7100`
  - `stimulus_mean_command_forward_proxy = 0.0886`
  - `command_forward_proxy_fold_change = 0.1248`
  - `command_forward_proxy_delta = -0.6214`
- `T4/T5` ablated:
  - `pre_mean_command_forward_proxy = 0.6477`
  - `stimulus_mean_command_forward_proxy = 0.1176`
  - `command_forward_proxy_fold_change = 0.1816`
  - `command_forward_proxy_delta = -0.5301`
- interpretation:
  - `T4/T5` ablation weakens the suppressive front-to-back effect
  - but does not abolish it
  - so the current parity stack now shows a partial causal Creamer-like effect
    on the command side

What failed:
- the treadmill mechanics seam is still broken in both runs:
  - `pre_mean_forward_speed = 0.0`
  - `stimulus_mean_forward_speed = 0.0`
  - valid samples existed in both runs
- the pair summary still leaves `summary_path` blank for each arm even though
  the summaries exist on disk; that is a bookkeeping bug, not a scientific one

Evidence:
- [creamer2018_parity_open_loop_pair_summary.json](/G:/flysim/outputs/creamer2018_parity_open_loop_2p0_commandmetrics_v1/metrics/creamer2018_parity_open_loop_pair_summary.json)
- [baseline summary](/G:/flysim/outputs/creamer2018_parity_open_loop_2p0_commandmetrics_v1/baseline/flygym-demo-20260403-223301/summary.json)
- [ablated summary](/G:/flysim/outputs/creamer2018_parity_open_loop_2p0_commandmetrics_v1/t4t5_ablated/flygym-demo-20260403-230440/summary.json)

Next actions:
- keep the command-side Creamer pair as the current admissible parity result
- continue treating treadmill ball motion as a separate downstream mechanics bug
- investigate why the `T4/T5` ablation only weakens, rather than removes, the
  suppressive effect
