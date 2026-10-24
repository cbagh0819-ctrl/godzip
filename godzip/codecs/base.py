"""Abstract Base Class for all GODZIP lossless codecs."""

import abc
from typing import Tuple

class Codec(abc.ABC):
    """Uniform interface implemented by every compression backend."""

    @property
    @abc.abstractmethod
    def codec_id(self) -> int:
        """Returns the unique uint8 identifier for this codec."""
        pass

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Returns human-readable name of codec."""
        pass

    @abc.abstractmethod
    def compress(self, data: bytes, level: int = 0) -> bytes:
        """Compresses data losslessly. Must raise on failure."""
        pass

    @abc.abstractmethod
    def decompress(self, data: bytes, uncompressed_size: int = 0) -> bytes:
        """Decompresses data back to original bytes. Must raise on failure."""
        pass

    def default_level(self) -> int:
        """Returns default compression level."""
        return 0

    def is_available(self) -> bool:
        """Indicates whether this codec's native library is available."""
        return True
