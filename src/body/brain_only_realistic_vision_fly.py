from __future__ import annotations

from typing import Any

import numpy as np

from flygym.fly import Fly
from flygym.examples.vision.realistic_vision import RealisticVisionFly


class BrainOnlyRealisticVisionFly(RealisticVisionFly):
    """Repo-local strict wrapper around FlyGym's realistic-vision fly.

    The upstream `HybridTurningFly` controller still applies rule-based
    corrections even when the descending drive is zero. For the production
    brain-only motor path here, zero decoded drive must result in a neutral
    low-level action instead of locomotion from controller internals.
    """

    def _zero_descending_drive(self, action: Any) -> bool:
        action_array = np.asarray(action, dtype=float).reshape(-1)
        return action_array.size == 2 and np.allclose(action_array, 0.0)

    def _neutral_low_level_action(self, sim) -> dict[str, np.ndarray]:
        default_pose = getattr(getattr(self, "preprogrammed_steps", None), "default_pose", None)
        if default_pose is not None:
            joint_positions = np.asarray(default_pose, dtype=float).reshape(-1).copy()
        else:
            obs = Fly.get_observation(self, sim)
            joint_positions = np.asarray(obs["joints"][0, : len(self.actuated_joints)], dtype=float)
        return {
            "joints": joint_positions.copy(),
            # A planted stance is a more stable no-locomotion default than
            # zero adhesion, which lets the body passively tumble.
            "adhesion": np.ones(self.n_legs, dtype=int),
        }

    def pre_step(self, action, sim):
        if self._zero_descending_drive(action):
            neutral_action = self._neutral_low_level_action(sim)
            self._all_net_corrections = np.zeros(self.n_legs, dtype=float)
            self._action = neutral_action
            return Fly.pre_step(self, neutral_action, sim)
        return super().pre_step(action, sim)
