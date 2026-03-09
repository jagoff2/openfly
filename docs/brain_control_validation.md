# Brain Control Validation

This document records the direct comparison used to show that the stable strict-default run is moving because of the real brain backend, not because of body fallback.

## Setup

Compared real WSL FlyGym runs at `5 s` simulated time:

1. strict default real-brain run
   - config: `configs/flygym_realistic_vision.yaml`
   - output: `outputs/compare_5s_strict_fast_v2/flygym-demo-20260308-195012`
2. zero-brain baseline
   - config: `configs/flygym_realistic_vision_zero_brain.yaml`
   - output: `outputs/compare_5s_zero_brain_fast/flygym-demo-20260308-201434`

Shared conditions:
- real FlyGym body
- real realistic vision
- `vision_payload_mode: fast`
- no `public_p9_context`
- no inferred-turn brain context
- no decoder idle-drive fallback
- planted zero-drive stance in `src/body/brain_only_realistic_vision_fly.py`

Comparison artifact:
- `outputs/metrics/compare_5s_strict_vs_zero.csv`

## Result

### Strict default real-brain run

- `stable = 1`
- `completed_full_duration = 1`
- `nonzero_command_cycles = 107`
- `path_length = 10.810298593539402`
- `avg_forward_speed = 2.1629248886633454`

### Zero-brain baseline

- `stable = 1`
- `completed_full_duration = 1`
- `nonzero_command_cycles = 0`
- `path_length = 0.3795886446352556`
- `avg_forward_speed = 0.07594810817031923`

## Interpretation

- The zero-brain run produces exactly zero commands for the entire `5 s`.
- The remaining `0.38` path length is passive drift / settling of the embodied model.
- The real-brain run produces `107` nonzero command cycles and about `28.5x` larger path length than the zero-brain baseline.

That is sufficient evidence that the stable strict-default motion is being driven by the real brain backend, not by hidden body fallback.

## Boundary

This validation proves brain-driven motion under the strict default stack.

It does not prove:
- full parity with the public Eon demo
- that the current locomotor policy is biologically complete
- that the current visual-to-brain bridge is the final correct mapping

But it does prove that the fly can now move stably under the real brain path without body-side scripted locomotion.
