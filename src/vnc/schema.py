from __future__ import annotations

from typing import Any


FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "root_id": ("pt_root_id", "root_id", "id", "bodyId", "mancBodyid", "root_id"),
    "region": ("region", "somaNeuromere", "nerve", "entryNerve", "exitNerve"),
    "entry_nerve": ("entry_nerve", "entryNerve"),
    "exit_nerve": ("exit_nerve", "exitNerve"),
    "flow": ("flow",),
    "super_class": ("super_class", "superclass"),
    "cell_class": ("cell_class", "class", "subclass", "supertype"),
    "cell_type": ("cell_type", "type", "mancType", "flywireType", "hemibrainType", "instance"),
    "side": ("side", "rootSide", "somaSide"),
}

EDGE_FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "pre_root_id": ("pre_pt_root_id", "pre_root_id", "source", "body_pre"),
    "post_root_id": ("post_pt_root_id", "post_root_id", "target", "body_post"),
    "weight": ("n", "weight"),
}


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def normalize_key(value: Any) -> str:
    return normalize_text(value).lstrip("\ufeff")


def first_present(row: dict[str, str], field: str, primary_column: str | None = None) -> str:
    if primary_column:
        value = normalize_text(row.get(primary_column, ""))
        if value:
            return value
    for key in FIELD_ALIASES.get(field, ()):
        value = normalize_text(row.get(key, ""))
        if value:
            return value
    return ""


def first_present_from_map(
    row: dict[str, str],
    alias_map: dict[str, tuple[str, ...]],
    field: str,
    primary_column: str | None = None,
) -> str:
    if primary_column:
        value = normalize_text(row.get(primary_column, ""))
        if value:
            return value
    for key in alias_map.get(field, ()):
        value = normalize_text(row.get(key, ""))
        if value:
            return value
    return ""


def canonical_super_class(value: str) -> str:
    text = normalize_text(value).lower()
    if not text:
        return ""
    if "descending" in text:
        return "descending"
    if "ascending" in text:
        return "ascending"
    if "motor" in text or "efferent" in text:
        return "motor"
    if "sensory" in text or "visual" in text:
        return "sensory"
    if "intrinsic" in text:
        return "interneuron"
    return text


def canonical_flow(value: str, super_class: str) -> str:
    text = normalize_text(value).lower()
    if text:
        return text
    if super_class in {"descending", "motor"}:
        return "efferent"
    if super_class in {"ascending", "sensory"}:
        return "afferent"
    if super_class:
        return "intrinsic"
    return ""


def canonical_side(value: str) -> str:
    text = normalize_text(value)
    lowered = text.lower()
    if lowered in {"l", "left"}:
        return "L"
    if lowered in {"r", "right"}:
        return "R"
    return text
