from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vnc.manc_slice import MANCThoracicSliceConfig, build_manc_thoracic_locomotor_graph_slice
from vnc.pathways import build_vnc_pathway_inventory
from vnc.spec_builder import build_vnc_structural_spec


def main() -> None:
    parser = argparse.ArgumentParser(description="Build real-data thoracic locomotor pathway/spec artifacts from public MANC annotations and edges.")
    parser.add_argument("--annotations", default="external/vnc/manc/body-annotations-male-cns-v0.9-minconf-0.5.feather")
    parser.add_argument("--edges", default="external/vnc/manc/connectome-weights-male-cns-v0.9-minconf-0.5.feather")
    parser.add_argument("--summary-json", required=True)
    parser.add_argument("--pathways-json", required=True)
    parser.add_argument("--spec-json", required=True)
    parser.add_argument("--nodes-csv", required=True)
    parser.add_argument("--edges-csv", required=True)
    parser.add_argument("--motor-target-mode", choices=["all_thoracic", "leg_subclass", "exit_nerve"], default="all_thoracic")
    parser.add_argument("--leg-motor-subclasses", default="fl,ml,hl")
    parser.add_argument("--motor-target-exit-nerves", default="ProLN,MesoLN,MetaLN")
    parser.add_argument("--min-premotor-total-weight", type=int, default=50)
    parser.add_argument("--min-premotor-motor-targets", type=int, default=2)
    parser.add_argument("--min-edge-weight", type=int, default=1)
    args = parser.parse_args()

    config = MANCThoracicSliceConfig(
        motor_target_mode=str(args.motor_target_mode),
        leg_motor_subclasses=tuple(part.strip() for part in str(args.leg_motor_subclasses).split(",") if part.strip()),
        motor_target_exit_nerves=tuple(part.strip() for part in str(args.motor_target_exit_nerves).split(",") if part.strip()),
        min_premotor_total_weight=int(args.min_premotor_total_weight),
        min_premotor_motor_targets=int(args.min_premotor_motor_targets),
        min_edge_weight=int(args.min_edge_weight),
    )
    result = build_manc_thoracic_locomotor_graph_slice(args.annotations, args.edges, config=config)
    pathways = build_vnc_pathway_inventory(result.graph)
    spec = build_vnc_structural_spec(result.graph)

    summary_json = Path(args.summary_json)
    pathways_json = Path(args.pathways_json)
    spec_json = Path(args.spec_json)
    nodes_csv = Path(args.nodes_csv)
    edges_csv = Path(args.edges_csv)
    for path in (summary_json, pathways_json, spec_json, nodes_csv, edges_csv):
        path.parent.mkdir(parents=True, exist_ok=True)

    summary_json.write_text(json.dumps(result.summary, indent=2), encoding="utf-8")
    pathways_json.write_text(json.dumps(pathways.to_dict(), indent=2), encoding="utf-8")
    spec_json.write_text(json.dumps(spec.to_dict(), indent=2), encoding="utf-8")

    with nodes_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["root_id", "region", "entry_nerve", "exit_nerve", "flow", "super_class", "cell_class", "cell_type", "side"],
        )
        writer.writeheader()
        for node in result.graph.nodes:
            writer.writerow(
                {
                    "root_id": node.root_id,
                    "region": node.region,
                    "entry_nerve": node.entry_nerve,
                    "exit_nerve": node.exit_nerve,
                    "flow": node.flow,
                    "super_class": node.super_class,
                    "cell_class": node.cell_class,
                    "cell_type": node.cell_type,
                    "side": node.side,
                }
            )

    with edges_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["pre_root_id", "post_root_id", "weight"])
        writer.writeheader()
        for edge in result.graph.edges:
            writer.writerow(
                {
                    "pre_root_id": edge.pre_root_id,
                    "post_root_id": edge.post_root_id,
                    "weight": edge.weight,
                }
            )

    print(json.dumps({"summary_json": str(summary_json), "pathways_json": str(pathways_json), "spec_json": str(spec_json)}, indent=2))


if __name__ == "__main__":
    main()
