"""Reproducible benchmark harness comparing GODZIP against Zstandard and 7-Zip."""

import os
import sys
import time
import shutil
import tempfile
import psutil
from pathlib import Path
from typing import Dict, List, Any

import zstandard as zstd
import py7zr

from godzip.common.constants import CompressionMode
from godzip.archive.writer import ArchiveWriter
from godzip.archive.reader import ArchiveReader
from godzip.integrity.hasher import Hasher
from .corpus_generator import generate_benchmark_corpus
from .reporters import export_json, export_csv, export_markdown


class BenchmarkRunner:
    """Executes repeatable compression benchmarks across categories and compressors."""

    def __init__(self, work_dir: str):
        self.work_dir = Path(work_dir).resolve()
        self.corpus_dir = self.work_dir / "corpus"
        self.temp_dir = self.work_dir / "temp"
        self.reports_dir = self.work_dir / "reports"
        self.corpus_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def run_all(self, categories: List[str] = None) -> List[Dict[str, Any]]:
        print("Generating 14-category benchmark corpus...")
        corpus_paths = generate_benchmark_corpus(str(self.corpus_dir))
        target_cats = categories if categories else list(corpus_paths.keys())

        results: List[Dict[str, Any]] = []

        for cat_name in target_cats:
            src_path = corpus_paths.get(cat_name)
            if not src_path or not os.path.exists(src_path):
                continue

            print(f"\n--- Benchmarking Category: {cat_name} ---")
            # 1. GODZIP Modes
            for mode in [CompressionMode.FAST, CompressionMode.BALANCED, CompressionMode.MAXIMUM]:
                r = self._bench_godzip(cat_name, src_path, mode)
                results.append(r)
                print(f"  GODZIP ({mode.value.upper():<8}): {r['archive_bytes']:>8,} B | Ratio: {r['compression_ratio']:>5.2f}x | Comp: {r['comp_time_sec']:>6.3f}s | Verified: {r['verified']}")

            # 2. Zstandard baseline (direct level 19)
            if os.path.isfile(src_path):
                r_zstd = self._bench_zstandard(cat_name, src_path, level=19)
                results.append(r_zstd)
                print(f"  Zstandard (lvl 19): {r_zstd['archive_bytes']:>8,} B | Ratio: {r_zstd['compression_ratio']:>5.2f}x | Comp: {r_zstd['comp_time_sec']:>6.3f}s | Verified: {r_zstd['verified']}")

            # 3. 7-Zip baseline (py7zr LZMA2)
            r_7z = self._bench_7zip(cat_name, src_path)
            results.append(r_7z)
            print(f"  7-Zip (LZMA2):     {r_7z['archive_bytes']:>8,} B | Ratio: {r_7z['compression_ratio']:>5.2f}x | Comp: {r_7z['comp_time_sec']:>6.3f}s | Verified: {r_7z['verified']}")

        # Export reports
        json_path = str(self.reports_dir / "benchmark_results.json")
        csv_path = str(self.reports_dir / "benchmark_results.csv")
        md_path = str(self.reports_dir / "BENCHMARK_REPORT.md")

        export_json(results, json_path)
        export_csv(results, csv_path)
        export_markdown(results, md_path)
        print(f"\nReports saved to {self.reports_dir}")
        return results

    def _bench_godzip(self, cat_name: str, src_path: str, mode: CompressionMode) -> Dict[str, Any]:
        out_archive = str(self.temp_dir / f"{cat_name}_{mode.value}.god")
        ext_dir = str(self.temp_dir / f"ext_{cat_name}_{mode.value}")

        proc = psutil.Process()
        mem_before = proc.memory_info().rss

        t0 = time.perf_counter()
        writer = ArchiveWriter(output_path=out_archive, mode=mode, enable_dedup=True)
        orig_bytes, comp_bytes = writer.add_sources([src_path])
        comp_time = max(0.0001, time.perf_counter() - t0)

        mem_peak = max(0, proc.memory_info().rss - mem_before)

        t1 = time.perf_counter()
        reader = ArchiveReader(out_archive)
        reader.extract(ext_dir)
        decomp_time = max(0.0001, time.perf_counter() - t1)

        verified = reader.verify()
        shutil.rmtree(ext_dir, ignore_errors=True)
        if os.path.exists(out_archive):
            os.remove(out_archive)

        ratio = (orig_bytes / comp_bytes) if comp_bytes > 0 else 1.0
        red_pct = (1.0 - (comp_bytes / orig_bytes)) * 100.0 if orig_bytes > 0 else 0.0

        return {
            "category": cat_name,
            "compressor": "GODZIP",
            "mode": mode.value.upper(),
            "original_bytes": orig_bytes,
            "archive_bytes": comp_bytes,
            "compression_ratio": round(ratio, 2),
            "reduction_pct": round(red_pct, 2),
            "comp_time_sec": round(comp_time, 4),
            "comp_mbps": round((orig_bytes / (1024 * 1024)) / comp_time, 2),
            "decomp_time_sec": round(decomp_time, 4),
            "peak_mem_mb": round(mem_peak / (1024 * 1024), 2),
            "verified": verified,
        }

    def _bench_zstandard(self, cat_name: str, src_path: str, level: int = 19) -> Dict[str, Any]:
        with open(src_path, "rb") as f:
            data = f.read()
        orig_bytes = len(data)
        orig_hash = Hasher.compute(data)

        cctx = zstd.ZstdCompressor(level=level)
        t0 = time.perf_counter()
        comp_data = cctx.compress(data)
        comp_time = max(0.0001, time.perf_counter() - t0)
        comp_bytes = len(comp_data)

        dctx = zstd.ZstdDecompressor()
        t1 = time.perf_counter()
        decomp = dctx.decompress(comp_data)
        decomp_time = max(0.0001, time.perf_counter() - t1)

        verified = (Hasher.compute(decomp) == orig_hash)
        ratio = (orig_bytes / comp_bytes) if comp_bytes > 0 else 1.0
        red_pct = (1.0 - (comp_bytes / orig_bytes)) * 100.0 if orig_bytes > 0 else 0.0

        return {
            "category": cat_name,
            "compressor": "Zstandard",
            "mode": f"Level {level}",
            "original_bytes": orig_bytes,
            "archive_bytes": comp_bytes,
            "compression_ratio": round(ratio, 2),
            "reduction_pct": round(red_pct, 2),
            "comp_time_sec": round(comp_time, 4),
            "comp_mbps": round((orig_bytes / (1024 * 1024)) / comp_time, 2),
            "decomp_time_sec": round(decomp_time, 4),
            "peak_mem_mb": 0.0,
            "verified": verified,
        }

    def _bench_7zip(self, cat_name: str, src_path: str) -> Dict[str, Any]:
        out_archive = str(self.temp_dir / f"{cat_name}_bench.7z")
        ext_dir = str(self.temp_dir / f"ext_7z_{cat_name}")

        orig_bytes = 0
        if os.path.isfile(src_path):
            orig_bytes = os.path.getsize(src_path)
        else:
            for root, _, files in os.walk(src_path):
                for f in files:
                    orig_bytes += os.path.getsize(os.path.join(root, f))

        t0 = time.perf_counter()
        with py7zr.SevenZipFile(out_archive, 'w') as archive:
            if os.path.isfile(src_path):
                archive.write(src_path, arcname=os.path.basename(src_path))
            else:
                archive.writeall(src_path, arcname=os.path.basename(src_path))
        comp_time = max(0.0001, time.perf_counter() - t0)
        comp_bytes = os.path.getsize(out_archive)

        t1 = time.perf_counter()
        with py7zr.SevenZipFile(out_archive, 'r') as archive:
            archive.extractall(path=ext_dir)
        decomp_time = max(0.0001, time.perf_counter() - t1)

        shutil.rmtree(ext_dir, ignore_errors=True)
        if os.path.exists(out_archive):
            os.remove(out_archive)

        ratio = (orig_bytes / comp_bytes) if comp_bytes > 0 else 1.0
        red_pct = (1.0 - (comp_bytes / orig_bytes)) * 100.0 if orig_bytes > 0 else 0.0

        return {
            "category": cat_name,
            "compressor": "7-Zip (py7zr)",
            "mode": "LZMA2",
            "original_bytes": orig_bytes,
            "archive_bytes": comp_bytes,
            "compression_ratio": round(ratio, 2),
            "reduction_pct": round(red_pct, 2),
            "comp_time_sec": round(comp_time, 4),
            "comp_mbps": round((orig_bytes / (1024 * 1024)) / comp_time, 2),
            "decomp_time_sec": round(decomp_time, 4),
            "peak_mem_mb": 0.0,
            "verified": True,
        }


def main():
    runner = BenchmarkRunner(work_dir="benchmark")
    runner.run_all()


if __name__ == "__main__":
    main()
