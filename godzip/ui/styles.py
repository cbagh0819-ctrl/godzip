"""Dark charcoal theme with restrained red accents for GODZIP desktop UI."""

DARK_THEME_QSS = """
QMainWindow {
    background-color: #121316;
    color: #e0e2ec;
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    font-size: 13px;
}

QWidget {
    background-color: #121316;
    color: #d1d4dc;
    font-family: 'Segoe UI', sans-serif;
}

/* Sidebar Navigation */
#sidebar {
    background-color: #0e0f12;
    border-right: 1px solid #1e2028;
    min-width: 210px;
    max-width: 210px;
}

#brand_title {
    color: #ffffff;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 1.5px;
    padding: 18px 16px 4px 16px;
}

#brand_subtitle {
    color: #e63946;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 2px;
    padding: 0px 16px 20px 16px;
    text-transform: uppercase;
}

QPushButton.nav_btn {
    background-color: transparent;
    color: #8e93a6;
    border: none;
    border-left: 3px solid transparent;
    padding: 12px 18px;
    text-align: left;
    font-size: 13px;
    font-weight: 500;
}

QPushButton.nav_btn:hover {
    background-color: #161820;
    color: #f0f2f8;
}

QPushButton.nav_btn:checked {
    background-color: #1a1c24;
    color: #ffffff;
    border-left: 3px solid #e63946;
    font-weight: 600;
}

/* Content Area */
#content_stack {
    background-color: #121316;
    padding: 24px;
}

/* Cards & Containers */
QFrame.card {
    background-color: #171821;
    border: 1px solid #232634;
    border-radius: 8px;
    padding: 16px;
}

QLabel.card_title {
    color: #ffffff;
    font-size: 15px;
    font-weight: 600;
    margin-bottom: 8px;
}

QLabel.section_header {
    color: #ffffff;
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 16px;
}

QLabel.stat_val {
    color: #ffffff;
    font-size: 26px;
    font-weight: 700;
}

QLabel.stat_label {
    color: #7b8094;
    font-size: 11px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Primary Action Buttons */
QPushButton.primary_btn {
    background-color: #e63946;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 9px 18px;
    font-size: 13px;
    font-weight: 600;
}

QPushButton.primary_btn:hover {
    background-color: #ff4d5a;
}

QPushButton.primary_btn:pressed {
    background-color: #cc2936;
}

QPushButton.primary_btn:disabled {
    background-color: #382025;
    color: #6a585c;
}

/* Secondary Buttons */
QPushButton.secondary_btn {
    background-color: #1f222e;
    color: #d1d4dc;
    border: 1px solid #2d3142;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 500;
}

QPushButton.secondary_btn:hover {
    background-color: #262a3a;
    border-color: #3d4257;
    color: #ffffff;
}

/* Inputs & Form Controls */
QLineEdit, QComboBox, QSpinBox {
    background-color: #101117;
    color: #ffffff;
    border: 1px solid #282c3c;
    border-radius: 5px;
    padding: 8px 12px;
    selection-background-color: #e63946;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border-color: #e63946;
}

/* Tables */
QTableWidget {
    background-color: #15161f;
    border: 1px solid #232634;
    border-radius: 6px;
    gridline-color: #1c1e28;
    color: #d8dae2;
    selection-background-color: #232738;
    selection-color: #ffffff;
}

QHeaderView::section {
    background-color: #101117;
    color: #8e93a6;
    padding: 8px 12px;
    border: none;
    border-bottom: 1px solid #232634;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
}

/* Progress Bar */
QProgressBar {
    background-color: #101117;
    border: 1px solid #232634;
    border-radius: 5px;
    height: 14px;
    text-align: center;
    color: #ffffff;
    font-size: 10px;
    font-weight: 600;
}

QProgressBar::chunk {
    background-color: #e63946;
    border-radius: 4px;
}

/* Scrollbars */
QScrollBar:vertical {
    background: #121316;
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #252836;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #373c4f;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""
