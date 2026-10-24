"""STORE codec: Uncompressed pass-through fallback."""

from .base import Codec
from ..common.constants import CODEC_ID_STORE

class StoreCodec(Codec):
    """Pass-through codec. Used when data is incompressible or pre-compressed."""

    @property
    def codec_id(self) -> int:
        return CODEC_ID_STORE

    @property
    def name(self) -> str:
        return "STORE"

    def compress(self, data: bytes, level: int = 0) -> bytes:
        return data

    def decompress(self, data: bytes, uncompressed_size: int = 0) -> bytes:
        return data

    def default_level(self) -> int:
        return 0
