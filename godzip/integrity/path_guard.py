"""Security path sanitizer to prevent Zip Slip and path traversal attacks."""

import os
import re
from pathlib import Path
from ..common.exceptions import UnsafePathError
from ..common.constants import MAX_PATH_LENGTH

_DRIVE_PATTERN = re.compile(r"^[a-zA-Z]:")
_UNC_PATTERN = re.compile(r"^[\\]{2}")
_ADS_PATTERN = re.compile(r":")


def sanitize_archive_path(raw_path: str) -> str:
    """Validates and normalizes an internal archive relative path.
    
    Raises UnsafePathError if path contains malicious segments or escape patterns.
    """
    if not raw_path or not raw_path.strip():
        raise UnsafePathError("Empty archive path entry")

    if len(raw_path.encode("utf-8")) > MAX_PATH_LENGTH:
        raise UnsafePathError(f"Path exceeds maximum allowed length of {MAX_PATH_LENGTH} bytes")

    if "\0" in raw_path:
        raise UnsafePathError("Path contains null byte")

    # Reject absolute root paths (leading slash or backslash)
    if raw_path.startswith("/") or raw_path.startswith("\\"):
        raise UnsafePathError(f"Absolute path with leading slash rejected: {raw_path}")

    # Reject Windows drive prefix (e.g. C:)
    if _DRIVE_PATTERN.match(raw_path):
        raise UnsafePathError(f"Absolute Windows drive letter path rejected: {raw_path}")

    # Reject UNC network paths
    if _UNC_PATTERN.match(raw_path):
        raise UnsafePathError(f"UNC network path rejected: {raw_path}")

    # Normalize forward and back slashes
    normalized = raw_path.replace("\\", "/").strip("/")

    # Reject Alternate Data Streams (colon in file name)
    if _ADS_PATTERN.search(normalized):
        raise UnsafePathError(f"Alternate Data Stream notation rejected: {raw_path}")

    parts = normalized.split("/")
    clean_parts = []

    for part in parts:
        if part in ("", "."):
            continue
        if part == "..":
            raise UnsafePathError(f"Directory traversal segment '..' detected in path: {raw_path}")
        clean_parts.append(part)

    if not clean_parts:
        raise UnsafePathError(f"Resolved path is empty or root reference: {raw_path}")

    return "/".join(clean_parts)


def resolve_safe_extract_path(destination_dir: str, archive_path: str) -> str:
    """Resolves an archive path under destination_dir, ensuring it cannot escape."""
    clean_rel = sanitize_archive_path(archive_path)
    dest_path = Path(destination_dir).resolve()
    target_path = (dest_path / clean_rel).resolve()

    try:
        # Must be strictly within destination_dir
        target_path.relative_to(dest_path)
    except ValueError:
        raise UnsafePathError(f"Path escapes destination directory: {archive_path}")

    return str(target_path)
