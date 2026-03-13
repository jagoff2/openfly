# VNC Data Sources

This document starts the explicit VNC-wide workstream for the repo.

The purpose is not to pretend that the repo already has a solved full
brain-to-VNC-to-muscle reconstruction. The purpose is to ground the next phase
in public datasets that are large enough to replace the current tiny sampled
descending readouts with something closer to a full ventral nerve cord spec.

## Public sources selected for first ingest

### 1. MANC

- Source: https://www.janelia.org/project-team/flyem/manc-connectome
- Download portal: https://male-cns.janelia.org/download/
- Why it matters:
  - Janelia describes MANC as a complete, extensively annotated adult ventral
    nerve cord connectome.
  - It includes rich annotation, neuPrint access, neurotransmitter
    predictions, and flat-file downloads.
  - It is the most direct public starting point for a VNC-first workstream.
- First ingest target:
  - `body-annotations-male-cns-v0.9-minconf-0.5.feather`
  - then `body-neurotransmitters-male-cns-v0.9.feather`
  - then `connectome-weights-male-cns-v0.9-minconf-0.5.feather`
- Why this exact target comes first:
  - it is a public flat file rather than a gated query path
  - it is small enough to use as the first real local normalization target
  - it should expose the controlled vocabulary needed for descending /
    premotor / motor typing before the repo touches a full edge dump
- Constraint:
  - neuPrint query access exists, but token-gated query paths are not the first
    ingest target for this repo

### 2. FANC

- Source: https://connectomics.hms.harvard.edu/adult-drosophila-vnc-tem-dataset-female-adult-nerve-cord-fanc
- Programmatic tooling: https://flyconnectome.github.io/fancr/
- Public reconstruction repo: https://github.com/htem/GridTape_VNC_paper
- Why it matters:
  - FANC is the main public female adult nerve cord resource.
  - It gives a female comparison point for premotor and motor organization.
- First ingest target:
  - published SWC reconstructions from `htem/GridTape_VNC_paper`
  - then public reconstruction / annotation exports from the HMS project page
- Constraint:
  - some programmatic access paths are authorization-gated
  - so the repo should treat public reconstruction / annotation exports as the
    default ingest path and protected autosegmentation as optional

### 3. BANC

- Source: https://flyconnectome.github.io/bancr/
- Code/tooling: https://github.com/jasper-tms/the-BANC-fly-connectome
- Paper / supplement entry: https://pmc.ncbi.nlm.nih.gov/articles/PMC12324551/
- Dataverse DOI: https://doi.org/10.7910/DVN/8TFGGB
- Why it matters:
  - BANC is the first unified brain-and-nerve-cord connectome of an adult fly
    central nervous system.
  - This is the cleanest public route to replacing the current brain-side
    sampled DN decoder with a broader brain+VNC pathway analysis.
- First ingest target:
  - `Supplementary Data 4` for AN/DN clusters
  - `Supplementary Data 5` for effector clusters
  - `media-1.zip` / official supplementary bundle
  - then Dataverse exports under `10.7910/DVN/8TFGGB`
- Constraint:
  - Codex is useful, but interactive server-side access is not the first repo
    ingest path because it is more operationally brittle than paper and
    Dataverse exports

## What the repo should ingest first

The first VNC ingest should not be meshes or raw EM volumes.

The current evidence-backed ingest order is:

1. MANC annotation feather
2. MANC neurotransmitter feather
3. BANC supplementary annotation tables
4. BANC edge-compatible exports
5. FANC public reconstructions

The repo tooling is now ready for the first MANC step at the file-format level:

- `src/vnc/annotation_atlas.py` reads `.feather`
- `src/vnc/ingest.py` reads `.feather`

That means the remaining blocker for `MANC` is the actual local file ingest,
not a missing parser.

That still means the repo should ingest:

1. annotation exports
2. controlled-vocabulary metadata
3. edge lists or adjacency slices
4. laterality and region labels
5. descending / premotor / motor / ascending typing

That is enough to build:

- a VNC atlas
- a VNC pathway inventory
- a first structural VNC spec candidate

before any expensive full-graph local processing.

## New repo scaffolding

This workstream now has initial code support under:

- `src/vnc/data_sources.py`
- `src/vnc/annotation_atlas.py`
- `scripts/build_vnc_annotation_atlas.py`
- `tests/test_vnc_annotation_atlas.py`

These files do not solve the VNC problem. They create the first executable
scaffolding for turning public VNC annotations into a repo-local atlas.
