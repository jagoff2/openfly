from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from zipfile import BadZipFile, ZipFile

import pandas as pd

from brain.spontaneous_data_sources import SpontaneousDatasetSource, get_spontaneous_dataset_source_map


USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Codex/1.0"


@dataclass(frozen=True)
class PublicDatasetFile:
    path: str
    size_bytes: int | None
    digest: str
    api_download_url: str | None
    browser_download_url: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PublicDatasetAccessResult:
    url: str
    ok: bool
    status_code: int | None
    error: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PublicDatasetManifest:
    source_key: str
    title: str
    primary_url: str
    data_access_url: str
    access: str
    version_id: str | None
    dataset_metadata: dict[str, Any]
    files: tuple[PublicDatasetFile, ...]
    access_checks: tuple[PublicDatasetAccessResult, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_key": self.source_key,
            "title": self.title,
            "primary_url": self.primary_url,
            "data_access_url": self.data_access_url,
            "access": self.access,
            "version_id": self.version_id,
            "dataset_metadata": self.dataset_metadata,
            "files": [item.to_dict() for item in self.files],
            "access_checks": [item.to_dict() for item in self.access_checks],
        }


def _fetch_json(url: str, *, timeout_s: float = 30.0) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urlopen(request, timeout=timeout_s) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def _check_url(url: str, *, timeout_s: float = 30.0) -> PublicDatasetAccessResult:
    bounded_timeout_s = min(float(timeout_s), 5.0)
    request = Request(url, headers={"User-Agent": USER_AGENT}, method="HEAD")
    try:
        with urlopen(request, timeout=bounded_timeout_s) as response:
            return PublicDatasetAccessResult(url=url, ok=True, status_code=getattr(response, "status", None), error="")
    except HTTPError as exc:
        return PublicDatasetAccessResult(url=url, ok=False, status_code=int(exc.code), error=str(exc))
    except URLError as exc:
        return PublicDatasetAccessResult(url=url, ok=False, status_code=None, error=str(exc))


def _resolve_dryad_href(href: str | None, *, base_url: str = "https://datadryad.org") -> str | None:
    if not href:
        return None
    return urljoin(base_url, str(href))


def fetch_dryad_manifest(source: SpontaneousDatasetSource, *, timeout_s: float = 30.0) -> PublicDatasetManifest:
    dataset_metadata = _fetch_json(source.metadata_url, timeout_s=timeout_s)
    versions_url = _resolve_dryad_href(dataset_metadata.get("_links", {}).get("stash:versions", {}).get("href"))
    versions_payload = _fetch_json(versions_url, timeout_s=timeout_s) if versions_url else {}
    versions = versions_payload.get("_embedded", {}).get("stash:versions", [])
    version_id = None
    if versions:
        version_id = str(versions[0].get("id") or "")
        if not version_id:
            self_href = str(versions[0].get("_links", {}).get("self", {}).get("href", ""))
            if self_href:
                version_id = self_href.rstrip("/").split("/")[-1]
    files_url = _resolve_dryad_href(versions[0].get("_links", {}).get("stash:files", {}).get("href")) if versions else None
    files_payload = _fetch_json(files_url, timeout_s=timeout_s) if files_url else {}
    raw_files = files_payload.get("_embedded", {}).get("stash:files", [])
    files: list[PublicDatasetFile] = []
    access_checks: list[PublicDatasetAccessResult] = []
    for item in raw_files:
        api_download_url = _resolve_dryad_href(item.get("_links", {}).get("stash:download", {}).get("href"))
        browser_download_url = None
        files.append(
            PublicDatasetFile(
                path=str(item.get("path", "")),
                size_bytes=int(item.get("size")) if item.get("size") is not None else None,
                digest=str(item.get("digest", "")),
                api_download_url=str(api_download_url) if api_download_url else None,
                browser_download_url=browser_download_url,
            )
        )
        if api_download_url:
            access_checks.append(_check_url(str(api_download_url), timeout_s=timeout_s))
        if browser_download_url:
            access_checks.append(_check_url(browser_download_url, timeout_s=timeout_s))
    return PublicDatasetManifest(
        source_key=source.key,
        title=source.title,
        primary_url=source.primary_url,
        data_access_url=source.metadata_url,
        access=source.access,
        version_id=version_id,
        dataset_metadata=dataset_metadata,
        files=tuple(files),
        access_checks=tuple(access_checks),
    )


def build_public_dataset_manifest(source_key: str, *, timeout_s: float = 30.0) -> PublicDatasetManifest:
    source_map = get_spontaneous_dataset_source_map()
    if source_key not in source_map:
        raise KeyError(f"Unknown spontaneous dataset source: {source_key}")
    source = source_map[source_key]
    if source.key == "aimon2023_dryad":
        return fetch_dryad_manifest(source, timeout_s=timeout_s)
    return PublicDatasetManifest(
        source_key=source.key,
        title=source.title,
        primary_url=source.primary_url,
        data_access_url=source.metadata_url,
        access=source.access,
        version_id=None,
        dataset_metadata=source.to_dict(),
        files=tuple(),
        access_checks=tuple(),
    )


def write_public_dataset_manifest(manifest: PublicDatasetManifest, output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest.to_dict(), indent=2), encoding="utf-8")


def normalize_dryad_file_listing(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    files = payload.get("_embedded", {}).get("stash:files", [])
    rows: list[dict[str, Any]] = []
    for item in files:
        rows.append(
            {
                "file_id": int(item.get("id")),
                "path": str(item.get("path", "")),
                "size_bytes": int(item.get("size")) if item.get("size") is not None else None,
                "digest": str(item.get("digest", "")),
                "mime_type": str(item.get("mimeType", "")),
                "api_download_url": _resolve_dryad_href(item.get("_links", {}).get("stash:download", {}).get("href")),
            }
        )
    return rows


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


def _zenodo_api_content_url(url: str | None) -> str | None:
    raw = str(url or "").strip()
    if not raw:
        return None
    match = re.match(r"^https://zenodo\.org/records/(\d+)/files/([^?]+)(?:\?download=1)?$", raw)
    if not match:
        return None
    record_id = match.group(1)
    filename = match.group(2)
    return f"https://zenodo.org/api/records/{record_id}/files/{filename}/content"


def _candidate_download_urls(url: str | None) -> list[str]:
    raw = str(url or "").strip()
    if not raw:
        return []
    api_url = _zenodo_api_content_url(raw)
    urls: list[str] = []
    if api_url:
        urls.append(api_url)
    urls.append(raw)
    return urls


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
        stderr = completed.stderr.strip()
        raise RuntimeError(f"curl failed with code {completed.returncode}: {stderr}")


def stage_public_dataset_file(
    dataset_key: str,
    file_name: str,
    *,
    root_dir: str | Path | None = None,
    timeout_s: float = 120.0,
) -> dict[str, Any]:
    source_map = get_spontaneous_dataset_source_map()
    if dataset_key not in source_map:
        raise KeyError(f"Unknown spontaneous dataset key: {dataset_key}")
    source = source_map[dataset_key]
    try:
        entry = next(item for item in source.files if item.name == file_name)
    except StopIteration as exc:
        raise KeyError(f"Unknown file for dataset {dataset_key}: {file_name}") from exc
    dataset_root = Path(root_dir or source.expected_local_dir)
    dataset_root.mkdir(parents=True, exist_ok=True)
    output_path = dataset_root / entry.name
    expected_algorithm = _infer_digest_algorithm(entry.md5)
    if output_path.exists():
        existing_size = int(output_path.stat().st_size)
        digest_match = None
        actual_digest = None
        if expected_algorithm and entry.md5:
            actual_digest = _compute_file_digest(output_path, algorithm=expected_algorithm)
            digest_match = actual_digest.lower() == str(entry.md5).lower()
        if (entry.size_bytes is None or existing_size == int(entry.size_bytes)) and (digest_match is not False):
            return {
                "dataset_key": dataset_key,
                "file_name": file_name,
                "path": str(output_path),
                "status": "already_valid",
                "size_bytes": existing_size,
                "expected_size_bytes": entry.size_bytes,
                "actual_digest": actual_digest,
                "expected_digest": entry.md5,
                "zip_valid": _zip_integrity_ok(output_path),
            }
    if not entry.primary_download_url:
        raise ValueError(f"No download URL available for {dataset_key}:{file_name}")
    download_error = None
    tmp_path = output_path.with_suffix(output_path.suffix + ".download")
    for candidate_url in _candidate_download_urls(entry.primary_download_url):
        try:
            _download_with_curl(candidate_url, tmp_path, timeout_s=timeout_s)
        except Exception as curl_exc:  # noqa: BLE001
            download_error = f"curl={type(curl_exc).__name__}: {curl_exc}"
            try:
                _download_with_urlopen(candidate_url, tmp_path, timeout_s=timeout_s)
            except Exception as exc:  # noqa: BLE001
                download_error = (
                    f"curl={type(curl_exc).__name__}: {curl_exc}; "
                    f"urlopen={type(exc).__name__}: {exc}"
                )
                if tmp_path.exists():
                    tmp_path.unlink(missing_ok=True)
                continue
        try:
            actual_size = int(tmp_path.stat().st_size)
            if entry.size_bytes is not None and actual_size != int(entry.size_bytes):
                raise ValueError(f"downloaded size mismatch for {file_name}: {actual_size} != {entry.size_bytes}")
            actual_digest = None
            if expected_algorithm and entry.md5:
                actual_digest = _compute_file_digest(tmp_path, algorithm=expected_algorithm)
                if actual_digest.lower() != str(entry.md5).lower():
                    raise ValueError(f"digest mismatch for {file_name}")
            tmp_path.replace(output_path)
            return {
                "dataset_key": dataset_key,
                "file_name": file_name,
                "path": str(output_path),
                "status": "downloaded",
                "source_url": candidate_url,
                "size_bytes": actual_size,
                "expected_size_bytes": entry.size_bytes,
                "actual_digest": actual_digest,
                "expected_digest": entry.md5,
                "zip_valid": _zip_integrity_ok(output_path),
            }
        except Exception as exc:  # noqa: BLE001
            download_error = f"{type(exc).__name__}: {exc}"
        finally:
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)
    raise RuntimeError(f"Failed to stage {dataset_key}:{file_name}: {download_error}")


def parse_aimon2023_readme(readme_text: str) -> dict[str, Any]:
    summary_metrics: dict[str, str] = {}
    metric_pattern = re.compile(r"^\*\s+(?P<key>[^:]+):\s*(?P<value>.+?)\s*$")
    file_blocks = re.finditer(
        r"Details for:\s*(?P<name>[^\n]+)\n[-]+\n(?P<body>.*?)(?=\nDetails for:|\Z)",
        readme_text,
        flags=re.DOTALL,
    )
    in_summary = False
    for raw_line in readme_text.splitlines():
        line = raw_line.strip()
        if line == "Summary Metrics":
            in_summary = True
            continue
        if in_summary and not line:
            in_summary = False
            continue
        if in_summary:
            match = metric_pattern.match(line)
            if match:
                summary_metrics[str(match.group("key")).strip()] = str(match.group("value")).strip()

    file_details: list[dict[str, str]] = []
    for match in file_blocks:
        body = match.group("body")
        description_match = re.search(r"\*\s*Description:\s*(.+)", body)
        format_match = re.search(r"\*\s*Format\(s\):\s*(.+)", body)
        size_match = re.search(r"\*\s*Size\(s\):\s*(.+)", body)
        file_details.append(
            {
                "name": str(match.group("name")).strip(),
                "description": str(description_match.group(1)).strip() if description_match else "",
                "formats": str(format_match.group(1)).strip() if format_match else "",
                "declared_size": str(size_match.group(1)).strip() if size_match else "",
            }
        )
    return {
        "summary_metrics": summary_metrics,
        "file_details": file_details,
    }


def summarize_goodics_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    def _non_empty_count(column: str) -> int:
        if column not in df.columns:
            return 0
        series = df[column]
        mask = series.notna()
        if mask.any():
            mask &= series.astype(str).str.strip().ne("")
        return int(mask.sum())

    summary = {
        "rows": int(len(df)),
        "unique_fly_ids": int(df["FlyID"].nunique()) if "FlyID" in df.columns else 0,
        "unique_exp_ids": int(df["expID"].nunique()) if "expID" in df.columns else 0,
        "unique_gal4_lines": int(df["GAL4"].nunique()) if "GAL4" in df.columns else 0,
        "unique_uas_lines": int(df["UAS"].nunique()) if "UAS" in df.columns else 0,
        "walk_regressor_rows": _non_empty_count("WalkRegressor"),
        "turn_regressor_rows": _non_empty_count("TurnRegressor"),
        "forced_walk_regressor_rows": _non_empty_count("ForcedWalkRegressor"),
        "forced_turn_regressor_rows": _non_empty_count("ForcedTurnRegressor"),
        "top_gal4_lines": {},
        "top_walk_substrates": {},
    }
    if "GAL4" in df.columns:
        summary["top_gal4_lines"] = {
            str(key): int(value)
            for key, value in df["GAL4"].fillna("UNKNOWN").astype(str).value_counts().head(10).items()
        }
    if "WalkSubstrate" in df.columns:
        summary["top_walk_substrates"] = {
            str(key): int(value)
            for key, value in df["WalkSubstrate"].fillna("UNKNOWN").astype(str).value_counts().head(10).items()
        }
    return summary


def inspect_local_spontaneous_dataset(dataset_key: str, *, root_dir: str | Path | None = None) -> dict[str, Any]:
    source_map = get_spontaneous_dataset_source_map()
    if dataset_key not in source_map:
        raise KeyError(f"Unknown spontaneous dataset key: {dataset_key}")
    source = source_map[dataset_key]
    dataset_root = Path(root_dir or source.expected_local_dir)
    file_rows = []
    for entry in source.files:
        path = dataset_root / entry.name
        actual_digest = None
        digest_algorithm = _infer_digest_algorithm(entry.md5)
        digest_match = None
        if path.exists() and digest_algorithm and entry.md5:
            actual_digest = _compute_file_digest(path, algorithm=digest_algorithm)
            digest_match = actual_digest.lower() == str(entry.md5).lower()
        file_rows.append(
            {
                "name": entry.name,
                "exists": path.exists(),
                "size_bytes": int(path.stat().st_size) if path.exists() else None,
                "expected_size_bytes": entry.size_bytes,
                "expected_digest": entry.md5,
                "actual_digest": actual_digest,
                "digest_algorithm": digest_algorithm,
                "digest_match": digest_match,
                "zip_valid": _zip_integrity_ok(path),
                "primary_download_url": entry.primary_download_url,
            }
        )
    payload = {
        "dataset": source.to_dict(),
        "root_dir": str(dataset_root),
        "files": file_rows,
    }
    readme_path = dataset_root / "README.md"
    if readme_path.exists():
        payload["readme_summary"] = parse_aimon2023_readme(readme_path.read_text(encoding="utf-8"))
    goodics_path = dataset_root / "GoodICsdf.pkl"
    if goodics_path.exists():
        payload["goodics_summary"] = summarize_goodics_dataframe(pd.read_pickle(goodics_path))
    return payload


def dataset_file_status_table(payload: Mapping[str, Any]) -> pd.DataFrame:
    table = pd.DataFrame(payload.get("files", []))
    if table.empty:
        return pd.DataFrame(
            columns=[
                "name",
                "exists",
                "size_bytes",
                "expected_size_bytes",
                "digest_match",
                "zip_valid",
                "primary_download_url",
            ]
        )
    return table[
        [
            "name",
            "exists",
            "size_bytes",
            "expected_size_bytes",
            "digest_match",
            "zip_valid",
            "primary_download_url",
        ]
    ].copy()


def write_public_dataset_summary(
    dataset_key: str,
    *,
    output_path: str | Path,
    root_dir: str | Path | None = None,
) -> dict[str, Any]:
    payload = inspect_local_spontaneous_dataset(dataset_key, root_dir=root_dir)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def public_dataset_note_lines(payload: Mapping[str, Any]) -> list[str]:
    source = payload.get("dataset", {})
    lines = [
        f"Dataset: {source.get('citation_label', source.get('title', 'unknown'))}",
        f"Access: {source.get('access', 'unknown')}",
        f"Root dir: {payload.get('root_dir', '')}",
    ]
    readme_summary = payload.get("readme_summary", {})
    if readme_summary:
        summary_metrics = readme_summary.get("summary_metrics", {})
        file_count = summary_metrics.get("File count")
        total_size = summary_metrics.get("Total file size")
        if file_count or total_size:
            lines.append(f"README summary: file_count={file_count or 'unknown'}, total_size={total_size or 'unknown'}")
    goodics_summary = payload.get("goodics_summary", {})
    if goodics_summary:
        lines.append(
            "GoodICs summary: "
            f"rows={goodics_summary.get('rows', 0)}, "
            f"unique_exp_ids={goodics_summary.get('unique_exp_ids', 0)}, "
            f"unique_gal4_lines={goodics_summary.get('unique_gal4_lines', 0)}"
        )
    return lines
