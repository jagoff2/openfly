from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from body.interfaces import BodyCommand, BodyObservation
from bridge.decoder import DecoderConfig, MotorDecoder
from runtime.closed_loop import build_body_runtime, load_config, run_closed_loop


def test_closed_loop_smoke_generates_artifacts(tmp_path: Path) -> None:
    config = load_config("configs/mock_demo.yaml")
    summary = run_closed_loop(config, mode="mock", duration_s=0.4, output_root=tmp_path)
    run_dir = Path(summary["run_dir"])
    assert run_dir.exists()
    assert Path(summary["metrics_path"]).exists()
    assert Path(summary["log_path"]).exists()
    assert (run_dir / "trajectory.png").exists()
    assert (run_dir / "commands.png").exists()


def test_closed_loop_smoke_logs_fast_vision_mode(tmp_path: Path) -> None:
    config = deepcopy(load_config("configs/mock_demo.yaml"))
    config.setdefault("runtime", {})["vision_payload_mode"] = "fast"
    summary = run_closed_loop(config, mode="mock", duration_s=0.2, output_root=tmp_path)
    log_path = Path(summary["log_path"])
    with log_path.open("r", encoding="utf-8") as handle:
        first_record = json.loads(handle.readline())

    assert first_record["vision_payload_mode"] == "fast"
    assert "vision_features" in first_record
    assert "public_input_rates" in first_record


def test_closed_loop_smoke_logs_public_p9_context_mode(tmp_path: Path) -> None:
    config = deepcopy(load_config("configs/mock_demo.yaml"))
    config.setdefault("brain_context", {})["mode"] = "public_p9_context"
    config["brain_context"]["p9_rate_hz"] = 100.0
    summary = run_closed_loop(config, mode="mock", duration_s=0.2, output_root=tmp_path)
    log_path = Path(summary["log_path"])
    with log_path.open("r", encoding="utf-8") as handle:
        records = [json.loads(line) for line in handle]

    assert records[0]["brain_context"]["mode"] == "public_p9_context"
    assert any(record["left_drive"] > 0.0 and record["right_drive"] > 0.0 for record in records)


def test_closed_loop_smoke_logs_inferred_visual_turn_context_mode(tmp_path: Path) -> None:
    config = deepcopy(load_config("configs/mock_inferred_visual_turn.yaml"))
    summary = run_closed_loop(config, mode="mock", duration_s=0.2, output_root=tmp_path)
    log_path = Path(summary["log_path"])
    with log_path.open("r", encoding="utf-8") as handle:
        records = [json.loads(line) for line in handle]

    assert records[0]["brain_context"]["mode"] == "inferred_visual_turn_context"
    assert "inferred_turn_bias" in records[0]["vision_features"]
    assert "inferred_turn_confidence" in records[0]["sensor_metadata"]


def test_closed_loop_smoke_logs_inferred_visual_p9_context_mode(tmp_path: Path) -> None:
    config = deepcopy(load_config("configs/mock_inferred_visual_p9.yaml"))
    summary = run_closed_loop(config, mode="mock", duration_s=0.2, output_root=tmp_path)
    log_path = Path(summary["log_path"])
    with log_path.open("r", encoding="utf-8") as handle:
        records = [json.loads(line) for line in handle]

    assert records[0]["brain_context"]["mode"] == "inferred_visual_p9_context"
    assert "locomotor_gate" in records[0]["brain_context"]
    assert any(record["left_drive"] > 0.0 or record["right_drive"] > 0.0 for record in records)


def test_closed_loop_smoke_supports_zero_backend(tmp_path: Path) -> None:
    config = deepcopy(load_config("configs/mock_demo.yaml"))
    config.setdefault("brain", {})["backend"] = "zero"
    summary = run_closed_loop(config, mode="mock", duration_s=0.2, output_root=tmp_path)

    assert summary["metrics"]["device"] == "zero"
    assert summary["metrics"]["stable"] == 1.0


def test_closed_loop_smoke_logs_hybrid_multidrive_fields(tmp_path: Path) -> None:
    config = deepcopy(load_config("configs/mock_multidrive.yaml"))
    summary = run_closed_loop(config, mode="mock", duration_s=0.2, output_root=tmp_path)
    log_path = Path(summary["log_path"])
    with log_path.open("r", encoding="utf-8") as handle:
        first_record = json.loads(handle.readline())

    assert "left_amp" in first_record
    assert "right_amp" in first_record
    assert "left_freq_scale" in first_record
    assert "retraction_gain" in first_record
    assert "stumbling_gain" in first_record


def test_contextual_fitted_basis_config_wires_target_conditioned_groups() -> None:
    config = load_config("configs/flygym_realistic_vision_splice_uvgrid_celltype_descending_readout_multidrive_fitted_basis_contextual.yaml")
    decoder = MotorDecoder(DecoderConfig.from_mapping(config.get("decoder")))

    assert decoder.config.forward_context_cell_types == ("DNae002", "DNpe016")
    assert decoder.config.turn_context_cell_types == ("DNpe040", "DNpe056")
    assert decoder.config.forward_context_mode == "boost"
    assert decoder.config.forward_context_boost == 0.35
    assert decoder.config.forward_context_blend == 0.0
    assert decoder.config.turn_context_mode == "aligned_asymmetry"
    assert decoder.config.turn_context_boost == 0.35
    assert decoder.config.latent_turn_priority_outer_amp_gain == 0.4
    assert decoder.config.latent_turn_priority_inner_amp_gain == 0.2
    assert decoder.config.monitor_candidates_json == "outputs/metrics/descending_readout_candidates_strict.json"
    assert "DNae002" in decoder.config.monitor_cell_types
    assert "DNb01" in decoder.config.monitor_cell_types


def test_closed_loop_smoke_logs_vnc_structural_decoder_fields(tmp_path: Path) -> None:
    config = deepcopy(load_config("configs/mock_vnc_structural_spec_exit_nerve.yaml"))
    config.setdefault("brain", {})["backend"] = "mock"
    summary = run_closed_loop(config, mode="mock", duration_s=0.1, output_root=tmp_path)
    log_path = Path(summary["log_path"])
    with log_path.open("r", encoding="utf-8") as handle:
        first_record = json.loads(handle.readline())

    assert "weighted_left_motor_drive_hz" in first_record["motor_readout"]
    assert "weighted_right_motor_drive_hz" in first_record["motor_readout"]
    assert first_record["motor_readout"]["vnc_channel_count"] > 0.0


def test_closed_loop_smoke_logs_flywire_semantic_vnc_monitor_fields(tmp_path: Path) -> None:
    config = deepcopy(load_config("configs/mock_vnc_structural_spec_exit_nerve_flywire_semantic.yaml"))
    config.setdefault("brain", {})["backend"] = "mock"
    summary = run_closed_loop(config, mode="mock", duration_s=0.1, output_root=tmp_path)
    log_path = Path(summary["log_path"])
    with log_path.open("r", encoding="utf-8") as handle:
        first_record = json.loads(handle.readline())

    assert first_record["motor_readout"]["vnc_channel_count"] > 0.0
    assert first_record["motor_readout"]["vnc_required_monitor_id_count"] > 600.0
    assert "normalized_left_motor_rate_hz" in first_record["motor_readout"]
    assert "normalized_right_motor_rate_hz" in first_record["motor_readout"]


def test_build_body_runtime_passes_camera_mode_to_flygym_runtime(tmp_path: Path, monkeypatch) -> None:
    import body.flygym_runtime as flygym_runtime_module

    captured: dict[str, object] = {}

    class FakeFlyGymRuntime:
        def __init__(self, **kwargs) -> None:
            captured.update(kwargs)

    monkeypatch.setattr(flygym_runtime_module, "FlyGymRealisticVisionRuntime", FakeFlyGymRuntime)
    config = deepcopy(load_config("configs/flygym_realistic_vision_splice_uvgrid_vnc_structural_spec_exit_nerve_flywire_semantic.yaml"))
    runtime = build_body_runtime("flygym", config, tmp_path)

    assert isinstance(runtime, FakeFlyGymRuntime)
    assert captured["camera_mode"] == "follow_yaw"


def test_closed_loop_smoke_writes_partial_metrics_on_runtime_failure(tmp_path: Path, monkeypatch) -> None:
    class FailingRuntime:
        timestep = 0.01

        def __init__(self) -> None:
            self._step_count = 0

        def reset(self, seed: int = 0) -> BodyObservation:
            return BodyObservation(
                sim_time=0.0,
                position_xy=(0.0, 0.0),
                yaw=0.0,
                forward_speed=0.0,
                yaw_rate=0.0,
                contact_force=0.0,
                realistic_vision={},
            )

        def step(self, command: BodyCommand, num_substeps: int) -> BodyObservation:
            self._step_count += 1
            if self._step_count >= 2:
                raise RuntimeError("forced failure")
            return BodyObservation(
                sim_time=0.02,
                position_xy=(0.1, 0.0),
                yaw=0.0,
                forward_speed=0.1,
                yaw_rate=0.0,
                contact_force=0.0,
                realistic_vision={},
            )

        def render_frame(self) -> Any:
            return None

        def close(self) -> None:
            return None

    monkeypatch.setattr("runtime.closed_loop.build_body_runtime", lambda mode, config, run_dir: FailingRuntime())
    config = deepcopy(load_config("configs/mock_demo.yaml"))
    summary = run_closed_loop(config, mode="mock", duration_s=0.2, output_root=tmp_path)

    with Path(summary["metrics_path"]).open("r", encoding="utf-8") as handle:
        metrics_text = handle.read()

    assert summary["metrics"]["stable"] == 0.0
    assert summary["metrics"]["failure_type"] == "RuntimeError"
    assert "forced failure" in summary["metrics"]["failure_message"]
    assert "RuntimeError" in metrics_text
