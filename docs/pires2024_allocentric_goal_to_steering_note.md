# Pires 2024 Goal-To-Steering Note

Paper:
- Pires, P. M., Zhang, L., Parache, V., Abbott, L. F., Maimon, G. *Converting an allocentric goal into an egocentric steering signal*. Nature 626, 808-818 (2024). https://www.nature.com/articles/s41586-023-07006-3

## Why This Paper Matters To OpenFly

Yes. This paper is directly relevant to the current embodied-steering bottleneck.
It gives a concrete brain-side circuit for converting a navigation goal into a
steering command in adult `Drosophila`, and its perturbation logic is close to
the repo's current target-jump assay.

The main mechanistic result is:

- `EPG` neurons encode heading angle in allocentric coordinates.
- `FC2` neurons encode goal angle in allocentric coordinates.
- `PFL3` neurons combine heading and goal information conjunctively.
- the comparison yields an egocentric steering signal appropriate for motor
  control, with output to the `LAL`.

That is exactly the kind of scaffold this repo is missing. The current active
branch has a decoder-internal brain latent that improves steering, but it does
not yet have a clearly grounded heading-goal-to-steering decomposition.

## What The Paper Changes About Our Interpretation

The paper makes the current target-jump assay more meaningful, but also shows
that it should be interpreted more carefully.

In the paper, flies perform menotaxis-like orientation relative to a visual cue.
The cue is then rotated, and flies make corrective turns to recover the prior
heading/goal relationship. That means the grounded biological comparison is not
"arbitrary moving-target pursuit." It is:

- heading / goal maintenance
- perturbation response
- corrective steering back toward the prior orientation goal

That is closer to our current `target_jump` assay than to generic continuous
moving-target pursuit.

However, our current assay is harsher than the paper's perturbation paradigm.
In OpenFly, after the jump the target keeps moving tangentially in world space.
So a strict failure to re-enter a narrow frontal cone within `2.0 s` does not
necessarily mean the steering policy is biologically wrong. It can also mean the
fly is producing the correct signed corrective turn but lacks the turning
authority to fully recapture a fast-moving target under continuous motion.

## Immediate Repo Consequences

This paper implies four concrete changes for future work.

1. The active jump metric should be treated as a heading-goal perturbation assay,
   not as a generic pursuit benchmark.
2. Stronger success metrics are corrective-turn metrics and heading-recovery
   metrics, not only strict frontal refixation fractions.
3. The next biologically grounded steering scaffold should target
   `EPG -> FC2 -> PFL3 -> LAL` style computations inside the brain model, not
   only output-side latent fitting.
4. A future assay should include a cue-jump / bar-jump style perturbation where
   the post-jump target is not simultaneously sweeping tangentially, so the repo
   can separate "correct steering computation" from "physical inability to catch
   a moving target fast enough."

## What This Paper Does Not Give Us

The paper is highly informative, but it does not solve the full repo problem on
its own.

It does not provide:

- a full whole-brain embodied closed-loop implementation
- direct FlyWire-root mappings for every relevant neuron in our current model
- a finished motor pathway down to the embodied FlyGym controller
- proof that our current latent branch already implements the same circuit

So the correct use of this paper is as a constraint and design target, not as a
license to overclaim parity.

## Practical Summary

This paper is one of the clearest external validations that the repo should move
toward an explicit brain-side heading / goal / steering scaffold. It also
supports a more honest interpretation of the current jump artifacts: the branch
can be doing the right corrective computation even when the moving-target
geometry prevents clean `20 deg` refixation within the current `2.0 s` window.
