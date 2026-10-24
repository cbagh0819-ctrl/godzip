"""Tests for ContentAnalyzer entropy and media detection across image, video, audio, and documents."""

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


def test_analyzer_image_detection():
    png_header = b"\x89PNG\r\n\x1a\n" + os.urandom(200)
    profile = ContentAnalyzer.analyze(png_header)
    assert profile.detected_format == "png"
    assert profile.detected_category == "image"
    assert profile.recommended_class == "IMAGE"


def test_analyzer_audio_detection():
    wav_header = b"RIFF\x24\x00\x00\x00WAVEfmt " + os.urandom(100)
    profile = ContentAnalyzer.analyze(wav_header)
    assert profile.detected_format == "wav"
    assert profile.detected_category == "audio"
    assert profile.recommended_class == "AUDIO"


def test_analyzer_video_detection():
    mp4_header = b"\x00\x00\x00\x18ftypisom" + os.urandom(100)
    profile = ContentAnalyzer.analyze(mp4_header)
    assert profile.detected_format == "mp4"
    assert profile.detected_category == "video"
    assert profile.recommended_class == "VIDEO"
