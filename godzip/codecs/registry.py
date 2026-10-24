"""Registry mapping codec IDs to their concrete Codec implementations."""

from typing import Dict
from .base import Codec
from .store import StoreCodec
from .zstd_codec import ZstdCodec
from .lzma2_codec import LZMA2Codec
from .brotli_codec import BrotliCodec
from .deflate_codec import DeflateCodec
from .lz4_codec import LZ4Codec
from .neural_codec import NeuralContextCodec
from ..common.constants import (
    CODEC_ID_STORE,
    CODEC_ID_ZSTD,
    CODEC_ID_LZMA2,
    CODEC_ID_BROTLI,
    CODEC_ID_DEFLATE,
    CODEC_ID_LZ4,
    CODEC_ID_NEURAL_CONTEXT,
)
from ..common.exceptions import CodecNotFoundError


class CodecRegistry:
    """Manages active codecs and resolves codec instances."""

    _codecs: Dict[int, Codec] = {}

    @classmethod
    def initialize(cls) -> None:
        cls._codecs = {
            CODEC_ID_STORE: StoreCodec(),
            CODEC_ID_ZSTD: ZstdCodec(),
            CODEC_ID_LZMA2: LZMA2Codec(),
            CODEC_ID_BROTLI: BrotliCodec(),
            CODEC_ID_DEFLATE: DeflateCodec(),
            CODEC_ID_LZ4: LZ4Codec(),
            CODEC_ID_NEURAL_CONTEXT: NeuralContextCodec(),
        }

    @classmethod
    def get(cls, codec_id: int) -> Codec:
        if not cls._codecs:
            cls.initialize()
        codec = cls._codecs.get(codec_id)
        if codec is None:
            raise CodecNotFoundError(f"Unsupported or unregistered codec ID: 0x{codec_id:02x}")
        return codec

    @classmethod
    def get_by_name(cls, name: str) -> Codec:
        if not cls._codecs:
            cls.initialize()
        norm = name.strip().upper()
        for codec in cls._codecs.values():
            if codec.name == norm:
                return codec
        raise CodecNotFoundError(f"No registered codec with name: {name}")

    @classmethod
    def all_codecs(cls) -> Dict[int, Codec]:
        if not cls._codecs:
            cls.initialize()
        return dict(cls._codecs)
