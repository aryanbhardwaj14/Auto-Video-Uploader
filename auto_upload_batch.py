import os, logging
logging.basicConfig(level=logging.INFO)

PAGE_ID = os.getenv("PAGE_ID")
PAGE_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
DROPBOX_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")

logging.info("DEBUG PAGE_ID present: %s", bool(PAGE_ID))
logging.info("DEBUG PAGE_ACCESS_TOKEN first 6: %s", (PAGE_TOKEN or "")[:6])
logging.info("DEBUG DROPBOX_ACCESS_TOKEN first 6: %s", (DROPBOX_TOKEN or "")[:6])

if not PAGE_ID or not PAGE_TOKEN or not DROPBOX_TOKEN:
    raise SystemExit("Missing environment variables!")
import os
import time
import logging
import requests
import dropbox
from random import sample

# logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# env (use consistent names)
PAGE_ID = os.getenv("PAGE_ID")
PAGE_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
# IMPORTANT: use DROPBOX_ACCESS_TOKEN (the name you already added in Railway)
DROPBOX_ACCESS_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")
VIDEO_DIR = os.getenv("VIDEO_DIR", "/AutoVideos")
UPLOADED_DIR = os.getenv("UPLOADED_DIR", "/uploaded")
UPLOAD_INTERVAL_HOURS = int(os.getenv("UPLOAD_INTERVAL_HOURS", "3"))
VIDEOS_PER_DAY = int(os.getenv("VIDEOS_PER_DAY", "8"))

# small safety check before creating client
if not (PAGE_ID and PAGE_TOKEN and DROPBOX_ACCESS_TOKEN):
    logging.error("Missing required environment variables. Please set PAGE_ID, PAGE_ACCESS_TOKEN and DROPBOX_ACCESS_TOKEN in Railway variables.")
    raise SystemExit(1)

# only create the Dropbox client after checking env
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
import os
import time
import random
import dropbox
import requests
from dotenv import load_dotenv

load_dotenv()

PAGE_ID = os.getenv("PAGE_ID")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
DROPBOX_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")
VIDEO_DIR = os.getenv("VIDEO_DIR", "/AutoVideos")

VIDEOS_PER_DAY = int(os.getenv("VIDEOS_PER_DAY", 8))
UPLOAD_INTERVAL_HOURS = int(os.getenv("UPLOAD_INTERVAL_HOURS", 3))

# 200 Viral Hashtags
HASHTAGS = [
    "#viral", "#reels", "#reelsindia", "#trending", "#foryou", "#fyp",
    "#bhabhi", "#gymvideos", "#ulluseries", "#romancevideo", "#love",
    "#statusvideo", "#tiktokindia", "#bollywood", "#funnyvideo",
] * 20  # replicate to reach 200 tags

dbx = dropbox.Dropbox(DROPBOX_TOKEN)

def get_videos():
    """Fetch video files from Dropbox folder."""
    response = dbx.files_list_folder(VIDEO_DIR)
    return [f for f in response.entries if isinstance(f, dropbox.files.FileMetadata) and f.name.endswith(".mp4")]

def download_video(path):
    """Download video bytes from Dropbox."""
    metadata, res = dbx.files_download(path)
    return res.content

def move_to_uploaded(path):
    """Move file to uploaded/ folder."""
    uploaded_path = f"{VIDEO_DIR}/uploaded/{os.path.basename(path)}"
    dbx.files_move_v2(path, uploaded_path, allow_shared_folder=True, autorename=True)

def generate_caption():
    """Random 7 hashtags."""
    return " ".join(random.sample(HASHTAGS, 7))

def upload_to_facebook(video_bytes, caption):
    """Upload the video to Facebook Page."""
    url = f"https://graph.facebook.com/{PAGE_ID}/videos"
    files = {"source": ("video.mp4", video_bytes, "video/mp4")}
    data = {"access_token": PAGE_ACCESS_TOKEN, "description": caption}

    response = requests.post(url, files=files, data=data)
    return response.json()

def run_job():
    print("🔍 Checking Dropbox for videos...")
    videos = get_videos()

    if not videos:
        print("❌ No videos found.")
        return

    video = videos[0]  # Take first video
    print(f"🎬 Uploading: {video.name}")

    video_bytes = download_video(video.path_lower)
    caption = generate_caption()

    result = upload_to_facebook(video_bytes, caption)
    print("📢 Facebook Response:", result)

    if "id" in result:
        print("✅ Uploaded successfully. Moving file...")
        move_to_uploaded(video.path_lower)
    else:
        print("❌ Upload failed.")

def main():
    print("🚀 Auto uploader started.")
    while True:
        run_job()
        print(f"⏳ Waiting {UPLOAD_INTERVAL_HOURS} hours for next upload...")
        time.sleep(UPLOAD_INTERVAL_HOURS * 3600)

if __name__ == "__main__":

    main()

