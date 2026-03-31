from __future__ import annotations

import numpy as np

from analysis.visual_speed_control_metrics import compute_visual_speed_control_metrics
from body.visual_speed_control import (
    FlatTerrain,
    VisualSpeedControlConfig,
    VisualSpeedBallTreadmillArena,
    VisualSpeedStripeCorridorArena,
    corridor_half_width_at_x,
    direction_label_from_signed_speed,
    wall_world_speed_from_gain,
    wrap_periodic,
)


def test_wrap_periodic_wraps_into_interval() -> None:
    assert wrap_periodic(12.5, -10.0, 10.0) == -7.5


def test_wall_world_speed_from_gain_matches_stationary_gain_one() -> None:
    assert wall_world_speed_from_gain(5.0, 1.0) == 0.0
    assert wall_world_speed_from_gain(5.0, 9.0) == -40.0
    assert wall_world_speed_from_gain(5.0, -1.0) == 10.0


def test_hourglass_half_width_narrows_at_center() -> None:
    edge = corridor_half_width_at_x(
        -12.0,
        base_half_width_mm=6.0,
        neck_half_width_mm=2.0,
        neck_center_x_mm=0.0,
        neck_half_length_mm=10.0,
    )
    center = corridor_half_width_at_x(
        0.0,
        base_half_width_mm=6.0,
        neck_half_width_mm=2.0,
        neck_center_x_mm=0.0,
        neck_half_length_mm=10.0,
    )
    assert edge == 6.0
    assert center == 2.0


def test_visual_speed_config_closed_loop_gain_uses_gain_formula() -> None:
    cfg = VisualSpeedControlConfig.from_mapping(
        {
            "enabled": True,
            "mode": "closed_loop_gain",
            "gain_baseline": 1.0,
            "gain_stimulus": 9.0,
            "stimulus_start_s": 0.5,
            "stimulus_end_s": 1.5,
        }
    )
    assert cfg.scene_world_speed_mm_s(0.0, 5.0) == 0.0
    assert cfg.scene_world_speed_mm_s(1.0, 5.0) == -40.0
    assert cfg.geometry == "free_corridor"


def test_direction_label_from_signed_speed() -> None:
    assert direction_label_from_signed_speed(-0.1) == "front_to_back"
    assert direction_label_from_signed_speed(0.1) == "back_to_front"
    assert direction_label_from_signed_speed(0.0) == "stationary"


def test_visual_speed_config_accepts_legacy_direction_aliases() -> None:
    cfg = VisualSpeedControlConfig.from_mapping(
        {
            "enabled": True,
            "scene_motion_direction": "ftb",
            "stimulus_scene_velocity_mm_s": 4.0,
            "pre_scene_velocity_mm_s": 1.0,
        }
    )
    assert cfg.stimulus_scene_velocity_mm_s == -4.0
    assert cfg.pre_scene_velocity_mm_s == -1.0


def test_visual_speed_config_parses_interleaved_block_schedule() -> None:
    cfg = VisualSpeedControlConfig.from_mapping(
        {
            "enabled": True,
            "mode": "interleaved_blocks",
            "block_duration_s": 0.25,
            "counterphase_flicker_hz": 4.0,
            "block_schedule": [
                {"kind": "stationary", "label": "baseline"},
                {"kind": "front_to_back", "scene_velocity_mm_s": 6.0, "label": "motion"},
                {"kind": "counterphase_flicker", "label": "flicker"},
            ],
        }
    )
    assert cfg.block_duration_s == 0.25
    assert len(cfg.block_schedule) == 3
    assert cfg.block_schedule[1]["kind"] == "front_to_back"
    assert cfg.block_schedule[1]["scene_velocity_mm_s"] == -6.0
    assert cfg.block_schedule[2]["kind"] == "counterphase_flicker"


def test_visual_speed_config_parses_synced_interleaved_block_schedule() -> None:
    cfg = VisualSpeedControlConfig.from_mapping(
        {
            "enabled": True,
            "mode": "interleaved_blocks",
            "block_duration_s": 0.25,
            "counterphase_flicker_hz": 4.0,
            "block_schedule": [
                {"kind": "stationary", "label": "baseline", "sync_to_fly_speed": True, "gain": 0.0},
                {
                    "kind": "front_to_back",
                    "label": "motion",
                    "sync_to_fly_speed": True,
                    "gain": 0.0,
                    "scene_velocity_offset_mm_s": -0.5,
                },
            ],
        }
    )

    assert cfg.block_schedule[0]["sync_to_fly_speed"] is True
    assert cfg.block_schedule[0]["gain"] == 0.0
    assert cfg.block_schedule[0]["scene_velocity_offset_mm_s"] == 0.0
    assert cfg.block_schedule[1]["kind"] == "front_to_back"
    assert cfg.block_schedule[1]["sync_to_fly_speed"] is True
    assert cfg.block_schedule[1]["gain"] == 0.0
    assert cfg.block_schedule[1]["scene_velocity_offset_mm_s"] == -0.5


def test_visual_speed_corridor_arena_reuses_flat_terrain_floor_contract() -> None:
    assert issubclass(VisualSpeedStripeCorridorArena, FlatTerrain)


def test_compute_visual_speed_metrics_open_loop_fold_change() -> None:
    records = []
    for idx in range(10):
        stimulus_active = idx >= 5
        records.append(
            {
                "sim_time": idx * 0.1,
                "forward_speed": 5.0 if not stimulus_active else 2.5,
                "body_metadata": {
                    "visual_speed_state": {
                        "enabled": True,
                        "mode": "open_loop_drift",
                        "stimulus_active": stimulus_active,
                        "scene_world_speed_mm_s": -30.0 if stimulus_active else 0.0,
                        "effective_visual_speed_mm_s": -35.0 if stimulus_active else -5.0,
                        "gain": 1.0,
                        "corridor_half_width_mm_at_fly": 6.0,
                        "fly_x_mm": float(idx),
                    }
                },
            }
        )
    metrics = compute_visual_speed_control_metrics(records)
    assert metrics["enabled"] is True
    assert metrics["mode"] == "open_loop_drift"
    assert metrics["speed_fold_change"] == 0.5


def test_compute_visual_speed_metrics_interleaved_blocks_use_local_stationary_residuals() -> None:
    records = []
    speeds_by_block = {
        0: 5.0,
        1: 4.0,
        2: 5.2,
        3: 4.9,
        4: 5.1,
        5: 4.1,
        6: 5.0,
    }
    turn_by_block = {
        0: 0.05,
        1: 0.08,
        2: 0.05,
        3: 0.25,
        4: 0.05,
        5: 0.30,
        6: 0.05,
    }
    kind_by_block = {
        0: "stationary",
        1: "front_to_back",
        2: "stationary",
        3: "counterphase_flicker",
        4: "stationary",
        5: "front_to_back",
        6: "stationary",
    }
    for idx in range(14):
        block = idx // 2
        records.append(
            {
                "sim_time": idx * 0.1,
                "forward_speed": speeds_by_block[block],
                "yaw_rate": turn_by_block[block],
                "motor_signals": {"turn_signal": turn_by_block[block]},
                "body_metadata": {
                    "visual_speed_state": {
                        "enabled": True,
                        "mode": "interleaved_blocks",
                        "stimulus_active": kind_by_block[block] != "stationary",
                        "scene_world_speed_mm_s": -4.0 if kind_by_block[block] == "front_to_back" else 0.0,
                        "effective_visual_speed_mm_s": -4.0 if kind_by_block[block] == "front_to_back" else 0.0,
                        "retinal_slip_mm_s": -4.0 if kind_by_block[block] == "front_to_back" else 0.0,
                        "block_index": float(block),
                        "block_kind": kind_by_block[block],
                        "block_label": f"block_{block}",
                        "gain": 1.0,
                        "corridor_half_width_mm_at_fly": 6.0,
                        "fly_x_mm": 0.0,
                    }
                },
            }
        )
    metrics = compute_visual_speed_control_metrics(records)
    assert metrics["mode"] == "interleaved_blocks"
    assert metrics["block_count"] == 7
    assert metrics["front_to_back_block_count"] == 2
    assert metrics["front_to_back_delta_forward_speed_mean"] < 0.0
    assert metrics["counterphase_flicker_delta_forward_speed_mean"] > metrics["front_to_back_delta_forward_speed_mean"]
    assert metrics["front_to_back_delta_forward_speed_low_turn_mean"] < 0.0


def test_compute_visual_speed_metrics_hourglass_detects_slowing() -> None:
    records = []
    for idx, x_mm in enumerate([-8.0, -4.0, -1.0, 0.0, 1.0, 4.0, 8.0]):
        width = 2.5 if abs(x_mm) <= 1.0 else 6.0
        speed = 2.0 if abs(x_mm) <= 1.0 else 5.0
        records.append(
            {
                "sim_time": idx * 0.1,
                "forward_speed": speed,
                "body_metadata": {
                    "visual_speed_state": {
                        "enabled": True,
                        "mode": "hourglass",
                        "stimulus_active": True,
                        "scene_world_speed_mm_s": 0.0,
                        "effective_visual_speed_mm_s": -speed,
                        "gain": 1.0,
                        "corridor_half_width_mm_at_fly": width,
                        "fly_x_mm": x_mm,
                    }
                },
            }
        )
    metrics = compute_visual_speed_control_metrics(records)
    assert metrics["hourglass_slowing_fraction"] > 0.0


def test_compute_visual_speed_metrics_uses_treadmill_measured_speed_and_track_x() -> None:
    records = []
    for idx, track_x in enumerate([-4.0, -2.0, 0.0, 2.0, 4.0]):
        width = 2.5 if abs(track_x) <= 0.5 else 6.0
        measured_speed = 1.5 if abs(track_x) <= 0.5 else 4.0
        records.append(
            {
                "sim_time": idx * 0.1,
                "forward_speed": 99.0,
                "body_metadata": {
                    "visual_speed_state": {
                        "enabled": True,
                        "geometry": "treadmill_ball",
                        "speed_source": "treadmill_ball",
                        "mode": "hourglass",
                        "stimulus_active": True,
                        "scene_world_speed_mm_s": 0.0,
                        "effective_visual_speed_mm_s": -measured_speed,
                        "gain": 1.0,
                        "corridor_half_width_mm_at_fly": width,
                        "fly_x_mm": 0.0,
                        "track_x_mm": track_x,
                        "fly_forward_speed_mm_s_measured": measured_speed,
                    }
                },
            }
        )
    metrics = compute_visual_speed_control_metrics(records)
    assert metrics["sample_count"] == 5
    assert metrics["neck_mean_speed"] < metrics["open_section_mean_speed"]


def test_visual_speed_config_preserves_treadmill_ball_geometry() -> None:
    cfg = VisualSpeedControlConfig.from_mapping({"enabled": True, "geometry": "treadmill_ball"})

    assert cfg.geometry == "treadmill_ball"


def test_treadmill_open_loop_retinal_slip_ignores_self_motion() -> None:
    arena = object.__new__(VisualSpeedBallTreadmillArena)
    arena.config = VisualSpeedControlConfig.from_mapping({"enabled": True, "geometry": "treadmill_ball", "mode": "open_loop_drift"})
    arena.curr_time = 0.6
    arena.scene_offset_x_mm = -3.0
    arena.virtual_track_x_mm = 25.0
    arena.filtered_fly_forward_speed_mm_s = 240.0
    arena.measured_forward_speed_mm_s = 240.0
    arena.fly_x_mm = 0.0
    arena.fly_y_mm = 0.0
    arena.fly_yaw_rad = 0.0
    arena.current_scene_world_speed_mm_s = -6.0
    assert arena._relative_world_x(10.0) == 7.0
    metadata = arena.metadata()
    assert metadata["effective_visual_speed_mm_s"] == -6.0
    assert metadata["retinal_slip_mm_s"] == -6.0
    assert metadata["effective_visual_motion_direction"] == "front_to_back"


def test_treadmill_closed_loop_retinal_slip_tracks_scene_minus_self_motion() -> None:
    arena = object.__new__(VisualSpeedBallTreadmillArena)
    arena.config = VisualSpeedControlConfig.from_mapping({"enabled": True, "geometry": "treadmill_ball", "mode": "closed_loop_gain"})
    arena.curr_time = 0.6
    arena.scene_offset_x_mm = -3.0
    arena.virtual_track_x_mm = 25.0
    arena.filtered_fly_forward_speed_mm_s = 240.0
    arena.measured_forward_speed_mm_s = 240.0
    arena.fly_x_mm = 0.0
    arena.fly_y_mm = 0.0
    arena.fly_yaw_rad = 0.0
    arena.current_scene_world_speed_mm_s = -6.0
    assert arena._relative_world_x(10.0) == -18.0
    metadata = arena.metadata()
    assert metadata["effective_visual_speed_mm_s"] == -246.0
    assert metadata["retinal_slip_mm_s"] == -246.0


def test_synced_interleaved_scene_world_speed_matches_fly_plus_small_offset() -> None:
    cfg = VisualSpeedControlConfig.from_mapping(
        {
            "enabled": True,
            "mode": "interleaved_blocks",
            "block_duration_s": 0.25,
            "block_schedule": [
                {"kind": "stationary", "label": "baseline", "sync_to_fly_speed": True, "gain": 0.0},
                {
                    "kind": "front_to_back",
                    "label": "motion",
                    "sync_to_fly_speed": True,
                    "gain": 0.0,
                    "scene_velocity_offset_mm_s": -0.5,
                },
            ],
        }
    )

    assert cfg.scene_world_speed_mm_s(0.10, 230.0) == 230.0
    assert cfg.scene_world_speed_mm_s(0.30, 230.0) == 229.5


def test_treadmill_synced_interleaved_retinal_slip_tracks_offset_only() -> None:
    arena = object.__new__(VisualSpeedBallTreadmillArena)
    arena.config = VisualSpeedControlConfig.from_mapping(
        {
            "enabled": True,
            "geometry": "treadmill_ball",
            "mode": "interleaved_blocks",
            "block_duration_s": 0.25,
            "block_schedule": [
                {"kind": "stationary", "label": "baseline", "sync_to_fly_speed": True, "gain": 0.0},
                {
                    "kind": "front_to_back",
                    "label": "motion",
                    "sync_to_fly_speed": True,
                    "gain": 0.0,
                    "scene_velocity_offset_mm_s": -0.5,
                },
            ],
        }
    )
    arena.curr_time = 0.30
    arena.scene_offset_x_mm = 0.0
    arena.virtual_track_x_mm = 25.0
    arena.filtered_fly_forward_speed_mm_s = 230.0
    arena.measured_forward_speed_mm_s = 230.0
    arena.fly_x_mm = 0.0
    arena.fly_y_mm = 0.0
    arena.fly_yaw_rad = 0.0
    arena.current_scene_world_speed_mm_s = arena.config.scene_world_speed_mm_s(arena.curr_time, arena.filtered_fly_forward_speed_mm_s)

    metadata = arena.metadata()
    assert metadata["block_sync_to_fly_speed"] is True
    assert metadata["block_kind"] == "front_to_back"
    assert metadata["scene_world_speed_mm_s"] == 229.5
    assert metadata["effective_visual_speed_mm_s"] == -0.5
    assert metadata["retinal_slip_mm_s"] == -0.5


def test_counterphase_flicker_phase_offset_alternates_half_stripe() -> None:
    cfg = VisualSpeedControlConfig.from_mapping(
        {
            "enabled": True,
            "mode": "interleaved_blocks",
            "stripe_width_mm": 2.0,
            "counterphase_flicker_hz": 4.0,
            "block_schedule": [{"kind": "counterphase_flicker"}],
        }
    )
    assert cfg.counterphase_flicker_phase_offset_mm(0.00) == 0.0
    assert cfg.counterphase_flicker_phase_offset_mm(0.13) == 1.0


def test_treadmill_ball_visual_hooks_hide_ball_only_during_visual_render() -> None:
    arena = object.__new__(VisualSpeedBallTreadmillArena)
    arena._treadmill_geom = object()
    arena._treadmill_visual_rgba = None

    class _BoundGeom:
        def __init__(self) -> None:
            self.rgba = np.array([0.25, 0.5, 0.75, 1.0], dtype=float)

    class _FakePhysics:
        def __init__(self) -> None:
            self.bound = _BoundGeom()

        def bind(self, geom):  # noqa: ANN001
            assert geom is arena._treadmill_geom
            return self.bound

    physics = _FakePhysics()

    arena.pre_visual_render_hook(physics)
    assert np.allclose(physics.bound.rgba, np.array([0.25, 0.5, 0.75, 0.0]))

    arena.post_visual_render_hook(physics)
    assert np.allclose(physics.bound.rgba, np.array([0.25, 0.5, 0.75, 1.0]))


def test_make_treadmill_visually_neutral_hides_ball_in_demo_render() -> None:
    arena = object.__new__(VisualSpeedBallTreadmillArena)

    class _Geom:
        def __init__(self) -> None:
            self.rgba = (1.0, 1.0, 1.0, 1.0)

    geom = _Geom()
    arena._treadmill_geom = geom
    arena._make_treadmill_visually_neutral()
    assert geom.rgba == (0.35, 0.35, 0.35, 0.0)
