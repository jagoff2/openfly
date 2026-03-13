# VNC Workstream Plan

This document starts the explicit transition from a sparse descending readout
decoder toward a broader VNC-wide control specification.

## Why this workstream exists

The current embodied branch is still bottlenecked by a small sampled output
decoder. The repo already documents that it does not yet implement a full
neck-connective, VNC, motor-neuron, and muscle pathway.

That means the next serious step is not another blind DN gain sweep.

It is:

- ingest public VNC-scale data
- build a typed VNC graph
- map descending-to-premotor-to-motor pathways
- derive a larger structural control spec from that graph

## Immediate milestones

### Milestone 1: VNC source registry and annotation atlas

Deliverables:

- `src/vnc/data_sources.py`
- `src/vnc/annotation_atlas.py`
- `scripts/build_vnc_annotation_atlas.py`
- `tests/test_vnc_annotation_atlas.py`
- `docs/vnc_data_sources.md`

Goal:

- make public VNC resources explicit
- create an executable path from annotation export to repo-local atlas summary

### Milestone 2: Typed VNC graph ingest

Planned deliverables:

- `src/vnc/graph_ingest.py`
- `scripts/build_vnc_graph_slice.py`
- `outputs/metrics/vnc_*`
- `docs/vnc_graph_model.md`

Goal:

- ingest edge slices plus annotation metadata
- preserve:
  - region
  - side
  - flow
  - super_class
  - cell_class
  - cell_type

### Milestone 3: Descending-to-motor pathway inventory

Planned deliverables:

- `src/vnc/pathways.py`
- `scripts/build_vnc_pathway_inventory.py`
- `outputs/metrics/vnc_pathway_inventory.*`
- `docs/vnc_pathway_inventory.md`

Goal:

- identify public structural routes from brain descending classes into:
  - premotor populations
  - motor neuron groups
  - local VNC modules

### Milestone 4: VNC-spec decoder candidate

Current deliverables:

- `src/vnc/spec_builder.py`
- `src/vnc/spec_decoder.py`
- `src/bridge/decoder_factory.py`
- `scripts/build_vnc_structural_spec.py`
- `tests/test_vnc_spec_decoder.py`
- `docs/vnc_spec_decoder.md`

Remaining deliverables:

- `configs/*vnc*`
- real public-data-backed spec artifacts
- selective real-slice decoder benchmark artifacts

Goal:

- replace tiny sampled DN populations with a broader structural decoder basis
- compare that basis against the current neck-output fitted decoder

Current gate after `T110`:

- the real MANC selective-slice comparison now favors the `exit_nerve` thoracic
  motor endpoint over the broader `leg_subclass` slice
- the next practical step is to benchmark the real `exit_nerve` structural spec
  as the first production decoder candidate
- do not skip directly to embodied sweeps for the broader baseline slice now
  that a cleaner endpoint exists

Current blocker after `T111`:

- the benchmark is now done, but the real MANC structural spec and the current
  FlyWire whole-brain backend live in different ID spaces
- the short real benchmark completed as a silent no-op because the decoder asked
  for `736` IDs and the backend matched `0`
- see `docs/vnc_exit_nerve_decoder_validation.md` and
  `outputs/metrics/t111_decoder_id_alignment_comparison.json`

Current state after `T112`:

- the ID-space blocker is now resolved by an explicit semantic bridge into the
  FlyWire monitor space
- the bridged decoder uses exact shared `cell_type + side` plus key-level
  `hemibrain_type` fallback, filtered to the live v783 backend completeness
  table
- the live bridged config now requests `685` IDs and matches `685`
- the first short real bridged run is no longer silent and produced nonzero
  commands on `43 / 50` cycles
- the next blocker is calibration, not monitor-space compatibility

See:

- `docs/vnc_flywire_semantic_bridge.md`
- `outputs/metrics/t112_decoder_id_alignment_comparison.json`
- `outputs/metrics/t112_exit_nerve_flywire_semantic_summary.json`

## What not to do next

Do not:

- keep piling hand-authored heuristics on top of `DNae002` / `DNpe016`
- claim a full biological VNC implementation from connectivity alone
- jump straight to raw EM volume processing
- run expensive embodied sweeps before the structural VNC graph is explicit

## Acceptance standard for this workstream

This VNC workstream is only useful if it produces:

- public-source-grounded data lineage
- executable ingest scripts
- tests
- atlas outputs
- pathway summaries
- a benchmarked replacement candidate for the current sparse output decoder
