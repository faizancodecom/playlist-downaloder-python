# Playlist Downloader (`playlist-downaloder-python`)

A high-performance desktop application built with **Python**, **PyQt6**, and **yt-dlp** for batch downloading and high-fidelity media extraction from YouTube playlists, albums, and individual videos.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green.svg)](https://pypi.org/project/PyQt6/)
[![yt-dlp](https://img.shields.io/badge/Engine-yt--dlp-red.svg)](https://github.com/yt-dlp/yt-dlp)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-playlist--downaloder--python-black.svg)](https://github.com/faizancodecom/playlist-downaloder-python)

---

## Key Features

- **Playlist & Single Media Extraction**: Fetches metadata, channel/artist names, video runtimes, and high-resolution thumbnail previews for full playlists or single videos.
- **Dynamic Format & Audio Studio Presets**:
  - **Audio (Music)**: Lossless conversion to **FLAC** (Hi-Res Studio Master > 3200 kbps, 24-bit 96kHz, Level 0 compression), **WAV** (up to 32-bit float master), **MP3** (320 kbps extreme / 256 / 192 / 128 kbps), **M4A (AAC)**, **OPUS**, and **OGG**.
  - **Video**: Merges best video and audio streams into **MP4**, **MKV**, **WEBM**, **AVI**, or **MOV** at resolutions up to **4K Ultra HD (2160p)** and **2K (1440p)**.
- **Real-Time Speed & Dual ETA Tracking**:
  - **Item ETA**: Dynamic speed smoothing calculation showing estimated seconds/minutes left for the current track.
  - **Playlist Batch ETA**: Real-time projected completion time for the entire batch queue.
- **Interactive Selection & Live Search Filtering**:
  - One-click **Select All**, **Deselect All**, and **Invert Selection**.
  - Instant live keyword filtering to search tracks by title or artist name.
  - Granular selection counter showing exact count and total runtime (`14 of 14 selected (46:18)`).
- **Automated Metadata & Cover Art Tagging**:
  - Embeds album artwork / thumbnail directly into media files.
  - Writes ID3 tags including artist name, track title, and album information.
- **Built-in Standalone FFmpeg Manager**:
  - Automated system-wide detection of `ffmpeg` and `ffprobe`.
  - One-click automatic installer that downloads and sets up standalone FFmpeg in the local `bin/` directory without requiring admin privileges or PATH edits.
  - Custom binary path configuration support.
- **Modern Slate Dark Theme**:
  - High-contrast, clean dark interface tailored for Windows, macOS, and Linux.
  - Non-blocking multithreaded architecture prevents GUI freezes during heavy downloads.
  - Activity log console drawer for real-time diagnostics.

---

## System Requirements

| Component | Minimum Requirement | Recommended |
|---|---|---|
| **Operating System** | Windows 10/11, macOS 11+, or Linux (x86_64) | Windows 11 (64-bit) / macOS Sonoma / Ubuntu 22.04+ |
| **Python** | Python 3.10 | Python 3.11, 3.12, or 3.13 |
| **Encoder / Muxer** | FFmpeg 4.4+ | FFmpeg 6.0+ (downloadable automatically inside the app) |
| **Disk Space** | 200 MB for app & FFmpeg | Ample storage for downloaded media |

---

## Complete Installation Guide

Follow these step-by-step instructions to get Playlist Downloader running on your machine.

### Step 1: Clone or Download the Repository

Open your terminal or command line and run:

```bash
git clone https://github.com/faizancodecom/playlist-downaloder-python.git
cd playlist-downaloder-python
```

*(Alternatively, click **Code -> Download ZIP** on GitHub and extract the folder).*

---

### Step 2: Create a Virtual Environment (Recommended)

An isolated virtual environment ensures packages do not conflict with your system Python.

#### On Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

> [!TIP]
> **PowerShell Execution Policy Error Fix:**  
> If you encounter `cannot be loaded because running scripts is disabled on this system`, run this command in PowerShell to allow script execution for your session:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
> .\venv\Scripts\Activate.ps1
> ```

#### On Windows (Command Prompt - CMD):
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

#### On macOS & Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### Step 3: Install Required Dependencies

Upgrade `pip` and install the project requirements:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Dependencies installed:
- `PyQt6` (>= 6.6.0): Native desktop GUI framework.
- `yt-dlp` (>= 2024.1.0): High-performance video & audio extraction backend.
- `requests` (>= 2.31.0): Network connectivity and API communication.
- `Pillow` (>= 10.0.0): Image manipulation for high-DPI thumbnails.

---

### Step 4: Setup FFmpeg

FFmpeg and FFprobe are required to extract high-bitrate audio (FLAC, MP3, WAV) and merge high-resolution video streams.

Choose either **Method A (Automatic)** or **Method B (System-Wide)**:

#### Method A: 1-Click Built-in Installer (Easiest)
1. Run the application:
   ```bash
   python main.py
   ```
2. Click the **"FFmpeg Status"** badge in the top-right corner.
3. In the diagnostic dialog, click **"Download & Setup Local FFmpeg"**.
4. The application will automatically download, extract, and configure official standalone `ffmpeg.exe` and `ffprobe.exe` binaries into the local `bin/` directory.

#### Method B: Manual / System-Wide Package Manager

- **Windows (winget)**:
  ```powershell
  winget install --id Gyan.FFmpeg
  ```
- **Windows (Chocolatey)**:
  ```powershell
  choco install ffmpeg
  ```
- **macOS (Homebrew)**:
  ```bash
  brew install ffmpeg
  ```
- **Ubuntu / Debian**:
  ```bash
  sudo apt update && sudo apt install ffmpeg
  ```

---

## Running the Application

Once installed and activated in your virtual environment:

```bash
python main.py
```

---

## User Guide & Workflow

1. **Paste URL**:
   - Paste any YouTube playlist, album, music track, or video URL into the top text box.
   - Click **"Fetch Playlist"** or hit `Enter`.
2. **Choose Mode & Quality**:
   - **Audio (Music)**: Select your desired audio container (**FLAC**, **MP3**, **M4A**, **WAV**, **OPUS**, **OGG**). For audiophile quality, select `Hi-Res Studio Master (> 3200 kbps / 24-bit 96kHz)`.
   - **Video**: Select container (**MP4**, **MKV**, etc.) and resolution (e.g. `4K Ultra HD (2160p)`, `1080p`).
3. **Select Tracks / Videos**:
   - Use **"Select All"**, **"Deselect All"**, or **"Invert"**.
   - Use the **"Filter videos..."** search box to instantly search by artist or song title.
   - Click individual checkboxes to customize your selection.
4. **Choose Destination Folder**:
   - Click **"Browse..."** to select your save directory (defaults to your `Downloads/PlaylistDownloads` folder).
5. **Start Download**:
   - Click **"Download Selected (X)"**.
   - Monitor live download speed (MB/s), current track ETA, and estimated remaining time for the overall batch.
6. **Open Completed Files**:
   - When download finishes, click **"Open Folder"** on the completion dialog to view your downloaded files immediately in File Explorer / Finder.

---

## Project Structure

```
playlist-downaloder-python/
|-- main.py                    # Entry point initializing Dark Palette & QApplication
|-- requirements.txt           # Python dependency definitions
|-- settings.json              # Persistent user preferences (JSON)
|-- bin/                       # Local directory for ffmpeg.exe & ffprobe.exe
\-- app/
    |-- __init__.py            # Application package initializer
    |-- config.py              # Configuration manager with JSON persistence
    |-- ffmpeg_manager.py      # Binary discovery, diagnostics & auto-downloader
    |-- downloader.py          # Multithreaded yt-dlp extraction, speed smoothing & ETA
    \-- ui/
        |-- __init__.py        # UI module initializer
        |-- main_window.py     # Main desktop interface and state orchestration
        |-- video_card.py      # Interactive row item with status badge & thumbnail
        |-- thumbnail_loader.py # Threaded background thumbnail fetcher
        |-- dialogs.py         # FFmpeg diagnostic, Settings & Completion dialogs
        \-- styles.py          # Native Dark Mode Qt Style Sheet (QSS)
```

---

## Configuration Settings

Preferences are saved in `settings.json` and configurable in the **Preferences** dialog:

- `output_dir`: Default directory for saved files.
- `media_type`: Default mode (`audio` or `video`).
- `video_format`: Video container (`mp4`, `mkv`, `webm`, `avi`, `mov`).
- `video_quality`: Maximum video resolution (`best`, `2160p`, `1440p`, `1080p`, `720p`).
- `audio_format`: Audio codec (`flac`, `mp3`, `m4a`, `wav`, `opus`, `ogg`).
- `audio_quality`: Audio bitrate / sample rate profile.
- `embed_thumbnail`: Embeds cover art into the audio/video file.
- `embed_metadata`: Writes artist, title, album, and track tags.
- `embed_subtitles`: Embeds subtitles when available.
- `custom_ffmpeg_path`: Custom binary path for `ffmpeg.exe`.

---

## Troubleshooting & FAQ

### Q1: The Download button was disabled after fetching a playlist?
This issue has been resolved in the current version. The download button automatically enables as soon as items are loaded and selected. You can also click **"Select All"** at any time to re-enable.

### Q2: Download shows `-- KB/s` or ETA jumps?
The engine now uses an exponential moving average to smooth speed fluctuations, accurately calculating both the single-item ETA and the overall batch estimated time remaining.

### Q3: How do I update `yt-dlp` if YouTube changes its format?
YouTube frequently updates its streaming APIs. You can update `yt-dlp` anytime with:
```bash
pip install --upgrade yt-dlp
```

### Q4: Antivirus blocks the FFmpeg download?
Some Windows security configurations flag `.zip` downloads from GitHub releases. You can either use **Method B** (`winget install --id Gyan.FFmpeg`) or download official FFmpeg builds directly from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) and place `ffmpeg.exe` and `ffprobe.exe` into the `bin/` folder.

---

## Contributing

Pull requests, bug reports, and suggestions are welcome!  
Feel free to open an issue or submit a pull request on the [GitHub repository](https://github.com/faizancodecom/playlist-downaloder-python).

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
