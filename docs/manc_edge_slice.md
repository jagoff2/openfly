# MANC Edge Slice

This document records the first real public edge-side work for the MANC VNC
pipeline.

## Goal

Do not try to push the full `151,871,794`-row MANC edge file through the small
fixture-oriented pathway code.

Instead:

- keep the real public edge file local
- filter early
- build the first biologically focused locomotor slice
- feed that filtered slice into the existing pathway and structural-spec code

## Real source file

- `external/vnc/manc/connectome-weights-male-cns-v0.9-minconf-0.5.feather`

Observed schema:

- `body_pre`
- `body_post`
- `weight`

## First slice choice

The first real-data slice is a strict thoracic locomotor slice:

- descending seeds:
  - canonical `super_class == descending`
  - known side
  - non-empty `cell_type`
- motor targets:
  - canonical `super_class == motor`
  - thoracic `region in {T1, T2, T3}`
  - known side
- premotor candidates:
  - canonical `super_class == interneuron`
  - `flow == intrinsic`
  - thoracic region
  - known side
  - selected structurally by real connections into thoracic motor neurons

This is the first real workaround for the fact that MANC annotations do not
appear to expose an explicit `premotor` class label in the public annotation
feather.

## New code

- `src/vnc/manc_slice.py`
- `src/vnc/ingest.py`
- `scripts/build_manc_thoracic_vnc_artifacts.py`

## Real first-pass artifacts

- `outputs/metrics/manc_thoracic_slice_summary.json`
- `outputs/metrics/manc_thoracic_pathway_inventory.json`
- `outputs/metrics/manc_thoracic_structural_spec.json`
- `outputs/metrics/manc_thoracic_slice_nodes.csv`
- `outputs/metrics/manc_thoracic_slice_edges.csv`
- `outputs/metrics/manc_thoracic_spec_overlap.json`

Observed first-pass scale on real MANC data:

- descending seeds: `1316`
- thoracic motor neurons: `516`
- promoted premotor candidates: `5474`
- selected nodes: `7291`
- selected edges: `228061`
- `descending -> premotor` edges: `124181`
- `premotor -> motor` edges: `90463`
- `descending -> motor` edges: `13417`
- two-step `descending -> premotor -> motor` paths: `2440537`

The resulting structural spec contains `1301` descending channels.

## First stability check

A stricter rerun using:

- `min_premotor_total_weight = 200`
- `min_premotor_motor_targets = 10`

produced:

- premotor candidates: `2164`
- selected nodes: `3977`
- selected edges: `121268`
- structural descending channels: `1297`

Comparison artifact:

- `outputs/metrics/manc_thoracic_slice_comparison.json`

This matters because the descending structural coverage barely moved while the
premotor candidate pool shrank substantially. That suggests the real MANC
thoracic spec is not purely an artifact of the loosest first threshold choice.

## Selective slice variants

The next `T110` step was to stop tuning only premotor thresholds and make the
motor endpoint itself more biologically selective.

Two selective motor-target rules now exist in
`src/vnc/manc_slice.py` and the CLI:

- `motor_target_mode = leg_subclass`
  - keep only thoracic motors with canonical subclasses `fl`, `ml`, `hl`
  - these are the clean foreleg / midleg / hindleg motor pools in the local
    MANC annotation file
- `motor_target_mode = exit_nerve`
  - keep only thoracic motors whose `exitNerve` is one of:
    - `ProLN`
    - `MesoLN`
    - `MetaLN`
  - this is the stricter core leg-nerve slice suggested by the literature and
    by the real annotation distribution on this machine

To support the nerve-filtered slice cleanly, the normalized VNC node model now
preserves:

- `entry_nerve`
- `exit_nerve`

Those fields are written into the selective node CSV artifacts so the selected
motor set can be audited directly.

## Real selective artifacts

Leg-subclass artifacts:

- `outputs/metrics/manc_thoracic_slice_summary_leg_subclass.json`
- `outputs/metrics/manc_thoracic_pathway_inventory_leg_subclass.json`
- `outputs/metrics/manc_thoracic_structural_spec_leg_subclass.json`
- `outputs/metrics/manc_thoracic_slice_nodes_leg_subclass.csv`
- `outputs/metrics/manc_thoracic_slice_edges_leg_subclass.csv`
- `outputs/metrics/manc_thoracic_spec_overlap_leg_subclass.json`

Leg-subclass strict-threshold artifacts:

- `outputs/metrics/manc_thoracic_slice_summary_leg_subclass_strict.json`
- `outputs/metrics/manc_thoracic_pathway_inventory_leg_subclass_strict.json`
- `outputs/metrics/manc_thoracic_structural_spec_leg_subclass_strict.json`
- `outputs/metrics/manc_thoracic_slice_nodes_leg_subclass_strict.csv`
- `outputs/metrics/manc_thoracic_slice_edges_leg_subclass_strict.csv`
- `outputs/metrics/manc_thoracic_spec_overlap_leg_subclass_strict.json`

Exit-nerve artifacts:

- `outputs/metrics/manc_thoracic_slice_summary_exit_nerve.json`
- `outputs/metrics/manc_thoracic_pathway_inventory_exit_nerve.json`
- `outputs/metrics/manc_thoracic_structural_spec_exit_nerve.json`
- `outputs/metrics/manc_thoracic_slice_nodes_exit_nerve.csv`
- `outputs/metrics/manc_thoracic_slice_edges_exit_nerve.csv`
- `outputs/metrics/manc_thoracic_spec_overlap_exit_nerve.json`

Exit-nerve strict-threshold artifacts:

- `outputs/metrics/manc_thoracic_slice_summary_exit_nerve_strict.json`
- `outputs/metrics/manc_thoracic_pathway_inventory_exit_nerve_strict.json`
- `outputs/metrics/manc_thoracic_structural_spec_exit_nerve_strict.json`
- `outputs/metrics/manc_thoracic_slice_nodes_exit_nerve_strict.csv`
- `outputs/metrics/manc_thoracic_slice_edges_exit_nerve_strict.csv`
- `outputs/metrics/manc_thoracic_spec_overlap_exit_nerve_strict.json`

Cross-variant comparison artifacts:

- `outputs/metrics/manc_thoracic_variant_comparison.json`
- `outputs/metrics/manc_thoracic_variant_overlap_comparison.json`

## Variant comparison

The real selective comparison is now:

- baseline `all_thoracic`
  - motor targets: `516`
  - premotor candidates: `5474`
  - selected edges: `228061`
  - two-step paths: `2440537`
  - descending structural channels: `1301`
- strict `all_thoracic`
  - motor targets: `516`
  - premotor candidates: `2164`
  - selected edges: `121268`
  - two-step paths: `1536717`
  - descending structural channels: `1297`
- `leg_subclass`
  - motor targets: `381`
  - premotor candidates: `3607`
  - selected edges: `140223`
  - two-step paths: `1460577`
  - descending structural channels: `1240`
- strict `leg_subclass`
  - motor targets: `381`
  - premotor candidates: `1304`
  - selected edges: `68222`
  - two-step paths: `848280`
  - descending structural channels: `1168`
- `exit_nerve`
  - motor targets: `319`
  - premotor candidates: `2850`
  - selected edges: `106154`
  - two-step paths: `1028420`
  - descending structural channels: `1232`
- strict `exit_nerve`
  - motor targets: `319`
  - premotor candidates: `910`
  - selected edges: `46554`
  - two-step paths: `550740`
  - descending structural channels: `1131`

The important qualitative result is not only that the graph shrank.

It is that the exit-nerve slice stayed biologically cleaner while preserving
nearly the full descending shortlist overlap used elsewhere in the repo:

- baseline overlap with the live locomotor shortlist: `30`
- strict `all_thoracic`: `30`
- `leg_subclass`: `30`
- strict `leg_subclass`: `30`
- `exit_nerve`: `30`
- strict `exit_nerve`: `29`

The only selective variant that lost shortlist coverage was the strict
exit-nerve slice, which dropped one `DNpe040` channel. That makes it a useful
stress test, but too aggressive to treat as the default candidate.

## Why the exit-nerve slice is the best next production candidate

The local MANC annotation file shows that a broad `leg_subclass` slice still
includes several ambiguous branch outputs:

- `DProN`
- `VProN`
- `ProAN`
- `AbN1`

By contrast, the `exit_nerve` slice keeps only the core leg-nerve endpoints:

- `ProLN`: `81`
- `MesoLN`: `116`
- `MetaLN`: `122`

That means the exit-nerve slice:

- removes the noisy T1 branch outputs that survive a pure subclass filter
- keeps the entire current locomotor shortlist overlap in the non-strict run
- still retains `1232` descending channels, so it is selective without
  collapsing into another tiny sampled decoder

The current recommendation is therefore:

- keep `leg_subclass` as a useful broad leg-biased reference slice
- treat `exit_nerve` as the default real MANC locomotor endpoint for the next
  decoder-candidate benchmark
- keep the strict exit-nerve slice as an ablation / stress test, not as the
  default

## Current rule for premotor candidates

For the first real slice, a node is promoted to `premotor_candidate` if it:

- is a thoracic intrinsic interneuron
- has at least `2` distinct thoracic motor targets
- has at least `50` total outgoing synaptic weight into the thoracic motor set

Those thresholds are CLI-configurable in the artifact-building script.

## Why this is acceptable as a first real pass

It is not a claim that the repo has solved exact biological premotor identity.

It is an explicit structural rule:

- narrow enough to be inspectable
- broad enough to move beyond tiny sampled DN populations
- directly grounded in real public MANC edges

## Overlap with current repo locomotor names

The real structural specs overlap strongly with the repo's current locomotor
descending shortlist. The overlap artifacts show real MANC channels for:

- `DNg97`
- `DNp103`
- `DNp18`
- `DNpe056`
- `DNpe016`
- `DNpe040`
- `DNp71`
- `DNa01`
- `DNa02`
- `MDN`
- `DNg74_a`
- `DNg74_b`
- `DNg105`
- `DNg108`

That does not prove the current sampled decoder is already correct, but it does
show that many of the repo's live descending hypotheses have real public MANC
thoracic motor reachability in every non-aggressive slice tested here.

## Promotion gate

The repo should not promote a real MANC slice directly into embodied runtime
just because the graph is now public-data-backed.

The next honest gate is:

- materialize the `exit_nerve` structural spec as a `vnc_structural_spec`
  decoder candidate
- run short local closed-loop smoke validation first
- only then compare it against the current sampled/fitted embodied decoder

Until that happens, the output of `T110` is:

- a completed real selective-slice comparison
- a recommended next candidate slice
- not yet an embodied performance claim
