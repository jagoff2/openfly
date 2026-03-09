from __future__ import annotations

from typing import Any, Sequence

import numpy as np

from vision.feature_extractor import VisionIndexCache


def _read_connectome_node_types(connectome: Any) -> np.ndarray:
    node_types = connectome.nodes.type[:]
    return np.asarray(node_types)


def load_node_types(connectome: Any) -> np.ndarray:
    raw_node_types = _read_connectome_node_types(connectome)
    return np.asarray(raw_node_types).reshape(-1)


def build_required_cell_indices(
    connectome: Any,
    tracking_cells: Sequence[str],
    flow_cells: Sequence[str],
) -> VisionIndexCache:
    node_types = load_node_types(connectome)
    return VisionIndexCache.from_node_types(
        node_types,
        tracking_cells=tracking_cells,
        flow_cells=flow_cells,
    )
