# Resi Studio Automation (`resi-automation`)

Automate Resi Studio (`studio.resi.io`) workflows using direct REST API calls and local `ffmpeg` video transcoding. Designed for **Cursor**, **Grok Bot**, **Hermes**, **Claude Code**, or any AI assistant environment.

---

## 📦 What's Included

* `resi.py` — Core Python client and CLI tool for Resi Studio.
* `SKILL.md` — Universal AI Agent Skill specification file.
* `SYSTEM_PROMPT.md` — System prompt for AI coding agents or Grok Bot.
* `.cursor/rules/resi.mdc` — Cursor IDE Rule definition.

---

## 🔒 Credentials & Configuration

**DO NOT commit Resi passwords or API tokens to git.**

Set your Resi API Client ID and Secret in your environment or local `.env` file:

```bash
export RESI_CLIENT_ID="your_client_id_here"
export RESI_CLIENT_SECRET="your_client_secret_here"
export RESI_CUSTOMER_ID="a6d06bd5-b77d-5c77-4e86-a64f16400362" # Optional override
```

Or set a Bearer token directly:
```bash
export RESI_BEARER_TOKEN="your_token_here"
```

---

## 🚀 Quick Usage

### Installation
```bash
pip install requests python-dotenv
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

### Cursor IDE
Copy `.cursor/rules/resi.mdc` into your project's `.cursor/rules/` directory.

### AI Agent / Skill Frameworks
Copy `SKILL.md` or `SYSTEM_PROMPT.md` into your agent's skill directory.
