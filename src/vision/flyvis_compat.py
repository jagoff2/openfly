from __future__ import annotations

import sys
from typing import Any

import torch


def resolve_flyvis_device(force_cpu: bool = False) -> torch.device:
    if force_cpu or not torch.cuda.is_available():
        return torch.device("cpu")
    return torch.device("cuda")


def patch_loaded_flyvis_modules(device: torch.device) -> list[str]:
    patched: list[str] = []
    for module_name, module in list(sys.modules.items()):
        if not module_name.startswith("flyvis"):
            continue
        if not hasattr(module, "device"):
            continue
        try:
            setattr(module, "device", device)
            patched.append(module_name)
        except Exception:
            continue
    return patched


def configure_flyvis_device(force_cpu: bool = False) -> dict[str, Any]:
    import flyvis

    device = resolve_flyvis_device(force_cpu=force_cpu)
    flyvis.device = device
    torch.set_default_device(device)
    patched_modules = patch_loaded_flyvis_modules(device)
    return {
        "device": str(device),
        "patched_modules": patched_modules,
    }
