# Third-Party Notices & Intellectual Property

**GODZIP Architecture, Container Specification (.god v1.0), Pre-Filter Pipeline, and Desktop Application**  
Copyright (c) 2026 Chandan Bagh <baghchandan53@gmail.com> (GitHub: @cbagh0819-ctrl). Distributed under the MIT License.

---

## Third-Party Libraries & Dependencies

GODZIP interfaces with the following open-source projects:

### 1. Zstandard (zstd)
- **License**: BSD 3-Clause / GPLv2
- **Origin**: Facebook / Meta (`https://github.com/facebook/zstd`)
- **Use in GODZIP**: High-speed, high-compression lossless baseline codec via `python-zstandard`.

### 2. Brotli
- **License**: MIT
- **Origin**: Google (`https://github.com/google/brotli`)
- **Use in GODZIP**: Web/text structured compression codec.

### 3. LZMA2 / 7-Zip
- **License**: GNU LGPL / unRAR restriction
- **Origin**: Igor Pavlov (`https://www.7-zip.org/`)
- **Use in GODZIP**: Maximum ratio dictionary compression backend via Python `lzma` & `py7zr`.

### 4. BLAKE3
- **License**: Apache 2.0 / CC0 1.0 Universal
- **Origin**: Jack O'Connor, Samuel Neves, Jean-Philippe Aumasson, Zooko Wilcox-O'Hearn
- **Use in GODZIP**: Cryptographic integrity and content chunk deduplication hashing.

### 5. LZ4
- **License**: BSD 2-Clause
- **Origin**: Yann Collet (`https://github.com/lz4/lz4`)
- **Use in GODZIP**: Real-time high-throughput streaming compression codec.

### 6. PySide6 (Qt 6 for Python)
- **License**: LGPLv3
- **Origin**: The Qt Company (`https://www.qt.io/`)
- **Use in GODZIP**: Windows desktop user interface framework.

---

### Research References

- **Nacrith**: Robert Tacconelli (`https://github.com/robtacconelli/Nacrith-GPU`). Evaluated under research adapter.
- **CMIX**: Byron Knoll (`https://github.com/byronknoll/cmix`). Evaluated under research adapter.
- **OmniZip**: Zhao et al., CVPR 2026. Evaluated under research adapter.
