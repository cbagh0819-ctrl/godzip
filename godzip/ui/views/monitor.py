"""Live Job Monitor: Real-time progress, throughput, ETA, and cancellation."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QProgressBar
)
from PySide6.QtCore import Signal
from ...common.types import JobProgress


class MonitorView(QWidget):
    cancel_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        header = QLabel("Live Job Monitor")
        header.setProperty("class", "section_header")
        layout.addWidget(header)

        # Main Progress Card
        card = QFrame()
        card.setProperty("class", "card")
        c_layout = QVBoxLayout(card)
        c_layout.setSpacing(14)

        self.lbl_status = QLabel("Idle - Waiting for job")
        self.lbl_status.setStyleSheet("font-size: 15px; font-weight: 600; color: #ffffff;")
        c_layout.addWidget(self.lbl_status)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        c_layout.addWidget(self.progress_bar)

        self.lbl_current_file = QLabel("File: --")
        self.lbl_current_file.setStyleSheet("color: #8e93a6; font-size: 12px;")
        c_layout.addWidget(self.lbl_current_file)

        # Metrics Grid
        grid = QHBoxLayout()
        grid.setSpacing(12)

        self.card_throughput = self._create_metric("THROUGHPUT", "0.0 MB/s", "#ffffff")
        self.card_processed = self._create_metric("PROCESSED", "0 B / 0 B", "#ffffff")
        self.card_elapsed = self._create_metric("ELAPSED TIME", "0.0 s", "#ffffff")
        self.card_eta = self._create_metric("ESTIMATED REMAINING", "--", "#e63946")

        grid.addWidget(self.card_throughput)
        grid.addWidget(self.card_processed)
        grid.addWidget(self.card_elapsed)
        grid.addWidget(self.card_eta)
        c_layout.addLayout(grid)

        layout.addWidget(card)

        # Cancel / Abort Control
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_cancel = QPushButton("Cancel Job")
        self.btn_cancel.setProperty("class", "primary_btn")
        self.btn_cancel.setStyleSheet("background-color: #ef4444;")
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self.cancel_requested.emit)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

        layout.addStretch()

    def _create_metric(self, label: str, value: str, color: str) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet("background-color: #121318; border: 1px solid #232634; border-radius: 6px; padding: 10px;")
        l = QVBoxLayout(frame)
        l.setContentsMargins(8, 8, 8, 8)
        lbl = QLabel(label)
        lbl.setProperty("class", "stat_label")
        val = QLabel(value)
        val.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: 700;")
        l.addWidget(lbl)
        l.addWidget(val)
        frame.val_label = val
        return frame

    def update_progress(self, p: JobProgress):
        pct = int((p.bytes_processed / p.total_bytes * 100)) if p.total_bytes > 0 else 0
        self.progress_bar.setValue(pct)
        self.lbl_status.setText(p.status_message)
        self.lbl_current_file.setText(f"File: {p.current_file}")
        self.card_throughput.val_label.setText(f"{p.throughput_mbps:.1f} MB/s")
        self.card_processed.val_label.setText(f"{p.bytes_processed / (1024*1024):.1f} MB / {p.total_bytes / (1024*1024):.1f} MB")
        self.card_elapsed.val_label.setText(f"{p.elapsed_seconds:.1f} s")
        if p.eta_seconds is not None and p.eta_seconds > 0:
            self.card_eta.val_label.setText(f"{p.eta_seconds:.1f} s")
        else:
            self.card_eta.val_label.setText("Done")
        self.btn_cancel.setEnabled(True)

    def set_job_finished(self, message: str, is_error: bool = False):
        self.btn_cancel.setEnabled(False)
        color = "#ef4444" if is_error else "#4ade80"
        self.lbl_status.setText(message)
        self.lbl_status.setStyleSheet(f"font-size: 15px; font-weight: 600; color: {color};")
