# GODZIP Benchmark Protocol & Measurement Methodology

## 1. Principles of Scientific Measurement

In accordance with strict scientific integrity:
1. **Never Guarantee 70–90% Compression**: Pre-compressed or pseudo-random data cannot be compressed without data loss. GODZIP measures actual byte results and reports honest compression ratios.
2. **Apple-to-Apple Size Accounting**: All reported archive sizes must include container headers, metadata, block framing, dictionaries, and index tables.
3. **Reproducibility**: Exact software versions, compression levels, hardware parameters, and test datasets must be logged.
4. **Byte-for-Byte Exactness**: Decompressed output must match the original uncompressed source byte-for-byte; otherwise, the benchmark run is marked as `FAILED`.

## 2. Benchmark Corpus Categories

The standard GODZIP benchmark suite spans 14 distinct data categories:
1. **Plain Text & System Logs**: Linux syslog, Apache web server logs.
2. **Source Code Repositories**: C/Rust/Python multi-file tree.
3. **JSON & Tabular CSV**: High-density schema data.
4. **XML & HTML**: Deeply nested tag structures.
5. **Documents**: Mixed PDF and Office document structures.
6. **Uncompressed Bitmaps & Repetitive Graphics**: BMP 24bpp images with runs and gradients.
7. **Pre-Compressed Images**: JPEG, PNG, WebP.
8. **Pre-Compressed Video**: MP4 container samples.
9. **Audio**: Uncompressed 16-bit WAV PCM and compressed audio.
10. **3D Models & Game Assets**: Wavefront OBJ and ASCII geometry.
11. **Software Packages**: Dynamic libraries and binary executables.
12. **High-Entropy / Pseudorandom Binary**: Cryptographic RNG output.
13. **Encrypted Blocks**: AES ciphertext samples.
14. **Deduplication Snapshots**: Multi-version backups sharing redundant data blocks.

## 3. Evaluated Metrics

- `original_bytes`: Raw source size.
- `archive_bytes`: Output archive size including all framing and metadata.
- `reduction_pct`: $(1 - \text{archive\_bytes} / \text{original\_bytes}) \times 100\%$.
- `compression_ratio`: $\text{original\_bytes} / \text{archive\_bytes}$.
- `compression_time_sec`: Wall-clock duration of archive creation.
- `decompression_time_sec`: Wall-clock duration of byte-exact restoration.
- `compression_mbps`: Throughput in Megabytes per second ($\text{original\_mb} / \text{time}$).
- `peak_memory_mb`: Maximum Resident Set Size (RSS) during execution.
- `hash_verified`: Boolean verifying decompressed digest == original digest.
