from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import pandas as pd

from brain.flywire_annotations import load_flywire_annotation_table


def _normalized_side(value: str) -> str:
    side = str(value).strip().lower()
    if side in {"l", "left"}:
        return "left"
    if side in {"r", "right"}:
        return "right"
    return "unknown"


def _clean_label(value: object) -> str:
    label = str(value or "").strip()
    if not label or label.lower() == "nan":
        return ""
    return label


@dataclass(frozen=True)
class FlyWireSemanticBridgeConfig:
    source_spec_json: str
    annotation_path: str = "outputs/cache/flywire_annotation_supplement.tsv"
    brain_completeness_path: str | None = "external/fly-brain/data/2025_Completeness_783.csv"
    aggregate_weights: str = "mean"
    min_monitor_roots: int = 1

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, object] | None) -> "FlyWireSemanticBridgeConfig":
        mapping = mapping or {}
        return cls(
            source_spec_json=str(mapping.get("source_spec_json", "")),
            annotation_path=str(mapping.get("annotation_path", "outputs/cache/flywire_annotation_supplement.tsv")),
            brain_completeness_path=None if mapping.get("brain_completeness_path") in (None, "") else str(mapping.get("brain_completeness_path")),
            aggregate_weights=str(mapping.get("aggregate_weights", "mean")),
            min_monitor_roots=int(mapping.get("min_monitor_roots", 1)),
        )


def _group_flywire_monitor_ids(annotation_table: pd.DataFrame) -> tuple[dict[tuple[str, str], tuple[int, ...]], dict[tuple[str, str], tuple[int, ...]]]:
    exact_groups: dict[tuple[str, str], list[int]] = defaultdict(list)
    hemibrain_groups: dict[tuple[str, str], list[int]] = defaultdict(list)
    for row in annotation_table.itertuples(index=False):
        root_id = int(getattr(row, "root_id"))
        side = _normalized_side(getattr(row, "side"))
        cell_type = _clean_label(getattr(row, "cell_type", ""))
        hemibrain_type = _clean_label(getattr(row, "hemibrain_type", ""))
        if cell_type:
            exact_groups[(cell_type, side)].append(root_id)
        if hemibrain_type:
            hemibrain_groups[(hemibrain_type, side)].append(root_id)
    return (
        {key: tuple(sorted(set(values))) for key, values in exact_groups.items()},
        {key: tuple(sorted(set(values))) for key, values in hemibrain_groups.items()},
    )


def resolve_flywire_monitor_group(
    annotation_table: pd.DataFrame,
    *,
    cell_type: str,
    side: str,
) -> tuple[tuple[int, ...], str | None]:
    exact_groups, hemibrain_groups = _group_flywire_monitor_ids(annotation_table)
    key = (_clean_label(cell_type), _normalized_side(side))
    if not key[0] or key[1] == "unknown":
        return (), None
    exact_ids = exact_groups.get(key, ())
    if exact_ids:
        return exact_ids, "cell_type"
    hemibrain_ids = hemibrain_groups.get(key, ())
    if hemibrain_ids:
        return hemibrain_ids, "hemibrain_type"
    return (), None


def _aggregate_weight(values: Sequence[float], mode: str) -> float:
    if not values:
        return 0.0
    normalized_mode = str(mode).strip().lower()
    if normalized_mode == "sum":
        return float(sum(values))
    if normalized_mode == "max":
        return float(max(values))
    return float(sum(values) / len(values))


def build_flywire_semantic_spec(
    source_spec: Mapping[str, Any],
    annotation_table: pd.DataFrame,
    *,
    aggregate_weights: str = "mean",
    min_monitor_roots: int = 1,
    valid_monitor_ids: set[int] | None = None,
    source_spec_json: str | None = None,
    annotation_path: str | None = None,
    brain_completeness_path: str | None = None,
) -> dict[str, Any]:
    grouped_channels: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for channel in source_spec.get("channels", []):
        if not isinstance(channel, Mapping):
            continue
        key = (_clean_label(channel.get("cell_type", "")), _normalized_side(channel.get("side", "")))
        if not key[0] or key[1] == "unknown":
            continue
        grouped_channels[key].append(dict(channel))

    exact_groups, hemibrain_groups = _group_flywire_monitor_ids(annotation_table)
    bridged_channels: list[dict[str, Any]] = []
    unmatched_keys: list[dict[str, Any]] = []
    match_counts = {"cell_type": 0, "hemibrain_type": 0}
    matched_source_channel_count = 0

    for (cell_type, side), items in sorted(grouped_channels.items()):
        monitor_ids = exact_groups.get((cell_type, side), ())
        match_field = "cell_type" if monitor_ids else None
        if not monitor_ids:
            monitor_ids = hemibrain_groups.get((cell_type, side), ())
            if monitor_ids:
                match_field = "hemibrain_type"
        if valid_monitor_ids is not None:
            monitor_ids = tuple(root_id for root_id in monitor_ids if int(root_id) in valid_monitor_ids)
        if len(monitor_ids) < int(min_monitor_roots):
            unmatched_keys.append(
                {
                    "cell_type": cell_type,
                    "side": side,
                    "source_channel_count": len(items),
                    "source_root_ids": sorted(int(item.get("root_id", 0)) for item in items if int(item.get("root_id", 0)) > 0),
                }
            )
            continue

        match_counts[str(match_field)] += 1
        matched_source_channel_count += len(items)
        source_root_ids = sorted(int(item.get("root_id", 0)) for item in items if int(item.get("root_id", 0)) > 0)
        bridged_channels.append(
            {
                "root_id": int(source_root_ids[0]) if source_root_ids else 0,
                "cell_type": cell_type,
                "side": side,
                "region": str(items[0].get("region", "")),
                "left_direct_weight": _aggregate_weight([float(item.get("left_direct_weight", 0.0)) for item in items], aggregate_weights),
                "right_direct_weight": _aggregate_weight([float(item.get("right_direct_weight", 0.0)) for item in items], aggregate_weights),
                "left_premotor_path_weight": _aggregate_weight([float(item.get("left_premotor_path_weight", 0.0)) for item in items], aggregate_weights),
                "right_premotor_path_weight": _aggregate_weight([float(item.get("right_premotor_path_weight", 0.0)) for item in items], aggregate_weights),
                "left_total_weight": _aggregate_weight([float(item.get("left_total_weight", 0.0)) for item in items], aggregate_weights),
                "right_total_weight": _aggregate_weight([float(item.get("right_total_weight", 0.0)) for item in items], aggregate_weights),
                "total_motor_weight": _aggregate_weight([float(item.get("total_motor_weight", 0.0)) for item in items], aggregate_weights),
                "motor_target_count": _aggregate_weight([float(item.get("motor_target_count", 0.0)) for item in items], aggregate_weights),
                "source_channel_count": int(len(items)),
                "source_root_ids": source_root_ids,
                "monitor_ids": [int(root_id) for root_id in monitor_ids],
                "monitor_root_count": int(len(monitor_ids)),
                "monitor_match_field": match_field,
            }
        )

    bridged_channels.sort(
        key=lambda item: (
            -float(item["total_motor_weight"]),
            -int(item["source_channel_count"]),
            str(item["cell_type"]),
            str(item["side"]),
        )
    )
    required_monitor_ids = sorted(
        {
            int(root_id)
            for channel in bridged_channels
            for root_id in channel.get("monitor_ids", [])
            if int(root_id) > 0
        }
    )
    return {
        "source_spec_json": source_spec_json or "",
        "annotation_path": annotation_path or "",
        "brain_completeness_path": brain_completeness_path or "",
        "monitor_space": "flywire_semantic",
        "bridge_kind": "cell_type_side_with_hemibrain_fallback",
        "aggregate_weights": str(aggregate_weights),
        "min_monitor_roots": int(min_monitor_roots),
        "source_channel_count": int(len(source_spec.get("channels", []))),
        "source_semantic_key_count": int(len(grouped_channels)),
        "bridged_channel_count": int(len(bridged_channels)),
        "matched_source_channel_count": int(matched_source_channel_count),
        "unmatched_source_channel_count": int(len(source_spec.get("channels", [])) - matched_source_channel_count),
        "required_monitor_id_count": int(len(required_monitor_ids)),
        "match_counts": {key: int(value) for key, value in match_counts.items()},
        "channels": bridged_channels,
        "unmatched_semantic_keys": unmatched_keys,
    }


def build_flywire_semantic_spec_from_files(config: FlyWireSemanticBridgeConfig) -> dict[str, Any]:
    source_spec_path = Path(config.source_spec_json)
    source_spec = json.loads(source_spec_path.read_text(encoding="utf-8"))
    annotation_table = load_flywire_annotation_table(config.annotation_path)
    valid_monitor_ids = None
    if config.brain_completeness_path:
        completeness_frame = pd.read_csv(config.brain_completeness_path, index_col=0)
        valid_monitor_ids = {int(index) for index in completeness_frame.index}
    return build_flywire_semantic_spec(
        source_spec,
        annotation_table,
        aggregate_weights=config.aggregate_weights,
        min_monitor_roots=config.min_monitor_roots,
        valid_monitor_ids=valid_monitor_ids,
        source_spec_json=str(source_spec_path),
        annotation_path=str(config.annotation_path),
        brain_completeness_path=str(config.brain_completeness_path or ""),
    )
