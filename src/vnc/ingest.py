from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.ipc as pa_ipc

from vnc.schema import EDGE_FIELD_ALIASES, canonical_flow, canonical_side, canonical_super_class, first_present, first_present_from_map, normalize_key, normalize_text


def _read_table(path: Path) -> list[dict[str, str]]:
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
            raise ValueError("Expected JSON table payload to be a list.")
        rows: list[dict[str, str]] = []
        for item in payload:
            if isinstance(item, dict):
                rows.append({normalize_key(key): normalize_text(value) for key, value in item.items()})
        return rows
    raise ValueError(f"Unsupported table format: {path}")


def _feather_schema_names(path: Path) -> tuple[str, ...]:
    with pa.memory_map(str(path), "r") as source:
        reader = pa_ipc.RecordBatchFileReader(source)
        return tuple(reader.schema.names)


def _resolve_edge_columns(path: Path) -> tuple[str, str, str]:
    available = set(_feather_schema_names(path))
    aliases = {
        field: tuple(column for column in EDGE_FIELD_ALIASES[field] if column in available)
        for field in ("pre_root_id", "post_root_id", "weight")
    }
    if not aliases["pre_root_id"] or not aliases["post_root_id"]:
        raise KeyError(f"Could not resolve edge columns for {path}. Available columns: {sorted(available)}")
    weight_candidates = aliases["weight"] or ("weight",)
    return aliases["pre_root_id"][0], aliases["post_root_id"][0], weight_candidates[0]


def _parse_int(value: Any, default: int = 0) -> int:
    text = normalize_text(value)
    if not text:
        return default
    return int(float(text))


@dataclass(frozen=True)
class VNCNode:
    root_id: int
    region: str
    entry_nerve: str
    exit_nerve: str
    flow: str
    super_class: str
    cell_class: str
    cell_type: str
    side: str


@dataclass(frozen=True)
class VNCEdge:
    pre_root_id: int
    post_root_id: int
    weight: int


@dataclass(frozen=True)
class VNCGraphSlice:
    nodes: tuple[VNCNode, ...]
    edges: tuple[VNCEdge, ...]

    def node_map(self) -> dict[int, VNCNode]:
        return {node.root_id: node for node in self.nodes}


def load_vnc_nodes(path: str | Path) -> tuple[VNCNode, ...]:
    rows = _read_table(Path(path))
    if not rows:
        return ()
    return tuple(
        VNCNode(
            root_id=_parse_int(first_present(row, "root_id")),
            region=first_present(row, "region"),
            entry_nerve=first_present(row, "entry_nerve"),
            exit_nerve=first_present(row, "exit_nerve"),
            flow=canonical_flow(first_present(row, "flow"), canonical_super_class(first_present(row, "super_class"))),
            super_class=canonical_super_class(first_present(row, "super_class")),
            cell_class=first_present(row, "cell_class"),
            cell_type=first_present(row, "cell_type"),
            side=canonical_side(first_present(row, "side")),
        )
        for row in rows
        if first_present(row, "root_id")
    )


def load_vnc_edges(path: str | Path) -> tuple[VNCEdge, ...]:
    edge_path = Path(path)
    if edge_path.suffix.lower() == ".feather":
        return load_vnc_edges_filtered(edge_path)
    rows = _read_table(edge_path)
    if not rows:
        return ()
    return tuple(
        VNCEdge(
            pre_root_id=_parse_int(first_present_from_map(row, EDGE_FIELD_ALIASES, "pre_root_id")),
            post_root_id=_parse_int(first_present_from_map(row, EDGE_FIELD_ALIASES, "post_root_id")),
            weight=_parse_int(first_present_from_map(row, EDGE_FIELD_ALIASES, "weight"), default=1),
        )
        for row in rows
        if first_present_from_map(row, EDGE_FIELD_ALIASES, "pre_root_id")
        and first_present_from_map(row, EDGE_FIELD_ALIASES, "post_root_id")
    )


def load_vnc_edge_frame(
    path: str | Path,
    *,
    pre_root_ids: set[int] | None = None,
    post_root_ids: set[int] | None = None,
    min_weight: int = 1,
) -> pd.DataFrame:
    edge_path = Path(path)
    if edge_path.suffix.lower() != ".feather":
        rows = load_vnc_edges(edge_path)
        frame = pd.DataFrame(
            [
                {
                    "pre_root_id": edge.pre_root_id,
                    "post_root_id": edge.post_root_id,
                    "weight": edge.weight,
                }
                for edge in rows
            ]
        )
    else:
        pre_column, post_column, weight_column = _resolve_edge_columns(edge_path)
        frame = pd.read_feather(edge_path, columns=[pre_column, post_column, weight_column]).rename(
            columns={
                pre_column: "pre_root_id",
                post_column: "post_root_id",
                weight_column: "weight",
            }
        )
    if min_weight > 1:
        frame = frame[frame["weight"] >= int(min_weight)]
    if pre_root_ids is not None:
        frame = frame[frame["pre_root_id"].isin(list(pre_root_ids))]
    if post_root_ids is not None:
        frame = frame[frame["post_root_id"].isin(list(post_root_ids))]
    return frame.reset_index(drop=True)


def load_vnc_edges_filtered(
    path: str | Path,
    *,
    pre_root_ids: set[int] | None = None,
    post_root_ids: set[int] | None = None,
    min_weight: int = 1,
) -> tuple[VNCEdge, ...]:
    frame = load_vnc_edge_frame(
        path,
        pre_root_ids=pre_root_ids,
        post_root_ids=post_root_ids,
        min_weight=min_weight,
    )
    return tuple(
        VNCEdge(
            pre_root_id=int(row.pre_root_id),
            post_root_id=int(row.post_root_id),
            weight=int(row.weight),
        )
        for row in frame.itertuples(index=False)
    )


def load_vnc_graph_slice(annotation_path: str | Path, edge_path: str | Path) -> VNCGraphSlice:
    return VNCGraphSlice(nodes=load_vnc_nodes(annotation_path), edges=load_vnc_edges(edge_path))
