"""Typed data models and structures for GODZIP."""

from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class BlockMetadata:
    block_id: int
    codec_id: int
    codec_param: int
    uncompressed_size: int
    compressed_size: int
    offset: int
    digest: bytes             # 32 bytes (BLAKE3 or SHA-256)
    crc32: int
    filter_id: int = 0        # Pre-filter transformation ID (e.g. delta, channel, BCJ)

@dataclass
class FileEntry:
    path: str                 # Normalized relative path
    original_size: int
    compressed_size: int
    mtime: int
    mode: int
    digest: bytes             # 32 bytes (BLAKE3 or SHA-256)
    block_ids: List[int] = field(default_factory=list)

@dataclass
class ArchiveHeader:
    version: int
    flags: int
    block_table_offset: int
    file_table_offset: int
    header_crc: int

@dataclass
class JobProgress:
    current_file: str
    files_processed: int
    total_files: int
    bytes_processed: int
    total_bytes: int
    current_compressed_bytes: int
    throughput_mbps: float
    elapsed_seconds: float
    eta_seconds: Optional[float]
    status_message: str
