from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from vnc.annotation_atlas import build_vnc_annotation_atlas
from vnc.data_sources import get_vnc_dataset_source_map, get_vnc_dataset_sources


def test_vnc_dataset_source_registry_contains_expected_public_sources() -> None:
    source_map = get_vnc_dataset_source_map()

    assert {"manc", "fanc", "banc"} <= set(source_map)
    assert source_map["manc"].access == "public"
    assert "janelia" in source_map["manc"].primary_url
    assert "body-annotations-male-cns-v0.9-minconf-0.5.feather" in source_map["manc"].recommended_first_exports
    assert "fancr" in source_map["fanc"].data_access_url
    assert "bancr" in source_map["banc"].primary_url
    assert "Supplementary Data 4 (AN/DN clusters)" in source_map["banc"].recommended_first_exports
    assert len(get_vnc_dataset_sources()) >= 3


def test_build_vnc_annotation_atlas_summarizes_counts_and_paired_types(tmp_path: Path) -> None:
    csv_path = tmp_path / "annotations.csv"
    csv_path.write_text(
        "\n".join(
            [
                "region,flow,super_class,cell_class,cell_type,side",
                "ventral_nerve_cord,efferent,descending,motor,DNx01,L",
                "ventral_nerve_cord,efferent,descending,motor,DNx01,R",
                "ventral_nerve_cord,intrinsic,motor,premotor,PMN01,L",
                "ventral_nerve_cord,intrinsic,motor,premotor,PMN01,R",
                "brain,afferent,sensory,visual,LC4,L",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    atlas = build_vnc_annotation_atlas(csv_path)

    assert atlas.row_count == 5
    assert atlas.top_region_counts[0] == {"label": "ventral_nerve_cord", "count": 4}
    assert atlas.top_flow_counts[0]["label"] == "efferent"
    assert any(item["cell_type"] == "DNx01" for item in atlas.paired_cell_types)
    assert any(item["cell_type"] == "PMN01" for item in atlas.paired_cell_types)


def test_build_vnc_annotation_atlas_reads_json_payload(tmp_path: Path) -> None:
    json_path = tmp_path / "annotations.json"
    json_path.write_text(
        json.dumps(
            [
                {"region": "ventral_nerve_cord", "flow": "efferent", "super_class": "descending", "cell_class": "motor", "cell_type": "DNa02", "side": "L"},
                {"region": "ventral_nerve_cord", "flow": "efferent", "super_class": "descending", "cell_class": "motor", "cell_type": "DNa02", "side": "R"},
            ]
        ),
        encoding="utf-8",
    )

    atlas = build_vnc_annotation_atlas(json_path)

    assert atlas.row_count == 2
    assert atlas.top_cell_type_counts[0]["label"] == "DNa02"
    assert atlas.paired_cell_types[0]["cell_type"] == "DNa02"


def test_build_vnc_annotation_atlas_reads_feather_payload(tmp_path: Path) -> None:
    feather_path = tmp_path / "annotations.feather"
    pd.DataFrame(
        [
            {"bodyId": 1, "superclass": "descending_neuron", "class": "motor", "type": "DNg97", "rootSide": "L", "somaSide": "L", "somaNeuromere": "T1"},
            {"bodyId": 2, "superclass": "descending_neuron", "class": "motor", "type": "DNg97", "rootSide": "R", "somaSide": "R", "somaNeuromere": "T1"},
        ]
    ).to_feather(feather_path)

    atlas = build_vnc_annotation_atlas(feather_path)

    assert atlas.row_count == 2
    assert atlas.top_super_class_counts[0]["label"] == "descending"
    assert atlas.top_flow_counts[0]["label"] == "efferent"
    assert atlas.top_region_counts[0]["label"] == "T1"
    assert atlas.top_cell_type_counts[0]["label"] == "DNg97"
    assert atlas.paired_cell_types[0]["cell_type"] == "DNg97"
