from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from vnc.schema import canonical_flow, canonical_side, canonical_super_class, first_present, normalize_key, normalize_text


def _read_rows(path: Path) -> list[dict[str, str]]:
    suffix = path.suffix.lower()
    if suffix in {".csv", ".tsv"}:
        delimiter = "\t" if suffix == ".tsv" else ","
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return [{normalize_key(key): normalize_text(value) for key, value in row.items()} for row in csv.DictReader(handle, delimiter=delimiter)]
    if suffix == ".feather":
        frame = pd.read_feather(path)
        return [
            {normalize_key(key): normalize_text(value) for key, value in row.items()}
            for row in frame.to_dict(orient="records")
        ]
    if suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError("Expected JSON annotation payload to be a list of row mappings.")
        rows: list[dict[str, str]] = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            rows.append({normalize_key(key): normalize_text(value) for key, value in item.items()})
        return rows
    raise ValueError(f"Unsupported annotation format for atlas builder: {path}")


def _canonical_value(
    row: dict[str, str],
    field: str,
    *,
    primary_column: str | None = None,
    super_class_column: str = "super_class",
) -> str:
    raw = first_present(row, field, primary_column)
    if field == "super_class":
        return canonical_super_class(raw)
    if field == "flow":
        super_class = _canonical_value(row, "super_class", primary_column=super_class_column)
        return canonical_flow(raw, super_class)
    if field == "side":
        return canonical_side(raw)
    return raw


def _count_by(rows: list[dict[str, str]], field: str, primary_column: str | None = None, super_class_column: str = "super_class") -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    for row in rows:
        key = _canonical_value(row, field, primary_column=primary_column, super_class_column=super_class_column) or "<missing>"
        counts[key] = counts.get(key, 0) + 1
    return [
        {"label": label, "count": count}
        for label, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]


def _paired_cell_types(rows: list[dict[str, str]], cell_type_column: str, side_column: str) -> list[dict[str, Any]]:
    side_map: dict[str, set[str]] = {}
    for row in rows:
        label = _canonical_value(row, "cell_type", primary_column=cell_type_column)
        side = _canonical_value(row, "side", primary_column=side_column)
        if not label:
            continue
        if side:
            side_map.setdefault(label, set()).add(side)
    paired = []
    for label, sides in side_map.items():
        normalized = {side.lower() for side in sides}
        if {"l", "r"} <= normalized or {"left", "right"} <= normalized:
            paired.append({"cell_type": label, "sides": sorted(sides)})
    return sorted(paired, key=lambda item: item["cell_type"])


@dataclass(frozen=True)
class VNCAnnotationAtlas:
    source_path: str
    row_count: int
    column_names: tuple[str, ...]
    top_region_counts: tuple[dict[str, Any], ...]
    top_flow_counts: tuple[dict[str, Any], ...]
    top_super_class_counts: tuple[dict[str, Any], ...]
    top_cell_class_counts: tuple[dict[str, Any], ...]
    top_cell_type_counts: tuple[dict[str, Any], ...]
    paired_cell_types: tuple[dict[str, Any], ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_path": self.source_path,
            "row_count": self.row_count,
            "column_names": list(self.column_names),
            "top_region_counts": list(self.top_region_counts),
            "top_flow_counts": list(self.top_flow_counts),
            "top_super_class_counts": list(self.top_super_class_counts),
            "top_cell_class_counts": list(self.top_cell_class_counts),
            "top_cell_type_counts": list(self.top_cell_type_counts),
            "paired_cell_types": list(self.paired_cell_types),
        }


def build_vnc_annotation_atlas(
    path: str | Path,
    *,
    region_column: str = "region",
    flow_column: str = "flow",
    super_class_column: str = "super_class",
    cell_class_column: str = "cell_class",
    cell_type_column: str = "cell_type",
    side_column: str = "side",
) -> VNCAnnotationAtlas:
    source_path = Path(path)
    rows = _read_rows(source_path)
    columns = tuple(rows[0].keys()) if rows else ()
    return VNCAnnotationAtlas(
        source_path=str(source_path),
        row_count=len(rows),
        column_names=columns,
        top_region_counts=tuple(_count_by(rows, "region", region_column, super_class_column=super_class_column)[:20]),
        top_flow_counts=tuple(_count_by(rows, "flow", flow_column, super_class_column=super_class_column)[:20]),
        top_super_class_counts=tuple(_count_by(rows, "super_class", super_class_column, super_class_column=super_class_column)[:20]),
        top_cell_class_counts=tuple(_count_by(rows, "cell_class", cell_class_column, super_class_column=super_class_column)[:30]),
        top_cell_type_counts=tuple(_count_by(rows, "cell_type", cell_type_column, super_class_column=super_class_column)[:50]),
        paired_cell_types=tuple(_paired_cell_types(rows, cell_type_column, side_column)),
    )
