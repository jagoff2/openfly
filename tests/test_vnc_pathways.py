from __future__ import annotations

from pathlib import Path

import pandas as pd

from vnc.ingest import load_vnc_graph_slice
from vnc.pathways import build_vnc_pathway_inventory


def test_build_vnc_pathway_inventory_finds_descending_premotor_motor_chain(tmp_path: Path) -> None:
    annotation_path = tmp_path / "annotations.csv"
    edge_path = tmp_path / "edges.csv"
    annotation_path.write_text(
        "\n".join(
            [
                "pt_root_id,region,flow,super_class,cell_class,cell_type,side",
                "1,brain,efferent,descending,motor,DNa02,L",
                "2,ventral_nerve_cord,intrinsic,interneuron,premotor,PMN01,L",
                "3,ventral_nerve_cord,efferent,motor,motor,MN-leg-01,L",
                "4,ventral_nerve_cord,efferent,motor,motor,MN-leg-02,L",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    edge_path.write_text(
        "\n".join(
            [
                "pre_pt_root_id,post_pt_root_id,n",
                "1,2,12",
                "2,3,8",
                "1,3,2",
                "2,4,3",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    graph = load_vnc_graph_slice(annotation_path, edge_path)
    inventory = build_vnc_pathway_inventory(graph)

    assert inventory.node_count == 4
    assert inventory.edge_count == 4
    assert inventory.descending_node_count == 1
    assert inventory.premotor_node_count == 1
    assert inventory.motor_node_count == 2
    assert len(inventory.descending_to_premotor_edges) == 1
    assert len(inventory.premotor_to_motor_edges) == 2
    assert len(inventory.descending_to_motor_edges) == 1
    assert len(inventory.descending_premotor_motor_paths) == 2
    assert inventory.descending_premotor_motor_paths[0]["descending_cell_type"] == "DNa02"
    assert inventory.descending_premotor_motor_paths[0]["premotor_cell_type"] == "PMN01"


def test_load_vnc_graph_slice_reads_feather_tables(tmp_path: Path) -> None:
    annotation_path = tmp_path / "annotations.feather"
    edge_path = tmp_path / "edges.feather"
    pd.DataFrame(
        [
            {"bodyId": 1, "somaNeuromere": "GNG", "superclass": "descending_neuron", "class": "motor", "type": "DNa02", "rootSide": "L"},
            {"bodyId": 2, "somaNeuromere": "T1", "superclass": "vnc_intrinsic", "class": "premotor", "type": "PMN01", "rootSide": "L", "entryNerve": "ProLN"},
            {"bodyId": 3, "somaNeuromere": "T1", "superclass": "vnc_motor", "class": "motor", "type": "MN-leg-01", "rootSide": "L", "exitNerve": "ProLN"},
        ]
    ).to_feather(annotation_path)
    pd.DataFrame(
        [
            {"pre_pt_root_id": 1, "post_pt_root_id": 2, "n": 12},
            {"pre_pt_root_id": 2, "post_pt_root_id": 3, "n": 8},
        ]
    ).to_feather(edge_path)

    graph = load_vnc_graph_slice(annotation_path, edge_path)
    inventory = build_vnc_pathway_inventory(graph)

    assert inventory.node_count == 3
    assert inventory.edge_count == 2
    assert graph.nodes[0].super_class == "descending"
    assert graph.nodes[1].flow == "intrinsic"
    assert graph.nodes[2].super_class == "motor"
    assert graph.nodes[1].entry_nerve == "ProLN"
    assert graph.nodes[2].exit_nerve == "ProLN"
    assert len(inventory.descending_premotor_motor_paths) == 1
