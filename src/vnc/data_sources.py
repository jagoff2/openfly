from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class VNCDatasetSource:
    key: str
    title: str
    organism: str
    sex: str
    scope: str
    access: str
    primary_url: str
    data_access_url: str
    notes: str
    recommended_first_ingest: str
    recommended_first_exports: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


VNC_DATASET_SOURCES: tuple[VNCDatasetSource, ...] = (
    VNCDatasetSource(
        key="manc",
        title="Male Adult Nerve Cord (MANC)",
        organism="Drosophila melanogaster",
        sex="male",
        scope="complete adult ventral nerve cord connectome with rich annotations",
        access="public",
        primary_url="https://www.janelia.org/project-team/flyem/manc-connectome",
        data_access_url="https://www.janelia.org/project-team/flyem/manc-connectome",
        notes=(
            "Janelia states that MANC is a complete, extensively annotated adult VNC connectome "
            "with neuPrint access, registration transforms, flat-file downloads, and neurotransmitter predictions."
        ),
        recommended_first_ingest=(
            "Cell annotations and metadata exports first; full edge list second; raw meshes and EM imagery later."
        ),
        recommended_first_exports=(
            "body-annotations-male-cns-v0.9-minconf-0.5.feather",
            "body-neurotransmitters-male-cns-v0.9.feather",
            "connectome-weights-male-cns-v0.9-minconf-0.5.feather",
        ),
    ),
    VNCDatasetSource(
        key="fanc",
        title="Female Adult Nerve Cord (FANC)",
        organism="Drosophila melanogaster",
        sex="female",
        scope="female adult ventral nerve cord TEM dataset and collaborative reconstructions",
        access="mixed",
        primary_url="https://connectomics.hms.harvard.edu/adult-drosophila-vnc-tem-dataset-female-adult-nerve-cord-fanc",
        data_access_url="https://flyconnectome.github.io/fancr/",
        notes=(
            "Harvard lists FANC as the female adult nerve cord TEM dataset with reconstructions available through "
            "Virtual Fly Brain. Programmatic fancr access exists, but parts of the autosegmentation workflow require authorization."
        ),
        recommended_first_ingest=(
            "Public reconstruction / annotation exports first; treat protected autosegmentation paths as optional."
        ),
        recommended_first_exports=(
            "published SWC reconstructions from htem/GridTape_VNC_paper",
            "public reconstruction and annotation exports from the HMS FANC project page",
        ),
    ),
    VNCDatasetSource(
        key="banc",
        title="Brain And Nerve Cord (BANC)",
        organism="Drosophila melanogaster",
        sex="female",
        scope="unified brain-and-VNC connectome across the full central nervous system",
        access="public-tooling plus evolving dataset release",
        primary_url="https://flyconnectome.github.io/bancr/",
        data_access_url="https://github.com/jasper-tms/the-BANC-fly-connectome",
        notes=(
            "The public bancr tooling describes BANC as the first unified brain-and-nerve-cord connectome with ~160k neurons, "
            "official Codex annotations, community annotations, and full edge-list access."
        ),
        recommended_first_ingest=(
            "Official Codex annotations first, then descending/ascending/VNC edge subsets, then broader embodied pathway slices."
        ),
        recommended_first_exports=(
            "Supplementary Data 4 (AN/DN clusters)",
            "Supplementary Data 5 (effector clusters)",
            "media-1.zip / official supplementary bundle",
            "Dataverse DOI 10.7910/DVN/8TFGGB",
        ),
    ),
)


def get_vnc_dataset_sources() -> list[VNCDatasetSource]:
    return list(VNC_DATASET_SOURCES)


def get_vnc_dataset_source_map() -> dict[str, VNCDatasetSource]:
    return {source.key: source for source in VNC_DATASET_SOURCES}
