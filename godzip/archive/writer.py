"""Deterministic, streaming archive creation engine for GODZIP (.god)."""

import os
import time
import zlib
import shutil
from pathlib import Path
from typing import List, Callable, Optional, Union, Tuple

from ..common.constants import (
    MAGIC_HEADER,
    MAGIC_TRAILER,
    FORMAT_VERSION,
    FLAG_DEDUP_ENABLED,
    FLAG_ADAPTIVE_SEARCH,
    FLAG_CHECKSUM_BLAKE3,
    CompressionMode,
    DEFAULT_CHUNK_SIZE,
)
from ..common.types import ArchiveHeader, BlockMetadata, FileEntry, JobProgress
from ..common.exceptions import JobCancelledError
from ..integrity.hasher import Hasher
from ..integrity.path_guard import sanitize_archive_path
from ..analyzer.analyzer import ContentAnalyzer
from ..dedup.chunker import StreamChunker
from ..dedup.index import DeduplicationIndex
from ..engine.adaptive import AdaptiveSearchEngine
from .format import (
    HEADER_STRUCT,
    FOOTER_STRUCT,
    serialize_header,
    serialize_block_table,
    serialize_file_table,
)


class ArchiveWriter:
    """Streams files into a finalized .god archive with deduplication and adaptive compression."""

    def __init__(
        self,
        output_path: str,
        mode: CompressionMode = CompressionMode.BALANCED,
        enable_dedup: bool = True,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        progress_callback: Optional[Callable[[JobProgress], None]] = None,
        cancel_check: Optional[Callable[[], bool]] = None,
    ):
        self.output_path = os.path.abspath(output_path)
        self.temp_output_path = self.output_path + f".tmp.godzip.{os.getpid()}"
        self.mode = mode
        self.enable_dedup = enable_dedup
        self.chunk_size = chunk_size
        self.progress_callback = progress_callback
        self.cancel_check = cancel_check
        self.dedup_index = DeduplicationIndex(use_blake3=True)
        self.chunker = StreamChunker(chunk_size=chunk_size)

    def add_sources(self, source_paths: List[str]) -> Tuple[int, int]:
        """Creates the .god archive from a list of files and directories.
        
        Returns:
            Tuple of (total_original_bytes, final_archive_bytes).
        """
        # Collect all files to archive
        file_list: List[Tuple[str, str]] = []  # (abs_path, relative_archive_path)
        for src in source_paths:
            src_path = Path(src).resolve()
            if not src_path.exists():
                continue
            if src_path.is_file():
                file_list.append((str(src_path), src_path.name))
            elif src_path.is_dir():
                for root, _, files in os.walk(src_path):
                    for f in files:
                        full_f = Path(root) / f
                        rel_f = full_f.relative_to(src_path)
                        # Archive relative path includes folder name as root
                        archive_rel = f"{src_path.name}/{rel_f.as_posix()}"
                        file_list.append((str(full_f), archive_rel))

        total_files = len(file_list)
        total_original_bytes = sum(os.path.getsize(p[0]) for p in file_list)

        os.makedirs(os.path.dirname(self.temp_output_path), exist_ok=True)

        blocks: List[BlockMetadata] = []
        files: List[FileEntry] = []
        bytes_processed = 0
        compressed_bytes_written = 0
        start_time = time.time()
        last_callback_time = 0.0

        with open(self.temp_output_path, "wb") as out_fp:
            # Reserve 32 bytes for header
            out_fp.write(b"\x00" * HEADER_STRUCT.size)

            next_block_id = 0

            for file_idx, (abs_path, rel_path) in enumerate(file_list):
                if self.cancel_check and self.cancel_check():
                    out_fp.close()
                    if os.path.exists(self.temp_output_path):
                        os.remove(self.temp_output_path)
                    raise JobCancelledError("Archive creation cancelled by user")

                clean_path = sanitize_archive_path(rel_path)
                stat_info = os.stat(abs_path)
                file_hasher = Hasher()
                file_block_ids: List[int] = []
                file_orig_size = stat_info.st_size
                file_comp_size = 0

                with open(abs_path, "rb") as in_fp:
                    for chunk in self.chunker.chunk_stream(in_fp):
                        if self.cancel_check and self.cancel_check():
                            out_fp.close()
                            if os.path.exists(self.temp_output_path):
                                os.remove(self.temp_output_path)
                            raise JobCancelledError("Archive creation cancelled by user")

                        chunk_len = len(chunk)
                        file_hasher.update(chunk)
                        chunk_digest = Hasher.compute(chunk)

                        # Deduplication lookup
                        existing_block = self.dedup_index.lookup(chunk_digest) if self.enable_dedup else None
                        if existing_block is not None:
                            # Re-use existing block
                            b_id, _ = existing_block
                            file_block_ids.append(b_id)
                        else:
                            # Compress new block
                            profile = ContentAnalyzer.analyze(chunk)
                            cid, cparam, comp_data = AdaptiveSearchEngine.choose_codec(chunk, profile, self.mode)
                            comp_len = len(comp_data)
                            offset = out_fp.tell()
                            crc = zlib.crc32(comp_data) & 0xFFFFFFFF

                            out_fp.write(comp_data)
                            compressed_bytes_written += comp_len
                            file_comp_size += comp_len

                            block_meta = BlockMetadata(
                                block_id=next_block_id,
                                codec_id=cid,
                                codec_param=cparam,
                                uncompressed_size=chunk_len,
                                compressed_size=comp_len,
                                offset=offset,
                                digest=chunk_digest,
                                crc32=crc
                            )
                            blocks.append(block_meta)
                            if self.enable_dedup:
                                self.dedup_index.register(chunk_digest, next_block_id, chunk_len)

                            file_block_ids.append(next_block_id)
                            next_block_id += 1

                        bytes_processed += chunk_len

                        # Progress update at 10 Hz
                        now = time.time()
                        if self.progress_callback and (now - last_callback_time > 0.1 or bytes_processed == total_original_bytes):
                            elapsed = max(0.001, now - start_time)
                            throughput = (bytes_processed / (1024 * 1024)) / elapsed
                            eta = ((total_original_bytes - bytes_processed) / (throughput * 1024 * 1024)) if throughput > 0 else 0.0
                            self.progress_callback(JobProgress(
                                current_file=clean_path,
                                files_processed=file_idx + 1,
                                total_files=total_files,
                                bytes_processed=bytes_processed,
                                total_bytes=total_original_bytes,
                                current_compressed_bytes=compressed_bytes_written,
                                throughput_mbps=round(throughput, 2),
                                elapsed_seconds=round(elapsed, 2),
                                eta_seconds=round(eta, 2),
                                status_message=f"Compressing {clean_path}..."
                            ))
                            last_callback_time = now

                files.append(FileEntry(
                    path=clean_path,
                    original_size=file_orig_size,
                    compressed_size=file_comp_size,
                    mtime=int(stat_info.st_mtime),
                    mode=stat_info.st_mode,
                    digest=file_hasher.digest(),
                    block_ids=file_block_ids
                ))

            # Write Block Table
            block_table_offset = out_fp.tell()
            block_table_bytes = serialize_block_table(blocks)
            out_fp.write(block_table_bytes)

            # Write File Table
            file_table_offset = out_fp.tell()
            file_table_bytes = serialize_file_table(files)
            out_fp.write(file_table_bytes)

            # Calculate catalog CRC32
            catalog_crc = zlib.crc32(block_table_bytes + file_table_bytes) & 0xFFFFFFFF

            # Write Footer (24 bytes)
            footer_bytes = FOOTER_STRUCT.pack(block_table_offset, file_table_offset, catalog_crc, MAGIC_TRAILER)
            out_fp.write(footer_bytes)

            # Write finalized Header at offset 0
            flags = FLAG_CHECKSUM_BLAKE3
            if self.enable_dedup:
                flags |= FLAG_DEDUP_ENABLED
            if self.mode in (CompressionMode.BALANCED, CompressionMode.MAXIMUM, CompressionMode.RESEARCH):
                flags |= FLAG_ADAPTIVE_SEARCH

            header = ArchiveHeader(
                version=FORMAT_VERSION,
                flags=flags,
                block_table_offset=block_table_offset,
                file_table_offset=file_table_offset,
                header_crc=0
            )
            out_fp.seek(0)
            out_fp.write(serialize_header(header))

        # Atomic commit
        if os.path.exists(self.output_path):
            os.remove(self.output_path)
        shutil.move(self.temp_output_path, self.output_path)

        final_size = os.path.getsize(self.output_path)
        return total_original_bytes, final_size
