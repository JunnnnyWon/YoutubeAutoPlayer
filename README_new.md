# CKBS Scheduler Program

A modern broadcasting-style school music scheduling system with support for both YouTube playlists and local audio files.

## Features

- 🎵 **Dual Media Support**: YouTube playlists and local audio files
- ⏰ **Advanced Scheduling**: Weekly schedule with hourly precision
- 🎨 **Modern UI**: Tkinter-based interface with custom Pretendard fonts
- 🔄 **Conflict Prevention**: Unified media controller prevents simultaneous playback
- 📊 **Real-time Monitoring**: Live broadcast log and current playing status
- 💾 **Persistent Settings**: Automatic configuration saving

## Files Structure

```
YoutubeAutoPlayer/
├── new_ui.py             # Main Tkinter GUI application
├── video_scheduler.py    # Core scheduling engine
├── media_controller.py   # Unified media playback controller
├── play_video.py         # YouTube video playback with anti-detection
├── audio_player.py       # Local audio file playback
├── font_manager.py       # Custom font management (Pretendard)
├── anti_detection.py     # Chrome anti-detection settings
├── schedule.json         # Schedule data storage
├── Pretendard-1.3.9/     # Custom font files
└── README.md            # This file
```

## Requirements

- Python 3.7+
- tkinter (usually included with Python)
- Selenium WebDriver
- pygame (for audio playback)
- Chrome browser

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. **Chrome Extensions Setup** (Important for team members):
   - The program uses Chrome with specific settings for YouTube playback
   - Chrome extensions need to be installed individually on each machine
   - When first running the program, Chrome will open with extension installation enabled
   - Install any required extensions manually as they cannot be shared via Git

3. Run the application:
```bash
python new_ui.py
```

## Usage

1. **Schedule Setup**: Set weekly schedules with precise start/end times
2. **Media Configuration**: Add YouTube URLs or local audio files
3. **Monitor**: View real-time broadcast logs and current status
4. **Font Display**: Automatic Pretendard font loading for modern UI

## Note for Team Members

⚠️ **Important**: The `profile/` folder contains Chrome user data but **extensions cannot be shared**

- Each team member must install Chrome extensions individually
- The program creates a Chrome profile locally but extensions require manual installation
- Settings and schedules in `schedule.json` will sync across team members
- Font files are included and will load automatically

## Why Extensions Don't Transfer

Chrome extensions are tied to:
- User-specific security tokens
- Installation metadata stored outside the profile folder
- Google account authentication
- Machine-specific permissions

**Solution**: Each team member should manually install required Chrome extensions when first running the program.
