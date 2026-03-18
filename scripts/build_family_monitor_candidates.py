from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def load_annotation_table(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep="\t", low_memory=False)
    keep_cols = [
        "root_id",
        "cell_type",
        "hemibrain_type",
        "side",
        "super_class",
        "flow",
        "soma_x",
        "soma_y",
        "soma_z",
        "pos_x",
        "pos_y",
        "pos_z",
    ]
    df = df[[column for column in keep_cols if column in df.columns]].copy()
    df = df.dropna(subset=["root_id", "side"])
    df["root_id"] = df["root_id"].astype("int64")
    df["side"] = df["side"].astype(str).str.lower()
    df["cell_type"] = df.get("cell_type", pd.Series(index=df.index, dtype=object)).fillna("").astype(str)
    df["hemibrain_type"] = df.get("hemibrain_type", pd.Series(index=df.index, dtype=object)).fillna("").astype(str)
    family = df["cell_type"].where(df["cell_type"].str.len() > 0, df["hemibrain_type"])
    df["family"] = family.fillna("").astype(str)
    return df


def _stats(frame: pd.DataFrame, xyz_prefix: str) -> list[float] | None:
    cols = [f"{xyz_prefix}_x", f"{xyz_prefix}_y", f"{xyz_prefix}_z"]
    if not set(cols).issubset(frame.columns):
        return None
    values = frame[cols].dropna()
    if values.empty:
        return None
    return [float(v) for v in values.mean(axis=0).tolist()]


def build_candidates(annotation_df: pd.DataFrame, families: list[str], min_roots_per_side: int) -> dict[str, object]:
    selected = []
    by_family = {str(family): group.copy() for family, group in annotation_df.groupby("family", sort=False)}
    for family in families:
        family_df = by_family.get(str(family))
        if family_df is None or family_df.empty:
            continue
        left = family_df[family_df["side"] == "left"].copy()
        right = family_df[family_df["side"] == "right"].copy()
        left_ids = sorted(int(root_id) for root_id in left["root_id"].dropna().unique().tolist())
        right_ids = sorted(int(root_id) for root_id in right["root_id"].dropna().unique().tolist())
        if len(left_ids) < int(min_roots_per_side) or len(right_ids) < int(min_roots_per_side):
            continue
        selected.append(
            {
                "candidate_label": str(family),
                "left_root_ids": left_ids,
                "right_root_ids": right_ids,
                "left_num_roots": int(len(left_ids)),
                "right_num_roots": int(len(right_ids)),
                "pair_score": float(len(left_ids) + len(right_ids)),
                "left_cell_types": sorted({value for value in left["cell_type"].tolist() if str(value).strip()}),
                "right_cell_types": sorted({value for value in right["cell_type"].tolist() if str(value).strip()}),
                "left_hemibrain_types": sorted({value for value in left["hemibrain_type"].tolist() if str(value).strip()}),
                "right_hemibrain_types": sorted({value for value in right["hemibrain_type"].tolist() if str(value).strip()}),
                "left_super_classes": sorted({value for value in left.get("super_class", pd.Series(dtype=object)).dropna().astype(str).tolist() if value}),
                "right_super_classes": sorted({value for value in right.get("super_class", pd.Series(dtype=object)).dropna().astype(str).tolist() if value}),
                "left_flows": sorted({value for value in left.get("flow", pd.Series(dtype=object)).dropna().astype(str).tolist() if value}),
                "right_flows": sorted({value for value in right.get("flow", pd.Series(dtype=object)).dropna().astype(str).tolist() if value}),
                "left_soma_xyz": _stats(left, "soma"),
                "right_soma_xyz": _stats(right, "soma"),
                "left_pos_xyz": _stats(left, "pos"),
                "right_pos_xyz": _stats(right, "pos"),
            }
        )
    return {
        "selection_rule": [
            "Candidates are bilateral family groups built directly from the FlyWire annotation supplement.",
            "Family labels use `cell_type` where available and fall back to `hemibrain_type`.",
            "These groups are for monitoring/shadow analysis first, not direct motor control promotion.",
        ],
        "selected_paired_cell_types": selected,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build bilateral monitor candidate JSON from FlyWire family labels.")
    parser.add_argument("--annotation-path", default="outputs/cache/flywire_annotation_supplement.tsv")
    parser.add_argument("--families-csv", default="outputs/metrics/iterative_decoding_cycle_monitor_expansion.csv")
    parser.add_argument("--family-column", default="family")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--min-roots-per-side", type=int, default=1)
    parser.add_argument("--base-candidates-json", default=None)
    parser.add_argument("--output-path", default="outputs/metrics/iterative_relay_monitor_candidates.json")
    args = parser.parse_args()

    annotation_df = load_annotation_table(args.annotation_path)
    families_df = pd.read_csv(args.families_csv)
    families = [str(value) for value in families_df[str(args.family_column)].tolist()[: int(args.limit)]]
    payload = build_candidates(annotation_df, families=families, min_roots_per_side=int(args.min_roots_per_side))
    if args.base_candidates_json:
        base_path = Path(args.base_candidates_json)
        if base_path.exists():
            base_payload = json.loads(base_path.read_text(encoding="utf-8"))
            seen = {
                str(item.get("candidate_label") or item.get("cell_type") or "").strip()
                for item in base_payload.get("selected_paired_cell_types", [])
            }
            merged = list(base_payload.get("selected_paired_cell_types", []))
            for item in payload.get("selected_paired_cell_types", []):
                label = str(item.get("candidate_label") or item.get("cell_type") or "").strip()
                if label in seen:
                    continue
                merged.append(item)
                seen.add(label)
            payload = {
                "selection_rule": list(base_payload.get("selection_rule", [])) + payload.get("selection_rule", []),
                "selected_paired_cell_types": merged,
            }

    output_path = Path(args.output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
