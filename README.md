# Linear - School Music Timer

A modern broadcasting-style school music scheduling system with support for both YouTube playlists and local audio files.

## Features

- 🎵 **Dual Media Support**: YouTube playlists and local audio files
- ⏰ **Advanced Scheduling**: Weekly schedule with hourly precision
- 🎨 **Modern UI**: Linear broadcast software inspired interface
- 🔄 **Conflict Prevention**: Unified media controller prevents simultaneous playback
- 📊 **Real-time Monitoring**: Live broadcast log and current playing status
- 💾 **Persistent Settings**: Automatic configuration saving

## Files Structure

```
YoutubeAutoPlayer/
├── gui.py                 # Main Linear-style GUI application
├── video_scheduler.py     # Core scheduling engine
├── media_controller.py    # Unified media playback controller
├── playvideo.py          # YouTube video playback with anti-detection
├── audio_player.py       # Local audio file playback
├── config.ini            # User settings and playlists
└── README.md            # This file
```

## Requirements

- Python 3.7+
- PyQt6
- Selenium WebDriver
- pygame (for audio playback)

## Installation

1. Install required packages:
```bash
pip install PyQt6 selenium pygame
```

2. Run the application:
```bash
python gui.py
```

## Usage

1. **Playlists**: Add YouTube URLs or local audio files
2. **Schedule**: Set weekly schedules with start/end times
3. **Monitor**: View real-time broadcast logs and current status

## UI Layout

- **Left Sidebar**: Navigation (Schedule, Playlists, Settings)
- **Main Area**: Weekly schedule grid with hourly slots
- **Right Panel**: Broadcast log and playback controls
- **Bottom**: Current playing track information

The interface is inspired by professional broadcasting software like Linear for a familiar and intuitive experience.

