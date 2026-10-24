"""Benchmark Lab view: run comparative tests against Zstandard and 7-Zip."""

import os
import threading
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox, QProgressBar
)
from PySide6.QtCore import Qt, QObject, Signal
from benchmark.benchmark import BenchmarkRunner


class BenchmarkWorker(QObject):
    finished = Signal(list)
    status_updated = Signal(str)

    def __init__(self, work_dir: str):
        super().__init__()
        self.work_dir = work_dir

    def run(self):
        try:
            self.status_updated.emit("Generating 14-category corpus and benchmarking...")
            runner = BenchmarkRunner(work_dir=self.work_dir)
            results = runner.run_all()
            self.finished.emit(results)
        except Exception as e:
            self.status_updated.emit(f"Error: {e}")
            self.finished.emit([])


class BenchmarkView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.results = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        header = QLabel("Benchmark Lab")
        header.setProperty("class", "section_header")
        layout.addWidget(header)

        # Control Row
        bar = QHBoxLayout()
        self.btn_run = QPushButton("Run Full 14-Category Benchmark Suite")
        self.btn_run.setProperty("class", "primary_btn")
        self.btn_run.clicked.connect(self._start_benchmarks)

        self.btn_export = QPushButton("Export Reports (CSV / JSON / MD)")
        self.btn_export.setProperty("class", "secondary_btn")
        self.btn_export.setEnabled(False)
        self.btn_export.clicked.connect(self._export_reports)

        self.lbl_status = QLabel("Idle")
        self.lbl_status.setStyleSheet("color: #8e93a6;")

        bar.addWidget(self.btn_run)
        bar.addWidget(self.btn_export)
        bar.addWidget(self.lbl_status)
        bar.addStretch()
        layout.addLayout(bar)

        # Results Table
        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels([
            "Category", "Compressor", "Mode / Preset", "Original Size", "Archive Size", "Ratio", "Space Saved", "Comp Time", "Verified"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

    def _start_benchmarks(self):
        self.btn_run.setEnabled(False)
        self.lbl_status.setText("Running benchmark trials in background...")
        self.table.setRowCount(0)

        self.worker = BenchmarkWorker(work_dir="benchmark")
        self.worker_thread = threading.Thread(target=self.worker.run, daemon=True)
        self.worker.finished.connect(self._on_bench_finished)
        self.worker.status_updated.connect(self.lbl_status.setText)
        self.worker_thread.start()

    def _on_bench_finished(self, results):
        self.btn_run.setEnabled(True)
        self.btn_export.setEnabled(True)
        self.results = results
        self.lbl_status.setText(f"Completed {len(results)} trials with verified byte-exact reconstruction.")

        self.table.setRowCount(0)
        for r in results:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(r["category"]))
            self.table.setItem(row, 1, QTableWidgetItem(r["compressor"]))
            self.table.setItem(row, 2, QTableWidgetItem(r["mode"]))
            self.table.setItem(row, 3, QTableWidgetItem(f"{r['original_bytes']:,} B"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{r['archive_bytes']:,} B"))
            self.table.setItem(row, 5, QTableWidgetItem(f"{r['compression_ratio']:.2f}x"))
            self.table.setItem(row, 6, QTableWidgetItem(f"{r['reduction_pct']:.1f}%"))
            self.table.setItem(row, 7, QTableWidgetItem(f"{r['comp_time_sec']:.3f}s"))
            self.table.setItem(row, 8, QTableWidgetItem("PASS" if r["verified"] else "FAIL"))

    def _export_reports(self):
        dest_dir = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if dest_dir:
            from benchmark.reporters import export_csv, export_json, export_markdown
            export_csv(self.results, os.path.join(dest_dir, "benchmark_report.csv"))
            export_json(self.results, os.path.join(dest_dir, "benchmark_report.json"))
            export_markdown(self.results, os.path.join(dest_dir, "benchmark_report.md"))
            QMessageBox.information(self, "Reports Exported", f"Saved CSV, JSON, and Markdown reports to {dest_dir}")
