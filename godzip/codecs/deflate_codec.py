"""DEFLATE (RFC 1951) compression codec implementation."""

import zlib
from .base import Codec
from ..common.constants import CODEC_ID_DEFLATE

class DeflateCodec(Codec):
    """Standard DEFLATE codec wrapper supporting levels 1 to 9."""

    @property
    def codec_id(self) -> int:
        return CODEC_ID_DEFLATE

    @property
    def name(self) -> str:
        return "DEFLATE"

    def default_level(self) -> int:
        return 6

    def compress(self, data: bytes, level: int = 6) -> bytes:
        if level <= 0:
            level = self.default_level()
        level = max(1, min(9, level))
        # wbits = -15 for raw deflate stream without zlib wrapper overhead
        compressor = zlib.compressobj(level=level, method=zlib.DEFLATED, wbits=-15)
        return compressor.compress(data) + compressor.flush()

    def decompress(self, data: bytes, uncompressed_size: int = 0) -> bytes:
        decompressor = zlib.decompressobj(wbits=-15)
        return decompressor.decompress(data)
