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
        'cuda_available': torch.cuda.is_available(),
        'device_count': torch.cuda.device_count(),
        'device_0': torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
    })
except Exception as exc:
    print({'torch_check_error': str(exc)})
PY
