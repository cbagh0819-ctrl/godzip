"""Cryptographic hash utilities for GODZIP."""

import hashlib
from typing import Union

try:
    import blake3
    _HAS_BLAKE3 = True
except ImportError:
    _HAS_BLAKE3 = False


class Hasher:
    """Incremental or one-shot cryptographic hasher supporting BLAKE3 and SHA-256."""

    def __init__(self, use_blake3: bool = True):
        self.use_blake3 = use_blake3 and _HAS_BLAKE3
        if self.use_blake3:
            self._ctx = blake3.blake3()
        else:
            self._ctx = hashlib.sha256()

    def update(self, data: Union[bytes, bytearray, memoryview]) -> None:
        self._ctx.update(data)

    def digest(self) -> bytes:
        return self._ctx.digest()

    def hexdigest(self) -> str:
        return self._ctx.hexdigest()

    @classmethod
    def compute(cls, data: bytes, use_blake3: bool = True) -> bytes:
        h = cls(use_blake3=use_blake3)
        h.update(data)
        return h.digest()
