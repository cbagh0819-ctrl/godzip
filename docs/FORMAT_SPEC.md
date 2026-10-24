# GODZIP (.god) Archive Format Specification v1.0

## 1. File Structure Layout

A GODZIP archive file (`.god`) is a deterministic, binary container format with little-endian byte ordering. It is structured into 4 sequential sections:

```
+-------------------------------------------------------------+
| Header (32 bytes)                                           |
|   - Magic Identifier (8 bytes: 'GODZIP\x01\x00')            |
|   - Format Version (u16: 1)                                 |
|   - Header Flags (u16 bitmask)                              |
|   - Block Table Offset (u64)                                |
|   - File Table Offset (u64)                                 |
|   - Header Checksum CRC32 (u32)                             |
+-------------------------------------------------------------+
| Payload Section (Variable length)                           |
|   - Block 0 [Metadata + Compressed Data]                    |
|   - Block 1 [Metadata + Compressed Data]                    |
|   ...                                                       |
|   - Block N-1 [Metadata + Compressed Data]                  |
+-------------------------------------------------------------+
| Deduplication & Block Table (Variable length)               |
|   - Number of Blocks (u32)                                  |
|   - Array of Block Records:                                 |
|       - Block ID (u32)                                      |
|       - Codec ID (u8)                                       |
|       - Codec Parameter (u8, e.g. level)                    |
|       - Reserved (u16)                                      |
|       - Uncompressed Size (u32)                             |
|       - Compressed Size (u32)                               |
|       - Stream File Offset (u64)                            |
|       - Block Digest (32 bytes BLAKE3)                      |
|       - Block CRC32 (u32)                                   |
+-------------------------------------------------------------+
| File Catalog Table (Variable length)                        |
|   - Number of Files (u32)                                   |
|   - Array of File Records:                                  |
|       - Relative Path Length (u16)                          |
|       - Relative Path (UTF-8 bytes, normalized '/' slash)   |
|       - Original File Size (u64)                            |
|       - Total Compressed Size (u64)                         |
|       - Modified Timestamp Unix (u64)                       |
|       - File Mode / Attributes (u32)                        |
|       - File Digest (32 bytes BLAKE3)                       |
|       - Number of Blocks (u32)                              |
|       - Block IDs List (u32 * num_blocks)                   |
+-------------------------------------------------------------+
| Archive Footer (24 bytes)                                   |
|   - Block Table Offset Mirror (u64)                         |
|   - File Table Offset Mirror (u64)                          |
|   - Catalog Checksum CRC32 (u32)                            |
|   - Magic Trailer (4 bytes: 'GEND')                         |
+-------------------------------------------------------------+
```

## 2. Header Flags Bitmask

| Bit | Name | Meaning |
|---|---|---|
| 0 | `FLAG_DEDUP_ENABLED` | Set if blocks are shared/deduplicated across files. |
| 1 | `FLAG_ADAPTIVE_SEARCH` | Set if adaptive search engine selected block codecs. |
| 2 | `FLAG_ENCRYPTION_RESERVED` | Reserved for future AES-256-GCM authenticated payloads. |
| 3 | `FLAG_CHECKSUM_BLAKE3` | Uses BLAKE3 digests (default: 1). If 0, uses SHA-256. |

## 3. Registered Codec Identifiers

| Codec ID | Name | Default Parameter | Description |
|---|---|---|---|
| `0x00` | `STORE` | 0 | Raw uncompressed data (lossless pass-through fallback). |
| `0x01` | `ZSTD` | 3 (Fast) to 22 (Max) | Zstandard compression. |
| `0x02` | `LZMA2` | 6 (Standard) to 9 (Max) | LZMA2 high-ratio dictionary compression. |
| `0x03` | `BROTLI` | 4 (Fast) to 11 (Max) | Brotli compression. |
| `0x04` | `DEFLATE`| 6 (Normal) to 9 (Max) | RFC 1951 DEFLATE (zlib). |
| `0x05` | `LZ4` | 0 (Fast) to 9 (High) | LZ4 real-time frame compression. |
| `0x10` | `NEURAL_CONTEXT` | 1 | Contextual neural entropy codec (Research). |

## 4. Security Bounds & Resource Limits

To safeguard against zip-bomb and parser exhaustion attacks:
- **Maximum File Entries**: 1,000,000 per archive.
- **Maximum Path Length**: 1,024 UTF-8 bytes.
- **Maximum Block Size**: 64 MB (Default chunk size: 1 MB).
- **Maximum Expansion Factor**: 1000x per block (checked before unpacking to prevent memory exhaustion).
- **Path Sanitization**: Relative paths MUST NOT begin with `/` or `\\`, MUST NOT contain drive letters (`C:`), MUST NOT contain path traversal segments (`..`), and MUST NOT reference alternate data streams (`:`).
