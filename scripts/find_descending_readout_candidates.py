from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]

import sys

sys.path.insert(0, str(REPO_ROOT / "src"))

def _is_descending(annotation_table: pd.DataFrame) -> pd.Series:
    hemibrain = annotation_table["hemibrain_type"].fillna("").astype(str)
    cell_type = annotation_table["cell_type"].fillna("").astype(str)
    super_class = annotation_table["super_class"].fillna("").astype(str)
    return (
        (super_class == "descending")
        | hemibrain.str.match(r"^(DN|VES)", na=False)
        | cell_type.str.match(r"^(DN|oDN|cL22|LTe)", na=False)
    )


def _is_strict_descending(annotation_table: pd.DataFrame) -> pd.Series:
    hemibrain = annotation_table["hemibrain_type"].fillna("").astype(str)
    cell_type = annotation_table["cell_type"].fillna("").astype(str)
    super_class = annotation_table["super_class"].fillna("").astype(str)
    flow = annotation_table["flow"].fillna("").astype(str)
    return (
        (super_class == "descending")
        & (flow == "efferent")
        & (
            hemibrain.str.match(r"^(DN|MDN|oDN)", na=False)
            | cell_type.str.match(r"^(DN|MDN|oDN)", na=False)
        )
    )


def _candidate_label(row: pd.Series) -> str:
    cell_type = str(row.get("cell_type") or "").strip()
    hemibrain_type = str(row.get("hemibrain_type") or "").strip()
    if cell_type and cell_type.lower() != "nan":
        return cell_type
    if hemibrain_type and hemibrain_type.lower() != "nan":
        return hemibrain_type
    return "unknown"


def _load_full_annotation_table(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep="\t", low_memory=False)
    df = df.dropna(subset=["root_id", "side"])
    df["root_id"] = df["root_id"].astype("int64")
    df["side"] = df["side"].astype(str).str.lower()
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Find broader descending readout candidates downstream of the visual splice relays.")
    parser.add_argument("--annotation-path", default="outputs/cache/flywire_annotation_supplement.tsv")
    parser.add_argument("--brain-completeness-path", default="external/fly-brain/data/2025_Completeness_783.csv")
    parser.add_argument("--brain-connectivity-path", default="external/fly-brain/data/2025_Connectivity_783.parquet")
    parser.add_argument("--relay-candidates-json", default="outputs/metrics/splice_relay_candidates.json")
    parser.add_argument("--top-k-pairs", type=int, default=16)
    parser.add_argument("--min-roots-per-side", type=int, default=1)
    parser.add_argument("--strict-descending-only", action="store_true")
    parser.add_argument("--roots-csv-output", default="outputs/metrics/descending_readout_candidates_roots.csv")
    parser.add_argument("--pairs-csv-output", default="outputs/metrics/descending_readout_candidates_pairs.csv")
    parser.add_argument("--json-output", default="outputs/metrics/descending_readout_candidates.json")
    args = parser.parse_args()

    annotation_table = _load_full_annotation_table(args.annotation_path)
    relay_data = json.loads(Path(args.relay_candidates_json).read_text(encoding="utf-8"))
    relay_roots = {
        int(root_id)
        for item in relay_data.get("selected_paired_cell_types", [])
        for side_key in ("left_root_ids", "right_root_ids")
        for root_id in item.get(side_key, [])
    }

    completeness_df = pd.read_csv(args.brain_completeness_path, index_col=0)
    flyid_to_index = {int(flywire_id): idx for idx, flywire_id in enumerate(completeness_df.index)}
    relay_indices = {flyid_to_index[root_id] for root_id in relay_roots if root_id in flyid_to_index}

    conn = pd.read_parquet(
        args.brain_connectivity_path,
        columns=["Presynaptic_Index", "Postsynaptic_Index", "Excitatory x Connectivity"],
    )
    from_relays = conn[conn["Presynaptic_Index"].isin(relay_indices)].groupby("Postsynaptic_Index")["Excitatory x Connectivity"].sum().rename("from_relays")

    desc_mask = _is_strict_descending(annotation_table) if args.strict_descending_only else _is_descending(annotation_table)
    desc = annotation_table[desc_mask].copy()
    desc["candidate_label"] = desc.apply(_candidate_label, axis=1)
    desc["brain_index"] = desc["root_id"].map(flyid_to_index)
    desc = desc.dropna(subset=["brain_index"]).copy()
    desc["brain_index"] = desc["brain_index"].astype(int)
    desc = desc.merge(from_relays, left_on="brain_index", right_index=True, how="left")
    desc["from_relays"] = desc["from_relays"].fillna(0.0)

    roots_csv = Path(args.roots_csv_output)
    roots_csv.parent.mkdir(parents=True, exist_ok=True)
    desc.sort_values("from_relays", ascending=False).to_csv(roots_csv, index=False)

    grouped = (
        desc.groupby(["candidate_label", "side"], dropna=False)
        .agg(
            num_roots=("root_id", "nunique"),
            total_from_relays=("from_relays", "sum"),
            mean_from_relays=("from_relays", "mean"),
            root_ids=("root_id", lambda values: sorted(int(value) for value in pd.unique(values))),
            cell_types=("cell_type", lambda values: sorted({str(value) for value in pd.unique(values) if str(value) and str(value).lower() != "nan"})),
            hemibrain_types=("hemibrain_type", lambda values: sorted({str(value) for value in pd.unique(values) if str(value) and str(value).lower() != "nan"})),
            super_classes=("super_class", lambda values: sorted({str(value) for value in pd.unique(values) if str(value)})),
            flows=("flow", lambda values: sorted({str(value) for value in pd.unique(values) if str(value)})),
            soma_x=("soma_x", "mean"),
            soma_y=("soma_y", "mean"),
            soma_z=("soma_z", "mean"),
            pos_x=("pos_x", "mean"),
            pos_y=("pos_y", "mean"),
            pos_z=("pos_z", "mean"),
        )
        .reset_index()
    )
    grouped = grouped[grouped["side"].isin(["left", "right"])].copy()

    left_groups = grouped[grouped["side"] == "left"].rename(
        columns={
            "num_roots": "left_num_roots",
            "total_from_relays": "left_total_from_relays",
            "mean_from_relays": "left_mean_from_relays",
            "root_ids": "left_root_ids",
            "cell_types": "left_cell_types",
            "hemibrain_types": "left_hemibrain_types",
            "super_classes": "left_super_classes",
            "flows": "left_flows",
            "soma_x": "left_soma_x",
            "soma_y": "left_soma_y",
            "soma_z": "left_soma_z",
            "pos_x": "left_pos_x",
            "pos_y": "left_pos_y",
            "pos_z": "left_pos_z",
        }
    )
    right_groups = grouped[grouped["side"] == "right"].rename(
        columns={
            "num_roots": "right_num_roots",
            "total_from_relays": "right_total_from_relays",
            "mean_from_relays": "right_mean_from_relays",
            "root_ids": "right_root_ids",
            "cell_types": "right_cell_types",
            "hemibrain_types": "right_hemibrain_types",
            "super_classes": "right_super_classes",
            "flows": "right_flows",
            "soma_x": "right_soma_x",
            "soma_y": "right_soma_y",
            "soma_z": "right_soma_z",
            "pos_x": "right_pos_x",
            "pos_y": "right_pos_y",
            "pos_z": "right_pos_z",
        }
    )
    pair_df = left_groups.merge(right_groups, on="candidate_label", how="inner")
    pair_df = pair_df[
        (pair_df["left_num_roots"] >= int(args.min_roots_per_side))
        & (pair_df["right_num_roots"] >= int(args.min_roots_per_side))
        & (pair_df["candidate_label"] != "unknown")
    ].copy()
    pair_df["pair_score"] = pair_df["left_total_from_relays"] + pair_df["right_total_from_relays"]
    pair_df = pair_df.sort_values("pair_score", ascending=False)

    pairs_csv = Path(args.pairs_csv_output)
    pairs_csv.parent.mkdir(parents=True, exist_ok=True)
    pair_df.to_csv(pairs_csv, index=False)

    selected = []
    for _, row in pair_df.head(int(args.top_k_pairs)).iterrows():
        selected.append(
            {
                "candidate_label": str(row["candidate_label"]),
                "left_root_ids": [int(value) for value in row["left_root_ids"]],
                "right_root_ids": [int(value) for value in row["right_root_ids"]],
                "left_num_roots": int(row["left_num_roots"]),
                "right_num_roots": int(row["right_num_roots"]),
                "left_total_from_relays": float(row["left_total_from_relays"]),
                "right_total_from_relays": float(row["right_total_from_relays"]),
                "pair_score": float(row["pair_score"]),
                "left_cell_types": list(row["left_cell_types"]),
                "right_cell_types": list(row["right_cell_types"]),
                "left_hemibrain_types": list(row["left_hemibrain_types"]),
                "right_hemibrain_types": list(row["right_hemibrain_types"]),
                "left_super_classes": list(row["left_super_classes"]),
                "right_super_classes": list(row["right_super_classes"]),
                "left_flows": list(row["left_flows"]),
                "right_flows": list(row["right_flows"]),
                "left_soma_xyz": [float(row["left_soma_x"]), float(row["left_soma_y"]), float(row["left_soma_z"])],
                "right_soma_xyz": [float(row["right_soma_x"]), float(row["right_soma_y"]), float(row["right_soma_z"])],
                "left_pos_xyz": [float(row["left_pos_x"]), float(row["left_pos_y"]), float(row["left_pos_z"])],
                "right_pos_xyz": [float(row["right_pos_x"]), float(row["right_pos_y"]), float(row["right_pos_z"])],
            }
        )

    output = {
        "selection_rule": [
            "Candidates are restricted to public descending / VES-style annotations or other annotations with descending super_class."
            if not args.strict_descending_only
            else "Candidates are restricted to strict descending annotations only: `super_class == descending`, `flow == efferent`, and DN/oDN/MDN-like labels.",
            "Candidates are ranked by summed structural input from the previously selected relay roots, not by optic-lobe activity directly.",
            "Only bilateral labels with roots on both sides are retained for the expanded descending-only readout experiment.",
        ],
        "selected_paired_cell_types": selected,
    }
    json_output = Path(args.json_output)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
