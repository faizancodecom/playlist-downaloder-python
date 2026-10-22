from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QCheckBox, QProgressBar, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath

class VideoCard(QFrame):
    selection_changed = pyqtSignal(bool)

    def __init__(self, item_data: dict, parent=None):
        super().__init__(parent)
        self.item = item_data
        self.item_id = item_data["id"]
        self._is_completed = False
        self._is_failed = False
        
        self.setObjectName("videoCard")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(84)
        
        self.setStyleSheet("""
            QFrame#videoCard {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 6px;
            }
            QFrame#videoCard:hover {
                border-color: #484f58;
                background-color: #1a202c;
            }
            QLabel {
                background: transparent;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 12, 8)
        layout.setSpacing(12)

        # Checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(item_data.get("selected", True))
        self.checkbox.stateChanged.connect(self._on_check_changed)
        layout.addWidget(self.checkbox)

        # Index label
        self.index_lbl = QLabel(f"#{item_data.get('index', 1):02d}")
        self.index_lbl.setFixedWidth(28)
        self.index_lbl.setStyleSheet("color: #6e7681; font-size: 11px; font-weight: 600;")
        layout.addWidget(self.index_lbl)

        # Thumbnail Label
        self.thumb_lbl = QLabel()
        self.thumb_lbl.setFixedSize(110, 62)
        self.thumb_lbl.setStyleSheet("""
            QLabel {
                background-color: #0d1117;
                border: 1px solid #21262d;
                border-radius: 4px;
            }
        """)
        self.thumb_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._set_default_thumbnail()
        layout.addWidget(self.thumb_lbl)

        # Middle Info Area
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 2, 0, 2)
        info_layout.setSpacing(4)

        # Title
        raw_title = item_data.get("title", "Untitled Video")
        self.title_lbl = QLabel(raw_title)
        self.title_lbl.setStyleSheet("color: #f0f6fc; font-weight: 600; font-size: 13px;")
        self.title_lbl.setToolTip(raw_title)
        info_layout.addWidget(self.title_lbl)

        # Meta Row: Channel + Duration
        meta_row = QHBoxLayout()
        meta_row.setSpacing(10)
        
        uploader = item_data.get("uploader", "Unknown Artist")
        self.uploader_lbl = QLabel(uploader)
        self.uploader_lbl.setStyleSheet("color: #8b949e; font-size: 11px;")
        meta_row.addWidget(self.uploader_lbl)

        duration_str = item_data.get("duration_str", "--:--")
        self.duration_lbl = QLabel(duration_str)
        self.duration_lbl.setStyleSheet("""
            QLabel {
                color: #58a6ff;
                background-color: #0d1117;
                padding: 1px 6px;
                border: 1px solid #21262d;
                border-radius: 3px;
                font-size: 11px;
                font-family: Consolas, monospace;
            }
        """)
        meta_row.addWidget(self.duration_lbl)
        meta_row.addStretch()

        info_layout.addLayout(meta_row)

        # Progress bar (hidden until downloading)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #0d1117;
                border: 1px solid #21262d;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: #238636;
                border-radius: 2px;
            }
        """)
        info_layout.addWidget(self.progress_bar)

        layout.addLayout(info_layout, stretch=1)

        # Right Status / Metrics Area
        status_layout = QVBoxLayout()
        status_layout.setContentsMargins(0, 2, 0, 2)
        status_layout.setSpacing(4)
        status_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # Status Badge
        self.status_badge = QLabel("Ready")
        self.status_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_badge.setStyleSheet(self._badge_style("#30363d", "#8b949e"))
        status_layout.addWidget(self.status_badge)

        # Metrics label (Speed / ETA / Size)
        self.metrics_lbl = QLabel("")
        self.metrics_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.metrics_lbl.setStyleSheet("color: #6e7681; font-size: 11px; font-family: Consolas, monospace;")
        status_layout.addWidget(self.metrics_lbl)

        layout.addLayout(status_layout)

    def _badge_style(self, border_color, text_color, bg_color="#0d1117"):
        return f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 3px 8px;
                font-size: 11px;
                font-weight: 600;
            }}
        """

    def _set_default_thumbnail(self):
        pixmap = QPixmap(110, 62)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.fillRect(0, 0, 110, 62, Qt.GlobalColor.black)
        painter.setPen(Qt.GlobalColor.darkGray)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "Loading...")
        painter.end()
        self.thumb_lbl.setPixmap(pixmap)

    def set_thumbnail(self, pixmap: QPixmap):
        if pixmap and not pixmap.isNull():
            scaled = pixmap.scaled(
                110, 62,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            # Crop to exact 110x62
            cropped = scaled.copy(
                max(0, (scaled.width() - 110) // 2),
                max(0, (scaled.height() - 62) // 2),
                110, 62
            )
            self.thumb_lbl.setPixmap(cropped)

    def _on_check_changed(self, state):
        is_chk = (state == Qt.CheckState.Checked.value or state == 2)
        self.item["selected"] = is_chk
        self.selection_changed.emit(is_chk)

    def set_selected(self, selected: bool):
        self.checkbox.setChecked(selected)
        self.item["selected"] = selected

    def is_selected(self) -> bool:
        return self.checkbox.isChecked()

    def set_progress(self, data: dict):
        self.progress_bar.setVisible(True)
        pct = data.get("percent", 0)
        self.progress_bar.setValue(pct)
        
        status_str = data.get("status", "Downloading")
        if "converting" in status_str.lower() or "processing" in status_str.lower():
            self.status_badge.setText("Processing")
            self.status_badge.setStyleSheet(self._badge_style("#388bfd", "#58a6ff"))
            self.metrics_lbl.setText("Muxing audio/video...")
        else:
            self.status_badge.setText(f"{pct}%")
            self.status_badge.setStyleSheet(self._badge_style("#1f6feb", "#58a6ff"))
            
            speed = data.get("speed_str", "")
            eta = data.get("eta_str", "")
            done = data.get("downloaded_str", "")
            tot = data.get("total_str", "")
            
            parts = []
            if done and tot:
                parts.append(f"{done}/{tot}")
            if speed and speed != "-- KB/s":
                parts.append(speed)
            if eta and eta != "--:--":
                parts.append(f"ETA: {eta}")
            self.metrics_lbl.setText(" | ".join(parts))

    def set_completed(self, filename: str):
        self._is_completed = True
        self.progress_bar.setVisible(False)
        self.status_badge.setText("Completed")
        self.status_badge.setStyleSheet(self._badge_style("#238636", "#3fb950"))
        self.metrics_lbl.setText("Finished")

    def set_failed(self, error_msg: str):
        self._is_failed = True
        self.progress_bar.setVisible(False)
        self.status_badge.setText("Failed")
        self.status_badge.setStyleSheet(self._badge_style("#da3633", "#f85149"))
        self.metrics_lbl.setText("Error occurred")
        self.setToolTip(error_msg)

    def matches_filter(self, query: str) -> bool:
        if not query:
            return True
        q = query.lower()
        title = self.item.get("title", "").lower()
        uploader = self.item.get("uploader", "").lower()
        return q in title or q in uploader
