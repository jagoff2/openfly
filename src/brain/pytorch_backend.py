from __future__ import annotations

import pickle
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Mapping

import pandas as pd
import torch
import torch.nn as nn

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

    def __post_init__(self) -> None:
        self.completeness_path = Path(self.completeness_path)
        self.connectivity_path = Path(self.connectivity_path)
        self.cache_dir = Path(self.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        if self.device.startswith("cuda") and not torch.cuda.is_available():
            self.device = "cpu"
        self.flyid_to_index, self.index_to_flyid = self._load_hash_tables()
        self.weights = self._load_weights().to(device=self.device)
        self.model = TorchWholeBrainModel(self.weights.shape[0], self.dt_ms, MODEL_PARAMS, self.weights, self.device)
        self.sensor_pool_indices = {name: self._ids_to_indices(ids) for name, ids in PUBLIC_INPUT_IDS.items()}
        monitored_ids = sorted({neuron_id for ids in MOTOR_READOUT_IDS.values() for neuron_id in ids})
        self.set_monitored_ids(monitored_ids)
        self.rates = torch.zeros(1, self.weights.shape[0], device=self.device)
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

    def _ids_to_indices(self, ids: list[int]) -> list[int]:
        return [self.flyid_to_index[int(neuron_id)] for neuron_id in ids if int(neuron_id) in self.flyid_to_index]

    def reset(self, seed: int | None = None) -> None:
        if seed is not None:
            torch.manual_seed(seed)
            if self.device.startswith("cuda"):
                torch.cuda.manual_seed_all(seed)
        self.conductance, self.delay_buffer, self.spikes, self.v, self.refrac = self.model.state_init()

    def set_monitored_ids(self, neuron_ids: list[int]) -> None:
        monitored_ids = sorted({int(neuron_id) for neuron_id in neuron_ids if int(neuron_id) in self.flyid_to_index})
        self.monitored_ids = monitored_ids
        self.monitored_indices = torch.tensor(self._ids_to_indices(monitored_ids), device=self.device, dtype=torch.long)

    def _build_inputs(
        self,
        sensor_pool_rates: Mapping[str, float],
        direct_input_rates_hz: Mapping[int, float] | None,
        direct_current_by_id: Mapping[int, float] | None,
    ) -> tuple[torch.Tensor, torch.Tensor | None]:
        self.rates.zero_()
        public_input_rates = collapse_sensor_pool_rates(dict(sensor_pool_rates))
        for pool_name, rate_hz in public_input_rates.items():
            indices = self.sensor_pool_indices.get(pool_name)
            if indices:
                self.rates[:, indices] = float(rate_hz)
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

    def _run_steps(
        self,
        sensor_pool_rates: Mapping[str, float],
        *,
        num_steps: int,
        direct_input_rates_hz: Mapping[int, float] | None,
        direct_current_by_id: Mapping[int, float] | None,
        collect_state: bool,
    ) -> tuple[dict[int, float], dict[int, float] | None, dict[int, float] | None]:
        rates, external_current = self._build_inputs(sensor_pool_rates, direct_input_rates_hz, direct_current_by_id)
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
        wall_start = perf_counter()
        self.step(sensor_pool_rates, num_steps=num_steps)
        wall_seconds = perf_counter() - wall_start
        return {
            "wall_seconds": wall_seconds,
            "sim_seconds": sim_seconds,
            "real_time_factor": sim_seconds / wall_seconds if wall_seconds else float("inf"),
        }
