# Copyright 2024, The Tor Project
# See LICENSE for licensing information

"""
Dark QSS theme for the nyx PyQt6 GUI.
"""

DARK_STYLE = """
/* === Hauptfenster === */
QMainWindow, QWidget {
    background-color: #1a1a2e;
    color: #e0e0e0;
    font-family: "Fira Code", "Courier New", monospace;
    font-size: 13px;
}

/* === Toolbar === */
QToolBar {
    background-color: #16213e;
    border-bottom: 2px solid #0f3460;
    padding: 6px 8px;
    spacing: 8px;
    min-height: 38px;
}

/* === Tabs === */
QTabWidget::pane {
    border: 1px solid #0f3460;
    background-color: #1a1a2e;
}

QTabBar::tab {
    background-color: #16213e;
    color: #a0a0c0;
    padding: 6px 16px;
    border: 1px solid #0f3460;
    border-bottom: none;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #7b2fbe;
    color: #ffffff;
    font-weight: bold;
}

QTabBar::tab:hover:!selected {
    background-color: #2d2d5e;
    color: #e0e0e0;
}

/* === Buttons === */
QPushButton {
    background-color: #0f3460;
    color: #e0e0e0;
    border: 1px solid #7b2fbe;
    border-radius: 4px;
    padding: 5px 14px;
}

QPushButton:hover {
    background-color: #7b2fbe;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #5a1f8c;
}

QPushButton#stop_button {
    background-color: #7b0d1e;
    color: #ffffff;
    border: 1px solid #c0392b;
    font-weight: bold;
    padding: 5px 18px;
}

QPushButton#stop_button:hover {
    background-color: #c0392b;
}

QPushButton#stop_button:pressed {
    background-color: #922b21;
}

/* === Tabellen === */
QTableWidget {
    background-color: #1a1a2e;
    color: #e0e0e0;
    gridline-color: #0f3460;
    border: none;
    selection-background-color: #7b2fbe;
    selection-color: #ffffff;
}

QTableWidget::item {
    padding: 3px 6px;
    border: none;
}

QTableWidget::item:selected {
    background-color: #7b2fbe;
}

QHeaderView::section {
    background-color: #16213e;
    color: #a0a0c0;
    padding: 5px;
    border: 1px solid #0f3460;
    font-weight: bold;
}

/* === Listen === */
QListWidget {
    background-color: #1a1a2e;
    color: #e0e0e0;
    border: none;
    selection-background-color: #7b2fbe;
}

QListWidget::item {
    padding: 2px 4px;
    border-bottom: 1px solid #16213e;
}

QListWidget::item:selected {
    background-color: #7b2fbe;
    color: #ffffff;
}

/* === TextEdit === */
QTextEdit, QPlainTextEdit {
    background-color: #0d0d1a;
    color: #e0e0e0;
    border: 1px solid #0f3460;
    selection-background-color: #7b2fbe;
}

/* === LineEdit === */
QLineEdit {
    background-color: #0d0d1a;
    color: #e0e0e0;
    border: 1px solid #0f3460;
    border-radius: 3px;
    padding: 4px 8px;
    selection-background-color: #7b2fbe;
}

QLineEdit:focus {
    border: 1px solid #7b2fbe;
}

/* === ComboBox === */
QComboBox {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #0f3460;
    border-radius: 3px;
    padding: 4px 8px;
}

QComboBox::drop-down {
    border: none;
    background-color: #7b2fbe;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #16213e;
    color: #e0e0e0;
    selection-background-color: #7b2fbe;
    border: 1px solid #0f3460;
}

/* === Scrollbars === */
QScrollBar:vertical {
    background-color: #16213e;
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #0f3460;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #7b2fbe;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: #16213e;
    height: 10px;
}

QScrollBar::handle:horizontal {
    background-color: #0f3460;
    min-width: 20px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #7b2fbe;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

/* === Labels === */
QLabel {
    color: #e0e0e0;
}

QLabel#status_connected {
    color: #2ecc71;
    font-weight: bold;
}

QLabel#status_disconnected {
    color: #e74c3c;
    font-weight: bold;
}

QLabel#status_label {
    color: #c0c0d8;
    font-size: 13px;
}

QLabel#status_text {
    color: #ffffff;
    font-weight: bold;
    font-size: 14px;
}

/* === Splitter === */
QSplitter::handle {
    background-color: #0f3460;
}

/* === Menü === */
QMenuBar {
    background-color: #16213e;
    color: #e0e0e0;
}

QMenuBar::item:selected {
    background-color: #7b2fbe;
}

QMenu {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #0f3460;
}

QMenu::item:selected {
    background-color: #7b2fbe;
}

/* === Statusbar === */
QStatusBar {
    background-color: #16213e;
    color: #a0a0c0;
    border-top: 1px solid #0f3460;
}

/* === MessageBox === */
QMessageBox {
    background-color: #1a1a2e;
    color: #e0e0e0;
}
"""

# Farben nach Log-Level
LOG_COLORS = {
    'ERR':         '#e74c3c',
    'WARN':        '#f39c12',
    'NOTICE':      '#2ecc71',
    'INFO':        '#3498db',
    'DEBUG':       '#7f8c8d',
    'NYX_ERROR':   '#e74c3c',
    'NYX_WARNING': '#f39c12',
    'NYX_NOTICE':  '#9b59b6',
}

# Farben nach Verbindungskategorie
CONNECTION_COLORS = {
    'INBOUND':   '#2ecc71',
    'OUTBOUND':  '#3498db',
    'EXIT':      '#e74c3c',
    'HIDDEN':    '#9b59b6',
    'SOCKS':     '#f39c12',
    'CIRCUIT':   '#1abc9c',
    'DIRECTORY': '#7f8c8d',
    'CONTROL':   '#e67e22',
}
