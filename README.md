# GODZIP

**Next-Generation Intelligent Lossless Compression Platform for Windows**

GODZIP (`.god`) is a modular, high-compression lossless archiver and Windows desktop application. Instead of applying one compression algorithm blindly across all files, GODZIP uses statistical content analysis (Shannon entropy, byte distributions, magic signatures), block deduplication, and an **Adaptive Search Engine** to select the optimal codec for every chunk of data.

---

## Key Features

- **Multi-Codec Architecture**: Combines Zstandard, LZMA2 (7-Zip compatible), Brotli, DEFLATE, and LZ4 with automatic `STORE` fallback when compression causes expansion.
- **Adaptive Search Engine**: Four distinct modes:
  - `FAST`: Prioritizes throughput using fast Zstd/LZ4 without exhaustive search.
  - `BALANCED`: Classifies content and tests top candidate configurations on representative blocks.
  - `MAXIMUM`: Tests high-ratio codecs (Zstd 22, LZMA2 9, Brotli 11) accounting for all container framing overhead to find the smallest lossless representation.
  - `RESEARCH`: Contextual neural entropy prediction models for structured text.
- **Block-Level Deduplication**: Splits streams into blocks and stores identical blocks only once across the entire archive using 256-bit BLAKE3 hashes.
- **Strict Security & Integrity**:
  - Full path traversal protection (blocks `..`, Windows drive letters, UNC, and NTFS Alternate Data Streams).
  - Cryptographic verification per block and per file.
  - Atomic file commit via temporary swap files.
- **Benchmark Lab**: Built-in 14-category corpus testing against standard compressors with CSV, JSON, and Markdown export.
- **Polished Windows Desktop GUI**: Native Qt 6 (PySide6) interface styled in charcoal and subtle crimson with 7 dedicated views: Dashboard, Workspace, Live Monitor, Inspector, Benchmark Lab, Settings, and About.

---

## Completed vs Planned Features

| Feature | Status | Notes |
|---|---|---|
| Binary `.god` container v1.0 | **Completed** | Full streaming reader and writer |
| Zstandard, LZMA2, Brotli, Deflate, LZ4, Store | **Completed** | Production-ready lossless codecs |
| Content Analyzer (Entropy & Signatures) | **Completed** | Shannon entropy, byte stats, magic bytes |
| Block Deduplication | **Completed** | BLAKE3 chunk index & duplicate avoidance |
| Adaptive Search Selection | **Completed** | Fast, Balanced, Maximum, and Research |
| Path Traversal Defense (`path_guard`) | **Completed** | Blocks Zip-slip, drive paths, ADS |
| Atomic File Commit & Hash Verification | **Completed** | Validates before replacing destination |
| CLI Interface (`godzip`) | **Completed** | create, extract, inspect, verify, benchmark |
| Qt 6 Windows Desktop GUI | **Completed** | Dark theme, 7 responsive tabs, live monitor |
| 14-Category Benchmark Corpus Generator | **Completed** | Repeatable synthetic & legal corpus |
| Nacrith / CMIX / OmniZip Research Adapters | **Completed** | Documented research evaluation modules |
| AES-256-GCM Archive Encryption | *Planned v1.1* | Container flag bit reserved |

---

## Installation & Running

### Requirements
- Windows 10/11 x64
- Python 3.10+ (tested on Python 3.12)
- Dependencies: `pip install -r requirements.txt`

### Launching the Desktop Application
```powershell
python -m godzip.ui.app
# Or run using launcher:
powershell -ExecutionPolicy Bypass -File scripts\launch_gui.ps1
```

### Command Line Interface
```powershell
# Create an archive (Maximum compression mode)
python -m godzip.cli create --input "path\to\folder" --output "backup.god" --mode max

# Inspect archive metadata without extracting
python -m godzip.cli inspect --archive "backup.god"

# Verify archive integrity
python -m godzip.cli verify --archive "backup.god"

# Extract archive safely
python -m godzip.cli extract --archive "backup.god" --output "extracted_folder"

# Run the 14-category benchmark suite
python -m godzip.cli benchmark --output-dir "benchmark\reports"
```

### Running Tests
```powershell
pytest tests -v
# Or run using script:
powershell -ExecutionPolicy Bypass -File scripts\run_tests.ps1
```
