from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import numpy as np

from analysis.best_branch_investigation import align_framewise_matrix
from analysis.turn_voltage_library import apply_baseline_asymmetry_from_voltage_matrix


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply baseline asymmetry correction to a voltage-turn signal library using an activation capture.")
    parser.add_argument("--signal-library", required=True)
    parser.add_argument("--capture", required=True)
    parser.add_argument("--output-path", required=True)
    args = parser.parse_args()

    signal_library_path = Path(args.signal_library)
    capture_path = Path(args.capture)
    output_path = Path(args.output_path)

    payload = json.loads(signal_library_path.read_text(encoding="utf-8"))
    capture = np.load(capture_path, allow_pickle=True)
    corrected = apply_baseline_asymmetry_from_voltage_matrix(
        payload,
        np.asarray(capture["monitored_root_ids"], dtype=np.int64),
        align_framewise_matrix(
            np.asarray(capture["monitored_voltage_matrix"], dtype=np.float32),
            np.asarray(capture["frame_cycles"], dtype=np.int64),
        ),
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(corrected, indent=2), encoding="utf-8")
    print(str(output_path))


if __name__ == "__main__":
    main()
