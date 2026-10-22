import urllib.request
from PyQt6.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QPixmap, QImage

class ThumbnailWorkerSignals(QObject):
    ready = pyqtSignal(str, QPixmap) # video_id, pixmap

class ThumbnailRunnable(QRunnable):
    def __init__(self, video_id: str, url: str, signals: ThumbnailWorkerSignals):
        super().__init__()
        self.video_id = video_id
        self.url = url
        self.signals = signals

    @pyqtSlot()
    def run(self):
        if not self.url:
            return
        try:
            req = urllib.request.Request(
                self.url,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = resp.read()
                image = QImage()
                if image.loadFromData(data):
                    pixmap = QPixmap.fromImage(image)
                    self.signals.ready.emit(self.video_id, pixmap)
        except Exception:
            pass


class ThumbnailLoader(QObject):
    thumbnail_loaded = pyqtSignal(str, QPixmap)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.signals = ThumbnailWorkerSignals()
        self.signals.ready.connect(self._on_thumbnail_ready)
        self.cache = {}
        self.pool = QThreadPool.globalInstance()
        self.pool.setMaxThreadCount(6)

    def load_thumbnail(self, video_id: str, url: str):
        if video_id in self.cache:
            self.thumbnail_loaded.emit(video_id, self.cache[video_id])
            return

        runnable = ThumbnailRunnable(video_id, url, self.signals)
        self.pool.start(runnable)

    def _on_thumbnail_ready(self, video_id: str, pixmap: QPixmap):
        self.cache[video_id] = pixmap
        self.thumbnail_loaded.emit(video_id, pixmap)
