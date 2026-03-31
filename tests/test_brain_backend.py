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


def test_torch_model_populates_multiple_synapse_classes() -> None:
    params = dict(MODEL_PARAMS)
    params["tDelay"] = 0.0
    params["tRefrac"] = 0.0
    params["vThreshold"] = 1e6
    model = TorchWholeBrainModel(
        size=2,
        dt_ms=0.1,
        params=params,
        weights=torch.tensor([[0.0, 20.0], [-30.0, 0.0]], dtype=torch.float32),
        device="cpu",
    )
    conductance, delay_buffer, spikes, v, refrac = model.state_init()
    rates = torch.tensor([[20000.0, 0.0]], dtype=torch.float32)
    spikes = torch.tensor([[1.0, 1.0]], dtype=torch.float32)
    modulatory_current = torch.tensor([[100.0, 50.0]], dtype=torch.float32)

    conductance, delay_buffer, spikes, v, refrac = model(
        rates,
        conductance,
        delay_buffer,
        spikes,
        v,
        refrac,
        modulatory_current=modulatory_current,
    )
    conductance, delay_buffer, spikes, v, refrac = model(
        rates,
        conductance,
        delay_buffer,
        spikes,
        v,
        refrac,
        modulatory_current=modulatory_current,
    )
    summary = model.synapse_class_summary()

    assert summary["fast_exc"] > 0.0
    assert summary["slow_exc"] > 0.0
    assert summary["fast_inh"] > 0.0
    assert summary["slow_inh"] > 0.0
    assert summary["modulatory"] > 0.0


def test_torch_model_accepts_precomputed_routed_class_inputs() -> None:
    params = dict(MODEL_PARAMS)
    params["tDelay"] = 0.0
    params["tRefrac"] = 0.0
    params["vThreshold"] = 1e6
    model = TorchWholeBrainModel(
        size=2,
        dt_ms=0.1,
        params=params,
        weights=torch.zeros((2, 2), dtype=torch.float32),
        device="cpu",
    )
    conductance, delay_buffer, spikes, v, refrac = model.state_init()
    rates = torch.zeros((1, 2), dtype=torch.float32)
    class_inputs = torch.stack(
        (
            torch.tensor([[100.0, 0.0]], dtype=torch.float32),
            torch.tensor([[50.0, 0.0]], dtype=torch.float32),
            torch.tensor([[0.0, 25.0]], dtype=torch.float32),
            torch.tensor([[0.0, 10.0]], dtype=torch.float32),
            torch.tensor([[5.0, 2.0]], dtype=torch.float32),
        ),
        dim=0,
    )

    conductance, delay_buffer, spikes, v, refrac = model(
        rates,
        conductance,
        delay_buffer,
        spikes,
        v,
        refrac,
        class_inputs=class_inputs,
    )
    conductance, delay_buffer, spikes, v, refrac = model(
        rates,
        conductance,
        delay_buffer,
        spikes,
        v,
        refrac,
        class_inputs=class_inputs,
    )
    summary = model.synapse_class_summary()

    assert summary["fast_exc"] > 0.0
    assert summary["slow_exc"] > 0.0
    assert summary["fast_inh"] > 0.0
    assert summary["slow_inh"] > 0.0
    assert summary["modulatory"] > 0.0
