from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("flygym")

from body.brain_only_realistic_vision_fly import BrainOnlyRealisticVisionFly


def test_neutral_low_level_action_uses_planted_default_pose() -> None:
    fly = BrainOnlyRealisticVisionFly.__new__(BrainOnlyRealisticVisionFly)
    fly.n_legs = 6
    fly.actuated_joints = tuple(range(7))
    fly.preprogrammed_steps = type("Steps", (), {"default_pose": np.arange(7, dtype=float)})()

    action = fly._neutral_low_level_action(sim=None)

    assert action["joints"].tolist() == [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    assert action["adhesion"].tolist() == [1, 1, 1, 1, 1, 1]
