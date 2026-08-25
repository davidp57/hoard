"""
Pytest configuration — sets env vars BEFORE backend.main is imported,
so module-level constants (MEDIA_ROOT, DB_PATH) point to temp dirs.
"""

import os
import tempfile
from pathlib import Path

import pytest

# ── Temp directories created once for the whole test session ──────────────────
_tmp = tempfile.mkdtemp(prefix="mediabrowser_test_")
MEDIA_DIR = Path(_tmp) / "media"
DATA_DIR = Path(_tmp) / "data"
MEDIA_DIR.mkdir(parents=True)
DATA_DIR.mkdir(parents=True)

os.environ["MEDIA_ROOT"] = str(MEDIA_DIR)
os.environ["DB_PATH"] = str(DATA_DIR / "test.db")
# Disable file logging: the test suite must not write outside its temp dir.
os.environ["LOG_DIR"] = ""


# ── Shared fixtures ───────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def clean_media():
    """Remove all files/dirs created in MEDIA_DIR and reset DB after each test."""
    yield
    for item in MEDIA_DIR.iterdir():
        if item.is_dir():
            import shutil

            shutil.rmtree(item)
        else:
            item.unlink()
    import sqlite3 as _sq

    _conn = _sq.connect(str(DATA_DIR / "test.db"))
    try:
        _conn.execute("DELETE FROM progress")
        _conn.execute("DELETE FROM quick_folders")
        _conn.execute("DELETE FROM settings")
        _conn.execute("DELETE FROM initial_sweep_folders")
        _conn.execute("DELETE FROM home_roots")
        _conn.execute("DELETE FROM file_tags")
        _conn.execute("DELETE FROM segments")
        _conn.execute("DELETE FROM downloads")
        _conn.commit()
    finally:
        _conn.close()

    # Clear in-memory job store to prevent cross-test pollution
    import backend.main as _main

    _main._jobs.clear()


@pytest.fixture()
def video_file():
    """Create a minimal fake .mp4 file in MEDIA_ROOT and return its relative path."""
    f = MEDIA_DIR / "sample.mp4"
    f.write_bytes(b"\x00" * 1024)  # 1 KB dummy content
    return "sample.mp4"


@pytest.fixture()
def subdir_with_video():
    """Create a subdirectory containing a fake .mp4 file."""
    d = MEDIA_DIR / "series"
    d.mkdir()
    (d / "episode01.mp4").write_bytes(b"\x00" * 512)
    return "series"


@pytest.fixture()
def subdir_without_video():
    """Create a unique empty subdirectory (no video files) and clean it up afterwards."""
    import shutil
    import uuid

    name = f"empty_dir_{uuid.uuid4().hex}"
    d = MEDIA_DIR / name
    d.mkdir()
    try:
        yield name
    finally:
        if d.exists():
            shutil.rmtree(d)


@pytest.fixture(autouse=True, scope="session")
def _never_kill_the_test_runner():
    """Neutralise the real process-termination call for the whole session.

    /api/restart terminates the process with SIGTERM. A test that patches it
    and loses a race would let a lingering thread kill pytest itself, which
    surfaces as a job dying with no explanation. This is the backstop: no test,
    present or future, can reach the real call. Individual tests still patch
    what they need to assert on (BL-081).
    """
    import backend.main as _main

    original = _main._terminate_process
    _main._terminate_process = lambda: None
    yield
    _main._terminate_process = original


@pytest.fixture(autouse=True, scope="session")
def _forbid_real_yt_dlp():
    """Make the real yt-dlp unreachable for the whole session.

    Tests patch sys.modules["yt_dlp"] individually, but monkeypatch restores it
    when the test ends — while download threads it started may still be running.
    Such a thread then imports the *real* yt-dlp and issues a real HTTP request
    with no timeout, which hangs forever: locally the suite stalls at random, and
    on CI the "Run tests" step sits there until the 6-hour limit.

    yt-dlp is a genuine dependency (requirements-dev pulls backend/requirements),
    so it really is importable here. Replacing it session-wide means a late
    thread fails loudly instead of hanging, and monkeypatch restores to this stub
    rather than to the real module.
    """
    import sys
    from unittest.mock import MagicMock

    class _DownloadError(Exception):
        pass

    def _refuse(*args, **kwargs):
        raise RuntimeError("the real yt-dlp was reached from a test — patch sys.modules['yt_dlp']")

    stub = MagicMock()
    stub.YoutubeDL = MagicMock(side_effect=_refuse)
    stub.utils = MagicMock()
    stub.utils.DownloadError = _DownloadError

    saved = sys.modules.get("yt_dlp")
    sys.modules["yt_dlp"] = stub
    yield
    if saved is None:
        sys.modules.pop("yt_dlp", None)
    else:
        sys.modules["yt_dlp"] = saved
