from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class CanonicalStimulus:
    stimulus_family: str
    stimulus_name: str
    units: str
    parameters: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CanonicalNeuronTrace:
    trace_id: str
    recorded_entity_id: str
    recorded_entity_type: str
    hemisphere: str | None
    trace_index: int | None
    sampling_rate_hz: float
    units: str
    transform: str
    values_path: str
    time_path: str | None = None
    flywire_mapping_key: str | None = None
    flywire_mapping_confidence: str | None = None
    tags: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["tags"] = list(self.tags)
        return payload


@dataclass(frozen=True)
class CanonicalTrial:
    trial_id: str
    split: str
    behavior_context: str
    stimulus: CanonicalStimulus
    timebase_path: str
    traces: tuple[CanonicalNeuronTrace, ...]
    behavior_paths: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["stimulus"] = self.stimulus.to_dict()
        payload["traces"] = [trace.to_dict() for trace in self.traces]
        return payload


@dataclass(frozen=True)
class CanonicalDatasetBundle:
    dataset_key: str
    citation_label: str
    modality: str
    normalization: dict[str, Any]
    identity_strategy: dict[str, Any]
    trials: tuple[CanonicalTrial, ...]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["trials"] = [trial.to_dict() for trial in self.trials]
        return payload


def canonical_schema_reference() -> dict[str, Any]:
    return {
        "dataset_level": [
            "dataset_key",
            "citation_label",
            "modality",
            "normalization",
            "identity_strategy",
            "trials",
        ],
        "trial_level": [
            "trial_id",
            "split",
            "behavior_context",
            "stimulus",
            "timebase_path",
            "traces",
            "behavior_paths",
            "metadata",
        ],
        "trace_level": [
            "trace_id",
            "recorded_entity_id",
            "recorded_entity_type",
            "hemisphere",
            "trace_index",
            "sampling_rate_hz",
            "units",
            "transform",
            "values_path",
            "time_path",
            "flywire_mapping_key",
            "flywire_mapping_confidence",
            "tags",
        ],
        "required_splits": ["train", "val", "test"],
        "identity_mapping_priority": [
            "exact_neuron_id",
            "cell_type",
            "cell_family",
            "region_component",
            "population_pool",
        ],
    }
