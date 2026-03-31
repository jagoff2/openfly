from __future__ import annotations

import math
import pickle
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter
from typing import Any, Mapping

import numpy as np
import pandas as pd
import torch
import torch.nn as nn

from brain.flywire_annotations import load_flywire_annotation_table
from brain.public_ids import MOTOR_READOUT_IDS, PUBLIC_INPUT_IDS, collapse_sensor_pool_rates

MODEL_PARAMS = {
    "tauSyn": 5.0,
    "tDelay": 1.8,
    "v0": -52.0,
    "vReset": -52.0,
    "vRest": -52.0,
    "vThreshold": -45.0,
    "tauMem": 20.0,
    "tRefrac": 2.2,
    "scalePoisson": 250.0,
    "wScale": 0.275,
}

DEFAULT_SYNAPSE_CLASSES: tuple[dict[str, float | str], ...] = (
    {"name": "fast_exc", "tau_ms": 5.0, "gain": 1.0},
    {"name": "slow_exc", "tau_ms": 25.0, "gain": 0.35},
    {"name": "fast_inh", "tau_ms": 10.0, "gain": -1.0},
    {"name": "slow_inh", "tau_ms": 50.0, "gain": -0.5},
    {"name": "modulatory", "tau_ms": 200.0, "gain": 0.2},
)


@dataclass(frozen=True)
class BackendDynamicsGroupConfig:
    tau_syn_fast_ms: float = MODEL_PARAMS["tauSyn"]
    tau_delay_ms: float = MODEL_PARAMS["tDelay"]
    v0_mv: float = MODEL_PARAMS["v0"]
    v_reset_mv: float = MODEL_PARAMS["vReset"]
    v_rest_mv: float = MODEL_PARAMS["vRest"]
    v_threshold_mv: float = MODEL_PARAMS["vThreshold"]
    tau_mem_ms: float = MODEL_PARAMS["tauMem"]
    tau_refrac_ms: float = MODEL_PARAMS["tRefrac"]
    scale_poisson: float = MODEL_PARAMS["scalePoisson"]
    w_scale: float = MODEL_PARAMS["wScale"]
    tau_adapt_ms: float = 80.0
    adapt_a: float = 0.0
    adapt_b: float = 0.0
    noise_sigma: float = 0.0
    noise_tau_ms: float = 10.0
    release_mode: str = "spiking"
    tau_release_ms: float = 8.0
    release_v_half_mv: float = -50.0
    release_slope_mv: float = 2.0
    tau_calcium_ms: float = 150.0
    calcium_spike_gain: float = 0.0
    calcium_release_gain: float = 0.0
    calcium_adapt_gain: float = 0.0
    calcium_release_feedback_gain: float = 0.0
    synaptic_gain_scale: float = 1.0
    release_gain_scale: float = 1.0
    neuromod_gain_scale: float = 1.0

    @classmethod
    def from_mapping(
        cls,
        mapping: Mapping[str, Any] | None,
        *,
        base: "BackendDynamicsGroupConfig" | None = None,
    ) -> "BackendDynamicsGroupConfig":
        mapping = dict(mapping or {})
        base = base or cls()
        release_mode = str(mapping.get("release_mode", base.release_mode))
        if release_mode not in {"spiking", "graded", "mixed"}:
            raise ValueError(
                f"Unsupported backend_dynamics release_mode={release_mode!r}; "
                "expected 'spiking', 'graded', or 'mixed'"
            )
        return cls(
            tau_syn_fast_ms=float(mapping.get("tau_syn_fast_ms", base.tau_syn_fast_ms)),
            tau_delay_ms=float(mapping.get("tau_delay_ms", base.tau_delay_ms)),
            v0_mv=float(mapping.get("v0_mv", base.v0_mv)),
            v_reset_mv=float(mapping.get("v_reset_mv", base.v_reset_mv)),
            v_rest_mv=float(mapping.get("v_rest_mv", base.v_rest_mv)),
            v_threshold_mv=float(mapping.get("v_threshold_mv", base.v_threshold_mv)),
            tau_mem_ms=float(mapping.get("tau_mem_ms", base.tau_mem_ms)),
            tau_refrac_ms=float(mapping.get("tau_refrac_ms", base.tau_refrac_ms)),
            scale_poisson=float(mapping.get("scale_poisson", base.scale_poisson)),
            w_scale=float(mapping.get("w_scale", base.w_scale)),
            tau_adapt_ms=float(mapping.get("tau_adapt_ms", base.tau_adapt_ms)),
            adapt_a=float(mapping.get("adapt_a", base.adapt_a)),
            adapt_b=float(mapping.get("adapt_b", base.adapt_b)),
            noise_sigma=float(mapping.get("noise_sigma", base.noise_sigma)),
            noise_tau_ms=float(mapping.get("noise_tau_ms", base.noise_tau_ms)),
            release_mode=release_mode,
            tau_release_ms=float(mapping.get("tau_release_ms", base.tau_release_ms)),
            release_v_half_mv=float(mapping.get("release_v_half_mv", base.release_v_half_mv)),
            release_slope_mv=float(mapping.get("release_slope_mv", base.release_slope_mv)),
            tau_calcium_ms=float(mapping.get("tau_calcium_ms", base.tau_calcium_ms)),
            calcium_spike_gain=float(mapping.get("calcium_spike_gain", base.calcium_spike_gain)),
            calcium_release_gain=float(mapping.get("calcium_release_gain", base.calcium_release_gain)),
            calcium_adapt_gain=float(mapping.get("calcium_adapt_gain", base.calcium_adapt_gain)),
            calcium_release_feedback_gain=float(
                mapping.get("calcium_release_feedback_gain", base.calcium_release_feedback_gain)
            ),
            synaptic_gain_scale=float(mapping.get("synaptic_gain_scale", base.synaptic_gain_scale)),
            release_gain_scale=float(mapping.get("release_gain_scale", base.release_gain_scale)),
            neuromod_gain_scale=float(mapping.get("neuromod_gain_scale", base.neuromod_gain_scale)),
        )

    def to_model_params(self) -> dict[str, float]:
        return {
            "tauSyn": self.tau_syn_fast_ms,
            "tDelay": self.tau_delay_ms,
            "v0": self.v0_mv,
            "vReset": self.v_reset_mv,
            "vRest": self.v_rest_mv,
            "vThreshold": self.v_threshold_mv,
            "tauMem": self.tau_mem_ms,
            "tRefrac": self.tau_refrac_ms,
            "scalePoisson": self.scale_poisson,
            "wScale": self.w_scale,
        }


@dataclass(frozen=True)
class BackendDynamicsGroup:
    name: str
    indices: tuple[int, ...]
    config: BackendDynamicsGroupConfig


@dataclass(frozen=True)
class BackendDynamicsConfig:
    mode: str = "legacy_lif"
    spontaneous_source: str = "diagnostic_surrogate"
    annotation_path: str = "outputs/cache/flywire_annotation_supplement.tsv"
    group_key: str = "super_class"
    neuromodulation_enabled: bool = False
    modulatory_group_names: tuple[str, ...] = ("endocrine", "dopamine", "serotonin", "octopamine", "tyramine")
    arousal_tau_ms: float = 500.0
    exafference_tau_ms: float = 250.0
    arousal_current_gain: float = 40.0
    adaptation_mod_gain: float = 0.5
    synaptic_mod_gain: float = 0.5
    release_mod_gain: float = 0.5
    default_group: BackendDynamicsGroupConfig = field(default_factory=BackendDynamicsGroupConfig)
    groups: dict[str, BackendDynamicsGroupConfig] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any] | None) -> "BackendDynamicsConfig":
        mapping = dict(mapping or {})
        default_group = BackendDynamicsGroupConfig.from_mapping(mapping.get("default_group"))
        raw_groups = dict(mapping.get("groups", {}) or {})
        groups = {
            str(name): BackendDynamicsGroupConfig.from_mapping(group_mapping, base=default_group)
            for name, group_mapping in raw_groups.items()
        }
        mode = str(mapping.get("mode", "legacy_lif"))
        spontaneous_source = str(mapping.get("spontaneous_source", "diagnostic_surrogate"))
        if mode not in {"legacy_lif", "grouped_glif_scaffold"}:
            raise ValueError(
                f"Unsupported backend_dynamics.mode={mode!r}; expected 'legacy_lif' or 'grouped_glif_scaffold'"
            )
        if spontaneous_source not in {"diagnostic_surrogate", "endogenous"}:
            raise ValueError(
                "Unsupported backend_dynamics.spontaneous_source="
                f"{spontaneous_source!r}; expected 'diagnostic_surrogate' or 'endogenous'"
            )
        return cls(
            mode=mode,
            spontaneous_source=spontaneous_source,
            annotation_path=str(mapping.get("annotation_path", "outputs/cache/flywire_annotation_supplement.tsv")),
            group_key=str(mapping.get("group_key", "super_class")),
            neuromodulation_enabled=bool(mapping.get("neuromodulation_enabled", False)),
            modulatory_group_names=tuple(str(value).lower() for value in mapping.get("modulatory_group_names", ("endocrine", "dopamine", "serotonin", "octopamine", "tyramine"))),
            arousal_tau_ms=float(mapping.get("arousal_tau_ms", 500.0)),
            exafference_tau_ms=float(mapping.get("exafference_tau_ms", 250.0)),
            arousal_current_gain=float(mapping.get("arousal_current_gain", 40.0)),
            adaptation_mod_gain=float(mapping.get("adaptation_mod_gain", 0.5)),
            synaptic_mod_gain=float(mapping.get("synaptic_mod_gain", 0.5)),
            release_mod_gain=float(mapping.get("release_mod_gain", 0.5)),
            default_group=default_group,
            groups=groups,
        )

    @property
    def use_diagnostic_surrogate(self) -> bool:
        return self.spontaneous_source == "diagnostic_surrogate"

    @property
    def endogenous_path_selected(self) -> bool:
        return self.spontaneous_source == "endogenous"


@dataclass(frozen=True)
class SpontaneousFamilyGroup:
    family: str
    left_indices: tuple[int, ...]
    right_indices: tuple[int, ...]


@dataclass(frozen=True)
class SpontaneousStateConfig:
    mode: str = "none"
    active_fraction: float = 0.0
    lognormal_mean_hz: float = 0.0
    lognormal_sigma: float = 1.0
    max_rate_hz: float = 0.0
    voltage_jitter_std_mv: float = 0.0
    latent_count: int = 0
    latent_target_fraction: float = 0.0
    latent_loading_std_hz: float = 0.0
    latent_ou_tau_s: float = 0.0
    latent_ou_sigma_hz: float = 0.0
    annotation_path: str = "outputs/cache/flywire_annotation_supplement.tsv"
    family_key: str = "auto"
    min_family_size_per_side: int = 2
    max_family_size_per_side: int = 0
    included_super_classes: tuple[str, ...] = ()
    bilateral_coupling: float = 0.9
    family_rate_jitter_fraction: float = 0.1
    neuron_rate_jitter_fraction: float = 0.05
    antisymmetric_latent_fraction: float = 0.1

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any] | None) -> "SpontaneousStateConfig":
        mapping = dict(mapping or {})
        return cls(
            mode=str(mapping.get("mode", "none")),
            active_fraction=float(mapping.get("active_fraction", 0.0)),
            lognormal_mean_hz=float(mapping.get("lognormal_mean_hz", 0.0)),
            lognormal_sigma=float(mapping.get("lognormal_sigma", 1.0)),
            max_rate_hz=float(mapping.get("max_rate_hz", 0.0)),
            voltage_jitter_std_mv=float(mapping.get("voltage_jitter_std_mv", 0.0)),
            latent_count=int(mapping.get("latent_count", 0)),
            latent_target_fraction=float(mapping.get("latent_target_fraction", 0.0)),
            latent_loading_std_hz=float(mapping.get("latent_loading_std_hz", 0.0)),
            latent_ou_tau_s=float(mapping.get("latent_ou_tau_s", 0.0)),
            latent_ou_sigma_hz=float(mapping.get("latent_ou_sigma_hz", 0.0)),
            annotation_path=str(mapping.get("annotation_path", "outputs/cache/flywire_annotation_supplement.tsv")),
            family_key=str(mapping.get("family_key", "auto")),
            min_family_size_per_side=int(mapping.get("min_family_size_per_side", 2)),
            max_family_size_per_side=int(mapping.get("max_family_size_per_side", 0)),
            included_super_classes=tuple(str(value).lower() for value in mapping.get("included_super_classes", ())),
            bilateral_coupling=float(mapping.get("bilateral_coupling", 0.9)),
            family_rate_jitter_fraction=float(mapping.get("family_rate_jitter_fraction", 0.1)),
            neuron_rate_jitter_fraction=float(mapping.get("neuron_rate_jitter_fraction", 0.05)),
            antisymmetric_latent_fraction=float(mapping.get("antisymmetric_latent_fraction", 0.1)),
        )

    @property
    def tonic_enabled(self) -> bool:
        return (
            self.mode != "none"
            and self.active_fraction > 0.0
            and self.lognormal_mean_hz > 0.0
            and self.max_rate_hz > 0.0
        )

    @property
    def latent_enabled(self) -> bool:
        return (
            self.mode != "none"
            and self.latent_count > 0
            and self.latent_target_fraction > 0.0
            and self.latent_loading_std_hz > 0.0
            and self.latent_ou_tau_s > 0.0
            and self.latent_ou_sigma_hz > 0.0
            and self.max_rate_hz > 0.0
        )

    @property
    def enabled(self) -> bool:
        return self.tonic_enabled or self.latent_enabled

class PoissonSpikeGenerator(nn.Module):
    def __init__(self, dt_ms: float, scale: float, device: str) -> None:
        super().__init__()
        self.prob_scale = dt_ms / 1000.0
        self.scale = scale
        self.device = device

    def forward(self, rates_hz: torch.Tensor) -> torch.Tensor:
        probabilities = torch.clamp(rates_hz * self.prob_scale, min=0.0, max=1.0)
        return torch.bernoulli(probabilities) * self.scale

class AlphaSynapse(nn.Module):
    def __init__(self, batch: int, size: int, dt_ms: float, params: dict[str, float], device: str) -> None:
        super().__init__()
        self.steps_delay = int(params["tDelay"] / dt_ms)
        self.batch = batch
        self.size = size
        self.device = device
        class_specs = tuple(params.get("synapse_classes", DEFAULT_SYNAPSE_CLASSES))
        self.class_names = [str(spec.get("name", f"class_{idx}")) for idx, spec in enumerate(class_specs)]
        self.class_time_factors = torch.tensor(
            [dt_ms / max(float(spec.get("tau_ms", params["tauSyn"])), dt_ms) for spec in class_specs],
            dtype=torch.float32,
            device=device,
        )
        self.class_gains = torch.tensor(
            [float(spec.get("gain", 1.0)) for spec in class_specs],
            dtype=torch.float32,
            device=device,
        )
        self.class_conductance = torch.zeros((len(self.class_names), batch, size), device=self.device)
        self.class_delay_buffer = torch.zeros((len(self.class_names), batch, self.steps_delay + 1, size), device=self.device)

    def state_init(self) -> tuple[torch.Tensor, torch.Tensor]:
        self.class_conductance.zero_()
        self.class_delay_buffer.zero_()
        conductance = torch.zeros(self.batch, self.size, device=self.device)
        delay_buffer = torch.zeros(self.batch, self.steps_delay + 1, self.size, device=self.device)
        return conductance, delay_buffer

    def forward(self, class_inputs: torch.Tensor, refrac_mask: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        refrac_mask = refrac_mask.unsqueeze(0)
        decay = (1.0 - self.class_time_factors).view(-1, 1, 1)
        delayed = self.class_delay_buffer[:, :, 0, :] * refrac_mask
        self.class_conductance = self.class_conductance * decay + delayed
        self.class_delay_buffer = torch.roll(self.class_delay_buffer, shifts=-1, dims=2)
        self.class_delay_buffer[:, :, -1, :] = class_inputs
        conductance_new = torch.sum(
            self.class_conductance * self.class_gains.view(-1, 1, 1),
            dim=0,
        )
        aggregate_delay_buffer = torch.sum(self.class_delay_buffer * self.class_gains.view(-1, 1, 1, 1), dim=0)
        return conductance_new, aggregate_delay_buffer

    def apply_spike_reset(self, spikes: torch.Tensor) -> None:
        self.class_conductance = self.class_conductance * (1.0 - spikes.unsqueeze(0))

    def class_state_summary(self) -> dict[str, float]:
        return {
            name: float(self.class_conductance[idx].abs().mean().detach().cpu().item())
            for idx, name in enumerate(self.class_names)
        }

class LIFNeuron(nn.Module):
    def __init__(self, batch: int, size: int, dt_ms: float, params: dict[str, float], device: str) -> None:
        super().__init__()
        self.batch = batch
        self.size = size
        self.time_factor = dt_ms / params["tauMem"]
        self.v_reset = params["vReset"]
        self.v_rest = params["vRest"]
        self.v_threshold = params["vThreshold"]
        self.v_0 = params["v0"]
        self.device = device

    def state_init(self) -> tuple[torch.Tensor, torch.Tensor]:
        spikes = torch.zeros(self.batch, self.size, device=self.device)
        v = torch.zeros(self.batch, self.size, device=self.device) + self.v_0
        return spikes, v

    def forward(self, input_current: torch.Tensor, v: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        v = v + self.time_factor * (input_current - (v - self.v_rest))
        spikes = (v > self.v_threshold).float()
        v = torch.where(spikes > 0, torch.full_like(v, self.v_reset), v)
        return spikes, v

class AlphaLIF(nn.Module):
    def __init__(self, batch: int, size: int, dt_ms: float, params: dict[str, float], device: str) -> None:
        super().__init__()
        self.synapse = AlphaSynapse(batch, size, dt_ms, params, device)
        self.neuron = LIFNeuron(batch, size, dt_ms, params, device)
        self.steps_refrac = int(params["tRefrac"] / dt_ms)

    def state_init(self) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        conductance, delay_buffer = self.synapse.state_init()
        spikes, v = self.neuron.state_init()
        refrac = self.steps_refrac + torch.zeros_like(v)
        return conductance, delay_buffer, spikes, v, refrac

    def forward(self, class_inputs: torch.Tensor, conductance: torch.Tensor, delay_buffer: torch.Tensor, spikes: torch.Tensor, v: torch.Tensor, refrac: torch.Tensor, direct_current: torch.Tensor | None = None) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        refrac = refrac * (1.0 - spikes)
        refrac = refrac + 1.0
        conductance_new, delay_buffer = self.synapse(class_inputs, (refrac > self.steps_refrac).float())
        neuron_input = conductance_new if direct_current is None else (conductance_new + direct_current)
        spikes, v_new = self.neuron(neuron_input, v)
        self.synapse.apply_spike_reset(spikes)
        conductance_new = torch.sum(
            self.synapse.class_conductance * self.synapse.class_gains.view(-1, 1, 1),
            dim=0,
        )
        return conductance_new, delay_buffer, spikes, v_new, refrac

class TorchWholeBrainModel(nn.Module):
    def __init__(self, size: int, dt_ms: float, params: dict[str, float], weights: torch.Tensor, device: str) -> None:
        super().__init__()
        self.neurons = AlphaLIF(1, size, dt_ms, params, device)
        self.weights = weights
        self.poisson = PoissonSpikeGenerator(dt_ms, params["scalePoisson"], device)
        self.scale = params["wScale"]

    def state_init(self) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        return self.neurons.state_init()

    def forward(
        self,
        rates_hz: torch.Tensor,
        conductance: torch.Tensor,
        delay_buffer: torch.Tensor,
        spikes: torch.Tensor,
        v: torch.Tensor,
        refrac: torch.Tensor,
        external_current: torch.Tensor | None = None,
        modulatory_current: torch.Tensor | None = None,
        class_inputs: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        if class_inputs is None:
            spikes_input = self.poisson(rates_hz)
            weighted_spikes = torch.matmul(spikes, self.weights.transpose(0, 1))
            recurrent_exc = torch.relu(weighted_spikes)
            recurrent_inh = torch.relu(-weighted_spikes)
            class_inputs = torch.stack(
                (
                    spikes_input + recurrent_exc,
                    recurrent_exc,
                    recurrent_inh,
                    recurrent_inh,
                    torch.relu(modulatory_current) if modulatory_current is not None else torch.zeros_like(rates_hz),
                ),
                dim=0,
            )
            class_inputs = self.scale * class_inputs
        return self.neurons(class_inputs, conductance, delay_buffer, spikes, v, refrac, direct_current=external_current)

    def synapse_class_summary(self) -> dict[str, float]:
        return self.neurons.synapse.class_state_summary()

@dataclass
class WholeBrainTorchBackend:
    completeness_path: str | Path
    connectivity_path: str | Path
    cache_dir: str | Path = "outputs/cache"
    device: str = "cuda:0"
    dt_ms: float = 0.1
    spontaneous_state: SpontaneousStateConfig | Mapping[str, Any] | None = None
    backend_dynamics: BackendDynamicsConfig | Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        self.completeness_path = Path(self.completeness_path)
        self.connectivity_path = Path(self.connectivity_path)
        self.cache_dir = Path(self.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        if self.device.startswith("cuda") and not torch.cuda.is_available():
            self.device = "cpu"
        if not isinstance(self.spontaneous_state, SpontaneousStateConfig):
            self.spontaneous_state = SpontaneousStateConfig.from_mapping(self.spontaneous_state)
        if not isinstance(self.backend_dynamics, BackendDynamicsConfig):
            self.backend_dynamics = BackendDynamicsConfig.from_mapping(self.backend_dynamics)
        self.flyid_to_index, self.index_to_flyid = self._load_hash_tables()
        self.spontaneous_family_groups = self._load_spontaneous_family_groups()
        self.backend_dynamics_groups = self._load_backend_dynamics_groups()
        self.weights = self._load_weights().to(device=self.device)
        self.model_params = self.backend_dynamics.default_group.to_model_params()
        self.model = TorchWholeBrainModel(self.weights.shape[0], self.dt_ms, self.model_params, self.weights, self.device)
        self._build_backend_dynamics_tensors()
        self.sensor_pool_indices = {name: self._ids_to_indices(ids) for name, ids in PUBLIC_INPUT_IDS.items()}
        monitored_ids = sorted({neuron_id for ids in MOTOR_READOUT_IDS.values() for neuron_id in ids})
        self.set_monitored_ids(monitored_ids)
        self.rates = torch.zeros(1, self.weights.shape[0], device=self.device)
        self.tonic_background_rates = torch.zeros_like(self.rates)
        self.background_rates = torch.zeros_like(self.rates)
        self.background_latent_state = torch.zeros((1, 0), device=self.device)
        self.background_latent_loadings = torch.zeros((0, self.weights.shape[0]), device=self.device)
        self.adaptation_current = torch.zeros_like(self.rates)
        self.intrinsic_noise_state = torch.zeros_like(self.rates)
        self.graded_release_state = torch.zeros_like(self.rates)
        self.intracellular_calcium_state = torch.zeros_like(self.rates)
        self.modulatory_arousal_state = torch.zeros((1, 1), device=self.device)
        self.modulatory_exafference_state = torch.zeros((1, 1), device=self.device)
        self.reset()

    @property
    def device_name(self) -> str:
        return self.device

    def _load_hash_tables(self) -> tuple[dict[int, int], dict[int, int]]:
        df = pd.read_csv(self.completeness_path, index_col=0)
        flyid_to_index = {int(flywire_id): idx for idx, flywire_id in enumerate(df.index)}
        index_to_flyid = {idx: flywire_id for flywire_id, idx in flyid_to_index.items()}
        return flyid_to_index, index_to_flyid

    def _load_weights(self) -> torch.Tensor:
        coo_path = self.cache_dir / "weight_coo.pkl"
        csr_path = self.cache_dir / "weight_csr.pkl"
        if csr_path.exists():
            with open(csr_path, "rb") as handle:
                return pickle.load(handle)
        conn = pd.read_parquet(self.connectivity_path)
        num_neurons = len(self.flyid_to_index)
        if coo_path.exists():
            with open(coo_path, "rb") as handle:
                weight_coo = pickle.load(handle)
        else:
            indices = [conn["Postsynaptic_Index"].to_list(), conn["Presynaptic_Index"].to_list()]
            values = conn["Excitatory x Connectivity"].to_list()
            weight_coo = torch.sparse_coo_tensor(indices, values, (num_neurons, num_neurons), dtype=torch.float32)
            with open(coo_path, "wb") as handle:
                pickle.dump(weight_coo, handle)
        weight_csr = weight_coo.to_sparse_csr()
        with open(csr_path, "wb") as handle:
            pickle.dump(weight_csr, handle)
        return weight_csr

    def _resolve_spontaneous_family_labels(self, annotation_table: pd.DataFrame) -> pd.Series:
        cfg = self.spontaneous_state
        cell_type = annotation_table.get("cell_type", pd.Series(index=annotation_table.index, dtype=object)).fillna("").astype(str)
        hemibrain_type = annotation_table.get("hemibrain_type", pd.Series(index=annotation_table.index, dtype=object)).fillna("").astype(str)
        super_class = annotation_table.get("super_class", pd.Series(index=annotation_table.index, dtype=object)).fillna("").astype(str)
        cell_class = annotation_table.get("cell_class", pd.Series(index=annotation_table.index, dtype=object)).fillna("").astype(str)
        cell_sub_class = annotation_table.get("cell_sub_class", pd.Series(index=annotation_table.index, dtype=object)).fillna("").astype(str)
        family_key = str(cfg.family_key).lower()
        if family_key == "cell_type":
            family = cell_type
        elif family_key == "hemibrain_type":
            family = hemibrain_type
        elif family_key == "super_class":
            family = super_class
        elif family_key == "cell_class":
            family = cell_class
        elif family_key == "cell_sub_class":
            family = cell_sub_class
        elif family_key == "auto":
            family = cell_type
            for fallback in (hemibrain_type, cell_sub_class, cell_class, super_class):
                family = family.where(family.str.len() > 0, fallback)
        else:
            raise ValueError(
                f"Unsupported spontaneous_state.family_key={cfg.family_key!r}; "
                "expected one of auto, cell_type, hemibrain_type, super_class, cell_class, cell_sub_class"
            )
        return family.fillna("").astype(str)

    def _load_spontaneous_family_groups(self) -> list[SpontaneousFamilyGroup]:
        cfg = self.spontaneous_state
        annotation_path = Path(str(cfg.annotation_path))
        if not cfg.enabled or not annotation_path.exists():
            return []
        try:
            annotation_table = load_flywire_annotation_table(annotation_path)
        except Exception:
            return []
        annotation_table = annotation_table[annotation_table["root_id"].isin(self.flyid_to_index)].copy()
        annotation_table = annotation_table[annotation_table["side"].isin(["left", "right"])].copy()
        if cfg.included_super_classes and "super_class" in annotation_table.columns:
            keep = {value.lower() for value in cfg.included_super_classes if value}
            annotation_table = annotation_table[
                annotation_table["super_class"].fillna("").astype(str).str.lower().isin(keep)
            ].copy()
        if annotation_table.empty:
            return []
        annotation_table["family"] = self._resolve_spontaneous_family_labels(annotation_table)
        annotation_table = annotation_table[annotation_table["family"].str.len() > 0].copy()
        groups: list[SpontaneousFamilyGroup] = []
        min_size = max(1, int(cfg.min_family_size_per_side))
        max_size = max(0, int(cfg.max_family_size_per_side))
        for family, group_df in annotation_table.groupby("family", sort=True):
            left_indices = tuple(
                sorted(
                    {
                        self.flyid_to_index[int(root_id)]
                        for root_id in group_df.loc[group_df["side"] == "left", "root_id"].tolist()
                        if int(root_id) in self.flyid_to_index
                    }
                )
            )
            right_indices = tuple(
                sorted(
                    {
                        self.flyid_to_index[int(root_id)]
                        for root_id in group_df.loc[group_df["side"] == "right", "root_id"].tolist()
                        if int(root_id) in self.flyid_to_index
                    }
                )
            )
            if len(left_indices) < min_size or len(right_indices) < min_size:
                continue
            if max_size > 0 and (len(left_indices) > max_size or len(right_indices) > max_size):
                continue
            groups.append(SpontaneousFamilyGroup(family=str(family), left_indices=left_indices, right_indices=right_indices))
        return groups

    def spontaneous_family_group_catalog(self) -> list[dict[str, object]]:
        return [
            {
                "family": str(group.family),
                "left_count": int(len(group.left_indices)),
                "right_count": int(len(group.right_indices)),
                "total_count": int(len(group.left_indices) + len(group.right_indices)),
                "family_key": str(self.spontaneous_state.family_key),
            }
            for group in self.spontaneous_family_groups
        ]

    def _resolve_backend_group_labels(self, annotation_table: pd.DataFrame) -> pd.Series:
        key = str(self.backend_dynamics.group_key).lower()
        available_columns = {
            "super_class": "super_class",
            "cell_class": "cell_class",
            "cell_sub_class": "cell_sub_class",
            "cell_type": "cell_type",
            "hemibrain_type": "hemibrain_type",
            "side": "side",
        }
        if key == "auto":
            for candidate in ("super_class", "cell_class", "cell_sub_class", "cell_type", "hemibrain_type", "side"):
                if candidate in annotation_table.columns:
                    series = annotation_table[candidate].fillna("").astype(str)
                    if bool((series.str.len() > 0).any()):
                        return series
            return pd.Series(["default"] * len(annotation_table), index=annotation_table.index, dtype=object)
        if key not in available_columns:
            raise ValueError(
                f"Unsupported backend_dynamics.group_key={self.backend_dynamics.group_key!r}; "
                "expected one of auto, super_class, cell_class, cell_sub_class, cell_type, hemibrain_type, side"
            )
        column = available_columns[key]
        if column not in annotation_table.columns:
            return pd.Series(["default"] * len(annotation_table), index=annotation_table.index, dtype=object)
        labels = annotation_table[column].fillna("").astype(str)
        return labels.where(labels.str.len() > 0, "default")

    def _load_backend_dynamics_groups(self) -> list[BackendDynamicsGroup]:
        cfg = self.backend_dynamics
        annotation_path = Path(str(cfg.annotation_path))
        size = len(self.flyid_to_index)
        default_group = BackendDynamicsGroup(name="default", indices=tuple(range(size)), config=cfg.default_group)
        if size == 0 or not annotation_path.exists():
            return [default_group]
        try:
            annotation_table = load_flywire_annotation_table(annotation_path)
        except Exception:
            return [default_group]
        annotation_table = annotation_table[annotation_table["root_id"].isin(self.flyid_to_index)].copy()
        if annotation_table.empty:
            return [default_group]
        annotation_table["group_label"] = self._resolve_backend_group_labels(annotation_table)
        groups: list[BackendDynamicsGroup] = []
        assigned_indices: set[int] = set()
        for label, group_df in annotation_table.groupby("group_label", sort=True):
            indices = tuple(
                sorted(
                    {
                        self.flyid_to_index[int(root_id)]
                        for root_id in group_df["root_id"].tolist()
                        if int(root_id) in self.flyid_to_index
                    }
                )
            )
            if not indices:
                continue
            assigned_indices.update(indices)
            group_cfg = cfg.groups.get(str(label), cfg.default_group)
            groups.append(BackendDynamicsGroup(name=str(label), indices=indices, config=group_cfg))
        unassigned = tuple(sorted(set(range(size)) - assigned_indices))
        if unassigned:
            groups.append(BackendDynamicsGroup(name="default", indices=unassigned, config=cfg.default_group))
        return groups or [default_group]

    def backend_dynamics_catalog(self) -> list[dict[str, object]]:
        return [
            {
                "name": str(group.name),
                "count": int(len(group.indices)),
                "release_mode": str(group.config.release_mode),
                "tau_mem_ms": float(group.config.tau_mem_ms),
                "tau_adapt_ms": float(group.config.tau_adapt_ms),
                "noise_sigma": float(group.config.noise_sigma),
                "tau_release_ms": float(group.config.tau_release_ms),
                "tau_calcium_ms": float(group.config.tau_calcium_ms),
                "calcium_spike_gain": float(group.config.calcium_spike_gain),
                "calcium_release_gain": float(group.config.calcium_release_gain),
                "calcium_adapt_gain": float(group.config.calcium_adapt_gain),
                "calcium_release_feedback_gain": float(group.config.calcium_release_feedback_gain),
            }
            for group in self.backend_dynamics_groups
        ]

    def _build_backend_dynamics_tensors(self) -> None:
        size = self.weights.shape[0]

        def _tensor_for(field_name: str, fallback: float) -> torch.Tensor:
            values = torch.full((1, size), float(fallback), device=self.device)
            for group in self.backend_dynamics_groups:
                if not group.indices:
                    continue
                values[:, list(group.indices)] = float(getattr(group.config, field_name))
            return values

        default_group = self.backend_dynamics.default_group
        self.group_v_rest_mv = _tensor_for("v_rest_mv", default_group.v_rest_mv)
        self.group_tau_adapt_ms = _tensor_for("tau_adapt_ms", default_group.tau_adapt_ms)
        self.group_adapt_a = _tensor_for("adapt_a", default_group.adapt_a)
        self.group_adapt_b = _tensor_for("adapt_b", default_group.adapt_b)
        self.group_noise_sigma = _tensor_for("noise_sigma", default_group.noise_sigma)
        self.group_noise_tau_ms = _tensor_for("noise_tau_ms", default_group.noise_tau_ms)
        self.group_tau_release_ms = _tensor_for("tau_release_ms", default_group.tau_release_ms)
        self.group_release_v_half_mv = _tensor_for("release_v_half_mv", default_group.release_v_half_mv)
        self.group_release_slope_mv = _tensor_for("release_slope_mv", default_group.release_slope_mv)
        self.group_tau_calcium_ms = _tensor_for("tau_calcium_ms", default_group.tau_calcium_ms)
        self.group_calcium_spike_gain = _tensor_for("calcium_spike_gain", default_group.calcium_spike_gain)
        self.group_calcium_release_gain = _tensor_for("calcium_release_gain", default_group.calcium_release_gain)
        self.group_calcium_adapt_gain = _tensor_for("calcium_adapt_gain", default_group.calcium_adapt_gain)
        self.group_calcium_release_feedback_gain = _tensor_for(
            "calcium_release_feedback_gain",
            default_group.calcium_release_feedback_gain,
        )
        self.group_release_gain_scale = _tensor_for("release_gain_scale", default_group.release_gain_scale)
        self.group_synaptic_gain_scale = _tensor_for("synaptic_gain_scale", default_group.synaptic_gain_scale)
        self.group_neuromod_gain_scale = _tensor_for("neuromod_gain_scale", default_group.neuromod_gain_scale)
        self.group_release_active_mask = torch.zeros((1, size), device=self.device)
        self.group_spike_recurrent_mask = torch.zeros((1, size), device=self.device)
        self.group_graded_recurrent_mask = torch.zeros((1, size), device=self.device)
        self.modulatory_population_mask = torch.zeros((1, size), device=self.device)
        modulatory_names = {value for value in self.backend_dynamics.modulatory_group_names if value}
        for group in self.backend_dynamics_groups:
            if not group.indices:
                continue
            is_modulatory_group = str(group.name).lower() in modulatory_names
            spike_active = group.config.release_mode in {"spiking", "mixed"} and not is_modulatory_group
            graded_active = group.config.release_mode in {"graded", "mixed"} and not is_modulatory_group
            release_active = group.config.release_mode in {"graded", "mixed"}
            self.group_release_active_mask[:, list(group.indices)] = 1.0 if release_active else 0.0
            self.group_spike_recurrent_mask[:, list(group.indices)] = 1.0 if spike_active else 0.0
            self.group_graded_recurrent_mask[:, list(group.indices)] = 1.0 if graded_active else 0.0
            self.modulatory_population_mask[:, list(group.indices)] = 1.0 if is_modulatory_group else 0.0
        if float(self.modulatory_population_mask.max().detach().cpu().item()) <= 0.0 and self.backend_dynamics.neuromodulation_enabled:
            self.modulatory_population_mask = self.group_release_active_mask.clone()

    def _advance_endogenous_intrinsic_current(self) -> torch.Tensor | None:
        if not self.backend_dynamics.endogenous_path_selected:
            return None
        tau_noise_ms = torch.clamp(self.group_noise_tau_ms, min=max(self.dt_ms, 1e-6))
        decay = torch.exp(torch.full_like(tau_noise_ms, -self.dt_ms) / tau_noise_ms)
        noise_scale = self.group_noise_sigma * torch.sqrt(torch.clamp(1.0 - decay * decay, min=0.0))
        self.intrinsic_noise_state = decay * self.intrinsic_noise_state + noise_scale * torch.randn_like(self.intrinsic_noise_state)
        neuromod_current = None
        if self.backend_dynamics.neuromodulation_enabled:
            neuromod_current = (
                self.modulatory_arousal_state * self.group_neuromod_gain_scale * float(self.backend_dynamics.arousal_current_gain)
            )
        total = self.intrinsic_noise_state - self.adaptation_current
        return total if neuromod_current is None else (total + neuromod_current)

    def _update_endogenous_intrinsic_state(self) -> None:
        if not self.backend_dynamics.endogenous_path_selected:
            return
        tau_adapt_ms = torch.clamp(self.group_tau_adapt_ms, min=max(self.dt_ms, 1e-6))
        decay = torch.exp(torch.full_like(tau_adapt_ms, -self.dt_ms) / tau_adapt_ms)
        voltage_drive = torch.relu(self.v - self.group_v_rest_mv)
        modulation = 1.0
        if self.backend_dynamics.neuromodulation_enabled:
            modulation = 1.0 + self.modulatory_arousal_state * self.group_neuromod_gain_scale * float(self.backend_dynamics.adaptation_mod_gain)
        calcium_drive = self.group_calcium_adapt_gain * self.intracellular_calcium_state * modulation
        self.adaptation_current = (
            decay * self.adaptation_current
            + (1.0 - decay) * (self.group_adapt_a * voltage_drive * modulation + calcium_drive)
            + self.spikes * self.group_adapt_b * modulation
        )

    def _routed_release_gain_terms(self) -> tuple[torch.Tensor, torch.Tensor]:
        release_gain = self.group_release_gain_scale
        syn_gain = self.group_synaptic_gain_scale
        calcium_feedback = 1.0 + self.group_calcium_release_feedback_gain * self.intracellular_calcium_state
        release_gain = release_gain * calcium_feedback
        if self.backend_dynamics.neuromodulation_enabled:
            release_gain = release_gain * (
                1.0 + self.modulatory_exafference_state * self.group_neuromod_gain_scale * float(self.backend_dynamics.release_mod_gain)
            )
            syn_gain = syn_gain * (
                1.0 + self.modulatory_exafference_state * self.group_neuromod_gain_scale * float(self.backend_dynamics.synaptic_mod_gain)
            )
        return release_gain, syn_gain

    def _build_routed_recurrent_class_inputs(self, rates_hz: torch.Tensor) -> torch.Tensor | None:
        if not self.backend_dynamics.endogenous_path_selected:
            return None
        spikes_input = self.model.poisson(rates_hz)
        weighted_fast = torch.matmul(self.spikes * self.group_spike_recurrent_mask, self.weights.transpose(0, 1))
        release_gain, syn_gain = self._routed_release_gain_terms()
        weighted_slow = torch.matmul(
            self.graded_release_state * self.group_graded_recurrent_mask * release_gain * syn_gain,
            self.weights.transpose(0, 1),
        )
        modulatory_source = torch.clamp(self.graded_release_state + self.intracellular_calcium_state, min=0.0)
        weighted_modulatory = torch.matmul(
            modulatory_source * self.modulatory_population_mask * release_gain * syn_gain,
            self.weights.transpose(0, 1),
        )
        class_inputs = torch.stack(
            (
                spikes_input + torch.relu(weighted_fast),
                torch.relu(weighted_slow),
                torch.relu(-weighted_fast),
                torch.relu(-weighted_slow),
                torch.relu(weighted_modulatory),
            ),
            dim=0,
        )
        return self.model.scale * class_inputs

    def _update_graded_release_state(self) -> None:
        if not self.backend_dynamics.endogenous_path_selected:
            return
        tau_release_ms = torch.clamp(self.group_tau_release_ms, min=max(self.dt_ms, 1e-6))
        decay = torch.exp(torch.full_like(tau_release_ms, -self.dt_ms) / tau_release_ms)
        slope = torch.clamp(self.group_release_slope_mv.abs(), min=1e-6)
        target = torch.sigmoid((self.v - self.group_release_v_half_mv) / slope) * self.group_release_active_mask
        self.graded_release_state = decay * self.graded_release_state + (1.0 - decay) * target

    def _update_intracellular_calcium_state(self) -> None:
        if not self.backend_dynamics.endogenous_path_selected:
            return
        tau_calcium_ms = torch.clamp(self.group_tau_calcium_ms, min=max(self.dt_ms, 1e-6))
        decay = torch.exp(torch.full_like(tau_calcium_ms, -self.dt_ms) / tau_calcium_ms)
        drive = self.spikes * self.group_calcium_spike_gain + self.graded_release_state * self.group_calcium_release_gain
        self.intracellular_calcium_state = decay * self.intracellular_calcium_state + (1.0 - decay) * drive

    def _update_neuromodulatory_state(self) -> None:
        if not self.backend_dynamics.endogenous_path_selected or not self.backend_dynamics.neuromodulation_enabled:
            return
        mask_sum = torch.clamp(self.modulatory_population_mask.sum(), min=1.0)
        modulatory_source = torch.clamp(self.graded_release_state + self.intracellular_calcium_state, min=0.0)
        drive = (modulatory_source * self.modulatory_population_mask).sum(dim=1, keepdim=True) / mask_sum

        def _advance_scalar_state(state: torch.Tensor, tau_ms: float, target: torch.Tensor) -> torch.Tensor:
            tau_ms = max(float(tau_ms), self.dt_ms)
            decay = math.exp(-self.dt_ms / tau_ms)
            return decay * state + (1.0 - decay) * target

        self.modulatory_arousal_state = _advance_scalar_state(
            self.modulatory_arousal_state,
            self.backend_dynamics.arousal_tau_ms,
            drive,
        )
        self.modulatory_exafference_state = _advance_scalar_state(
            self.modulatory_exafference_state,
            self.backend_dynamics.exafference_tau_ms,
            drive,
        )

    def _ids_to_indices(self, ids: list[int]) -> list[int]:
        return [self.flyid_to_index[int(neuron_id)] for neuron_id in ids if int(neuron_id) in self.flyid_to_index]

    def reset(self, seed: int | None = None) -> None:
        if seed is not None:
            torch.manual_seed(seed)
            if self.device.startswith("cuda"):
                torch.cuda.manual_seed_all(seed)
        self.conductance, self.delay_buffer, self.spikes, self.v, self.refrac = self.model.state_init()
        self.adaptation_current.zero_()
        self.intrinsic_noise_state.zero_()
        self.graded_release_state.zero_()
        self.intracellular_calcium_state.zero_()
        self.modulatory_arousal_state.zero_()
        self.modulatory_exafference_state.zero_()
        self.tonic_background_rates.zero_()
        self.background_rates.zero_()
        cfg = self.spontaneous_state
        if self.backend_dynamics.use_diagnostic_surrogate and cfg.tonic_enabled:
            self.tonic_background_rates = self._sample_tonic_background_rates()
        if self.backend_dynamics.use_diagnostic_surrogate and cfg.latent_enabled:
            latent_count = max(1, int(cfg.latent_count))
            self.background_latent_loadings = self._sample_latent_loadings(latent_count)
            self.background_latent_state = float(cfg.latent_ou_sigma_hz) * torch.randn((1, latent_count), device=self.device)
        else:
            self.background_latent_state = torch.zeros((1, 0), device=self.device)
            self.background_latent_loadings = torch.zeros((0, self.background_rates.shape[1]), device=self.device)
        if self.backend_dynamics.use_diagnostic_surrogate:
            self._refresh_background_rates()
        if self.backend_dynamics.use_diagnostic_surrogate and float(cfg.voltage_jitter_std_mv) > 0.0:
            self.v = self.v + float(cfg.voltage_jitter_std_mv) * torch.randn_like(self.v)

    def _sample_tonic_background_rates(self) -> torch.Tensor:
        cfg = self.spontaneous_state
        size = self.background_rates.shape[1]
        if not self.spontaneous_family_groups:
            active_fraction = float(np.clip(cfg.active_fraction, 0.0, 1.0))
            active_mask = torch.rand((1, size), device=self.device) < active_fraction
            sigma = max(float(cfg.lognormal_sigma), 1e-6)
            mean_hz = max(float(cfg.lognormal_mean_hz), 1e-6)
            mu = float(np.log(mean_hz) - 0.5 * sigma * sigma)
            sampled = torch.exp(mu + sigma * torch.randn((1, size), device=self.device))
            sampled = torch.clamp(sampled, min=0.0, max=float(cfg.max_rate_hz))
            return torch.where(active_mask, sampled, torch.zeros_like(sampled))
        rates = torch.zeros((1, size), device=self.device)
        active_fraction = float(np.clip(cfg.active_fraction, 0.0, 1.0))
        sigma = max(float(cfg.lognormal_sigma), 1e-6)
        mean_hz = max(float(cfg.lognormal_mean_hz), 1e-6)
        mu = float(np.log(mean_hz) - 0.5 * sigma * sigma)
        bilateral_coupling = float(np.clip(cfg.bilateral_coupling, 0.0, 1.0))
        family_jitter = max(0.0, float(cfg.family_rate_jitter_fraction))
        neuron_jitter = max(0.0, float(cfg.neuron_rate_jitter_fraction))
        for group in self.spontaneous_family_groups:
            if bool((torch.rand(1, device=self.device) < active_fraction).item()) is False:
                continue
            base_rate = torch.exp(torch.tensor(mu, device=self.device) + sigma * torch.randn(1, device=self.device))
            base_rate = torch.clamp(base_rate, min=0.0, max=float(cfg.max_rate_hz))
            common_scale = torch.clamp(1.0 + family_jitter * torch.randn(1, device=self.device), min=0.0)
            side_delta = (1.0 - bilateral_coupling) * family_jitter * torch.randn(1, device=self.device)
            left_rate = torch.clamp(base_rate * torch.clamp(common_scale + side_delta, min=0.0), min=0.0, max=float(cfg.max_rate_hz))
            right_rate = torch.clamp(base_rate * torch.clamp(common_scale - side_delta, min=0.0), min=0.0, max=float(cfg.max_rate_hz))
            if group.left_indices:
                left_values = left_rate * torch.clamp(
                    1.0 + neuron_jitter * torch.randn((len(group.left_indices),), device=self.device),
                    min=0.0,
                )
                rates[0, list(group.left_indices)] = torch.clamp(left_values, min=0.0, max=float(cfg.max_rate_hz))
            if group.right_indices:
                right_values = right_rate * torch.clamp(
                    1.0 + neuron_jitter * torch.randn((len(group.right_indices),), device=self.device),
                    min=0.0,
                )
                rates[0, list(group.right_indices)] = torch.clamp(right_values, min=0.0, max=float(cfg.max_rate_hz))
        return rates

    def _sample_latent_loadings(self, latent_count: int) -> torch.Tensor:
        cfg = self.spontaneous_state
        size = self.background_rates.shape[1]
        target_fraction = float(np.clip(cfg.latent_target_fraction, 0.0, 1.0))
        load_std = float(cfg.latent_loading_std_hz)
        neuron_jitter = max(0.0, float(cfg.neuron_rate_jitter_fraction))
        antisym_fraction = max(0.0, float(cfg.antisymmetric_latent_fraction))
        if not self.spontaneous_family_groups:
            loadings = load_std * torch.randn((latent_count, size), device=self.device)
            mask = (torch.rand((latent_count, size), device=self.device) < target_fraction).float()
            return loadings * mask
        loadings = torch.zeros((latent_count, size), device=self.device)
        bilateral_coupling = float(np.clip(cfg.bilateral_coupling, 0.0, 1.0))
        for latent_index in range(latent_count):
            for group in self.spontaneous_family_groups:
                if bool((torch.rand(1, device=self.device) < target_fraction).item()) is False:
                    continue
                common_loading = load_std * torch.randn(1, device=self.device)
                antisym_loading = load_std * antisym_fraction * (1.0 - bilateral_coupling) * torch.randn(1, device=self.device)
                left_loading = common_loading + antisym_loading
                right_loading = common_loading - antisym_loading
                if group.left_indices:
                    left_values = left_loading * (
                        1.0 + neuron_jitter * torch.randn((len(group.left_indices),), device=self.device)
                    )
                    loadings[latent_index, list(group.left_indices)] = left_values
                if group.right_indices:
                    right_values = right_loading * (
                        1.0 + neuron_jitter * torch.randn((len(group.right_indices),), device=self.device)
                    )
                    loadings[latent_index, list(group.right_indices)] = right_values
        return loadings

    def _refresh_background_rates(self) -> None:
        cfg = self.spontaneous_state
        self.background_rates = self.tonic_background_rates.clone()
        if cfg.latent_enabled and self.background_latent_state.numel() and self.background_latent_loadings.numel():
            self.background_rates = self.background_rates + torch.matmul(self.background_latent_state, self.background_latent_loadings)
        if cfg.max_rate_hz > 0.0:
            self.background_rates = torch.clamp(self.background_rates, min=0.0, max=float(cfg.max_rate_hz))

    def _advance_background_state(self, window_steps: int) -> None:
        cfg = self.spontaneous_state
        if not cfg.latent_enabled or not self.background_latent_state.numel():
            self._refresh_background_rates()
            return
        dt_s = max(1, int(window_steps)) * (self.dt_ms / 1000.0)
        tau_s = max(float(cfg.latent_ou_tau_s), 1e-6)
        decay = math.exp(-dt_s / tau_s)
        stationary_std = float(cfg.latent_ou_sigma_hz)
        noise_scale = stationary_std * math.sqrt(max(0.0, 1.0 - decay * decay))
        self.background_latent_state = decay * self.background_latent_state + noise_scale * torch.randn_like(self.background_latent_state)
        self._refresh_background_rates()

    def set_monitored_ids(self, neuron_ids: list[int]) -> None:
        monitored_ids = sorted({int(neuron_id) for neuron_id in neuron_ids if int(neuron_id) in self.flyid_to_index})
        self.monitored_ids = monitored_ids
        self.monitored_indices = torch.tensor(self._ids_to_indices(monitored_ids), device=self.device, dtype=torch.long)

    def _build_inputs(
        self,
        sensor_pool_rates: Mapping[str, float],
        direct_input_rates_hz: Mapping[int, float] | None,
        direct_current_by_id: Mapping[int, float] | None,
        *,
        window_steps: int,
    ) -> tuple[torch.Tensor, torch.Tensor | None]:
        self.rates.zero_()
        if self.backend_dynamics.use_diagnostic_surrogate and self.spontaneous_state.enabled:
            self._advance_background_state(window_steps)
            self.rates += self.background_rates
        public_input_rates = collapse_sensor_pool_rates(dict(sensor_pool_rates))
        for pool_name, rate_hz in public_input_rates.items():
            indices = self.sensor_pool_indices.get(pool_name)
            if indices:
                self.rates[:, indices] += float(rate_hz)
        for neuron_id, rate_hz in (direct_input_rates_hz or {}).items():
            index = self.flyid_to_index.get(int(neuron_id))
            if index is not None:
                self.rates[:, index] += float(rate_hz)
        external_current = None
        if direct_current_by_id:
            external_current = torch.zeros_like(self.rates)
            for neuron_id, current in direct_current_by_id.items():
                index = self.flyid_to_index.get(int(neuron_id))
                if index is not None:
                    external_current[:, index] += float(current)
        return self.rates, external_current

    def state_summary(self) -> dict[str, float]:
        spike_fraction = float(self.spikes.mean().detach().cpu().item())
        mean_voltage = float(self.v.mean().detach().cpu().item())
        std_voltage = float(self.v.std(unbiased=False).detach().cpu().item())
        mean_conductance = float(self.conductance.mean().detach().cpu().item())
        std_conductance = float(self.conductance.std(unbiased=False).detach().cpu().item())
        latent_mean_abs_hz = float(self.background_latent_state.abs().mean().detach().cpu().item()) if self.background_latent_state.numel() else 0.0
        latent_std_hz = float(self.background_latent_state.std(unbiased=False).detach().cpu().item()) if self.background_latent_state.numel() else 0.0
        background_mean_hz = float(self.background_rates.mean().detach().cpu().item())
        background_active_fraction = float((self.background_rates > 0.0).float().mean().detach().cpu().item())
        adaptation_mean_abs = float(self.adaptation_current.abs().mean().detach().cpu().item())
        noise_mean_abs = float(self.intrinsic_noise_state.abs().mean().detach().cpu().item())
        graded_release_mean = float(self.graded_release_state.mean().detach().cpu().item())
        intracellular_calcium_mean = float(self.intracellular_calcium_state.mean().detach().cpu().item())
        synapse_class_summary = self.model.synapse_class_summary()
        modulatory_arousal_mean = float(self.modulatory_arousal_state.mean().detach().cpu().item())
        modulatory_exafference_mean = float(self.modulatory_exafference_state.mean().detach().cpu().item())
        return {
            "global_spike_fraction": spike_fraction,
            "global_mean_voltage": mean_voltage,
            "global_voltage_std": std_voltage,
            "global_mean_conductance": mean_conductance,
            "global_conductance_std": std_conductance,
            "background_mean_rate_hz": background_mean_hz,
            "background_active_fraction": background_active_fraction,
            "background_latent_mean_abs_hz": latent_mean_abs_hz,
            "background_latent_std_hz": latent_std_hz,
            "background_family_group_count": float(len(self.spontaneous_family_groups)),
            "background_structured_family_mode": float(1.0 if bool(self.spontaneous_family_groups) else 0.0),
            "background_super_class_filter_active": float(1.0 if bool(self.spontaneous_state.included_super_classes) else 0.0),
            "intrinsic_adaptation_mean_abs": adaptation_mean_abs,
            "intrinsic_noise_mean_abs": noise_mean_abs,
            "graded_release_mean": graded_release_mean,
            "intracellular_calcium_mean": intracellular_calcium_mean,
            "synapse_fast_exc_mean_abs": float(synapse_class_summary.get("fast_exc", 0.0)),
            "synapse_slow_exc_mean_abs": float(synapse_class_summary.get("slow_exc", 0.0)),
            "synapse_fast_inh_mean_abs": float(synapse_class_summary.get("fast_inh", 0.0)),
            "synapse_slow_inh_mean_abs": float(synapse_class_summary.get("slow_inh", 0.0)),
            "synapse_modulatory_mean_abs": float(synapse_class_summary.get("modulatory", 0.0)),
            "modulatory_arousal_mean": modulatory_arousal_mean,
            "modulatory_exafference_mean": modulatory_exafference_mean,
            "routed_fast_source_fraction": float(self.group_spike_recurrent_mask.mean().detach().cpu().item()),
            "routed_slow_source_fraction": float(self.group_graded_recurrent_mask.mean().detach().cpu().item()),
            "routed_modulatory_source_fraction": float(self.modulatory_population_mask.mean().detach().cpu().item()),
            "backend_dynamics_group_count": float(len(self.backend_dynamics_groups)),
            "backend_dynamics_grouped_mode_active": float(1.0 if self.backend_dynamics.mode == "grouped_glif_scaffold" else 0.0),
            "diagnostic_spontaneous_surrogate_active": float(
                1.0 if self.backend_dynamics.use_diagnostic_surrogate and self.spontaneous_state.enabled else 0.0
            ),
            "endogenous_spontaneous_path_selected": float(1.0 if self.backend_dynamics.endogenous_path_selected else 0.0),
        }

    def _run_steps(
        self,
        sensor_pool_rates: Mapping[str, float],
        *,
        num_steps: int,
        direct_input_rates_hz: Mapping[int, float] | None,
        direct_current_by_id: Mapping[int, float] | None,
        collect_state: bool,
    ) -> tuple[dict[int, float], dict[int, float] | None, dict[int, float] | None]:
        rates, external_current = self._build_inputs(
            sensor_pool_rates,
            direct_input_rates_hz,
            direct_current_by_id,
            window_steps=num_steps,
        )
        spike_counts = torch.zeros(len(self.monitored_ids), device=self.device)
        voltage_sums = torch.zeros(len(self.monitored_ids), device=self.device) if collect_state else None
        conductance_sums = torch.zeros(len(self.monitored_ids), device=self.device) if collect_state else None
        for _ in range(max(1, int(num_steps))):
            step_external_current = external_current
            intrinsic_current = self._advance_endogenous_intrinsic_current()
            if intrinsic_current is not None:
                step_external_current = intrinsic_current if step_external_current is None else (step_external_current + intrinsic_current)
            routed_class_inputs = self._build_routed_recurrent_class_inputs(rates)
            self.conductance, self.delay_buffer, self.spikes, self.v, self.refrac = self.model(
                rates,
                self.conductance,
                self.delay_buffer,
                self.spikes,
                self.v,
                self.refrac,
                external_current=step_external_current,
                class_inputs=routed_class_inputs,
            )
            self._update_endogenous_intrinsic_state()
            self._update_graded_release_state()
            self._update_intracellular_calcium_state()
            self._update_neuromodulatory_state()
            spike_counts += self.spikes[0, self.monitored_indices]
            if collect_state and voltage_sums is not None and conductance_sums is not None:
                voltage_sums += self.v[0, self.monitored_indices]
                conductance_sums += self.conductance[0, self.monitored_indices]
        window_seconds = max(1, int(num_steps)) * (self.dt_ms / 1000.0)
        firing_rates = (spike_counts / window_seconds).detach().cpu().tolist()
        firing_rate_by_id = {neuron_id: float(rate) for neuron_id, rate in zip(self.monitored_ids, firing_rates)}
        if not collect_state or voltage_sums is None or conductance_sums is None:
            return firing_rate_by_id, None, None
        mean_voltage = (voltage_sums / max(1, int(num_steps))).detach().cpu().tolist()
        mean_conductance = (conductance_sums / max(1, int(num_steps))).detach().cpu().tolist()
        return (
            firing_rate_by_id,
            {neuron_id: float(value) for neuron_id, value in zip(self.monitored_ids, mean_voltage)},
            {neuron_id: float(value) for neuron_id, value in zip(self.monitored_ids, mean_conductance)},
        )

    def step(
        self,
        sensor_pool_rates: Mapping[str, float],
        num_steps: int = 1,
        direct_input_rates_hz: Mapping[int, float] | None = None,
        direct_current_by_id: Mapping[int, float] | None = None,
    ) -> dict[int, float]:
        firing_rates, _, _ = self._run_steps(
            sensor_pool_rates,
            num_steps=num_steps,
            direct_input_rates_hz=direct_input_rates_hz,
            direct_current_by_id=direct_current_by_id,
            collect_state=False,
        )
        return firing_rates

    def step_with_state(
        self,
        sensor_pool_rates: Mapping[str, float],
        num_steps: int = 1,
        direct_input_rates_hz: Mapping[int, float] | None = None,
        direct_current_by_id: Mapping[int, float] | None = None,
    ) -> tuple[dict[int, float], dict[int, float], dict[int, float]]:
        firing_rates, mean_voltage, mean_conductance = self._run_steps(
            sensor_pool_rates,
            num_steps=num_steps,
            direct_input_rates_hz=direct_input_rates_hz,
            direct_current_by_id=direct_current_by_id,
            collect_state=True,
        )
        return firing_rates, mean_voltage or {}, mean_conductance or {}

    def benchmark(self, sensor_pool_rates: Mapping[str, float], sim_seconds: float) -> dict[str, float]:
        num_steps = int(sim_seconds * 1000.0 / self.dt_ms)
        self.reset()
        wall_start = perf_counter()
        self.step(sensor_pool_rates, num_steps=num_steps)
        wall_seconds = perf_counter() - wall_start
        return {
            "wall_seconds": wall_seconds,
            "sim_seconds": sim_seconds,
            "real_time_factor": sim_seconds / wall_seconds if wall_seconds else float("inf"),
        }
