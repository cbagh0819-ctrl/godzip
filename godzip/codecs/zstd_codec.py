"""Zstandard compression codec implementation."""

import zstandard as zstd
from .base import Codec
from ..common.constants import CODEC_ID_ZSTD

class ZstdCodec(Codec):
    """Zstandard codec wrapper supporting levels 1 to 22."""

    @property
    def codec_id(self) -> int:
        return CODEC_ID_ZSTD

    @property
    def name(self) -> str:
        return "ZSTD"

    def default_level(self) -> int:
        return 3

    def compress(self, data: bytes, level: int = 3) -> bytes:
        if level <= 0:
            level = self.default_level()
        # Cap level between 1 and 22
        level = max(1, min(22, level))
        cctx = zstd.ZstdCompressor(level=level)
        return cctx.compress(data)

    def decompress(self, data: bytes, uncompressed_size: int = 0) -> bytes:
        dctx = zstd.ZstdDecompressor()
        if uncompressed_size > 0:
            return dctx.decompress(data, max_output_size=uncompressed_size)
        return dctx.decompress(data)
