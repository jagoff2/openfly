from __future__ import annotations

from body.target_schedule import TargetScheduleState, parse_target_schedule


def test_parse_target_schedule_expands_hide_event() -> None:
    schedule = parse_target_schedule(
        [
            {"kind": "jump", "time_s": 0.5, "delta_phase_rad": 1.0},
            {"kind": "hide", "start_s": 1.0, "duration_s": 0.3},
        ]
    )

    assert [event.kind for event in schedule] == ["jump", "hide_start", "hide_end"]
    assert schedule[1].trigger_time_s == 1.0
    assert schedule[2].trigger_time_s == 1.3


def test_target_schedule_state_applies_jump_and_visibility() -> None:
    state = TargetScheduleState(
        parse_target_schedule(
            [
                {"kind": "jump", "time_s": 0.2, "delta_phase_rad": 0.8},
                {"kind": "hide", "start_s": 0.4, "duration_s": 0.2},
            ]
        )
    )

    state.advance(0.19)
    assert state.phase_offset_rad == 0.0
    assert state.visible is True

    state.advance(0.2)
    assert state.phase_offset_rad == 0.8
    assert state.last_event_kind == "jump"
    assert state.last_event_id == 1

    state.advance(0.45)
    assert state.visible is False
    assert state.last_event_kind == "hide_start"
    assert state.last_event_id == 2

    state.advance(0.61)
    assert state.visible is True
    assert state.last_event_kind == "hide_end"
    assert state.last_event_id == 3
