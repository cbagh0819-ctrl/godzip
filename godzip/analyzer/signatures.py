"""Comprehensive file signature detection for images, video, audio, and all file formats."""

from typing import Optional, Dict, Tuple

# Categories
CATEGORY_IMAGE = "image"
CATEGORY_VIDEO = "video"
CATEGORY_AUDIO = "audio"
CATEGORY_DOCUMENT = "document"
CATEGORY_ARCHIVE = "archive"
CATEGORY_EXECUTABLE = "executable"
CATEGORY_DATA = "data"
CATEGORY_UNKNOWN = "unknown"

# Comprehensive magic byte signatures
SIGNATURES: Dict[bytes, Tuple[str, str]] = {
    # Images
    b"\x89PNG\r\n\x1a\n": ("png", CATEGORY_IMAGE),
    b"\xff\xd8\xff": ("jpeg", CATEGORY_IMAGE),
    b"GIF87a": ("gif", CATEGORY_IMAGE),
    b"GIF89a": ("gif", CATEGORY_IMAGE),
    b"BM": ("bmp", CATEGORY_IMAGE),
    b"II*\x00": ("tiff_le", CATEGORY_IMAGE),
    b"MM\x00*": ("tiff_be", CATEGORY_IMAGE),
    b"\x00\x00\x01\x00": ("ico", CATEGORY_IMAGE),
    b"8BPS": ("psd", CATEGORY_IMAGE),

    # Audio
    b"ID3": ("mp3", CATEGORY_AUDIO),
    b"\xff\xfb": ("mp3", CATEGORY_AUDIO),
    b"\xff\xf3": ("mp3", CATEGORY_AUDIO),
    b"\xff\xf2": ("mp3", CATEGORY_AUDIO),
    b"fLaC": ("flac", CATEGORY_AUDIO),
    b"OggS": ("ogg", CATEGORY_AUDIO),
    b"MThd": ("midi", CATEGORY_AUDIO),

    # Video & Media Containers
    b"\x1aE\xdf\xa3": ("mkv_webm", CATEGORY_VIDEO),
    b"FLV\x01": ("flv", CATEGORY_VIDEO),
    b"\x00\x00\x01\xba": ("mpeg_ps", CATEGORY_VIDEO),
    b"\x00\x00\x01\xb3": ("mpeg_video", CATEGORY_VIDEO),
    b"0&\xb2u\x8ef\xcf\x11": ("wmv_asf", CATEGORY_VIDEO),

    # Archives & Compressed formats
    b"PK\x03\x04": ("zip", CATEGORY_ARCHIVE),
    b"PK\x05\x06": ("zip_empty", CATEGORY_ARCHIVE),
    b"\x1f\x8b\x08": ("gzip", CATEGORY_ARCHIVE),
    b"7z\xbc\xaf\x27\x1c": ("7z", CATEGORY_ARCHIVE),
    b"BZh": ("bzip2", CATEGORY_ARCHIVE),
    b"\xfd7zXZ\x00": ("xz", CATEGORY_ARCHIVE),
    b"Rar!\x1a\x07": ("rar", CATEGORY_ARCHIVE),
    b"(\xb5/\xfd": ("zstandard", CATEGORY_ARCHIVE),
    b"\x04\"M\x18": ("lz4_frame", CATEGORY_ARCHIVE),
    b"MSCF": ("cab", CATEGORY_ARCHIVE),
    b"GODZIP\x01\x00": ("godzip", CATEGORY_ARCHIVE),

    # Documents & Executables
    b"%PDF": ("pdf", CATEGORY_DOCUMENT),
    b"{\\rtf": ("rtf", CATEGORY_DOCUMENT),
    b"MZ": ("pe_executable", CATEGORY_EXECUTABLE),
    b"\x7fELF": ("elf_executable", CATEGORY_EXECUTABLE),
    b"\x00asm": ("wasm", CATEGORY_EXECUTABLE),
}


def detect_file_format(data: bytes) -> Tuple[str, str]:
    """Detects file format and category (image, video, audio, archive, etc.).
    
    Returns:
        (format_name, category)
    """
    if not data:
        return "empty", CATEGORY_DATA

    # Check direct magic table
    for magic, (fmt, cat) in SIGNATURES.items():
        if data.startswith(magic):
            return fmt, cat

    # RIFF container sub-types: WAV, WebP, AVI
    if len(data) >= 12 and data.startswith(b"RIFF"):
        subtype = data[8:12]
        if subtype == b"WEBP":
            return "webp", CATEGORY_IMAGE
        elif subtype == b"WAVE":
            return "wav", CATEGORY_AUDIO
        elif subtype == b"AVI ":
            return "avi", CATEGORY_VIDEO
        return "riff_media", CATEGORY_VIDEO

    # AIFF container
    if len(data) >= 12 and data.startswith(b"FORM") and data[8:12] in (b"AIFF", b"AIFC"):
        return "aiff", CATEGORY_AUDIO

    # MP4 / MOV / M4A / 3GP container (ISO Base Media File Format)
    if len(data) >= 8 and data[4:8] == b"ftyp":
        major_brand = data[8:12] if len(data) >= 12 else b""
        if major_brand in (b"M4A ", b"M4B ", b"M4P "):
            return "m4a", CATEGORY_AUDIO
        return "mp4", CATEGORY_VIDEO

    # SVG text image
    sample_head = data[:512].lower()
    if b"<svg" in sample_head or (b"<?xml" in sample_head and b"<svg" in data[:2048].lower()):
        return "svg", CATEGORY_IMAGE

    return "generic_binary", CATEGORY_UNKNOWN


def detect_signature(data: bytes) -> Optional[str]:
    """Backward-compatible signature detector."""
    fmt, _ = detect_file_format(data)
    return fmt if fmt != "generic_binary" else None


def is_likely_precompressed(data: bytes) -> bool:
    """Returns True if the format is typically already compressed, but compression will still be tested."""
    fmt, cat = detect_file_format(data)
    return cat in (CATEGORY_ARCHIVE, CATEGORY_VIDEO) or fmt in ("jpeg", "png", "webp", "mp3", "ogg")
