"""Compression workspace: file/folder selection, mode configuration, job start."""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QLineEdit, QFileDialog, QComboBox, QCheckBox, QSpinBox, QListWidget
)
from PySide6.QtCore import Signal
from ...common.constants import CompressionMode


class WorkspaceView(QWidget):
    start_compression = Signal(list, str, object, bool, str) # files, output_path, mode, dedup, password

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_paths = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        header = QLabel("Compression Workspace")
        header.setProperty("class", "section_header")
        layout.addWidget(header)

        # File Selection Card
        sel_card = QFrame()
        sel_card.setProperty("class", "card")
        sel_layout = QVBoxLayout(sel_card)

        sel_title = QLabel("Input Files & Folders")
        sel_title.setProperty("class", "card_title")
        sel_layout.addWidget(sel_title)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("background-color: #101117; border: 1px solid #282c3c; border-radius: 4px; padding: 4px;")
        sel_layout.addWidget(self.list_widget)

        btns_row = QHBoxLayout()
        btn_add_files = QPushButton("+ Add Files")
        btn_add_files.setProperty("class", "secondary_btn")
        btn_add_files.clicked.connect(self._browse_files)

        btn_add_folder = QPushButton("+ Add Folder")
        btn_add_folder.setProperty("class", "secondary_btn")
        btn_add_folder.clicked.connect(self._browse_folder)

        btn_clear = QPushButton("Clear Selection")
        btn_clear.setProperty("class", "secondary_btn")
        btn_clear.clicked.connect(self._clear_selection)

        btns_row.addWidget(btn_add_files)
        btns_row.addWidget(btn_add_folder)
        btns_row.addWidget(btn_clear)
        btns_row.addStretch()
        sel_layout.addLayout(btns_row)
        layout.addWidget(sel_card)

        # Options Card
        opt_card = QFrame()
        opt_card.setProperty("class", "card")
        opt_layout = QVBoxLayout(opt_card)

        opt_title = QLabel("Archive Settings")
        opt_title.setProperty("class", "card_title")
        opt_layout.addWidget(opt_title)

        # Destination .god archive row
        dest_row = QHBoxLayout()
        dest_lbl = QLabel("Output Archive:")
        dest_lbl.setFixedWidth(120)
        self.dest_edit = QLineEdit()
        self.dest_edit.setPlaceholderText("Select destination path (e.g. D:\\backups\\archive.god)")
        btn_browse_dest = QPushButton("Browse...")
        btn_browse_dest.setProperty("class", "secondary_btn")
        btn_browse_dest.clicked.connect(self._browse_dest)
        dest_row.addWidget(dest_lbl)
        dest_row.addWidget(self.dest_edit)
        dest_row.addWidget(btn_browse_dest)
        opt_layout.addLayout(dest_row)

        # Mode row
        mode_row = QHBoxLayout()
        mode_lbl = QLabel("Compression Mode:")
        mode_lbl.setFixedWidth(120)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "BALANCED - Fast content profiling with candidate trials (Recommended)",
            "FAST - Real-time LZ4 & low-latency Zstd",
            "MAXIMUM - Exhaustive candidate search (Zstd 22, LZMA2 9, Brotli 11)",
            "RESEARCH - Experimental neural context entropy coding"
        ])
        mode_row.addWidget(mode_lbl)
        mode_row.addWidget(self.mode_combo)
        opt_layout.addLayout(mode_row)

        # Deduplication checkbox
        self.chk_dedup = QCheckBox("Enable Block-Level Deduplication (Content-defined chunking)")
        self.chk_dedup.setChecked(True)
        opt_layout.addWidget(self.chk_dedup)

        # Password Protection Row
        pass_row = QHBoxLayout()
        pass_lbl = QLabel("Password (AES-256):")
        pass_lbl.setFixedWidth(120)
        self.pass_edit = QLineEdit()
        self.pass_edit.setPlaceholderText("Optional: Leave empty for unencrypted archive")
        self.pass_edit.setEchoMode(QLineEdit.Password)
        
        self.chk_show_pass = QCheckBox("Show")
        self.chk_show_pass.stateChanged.connect(
            lambda s: self.pass_edit.setEchoMode(QLineEdit.Normal if s else QLineEdit.Password)
        )
        pass_row.addWidget(pass_lbl)
        pass_row.addWidget(self.pass_edit)
        pass_row.addWidget(self.chk_show_pass)
        opt_layout.addLayout(pass_row)

        layout.addWidget(opt_card)

        # Start button
        self.btn_start = QPushButton("Start Compression")
        self.btn_start.setProperty("class", "primary_btn")
        self.btn_start.setFixedHeight(40)
        self.btn_start.clicked.connect(self._on_start_clicked)
        layout.addWidget(self.btn_start)

    def _browse_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files to Compress")
        if files:
            for f in files:
                if f not in self.selected_paths:
                    self.selected_paths.append(f)
                    self.list_widget.addItem(f)
            self._auto_populate_dest()

    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Compress")
        if folder and folder not in self.selected_paths:
            self.selected_paths.append(folder)
            self.list_widget.addItem(folder)
            self._auto_populate_dest()

    def _clear_selection(self):
        self.selected_paths.clear()
        self.list_widget.clear()

    def add_paths(self, paths: list[str]):
        """Add input paths programmatically (e.g. from command line or Explorer)."""
        for p in paths:
            if p not in self.selected_paths:
                self.selected_paths.append(p)
                self.list_widget.addItem(p)
        self._auto_populate_dest()

    def _auto_populate_dest(self):
        if not self.dest_edit.text() and self.selected_paths:
            first = self.selected_paths[0]
            base = os.path.splitext(first)[0] if os.path.isfile(first) else first
            self.dest_edit.setText(base + ".god")

    def _browse_dest(self):
        dest, _ = QFileDialog.getSaveFileName(self, "Select Output .god Archive", filter="GODZIP Archive (*.god)")
        if dest:
            if not dest.endswith(".god"):
                dest += ".god"
            self.dest_edit.setText(dest)

    def _on_start_clicked(self):
        if not self.selected_paths:
            return
        dest = self.dest_edit.text().strip()
        if not dest:
            return

        mode_idx = self.mode_combo.currentIndex()
        modes = [CompressionMode.BALANCED, CompressionMode.FAST, CompressionMode.MAXIMUM, CompressionMode.RESEARCH]
        mode = modes[mode_idx]

        password = self.pass_edit.text().strip() or None
        self.start_compression.emit(self.selected_paths, dest, mode, self.chk_dedup.isChecked(), password)
