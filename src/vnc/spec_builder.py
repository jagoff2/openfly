from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from vnc.ingest import VNCEdge, VNCGraphSlice, VNCNode


def _norm(value: str) -> str:
    return value.strip().lower()


def _normalized_side(value: str) -> str:
    side = _norm(value)
    if side in {"l", "left"}:
        return "left"
    if side in {"r", "right"}:
        return "right"
    return "unknown"


def _is_descending(node: VNCNode) -> bool:
    return _norm(node.super_class) == "descending"


def _is_motor(node: VNCNode) -> bool:
    return _norm(node.super_class) == "motor"


def _is_premotor(node: VNCNode) -> bool:
    return "premotor" in _norm(node.cell_class) or "premotor" in _norm(node.cell_type)


@dataclass(frozen=True)
class VNCStructuralChannel:
    root_id: int
    cell_type: str
    side: str
    region: str
    left_direct_weight: int
    right_direct_weight: int
    left_premotor_path_weight: int
    right_premotor_path_weight: int
    left_total_weight: int
    right_total_weight: int
    total_motor_weight: int
    motor_target_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "root_id": self.root_id,
            "cell_type": self.cell_type,
            "side": self.side,
            "region": self.region,
            "left_direct_weight": self.left_direct_weight,
            "right_direct_weight": self.right_direct_weight,
            "left_premotor_path_weight": self.left_premotor_path_weight,
            "right_premotor_path_weight": self.right_premotor_path_weight,
            "left_total_weight": self.left_total_weight,
            "right_total_weight": self.right_total_weight,
            "total_motor_weight": self.total_motor_weight,
            "motor_target_count": self.motor_target_count,
        }


@dataclass(frozen=True)
class VNCStructuralSpec:
    node_count: int
    edge_count: int
    descending_channel_count: int
    left_motor_total_weight: int
    right_motor_total_weight: int
    channels: tuple[VNCStructuralChannel, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "descending_channel_count": self.descending_channel_count,
            "left_motor_total_weight": self.left_motor_total_weight,
            "right_motor_total_weight": self.right_motor_total_weight,
            "channels": [channel.to_dict() for channel in self.channels],
        }


def _accumulate_motor_side(weight: int, node: VNCNode, totals: dict[str, int]) -> None:
    side = _normalized_side(node.side)
    if side == "left":
        totals["left"] += int(weight)
    elif side == "right":
        totals["right"] += int(weight)


def _outgoing_edges(edges: tuple[VNCEdge, ...]) -> dict[int, list[VNCEdge]]:
    outgoing: dict[int, list[VNCEdge]] = {}
    for edge in edges:
        outgoing.setdefault(edge.pre_root_id, []).append(edge)
    return outgoing


def build_vnc_structural_spec(graph: VNCGraphSlice) -> VNCStructuralSpec:
    node_map = graph.node_map()
    outgoing = _outgoing_edges(graph.edges)
    channels: list[VNCStructuralChannel] = []

    for node in graph.nodes:
        if not _is_descending(node):
            continue

        direct_totals = {"left": 0, "right": 0}
        path_totals = {"left": 0, "right": 0}
        motor_targets: set[int] = set()

        for edge_one in outgoing.get(node.root_id, []):
            post = node_map.get(edge_one.post_root_id)
            if post is None:
                continue
            if _is_motor(post):
                _accumulate_motor_side(edge_one.weight, post, direct_totals)
                motor_targets.add(post.root_id)
                continue
            if not _is_premotor(post):
                continue
            for edge_two in outgoing.get(post.root_id, []):
                motor = node_map.get(edge_two.post_root_id)
                if motor is None or not _is_motor(motor):
                    continue
                path_weight = min(int(edge_one.weight), int(edge_two.weight))
                _accumulate_motor_side(path_weight, motor, path_totals)
                motor_targets.add(motor.root_id)

        left_total_weight = direct_totals["left"] + path_totals["left"]
        right_total_weight = direct_totals["right"] + path_totals["right"]
        total_motor_weight = left_total_weight + right_total_weight
        if total_motor_weight <= 0:
            continue

        channels.append(
            VNCStructuralChannel(
                root_id=node.root_id,
                cell_type=node.cell_type,
                side=_normalized_side(node.side),
                region=node.region,
                left_direct_weight=direct_totals["left"],
                right_direct_weight=direct_totals["right"],
                left_premotor_path_weight=path_totals["left"],
                right_premotor_path_weight=path_totals["right"],
                left_total_weight=left_total_weight,
                right_total_weight=right_total_weight,
                total_motor_weight=total_motor_weight,
                motor_target_count=len(motor_targets),
            )
        )

    channels.sort(
        key=lambda item: (
            -item.total_motor_weight,
            -item.motor_target_count,
            item.cell_type,
            item.root_id,
        )
    )
    return VNCStructuralSpec(
        node_count=len(graph.nodes),
        edge_count=len(graph.edges),
        descending_channel_count=len(channels),
        left_motor_total_weight=sum(channel.left_total_weight for channel in channels),
        right_motor_total_weight=sum(channel.right_total_weight for channel in channels),
        channels=tuple(channels),
    )
