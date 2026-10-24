"""Binary serialization and deserialization for the .god archive container."""

import struct
import zlib
from typing import List, Tuple
from ..common.constants import (
    MAGIC_HEADER,
    MAGIC_TRAILER,
    FORMAT_VERSION,
    MAX_FILE_ENTRIES,
    MAX_PATH_LENGTH,
)
from ..common.types import ArchiveHeader, BlockMetadata, FileEntry
from ..common.exceptions import CorruptArchiveError, UnsupportedVersionError

HEADER_STRUCT = struct.Struct("<8sHHQQI")    # 32 bytes
BLOCK_ENTRY_STRUCT = struct.Struct("<IBBHIIQ32sI")  # 60 bytes
FOOTER_STRUCT = struct.Struct("<QQI4s")        # 24 bytes


def serialize_header(header: ArchiveHeader) -> bytes:
    """Serializes the 32-byte archive header."""
    raw_without_crc = struct.pack("<8sHHQQ", MAGIC_HEADER, header.version, header.flags,
                                  header.block_table_offset, header.file_table_offset)
    crc = zlib.crc32(raw_without_crc) & 0xFFFFFFFF
    return HEADER_STRUCT.pack(MAGIC_HEADER, header.version, header.flags,
                              header.block_table_offset, header.file_table_offset, crc)


def deserialize_header(data: bytes) -> ArchiveHeader:
    """Parses and verifies the 32-byte archive header."""
    if len(data) < HEADER_STRUCT.size:
        raise CorruptArchiveError("File is smaller than minimum GODZIP header (32 bytes)")
    
    magic, version, flags, b_offset, f_offset, crc = HEADER_STRUCT.unpack(data[:HEADER_STRUCT.size])
    if magic != MAGIC_HEADER:
        raise CorruptArchiveError(f"Invalid magic identifier: expected {MAGIC_HEADER!r}, got {magic!r}")
    
    if version != FORMAT_VERSION:
        raise UnsupportedVersionError(f"Unsupported GODZIP version: {version} (expected {FORMAT_VERSION})")
    
    raw_without_crc = struct.pack("<8sHHQQ", magic, version, flags, b_offset, f_offset)
    expected_crc = zlib.crc32(raw_without_crc) & 0xFFFFFFFF
    if crc != expected_crc:
        raise CorruptArchiveError(f"Header CRC32 mismatch: expected 0x{expected_crc:08x}, got 0x{crc:08x}")
    
    return ArchiveHeader(
        version=version,
        flags=flags,
        block_table_offset=b_offset,
        file_table_offset=f_offset,
        header_crc=crc
    )


def serialize_block_table(blocks: List[BlockMetadata]) -> bytes:
    """Serializes the block index table."""
    buf = bytearray()
    buf.extend(struct.pack("<I", len(blocks)))
    for b in blocks:
        buf.extend(BLOCK_ENTRY_STRUCT.pack(
            b.block_id,
            b.codec_id,
            b.codec_param,
            b.filter_id,
            b.uncompressed_size,
            b.compressed_size,
            b.offset,
            b.digest,
            b.crc32
        ))
    return bytes(buf)


def deserialize_block_table(data: bytes) -> List[BlockMetadata]:
    """Deserializes the block index table."""
    if len(data) < 4:
        raise CorruptArchiveError("Corrupted block table: missing count header")
    num_blocks = struct.unpack_from("<I", data, 0)[0]
    expected_size = 4 + (num_blocks * BLOCK_ENTRY_STRUCT.size)
    if len(data) < expected_size:
        raise CorruptArchiveError(f"Truncated block table: expected {expected_size} bytes, got {len(data)}")
    
    blocks = []
    offset = 4
    for _ in range(num_blocks):
        b_id, c_id, c_param, f_id, u_size, c_size, f_offset, digest, crc = BLOCK_ENTRY_STRUCT.unpack_from(data, offset)
        blocks.append(BlockMetadata(
            block_id=b_id,
            codec_id=c_id,
            codec_param=c_param,
            filter_id=f_id,
            uncompressed_size=u_size,
            compressed_size=c_size,
            offset=f_offset,
            digest=digest,
            crc32=crc
        ))
        offset += BLOCK_ENTRY_STRUCT.size
    return blocks


def serialize_file_table(files: List[FileEntry]) -> bytes:
    """Serializes the file catalog table."""
    buf = bytearray()
    buf.extend(struct.pack("<I", len(files)))
    for f in files:
        path_bytes = f.path.encode("utf-8")
        buf.extend(struct.pack("<H", len(path_bytes)))
        buf.extend(path_bytes)
        buf.extend(struct.pack("<QQII32sI", f.original_size, f.compressed_size, f.mtime, f.mode, f.digest, len(f.block_ids)))
        if f.block_ids:
            buf.extend(struct.pack(f"<{len(f.block_ids)}I", *f.block_ids))
    return bytes(buf)


def deserialize_file_table(data: bytes) -> List[FileEntry]:
    """Deserializes the file catalog table."""
    if len(data) < 4:
        raise CorruptArchiveError("Corrupted file catalog: missing file count")
    num_files = struct.unpack_from("<I", data, 0)[0]
    if num_files > MAX_FILE_ENTRIES:
        raise CorruptArchiveError(f"File count {num_files} exceeds safety limit of {MAX_FILE_ENTRIES}")
    
    offset = 4
    files = []
    data_len = len(data)
    for _ in range(num_files):
        if offset + 2 > data_len:
            raise CorruptArchiveError("Truncated file entry path length")
        path_len = struct.unpack_from("<H", data, offset)[0]
        offset += 2
        if path_len > MAX_PATH_LENGTH or offset + path_len > data_len:
            raise CorruptArchiveError("Invalid or out-of-bounds file path length")
        path = data[offset:offset + path_len].decode("utf-8", errors="replace")
        offset += path_len

        # original_size (Q), compressed_size (Q), mtime (I), mode (I), digest (32s), num_blocks (I)
        meta_size = 8 + 8 + 4 + 4 + 32 + 4
        if offset + meta_size > data_len:
            raise CorruptArchiveError("Truncated file entry metadata")
        orig_size, comp_size, mtime, mode, digest, num_blocks = struct.unpack_from("<QQII32sI", data, offset)
        offset += meta_size

        block_ids = []
        if num_blocks > 0:
            block_bytes = num_blocks * 4
            if offset + block_bytes > data_len:
                raise CorruptArchiveError("Truncated file block ID array")
            block_ids = list(struct.unpack_from(f"<{num_blocks}I", data, offset))
            offset += block_bytes

        files.append(FileEntry(
            path=path,
            original_size=orig_size,
            compressed_size=comp_size,
            mtime=mtime,
            mode=mode,
            digest=digest,
            block_ids=block_ids
        ))
    return files
