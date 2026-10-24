"""Tests for ContentAnalyzer entropy and magic detection."""

import os
from godzip.analyzer.analyzer import ContentAnalyzer


def test_analyzer_text():
    data = b"Hello world! This is a typical English text paragraph repeating for analysis.\n" * 100
    profile = ContentAnalyzer.analyze(data)
    assert profile.recommended_class == "TEXT"
    assert profile.ascii_ratio > 0.9
    assert 3.0 < profile.shannon_entropy < 5.0


def test_analyzer_repetitive():
    data = b"\x00" * 10000
    profile = ContentAnalyzer.analyze(data)
    assert profile.recommended_class == "REPETITIVE"
    assert profile.shannon_entropy == 0.0
    assert profile.zero_ratio == 1.0


def test_analyzer_precompressed_magic():
    png_header = b"\x89PNG\r\n\x1a\n" + os.urandom(200)
    profile = ContentAnalyzer.analyze(png_header)
    assert profile.detected_format == "png"
    assert profile.likely_precompressed is True
    assert profile.recommended_class == "PRECOMPRESSED"
