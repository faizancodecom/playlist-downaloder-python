import os
import sys
import subprocess
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QFileDialog, QScrollArea, QFrame, QProgressBar,
    QPlainTextEdit, QMessageBox, QApplication, QButtonGroup, QRadioButton
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QKeySequence, QShortcut

from app.config import config
from app.ffmpeg_manager import get_ffmpeg_status
from app.downloader import PlaylistFetchWorker, PlaylistDownloadWorker, format_duration
from app.ui.video_card import VideoCard
from app.ui.thumbnail_loader import ThumbnailLoader
from app.ui.dialogs import FFmpegDialog, SettingsDialog
from app.ui.styles import DARK_STYLESHEET

VIDEO_FORMATS = ["mp4", "mkv", "webm", "avi", "mov"]
VIDEO_QUALITIES = [
    ("Best Available", "best"),
    ("4K Ultra HD (2160p)", "2160p"),
    ("2K Quad HD (1440p)", "1440p"),
    ("Full HD (1080p)", "1080p"),
    ("HD (720p)", "720p"),
    ("SD (480p)", "480p"),
    ("Low (360p)", "360p")
]

AUDIO_FORMATS = ["flac", "mp3", "m4a", "wav", "opus", "ogg"]

AUDIO_QUALITIES_MAP = {
    "flac": [
        ("Hi-Res Studio Master (> 3200 kbps / 24-bit 96kHz)", "3200"),
        ("Ultra Lossless (3000+ kbps / Fast Level 0)", "3000"),
        ("Lossless CD Quality (1411 kbps / 16-bit)", "1411"),
        ("Best Available Lossless (Source Quality)", "best"),
    ],
    "wav": [
        ("32-bit Float Master (> 3000 kbps / 96kHz WAV)", "3200"),
        ("24-bit Studio (2304 kbps / 48kHz WAV)", "2304"),
        ("16-bit CD Quality (1411 kbps WAV)", "1411"),
        ("Best Source WAV", "best"),
    ],
    "default": [
        ("320 kbps (Extreme Quality)", "320"),
        ("256 kbps (Very Good)", "256"),
        ("192 kbps (Standard)", "192"),
        ("128 kbps (Compact)", "128"),
        ("Best Source Audio", "best"),
    ]
}



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Professional Playlist & Media Downloader")
        self.resize(1020, 820)
        self.setMinimumSize(880, 680)

        self.setStyleSheet(DARK_STYLESHEET)

        self.cards = []
        self.current_playlist_info = None
        self.fetch_worker = None
        self.download_worker = None
        self.thumbnail_loader = ThumbnailLoader(self)
        self.thumbnail_loader.thumbnail_loaded.connect(self._on_thumbnail_loaded)

        self._init_ui()
        self._update_ffmpeg_indicator()

        # Keyboard shortcuts
        QShortcut(QKeySequence("Ctrl+V"), self, self.paste_clipboard)
        QShortcut(QKeySequence("Return"), self, self.start_fetch)

    def _init_ui(self):
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(18, 16, 18, 14)
        main_layout.setSpacing(12)

        # 1. Top Header & App Bar
        top_bar = QHBoxLayout()
        top_bar.setSpacing(12)

        app_title = QLabel("Playlist Downloader")
        app_title.setStyleSheet("font-size: 18px; font-weight: 700; color: #f0f6fc; letter-spacing: 0.5px;")
        top_bar.addWidget(app_title)

        app_subtitle = QLabel("High-Performance Audio & Video Extraction")
        app_subtitle.setStyleSheet("color: #8b949e; font-size: 12px; margin-top: 4px;")
        top_bar.addWidget(app_subtitle)

        top_bar.addStretch()

        # FFmpeg status badge button
        self.ffmpeg_btn = QPushButton("Checking FFmpeg...")
        self.ffmpeg_btn.setStyleSheet("""
            QPushButton {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 12px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton:hover {
                border-color: #58a6ff;
            }
        """)
        self.ffmpeg_btn.clicked.connect(self.open_ffmpeg_dialog)
        top_bar.addWidget(self.ffmpeg_btn)

        # Preferences button
        self.settings_btn = QPushButton("Preferences")
        self.settings_btn.setStyleSheet("padding: 4px 12px; font-size: 12px;")
        self.settings_btn.clicked.connect(self.open_settings_dialog)
        top_bar.addWidget(self.settings_btn)

        main_layout.addLayout(top_bar)

        # 2. URL Input Panel
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 8px;
            }
        """)
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(12, 10, 12, 10)
        input_layout.setSpacing(10)

        url_label = QLabel("URL:")
        url_label.setStyleSheet("color: #8b949e; font-weight: 600; border: none; background: transparent;")
        input_layout.addWidget(url_label)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube Playlist or Video URL (e.g., https://www.youtube.com/playlist?list=...)")
        self.url_input.setClearButtonEnabled(True)
        input_layout.addWidget(self.url_input, stretch=1)

        self.paste_btn = QPushButton("Paste")
        self.paste_btn.clicked.connect(self.paste_clipboard)
        input_layout.addWidget(self.paste_btn)

        self.fetch_btn = QPushButton("Fetch Playlist")
        self.fetch_btn.setObjectName("accentButton")
        self.fetch_btn.clicked.connect(self.start_fetch)
        input_layout.addWidget(self.fetch_btn)

        main_layout.addWidget(input_frame)

        # 3. Format, Quality & Output Configuration Bar
        config_frame = QFrame()
        config_frame.setStyleSheet("""
            QFrame {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 8px;
            }
            QLabel {
                border: none;
                background: transparent;
            }
        """)
        config_layout = QVBoxLayout(config_frame)
        config_layout.setContentsMargins(14, 12, 14, 12)
        config_layout.setSpacing(10)

        # Row 1: Mode, Format, and Quality Selectors
        row1 = QHBoxLayout()
        row1.setSpacing(16)

        # Media Type Radio Buttons (Video vs Audio)
        type_box = QHBoxLayout()
        type_box.setSpacing(10)
        type_lbl = QLabel("Mode:")
        type_lbl.setStyleSheet("color: #c9d1d9; font-weight: 600; font-size: 13px;")
        type_box.addWidget(type_lbl)

        self.mode_group = QButtonGroup(self)
        self.radio_video = QRadioButton("Video")
        self.radio_audio = QRadioButton("Audio (Music)")
        
        radio_style = """
            QRadioButton {
                color: #f0f6fc;
                font-size: 13px;
                font-weight: 500;
                spacing: 6px;
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
        """
        self.radio_video.setStyleSheet(radio_style)
        self.radio_audio.setStyleSheet(radio_style)
        self.radio_video.setCursor(Qt.CursorShape.PointingHandCursor)
        self.radio_audio.setCursor(Qt.CursorShape.PointingHandCursor)

        self.mode_group.addButton(self.radio_video)
        self.mode_group.addButton(self.radio_audio)

        initial_media_type = config.get("media_type", "video")
        if initial_media_type == "audio":
            self.radio_audio.setChecked(True)
        else:
            self.radio_video.setChecked(True)

        self.radio_video.toggled.connect(self._on_media_mode_changed)
        self.radio_audio.toggled.connect(self._on_media_mode_changed)
        type_box.addWidget(self.radio_video)
        type_box.addWidget(self.radio_audio)
        row1.addLayout(type_box)

        # Format Dropdown
        fmt_box = QHBoxLayout()
        fmt_box.setSpacing(6)
        self.format_label = QLabel("Format:")
        self.format_label.setStyleSheet("color: #c9d1d9; font-weight: 600; font-size: 13px;")
        fmt_box.addWidget(self.format_label)

        self.format_combo = QComboBox()
        self.format_combo.setFixedWidth(110)
        self.format_combo.currentIndexChanged.connect(self._on_format_changed)
        fmt_box.addWidget(self.format_combo)
        row1.addLayout(fmt_box)

        # Quality Dropdown
        qual_box = QHBoxLayout()
        qual_box.setSpacing(6)
        self.qual_label = QLabel("Quality:")
        self.qual_label.setStyleSheet("color: #c9d1d9; font-weight: 600; font-size: 13px;")
        qual_box.addWidget(self.qual_label)

        self.qual_combo = QComboBox()
        self.qual_combo.setMinimumWidth(320)
        qual_box.addWidget(self.qual_combo)
        row1.addLayout(qual_box)

        row1.addStretch()
        config_layout.addLayout(row1)

        # Row 2: Destination Folder Controls
        row2 = QHBoxLayout()
        row2.setSpacing(10)

        dir_lbl = QLabel("Save to:")
        dir_lbl.setStyleSheet("color: #c9d1d9; font-weight: 600; font-size: 13px;")
        row2.addWidget(dir_lbl)

        self.dir_input = QLineEdit()
        self.dir_input.setText(config.get("output_dir"))
        self.dir_input.setReadOnly(True)
        row2.addWidget(self.dir_input, stretch=1)

        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.setStyleSheet("padding: 7px 18px;")
        self.browse_btn.clicked.connect(self.browse_output_dir)
        row2.addWidget(self.browse_btn)

        self.open_dir_btn = QPushButton("Open Folder")
        self.open_dir_btn.setStyleSheet("padding: 7px 18px;")
        self.open_dir_btn.setToolTip("Open destination folder in File Explorer")
        self.open_dir_btn.clicked.connect(self.open_output_dir)
        row2.addWidget(self.open_dir_btn)

        config_layout.addLayout(row2)

        main_layout.addWidget(config_frame)

        # Initialize dropdowns based on active mode
        self._populate_format_dropdowns()

        # 4. Playlist Selection Header & Filtering
        playlist_toolbar = QHBoxLayout()
        playlist_toolbar.setSpacing(10)

        self.playlist_info_lbl = QLabel("No playlist loaded.")
        self.playlist_info_lbl.setStyleSheet("color: #f0f6fc; font-weight: 600; font-size: 13px;")
        playlist_toolbar.addWidget(self.playlist_info_lbl)

        playlist_toolbar.addStretch()

        # Selection buttons
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(lambda: self.set_all_selected(True))
        playlist_toolbar.addWidget(self.select_all_btn)

        self.deselect_all_btn = QPushButton("Deselect All")
        self.deselect_all_btn.clicked.connect(lambda: self.set_all_selected(False))
        playlist_toolbar.addWidget(self.deselect_all_btn)

        self.invert_sel_btn = QPushButton("Invert")
        self.invert_sel_btn.clicked.connect(self.invert_selection)
        playlist_toolbar.addWidget(self.invert_sel_btn)

        # Filter input
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter videos...")
        self.filter_input.setFixedWidth(160)
        self.filter_input.textChanged.connect(self.filter_items)
        playlist_toolbar.addWidget(self.filter_input)

        # Selection counter
        self.selection_count_lbl = QLabel("0 selected")
        self.selection_count_lbl.setStyleSheet("""
            color: #58a6ff;
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 4px;
            padding: 4px 10px;
            font-size: 12px;
            font-weight: 600;
        """)
        playlist_toolbar.addWidget(self.selection_count_lbl)

        main_layout.addLayout(playlist_toolbar)

        # 5. Video Items Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("scrollContent")
        self.scroll_content.setStyleSheet("background-color: #0d1117;")
        self.cards_layout = QVBoxLayout(self.scroll_content)
        self.cards_layout.setContentsMargins(4, 4, 4, 4)
        self.cards_layout.setSpacing(6)
        self.cards_layout.addStretch()

        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area, stretch=1)

        # 6. Bottom Progress & Download Action Bar
        bottom_frame = QFrame()
        bottom_frame.setStyleSheet("""
            QFrame {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 8px;
            }
        """)
        bottom_layout = QVBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(14, 12, 14, 12)
        bottom_layout.setSpacing(8)

        # Progress bar & overall status row
        stat_row = QHBoxLayout()
        self.overall_status_lbl = QLabel("Ready to download")
        self.overall_status_lbl.setStyleSheet("color: #8b949e; font-weight: 500; font-size: 12px; border: none;")
        stat_row.addWidget(self.overall_status_lbl)

        stat_row.addStretch()

        self.overall_speed_lbl = QLabel("")
        self.overall_speed_lbl.setStyleSheet("color: #58a6ff; font-family: Consolas, monospace; font-size: 12px; border: none;")
        stat_row.addWidget(self.overall_speed_lbl)

        bottom_layout.addLayout(stat_row)

        self.overall_progress_bar = QProgressBar()
        self.overall_progress_bar.setValue(0)
        self.overall_progress_bar.setFixedHeight(12)
        self.overall_progress_bar.setTextVisible(False)
        bottom_layout.addWidget(self.overall_progress_bar)

        # Buttons row
        action_row = QHBoxLayout()
        action_row.setSpacing(10)

        self.log_toggle_btn = QPushButton("Show Activity Log")
        self.log_toggle_btn.clicked.connect(self.toggle_log_drawer)
        action_row.addWidget(self.log_toggle_btn)

        action_row.addStretch()

        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self.toggle_pause_download)
        action_row.addWidget(self.pause_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("dangerButton")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_download)
        action_row.addWidget(self.cancel_btn)

        self.download_btn = QPushButton("Download Selected")
        self.download_btn.setObjectName("primaryButton")
        self.download_btn.setEnabled(False)
        self.download_btn.clicked.connect(self.start_download)
        action_row.addWidget(self.download_btn)

        bottom_layout.addLayout(action_row)

        # Terminal / Log drawer (hidden by default)
        self.log_console = QPlainTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setMaximumHeight(140)
        self.log_console.setVisible(False)
        bottom_layout.addWidget(self.log_console)

        main_layout.addWidget(bottom_frame)

    def _update_ffmpeg_indicator(self):
        status = get_ffmpeg_status()
        if status["available"]:
            ver_text = status.get("version", "Active")
            self.ffmpeg_btn.setText(f"FFmpeg: {ver_text}")
            self.ffmpeg_btn.setStyleSheet("""
                QPushButton {
                    background-color: #102a18;
                    color: #3fb950;
                    border: 1px solid #238636;
                    border-radius: 12px;
                    padding: 4px 12px;
                    font-size: 11px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #1b4b27;
                }
            """)
        else:
            self.ffmpeg_btn.setText("FFmpeg: Missing (Click to setup)")
            self.ffmpeg_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3d1517;
                    color: #f85149;
                    border: 1px solid #da3633;
                    border-radius: 12px;
                    padding: 4px 12px;
                    font-size: 11px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #5c1e22;
                }
            """)

    def _on_media_mode_changed(self, *args):
        self._populate_format_dropdowns()

    def _on_format_changed(self, *args):
        if not self.radio_audio.isChecked():
            return
        cur_fmt = self.format_combo.currentData() or "flac"
        qualities = AUDIO_QUALITIES_MAP.get(cur_fmt.lower(), AUDIO_QUALITIES_MAP["default"])

        self.qual_combo.blockSignals(True)
        cur_val = self.qual_combo.currentData()
        self.qual_combo.clear()
        for label, val in qualities:
            self.qual_combo.addItem(label, val)

        idx = self.qual_combo.findData(cur_val)
        if idx >= 0:
            self.qual_combo.setCurrentIndex(idx)
        else:
            self.qual_combo.setCurrentIndex(0)
        self.qual_combo.blockSignals(False)

    def _populate_format_dropdowns(self):
        self.format_combo.blockSignals(True)
        self.qual_combo.blockSignals(True)
        self.format_combo.clear()
        self.qual_combo.clear()

        if self.radio_video.isChecked():
            # Video Mode
            for fmt in VIDEO_FORMATS:
                self.format_combo.addItem(fmt.upper(), fmt)
            for label, val in VIDEO_QUALITIES:
                self.qual_combo.addItem(label, val)

            # Restore saved defaults
            cur_fmt = config.get("video_format", "mp4").lower()
            idx = self.format_combo.findData(cur_fmt)
            if idx >= 0:
                self.format_combo.setCurrentIndex(idx)

            cur_qual = config.get("video_quality", "best")
            idx = self.qual_combo.findData(cur_qual)
            if idx >= 0:
                self.qual_combo.setCurrentIndex(idx)
        else:
            # Audio Mode
            for fmt in AUDIO_FORMATS:
                self.format_combo.addItem(fmt.upper(), fmt)

            cur_fmt = config.get("audio_format", "flac").lower()
            idx = self.format_combo.findData(cur_fmt)
            if idx >= 0:
                self.format_combo.setCurrentIndex(idx)
            else:
                self.format_combo.setCurrentIndex(0)

            chosen_fmt = self.format_combo.currentData() or "flac"
            qualities = AUDIO_QUALITIES_MAP.get(chosen_fmt.lower(), AUDIO_QUALITIES_MAP["default"])
            for label, val in qualities:
                self.qual_combo.addItem(label, val)

            cur_qual = config.get("audio_quality", "3200")
            idx = self.qual_combo.findData(cur_qual)
            if idx >= 0:
                self.qual_combo.setCurrentIndex(idx)
            else:
                self.qual_combo.setCurrentIndex(0)

        self.format_combo.blockSignals(False)
        self.qual_combo.blockSignals(False)

    def paste_clipboard(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        if text:
            self.url_input.setText(text)
            self.start_fetch()

    def browse_output_dir(self):
        cur = self.dir_input.text() or str(Path.home())
        chosen = QFileDialog.getExistingDirectory(self, "Select Destination Folder", cur)
        if chosen:
            self.dir_input.setText(chosen)
            config.set("output_dir", chosen)

    def open_output_dir(self):
        path = self.dir_input.text()
        if os.path.exists(path):
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        else:
            QMessageBox.warning(self, "Folder Not Found", f"The directory does not exist:\n{path}")

    def open_ffmpeg_dialog(self):
        dlg = FFmpegDialog(self)
        dlg.exec()
        self._update_ffmpeg_indicator()

    def open_settings_dialog(self):
        dlg = SettingsDialog(self)
        dlg.exec()

    def toggle_log_drawer(self):
        vis = not self.log_console.isVisible()
        self.log_console.setVisible(vis)
        self.log_toggle_btn.setText("Hide Activity Log" if vis else "Show Activity Log")

    def append_log(self, text: str):
        self.log_console.appendPlainText(text)

    # ---------------- Fetching Logic ----------------

    def start_fetch(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.information(self, "Missing URL", "Please enter or paste a playlist or video URL.")
            return

        # Clear existing cards
        self._clear_cards()
        self.playlist_info_lbl.setText("Extracting playlist metadata...")
        self.fetch_btn.setEnabled(False)
        self.fetch_btn.setText("Loading...")
        self.download_btn.setEnabled(False)
        self.append_log(f"Fetching: {url}")

        self.fetch_worker = PlaylistFetchWorker(url, self)
        self.fetch_worker.item_fetched.connect(self._on_item_fetched)
        self.fetch_worker.fetch_finished.connect(self._on_fetch_finished)
        self.fetch_worker.fetch_error.connect(self._on_fetch_error)
        self.fetch_worker.log_message.connect(self.append_log)
        self.fetch_worker.start()

    def _clear_cards(self):
        for card in self.cards:
            card.setParent(None)
            card.deleteLater()
        self.cards.clear()
        self.update_selection_counter()

    def _on_item_fetched(self, item_data: dict):
        card = VideoCard(item_data, self.scroll_content)
        card.selection_changed.connect(self.update_selection_counter)
        self.cards.append(card)
        # Insert before the stretch
        self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)
        
        # Load thumbnail asynchronously
        thumb_url = item_data.get("thumbnail_url")
        if thumb_url:
            self.thumbnail_loader.load_thumbnail(item_data["id"], thumb_url)
        
        self.update_selection_counter()

    def _on_thumbnail_loaded(self, video_id: str, pixmap):
        for card in self.cards:
            if card.item_id == video_id:
                card.set_thumbnail(pixmap)
                break

    def _on_fetch_finished(self, playlist_info: dict, items: list):
        self.current_playlist_info = playlist_info
        self.fetch_btn.setEnabled(True)
        self.fetch_btn.setText("Fetch Playlist")

        title = playlist_info.get("title", "Playlist")
        total = len(items)
        uploader = playlist_info.get("uploader", "")
        
        info_text = f"{title}"
        if uploader:
            info_text += f" • {uploader}"
        info_text += f" ({total} items)"
        self.playlist_info_lbl.setText(info_text)

        self.update_selection_counter()

    def _on_fetch_error(self, err_msg: str):
        self.fetch_btn.setEnabled(True)
        self.fetch_btn.setText("Fetch Playlist")
        self.playlist_info_lbl.setText("Failed to load playlist.")
        QMessageBox.critical(self, "Extraction Error", f"Unable to fetch playlist:\n{err_msg}")

    # ---------------- Selection Controls ----------------

    def set_all_selected(self, select: bool):
        for card in self.cards:
            if card.isVisible():
                card.set_selected(select)
        self.update_selection_counter()

    def invert_selection(self):
        for card in self.cards:
            if card.isVisible():
                card.set_selected(not card.is_selected())
        self.update_selection_counter()

    def filter_items(self, query: str):
        for card in self.cards:
            visible = card.matches_filter(query)
            card.setVisible(visible)
        self.update_selection_counter()

    def update_selection_counter(self):
        visible_cards = [c for c in self.cards if c.isVisible()]
        selected_cards = [c for c in visible_cards if c.is_selected()]
        
        tot_vis = len(visible_cards)
        tot_sel = len(selected_cards)
        
        total_duration = sum(c.item.get("duration_sec", 0) for c in selected_cards)
        dur_str = format_duration(total_duration) if total_duration > 0 else ""

        if dur_str:
            self.selection_count_lbl.setText(f"{tot_sel} of {tot_vis} selected ({dur_str})")
        else:
            self.selection_count_lbl.setText(f"{tot_sel} of {tot_vis} selected")

        self.download_btn.setEnabled(tot_sel > 0 and (self.download_worker is None or not self.download_worker.isRunning()))
        self.download_btn.setText(f"Download Selected ({tot_sel})" if tot_sel > 0 else "Download Selected")

    # ---------------- Download Execution ----------------

    def start_download(self):
        selected_cards = [c for c in self.cards if c.is_selected()]
        if not selected_cards:
            QMessageBox.information(self, "No Videos Selected", "Please select at least one video to download.")
            return

        items_to_download = [c.item for c in selected_cards]
        out_dir = self.dir_input.text().strip()
        if not out_dir:
            out_dir = config.get("output_dir")
            self.dir_input.setText(out_dir)

        media_type = "video" if self.radio_video.isChecked() else "audio"
        chosen_fmt = self.format_combo.currentData()
        chosen_qual = self.qual_combo.currentData()

        # Save active choices into config
        config.set("media_type", media_type)
        if media_type == "video":
            config.set("video_format", chosen_fmt)
            config.set("video_quality", chosen_qual)
        else:
            config.set("audio_format", chosen_fmt)
            config.set("audio_quality", chosen_qual)

        download_opts = {
            "output_dir": out_dir,
            "media_type": media_type,
            "video_format": chosen_fmt,
            "video_quality": chosen_qual,
            "audio_format": chosen_fmt,
            "audio_quality": chosen_qual,
            "embed_thumbnail": config.get("embed_thumbnail", True),
            "embed_metadata": config.get("embed_metadata", True),
            "number_files": len(items_to_download) > 1
        }

        # UI state during download
        self.download_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.pause_btn.setEnabled(True)
        self.pause_btn.setText("Pause")
        self.fetch_btn.setEnabled(False)
        self.overall_progress_bar.setValue(0)
        self.overall_status_lbl.setText(f"Preparing batch of {len(items_to_download)} items...")

        self.download_worker = PlaylistDownloadWorker(items_to_download, download_opts, self)
        self.download_worker.overall_progress.connect(self._on_overall_progress)
        self.download_worker.item_started.connect(self._on_item_download_started)
        self.download_worker.item_progress.connect(self._on_item_download_progress)
        self.download_worker.item_completed.connect(self._on_item_download_completed)
        self.download_worker.item_failed.connect(self._on_item_download_failed)
        self.download_worker.all_completed.connect(self._on_all_downloads_completed)
        self.download_worker.log_message.connect(self.append_log)
        self.download_worker.start()

    def toggle_pause_download(self):
        if not self.download_worker:
            return
        if self.download_worker.is_paused():
            self.download_worker.resume()
            self.pause_btn.setText("Pause")
            self.overall_status_lbl.setText("Resuming download queue...")
        else:
            self.download_worker.pause()
            self.pause_btn.setText("Resume")
            self.overall_status_lbl.setText("Downloads paused.")

    def cancel_download(self):
        if self.download_worker and self.download_worker.isRunning():
            reply = QMessageBox.question(
                self, "Cancel Download",
                "Are you sure you want to cancel the current download process?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.download_worker.cancel()
                self.cancel_btn.setEnabled(False)
                self.overall_status_lbl.setText("Cancelling downloads...")

    def _on_overall_progress(self, idx: int, total: int, percent: int):
        self.overall_progress_bar.setValue(percent)
        self.overall_status_lbl.setText(f"Processing item {idx} of {total} ({percent}%)")

    def _on_item_download_started(self, item_id: str, idx: int, title: str):
        for card in self.cards:
            if card.item_id == item_id:
                card.status_badge.setText("Starting...")
                break

    def _on_item_download_progress(self, item_id: str, data: dict):
        for card in self.cards:
            if card.item_id == item_id:
                card.set_progress(data)
                break
        
        speed = data.get("speed_str", "")
        eta = data.get("eta_str", "")
        if speed or eta:
            self.overall_speed_lbl.setText(f"{speed} | ETA: {eta}")

    def _on_item_download_completed(self, item_id: str, filename: str):
        for card in self.cards:
            if card.item_id == item_id:
                card.set_completed(filename)
                break

    def _on_item_download_failed(self, item_id: str, error_msg: str):
        for card in self.cards:
            if card.item_id == item_id:
                card.set_failed(error_msg)
                break

    def _on_all_downloads_completed(self, successful: int, failed: int):
        self.download_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)
        self.fetch_btn.setEnabled(True)
        self.overall_speed_lbl.setText("")
        self.overall_progress_bar.setValue(100)

        status_msg = f"Completed: {successful} succeeded"
        if failed > 0:
            status_msg += f", {failed} failed"
        self.overall_status_lbl.setText(status_msg)

        QMessageBox.information(
            self,
            "Download Finished",
            f"Batch download completed!\n\nSuccessfully downloaded: {successful}\nFailed: {failed}\n\nFiles saved in:\n{self.dir_input.text()}"
        )
        self.update_selection_counter()
