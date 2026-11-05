import os
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar,
    QPlainTextEdit, QFileDialog, QCheckBox, QSpinBox, QGroupBox, QMessageBox,
    QLineEdit, QFrame
)
from PyQt6.QtCore import Qt
import sys

from app.ffmpeg_manager import get_ffmpeg_status, FFmpegDownloaderThread, BIN_DIR
from app.config import config

class FFmpegDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("FFmpeg Configuration & Diagnostics")
        self.setFixedSize(560, 460)
        self.download_thread = None

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(18, 18, 18, 18)

        # Title
        title_lbl = QLabel("FFmpeg & Codec Environment")
        title_lbl.setStyleSheet("font-size: 15px; font-weight: 700; color: #f0f6fc;")
        layout.addWidget(title_lbl)

        # Info Card
        self.info_box = QGroupBox("Detected Components")
        info_layout = QVBoxLayout(self.info_box)
        info_layout.setSpacing(6)

        self.ffmpeg_path_lbl = QLabel("FFmpeg: Checking...")
        self.ffmpeg_path_lbl.setStyleSheet("color: #8b949e; font-family: Consolas, monospace; font-size: 11px;")
        info_layout.addWidget(self.ffmpeg_path_lbl)

        self.ffprobe_path_lbl = QLabel("FFprobe: Checking...")
        self.ffprobe_path_lbl.setStyleSheet("color: #8b949e; font-family: Consolas, monospace; font-size: 11px;")
        info_layout.addWidget(self.ffprobe_path_lbl)

        self.version_lbl = QLabel("Version: Checking...")
        self.version_lbl.setStyleSheet("color: #3fb950; font-weight: 600; font-size: 12px;")
        info_layout.addWidget(self.version_lbl)

        layout.addWidget(self.info_box)

        # Action Buttons
        btn_layout = QHBoxLayout()
        self.test_btn = QPushButton("Test FFmpeg Execution")
        self.test_btn.clicked.connect(self.run_test)
        btn_layout.addWidget(self.test_btn)

        self.install_btn = QPushButton("Download & Setup Local FFmpeg")
        self.install_btn.setObjectName("accentButton")
        self.install_btn.clicked.connect(self.start_download)
        btn_layout.addWidget(self.install_btn)

        layout.addLayout(btn_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(16)
        layout.addWidget(self.progress_bar)

        # Status output
        self.log_edit = QPlainTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setPlaceholderText("Diagnostic and installation logs will appear here...")
        layout.addWidget(self.log_edit)

        # Close button
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        bottom_layout.addWidget(close_btn)
        layout.addLayout(bottom_layout)

        self.refresh_status()

    def refresh_status(self):
        status = get_ffmpeg_status()
        if status["available"]:
            self.ffmpeg_path_lbl.setText(f"FFmpeg: {status['ffmpeg_path']}")
            self.ffprobe_path_lbl.setText(f"FFprobe: {status['ffprobe_path'] or 'Not found'}")
            self.version_lbl.setText(f"Status: Ready ({status['version']})")
            self.version_lbl.setStyleSheet("color: #3fb950; font-weight: 600; font-size: 12px;")
        else:
            self.ffmpeg_path_lbl.setText("FFmpeg: Not detected in PATH or local bin/")
            self.ffprobe_path_lbl.setText("FFprobe: Not detected")
            self.version_lbl.setText("Status: Missing (Click 'Download & Setup Local FFmpeg' below)")
            self.version_lbl.setStyleSheet("color: #f85149; font-weight: 600; font-size: 12px;")

    def run_test(self):
        status = get_ffmpeg_status()
        if not status["available"]:
            self.log_edit.appendPlainText("Cannot test: FFmpeg executable is not available.")
            return

        self.log_edit.appendPlainText(f"Running test on: {status['ffmpeg_path']}")
        try:
            res = subprocess.run(
                [status["ffmpeg_path"], "-codecs"],
                capture_output=True,
                text=True,
                timeout=5
            )
            sample = "\n".join(res.stdout.splitlines()[:12])
            self.log_edit.appendPlainText(f"Success! Codecs recognized:\n{sample}\n...\n")
        except Exception as e:
            self.log_edit.appendPlainText(f"Error testing FFmpeg: {str(e)}")

    def start_download(self):
        if self.download_thread and self.download_thread.isRunning():
            return

        self.install_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.log_edit.appendPlainText(f"Starting standalone FFmpeg download from official repo to: {BIN_DIR}")

        self.download_thread = FFmpegDownloaderThread(self)
        self.download_thread.progress.connect(self._on_download_progress)
        self.download_thread.finished.connect(self._on_download_finished)
        self.download_thread.start()

    def _on_download_progress(self, pct, msg):
        self.progress_bar.setValue(pct)
        self.log_edit.appendPlainText(msg)

    def _on_download_finished(self, success, msg):
        self.install_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.log_edit.appendPlainText(msg)
        self.refresh_status()
        if success:
            QMessageBox.information(self, "FFmpeg Installed", "FFmpeg binaries installed successfully!")


class DownloadCompletedDialog(QDialog):
    """
    Polished Dark-Themed Completion Dialog
    Replaces ugly/unreadable standard QMessageBox popups.
    """
    def __init__(self, successful: int, failed: int, output_dir: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Download Finished")
        self.setFixedSize(480, 260)
        self.output_dir = output_dir

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(22, 20, 22, 20)

        # Header with icon and title
        header = QHBoxLayout()
        header.setSpacing(12)

        icon_lbl = QLabel("✓" if failed == 0 else "ℹ")
        icon_lbl.setFixedSize(38, 38)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bg_col = "#1b4b27" if failed == 0 else "#2d333b"
        border_col = "#238636" if failed == 0 else "#58a6ff"
        text_col = "#3fb950" if failed == 0 else "#58a6ff"
        icon_lbl.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_col};
                color: {text_col};
                border: 2px solid {border_col};
                border-radius: 19px;
                font-size: 20px;
                font-weight: bold;
            }}
        """)
        header.addWidget(icon_lbl)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        main_title = QLabel("Batch Download Completed" if failed == 0 else "Download Finished with Notices")
        main_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #f0f6fc;")
        title_box.addWidget(main_title)

        sub_title = QLabel(f"Processed batch to destination folder")
        sub_title.setStyleSheet("color: #8b949e; font-size: 12px;")
        title_box.addWidget(sub_title)

        header.addLayout(title_box)
        header.addStretch()
        layout.addLayout(header)

        # Stats Card
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        stats_layout = QVBoxLayout(stats_frame)
        stats_layout.setContentsMargins(12, 10, 12, 10)
        stats_layout.setSpacing(6)

        stat_row = QHBoxLayout()
        succ_lbl = QLabel(f"Successfully downloaded: {successful} files")
        succ_lbl.setStyleSheet("color: #3fb950; font-weight: 600; font-size: 13px;")
        stat_row.addWidget(succ_lbl)

        if failed > 0:
            fail_lbl = QLabel(f"• Failed: {failed}")
            fail_lbl.setStyleSheet("color: #f85149; font-weight: 600; font-size: 13px;")
            stat_row.addWidget(fail_lbl)
        stat_row.addStretch()
        stats_layout.addLayout(stat_row)

        dir_lbl = QLabel(f"Destination: {self.output_dir}")
        dir_lbl.setStyleSheet("color: #8b949e; font-size: 11px; font-family: Consolas, monospace;")
        dir_lbl.setWordWrap(True)
        stats_layout.addWidget(dir_lbl)

        layout.addWidget(stats_frame)

        # Bottom Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.close_btn = QPushButton("Done")
        self.close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.close_btn)

        self.open_folder_btn = QPushButton("Open Folder")
        self.open_folder_btn.setObjectName("primaryButton")
        self.open_folder_btn.clicked.connect(self.open_folder)
        btn_layout.addWidget(self.open_folder_btn)

        layout.addLayout(btn_layout)

    def open_folder(self):
        if os.path.exists(self.output_dir):
            if sys.platform == "win32":
                os.startfile(self.output_dir)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", self.output_dir])
            else:
                subprocess.Popen(["xdg-open", self.output_dir])
        self.accept()


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences & Defaults")
        self.setFixedSize(520, 420)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(18, 18, 18, 18)

        # Title
        title_lbl = QLabel("Application Settings")
        title_lbl.setStyleSheet("font-size: 15px; font-weight: 700; color: #f0f6fc;")
        layout.addWidget(title_lbl)

        # Options group
        group = QGroupBox("Download Preferences")
        g_layout = QVBoxLayout(group)
        g_layout.setSpacing(10)

        self.chk_thumb = QCheckBox("Embed album art / thumbnail into media files")
        self.chk_thumb.setChecked(config.get("embed_thumbnail", True))
        g_layout.addWidget(self.chk_thumb)

        self.chk_meta = QCheckBox("Embed artist, title, and playlist metadata tags")
        self.chk_meta.setChecked(config.get("embed_metadata", True))
        g_layout.addWidget(self.chk_meta)

        self.chk_sub = QCheckBox("Download and embed subtitles (when available)")
        self.chk_sub.setChecked(config.get("embed_subtitles", False))
        g_layout.addWidget(self.chk_sub)

        layout.addWidget(group)

        # Custom FFmpeg Path Group
        ffmpeg_grp = QGroupBox("Custom FFmpeg Executable (Optional)")
        f_layout = QHBoxLayout(ffmpeg_grp)
        f_layout.setSpacing(8)

        self.ffmpeg_input = QLineEdit()
        self.ffmpeg_input.setPlaceholderText("Leave blank to use auto-detected / local FFmpeg")
        self.ffmpeg_input.setText(config.get("custom_ffmpeg_path", ""))
        f_layout.addWidget(self.ffmpeg_input)

        browse_ff_btn = QPushButton("Browse...")
        browse_ff_btn.clicked.connect(self.browse_ffmpeg)
        f_layout.addWidget(browse_ff_btn)

        layout.addWidget(ffmpeg_grp)

        # Bottom buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def browse_ffmpeg(self):
        filter_str = "Executable (*.exe);;All Files (*)" if sys.platform == "win32" else "All Files (*)"
        chosen, _ = QFileDialog.getOpenFileName(self, "Select FFmpeg Binary", "", filter_str)
        if chosen:
            self.ffmpeg_input.setText(chosen)

    def save_settings(self):
        config.set("embed_thumbnail", self.chk_thumb.isChecked())
        config.set("embed_metadata", self.chk_meta.isChecked())
        config.set("embed_subtitles", self.chk_sub.isChecked())
        config.set("custom_ffmpeg_path", self.ffmpeg_input.text().strip())
        self.accept()
