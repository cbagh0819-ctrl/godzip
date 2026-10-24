"""Integrity verifier and safe atomic commit file handler."""

import os
import zlib
import shutil
from pathlib import Path
from typing import Optional
from .hasher import Hasher
from .path_guard import resolve_safe_extract_path
from ..common.exceptions import ChecksumMismatchError, CorruptArchiveError


class IntegrityVerifier:
    """Provides file-level and block-level hash and CRC verification."""

    @staticmethod
    def verify_crc32(data: bytes, expected_crc: int) -> bool:
        actual_crc = zlib.crc32(data) & 0xFFFFFFFF
        return actual_crc == (expected_crc & 0xFFFFFFFF)

    @staticmethod
    def verify_block_digest(data: bytes, expected_digest: bytes, use_blake3: bool = True) -> bool:
        actual_digest = Hasher.compute(data, use_blake3=use_blake3)
        return actual_digest == expected_digest


class SafeFileWriter:
    """Writes extraction files to atomic temporary locations and finalizes only upon verification."""

    def __init__(self, destination_dir: str, archive_path: str):
        self.target_path = resolve_safe_extract_path(destination_dir, archive_path)
        self.temp_path = self.target_path + f".tmp.godzip.{os.getpid()}"
        self.file_handle = None
        self._hasher = None

    def __enter__(self):
        os.makedirs(os.path.dirname(self.temp_path), exist_ok=True)
        self.file_handle = open(self.temp_path, "wb")
        self._hasher = Hasher()
        return self

    def write_chunk(self, chunk: bytes) -> None:
        self.file_handle.write(chunk)
        self._hasher.update(chunk)

    def commit(self, expected_digest: Optional[bytes] = None) -> None:
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None

        if expected_digest is not None:
            actual = self._hasher.digest()
            if actual != expected_digest:
                if os.path.exists(self.temp_path):
                    os.remove(self.temp_path)
                raise ChecksumMismatchError(
                    f"Integrity check failed for {self.target_path}. "
                    f"Expected: {expected_digest.hex()[:16]}, Actual: {actual.hex()[:16]}"
                )

        # Atomic rename or replace
        if os.path.exists(self.target_path):
            os.remove(self.target_path)
        shutil.move(self.temp_path, self.target_path)

    def abort(self) -> None:
        if self.file_handle and not self.file_handle.closed:
            self.file_handle.close()
            self.file_handle = None
        if os.path.exists(self.temp_path):
            try:
                os.remove(self.temp_path)
            except OSError:
                pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.abort()
