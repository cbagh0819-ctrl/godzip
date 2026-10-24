# Architecture Decision Records (ADR)

## ADR-001: Binary Container Format Layout
- **Decision**: Design a custom deterministic binary container (`.god` v1.0) with an 8-byte magic header (`GODZIP\x01\x00`), 64-bit offsets, chunk-level deduplication block table, file catalog, and trailing index mirror.
- **Rationale**: Standard formats (TAR, ZIP) lack native multi-codec block-level deduplication, per-block cryptographic hashes, and adaptive codec framing. A custom container enables storing mixed codecs within a single archive (e.g. Brotli for text, Zstd for binary, Store for JPEG) while maintaining streaming decompression.

## ADR-002: Desktop Framework Selection (PySide6 / Qt 6)
- **Decision**: Use PySide6 (Qt 6.12) for the Windows desktop interface.
- **Rationale**: Rust cargo and MSVC compiler are not installed in the Windows environment, whereas Python 3.12 with PySide6 is fully installed and provides native Windows x64 rendering, dark styling, QThread concurrency, drag-and-drop, high-DPI scaling, and direct memory sharing with high-performance C-accelerated codecs (zstandard, brotli, lz4, blake3).

## ADR-003: Cryptographic Integrity Scheme
- **Decision**: Employ BLAKE3 as primary cryptographic digest (with SHA-256 fallback), stored in 32-byte fields per block and per file.
- **Rationale**: BLAKE3 provides cryptographic security equivalent to SHA-256 while operating at several gigabytes per second on x64 SIMD, preventing hash verification from bottlenecking compression/decompression throughput.

## ADR-004: Defense-in-Depth Path Traversal Sanitization
- **Decision**: Enforce path normalization and reject any archive member containing relative parent paths (`..`), Windows drive prefixes (`C:`), network paths (`\\`), or NTFS alternate data streams (`::$DATA`). Write uncommitted files to `.tmp` files with atomic rename.
- **Rationale**: Prevents Zip Slip and overwrite vulnerabilities from malicious or corrupted archives.
