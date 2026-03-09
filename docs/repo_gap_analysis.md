# Repo Gap Analysis

## Summary

No single public repo already implements the target system described in `AGENTS.MD`.

The public materials are complementary rather than turnkey:

- `fly-brain` gives the brain benchmark backends
- `Drosophila_brain_model` gives the original paper model
- `flygym` gives the body, MuJoCo runtime, and realistic vision

This repo therefore has to supply the missing online glue.

## Gap Table

| Requirement from `AGENTS.MD` | Public Coverage | Gap | Planned Repo Action |
| --- | --- | --- | --- |
| Whole-brain neural simulation | yes, via `fly-brain` / Shiu model | no persistent online stepping API exposed for embodiment | wrap PyTorch backend into a persistent online runtime |
| Embodied musculoskeletal fly simulation | yes, via `flygym` | not connected to whole-brain stack | implement FlyGym adapter |
| Realistic vision | yes, via `flygym` + `flyvis` | not mapped into whole-brain input neurons | implement sensory encoder using public visual proxy pools |
| Closed-loop online control | partially, FlyGym has controller examples | no public whole-brain + body bridge | implement scheduler + bridge |
| Observable Eon-style parity metrics | no | no parity criteria or reports | create parity metrics + report templates |
| Benchmarking across modules | partially | not unified across body/brain/full stack | add benchmark runners and common CSV schema |
| One-command reproducibility | no | multiple public repos, conflicting deps | add bootstrap scripts and config-driven CLI |
| Tests for bridge/runtime | no | absent | add unit, smoke, and acceptance tests |

## Concrete Missing Pieces

### Missing piece 1: online brain stepping

The public PyTorch runner in `fly-brain` does this:

- load sparse weights
- allocate state tensors
- step through a fixed benchmark window
- dump all spikes to parquet

It does not do this:

- accept new sensory drive every sync window
- expose persistent state between windows
- provide decoded motor readouts for embodiment

This repo must add that API.

### Missing piece 2: sensorimotor mapping

The public artifacts expose useful neuron IDs, but not a published, ready-to-run mapping from:

- FlyGym realistic-vision outputs
- FlyGym body state / mechanosensory signals
- whole-brain input neuron pools
- whole-brain descending neurons
- FlyGym descending-drive control actions

This repo must define and document an inferred mapping. That mapping is a scientific assumption, not a recovered private truth.

### Missing piece 3: scheduler and timing model

The public repos do not agree on a shared runtime loop.

Needed here:

- body timestep handling
- brain timestep handling
- realistic vision refresh cadence
- sync window / hold-last-command logic
- logging of sim time vs wall time

### Missing piece 4: artifact generation

The public repos ship examples and benchmark outputs, but not the full set required by `AGENTS.MD`:

- unified benchmark CSVs
- plots
- videos
- JSONL timing logs
- parity report
- assumptions/gaps report

## NEST GPU Gap

The public `fly-brain` repo suggests NEST GPU support is real but nontrivial:

- custom source patching
- source build in Linux
- likely architecture-specific tuning
- longer failure/debug loop than the PyTorch backend

Decision:

- treat NEST GPU as optional secondary work after PyTorch full-stack integration works
- if it remains unbuildable or too fragile, mark it blocked with explicit evidence rather than hiding the failure
