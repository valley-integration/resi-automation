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

Set your Resi configuration in your environment or local `.env` file:

```bash
# 1. Official API Credentials (for Encoders, Schedules, and Library Uploads)
export RESI_CLIENT_ID="your_client_id_here"
export RESI_CLIENT_SECRET="your_client_secret_here"
export RESI_CUSTOMER_ID="your_customer_uuid_here"

# 2. Studio Web Credentials (for Telemetry & Viewer Analytics)
export RESI_EMAIL="user@yourdomain.church"
export RESI_PASSWORD="your_password_here"

# 3. Optional Direct Session Token Override
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
