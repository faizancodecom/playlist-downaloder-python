"""
Professional, native-grade Dark Theme Stylesheet for PyQt6
Carefully tuned to avoid 'AI-generated' appearance:
- Pure dark slate and graphite tones
- Balanced contrast and crisp border hierarchy
- Clean typography and native OS control metrics
"""

DARK_STYLESHEET = """
/* Base Window & Dialog */
QMainWindow, QDialog, QWidget#centralWidget {
    background-color: #0d1117;
    color: #e6edf3;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}

QWidget {
    outline: none;
}

/* Tooltips */
QToolTip {
    background-color: #1f242c;
    color: #e6edf3;
    border: 1px solid #30363d;
    padding: 5px 8px;
    border-radius: 4px;
    font-size: 12px;
}

/* Group Boxes / Cards */
QGroupBox {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    margin-top: 18px;
    padding-top: 14px;
    font-weight: 600;
    color: #f0f6fc;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    left: 12px;
    color: #58a6ff;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Input Fields */
QLineEdit {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px 12px;
    color: #f0f6fc;
    selection-background-color: #1f6feb;
    selection-color: #ffffff;
    font-size: 13px;
}

QLineEdit:focus {
    border: 1px solid #58a6ff;
    background-color: #11161f;
}

QLineEdit:disabled {
    background-color: #161b22;
    color: #6e7681;
    border-color: #21262d;
}

/* Push Buttons */
QPushButton {
    background-color: #21262d;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px 16px;
    color: #c9d1d9;
    font-weight: 500;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #30363d;
    border-color: #8b949e;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #161b22;
    border-color: #58a6ff;
}

QPushButton:disabled {
    background-color: #161b22;
    color: #484f58;
    border-color: #21262d;
}

/* Primary Action Button */
QPushButton#primaryButton {
    background-color: #238636;
    border: 1px solid #2ea043;
    color: #ffffff;
    font-weight: 600;
    font-size: 13px;
    padding: 9px 20px;
}

QPushButton#primaryButton:hover {
    background-color: #2ea043;
    border-color: #3fb950;
}

QPushButton#primaryButton:pressed {
    background-color: #1f6feb;
    border-color: #388bfd;
}

QPushButton#primaryButton:disabled {
    background-color: #1b4b27;
    border-color: #1b4b27;
    color: #8b949e;
}

/* Accent Button */
QPushButton#accentButton {
    background-color: #1f6feb;
    border: 1px solid #388bfd;
    color: #ffffff;
    font-weight: 600;
}

QPushButton#accentButton:hover {
    background-color: #388bfd;
}

QPushButton#accentButton:pressed {
    background-color: #1158c7;
}

/* Danger / Stop Button */
QPushButton#dangerButton {
    background-color: #21262d;
    border: 1px solid #da3633;
    color: #f85149;
}

QPushButton#dangerButton:hover {
    background-color: #b62324;
    border-color: #f85149;
    color: #ffffff;
}

/* Combo Boxes */
QComboBox {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 12px;
    color: #f0f6fc;
    min-height: 20px;
}

QComboBox:hover {
    border-color: #8b949e;
}

QComboBox:focus {
    border-color: #58a6ff;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid #30363d;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #8b949e;
    margin-right: 6px;
}

QComboBox QAbstractItemView {
    background-color: #161b22;
    border: 1px solid #30363d;
    selection-background-color: #1f6feb;
    selection-color: #ffffff;
    color: #e6edf3;
    padding: 4px;
}

/* Checkboxes */
QCheckBox {
    spacing: 8px;
    color: #f0f6fc;
    font-size: 13px;
}

QCheckBox::indicator {
    width: 17px;
    height: 17px;
    border: 1px solid #30363d;
    border-radius: 4px;
    background-color: #0d1117;
}

QCheckBox::indicator:hover {
    border-color: #58a6ff;
}

QCheckBox::indicator:checked {
    background-color: #1f6feb;
    border-color: #58a6ff;
    image: none;
}

/* Radio Buttons */
QRadioButton {
    spacing: 8px;
    color: #f0f6fc;
    font-size: 13px;
    font-weight: 500;
    background: transparent;
}

QRadioButton:hover {
    color: #ffffff;
}

QRadioButton:checked {
    color: #58a6ff;
    font-weight: 600;
}

QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #484f58;
    border-radius: 8px;
    background-color: #0d1117;
}

QRadioButton::indicator:hover {
    border-color: #58a6ff;
}

QRadioButton::indicator:checked {
    border: 3px solid #1f6feb;
    background-color: #58a6ff;
}

/* Progress Bars */
QProgressBar {
    border: 1px solid #30363d;
    border-radius: 6px;
    text-align: center;
    background-color: #0d1117;
    color: #f0f6fc;
    font-weight: 600;
    font-size: 11px;
    min-height: 16px;
    max-height: 16px;
}

QProgressBar::chunk {
    background-color: #238636;
    border-radius: 5px;
}

/* Scroll Area & Scroll Bars */
QScrollArea {
    border: 1px solid #30363d;
    border-radius: 8px;
    background-color: #0d1117;
}

QScrollBar:vertical {
    border: none;
    background: #0d1117;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #30363d;
    min-height: 24px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #484f58;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Tab / Segmented Bar */
QTabBar::tab {
    background: #161b22;
    color: #8b949e;
    padding: 8px 18px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    border: 1px solid transparent;
    margin-right: 2px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background: #0d1117;
    color: #58a6ff;
    border: 1px solid #30363d;
    border-bottom: 1px solid #0d1117;
}

QTabBar::tab:hover:!selected {
    background: #21262d;
    color: #c9d1d9;
}

/* List / Tree View */
QListWidget, QTreeWidget, QTableWidget {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    color: #c9d1d9;
}

/* Text Edit / Log Console */
QPlainTextEdit {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    color: #8b949e;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 11px;
    padding: 6px;
}

/* Status Bar */
QStatusBar {
    background-color: #161b22;
    border-top: 1px solid #30363d;
    color: #8b949e;
    font-size: 12px;
}
"""
