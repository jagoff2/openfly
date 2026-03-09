#!/usr/bin/env bash
set -euo pipefail

python - <<'PY'
report = {}
for module_name in ['mujoco', 'dm_control', 'flygym']:
    try:
        module = __import__(module_name)
        report[module_name] = getattr(module, '__version__', 'imported')
    except Exception as exc:
        report[module_name] = f'ERROR: {exc}'
print(report)
PY
