"""Archive Inspector: View archive contents, block records, compression ratios, and verify integrity."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox,
    QInputDialog, QLineEdit
)
from PySide6.QtCore import Signal
from ...archive.reader import ArchiveReader


class InspectorView(QWidget):
    extract_requested = Signal(str, str, object) # archive_path, destination, password

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_archive_path = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        header = QLabel("Archive Inspector")
        header.setProperty("class", "section_header")
        layout.addWidget(header)

        # Top Bar
        bar = QHBoxLayout()
        self.btn_open = QPushButton("Open .god Archive...")
        self.btn_open.setProperty("class", "primary_btn")
        self.btn_open.clicked.connect(self._on_open_clicked)

        self.btn_verify = QPushButton("Verify Integrity")
        self.btn_verify.setProperty("class", "secondary_btn")
        self.btn_verify.setEnabled(False)
        self.btn_verify.clicked.connect(self._on_verify_clicked)

        self.btn_extract = QPushButton("Extract All...")
        self.btn_extract.setProperty("class", "secondary_btn")
        self.btn_extract.setEnabled(False)
        self.btn_extract.clicked.connect(self._on_extract_clicked)

        self.btn_sfx = QPushButton("Export as SFX (.exe)")
        self.btn_sfx.setProperty("class", "secondary_btn")
        self.btn_sfx.setEnabled(False)
        self.btn_sfx.clicked.connect(self._on_sfx_clicked)

        self.lbl_path = QLabel("No archive loaded")
        self.lbl_path.setStyleSheet("color: #8e93a6;")

        bar.addWidget(self.btn_open)
        bar.addWidget(self.btn_verify)
        bar.addWidget(self.btn_extract)
        bar.addWidget(self.btn_sfx)
        bar.addWidget(self.lbl_path)
        bar.addStretch()
        layout.addLayout(bar)

        # Summary Frame
        self.summary_frame = QFrame()
        self.summary_frame.setProperty("class", "card")
        sum_l = QHBoxLayout(self.summary_frame)
        self.sum_files = QLabel("Files: --")
        self.sum_orig = QLabel("Original: --")
        self.sum_comp = QLabel("Compressed: --")
        self.sum_ratio = QLabel("Ratio: --")
        for lbl in (self.sum_files, self.sum_orig, self.sum_comp, self.sum_ratio):
            lbl.setStyleSheet("font-weight: 600; color: #ffffff;")
            sum_l.addWidget(lbl)
        layout.addWidget(self.summary_frame)

        # File List Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Path", "Original Size", "Compressed Size", "Blocks", "Digest"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

    def load_archive(self, path: str):
        try:
            reader = ArchiveReader(path)
            info = reader.inspect()
            self.current_archive_path = path
            self.lbl_path.setText(path)
            self.btn_verify.setEnabled(True)
            self.btn_extract.setEnabled(True)
            self.btn_sfx.setEnabled(True)

            self.sum_files.setText(f"Files: {info['total_files']:,}")
            self.sum_orig.setText(f"Original: {info['original_bytes'] / (1024*1024):.2f} MB")
            self.sum_comp.setText(f"Compressed: {info['compressed_bytes'] / (1024*1024):.2f} MB")
            enc_str = " | 🔒 AES-256" if info.get("is_encrypted") else ""
            self.sum_ratio.setText(f"Ratio: {info['compression_ratio']:.2f}x ({info['reduction_pct']:.1f}%){enc_str}")

            self.table.setRowCount(0)
            for f in info["files"]:
                r = self.table.rowCount()
                self.table.insertRow(r)
                self.table.setItem(r, 0, QTableWidgetItem(f["path"]))
                self.table.setItem(r, 1, QTableWidgetItem(f"{f['original_size']:,} B"))
                self.table.setItem(r, 2, QTableWidgetItem(f"{f['compressed_size']:,} B"))
                self.table.setItem(r, 3, QTableWidgetItem(str(f["blocks"])))
                self.table.setItem(r, 4, QTableWidgetItem(f["digest"][:16] + "..."))
        except Exception as e:
            QMessageBox.critical(self, "Failed to Load Archive", str(e))

    def _on_open_clicked(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open GODZIP Archive", filter="GODZIP Archives (*.god)")
        if path:
            self.load_archive(path)

    def _on_verify_clicked(self):
        if not self.current_archive_path:
            return
        try:
            reader = ArchiveReader(self.current_archive_path)
            info = reader.inspect()
            password = None
            if info.get("is_encrypted"):
                pwd, ok = QInputDialog.getText(
                    self, "Password Required", "Enter password for encrypted archive:", QLineEdit.Password
                )
                if not ok or not pwd:
                    return
                password = pwd

            reader = ArchiveReader(self.current_archive_path, password=password)
            if reader.verify():
                QMessageBox.information(self, "Integrity Verified", "All block CRCs, cryptographic digests, and recovery bytes match perfectly!")
        except Exception as e:
            QMessageBox.critical(self, "Integrity Verification Failed", str(e))

    def _on_extract_clicked(self):
        if not self.current_archive_path:
            return
        reader = ArchiveReader(self.current_archive_path)
        info = reader.inspect()
        password = None
        if info.get("is_encrypted"):
            pwd, ok = QInputDialog.getText(
                self, "Password Required", "Enter password for encrypted archive:", QLineEdit.Password
            )
            if not ok or not pwd:
                return
            password = pwd

        dest = QFileDialog.getExistingDirectory(self, "Select Destination Directory")
        if dest:
            self.extract_requested.emit(self.current_archive_path, dest, password)

    def _on_sfx_clicked(self):
        if not self.current_archive_path:
            return
        default_name = os.path.splitext(self.current_archive_path)[0] + ".exe"
        dest_exe, _ = QFileDialog.getSaveFileName(
            self, "Export Self-Extracting Executable", default_name, filter="Windows Executable (*.exe)"
        )
        if not dest_exe:
            return
        if not dest_exe.lower().endswith(".exe"):
            dest_exe += ".exe"
        try:
            from ...archive.sfx import create_sfx_executable
            ok, msg = create_sfx_executable(self.current_archive_path, dest_exe)
            if ok:
                QMessageBox.information(
                    self,
                    "SFX Export Complete",
                    f"Self-Extracting executable created successfully!\n\nLocation: {dest_exe}\n\n"
                    "This executable can be run on any Windows machine to extract your files with zero dependencies."
                )
            else:
                QMessageBox.warning(self, "SFX Export Failed", msg)
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))
