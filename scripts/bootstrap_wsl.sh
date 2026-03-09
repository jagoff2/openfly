#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL_CUDA_TOOLKIT="${INSTALL_CUDA_TOOLKIT:-0}"
CUDA_REPO_DEB="${CUDA_REPO_DEB:-cuda-repo-wsl-ubuntu-12-6-local_12.6.3-1_amd64.deb}"
CUDA_REPO_URL="${CUDA_REPO_URL:-https://developer.download.nvidia.com/compute/cuda/12.6.3/local_installers/${CUDA_REPO_DEB}}"

if ! grep -qi microsoft /proc/version; then
  echo "This script is intended for WSL2." >&2
  exit 1
fi

echo "[bootstrap_wsl] updating apt and installing base packages"
sudo apt-get update
sudo apt-get install -y   build-essential   cmake   curl   ffmpeg   git   pkg-config   python3-venv   wget

if [[ "${INSTALL_CUDA_TOOLKIT}" == "1" ]]; then
  echo "[bootstrap_wsl] installing optional CUDA toolkit for Brian2CUDA / NEST GPU"
  tmp_dir="$(mktemp -d)"
  pushd "${tmp_dir}" >/dev/null
  wget -q "${CUDA_REPO_URL}"
  wget -q https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-wsl-ubuntu.pin
  sudo mv cuda-wsl-ubuntu.pin /etc/apt/preferences.d/cuda-repository-pin-600
  sudo dpkg -i "${CUDA_REPO_DEB}"
  sudo cp /var/cuda-repo-wsl-ubuntu-*/cuda-*-keyring.gpg /usr/share/keyrings/
  sudo apt-get update
  sudo apt-get install -y cuda-toolkit-12-6
  popd >/dev/null
  rm -rf "${tmp_dir}"
fi

echo "[bootstrap_wsl] done"
echo "Next: ${ROOT_DIR}/scripts/bootstrap_env.sh"
