from __future__ import annotations

from typing import Any

import numpy as np
from gymnasium import spaces

from flygym.fly import Fly
from flygym.examples.locomotion.turning_fly import HybridTurningFly

from body.brain_only_realistic_vision_fly import BrainOnlyRealisticVisionFly


class ConnectomeTurningFly(BrainOnlyRealisticVisionFly):
    """HybridTurningFly variant driven by richer descending motor latents.

    The goal is not to jump straight to muscles. The goal is to move from a
    two-scalar throttle to a small set of latents that more closely match the
    existing locomotor controller's real internal knobs:
    - left/right CPG amplitude
    - left/right CPG frequency scaling
    - sensory correction gains
    - reverse gate
    """

    def __init__(
        self,
        *args,
        amplitude_range: tuple[float, float] = (0.0, 1.5),
        frequency_scale_range: tuple[float, float] = (0.0, 2.0),
        correction_gain_range: tuple[float, float] = (0.0, 3.0),
        reverse_gate_range: tuple[float, float] = (0.0, 1.0),
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.amplitude_range = amplitude_range
        self.frequency_scale_range = frequency_scale_range
        self.correction_gain_range = correction_gain_range
        self.reverse_gate_range = reverse_gate_range
        self.action_space = spaces.Box(
            low=np.array(
                [
                    amplitude_range[0],
                    amplitude_range[0],
                    frequency_scale_range[0],
                    frequency_scale_range[0],
                    correction_gain_range[0],
                    correction_gain_range[0],
                    reverse_gate_range[0],
                ],
                dtype=np.float32,
            ),
            high=np.array(
                [
                    amplitude_range[1],
                    amplitude_range[1],
                    frequency_scale_range[1],
                    frequency_scale_range[1],
                    correction_gain_range[1],
                    correction_gain_range[1],
                    reverse_gate_range[1],
                ],
                dtype=np.float32,
            ),
        )
        self._base_intrinsic_freqs = np.asarray(self.intrinsic_freqs, dtype=float).copy()
        self._base_intrinsic_amps = np.asarray(self.intrinsic_amps, dtype=float).copy()
        self._base_correction_rates = {
            key: (float(value[0]), float(value[1])) for key, value in self.correction_rates.items()
        }
        self._motor_latent_action = None

    def _parse_motor_latents(self, action: Any) -> dict[str, float]:
        action_array = np.asarray(action, dtype=float).reshape(-1)
        if action_array.size == 2:
            # Backward compatibility for legacy two-drive actions.
            left_drive = float(np.clip(action_array[0], -self.amplitude_range[1], self.amplitude_range[1]))
            right_drive = float(np.clip(action_array[1], -self.amplitude_range[1], self.amplitude_range[1]))
            active = not np.allclose([left_drive, right_drive], 0.0)
            return {
                "left_amp": abs(left_drive),
                "right_amp": abs(right_drive),
                "left_freq_scale": 1.0 if active else 0.0,
                "right_freq_scale": 1.0 if active else 0.0,
                "retraction_gain": 1.0,
                "stumbling_gain": 1.0,
                "reverse_gate": 1.0 if max(-left_drive, -right_drive) > max(left_drive, right_drive) else 0.0,
            }
        if action_array.size != 7:
            raise ValueError(f"Expected 7 motor latents or 2 legacy drives, got shape {action_array.shape}.")
        return {
            "left_amp": float(np.clip(action_array[0], *self.amplitude_range)),
            "right_amp": float(np.clip(action_array[1], *self.amplitude_range)),
            "left_freq_scale": float(np.clip(action_array[2], *self.frequency_scale_range)),
            "right_freq_scale": float(np.clip(action_array[3], *self.frequency_scale_range)),
            "retraction_gain": float(np.clip(action_array[4], *self.correction_gain_range)),
            "stumbling_gain": float(np.clip(action_array[5], *self.correction_gain_range)),
            "reverse_gate": float(np.clip(action_array[6], *self.reverse_gate_range)),
        }

    def _zero_motor_latents(self, latents: dict[str, float]) -> bool:
        return (
            np.isclose(latents["left_amp"], 0.0)
            and np.isclose(latents["right_amp"], 0.0)
            and np.isclose(latents["left_freq_scale"], 0.0)
            and np.isclose(latents["right_freq_scale"], 0.0)
            and np.isclose(latents["reverse_gate"], 0.0)
        )

    def _active_correction_rates(self, latents: dict[str, float]) -> dict[str, tuple[float, float]]:
        return {
            "retraction": (
                self._base_correction_rates["retraction"][0] * latents["retraction_gain"],
                self._base_correction_rates["retraction"][1] * latents["retraction_gain"],
            ),
            "stumbling": (
                self._base_correction_rates["stumbling"][0] * latents["stumbling_gain"],
                self._base_correction_rates["stumbling"][1] * latents["stumbling_gain"],
            ),
        }

    def pre_step(self, action, sim):
        latents = self._parse_motor_latents(action)
        self._motor_latent_action = latents
        if self._zero_motor_latents(latents):
            neutral_action = self._neutral_low_level_action(sim)
            self._all_net_corrections = np.zeros(self.n_legs, dtype=float)
            self._action = neutral_action
            return Fly.pre_step(self, neutral_action, sim)

        direction = -1.0 if latents["reverse_gate"] >= 0.5 else 1.0
        amps = np.array(
            [
                latents["left_amp"],
                latents["left_amp"],
                latents["left_amp"],
                latents["right_amp"],
                latents["right_amp"],
                latents["right_amp"],
            ],
            dtype=float,
        )
        freq_scales = np.array(
            [
                latents["left_freq_scale"],
                latents["left_freq_scale"],
                latents["left_freq_scale"],
                latents["right_freq_scale"],
                latents["right_freq_scale"],
                latents["right_freq_scale"],
            ],
            dtype=float,
        )
        self.cpg_network.intrinsic_amps = self._base_intrinsic_amps * amps
        self.cpg_network.intrinsic_freqs = self._base_intrinsic_freqs * freq_scales * direction
        correction_rates = self._active_correction_rates(latents)

        obs = Fly.get_observation(self, sim)
        leg_to_correct_retraction = self._retraction_rule_find_leg(obs)
        self._update_persistence_counter()
        persistent_retraction = self.retraction_persistence_counter > 0

        self.cpg_network.step()

        joints_angles = []
        adhesion_onoff = []
        all_net_corrections = []
        for i, leg in enumerate(self.preprogrammed_steps.legs):
            retraction_correction, _ = self._update_correction_amount(
                condition=((i == leg_to_correct_retraction) or persistent_retraction[i]),
                curr_amount=self.retraction_correction[i],
                correction_rates=correction_rates["retraction"],
                viz_segment=f"{leg}Tibia" if self.draw_corrections else None,
                sim=sim,
            )
            self.retraction_correction[i] = retraction_correction

            self.stumbling_correction[i], _ = self._update_correction_amount(
                condition=self._stumbling_rule_check_condition(obs, leg),
                curr_amount=self.stumbling_correction[i],
                correction_rates=correction_rates["stumbling"],
                viz_segment=f"{leg}Femur" if self.draw_corrections and retraction_correction <= 0 else None,
                sim=sim,
            )

            net_correction, reset_stumbling = self._get_net_correction(
                self.retraction_correction[i], self.stumbling_correction[i]
            )
            if reset_stumbling:
                self.stumbling_correction[i] = 0.0

            net_correction = np.clip(net_correction, 0, self.max_increment)
            if leg[0] == "R":
                net_correction *= self.right_leg_inversion[i]
            net_correction *= self.phasic_multiplier[leg](self.cpg_network.curr_phases[i] % (2 * np.pi))

            my_joints_angles = self.preprogrammed_steps.get_joint_angles(
                leg,
                self.cpg_network.curr_phases[i],
                self.cpg_network.curr_magnitudes[i],
            )
            my_joints_angles += net_correction * self.correction_vectors[leg[1]]
            joints_angles.append(my_joints_angles)
            all_net_corrections.append(net_correction)
            adhesion_onoff.append(self.preprogrammed_steps.get_adhesion_onoff(leg, self.cpg_network.curr_phases[i]))

        low_level_action = {
            "joints": np.array(np.concatenate(joints_angles)),
            "adhesion": np.array(adhesion_onoff).astype(int),
        }
        self._all_net_corrections = all_net_corrections
        self._action = low_level_action
        return Fly.pre_step(self, low_level_action, sim)

    def post_step(self, sim):
        obs, reward, terminated, truncated, info = super().post_step(sim)
        if self._motor_latent_action is not None:
            info["motor_latent_action"] = {key: float(value) for key, value in self._motor_latent_action.items()}
        return obs, reward, terminated, truncated, info
