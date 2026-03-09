# System Architecture

## Production Path

The current production architecture is:

1. `FlyGymRealisticVisionRuntime`
- owns the MuJoCo body simulation and realistic vision pipeline
- exposes body state, contact forces, and visual neural activity

2. `WholeBrainTorchBackend`
- persistent PyTorch implementation of the public whole-brain LIF model
- accepts pool-wise sensory rates every control window
- returns descending-neuron readout firing rates

3. `ClosedLoopBridge`
- extracts realistic-vision features from neural activity
- encodes body + vision into public sensory proxy pools
- decodes descending-neuron firing into left/right descending drive

4. `runtime.closed_loop`
- schedules the body and brain at a configurable sync cadence
- logs JSONL events, writes metrics CSV, trajectory plots, command plots, and demo video

## Test Path

The deterministic test path replaces the production body and brain with:

- `MockEmbodiedRuntime`
- `MockWholeBrainBackend`

This keeps unit and smoke tests fast while preserving the same bridge and runtime interfaces.

## Artifact Flow

- logs: `outputs/demos/<run>/run.jsonl`
- metrics: `outputs/demos/<run>/metrics.csv`
- plots: `trajectory.png`, `commands.png`
- video: `demo.mp4` or fallback `.gif`
- benchmark CSVs: `outputs/benchmarks/*.csv`
