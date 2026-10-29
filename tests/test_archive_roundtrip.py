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


def test_encrypted_archive_lifecycle(temp_dir):
    """Verifies AES-256-GCM encryption, wrong password rejection, and exact decrypted restoration."""
    from godzip.common.exceptions import ArchiveEncryptedError, InvalidPasswordError

    secret_file = os.path.join(temp_dir, "confidential.txt")
    secret_data = b"TOP SECRET: Encrypted archive test payload with confidential data.\n" * 200
    with open(secret_file, "wb") as f:
        f.write(secret_data)

    enc_archive = os.path.join(temp_dir, "protected.god")
    password = "MasterPassword2026!"

    # Create encrypted archive
    writer = ArchiveWriter(output_path=enc_archive, password=password)
    writer.add_sources([secret_file])

    # 1. Inspect without password (metadata visible, flag marked)
    reader_no_pass = ArchiveReader(enc_archive)
    info = reader_no_pass.inspect()
    assert info["is_encrypted"] is True

    # 2. Extract without password must fail
    with pytest.raises(ArchiveEncryptedError):
        reader_no_pass.extract(os.path.join(temp_dir, "fail_dest"))

    # 3. Extract with WRONG password must fail
    with pytest.raises(InvalidPasswordError):
        reader_wrong = ArchiveReader(enc_archive, password="WrongPassword123")
        reader_wrong.extract(os.path.join(temp_dir, "fail_dest"))

    # 4. Extract with CORRECT password must succeed and restore 100% byte-exact
    dest_dir = os.path.join(temp_dir, "success_dest")
    reader_correct = ArchiveReader(enc_archive, password=password)
    assert reader_correct.verify() is True
    reader_correct.extract(dest_dir)

    recovered = os.path.join(dest_dir, "confidential.txt")
    assert os.path.exists(recovered)
    with open(recovered, "rb") as rf:
        assert rf.read() == secret_data


def test_multivolume_archive_splitting_lifecycle(temp_dir):
    """Verifies multi-volume archive splitting, part discovery, and byte-exact extraction."""
    large_file = os.path.join(temp_dir, "bigdata.bin")
    # 100 KB random payload to test splitting across multiple volumes
    payload = os.urandom(100 * 1024)
    with open(large_file, "wb") as f:
        f.write(payload)

    archive_base = os.path.join(temp_dir, "dataset.god")
    split_size = 35 * 1024  # 35 KB per volume

    writer = ArchiveWriter(
        output_path=archive_base,
        mode=CompressionMode.FAST,
        split_size=split_size
    )
    writer.add_sources([large_file])

    # Check part files exist
    part1 = os.path.join(temp_dir, "dataset.part01.god")
    part2 = os.path.join(temp_dir, "dataset.part02.god")
    part3 = os.path.join(temp_dir, "dataset.part03.god")
    assert os.path.exists(part1), "dataset.part01.god was not created"
    assert os.path.exists(part2), "dataset.part02.god was not created"
    assert os.path.exists(part3), "dataset.part03.god was not created"
    assert os.path.getsize(part1) <= split_size

    # 1. Read archive pointing to part01
    reader = ArchiveReader(part1)
    assert len(reader.volume_parts) >= 3
    assert reader.verify() is True

    extract_dir = os.path.join(temp_dir, "extracted_split")
    reader.extract(extract_dir)

    recovered = os.path.join(extract_dir, "bigdata.bin")
    assert os.path.exists(recovered)
    with open(recovered, "rb") as rf:
        assert rf.read() == payload

    # 2. Read archive pointing to base name (auto-discovers part01, part02...)
    reader_base = ArchiveReader(archive_base)
    assert len(reader_base.volume_parts) >= 3
    assert reader_base.verify() is True


def test_sfx_executable_generation(temp_dir):
    """Verifies that a valid .god archive can be packaged into an SFX executable."""
    from godzip.archive.sfx import create_sfx_executable
    sample_file = os.path.join(temp_dir, "document.txt")
    with open(sample_file, "wb") as f:
        f.write(b"GODZIP Standalone SFX Executable Test Payload - Chandan Bagh\n" * 50)

    god_path = os.path.join(temp_dir, "document.god")
    writer = ArchiveWriter(output_path=god_path)
    writer.add_sources([sample_file])
    assert os.path.exists(god_path)

    sfx_exe = os.path.join(temp_dir, "document_extractor.exe")
    ok, msg = create_sfx_executable(god_path, sfx_exe)
    assert ok is True
    assert os.path.exists(sfx_exe)
    assert os.path.getsize(sfx_exe) > os.path.getsize(god_path)

    # Verify that the embedded GODZIP container magic exists inside the generated .exe
    with open(sfx_exe, "rb") as ef:
        exe_bytes = ef.read()
    assert b"GODZIP\x01\x00" in exe_bytes
    assert b"GEND" in exe_bytes
