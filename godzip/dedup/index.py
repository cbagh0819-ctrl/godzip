"""Deduplication block index and collision-safe mapping."""

from typing import Dict, Optional, Tuple
from ..integrity.hasher import Hasher

class DeduplicationIndex:
    """Tracks block hashes to existing block IDs across an archive."""

    def __init__(self, use_blake3: bool = True):
        self.use_blake3 = use_blake3
        # Map: digest (bytes) -> (block_id, uncompressed_size)
        self._index: Dict[bytes, Tuple[int, int]] = {}

    def lookup(self, digest: bytes) -> Optional[Tuple[int, int]]:
        """Returns (block_id, uncompressed_size) if the chunk digest is already stored."""
        return self._index.get(digest)

    def register(self, digest: bytes, block_id: int, uncompressed_size: int) -> None:
        """Registers a newly written block into the deduplication index."""
        self._index[digest] = (block_id, uncompressed_size)

    def clear(self) -> None:
        self._index.clear()

    @property
    def total_entries(self) -> int:
        return len(self._index)
