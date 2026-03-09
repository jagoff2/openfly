from __future__ import annotations

from typing import Any

import flyvis
from torch import Tensor

from flygym.examples.locomotion import HybridTurningFly

from body.brain_only_realistic_vision_fly import BrainOnlyRealisticVisionFly
from bridge.visual_splice import FlyVisConnectomeCache
from vision.feature_extractor import RealisticVisionFeatureExtractor
from vision.flyvis_fast_path import build_required_cell_indices


class FastRealisticVisionFly(BrainOnlyRealisticVisionFly):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._vision_feature_extractor = RealisticVisionFeatureExtractor()
        self._vision_index_cache = None
        self._vision_splice_cache = None
        self._vision_features_buffer = None
        self._nn_activities_arr_buffer = None

    def _initialize_vision_network(self, vision_obs: Any) -> None:
        super()._initialize_vision_network(vision_obs)
        if self._vision_index_cache is None:
            self._vision_index_cache = build_required_cell_indices(
                self.vision_network.connectome,
                tracking_cells=self._vision_feature_extractor.tracking_cells,
                flow_cells=self._vision_feature_extractor.flow_cells,
            )
        if self._vision_splice_cache is None:
            self._vision_splice_cache = FlyVisConnectomeCache.from_connectome(self.vision_network.connectome)

    def _get_visual_nn_activities(self, vision_obs: Any) -> tuple[Any, dict[str, float]]:
        vision_obs_grayscale = vision_obs.max(axis=-1)
        visual_input = self.retina_mapper.flygym_to_flyvis(vision_obs_grayscale)
        visual_input = Tensor(visual_input).to(flyvis.device)
        nn_activities_arr = self.vision_network.forward_one_step(visual_input)
        if hasattr(nn_activities_arr, "detach"):
            nn_activities_arr = nn_activities_arr.detach()
        if hasattr(nn_activities_arr, "cpu"):
            nn_activities_arr = nn_activities_arr.cpu().numpy()
        nn_activities_arr = nn_activities_arr.astype(float, copy=False)
        vision_features = self._vision_feature_extractor.extract_from_array(
            nn_activities_arr,
            self._vision_index_cache,
        )
        return nn_activities_arr, vision_features.to_dict()

    def _update_visual_buffers(self, vision_obs: Any) -> None:
        nn_activities_arr, vision_features = self._get_visual_nn_activities(vision_obs)
        self._nn_activities_arr_buffer = nn_activities_arr
        self._vision_features_buffer = vision_features

    def _attach_fast_payload(self, obs: dict[str, Any], info: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        info["vision_payload_mode"] = "fast"
        info["vision_features_fast"] = self._vision_features_buffer
        info["vision_index_cache"] = self._vision_index_cache
        info["vision_splice_cache"] = self._vision_splice_cache
        info["nn_activities_arr"] = self._nn_activities_arr_buffer
        obs["nn_activities_arr"] = self._nn_activities_arr_buffer
        return obs, info

    def post_step(self, sim):
        obs, reward, terminated, truncated, info = HybridTurningFly.post_step(self, sim)
        if not self._vision_network_initialized:
            self._initialize_vision_network(obs["vision"])
        if info["vision_updated"] or self._nn_activities_arr_buffer is None:
            self._update_visual_buffers(obs["vision"])
        obs, info = self._attach_fast_payload(obs, info)
        return obs, reward, terminated, truncated, info

    def reset(self, *args, **kwargs):
        if self._vision_network_initialized:
            self.vision_network.cleanup_step_by_step_simulation()
            self._vision_network_initialized = False
        obs, info = HybridTurningFly.reset(self, *args, **kwargs)
        self._initialize_vision_network(obs["vision"])
        self._update_visual_buffers(obs["vision"])
        obs, info = self._attach_fast_payload(obs, info)
        return obs, info
