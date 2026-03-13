from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from vnc.ingest import VNCEdge, VNCGraphSlice, VNCNode


def _norm(value: str) -> str:
    return value.strip().lower()


def _is_descending(node: VNCNode) -> bool:
    return _norm(node.super_class) == "descending"


def _is_motor(node: VNCNode) -> bool:
    return _norm(node.super_class) == "motor"


def _is_premotor(node: VNCNode) -> bool:
    return "premotor" in _norm(node.cell_class) or "premotor" in _norm(node.cell_type)


@dataclass(frozen=True)
class VNCPathwayInventory:
    node_count: int
    edge_count: int
    descending_node_count: int
    premotor_node_count: int
    motor_node_count: int
    descending_to_premotor_edges: tuple[dict[str, Any], ...]
    premotor_to_motor_edges: tuple[dict[str, Any], ...]
    descending_to_motor_edges: tuple[dict[str, Any], ...]
    descending_premotor_motor_paths: tuple[dict[str, Any], ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "descending_node_count": self.descending_node_count,
            "premotor_node_count": self.premotor_node_count,
            "motor_node_count": self.motor_node_count,
            "descending_to_premotor_edges": list(self.descending_to_premotor_edges),
            "premotor_to_motor_edges": list(self.premotor_to_motor_edges),
            "descending_to_motor_edges": list(self.descending_to_motor_edges),
            "descending_premotor_motor_paths": list(self.descending_premotor_motor_paths),
        }


def build_vnc_pathway_inventory(graph: VNCGraphSlice) -> VNCPathwayInventory:
    node_map = graph.node_map()
    outgoing: dict[int, list[VNCEdge]] = {}
    for edge in graph.edges:
        outgoing.setdefault(edge.pre_root_id, []).append(edge)

    d2p: list[dict[str, Any]] = []
    p2m: list[dict[str, Any]] = []
    d2m: list[dict[str, Any]] = []
    paths: list[dict[str, Any]] = []

    for edge in graph.edges:
        pre = node_map.get(edge.pre_root_id)
        post = node_map.get(edge.post_root_id)
        if pre is None or post is None:
            continue
        if _is_descending(pre) and _is_premotor(post):
            d2p.append(
                {
                    "pre_root_id": pre.root_id,
                    "pre_cell_type": pre.cell_type,
                    "post_root_id": post.root_id,
                    "post_cell_type": post.cell_type,
                    "weight": edge.weight,
                }
            )
        if _is_premotor(pre) and _is_motor(post):
            p2m.append(
                {
                    "pre_root_id": pre.root_id,
                    "pre_cell_type": pre.cell_type,
                    "post_root_id": post.root_id,
                    "post_cell_type": post.cell_type,
                    "weight": edge.weight,
                }
            )
        if _is_descending(pre) and _is_motor(post):
            d2m.append(
                {
                    "pre_root_id": pre.root_id,
                    "pre_cell_type": pre.cell_type,
                    "post_root_id": post.root_id,
                    "post_cell_type": post.cell_type,
                    "weight": edge.weight,
                }
            )

    for node in graph.nodes:
        if not _is_descending(node):
            continue
        for edge_one in outgoing.get(node.root_id, []):
            mid = node_map.get(edge_one.post_root_id)
            if mid is None or not _is_premotor(mid):
                continue
            for edge_two in outgoing.get(mid.root_id, []):
                end = node_map.get(edge_two.post_root_id)
                if end is None or not _is_motor(end):
                    continue
                paths.append(
                    {
                        "descending_root_id": node.root_id,
                        "descending_cell_type": node.cell_type,
                        "premotor_root_id": mid.root_id,
                        "premotor_cell_type": mid.cell_type,
                        "motor_root_id": end.root_id,
                        "motor_cell_type": end.cell_type,
                        "first_edge_weight": edge_one.weight,
                        "second_edge_weight": edge_two.weight,
                        "path_weight_min": min(edge_one.weight, edge_two.weight),
                    }
                )

    paths.sort(key=lambda item: (-int(item["path_weight_min"]), item["descending_cell_type"], item["motor_cell_type"]))
    return VNCPathwayInventory(
        node_count=len(graph.nodes),
        edge_count=len(graph.edges),
        descending_node_count=sum(1 for node in graph.nodes if _is_descending(node)),
        premotor_node_count=sum(1 for node in graph.nodes if _is_premotor(node)),
        motor_node_count=sum(1 for node in graph.nodes if _is_motor(node)),
        descending_to_premotor_edges=tuple(d2p),
        premotor_to_motor_edges=tuple(p2m),
        descending_to_motor_edges=tuple(d2m),
        descending_premotor_motor_paths=tuple(paths),
    )
