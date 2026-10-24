# GODZIP Security & Defensive Architecture

## 1. Threat Model & Defensive Mitigations

GODZIP is built with defense-in-depth principles to process untrusted archive files safely on Windows.

### 1.1 Directory Traversal Protection (Zip Slip / Path Traversal)
- **Attack Vector**: An attacker crafts an archive with filenames such as `../../Windows/System32/evil.dll`, `C:\autoexec.bat`, or `\\remote\share\file`.
- **Mitigation (`path_guard.py`)**:
  - All relative paths inside `.god` archives are strictly validated prior to extraction.
  - Paths are normalized using POSIX slash conventions.
  - Any path containing `..`, absolute Windows drive prefixes (`^[a-zA-Z]:`), UNC network prefixes (`^\\\\`), leading separators, or null bytes is immediately rejected with `UnsafePathException`.
  - The extracted path is checked to ensure `os.path.commonpath([dest_dir, target_path]) == dest_dir`.
  - Alternate Data Streams (e.g. `secret.txt::$DATA` or `file.txt:evil.exe`) are forbidden.

### 1.2 Resource Exhaustion & Denial of Service (Zip Bombs)
- **Attack Vector**: An archive with high compression ratios expands billions of uncompressed bytes into RAM or disk.
- **Mitigation**:
  - Block sizes are capped at 64 MB uncompressed.
  - The maximum decompression expansion ratio is validated: any block claiming $\ge 1000\times$ expansion without user override triggers a safety abort.
  - Decompression is streamed to disk in bounded buffer chunks (64 KB). The total written bytes are tracked against stated entry limits.

### 1.3 Cryptographic Integrity & Tamper Detection
- **Mechanism**:
  - Every block carries a 256-bit cryptographic digest (BLAKE3 or SHA-256) plus a 32-bit CRC.
  - Every file record stores a cumulative digest of its original content.
  - During extraction, each block is verified as it is decompressed. If the hash does not match, extraction fails immediately.
  - Output is written to temporary files (`*.tmp.godzip.*`) in the destination directory and only atomically renamed to the final filename after full cryptographic verification passes.

### 1.4 Code Execution & Serialization Safety
- **Policy**:
  - The `.god` container uses a strictly defined binary layout (fixed struct headers + binary length-prefixed fields).
  - No Python `pickle`, `yaml.unsafe_load`, or arbitrary executable serialization formats are ever parsed from archives.
  - No arbitrary shell commands or subprocess execution are triggered by archive contents or the desktop GUI.
