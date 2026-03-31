from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

from analysis.aimon_spontaneous_fit import AimonReplayConfig
from analysis.schaffer_spontaneous_fit import SchafferReplayConfig


def _load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_aimon_runner_writes_manifest_and_status(tmp_path: Path) -> None:
    module = _load_module(Path("scripts/run_aimon_spontaneous_fit.py"), "run_aimon_spontaneous_fit_test")
    output_dir = tmp_path / "aimon"
    args = argparse.Namespace(
        bundle_path=Path("outputs/derived/aimon2023_canonical/aimon2023_canonical_bundle.json"),
        brain_config_path=Path("configs/brain_endogenous_public_parity.yaml"),
        output_dir=output_dir,
        device="cpu",
        seed=0,
        warmup_s=1.0,
        max_basis_dim=8,
        ridge_lambda=1e-2,
        force_forward_speed=1.0,
        force_contact_force=1.0,
        trial_id=[],
        fit_split=[],
        observation_tau_s=[0.5],
        readout_mode="tiny",
        tiny_bilateral_limit=4,
        no_asymmetry_basis=False,
        no_global_features=False,
        no_regressor_feature=False,
    )
    replay_config = AimonReplayConfig(
        brain_config_path=args.brain_config_path,
        device=args.device,
        seed=args.seed,
        warmup_s=args.warmup_s,
        max_basis_dim=args.max_basis_dim,
        ridge_lambda=args.ridge_lambda,
        observation_taus_s=tuple(args.observation_tau_s),
        readout_mode=args.readout_mode,
        tiny_bilateral_limit=args.tiny_bilateral_limit,
    )
    manifest_path, status_path = module._write_run_manifest(
        output_dir=output_dir,
        args=args,
        replay_config=replay_config,
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    status = json.loads(status_path.read_text(encoding="utf-8"))
    assert manifest["readout_mode"] == "tiny"
    assert manifest["output_dir"] == str(output_dir.resolve())
    assert status["status"] == "running"
    module._write_run_status(status_path=status_path, status="completed", summary_path=output_dir / "aimon_spontaneous_fit_summary.json")
    completed = json.loads(status_path.read_text(encoding="utf-8"))
    assert completed["status"] == "completed"
    assert completed["summary_path"].endswith("aimon_spontaneous_fit_summary.json")


def test_schaffer_runner_writes_manifest_and_status(tmp_path: Path) -> None:
    module = _load_module(Path("scripts/run_schaffer_spontaneous_fit.py"), "run_schaffer_spontaneous_fit_test")
    output_dir = tmp_path / "schaffer"
    args = argparse.Namespace(
        bundle_path=Path("outputs/derived/schaffer2023_nwb_canonical/schaffer2023_nwb_canonical_bundle.json"),
        brain_config_path=Path("configs/brain_endogenous_public_parity.yaml"),
        output_dir=output_dir,
        device="cpu",
        seed=0,
        warmup_s=1.0,
        max_basis_dim=8,
        ridge_lambda=1e-2,
        force_forward_speed=1.0,
        force_contact_force=1.0,
        trial_id=[],
        fit_split=[],
        fit_trial_id=[],
        observation_tau_s=[0.5],
        readout_mode="tiny",
        tiny_bilateral_limit=4,
        no_asymmetry_basis=False,
        no_global_features=False,
        no_ball_motion_feature=False,
        no_behavioral_state_features=False,
        no_preserve_session_state=False,
    )
    replay_config = SchafferReplayConfig(
        brain_config_path=args.brain_config_path,
        device=args.device,
        seed=args.seed,
        warmup_s=args.warmup_s,
        max_basis_dim=args.max_basis_dim,
        ridge_lambda=args.ridge_lambda,
        observation_taus_s=tuple(args.observation_tau_s),
        readout_mode=args.readout_mode,
        tiny_bilateral_limit=args.tiny_bilateral_limit,
    )
    manifest_path, status_path = module._write_run_manifest(
        output_dir=output_dir,
        args=args,
        replay_config=replay_config,
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    status = json.loads(status_path.read_text(encoding="utf-8"))
    assert manifest["readout_mode"] == "tiny"
    assert manifest["output_dir"] == str(output_dir.resolve())
    assert status["status"] == "running"
    module._write_run_status(status_path=status_path, status="failed", error="RuntimeError('x')")
    failed = json.loads(status_path.read_text(encoding="utf-8"))
    assert failed["status"] == "failed"
    assert "RuntimeError" in failed["error"]
