"""Brotli compression codec implementation."""

import brotli
from .base import Codec
from ..common.constants import CODEC_ID_BROTLI

class BrotliCodec(Codec):
    """Google Brotli codec wrapper supporting quality 0 to 11."""

    @property
    def codec_id(self) -> int:
        return CODEC_ID_BROTLI

    @property
    def name(self) -> str:
        return "BROTLI"

    def default_level(self) -> int:
        return 4

    def compress(self, data: bytes, level: int = 4) -> bytes:
        if level < 0:
            level = self.default_level()
        level = max(0, min(11, level))
        return brotli.compress(data, quality=level)

    def decompress(self, data: bytes, uncompressed_size: int = 0) -> bytes:
        return brotli.decompress(data)
