import os
import re
import sys
import time
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal
import yt_dlp

from app.ffmpeg_manager import find_binary, BIN_DIR

def format_duration(seconds):
    if not seconds or not isinstance(seconds, (int, float)):
        return "--:--"
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"

def format_bytes(bytes_num):
    if not bytes_num or not isinstance(bytes_num, (int, float)):
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_num < 1024.0:
            return f"{bytes_num:.1f} {unit}"
        bytes_num /= 1024.0
    return f"{bytes_num:.1f} PB"

def format_speed(bytes_per_sec):
    if not bytes_per_sec or not isinstance(bytes_per_sec, (int, float)):
        return "-- KB/s"
    return f"{format_bytes(bytes_per_sec)}/s"

def format_eta(seconds):
    if not seconds or not isinstance(seconds, (int, float)):
        return "--:--"
    seconds = int(seconds)
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"


class PlaylistFetchWorker(QThread):
    fetch_started = pyqtSignal(str)
    item_fetched = pyqtSignal(dict)
    fetch_finished = pyqtSignal(dict, list)   # playlist_info, list of item dicts
    fetch_error = pyqtSignal(str)
    log_message = pyqtSignal(str)

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self.url = url.strip()
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        self.fetch_started.emit(self.url)
        self.log_message.emit(f"Connecting and extracting info for: {self.url}")

        ydl_opts = {
            'extract_flat': 'in_playlist',
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)

                if self._is_cancelled:
                    return

                if not info:
                    self.fetch_error.emit("Could not retrieve information from the provided URL.")
                    return

                entries = []
                playlist_info = {
                    "id": info.get("id", ""),
                    "title": info.get("title", "Untitled Playlist / Video"),
                    "uploader": info.get("uploader") or info.get("channel", "Unknown Channel"),
                    "webpage_url": info.get("webpage_url", self.url),
                    "thumbnail": info.get("thumbnail", ""),
                    "is_playlist": "entries" in info,
                }

                if "entries" in info and info["entries"] is not None:
                    # It is a playlist
                    raw_entries = list(info["entries"])
                    playlist_info["total_count"] = len(raw_entries)
                    self.log_message.emit(f"Discovered playlist with {len(raw_entries)} videos.")

                    for idx, entry in enumerate(raw_entries, start=1):
                        if self._is_cancelled:
                            return
                        if not entry:
                            continue

                        # Extract best thumbnail
                        thumb = entry.get("thumbnail") or ""
                        if not thumb and entry.get("thumbnails"):
                            thumb = entry["thumbnails"][-1].get("url", "")
                        
                        video_id = entry.get("id", "")
                        if not thumb and video_id:
                            # YouTube fallback thumbnail
                            thumb = f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg"

                        item = {
                            "index": idx,
                            "id": video_id,
                            "title": entry.get("title", f"Video {idx}"),
                            "duration_sec": entry.get("duration", 0),
                            "duration_str": format_duration(entry.get("duration", 0)),
                            "uploader": entry.get("uploader") or entry.get("channel", playlist_info["uploader"]),
                            "thumbnail_url": thumb,
                            "url": entry.get("url") or entry.get("webpage_url") or f"https://www.youtube.com/watch?v={video_id}",
                            "status": "Ready",
                            "selected": True
                        }
                        entries.append(item)
                        self.item_fetched.emit(item)
                else:
                    # Single video
                    playlist_info["total_count"] = 1
                    playlist_info["is_playlist"] = False
                    
                    thumb = info.get("thumbnail") or ""
                    if not thumb and info.get("thumbnails"):
                        thumb = info["thumbnails"][-1].get("url", "")
                    
                    video_id = info.get("id", "")
                    if not thumb and video_id:
                        thumb = f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg"

                    item = {
                        "index": 1,
                        "id": video_id,
                        "title": info.get("title", "Video 1"),
                        "duration_sec": info.get("duration", 0),
                        "duration_str": format_duration(info.get("duration", 0)),
                        "uploader": info.get("uploader") or info.get("channel", "Unknown Channel"),
                        "thumbnail_url": thumb,
                        "url": info.get("webpage_url", self.url),
                        "status": "Ready",
                        "selected": True
                    }
                    entries.append(item)
                    self.item_fetched.emit(item)

                if self._is_cancelled:
                    return

                self.log_message.emit(f"Metadata extraction finished: {len(entries)} items loaded.")
                self.fetch_finished.emit(playlist_info, entries)

        except Exception as e:
            err_msg = str(e)
            self.log_message.emit(f"Error fetching playlist: {err_msg}")
            self.fetch_error.emit(err_msg)


class PlaylistDownloadWorker(QThread):
    overall_progress = pyqtSignal(int, int, int)       # index, total, overall_percent
    item_started = pyqtSignal(str, int, str)           # item_id, index, title
    item_progress = pyqtSignal(str, dict)              # item_id, progress_dict
    item_completed = pyqtSignal(str, str)              # item_id, filename
    item_failed = pyqtSignal(str, str)                 # item_id, error_msg
    all_completed = pyqtSignal(int, int)               # successful, failed
    log_message = pyqtSignal(str)

    def __init__(self, items, download_options, parent=None):
        super().__init__(parent)
        self.items = items
        self.opts = download_options
        self._is_cancelled = False
        self._is_paused = False
        self._current_item_id = None

    def cancel(self):
        self._is_cancelled = True

    def pause(self):
        self._is_paused = True

    def resume(self):
        self._is_paused = False

    def is_paused(self):
        return self._is_paused

    def _progress_hook(self, d):
        if self._is_cancelled:
            raise Exception("Download cancelled by user.")

        while self._is_paused and not self._is_cancelled:
            time.sleep(0.2)

        status = d.get('status')
        if status == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded = d.get('downloaded_bytes') or 0
            speed = d.get('speed') or 0
            eta = d.get('eta') or 0

            percent = 0
            if total > 0:
                percent = int((downloaded / total) * 100)

            data = {
                "status": "Downloading",
                "percent": min(100, max(0, percent)),
                "downloaded_bytes": downloaded,
                "total_bytes": total,
                "speed_str": format_speed(speed),
                "eta_str": format_eta(eta),
                "downloaded_str": format_bytes(downloaded),
                "total_str": format_bytes(total)
            }
            if self._current_item_id:
                self.item_progress.emit(self._current_item_id, data)

        elif status == 'finished':
            filename = d.get('filename', '')
            if self._current_item_id:
                self.item_progress.emit(self._current_item_id, {
                    "status": "Processing / Converting...",
                    "percent": 100,
                    "speed_str": "--",
                    "eta_str": "00:00",
                    "downloaded_str": "",
                    "total_str": ""
                })

    def run(self):
        output_dir = self.opts.get("output_dir")
        os.makedirs(output_dir, exist_ok=True)

        media_type = self.opts.get("media_type", "video")
        video_format = self.opts.get("video_format", "mp4").lower()
        video_quality = self.opts.get("video_quality", "best")
        audio_format = self.opts.get("audio_format", "mp3").lower()
        audio_quality = self.opts.get("audio_quality", "320")
        embed_thumb = self.opts.get("embed_thumbnail", True)
        embed_meta = self.opts.get("embed_metadata", True)
        numbering = self.opts.get("number_files", True)

        # Detect FFmpeg location
        ffmpeg_bin = find_binary("ffmpeg")
        ffmpeg_dir = str(Path(ffmpeg_bin).parent) if ffmpeg_bin else str(BIN_DIR)

        self.log_message.emit(f"Output directory: {output_dir}")
        self.log_message.emit(f"Media mode: {media_type.upper()} | Output Format: {video_format if media_type == 'video' else audio_format}")
        if ffmpeg_bin:
            self.log_message.emit(f"FFmpeg binary detected: {ffmpeg_bin}")
        else:
            self.log_message.emit("Warning: FFmpeg binary not found. Formats requiring muxing may fail.")

        total_items = len(self.items)
        successful = 0
        failed = 0

        for idx, item in enumerate(self.items):
            if self._is_cancelled:
                self.log_message.emit("Download queue cancelled by user.")
                break

            self._current_item_id = item["id"]
            title = item.get("title", f"Item {idx+1}")
            self.item_started.emit(item["id"], idx + 1, title)
            self.log_message.emit(f"[{idx+1}/{total_items}] Starting: {title}")

            # Calculate overall progress percentage
            overall_pct = int((idx / total_items) * 100)
            self.overall_progress.emit(idx + 1, total_items, overall_pct)

            # Build filename template
            if numbering and total_items > 1:
                filename_template = os.path.join(output_dir, f"%(playlist_index)02d - %(title)s.%(ext)s")
            else:
                filename_template = os.path.join(output_dir, "%(title)s.%(ext)s")

            # Setup yt-dlp options
            ydl_opts = {
                'outtmpl': filename_template,
                'progress_hooks': [self._progress_hook],
                'quiet': True,
                'no_warnings': True,
                'ffmpeg_location': ffmpeg_dir,
                'restrictfilenames': False,
                'windowsfilenames': True,
            }

            # Configure video vs audio settings
            if media_type == "video":
                # Video format and quality selection
                if video_quality == "best":
                    fmt = "bestvideo+bestaudio/best"
                else:
                    height_match = re.search(r'(\d+)p?', video_quality)
                    if height_match:
                        h = height_match.group(1)
                        fmt = f"bestvideo[height<={h}]+bestaudio/best[height<={h}]/best"
                    else:
                        fmt = "bestvideo+bestaudio/best"

                ydl_opts['format'] = fmt
                ydl_opts['merge_output_format'] = video_format

                postprocessors = []
                if embed_thumb:
                    postprocessors.append({'key': 'FFmpegThumbnailsConvertor', 'format': 'jpg'})
                    postprocessors.append({'key': 'EmbedThumbnail'})
                if embed_meta:
                    postprocessors.append({'key': 'FFmpegMetadata'})
                
                if postprocessors:
                    ydl_opts['postprocessors'] = postprocessors

            else:
                # Audio mode
                ydl_opts['format'] = 'bestaudio/best'
                postprocessors = [
                    {
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': audio_format,
                        'preferredquality': audio_quality if audio_format in ['mp3', 'm4a', 'opus'] else None
                    }
                ]
                
                # High-bitrate parameters for lossless formats (FLAC / WAV)
                pp_args = []
                if audio_format == 'flac':
                    if audio_quality in ['3200', '3000'] or (audio_quality.isdigit() and int(audio_quality) >= 3000):
                        # Studio Master 24-bit / 96kHz stream yielding bitrate > 3000 kbps
                        pp_args = ['-ar', '96000', '-sample_fmt', 's24', '-compression_level', '0']
                    elif audio_quality == '1411':
                        # 16-bit 44.1kHz standard CD quality
                        pp_args = ['-ar', '44100', '-sample_fmt', 's16']
                elif audio_format == 'wav':
                    if audio_quality in ['3200', '3000'] or (audio_quality.isdigit() and int(audio_quality) >= 3000):
                        pp_args = ['-ar', '96000', '-sample_fmt', 's32']
                    elif audio_quality in ['2304', '1411']:
                        pp_args = ['-ar', '48000', '-sample_fmt', 's24']

                if pp_args:
                    ydl_opts['postprocessor_args'] = {
                        'FFmpegExtractAudio': pp_args
                    }

                if embed_thumb and audio_format in ['mp3', 'm4a', 'flac']:
                    postprocessors.append({'key': 'FFmpegThumbnailsConvertor', 'format': 'jpg'})
                    postprocessors.append({'key': 'EmbedThumbnail'})
                if embed_meta:
                    postprocessors.append({'key': 'FFmpegMetadata'})

                ydl_opts['postprocessors'] = postprocessors

            try:
                video_url = item.get("url") or f"https://www.youtube.com/watch?v={item['id']}"
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(video_url, download=True)
                    final_filename = ydl.prepare_filename(info_dict)

                successful += 1
                self.item_completed.emit(item["id"], final_filename)
                self.log_message.emit(f"Completed: {title}")

            except Exception as e:
                err_msg = str(e)
                if "cancelled by user" in err_msg.lower():
                    self.log_message.emit("Download cancelled.")
                    break
                failed += 1
                self.item_failed.emit(item["id"], err_msg)
                self.log_message.emit(f"Failed [{title}]: {err_msg}")

            # Update overall progress
            new_overall = int(((idx + 1) / total_items) * 100)
            self.overall_progress.emit(idx + 1, total_items, new_overall)

        self.all_completed.emit(successful, failed)
        self.log_message.emit(f"Batch completed: {successful} succeeded, {failed} failed.")
