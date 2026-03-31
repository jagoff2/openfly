from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _normalize_scalar(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, np.bytes_):
        return value.tobytes().decode("utf-8", errors="replace")
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _to_numpy(value: Any) -> np.ndarray:
    if hasattr(value, "numpy"):
        value = value.numpy()
    return np.asarray(value)


def _extract_attr_array(nodes: Any, attr_name: str) -> tuple[np.ndarray | None, str | None]:
    try:
        value = getattr(nodes, attr_name)
    except Exception as exc:
        return None, f"getattr failed: {type(exc).__name__}: {exc}"
    for candidate in (value,):
        try:
            return _to_numpy(candidate[:]), None
        except Exception:
            pass
    try:
        return _to_numpy(value), None
    except Exception as exc:
        return None, f"array conversion failed: {type(exc).__name__}: {exc}"


def _summarize_array(array: np.ndarray, max_items: int = 5) -> dict[str, Any]:
    flat = array.reshape(-1) if array.size else array
    return {
        "shape": list(array.shape),
        "dtype": str(array.dtype),
        "sample": [_normalize_scalar(item) for item in flat[:max_items]],
    }


def main() -> None:
    import flyvis
    from flygym.examples.vision.vision_network import RealTimeVisionNetworkView
    from vision.flyvis_compat import configure_flyvis_device

    configure_flyvis_device(force_cpu=False)

    output_path = Path("outputs/metrics/flyvis_overlap_inventory.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    completeness_df = pd.read_csv("external/fly-brain/data/2025_Completeness_783.csv", index_col=0)
    whole_brain_ids = {int(index) for index in completeness_df.index}

    model_dir = flyvis.results_dir / "flow/0000/000"
    network_view = RealTimeVisionNetworkView(model_dir)
    network = network_view.init_network(chkpt="best_chkpt")
    nodes = network.connectome.nodes

    node_type_array, error = _extract_attr_array(nodes, "type")
    if node_type_array is None:
        raise RuntimeError(f"Could not read FlyVis node types: {error}")
    num_nodes = int(node_type_array.reshape(-1).shape[0])
    unique_types = sorted({_normalize_scalar(item) for item in node_type_array.reshape(-1)})

    attr_summaries: dict[str, Any] = {}
    identity_candidates: list[dict[str, Any]] = []
    for attr_name in sorted(name for name in dir(nodes) if not name.startswith("_")):
        array, err = _extract_attr_array(nodes, attr_name)
        if array is None:
            attr_summaries[attr_name] = {"error": err}
            continue
        summary = _summarize_array(array)
        summary["node_aligned"] = bool(array.size == num_nodes or (array.ndim > 0 and array.shape[0] == num_nodes))
        attr_summaries[attr_name] = summary
        if array.size == 0:
            continue
        if np.issubdtype(array.dtype, np.integer):
            values = {int(value) for value in array.reshape(-1).tolist()}
            overlap_count = len(values & whole_brain_ids)
            if overlap_count:
                identity_candidates.append(
                    {
                        "attr_name": attr_name,
                        "overlap_count": overlap_count,
                        "fraction_of_whole_brain_ids": overlap_count / max(1, len(whole_brain_ids)),
                        "fraction_of_attr_values": overlap_count / max(1, len(values)),
                        "summary": summary,
                    }
                )

    identity_candidates.sort(key=lambda item: item["overlap_count"], reverse=True)

    result = {
        "flyvis_model_dir": str(model_dir),
        "num_flyvis_nodes": num_nodes,
        "num_unique_flyvis_types": len(unique_types),
        "flyvis_types_sample": unique_types[:100],
        "candidate_identity_fields": identity_candidates[:20],
        "node_attributes": attr_summaries,
    }
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
