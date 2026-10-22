import os
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar,
    QPlainTextEdit, QFileDialog, QCheckBox, QSpinBox, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt

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


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences & Defaults")
        self.setFixedSize(480, 360)

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

    def save_settings(self):
        config.set("embed_thumbnail", self.chk_thumb.isChecked())
        config.set("embed_metadata", self.chk_meta.isChecked())
        config.set("embed_subtitles", self.chk_sub.isChecked())
        self.accept()
