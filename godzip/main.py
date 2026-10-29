"""Unified main entry point for GODZIP standalone application (GUI & CLI).

Author: Chandan Bagh (baghchandan53@gmail.com, GitHub: @cbagh0819-ctrl)
"""

import sys
import os

CLI_COMMANDS = {"create", "compress", "extract", "inspect", "verify", "analyze", "shell", "sfx", "-h", "--help", "-v", "--version"}


def main():
    # If explicit CLI command is provided
    if len(sys.argv) > 1 and sys.argv[1].lower() in CLI_COMMANDS:
        from godzip.cli import main as cli_main
        sys.exit(cli_main())

    # Otherwise launch full PySide6 Desktop Application
    from godzip.ui.app import main as ui_main
    ui_main()


if __name__ == "__main__":
    main()
