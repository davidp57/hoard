"""Unit tests for MediaBrowser API endpoints."""

import sys
import threading
from unittest.mock import MagicMock

import pytest
from starlette.testclient import TestClient  # bundled with fastapi

# Env vars are already set by conftest.py before this import
from backend.main import MEDIA_ROOT, app

client = TestClient(app)


# ── /api/quick-folders ──────────────────────────────────────────────────────────────────


class TestQuickFolders:
    def test_empty_initially(self):
        resp = client.get("/api/quick-folders")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_add_and_list(self, subdir_with_video):
        client.post("/api/quick-folders", json={"path": subdir_with_video})
        resp = client.get("/api/quick-folders")
        data = resp.json()
        assert len(data) == 1
        assert data[0]["path"] == subdir_with_video
        assert data[0]["name"] == "series"

    def test_add_idempotent(self, subdir_with_video):
        client.post("/api/quick-folders", json={"path": subdir_with_video})
        client.post("/api/quick-folders", json={"path": subdir_with_video})
        assert len(client.get("/api/quick-folders").json()) == 1

    def test_remove(self, subdir_with_video):
        client.post("/api/quick-folders", json={"path": subdir_with_video})
        resp = client.delete(f"/api/quick-folders?path={subdir_with_video}")
        assert resp.status_code == 200
        assert client.get("/api/quick-folders").json() == []

    def test_add_file_rejected(self, video_file):
        resp = client.post("/api/quick-folders", json={"path": video_file})
        assert resp.status_code == 404

    def test_add_nonexistent_rejected(self):
        resp = client.post("/api/quick-folders", json={"path": "ghost_dir"})
        assert resp.status_code == 404

    def test_path_traversal_blocked(self):
        resp = client.post("/api/quick-folders", json={"path": "../../etc"})
        assert resp.status_code == 403

    def test_is_quick_folder_marked_in_file_list(self, subdir_with_video):
        client.post("/api/quick-folders", json={"path": subdir_with_video})
        entries = client.get("/api/files").json()["entries"]
        entry = next(e for e in entries if e["name"] == "series")
        assert entry["is_quick_folder"] is True

    def test_is_quick_folder_false_by_default(self, subdir_with_video):
        entries = client.get("/api/files").json()["entries"]
        entry = next(e for e in entries if e["name"] == "series")
        assert entry["is_quick_folder"] is False


# ── /api/files ────────────────────────────────────────────────────────────────


class TestListFiles:
    def test_root_empty(self):
        resp = client.get("/api/files")
        assert resp.status_code == 200
        data = resp.json()
        assert data["path"] == ""
        assert data["entries"] == []
        assert data["breadcrumb"] == []

    def test_root_lists_video(self, video_file):
        resp = client.get("/api/files")
        assert resp.status_code == 200
        names = [e["name"] for e in resp.json()["entries"]]
        assert "sample.mp4" in names

    def test_video_entry_has_progress(self, video_file):
        resp = client.get("/api/files")
        entry = next(e for e in resp.json()["entries"] if e["name"] == "sample.mp4")
        assert entry["is_video"] is True
        assert "progress" in entry
        assert entry["progress"]["percent"] == 0

    def test_directory_entry_has_no_progress(self, subdir_with_video):
        resp = client.get("/api/files")
        entry = next(e for e in resp.json()["entries"] if e["name"] == "series")
        assert entry["is_dir"] is True
        assert "progress" not in entry

    def test_subdir_listing(self, subdir_with_video):
        resp = client.get("/api/files?path=series")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["breadcrumb"]) == 1
        assert data["breadcrumb"][0]["name"] == "series"
        names = [e["name"] for e in data["entries"]]
        assert "episode01.mp4" in names

    def test_not_found(self):
        resp = client.get("/api/files?path=does_not_exist")
        assert resp.status_code == 404

    def test_path_traversal_blocked(self):
        resp = client.get("/api/files?path=../../etc/passwd")
        assert resp.status_code == 403

    def test_hidden_files_excluded(self):
        hidden = MEDIA_ROOT / ".hidden.mp4"
        hidden.write_bytes(b"\x00" * 64)
        resp = client.get("/api/files")
        names = [e["name"] for e in resp.json()["entries"]]
        assert ".hidden.mp4" not in names

    def test_entries_sorted_by_mtime_desc(self, subdir_with_video, video_file):
        """Entries should be sorted newest-first regardless of type."""
        resp = client.get("/api/files")
        entries = resp.json()["entries"]
        mtimes = [e["mtime"] for e in entries]
        assert mtimes == sorted(mtimes, reverse=True)

    def test_has_progress_false_on_new_dir(self, subdir_with_video):
        resp = client.get("/api/files")
        entry = next(e for e in resp.json()["entries"] if e["name"] == "series")
        assert entry["folder_state"] == "new"

    def test_has_progress_true_when_child_watched(self, subdir_with_video):
        # Save progress for the episode inside the subdir
        client.post(
            "/api/progress?path=series/episode01.mp4",
            json={"position": 300.0, "duration": 600.0},
        )
        resp = client.get("/api/files")
        entry = next(e for e in resp.json()["entries"] if e["name"] == "series")
        assert entry["folder_state"] == "inprogress"

    def test_folder_state_seen_when_all_watched(self, subdir_with_video):
        client.post(
            "/api/progress?path=series/episode01.mp4",
            json={"position": 580.0, "duration": 600.0},
        )
        resp = client.get("/api/files")
        entry = next(e for e in resp.json()["entries"] if e["name"] == "series")
        assert entry["folder_state"] == "seen"


# ── /api/progress ─────────────────────────────────────────────────────────────


class TestProgress:
    def test_no_record_returns_zero(self, video_file):
        resp = client.get(f"/api/progress?path={video_file}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["position"] == 0
        assert data["duration"] == 0
        assert data["percent"] == 0

    def test_save_and_read(self, video_file):
        # Save
        resp = client.post(
            f"/api/progress?path={video_file}",
            json={"position": 120.5, "duration": 600.0},
        )
        assert resp.status_code == 200
        assert resp.json()["ok"] is True

        # Read back
        resp = client.get(f"/api/progress?path={video_file}")
        data = resp.json()
        assert data["position"] == 120.5
        assert data["duration"] == 600.0
        assert data["percent"] == pytest.approx(20.1, abs=0.1)

    def test_update_overwrites(self, video_file):
        client.post(f"/api/progress?path={video_file}", json={"position": 10, "duration": 100})
        client.post(f"/api/progress?path={video_file}", json={"position": 50, "duration": 100})
        resp = client.get(f"/api/progress?path={video_file}")
        assert resp.json()["position"] == 50

    def test_progress_not_found(self):
        resp = client.get("/api/progress?path=ghost.mp4")
        assert resp.status_code == 404

    def test_path_traversal_on_progress(self):
        resp = client.get("/api/progress?path=../../etc/passwd")
        assert resp.status_code == 403


# ── /api/files DELETE ─────────────────────────────────────────────────────────


class TestDeleteFile:
    def test_delete_file(self, video_file):
        resp = client.delete(f"/api/files?path={video_file}")
        assert resp.status_code == 200
        assert not (MEDIA_ROOT / video_file).exists()

    def test_delete_also_clears_progress(self, video_file):
        client.post(f"/api/progress?path={video_file}", json={"position": 10, "duration": 100})
        client.delete(f"/api/files?path={video_file}")
        # File gone, progress should return 404 (file does not exist)
        resp = client.get(f"/api/progress?path={video_file}")
        assert resp.status_code == 404

    def test_delete_directory(self, subdir_with_video):
        resp = client.delete(f"/api/files?path={subdir_with_video}")
        assert resp.status_code == 200
        assert not (MEDIA_ROOT / subdir_with_video).exists()

    def test_delete_not_found(self):
        resp = client.delete("/api/files?path=ghost.mp4")
        assert resp.status_code == 404

    def test_delete_path_traversal_blocked(self):
        resp = client.delete("/api/files?path=../../important")
        assert resp.status_code == 403


# ── /api/files/move ───────────────────────────────────────────────────────────


class TestMoveFile:
    def _sync_thread(self, monkeypatch):
        """Patch threading.Thread to run the target synchronously (no background thread)."""
        import threading as _threading

        class SyncThread:
            def __init__(self, target, args, daemon=True):
                self._target = target
                self._args = args

            def start(self):
                self._target(*self._args)

        monkeypatch.setattr(_threading, "Thread", SyncThread)

    def test_move_to_subdir(self, video_file, subdir_with_video, monkeypatch):
        self._sync_thread(monkeypatch)
        resp = client.post(
            f"/api/files/move?path={video_file}",
            json={"destination": subdir_with_video},
        )
        assert resp.status_code == 200
        assert "job_id" in resp.json()
        assert (MEDIA_ROOT / subdir_with_video / "sample.mp4").exists()
        assert not (MEDIA_ROOT / video_file).exists()

    def test_move_not_found(self):
        resp = client.post(
            "/api/files/move?path=ghost.mp4",
            json={"destination": "series"},
        )
        assert resp.status_code == 404

    def test_move_updates_progress_key(self, video_file, subdir_with_video, monkeypatch):
        self._sync_thread(monkeypatch)
        client.post(f"/api/progress?path={video_file}", json={"position": 30, "duration": 200})
        client.post(f"/api/files/move?path={video_file}", json={"destination": subdir_with_video})
        resp = client.get("/api/progress?path=series/sample.mp4")
        assert resp.status_code == 200
        assert resp.json()["position"] == 30


# ── /api/stream ───────────────────────────────────────────────────────────────


class TestStream:
    def test_stream_returns_200(self, video_file):
        resp = client.get(f"/api/stream?path={video_file}")
        assert resp.status_code == 200
        assert "video" in resp.headers["content-type"]

    def test_stream_range_returns_206(self, video_file):
        resp = client.get(f"/api/stream?path={video_file}", headers={"Range": "bytes=0-99"})
        assert resp.status_code == 206
        assert resp.headers["content-range"].startswith("bytes 0-99/")
        assert len(resp.content) == 100

    def test_stream_not_found(self):
        resp = client.get("/api/stream?path=ghost.mp4")
        assert resp.status_code == 404

    def test_stream_non_video_rejected(self):
        txt = MEDIA_ROOT / "readme.txt"
        txt.write_text("hello")
        resp = client.get("/api/stream?path=readme.txt")
        assert resp.status_code == 404

    def test_stream_path_traversal_blocked(self):
        resp = client.get("/api/stream?path=../../etc/passwd")
        assert resp.status_code == 403


# ── /api/browse ───────────────────────────────────────────────────────────────


class TestBrowse:
    def test_browse_root_returns_dirs(self):
        resp = client.get("/api/browse?path=")
        assert resp.status_code == 200
        data = resp.json()
        assert "dirs" in data
        # Every entry must have name and path
        for d in data["dirs"]:
            assert "name" in d
            assert "path" in d

    def test_browse_subdir(self, subdir_with_video):
        resp = client.get(f"/api/browse?path={MEDIA_ROOT}")
        assert resp.status_code == 200
        names = [d["name"] for d in resp.json()["dirs"]]
        assert "series" in names

    def test_browse_not_found(self):
        resp = client.get("/api/browse?path=/does/not/exist/anywhere")
        assert resp.status_code == 404

    def test_browse_parent_is_none_at_root(self):
        resp = client.get("/api/browse?path=")
        assert resp.json()["parent"] is None


# ── /api/settings ─────────────────────────────────────────────────────────────


class TestSettings:
    def test_get_settings_returns_media_root(self):
        resp = client.get("/api/settings")
        assert resp.status_code == 200
        assert "media_root" in resp.json()

    def test_update_media_root(self, tmp_path):
        new_root = tmp_path / "new_media"
        new_root.mkdir()
        resp = client.post("/api/settings", json={"media_root": str(new_root)})
        assert resp.status_code == 200
        assert resp.json()["ok"] is True
        # Restore original for subsequent tests
        client.post("/api/settings", json={"media_root": str(MEDIA_ROOT)})

    def test_update_media_root_not_found(self):
        resp = client.post("/api/settings", json={"media_root": "/does/not/exist"})
        assert resp.status_code == 404


# ── /api/files/mkdir ──────────────────────────────────────────────────────────


class TestMkdir:
    def test_mkdir_creates_folder(self):
        resp = client.post("/api/files/mkdir?path=", json={"name": "new_folder"})
        assert resp.status_code == 200
        assert (MEDIA_ROOT / "new_folder").is_dir()
        (MEDIA_ROOT / "new_folder").rmdir()

    def test_mkdir_in_subdir(self, subdir_with_video):
        resp = client.post(f"/api/files/mkdir?path={subdir_with_video}", json={"name": "sub"})
        assert resp.status_code == 200
        assert (MEDIA_ROOT / subdir_with_video / "sub").is_dir()

    def test_mkdir_conflict(self):
        (MEDIA_ROOT / "existing").mkdir(exist_ok=True)
        resp = client.post("/api/files/mkdir?path=", json={"name": "existing"})
        assert resp.status_code == 409
        (MEDIA_ROOT / "existing").rmdir()

    def test_mkdir_invalid_name(self):
        resp = client.post("/api/files/mkdir?path=", json={"name": "../escape"})
        assert resp.status_code == 400

    def test_mkdir_parent_not_found(self):
        resp = client.post("/api/files/mkdir?path=ghost_dir", json={"name": "sub"})
        assert resp.status_code == 404


# ── /api/files/cut + /api/jobs ───────────────────────────────────────────────


class TestCut:
    def _noop_thread(self, monkeypatch):
        import threading as _threading

        monkeypatch.setattr(
            _threading,
            "Thread",
            lambda target, args, daemon: type("T", (), {"start": lambda self: None})(),
        )

    def test_cut_returns_job_id(self, video_file, monkeypatch):
        self._noop_thread(monkeypatch)
        (MEDIA_ROOT / "dest").mkdir(exist_ok=True)
        resp = client.post(
            f"/api/files/cut?path={video_file}",
            json={"start": 0.0, "end": 10.0, "destination": "dest"},
        )
        assert resp.status_code == 200
        assert "job_id" in resp.json()

    def test_cut_invalid_range(self, video_file):
        (MEDIA_ROOT / "dest").mkdir(exist_ok=True)
        resp = client.post(
            f"/api/files/cut?path={video_file}",
            json={"start": 20.0, "end": 10.0, "destination": "dest"},
        )
        assert resp.status_code == 400

    def test_cut_dest_not_found(self, video_file):
        resp = client.post(
            f"/api/files/cut?path={video_file}",
            json={"start": 0.0, "end": 10.0, "destination": "no_such_dir"},
        )
        assert resp.status_code == 404

    def test_cut_source_not_found(self):
        (MEDIA_ROOT / "dest").mkdir(exist_ok=True)
        resp = client.post(
            "/api/files/cut?path=ghost.mp4",
            json={"start": 0.0, "end": 10.0, "destination": "dest"},
        )
        assert resp.status_code == 404

    def test_jobs_list(self, video_file, monkeypatch):
        self._noop_thread(monkeypatch)
        (MEDIA_ROOT / "dest").mkdir(exist_ok=True)
        client.post(
            f"/api/files/cut?path={video_file}",
            json={"start": 0.0, "end": 5.0, "destination": "dest"},
        )
        resp = client.get("/api/jobs")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        assert len(resp.json()) >= 1


# ── /api/download ─────────────────────────────────────────────────────────────


def _make_yt_dlp_mock(output_name: str = "video.mp4") -> MagicMock:
    """Return a sys.modules-compatible yt_dlp mock."""
    ydl_instance = MagicMock()
    ydl_instance.__enter__ = MagicMock(return_value=ydl_instance)
    ydl_instance.__exit__ = MagicMock(return_value=False)
    ydl_instance.extract_info = MagicMock(return_value={"title": "test", "ext": "mp4"})
    ydl_instance.prepare_filename = MagicMock(return_value=f"/tmp/{output_name}")

    class _FakeDownloadError(Exception):
        pass

    mock_module = MagicMock()
    mock_module.YoutubeDL = MagicMock(return_value=ydl_instance)
    mock_module.utils = MagicMock()
    mock_module.utils.DownloadError = _FakeDownloadError
    return mock_module


def _sync_thread_patch(monkeypatch):
    """Run threading.Thread targets synchronously."""

    class SyncThread:
        def __init__(self, target, args, daemon=True):
            self._target = target
            self._args = args

        def start(self):
            self._target(*self._args)

    monkeypatch.setattr(threading, "Thread", SyncThread)


class TestDownload:
    def test_valid_url_returns_job_id(self, monkeypatch):
        monkeypatch.setitem(sys.modules, "yt_dlp", _make_yt_dlp_mock())
        # No background thread needed — just check the response
        resp = client.post("/api/download", json={"url": "https://example.com/video"})
        assert resp.status_code == 200
        data = resp.json()
        assert "job_id" in data

    def test_empty_url_rejected(self):
        resp = client.post("/api/download", json={"url": ""})
        assert resp.status_code == 400

    def test_file_scheme_rejected(self):
        resp = client.post("/api/download", json={"url": "file:///etc/passwd"})
        assert resp.status_code == 400

    def test_localhost_url_rejected(self):
        resp = client.post("/api/download", json={"url": "http://localhost/video"})
        assert resp.status_code == 400

    def test_private_ip_rejected(self):
        resp = client.post("/api/download", json={"url": "http://192.168.1.1/video"})
        assert resp.status_code == 400

    def test_download_creates_output_dir(self, monkeypatch):
        monkeypatch.setitem(sys.modules, "yt_dlp", _make_yt_dlp_mock())
        _sync_thread_patch(monkeypatch)
        # Set a custom download folder that does not exist yet
        client.post("/api/settings", json={"download_folder": "MyDownloads"})
        resp = client.post("/api/download", json={"url": "https://example.com/video"})
        assert resp.status_code == 200
        from backend.main import MEDIA_ROOT

        assert (MEDIA_ROOT / "MyDownloads").is_dir()

    def test_download_job_appears_in_jobs_list(self, monkeypatch):
        monkeypatch.setitem(sys.modules, "yt_dlp", _make_yt_dlp_mock())

        class NoopThread:
            def __init__(self, target, args, daemon=True):
                pass

            def start(self):
                pass

        monkeypatch.setattr(threading, "Thread", NoopThread)
        client.post("/api/download", json={"url": "https://example.com/video"})
        jobs = client.get("/api/jobs").json()
        download_jobs = [j for j in jobs if j.get("type") == "download"]
        assert len(download_jobs) >= 1
        assert download_jobs[-1]["url"] == "https://example.com/video"

    def test_download_done_after_sync_thread(self, monkeypatch):
        monkeypatch.setitem(sys.modules, "yt_dlp", _make_yt_dlp_mock())
        _sync_thread_patch(monkeypatch)
        resp = client.post("/api/download", json={"url": "https://example.com/video"})
        job_id = resp.json()["job_id"]
        jobs = {j["id"]: j for j in client.get("/api/jobs").json()}
        assert jobs[job_id]["status"] == "done"
        assert jobs[job_id]["progress"] == 100

    def test_download_error_on_yt_dlp_failure(self, monkeypatch):
        mock_yt_dlp = _make_yt_dlp_mock()
        mock_yt_dlp.YoutubeDL.return_value.extract_info.side_effect = Exception("network error")
        monkeypatch.setitem(sys.modules, "yt_dlp", mock_yt_dlp)
        _sync_thread_patch(monkeypatch)
        resp = client.post("/api/download", json={"url": "https://example.com/video"})
        job_id = resp.json()["job_id"]
        jobs = {j["id"]: j for j in client.get("/api/jobs").json()}
        assert jobs[job_id]["status"] == "error"
        assert "network error" in jobs[job_id]["error"]

    def test_download_with_cookies_str(self, monkeypatch):
        """Cookies string should be passed to yt-dlp via a temp file."""
        captured_opts = {}

        def mock_ytdl_init(opts):
            captured_opts.update(opts)
            return _make_yt_dlp_mock().YoutubeDL.return_value

        mock_module = MagicMock()
        mock_module.YoutubeDL = MagicMock(side_effect=mock_ytdl_init)
        monkeypatch.setitem(sys.modules, "yt_dlp", mock_module)
        _sync_thread_patch(monkeypatch)
        client.post(
            "/api/download",
            json={"url": "https://example.com/video", "cookies": "session=abc; token=xyz"},
        )
        assert "cookiefile" in captured_opts

    def test_download_cookies_persistent_file_takes_precedence(self, monkeypatch, tmp_path):
        """When the configured cookies file exists it takes precedence over the inline string."""
        cookies_file = tmp_path / "cookies.txt"
        cookies_file.write_text("persisted=1", encoding="utf-8")

        client.post(
            "/api/settings",
            json={"download_cookies_path": str(cookies_file)},
        )

        captured_opts = {}

        def mock_ytdl_init(opts):
            captured_opts.update(opts)
            return _make_yt_dlp_mock().YoutubeDL.return_value

        mock_module = MagicMock()
        mock_module.YoutubeDL = MagicMock(side_effect=mock_ytdl_init)
        monkeypatch.setitem(sys.modules, "yt_dlp", mock_module)
        _sync_thread_patch(monkeypatch)
        client.post(
            "/api/download",
            json={"url": "https://example.com/video", "cookies": "session=abc"},
        )
        assert captured_opts.get("cookiefile") == str(cookies_file)

        # Reset setting so other tests are unaffected
        client.post("/api/settings", json={"download_cookies_path": ""})

    def test_download_cookies_fallback_when_persistent_file_missing(self, monkeypatch, tmp_path):
        """When the configured cookies file does not exist, fall back to the inline cookies."""
        missing = tmp_path / "missing_cookies.txt"
        assert not missing.exists()

        client.post(
            "/api/settings",
            json={"download_cookies_path": str(missing)},
        )

        captured_opts = {}

        def mock_ytdl_init(opts):
            captured_opts.update(opts)
            return _make_yt_dlp_mock().YoutubeDL.return_value

        mock_module = MagicMock()
        mock_module.YoutubeDL = MagicMock(side_effect=mock_ytdl_init)
        monkeypatch.setitem(sys.modules, "yt_dlp", mock_module)
        _sync_thread_patch(monkeypatch)
        client.post(
            "/api/download",
            json={"url": "https://example.com/video", "cookies": "session=abc"},
        )
        # A temp file should be used — not the missing configured path
        assert "cookiefile" in captured_opts
        assert captured_opts["cookiefile"] != str(missing)

        # Reset setting so other tests are unaffected
        client.post("/api/settings", json={"download_cookies_path": ""})

    def test_download_settings_persisted(self):
        resp = client.post(
            "/api/settings",
            json={"download_folder": "WebVideos", "download_cookies_path": "/data/cookies.txt"},
        )
        assert resp.status_code == 200
        settings = client.get("/api/settings").json()
        assert settings["download_folder"] == "WebVideos"
        assert settings["download_cookies_path"] == "/data/cookies.txt"

    def test_download_referer_sets_http_headers(self, monkeypatch):
        """When referer is provided, yt-dlp should receive an http_headers dict."""
        captured_opts = {}

        def mock_ytdl_init(opts):
            captured_opts.update(opts)
            return _make_yt_dlp_mock().YoutubeDL.return_value

        mock_module = MagicMock()
        mock_module.YoutubeDL = MagicMock(side_effect=mock_ytdl_init)
        monkeypatch.setitem(sys.modules, "yt_dlp", mock_module)
        _sync_thread_patch(monkeypatch)
        client.post(
            "/api/download",
            json={
                "url": "https://cdn.example.com/video.mp4",
                "referer": "https://example.com/posts/123",
            },
        )
        assert (
            captured_opts.get("http_headers", {}).get("Referer") == "https://example.com/posts/123"
        )

    def test_download_no_referer_no_http_headers(self, monkeypatch):
        """When referer is not provided, http_headers should not be set."""
        captured_opts = {}

        def mock_ytdl_init(opts):
            captured_opts.update(opts)
            return _make_yt_dlp_mock().YoutubeDL.return_value

        mock_module = MagicMock()
        mock_module.YoutubeDL = MagicMock(side_effect=mock_ytdl_init)
        monkeypatch.setitem(sys.modules, "yt_dlp", mock_module)
        _sync_thread_patch(monkeypatch)
        client.post(
            "/api/download",
            json={"url": "https://example.com/video"},
        )
        assert "http_headers" not in captured_opts

    def test_download_title_overrides_outtmpl(self, monkeypatch):
        """When title is provided, outtmpl should use the sanitized title instead of %(title)s."""
        captured_opts = {}

        def mock_ytdl_init(opts):
            captured_opts.update(opts)
            return _make_yt_dlp_mock().YoutubeDL.return_value

        mock_module = MagicMock()
        mock_module.YoutubeDL = MagicMock(side_effect=mock_ytdl_init)
        monkeypatch.setitem(sys.modules, "yt_dlp", mock_module)
        _sync_thread_patch(monkeypatch)
        client.post(
            "/api/download",
            json={"url": "https://example.com/video", "title": "My Great Video"},
        )
        outtmpl = captured_opts.get("outtmpl", "")
        assert "My Great Video" in outtmpl
        assert "%(title)s" not in outtmpl

    def test_download_no_title_uses_yt_dlp_title(self, monkeypatch):
        """When title is not provided, outtmpl should use %(title)s (yt-dlp default)."""
        captured_opts = {}

        def mock_ytdl_init(opts):
            captured_opts.update(opts)
            return _make_yt_dlp_mock().YoutubeDL.return_value

        mock_module = MagicMock()
        mock_module.YoutubeDL = MagicMock(side_effect=mock_ytdl_init)
        monkeypatch.setitem(sys.modules, "yt_dlp", mock_module)
        _sync_thread_patch(monkeypatch)
        client.post(
            "/api/download",
            json={"url": "https://example.com/video"},
        )
        outtmpl = captured_opts.get("outtmpl", "")
        assert "%(title)s" in outtmpl

    def test_download_sniffs_html_on_unsupported_url(self, monkeypatch):
        """When yt-dlp returns 'Unsupported URL', backend sniffs HTML and retries."""
        mock_yt_dlp = _make_yt_dlp_mock()
        call_count = [0]
        original_extract = mock_yt_dlp.YoutubeDL.return_value.extract_info

        def _extract_with_fallback(url, download):
            call_count[0] += 1
            if call_count[0] == 1:
                raise mock_yt_dlp.utils.DownloadError(
                    "ERROR: Unsupported URL: https://example.com/page"
                )
            return original_extract(url, download)

        mock_yt_dlp.YoutubeDL.return_value.extract_info = MagicMock(
            side_effect=_extract_with_fallback
        )
        monkeypatch.setitem(sys.modules, "yt_dlp", mock_yt_dlp)
        monkeypatch.setattr(
            "backend.main._sniff_video_source",
            lambda url, cookies: "https://iframe.mediadelivery.net/embed/123/abc",
        )
        _sync_thread_patch(monkeypatch)
        resp = client.post("/api/download", json={"url": "https://example.com/page"})
        job_id = resp.json()["job_id"]
        jobs = {j["id"]: j for j in client.get("/api/jobs").json()}
        assert jobs[job_id]["status"] == "done"
        assert call_count[0] == 2  # first attempt + retry with sniffed URL

    def test_download_sniff_fails_reports_error(self, monkeypatch):
        """When yt-dlp fails + sniffing finds nothing, the job status is 'error'."""
        mock_yt_dlp = _make_yt_dlp_mock()
        mock_yt_dlp.YoutubeDL.return_value.extract_info = MagicMock(
            side_effect=mock_yt_dlp.utils.DownloadError(
                "ERROR: Unsupported URL: https://example.com/page"
            )
        )
        monkeypatch.setitem(sys.modules, "yt_dlp", mock_yt_dlp)
        monkeypatch.setattr("backend.main._sniff_video_source", lambda url, cookies: None)
        _sync_thread_patch(monkeypatch)
        resp = client.post("/api/download", json={"url": "https://example.com/page"})
        job_id = resp.json()["job_id"]
        jobs = {j["id"]: j for j in client.get("/api/jobs").json()}
        assert jobs[job_id]["status"] == "error"
        assert "Unsupported URL" in jobs[job_id]["error"]


class TestSanitizeFilename:
    def test_removes_invalid_chars(self):
        from backend.main import _sanitize_filename

        assert _sanitize_filename('My Video: "Best" <2024>') == "My Video Best 2024"

    def test_limits_length(self):
        from backend.main import _sanitize_filename

        long_name = "a" * 300
        assert len(_sanitize_filename(long_name)) == 180

    def test_strips_leading_trailing_dots_and_spaces(self):
        from backend.main import _sanitize_filename

        assert _sanitize_filename("  .hidden.  ") == "hidden"

    def test_empty_string_returns_video(self):
        from backend.main import _sanitize_filename

        assert _sanitize_filename("") == "video"

    def test_only_invalid_chars_returns_video(self):
        from backend.main import _sanitize_filename

        assert _sanitize_filename('<>:"/\\|?*') == "video"


class TestDeleteJob:
    def test_delete_existing_done_job(self, monkeypatch):
        """DELETE /api/jobs/{id} removes a done job from the store."""
        from backend.main import _jobs

        job_id = "test-del-job-1"
        _jobs[job_id] = {"id": job_id, "status": "done", "type": "download"}
        resp = client.delete(f"/api/jobs/{job_id}")
        assert resp.status_code == 200
        assert job_id not in _jobs

    def test_delete_nonexistent_job_returns_404(self):
        """DELETE /api/jobs/{id} returns 404 for unknown job."""
        resp = client.delete("/api/jobs/does-not-exist")
        assert resp.status_code == 404

    def test_delete_running_job_allowed(self, monkeypatch):
        """DELETE /api/jobs/{id} is allowed even for active jobs (download continues)."""
        from backend.main import _jobs

        job_id = "test-del-job-2"
        _jobs[job_id] = {"id": job_id, "status": "running", "type": "download"}
        resp = client.delete(f"/api/jobs/{job_id}")
        assert resp.status_code == 200
        assert job_id not in _jobs

    def test_delete_job_removed_from_list(self, monkeypatch):
        """After deletion, job no longer appears in GET /api/jobs."""
        from backend.main import _jobs

        job_id = "test-del-job-3"
        _jobs[job_id] = {"id": job_id, "status": "done", "type": "download"}
        client.delete(f"/api/jobs/{job_id}")
        jobs = client.get("/api/jobs").json()
        assert all(j["id"] != job_id for j in jobs)


class TestCookiesToNetscape:
    def test_basic_conversion(self):
        from backend.main import _cookies_to_netscape

        result = _cookies_to_netscape("foo=bar; baz=qux", "example.com")
        assert "# Netscape HTTP Cookie File" in result
        assert "example.com" in result
        assert "foo\tbar" in result
        assert "baz\tqux" in result

    def test_empty_string(self):
        from backend.main import _cookies_to_netscape

        result = _cookies_to_netscape("", "example.com")
        assert result.strip() == "# Netscape HTTP Cookie File"

    def test_pair_without_value(self):
        from backend.main import _cookies_to_netscape

        result = _cookies_to_netscape("key=; other=val", "example.com")
        lines = result.strip().splitlines()
        # key= should produce an entry with empty value
        assert any("key" in line for line in lines[1:])

    def test_value_with_equals(self):
        from backend.main import _cookies_to_netscape

        # Values containing '=' should be preserved (partition only splits on first =)
        result = _cookies_to_netscape("token=abc=def", "example.com")
        assert "token\tabc=def" in result
