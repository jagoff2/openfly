from __future__ import annotations

from pathlib import Path

import numpy as np

from body.interfaces import BodyObservation
from bridge.visual_splice import FlyVisConnectomeCache, VisualSpliceConfig, VisualSpliceInjector


def _write_annotation(path: Path) -> None:
    path.write_text(
        "root_id\tcell_type\tside\tsoma_x\tsoma_y\tsoma_z\n"
        "1\tTmY14\tleft\t0\t0\t0\n"
        "2\tTmY14\tleft\t1\t0\t0\n"
        "3\tTmY14\tright\t0\t0\t0\n"
        "4\tTmY14\tright\t1\t0\t0\n"
        "5\tT5d\tleft\t0\t1\t0\n"
        "6\tT5d\tleft\t1\t1\t0\n"
        "7\tT5d\tright\t0\t1\t0\n"
        "8\tT5d\tright\t1\t1\t0\n",
        encoding="utf-8",
    )


def _obs(arr: np.ndarray, cache: FlyVisConnectomeCache) -> BodyObservation:
    return BodyObservation(
        sim_time=0.0,
        position_xy=(0.0, 0.0),
        yaw=0.0,
        forward_speed=0.0,
        yaw_rate=0.0,
        contact_force=0.0,
        realistic_vision_array=arr,
        realistic_vision_splice_cache=cache,
        vision_payload_mode="fast",
    )


def test_visual_splice_initializes_baseline_then_emits_signed_current(tmp_path: Path) -> None:
    annotation_path = tmp_path / "annot.tsv"
    _write_annotation(annotation_path)
    cache = FlyVisConnectomeCache(
        node_types=np.asarray(["TmY14", "TmY14", "T5d", "T5d"], dtype=object),
        node_u=np.asarray([0.0, 1.0, 0.0, 1.0], dtype=float),
        node_v=np.asarray([0.0, 0.0, 1.0, 1.0], dtype=float),
    )
    injector = VisualSpliceInjector(
        VisualSpliceConfig(
            enabled=True,
            annotation_path=str(annotation_path),
            spatial_mode="axis1d",
            spatial_bins=2,
            min_roots_per_bin=1,
            value_scale=10.0,
            max_abs_current=5.0,
        )
    )
    baseline = np.ones((2, 4), dtype=float)
    currents0, info0 = injector.build(_obs(baseline, cache))
    assert currents0 == {}
    assert info0["initialized_baseline"] is True
    current = baseline.copy()
    current[0, 0] = 0.5
    current[1, 1] = 1.5
    currents1, info1 = injector.build(_obs(current, cache))
    assert info1["initialized_baseline"] is False
    assert info1["nonzero_root_count"] > 0
    assert any(value < 0.0 for value in currents1.values())
    assert any(value > 0.0 for value in currents1.values())
