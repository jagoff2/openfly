#!/usr/bin/env bash
set -euo pipefail

echo "[check_cuda] nvidia-smi"
nvidia-smi

echo "[check_cuda] nvcc (if installed)"
if command -v nvcc >/dev/null 2>&1; then
  nvcc --version
else
  echo "nvcc not installed"
fi

echo "[check_cuda] torch cuda"
python - <<'PY'
try:
    import torch
    print({
        'torch_version': torch.__version__,
        'cuda_version': torch.version.cuda,
        'cuda_available': torch.cuda.is_available(),
        'device_count': torch.cuda.device_count(),
        'device_0': torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        'compute_capability_0': (
            f"{torch.cuda.get_device_properties(0).major}.{torch.cuda.get_device_properties(0).minor}"
            if torch.cuda.is_available()
            else None
        ),
    })
    if torch.cuda.is_available():
        x = torch.randn(256, 256, device="cuda")
        y = torch.randn(256, 256, device="cuda")
        z = x @ y
        print({'cuda_tensor_smoke': 'ok', 'cuda_tensor_device': str(z.device), 'cuda_tensor_probe': float(z[0, 0].item())})
except Exception as exc:
    print({'torch_check_error': str(exc)})
PY
