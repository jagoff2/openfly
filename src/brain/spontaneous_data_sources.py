from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class SpontaneousDatasetFile:
    name: str
    size_bytes: int | None
    description: str
    primary_download_url: str | None = None
    md5: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SpontaneousDatasetSource:
    key: str
    title: str
    citation_label: str
    scope: str
    access: str
    primary_url: str
    metadata_url: str
    notes: str
    expected_local_dir: str
    files: tuple[SpontaneousDatasetFile, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["files"] = [entry.to_dict() for entry in self.files]
        return payload

    @property
    def api_dataset_url(self) -> str:
        return self.metadata_url


SPONTANEOUS_DATASET_SOURCES: tuple[SpontaneousDatasetSource, ...] = (
    SpontaneousDatasetSource(
        key="aimon2023_dryad",
        title="Global change in brain state during spontaneous and forced walk in Drosophila",
        citation_label="Aimon et al. 2023 eLife / Dryad",
        scope=(
            "Fast whole-brain light-field imaging with walk- and turn-linked regressors, "
            "regional timeseries, PCA/ICA component timeseries, and experiment metadata."
        ),
        access="public metadata plus browser-downloadable data files",
        primary_url="https://datadryad.org/dataset/doi:10.5061/dryad.3bk3j9kpb",
        metadata_url="https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.3bk3j9kpb",
        notes=(
            "Dryad exposes version/file metadata publicly through the JSON API. Direct scripted file download "
            "from Dryad is inconsistent because file-stream endpoints may trigger anti-bot validation. The same "
            "record is mirrored on Zenodo with stable public file URLs."
        ),
        expected_local_dir="external/spontaneous/aimon2023_dryad",
        files=(
            SpontaneousDatasetFile(
                name="README.md",
                size_bytes=4917,
                description="Dataset structure and file-level description.",
                primary_download_url="https://zenodo.org/records/7849014/files/README.md?download=1",
                md5="639569d783c0611da52ace054c5a573775efc92699a4713090e02a661cc55553",
            ),
            SpontaneousDatasetFile(
                name="GoodICsdf.pkl",
                size_bytes=240944,
                description="Pandas experiment/component metadata used to interpret the walk component files.",
                primary_download_url="https://zenodo.org/records/7849014/files/GoodICsdf.pkl?download=1",
                md5="c03572c270b333aef2f4ec645f400c868e5a4c78d2d65f623b1871be88eacbd5",
            ),
            SpontaneousDatasetFile(
                name="Walk_anatomical_regions.zip",
                size_bytes=176088991,
                description="Regional calcium timeseries and walk/turn regressors for Fig. 1-3, 6SA, 7A.",
                primary_download_url="https://zenodo.org/records/7849014/files/Walk_anatomical_regions.zip?download=1",
                md5="14039b2ab1a689e58b08324747daf275b8555837395df1951c7528ab3f8d4a91",
            ),
            SpontaneousDatasetFile(
                name="Walk_components.zip",
                size_bytes=186935529,
                description="PCA/ICA component timeseries and walk/turn regressors for Fig. 4-7.",
                primary_download_url="https://zenodo.org/records/7849014/files/Walk_components.zip?download=1",
                md5="b557b4d267e8d926da4d21a51dc7b311fbd48cd68daa318243ae6d216f12d176",
            ),
            SpontaneousDatasetFile(
                name="Additional_data.zip",
                size_bytes=599364517,
                description="Additional masks, regressors, and less-curated figure-side data.",
                primary_download_url="https://zenodo.org/records/7849014/files/Additional_data.zip?download=1",
                md5="fd96bc47ee8761bb5f2704c616708855c11bc5a05ef2ecb2d1d7b2dd87436631",
            ),
        ),
    ),
    SpontaneousDatasetSource(
        key="aimon2019_crcns_fly1",
        title="Whole-brain recordings of adult Drosophila using light field microscopy along with corresponding behavior or stimuli data",
        citation_label="Aimon et al. 2019 CRCNS fly-1",
        scope=(
            "Adult whole-brain calcium or voltage recordings with behavior or stimulus traces, "
            "including spontaneous walk/groom and stimulus conditions."
        ),
        access="public metadata, account-gated download",
        primary_url="https://crcns.org/data-sets/ia/fly-1/about-fly-1",
        metadata_url="https://crcns.org/data-sets/ia/fly-1/about-fly-1",
        notes=(
            "Metadata, documentation, and the NERSC download endpoint are public. The actual dataset download "
            "requires a CRCNS.org account."
        ),
        expected_local_dir="external/spontaneous/aimon2019_crcns_fly1",
        files=(
            SpontaneousDatasetFile(
                name="crcns_fly-1_data_description.pdf",
                size_bytes=None,
                description="Dataset description document linked from the CRCNS about page.",
                primary_download_url=None,
                md5=None,
            ),
        ),
    ),
    SpontaneousDatasetSource(
        key="mann2017_intrinsic_network",
        title="Whole-Brain Calcium Imaging Reveals an Intrinsic Functional Network in Drosophila",
        citation_label="Mann et al. 2017 Current Biology",
        scope="Intrinsic-network and resting-state whole-brain spontaneous functional organization.",
        access="public paper / supplementary evidence",
        primary_url="https://pmc.ncbi.nlm.nih.gov/articles/PMC5967399/",
        metadata_url="https://pmc.ncbi.nlm.nih.gov/articles/PMC5967399/",
        notes=(
            "Primary literature anchor for intrinsic-network mesoscale coupling when downloadable "
            "whole-brain matrices are not yet ingested locally."
        ),
        expected_local_dir="external/spontaneous/mann2017_intrinsic_network",
    ),
    SpontaneousDatasetSource(
        key="turner2021_resting_fc",
        title="The connectome predicts resting-state functional connectivity across the Drosophila brain",
        citation_label="Turner et al. 2021 Current Biology",
        scope="Structure-function relationship for resting-state mesoscale coupling.",
        access="public paper / supplementary evidence",
        primary_url="https://pubmed.ncbi.nlm.nih.gov/33770490/",
        metadata_url="https://pubmed.ncbi.nlm.nih.gov/33770490/",
        notes="Primary literature anchor for family- and region-level structure-function correspondence.",
        expected_local_dir="external/spontaneous/turner2021_resting_fc",
    ),
    SpontaneousDatasetSource(
        key="schaffer2023_residual_dynamics",
        title="The spatial and temporal structure of neural activity across the fly brain",
        citation_label="Schaffer et al. 2023 Nature Neuroscience",
        scope="Residual high-dimensional spontaneous dynamics after regressing behavior.",
        access="public paper / supplementary evidence",
        primary_url="https://pubmed.ncbi.nlm.nih.gov/37696814/",
        metadata_url="https://pubmed.ncbi.nlm.nih.gov/37696814/",
        notes="Primary literature anchor for residual, sparse, structured mesoscale activity.",
        expected_local_dir="external/spontaneous/schaffer2023_residual_dynamics",
    ),
)


def get_spontaneous_dataset_sources() -> list[SpontaneousDatasetSource]:
    return list(SPONTANEOUS_DATASET_SOURCES)


def get_spontaneous_dataset_source_map() -> dict[str, SpontaneousDatasetSource]:
    return {source.key: source for source in SPONTANEOUS_DATASET_SOURCES}
