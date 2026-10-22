import os
import json
from pathlib import Path

DEFAULT_OUTPUT_DIR = str(Path.home() / "Downloads" / "PlaylistDownloads")
CONFIG_FILE = Path(__file__).resolve().parent.parent / "settings.json"

DEFAULT_CONFIG = {
    "output_dir": DEFAULT_OUTPUT_DIR,
    "media_type": "video",       # "video" or "audio"
    "video_format": "mp4",       # mp4, mkv, webm, avi, mov
    "video_quality": "best",     # best, 2160p, 1440p, 1080p, 720p, 480p, 360p
    "audio_format": "mp3",       # mp3, flac, m4a, wav, opus, aac
    "audio_quality": "320",      # 320, 256, 192, 128, best
    "embed_thumbnail": True,
    "embed_metadata": True,
    "embed_subtitles": False,
    "max_concurrent_downloads": 1,
    "custom_ffmpeg_path": ""
}

class AppConfig:
    def __init__(self):
        self.data = dict(DEFAULT_CONFIG)
        self.load()

    def load(self):
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self.data.update(loaded)
        except Exception:
            pass
        
        # Ensure output directory exists or can be resolved
        out_dir = self.data.get("output_dir", DEFAULT_OUTPUT_DIR)
        try:
            os.makedirs(out_dir, exist_ok=True)
        except Exception:
            self.data["output_dir"] = DEFAULT_OUTPUT_DIR

    def save(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

config = AppConfig()
