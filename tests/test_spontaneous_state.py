from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "run_spontaneous_state_probe.py"
SPONTANEOUS_CONFIG_PATH = ROOT / "configs" / "brain_spontaneous_probe.yaml"
COMPLETENESS_PATH = ROOT / "external" / "fly-brain" / "data" / "2025_Completeness_783.csv"
CONNECTIVITY_PATH = ROOT / "external" / "fly-brain" / "data" / "2025_Connectivity_783.parquet"


def _load_probe_module():
    spec = importlib.util.spec_from_file_location("run_spontaneous_state_probe", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load spontaneous-state probe module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def spontaneous_probe_result(tmp_path_factory: pytest.TempPathFactory) -> dict[str, object]:
    pytest.importorskip("torch")
    if not SCRIPT_PATH.exists():
        pytest.skip(f"Missing probe script: {SCRIPT_PATH}")
    if not COMPLETENESS_PATH.exists() or not CONNECTIVITY_PATH.exists():
        pytest.skip("Requires the public fly-brain completeness/connectivity assets.")

    probe_module = _load_probe_module()
    summary = probe_module.run_spontaneous_state_probe(
        config_path=str(SPONTANEOUS_CONFIG_PATH),
        device="cpu",
        seed=0,
        baseline_steps=200,
        perturb_steps=10,
        response_steps=20,
        recovery_steps=50,
        perturb_current=50.0,
    )

    output_dir = tmp_path_factory.mktemp("spontaneous_state_probe")
    json_path = output_dir / "summary.json"
    csv_path = output_dir / "per_neuron.csv"
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--config",
            str(SPONTANEOUS_CONFIG_PATH),
            "--device",
            "cpu",
            "--seed",
            "0",
            "--baseline-steps",
            "200",
            "--perturb-steps",
            "10",
            "--response-steps",
            "20",
            "--recovery-steps",
            "50",
            "--perturb-current",
            "50",
            "--output-json",
            str(json_path),
            "--output-csv",
            str(csv_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    cli_summary = json.loads(completed.stdout)
    assert json_path.exists()
    assert csv_path.exists()
    assert cli_summary["delta_l1_hz"] == pytest.approx(summary["delta_l1_hz"])
    return summary


def test_spontaneous_state_exhibits_activity_without_external_input(
    spontaneous_probe_result: dict[str, object],
) -> None:
    baseline = spontaneous_probe_result["baseline"]
    assert spontaneous_probe_result["spontaneous_activity_present"] is True
    assert baseline["state_background_mean_rate_hz"] > 0.0


def test_spontaneous_state_activity_stays_bounded(
    spontaneous_probe_result: dict[str, object],
) -> None:
    assert spontaneous_probe_result["activity_bounded"] is True
    assert spontaneous_probe_result["max_abs_rate_hz"] <= 1000.0
    assert spontaneous_probe_result["max_abs_voltage_mv"] <= 200.0
    assert spontaneous_probe_result["max_abs_conductance"] <= 1000.0
    recovery = spontaneous_probe_result["recovery"]
    response = spontaneous_probe_result["response"]
    assert recovery["max_rate_hz"] <= response["max_rate_hz"]


def test_small_perturbation_changes_monitored_output(
    spontaneous_probe_result: dict[str, object],
) -> None:
    assert spontaneous_probe_result["perturbation_detected"] is True
    assert spontaneous_probe_result["delta_l1_hz"] > 0.0
    assert spontaneous_probe_result["changed_units"] >= 1
