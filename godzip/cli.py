"""GODZIP Command-Line Interface."""

import argparse
import sys
import os
import time
from pathlib import Path
from .common.constants import CompressionMode
from .common.types import JobProgress
from .archive.writer import ArchiveWriter
from .archive.reader import ArchiveReader
from .analyzer.analyzer import ContentAnalyzer


def _print_progress(p: JobProgress) -> None:
    pct = (p.bytes_processed / p.total_bytes * 100) if p.total_bytes > 0 else 100
    bar_len = 25
    filled = int(bar_len * (pct / 100.0))
    bar = "=" * filled + "-" * (bar_len - filled)
    sys.stdout.write(f"\r[{bar}] {pct:5.1f}% | {p.throughput_mbps:6.1f} MB/s | {p.current_file[:25]:<25}")
    sys.stdout.flush()


def cmd_create(args) -> int:
    inputs = args.input
    output = args.output
    mode_map = {
        "fast": CompressionMode.FAST,
        "balanced": CompressionMode.BALANCED,
        "max": CompressionMode.MAXIMUM,
        "research": CompressionMode.RESEARCH,
    }
    mode = mode_map.get(args.mode.lower(), CompressionMode.BALANCED)
    print(f"GODZIP: Creating archive '{output}' (Mode: {mode.value.upper()}, Dedup: {not args.no_dedup})...")
    
    start_time = time.time()
    writer = ArchiveWriter(
        output_path=output,
        mode=mode,
        enable_dedup=not args.no_dedup,
        password=args.password,
        progress_callback=_print_progress,
    )
    orig_bytes, comp_bytes = writer.add_sources(inputs)
    sys.stdout.write("\n")
    elapsed = max(0.001, time.time() - start_time)
    ratio = (orig_bytes / comp_bytes) if comp_bytes > 0 else 1.0
    red_pct = (1.0 - (comp_bytes / orig_bytes)) * 100.0 if orig_bytes > 0 else 0.0

    print(f"Archive created successfully in {elapsed:.2f}s!")
    print(f"  Original Size:   {orig_bytes:,} bytes")
    print(f"  Archive Size:    {comp_bytes:,} bytes")
    print(f"  Ratio:           {ratio:.2f}:1 ({red_pct:.1f}% space saved)")
    return 0


def cmd_extract(args) -> int:
    archive = args.archive
    output = args.output or "."
    print(f"GODZIP: Extracting '{archive}' to '{output}'...")
    start_time = time.time()
    reader = ArchiveReader(archive, password=args.password)
    bytes_written = reader.extract(
        destination_dir=output,
        progress_callback=_print_progress
    )
    sys.stdout.write("\n")
    elapsed = max(0.001, time.time() - start_time)
    print(f"Extracted {len(reader.files)} files ({bytes_written:,} bytes) in {elapsed:.2f}s with verified integrity.")
    return 0


def cmd_inspect(args) -> int:
    archive = args.archive
    reader = ArchiveReader(archive)
    info = reader.inspect()
    print("=" * 60)
    print(f"GODZIP Archive: {info['archive_path']}")
    print(f"Format Version: v{info['version']} | Flags: 0x{info['flags']:02x}")
    print(f"Files: {info['total_files']} | Blocks: {info['total_blocks']}")
    print(f"Original: {info['original_bytes']:,} bytes | Compressed: {info['compressed_bytes']:,} bytes")
    print(f"Ratio: {info['compression_ratio']:.2f}:1 ({info['reduction_pct']:.1f}% reduction)")
    print("-" * 60)
    print(f"{'Path':<35} {'Size':>10} {'Blocks':>7}")
    print("-" * 60)
    for f in info["files"][:25]:
        print(f"{f['path'][:35]:<35} {f['original_size']:>10,} {f['blocks']:>7}")
    if len(info["files"]) > 25:
        print(f"... and {len(info['files']) - 25} more files.")
    print("=" * 60)
    return 0


def cmd_verify(args) -> int:
    archive = args.archive
    print(f"GODZIP: Verifying cryptographic digests for '{archive}'...")
    reader = ArchiveReader(archive, password=args.password)
    reader.verify(progress_callback=_print_progress)
    sys.stdout.write("\n")
    print("All blocks and file checksums verified: 100% BYTE-EXACT INTEGRITY CONFIRMED.")
    return 0


def cmd_analyze(args) -> int:
    path = args.path
    with open(path, "rb") as fp:
        data = fp.read(131072)
    profile = ContentAnalyzer.analyze(data)
    print(f"Content Analysis for '{path}':")
    print(f"  Shannon Entropy:      {profile.shannon_entropy:.4f} bits/byte")
    print(f"  Printable ASCII:      {profile.ascii_ratio * 100:.1f}%")
    print(f"  Zero Bytes:           {profile.zero_ratio * 100:.1f}%")
    print(f"  Unique Byte Count:    {profile.unique_byte_count} / 256")
    print(f"  Detected Magic:       {profile.detected_format}")
    print(f"  Precompressed:        {profile.likely_precompressed}")
    print(f"  Recommended Class:    {profile.recommended_class}")
    return 0


def main():
    parser = argparse.ArgumentParser(prog="godzip", description="GODZIP Next-Generation Lossless Archiver")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Create
    p_create = subparsers.add_parser("create", help="Create a .god archive")
    p_create.add_argument("-i", "--input", nargs="+", required=True, help="Input files or directories")
    p_create.add_argument("-o", "--output", required=True, help="Destination .god file")
    p_create.add_argument("-m", "--mode", default="balanced", choices=["fast", "balanced", "max", "research"], help="Compression mode")
    p_create.add_argument("--no-dedup", action="store_true", help="Disable deduplication")
    p_create.add_argument("-p", "--password", default=None, help="Encrypt archive with AES-256-GCM password")

    # Extract
    p_extract = subparsers.add_parser("extract", help="Extract a .god archive")
    p_extract.add_argument("-a", "--archive", required=True, help="Input .god file")
    p_extract.add_argument("-o", "--output", default=".", help="Output directory")
    p_extract.add_argument("-p", "--password", default=None, help="Password for encrypted archive")

    # Inspect
    p_inspect = subparsers.add_parser("inspect", help="Inspect archive structure and file list")
    p_inspect.add_argument("-a", "--archive", required=True, help="Input .god file")

    # Verify
    p_verify = subparsers.add_parser("verify", help="Verify archive block and file digests")
    p_verify.add_argument("-a", "--archive", required=True, help="Input .god file")
    p_verify.add_argument("-p", "--password", default=None, help="Password for encrypted archive")

    # Analyze
    p_analyze = subparsers.add_parser("analyze", help="Analyze data profile of a file")
    p_analyze.add_argument("path", help="File to analyze")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == "create":
            return cmd_create(args)
        elif args.command == "extract":
            return cmd_extract(args)
        elif args.command == "inspect":
            return cmd_inspect(args)
        elif args.command == "verify":
            return cmd_verify(args)
        elif args.command == "analyze":
            return cmd_analyze(args)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
