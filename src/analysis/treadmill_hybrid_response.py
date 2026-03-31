from __future__ import annotations

from dataclasses import dataclass
from statistics import mean


@dataclass(frozen=True)
class TreadmillHybridResponseSample:
    warmup_s: float
    measure_s: float
    mean_forward_speed_mm_s: float
    mean_abs_yaw_rate: float
    locomotor_active_fraction: float


def summarize_treadmill_response(
    records: list[dict[str, float]],
    *,
    warmup_s: float,
) -> TreadmillHybridResponseSample:
    measured = [row for row in records if float(row["sim_time"]) >= float(warmup_s)]
    if not measured:
        raise ValueError("No measured records available after warmup.")
    forward_speeds = [float(row["forward_speed_mm_s"]) for row in measured]
    yaw_rates = [abs(float(row["yaw_rate_rad_s"])) for row in measured]
    locomotor_fraction = sum(1.0 for value in forward_speeds if abs(value) > 1e-6) / float(len(forward_speeds))
    return TreadmillHybridResponseSample(
        warmup_s=float(warmup_s),
        measure_s=float(measured[-1]["sim_time"]) - float(warmup_s),
        mean_forward_speed_mm_s=float(mean(forward_speeds)),
        mean_abs_yaw_rate=float(mean(yaw_rates)),
        locomotor_active_fraction=float(locomotor_fraction),
    )
