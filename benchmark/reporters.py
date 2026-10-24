"""Benchmark report generators exporting JSON, CSV, and Markdown summaries."""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any


def export_json(results: List[Dict[str, Any]], filepath: str) -> None:
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)


def export_csv(results: List[Dict[str, Any]], filepath: str) -> None:
    if not results:
        return
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(results[0].keys())
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def export_markdown(results: List[Dict[str, Any]], filepath: str) -> str:
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# GODZIP Benchmark Report",
        "",
        "| Category | Compressor | Mode / Level | Orig (bytes) | Arch (bytes) | Ratio | Red % | Comp (s) | Comp (MB/s) | Decomp (s) | Verified |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {r['category']} | {r['compressor']} | {r['mode']} | {r['original_bytes']:,} | {r['archive_bytes']:,} | {r['compression_ratio']:.2f}x | {r['reduction_pct']:.1f}% | {r['comp_time_sec']:.3f} | {r['comp_mbps']:.1f} | {r['decomp_time_sec']:.3f} | {r['verified']} |"
        )
    lines.append("")
    md_content = "\n".join(lines)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md_content)
    return md_content
