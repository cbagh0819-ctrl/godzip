"""Windows Shell Context Menu & File Association Integration for GODZIP.

Author: Chandan Bagh (baghchandan53@gmail.com, GitHub: @cbagh0819-ctrl)
"""

import sys
import os
from typing import Tuple, Optional

if sys.platform == "win32":
    import winreg
else:
    winreg = None


SHELL_ROOT = r"Software\Classes"
APP_PROGID = "GODZIP.Archive"
FILE_EXT = ".god"


def _get_python_paths() -> Tuple[str, str]:
    """Return paths to python.exe (console) and pythonw.exe (windowed)."""
    python_exe = sys.executable
    bindir = os.path.dirname(python_exe)
    pythonw_exe = os.path.join(bindir, "pythonw.exe")
    if not os.path.isfile(pythonw_exe):
        pythonw_exe = python_exe
    return python_exe, pythonw_exe


def _set_reg_value(root_key, subkey_path: str, value_name: Optional[str], value_str: str) -> None:
    """Helper to create/open a registry key and set a string value."""
    with winreg.CreateKey(root_key, subkey_path) as key:
        winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, value_str)


def _delete_reg_tree(root_key, subkey_path: str) -> None:
    """Recursively delete a registry key and all its subkeys."""
    try:
        with winreg.OpenKey(root_key, subkey_path, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
            while True:
                try:
                    sub = winreg.EnumKey(key, 0)
                    _delete_reg_tree(root_key, f"{subkey_path}\\{sub}")
                except OSError:
                    break
        winreg.DeleteKey(root_key, subkey_path)
    except FileNotFoundError:
        pass
    except OSError:
        pass


def is_registered() -> bool:
    """Check whether GODZIP context menu integration is active in HKCU."""
    if not winreg:
        return False
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, f"{SHELL_ROOT}\\*\\shell\\GODZIP.Compress"):
            return True
    except FileNotFoundError:
        return False


def register_shell_integration(custom_exe: Optional[str] = None) -> Tuple[bool, str]:
    """Register right-click Explorer context menu and .god file associations in HKCU."""
    if not winreg:
        return False, "Context menu integration is only supported on Windows."

    try:
        python_exe, pythonw_exe = _get_python_paths()
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

        if custom_exe and os.path.isfile(custom_exe):
            cmd_compress = f'"{custom_exe}" create -i "%1" -o "%1.god"'
            cmd_open = f'"{custom_exe}" "%1"'
            cmd_extract = f'"{custom_exe}" extract -a "%1" -o "%1_extracted"'
            cmd_extract_here = f'"{custom_exe}" extract -a "%1" -o "."'
            cmd_verify = f'"{custom_exe}" verify -a "%1"'
            icon_path = f'"{custom_exe}",0'
        else:
            # Running via Python module in repository
            cmd_compress = f'"{python_exe}" -m godzip.cli create -i "%1" -o "%1.god"'
            cmd_open = f'"{pythonw_exe}" -m godzip.ui.app "%1"'
            cmd_extract = f'"{python_exe}" -m godzip.cli extract -a "%1" -o "%1_extracted"'
            cmd_extract_here = f'"{python_exe}" -m godzip.cli extract -a "%1" -o "."'
            cmd_verify = f'"{python_exe}" -m godzip.cli verify -a "%1"'
            icon_path = f'"{python_exe}",0'

        # 1. Right click on any file -> Compress with GODZIP
        _set_reg_value(winreg.HKEY_CURRENT_USER, f"{SHELL_ROOT}\\*\\shell\\GODZIP.Compress", None, "Compress with GODZIP")
        _set_reg_value(winreg.HKEY_CURRENT_USER, f"{SHELL_ROOT}\\*\\shell\\GODZIP.Compress", "Icon", icon_path)
        _set_reg_value(winreg.HKEY_CURRENT_USER, f"{SHELL_ROOT}\\*\\shell\\GODZIP.Compress\\command", None, cmd_compress)

        # 2. Right click on any directory -> Compress with GODZIP
        _set_reg_value(winreg.HKEY_CURRENT_USER, f"{SHELL_ROOT}\\Directory\\shell\\GODZIP.Compress", None, "Compress with GODZIP")
        _set_reg_value(winreg.HKEY_CURRENT_USER, f"{SHELL_ROOT}\\Directory\\shell\\GODZIP.Compress", "Icon", icon_path)
        _set_reg_value(winreg.HKEY_CURRENT_USER, f"{SHELL_ROOT}\\Directory\\shell\\GODZIP.Compress\\command", None, cmd_compress)

        # 3. Associate .god extension with GODZIP.Archive
        _set_reg_value(winreg.HKEY_CURRENT_USER, f"{SHELL_ROOT}\\{FILE_EXT}", None, APP_PROGID)
        _set_reg_value(winreg.HKEY_CURRENT_USER, f"{SHELL_ROOT}\\{FILE_EXT}", "Content Type", "application/x-godzip")

        # 4. Define GODZIP.Archive ProgID and context actions
        _set_reg_value(winreg.HKEY_CURRENT_USER, f"{SHELL_ROOT}\\{APP_PROGID}", None, "GODZIP Compressed Archive")
        _set_reg_value(winreg.HKEY_CURRENT_USER, f"{SHELL_ROOT}\\{APP_PROGID}\\DefaultIcon", None, icon_path)

        # Open in GODZIP Desktop GUI
        _set_reg_value(winreg.HKEY_CURRENT_USER, f"{SHELL_ROOT}\\{APP_PROGID}\\shell\\open", None, "Open in GODZIP")
        _set_reg_value(winreg.HKEY_CURRENT_USER, f"{SHELL_ROOT}\\{APP_PROGID}\\shell\\open\\command", None, cmd_open)

        # Extract to folder
        _set_reg_value(winreg.HKEY_CURRENT_USER, f"{SHELL_ROOT}\\{APP_PROGID}\\shell\\extract", None, "Extract to folder")
        _set_reg_value(winreg.HKEY_CURRENT_USER, f"{SHELL_ROOT}\\{APP_PROGID}\\shell\\extract\\command", None, cmd_extract)

        # Extract Here
        _set_reg_value(winreg.HKEY_CURRENT_USER, f"{SHELL_ROOT}\\{APP_PROGID}\\shell\\extract_here", None, "Extract Here")
        _set_reg_value(winreg.HKEY_CURRENT_USER, f"{SHELL_ROOT}\\{APP_PROGID}\\shell\\extract_here\\command", None, cmd_extract_here)

        # Verify
        _set_reg_value(winreg.HKEY_CURRENT_USER, f"{SHELL_ROOT}\\{APP_PROGID}\\shell\\verify", None, "Verify Archive Integrity")
        _set_reg_value(winreg.HKEY_CURRENT_USER, f"{SHELL_ROOT}\\{APP_PROGID}\\shell\\verify\\command", None, cmd_verify)

        # Notify Windows Shell of association change
        try:
            import ctypes
            ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)  # SHCNE_ASSOCCHANGED
        except Exception:
            pass

        return True, "GODZIP Explorer context menu and .god file associations registered successfully."

    except Exception as e:
        return False, f"Failed to register context menu: {e}"


def unregister_shell_integration() -> Tuple[bool, str]:
    """Remove GODZIP context menus and associations from HKCU."""
    if not winreg:
        return False, "Context menu integration is only supported on Windows."

    try:
        _delete_reg_tree(winreg.HKEY_CURRENT_USER, f"{SHELL_ROOT}\\*\\shell\\GODZIP.Compress")
        _delete_reg_tree(winreg.HKEY_CURRENT_USER, f"{SHELL_ROOT}\\Directory\\shell\\GODZIP.Compress")
        _delete_reg_tree(winreg.HKEY_CURRENT_USER, f"{SHELL_ROOT}\\{FILE_EXT}")
        _delete_reg_tree(winreg.HKEY_CURRENT_USER, f"{SHELL_ROOT}\\{APP_PROGID}")

        try:
            import ctypes
            ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)
        except Exception:
            pass

        return True, "GODZIP Explorer context menu and .god file associations removed successfully."
    except Exception as e:
        return False, f"Failed to unregister context menu: {e}"
