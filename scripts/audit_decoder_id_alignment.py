from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bridge.decoder_factory import build_motor_decoder


def load_config(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_id_space(completeness_path: str | Path) -> set[int]:
    frame = pd.read_csv(completeness_path, index_col=0)
    return {int(index) for index in frame.index}


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit whether decoder requested neuron IDs exist in the configured brain backend ID space.")
    parser.add_argument("--config", action="append", required=True, help="Config path to audit. Pass multiple times for comparison.")
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--sample-limit", type=int, default=12)
    args = parser.parse_args()

    id_space_cache: dict[str, set[int]] = {}
    payload: dict[str, dict[str, object]] = {}

    for config_path in args.config:
        config = load_config(config_path)
        decoder = build_motor_decoder(config.get("decoder"))
        requested_ids = decoder.required_neuron_ids() if hasattr(decoder, "required_neuron_ids") else []
        completeness_path = str(config.get("brain", {}).get("completeness_path", ""))
        if completeness_path:
            if completeness_path not in id_space_cache:
                id_space_cache[completeness_path] = load_id_space(completeness_path)
            known_ids = id_space_cache[completeness_path]
        else:
            known_ids = set()

        matched_ids = [neuron_id for neuron_id in requested_ids if neuron_id in known_ids]
        unmatched_ids = [neuron_id for neuron_id in requested_ids if neuron_id not in known_ids]
        label = Path(config_path).stem
        payload[label] = {
            "config": str(config_path),
            "decoder_type": str(config.get("decoder", {}).get("type", "sampled_descending")),
            "requested_id_count": int(len(requested_ids)),
            "matched_id_count": int(len(matched_ids)),
            "unmatched_id_count": int(len(unmatched_ids)),
            "matched_fraction": float(len(matched_ids) / len(requested_ids)) if requested_ids else 1.0,
            "matched_id_samples": matched_ids[: int(args.sample_limit)],
            "unmatched_id_samples": unmatched_ids[: int(args.sample_limit)],
            "completeness_path": completeness_path,
        }

    output_path = Path(args.output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
