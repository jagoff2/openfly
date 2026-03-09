from __future__ import annotations

import json

import flyvis
from flygym.examples.vision import RealTimeVisionNetworkView


def main() -> None:
    net_view = RealTimeVisionNetworkView(str(flyvis.results_dir / "flow/0000/000"))
    network = net_view.init_network(chkpt="best_chkpt")
    conn = network.connectome
    payload: dict[str, object] = {
        "node_attrs": [name for name in dir(conn.nodes) if not name.startswith("_")][:200],
        "selected": {},
    }
    for name in ["type", "layer_index", "root_id", "id", "cell_type", "hemisphere", "bodyId", "instance"]:
        if hasattr(conn.nodes, name):
            value = getattr(conn.nodes, name)
            row = {"type": type(value).__name__}
            try:
                arr = value[:]
                row["shape"] = getattr(arr, "shape", None)
                row["dtype"] = str(getattr(arr, "dtype", None))
                row["sample"] = [str(x) for x in arr[:5]]
            except Exception as exc:
                row["slice_error"] = repr(exc)
            payload["selected"][name] = row
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
