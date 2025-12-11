# Facebook Auto Uploader (Railway)


**Purpose:** Upload N videos per run from a Dropbox folder (or local folder) to a Facebook Page. Generates captions from filenames with optional Hindi/emoji templates. Moves processed files to an `uploaded/` folder.


**Goal:** Deploy to Railway in 5 minutes and run automatically using Railway Cron Jobs.


---


## What you get


- `auto_upload_batch.py` — production script (Dropbox + local support)
- `requirements.txt`
- Exact Railway environment variables to add
- Exact Cron expressions to schedule runs
- Caption customization built-in (edit templates in script)


---


## Where to put your videos


**Recommended (Dropbox - secure & cloud):**
- Upload all videos to the Dropbox folder: `/AutoVideos`
- The script will process oldest-first (FIFO). After upload, files move to `/AutoVideos/uploaded` automatically.


**Alternative (Local):**
- Create a folder in the repo or server: `/videos`
- The script will pick files from `LOCAL_VIDEO_DIR` and move them to `uploaded/` after processing.


---


## Required Railway environment variables (set in Project → Variables)

Notes:
- For 4 uploads spread across the day: set `UPLOADS_PER_RUN=1` and schedule the job every 6 hours (`0 */6 * * *`).
- For 4 uploads at once: set `UPLOADS_PER_RUN=4` and schedule once per day.


---


## Deploy steps (5 minutes)


1. Create a new GitHub repo and push the files from this package.
2. Go to https://railway.app, sign in with GitHub.
3. Create a new Project → Deploy from Repository → select your repo.
4. In Railway Project → Variables, add the environment variables above (PAGE_ID, PAGE_ACCESS_TOKEN, DROPBOX_TOKEN, etc.)
5. In Railway, open the **Cron Jobs** tab and create a new Cron Job with command: