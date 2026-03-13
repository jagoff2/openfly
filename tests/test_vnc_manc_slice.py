from __future__ import annotations

from pathlib import Path

import pandas as pd

from vnc.ingest import load_vnc_edge_frame
from vnc.manc_slice import MANCThoracicSliceConfig, build_manc_thoracic_locomotor_graph_slice
from vnc.pathways import build_vnc_pathway_inventory
from vnc.spec_builder import build_vnc_structural_spec


def test_load_vnc_edge_frame_reads_manc_style_feather_and_filters() -> None:
    edge_path = Path("tests/.tmp/vnc_manc_edge_frame.feather")
    edge_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {"body_pre": 11, "body_post": 31, "weight": 10},
            {"body_pre": 11, "body_post": 32, "weight": 3},
            {"body_pre": 12, "body_post": 31, "weight": 1},
        ]
    ).to_feather(edge_path)

    frame = load_vnc_edge_frame(edge_path, pre_root_ids={11}, post_root_ids={31, 32}, min_weight=2)

    assert list(frame.columns) == ["pre_root_id", "post_root_id", "weight"]
    assert len(frame) == 2
    assert set(frame["pre_root_id"].tolist()) == {11}


def test_build_manc_thoracic_locomotor_graph_slice_promotes_structural_premotor_candidates(tmp_path: Path) -> None:
    annotation_path = tmp_path / "annotations.feather"
    edge_path = tmp_path / "edges.feather"
    pd.DataFrame(
        [
            {"bodyId": 11, "superclass": "descending_neuron", "class": "xl", "type": "DNa02", "rootSide": "L", "somaNeuromere": "GNG"},
            {"bodyId": 12, "superclass": "descending_neuron", "class": "xl", "type": "DNa01", "rootSide": "R", "somaNeuromere": "GNG"},
            {"bodyId": 21, "superclass": "vnc_intrinsic", "class": "BI", "type": "IN21", "rootSide": "L", "somaNeuromere": "T1"},
            {"bodyId": 22, "superclass": "vnc_intrinsic", "class": "BI", "type": "IN22", "rootSide": "R", "somaNeuromere": "T2"},
            {"bodyId": 31, "superclass": "vnc_motor", "class": "ad", "type": "MN1", "rootSide": "L", "somaNeuromere": "T1"},
            {"bodyId": 32, "superclass": "vnc_motor", "class": "ad", "type": "MN2", "rootSide": "R", "somaNeuromere": "T2"},
        ]
    ).to_feather(annotation_path)
    pd.DataFrame(
        [
            {"body_pre": 11, "body_post": 21, "weight": 12},
            {"body_pre": 12, "body_post": 22, "weight": 11},
            {"body_pre": 21, "body_post": 31, "weight": 30},
            {"body_pre": 21, "body_post": 32, "weight": 25},
            {"body_pre": 22, "body_post": 31, "weight": 19},
            {"body_pre": 22, "body_post": 32, "weight": 23},
            {"body_pre": 11, "body_post": 31, "weight": 5},
        ]
    ).to_feather(edge_path)

    result = build_manc_thoracic_locomotor_graph_slice(
        str(annotation_path),
        str(edge_path),
        config=MANCThoracicSliceConfig(min_premotor_total_weight=20, min_premotor_motor_targets=2),
    )

    graph = result.graph
    pathways = build_vnc_pathway_inventory(graph)
    spec = build_vnc_structural_spec(graph)

    assert result.summary["premotor_candidate_count"] == 2
    assert result.summary["descending_to_premotor_edge_count"] == 2
    assert result.summary["premotor_to_motor_edge_count"] == 4
    promoted = {node.root_id: node for node in graph.nodes}
    assert "premotor" in promoted[21].cell_class
    assert len(pathways.descending_premotor_motor_paths) == 4
    assert spec.descending_channel_count == 2


def test_build_manc_thoracic_locomotor_graph_slice_leg_subclass_mode_filters_non_leg_thoracic_motors(
    tmp_path: Path,
) -> None:
    annotation_path = tmp_path / "annotations_leg_mode.feather"
    edge_path = tmp_path / "edges_leg_mode.feather"
    pd.DataFrame(
        [
            {"bodyId": 11, "superclass": "descending_neuron", "class": "xl", "type": "DNa02", "rootSide": "L", "somaNeuromere": "GNG"},
            {"bodyId": 21, "superclass": "vnc_intrinsic", "class": "BI", "type": "IN21", "rootSide": "L", "somaNeuromere": "T1"},
            {"bodyId": 31, "superclass": "vnc_motor", "subclass": "fl", "type": "Ti extensor MN", "rootSide": "L", "somaNeuromere": "T1"},
            {"bodyId": 32, "superclass": "vnc_motor", "subclass": "wm", "type": "DLMn a, b", "rootSide": "R", "somaNeuromere": "T1"},
        ]
    ).to_feather(annotation_path)
    pd.DataFrame(
        [
            {"body_pre": 11, "body_post": 21, "weight": 12},
            {"body_pre": 21, "body_post": 31, "weight": 30},
            {"body_pre": 21, "body_post": 32, "weight": 50},
            {"body_pre": 11, "body_post": 32, "weight": 8},
        ]
    ).to_feather(edge_path)

    result = build_manc_thoracic_locomotor_graph_slice(
        str(annotation_path),
        str(edge_path),
        config=MANCThoracicSliceConfig(
            motor_target_mode="leg_subclass",
            min_premotor_total_weight=20,
            min_premotor_motor_targets=1,
        ),
    )

    graph = result.graph
    selected_root_ids = {node.root_id for node in graph.nodes}

    assert result.summary["motor_target_mode"] == "leg_subclass"
    assert result.summary["thoracic_motor_pool_count"] == 2
    assert result.summary["motor_target_count"] == 1
    assert result.summary["motor_target_class_counts"] == {"fl": 1}
    assert 31 in selected_root_ids
    assert 32 not in selected_root_ids


def test_build_manc_thoracic_locomotor_graph_slice_exit_nerve_mode_filters_to_requested_leg_nerves(
    tmp_path: Path,
) -> None:
    annotation_path = tmp_path / "annotations_exit_nerve.feather"
    edge_path = tmp_path / "edges_exit_nerve.feather"
    pd.DataFrame(
        [
            {"bodyId": 11, "superclass": "descending_neuron", "class": "xl", "type": "DNa01", "rootSide": "L", "somaNeuromere": "GNG"},
            {"bodyId": 21, "superclass": "vnc_intrinsic", "class": "BI", "type": "IN21", "rootSide": "L", "somaNeuromere": "T2"},
            {"bodyId": 31, "superclass": "vnc_motor", "subclass": "ml", "type": "Ti flexor MN", "rootSide": "L", "somaNeuromere": "T2", "exitNerve": "MesoLN"},
            {"bodyId": 32, "superclass": "vnc_motor", "subclass": "wm", "type": "DLMn a, b", "rootSide": "R", "somaNeuromere": "T2", "exitNerve": "ADMN"},
        ]
    ).to_feather(annotation_path)
    pd.DataFrame(
        [
            {"body_pre": 11, "body_post": 21, "weight": 12},
            {"body_pre": 21, "body_post": 31, "weight": 30},
            {"body_pre": 21, "body_post": 32, "weight": 40},
            {"body_pre": 11, "body_post": 32, "weight": 9},
        ]
    ).to_feather(edge_path)

    result = build_manc_thoracic_locomotor_graph_slice(
        str(annotation_path),
        str(edge_path),
        config=MANCThoracicSliceConfig(
            motor_target_mode="exit_nerve",
            motor_target_exit_nerves=("MesoLN",),
            min_premotor_total_weight=20,
            min_premotor_motor_targets=1,
        ),
    )

    selected_root_ids = {node.root_id for node in result.graph.nodes}

    assert result.summary["motor_target_mode"] == "exit_nerve"
    assert result.summary["motor_target_count"] == 1
    assert result.summary["motor_target_exit_nerve_counts"] == {"MesoLN": 1}
    assert 31 in selected_root_ids
    assert 32 not in selected_root_ids
