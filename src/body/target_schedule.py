from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class ScheduledTargetEvent:
    trigger_time_s: float
    kind: str
    delta_phase_rad: float = 0.0
    visible: bool | None = None


def parse_target_schedule(raw_events: Sequence[Mapping[str, Any]] | None) -> tuple[ScheduledTargetEvent, ...]:
    if not raw_events:
        return ()
    events: list[ScheduledTargetEvent] = []
    for item in raw_events:
        if not isinstance(item, Mapping):
            continue
        kind = str(item.get("kind", "")).strip().lower()
        if kind == "jump":
            trigger_time_s = float(item.get("time_s", 0.0))
            delta_phase_rad = float(item.get("delta_phase_rad", item.get("delta_rad", 0.0)))
            events.append(
                ScheduledTargetEvent(
                    trigger_time_s=trigger_time_s,
                    kind="jump",
                    delta_phase_rad=delta_phase_rad,
                )
            )
            continue
        if kind in {"hide", "remove", "occlude"}:
            start_s = float(item.get("start_s", item.get("time_s", 0.0)))
            if "duration_s" in item:
                end_s = start_s + float(item.get("duration_s", 0.0))
            else:
                end_s = float(item.get("end_s", start_s))
            events.append(
                ScheduledTargetEvent(
                    trigger_time_s=start_s,
                    kind="hide_start",
                    visible=False,
                )
            )
            events.append(
                ScheduledTargetEvent(
                    trigger_time_s=end_s,
                    kind="hide_end",
                    visible=True,
                )
            )
            continue
        if kind == "set_visible":
            trigger_time_s = float(item.get("time_s", 0.0))
            visible = bool(item.get("visible", True))
            events.append(
                ScheduledTargetEvent(
                    trigger_time_s=trigger_time_s,
                    kind="hide_end" if visible else "hide_start",
                    visible=visible,
                )
            )
    return tuple(sorted(events, key=lambda event: (event.trigger_time_s, event.kind)))


class TargetScheduleState:
    def __init__(self, events: Sequence[ScheduledTargetEvent] | None = None) -> None:
        self._events = tuple(events or ())
        self.reset()

    def reset(self) -> None:
        self.phase_offset_rad = 0.0
        self.visible = True
        self.last_event_id = 0
        self.last_event_kind: str | None = None
        self.last_event_time_s: float | None = None
        self.last_event_delta_phase_rad = 0.0
        self._next_index = 0

    def advance(self, current_time_s: float) -> None:
        eps = 1e-9
        while self._next_index < len(self._events):
            event = self._events[self._next_index]
            if event.trigger_time_s > current_time_s + eps:
                break
            if event.kind == "jump":
                self.phase_offset_rad += float(event.delta_phase_rad)
                self.last_event_delta_phase_rad = float(event.delta_phase_rad)
            elif event.visible is not None:
                self.visible = bool(event.visible)
                self.last_event_delta_phase_rad = 0.0
            self.last_event_id += 1
            self.last_event_kind = event.kind
            self.last_event_time_s = float(event.trigger_time_s)
            self._next_index += 1

    def metadata(self, current_time_s: float) -> dict[str, Any]:
        time_since = None
        if self.last_event_time_s is not None:
            time_since = float(max(0.0, current_time_s - self.last_event_time_s))
        return {
            "visible": bool(self.visible),
            "last_event_id": int(self.last_event_id),
            "last_event_kind": self.last_event_kind,
            "last_event_time_s": self.last_event_time_s,
            "time_since_last_event_s": time_since,
            "phase_offset_rad": float(self.phase_offset_rad),
            "last_event_delta_phase_rad": float(self.last_event_delta_phase_rad),
        }
