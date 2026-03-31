from __future__ import annotations

import sys
import types

import pytest
import torch

from vision import flyvis_compat


def test_patch_loaded_flyvis_modules_updates_all_loaded_device_attrs() -> None:
    fake_root = types.SimpleNamespace(device=torch.device("cpu"))
    fake_submodule = types.SimpleNamespace(device=torch.device("cpu"))
    fake_without_device = types.SimpleNamespace()
    original_root = sys.modules.get("flyvis")
    original_submodule = sys.modules.get("flyvis.network.initialization")
    original_other = sys.modules.get("flyvis.other")
    try:
        sys.modules["flyvis"] = fake_root
        sys.modules["flyvis.network.initialization"] = fake_submodule
        sys.modules["flyvis.other"] = fake_without_device
        patched = flyvis_compat.patch_loaded_flyvis_modules(torch.device("cuda"))
        assert fake_root.device == torch.device("cuda")
        assert fake_submodule.device == torch.device("cuda")
        assert "flyvis" in patched
        assert "flyvis.network.initialization" in patched
        assert "flyvis.other" not in patched
    finally:
        if original_root is not None:
            sys.modules["flyvis"] = original_root
        else:
            sys.modules.pop("flyvis", None)
        if original_submodule is not None:
            sys.modules["flyvis.network.initialization"] = original_submodule
        else:
            sys.modules.pop("flyvis.network.initialization", None)
        if original_other is not None:
            sys.modules["flyvis.other"] = original_other
        else:
            sys.modules.pop("flyvis.other", None)


def test_resolve_flyvis_device_prefers_cpu_when_forced(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(flyvis_compat.torch.cuda, "is_available", lambda: True)
    assert flyvis_compat.resolve_flyvis_device(force_cpu=True) == torch.device("cpu")


def test_resolve_flyvis_device_uses_cuda_when_available(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(flyvis_compat.torch.cuda, "is_available", lambda: True)
    assert flyvis_compat.resolve_flyvis_device(force_cpu=False) == torch.device("cuda")
