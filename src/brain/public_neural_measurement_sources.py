from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class PublicNeuralMeasurementFile:
    name: str
    size_bytes: int | None
    description: str
    primary_download_url: str | None = None
    digest: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PublicNeuralMeasurementSource:
    key: str
    title: str
    citation_label: str
    scope: str
    access: str
    repository_kind: str
    primary_url: str
    metadata_url: str
    expected_local_dir: str
    notes: str
    doi: str | None = None
    files: tuple[PublicNeuralMeasurementFile, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["files"] = [entry.to_dict() for entry in self.files]
        return payload


PUBLIC_NEURAL_MEASUREMENT_SOURCES: tuple[PublicNeuralMeasurementSource, ...] = (
    PublicNeuralMeasurementSource(
        key="aimon2023_dryad",
        title="Global change in brain state during spontaneous and forced walk in Drosophila",
        citation_label="Aimon et al. 2023 eLife / Dryad",
        scope=(
            "Fast whole-brain light-field imaging with spontaneous and forced walking, "
            "regional timeseries, PCA/ICA component timeseries, and walk/turn regressors."
        ),
        access="public metadata plus browser-downloadable data files",
        repository_kind="dryad",
        primary_url="https://datadryad.org/dataset/doi:10.5061/dryad.3bk3j9kpb",
        metadata_url="https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.3bk3j9kpb",
        expected_local_dir="external/spontaneous/aimon2023_dryad",
        doi="10.5061/dryad.3bk3j9kpb",
        notes=(
            "Primary whole-brain spontaneous/forced-walking fit source. This repo already has a "
            "validated staging path and local copy under external/spontaneous/aimon2023_dryad."
        ),
        files=(
            PublicNeuralMeasurementFile(
                name="README.md",
                size_bytes=4917,
                description="Dataset structure and file-level description.",
                primary_download_url="https://zenodo.org/records/7849014/files/README.md?download=1",
                digest="639569d783c0611da52ace054c5a573775efc92699a4713090e02a661cc55553",
            ),
            PublicNeuralMeasurementFile(
                name="GoodICsdf.pkl",
                size_bytes=240944,
                description="Experiment and component metadata.",
                primary_download_url="https://zenodo.org/records/7849014/files/GoodICsdf.pkl?download=1",
                digest="c03572c270b333aef2f4ec645f400c868e5a4c78d2d65f623b1871be88eacbd5",
            ),
            PublicNeuralMeasurementFile(
                name="Walk_anatomical_regions.zip",
                size_bytes=176088991,
                description="Regional calcium timeseries and walk/turn regressors.",
                primary_download_url="https://zenodo.org/records/7849014/files/Walk_anatomical_regions.zip?download=1",
                digest="14039b2ab1a689e58b08324747daf275b8555837395df1951c7528ab3f8d4a91",
            ),
            PublicNeuralMeasurementFile(
                name="Walk_components.zip",
                size_bytes=186935529,
                description="PCA/ICA component timeseries and walk/turn regressors.",
                primary_download_url="https://zenodo.org/records/7849014/files/Walk_components.zip?download=1",
                digest="b557b4d267e8d926da4d21a51dc7b311fbd48cd68daa318243ae6d216f12d176",
            ),
            PublicNeuralMeasurementFile(
                name="Additional_data.zip",
                size_bytes=599364517,
                description="Masks, regressors, and additional figure-side data.",
                primary_download_url="https://zenodo.org/records/7849014/files/Additional_data.zip?download=1",
                digest="fd96bc47ee8761bb5f2704c616708855c11bc5a05ef2ecb2d1d7b2dd87436631",
            ),
        ),
    ),
    PublicNeuralMeasurementSource(
        key="schaffer2023_figshare",
        title="The spatial and temporal structure of neural activity across the fly brain",
        citation_label="Schaffer et al. 2023 Figshare",
        scope="Whole-brain behaving-fly imaging with locomotor-state structure and residual dynamics.",
        access="public DOI-backed Figshare record",
        repository_kind="figshare",
        primary_url="https://doi.org/10.6084/m9.figshare.23749074",
        metadata_url="https://api.figshare.com/v2/articles/23749074",
        expected_local_dir="external/neural_measurements/schaffer2023_figshare",
        doi="10.6084/m9.figshare.23749074",
        notes="Whole-brain treadmill/walking fit target for residual dynamics beyond Aimon.",
    ),
    PublicNeuralMeasurementSource(
        key="ketkar2022_zenodo",
        title="Ketkar et al. 2022 visual neuron recordings",
        citation_label="Ketkar et al. 2022 Zenodo",
        scope="Identified early visual channel recordings and matched walking-ball behavior.",
        access="public DOI-backed Zenodo record",
        repository_kind="zenodo",
        primary_url="https://doi.org/10.5281/zenodo.6335347",
        metadata_url="https://zenodo.org/api/records/6335347",
        expected_local_dir="external/neural_measurements/ketkar2022_zenodo",
        doi="10.5281/zenodo.6335347",
        notes="Primary identified-neuron fit target for L1/L2/L3-like preprocessing.",
    ),
    PublicNeuralMeasurementSource(
        key="gruntman2019_janelia",
        title="Gruntman et al. 2019 T5 recordings",
        citation_label="Gruntman et al. 2019 Janelia",
        scope="Identified T5 motion recordings under controlled visual stimuli.",
        access="public DOI-backed Janelia dataset landing page",
        repository_kind="janelia",
        primary_url="https://doi.org/10.25378/janelia.c.4771805.v1",
        metadata_url="https://doi.org/10.25378/janelia.c.4771805.v1",
        expected_local_dir="external/neural_measurements/gruntman2019_janelia",
        doi="10.25378/janelia.c.4771805.v1",
        notes="Primary OFF-path motion-channel fit target for T5-like timing and TF tuning.",
    ),
    PublicNeuralMeasurementSource(
        key="shomar2025_dryad",
        title="Shomar et al. 2025 visual-to-locomotor channel dataset",
        citation_label="Shomar et al. 2025 Dryad",
        scope="Identified visual-to-locomotor channel recordings for downstream motion-to-locomotor coupling.",
        access="public DOI-backed Dryad record",
        repository_kind="dryad",
        primary_url="https://doi.org/10.5061/dryad.kkwh70sgw",
        metadata_url="https://doi.org/10.5061/dryad.kkwh70sgw",
        expected_local_dir="external/neural_measurements/shomar2025_dryad",
        doi="10.5061/dryad.kkwh70sgw",
        notes="Downstream identified-neuron fit target for visual-motion-to-locomotor transformations.",
    ),
    PublicNeuralMeasurementSource(
        key="dallmann2025_dryad",
        title="Dallmann et al. 2025 treadmill proprioceptive and feedback dataset",
        citation_label="Dallmann et al. 2025 Dryad",
        scope="Treadmill proprioceptive and ascending-feedback recordings relevant to body-brain coupling.",
        access="public DOI-backed Dryad record",
        repository_kind="dryad",
        primary_url="https://doi.org/10.5061/dryad.gqnk98t16",
        metadata_url="https://doi.org/10.5061/dryad.gqnk98t16",
        expected_local_dir="external/neural_measurements/dallmann2025_dryad",
        doi="10.5061/dryad.gqnk98t16",
        notes="Primary treadmill/body-feedback fit target for the spontaneous embodied branch.",
    ),
)


def get_public_neural_measurement_sources() -> list[PublicNeuralMeasurementSource]:
    return list(PUBLIC_NEURAL_MEASUREMENT_SOURCES)


def get_public_neural_measurement_source_map() -> dict[str, PublicNeuralMeasurementSource]:
    return {source.key: source for source in PUBLIC_NEURAL_MEASUREMENT_SOURCES}
