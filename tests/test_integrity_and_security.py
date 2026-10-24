"""Security and integrity tests for path traversal, zip slip, and archive corruption."""

import os
import pytest
from godzip.integrity.path_guard import sanitize_archive_path, resolve_safe_extract_path
from godzip.integrity.verifier import IntegrityVerifier, SafeFileWriter
from godzip.common.exceptions import UnsafePathError, ChecksumMismatchError, CorruptArchiveError
from godzip.archive.writer import ArchiveWriter
from godzip.archive.reader import ArchiveReader


def test_path_sanitization_valid():
    assert sanitize_archive_path("foo/bar.txt") == "foo/bar.txt"
    assert sanitize_archive_path("foo\\bar.txt") == "foo/bar.txt"
    assert sanitize_archive_path("./docs/report.pdf") == "docs/report.pdf"


@pytest.mark.parametrize("malicious_path", [
    "../secret.txt",
    "foo/../../secret.txt",
    "/etc/shadow",
    "\\windows\\system32\\cmd.exe",
    "C:\\autoexec.bat",
    "D:/data.db",
    "\\\\attacker.server\\share\\malware.exe",
    "file.txt::$DATA",
    "file.txt:stream",
    "null\x00byte.txt",
])
def test_path_traversal_blocked(malicious_path):
    with pytest.raises(UnsafePathError):
        sanitize_archive_path(malicious_path)


def test_safe_extract_path_enclosure(temp_dir):
    dest = os.path.join(temp_dir, "dest")
    os.makedirs(dest, exist_ok=True)
    resolved = resolve_safe_extract_path(dest, "sub/file.txt")
    assert resolved.startswith(os.path.abspath(dest))


def test_corrupt_archive_detection(temp_dir):
    corrupt_file = os.path.join(temp_dir, "corrupt.god")
    with open(corrupt_file, "wb") as fp:
        fp.write(b"NOT_A_VALID_ARCHIVE_HEADER_TEST")
    
    with pytest.raises(CorruptArchiveError):
        ArchiveReader(corrupt_file)


def test_tampered_archive_digest_mismatch(temp_dir):
    src_file = os.path.join(temp_dir, "test.txt")
    with open(src_file, "wb") as fp:
        fp.write(b"Genuine uncorrupted content for tamper test")

    god_file = os.path.join(temp_dir, "test.god")
    writer = ArchiveWriter(output_path=god_file)
    writer.add_sources([src_file])

    # Tamper with archive bytes in the middle (payload block)
    with open(god_file, "r+b") as fp:
        fp.seek(40) # Into block payload
        b = fp.read(1)
        fp.seek(40)
        fp.write(bytes([(b[0] ^ 0xFF)])) # Flip bits

    reader = ArchiveReader(god_file)
    with pytest.raises((ChecksumMismatchError, CorruptArchiveError)):
        reader.verify()
