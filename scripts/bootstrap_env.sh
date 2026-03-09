#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAMBA_BIN="${MAMBA_BIN:-$HOME/.local/bin/micromamba}"
MAMBA_ROOT_PREFIX="${MAMBA_ROOT_PREFIX:-$HOME/.local/share/mamba}"
FULL_ENV="${FULL_ENV:-flysim-full}"
BRAIN_ENV="${BRAIN_ENV:-flysim-brain-brian2}"

mkdir -p "$(dirname "${MAMBA_BIN}")"

if [[ ! -x "${MAMBA_BIN}" ]]; then
  echo "[bootstrap_env] installing micromamba"
  tmp_dir="$(mktemp -d)"
  pushd "${tmp_dir}" >/dev/null
  curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xj
  mv bin/micromamba "${MAMBA_BIN}"
  popd >/dev/null
  rm -rf "${tmp_dir}"
fi

eval "$(${MAMBA_BIN} shell hook -s bash)"

if ! micromamba env list | awk '{print $1}' | grep -qx "${FULL_ENV}"; then
  micromamba create -y -n "${FULL_ENV}" python=3.10 pip ffmpeg
fi
micromamba run -n "${FULL_ENV}" pip install -U pip setuptools wheel
micromamba run -n "${FULL_ENV}" pip install -r "${ROOT_DIR}/environment/requirements-full.txt"
micromamba run -n "${FULL_ENV}" pip install -e "${ROOT_DIR}[dev]"
micromamba run -n "${FULL_ENV}" flyvis download-pretrained

if ! micromamba env list | awk '{print $1}' | grep -qx "${BRAIN_ENV}"; then
  micromamba create -y -n "${BRAIN_ENV}" python=3.10 pip
fi
micromamba run -n "${BRAIN_ENV}" pip install -U pip setuptools wheel
micromamba run -n "${BRAIN_ENV}" pip install "setuptools<81"
micromamba run -n "${BRAIN_ENV}" pip install -r "${ROOT_DIR}/environment/requirements-brain-brian2.txt"
micromamba run -n "${BRAIN_ENV}" pip install -e "${ROOT_DIR}[dev]"

echo "[bootstrap_env] environments ready"
echo "  full stack env:   ${FULL_ENV}"
echo "  brian2 env:       ${BRAIN_ENV}"
