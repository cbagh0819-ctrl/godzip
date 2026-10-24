"""About and Diagnostics: system info, installed codec engines, licenses."""

import sys
import platform
import psutil
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QTextEdit
)
from ...codecs.registry import CodecRegistry


class AboutView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        header = QLabel("About & Diagnostics")
        header.setProperty("class", "section_header")
        layout.addWidget(header)

        # Overview Card
        card = QFrame()
        card.setProperty("class", "card")
        c_layout = QVBoxLayout(card)

        title = QLabel("GODZIP v1.0.0 (Production Release)")
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #ffffff;")
        c_layout.addWidget(title)

        desc = QLabel("Next-Generation Intelligent Lossless Compression Platform for Windows x64.")
        desc.setStyleSheet("color: #8e93a6; font-size: 13px; margin-bottom: 12px;")
        c_layout.addWidget(desc)

        # Hardware & OS Diagnostics
        mem = psutil.virtual_memory()
        info_lines = [
            f"<b>Platform:</b> {platform.platform()} ({platform.machine()})",
            f"<b>Python Runtime:</b> {sys.version.split()[0]} (64-bit)",
            f"<b>Logical CPUs:</b> {psutil.cpu_count(logical=True)} | <b>Physical Cores:</b> {psutil.cpu_count(logical=False)}",
            f"<b>Total System RAM:</b> {mem.total / (1024**3):.1f} GB ({mem.percent}% in use)",
            f"<b>Supported Container:</b> .god Format Specification v1.0 with BLAKE3 Digests",
        ]
        info_lbl = QLabel("<br>".join(info_lines))
        info_lbl.setStyleSheet("color: #c5c9d6; line-height: 1.6;")
        c_layout.addWidget(info_lbl)
        layout.addWidget(card)

        # Installed Codecs Card
        codecs_card = QFrame()
        codecs_card.setProperty("class", "card")
        cd_layout = QVBoxLayout(codecs_card)

        cd_title = QLabel("Installed Compression Backends")
        cd_title.setProperty("class", "card_title")
        cd_layout.addWidget(cd_title)

        active_codecs = CodecRegistry.all_codecs()
        codec_strs = [f"• <b>{c.name}</b> (ID: 0x{c.codec_id:02x}) — Operational" for c in active_codecs.values()]
        codec_lbl = QLabel("<br>".join(codec_strs))
        codec_lbl.setStyleSheet("color: #4ade80; line-height: 1.5;")
        cd_layout.addWidget(codec_lbl)
        layout.addWidget(codecs_card)

        # Legal Notices
        lic_card = QFrame()
        lic_card.setProperty("class", "card")
        lic_layout = QVBoxLayout(lic_card)
        lic_title = QLabel("Open Source Notices & Attribution")
        lic_title.setProperty("class", "card_title")
        lic_layout.addWidget(lic_title)

        lic_text = (
            "GODZIP is open-source software under the MIT License.\n"
            "Includes Zstandard (BSD/GPLv2), Brotli (MIT), LZMA2 (LGPL), LZ4 (BSD), "
            "BLAKE3 (Apache 2.0/CC0), and PySide6 / Qt 6 (LGPLv3).\n"
            "Honest scientific benchmarking: never claims compression ratios without reproducible empirical evidence."
        )
        lic_lbl = QLabel(lic_text)
        lic_lbl.setStyleSheet("color: #7b8094; font-size: 11px;")
        lic_layout.addWidget(lic_lbl)
        layout.addWidget(lic_card)

        layout.addStretch()
