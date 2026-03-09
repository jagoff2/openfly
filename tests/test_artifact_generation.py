from __future__ import annotations

from pathlib import Path

from runtime.closed_loop import load_config, run_closed_loop


def test_summary_json_and_video_slot_exist(tmp_path: Path) -> None:
    config = load_config("configs/mock_demo.yaml")
    summary = run_closed_loop(config, mode="mock", duration_s=0.2, output_root=tmp_path)
    run_dir = Path(summary["run_dir"])
    assert (run_dir / "summary.json").exists()
    assert summary["video_path"] is None or Path(summary["video_path"]).exists()
