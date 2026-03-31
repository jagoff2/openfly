from __future__ import annotations

from analysis.treadmill_hybrid_response import summarize_treadmill_response


def test_summarize_treadmill_response_uses_post_warmup_window() -> None:
    rows = [
        {"sim_time": 0.0, "forward_speed_mm_s": 10.0, "yaw_rate_rad_s": 1.0},
        {"sim_time": 0.25, "forward_speed_mm_s": 20.0, "yaw_rate_rad_s": -2.0},
        {"sim_time": 0.5, "forward_speed_mm_s": 30.0, "yaw_rate_rad_s": 3.0},
        {"sim_time": 0.75, "forward_speed_mm_s": 40.0, "yaw_rate_rad_s": -4.0},
    ]
    summary = summarize_treadmill_response(rows, warmup_s=0.5)
    assert summary.warmup_s == 0.5
    assert summary.measure_s == 0.25
    assert summary.mean_forward_speed_mm_s == 35.0
    assert summary.mean_abs_yaw_rate == 3.5
    assert summary.locomotor_active_fraction == 1.0
