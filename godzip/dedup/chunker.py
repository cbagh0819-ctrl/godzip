"""Stream chunker for splitting large files into deduplicable blocks."""

from typing import Iterator
from ..common.constants import DEFAULT_CHUNK_SIZE, MAX_BLOCK_SIZE, MIN_CHUNK_SIZE

class StreamChunker:
    """Splits binary streams or buffers into fixed or adaptive chunks."""

    def __init__(self, chunk_size: int = DEFAULT_CHUNK_SIZE):
        self.chunk_size = max(MIN_CHUNK_SIZE, min(MAX_BLOCK_SIZE, chunk_size))

    def chunk_bytes(self, data: bytes) -> Iterator[bytes]:
        """Yields chunks from an in-memory byte buffer."""
        for i in range(0, len(data), self.chunk_size):
            yield data[i:i + self.chunk_size]

    def chunk_stream(self, stream) -> Iterator[bytes]:
        """Yields chunks read from an open binary file stream."""
        while True:
            chunk = stream.read(self.chunk_size)
            if not chunk:
                break
            yield chunk
