from __future__ import annotations

from brain.spontaneous_data_sources import get_spontaneous_dataset_source_map, get_spontaneous_dataset_sources


def test_spontaneous_dataset_source_map_contains_expected_sources() -> None:
    sources = get_spontaneous_dataset_sources()
    source_map = get_spontaneous_dataset_source_map()
    assert len(sources) >= 4
    assert "aimon2023_dryad" in source_map
    assert "aimon2019_crcns_fly1" in source_map
    assert "mann2017_intrinsic_network" in source_map
    aimon = source_map["aimon2023_dryad"]
    assert aimon.expected_local_dir.endswith("external/spontaneous/aimon2023_dryad")
    assert any(entry.name == "GoodICsdf.pkl" for entry in aimon.files)
