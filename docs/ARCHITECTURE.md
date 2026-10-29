# GODZIP Architecture Specification

**Lead Architect & Creator:** Chandan Bagh (<baghchandan53@gmail.com> | GitHub: [@cbagh0819-ctrl](https://github.com/cbagh0819-ctrl))  
**Copyright:** (c) 2026 Chandan Bagh under the MIT License

## 1. System Overview

**GODZIP** is an intelligent, modular, lossless file compression platform for Windows x64. The platform addresses fundamental limitations in traditional static archivers by coupling multi-codec streaming, content-defined deduplication, lightweight data characterization (entropy, byte distributions, file magic), and an adaptive search engine that selects optimal compression representations based on empirical measurements rather than naive heuristics.

```
+-------------------------------------------------------------------------------+
|                             GODZIP Desktop (Qt 6)                             |
|  [Dashboard] [Workspace] [Live Monitor] [Inspector] [Benchmark Lab] [Settings]|
+---------------------------------------+---------------------------------------+
                                        | (Qt Signals / Progress Callbacks)
                                        v
+-------------------------------------------------------------------------------+
|                            Job Controller & Workers                           |
|       - Concurrency Bounding       - Resource Governors (RAM / CPU / Time)    |
|       - Cancellation & Pause       - Safe Atomic Output Finalization          |
+---------------------------------------+---------------------------------------+
                                        |
                 +----------------------+----------------------+
                 |                                             |
                 v                                             v
+---------------------------------+           +---------------------------------+
|        Content Analyzer         |           |       Deduplication Engine      |
| - Byte Frequency & Shannon H    |           | - Fixed & FastCDC Chunking      |
| - Magic Signature Detection     |           | - BLAKE3 / SHA-256 Block Digest |
| - Incompressibility Heuristics  |           | - Collision-Safe Block Table    |
+---------------------------------+           +---------------------------------+
                 |                                             |
                 +----------------------+----------------------+
                                        v
+-------------------------------------------------------------------------------+
|                    Adaptive Search Compression Engine                         |
|   Modes: FAST | BALANCED | MAXIMUM | RESEARCH                                 |
|   - Candidate Enumerator based on file characterization                       |
|   - Trial compression on representative blocks                                |
|   - Exact framing & metadata overhead accounting                              |
|   - Best verified codec selection with lossless guarantee                     |
+---------------------------------------+---------------------------------------+
                                        |
                 +----------------------+----------------------+
                 |                                             |
                 v                                             v
+---------------------------------+           +---------------------------------+
|         Standard Codecs         |           |   Research & Neural Codecs      |
| - Zstandard (Levels 1 - 22)     |           | - Contextual Neural Entropy     |
| - LZMA2 (Presets 0 - 9)         |           | - Nacrith / CMIX Adapters       |
| - Brotli (Quality 0 - 11)       |           | - Model Overhead Verification   |
| - DEFLATE & LZ4                 |           |                                 |
| - Pass-Through (STORE Fallback) |           |                                 |
+---------------------------------+           +---------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                          Archive Container (.god)                             |
|   Header (Magic, Version, Flags, Table Offset, Checksum)                      |
|   Payload Blocks (Block ID, Codec ID, Compressed Data, CRC32/BLAKE3)          |
|   Deduplication & Block Index                                                 |
|   File Table (Relative Paths, Timestamps, Attributes, Block References)       |
|   Footer Integrity Checksum & Trailing Index Pointer                          |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                          Integrity & Security Guard                           |
| - Zero Unsafe Path Traversal (Blocks `..`, drive letters, UNC, ADS)           |
| - Block-by-block and File-level Cryptographic Verification                    |
| - Atomic Extractor with Rollback on Incomplete / Corrupted Archives           |
+-------------------------------------------------------------------------------+
```

---

## 2. Component Deconstructions

### 2.1 Job Controller & Concurrency Pipeline
- **Role**: Mediates all compression, decompression, analysis, and verification workloads.
- **Characteristics**:
  - Non-blocking execution running on dedicated background worker threads (`QThread` / `concurrent.futures`).
  - Strict resource bounding: user-configurable thread counts and memory quotas (e.g. 512 MB to 32 GB).
  - Cancellation semantics: gracefully aborts operations, cleans up temporary swap files, and guarantees no partial/corrupted files replace source files.
  - Progress reporting: delivers granular status events (bytes processed, throughput in MB/s, ETA, compression ratio) at 10 Hz without degrading engine throughput.

### 2.2 Content Analyzer
- **Role**: Quickly examines data characteristics to prune the candidate codec search space.
- **Metrics Computed**:
  - **Shannon Entropy** ($H = -\sum p_i \log_2 p_i$): Identifies random or already compressed data.
  - **Byte Value Distribution & Chi-Square Uniformity**: Differentiates structured text/JSON/code from arbitrary binary.
  - **Magic Byte & File Signature Detection**: Recognizes PNG, JPEG, ZIP, GZ, MP4, MP3, 7Z, PDF, and skips futile re-compression.
  - **Repetition Ratio**: Identifies highly redundant runs for LZ4 or high-dictionary LZMA2.

### 2.3 Adaptive Search Compression Engine
- **Search Strategy by Mode**:
  - `FAST`: Selects either LZ4 or Zstandard (level 1-3) based on basic entropy without candidate trials.
  - `BALANCED`: Characterizes block type, tests top 2 most promising candidate configurations on a sample chunk, selects the winner.
  - `MAXIMUM`: Tests multiple candidate codecs (Zstandard levels 19-22, LZMA2 preset 9, Brotli quality 11, DEFLATE level 9). Accounts for all metadata framing overhead and selects strictly the smallest output. Falls back to `STORE` if compressed size $\ge$ raw size.
  - `RESEARCH`: Engages experimental predictors and contextual neural compression models with round-trip verification.

### 2.4 Deduplication Subsystem
- **Mechanism**: Splits incoming streams into blocks (fixed 1 MB default, or content-defined chunking for repetitive backups).
- **Indexing**: Computes 256-bit BLAKE3 hashes for every chunk. Identical chunks across any file within the archive are stored exactly once and referenced in the file-block map.
- **Collision Safety**: Hashes are verified against cryptographic properties, and chunk lengths must match.

### 2.5 Archive Container (`.god`)
- Fully documented binary specification with versioning, 64-bit offsets, extensible header flags, block table, and file catalog.
- Robust against truncated or malicious inputs with strict parser limits (max entries, max path depth, max unpacked block size).

### 2.6 Security & Integrity Guard
- **Path Guard**: Rejects directory traversal attempts (`..`, `\..\`, `/../`), absolute paths (`/etc/`, `C:\Windows\`), Windows drive letters (`D:`), UNC paths (`\\server\share`), and NTFS alternate data streams (`file:stream`).
- **Cryptographic Hashes**: BLAKE3 and SHA-256 validation per file and block.
- **Atomic Operations**: Decompression writes to `.tmp` files and renames only after full hash verification succeeds.
