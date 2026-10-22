import os
import sys
import shutil
import subprocess
import zipfile
import urllib.request
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal

FFMPEG_WIN64_URL = "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BIN_DIR = PROJECT_ROOT / "bin"

def get_ffmpeg_dir():
    """Returns local bin directory if ffmpeg.exe exists there, otherwise None."""
    local_ffmpeg = BIN_DIR / "ffmpeg.exe"
    if local_ffmpeg.exists():
        return str(BIN_DIR)
    return None

def find_binary(binary_name="ffmpeg"):
    """
    Finds executable path for ffmpeg or ffprobe.
    Checks:
    1. Local bin/ directory in project
    2. System PATH
    3. Common Windows directories
    """
    exe_name = f"{binary_name}.exe" if sys.platform == "win32" else binary_name
    
    # 1. Check local bin
    local_path = BIN_DIR / exe_name
    if local_path.exists():
        return str(local_path)
    
    # 2. Check system PATH
    path_which = shutil.which(binary_name)
    if path_which:
        return path_which

    # 3. Check common Windows paths
    candidates = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Links" / exe_name,
        Path("C:/ffmpeg/bin") / exe_name,
        Path("C:/Program Files/ffmpeg/bin") / exe_name,
        Path("C:/ProgramData/chocolatey/bin") / exe_name,
        Path("D:/softwares") / exe_name,
    ]
    for c in candidates:
        if c.exists():
            return str(c)

    return None

def get_ffmpeg_status():
    """
    Returns a dict with detection status:
    {
        "available": bool,
        "ffmpeg_path": str or None,
        "ffprobe_path": str or None,
        "version": str or None,
        "is_local": bool
    }
    """
    ffmpeg_path = find_binary("ffmpeg")
    ffprobe_path = find_binary("ffprobe")
    available = bool(ffmpeg_path)
    version = None
    is_local = False

    if ffmpeg_path:
        is_local = str(BIN_DIR).lower() in ffmpeg_path.lower()
        try:
            res = subprocess.run(
                [ffmpeg_path, "-version"],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            if res.returncode == 0:
                first_line = res.stdout.splitlines()[0]
                version = first_line.replace("ffmpeg version", "").strip().split()[0]
        except Exception:
            pass

    return {
        "available": available,
        "has_ffprobe": bool(ffprobe_path),
        "ffmpeg_path": ffmpeg_path,
        "ffprobe_path": ffprobe_path,
        "version": version or ("Detected" if available else "Not Found"),
        "is_local": is_local
    }

class FFmpegDownloaderThread(QThread):
    progress = pyqtSignal(int, str)      # percent (0-100), status message
    finished = pyqtSignal(bool, str)     # success, message

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        try:
            BIN_DIR.mkdir(parents=True, exist_ok=True)
            zip_dest = BIN_DIR / "ffmpeg_temp.zip"

            self.progress.emit(5, "Connecting to download server...")
            
            req = urllib.request.Request(
                FFMPEG_WIN64_URL,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )

            with urllib.request.urlopen(req, timeout=30) as response, open(zip_dest, "wb") as out_file:
                total_length = response.getheader("content-length")
                total_size = int(total_length) if total_length else 0
                downloaded = 0
                block_size = 1024 * 64

                while True:
                    if self._is_cancelled:
                        out_file.close()
                        if zip_dest.exists():
                            zip_dest.unlink()
                        self.finished.emit(False, "Installation cancelled by user.")
                        return

                    buffer = response.read(block_size)
                    if not buffer:
                        break
                    downloaded += len(buffer)
                    out_file.write(buffer)

                    if total_size > 0:
                        pct = int((downloaded / total_size) * 80) + 5
                        mb_done = downloaded / (1024 * 1024)
                        mb_tot = total_size / (1024 * 1024)
                        self.progress.emit(pct, f"Downloading FFmpeg: {mb_done:.1f} MB / {mb_tot:.1f} MB ({pct}%)")
                    else:
                        mb_done = downloaded / (1024 * 1024)
                        self.progress.emit(40, f"Downloading FFmpeg: {mb_done:.1f} MB...")

            self.progress.emit(85, "Extracting ffmpeg and ffprobe binaries...")

            # Extract only ffmpeg.exe and ffprobe.exe
            with zipfile.ZipFile(zip_dest, "r") as zip_ref:
                for member in zip_ref.namelist():
                    basename = Path(member).name.lower()
                    if basename in ("ffmpeg.exe", "ffprobe.exe"):
                        target_file = BIN_DIR / Path(member).name
                        with zip_ref.open(member) as source, open(target_file, "wb") as target:
                            shutil.copyfileobj(source, target)

            # Cleanup zip
            if zip_dest.exists():
                try:
                    zip_dest.unlink()
                except Exception:
                    pass

            self.progress.emit(100, "FFmpeg installation completed successfully!")
            self.finished.emit(True, f"FFmpeg binaries successfully placed in:\n{BIN_DIR}")

        except Exception as e:
            self.finished.emit(False, f"Failed to download FFmpeg: {str(e)}")
