# Architecture Scout

## Objective Reference

Per `AGENTS.MD`, the target is a local public-equivalent recreation of the Eon-style embodied fly demo with:

- a whole-brain neural simulation
- an embodied fly body simulator
- realistic vision
- an explicit online closed loop
- reproducible local benchmarks and parity artifacts

## Public Repo Findings

### 1. `eonsystemspbc/fly-brain`

Observed files:

- `external/fly-brain/main.py`
- `external/fly-brain/code/benchmark.py`
- `external/fly-brain/code/run_brian2_cuda.py`
- `external/fly-brain/code/run_pytorch.py`
- `external/fly-brain/code/run_nestgpu.py`
- `external/fly-brain/code/paper-phil-drosophila/example.ipynb`

What it provides:

- a FlyWire-derived whole-brain leaky integrate-and-fire model
- benchmark orchestration for four backends: Brian2 CPU, Brian2CUDA, PyTorch, NEST GPU
- public neuron IDs for several descending and sensory-related neurons in the notebook material
- data files for FlyWire v783 connectivity and completeness

What it does not provide:

- no persistent embodied control runtime
- no body/brain synchronization layer
- no direct integration with FlyGym / NeuroMechFly
- no realistic vision adapter into the whole-brain model

Most important reuse point:

- `code/run_pytorch.py` already contains a sparse PyTorch implementation suitable for conversion into a persistent online backend.

### 2. `philshiu/Drosophila_brain_model`

Observed files:

- `external/Drosophila_brain_model/model.py`
- `external/Drosophila_brain_model/utils.py`
- `external/Drosophila_brain_model/example.ipynb`
- `external/Drosophila_brain_model/environment.yml`

What it provides:

- the original Brian2 batch-style model used for the paper
- experiment and figure-generation workflows
- clear evidence that the public model is oriented around offline runs, not persistent control

What it does not provide:

- no online stepping API
- no embodied runtime integration
- no realistic vision pipeline
- no multi-backend benchmark harness

Relationship to `fly-brain`:

- `fly-brain` is the stronger starting point for this repo because it already modernizes the public model into multiple backends and benchmark runners.

### 3. `NeLy-EPFL/flygym`

Observed files:

- `external/flygym/pyproject.toml`
- `external/flygym/flygym/examples/vision/realistic_vision.py`
- `external/flygym/flygym/examples/vision/follow_fly_closed_loop.py`
- `external/flygym/flygym/examples/locomotion/turning_controller.py`
- `external/flygym/doc/source/tutorials/advanced_vision.rst`

What it provides:

- embodied MuJoCo fly simulation
- realistic vision via a connectome-constrained visual system model (`flyvis`)
- high-level descending-drive locomotor control interfaces
- example closed-loop visual tracking controllers

What it does not provide:

- no direct hook to the public whole-brain FlyWire/Shiu model
- no one-command integration with `fly-brain`
- no published mapping from realistic-vision outputs into the whole-brain model's input neuron IDs

## Reconstructed Public-Equivalent Stack

The best public-equivalent system is therefore:

1. `FlyGym` for the body and realistic vision
2. the `fly-brain` PyTorch backend for the online whole-brain runtime
3. a new bridge layer in this repo that:
   - encodes body + realistic-vision observations into brain input rates
   - advances the brain state persistently at a fixed sync cadence
   - decodes descending neuron activity into body control commands
   - logs metrics and artifacts

## Public Neuron Assets Found in Notebooks

From `external/fly-brain/code/paper-phil-drosophila/example.ipynb`:

- Forward / locomotion readouts: `P9_oDN1_left`, `P9_oDN1_right`, `P9_left`, `P9_right`
- Turning readouts: `DNa01_left`, `DNa01_right`, `DNa02_left`, `DNa02_right`
- Reverse / escape candidates: `MDN_1` through `MDN_4`, `Giant_Fiber_1`, `Giant_Fiber_2`
- Grooming / feeding readouts also present

From the same notebook and figure notebooks:

- `LC_4s` visual proxy pool
- `neu_JON_all` mechanosensory proxy pool

These IDs are the strongest public anchors available for building the bridge without inventing arbitrary neuron sets.

## Initial Architecture Decision

Use a split design:

- production full-stack runtime: PyTorch whole-brain backend + FlyGym realistic vision/body runtime
- secondary benchmark env: Brian2 / Brian2CUDA / NEST GPU runners kept separate for module benchmarking
- mock runtime: deterministic in-repo simulator used for tests and artifact-format validation
