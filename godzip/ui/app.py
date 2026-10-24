"""Main desktop application window and PySide6 application entry point."""

import sys
import os
import time
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget, QPushButton, QLabel, QFrame, QMessageBox, QButtonGroup
)
from PySide6.QtCore import Qt, Signal, QObject
from .styles import DARK_THEME_QSS
from .views.dashboard import DashboardView
from .views.workspace import WorkspaceView
from .views.monitor import MonitorView
from .views.inspector import InspectorView
from .views.benchmark_view import BenchmarkView
from .views.settings_view import SettingsView
from .views.about_view import AboutView
from ..jobs.controller import JobController
from ..common.constants import CompressionMode
from ..common.types import JobProgress


class JobBridge(QObject):
    """Bridge for safely dispatching thread callbacks to Qt GUI main thread."""
    progress = Signal(object)
    completed = Signal(dict)
    error = Signal(str)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GODZIP — Next-Generation Lossless Compression Platform")
        self.resize(1100, 720)
        self.setMinimumSize(900, 600)

        self.job_controller = JobController()
        self.job_bridge = JobBridge()
        self.job_bridge.progress.connect(self._on_job_progress)
        self.job_bridge.completed.connect(self._on_job_completed)
        self.job_bridge.error.connect(self._on_job_error)

        self._init_ui()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Sidebar Navigation
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(0, 0, 0, 0)
        sb_layout.setSpacing(2)

        # Brand header
        brand_title = QLabel("GODZIP")
        brand_title.setObjectName("brand_title")
        brand_sub = QLabel("LOSSLESS PLATFORM")
        brand_sub.setObjectName("brand_sub")
        brand_sub.setStyleSheet("color: #e63946; font-size: 10px; font-weight: 700; letter-spacing: 1.5px; padding: 0 16px 16px 16px;")
        sb_layout.addWidget(brand_title)
        sb_layout.addWidget(brand_sub)

        # Nav Buttons
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        self.btn_nav_dash = self._create_nav_btn("Dashboard", 0)
        self.btn_nav_work = self._create_nav_btn("Compression Workspace", 1)
        self.btn_nav_mon = self._create_nav_btn("Live Job Monitor", 2)
        self.btn_nav_insp = self._create_nav_btn("Archive Inspector", 3)
        self.btn_nav_bench = self._create_nav_btn("Benchmark Lab", 4)
        self.btn_nav_sett = self._create_nav_btn("Settings", 5)
        self.btn_nav_about = self._create_nav_btn("About & Diagnostics", 6)

        for btn in (self.btn_nav_dash, self.btn_nav_work, self.btn_nav_mon,
                    self.btn_nav_insp, self.btn_nav_bench, self.btn_nav_sett, self.btn_nav_about):
            sb_layout.addWidget(btn)

        sb_layout.addStretch()
        main_layout.addWidget(sidebar)

        # 2. Main Stacked Pages
        self.stack = QStackedWidget()
        self.stack.setObjectName("content_stack")

        self.view_dashboard = DashboardView()
        self.view_workspace = WorkspaceView()
        self.view_monitor = MonitorView()
        self.view_inspector = InspectorView()
        self.view_benchmark = BenchmarkView()
        self.view_settings = SettingsView()
        self.view_about = AboutView()

        self.stack.addWidget(self.view_dashboard)
        self.stack.addWidget(self.view_workspace)
        self.stack.addWidget(self.view_monitor)
        self.stack.addWidget(self.view_inspector)
        self.stack.addWidget(self.view_benchmark)
        self.stack.addWidget(self.view_settings)
        self.stack.addWidget(self.view_about)

        main_layout.addWidget(self.stack)

        # Connect Navigation Actions
        self.view_dashboard.compress_requested.connect(lambda: self.switch_page(1))
        self.view_dashboard.extract_requested.connect(self._quick_extract)
        self.view_dashboard.inspect_requested.connect(lambda: self.switch_page(3))
        self.view_dashboard.benchmark_requested.connect(lambda: self.switch_page(4))

        self.view_workspace.start_compression.connect(self._start_compression_job)
        self.view_monitor.cancel_requested.connect(self._cancel_job)
        self.view_inspector.extract_requested.connect(self._start_extraction_job)

        self.btn_nav_dash.setChecked(True)

    def _create_nav_btn(self, text: str, page_index: int) -> QPushButton:
        btn = QPushButton(text)
        btn.setProperty("class", "nav_btn")
        btn.setCheckable(True)
        self.nav_group.addButton(btn, page_index)
        btn.clicked.connect(lambda: self.switch_page(page_index))
        return btn

    def switch_page(self, index: int):
        self.stack.setCurrentIndex(index)
        btn = self.nav_group.button(index)
        if btn:
            btn.setChecked(True)

    def _quick_extract(self):
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(self, "Select .god Archive to Extract", filter="GODZIP Archives (*.god)")
        if path:
            dest = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
            if dest:
                self._start_extraction_job(path, dest)

    def _start_compression_job(self, source_paths: list, output_path: str, mode: CompressionMode, enable_dedup: bool):
        try:
            self.job_controller.start_compression(
                source_paths=source_paths,
                output_path=output_path,
                mode=mode,
                enable_dedup=enable_dedup,
                on_progress=lambda p: self.job_bridge.progress.emit(p),
                on_complete=lambda res: self.job_bridge.completed.emit(res),
                on_error=lambda err: self.job_bridge.error.emit(err),
            )
            self.switch_page(2) # Switch to Live Monitor
        except Exception as e:
            QMessageBox.critical(self, "Job Start Error", str(e))

    def _start_extraction_job(self, archive_path: str, destination_dir: str):
        try:
            self.job_controller.start_extraction(
                archive_path=archive_path,
                destination_dir=destination_dir,
                on_progress=lambda p: self.job_bridge.progress.emit(p),
                on_complete=lambda res: self.job_bridge.completed.emit(res),
                on_error=lambda err: self.job_bridge.error.emit(err),
            )
            self.switch_page(2) # Switch to Live Monitor
        except Exception as e:
            QMessageBox.critical(self, "Extraction Error", str(e))

    def _cancel_job(self):
        self.job_controller.cancel()

    def _on_job_progress(self, p: JobProgress):
        self.view_monitor.update_progress(p)

    def _on_job_completed(self, res: dict):
        if res.get("action") == "compress":
            msg = f"Archive created: {res['compressed_bytes']:,} bytes (Ratio: {res['ratio']:.2f}x) in {res['elapsed_seconds']}s"
            self.view_monitor.set_job_finished(msg, is_error=False)
            self.view_dashboard.add_recent_job(
                time.strftime("%H:%M:%S"),
                os.path.basename(res['output_path']),
                "MAX / BAL",
                f"{res['ratio']:.2f}x",
                "COMPLETED"
            )
        else:
            msg = f"Extraction complete: {res['bytes_extracted']:,} bytes extracted to {res['destination']}."
            self.view_monitor.set_job_finished(msg, is_error=False)

    def _on_job_error(self, err: str):
        self.view_monitor.set_job_finished(f"Error: {err}", is_error=True)
        QMessageBox.critical(self, "Job Error", err)


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME_QSS)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
