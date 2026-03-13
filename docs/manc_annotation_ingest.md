# MANC Annotation Ingest

This document records the first real public VNC annotation ingest performed in
the repo.

## Source file

- Local file:
  - `external/vnc/manc/body-annotations-male-cns-v0.9-minconf-0.5.feather`
- Official source page:
  - https://male-cns.janelia.org/download/
- Direct download URL used:
  - `https://storage.googleapis.com/flyem-male-cns/v0.9/connectome-data/flat-connectome/body-annotations-male-cns-v0.9-minconf-0.5.feather`

## What was done

1. Download the public MANC annotation feather locally.
2. Extend the VNC atlas and typed-node ingest code so `.feather` files are supported.
3. Add schema normalization for MANC-native columns such as:
   - `bodyId`
   - `superclass`
   - `class`
   - `type`
   - `rootSide`
   - `somaSide`
   - `somaNeuromere`
4. Run the existing atlas tool on the real file.
5. Emit a compact normalized node summary.

## Artifacts

- Real atlas:
  - `outputs/metrics/vnc_annotation_atlas_manc_v0p9.json`
  - `outputs/metrics/vnc_annotation_atlas_manc_v0p9.csv`
- Normalized node summary:
  - `outputs/metrics/vnc_manc_annotation_node_summary.json`

## Observed scale

- Rows loaded: `211743`
- Canonical super-class counts:
  - `interneuron`: `134722`
  - `sensory`: `27153`
  - `ascending`: `2392`
  - `descending`: `1332`
  - `motor`: `933`
- Canonical flow counts:
  - `intrinsic`: `134884`
  - `afferent`: `29545`
  - `efferent`: `2265`

## Important limitations in the first ingest

- The file is annotation-only. It does not yet provide the graph edges needed
  for pathway inventory or structural-spec compilation on real public data.
- Many rows are still missing `region`, `superclass`, or `type`, so the atlas
  shows a large `<missing>` bucket. That is expected for a first raw annotation
  ingest and should be handled explicitly rather than hidden.
- `region` is currently normalized from `somaNeuromere`, which is useful for a
  first atlas but is not the full ROI story.

## Why this matters

This is the first point where the VNC workstream stopped being fixture-only.
The repo can now:

- load a real public VNC annotation export
- normalize it into the repo's canonical node vocabulary
- produce real atlas artifacts from public MANC data

The next honest step is the corresponding real edge ingest, not another mocked
structural-spec example.
