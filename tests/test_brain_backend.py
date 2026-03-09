from __future__ import annotations

import torch

from brain.pytorch_backend import MODEL_PARAMS, PoissonSpikeGenerator, TorchWholeBrainModel


def test_poisson_spike_generator_clamps_invalid_probabilities() -> None:
    generator = PoissonSpikeGenerator(dt_ms=0.1, scale=250.0, device="cpu")
    rates = torch.tensor([[-50.0, 5000.0, 20000.0]], dtype=torch.float32)

    spikes = generator(rates)

    assert spikes.shape == rates.shape
    assert float(spikes[0, 0]) == 0.0
    assert float(spikes[0, 1]) in {0.0, 250.0}
    assert float(spikes[0, 2]) == 250.0


def test_torch_model_accepts_signed_external_current() -> None:
    params = dict(MODEL_PARAMS)
    params["tDelay"] = 0.0
    model = TorchWholeBrainModel(
        size=1,
        dt_ms=0.1,
        params=params,
        weights=torch.zeros((1, 1), dtype=torch.float32),
        device="cpu",
    )
    conductance, delay_buffer, spikes, v, refrac = model.state_init()
    rates = torch.zeros((1, 1), dtype=torch.float32)
    external_current = torch.tensor([[2000.0]], dtype=torch.float32)

    conductance, delay_buffer, spikes, v, refrac = model(
        rates,
        conductance,
        delay_buffer,
        spikes,
        v,
        refrac,
        external_current=external_current,
    )
    conductance, delay_buffer, spikes, v, refrac = model(
        rates,
        conductance,
        delay_buffer,
        spikes,
        v,
        refrac,
        external_current=external_current,
    )
    _, _, spikes, _, _ = model(
        rates,
        conductance,
        delay_buffer,
        spikes,
        v,
        refrac,
        external_current=external_current,
    )

    assert float(spikes[0, 0]) == 1.0


def test_torch_model_negative_external_current_hyperpolarizes_without_spiking() -> None:
    params = dict(MODEL_PARAMS)
    params["tDelay"] = 0.0
    model = TorchWholeBrainModel(
        size=1,
        dt_ms=0.1,
        params=params,
        weights=torch.zeros((1, 1), dtype=torch.float32),
        device="cpu",
    )
    conductance, delay_buffer, spikes, v, refrac = model.state_init()
    rates = torch.zeros((1, 1), dtype=torch.float32)
    external_current = torch.tensor([[-200.0]], dtype=torch.float32)

    conductance, delay_buffer, spikes, v, refrac = model(
        rates,
        conductance,
        delay_buffer,
        spikes,
        v,
        refrac,
        external_current=external_current,
    )
    conductance, delay_buffer, spikes, v, refrac = model(
        rates,
        conductance,
        delay_buffer,
        spikes,
        v,
        refrac,
        external_current=external_current,
    )
    _, _, spikes, v, _ = model(
        rates,
        conductance,
        delay_buffer,
        spikes,
        v,
        refrac,
        external_current=external_current,
    )

    assert float(spikes[0, 0]) == 0.0
    assert float(v[0, 0]) < MODEL_PARAMS["vRest"]
