from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Select a descending-only expanded readout from the body-free descending probe results."
    )
    parser.add_argument(
        "--pairs-csv",
        default="outputs/metrics/descending_readout_probe_strict_pairs.csv",
    )
    parser.add_argument(
        "--candidates-json",
        default="outputs/metrics/descending_readout_candidates_strict.json",
    )
    parser.add_argument("--window-ms", type=float, default=100.0)
    parser.add_argument("--num-forward", type=int, default=4)
    parser.add_argument("--num-turn", type=int, default=3)
    parser.add_argument(
        "--exclude-labels",
        default="DNp09,DNg97,DNa02",
        help="Comma-separated labels to exclude because they are already covered by the fixed decoder DN set.",
    )
    parser.add_argument(
        "--json-output",
        default="outputs/metrics/descending_readout_recommended.json",
    )
    args = parser.parse_args()

    pairs = pd.read_csv(args.pairs_csv)
    rows = pairs[pairs["window_ms"] == float(args.window_ms)].copy()
    excluded = {label.strip() for label in str(args.exclude_labels).split(",") if label.strip()}
    if excluded:
        rows = rows[~rows["candidate_label"].isin(excluded)].copy()

    rows["forward_balance_score"] = rows["bilateral_mean_rate_hz"] / (
        1.0
        + rows["left_dark_right_minus_left_rate_hz"].abs()
        + rows["right_dark_right_minus_left_rate_hz"].abs()
    )
    rows["turn_rate_score"] = rows["turn_flip_rate_score"] * (1.0 + 0.001 * rows["pair_score"])

    turn = (
        rows[rows["turn_flip_rate_score"] > 0.0]
        .sort_values(
            ["turn_rate_score", "bilateral_mean_rate_hz", "pair_score"],
            ascending=[False, False, False],
        )
        .head(int(args.num_turn))
    )
    turn_labels = {str(label) for label in turn["candidate_label"].tolist()}
    forward = (
        rows[~rows["candidate_label"].isin(turn_labels)]
        .sort_values(
            ["forward_balance_score", "bilateral_mean_rate_hz", "pair_score"],
            ascending=[False, False, False],
        )
        .head(int(args.num_forward))
    )

    output = {
        "selection_rule": [
            f"Use the {args.window_ms:g} ms body-free descending probe because the splice still drifts at 500 ms.",
            "Forward groups are selected by high bilateral firing with low left/right imbalance.",
            "Turn groups are selected by rate-level left/right sign flip under left-dark vs right-dark conditions.",
            "Labels already covered by the fixed decoder DN set are excluded from the supplemental population lists.",
        ],
        "pairs_csv": args.pairs_csv,
        "candidates_json": args.candidates_json,
        "window_ms": float(args.window_ms),
        "excluded_labels": sorted(excluded),
        "forward_cell_types": [str(label) for label in forward["candidate_label"].tolist()],
        "turn_cell_types": [str(label) for label in turn["candidate_label"].tolist()],
        "forward_ranking": forward[
            [
                "candidate_label",
                "forward_balance_score",
                "bilateral_mean_rate_hz",
                "left_dark_right_minus_left_rate_hz",
                "right_dark_right_minus_left_rate_hz",
                "pair_score",
            ]
        ].to_dict(orient="records"),
        "turn_ranking": turn[
            [
                "candidate_label",
                "turn_flip_rate_score",
                "bilateral_mean_rate_hz",
                "left_dark_right_minus_left_rate_hz",
                "right_dark_right_minus_left_rate_hz",
                "pair_score",
            ]
        ].to_dict(orient="records"),
    }

    output_path = Path(args.json_output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
