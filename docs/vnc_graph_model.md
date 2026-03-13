# VNC Graph Model

The first executable VNC graph layer in this repo is intentionally simple.

It is not yet a simulator. It is a typed ingest and pathway inventory layer
for public annotation and edge exports.

## Current code

- `src/vnc/ingest.py`
- `src/vnc/pathways.py`
- `scripts/build_vnc_pathway_inventory.py`
- `tests/test_vnc_pathways.py`

## Current graph model

Nodes currently preserve:

- `root_id`
- `region`
- `flow`
- `super_class`
- `cell_class`
- `cell_type`
- `side`

Edges currently preserve:

- `pre_root_id`
- `post_root_id`
- `weight`

## Current inventory objective

The first pathway inventory is focused on the structural motif:

- descending -> premotor -> motor

That is not the full VNC story, but it is the first route that lets the repo
replace tiny sampled DN readouts with a broader, graph-grounded path toward a
future VNC-spec decoder.

## Why this is the right current abstraction

The repo is not ready for a whole-VNC dynamical emulator yet.

Before that, it needs:

1. typed public node/edge ingest
2. reproducible pathway extraction
3. test coverage
4. summary outputs that can be compared across MANC, FANC, and BANC exports

That is what this first graph layer provides.
