"""Pytest fixtures for GODZIP test suite."""

import os
import shutil
import tempfile
import pytest

@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp(prefix="godzip_test_")
    yield d
    shutil.rmtree(d, ignore_errors=True)

@pytest.fixture
def sample_text_data():
    return b"The quick brown fox jumps over the lazy dog. " * 1000

@pytest.fixture
def sample_binary_data():
    return bytes(range(256)) * 64

@pytest.fixture
def sample_repetitive_data():
    return b"\x00" * 50000 + b"ABCDEF" * 2000
