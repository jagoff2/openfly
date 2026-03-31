from __future__ import annotations

import json
from pathlib import Path

from analysis.creamer_diagnosis import compare_creamer_runs, summarize_creamer_run


def _write_run(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def _row(block_label: str, forward_speed: float, forward_signal: float, turn_voltage_signal: float, *, splice_roots: float, splice_current: float) -> dict:
    return {
        "forward_speed": forward_speed,
        "body_metadata": {
            "visual_speed_state": {
                "block_label": block_label,
                "retinal_slip_mm_s": -forward_speed,
                "effective_visual_speed_mm_s": -forward_speed,
            }
        },
        "motor_signals": {
            "forward_signal": forward_signal,
            "turn_signal": 0.0,
            "reverse_signal": 0.0,
        },
        "motor_readout": {
            "dn_forward_signal": 0.0,
            "population_forward_signal": forward_signal,
            "forward_state": forward_signal,
            "dn_turn_signal": 0.0,
            "population_turn_signal": 0.0,
            "turn_voltage_signal": turn_voltage_signal,
            "turn_state": turn_voltage_signal,
        },
        "visual_splice": {
            "nonzero_root_count": splice_roots,
            "max_abs_current": splice_current,
        },
    }


def test_compare_creamer_runs_identifies_speed_forward_decoupling(tmp_path: Path) -> None:
    baseline_path = tmp_path / "baseline.jsonl"
    ablated_path = tmp_path / "ablated.jsonl"
    _write_run(
        baseline_path,
        [
            _row("baseline_a", 100.0, 0.10, 0.30, splice_roots=1000.0, splice_current=5.0),
            _row("motion_ftb_a", 112.0, 0.18, 0.12, splice_roots=1100.0, splice_current=6.0),
        ],
    )
    _write_run(
        ablated_path,
        [
            _row("baseline_a", 100.5, 0.09, 0.45, splice_roots=0.0, splice_current=0.0),
            _row("motion_ftb_a", 112.2, 0.09, 0.45, splice_roots=0.0, splice_current=0.0),
        ],
    )

    comparison = compare_creamer_runs(summarize_creamer_run(baseline_path), summarize_creamer_run(ablated_path))

    assert comparison["diagnosis"]["speed_delta_survives_ablation_first_motion_block"] is True
    assert comparison["diagnosis"]["front_to_back_speed_delta_is_decoupled_from_forward_signal"] is True
    assert comparison["diagnosis"]["motion_pathway_primarily_modulates_turn_structure_not_speed"] is True


def test_summarize_creamer_run_averages_block_fields(tmp_path: Path) -> None:
    run_path = tmp_path / "run.jsonl"
    _write_run(
        run_path,
        [
            _row("baseline_a", 10.0, 0.1, 0.2, splice_roots=10.0, splice_current=1.0),
            _row("baseline_a", 14.0, 0.3, 0.4, splice_roots=30.0, splice_current=3.0),
        ],
    )
    summary = summarize_creamer_run(run_path)
    assert summary.block_means["baseline_a"]["forward_speed_mm_s"] == 12.0
    assert summary.block_means["baseline_a"]["forward_signal"] == 0.2
    assert summary.block_means["baseline_a"]["turn_voltage_signal"] == 0.30000000000000004
    assert summary.block_means["baseline_a"]["splice_nonzero_root_count"] == 20.0
