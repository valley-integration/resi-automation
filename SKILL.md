---
name: resi-automation
description: Automate Resi Studio video and stream tasks.
---

# Resi Studio Automation Skill

Use when managing Resi Studio streams, schedules, encoders, webplayer links, analytics, and media library uploads/downloads.

## Script Location
Script: `./resi.py`

## Credentials & Configuration
Set `RESI_EMAIL` and `RESI_PASSWORD` or `RESI_BEARER_TOKEN` in your environment or local `.env` file.
Never commit raw Resi user credentials, passwords, or bearer tokens to git.

```bash
export RESI_EMAIL="user@domain.com"
export RESI_PASSWORD="your_password_here"
```

## Features & Usage

### 1. List Schedules & Encoders
```bash
python3 resi.py list-schedules
python3 resi.py list-encoders
```

### 2. View Stream Analytics
```bash
python3 resi.py get-analytics
```

### 3. Stop a Live Stream / Encoder
```bash
python3 resi.py stop-encoder <encoder_uuid>
```

### 4. Generate Standalone Webplayer Link
```bash
python3 resi.py get-player-link <media_uuid>
```

### 5. Upload & Transcode Video to Resi Library
Resi requires stereo 48kHz audio and strict 2-second keyframe GOP intervals.
`resi.py` automatically transcodes local files via `ffmpeg`:
```bash
python3 resi.py upload-video /path/to/video.mp4 --title "Sunday Service Sermon" --description "Luke 12:35-48"
```

To skip transcoding if the file is already Resi-compliant:
```bash
python3 resi.py upload-video /path/to/video.mp4 --title "Pre-rendered Video" --no-transcode
```

### 6. Delete a Schedule
```bash
python3 resi.py delete-schedule <schedule_uuid>
```
