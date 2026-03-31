from __future__ import annotations

from brain.public_neural_measurement_sources import (
    get_public_neural_measurement_source_map,
    get_public_neural_measurement_sources,
)


def test_public_neural_measurement_source_map_contains_priority_sources() -> None:
    sources = get_public_neural_measurement_sources()
    source_map = get_public_neural_measurement_source_map()
    assert len(sources) >= 6
    assert "aimon2023_dryad" in source_map
    assert "schaffer2023_figshare" in source_map
    assert "ketkar2022_zenodo" in source_map
    assert "gruntman2019_janelia" in source_map
    assert "shomar2025_dryad" in source_map
    assert "dallmann2025_dryad" in source_map
    assert source_map["aimon2023_dryad"].expected_local_dir.endswith("external/spontaneous/aimon2023_dryad")
