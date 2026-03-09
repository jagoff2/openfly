# Public P9 Context Mode

This repo now includes a clearly labeled brain-side experiment mode:

- `brain_context.mode: public_p9_context`

It exists to reproduce the public notebook framing more honestly than decoder or body-side fallback locomotion.

## What It Does

It injects direct public `P9` drive into the whole-brain backend on each control cycle:

- `P9_left = 100 Hz`
- `P9_right = 100 Hz`

by default, matching the public notebook's forward-walking baseline setup.

This mode does **not**:

- restore decoder idle drive
- restore a minimum positive drive floor
- restore body-side hidden locomotion

So any resulting motion still has to pass through:

- the whole-brain backend
- the monitored DN readouts
- the existing decoder
- the FlyGym body controller

## Why It Exists

The checked public notebook in `external/fly-brain/code/paper-phil-drosophila/example.ipynb` uses:

- `P9s_100Hz` first
- then `P9_LC4s`
- then `P9_JO_CE_bilateral`

That means the public examples are using direct `P9` locomotor context as the baseline, then adding sensory co-stimulation on top.

The strict default production path in this repo does **not** inject that context. That stricter path is more honest as a sensory-only test, but it currently yields no meaningful locomotor output.

## Configuration

Config file:

- `configs/flygym_realistic_vision_public_p9_context.yaml`

CLI override example:

```bash
python benchmarks/run_fullstack_with_realistic_vision.py \
  --config configs/flygym_realistic_vision.yaml \
  --mode flygym \
  --duration 0.02 \
  --vision-payload-mode fast \
  --brain-context-mode public_p9_context \
  --brain-context-p9-rate-hz 100
```

## Validation Evidence

Short real WSL validation run:

- benchmark CSV: `outputs/benchmarks/fullstack_public_p9_context_test.csv`
- plot: `outputs/plots/fullstack_public_p9_context_test.png`
- video: `outputs/public_p9_context_test/demos/flygym-demo-20260308-165839.mp4`
- log: `outputs/public_p9_context_test/logs/flygym-demo-20260308-165839.jsonl`
- metrics: `outputs/public_p9_context_test/metrics/flygym-demo-20260308-165839.csv`

Measured result:

- `wall_seconds = 5.0650771999999975`
- `sim_seconds = 0.018000000000000002`
- `real_time_factor = 0.003553746426609255`

Observed from the log:

- `brain_context.mode = public_p9_context`
- `brain_context.direct_input_rates_hz = {P9_left: 100.0, P9_right: 100.0}`
- `max_forward_left_hz = 249.99998474121094`
- `max_forward_right_hz = 249.99998474121094`
- `nonzero command cycles = 2 / 10`

## Interpretation

This mode is useful as a public-experiment analogue:

- it keeps brain-only motor semantics intact
- it avoids hidden decoder/body fallback
- it reproduces the public `P9` baseline framing

But it is not the same claim as strict sensory-only closed-loop control.

The default faithful production mode remains:

- `brain_context.mode: none`

The `public_p9_context` mode should be treated as an explicit experiment mode, not as proof that realistic vision alone is currently driving locomotion in the public-equivalent stack.
