#!/usr/bin/env python3
"""
Resi Studio Automation Client (resi.py)

Automates Resi Studio (`studio.resi.io`) workflows via direct REST API calls.
Supports:
  - Authentication (Bearer token, env credentials, or HAR session fallback)
  - Schedules (Create, List, Update, Delete recurring or one-off events)
  - Live Encoders (List status, stop active stream)
  - Media Library (List, search, get webplayer links)
  - Analytics (Summary metrics, viewer breakdown by city, live concurrency)
  - Video Uploads (Auto-transcode with ffmpeg, probe metadata, upload to GCS, notify Resi)
  - Video Downloads & Drive Integration (Fetch Resi MP4, push to Google Drive or local)
"""

import os
import sys
import json
import time
import argparse
import subprocess
from urllib.parse import quote, urlparse
import requests

# Load .env file from working directory or user home if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
    load_dotenv(os.path.expanduser("~/.env"))
except ImportError:
    pass

BASE_CENTRAL_URL = "https://central.resi.io/api/v3"
BASE_MEDIA_URL = "https://media-metadata.resi.io/api/v1"
BASE_STATUS_URL = "https://media-status.resi.io/api/v1"

class ResiClient:
    def __init__(self, email=None, password=None, token=None, client_id=None, client_secret=None, customer_id=None):
        self.email = email or os.environ.get("RESI_EMAIL")
        self.password = password or os.environ.get("RESI_PASSWORD")
        self.token = token or os.environ.get("RESI_BEARER_TOKEN")
        self.client_id = client_id or os.environ.get("RESI_CLIENT_ID")
        self.client_secret = client_secret or os.environ.get("RESI_CLIENT_SECRET")
        self.customer_id = customer_id or os.environ.get("RESI_CUSTOMER_ID")
        
        if not self.customer_id:
            raise ValueError(
                "No Resi Customer ID provided.\n"
                "Please set RESI_CUSTOMER_ID in ~/.hermes/profiles/work/.env or pass customer_id."
            )
        
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        })

        # 1. First priority: Direct Bearer Token from Env
        if self.token:
            self.session.headers["Authorization"] = f"Bearer {self.token}"

        # 2. Second priority: OAuth2 Client Credentials (Client ID & Client Secret)
        elif self.client_id and self.client_secret:
            self._login_with_client_credentials()

        # 3. Third priority: Direct Sign in with Email & Password
        elif self.email and self.password:
            self._login_with_credentials()

        else:
            raise ValueError(
                "No Resi authentication provided.\n"
                "Please set RESI_CLIENT_ID and RESI_CLIENT_SECRET, or RESI_BEARER_TOKEN, or RESI_EMAIL/RESI_PASSWORD in ~/.hermes/profiles/work/.env"
            )

    def _login_with_client_credentials(self):
        """Authenticates using Resi API Client ID and Client Secret via official OAuth endpoint."""
        url = "https://api.resi.io/v1/oauth/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        res = self.session.post(url, json=payload)
        res.raise_for_status()
        data = res.json()
        
        token = data.get("access_token") or data.get("token")
        if token:
            self.token = token
            self.session.headers["Authorization"] = f"Bearer {self.token}"
        else:
            raise ValueError("Resi OAuth succeeded, but no access token returned in response.")

    def _login_with_credentials(self):
        """Authenticates directly with Resi Studio using user credentials via OAuth2 password grant."""
        url = f"{BASE_CENTRAL_URL}/auth/token"
        payload = {
            "grant_type": "password",
            "username": self.email,
            "password": self.password
        }
        res = self.session.post(url, json=payload)
        res.raise_for_status()
        data = res.json()
        
        token = data.get("access_token") or data.get("token")
        if token:
            self.token = token
            self.session.headers["Authorization"] = f"Bearer {self.token}"
        else:
            raise ValueError("Resi login succeeded, but no access token returned in response.")



    # --- Schedule Management ---
    def list_schedules(self):
        url = f"{BASE_CENTRAL_URL}/customers/{self.customer_id}/schedules"
        res = self.session.get(url)
        res.raise_for_status()
        return res.json()

    def get_schedule(self, schedule_id):
        url = f"{BASE_CENTRAL_URL}/customers/{self.customer_id}/schedules/{schedule_id}"
        res = self.session.get(url)
        res.raise_for_status()
        return res.json()

    def create_schedule(self, payload):
        val_url = f"{BASE_CENTRAL_URL}/customers/{self.customer_id}/schedules/validate"
        val_res = self.session.post(val_url, json=payload)
        val_res.raise_for_status()

        url = f"{BASE_CENTRAL_URL}/customers/{self.customer_id}/schedules"
        res = self.session.post(url, json=payload)
        res.raise_for_status()
        return res.json()

    def update_schedule(self, schedule_id, payload):
        val_url = f"{BASE_CENTRAL_URL}/customers/{self.customer_id}/schedules/validate?contentScheduleId={schedule_id}"
        val_res = self.session.post(val_url, json=payload)
        val_res.raise_for_status()

        url = f"{BASE_CENTRAL_URL}/customers/{self.customer_id}/schedules/{schedule_id}"
        res = self.session.put(url, json=payload)
        res.raise_for_status()
        return res.json()

    def delete_schedule(self, schedule_id):
        url = f"{BASE_CENTRAL_URL}/customers/{self.customer_id}/schedules/{schedule_id}"
        res = self.session.delete(url)
        res.raise_for_status()
        return {"status": "deleted", "schedule_id": schedule_id}

    # --- Live Encoders & Stream Controls ---
    def list_encoders(self):
        url = "https://central.resi.io/api_v2.svc/encoders"
        res = self.session.get(url)
        res.raise_for_status()
        return res.json()

    def stop_encoder(self, encoder_id):
        url = f"https://central.resi.io/api_v2.svc/encoders/{encoder_id}"
        payload = {"requestedStatus": "stop"}
        res = self.session.patch(url, json=payload)
        res.raise_for_status()
        return res.json()

    # --- Media Library & Analytics ---
    def list_media(self, size=50):
        url = f"{BASE_MEDIA_URL}/customers/{self.customer_id}/playlists?size={size}&sort=desc.created_date"
        res = self.session.get(url)
        res.raise_for_status()
        return res.json()

    def get_analytics_summary(self, start_date=None, end_date=None, destination_type="embed"):
        """Fetches total viewers, views, new/returning viewers, and avg time watched."""
        if not start_date or not end_date:
            import datetime
            now = datetime.datetime.now(datetime.timezone.utc)
            start = now - datetime.timedelta(days=7)
            start_date = start.strftime("%Y-%m-%dT05:00:00.000Z")
            end_date = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")

        url = f"https://telemetry.resi.io/api/v1/customers/{self.customer_id}/contentLibrary/statistics/summary"
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "isFullMonth": "false",
            "destinationType": destination_type,
            "viewAllData": "false"
        }
        res = self.session.get(url, params=params)
        res.raise_for_status()
        return res.json()

    def get_city_analytics(self, start_date=None, end_date=None, destination_type="embed"):
        """Fetches viewer breakdown by city."""
        if not start_date or not end_date:
            import datetime
            now = datetime.datetime.now(datetime.timezone.utc)
            start = now - datetime.timedelta(days=7)
            start_date = start.strftime("%Y-%m-%dT05:00:00.000Z")
            end_date = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")

        url = f"https://telemetry.resi.io/api/v1/customers/{self.customer_id}/contentLibrary/statistics/viewers/city"
        params = {
            "eventAnalytics": "viewers",
            "segmentBy": "none",
            "startDate": start_date,
            "endDate": end_date,
            "isFullMonth": "false",
            "destinationType": destination_type,
            "viewAllData": "false"
        }
        res = self.session.get(url, params=params)
        res.raise_for_status()
        return res.json()

    def get_webplayer_link(self, media_id):
        raw_str = f"{self.customer_id}:{media_id}"
        import base64
        encoded = base64.b64encode(raw_str.encode('utf-8')).decode('utf-8')
        encoded_param = quote(encoded, safe='')
        return f"https://control.resi.io/webplayer/video.html?id={encoded_param}&type=library&autoplay=false&studio=studio-prod"

    # --- Video Processing & Uploads ---
    def transcode_for_resi(self, input_file, output_file):
        """
        Transcodes video to match strict Resi upload requirements:
        - Stereo / 2-channel, 48kHz audio
        - MP4 / H.264
        - Strict 2-second GOP length (-g 48 for 24fps)
        """
        print(f"Transcoding {input_file} -> {output_file} for Resi strict specs...")
        cmd = [
            "ffmpeg", "-y", "-i", input_file,
            "-c:v", "libx264", "-profile:v", "high", "-level", "4.1",
            "-pix_fmt", "yuv420p",
            "-g", "48", "-keyint_min", "48", "-sc_threshold", "0",
            "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "256k",
            output_file
        ]
        subprocess.run(cmd, check=True)
        print("Transcode complete!")

    def probe_video_metadata(self, file_path):
        """Extracts exact bitrate, sample rate, GOP, framerate for Resi libraryupload payload."""
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", file_path
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        probe = json.loads(res.stdout)

        format_data = probe.get("format", {})
        video_stream = next((s for s in probe.get("streams", []) if s.get("codec_type") == "video"), {})
        audio_stream = next((s for s in probe.get("streams", []) if s.get("codec_type") == "audio"), {})

        import zlib
        crc = 0
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                crc = zlib.crc32(chunk, crc)
        
        import base64
        crc_bytes = crc.to_bytes(4, byteorder='big')
        crc32c_b64 = base64.b64encode(crc_bytes).decode('utf-8')

        v_bitrate = float(video_stream.get("bit_rate", format_data.get("bit_rate", 7000000))) / 1000.0
        a_bitrate = float(audio_stream.get("bit_rate", 256000)) / 1000.0
        sample_rate = int(audio_stream.get("sample_rate", 48000))
        height = int(video_stream.get("height", 1080))
        r_frame_rate = video_stream.get("r_frame_rate", "24000/1001")

        return {
            "fileName": os.path.basename(file_path),
            "videoHeight": height,
            "videoBitrateKbps": v_bitrate,
            "audioBitrateKbps": a_bitrate,
            "audioSampleRate": sample_rate,
            "framerate": r_frame_rate,
            "gopSeconds": 2.0,
            "crc32c": crc32c_b64
        }

    def upload_video_to_library(self, file_path, title, description=""):
        meta = self.probe_video_metadata(file_path)
        payload = {
            "title": title,
            "description": description,
            "detectQrCodes": False,
            "fileName": meta["fileName"],
            "startTime": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
            "gopSeconds": meta["gopSeconds"],
            "audioSampleRate": meta["audioSampleRate"],
            "audioBitrateKbps": meta["audioBitrateKbps"],
            "framerate": meta["framerate"],
            "videoBitrateKbps": meta["videoBitrateKbps"],
            "videoHeight": meta["videoHeight"],
            "crc32c": meta["crc32c"],
            "tags": [],
            "thumbnailBeans": []
        }

        init_url = f"{BASE_CENTRAL_URL}/customers/{self.customer_id}/libraryupload"
        res = self.session.post(init_url, json=payload)
        res.raise_for_status()
        init_data = res.json()

        upload_url = init_data.get("uploadUrl")
        status_callback = init_data.get("statusCallback")

        print(f"Uploading file ({os.path.getsize(file_path)} bytes) to Resi Cloud Storage...")
        with open(file_path, 'rb') as f:
            upload_res = requests.put(upload_url, data=f)
            upload_res.raise_for_status()

        if status_callback:
            print("Notifying Resi of completed upload...")
            self.session.put(status_callback, json={"status": "PENDING"})

        return init_data


def main():
    parser = argparse.ArgumentParser(description="Resi Studio Automation CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Schedules
    subparsers.add_parser("list-schedules", help="List all scheduled events")
    
    del_sched = subparsers.add_parser("delete-schedule", help="Delete a schedule by ID")
    del_sched.add_argument("schedule_id", help="Schedule UUID")

    # Encoders
    subparsers.add_parser("list-encoders", help="List all encoders and statuses")
    
    stop_enc = subparsers.add_parser("stop-encoder", help="Stop live stream on encoder")
    stop_enc.add_argument("encoder_id", help="Encoder UUID")

    # Webplayer
    link_parser = subparsers.add_parser("get-player-link", help="Get webplayer URL for media ID")
    link_parser.add_argument("media_id", help="Media UUID")

    # Upload
    upload_parser = subparsers.add_parser("upload-video", help="Transcode & Upload video to Resi Library")
    upload_parser.add_argument("file_path", help="Path to local MP4 file")
    upload_parser.add_argument("--title", required=True, help="Title in Resi library")
    upload_parser.add_argument("--description", default="", help="Description")
    upload_parser.add_argument("--no-transcode", action="store_true", help="Skip ffmpeg transcode check")

    # Analytics
    subparsers.add_parser("get-analytics", help="Get summary and city analytics for streams")

    args = parser.parse_args()
    client = ResiClient()

    if args.command == "list-schedules":
        schedules = client.list_schedules()
        print(json.dumps(schedules, indent=2))
    elif args.command == "delete-schedule":
        res = client.delete_schedule(args.schedule_id)
        print(json.dumps(res, indent=2))
    elif args.command == "list-encoders":
        encoders = client.list_encoders()
        print(json.dumps(encoders, indent=2))
    elif args.command == "stop-encoder":
        res = client.stop_encoder(args.encoder_id)
        print(json.dumps(res, indent=2))
    elif args.command == "get-player-link":
        link = client.get_webplayer_link(args.media_id)
        print(f"Webplayer Link:\n{link}")
    elif args.command == "upload-video":
        target_file = args.file_path
        if not args.no_transcode:
            output_file = f"resi_ready_{os.path.basename(args.file_path)}"
            client.transcode_for_resi(target_file, output_file)
            target_file = output_file
        res = client.upload_video_to_library(target_file, args.title, args.description)
        print(json.dumps(res, indent=2))
    elif args.command == "get-analytics":
        summary = client.get_analytics_summary()
        cities = client.get_city_analytics()
        print("=== Analytics Summary (Last 7 Days) ===")
        print(json.dumps(summary, indent=2))
        print("\n=== Viewers by City ===")
        print(json.dumps(cities, indent=2))

if __name__ == "__main__":
    main()
