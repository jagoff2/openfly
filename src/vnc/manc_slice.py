from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any

import pandas as pd

from vnc.ingest import VNCEdge, VNCGraphSlice, VNCNode, load_vnc_edge_frame, load_vnc_nodes


THORACIC_REGIONS: tuple[str, ...] = ("T1", "T2", "T3")
LEG_MOTOR_SUBCLASSES: tuple[str, ...] = ("fl", "ml", "hl")
LEG_EXIT_NERVES: tuple[str, ...] = ("ProLN", "MesoLN", "MetaLN")


def _is_known_side(node: VNCNode) -> bool:
    return node.side in {"L", "R"}


def _promote_premotor_candidate(node: VNCNode) -> VNCNode:
    if "premotor" in node.cell_class.lower():
        return node
    promoted_class = f"{node.cell_class}|premotor_candidate" if node.cell_class else "premotor_candidate"
    return VNCNode(
        root_id=node.root_id,
        region=node.region,
        entry_nerve=node.entry_nerve,
        exit_nerve=node.exit_nerve,
        flow=node.flow,
        super_class=node.super_class,
        cell_class=promoted_class,
        cell_type=node.cell_type,
        side=node.side,
    )


def _normalize_label_set(values: tuple[str, ...]) -> set[str]:
    return {value.strip().lower() for value in values if value.strip()}


def _is_thoracic_motor(node: VNCNode, thoracic_regions: set[str]) -> bool:
    return node.super_class == "motor" and node.region in thoracic_regions and _is_known_side(node)


def _select_motor_targets(
    nodes: tuple[VNCNode, ...],
    thoracic_regions: set[str],
    *,
    motor_target_mode: str,
    leg_motor_subclasses: tuple[str, ...],
    motor_target_exit_nerves: tuple[str, ...],
) -> tuple[set[int], dict[str, Any]]:
    allowed_leg_subclasses = _normalize_label_set(leg_motor_subclasses)
    allowed_exit_nerves = {value.strip() for value in motor_target_exit_nerves if value.strip()}
    if motor_target_mode not in {"all_thoracic", "leg_subclass", "exit_nerve"}:
        raise ValueError(f"Unsupported motor_target_mode: {motor_target_mode}")

    thoracic_motors = [node for node in nodes if _is_thoracic_motor(node, thoracic_regions)]
    selected_motors: list[VNCNode] = []
    for node in thoracic_motors:
        if motor_target_mode == "all_thoracic":
            selected_motors.append(node)
            continue
        if motor_target_mode == "leg_subclass" and node.cell_class.lower() in allowed_leg_subclasses:
            selected_motors.append(node)
            continue
        if motor_target_mode == "exit_nerve" and node.exit_nerve in allowed_exit_nerves:
            selected_motors.append(node)

    selection_summary = {
        "motor_target_mode": motor_target_mode,
        "thoracic_motor_pool_count": len(thoracic_motors),
        "thoracic_motor_pool_region_counts": dict(sorted(Counter(node.region for node in thoracic_motors).items())),
        "thoracic_motor_pool_class_counts": dict(sorted(Counter(node.cell_class for node in thoracic_motors).items())),
        "thoracic_motor_pool_exit_nerve_counts": dict(sorted(Counter(node.exit_nerve for node in thoracic_motors).items())),
        "motor_target_count": len(selected_motors),
        "motor_target_region_counts": dict(sorted(Counter(node.region for node in selected_motors).items())),
        "motor_target_class_counts": dict(sorted(Counter(node.cell_class for node in selected_motors).items())),
        "motor_target_exit_nerve_counts": dict(sorted(Counter(node.exit_nerve for node in selected_motors).items())),
        "leg_motor_subclasses": list(leg_motor_subclasses),
        "motor_target_exit_nerves": list(motor_target_exit_nerves),
    }
    return {node.root_id for node in selected_motors}, selection_summary


@dataclass(frozen=True)
class MANCThoracicSliceConfig:
    thoracic_regions: tuple[str, ...] = THORACIC_REGIONS
    motor_target_mode: str = "all_thoracic"
    leg_motor_subclasses: tuple[str, ...] = LEG_MOTOR_SUBCLASSES
    motor_target_exit_nerves: tuple[str, ...] = LEG_EXIT_NERVES
    min_premotor_total_weight: int = 50
    min_premotor_motor_targets: int = 2
    min_edge_weight: int = 1


@dataclass(frozen=True)
class MANCThoracicSliceResult:
    graph: VNCGraphSlice
    summary: dict[str, Any]


def build_manc_thoracic_locomotor_graph_slice(
    annotation_path: str,
    edge_path: str,
    config: MANCThoracicSliceConfig | None = None,
) -> MANCThoracicSliceResult:
    cfg = config or MANCThoracicSliceConfig()
    thoracic_regions = set(cfg.thoracic_regions)
    nodes = load_vnc_nodes(annotation_path)
    node_by_id = {node.root_id: node for node in nodes}

    descending_ids = {
        node.root_id
        for node in nodes
        if node.super_class == "descending" and _is_known_side(node) and bool(node.cell_type)
    }
    motor_ids, motor_selection_summary = _select_motor_targets(
        nodes,
        thoracic_regions,
        motor_target_mode=cfg.motor_target_mode,
        leg_motor_subclasses=cfg.leg_motor_subclasses,
        motor_target_exit_nerves=cfg.motor_target_exit_nerves,
    )

    motor_edge_frame = load_vnc_edge_frame(
        edge_path,
        post_root_ids=motor_ids,
        min_weight=cfg.min_edge_weight,
    )
    grouped = (
        motor_edge_frame.groupby("pre_root_id")
        .agg(total_weight=("weight", "sum"), motor_targets=("post_root_id", "nunique"))
        .reset_index()
    )

    premotor_candidate_ids: set[int] = set()
    premotor_totals: dict[int, tuple[int, int]] = {}
    for row in grouped.itertuples(index=False):
        root_id = int(row.pre_root_id)
        node = node_by_id.get(root_id)
        if node is None:
            continue
        if node.super_class != "interneuron" or node.flow != "intrinsic":
            continue
        if node.region not in thoracic_regions or not _is_known_side(node):
            continue
        if int(row.total_weight) < cfg.min_premotor_total_weight:
            continue
        if int(row.motor_targets) < cfg.min_premotor_motor_targets:
            continue
        premotor_candidate_ids.add(root_id)
        premotor_totals[root_id] = (int(row.total_weight), int(row.motor_targets))

    descending_to_premotor_frame = load_vnc_edge_frame(
        edge_path,
        pre_root_ids=descending_ids,
        post_root_ids=premotor_candidate_ids,
        min_weight=cfg.min_edge_weight,
    )
    descending_to_motor_frame = motor_edge_frame[motor_edge_frame["pre_root_id"].isin(descending_ids)]
    premotor_to_motor_frame = motor_edge_frame[motor_edge_frame["pre_root_id"].isin(premotor_candidate_ids)]

    combined_edge_frame = pd.concat(
        [
            descending_to_premotor_frame,
            descending_to_motor_frame,
            premotor_to_motor_frame,
        ],
        ignore_index=True,
    ).drop_duplicates()

    touched_ids = set(combined_edge_frame["pre_root_id"].tolist()) | set(combined_edge_frame["post_root_id"].tolist())
    selected_nodes: list[VNCNode] = []
    for root_id in sorted(touched_ids):
        node = node_by_id.get(int(root_id))
        if node is None:
            continue
        if root_id in premotor_candidate_ids:
            node = _promote_premotor_candidate(node)
        selected_nodes.append(node)

    selected_edges = tuple(
        VNCEdge(
            pre_root_id=int(row.pre_root_id),
            post_root_id=int(row.post_root_id),
            weight=int(row.weight),
        )
        for row in combined_edge_frame.itertuples(index=False)
    )
    graph = VNCGraphSlice(nodes=tuple(selected_nodes), edges=selected_edges)

    selected_node_map = {node.root_id: node for node in selected_nodes}
    premotor_region_counts = Counter(
        selected_node_map[root_id].region for root_id in premotor_candidate_ids if root_id in selected_node_map
    )
    summary = {
        **motor_selection_summary,
        "descending_seed_count": len(descending_ids),
        "thoracic_motor_count": len(motor_ids),
        "premotor_candidate_count": len(premotor_candidate_ids),
        "selected_node_count": len(selected_nodes),
        "selected_edge_count": len(selected_edges),
        "descending_to_premotor_edge_count": int(len(descending_to_premotor_frame)),
        "descending_to_motor_edge_count": int(len(descending_to_motor_frame)),
        "premotor_to_motor_edge_count": int(len(premotor_to_motor_frame)),
        "premotor_region_counts": dict(sorted(premotor_region_counts.items())),
        "top_premotor_candidates": [
            {
                "root_id": int(root_id),
                "cell_type": selected_node_map[root_id].cell_type if root_id in selected_node_map else "",
                "region": selected_node_map[root_id].region if root_id in selected_node_map else "",
                "cell_class": selected_node_map[root_id].cell_class if root_id in selected_node_map else "",
                "total_motor_weight": premotor_totals[root_id][0],
                "motor_target_count": premotor_totals[root_id][1],
            }
            for root_id in sorted(
                premotor_candidate_ids,
                key=lambda value: (
                    -premotor_totals[value][0],
                    -premotor_totals[value][1],
                    value,
                ),
            )[:50]
        ],
    }
    return MANCThoracicSliceResult(graph=graph, summary=summary)
