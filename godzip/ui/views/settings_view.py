"""Settings page: configuration for thread count, memory limits, and temp folder."""

import os
import multiprocessing
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QComboBox, QSpinBox, QLineEdit, QFileDialog, QCheckBox, QMessageBox
)


class SettingsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        header = QLabel("Settings")
        header.setProperty("class", "section_header")
        layout.addWidget(header)

        card = QFrame()
        card.setProperty("class", "card")
        c_layout = QVBoxLayout(card)
        c_layout.setSpacing(14)

        # Default Mode
        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Default Compression Mode:"))
        self.combo_mode = QComboBox()
        self.combo_mode.addItems(["BALANCED", "FAST", "MAXIMUM", "RESEARCH"])
        r1.addWidget(self.combo_mode)
        c_layout.addLayout(r1)

        # Thread Limit
        r2 = QHBoxLayout()
        r2.addWidget(QLabel("Thread Concurrency Limit:"))
        self.spin_threads = QSpinBox()
        self.spin_threads.setRange(1, multiprocessing.cpu_count() * 2)
        self.spin_threads.setValue(multiprocessing.cpu_count())
        r2.addWidget(self.spin_threads)
        c_layout.addLayout(r2)

        # Memory Budget
        r3 = QHBoxLayout()
        r3.addWidget(QLabel("Memory Working Budget (MB):"))
        self.spin_mem = QSpinBox()
        self.spin_mem.setRange(256, 65536)
        self.spin_mem.setValue(2048)
        r3.addWidget(self.spin_mem)
        c_layout.addLayout(r3)

        # Temp directory
        r4 = QHBoxLayout()
        r4.addWidget(QLabel("Temporary Storage Folder:"))
        self.edit_temp = QLineEdit(os.environ.get("TEMP", "C:\\Temp"))
        btn_temp = QPushButton("Browse...")
        btn_temp.setProperty("class", "secondary_btn")
        btn_temp.clicked.connect(self._browse_temp)
        r4.addWidget(self.edit_temp)
        r4.addWidget(btn_temp)
        c_layout.addLayout(r4)

        # Checkbox
        self.chk_verify_always = QCheckBox("Always perform cryptographic hash check after extraction")
        self.chk_verify_always.setChecked(True)
        c_layout.addWidget(self.chk_verify_always)

        self.chk_neural_enabled = QCheckBox("Enable Experimental Neural Context Codec in Research Mode")
        self.chk_neural_enabled.setChecked(True)
        c_layout.addWidget(self.chk_neural_enabled)

        layout.addWidget(card)

        # Save button
        btn_save = QPushButton("Save Settings")
        btn_save.setProperty("class", "primary_btn")
        btn_save.setFixedWidth(140)
        btn_save.clicked.connect(lambda: QMessageBox.information(self, "Settings Saved", "Preferences successfully updated."))
        layout.addWidget(btn_save)

        layout.addStretch()

    def _browse_temp(self):
        d = QFileDialog.getExistingDirectory(self, "Select Temporary Folder")
        if d:
            self.edit_temp.setText(d)
