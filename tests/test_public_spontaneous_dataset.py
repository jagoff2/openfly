from __future__ import annotations

import hashlib
import json
from io import BytesIO
from zipfile import ZipFile

import pandas as pd
import pytest

import analysis.public_spontaneous_dataset as public_dataset_module
from brain.spontaneous_data_sources import SpontaneousDatasetFile, SpontaneousDatasetSource


class _FakeResponse:
    def __init__(self, payload: str, status: int = 200) -> None:
        self._payload = payload.encode("utf-8")
        self.status = status

    def read(self) -> bytes:
        return self._payload

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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


def test_build_public_dataset_manifest_for_dryad(monkeypatch: pytest.MonkeyPatch) -> None:
    dataset_payload = {"_links": {"stash:versions": {"href": "https://example.test/versions"}}}
    versions_payload = {
        "_embedded": {
            "stash:versions": [
                {
                    "id": 230771,
                    "_links": {"stash:files": {"href": "https://example.test/files"}},
                }
            ]
        }
    }
    files_payload = {
        "_embedded": {
            "stash:files": [
                {
                    "id": 2240212,
                    "path": "Additional_data.zip",
                    "size": 599364517,
                    "digest": "abc",
                    "_links": {"stash:download": {"href": "https://example.test/download/2240212"}},
                }
            ]
        }
    }

    def fake_urlopen(request, timeout=30.0):
        url = request.full_url
        if url == "https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.3bk3j9kpb":
            return _FakeResponse(json.dumps(dataset_payload))
        if url == "https://example.test/versions":
            return _FakeResponse(json.dumps(versions_payload))
        if url == "https://example.test/files":
            return _FakeResponse(json.dumps(files_payload))
        return _FakeResponse("", status=200)

    monkeypatch.setattr(public_dataset_module, "urlopen", fake_urlopen)

    manifest = public_dataset_module.build_public_dataset_manifest("aimon2023_dryad")

    assert manifest.version_id == "230771"
    assert len(manifest.files) == 1
    assert manifest.files[0].path == "Additional_data.zip"


def test_build_public_dataset_manifest_for_static_source() -> None:
    manifest = public_dataset_module.build_public_dataset_manifest("mann2017_intrinsic_network")

    assert manifest.source_key == "mann2017_intrinsic_network"
    assert manifest.version_id is None
    assert len(manifest.files) == 0


def test_resolve_dryad_href_normalizes_relative_paths() -> None:
    assert (
        public_dataset_module._resolve_dryad_href("/api/v2/files/2240206/download")
        == "https://datadryad.org/api/v2/files/2240206/download"
    )
    assert public_dataset_module._resolve_dryad_href("https://example.test/x") == "https://example.test/x"
    assert public_dataset_module._resolve_dryad_href(None) is None


def test_candidate_download_urls_prefers_zenodo_api_content() -> None:
    urls = public_dataset_module._candidate_download_urls(
        "https://zenodo.org/records/7849014/files/Additional_data.zip?download=1"
    )
    assert urls[0] == "https://zenodo.org/api/records/7849014/files/Additional_data.zip/content"
    assert urls[1] == "https://zenodo.org/records/7849014/files/Additional_data.zip?download=1"


def test_stage_public_dataset_file_downloads_and_validates_zip(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    buffer = BytesIO()
    with ZipFile(buffer, mode="w") as archive:
        archive.writestr("folder/test.txt", "hello world")
    payload = buffer.getvalue()
    digest = hashlib.sha256(payload).hexdigest()
    source = SpontaneousDatasetSource(
        key="test_dataset",
        title="Test Dataset",
        citation_label="Test",
        scope="test",
        access="public",
        primary_url="https://example.test",
        metadata_url="https://example.test/meta",
        notes="",
        expected_local_dir=str(tmp_path / "default"),
        files=(
            SpontaneousDatasetFile(
                name="test.zip",
                size_bytes=len(payload),
                description="zip payload",
                primary_download_url="https://zenodo.org/records/1/files/test.zip?download=1",
                md5=digest,
            ),
        ),
    )

    def fake_urlopen(request, timeout=120.0):
        return _FakeBinaryResponse(payload)

    def fake_curl(url: str, output_path, *, timeout_s: float) -> None:
        raise RuntimeError("curl disabled in unit test")

    monkeypatch.setattr(public_dataset_module, "urlopen", fake_urlopen)
    monkeypatch.setattr(public_dataset_module, "_download_with_curl", fake_curl)
    monkeypatch.setattr(
        public_dataset_module,
        "get_spontaneous_dataset_source_map",
        lambda: {"test_dataset": source},
    )

    result = public_dataset_module.stage_public_dataset_file(
        "test_dataset",
        "test.zip",
        root_dir=tmp_path,
    )

    assert result["status"] == "downloaded"
    assert result["size_bytes"] == len(payload)
    assert result["expected_digest"] == digest
    assert result["actual_digest"] == digest
    assert result["zip_valid"] is True
    assert (tmp_path / "test.zip").exists()


def test_stage_public_dataset_file_short_circuits_for_existing_valid_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    payload = b"plain text payload"
    digest = hashlib.sha256(payload).hexdigest()
    target_path = tmp_path / "plain.bin"
    target_path.write_bytes(payload)
    source = SpontaneousDatasetSource(
        key="test_dataset",
        title="Test Dataset",
        citation_label="Test",
        scope="test",
        access="public",
        primary_url="https://example.test",
        metadata_url="https://example.test/meta",
        notes="",
        expected_local_dir=str(tmp_path / "default"),
        files=(
            SpontaneousDatasetFile(
                name="plain.bin",
                size_bytes=len(payload),
                description="plain payload",
                primary_download_url="https://example.test/plain.bin",
                md5=digest,
            ),
        ),
    )

    def fail_urlopen(request, timeout=120.0):
        raise AssertionError("urlopen should not be called when an existing file is already valid")

    monkeypatch.setattr(public_dataset_module, "urlopen", fail_urlopen)
    monkeypatch.setattr(
        public_dataset_module,
        "get_spontaneous_dataset_source_map",
        lambda: {"test_dataset": source},
    )

    result = public_dataset_module.stage_public_dataset_file(
        "test_dataset",
        "plain.bin",
        root_dir=tmp_path,
    )

    assert result["status"] == "already_valid"
    assert result["size_bytes"] == len(payload)
    assert result["actual_digest"] == digest


def test_summarize_goodics_dataframe_ignores_blank_regressor_strings() -> None:
    df = pd.DataFrame(
        {
            "expID": ["A", "B", "C"],
            "WalkRegressor": ["foo.mat", "", None],
            "TurnRegressor": ["  ", "bar.mat", None],
            "ForcedWalkRegressor": ["", "", "baz.mat"],
            "ForcedTurnRegressor": [None, "   ", "qux.mat"],
            "WalkSubstrate": ["AirBall", "Styr", "AirBall"],
        }
    )

    summary = public_dataset_module.summarize_goodics_dataframe(df)

    assert summary["walk_regressor_rows"] == 1
    assert summary["turn_regressor_rows"] == 1
    assert summary["forced_walk_regressor_rows"] == 1
    assert summary["forced_turn_regressor_rows"] == 1
