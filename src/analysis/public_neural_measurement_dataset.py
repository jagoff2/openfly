from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin
from urllib.request import Request, urlopen
from zipfile import BadZipFile, ZipFile

from brain.public_neural_measurement_sources import (
    PublicNeuralMeasurementFile,
    PublicNeuralMeasurementSource,
    get_public_neural_measurement_source_map,
)


USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Codex/1.0"
MAX_FILE_ACCESS_CHECKS = 0


@dataclass(frozen=True)
class PublicNeuralMeasurementAccessResult:
    url: str
    ok: bool
    status_code: int | None
    error: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PublicNeuralMeasurementManifest:
    source_key: str
    title: str
    primary_url: str
    metadata_url: str
    access: str
    repository_kind: str
    resolved_landing_url: str | None
    version_id: str | None
    dataset_metadata: dict[str, Any]
    files: tuple[PublicNeuralMeasurementFile, ...]
    access_checks: tuple[PublicNeuralMeasurementAccessResult, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_key": self.source_key,
            "title": self.title,
            "primary_url": self.primary_url,
            "metadata_url": self.metadata_url,
            "access": self.access,
            "repository_kind": self.repository_kind,
            "resolved_landing_url": self.resolved_landing_url,
            "version_id": self.version_id,
            "dataset_metadata": self.dataset_metadata,
            "files": [entry.to_dict() for entry in self.files],
            "access_checks": [entry.to_dict() for entry in self.access_checks],
        }


def _fetch_json(url: str, *, timeout_s: float = 30.0) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urlopen(request, timeout=timeout_s) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception:  # noqa: BLE001
        curl_binary = shutil.which("curl.exe") or shutil.which("curl")
        if not curl_binary:
            raise
        connect_timeout_s = max(10, int(timeout_s))
        max_time_s = max(connect_timeout_s + 30, int(timeout_s) * 3)
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as handle:
            tmp_path = Path(handle.name)
        try:
            completed = subprocess.run(
                [
                    curl_binary,
                    "-L",
                    "--fail",
                    "--silent",
                    "--show-error",
                    "--connect-timeout",
                    str(connect_timeout_s),
                    "--max-time",
                    str(max_time_s),
                    "--output",
                    str(tmp_path),
                    url,
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if completed.returncode != 0:
                raise RuntimeError(f"curl failed with code {completed.returncode}: {completed.stderr.strip()}")
            return json.loads(tmp_path.read_text(encoding="utf-8"))
        finally:
            tmp_path.unlink(missing_ok=True)


def _resolve_doi_url(url: str, *, timeout_s: float = 30.0) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout_s) as response:
        return str(response.geturl())


def _check_url(url: str, *, timeout_s: float = 30.0) -> PublicNeuralMeasurementAccessResult:
    bounded_timeout_s = min(float(timeout_s), 5.0)
    request = Request(url, headers={"User-Agent": USER_AGENT}, method="HEAD")
    try:
        with urlopen(request, timeout=bounded_timeout_s) as response:
            return PublicNeuralMeasurementAccessResult(url=url, ok=True, status_code=getattr(response, "status", None), error="")
    except HTTPError as exc:
        return PublicNeuralMeasurementAccessResult(url=url, ok=False, status_code=int(exc.code), error=str(exc))
    except URLError as exc:
        return PublicNeuralMeasurementAccessResult(url=url, ok=False, status_code=None, error=str(exc))


def _resolve_dryad_href(href: str | None, *, base_url: str = "https://datadryad.org") -> str | None:
    if not href:
        return None
    return urljoin(base_url, str(href))


def _dryad_metadata_url_from_doi(doi: str) -> str:
    return f"https://datadryad.org/api/v2/datasets/doi%3A{quote(doi, safe='')}"


def _zenodo_api_url_from_resolved_url(url: str) -> str | None:
    match = re.search(r"zenodo\.org/(?:records|record)/(\d+)", url)
    if not match:
        return None
    return f"https://zenodo.org/api/records/{match.group(1)}"


def _figshare_api_url_from_resolved_url(url: str) -> str | None:
    match = re.search(r"figshare\.com/articles/(?:dataset|media)/[^/]+/(\d+)", url)
    if not match:
        return None
    return f"https://api.figshare.com/v2/articles/{match.group(1)}"


def _manifest_file(
    *,
    name: str,
    size_bytes: int | None,
    description: str,
    primary_download_url: str | None,
    digest: str | None,
) -> PublicNeuralMeasurementFile:
    return PublicNeuralMeasurementFile(
        name=name,
        size_bytes=size_bytes,
        description=description,
        primary_download_url=primary_download_url,
        digest=digest,
    )


def fetch_dryad_manifest(source: PublicNeuralMeasurementSource, *, timeout_s: float = 30.0) -> PublicNeuralMeasurementManifest:
    metadata_url = source.metadata_url
    if "datadryad.org/api" not in metadata_url and source.doi:
        metadata_url = _dryad_metadata_url_from_doi(source.doi)
    dataset_metadata = _fetch_json(metadata_url, timeout_s=timeout_s)
    versions_url = _resolve_dryad_href(dataset_metadata.get("_links", {}).get("stash:versions", {}).get("href"))
    versions_payload = _fetch_json(versions_url, timeout_s=timeout_s) if versions_url else {}
    versions = versions_payload.get("_embedded", {}).get("stash:versions", [])
    version_id = None
    resolved_landing_url = dataset_metadata.get("_links", {}).get("stash:html", {}).get("href")
    if versions:
        version_id = str(versions[0].get("id") or "")
        if not version_id:
            self_href = str(versions[0].get("_links", {}).get("self", {}).get("href", ""))
            if self_href:
                version_id = self_href.rstrip("/").split("/")[-1]
    files_url = _resolve_dryad_href(versions[0].get("_links", {}).get("stash:files", {}).get("href")) if versions else None
    files_payload = _fetch_json(files_url, timeout_s=timeout_s) if files_url else {}
    raw_files = files_payload.get("_embedded", {}).get("stash:files", [])
    files: list[PublicNeuralMeasurementFile] = []
    access_checks: list[PublicNeuralMeasurementAccessResult] = []
    for index, item in enumerate(raw_files):
        api_download_url = _resolve_dryad_href(item.get("_links", {}).get("stash:download", {}).get("href"))
        digest = str(item.get("digest", "")).strip() or None
        files.append(
            _manifest_file(
                name=str(item.get("path", "")),
                size_bytes=int(item.get("size")) if item.get("size") is not None else None,
                description=str(item.get("resourceType", "Dryad file")),
                primary_download_url=api_download_url,
                digest=digest,
            )
        )
        if api_download_url and index < MAX_FILE_ACCESS_CHECKS:
            access_checks.append(_check_url(api_download_url, timeout_s=timeout_s))
    return PublicNeuralMeasurementManifest(
        source_key=source.key,
        title=source.title,
        primary_url=source.primary_url,
        metadata_url=metadata_url,
        access=source.access,
        repository_kind=source.repository_kind,
        resolved_landing_url=str(resolved_landing_url) if resolved_landing_url else None,
        version_id=version_id or None,
        dataset_metadata=dataset_metadata,
        files=tuple(files),
        access_checks=tuple(access_checks),
    )


def fetch_zenodo_manifest(source: PublicNeuralMeasurementSource, *, timeout_s: float = 30.0) -> PublicNeuralMeasurementManifest:
    resolved_url = source.metadata_url
    api_url = source.metadata_url if "zenodo.org/api/records/" in source.metadata_url else None
    if not api_url:
        resolved_url = _resolve_doi_url(source.metadata_url, timeout_s=timeout_s)
        api_url = _zenodo_api_url_from_resolved_url(resolved_url)
    if not api_url:
        raise ValueError(f"Could not derive Zenodo API URL from {resolved_url}")
    payload = _fetch_json(api_url, timeout_s=timeout_s)
    files: list[PublicNeuralMeasurementFile] = []
    access_checks: list[PublicNeuralMeasurementAccessResult] = []
    for index, item in enumerate(payload.get("files", [])):
        download_url = item.get("links", {}).get("content") or item.get("links", {}).get("self") or item.get("links", {}).get("download")
        checksum = str(item.get("checksum", "")).strip()
        if checksum.startswith("md5:"):
            checksum = checksum.split(":", 1)[1]
        files.append(
            _manifest_file(
                name=str(item.get("key", "") or item.get("filename", "")),
                size_bytes=int(item.get("size")) if item.get("size") is not None else None,
                description="Zenodo file",
                primary_download_url=str(download_url) if download_url else None,
                digest=checksum or None,
            )
        )
        if download_url and index < MAX_FILE_ACCESS_CHECKS:
            access_checks.append(_check_url(str(download_url), timeout_s=timeout_s))
    return PublicNeuralMeasurementManifest(
        source_key=source.key,
        title=source.title,
        primary_url=source.primary_url,
        metadata_url=api_url,
        access=source.access,
        repository_kind=source.repository_kind,
        resolved_landing_url=resolved_url,
        version_id=str(payload.get("id") or "") or None,
        dataset_metadata=payload,
        files=tuple(files),
        access_checks=tuple(access_checks),
    )


def fetch_figshare_manifest(source: PublicNeuralMeasurementSource, *, timeout_s: float = 30.0) -> PublicNeuralMeasurementManifest:
    resolved_url = source.metadata_url
    api_url = source.metadata_url if "api.figshare.com/v2/articles/" in source.metadata_url else None
    if not api_url:
        resolved_url = _resolve_doi_url(source.metadata_url, timeout_s=timeout_s)
        api_url = _figshare_api_url_from_resolved_url(resolved_url)
    if not api_url:
        raise ValueError(f"Could not derive Figshare API URL from {resolved_url}")
    payload = _fetch_json(api_url, timeout_s=timeout_s)
    files: list[PublicNeuralMeasurementFile] = []
    access_checks: list[PublicNeuralMeasurementAccessResult] = []
    for index, item in enumerate(payload.get("files", [])):
        download_url = item.get("download_url")
        digest = str(item.get("supplied_md5", "") or item.get("computed_md5", "")).strip() or None
        files.append(
            _manifest_file(
                name=str(item.get("name", "")),
                size_bytes=int(item.get("size")) if item.get("size") is not None else None,
                description="Figshare file",
                primary_download_url=str(download_url) if download_url else None,
                digest=digest,
            )
        )
        if download_url and index < MAX_FILE_ACCESS_CHECKS:
            access_checks.append(_check_url(str(download_url), timeout_s=timeout_s))
    return PublicNeuralMeasurementManifest(
        source_key=source.key,
        title=source.title,
        primary_url=source.primary_url,
        metadata_url=api_url,
        access=source.access,
        repository_kind=source.repository_kind,
        resolved_landing_url=resolved_url,
        version_id=str(payload.get("id") or "") or None,
        dataset_metadata=payload,
        files=tuple(files),
        access_checks=tuple(access_checks),
    )


def fetch_janelia_manifest(source: PublicNeuralMeasurementSource, *, timeout_s: float = 30.0) -> PublicNeuralMeasurementManifest:
    resolved_url = _resolve_doi_url(source.metadata_url, timeout_s=timeout_s)
    access_checks: list[PublicNeuralMeasurementAccessResult] = []
    return PublicNeuralMeasurementManifest(
        source_key=source.key,
        title=source.title,
        primary_url=source.primary_url,
        metadata_url=source.metadata_url,
        access=source.access,
        repository_kind=source.repository_kind,
        resolved_landing_url=resolved_url,
        version_id=None,
        dataset_metadata=source.to_dict(),
        files=tuple(source.files),
        access_checks=tuple(access_checks),
    )


def build_public_neural_measurement_manifest(source_key: str, *, timeout_s: float = 30.0) -> PublicNeuralMeasurementManifest:
    source_map = get_public_neural_measurement_source_map()
    if source_key not in source_map:
        raise KeyError(f"Unknown public neural measurement source: {source_key}")
    source = source_map[source_key]
    if source.repository_kind == "dryad":
        return fetch_dryad_manifest(source, timeout_s=timeout_s)
    if source.repository_kind == "zenodo":
        return fetch_zenodo_manifest(source, timeout_s=timeout_s)
    if source.repository_kind == "figshare":
        return fetch_figshare_manifest(source, timeout_s=timeout_s)
    if source.repository_kind == "janelia":
        return fetch_janelia_manifest(source, timeout_s=timeout_s)
    return PublicNeuralMeasurementManifest(
        source_key=source.key,
        title=source.title,
        primary_url=source.primary_url,
        metadata_url=source.metadata_url,
        access=source.access,
        repository_kind=source.repository_kind,
        resolved_landing_url=None,
        version_id=None,
        dataset_metadata=source.to_dict(),
        files=tuple(source.files),
        access_checks=tuple(),
    )


def write_public_neural_measurement_manifest(manifest: PublicNeuralMeasurementManifest, output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest.to_dict(), indent=2), encoding="utf-8")


def _infer_digest_algorithm(expected_digest: str | None) -> str | None:
    digest = str(expected_digest or "").strip().lower()
    if not digest:
        return None
    if re.fullmatch(r"[0-9a-f]{64}", digest):
        return "sha256"
    if re.fullmatch(r"[0-9a-f]{32}", digest):
        return "md5"
    return None


def _compute_file_digest(path: str | Path, *, algorithm: str) -> str:
    hasher = hashlib.new(algorithm)
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _zip_integrity_ok(path: str | Path) -> bool | None:
    path = Path(path)
    if path.suffix.lower() != ".zip" or not path.exists():
        return None
    try:
        with ZipFile(path) as archive:
            return archive.testzip() is None
    except BadZipFile:
        return False


def _download_with_urlopen(url: str, output_path: Path, *, timeout_s: float) -> None:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout_s) as response, output_path.open("wb") as handle:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)


def _download_with_curl(url: str, output_path: Path, *, timeout_s: float) -> None:
    curl_binary = shutil.which("curl.exe") or shutil.which("curl")
    if not curl_binary:
        raise RuntimeError("curl is not available")
    connect_timeout_s = max(30, int(timeout_s))
    max_time_s = max(connect_timeout_s + 60, int(timeout_s) * 4)
    completed = subprocess.run(
        [
            curl_binary,
            "-L",
            "--fail",
            "--silent",
            "--show-error",
            "--connect-timeout",
            str(connect_timeout_s),
            "--max-time",
            str(max_time_s),
            "--output",
            str(output_path),
            url,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"curl failed with code {completed.returncode}: {completed.stderr.strip()}")


def stage_public_neural_measurement_file(
    dataset_key: str,
    file_name: str,
    *,
    root_dir: str | Path | None = None,
    timeout_s: float = 120.0,
) -> dict[str, Any]:
    source_map = get_public_neural_measurement_source_map()
    if dataset_key not in source_map:
        raise KeyError(f"Unknown public neural measurement source: {dataset_key}")
    source = source_map[dataset_key]
    manifest = build_public_neural_measurement_manifest(dataset_key, timeout_s=min(timeout_s, 30.0))
    try:
        entry = next(item for item in manifest.files if item.name == file_name)
    except StopIteration as exc:
        raise KeyError(f"Unknown file for dataset {dataset_key}: {file_name}") from exc
    if not entry.primary_download_url:
        raise ValueError(f"No download URL available for {dataset_key}:{file_name}")
    dataset_root = Path(root_dir or source.expected_local_dir)
    dataset_root.mkdir(parents=True, exist_ok=True)
    output_path = dataset_root / entry.name
    expected_algorithm = _infer_digest_algorithm(entry.digest)
    if output_path.exists():
        existing_size = int(output_path.stat().st_size)
        digest_match = None
        actual_digest = None
        if expected_algorithm and entry.digest:
            actual_digest = _compute_file_digest(output_path, algorithm=expected_algorithm)
            digest_match = actual_digest.lower() == str(entry.digest).lower()
        if (entry.size_bytes is None or existing_size == int(entry.size_bytes)) and (digest_match is not False):
            return {
                "dataset_key": dataset_key,
                "file_name": file_name,
                "path": str(output_path),
                "status": "already_valid",
                "size_bytes": existing_size,
                "expected_size_bytes": entry.size_bytes,
                "actual_digest": actual_digest,
                "expected_digest": entry.digest,
                "zip_valid": _zip_integrity_ok(output_path),
            }
    tmp_path = output_path.with_suffix(output_path.suffix + ".download")
    try:
        _download_with_curl(entry.primary_download_url, tmp_path, timeout_s=timeout_s)
    except Exception as curl_exc:  # noqa: BLE001
        try:
            _download_with_urlopen(entry.primary_download_url, tmp_path, timeout_s=timeout_s)
        except Exception as url_exc:  # noqa: BLE001
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)
            raise RuntimeError(
                f"Failed to download {dataset_key}:{file_name}: "
                f"curl={type(curl_exc).__name__}: {curl_exc}; "
                f"urlopen={type(url_exc).__name__}: {url_exc}"
            ) from url_exc
    try:
        actual_size = int(tmp_path.stat().st_size)
        if entry.size_bytes is not None and actual_size != int(entry.size_bytes):
            raise ValueError(f"downloaded size mismatch for {file_name}: {actual_size} != {entry.size_bytes}")
        actual_digest = None
        if expected_algorithm and entry.digest:
            actual_digest = _compute_file_digest(tmp_path, algorithm=expected_algorithm)
            if actual_digest.lower() != str(entry.digest).lower():
                raise ValueError(f"digest mismatch for {file_name}")
        tmp_path.replace(output_path)
        return {
            "dataset_key": dataset_key,
            "file_name": file_name,
            "path": str(output_path),
            "status": "downloaded",
            "source_url": entry.primary_download_url,
            "size_bytes": actual_size,
            "expected_size_bytes": entry.size_bytes,
            "actual_digest": actual_digest,
            "expected_digest": entry.digest,
            "zip_valid": _zip_integrity_ok(output_path),
        }
    finally:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)


def inspect_local_public_neural_measurement_dataset(
    dataset_key: str,
    *,
    root_dir: str | Path | None = None,
    timeout_s: float = 30.0,
) -> dict[str, Any]:
    source_map = get_public_neural_measurement_source_map()
    if dataset_key not in source_map:
        raise KeyError(f"Unknown public neural measurement source: {dataset_key}")
    source = source_map[dataset_key]
    manifest = build_public_neural_measurement_manifest(dataset_key, timeout_s=timeout_s)
    dataset_root = Path(root_dir or source.expected_local_dir)
    file_rows = []
    for entry in manifest.files:
        path = dataset_root / entry.name
        actual_digest = None
        digest_algorithm = _infer_digest_algorithm(entry.digest)
        digest_match = None
        if path.exists() and digest_algorithm and entry.digest:
            actual_digest = _compute_file_digest(path, algorithm=digest_algorithm)
            digest_match = actual_digest.lower() == str(entry.digest).lower()
        file_rows.append(
            {
                "name": entry.name,
                "exists": path.exists(),
                "size_bytes": int(path.stat().st_size) if path.exists() else None,
                "expected_size_bytes": entry.size_bytes,
                "expected_digest": entry.digest,
                "actual_digest": actual_digest,
                "digest_algorithm": digest_algorithm,
                "digest_match": digest_match,
                "zip_valid": _zip_integrity_ok(path),
                "primary_download_url": entry.primary_download_url,
            }
        )
    return {
        "dataset": source.to_dict(),
        "manifest": manifest.to_dict(),
        "root_dir": str(dataset_root),
        "files": file_rows,
    }


def write_public_neural_measurement_summary(
    dataset_key: str,
    *,
    output_path: str | Path,
    root_dir: str | Path | None = None,
    timeout_s: float = 30.0,
) -> dict[str, Any]:
    payload = inspect_local_public_neural_measurement_dataset(dataset_key, root_dir=root_dir, timeout_s=timeout_s)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload
