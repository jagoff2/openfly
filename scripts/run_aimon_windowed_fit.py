from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from analysis.aimon_parity_harness import load_aimon_canonical_trial_data
from analysis.aimon_spontaneous_fit import (
    AimonReplayConfig,
    run_aimon_spontaneous_fit,
    split_aimon_trial_into_windows,
)


def _write_run_manifest(
    *,
    output_dir: Path,
    args: argparse.Namespace,
    replay_config: AimonReplayConfig,
    prepared_trial_ids: list[str],
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "fit_run_manifest.json"
    status_path = output_dir / "fit_run_status.json"
    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "script": str(Path(__file__).resolve()),
        "bundle_path": str(Path(args.bundle_path).resolve()),
        "brain_config_path": str(Path(args.brain_config_path).resolve()),
        "output_dir": str(output_dir.resolve()),
        "device": args.device,
        "seed": int(args.seed),
        "warmup_s": float(args.warmup_s),
        "max_basis_dim": int(args.max_basis_dim),
        "ridge_lambda": float(args.ridge_lambda),
        "force_forward_speed": float(args.force_forward_speed),
        "force_contact_force": float(args.force_contact_force),
        "source_trial_ids": [str(value) for value in args.trial_id],
        "prepared_trial_ids": prepared_trial_ids,
        "window_count": int(args.window_count),
        "include_window_indices": [int(value) for value in args.include_window_index],
        "fit_window_indices": [int(value) for value in args.fit_window_index],
        "test_window_indices": [int(value) for value in args.test_window_index],
        "preserve_continuity_by_source_trial": True,
        "observation_taus_s": [float(value) for value in args.observation_tau_s],
        "readout_mode": str(args.readout_mode),
        "tiny_bilateral_limit": int(args.tiny_bilateral_limit),
        "no_asymmetry_basis": bool(args.no_asymmetry_basis),
        "no_global_features": bool(args.no_global_features),
        "no_regressor_feature": bool(args.no_regressor_feature),
        "replay_config": {
            "warmup_s": float(replay_config.warmup_s),
            "max_basis_dim": int(replay_config.max_basis_dim),
            "ridge_lambda": float(replay_config.ridge_lambda),
            "readout_mode": str(replay_config.readout_mode),
            "tiny_bilateral_limit": int(replay_config.tiny_bilateral_limit),
            "observation_taus_s": [float(value) for value in replay_config.observation_taus_s],
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    status_path.write_text(
        json.dumps(
            {
                "status": "running",
                "updated_at_utc": datetime.now(timezone.utc).isoformat(),
                "manifest_path": str(manifest_path),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return manifest_path, status_path


def _write_run_status(
    *,
    status_path: Path,
    status: str,
    summary_path: Path | None = None,
    error: str | None = None,
) -> None:
    payload = {
        "status": str(status),
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    if summary_path is not None:
        payload["summary_path"] = str(summary_path)
    if error is not None:
        payload["error"] = str(error)
    status_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run identity-safe within-experiment Aimon windowed fits.")
    parser.add_argument(
        "--bundle-path",
        type=Path,
        default=Path("outputs/derived/aimon2023_canonical/aimon2023_canonical_bundle.json"),
        help="Canonical Aimon bundle JSON path.",
    )
    parser.add_argument(
        "--brain-config-path",
        type=Path,
        default=Path("configs/brain_endogenous_public_parity.yaml"),
        help="Brain config used for backend instantiation.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Output directory for summary, model, and predicted matrices.",
    )
    parser.add_argument("--trial-id", action="append", required=True, default=[], help="Canonical Aimon trial ids to split into windows.")
    parser.add_argument("--window-count", type=int, default=4, help="Number of windows per selected trial.")
    parser.add_argument("--include-window-index", action="append", type=int, default=[], help="Optional explicit subset of window indices to keep.")
    parser.add_argument("--fit-window-index", action="append", type=int, default=[], help="Window indices to use for fit; others become test if omitted.")
    parser.add_argument("--test-window-index", action="append", type=int, default=[], help="Optional explicit window indices to mark as test.")
    parser.add_argument("--device", type=str, default=None, help="Optional backend device override, e.g. cuda:0.")
    parser.add_argument("--seed", type=int, default=0, help="Random seed for backend reset.")
    parser.add_argument("--warmup-s", type=float, default=1.0, help="Warmup duration before each windowed trial.")
    parser.add_argument("--max-basis-dim", type=int, default=8, help="Reduced basis dimension for the fit.")
    parser.add_argument("--ridge-lambda", type=float, default=1e-2, help="Ridge penalty for the linear projection.")
    parser.add_argument("--force-forward-speed", type=float, default=1.0, help="Symmetric forward-speed scale used for forced_walk mechanosensory forcing.")
    parser.add_argument("--force-contact-force", type=float, default=1.0, help="Symmetric contact-force scale used for forced_walk mechanosensory forcing.")
    parser.add_argument("--observation-tau-s", action="append", default=[], type=float, help="Optional causal low-pass observation tau in seconds; repeat to append multiple imaging readout bases.")
    parser.add_argument("--readout-mode", choices=("reduced", "tiny"), default="tiny", help="Readout mode for parity fitting.")
    parser.add_argument("--tiny-bilateral-limit", type=int, default=4, help="Maximum number of bilateral family features kept in tiny mode.")
    parser.add_argument("--no-asymmetry-basis", action="store_true", help="Disable family asymmetry basis features.")
    parser.add_argument("--no-global-features", action="store_true", help="Disable global state features.")
    parser.add_argument("--no-regressor-feature", action="store_true", help="Disable the explicit public regressor covariate feature.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    replay_config = AimonReplayConfig(
        brain_config_path=args.brain_config_path,
        device=args.device,
        seed=int(args.seed),
        warmup_s=float(args.warmup_s),
        max_basis_dim=int(args.max_basis_dim),
        ridge_lambda=float(args.ridge_lambda),
        force_forward_speed=float(args.force_forward_speed),
        force_contact_force=float(args.force_contact_force),
        include_asymmetry_basis=not bool(args.no_asymmetry_basis),
        include_global_features=not bool(args.no_global_features),
        include_regressor_feature=not bool(args.no_regressor_feature),
        observation_taus_s=tuple(float(value) for value in args.observation_tau_s),
        readout_mode=str(args.readout_mode),
        tiny_bilateral_limit=int(args.tiny_bilateral_limit),
    )
    trials = load_aimon_canonical_trial_data(args.bundle_path)
    selected = {str(value) for value in args.trial_id}
    prepared_trials = []
    for trial in trials:
        if trial.trial_id not in selected:
            continue
        prepared_trials.extend(
            split_aimon_trial_into_windows(
                trial,
                window_count=int(args.window_count),
                include_window_indices=tuple(int(value) for value in args.include_window_index),
                fit_window_indices=tuple(int(value) for value in args.fit_window_index),
                test_window_indices=tuple(int(value) for value in args.test_window_index),
            )
        )
    if not prepared_trials:
        raise ValueError("No Aimon trials selected for windowed fit")
    output_dir = Path(args.output_dir)
    _, status_path = _write_run_manifest(
        output_dir=output_dir,
        args=args,
        replay_config=replay_config,
        prepared_trial_ids=[trial.trial_id for trial in prepared_trials],
    )
    try:
        summary = run_aimon_spontaneous_fit(
            bundle_path=args.bundle_path,
            replay_config=replay_config,
            output_dir=output_dir,
            fit_splits=("train",),
            trial_data_override=prepared_trials,
            preserve_continuity_by_source_trial=True,
        )
        summary_path = output_dir / "aimon_spontaneous_fit_summary.json"
        _write_run_status(status_path=status_path, status="completed", summary_path=summary_path)
        print(json.dumps(summary, indent=2))
    except Exception as exc:
        _write_run_status(status_path=status_path, status="failed", error=repr(exc))
        raise


if __name__ == "__main__":
    main()
