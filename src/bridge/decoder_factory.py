from __future__ import annotations

from typing import Any

from bridge.decoder import DecoderConfig, MotorDecoder
from vnc.spec_decoder import VNCSpecDecoder, VNCSpecDecoderConfig


def build_motor_decoder(mapping: dict[str, Any] | None = None) -> MotorDecoder | VNCSpecDecoder:
    mapping = mapping or {}
    decoder_type = str(mapping.get("type", "sampled_descending"))
    if decoder_type == "vnc_structural_spec":
        return VNCSpecDecoder(VNCSpecDecoderConfig.from_mapping(mapping))
    return MotorDecoder(DecoderConfig.from_mapping(mapping))
