"""Tests for Windows shell context menu integration."""

import sys
import pytest
from godzip.platform import windows_shell


@pytest.mark.skipif(sys.platform != "win32", reason="Windows only test")
def test_windows_shell_registration_cycle():
    # Test registration
    ok, msg = windows_shell.register_shell_integration()
    assert ok is True
    assert windows_shell.is_registered() is True

    # Test unregistration
    ok, msg = windows_shell.unregister_shell_integration()
    assert ok is True
    assert windows_shell.is_registered() is False
