from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pandas as pd
import pytest
import torch

from brain.flywire_annotations import load_flywire_annotation_table
from brain.pytorch_backend import MODEL_PARAMS, SpontaneousFamilyGroup, WholeBrainTorchBackend
from runtime.closed_loop import build_brain_backend, load_config


def _build_small_backend(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    *,
    spontaneous_state: dict | None = None,
    backend_dynamics: dict | None = None,
    family_groups: list[SpontaneousFamilyGroup] | None = None,
    dt_ms: float = 0.1,
) -> WholeBrainTorchBackend:
    flyid_to_index = {1001: 0, 1002: 1, 1003: 2, 1004: 3}
    index_to_flyid = {index: neuron_id for neuron_id, index in flyid_to_index.items()}
    weights = torch.tensor(
        [
            [0.0, 55.0, -40.0, 0.0],
            [50.0, 0.0, 0.0, -35.0],
            [-32.0, 0.0, 0.0, 45.0],
            [0.0, -28.0, 48.0, 0.0],
        ],
        dtype=torch.float32,
    )

    monkeypatch.setattr(WholeBrainTorchBackend, "_load_hash_tables", lambda self: (flyid_to_index, index_to_flyid))
    monkeypatch.setattr(WholeBrainTorchBackend, "_load_spontaneous_family_groups", lambda self: family_groups or [])
    monkeypatch.setattr(WholeBrainTorchBackend, "_load_weights", lambda self: weights)

    backend = WholeBrainTorchBackend(
        completeness_path="unused.csv",
        connectivity_path="unused.parquet",
        cache_dir=tmp_path / "cache",
        device="cpu",
        dt_ms=dt_ms,
        spontaneous_state=spontaneous_state,
        backend_dynamics=backend_dynamics,
    )
    backend.set_monitored_ids(list(flyid_to_index))
    return backend


def test_backend_without_spontaneous_state_remains_quiescent(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    backend = _build_small_backend(monkeypatch, tmp_path)

    backend.reset(seed=0)
    firing_rates = backend.step({}, num_steps=100)
    summary = backend.state_summary()

    assert all(rate == 0.0 for rate in firing_rates.values())
    assert summary["global_spike_fraction"] == 0.0
    assert summary["background_mean_rate_hz"] == 0.0
    assert summary["background_active_fraction"] == 0.0
    assert summary["global_mean_voltage"] == pytest.approx(MODEL_PARAMS["vRest"])


def test_spontaneous_state_reset_is_seed_reproducible(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    config = {
        "mode": "sparse_lognormal_poisson",
        "active_fraction": 0.5,
        "lognormal_mean_hz": 0.8,
        "lognormal_sigma": 0.7,
        "max_rate_hz": 4.0,
        "voltage_jitter_std_mv": 0.35,
    }
    backend = _build_small_backend(monkeypatch, tmp_path, spontaneous_state=config)

    backend.reset(seed=7)
    first_background = backend.background_rates.clone()
    first_voltage = backend.v.clone()

    backend.reset(seed=7)
    second_background = backend.background_rates.clone()
    second_voltage = backend.v.clone()

    backend.reset(seed=8)
    third_background = backend.background_rates.clone()

    assert torch.equal(first_background, second_background)
    assert torch.equal(first_voltage, second_voltage)
    assert not torch.equal(first_background, third_background)


def test_spontaneous_state_generates_bounded_activity(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    config = {
        "mode": "sparse_lognormal_poisson",
        "active_fraction": 1.0,
        "lognormal_mean_hz": 30.0,
        "lognormal_sigma": 0.25,
        "max_rate_hz": 60.0,
        "voltage_jitter_std_mv": 0.2,
    }
    backend = _build_small_backend(monkeypatch, tmp_path, spontaneous_state=config)

    backend.reset(seed=3)
    firing_rates = backend.step({}, num_steps=1000)
    summary = backend.state_summary()

    assert any(rate > 0.0 for rate in firing_rates.values())
    assert 0.0 < summary["background_mean_rate_hz"] <= config["max_rate_hz"]
    assert summary["global_spike_fraction"] >= 0.0
    assert summary["global_spike_fraction"] <= 1.0
    assert torch.isfinite(backend.v).all()
    assert torch.isfinite(backend.conductance).all()
    assert summary["global_voltage_std"] > 0.0


def test_latent_spontaneous_state_changes_background_between_windows(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    config = {
        "mode": "sparse_lognormal_latent_ou",
        "active_fraction": 0.6,
        "lognormal_mean_hz": 8.0,
        "lognormal_sigma": 0.2,
        "max_rate_hz": 20.0,
        "latent_count": 2,
        "latent_target_fraction": 1.0,
        "latent_loading_std_hz": 1.5,
        "latent_ou_tau_s": 0.2,
        "latent_ou_sigma_hz": 1.0,
    }
    backend = _build_small_backend(monkeypatch, tmp_path, spontaneous_state=config)

    backend.reset(seed=11)
    initial_background = backend.background_rates.clone()
    backend.step({}, num_steps=50)
    first_background = backend.background_rates.clone()
    backend.step({}, num_steps=50)
    second_background = backend.background_rates.clone()

    assert not torch.equal(initial_background, first_background)
    assert not torch.equal(first_background, second_background)
    assert torch.all(first_background >= 0.0)
    assert torch.all(second_background >= 0.0)
    assert torch.all(first_background <= config["max_rate_hz"])
    assert torch.all(second_background <= config["max_rate_hz"])


def test_bilateral_family_structured_background_stays_balanced_at_reset(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    config = {
        "mode": "sparse_lognormal_latent_ou",
        "active_fraction": 1.0,
        "lognormal_mean_hz": 5.0,
        "lognormal_sigma": 0.1,
        "max_rate_hz": 12.0,
        "latent_count": 2,
        "latent_target_fraction": 1.0,
        "latent_loading_std_hz": 0.5,
        "latent_ou_tau_s": 1.0,
        "latent_ou_sigma_hz": 0.3,
        "bilateral_coupling": 1.0,
        "family_rate_jitter_fraction": 0.0,
        "neuron_rate_jitter_fraction": 0.0,
        "antisymmetric_latent_fraction": 0.0,
    }
    family_groups = [
        SpontaneousFamilyGroup(family="fam_a", left_indices=(0,), right_indices=(1,)),
        SpontaneousFamilyGroup(family="fam_b", left_indices=(2,), right_indices=(3,)),
    ]
    backend = _build_small_backend(monkeypatch, tmp_path, spontaneous_state=config, family_groups=family_groups)

    backend.reset(seed=5)

    assert float(backend.background_rates[0, 0]) == pytest.approx(float(backend.background_rates[0, 1]))
    assert float(backend.background_rates[0, 2]) == pytest.approx(float(backend.background_rates[0, 3]))


def test_build_brain_backend_passes_spontaneous_state_config(monkeypatch: pytest.MonkeyPatch) -> None:
    import brain.pytorch_backend as pytorch_backend_module

    captured: dict[str, object] = {}

    class FakeBackend:
        def __init__(self, **kwargs) -> None:
            captured.update(kwargs)

    monkeypatch.setattr(pytorch_backend_module, "WholeBrainTorchBackend", FakeBackend)
    config = deepcopy(load_config("configs/mock_multidrive_torch.yaml"))
    config.setdefault("brain", {})["spontaneous_state"] = {
        "mode": "sparse_lognormal_poisson",
        "active_fraction": 0.03,
        "lognormal_mean_hz": 0.7,
        "lognormal_sigma": 0.9,
        "max_rate_hz": 5.0,
        "voltage_jitter_std_mv": 0.5,
    }

    backend = build_brain_backend("flygym", config)

    assert isinstance(backend, FakeBackend)
    assert captured["spontaneous_state"] == config["brain"]["spontaneous_state"]


def test_build_brain_backend_passes_backend_dynamics_config(monkeypatch: pytest.MonkeyPatch) -> None:
    import brain.pytorch_backend as pytorch_backend_module

    captured: dict[str, object] = {}

    class FakeBackend:
        def __init__(self, **kwargs) -> None:
            captured.update(kwargs)

    monkeypatch.setattr(pytorch_backend_module, "WholeBrainTorchBackend", FakeBackend)
    config = deepcopy(load_config("configs/mock_multidrive_torch.yaml"))
    config.setdefault("brain", {})["backend_dynamics"] = {
        "mode": "grouped_glif_scaffold",
        "spontaneous_source": "endogenous",
        "group_key": "super_class",
        "default_group": {
            "tau_mem_ms": 25.0,
            "tau_adapt_ms": 90.0,
            "noise_sigma": 0.2,
            "release_mode": "mixed",
        },
    }

    backend = build_brain_backend("flygym", config)

    assert isinstance(backend, FakeBackend)
    assert captured["backend_dynamics"] == config["brain"]["backend_dynamics"]


def test_load_flywire_annotation_table_preserves_class_columns(tmp_path: Path) -> None:
    path = tmp_path / "annotations.tsv"
    path.write_text(
        "\n".join(
            [
                "root_id\tcell_type\themibrain_type\tside\tsuper_class\tcell_class\tcell_sub_class",
                "1001\tA\tHA\tleft\tcentral\tclass_a\tsub_a",
                "1002\t\tHB\tright\tvisual_projection\tclass_b\tsub_b",
            ]
        ),
        encoding="utf-8",
    )

    df = load_flywire_annotation_table(path)

    assert "super_class" in df.columns
    assert "cell_class" in df.columns
    assert "cell_sub_class" in df.columns
    assert df.loc[df["root_id"] == 1001, "super_class"].iloc[0] == "central"


def test_resolve_spontaneous_family_labels_supports_super_and_cell_classes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    backend = _build_small_backend(
        monkeypatch,
        tmp_path,
        spontaneous_state={
            "mode": "sparse_lognormal_latent_ou",
            "family_key": "super_class",
            "active_fraction": 0.5,
            "lognormal_mean_hz": 1.0,
            "lognormal_sigma": 0.5,
            "max_rate_hz": 5.0,
        },
    )
    annotation_df = pd.DataFrame(
        {
            "cell_type": ["A", "B"],
            "hemibrain_type": ["HA", "HB"],
            "super_class": ["central", "ascending"],
            "cell_class": ["class_a", "class_b"],
            "cell_sub_class": ["sub_a", "sub_b"],
        }
    )

    backend.spontaneous_state = backend.spontaneous_state.from_mapping({"family_key": "super_class"})
    assert backend._resolve_spontaneous_family_labels(annotation_df).tolist() == ["central", "ascending"]

    backend.spontaneous_state = backend.spontaneous_state.from_mapping({"family_key": "cell_class"})
    assert backend._resolve_spontaneous_family_labels(annotation_df).tolist() == ["class_a", "class_b"]

    backend.spontaneous_state = backend.spontaneous_state.from_mapping({"family_key": "cell_sub_class"})
    assert backend._resolve_spontaneous_family_labels(annotation_df).tolist() == ["sub_a", "sub_b"]


def test_unknown_spontaneous_family_key_raises(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    backend = _build_small_backend(
        monkeypatch,
        tmp_path,
        spontaneous_state={
            "mode": "sparse_lognormal_latent_ou",
            "family_key": "bad_key",
            "active_fraction": 0.5,
            "lognormal_mean_hz": 1.0,
            "lognormal_sigma": 0.5,
            "max_rate_hz": 5.0,
        },
    )
    annotation_df = pd.DataFrame(
        {
            "cell_type": ["A"],
            "hemibrain_type": ["HA"],
            "super_class": ["central"],
            "cell_class": ["class_a"],
            "cell_sub_class": ["sub_a"],
        }
    )

    with pytest.raises(ValueError, match="Unsupported spontaneous_state.family_key"):
        backend._resolve_spontaneous_family_labels(annotation_df)


def test_endogenous_backend_path_disables_diagnostic_surrogate_injection(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = {
        "mode": "sparse_lognormal_latent_ou",
        "active_fraction": 1.0,
        "lognormal_mean_hz": 30.0,
        "lognormal_sigma": 0.25,
        "max_rate_hz": 60.0,
        "latent_count": 2,
        "latent_target_fraction": 1.0,
        "latent_loading_std_hz": 1.0,
        "latent_ou_tau_s": 0.2,
        "latent_ou_sigma_hz": 1.0,
        "voltage_jitter_std_mv": 0.5,
    }
    backend = _build_small_backend(
        monkeypatch,
        tmp_path,
        spontaneous_state=config,
        backend_dynamics={
            "mode": "grouped_glif_scaffold",
            "spontaneous_source": "endogenous",
        },
    )

    backend.reset(seed=3)
    firing_rates = backend.step({}, num_steps=1000)
    summary = backend.state_summary()

    assert all(rate == 0.0 for rate in firing_rates.values())
    assert summary["background_mean_rate_hz"] == 0.0
    assert summary["diagnostic_spontaneous_surrogate_active"] == 0.0
    assert summary["endogenous_spontaneous_path_selected"] == 1.0


def test_endogenous_intrinsic_noise_can_generate_bounded_activity_without_surrogate(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    backend = _build_small_backend(
        monkeypatch,
        tmp_path,
        spontaneous_state=None,
        backend_dynamics={
            "mode": "grouped_glif_scaffold",
            "spontaneous_source": "endogenous",
            "default_group": {
                "noise_sigma": 220.0,
                "noise_tau_ms": 8.0,
                "tau_adapt_ms": 60.0,
                "adapt_b": 25.0,
            },
        },
        dt_ms=1.0,
    )

    backend.reset(seed=4)
    firing_rates = backend.step({}, num_steps=10_000)
    summary = backend.state_summary()

    assert any(rate > 0.0 for rate in firing_rates.values())
    assert summary["diagnostic_spontaneous_surrogate_active"] == 0.0
    assert summary["endogenous_spontaneous_path_selected"] == 1.0
    assert summary["intrinsic_noise_mean_abs"] > 0.0
    assert torch.isfinite(backend.v).all()
    assert torch.isfinite(backend.conductance).all()
    assert torch.isfinite(backend.adaptation_current).all()
    assert torch.isfinite(backend.intrinsic_noise_state).all()
    assert 0.0 <= summary["global_spike_fraction"] <= 1.0


def test_endogenous_graded_release_tracks_voltage_for_nonspiking_release_modes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    graded_backend = _build_small_backend(
        monkeypatch,
        tmp_path,
        spontaneous_state=None,
        backend_dynamics={
            "mode": "grouped_glif_scaffold",
            "spontaneous_source": "endogenous",
            "default_group": {
                "release_mode": "graded",
                "tau_release_ms": 12.0,
                "release_v_half_mv": -55.0,
                "release_slope_mv": 2.0,
            },
        },
        dt_ms=1.0,
    )
    spiking_backend = _build_small_backend(
        monkeypatch,
        tmp_path,
        spontaneous_state=None,
        backend_dynamics={
            "mode": "grouped_glif_scaffold",
            "spontaneous_source": "endogenous",
            "default_group": {
                "release_mode": "spiking",
                "tau_release_ms": 12.0,
                "release_v_half_mv": -55.0,
                "release_slope_mv": 2.0,
            },
        },
        dt_ms=1.0,
    )

    graded_backend.reset(seed=2)
    spiking_backend.reset(seed=2)
    graded_backend.step({}, num_steps=20, direct_current_by_id={1001: 500.0})
    spiking_backend.step({}, num_steps=20, direct_current_by_id={1001: 500.0})

    graded_summary = graded_backend.state_summary()
    spiking_summary = spiking_backend.state_summary()

    assert float(graded_backend.graded_release_state[0, 0]) > 0.0
    assert graded_summary["graded_release_mean"] > 0.0
    assert torch.all(spiking_backend.graded_release_state == 0.0)
    assert spiking_summary["graded_release_mean"] == 0.0


def test_endogenous_neuromodulatory_states_accumulate_from_graded_activity(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    backend = _build_small_backend(
        monkeypatch,
        tmp_path,
        spontaneous_state=None,
        backend_dynamics={
            "mode": "grouped_glif_scaffold",
            "spontaneous_source": "endogenous",
            "neuromodulation_enabled": True,
            "modulatory_group_names": ["default"],
            "arousal_tau_ms": 50.0,
            "exafference_tau_ms": 25.0,
            "default_group": {
                "release_mode": "graded",
                "tau_release_ms": 8.0,
                "release_v_half_mv": -55.0,
                "release_slope_mv": 2.0,
                "noise_sigma": 0.0,
            },
        },
        dt_ms=1.0,
    )

    backend.reset(seed=2)
    backend.step({"mech_f_bilateral": 75.0}, num_steps=40, direct_current_by_id={1001: 500.0})
    summary = backend.state_summary()

    assert summary["graded_release_mean"] > 0.0
    assert summary["modulatory_arousal_mean"] > 0.0
    assert summary["modulatory_exafference_mean"] > 0.0
    assert summary["public_exafference_target_mean"] > 0.0


def test_endogenous_exafference_state_requires_public_body_drive(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    backend = _build_small_backend(
        monkeypatch,
        tmp_path,
        spontaneous_state=None,
        backend_dynamics={
            "mode": "grouped_glif_scaffold",
            "spontaneous_source": "endogenous",
            "neuromodulation_enabled": True,
            "modulatory_group_names": ["default"],
            "default_group": {
                "release_mode": "graded",
                "tau_release_ms": 8.0,
                "release_v_half_mv": -55.0,
                "release_slope_mv": 2.0,
                "noise_sigma": 0.0,
            },
        },
        dt_ms=1.0,
    )

    backend.reset(seed=2)
    backend.step({}, num_steps=40, direct_current_by_id={1001: 500.0})
    summary = backend.state_summary()

    assert summary["graded_release_mean"] > 0.0
    assert summary["modulatory_arousal_mean"] > 0.0
    assert summary["modulatory_exafference_mean"] == pytest.approx(0.0)
    assert summary["public_exafference_target_mean"] == pytest.approx(0.0)


def test_endogenous_intracellular_calcium_state_accumulates_and_persists(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    backend = _build_small_backend(
        monkeypatch,
        tmp_path,
        spontaneous_state=None,
        backend_dynamics={
            "mode": "grouped_glif_scaffold",
            "spontaneous_source": "endogenous",
            "default_group": {
                "release_mode": "graded",
                "tau_release_ms": 8.0,
                "release_v_half_mv": -55.0,
                "release_slope_mv": 2.0,
                    "tau_calcium_ms": 120.0,
                    "calcium_spike_gain": 1.5,
                    "calcium_release_gain": 0.75,
                    "calcium_adapt_gain": 0.2,
                    "calcium_release_feedback_gain": 0.0,
                    "noise_sigma": 0.0,
                },
            },
        dt_ms=1.0,
    )

    backend.reset(seed=2)
    backend.step({}, num_steps=20, direct_current_by_id={1001: 500.0})
    first_summary = backend.state_summary()
    calcium_after_drive = float(backend.intracellular_calcium_state.mean().item())
    backend.step({}, num_steps=30)
    calcium_after_persistence = float(backend.intracellular_calcium_state.mean().item())
    backend.step({}, num_steps=300)
    second_summary = backend.state_summary()
    calcium_after_decay = float(backend.intracellular_calcium_state.mean().item())

    assert first_summary["graded_release_mean"] > 0.0
    assert first_summary["intracellular_calcium_mean"] > 0.0
    assert calcium_after_drive > 0.0
    assert calcium_after_persistence > 0.0
    assert calcium_after_decay > 0.0
    assert calcium_after_decay < 5.0
    assert second_summary["intracellular_calcium_mean"] > 0.0


def test_endogenous_routed_recurrent_classes_split_fast_slow_and_modulatory_sources(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    flyid_to_index = {1001: 0, 1002: 1, 1003: 2, 1004: 3}
    index_to_flyid = {index: neuron_id for neuron_id, index in flyid_to_index.items()}
    weights = torch.tensor(
        [
            [0.0, 10.0, 10.0, 10.0],
            [0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0],
        ],
        dtype=torch.float32,
    )
    annotation_path = tmp_path / "annotations.tsv"
    annotation_path.write_text(
        "\n".join(
            [
                "root_id\tcell_type\themibrain_type\tside\tsuper_class\tcell_class\tcell_sub_class",
                "1001\tA\tHA\tleft\tcentral\tclass_a\tsub_a",
                "1002\tB\tHB\tright\tvisual_projection\tclass_b\tsub_b",
                "1003\tC\tHC\tleft\tendocrine\tclass_c\tsub_c",
                "1004\tD\tHD\tright\tascending\tclass_d\tsub_d",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(WholeBrainTorchBackend, "_load_hash_tables", lambda self: (flyid_to_index, index_to_flyid))
    monkeypatch.setattr(WholeBrainTorchBackend, "_load_weights", lambda self: weights)

    backend = WholeBrainTorchBackend(
        completeness_path="unused.csv",
        connectivity_path="unused.parquet",
        cache_dir=tmp_path / "cache",
        device="cpu",
        dt_ms=0.1,
        backend_dynamics={
            "mode": "grouped_glif_scaffold",
            "spontaneous_source": "endogenous",
            "annotation_path": str(annotation_path),
            "group_key": "super_class",
            "neuromodulation_enabled": True,
            "modulatory_group_names": ["endocrine"],
            "default_group": {"release_mode": "spiking"},
            "groups": {
                "central": {"release_mode": "mixed"},
                "visual_projection": {"release_mode": "graded"},
                "endocrine": {"release_mode": "graded"},
                "ascending": {"release_mode": "spiking"},
            },
        },
    )

    backend.reset(seed=0)
    backend.spikes.zero_()
    backend.graded_release_state.zero_()
    backend.intracellular_calcium_state.zero_()
    backend.spikes[0, 0] = 1.0
    backend.spikes[0, 3] = 1.0
    backend.graded_release_state[0, 0] = 0.5
    backend.graded_release_state[0, 1] = 1.0
    backend.graded_release_state[0, 2] = 1.0
    backend.intracellular_calcium_state[0, 2] = 0.5

    class_inputs = backend._build_routed_recurrent_class_inputs(torch.zeros((1, 4), dtype=torch.float32))

    assert float(class_inputs[0, 0, 0]) > 0.0
    assert float(class_inputs[1, 0, 0]) > 0.0
    assert float(class_inputs[4, 0, 0]) > 0.0
    assert float(class_inputs[2, 0, 0]) == 0.0
    assert float(class_inputs[3, 0, 0]) == 0.0

    summary = backend.state_summary()
    assert summary["routed_fast_source_fraction"] > 0.0
    assert summary["routed_slow_source_fraction"] > 0.0
    assert summary["routed_modulatory_source_fraction"] > 0.0


def test_endogenous_distributed_temporal_state_accumulates_and_persists(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    flyid_to_index = {1001: 0, 1002: 1}
    index_to_flyid = {index: neuron_id for neuron_id, index in flyid_to_index.items()}
    weights = torch.tensor(
        [
            [0.0, 6.0],
            [0.0, 0.0],
        ],
        dtype=torch.float32,
    )

    monkeypatch.setattr(WholeBrainTorchBackend, "_load_hash_tables", lambda self: (flyid_to_index, index_to_flyid))
    monkeypatch.setattr(WholeBrainTorchBackend, "_load_weights", lambda self: weights)

    backend = WholeBrainTorchBackend(
        completeness_path="unused.csv",
        connectivity_path="unused.parquet",
        cache_dir=tmp_path / "cache",
        device="cpu",
        dt_ms=1.0,
        backend_dynamics={
            "mode": "grouped_glif_scaffold",
            "spontaneous_source": "endogenous",
            "neuromodulation_enabled": True,
            "modulatory_group_names": ["default"],
            "default_group": {
                "release_mode": "graded",
                "tau_release_ms": 8.0,
                "release_v_half_mv": -55.0,
                "release_slope_mv": 2.0,
                "tau_context_exc_ms": 120.0,
                "tau_context_inh_ms": 180.0,
                "tau_context_mod_ms": 240.0,
                "context_exc_gain": 0.0,
                "context_inh_gain": 0.0,
                "context_mod_gain": 0.0,
                "noise_sigma": 0.0,
            },
        },
    )

    backend.reset(seed=0)
    weighted_fast = torch.zeros((1, 2), dtype=torch.float32)
    weighted_slow = torch.tensor([[4.0, -2.0]], dtype=torch.float32)
    weighted_modulatory = torch.tensor([[1.5, 0.0]], dtype=torch.float32)
    monkeypatch.setattr(
        backend,
        "_compute_routed_weighted_components",
        lambda: (weighted_fast, weighted_slow, weighted_modulatory),
    )
    backend._update_distributed_temporal_state()
    exc_after_drive = float(backend.distributed_context_exc_state.mean().item())
    mod_after_drive = float(backend.distributed_context_mod_state.mean().item())
    summary = backend.state_summary()
    monkeypatch.setattr(
        backend,
        "_compute_routed_weighted_components",
        lambda: (
            torch.zeros((1, 2), dtype=torch.float32),
            torch.zeros((1, 2), dtype=torch.float32),
            torch.zeros((1, 2), dtype=torch.float32),
        ),
    )
    for _ in range(40):
        backend._update_distributed_temporal_state()
    exc_after_persist = float(backend.distributed_context_exc_state.mean().item())
    mod_after_persist = float(backend.distributed_context_mod_state.mean().item())
    for _ in range(400):
        backend._update_distributed_temporal_state()
    exc_after_decay = float(backend.distributed_context_exc_state.mean().item())
    mod_after_decay = float(backend.distributed_context_mod_state.mean().item())

    assert exc_after_drive > 0.0
    assert mod_after_drive > 0.0
    assert exc_after_persist > 0.0
    assert mod_after_persist > 0.0
    assert exc_after_decay >= 0.0
    assert exc_after_decay < exc_after_persist
    assert mod_after_decay <= mod_after_persist
    assert summary["distributed_context_exc_mean"] > 0.0


def test_routed_class_inputs_include_distributed_temporal_feedback(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    flyid_to_index = {1001: 0, 1002: 1, 1003: 2}
    index_to_flyid = {index: neuron_id for neuron_id, index in flyid_to_index.items()}
    weights = torch.zeros((3, 3), dtype=torch.float32)

    monkeypatch.setattr(WholeBrainTorchBackend, "_load_hash_tables", lambda self: (flyid_to_index, index_to_flyid))
    monkeypatch.setattr(WholeBrainTorchBackend, "_load_weights", lambda self: weights)

    backend = WholeBrainTorchBackend(
        completeness_path="unused.csv",
        connectivity_path="unused.parquet",
        cache_dir=tmp_path / "cache",
        device="cpu",
        dt_ms=1.0,
        backend_dynamics={
            "mode": "grouped_glif_scaffold",
            "spontaneous_source": "endogenous",
            "neuromodulation_enabled": True,
            "modulatory_group_names": ["default"],
            "default_group": {
                "release_mode": "graded",
                "tau_context_exc_ms": 120.0,
                "tau_context_inh_ms": 200.0,
                "tau_context_mod_ms": 320.0,
                "context_exc_gain": 0.5,
                "context_inh_gain": 0.4,
                "context_mod_gain": 0.3,
            },
        },
    )

    backend.reset(seed=0)
    backend.distributed_context_exc_state[0, 0] = 2.0
    backend.distributed_context_inh_state[0, 1] = 3.0
    backend.distributed_context_mod_state[0, 2] = 4.0

    class_inputs = backend._build_routed_recurrent_class_inputs(torch.zeros((1, 3), dtype=torch.float32))

    assert float(class_inputs[1, 0, 0]) > 0.0
    assert float(class_inputs[3, 0, 1]) > 0.0
    assert float(class_inputs[4, 0, 2]) > 0.0


def test_backend_dynamics_catalog_uses_group_overrides(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    flyid_to_index = {1001: 0, 1002: 1, 1003: 2, 1004: 3}
    index_to_flyid = {index: neuron_id for neuron_id, index in flyid_to_index.items()}
    weights = torch.zeros((4, 4), dtype=torch.float32)
    annotation_path = tmp_path / "annotations.tsv"
    annotation_path.write_text(
        "\n".join(
            [
                "root_id\tcell_type\themibrain_type\tside\tsuper_class\tcell_class\tcell_sub_class",
                "1001\tFamA\tHA\tleft\tcentral\tclass_a\tsub_a",
                "1002\tFamA\tHA\tright\tcentral\tclass_a\tsub_a",
                "1003\tFamB\tHB\tleft\tascending\tclass_b\tsub_b",
                "1004\tFamB\tHB\tright\tascending\tclass_b\tsub_b",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(WholeBrainTorchBackend, "_load_hash_tables", lambda self: (flyid_to_index, index_to_flyid))
    monkeypatch.setattr(WholeBrainTorchBackend, "_load_weights", lambda self: weights)

    backend = WholeBrainTorchBackend(
        completeness_path="unused.csv",
        connectivity_path="unused.parquet",
        cache_dir=tmp_path / "cache",
        device="cpu",
        dt_ms=0.1,
        backend_dynamics={
            "mode": "grouped_glif_scaffold",
            "spontaneous_source": "endogenous",
            "annotation_path": str(annotation_path),
            "group_key": "super_class",
            "default_group": {"tau_mem_ms": 20.0, "release_mode": "spiking", "tau_calcium_ms": 140.0},
            "groups": {
                "central": {"tau_mem_ms": 30.0, "release_mode": "mixed", "tau_calcium_ms": 180.0},
                "ascending": {"tau_mem_ms": 40.0, "release_mode": "graded", "tau_calcium_ms": 220.0},
            },
        },
    )

    catalog = {row["name"]: row for row in backend.backend_dynamics_catalog()}

    assert catalog["central"]["count"] == 2
    assert catalog["central"]["tau_mem_ms"] == pytest.approx(30.0)
    assert catalog["central"]["release_mode"] == "mixed"
    assert catalog["central"]["tau_calcium_ms"] == pytest.approx(180.0)
    assert catalog["ascending"]["count"] == 2
    assert catalog["ascending"]["tau_mem_ms"] == pytest.approx(40.0)
    assert catalog["ascending"]["release_mode"] == "graded"
    assert catalog["ascending"]["tau_calcium_ms"] == pytest.approx(220.0)


def test_load_spontaneous_family_groups_respects_included_super_classes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    flyid_to_index = {1001: 0, 1002: 1, 1003: 2, 1004: 3}
    index_to_flyid = {index: neuron_id for neuron_id, index in flyid_to_index.items()}
    weights = torch.zeros((4, 4), dtype=torch.float32)
    annotation_path = tmp_path / "annotations.tsv"
    annotation_path.write_text(
        "\n".join(
            [
                "root_id\tcell_type\themibrain_type\tside\tsuper_class\tcell_class\tcell_sub_class",
                "1001\tFamA\tHA\tleft\tcentral\tclass_a\tsub_a",
                "1002\tFamA\tHA\tright\tcentral\tclass_a\tsub_a",
                "1003\tFamB\tHB\tleft\tascending\tclass_b\tsub_b",
                "1004\tFamB\tHB\tright\tascending\tclass_b\tsub_b",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(WholeBrainTorchBackend, "_load_hash_tables", lambda self: (flyid_to_index, index_to_flyid))
    monkeypatch.setattr(WholeBrainTorchBackend, "_load_weights", lambda self: weights)

    backend = WholeBrainTorchBackend(
        completeness_path="unused.csv",
        connectivity_path="unused.parquet",
        cache_dir=tmp_path / "cache",
        device="cpu",
        dt_ms=0.1,
        spontaneous_state={
            "mode": "sparse_lognormal_latent_ou",
            "active_fraction": 0.5,
            "lognormal_mean_hz": 1.0,
            "lognormal_sigma": 0.5,
            "max_rate_hz": 5.0,
            "annotation_path": str(annotation_path),
            "family_key": "cell_type",
            "min_family_size_per_side": 1,
            "included_super_classes": ["central"],
        },
    )

    assert [group.family for group in backend.spontaneous_family_groups] == ["FamA"]
    catalog = backend.spontaneous_family_group_catalog()
    assert catalog[0]["left_count"] == 1
    assert catalog[0]["right_count"] == 1
