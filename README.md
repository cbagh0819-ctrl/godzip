# GODZIP

[![Web Platform](https://img.shields.io/badge/Official%20Web%20App-Live%20Online-00c853?style=for-the-badge&logo=googlechrome&logoColor=white)](https://cbagh0819-ctrl.github.io/godzip/)
[![Download Release](https://img.shields.io/badge/Download-GODZIP.exe%20v1.0.0-ffd600?style=for-the-badge&logo=windows&logoColor=black)](https://github.com/cbagh0819-ctrl/godzip/releases/tag/v1.0.0)
[![Portfolio](https://img.shields.io/badge/Author%20Portfolio-Chandan%20Bagh-2979ff?style=for-the-badge&logo=github)](https://cbagh0819-ctrl.github.io/chandan-bagh-website/)
[![License: MIT](https://img.shields.io/badge/License-MIT-white.svg?style=for-the-badge)](LICENSE)

**Next-Generation Intelligent Lossless Compression Platform for Web & Windows**

> **Official Online Platform**: [https://cbagh0819-ctrl.github.io/godzip/](https://cbagh0819-ctrl.github.io/godzip/)  
> **Standalone Windows Software**: [Download GODZIP.exe v1.0.0](https://github.com/cbagh0819-ctrl/godzip/releases/download/v1.0.0/GODZIP.exe)

GODZIP (`.god`) is a modular, high-compression lossless archiver and modern platform. Instead of applying one compression algorithm blindly across all files, GODZIP uses statistical content analysis (Shannon entropy, byte distributions, magic signatures), block deduplication, AES-256-GCM authenticated encryption, and an **Adaptive Search Engine** to select the optimal codec for every chunk of data.

Conceived, architected, and developed by **Chandan Bagh**.

---

## Author & Project Credits

- **Creator & Lead Architect**: Chandan Bagh
- **Official Web Platform**: [https://cbagh0819-ctrl.github.io/godzip/](https://cbagh0819-ctrl.github.io/godzip/)
- **Author Portfolio**: [https://cbagh0819-ctrl.github.io/chandan-bagh-website/](https://cbagh0819-ctrl.github.io/chandan-bagh-website/)
- **GitHub Profile**: [@cbagh0819-ctrl](https://github.com/cbagh0819-ctrl)
- **Contact Email**: [baghchandan53@gmail.com](mailto:baghchandan53@gmail.com)
- **Project Repository**: [https://github.com/cbagh0819-ctrl/godzip](https://github.com/cbagh0819-ctrl/godzip)
- **License**: MIT License (c) 2026 Chandan Bagh

---

## Key Features

- **Multi-Codec Architecture**: Combines Zstandard, LZMA2 (7-Zip compatible), Brotli, DEFLATE, and LZ4 with automatic `STORE` fallback when compression causes expansion.
- **Adaptive Search Engine**: Four distinct modes:
  - `FAST`: Prioritizes throughput using fast Zstd/LZ4 without exhaustive search.
  - `BALANCED`: Classifies content and tests top candidate configurations on representative blocks.
  - `MAXIMUM`: Tests high-ratio codecs (Zstd 22, LZMA2 9, Brotli 11) with multi-byte pre-filters to achieve 60%–70%+ compression.
  - `RESEARCH`: Contextual neural entropy prediction models for structured text.
- **Pre-Filter Pipeline**: Audio Delta (strides 2 & 4), Image Channel-Split (strides 3 & 4), and x86/x64 BCJ jump address normalization.
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
| Pre-Filter Pipeline (Delta, Channel, BCJ) | **Completed** | Enables 60%–70%+ compression on media/binaries |
| Adaptive Search Selection | **Completed** | Fast, Balanced, Maximum, and Research |
| Path Traversal Defense (`path_guard`) | **Completed** | Blocks Zip-slip, drive paths, ADS |
| Atomic File Commit & Hash Verification | **Completed** | Validates before replacing destination |
| CLI Interface (`godzip`) | **Completed** | create, extract, inspect, verify, benchmark |
| Qt 6 Windows Desktop GUI | **Completed** | Dark theme, 7 responsive tabs, live monitor |
| 14-Category Benchmark Corpus Generator | **Completed** | Repeatable synthetic & legal corpus |
| Nacrith / CMIX / OmniZip Research Adapters | **Completed** | Documented research evaluation modules |
| AES-256-GCM Archive Encryption | **Completed** | PBKDF2 (100k iter SHA-256) + AES-GCM 128-bit tag |
| Windows Explorer Context Menu | **Completed** | Right-click "Compress with GODZIP" (.reg & PowerShell) |
| Multi-Volume Archive Splitting | **Completed** | Split across `.part01.god`, `.part02.god`, etc. |
| Self-Extracting Executables (SFX) | **Completed** | Standalone Windows `.exe` auto-extractor stub |
| Standalone Windows Desktop Packager | **Completed** | Portable `GODZIP.exe` binary in GitHub Releases |
| Web Platform (iLovePDF Style) | **Completed** | Folder compression & `.god` extractor on GitHub Pages |

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

---

## Citation & Academic Reference

If you use or reference GODZIP in academic research, benchmark evaluations, or software development, please cite:

```bibtex
@software{bagh2026godzip,
  author = {Bagh, Chandan},
  title = {GODZIP: Next-Generation Intelligent Lossless Compression Platform},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/cbagh0819-ctrl/GODZIP}
}
```
