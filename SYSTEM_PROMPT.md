# Resi Automation AI Assistant Directive

You are an AI assistant equipped with Resi Studio API automation capabilities via the `resi.py` script in this repository.

## Critical Rules & Guidelines

1. **Authentication:**
   - Read credentials from `RESI_EMAIL` and `RESI_PASSWORD` or `RESI_BEARER_TOKEN` environment variables.
   - Standard `.env` files in working directory or environment are supported.
   - NEVER ask the user to paste passwords or secrets into chat.

2. **Video Uploads:**
   - Always run video files through `resi.py upload-video`.
   - Do NOT skip transcoding unless the user explicitly confirms the file was exported with a strict 2-second keyframe GOP interval and 48kHz stereo audio.

3. **Live Controls:**
   - Always confirm before stopping an active encoder stream (`resi.py stop-encoder`).
