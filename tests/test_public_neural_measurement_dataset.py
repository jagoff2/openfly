from __future__ import annotations

import json
from io import BytesIO
from zipfile import ZipFile

import pytest

import analysis.public_neural_measurement_dataset as measurement_module
from brain.public_neural_measurement_sources import PublicNeuralMeasurementSource


class _FakeResponse:
    def __init__(self, payload: str, status: int = 200) -> None:
        self._payload = payload.encode("utf-8")
        self.status = status

    def read(self, size: int = -1) -> bytes:
        return self._payload if size == -1 else self._payload[:size]

    def geturl(self) -> str:
        return "https://example.test/final"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


class _FakeBinaryResponse:
    def __init__(self, payload: bytes, status: int = 200) -> None:
        self._buffer = BytesIO(payload)
        self.status = status

    def read(self, size: int = -1) -> bytes:
        return self._buffer.read(size)

    def geturl(self) -> str:
        return "https://example.test/final"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


def test_doi_helper_url_derivations() -> None:
    assert measurement_module._dryad_metadata_url_from_doi("10.5061/dryad.abc123") == (
        "https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.abc123"
    )
    assert measurement_module._zenodo_api_url_from_resolved_url("https://zenodo.org/records/6335347") == (
        "https://zenodo.org/api/records/6335347"
    )
    assert measurement_module._figshare_api_url_from_resolved_url(
        "https://figshare.com/articles/dataset/example/23749074"
    ) == "https://api.figshare.com/v2/articles/23749074"


def test_build_public_neural_measurement_manifest_for_zenodo(monkeypatch: pytest.MonkeyPatch) -> None:
    source = PublicNeuralMeasurementSource(
        key="test_zenodo",
        title="Test Zenodo",
        citation_label="Test",
        scope="test",
        access="public",
        repository_kind="zenodo",
        primary_url="https://doi.org/10.5281/zenodo.1",
        metadata_url="https://doi.org/10.5281/zenodo.1",
        expected_local_dir="external/neural_measurements/test_zenodo",
        notes="",
        doi="10.5281/zenodo.1",
    )
    payload = {
        "id": 42,
        "files": [
            {
                "key": "trace.npy",
                "size": 123,
                "checksum": "md5:abc123",
                "links": {"content": "https://example.test/trace.npy"},
            }
        ],
    }

    monkeypatch.setattr(measurement_module, "_resolve_doi_url", lambda url, timeout_s=30.0: "https://zenodo.org/records/42")
    monkeypatch.setattr(measurement_module, "_fetch_json", lambda url, timeout_s=30.0: payload)
    monkeypatch.setattr(measurement_module, "_check_url", lambda url, timeout_s=30.0: measurement_module.PublicNeuralMeasurementAccessResult(url, True, 200, ""))
    monkeypatch.setattr(
        measurement_module,
        "get_public_neural_measurement_source_map",
        lambda: {"test_zenodo": source},
    )

    manifest = measurement_module.build_public_neural_measurement_manifest("test_zenodo")

    assert manifest.version_id == "42"
    assert manifest.resolved_landing_url == "https://zenodo.org/records/42"
    assert len(manifest.files) == 1
    assert manifest.files[0].name == "trace.npy"


def test_stage_public_neural_measurement_file_uses_manifest_entry(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    buffer = BytesIO()
    with ZipFile(buffer, mode="w") as archive:
        archive.writestr("trial/trace.txt", "hello")
    payload = buffer.getvalue()
    digest = measurement_module.hashlib.sha256(payload).hexdigest()
    source = PublicNeuralMeasurementSource(
        key="test_dataset",
        title="Test",
        citation_label="Test",
        scope="test",
        access="public",
        repository_kind="zenodo",
        primary_url="https://doi.org/10.5281/zenodo.1",
        metadata_url="https://doi.org/10.5281/zenodo.1",
        expected_local_dir=str(tmp_path),
        notes="",
    )
    manifest = measurement_module.PublicNeuralMeasurementManifest(
        source_key="test_dataset",
        title="Test",
        primary_url=source.primary_url,
        metadata_url="https://example.test/api",
        access="public",
        repository_kind="zenodo",
        resolved_landing_url="https://example.test/landing",
        version_id="1",
        dataset_metadata={},
        files=(
            measurement_module.PublicNeuralMeasurementFile(
                name="test.zip",
                size_bytes=len(payload),
                description="zip payload",
                primary_download_url="https://example.test/test.zip",
                digest=digest,
            ),
        ),
        access_checks=(),
    )

    monkeypatch.setattr(
        measurement_module,
        "get_public_neural_measurement_source_map",
        lambda: {"test_dataset": source},
    )
    monkeypatch.setattr(measurement_module, "build_public_neural_measurement_manifest", lambda source_key, timeout_s=30.0: manifest)
    monkeypatch.setattr(measurement_module, "_download_with_curl", lambda url, output_path, timeout_s=120.0: output_path.write_bytes(payload))

    result = measurement_module.stage_public_neural_measurement_file("test_dataset", "test.zip", root_dir=tmp_path)

    assert result["status"] == "downloaded"
    assert result["actual_digest"] == digest
    assert result["zip_valid"] is True
