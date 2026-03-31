from __future__ import annotations

import json
from pathlib import Path

from analysis.creamer_forward_context import (
    compare_forward_context_candidates,
    summarize_monitor_bilateral_block_means,
)
import importlib.util


def _load_builder_module():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "build_creamer_forward_context_library.py"
    spec = importlib.util.spec_from_file_location("build_creamer_forward_context_library", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_run(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def _row(block_label: str, monitor_values: dict[str, float]) -> dict:
    return {
        "body_metadata": {"visual_speed_state": {"block_label": block_label}},
        "motor_readout": {
            f"monitor_{cell_type}_bilateral_hz": float(value)
            for cell_type, value in monitor_values.items()
        },
    }


def test_forward_context_candidate_ranking_prefers_motion_over_flicker_and_ablation(tmp_path: Path) -> None:
    baseline_rows = [
        _row("baseline_a", {"A": 10.0, "B": 5.0, "C": 10.0, "D": 20.0}),
        _row("motion_ftb_a", {"A": 20.0, "B": 6.0, "C": 18.0, "D": 12.0}),
        _row("baseline_b", {"A": 10.0, "B": 5.0, "C": 10.0, "D": 20.0}),
        _row("flicker", {"A": 11.0, "B": 9.5, "C": 10.5, "D": 19.5}),
        _row("baseline_c", {"A": 10.0, "B": 5.0, "C": 10.0, "D": 20.0}),
        _row("motion_btf", {"A": 17.0, "B": 5.5, "C": 10.0, "D": 11.0}),
        _row("baseline_d", {"A": 10.0, "B": 5.0, "C": 10.0, "D": 20.0}),
        _row("motion_ftb_b", {"A": 18.0, "B": 6.0, "C": 17.0, "D": 13.0}),
    ]
    ablated_rows = [
        _row("baseline_a", {"A": 10.0, "B": 5.0, "C": 10.0, "D": 20.0}),
        _row("motion_ftb_a", {"A": 11.0, "B": 5.5, "C": 17.0, "D": 19.0}),
        _row("baseline_b", {"A": 10.0, "B": 5.0, "C": 10.0, "D": 20.0}),
        _row("flicker", {"A": 10.2, "B": 9.0, "C": 10.4, "D": 20.0}),
        _row("baseline_c", {"A": 10.0, "B": 5.0, "C": 10.0, "D": 20.0}),
        _row("motion_btf", {"A": 10.5, "B": 5.5, "C": 10.0, "D": 19.0}),
        _row("baseline_d", {"A": 10.0, "B": 5.0, "C": 10.0, "D": 20.0}),
        _row("motion_ftb_b", {"A": 10.5, "B": 5.5, "C": 16.5, "D": 19.5}),
    ]
    baseline_path = tmp_path / "baseline.jsonl"
    ablated_path = tmp_path / "ablated.jsonl"
    _write_run(baseline_path, baseline_rows)
    _write_run(ablated_path, ablated_rows)

    baseline = summarize_monitor_bilateral_block_means(baseline_path)
    ablated = summarize_monitor_bilateral_block_means(ablated_path)
    rows = compare_forward_context_candidates(baseline, ablated)

    positive = next(row for row in rows if row["cell_type"] == "A")
    assert float(positive["baseline_ftb_mean_delta_hz"]) > 0.0
    assert float(positive["baseline_btf_mean_delta_hz"]) > 0.0
    assert float(positive["ablation_component_hz"]) > 0.0
    assert float(positive["baseline_flicker_delta_hz"]) < float(positive["baseline_ftb_mean_delta_hz"])
    assert float(positive["candidate_score"]) > float(next(row for row in rows if row["cell_type"] == "B")["candidate_score"])
    negative = next(row for row in rows if row["cell_type"] == "D")
    assert float(negative["motion_component_hz"]) > 0.0
    assert float(negative["signed_motion_mean_delta_hz"]) < 0.0
    assert float(negative["signed_ablation_component_hz"]) < 0.0


def test_builder_weight_scale_override_parser_and_scaling() -> None:
    module = _load_builder_module()

    overrides = module._parse_weight_scale_overrides("VCH=0.02,T5a=0.5")

    assert overrides == {"VCH": 0.02, "T5a": 0.5}
