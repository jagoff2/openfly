from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import pandas as pd

from analysis.best_branch_investigation import pearson_correlation
from bridge.voltage_decoder import VoltageTurnDecoder, VoltageTurnDecoderConfig


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay a voltage-driven shadow turn decoder against an existing run log.")
    parser.add_argument("--log", required=True)
    parser.add_argument("--signal-library", required=True)
    parser.add_argument("--output-prefix", default="outputs/metrics/voltage_turn_shadow_replay")
    parser.add_argument("--turn-gain", type=float, default=0.65)
    parser.add_argument("--turn-scale-mv", type=float, default=5.0)
    parser.add_argument("--signal-smoothing-alpha", type=float, default=1.0)
    args = parser.parse_args()

    decoder = VoltageTurnDecoder(
        VoltageTurnDecoderConfig(
            signal_library_json=str(args.signal_library),
            turn_gain=float(args.turn_gain),
            turn_scale_mv=float(args.turn_scale_mv),
            signal_smoothing_alpha=float(args.signal_smoothing_alpha),
        )
    )
    records = [json.loads(line) for line in Path(args.log).read_text(encoding="utf-8").splitlines() if line.strip()]
    rows = []
    for idx, record in enumerate(records):
        shadow = decoder.decode_state(monitored_voltage=record.get("brain_monitored_voltage", {}))
        target_state = record.get("target_state", {})
        target_bearing = target_state.get("bearing_rad_body", target_state.get("bearing_body"))
        rows.append(
            {
                "cycle": idx,
                "sim_time": float(record.get("sim_time", 0.0)),
                "target_bearing_rad_body": None if target_bearing is None else float(target_bearing),
                "live_turn_signal": float(record.get("motor_signals", {}).get("turn_signal", 0.0)),
                "shadow_turn_signal": float(shadow.turn_signal),
                "shadow_left_drive": float(shadow.command.left_drive),
                "shadow_right_drive": float(shadow.command.right_drive),
            }
        )
    df = pd.DataFrame(rows)
    output_prefix = Path(args.output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    csv_path = output_prefix.with_suffix(".csv")
    json_path = output_prefix.with_suffix(".json")
    df.to_csv(csv_path, index=False)
    target_df = df[df["target_bearing_rad_body"].notna()].copy()
    summary = {
        "n_cycles": int(len(df)),
        "target_enabled": bool(not target_df.empty),
        "shadow_nonzero_turn_fraction": float((df["shadow_turn_signal"].abs() > 1e-6).mean()) if not df.empty else 0.0,
        "shadow_abs_turn_mean": float(df["shadow_turn_signal"].abs().mean()) if not df.empty else 0.0,
        "live_abs_turn_mean": float(df["live_turn_signal"].abs().mean()) if not df.empty else 0.0,
        "shadow_turn_bearing_corr": None,
        "live_turn_bearing_corr": None,
    }
    if not target_df.empty:
        summary["shadow_turn_bearing_corr"] = float(
            pearson_correlation(target_df["shadow_turn_signal"].to_numpy(), target_df["target_bearing_rad_body"].to_numpy())
        )
        summary["live_turn_bearing_corr"] = float(
            pearson_correlation(target_df["live_turn_signal"].to_numpy(), target_df["target_bearing_rad_body"].to_numpy())
        )
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({"csv": str(csv_path), "json": str(json_path), "summary": summary}, indent=2))


if __name__ == "__main__":
    main()
