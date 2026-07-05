# CKBS Scheduler

Desktop scheduler for school broadcast playback with YouTube playlist support, local audio playback, and weekly time slots.

<p>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.7%2B-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img alt="Tkinter" src="https://img.shields.io/badge/UI-Tkinter-0f766e?style=flat-square" />
  <img alt="Selenium" src="https://img.shields.io/badge/browser-Selenium-43B02A?style=flat-square&logo=selenium&logoColor=white" />
  <img alt="Audio" src="https://img.shields.io/badge/audio-pygame-f97316?style=flat-square" />
</p>

## Overview

CKBS Scheduler is a local desktop app for running recurring broadcast music. It combines a Tkinter operator UI, a weekly schedule file, Selenium-based YouTube playback, and pygame-backed local audio playback behind a single media controller.

## Features

| Area | Details |
| --- | --- |
| Scheduling | Weekly schedule with start and end times |
| Media | YouTube URLs and local audio files |
| Playback control | Unified controller prevents overlapping media sessions |
| UI | Tkinter interface with bundled Pretendard font files |
| Persistence | Schedule and settings stored as local JSON |
| Browser playback | Chrome profile support for YouTube sessions |

## Runtime Flow

```mermaid
flowchart LR
  UI["new_ui.py"] --> Scheduler["video_scheduler.py"]
  Scheduler --> Controller["media_controller.py"]
  Controller --> YouTube["play_video.py + Chrome"]
  Controller --> Audio["audio_player.py + pygame"]
  UI --> Schedule["schedule.json"]
  Font["Pretendard fonts"] --> UI
```

## Getting Started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python new_ui.py
```

On Windows, activate the virtual environment with:

```bat
.venv\Scripts\activate
```

## Repository Layout

```text
.
├── new_ui.py                 # Main Tkinter app
├── video_scheduler.py        # Schedule evaluation
├── media_controller.py       # Single playback coordinator
├── play_video.py             # YouTube playback automation
├── audio_player.py           # Local audio playback
├── anti_detection.py         # Chrome launch settings
├── font_manager.py           # Pretendard font loading
├── schedule.json             # Local schedule data
├── Pretendard-1.3.9/         # Bundled font files
└── Release/                  # Packaged user guide and release notes
```

## Chrome Profile Note

The app can create and reuse a local Chrome profile for YouTube playback. Browser extensions and account-specific Chrome state should be configured on each machine instead of being shared through Git.

## Build Notes

`CKBS_Scheduler.spec` is included for PyInstaller-based packaging. Validate playback on the target machine because Chrome, audio devices, and extension state are machine-specific.
