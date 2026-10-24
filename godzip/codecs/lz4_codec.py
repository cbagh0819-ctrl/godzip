"""LZ4 real-time compression codec implementation."""

import lz4.frame
from .base import Codec
from ..common.constants import CODEC_ID_LZ4

class LZ4Codec(Codec):
    """LZ4 frame codec wrapper supporting fast real-time streaming."""

    @property
    def codec_id(self) -> int:
        return CODEC_ID_LZ4

    @property
    def name(self) -> str:
        return "LZ4"

    def default_level(self) -> int:
        return 0

    def compress(self, data: bytes, level: int = 0) -> bytes:
        # lz4.frame compression level: 0 (default fast) to 16 (high compression)
        level = max(0, min(16, level))
        return lz4.frame.compress(data, compression_level=level)

    def decompress(self, data: bytes, uncompressed_size: int = 0) -> bytes:
        return lz4.frame.decompress(data)
