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
        _conn.commit()
    finally:
        _conn.close()


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
