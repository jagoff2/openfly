from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize shadow decoder signals from a run log.")
    parser.add_argument("--log", required=True)
    parser.add_argument("--shadow-label", required=True)
    parser.add_argument("--output-prefix", default="outputs/metrics/shadow_decode_summary")
    args = parser.parse_args()

    records = [json.loads(line) for line in Path(args.log).read_text(encoding="utf-8").splitlines() if line.strip()]
    shadow = [record.get("shadow_decodes", {}).get(str(args.shadow_label), {}) for record in records]
    rows = []
    for idx, item in enumerate(shadow):
        command = item.get("command", {})
        rows.append(
            {
                "cycle": idx,
                "forward_signal": item.get("forward_signal", 0.0),
                "turn_signal": item.get("turn_signal", 0.0),
                "reverse_signal": item.get("reverse_signal", 0.0),
                "left_drive": command.get("left_drive", 0.0),
                "right_drive": command.get("right_drive", 0.0),
            }
        )
    df = pd.DataFrame(rows)
    output_prefix = Path(args.output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    csv_path = output_prefix.with_suffix(".csv")
    json_path = output_prefix.with_suffix(".json")
    df.to_csv(csv_path, index=False)
    summary = {
        "shadow_label": str(args.shadow_label),
        "n_cycles": int(len(df)),
        "forward_mean": float(df["forward_signal"].mean()) if not df.empty else 0.0,
        "turn_mean": float(df["turn_signal"].mean()) if not df.empty else 0.0,
        "abs_turn_mean": float(df["turn_signal"].abs().mean()) if not df.empty else 0.0,
        "nonzero_turn_fraction": float((df["turn_signal"].abs() > 1e-6).mean()) if not df.empty else 0.0,
    }
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
