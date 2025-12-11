import os
import time
import random
import logging

import requests
import dropbox
from dotenv import load_dotenv

# Load .env when running locally (Railway uses its own env vars)
load_dotenv()

# --------------------------------------------------
# Environment variables
# --------------------------------------------------
PAGE_ID = os.getenv("PAGE_ID")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")

# NEW: use refresh token + app key + app secret
DROPBOX_REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")
DROPBOX_APP_KEY = os.getenv("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = os.getenv("DROPBOX_APP_SECRET")

VIDEO_DIR = os.getenv("VIDEO_DIR", "/AutoVideos")
VIDEOS_PER_DAY = int(os.getenv("VIDEOS_PER_DAY", 8))
UPLOAD_INTERVAL_HOURS = int(os.getenv("UPLOAD_INTERVAL_HOURS", 3))

# 200 Viral Hashtags (simple repeat)
HASHTAGS = [
    "#viral", "#reels", "#reelsindia", "#trending", "#foryou", "#fyp",
    "#bhabhi", "#gymvideos", "#ulluseries", "#romancevideo", "#love",
    "#statusvideo", "#tiktokindia", "#bollywood", "#funnyvideo",
] * 20  # replicate to reach ~200 tags

# --------------------------------------------------
# Logging
# --------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

logging.info(
    "Env present: PAGE_ID=%s, PAGE_ACCESS_TOKEN=%s, "
    "DROPBOX_REFRESH_TOKEN=%s, DROPBOX_APP_KEY=%s, DROPBOX_APP_SECRET=%s",
    bool(PAGE_ID),
    bool(PAGE_ACCESS_TOKEN),
    bool(DROPBOX_REFRESH_TOKEN),
    bool(DROPBOX_APP_KEY),
    bool(DROPBOX_APP_SECRET),
)

# --------------------------------------------------
# Safety checks
# --------------------------------------------------
if not PAGE_ID or not PAGE_ACCESS_TOKEN:
    raise SystemExit("Missing PAGE_ID or PAGE_ACCESS_TOKEN env vars.")

if not (DROPBOX_REFRESH_TOKEN and DROPBOX_APP_KEY and DROPBOX_APP_SECRET):
    raise SystemExit(
        "Missing Dropbox env vars. Need DROPBOX_REFRESH_TOKEN, "
        "DROPBOX_APP_KEY and DROPBOX_APP_SECRET."
    )

# --------------------------------------------------
# Dropbox client (AUTO refresh using refresh token)
# --------------------------------------------------
dbx = dropbox.Dropbox(
    oauth2_refresh_token=DROPBOX_REFRESH_TOKEN,
    app_key=DROPBOX_APP_KEY,
    app_secret=DROPBOX_APP_SECRET,
)


# --------------------------------------------------
# Helper functions
# --------------------------------------------------
def get_videos():
    """Fetch .mp4 video files from Dropbox folder."""
    logging.info("Listing videos from Dropbox folder: %s", VIDEO_DIR)
    response = dbx.files_list_folder(VIDEO_DIR)
    return [
        f
        for f in response.entries
        if isinstance(f, dropbox.files.FileMetadata) and f.name.lower().endswith(".mp4")
    ]


def download_video(path):
    """Download video bytes from Dropbox."""
    logging.info("Downloading video from Dropbox: %s", path)
    metadata, res = dbx.files_download(path)
    return res.content


def move_to_uploaded(path):
    """Move file to uploaded/ folder inside VIDEO_DIR."""
    uploaded_path = f"{VIDEO_DIR}/uploaded/{os.path.basename(path)}"
    logging.info("Moving file to uploaded folder: %s -> %s", path, uploaded_path)
    dbx.files_move_v2(path, uploaded_path, allow_shared_folder=True, autorename=True)


def generate_caption():
    """Generate a caption with random 7 hashtags."""
    return " ".join(random.sample(HASHTAGS, 7))


def upload_to_facebook(video_bytes, caption):
    """Upload the video to Facebook Page."""
    url = f"https://graph.facebook.com/{PAGE_ID}/videos"
    files = {"source": ("video.mp4", video_bytes, "video/mp4")}
    data = {"access_token": PAGE_ACCESS_TOKEN, "description": caption}

    logging.info("Uploading video to Facebook...")
    response = requests.post(url, files=files, data=data)
    logging.info("Facebook upload status code: %s", response.status_code)
    try:
        return response.json()
    except Exception:
        logging.error("Failed to decode Facebook response JSON: %s", response.text)
        return {}


# --------------------------------------------------
# Main job
# --------------------------------------------------
def run_job():
    print("🔍 Checking Dropbox for videos...")
    videos = get_videos()

    if not videos:
        print("❌ No videos found.")
        return

    # Take first video
    video = videos[0]
    print(f"🎬 Uploading: {video.name}")

    video_bytes = download_video(video.path_lower)
    caption = generate_caption()

    result = upload_to_facebook(video_bytes, caption)
    print("📢 Facebook Response:", result)

    if "id" in result:
        print("✅ Uploaded successfully. Moving file...")
        move_to_uploaded(video.path_lower)
    else:
        print("❌ Upload failed, not moving file.")


def main():
    print("🚀 Auto uploader started.")
    while True:
        run_job()
        print(f"⏳ Waiting {UPLOAD_INTERVAL_HOURS} hours for next upload...")
        time.sleep(UPLOAD_INTERVAL_HOURS * 3600)


if __name__ == "__main__":
    main()
