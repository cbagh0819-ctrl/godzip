"""Self-Extracting Executable (SFX) Generator for GODZIP (.exe).

Author: Chandan Bagh (baghchandan53@gmail.com, GitHub: @cbagh0819-ctrl)
"""

import os
import sys
import shutil
import subprocess
from typing import Optional, Tuple


ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
DEFAULT_STUB_PATH = os.path.join(ASSETS_DIR, "sfx_stub.exe")
RUNNER_SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), "sfx_runner.py"))


def build_base_sfx_stub(output_stub_path: Optional[str] = None) -> str:
    """Compiles the minimal standalone sfx_runner into sfx_stub.exe using PyInstaller."""
    target_path = output_stub_path or DEFAULT_STUB_PATH
    os.makedirs(os.path.dirname(target_path), exist_ok=True)

    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        "--onefile",
        "--noconsole",
        "--name", "sfx_stub",
        RUNNER_SCRIPT,
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"PyInstaller build failed: {res.stderr}\n{res.stdout}")

    # Move generated executable from dist/sfx_stub.exe to target_path
    dist_stub = os.path.abspath(os.path.join("dist", "sfx_stub.exe"))
    if not os.path.exists(dist_stub):
        raise FileNotFoundError(f"Expected compiled stub at {dist_stub}")

    if os.path.exists(target_path):
        os.remove(target_path)
    shutil.move(dist_stub, target_path)

    # Clean build artifacts
    for d in ["build", "dist"]:
        if os.path.exists(d):
            shutil.rmtree(d, ignore_errors=True)
    for f in ["sfx_stub.spec"]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except OSError:
                pass

    return target_path


def create_sfx_executable(
    archive_path: str,
    output_exe_path: str,
    custom_stub_path: Optional[str] = None
) -> Tuple[bool, str]:
    """Generates a standalone Windows Self-Extracting Executable (.exe) for a .god archive.
    
    Appends the .god archive container payload as an executable overlay to the SFX stub.
    """
    archive_path = os.path.abspath(archive_path)
    output_exe_path = os.path.abspath(output_exe_path)

    if not os.path.exists(archive_path):
        return False, f"Archive not found: {archive_path}"

    stub_path = custom_stub_path or DEFAULT_STUB_PATH

    # If base stub executable doesn't exist yet, compile it now
    if not os.path.exists(stub_path):
        try:
            build_base_sfx_stub(stub_path)
        except Exception as e:
            return False, f"Failed to build SFX stub executable: {e}"

    try:
        # Create final executable: stub + archive overlay
        with open(stub_path, "rb") as stub_fp, open(archive_path, "rb") as god_fp:
            stub_bytes = stub_fp.read()
            archive_bytes = god_fp.read()

        temp_exe = output_exe_path + f".tmp.{os.getpid()}"
        with open(temp_exe, "wb") as out_fp:
            out_fp.write(stub_bytes)
            out_fp.write(archive_bytes)

        if os.path.exists(output_exe_path):
            os.remove(output_exe_path)
        os.replace(temp_exe, output_exe_path)

        total_size = os.path.getsize(output_exe_path)
        return True, f"Self-Extracting archive created: {output_exe_path} ({total_size:,} bytes)"

    except Exception as e:
        return False, f"Error building SFX archive: {e}"
