import os
import sys
from pathlib import Path

# Ensure high DPI scaling on modern displays
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

from app.ui.main_window import MainWindow
from app.ui.styles import DARK_STYLESHEET

def setup_dark_palette(app: QApplication):
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#0d1117"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#f0f6fc"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#161b22"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#0d1117"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#1f242c"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#f0f6fc"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#f0f6fc"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#21262d"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#f0f6fc"))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.Link, QColor("#58a6ff"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#1f6feb"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#6e7681"))
    app.setPalette(palette)
    app.setStyleSheet(DARK_STYLESHEET)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Playlist Downloader")
    app.setOrganizationName("MediaTools")

    setup_dark_palette(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
