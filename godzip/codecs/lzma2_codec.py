"""LZMA2 compression codec implementation."""

import lzma
from .base import Codec
from ..common.constants import CODEC_ID_LZMA2

class LZMA2Codec(Codec):
    """LZMA2 high-ratio dictionary codec wrapper supporting presets 0 to 9."""

    @property
    def codec_id(self) -> int:
        return CODEC_ID_LZMA2

    @property
    def name(self) -> str:
        return "LZMA2"

    def default_level(self) -> int:
        return 6

    def compress(self, data: bytes, level: int = 6) -> bytes:
        if level <= 0:
            level = self.default_level()
        level = max(0, min(9, level))
        # Use FORMAT_XZ with LZMA2 filter
        filters = [{"id": lzma.FILTER_LZMA2, "preset": level}]
        return lzma.compress(data, format=lzma.FORMAT_XZ, filters=filters)

    def decompress(self, data: bytes, uncompressed_size: int = 0) -> bytes:
        return lzma.decompress(data, format=lzma.FORMAT_XZ)
