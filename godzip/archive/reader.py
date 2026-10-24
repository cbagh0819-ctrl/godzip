"""Streaming decompression, integrity verification, and safe extraction for .god archives."""

import os
import time
import zlib
from pathlib import Path
from typing import List, Dict, Callable, Optional, Tuple

from ..common.constants import (
    MAGIC_HEADER,
    MAGIC_TRAILER,
    MAX_EXPANSION_RATIO,
    MAX_BLOCK_SIZE,
)
from ..common.types import ArchiveHeader, BlockMetadata, FileEntry, JobProgress
from ..common.exceptions import (
    CorruptArchiveError,
    ChecksumMismatchError,
    DecompressionBombError,
    JobCancelledError,
)
from ..codecs.registry import CodecRegistry
from ..engine.filters import invert_filter
from ..integrity.hasher import Hasher
from ..integrity.verifier import IntegrityVerifier, SafeFileWriter
from .format import (
    HEADER_STRUCT,
    FOOTER_STRUCT,
    deserialize_header,
    deserialize_block_table,
    deserialize_file_table,
)


class ArchiveReader:
    """Reads, inspects, verifies, and safely extracts GODZIP archives."""

    def __init__(self, archive_path: str):
        self.archive_path = os.path.abspath(archive_path)
        if not os.path.exists(self.archive_path):
            raise FileNotFoundError(f"Archive not found: {self.archive_path}")

        self.header: ArchiveHeader = None
        self.blocks: List[BlockMetadata] = []
        self.block_map: Dict[int, BlockMetadata] = {}
        self.files: List[FileEntry] = []
        self._load_catalog()

    def _load_catalog(self) -> None:
        file_size = os.path.getsize(self.archive_path)
        if file_size < HEADER_STRUCT.size + FOOTER_STRUCT.size:
            raise CorruptArchiveError("Archive file is smaller than container overhead")

        with open(self.archive_path, "rb") as fp:
            # 1. Read header
            header_data = fp.read(HEADER_STRUCT.size)
            self.header = deserialize_header(header_data)

            # 2. Read footer
            fp.seek(file_size - FOOTER_STRUCT.size)
            footer_data = fp.read(FOOTER_STRUCT.size)
            b_offset, f_offset, catalog_crc, trailer = FOOTER_STRUCT.unpack(footer_data)
            if trailer != MAGIC_TRAILER:
                raise CorruptArchiveError("Corrupt archive: trailer magic mismatch")
            if b_offset != self.header.block_table_offset or f_offset != self.header.file_table_offset:
                raise CorruptArchiveError("Corrupt archive: header and footer offset mismatch")

            # 3. Read block table
            fp.seek(self.header.block_table_offset)
            block_table_size = self.header.file_table_offset - self.header.block_table_offset
            block_table_bytes = fp.read(block_table_size)
            self.blocks = deserialize_block_table(block_table_bytes)
            self.block_map = {b.block_id: b for b in self.blocks}

            # 4. Read file table
            file_table_size = (file_size - FOOTER_STRUCT.size) - self.header.file_table_offset
            file_table_bytes = fp.read(file_table_size)
            self.files = deserialize_file_table(file_table_bytes)

            # 5. Verify catalog CRC32
            actual_catalog_crc = zlib.crc32(block_table_bytes + file_table_bytes) & 0xFFFFFFFF
            if actual_catalog_crc != catalog_crc:
                raise CorruptArchiveError("Catalog checksum CRC32 verification failed")

    def inspect(self) -> Dict:
        """Returns structured metadata about the archive contents."""
        total_orig = sum(f.original_size for f in self.files)
        total_comp = sum(b.compressed_size for b in self.blocks)
        ratio = (total_orig / total_comp) if total_comp > 0 else 1.0
        reduction = (1.0 - (total_comp / total_orig)) * 100.0 if total_orig > 0 else 0.0

        return {
            "archive_path": self.archive_path,
            "version": self.header.version,
            "flags": self.header.flags,
            "total_files": len(self.files),
            "total_blocks": len(self.blocks),
            "original_bytes": total_orig,
            "compressed_bytes": total_comp,
            "compression_ratio": round(ratio, 2),
            "reduction_pct": round(reduction, 2),
            "files": [
                {
                    "path": f.path,
                    "original_size": f.original_size,
                    "compressed_size": f.compressed_size,
                    "mtime": f.mtime,
                    "blocks": len(f.block_ids),
                    "digest": f.digest.hex(),
                }
                for f in self.files
            ]
        }

    def verify(
        self,
        progress_callback: Optional[Callable[[JobProgress], None]] = None,
        cancel_check: Optional[Callable[[], bool]] = None
    ) -> bool:
        """Verifies every block CRC, decompression roundtrip, and hash without writing to disk."""
        total_bytes = sum(f.original_size for f in self.files)
        bytes_checked = 0
        start_time = time.time()

        with open(self.archive_path, "rb") as fp:
            for f_idx, f_entry in enumerate(self.files):
                if cancel_check and cancel_check():
                    raise JobCancelledError("Verification cancelled")

                file_hasher = Hasher()
                for b_id in f_entry.block_ids:
                    if cancel_check and cancel_check():
                        raise JobCancelledError("Verification cancelled")

                    meta = self.block_map.get(b_id)
                    if not meta:
                        raise CorruptArchiveError(f"Missing referenced block ID: {b_id}")

                    fp.seek(meta.offset)
                    comp_data = fp.read(meta.compressed_size)

                    # Check block CRC
                    if not IntegrityVerifier.verify_crc32(comp_data, meta.crc32):
                        raise ChecksumMismatchError(f"CRC32 mismatch on block {b_id}")

                    # Decompress and verify
                    codec = CodecRegistry.get(meta.codec_id)
                    decomp = codec.decompress(comp_data, meta.uncompressed_size)
                    if meta.filter_id != 0:
                        decomp = invert_filter(decomp, meta.filter_id)
                    if len(decomp) != meta.uncompressed_size:
                        raise CorruptArchiveError(f"Decompressed size mismatch on block {b_id}")

                    # Verify block cryptographic digest
                    if not IntegrityVerifier.verify_block_digest(decomp, meta.digest):
                        raise ChecksumMismatchError(f"Cryptographic digest mismatch on block {b_id}")

                    file_hasher.update(decomp)
                    bytes_checked += meta.uncompressed_size

                # Check file cumulative digest
                if file_hasher.digest() != f_entry.digest:
                    raise ChecksumMismatchError(f"File digest verification failed for {f_entry.path}")

                if progress_callback:
                    elapsed = max(0.001, time.time() - start_time)
                    progress_callback(JobProgress(
                        current_file=f_entry.path,
                        files_processed=f_idx + 1,
                        total_files=len(self.files),
                        bytes_processed=bytes_checked,
                        total_bytes=total_bytes,
                        current_compressed_bytes=0,
                        throughput_mbps=round((bytes_checked / (1024 * 1024)) / elapsed, 2),
                        elapsed_seconds=round(elapsed, 2),
                        eta_seconds=0.0,
                        status_message=f"Verified {f_entry.path}"
                    ))

        return True

    def extract(
        self,
        destination_dir: str,
        progress_callback: Optional[Callable[[JobProgress], None]] = None,
        cancel_check: Optional[Callable[[], bool]] = None
    ) -> int:
        """Extracts all files in the archive to destination_dir with full path and integrity guards.
        
        Returns total bytes written.
        """
        dest_path = Path(destination_dir).resolve()
        dest_path.mkdir(parents=True, exist_ok=True)

        total_bytes = sum(f.original_size for f in self.files)
        bytes_written = 0
        start_time = time.time()

        with open(self.archive_path, "rb") as fp:
            for f_idx, f_entry in enumerate(self.files):
                if cancel_check and cancel_check():
                    raise JobCancelledError("Extraction cancelled by user")

                with SafeFileWriter(str(dest_path), f_entry.path) as writer:
                    for b_id in f_entry.block_ids:
                        if cancel_check and cancel_check():
                            writer.abort()
                            raise JobCancelledError("Extraction cancelled by user")

                        meta = self.block_map.get(b_id)
                        if not meta:
                            raise CorruptArchiveError(f"Missing referenced block ID {b_id}")

                        # Zip-bomb guard
                        if meta.uncompressed_size > MAX_BLOCK_SIZE:
                            raise DecompressionBombError(f"Block uncompressed size {meta.uncompressed_size} exceeds safety limit")
                        if meta.compressed_size > 0 and (meta.uncompressed_size / meta.compressed_size > MAX_EXPANSION_RATIO):
                            raise DecompressionBombError(f"Expansion factor exceeds safety limit {MAX_EXPANSION_RATIO}x")

                        fp.seek(meta.offset)
                        comp_data = fp.read(meta.compressed_size)

                        if not IntegrityVerifier.verify_crc32(comp_data, meta.crc32):
                            raise ChecksumMismatchError(f"CRC32 mismatch on block {b_id}")

                        codec = CodecRegistry.get(meta.codec_id)
                        decomp = codec.decompress(comp_data, meta.uncompressed_size)
                        if meta.filter_id != 0:
                            decomp = invert_filter(decomp, meta.filter_id)

                        if not IntegrityVerifier.verify_block_digest(decomp, meta.digest):
                            raise ChecksumMismatchError(f"Block digest mismatch on block {b_id}")

                        writer.write_chunk(decomp)
                        bytes_written += len(decomp)

                    writer.commit(expected_digest=f_entry.digest)

                if progress_callback:
                    elapsed = max(0.001, time.time() - start_time)
                    progress_callback(JobProgress(
                        current_file=f_entry.path,
                        files_processed=f_idx + 1,
                        total_files=len(self.files),
                        bytes_processed=bytes_written,
                        total_bytes=total_bytes,
                        current_compressed_bytes=0,
                        throughput_mbps=round((bytes_written / (1024 * 1024)) / elapsed, 2),
                        elapsed_seconds=round(elapsed, 2),
                        eta_seconds=0.0,
                        status_message=f"Extracted {f_entry.path}"
                    ))

        return bytes_written
