from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]

import sys

sys.path.insert(0, str(REPO_ROOT / "src"))

from brain.flywire_annotations import load_flywire_annotation_table
from brain.public_ids import MOTOR_READOUT_IDS


def main() -> None:
    parser = argparse.ArgumentParser(description="Find annotated intermediate relay candidates between the visual splice boundary and motor readouts.")
    parser.add_argument("--annotation-path", default="outputs/cache/flywire_annotation_supplement.tsv")
    parser.add_argument("--brain-completeness-path", default="external/fly-brain/data/2025_Completeness_783.csv")
    parser.add_argument("--brain-connectivity-path", default="external/fly-brain/data/2025_Connectivity_783.parquet")
    parser.add_argument("--splice-summary-path", default="outputs/metrics/splice_probe_summary.json")
    parser.add_argument("--top-k-pairs", type=int, default=6)
    parser.add_argument("--min-roots-per-side", type=int, default=2)
    parser.add_argument("--roots-csv-output", default="outputs/metrics/splice_relay_candidates_roots.csv")
    parser.add_argument("--pairs-csv-output", default="outputs/metrics/splice_relay_candidates_pairs.csv")
    parser.add_argument("--json-output", default="outputs/metrics/splice_relay_candidates.json")
    args = parser.parse_args()

    annotation_table = load_flywire_annotation_table(args.annotation_path)
    completeness_df = pd.read_csv(args.brain_completeness_path, index_col=0)
    flyid_to_index = {int(flywire_id): idx for idx, flywire_id in enumerate(completeness_df.index)}
    index_to_flyid = {idx: int(flywire_id) for flywire_id, idx in flyid_to_index.items()}

    splice_summary = json.loads(Path(args.splice_summary_path).read_text(encoding="utf-8"))
    overlap_types = set(splice_summary["overlap_summary"]["complete_bilateral_cell_types"])

    source_roots = set(annotation_table.loc[annotation_table["cell_type"].isin(overlap_types), "root_id"].tolist())
    source_indices = {flyid_to_index[root_id] for root_id in source_roots if root_id in flyid_to_index}
    motor_roots = {root_id for group in MOTOR_READOUT_IDS.values() for root_id in group}
    motor_indices = {flyid_to_index[root_id] for root_id in motor_roots if root_id in flyid_to_index}

    conn = pd.read_parquet(
        args.brain_connectivity_path,
        columns=["Presynaptic_Index", "Postsynaptic_Index", "Excitatory x Connectivity"],
    )
    from_overlap = conn[conn["Presynaptic_Index"].isin(source_indices)].groupby("Postsynaptic_Index")["Excitatory x Connectivity"].sum().rename("from_overlap")
    to_motor = conn[conn["Postsynaptic_Index"].isin(motor_indices)].groupby("Presynaptic_Index")["Excitatory x Connectivity"].sum().rename("to_motor")
    relay_df = pd.concat([from_overlap, to_motor], axis=1, join="inner").dropna().reset_index().rename(columns={"index": "brain_index"})
    relay_df["root_id"] = relay_df["brain_index"].map(index_to_flyid)
    relay_df = relay_df.merge(
        annotation_table[["root_id", "cell_type", "side"]].drop_duplicates("root_id"),
        on="root_id",
        how="left",
    )
    relay_df["cell_type"] = relay_df["cell_type"].fillna("unknown")
    relay_df["side"] = relay_df["side"].fillna("unknown")
    relay_df["score"] = relay_df["from_overlap"] * relay_df["to_motor"]
    relay_df = relay_df[~relay_df["root_id"].isin(motor_roots)].copy()
    relay_df = relay_df[~relay_df["cell_type"].isin(overlap_types)].copy()

    roots_csv = Path(args.roots_csv_output)
    roots_csv.parent.mkdir(parents=True, exist_ok=True)
    relay_df.sort_values("score", ascending=False).to_csv(roots_csv, index=False)

    grouped = (
        relay_df.groupby(["cell_type", "side"], dropna=False)
        .agg(
            num_roots=("root_id", "nunique"),
            total_score=("score", "sum"),
            from_overlap=("from_overlap", "sum"),
            to_motor=("to_motor", "sum"),
            root_ids=("root_id", lambda values: sorted(int(value) for value in pd.unique(values))),
        )
        .reset_index()
    )
    grouped = grouped[grouped["side"].isin(["left", "right"])].copy()

    left_groups = grouped[grouped["side"] == "left"].rename(
        columns={
            "num_roots": "left_num_roots",
            "total_score": "left_total_score",
            "from_overlap": "left_from_overlap",
            "to_motor": "left_to_motor",
            "root_ids": "left_root_ids",
        }
    )
    right_groups = grouped[grouped["side"] == "right"].rename(
        columns={
            "num_roots": "right_num_roots",
            "total_score": "right_total_score",
            "from_overlap": "right_from_overlap",
            "to_motor": "right_to_motor",
            "root_ids": "right_root_ids",
        }
    )
    pair_df = left_groups.merge(right_groups, on="cell_type", how="inner")
    pair_df = pair_df[
        (pair_df["left_num_roots"] >= int(args.min_roots_per_side))
        & (pair_df["right_num_roots"] >= int(args.min_roots_per_side))
        & (pair_df["cell_type"] != "unknown")
    ].copy()
    pair_df["pair_score"] = pair_df["left_total_score"] + pair_df["right_total_score"]
    pair_df = pair_df.sort_values("pair_score", ascending=False)

    pairs_csv = Path(args.pairs_csv_output)
    pairs_csv.parent.mkdir(parents=True, exist_ok=True)
    pair_df.to_csv(pairs_csv, index=False)

    selected = []
    for _, row in pair_df.head(int(args.top_k_pairs)).iterrows():
        selected.append(
            {
                "cell_type": str(row["cell_type"]),
                "left_root_ids": [int(value) for value in row["left_root_ids"]],
                "right_root_ids": [int(value) for value in row["right_root_ids"]],
                "left_total_score": float(row["left_total_score"]),
                "right_total_score": float(row["right_total_score"]),
                "pair_score": float(row["pair_score"]),
                "left_num_roots": int(row["left_num_roots"]),
                "right_num_roots": int(row["right_num_roots"]),
            }
        )

    output = {
        "selection_rule": [
            "Candidates are inferred from two-hop structural overlap: summed input from the grounded visual overlap boundary and summed output to the monitored motor readout set.",
            "Overlap cell types and the motor readout neurons themselves are excluded.",
            "Only annotated bilateral cell types with enough roots on both sides are selected for the paired relay probe.",
        ],
        "selected_paired_cell_types": selected,
    }
    json_output = Path(args.json_output)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
