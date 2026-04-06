import hashlib
import ipaddress
import mimetypes
import os
import re
import shutil
import sqlite3
import string as _string
import subprocess
import tempfile
import threading
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ── Config ────────────────────────────────────────────────────────────────────
MEDIA_ROOT = Path(os.environ.get("MEDIA_ROOT", "/media"))
DB_PATH = Path(os.environ.get("DB_PATH", "/data/progress.db"))


def _resolve_ffmpeg() -> str:
    explicit = os.environ.get("FFMPEG_BIN")
    if explicit:
        return explicit
    if shutil.which("ffmpeg"):
        return "ffmpeg"
    # Search WinGet packages on Windows
    local_app = os.environ.get("LOCALAPPDATA", "")
    if local_app:
        winget_base = Path(local_app) / "Microsoft" / "WinGet" / "Packages"
        if winget_base.exists():
            for candidate in winget_base.rglob("ffmpeg.exe"):
                if "LosslessCut" not in str(candidate):
                    return str(candidate)
    return "ffmpeg"


FFMPEG_BIN = _resolve_ffmpeg()

# ── App ───────────────────────────────────────────────────────────────────────
VERSION = "1.0.0"

app = FastAPI(title="Hoard", version=VERSION)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# ── DB ────────────────────────────────────────────────────────────────────────
@contextmanager
def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                path TEXT PRIMARY KEY,
                position REAL DEFAULT 0,
                duration REAL DEFAULT 0,
                cut_in REAL DEFAULT NULL,
                cut_out REAL DEFAULT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Migration: add cut_in/cut_out if upgrading from older schema
        for col in ("cut_in", "cut_out"):
            try:
                conn.execute(f"ALTER TABLE progress ADD COLUMN {col} REAL DEFAULT NULL")
            except Exception:
                pass
        conn.execute("""
            CREATE TABLE IF NOT EXISTS quick_folders (
                path TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        conn.commit()


def reload_media_root():
    """Override MEDIA_ROOT from DB settings if set."""
    global MEDIA_ROOT
    with get_db() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key='media_root'").fetchone()
    if row:
        candidate = Path(row["value"])
        if candidate.exists() and candidate.is_dir():
            MEDIA_ROOT = candidate


init_db()
reload_media_root()
print(f"Hoard v{VERSION} — media: {MEDIA_ROOT}")


# ── Models ────────────────────────────────────────────────────────────────────
class ProgressUpdate(BaseModel):
    position: float
    duration: float
    cut_in: float | None = None
    cut_out: float | None = None


class MoveRequest(BaseModel):
    destination: str  # relative path from MEDIA_ROOT


class QuickFolderRequest(BaseModel):
    path: str  # relative path from MEDIA_ROOT


class MkdirRequest(BaseModel):
    name: str  # folder name only (no slashes)


class CutRequest(BaseModel):
    start: float  # seconds
    end: float  # seconds
    destination: str  # relative path from MEDIA_ROOT


class DownloadRequest(BaseModel):
    url: str  # URL to download
    cookies: str | None = None  # document.cookie string from the bookmarklet
    referer: str | None = None  # page URL (when url is a direct video source)
    title: str | None = None  # user-supplied filename hint (from bookmarklet page title)


# ── Job store (in-memory) ─────────────────────────────────────────────────────
_jobs: dict[str, dict] = {}


def _fmt_hms(s: float) -> str:
    s = int(s)
    h, m, sec = s // 3600, (s % 3600) // 60, s % 60
    return f"{h:02d}h{m:02d}m{sec:02d}s"


def _run_cut(
    job_id: str, source: Path, output: Path, start: float, end: float, dest_dir: Path
) -> None:
    job = _jobs[job_id]
    job["status"] = "running"
    duration = end - start
    cmd = [
        FFMPEG_BIN,
        "-y",
        "-ss",
        str(start),
        "-i",
        str(source),
        "-t",
        str(duration),
        "-c",
        "copy",
        "-avoid_negative_ts",
        "make_zero",
        str(output),
    ]
    try:
        proc = subprocess.Popen(
            cmd,
            stderr=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            universal_newlines=True,
            errors="replace",
        )
        for line in proc.stderr:  # type: ignore[union-attr]
            m = re.search(r"time=(\d+):(\d+):(\d+\.?\d*)", line)
            if m:
                elapsed = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
                job["progress"] = min(99, int(elapsed / duration * 100)) if duration > 0 else 99
        proc.wait()
        if proc.returncode != 0:
            job["status"] = "error"
            job["error"] = f"FFmpeg exited with code {proc.returncode}"
            return
        # Move source to destination
        dest_source = dest_dir / source.name
        if dest_source.resolve() != source.resolve():
            try:
                shutil.move(str(source), str(dest_source))
                old_rel = str(source.relative_to(MEDIA_ROOT))
                new_rel = str(dest_source.relative_to(MEDIA_ROOT))
                with get_db() as conn:
                    conn.execute("UPDATE progress SET path = ? WHERE path = ?", (new_rel, old_rel))
                    conn.commit()
            except Exception as e:
                job["move_error"] = str(e)
        job["status"] = "done"
        job["progress"] = 100
    except FileNotFoundError:
        job["status"] = "error"
        job["error"] = "FFmpeg introuvable — installez-le (winget install ffmpeg)"
    except Exception as e:
        job["status"] = "error"
        job["error"] = str(e)


def _run_move(job_id: str, source: Path, destination: Path) -> None:
    job = _jobs[job_id]
    job["status"] = "running"
    final_dest = (destination / source.name) if destination.is_dir() else destination
    final_dest.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(5):
        try:
            shutil.move(str(source), str(final_dest))
            break
        except PermissionError:
            if attempt < 4:
                time.sleep(0.6)
            else:
                job["status"] = "error"
                job["error"] = "File is locked by another process"
                return
        except Exception as e:
            job["status"] = "error"
            job["error"] = str(e)
            return
    old_rel = to_rel(source)
    new_rel = to_rel(final_dest)
    with get_db() as conn:
        conn.execute("UPDATE progress SET path = ? WHERE path = ?", (new_rel, old_rel))
        conn.commit()
    job["status"] = "done"
    job["progress"] = 100


# ── Download helpers ──────────────────────────────────────────────────────────


def _cookies_to_netscape(cookie_str: str, domain: str) -> str:
    """Convert a document.cookie string into Netscape cookies.txt format.

    The resulting text can be passed directly to yt-dlp as a cookies file.
    HttpOnly and Secure attributes are unknown client-side, so we use safe
    defaults (non-secure, session-only).

    The Netscape format requires the include_subdomains field to be TRUE only
    when the domain starts with a dot.  We always add the leading dot so that
    cookies are sent to all sub-domains of the host (better download success).
    """
    lines = ["# Netscape HTTP Cookie File"]
    # Domain must start with '.' for include_subdomains=TRUE to be valid
    cookie_domain = domain if domain.startswith(".") else f".{domain}"
    for pair in cookie_str.split(";"):
        pair = pair.strip()
        if "=" not in pair:
            continue
        name, _, value = pair.partition("=")
        name = name.strip()
        # Remove characters that would break the tab-delimited format
        value = value.strip().replace("\t", "").replace("\n", "").replace("\r", "")
        if not name:
            continue
        # domain  include_subdomain  path  secure  expiry  name  value
        lines.append(f"{cookie_domain}\tTRUE\t/\tFALSE\t0\t{name}\t{value}")
    return "\n".join(lines) + "\n"


def _sanitize_filename(name: str) -> str:
    """Strip characters that are invalid in filenames on Windows and Linux."""
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", name)
    name = name.strip(". ")
    return name[:180] or "video"


# Known video-hosting domains whose embed URLs yt-dlp can extract directly.
# Mirrors the bookmarklet's iframe-detection strategy.
_VIDEO_HOSTS_RE = re.compile(
    r"mediadelivery\.net|bunnycdn\.com|youtube\.com/embed"
    r"|player\.vimeo\.com|dailymotion\.com/embed",
    re.IGNORECASE,
)


def _sniff_video_source(page_url: str, cookies_str: str | None) -> str | None:
    """Fetch *page_url* as a browser would and look for an embedded video source.

    Mirrors the bookmarklet's server-side equivalent:
    1. ``<video src>`` / ``<source src>``  (skip blob: URLs)
    2. ``<iframe src>`` pointing to a known video-hosting domain

    Returns the best candidate URL or ``None`` if nothing is found.
    """
    from html.parser import HTMLParser
    from urllib.request import Request as _UrlRequest
    from urllib.request import urlopen

    class _Parser(HTMLParser):
        def __init__(self) -> None:
            super().__init__()
            self.video_srcs: list[str] = []
            self.iframe_srcs: list[str] = []

        def handle_starttag(self, tag: str, attrs: list) -> None:
            attrs_dict = dict(attrs)
            src = attrs_dict.get("src") or ""
            if tag in {"video", "source"}:
                if src and not src.startswith("blob:"):
                    self.video_srcs.append(src)
            elif tag == "iframe":
                if src and _VIDEO_HOSTS_RE.search(src):
                    self.iframe_srcs.append(src)

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        if cookies_str:
            headers["Cookie"] = cookies_str
        req = _UrlRequest(page_url, headers=headers)
        with urlopen(req, timeout=10) as resp:  # noqa: S310
            html_content = resp.read().decode("utf-8", errors="ignore")
        parser = _Parser()
        parser.feed(html_content)
        # Prefer iframe from known hosts (most reliable with yt-dlp extractors)
        if parser.iframe_srcs:
            return parser.iframe_srcs[0]
        if parser.video_srcs:
            return parser.video_srcs[0]
    except Exception:
        pass
    return None


def _run_download(
    job_id: str,
    url: str,
    output_dir: Path,
    cookies_str: str | None,
    cookies_file_path: str,
    referer: str | None = None,
    title: str | None = None,
) -> None:
    """Background worker: download a URL via yt-dlp and update the job dict."""
    import yt_dlp  # imported here to keep startup fast when yt-dlp isn't needed

    job = _jobs[job_id]
    job["status"] = "running"

    tmp_cookies_file: str | None = None

    try:
        # Build yt-dlp options
        # If a title hint was supplied (from bookmarklet page title), use it
        # directly as the output filename so we don't get the embed page title.
        if title:
            outtmpl = str(output_dir / f"{_sanitize_filename(title)}.%(ext)s")
        else:
            outtmpl = str(output_dir / "%(title)s.%(ext)s")

        ydl_opts: dict = {
            "outtmpl": outtmpl,
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "quiet": True,
            # Impersonate a real browser to bypass Cloudflare anti-bot challenges
            # (requires curl-cffi, see backend/requirements.txt)
            "impersonate": yt_dlp.networking.impersonate.ImpersonateTarget.from_str("chrome"),
            "no_warnings": True,
            "noprogress": False,
        }

        # When downloading a direct video URL extracted from a page, send the
        # page URL as Referer so CDNs that check the origin don't reject us.
        if referer:
            ydl_opts["http_headers"] = {"Referer": referer}

        # Cookies: prefer persistent file, fall back to bookmarklet cookies
        if cookies_file_path and Path(cookies_file_path).is_file():
            ydl_opts["cookiefile"] = cookies_file_path
        elif cookies_str:
            domain = urlparse(url).hostname or ""
            netscape_content = _cookies_to_netscape(cookies_str, domain)
            tmp_fd, tmp_cookies_file = tempfile.mkstemp(suffix=".txt", prefix="hoard_cookies_")
            try:
                with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                    f.write(netscape_content)
            except Exception:
                os.close(tmp_fd)
                raise
            ydl_opts["cookiefile"] = tmp_cookies_file

        def _progress_hook(d: dict) -> None:
            if d.get("status") == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                downloaded = d.get("downloaded_bytes") or 0
                if total > 0:
                    job["progress"] = min(99, int(downloaded / total * 100))
                # Update output filename as soon as we know it
                filename = d.get("filename") or d.get("tmpfilename", "")
                if filename:
                    job["output_name"] = Path(filename).name
            elif d.get("status") == "finished":
                job["progress"] = 99  # will be set to 100 when all hooks complete

        ydl_opts["progress_hooks"] = [_progress_hook]

        def _extract(target_url: str, opts: dict) -> None:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(target_url, download=True)
                if info:
                    final = ydl.prepare_filename(info)
                    if opts.get("merge_output_format"):
                        final = str(Path(final).with_suffix(f".{opts['merge_output_format']}"))
                    job["output_name"] = Path(final).name

        try:
            _extract(url, ydl_opts)
        except yt_dlp.utils.DownloadError as first_err:
            # If yt-dlp can't handle the page URL (no extractor), try fetching
            # the HTML to detect an embedded video/iframe source — same strategy
            # as the bookmarklet but running server-side.  Only attempt this when
            # no referer is set (meaning the URL is a plain page, not an already-
            # resolved direct video source sent by the bookmarklet).
            if "Unsupported URL" not in str(first_err) or referer:
                raise
            sniffed = _sniff_video_source(url, cookies_str)
            if not sniffed:
                raise
            # Use the original page URL as Referer for the CDN request
            ydl_opts["http_headers"] = {"Referer": url}
            job["source_name"] = sniffed
            _extract(sniffed, ydl_opts)

        job["status"] = "done"
        job["progress"] = 100

    except Exception as e:
        job["status"] = "error"
        job["error"] = str(e)
    finally:
        if tmp_cookies_file:
            try:
                os.unlink(tmp_cookies_file)
            except OSError:
                pass


# ── Helpers ───────────────────────────────────────────────────────────────────
VIDEO_EXTENSIONS = {
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".wmv",
    ".flv",
    ".m4v",
    ".ts",
    ".webm",
    ".mpg",
    ".mpeg",
}


def is_video(path: Path) -> bool:
    return path.suffix.lower() in VIDEO_EXTENSIONS


def safe_path(rel: str) -> Path:
    """Resolve and ensure path stays within MEDIA_ROOT."""
    resolved = (MEDIA_ROOT / rel).resolve()
    if not str(resolved).startswith(str(MEDIA_ROOT.resolve())):
        raise HTTPException(status_code=403, detail="Access denied")
    return resolved


def to_rel(path: Path) -> str:
    """Relative path from MEDIA_ROOT, always using forward slashes."""
    return str(path.relative_to(MEDIA_ROOT)).replace("\\", "/")


def get_progress(path: Path) -> dict:
    rel = to_rel(path)
    with get_db() as conn:
        row = conn.execute(
            "SELECT position, duration, cut_in, cut_out FROM progress WHERE path = ?", (rel,)
        ).fetchone()
    if row:
        pos, dur = row["position"], row["duration"]
        pct = (pos / dur * 100) if dur > 0 else 0
        return {
            "position": pos,
            "duration": dur,
            "percent": round(pct, 1),
            "cut_in": row["cut_in"],
            "cut_out": row["cut_out"],
        }
    return {"position": 0, "duration": 0, "percent": 0, "cut_in": None, "cut_out": None}


def get_folder_state(folder: Path, progress_map: dict) -> str:
    """Return 'new', 'inprogress', or 'seen' based on recursive video file progress."""
    video_files = [f for f in folder.rglob("*") if f.is_file() and is_video(f)]
    if not video_files:
        return "new"
    total = len(video_files)
    seen_count = sum(1 for vf in video_files if progress_map.get(to_rel(vf), 0) >= 90)
    inprogress_count = sum(1 for vf in video_files if 0 < progress_map.get(to_rel(vf), 0) < 90)
    if seen_count == total:
        return "seen"
    if seen_count > 0 or inprogress_count > 0:
        return "inprogress"
    return "new"


# ── Routes ────────────────────────────────────────────────────────────────────


@app.get("/api/files")
def list_files(path: str = ""):
    folder = safe_path(path)
    if not folder.exists() or not folder.is_dir():
        raise HTTPException(status_code=404, detail="Folder not found")

    with get_db() as conn:
        qf_paths = {
            row["path"] for row in conn.execute("SELECT path FROM quick_folders").fetchall()
        }
        rows = conn.execute(
            "SELECT path, position, duration FROM progress WHERE duration > 0"
        ).fetchall()
        progress_map = {row["path"]: row["position"] / row["duration"] * 100 for row in rows}

    # Gather items with stat cached
    items_with_stat = []
    for item in folder.iterdir():
        if item.name.startswith("."):
            continue
        try:
            st = item.stat()
        except PermissionError:
            continue
        items_with_stat.append((item, st))

    # Sort by modification time descending (atime excluded — changes on every rglob scan)
    items_with_stat.sort(key=lambda x: x[1].st_mtime, reverse=True)

    entries = []
    for item, st in items_with_stat:
        rel = to_rel(item)
        entry = {
            "name": item.name,
            "path": rel,
            "is_dir": item.is_dir(),
            "is_video": is_video(item) if item.is_file() else False,
            "size": st.st_size if item.is_file() else 0,
            "mtime": st.st_mtime,
            "is_quick_folder": rel in qf_paths if item.is_dir() else False,
            "folder_state": get_folder_state(item, progress_map) if item.is_dir() else None,
        }
        if entry["is_video"]:
            entry["progress"] = get_progress(item)
        entries.append(entry)

    # Breadcrumb
    parts = []
    current = Path(path)
    accumulated = Path("")
    for part in current.parts:
        accumulated = accumulated / part
        parts.append({"name": part, "path": str(accumulated).replace("\\", "/")})

    return {"path": path, "breadcrumb": parts, "entries": entries}


@app.get("/api/progress")
def read_progress(path: str):
    file = safe_path(path)
    if not file.exists():
        raise HTTPException(status_code=404)
    return get_progress(file)


@app.post("/api/progress")
def save_progress(path: str, body: ProgressUpdate):
    file = safe_path(path)
    rel = to_rel(file)
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO progress (path, position, duration, cut_in, cut_out, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(path) DO UPDATE SET
                position=excluded.position,
                duration=excluded.duration,
                cut_in=excluded.cut_in,
                cut_out=excluded.cut_out,
                updated_at=CURRENT_TIMESTAMP
        """,
            (rel, body.position, body.duration, body.cut_in, body.cut_out),
        )
        conn.commit()
    return {"ok": True}


@app.delete("/api/files")
def delete_file(path: str):
    target = safe_path(path)
    if not target.exists():
        raise HTTPException(status_code=404)
    try:
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()
    except PermissionError:
        raise HTTPException(status_code=423, detail="File is locked by another process") from None
    # Clean progress entry
    rel = to_rel(target)
    with get_db() as conn:
        conn.execute("DELETE FROM progress WHERE path = ?", (rel,))
        conn.commit()
    return {"ok": True}


@app.post("/api/files/move")
def move_file(path: str, body: MoveRequest):
    source = safe_path(path)
    destination = safe_path(body.destination)
    if not source.exists():
        raise HTTPException(status_code=404)
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        "id": job_id,
        "source_name": source.name,
        "output_name": destination.name,
        "status": "pending",
        "progress": 0,
        "error": None,
    }
    threading.Thread(
        target=_run_move,
        args=(job_id, source, destination),
        daemon=True,
    ).start()
    return {"job_id": job_id}


@app.post("/api/files/mkdir")
def make_directory(path: str, body: MkdirRequest):
    parent = safe_path(path)
    if not parent.is_dir():
        raise HTTPException(status_code=404, detail="Parent folder not found")
    name = body.name.strip()
    if not name or any(c in name for c in ("/", "\\", "\0")) or name in (".", ".."):
        raise HTTPException(status_code=400, detail="Invalid folder name")
    new_dir = parent / name
    if new_dir.exists():
        raise HTTPException(status_code=409, detail="Already exists")
    new_dir.mkdir()
    return {"ok": True}


# ── Cut / Jobs ────────────────────────────────────────────────────────────────


@app.post("/api/files/cut")
def cut_video(path: str, body: CutRequest):
    source = safe_path(path)
    if not source.exists() or not is_video(source):
        raise HTTPException(status_code=404, detail="Video not found")
    if body.end <= body.start:
        raise HTTPException(status_code=400, detail="end must be after start")
    dest_dir = safe_path(body.destination)
    if not dest_dir.is_dir():
        raise HTTPException(status_code=404, detail="Destination folder not found")
    out_name = f"{source.stem} [cut {_fmt_hms(body.start)}-{_fmt_hms(body.end)}]{source.suffix}"
    output = dest_dir / out_name
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        "id": job_id,
        "source_name": source.name,
        "output_name": out_name,
        "status": "pending",
        "progress": 0,
        "error": None,
    }
    threading.Thread(
        target=_run_cut,
        args=(job_id, source, output, body.start, body.end, dest_dir),
        daemon=True,
    ).start()
    return {"job_id": job_id}


@app.get("/api/jobs")
def list_jobs():
    return list(_jobs.values())


@app.delete("/api/jobs/{job_id}")
def delete_job(job_id: str):
    """Remove a job from the in-memory store (e.g. to dismiss a completed download)."""
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    del _jobs[job_id]
    return {"ok": True}


# ── Download ──────────────────────────────────────────────────────────────────

# Private / reserved IP ranges used for SSRF protection (RFC1918, loopback, link-local, CGN)
_PRIVATE_NETWORKS = (
    ipaddress.ip_network("127.0.0.0/8"),  # loopback
    ipaddress.ip_network("10.0.0.0/8"),  # RFC 1918
    ipaddress.ip_network("172.16.0.0/12"),  # RFC 1918 (not the full 172.x block)
    ipaddress.ip_network("192.168.0.0/16"),  # RFC 1918
    ipaddress.ip_network("169.254.0.0/16"),  # link-local
    ipaddress.ip_network("100.64.0.0/10"),  # carrier-grade NAT
    ipaddress.ip_network("::1/128"),  # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),  # IPv6 unique local
    ipaddress.ip_network("fe80::/10"),  # IPv6 link-local
)


def _validate_download_url(url: str) -> None:
    """Raise HTTPException 400 for clearly invalid or dangerous URLs."""
    if not url or not url.strip():
        raise HTTPException(status_code=400, detail="URL is required")
    try:
        parsed = urlparse(url)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid URL") from None
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Only http/https URLs are allowed")
    host = (parsed.hostname or "").lower()
    if not host:
        raise HTTPException(status_code=400, detail="URL has no host")
    # Reject localhost by name
    if host == "localhost":
        raise HTTPException(status_code=400, detail="Local network URLs are not allowed")
    # If the host is a literal IP address, reject private/reserved ranges using CIDR checks
    try:
        ip = ipaddress.ip_address(host)
        if any(ip in net for net in _PRIVATE_NETWORKS):
            raise HTTPException(status_code=400, detail="Local network URLs are not allowed")
    except ValueError:
        pass  # hostname (not a literal IP) — allow


@app.post("/api/download")
def start_download(body: DownloadRequest):
    """Start a yt-dlp download in the background and return a job_id."""
    _validate_download_url(body.url)

    with get_db() as conn:
        s = _read_all_settings(conn)

    download_folder_rel = s.get("download_folder", "Downloads")
    cookies_file_path = s.get("download_cookies_path", "")

    # Resolve (and create if needed) the download destination
    output_dir = safe_path(download_folder_rel)
    output_dir.mkdir(parents=True, exist_ok=True)

    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        "id": job_id,
        "type": "download",
        "url": body.url,
        "source_name": body.url,
        "output_name": "",
        "status": "pending",
        "progress": 0,
        "error": None,
    }
    threading.Thread(
        target=_run_download,
        args=(
            job_id,
            body.url,
            output_dir,
            body.cookies,
            cookies_file_path,
            body.referer,
            body.title,
        ),
        daemon=True,
    ).start()
    return {"job_id": job_id}


# ── Quick folders ─────────────────────────────────────────────────────────────


@app.get("/api/quick-folders")
def list_quick_folders():
    with get_db() as conn:
        rows = conn.execute("SELECT path FROM quick_folders ORDER BY created_at").fetchall()
    result = []
    for row in rows:
        p = MEDIA_ROOT / row["path"]
        if p.exists() and p.is_dir():
            result.append({"path": row["path"], "name": p.name})
    return result


@app.post("/api/quick-folders")
def add_quick_folder(body: QuickFolderRequest):
    target = safe_path(body.path)
    if not target.exists() or not target.is_dir():
        raise HTTPException(status_code=404, detail="Folder not found")
    rel = to_rel(target)
    with get_db() as conn:
        conn.execute("INSERT OR IGNORE INTO quick_folders (path) VALUES (?)", (rel,))
        conn.commit()
    return {"ok": True}


@app.delete("/api/quick-folders")
def remove_quick_folder(path: str):
    safe_path(path)  # validate path stays within MEDIA_ROOT
    rel = path.replace("\\", "/")
    with get_db() as conn:
        conn.execute("DELETE FROM quick_folders WHERE path = ?", (rel,))
        conn.commit()
    return {"ok": True}


# ── Filesystem browser (unrestricted, dirs only) ──────────────────────────────


@app.get("/api/browse")
def browse_filesystem(path: str = ""):
    """List subdirectories at any server path. Used by the home-folder picker."""
    if path == "":
        # Return filesystem roots
        if os.name == "nt":
            drives = [
                {"name": f"{d}:\\", "path": f"{d}:\\"}
                for d in _string.ascii_uppercase
                if Path(f"{d}:\\").exists()
            ]
            return {"path": "", "parent": None, "dirs": drives}
        else:
            current = Path("/")
    else:
        current = Path(path)

    if not current.exists() or not current.is_dir():
        raise HTTPException(status_code=404, detail="Path not found")

    dirs = []
    try:
        for d in sorted(current.iterdir()):
            if not d.is_dir() or d.name.startswith("."):
                continue
            try:
                d.stat()
                dirs.append({"name": d.name, "path": str(d).replace("\\", "/")})
            except (PermissionError, OSError):
                continue
    except PermissionError:
        raise HTTPException(status_code=403, detail="Access denied") from None

    # Compute parent
    # On Windows: drive root (e.g. C:\) -> "" (back to drive list)
    # On Linux: "/" -> None (no parent)
    if current.parent == current:
        parent = "" if os.name == "nt" else None
    else:
        parent = str(current.parent).replace("\\", "/")

    return {
        "path": str(current).replace("\\", "/"),
        "parent": parent,
        "dirs": dirs,
    }


# ── Settings ──────────────────────────────────────────────────────────────────

# Keys stored in the settings table (besides media_root which is handled separately)
_SETTINGS_KEYS = {
    "pin_hash",  # SHA-256 hex of PIN, empty string = disabled
    "privacy_timeout",  # minutes (int), 0 = disabled
    "watched_threshold",  # percent (int), default 90
    "home_folder",  # relative path from MEDIA_ROOT
    "sort_by",  # 'date' | 'name'
    "sort_dir",  # 'asc' | 'desc'
    "gesture_enabled",  # '1' | '0'
    "gesture_seek",  # '1' | '0'
    "gesture_volume",  # '1' | '0'
    "gesture_brightness",  # '1' | '0'
    "gesture_doubletap",  # '1' | '0'
    "gesture_edge_pct",  # int 10-35
    "gesture_swipe_threshold",  # px int, default 15
    "gesture_swipe_sensitivity",  # 'slow'|'medium'|'fast'
    "doubletap_left",  # seconds int
    "doubletap_right_bottom",  # seconds int
    "doubletap_right_mid",  # seconds int
    "doubletap_right_top",  # seconds int
    "download_folder",  # relative path from MEDIA_ROOT, default 'Downloads'
    "download_cookies_path",  # absolute path to a Netscape cookies.txt file, optional
}

_SETTINGS_DEFAULTS: dict[str, str] = {
    "pin_hash": "",
    "privacy_timeout": "10",
    "watched_threshold": "90",
    "home_folder": "",
    "sort_by": "date",
    "sort_dir": "desc",
    "gesture_enabled": "1",
    "gesture_seek": "1",
    "gesture_volume": "1",
    "gesture_brightness": "1",
    "gesture_doubletap": "1",
    "gesture_edge_pct": "20",
    "gesture_swipe_threshold": "15",
    "gesture_swipe_sensitivity": "medium",
    "doubletap_left": "30",
    "doubletap_right_bottom": "30",
    "doubletap_right_mid": "60",
    "doubletap_right_top": "90",
    "download_folder": "Downloads",
    "download_cookies_path": "",
}


def _read_all_settings(conn: sqlite3.Connection) -> dict[str, str]:
    rows = conn.execute("SELECT key, value FROM settings").fetchall()
    result = dict(_SETTINGS_DEFAULTS)
    for row in rows:
        result[row["key"]] = row["value"]
    return result


def _write_setting(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
        (key, value),
    )


class SettingsPayload(BaseModel):
    """All writeable settings in one payload. Fields absent from the request are left unchanged."""

    media_root: str | None = None
    pin: str | None = None  # raw PIN to hash; empty string = disable
    privacy_timeout: int | None = None
    watched_threshold: int | None = None
    home_folder: str | None = None
    sort_by: str | None = None
    sort_dir: str | None = None
    gesture_enabled: bool | None = None
    gesture_seek: bool | None = None
    gesture_volume: bool | None = None
    gesture_brightness: bool | None = None
    gesture_doubletap: bool | None = None
    gesture_edge_pct: int | None = None
    gesture_swipe_threshold: int | None = None
    gesture_swipe_sensitivity: str | None = None
    doubletap_left: int | None = None
    doubletap_right_bottom: int | None = None
    doubletap_right_mid: int | None = None
    doubletap_right_top: int | None = None
    download_folder: str | None = None
    download_cookies_path: str | None = None


@app.get("/api/settings")
def get_settings():
    with get_db() as conn:
        s = _read_all_settings(conn)
    # Never expose the raw hash; just tell the frontend whether a PIN is set
    result = {k: v for k, v in s.items() if k != "pin_hash"}
    result["pin_set"] = bool(s.get("pin_hash"))
    result["media_root"] = str(MEDIA_ROOT).replace("\\", "/")
    result["app_version"] = VERSION
    return result


@app.post("/api/settings")
def update_settings(body: SettingsPayload):
    global MEDIA_ROOT
    with get_db() as conn:
        if body.media_root is not None:
            new_root = Path(body.media_root)
            if not new_root.is_dir():
                raise HTTPException(
                    status_code=404, detail="Path does not exist or is not a directory"
                )
            MEDIA_ROOT = new_root
            _write_setting(conn, "media_root", str(new_root))

        if body.pin is not None:
            if body.pin == "":
                _write_setting(conn, "pin_hash", "")
            else:
                h = hashlib.sha256(body.pin.encode()).hexdigest()
                _write_setting(conn, "pin_hash", h)

        _simple: list[tuple[str, object]] = [
            ("privacy_timeout", body.privacy_timeout),
            ("watched_threshold", body.watched_threshold),
            ("home_folder", body.home_folder),
            ("sort_by", body.sort_by),
            ("sort_dir", body.sort_dir),
            ("gesture_swipe_threshold", body.gesture_swipe_threshold),
            ("gesture_edge_pct", body.gesture_edge_pct),
            ("gesture_swipe_sensitivity", body.gesture_swipe_sensitivity),
            ("doubletap_left", body.doubletap_left),
            ("doubletap_right_bottom", body.doubletap_right_bottom),
            ("doubletap_right_mid", body.doubletap_right_mid),
            ("doubletap_right_top", body.doubletap_right_top),
            ("download_folder", body.download_folder),
            ("download_cookies_path", body.download_cookies_path),
        ]
        for key, val in _simple:
            if val is not None:
                _write_setting(conn, key, str(val))

        _bools: list[tuple[str, bool | None]] = [
            ("gesture_enabled", body.gesture_enabled),
            ("gesture_seek", body.gesture_seek),
            ("gesture_volume", body.gesture_volume),
            ("gesture_brightness", body.gesture_brightness),
            ("gesture_doubletap", body.gesture_doubletap),
        ]
        for key, val in _bools:
            if val is not None:
                _write_setting(conn, key, "1" if val else "0")

        conn.commit()

    return {"ok": True}


@app.post("/api/settings/check-pin")
def check_pin(body: dict):
    """Returns {ok: true} if the supplied PIN matches, 401 otherwise."""
    pin = str(body.get("pin", ""))
    with get_db() as conn:
        s = _read_all_settings(conn)
    stored_hash = s.get("pin_hash", "")
    if not stored_hash:
        # No PIN set — always OK
        return {"ok": True}
    if hashlib.sha256(pin.encode()).hexdigest() == stored_hash:
        return {"ok": True}
    raise HTTPException(status_code=401, detail="Wrong PIN")


@app.get("/api/stream")
def stream_video(path: str, request: Request):
    file = safe_path(path)
    if not file.exists() or not is_video(file):
        raise HTTPException(status_code=404)

    file_size = file.stat().st_size
    mime_type = mimetypes.guess_type(str(file))[0] or "video/mp4"

    range_header = request.headers.get("range")
    if range_header:
        start, end = 0, file_size - 1
        range_str = range_header.replace("bytes=", "")
        parts = range_str.split("-")
        start = int(parts[0]) if parts[0] else 0
        end = int(parts[1]) if parts[1] else file_size - 1
        chunk_size = end - start + 1

        def iter_file():
            with open(file, "rb") as f:
                f.seek(start)
                remaining = chunk_size
                while remaining > 0:
                    chunk = f.read(min(65536, remaining))
                    if not chunk:
                        break
                    yield chunk
                    remaining -= len(chunk)

        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(chunk_size),
            "Content-Type": mime_type,
        }
        return StreamingResponse(iter_file(), status_code=206, headers=headers)

    def iter_full():
        with open(file, "rb") as f:
            while chunk := f.read(65536):
                yield chunk

    return StreamingResponse(
        iter_full(),
        media_type=mime_type,
        headers={"Accept-Ranges": "bytes", "Content-Length": str(file_size)},
    )


@app.get("/api/transcode")
def transcode_video(path: str):
    """Transcode to H.264/AAC on-the-fly for unsupported codecs (e.g. H.265)."""
    file = safe_path(path)
    if not file.exists() or not is_video(file):
        raise HTTPException(status_code=404)
    if not FFMPEG_BIN:
        raise HTTPException(status_code=503, detail="FFmpeg not available")

    cmd = [
        FFMPEG_BIN,
        "-i",
        str(file),
        "-c:v",
        "libx264",
        "-preset",
        "ultrafast",
        "-crf",
        "23",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-movflags",
        "frag_keyframe+empty_moov+faststart",
        "-f",
        "mp4",
        "pipe:1",
    ]

    def iter_transcode():
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        try:
            while True:
                chunk = proc.stdout.read(65536)
                if not chunk:
                    break
                yield chunk
        finally:
            proc.stdout.close()
            proc.wait()

    return StreamingResponse(
        iter_transcode(),
        media_type="video/mp4",
        headers={"Cache-Control": "no-cache"},
    )


# Serve frontend
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():

    @app.get("/")
    def serve_index():
        from fastapi.responses import FileResponse

        return FileResponse(
            frontend_path / "index.html",
            headers={"Cache-Control": "no-store"},
        )

    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
