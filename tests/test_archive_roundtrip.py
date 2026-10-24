"""End-to-end roundtrip compression, extraction, and verification tests."""

import os
import pytest
from godzip.common.constants import CompressionMode
from godzip.archive.writer import ArchiveWriter
from godzip.archive.reader import ArchiveReader


@pytest.mark.parametrize("mode", [
    CompressionMode.FAST,
    CompressionMode.BALANCED,
    CompressionMode.MAXIMUM,
    CompressionMode.RESEARCH,
])
def test_full_roundtrip_modes(temp_dir, mode):
    # Setup test directory tree
    src_dir = os.path.join(temp_dir, "src")
    os.makedirs(os.path.join(src_dir, "subdir"), exist_ok=True)

    file_a = os.path.join(src_dir, "file_a.txt")
    with open(file_a, "wb") as fp:
        fp.write(b"Text data for compression roundtrip testing.\n" * 500)

    file_b = os.path.join(src_dir, "subdir", "file_b.bin")
    with open(file_b, "wb") as fp:
        fp.write(bytes(range(256)) * 100)

    archive_path = os.path.join(temp_dir, f"test_{mode.value}.god")
    writer = ArchiveWriter(output_path=archive_path, mode=mode, enable_dedup=True)
    orig_bytes, comp_bytes = writer.add_sources([src_dir])

    assert os.path.exists(archive_path)
    assert comp_bytes > 0
    assert orig_bytes > 0

    # Verify without extracting
    reader = ArchiveReader(archive_path)
    assert reader.verify() is True

    # Extract to target directory
    extract_dir = os.path.join(temp_dir, f"extracted_{mode.value}")
    extracted_bytes = reader.extract(destination_dir=extract_dir)
    assert extracted_bytes == orig_bytes

    # Byte-for-byte comparison
    recovered_a = os.path.join(extract_dir, "src", "file_a.txt")
    recovered_b = os.path.join(extract_dir, "src", "subdir", "file_b.bin")

    assert os.path.exists(recovered_a)
    assert os.path.exists(recovered_b)

    with open(file_a, "rb") as orig_fp, open(recovered_a, "rb") as rec_fp:
        assert orig_fp.read() == rec_fp.read()

    with open(file_b, "rb") as orig_fp, open(recovered_b, "rb") as rec_fp:
        assert orig_fp.read() == rec_fp.read()


def test_deduplication_efficiency(temp_dir):
    src_dir = os.path.join(temp_dir, "dedup_src")
    os.makedirs(src_dir, exist_ok=True)

    block = b"Identical repeated chunk " * 10000 # ~250 KB
    for i in range(5):
        with open(os.path.join(src_dir, f"copy_{i}.txt"), "wb") as fp:
            fp.write(block)

    # 1. Archive WITH deduplication
    with_dedup = os.path.join(temp_dir, "with_dedup.god")
    writer_dedup = ArchiveWriter(output_path=with_dedup, enable_dedup=True)
    orig_dedup, comp_dedup = writer_dedup.add_sources([src_dir])

    # 2. Archive WITHOUT deduplication
    without_dedup = os.path.join(temp_dir, "without_dedup.god")
    writer_nodedup = ArchiveWriter(output_path=without_dedup, enable_dedup=False)
    orig_nodedup, comp_nodedup = writer_nodedup.add_sources([src_dir])

    reader_dedup = ArchiveReader(with_dedup)
    reader_nodedup = ArchiveReader(without_dedup)

    # With dedup, exactly 1 payload block is stored for all 5 files
    assert len(reader_dedup.blocks) == 1
    assert len(reader_nodedup.blocks) == 5
    assert comp_dedup < comp_nodedup

    # Verify extraction restores all 5 files exactly
    ext_dir = os.path.join(temp_dir, "ext_dedup")
    reader_dedup.extract(ext_dir)
    for i in range(5):
        ext_file = os.path.join(ext_dir, "dedup_src", f"copy_{i}.txt")
        assert os.path.exists(ext_file)
        with open(ext_file, "rb") as fp:
            assert fp.read() == block


def test_mixed_media_folder_compression(temp_dir):
    """Verifies that a folder with images, audio, video, and documents in any format all get compressed."""
    media_dir = os.path.join(temp_dir, "mixed_media")
    os.makedirs(media_dir, exist_ok=True)

    # 1. Image: Uncompressed BMP
    bmp_path = os.path.join(media_dir, "photo.bmp")
    with open(bmp_path, "wb") as f:
        f.write(b"BM" + b"\x00" * 52 + (bytes(range(128)) * 100))

    # 2. Image: PNG
    png_path = os.path.join(media_dir, "icon.png")
    with open(png_path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + b"IDAT" + (b"\x12\x34\x56\x78" * 500))

    # 3. Audio: WAV PCM
    wav_path = os.path.join(media_dir, "sound.wav")
    with open(wav_path, "wb") as f:
        f.write(b"RIFF\x24\x00\x00\x00WAVEfmt " + (b"\x00\x01\x00\x02" * 500))

    # 4. Audio: MP3
    mp3_path = os.path.join(media_dir, "music.mp3")
    with open(mp3_path, "wb") as f:
        f.write(b"ID3\x03\x00\x00\x00" + (b"\xff\xfb\x90\x44" * 400))

    # 5. Video: MP4 container
    mp4_path = os.path.join(media_dir, "clip.mp4")
    with open(mp4_path, "wb") as f:
        f.write(b"\x00\x00\x00\x18ftypmp42" + (b"mdat\xaa\xbb\xcc\xdd" * 300))

    # 6. Document: PDF
    pdf_path = os.path.join(media_dir, "manual.pdf")
    with open(pdf_path, "wb") as f:
        f.write(b"%PDF-1.4\n" + (b"1 0 obj << /Type /Catalog >> endobj\n" * 100))

    # Compress the mixed media folder
    archive_path = os.path.join(temp_dir, "mixed_media.god")
    writer = ArchiveWriter(output_path=archive_path, mode=CompressionMode.MAXIMUM, enable_dedup=True)
    orig_bytes, comp_bytes = writer.add_sources([media_dir])

    assert comp_bytes > 0
    assert orig_bytes > 0
    # High compression achieved across the mixed folder
    assert comp_bytes < orig_bytes

    # Verify and extract
    reader = ArchiveReader(archive_path)
    assert reader.verify() is True
    assert len(reader.files) == 6

    extract_dir = os.path.join(temp_dir, "ext_mixed")
    reader.extract(destination_dir=extract_dir)

    # Check byte-for-byte exact recovery for every single media file
    for fname in ["photo.bmp", "icon.png", "sound.wav", "music.mp3", "clip.mp4", "manual.pdf"]:
        orig_f = os.path.join(media_dir, fname)
        rec_f = os.path.join(extract_dir, "mixed_media", fname)
        assert os.path.exists(rec_f), f"Recovered file missing: {fname}"
        with open(orig_f, "rb") as of, open(rec_f, "rb") as rf:
            assert of.read() == rf.read(), f"Byte mismatch for {fname}"
