# Resi Studio Automation (`resi-automation`)

Automate Resi Studio (`studio.resi.io`) workflows using direct REST API calls and local `ffmpeg` video transcoding. Designed for **Hermes Agent**, **Grok Bot**, **Cursor**, **Claude Code**, or any AI assistant environment.

---

## 📦 What's Included

* `resi.py` — Core Python client and CLI tool for Resi Studio.
* `SKILL.md` — Hermes / AI Agent Skill specification file.
* `SYSTEM_PROMPT.md` — System prompt for AI coding agents or Grok Bot.
* `.cursor/rules/resi.mdc` — Cursor IDE Rule definition.

---

## 🔒 Credentials & Configuration

**DO NOT commit Resi passwords or API tokens to git.**

Set your Resi Bearer Token in your environment or profile `.env` file (`~/.hermes/profiles/work/.env`):

```bash
export RESI_BEARER_TOKEN="your_token_here"
```

---

## 🚀 Quick Usage

### Installation
```bash
pip install requests
```

### List Schedules & Encoders
```bash
python3 resi.py list-schedules
python3 resi.py list-encoders
```

### View Stream Analytics & Viewers
```bash
python3 resi.py get-analytics
```

### Get Standalone Webplayer Link
```bash
python3 resi.py get-player-link <media_uuid>
```

### Transcode & Upload Video to Resi Library
Resi requires stereo 48kHz audio and a strict 2-second keyframe GOP interval. `resi.py` transcodes automatically:
```bash
python3 resi.py upload-video /path/to/video.mp4 --title "Sunday Service Sermon" --description "The Gospel of Luke"
```

---

## 🛠 Integrating with AI Assistants

### Hermes / AI Agent
Copy `SKILL.md` into your local skill directory:
```bash
cp SKILL.md ~/.hermes/skills/resi-automation/SKILL.md
```

### Cursor IDE
Copy `.cursor/rules/resi.mdc` into your project's `.cursor/rules/` directory.
