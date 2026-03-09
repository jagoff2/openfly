# Timing Model

## Current Sync Model

The runtime uses a hold-last-command explicit scheduler.

Definitions:

- `body_timestep_s`: physics/body update interval
- `brain_dt_ms`: neural integration timestep in milliseconds
- `control_interval_s`: closed-loop synchronization interval

For each control cycle:

1. observe current body state and realistic-vision neural activity
2. extract compact vision features
3. encode body + vision into sensory pool rates
4. step the brain for `control_interval_s / brain_dt`
5. decode descending-neuron readouts into left/right drive
6. apply that drive to the body for `control_interval_s / body_timestep`

## Current Configurations

### Mock config

- `body_timestep_s = 0.01`
- `control_interval_s = 0.02`
- `brain_dt_ms = 0.1`
- body substeps per control cycle: 2
- brain steps per control cycle: 200

### FlyGym realistic-vision config

- `body_timestep_s = 0.0001`
- `control_interval_s = 0.002`
- `brain_dt_ms = 0.1`
- body substeps per control cycle: 20
- brain steps per control cycle: 20

The FlyGym production cadence deliberately aligns the sync window with the 500 Hz realistic-vision refresh used by the public example code.
