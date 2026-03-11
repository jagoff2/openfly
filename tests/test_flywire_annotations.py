from __future__ import annotations

from pathlib import Path

from brain.flywire_annotations import (
    build_overlap_groups,
    build_spatial_grid_overlap_groups,
    build_spatial_overlap_groups,
    find_exact_cell_type_overlap,
    FlywireSpatialTransform,
    load_flywire_annotation_table,
)


def test_load_flywire_annotation_table_normalizes_relevant_columns(tmp_path: Path) -> None:
    path = tmp_path / "annotations.tsv"
    path.write_text(
        "root_id\tcell_type\tside\tignored\n"
        "1\tT4a\tLeft\tx\n"
        "2\tT4a\tright\ty\n"
        "3\tTmY14\tLEFT\tz\n",
        encoding="utf-8",
    )
    table = load_flywire_annotation_table(path)
    assert table.columns.tolist() == ["root_id", "cell_type", "side"]
    assert table["root_id"].tolist() == [1, 2, 3]
    assert table["side"].tolist() == ["left", "right", "left"]


def test_overlap_groups_require_bilateral_support(tmp_path: Path) -> None:
    path = tmp_path / "annotations.tsv"
    path.write_text(
        "root_id\tcell_type\tside\n"
        "1\tT4a\tleft\n"
        "2\tT4a\tright\n"
        "3\tTmY14\tleft\n"
        "4\tTmY14\tleft\n",
        encoding="utf-8",
    )
    table = load_flywire_annotation_table(path)
    overlap = find_exact_cell_type_overlap(["T4a", "TmY14", "Foo"], table)
    assert overlap == ["T4a", "TmY14"]
    groups = build_overlap_groups(table, cell_types=overlap, min_roots_per_side=1)
    assert [(group.cell_type, group.side, group.root_ids) for group in groups] == [
        ("T4a", "left", (1,)),
        ("T4a", "right", (2,)),
        ("TmY14", "left", (3, 4)),
    ]


def test_spatial_overlap_groups_split_roots_by_position_bins(tmp_path: Path) -> None:
    path = tmp_path / "annotations.tsv"
    path.write_text(
        "root_id\tcell_type\tside\tpos_x\tpos_y\tpos_z\n"
        "1\tT4a\tleft\t0\t0\t0\n"
        "2\tT4a\tleft\t1\t0\t0\n"
        "3\tT4a\tleft\t2\t0\t0\n"
        "4\tT4a\tleft\t3\t0\t0\n"
        "5\tT4a\tright\t0\t0\t0\n"
        "6\tT4a\tright\t1\t0\t0\n"
        "7\tT4a\tright\t2\t0\t0\n"
        "8\tT4a\tright\t3\t0\t0\n",
        encoding="utf-8",
    )
    table = load_flywire_annotation_table(path)
    groups = build_spatial_overlap_groups(table, cell_types=["T4a"], num_bins=2, min_roots_per_bin=1)
    assert [(group.side, group.bin_index, group.root_ids) for group in groups] == [
        ("left", 0, (1, 2)),
        ("left", 1, (3, 4)),
        ("right", 0, (5, 6)),
        ("right", 1, (7, 8)),
    ]


def test_spatial_grid_overlap_groups_split_roots_by_two_axes(tmp_path: Path) -> None:
    path = tmp_path / "annotations.tsv"
    path.write_text(
        "root_id\tcell_type\tside\tpos_x\tpos_y\tpos_z\n"
        "1\tT4a\tleft\t0\t0\t0\n"
        "2\tT4a\tleft\t1\t0\t0\n"
        "3\tT4a\tleft\t0\t1\t0\n"
        "4\tT4a\tleft\t1\t1\t0\n"
        "5\tT4a\tright\t0\t0\t0\n"
        "6\tT4a\tright\t1\t0\t0\n"
        "7\tT4a\tright\t0\t1\t0\n"
        "8\tT4a\tright\t1\t1\t0\n",
        encoding="utf-8",
    )
    table = load_flywire_annotation_table(path)
    groups = build_spatial_grid_overlap_groups(
        table,
        cell_types=["T4a"],
        num_u_bins=2,
        num_v_bins=2,
        min_roots_per_bin=1,
    )
    assert len(groups) == 8
    assert sorted((group.side, group.u_bin, group.v_bin) for group in groups) == [
        ("left", 0, 0),
        ("left", 0, 1),
        ("left", 1, 0),
        ("left", 1, 1),
        ("right", 0, 0),
        ("right", 0, 1),
        ("right", 1, 0),
        ("right", 1, 1),
    ]
    left_roots = sorted(int(root_id) for group in groups if group.side == "left" for root_id in group.root_ids)
    right_roots = sorted(int(root_id) for group in groups if group.side == "right" for root_id in group.root_ids)
    assert left_roots == [1, 2, 3, 4]
    assert right_roots == [5, 6, 7, 8]
    assert all(len(group.root_ids) == 1 for group in groups)


def test_spatial_grid_overlap_groups_support_axis_swap(tmp_path: Path) -> None:
    path = tmp_path / "annotations.tsv"
    path.write_text(
        "root_id\tcell_type\tside\tpos_x\tpos_y\tpos_z\n"
        "1\tT4a\tleft\t0\t0\t0\n"
        "2\tT4a\tleft\t0\t1\t0\n"
        "3\tT4a\tleft\t3\t0\t0\n"
        "4\tT4a\tleft\t3\t1\t0\n",
        encoding="utf-8",
    )
    table = load_flywire_annotation_table(path)
    groups_default = build_spatial_grid_overlap_groups(
        table,
        cell_types=["T4a"],
        num_u_bins=2,
        num_v_bins=2,
        min_roots_per_bin=1,
    )
    groups_swapped = build_spatial_grid_overlap_groups(
        table,
        cell_types=["T4a"],
        num_u_bins=2,
        num_v_bins=2,
        swap_uv=True,
        min_roots_per_bin=1,
    )
    default_roots = sorted(int(root_id) for group in groups_default for root_id in group.root_ids)
    swapped_roots = sorted(int(root_id) for group in groups_swapped for root_id in group.root_ids)
    assert default_roots == [1, 2, 3, 4]
    assert swapped_roots == [1, 2, 3, 4]
    default_assignments = sorted((group.root_ids[0], group.u_bin, group.v_bin) for group in groups_default)
    swapped_assignments = sorted((group.root_ids[0], group.u_bin, group.v_bin) for group in groups_swapped)
    assert default_assignments != swapped_assignments


def test_spatial_grid_overlap_groups_support_side_specific_u_mirroring(tmp_path: Path) -> None:
    path = tmp_path / "annotations.tsv"
    path.write_text(
        "root_id\tcell_type\tside\tpos_x\tpos_y\tpos_z\n"
        "1\tT4a\tleft\t0\t0\t0\n"
        "2\tT4a\tleft\t2\t0\t0\n"
        "3\tT4a\tright\t0\t0\t0\n"
        "4\tT4a\tright\t2\t0\t0\n",
        encoding="utf-8",
    )
    table = load_flywire_annotation_table(path)
    groups_default = build_spatial_grid_overlap_groups(
        table,
        cell_types=["T4a"],
        num_u_bins=2,
        num_v_bins=1,
        min_roots_per_bin=1,
    )
    groups_mirrored = build_spatial_grid_overlap_groups(
        table,
        cell_types=["T4a"],
        num_u_bins=2,
        num_v_bins=1,
        mirror_u_by_side=True,
        min_roots_per_bin=1,
    )
    default_left = sorted((group.u_bin, group.root_ids) for group in groups_default if group.side == "left")
    mirrored_left = sorted((group.u_bin, group.root_ids) for group in groups_mirrored if group.side == "left")
    default_right = sorted((group.u_bin, group.root_ids) for group in groups_default if group.side == "right")
    mirrored_right = sorted((group.u_bin, group.root_ids) for group in groups_mirrored if group.side == "right")
    assert default_left == mirrored_left
    assert default_right != mirrored_right


def test_spatial_grid_overlap_groups_support_per_cell_type_transform_overrides(tmp_path: Path) -> None:
    path = tmp_path / "annotations.tsv"
    path.write_text(
        "root_id\tcell_type\tside\tpos_x\tpos_y\tpos_z\n"
        "1\tT4a\tleft\t0\t0\t0\n"
        "2\tT4a\tleft\t2\t0\t0\n"
        "3\tT4a\tright\t0\t0\t0\n"
        "4\tT4a\tright\t2\t0\t0\n"
        "5\tT5a\tleft\t0\t0\t0\n"
        "6\tT5a\tleft\t2\t0\t0\n"
        "7\tT5a\tright\t0\t0\t0\n"
        "8\tT5a\tright\t2\t0\t0\n",
        encoding="utf-8",
    )
    table = load_flywire_annotation_table(path)
    groups_default = build_spatial_grid_overlap_groups(
        table,
        cell_types=["T4a", "T5a"],
        num_u_bins=2,
        num_v_bins=1,
        min_roots_per_bin=1,
    )
    groups_overridden = build_spatial_grid_overlap_groups(
        table,
        cell_types=["T4a", "T5a"],
        num_u_bins=2,
        num_v_bins=1,
        cell_type_transforms={"T4a": FlywireSpatialTransform(mirror_u_by_side=True)},
        min_roots_per_bin=1,
    )
    default_t4a_right = sorted((group.u_bin, group.root_ids) for group in groups_default if group.cell_type == "T4a" and group.side == "right")
    override_t4a_right = sorted((group.u_bin, group.root_ids) for group in groups_overridden if group.cell_type == "T4a" and group.side == "right")
    default_t5a_right = sorted((group.u_bin, group.root_ids) for group in groups_default if group.cell_type == "T5a" and group.side == "right")
    override_t5a_right = sorted((group.u_bin, group.root_ids) for group in groups_overridden if group.cell_type == "T5a" and group.side == "right")
    assert default_t4a_right != override_t4a_right
    assert default_t5a_right == override_t5a_right
