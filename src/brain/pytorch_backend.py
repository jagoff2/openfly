from __future__ import annotations

import math
import pickle
from dataclasses import dataclass
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
        self.time_factor = dt_ms / params["tauSyn"]
        self.steps_delay = int(params["tDelay"] / dt_ms)
        self.batch = batch
        self.size = size
        self.device = device

    def state_init(self) -> tuple[torch.Tensor, torch.Tensor]:
        conductance = torch.zeros(self.batch, self.size, device=self.device)
        delay_buffer = torch.zeros(self.batch, self.steps_delay + 1, self.size, device=self.device)
        return conductance, delay_buffer

    def forward(self, input_current: torch.Tensor, conductance: torch.Tensor, delay_buffer: torch.Tensor, refrac_mask: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        conductance_new = conductance * (1.0 - self.time_factor) + delay_buffer[:, 0, :] * refrac_mask
        delay_buffer = torch.roll(delay_buffer, shifts=-1, dims=1)
        delay_buffer[:, -1, :] = input_current
        return conductance_new, delay_buffer

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

    def forward(self, input_current: torch.Tensor, conductance: torch.Tensor, delay_buffer: torch.Tensor, spikes: torch.Tensor, v: torch.Tensor, refrac: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        refrac = refrac * (1.0 - spikes)
        refrac = refrac + 1.0
        conductance_new, delay_buffer = self.synapse(input_current, conductance, delay_buffer, (refrac > self.steps_refrac).float())
        spikes, v_new = self.neuron(conductance, v)
        conductance_new = conductance_new - (conductance_new * spikes).detach()
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
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        spikes_input = self.poisson(rates_hz)
        weighted_spikes = torch.matmul(spikes, self.weights.transpose(0, 1))
        total_current = self.scale * (spikes_input + weighted_spikes)
        if external_current is not None:
            total_current = total_current + external_current
        return self.neurons(total_current, conductance, delay_buffer, spikes, v, refrac)

@dataclass
class WholeBrainTorchBackend:
    completeness_path: str | Path
    connectivity_path: str | Path
    cache_dir: str | Path = "outputs/cache"
    device: str = "cuda:0"
    dt_ms: float = 0.1
    spontaneous_state: SpontaneousStateConfig | Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        self.completeness_path = Path(self.completeness_path)
        self.connectivity_path = Path(self.connectivity_path)
        self.cache_dir = Path(self.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        if self.device.startswith("cuda") and not torch.cuda.is_available():
            self.device = "cpu"
        if not isinstance(self.spontaneous_state, SpontaneousStateConfig):
            self.spontaneous_state = SpontaneousStateConfig.from_mapping(self.spontaneous_state)
        self.flyid_to_index, self.index_to_flyid = self._load_hash_tables()
        self.spontaneous_family_groups = self._load_spontaneous_family_groups()
        self.weights = self._load_weights().to(device=self.device)
        self.model = TorchWholeBrainModel(self.weights.shape[0], self.dt_ms, MODEL_PARAMS, self.weights, self.device)
        self.sensor_pool_indices = {name: self._ids_to_indices(ids) for name, ids in PUBLIC_INPUT_IDS.items()}
        monitored_ids = sorted({neuron_id for ids in MOTOR_READOUT_IDS.values() for neuron_id in ids})
        self.set_monitored_ids(monitored_ids)
        self.rates = torch.zeros(1, self.weights.shape[0], device=self.device)
        self.tonic_background_rates = torch.zeros_like(self.rates)
        self.background_rates = torch.zeros_like(self.rates)
        self.background_latent_state = torch.zeros((1, 0), device=self.device)
        self.background_latent_loadings = torch.zeros((0, self.weights.shape[0]), device=self.device)
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

    def _ids_to_indices(self, ids: list[int]) -> list[int]:
        return [self.flyid_to_index[int(neuron_id)] for neuron_id in ids if int(neuron_id) in self.flyid_to_index]

    def reset(self, seed: int | None = None) -> None:
        if seed is not None:
            torch.manual_seed(seed)
            if self.device.startswith("cuda"):
                torch.cuda.manual_seed_all(seed)
        self.conductance, self.delay_buffer, self.spikes, self.v, self.refrac = self.model.state_init()
        self.tonic_background_rates.zero_()
        self.background_rates.zero_()
        cfg = self.spontaneous_state
        if cfg.tonic_enabled:
            self.tonic_background_rates = self._sample_tonic_background_rates()
        if cfg.latent_enabled:
            latent_count = max(1, int(cfg.latent_count))
            self.background_latent_loadings = self._sample_latent_loadings(latent_count)
            self.background_latent_state = float(cfg.latent_ou_sigma_hz) * torch.randn((1, latent_count), device=self.device)
        else:
            self.background_latent_state = torch.zeros((1, 0), device=self.device)
            self.background_latent_loadings = torch.zeros((0, self.background_rates.shape[1]), device=self.device)
        self._refresh_background_rates()
        if float(cfg.voltage_jitter_std_mv) > 0.0:
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
        if self.spontaneous_state.enabled:
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
            self.conductance, self.delay_buffer, self.spikes, self.v, self.refrac = self.model(
                rates,
                self.conductance,
                self.delay_buffer,
                self.spikes,
                self.v,
                self.refrac,
                external_current=external_current,
            )
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
