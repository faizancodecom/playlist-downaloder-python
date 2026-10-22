# StreamHarvester: Professional Media and Playlist Downloader

StreamHarvester is a high-performance desktop application built in Python and PyQt6 for batch downloading and format conversion of playlists and standalone media from YouTube and other supported streaming services.

---

## Key Features

- Playlist and Single Media Extraction: Analyzes full playlists or single media URLs, retrieving metadata, titles, uploaders, durations, and high-resolution thumbnail previews.
- Dynamic Format Selection:
  - Video Mode: Supports MP4, MKV, WEBM, AVI, and MOV containers with quality presets ranging from 360p up to 4K Ultra HD (2160p).
  - Audio Mode: Direct audio stream extraction and conversion to FLAC (Hi-Res studio master exceeding 3000 kbps, 24-bit 96kHz), MP3, M4A (AAC), WAV, OPUS, and OGG with configurable bitrates up to lossless studio master levels.
- Granular Selection Controls: Select individual items via checkboxes, batch select all items, invert selection, or use live keyword filtering to quickly locate specific tracks or videos.
- Non-Blocking Background Processing: Multi-threaded engine powered by PyQt6 QThread and QThreadPool prevents GUI freezing during metadata inspection, thumbnail rendering, and large file transfers.
- Dual Progress Tracking: Separate indicators for individual file transfer metrics (real-time speed in MB/s, ETA, downloaded size) and overall playlist completion status.
- Self-Contained FFmpeg Integration: Bundles automated detection for system FFmpeg and FFprobe binaries, alongside a dedicated one-click installer for isolated local setup.
- Persistent Preferences: User choices for target directory, format defaults, and metadata embedding tags are saved locally in JSON format.

---

## System Requirements

- Operating System: Windows 10/11, macOS 11+, or Linux (x86_64)
- Python Runtime: Python 3.10 or higher
- Multimedia Tools: FFmpeg and FFprobe (automatically managed or pre-installed)

---

## Installation

### 1. Clone or Download Repository
Clone the repository to your local directory:
```bash
git clone https://github.com/faizancodecom/stream-harvester.git
cd stream-harvester
```

### 2. Set Up Virtual Environment (Recommended)
Create and activate an isolated Python environment:

On Windows:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

On Linux / macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install all required Python packages using pip:
```bash
pip install -r requirements.txt
```

The application relies on:
- PyQt6: Modern GUI framework and threading infrastructure.
- yt-dlp: Robust backend media extraction and download engine.
- requests: Network requests and API endpoints.
- Pillow: Image processing for high-DPI thumbnails.

---

## FFmpeg Setup

FFmpeg and FFprobe are required for merging separate video/audio streams and converting audio to target formats such as MP3 or FLAC.

StreamHarvester offers two installation methods:

### Method A: Local Automated Installation (Recommended)
1. Launch the application.
2. Click the "FFmpeg Status" indicator in the top-right header.
3. In the diagnostic dialog, click "Download & Setup Local FFmpeg".
4. The application downloads and extracts the official static Windows build into the `bin/` directory within the application folder. No administrative privileges or system environment edits are required.

### Method B: System-Wide Installation via Package Manager
On Windows (via winget):
```powershell
winget install --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements
```

On macOS (via Homebrew):
```bash
brew install ffmpeg
```

On Ubuntu / Debian:
```bash
sudo apt update && sudo apt install ffmpeg
```

---

## Usage Guide

### Starting the Application
Execute the primary entry script:
```bash
python main.py
```

### Downloading a Playlist or Video
1. Paste URL: Insert any YouTube playlist link, album link, or individual video URL into the top input field and click "Fetch Playlist".
2. Select Media Mode:
   - Select "Video" to download container files (MP4, MKV, etc.) with resolution preferences.
   - Select "Audio (Music)" to convert directly to MP3, FLAC, M4A, or WAV.
3. Filter and Choose Items:
   - Use "Select All", "Deselect All", or "Invert" buttons.
   - Enter text into the filter box to narrow down items by title or artist.
   - Check or uncheck individual video cards.
4. Set Output Folder: Click "Browse..." to choose a custom save directory, or use the default Downloads location.
5. Initiate Download: Click "Download Selected". Monitor real-time download speeds, ETA, and progress bar updates.
6. Access Files: Once finished, click "Open" next to the folder path to open Windows Explorer directly at the destination.

---

## Project Structure

```
stream-harvester/
|-- main.py                  Entry point initializing QApplication and main window
|-- requirements.txt         Package dependency definitions
|-- settings.json            Local persistent user preferences
|-- bin/                     Local directory for ffmpeg.exe and ffprobe.exe
\-- app/
    |-- __init__.py          Application module initialization
    |-- config.py            Configuration manager with JSON persistence
    |-- ffmpeg_manager.py    Binary locator, diagnostics, and download worker
    |-- downloader.py        yt-dlp integration, extraction and download threads
    \-- ui/
        |-- __init__.py      UI module definitions
        |-- main_window.py   Main desktop interface and interaction logic
        |-- video_card.py    Interactive playlist row item with thumbnail and status
        |-- thumbnail_loader.py  Threaded asynchronous thumbnail retrieval
        |-- dialogs.py       FFmpeg diagnostics and configuration windows
        \-- styles.py        Refined dark-mode Qt Style Sheet (QSS)
```

---

## Configuration Settings

Settings are stored in `settings.json` and configurable through the Preferences menu:
- `output_dir`: Default save directory for downloaded files.
- `media_type`: Default mode (`video` or `audio`).
- `video_format`: Default video container (`mp4`, `mkv`, `webm`, `avi`, `mov`).
- `video_quality`: Quality threshold (`best`, `2160p`, `1440p`, `1080p`, `720p`, `480p`, `360p`).
- `audio_format`: Default audio codec (`mp3`, `flac`, `m4a`, `wav`, `opus`, `ogg`).
- `audio_quality`: Audio bitrate preset (`320`, `256`, `192`, `128`, `best`).
- `embed_thumbnail`: Embed album cover / thumbnail as ID3 or video cover art.
- `embed_metadata`: Write artist, track title, and album metadata tags into media files.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.
