"""File magic signatures and known media type detection."""

from typing import Optional, Dict

# Known magic byte prefixes
SIGNATURES: Dict[bytes, str] = {
    b"\x89PNG\r\n\x1a\n": "png",
    b"\xff\xd8\xff": "jpeg",
    b"GIF87a": "gif",
    b"GIF89a": "gif",
    b"PK\x03\x04": "zip",
    b"PK\x05\x06": "zip",
    b"\x1f\x8b\x08": "gzip",
    b"7z\xbc\xaf\x27\x1c": "7z",
    b"BZh": "bzip2",
    b"\xfd7zXZ\x00": "xz",
    b"%PDF": "pdf",
    b"\x1aE\xdf\xa3": "mkv",
    b"ID3": "mp3",
    b"\xff\xfb": "mp3",
    b"\xff\xf3": "mp3",
    b"OggS": "ogg",
    b"RIFF": "riff_media",   # WAV / WebP / AVI
    b"GODZIP\x01\x00": "godzip",
}

PRECOMPRESSED_TYPES = {
    "png", "jpeg", "gif", "zip", "gzip", "7z", "bzip2", "xz", "mkv", "mp3", "ogg"
}

def detect_signature(data: bytes) -> Optional[str]:
    """Detects magic file signature from the first bytes of data."""
    if not data:
        return None
    for magic, fmt in SIGNATURES.items():
        if data.startswith(magic):
            return fmt
    # Special check for MP4 ftyp box
    if len(data) >= 8 and data[4:8] == b"ftyp":
        return "mp4"
    return None

def is_likely_precompressed(data: bytes) -> bool:
    """Returns True if the file matches known pre-compressed container signatures."""
    sig = detect_signature(data)
    return sig in PRECOMPRESSED_TYPES
