"""Dashboard page: quick actions, recent jobs, storage overview."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, Signal


class DashboardView(QWidget):
    compress_requested = Signal()
    extract_requested = Signal()
    inspect_requested = Signal()
    benchmark_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        header = QLabel("Dashboard")
        header.setProperty("class", "section_header")
        layout.addWidget(header)

        # Quick Stats Cards Row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)

        self.card_orig = self._create_stat_card("TOTAL PROCESSED", "512.4 MB", "#ffffff")
        self.card_comp = self._create_stat_card("ARCHIVE STORAGE", "168.2 MB", "#ffffff")
        self.card_ratio = self._create_stat_card("AVERAGE RATIO", "3.05 : 1", "#e63946")
        self.card_integrity = self._create_stat_card("VERIFIED RECOVERY", "100.0 %", "#4ade80")

        stats_layout.addWidget(self.card_orig)
        stats_layout.addWidget(self.card_comp)
        stats_layout.addWidget(self.card_ratio)
        stats_layout.addWidget(self.card_integrity)
        layout.addLayout(stats_layout)

        # Quick Actions Row
        actions_card = QFrame()
        actions_card.setProperty("class", "card")
        act_layout = QVBoxLayout(actions_card)

        act_title = QLabel("Quick Actions")
        act_title.setProperty("class", "card_title")
        act_layout.addWidget(act_title)

        btns_layout = QHBoxLayout()
        btn_compress = QPushButton("Compress Files or Folders")
        btn_compress.setProperty("class", "primary_btn")
        btn_compress.clicked.connect(self.compress_requested.emit)

        btn_extract = QPushButton("Extract .god Archive")
        btn_extract.setProperty("class", "secondary_btn")
        btn_extract.clicked.connect(self.extract_requested.emit)

        btn_inspect = QPushButton("Inspect Archive Metadata")
        btn_inspect.setProperty("class", "secondary_btn")
        btn_inspect.clicked.connect(self.inspect_requested.emit)

        btn_bench = QPushButton("Open Benchmark Lab")
        btn_bench.setProperty("class", "secondary_btn")
        btn_bench.clicked.connect(self.benchmark_requested.emit)

        btns_layout.addWidget(btn_compress)
        btns_layout.addWidget(btn_extract)
        btns_layout.addWidget(btn_inspect)
        btns_layout.addWidget(btn_bench)
        act_layout.addLayout(btns_layout)
        layout.addWidget(actions_card)

        # Recent Jobs Table
        recent_card = QFrame()
        recent_card.setProperty("class", "card")
        rec_layout = QVBoxLayout(recent_card)

        rec_title = QLabel("Recent Compression Operations")
        rec_title.setProperty("class", "card_title")
        rec_layout.addWidget(rec_title)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Target", "Mode", "Ratio", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        rec_layout.addWidget(self.table)

        layout.addWidget(recent_card)

    def _create_stat_card(self, label: str, value: str, val_color: str) -> QFrame:
        card = QFrame()
        card.setProperty("class", "card")
        l = QVBoxLayout(card)
        l.setContentsMargins(16, 14, 16, 14)

        lbl = QLabel(label)
        lbl.setProperty("class", "stat_label")
        val = QLabel(value)
        val.setProperty("class", "stat_val")
        val.setStyleSheet(f"color: {val_color};")

        l.addWidget(lbl)
        l.addWidget(val)
        return card

    def add_recent_job(self, timestamp: str, target: str, mode: str, ratio: str, status: str):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(timestamp))
        self.table.setItem(row, 1, QTableWidgetItem(target))
        self.table.setItem(row, 2, QTableWidgetItem(mode))
        self.table.setItem(row, 3, QTableWidgetItem(ratio))
        self.table.setItem(row, 4, QTableWidgetItem(status))
