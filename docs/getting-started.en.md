# Hoard — Getting Started

This tutorial walks you through installing Hoard and playing your first videos with watch-progress tracking.

---

## Step 1 — Start the Application

### Option A: locally with Python

```bash
git clone https://github.com/davidp57/hoard.git
cd hoard
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux / macOS
pip install -r requirements-dev.txt

# Replace with the path to your video folder
$env:MEDIA_ROOT = "C:\Videos"        # Windows PowerShell
export MEDIA_ROOT=/home/user/Videos  # Linux / macOS
export DB_PATH=/tmp/hoard.db

uvicorn backend.main:app --port 8000
```

### Option B: with Docker

```bash
mkdir dev-media
# Copy a few videos into dev-media/

docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

Open `http://localhost:8000` in your browser.

---

## Step 2 — Browse Files

When the app opens, you see the **list of files and folders** from your root folder.

- Click a **📁 folder** to open it.
- The **breadcrumb** at the top shows where you are. Click any element to navigate up.
- The **🏠** button at the left returns you to the root.

---

## Step 3 — Play a Video

Click on a **video file name** (or the ▶ button that appears on hover).

The player opens on the right (or full-screen on mobile). The video starts automatically.

### Basic controls

| Action | How |
|--------|-----|
| Pause / Play | Click **⏸ / ▶** or press `Space` |
| Seek forward / back | **▶▶ / ◀◀** buttons (±10 s) or `←` `→` keys |
| Volume | Slider or `↑` `↓` keys |
| Fullscreen | **⛶** button or `F` key |

---

## Step 4 — Stop and Resume

Stop the video at any point (close the tab, navigate away, lock your screen). Progress is saved **automatically every 5 seconds**.

When you return to the file, playback **resumes exactly where you left off**.

In the file list, the file now shows:
- A **yellow background**
- A **progress bar** and a percentage

Once you reach ≥ 90 % of the file, it turns **green** ("watched").

---

## Step 5 — Touch Gestures (touchscreen or mobile)

On the video image:

| Gesture | Action |
|---------|--------|
| **Tap** in the centre | Pause / Play |
| **Double-tap** left edge | − 30 s |
| **Double-tap** right edge (bottom) | + 30 s |
| **Double-tap** right edge (middle) | + 60 s |
| **Double-tap** right edge (top) | + 90 s |
| **Horizontal swipe** | Progressive seek (variable speed) |
| **Vertical swipe** right side | Volume |
| **Vertical swipe** left side | Brightness |

---

## Step 6 — Move a File

Hoard lets you move files to **quick folders** that you have previously pinned.

### Pin a folder

1. Navigate to the folder you want to pin.
2. Click the **📌** icon on the right of its name in the list.
3. The folder is now available as a quick destination.

### Move a file

1. Hover over (or long-press) the file you want to move.
2. Click the **📁** button.
3. In the modal, click the destination folder.

---

## Step 7 — Delete a File

1. Hover over (or long-press) the file to delete.
2. Click the **🗑** button.
3. Confirm deletion in the dialog.

---

## Going Further

- [Full user guide](user-guide.en.md) — all gestures, shortcuts, and features in detail.
- [Installation guide](installation.en.md) — Synology NAS deployment, advanced configuration.
- [Developer guide](developer.en.md) — architecture, API, contributing to the project.
