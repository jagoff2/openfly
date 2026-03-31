from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import flyvis
from flygym.examples.vision import RealTimeVisionNetworkView

from body.flygym_runtime import FlyGymRealisticVisionRuntime
from vision.flyvis_compat import configure_flyvis_device


def main() -> None:
    output_path = ROOT / "outputs" / "profiling" / "flyvis_gpu_sm120_check.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    device_info = configure_flyvis_device(force_cpu=False)
    vision_network_dir = flyvis.results_dir / "flow/0000/000"
    t0 = time.time()
    network_view = RealTimeVisionNetworkView(vision_network_dir)
    network = network_view.init_network(chkpt="best_chkpt")
    visual_input = torch.full((2, 721), 0.5, dtype=torch.float32, device=flyvis.device)
    initial_state = network.fade_in_state(
        t_fade_in=0.02,
        dt=1 / 500,
        initial_frames=visual_input.unsqueeze(1),
    )
    network.setup_step_by_step_simulation(
        dt=1 / 500,
        initial_state=initial_state,
        as_states=False,
        num_samples=2,
    )
    nn_activities_arr = network.forward_one_step(visual_input).detach()
    network.cleanup_step_by_step_simulation()
    elapsed_s = time.time() - t0

    payload = {
        "torch_version": torch.__version__,
        "torch_cuda_version": torch.version.cuda,
        "flyvis_version": getattr(flyvis, "__version__", "unknown"),
        "flyvis_device": str(flyvis.device),
        "patched_modules": device_info["patched_modules"],
        "vision_network_dir": str(vision_network_dir),
        "output_device": str(nn_activities_arr.device),
        "output_shape": list(nn_activities_arr.shape),
        "output_mean": float(nn_activities_arr.mean().item()),
        "elapsed_s": float(elapsed_s),
        "device_count": int(torch.cuda.device_count()),
        "devices": [
            {
                "index": i,
                "name": torch.cuda.get_device_name(i),
                "compute_capability": f"{torch.cuda.get_device_properties(i).major}.{torch.cuda.get_device_properties(i).minor}",
            }
            for i in range(torch.cuda.device_count())
        ],
    }
    runtime = None
    try:
        runtime_t0 = time.time()
        runtime = FlyGymRealisticVisionRuntime(
            output_dir=ROOT / "outputs" / "flyvis_gpu_runtime_smoke",
            target_fly_enabled=False,
            force_cpu_vision=False,
            vision_payload_mode="fast",
            camera_fps=1,
        )
        obs = runtime.reset(seed=0)
        payload["runtime_smoke"] = {
            "elapsed_s": float(time.time() - runtime_t0),
            "flyvis_device_info": getattr(runtime, "_flyvis_device_info", None),
            "vision_parameter_device": str(next(runtime.fly.vision_network.parameters()).device),
            "vision_payload_mode": str(obs.vision_payload_mode),
            "has_nn_activities_arr": bool(obs.realistic_vision_array is not None),
        }
    except Exception as exc:
        payload["runtime_smoke"] = {
            "error": repr(exc),
        }
    finally:
        if runtime is not None:
            runtime.close()
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
