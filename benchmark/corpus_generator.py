"""Automated corpus generator creating repeatable legal datasets across all 14 categories."""

import os
import json
import struct
import math
import hashlib
from pathlib import Path
from typing import Dict, List


def generate_benchmark_corpus(output_dir: str) -> Dict[str, str]:
    """Generates synthetic and deterministic test files for all 14 benchmark categories.
    
    Returns a dictionary mapping category_id -> absolute file/folder path.
    """
    base = Path(output_dir).resolve()
    base.mkdir(parents=True, exist_ok=True)
    paths: Dict[str, str] = {}

    # 1. Plain text and logs (syslog & web log style)
    cat1 = base / "01_text_logs.log"
    with open(cat1, "w", encoding="utf-8") as f:
        for i in range(5000):
            f.write(f"2026-10-24 10:{i%60:02d}:{(i*7)%60:02d} [INFO] worker-{i%8} Processed request #{i} status=200 latency={i%50}.{i%9}ms ip=192.168.1.{i%254}\n")
    paths["text_logs"] = str(cat1)

    # 2. Source code repository (multi-file C / Python tree)
    cat2_dir = base / "02_source_code"
    cat2_dir.mkdir(exist_ok=True)
    with open(cat2_dir / "main.c", "w", encoding="utf-8") as f:
        f.write("""#include <stdio.h>\n#include <stdlib.h>\n\nint main(int argc, char** argv) {\n    for (int i = 0; i < 1000; i++) {\n        printf("Index: %d\\n", i);\n    }\n    return 0;\n}\n""")
    with open(cat2_dir / "algo.py", "w", encoding="utf-8") as f:
        f.write("""import math\n\ndef sieve(n):\n    primes = [True] * (n + 1)\n    p = 2\n    while p * p <= n:\n        if primes[p]:\n            for i in range(p * p, n + 1, p):\n                primes[i] = False\n        p += 1\n    return [p for p in range(2, n + 1) if primes[p]]\n""" * 20)
    paths["source_code"] = str(cat2_dir)

    # 3. JSON & Tabular CSV
    cat3 = base / "03_data.json"
    records = [{"id": i, "user": f"user_{i}", "score": i * 1.5, "tags": ["admin", "dev"] if i % 2 == 0 else ["guest"]} for i in range(2000)]
    with open(cat3, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    paths["json_csv"] = str(cat3)

    # 4. XML and HTML
    cat4 = base / "04_document.html"
    with open(cat4, "w", encoding="utf-8") as f:
        f.write("<!DOCTYPE html><html><head><title>Benchmark HTML</title></head><body>\n")
        for i in range(1500):
            f.write(f'<div class="card" id="item-{i}"><h3 class="title">Section Header {i}</h3><p class="body">Detailed paragraph content with repeating boilerplate structure.</p></div>\n')
        f.write("</body></html>\n")
    paths["xml_html"] = str(cat4)

    # 5. Documents and synthetic PDF
    cat5 = base / "05_document.pdf"
    with open(cat5, "wb") as f:
        f.write(b"%PDF-1.4\n")
        f.write(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
        for i in range(500):
            f.write(f"obj {i+2} << /Length {i*10} >> stream\nSample document uncompressed text streams with dictionary cross references {i}\nendstream endobj\n".encode("utf-8"))
        f.write(b"%%EOF\n")
    paths["documents_pdf"] = str(cat5)

    # 6. Uncompressed Bitmap BMP (24 bpp, repetitive color runs and gradients)
    cat6 = base / "06_image.bmp"
    w, h = 256, 256
    row_bytes = w * 3
    padding = (4 - (row_bytes % 4)) % 4
    file_size = 54 + (row_bytes + padding) * h
    with open(cat6, "wb") as f:
        # BMP Header (14 bytes)
        f.write(struct.pack("<2sIHHI", b"BM", file_size, 0, 0, 54))
        # DIB Header (40 bytes)
        f.write(struct.pack("<IIIHHIIIIII", 40, w, h, 1, 24, 0, (row_bytes + padding) * h, 2835, 2835, 0, 0))
        for y in range(h):
            for x in range(w):
                f.write(bytes([(x % 256), ((x + y) % 256), (y % 256)]))
            if padding:
                f.write(b"\x00" * padding)
    paths["uncompressed_bmp"] = str(cat6)

    # 7. Pre-compressed PNG / JPEG image
    cat7 = base / "07_compressed.png"
    # Valid minimal PNG 1x1 pixel with zlib compressed payload
    png_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    with open(cat7, "wb") as f:
        f.write(png_data * 200) # Precompressed repeated PNG chunks
    paths["compressed_image"] = str(cat7)

    # 8. Pre-compressed MP4 Video container
    cat8 = base / "08_video.mp4"
    with open(cat8, "wb") as f:
        f.write(b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00isommp42")
        # Simulating pseudo-random mdat payload typical of h264
        prng = hashlib.sha256(b"seed_mp4")
        for _ in range(500):
            prng.update(b"video_block")
            f.write(prng.digest())
    paths["compressed_video"] = str(cat8)

    # 9. Audio: Uncompressed 16-bit WAV PCM
    cat9 = base / "09_audio.wav"
    sample_rate = 8000
    duration = 2
    num_samples = sample_rate * duration
    with open(cat9, "wb") as f:
        # RIFF header
        f.write(b"RIFF")
        f.write(struct.pack("<I", 36 + num_samples * 2))
        f.write(b"WAVEfmt ")
        f.write(struct.pack("<IHHIIHH", 16, 1, 1, sample_rate, sample_rate * 2, 2, 16))
        f.write(b"data")
        f.write(struct.pack("<I", num_samples * 2))
        for i in range(num_samples):
            # 440 Hz sine wave
            val = int(10000 * math.sin(2 * math.pi * 440 * i / sample_rate))
            f.write(struct.pack("<h", val))
    paths["audio_wav"] = str(cat9)

    # 10. 3D Model Wavefront OBJ
    cat10 = base / "10_mesh.obj"
    with open(cat10, "w", encoding="utf-8") as f:
        f.write("# GODZIP 3D Benchmark Mesh\n")
        for i in range(1000):
            f.write(f"v {(i*0.1):.4f} {(math.sin(i)*2):.4f} {(math.cos(i)*2):.4f}\n")
            f.write(f"vn {((i%5)*0.2):.2f} {((i%3)*0.33):.2f} 1.00\n")
        for i in range(1, 999):
            f.write(f"f {i}//{i} {i+1}//{i+1} {i+2}//{i+2}\n")
    paths["mesh_3d"] = str(cat10)

    # 11. Software package / DLL binary structure
    cat11 = base / "11_binary.dll"
    with open(cat11, "wb") as f:
        # PE DOS header MZ
        f.write(b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00")
        f.write(b"\xb8\x00\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00")
        f.write(b"This program cannot be run in DOS mode.\r\r\n$\x00\x00\x00\x00")
        # Mixed machine code patterns + zero padding sections
        for i in range(200):
            f.write(b"\x55\x89\xe5\x83\xec\x10\x8b\x45\x08" * 50)
            f.write(b"\x00" * 256)
    paths["software_pkg"] = str(cat11)

    # 12. High-entropy / pseudorandom binary
    cat12 = base / "12_random.bin"
    with open(cat12, "wb") as f:
        h = hashlib.sha256(b"pseudorandom_seed")
        for _ in range(1000):
            h.update(b"next")
            f.write(h.digest())
    paths["random_binary"] = str(cat12)

    # 13. Encrypted block sample
    cat13 = base / "13_encrypted.enc"
    with open(cat13, "wb") as f:
        h = hashlib.sha256(b"aes_cipher_simulation")
        for _ in range(500):
            h.update(b"iv_cipher")
            f.write(h.digest())
    paths["encrypted_sample"] = str(cat13)

    # 14. Repeated backups for deduplication
    cat14_dir = base / "14_backup_snapshots"
    cat14_dir.mkdir(exist_ok=True)
    shared_data = b"Shared enterprise database cluster snapshot block\n" * 1000
    with open(cat14_dir / "snapshot_v1.db", "wb") as f:
        f.write(shared_data + b"V1 SPECIFIC LOGS\n" * 100)
    with open(cat14_dir / "snapshot_v2.db", "wb") as f:
        f.write(shared_data + b"V2 SPECIFIC LOGS\n" * 100)
    paths["dedup_snapshots"] = str(cat14_dir)

    return paths
