## Descending Visual-Drive Validation

This document tests the strongest claim we can currently make about the new descending-only embodied branch:

- whether the movement and descending readout are visually driven
- not whether the selected descending groups are the final true biological locomotor code

The tested branch is:

- `configs/flygym_realistic_vision_splice_axis1d_descending_readout.yaml`

The runtime now logs explicit target state directly from the simulation:

- `target_state.position_x`
- `target_state.position_y`
- `target_state.yaw`
- `target_state.distance`
- `target_state.bearing_body`

So the current pursuit analysis no longer needs to reconstruct target motion from the public `MovingFlyArena` formula.

It keeps:

- the calibrated embodied visual splice
- the descending-only supplemental readout

And it does **not** use:

- `P9` prosthetic brain context
- optic-lobe-as-motor shortcuts
- decoder idle locomotion fallback
- body-side hidden locomotion fallback

## Matched runs

### 1. Target + real brain

- config: `configs/flygym_realistic_vision_splice_axis1d_descending_readout.yaml`
- video: `outputs/requested_2s_splice_descending_logged_target/flygym-demo-20260309-142600/demo.mp4`
- metrics: `outputs/requested_2s_splice_descending_logged_target/flygym-demo-20260309-142600/metrics.csv`

### 2. Target + zero brain

- config: `configs/flygym_realistic_vision_splice_axis1d_descending_readout_zero_brain.yaml`
- video: `outputs/requested_2s_splice_descending_zero_brain/flygym-demo-20260309-122135/demo.mp4`
- metrics: `outputs/requested_2s_splice_descending_zero_brain/flygym-demo-20260309-122135/metrics.csv`

### 3. No target + real brain

- config: `configs/flygym_realistic_vision_splice_axis1d_descending_readout_no_target.yaml`
- video: `outputs/requested_2s_splice_descending_no_target/flygym-demo-20260309-122723/demo.mp4`
- metrics: `outputs/requested_2s_splice_descending_no_target/flygym-demo-20260309-122723/metrics.csv`

Comparison artifact:

- `outputs/metrics/descending_visual_drive_validation.csv`
- `outputs/metrics/descending_visual_drive_validation.json`
- reproducible summarizer:
  - `scripts/summarize_descending_visual_drive.py`

Controlled side-condition artifacts:

- moving target, initialized left:
  - `outputs/requested_1s_splice_descending_target_left/flygym-demo-20260309-134958/demo.mp4`
- moving target, initialized right:
  - `outputs/requested_1s_splice_descending_target_right/flygym-demo-20260309-135758/demo.mp4`
- stationary target, left:
  - `outputs/requested_1s_splice_descending_stationary_left/flygym-demo-20260309-140844/demo.mp4`
- stationary target, right:
  - `outputs/requested_1s_splice_descending_stationary_right/flygym-demo-20260309-141702/demo.mp4`
- direct target-condition summaries:
  - `outputs/metrics/descending_target_conditions.csv`
  - `outputs/metrics/descending_target_conditions.json`
- reproducible summarizer:
  - `scripts/summarize_descending_target_conditions.py`

## What is proven

### A. No hidden fallback locomotion

The zero-brain matched run shows that this branch does not move meaningfully without the brain:

- `nonzero_command_cycles = 0`
- `net_displacement = 0.011823383234191902`
- `displacement_efficiency = 0.0320475393946615`

So the new traversal in the target run is not coming from a hidden body fallback.

### B. Visual input modulates the descending branch

Comparing target vs no-target, both with the real brain:

- target run:
  - `avg_forward_speed = 4.326325286840003`
  - `mean_total_drive = 0.48122784453026124`
  - `mean_abs_drive_diff = 0.18706207480312084`
- no-target run:
  - `avg_forward_speed = 3.6971077463080686`
  - `mean_total_drive = 0.436327681959764`
  - `mean_abs_drive_diff = 0.12627696034183364`

Relative change from adding the moving target:

- forward speed: about `+17.02%`
- mean total drive: about `+10.29%`
- mean steering asymmetry: about `+48.14%`

So the moving target is not required to get *any* locomotion, but it does measurably increase both drive magnitude and steering asymmetry.

### C. Steering in the target run tracks target bearing

Using the directly logged `target_state.bearing_body` from:

- `outputs/requested_2s_splice_descending_logged_target/flygym-demo-20260309-142600/run.jsonl`

the target-bearing analysis gives:

- `corr(right_drive - left_drive, target_bearing) = 0.7228049533574713`
- sign match rate between steering command and target bearing = `0.7476828012358393`
- sign opposition rate = `0.23274974253347064`

This is strong evidence that the descending readout is steering in relation to the visual target rather than moving randomly.

### D. Forward drive increases when the target is more frontal

Same direct logged-target analysis:

- `corr(total_drive, target_frontalness) = 0.330852251649671`
- `corr(total_drive, -abs(target_bearing)) = 0.330852251649671`
- `corr(forward_speed, target_frontalness) = 0.2452151723394304`

Interpretation:

- when the target is more centered in front of the fly, the model tends to command more total forward drive
- this is consistent with the observed acceleration when the target enters both visual fields

## What is not proven

### 1. Target is not the only visual driver of locomotion

The no-target run still shows substantial movement:

- `net_displacement = 4.938367142047433`
- `displacement_efficiency = 0.6685375152288059`

So locomotion in this branch is not purely “see target fly -> move”.

Likely explanation:

- the realistic visual system still sees the checkerboard ground and self-motion
- that optic flow / scene structure can drive the brain and the descending readout even without a target fly

Therefore the strongest honest claim is:

- the branch is visually driven
- and the target modulates steering / drive
- but the target is not the only source of visual drive

### 2. Controlled left/right target conditions are now explicit, but the short side-isolated steering result is still mixed

The runtime now logs direct target state and the repo now has controlled left/right initial target conditions.

For the stationary left/right conditions:

- left stationary initial bearing:
  - `+1.5726071797408192`
- right stationary initial bearing:
  - `-1.5726715812462848`

So the condition control itself is working.

However, the short `1 s` side-isolated steering result is not yet cleanly mirrored:

- left stationary, early mean drive difference:
  - `-0.056939209407958435`
- right stationary, early mean drive difference:
  - `-0.017198015031286273`

Interpretation:

- the branch clearly sees the side-specific target
- but in these short isolated side conditions, the immediate steering command is not yet a clean left-vs-right mirror

So these side conditions strengthen the runtime instrumentation and stimulus control, but they do not by themselves prove a pure left/right pursuit reflex.

The moving left/right initialization runs are also controlled and logged correctly:

- left moving initial bearing: `+1.5697550741127948`
- right moving initial bearing: `-1.5755194594138011`

But they are also mixed over the short `1 s` window:

- left moving, early mean drive difference: `-0.05511041478293597`
- right moving, early mean drive difference: `-0.021594800448792844`

So the target-state instrumentation is now correct, but a clean mirrored side-specific pursuit reflex is still not established in the short controlled conditions.

### 3. The selected descending groups are not yet proven to be the true biological locomotor code

The branch now uses public descending/efferent neurons, which is anatomically the correct side of the system.

But the selected supplemental groups are still chosen by:

- public anatomy
- body-free splice probe behavior
- embodied movement utility

That is much better than the old optic-lobe shortcut, but it is still not a final proof that these are the unique natural locomotor command neurons.

## Bottom line

What is now supported by evidence:

- movement in the descending-only branch depends on the real brain, not hidden fallback
- visual input is driving the descending branch
- the moving target measurably increases drive and steering asymmetry
- steering commands track directly logged target bearing strongly
- forward drive increases as the target becomes more frontal

What remains open:

- whether this is already the correct biological motor interface
- how much of the remaining behavior is target pursuit versus more general visually driven locomotion from optic flow / scene structure
