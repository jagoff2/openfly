# Feeding And Grooming Brain Tasks

This repo now includes grounded brain-only task probes for the two public behaviors validated in:

- `https://www.nature.com/articles/s41586-024-07763-9`

These additions are intentionally scoped as **brain tasks**, not finished embodied behaviors.

## What was added

Public task IDs:

- `src/brain/paper_task_ids.py`

Reusable probe logic:

- `src/brain/paper_task_probes.py`

Runnable scripts:

- `scripts/run_feeding_probe.py`
- `scripts/run_grooming_probe.py`

The scripts use the public notebook IDs already present in the checked-out `fly-brain` repo:

- feeding inputs: labellar sugar GRNs
- feeding outputs: `MN9_left`, `MN9_right`
- grooming inputs: `JON_CE`, `JON_F`, `JON_D_m`, and `JON_all`
- grooming outputs: `aDN1_left`, `aDN1_right`, `aBN1`

## Why this is biologically cleaner than the old locomotion hacks

These task probes:

- use published sensory input neuron sets from the paper notebooks
- use published downstream readout neurons from the same public artifacts
- drive the brain through `direct_input_rates_hz`, which matches the public notebook stimulation style

They do **not**:

- restore decoder idle locomotion
- inject `P9` prosthetic locomotor context
- claim that feeding or grooming is already embodied in FlyGym

## What these probes are for

They let the repo reproduce the paper-style sensorimotor brain tasks directly in the current whole-brain backend.

That gives us:

- grounded non-locomotion brain tasks
- public sensory input sets we can reuse later
- public output neurons we can target in future embodiment experiments

## What they do not prove

They do not yet prove:

- an embodied feeding behavior
- an embodied grooming behavior
- that the current body stack already supports proboscis or foreleg grooming control

Those are later embodiment tasks.

## How to run

Host or WSL, as long as the configured Torch backend can access the public brain files:

```bash
python scripts/run_feeding_probe.py --config configs/default.yaml
python scripts/run_grooming_probe.py --config configs/default.yaml
```

Default outputs:

- `outputs/metrics/feeding_probe.csv`
- `outputs/metrics/feeding_probe_summary.json`
- `outputs/plots/feeding_probe.png`
- `outputs/metrics/grooming_probe.csv`
- `outputs/metrics/grooming_probe_summary.json`
- `outputs/plots/grooming_probe.png`

## Initial local results

The first local probe runs were executed with the default `100 ms` windows:

- feeding summary:
  - `outputs/metrics/feeding_probe_summary.json`
- grooming summary:
  - `outputs/metrics/grooming_probe_summary.json`
- longer grooming follow-up:
  - `outputs/metrics/grooming_probe_500ms_summary.json`

Observed behavior on this repo's current Torch whole-brain backend:

1. Feeding
   - `sugar_right` produced a clear `MN9` response in the `100–200 Hz` range.
   - strongest observed row in the first sweep:
     - `sugar_right @ 180 Hz`
     - `mn9_left = 60 Hz`
     - `mn9_right = 40 Hz`
     - `mn9_total = 100 Hz`
   - `sugar_left` stayed silent in the same short `100 ms` sweep.

2. Grooming
   - in the first short `100 ms` sweep, `aBN1` responded to `JON_CE` and `JON_all`.
   - strongest observed `aBN1` rows in the first sweep were in the high-frequency `JON_CE` / `JON_all` conditions, reaching `20 Hz`.
   - `aDN1_left/right` did not spike in that same short-window sweep.
   - in a longer `500 ms` follow-up sweep:
     - `jon_all @ 220 Hz` produced:
       - `aDN1_right = 6 Hz`
       - `aBN1 = 28 Hz`
     - `jon_ce @ 220 Hz` produced:
       - `aBN1 = 24 Hz`
       - `aDN1` still stayed at `0 Hz`

Interpretation:

- the feeding and grooming task probes are now wired and runnable
- the current backend already shows task-relevant downstream responses
- but the exact response quality depends on stimulus side, stimulus family, and probe window
- these are now good grounded starting points for later embodiment experiments, not final embodied behaviors

## Embodiment follow-up

These brain tasks are now ready for later embodiment experiments:

1. Feeding:
   - connect real contact / gustatory state in the body to the published sugar GRN sets
   - map `MN9` readout to a proboscis actuation interface

2. Grooming:
   - connect antennal contact / deflection to the published JON groups
   - map `aDN1` / `aBN1` readout into a foreleg or head-grooming actuation interface

Those future steps will require new body-side interfaces. They are not already solved by these probe scripts.
