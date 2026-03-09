# Dependency Matrix

## Machine Snapshot

| Item | Observed Value | Evidence |
| --- | --- | --- |
| Host OS | Windows Pro host reporting version 2009 | local `Get-ComputerInfo` |
| WSL distro | Ubuntu 24.04, WSL2 | local `wsl -l -v` |
| Host Python | 3.10.11 | local `python --version` |
| WSL Python | 3.12.3 | local `wsl ... python3 --version` |
| GPUs | 2x RTX 5060 Ti 16 GB | local `nvidia-smi`, `wsl ... nvidia-smi` |
| Host driver | 581.29 | local `nvidia-smi` |
| CUDA capability seen by driver | 13.0 | local `nvidia-smi` |
| RAM | 205,983,105,024 bytes (~192 GiB) | local CIM query |

## Public Repo Dependency Findings

| Component | Python | Key Runtime Deps | GPU / CUDA Notes | Status for This Repo |
| --- | --- | --- | --- | --- |
| `fly-brain` | 3.10 | `torch`, `brian2cuda==1.0a7`, `pandas`, `pyarrow`, `scipy`, `matplotlib` | public env points to PyTorch CUDA wheels and Brian2CUDA | reusable for standalone brain benchmarks |
| `Drosophila_brain_model` | 3.10 | `brian2=2.5.1`, `numpy=1.24`, `pandas`, `pyarrow`, `joblib` | CPU-oriented baseline | reference only |
| `flygym` 1.2.1 | >=3.10,<3.13 | `mujoco==3.2.7`, `dm_control==1.0.27`, `numpy>=2,<3`, `gymnasium`, `mediapy`, `opencv-python` | realistic vision example also needs `flyvis==1.1.2`, `torch` via optional examples | reusable for body + realistic vision |
| `flygym[examples]` | >=3.10,<3.13 | adds `flyvis`, `lightning`, `h5py`, `pandas`, `networkx`, `scikit-learn` | required for connectome-constrained realistic vision example | needed for production full stack |
| NEST GPU | separate source build | CUDA toolkit, CMake, patched sources | `fly-brain` README documents a custom `user_m1` neuron model | optional and likely high-effort |

## Important Compatibility Constraints

### Constraint 1: `FlyGym` vs Brian2-era stack

- `flygym` 1.2.1 requires `numpy>=2.0`.
- the original Shiu model and the public `fly-brain` conda files are pinned around `numpy 1.24-1.26` and `brian2 2.5.1`.
- this strongly suggests a single unified environment is risky.

Decision:

- use a modern full-stack environment for `FlyGym + PyTorch whole-brain runtime`
- keep `Brian2 / Brian2CUDA / NEST GPU` in separate benchmark-only environments or subprocess entrypoints

### Constraint 2: WSL is the preferred execution target

- `fly-brain` README explicitly says it was tested on Ubuntu 22.04 under WSL2 on Windows 11.
- `FlyGym` is Linux-friendly and MuJoCo is straightforward in WSL.
- the host already has GPU visibility inside WSL.

Decision:

- make WSL the documented primary path
- keep mock/unit tests runnable from the host Python as well

### Constraint 3: NEST GPU practicality

Evidence from public artifacts:

- `fly-brain` ships a custom NEST GPU runner and documents a patched source build.
- it requires copying a custom neuron model into the NEST GPU source tree and building from source.
- the public repo's own benchmark CSV already shows long-running / timeout failures on some NEST GPU cases.

Preliminary assessment:

- NEST GPU is plausibly buildable on this machine because WSL2 + NVIDIA GPUs are present.
- it is not the fastest path to a first runnable full stack.
- treat it as a secondary benchmark backend, not as the initial production integration path.

## Provisioning Strategy

1. WSL bootstrap script installs shell tooling, CUDA toolkit hooks, and FFmpeg.
2. Main full-stack env installs:
- Python 3.10
- `torch`
- `flygym[examples]==1.2.1`
- `pandas`, `pyarrow`, `pyyaml`, `matplotlib`, `pytest`, `psutil`
3. Optional benchmark env installs:
- `brian2`, `brian2cuda==1.0a7`
- public `fly-brain` dependencies
4. Optional NEST GPU build remains separate and explicitly documented.
