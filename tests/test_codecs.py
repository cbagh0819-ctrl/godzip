"""Tests verifying every lossless codec guarantees exact byte restoration."""

import pytest
from godzip.codecs.registry import CodecRegistry
from godzip.common.constants import (
    CODEC_ID_STORE,
    CODEC_ID_ZSTD,
    CODEC_ID_LZMA2,
    CODEC_ID_BROTLI,
    CODEC_ID_DEFLATE,
    CODEC_ID_LZ4,
    CODEC_ID_NEURAL_CONTEXT,
)


@pytest.mark.parametrize("codec_id", [
    CODEC_ID_STORE,
    CODEC_ID_ZSTD,
    CODEC_ID_LZMA2,
    CODEC_ID_BROTLI,
    CODEC_ID_DEFLATE,
    CODEC_ID_LZ4,
    CODEC_ID_NEURAL_CONTEXT,
])
def test_codec_roundtrip_text(codec_id, sample_text_data):
    codec = CodecRegistry.get(codec_id)
    compressed = codec.compress(sample_text_data)
    decompressed = codec.decompress(compressed, len(sample_text_data))
    assert decompressed == sample_text_data, f"Codec {codec.name} failed byte-exact text roundtrip"


@pytest.mark.parametrize("codec_id", [
    CODEC_ID_STORE,
    CODEC_ID_ZSTD,
    CODEC_ID_LZMA2,
    CODEC_ID_BROTLI,
    CODEC_ID_DEFLATE,
    CODEC_ID_LZ4,
    CODEC_ID_NEURAL_CONTEXT,
])
def test_codec_roundtrip_binary(codec_id, sample_binary_data):
    codec = CodecRegistry.get(codec_id)
    compressed = codec.compress(sample_binary_data)
    decompressed = codec.decompress(compressed, len(sample_binary_data))
    assert decompressed == sample_binary_data, f"Codec {codec.name} failed byte-exact binary roundtrip"


def test_empty_buffer():
    for cid in [CODEC_ID_STORE, CODEC_ID_ZSTD, CODEC_ID_LZMA2, CODEC_ID_BROTLI, CODEC_ID_DEFLATE, CODEC_ID_LZ4]:
        codec = CodecRegistry.get(cid)
        comp = codec.compress(b"")
        decomp = codec.decompress(comp, 0)
        assert decomp == b""
