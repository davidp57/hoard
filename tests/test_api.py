"""Unit tests for MediaBrowser API endpoints."""

import json
import sys
import threading
import time
from unittest.mock import MagicMock

import pytest
from starlette.testclient import TestClient  # bundled with fastapi

# Env vars are already set by conftest.py before this import
import backend.main as main_mod
from backend.main import MEDIA_ROOT, app

client = TestClient(app)


# ── Frontend shell ────────────────────────────────────────────────────────────


class TestFrontendShell:
    def test_manifest_is_served(self):
        resp = client.get("/manifest.webmanifest")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Hoard"
        assert data["display"] == "standalone"

    def test_service_worker_is_served(self):
        resp = client.get("/service-worker.js")
        assert resp.status_code == 200
        assert "self.addEventListener" in resp.text
        assert "CACHE_NAME" in resp.text


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


# ── /api/home-roots ────────────────────────────────────────────────────────────


class TestHomeRoots:
    def test_empty_initially(self):
        resp = client.get("/api/home-roots")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_add_and_list(self, subdir_with_video):
        resp = client.post("/api/home-roots", json={"name": "Séries", "path": subdir_with_video})
        assert resp.status_code == 200
        data = client.get("/api/home-roots").json()
        assert len(data) == 1
        assert data[0]["name"] == "Séries"
        assert data[0]["path"] == subdir_with_video
        assert "id" in data[0]

    def test_add_nonexistent_rejected(self):
        resp = client.post("/api/home-roots", json={"name": "Ghost", "path": "ghost_dir"})
        assert resp.status_code == 404

    def test_add_file_rejected(self, video_file):
        resp = client.post("/api/home-roots", json={"name": "Video", "path": video_file})
        assert resp.status_code == 404

    def test_add_empty_name_rejected(self, subdir_with_video):
        resp = client.post("/api/home-roots", json={"name": "", "path": subdir_with_video})
        assert resp.status_code == 400

    def test_add_whitespace_name_rejected(self, subdir_with_video):
        resp = client.post("/api/home-roots", json={"name": "   ", "path": subdir_with_video})
        assert resp.status_code == 400

    def test_add_duplicate_rejected(self, subdir_with_video):
        client.post("/api/home-roots", json={"name": "A", "path": subdir_with_video})
        resp = client.post("/api/home-roots", json={"name": "B", "path": subdir_with_video})
        assert resp.status_code == 409

    def test_remove(self, subdir_with_video):
        client.post("/api/home-roots", json={"name": "Séries", "path": subdir_with_video})
        root_id = client.get("/api/home-roots").json()[0]["id"]
        resp = client.delete(f"/api/home-roots/{root_id}")
        assert resp.status_code == 200
        assert client.get("/api/home-roots").json() == []

    def test_remove_nonexistent(self):
        resp = client.delete("/api/home-roots/9999")
        assert resp.status_code == 404

    def test_path_traversal_blocked(self):
        resp = client.post("/api/home-roots", json={"name": "Escape", "path": "../../../etc"})
        assert resp.status_code == 403

    def test_first_root_is_default(self, subdir_with_video):
        client.post("/api/home-roots", json={"name": "First", "path": subdir_with_video})
        data = client.get("/api/home-roots").json()
        assert data[0]["is_default"] is True

    def test_second_root_not_default(self, subdir_with_video, subdir_without_video):
        client.post("/api/home-roots", json={"name": "First", "path": subdir_with_video})
        client.post("/api/home-roots", json={"name": "Second", "path": subdir_without_video})
        data = client.get("/api/home-roots").json()
        defaults = [r for r in data if r["is_default"]]
        assert len(defaults) == 1
        assert defaults[0]["name"] == "First"

    def test_set_default(self, subdir_with_video, subdir_without_video):
        client.post("/api/home-roots", json={"name": "First", "path": subdir_with_video})
        client.post("/api/home-roots", json={"name": "Second", "path": subdir_without_video})
        data = client.get("/api/home-roots").json()
        second_id = next(r["id"] for r in data if r["name"] == "Second")
        resp = client.post(f"/api/home-roots/{second_id}/set-default")
        assert resp.status_code == 200
        data = client.get("/api/home-roots").json()
        assert next(r for r in data if r["name"] == "Second")["is_default"] is True
        assert next(r for r in data if r["name"] == "First")["is_default"] is False

    def test_set_default_nonexistent(self):
        resp = client.post("/api/home-roots/9999/set-default")
        assert resp.status_code == 404

    def test_delete_default_promotes_next(self, subdir_with_video, subdir_without_video):
        client.post("/api/home-roots", json={"name": "First", "path": subdir_with_video})
        client.post("/api/home-roots", json={"name": "Second", "path": subdir_without_video})
        data = client.get("/api/home-roots").json()
        first_id = next(r["id"] for r in data if r["name"] == "First")
        client.delete(f"/api/home-roots/{first_id}")
        data = client.get("/api/home-roots").json()
        assert len(data) == 1
        assert data[0]["is_default"] is True
        assert data[0]["name"] == "Second"


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


# ── Galleries (image folder as a single media) ──────────────────────────────────


def _make_image(rel_path: str) -> None:
    """Create a dummy image file (content irrelevant for detection/listing)."""
    p = MEDIA_ROOT / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 32)


class TestGallery:
    def test_folder_with_images_is_gallery(self):
        for i in range(4):
            _make_image(f"album/p{i}.jpg")
        entry = next(e for e in client.get("/api/files").json()["entries"] if e["name"] == "album")
        assert entry["is_dir"] is True
        assert entry["media_type"] == "gallery"
        assert "progress" in entry

    def test_three_images_is_not_gallery(self):
        for i in range(3):
            _make_image(f"few/p{i}.jpg")
        entry = next(e for e in client.get("/api/files").json()["entries"] if e["name"] == "few")
        assert entry["media_type"] == "other"
        assert entry["folder_state"] == "new"

    def test_folder_with_video_is_not_gallery(self):
        for i in range(4):
            _make_image(f"mixed/p{i}.jpg")
        (MEDIA_ROOT / "mixed" / "clip.mp4").write_bytes(b"\x00" * 16)
        entry = next(e for e in client.get("/api/files").json()["entries"] if e["name"] == "mixed")
        assert entry["media_type"] == "other"

    def test_is_gallery_handles_permission_error(self):
        folder = MagicMock()
        folder.iterdir.side_effect = PermissionError
        assert main_mod.is_gallery(folder) is False

    def test_folder_with_image_subdir_is_container(self):
        # A folder that contains sub-folders is a browsable container, not a gallery;
        # each leaf sub-folder is its own gallery (no recursive flattening).
        for name in ("a", "b", "c", "d"):
            _make_image(f"library/Album-01/{name}.jpg")
        for name in ("a", "b", "c", "d"):
            _make_image(f"library/Album-02/{name}.jpg")
        root = client.get("/api/files").json()["entries"]
        assert next(e for e in root if e["name"] == "library")["media_type"] == "other"
        albums = client.get("/api/files?path=library").json()["entries"]
        assert {e["name"]: e["media_type"] for e in albums} == {
            "Album-01": "gallery",
            "Album-02": "gallery",
        }

    def test_gallery_list_is_own_level_only(self):
        # Galleries are leaf folders; the sequence never descends into sub-folders.
        for name in ("couverture", "01", "02", "03"):
            _make_image(f"book/{name}.jpg")
        _make_image("book/extra/should-be-ignored.jpg")
        paths = [it["path"] for it in client.get("/api/gallery/list?path=book").json()["items"]]
        assert paths == [
            "book/01.jpg",
            "book/02.jpg",
            "book/03.jpg",
            "book/couverture.jpg",
        ]

    def test_gallery_list_natural_sort(self):
        for n in (1, 2, 10):
            _make_image(f"pages/page-{n}.jpg")
        _make_image("pages/page-3.jpg")
        paths = [it["path"] for it in client.get("/api/gallery/list?path=pages").json()["items"]]
        assert paths == [
            "pages/page-1.jpg",
            "pages/page-2.jpg",
            "pages/page-3.jpg",
            "pages/page-10.jpg",
        ]

    def test_gallery_progress_anchored_on_folder(self):
        for i in range(4):
            _make_image(f"g/p{i}.jpg")
        client.post("/api/progress?path=g", json={"position": 2.0, "duration": 4.0})
        entry = next(e for e in client.get("/api/files").json()["entries"] if e["name"] == "g")
        assert entry["progress"]["position"] == 2.0
        assert entry["progress"]["duration"] == 4.0
        assert entry["progress"]["percent"] == 50.0

    def test_folder_with_pdf_is_still_gallery(self):
        for i in range(4):
            _make_image(f"gp/p{i}.jpg")
        (MEDIA_ROOT / "gp" / "doc.pdf").write_bytes(b"%PDF-1.4")
        entry = next(e for e in client.get("/api/files").json()["entries"] if e["name"] == "gp")
        assert entry["media_type"] == "gallery"

    def test_passengers_with_few_images_is_not_gallery(self):
        # Passenger count must not influence detection: it relies on image_count > 3.
        for i in range(2):
            _make_image(f"gp_mixed/p{i}.jpg")
        (MEDIA_ROOT / "gp_mixed" / "doc.pdf").write_bytes(b"%PDF-1.4")
        (MEDIA_ROOT / "gp_mixed" / "notes.txt").write_text("notes")
        (MEDIA_ROOT / "gp_mixed" / "audio.mp3").write_bytes(b"ID3")
        entry = next(
            e for e in client.get("/api/files").json()["entries"] if e["name"] == "gp_mixed"
        )
        assert entry["media_type"] == "other"

    def test_gallery_list_includes_passengers_in_order(self):
        _make_image("mix/01.jpg")
        _make_image("mix/03.jpg")
        (MEDIA_ROOT / "mix" / "02.pdf").write_bytes(b"%PDF-1.4")
        (MEDIA_ROOT / "mix" / "04.txt").write_text("hello")
        (MEDIA_ROOT / "mix" / "ignore.bin").write_bytes(b"\x00")  # not a passenger → skipped
        items = client.get("/api/gallery/list?path=mix").json()["items"]
        assert [(it["path"].split("/")[-1], it["type"]) for it in items] == [
            ("01.jpg", "image"),
            ("02.pdf", "pdf"),
            ("03.jpg", "image"),
            ("04.txt", "text"),
        ]

    def test_gallery_list_not_found(self):
        resp = client.get("/api/gallery/list?path=nope")
        assert resp.status_code == 404

    def test_gallery_list_path_traversal_blocked(self):
        resp = client.get("/api/gallery/list?path=../../etc")
        assert resp.status_code == 403


class TestThumbnail:
    def test_thumbnail_returns_jpeg(self, monkeypatch):
        _make_image("g/p0.jpg")
        monkeypatch.setattr(main_mod, "FFMPEG_BIN", "ffmpeg")
        monkeypatch.setattr(
            main_mod.subprocess,
            "run",
            lambda *args, **kwargs: MagicMock(stdout=b"\xff\xd8\xff\xe0fakejpeg"),
        )
        resp = client.get("/api/thumbnail?path=g/p0.jpg")
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("image/")
        assert resp.content.startswith(b"\xff\xd8")

    def test_thumbnail_404_missing(self):
        resp = client.get("/api/thumbnail?path=nope.jpg")
        assert resp.status_code == 404

    def test_thumbnail_415_not_image(self):
        (MEDIA_ROOT / "note.txt").write_text("hello")
        resp = client.get("/api/thumbnail?path=note.txt")
        assert resp.status_code == 415

    def test_thumbnail_503_without_ffmpeg(self, monkeypatch):
        _make_image("g/p0.jpg")
        monkeypatch.setattr(main_mod, "FFMPEG_BIN", "")
        resp = client.get("/api/thumbnail?path=g/p0.jpg")
        assert resp.status_code == 503

    def test_thumbnail_path_traversal_blocked(self):
        resp = client.get("/api/thumbnail?path=../../etc/passwd")
        assert resp.status_code == 403

    def test_archive_thumbnail_returns_jpeg(self, monkeypatch):
        import zipfile

        with zipfile.ZipFile(MEDIA_ROOT / "book.cbz", "w") as zf:
            zf.writestr("01.jpg", b"\xff\xd8\xff\xe0dummy")
        monkeypatch.setattr(main_mod, "FFMPEG_BIN", "ffmpeg")
        monkeypatch.setattr(
            main_mod.subprocess,
            "run",
            lambda *args, **kwargs: MagicMock(stdout=b"\xff\xd8thumb"),
        )
        resp = client.get("/api/archive/thumbnail?path=book.cbz&index=0")
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("image/")

    def test_archive_thumbnail_index_out_of_range(self, monkeypatch):
        import zipfile

        with zipfile.ZipFile(MEDIA_ROOT / "book.cbz", "w") as zf:
            zf.writestr("01.jpg", b"x")
        monkeypatch.setattr(main_mod, "FFMPEG_BIN", "ffmpeg")
        resp = client.get("/api/archive/thumbnail?path=book.cbz&index=5")
        assert resp.status_code == 404


# ── /api/progress ─────────────────────────────────────────────────────────────


class TestProgress:
    def test_no_record_returns_zero(self, video_file):
        resp = client.get(f"/api/progress?path={video_file}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["position"] == 0
        assert data["duration"] == 0
        assert data["percent"] == 0
        assert data["has_saved_progress"] is False

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
        assert data["has_saved_progress"] is True

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


# Note: the legacy /api/stream endpoint was removed (BL-067). Playback of any
# media file now goes through /api/file — see TestFile (range, multi-range,
# 404 and path-traversal coverage).


class TestMediaInfo:
    def test_media_info_returns_baseline_strategy_for_mp4_h264_aac(self, video_file, monkeypatch):
        ffprobe_payload = {
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "h264",
                    "codec_tag_string": "avc1",
                    "width": 1920,
                    "height": 1080,
                    "bit_rate": "1500000",
                    "r_frame_rate": "30000/1001",
                    "bits_per_raw_sample": "8",
                },
                {
                    "codec_type": "audio",
                    "codec_name": "aac",
                    "codec_tag_string": "mp4a",
                    "channels": 2,
                    "sample_rate": "48000",
                    "bit_rate": "128000",
                },
            ],
            "format": {
                "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
                "bit_rate": "1628000",
                "duration": "60.0",
            },
        }

        monkeypatch.setattr(main_mod, "FFPROBE_BIN", "ffprobe")
        monkeypatch.setattr(
            main_mod.subprocess,
            "run",
            lambda *args, **kwargs: MagicMock(stdout=json.dumps(ffprobe_payload)),
        )

        resp = client.get(f"/api/media-info?path={video_file}")

        assert resp.status_code == 200
        data = resp.json()
        assert data["path"] == video_file
        assert data["mime_type"] == "video/mp4"
        assert data["strategy"] == "baseline"
        assert data["content_type"] == 'video/mp4; codecs="avc1, mp4a.40.2"'
        assert data["video"]["codec"] == "h264"
        assert data["video"]["content_type"] == 'video/mp4; codecs="avc1"'
        assert data["audio"]["codec"] == "aac"
        assert data["audio"]["content_type"] == 'audio/mp4; codecs="mp4a.40.2"'

    def test_media_info_returns_probe_strategy_for_mp4_hevc(self, video_file, monkeypatch):
        ffprobe_payload = {
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "hevc",
                    "codec_tag_string": "hvc1",
                    "width": 3840,
                    "height": 2160,
                    "bit_rate": "9000000",
                    "avg_frame_rate": "24/1",
                    "bits_per_raw_sample": "10",
                },
                {
                    "codec_type": "audio",
                    "codec_name": "aac",
                    "codec_tag_string": "mp4a",
                    "channels": 6,
                    "sample_rate": "48000",
                    "bit_rate": "384000",
                },
            ],
            "format": {
                "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
                "bit_rate": "9384000",
                "duration": "120.0",
            },
        }

        monkeypatch.setattr(main_mod, "FFPROBE_BIN", "ffprobe")
        monkeypatch.setattr(
            main_mod.subprocess,
            "run",
            lambda *args, **kwargs: MagicMock(stdout=json.dumps(ffprobe_payload)),
        )

        resp = client.get(f"/api/media-info?path={video_file}")

        assert resp.status_code == 200
        data = resp.json()
        assert data["strategy"] == "probe"
        assert data["content_type"] == 'video/mp4; codecs="hvc1, mp4a.40.2"'
        assert data["video"]["codec"] == "hevc"
        assert data["video"]["bit_depth"] == 10
        assert data["audio_native"] is True

    def test_media_info_returns_fallback_strategy_for_ac3_audio(self, video_file, monkeypatch):
        ffprobe_payload = {
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "h264",
                    "codec_tag_string": "avc1",
                    "width": 1920,
                    "height": 1080,
                    "bit_rate": "3000000",
                    "avg_frame_rate": "24/1",
                    "bits_per_raw_sample": "8",
                },
                {
                    "codec_type": "audio",
                    "codec_name": "ac3",
                    "codec_tag_string": "ac-3",
                    "channels": 6,
                    "sample_rate": "48000",
                    "bit_rate": "384000",
                },
            ],
            "format": {
                "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
                "bit_rate": "3384000",
                "duration": "90.0",
            },
        }

        monkeypatch.setattr(main_mod, "FFPROBE_BIN", "ffprobe")
        monkeypatch.setattr(
            main_mod.subprocess,
            "run",
            lambda *args, **kwargs: MagicMock(stdout=json.dumps(ffprobe_payload)),
        )

        resp = client.get(f"/api/media-info?path={video_file}")

        assert resp.status_code == 200
        data = resp.json()
        assert data["strategy"] == "fallback"
        assert data["audio_native"] is False
        assert data["audio"]["codec"] == "ac3"
        assert data["content_type"] == 'video/mp4; codecs="avc1, ac-3"'
        assert data["audio"]["content_type"] == 'audio/mp4; codecs="ac-3"'

    def test_media_info_returns_fallback_strategy_for_eac3_audio(self, video_file, monkeypatch):
        ffprobe_payload = {
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "h264",
                    "codec_tag_string": "avc1",
                    "width": 1920,
                    "height": 1080,
                    "bit_rate": "3000000",
                    "avg_frame_rate": "24/1",
                },
                {
                    "codec_type": "audio",
                    "codec_name": "eac3",
                    "codec_tag_string": "ec-3",
                    "channels": 6,
                    "sample_rate": "48000",
                    "bit_rate": "256000",
                },
            ],
            "format": {
                "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
                "bit_rate": "3256000",
                "duration": "90.0",
            },
        }

        monkeypatch.setattr(main_mod, "FFPROBE_BIN", "ffprobe")
        monkeypatch.setattr(
            main_mod.subprocess,
            "run",
            lambda *args, **kwargs: MagicMock(stdout=json.dumps(ffprobe_payload)),
        )

        resp = client.get(f"/api/media-info?path={video_file}")

        assert resp.status_code == 200
        data = resp.json()
        assert data["strategy"] == "fallback"
        assert data["audio_native"] is False
        assert data["content_type"] == 'video/mp4; codecs="avc1, ec-3"'

    def test_media_info_returns_fallback_strategy_for_dts_audio(self, video_file, monkeypatch):
        ffprobe_payload = {
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "h264",
                    "codec_tag_string": "avc1",
                    "width": 1920,
                    "height": 1080,
                    "bit_rate": "3000000",
                    "avg_frame_rate": "24/1",
                },
                {
                    "codec_type": "audio",
                    "codec_name": "dts",
                    "codec_tag_string": "DTS ",
                    "channels": 6,
                    "sample_rate": "48000",
                    "bit_rate": "1509000",
                },
            ],
            "format": {
                "format_name": "matroska,webm",
                "bit_rate": "4509000",
                "duration": "90.0",
            },
        }

        monkeypatch.setattr(main_mod, "FFPROBE_BIN", "ffprobe")
        monkeypatch.setattr(
            main_mod.subprocess,
            "run",
            lambda *args, **kwargs: MagicMock(stdout=json.dumps(ffprobe_payload)),
        )

        resp = client.get(f"/api/media-info?path={video_file}")

        assert resp.status_code == 200
        data = resp.json()
        assert data["strategy"] == "fallback"
        assert data["audio_native"] is False
        assert data["audio"]["codec"] == "dts"

    def test_media_info_audio_native_true_for_baseline(self, video_file, monkeypatch):
        ffprobe_payload = {
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "h264",
                    "codec_tag_string": "avc1",
                    "width": 1280,
                    "height": 720,
                    "bit_rate": "1500000",
                    "avg_frame_rate": "30/1",
                },
                {
                    "codec_type": "audio",
                    "codec_name": "aac",
                    "codec_tag_string": "mp4a",
                    "channels": 2,
                    "sample_rate": "44100",
                    "bit_rate": "128000",
                },
            ],
            "format": {
                "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
                "bit_rate": "1628000",
                "duration": "30.0",
            },
        }

        monkeypatch.setattr(main_mod, "FFPROBE_BIN", "ffprobe")
        monkeypatch.setattr(
            main_mod.subprocess,
            "run",
            lambda *args, **kwargs: MagicMock(stdout=json.dumps(ffprobe_payload)),
        )

        resp = client.get(f"/api/media-info?path={video_file}")

        assert resp.status_code == 200
        data = resp.json()
        assert data["strategy"] == "baseline"
        assert data["audio_native"] is True

    def test_media_info_returns_503_without_ffprobe(self, video_file, monkeypatch):
        monkeypatch.setattr(main_mod, "FFPROBE_BIN", "")

        resp = client.get(f"/api/media-info?path={video_file}")

        assert resp.status_code == 503

    def test_media_info_not_found(self):
        resp = client.get("/api/media-info?path=ghost.mp4")
        assert resp.status_code == 404

    def test_media_info_path_traversal_blocked(self):
        resp = client.get("/api/media-info?path=../../etc/passwd")
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

    def test_get_settings_returns_default_initial_sweep_seconds(self):
        resp = client.get("/api/settings")
        assert resp.status_code == 200
        assert resp.json()["initial_sweep_seconds"] == "0"

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

    def test_update_initial_sweep_seconds(self):
        resp = client.post("/api/settings", json={"initial_sweep_seconds": 600})
        assert resp.status_code == 200
        assert resp.json()["ok"] is True

        resp = client.get("/api/settings")
        assert resp.status_code == 200
        assert resp.json()["initial_sweep_seconds"] == "600"

    def test_update_initial_sweep_seconds_rejects_large_value(self):
        resp = client.post("/api/settings", json={"initial_sweep_seconds": 7201})
        assert resp.status_code == 422

    def test_gestures_overlay_seen_persists(self):
        client.post("/api/settings", json={"gestures_overlay_seen": True})
        assert client.get("/api/settings").json()["gestures_overlay_seen"] == "1"
        client.post("/api/settings", json={"gestures_overlay_seen": False})
        assert client.get("/api/settings").json()["gestures_overlay_seen"] == "0"

    def test_cookies_path_accepts_valid_txt_file(self, tmp_path):
        cookies = tmp_path / "cookies.txt"
        cookies.write_text("# Netscape HTTP Cookie File\n")
        resp = client.post("/api/settings", json={"download_cookies_path": str(cookies)})
        assert resp.status_code == 200
        assert resp.json()["ok"] is True
        # Clear it again so it does not leak into other tests.
        client.post("/api/settings", json={"download_cookies_path": ""})

    def test_cookies_path_empty_clears_setting(self):
        resp = client.post("/api/settings", json={"download_cookies_path": ""})
        assert resp.status_code == 200
        assert resp.json()["ok"] is True

    def test_cookies_path_rejects_relative_path(self):
        resp = client.post("/api/settings", json={"download_cookies_path": "cookies.txt"})
        assert resp.status_code == 422

    def test_cookies_path_rejects_non_txt_extension(self, tmp_path):
        secret = tmp_path / "secret"
        secret.write_text("sensitive")
        resp = client.post("/api/settings", json={"download_cookies_path": str(secret)})
        assert resp.status_code == 422

    def test_cookies_path_rejects_missing_file(self, tmp_path):
        missing = tmp_path / "nope.txt"
        resp = client.post("/api/settings", json={"download_cookies_path": str(missing)})
        assert resp.status_code == 422

    def test_seek_settings_defaults(self):
        resp = client.get("/api/settings")
        assert resp.status_code == 200
        data = resp.json()
        assert data["seek_short"] == "10"
        assert data["seek_medium"] == "30"
        assert data["seek_long"] == "60"
        assert data["seek_xlong"] == "120"

    def test_seek_settings_can_be_updated(self):
        resp = client.post(
            "/api/settings",
            json={
                "seek_short": 5,
                "seek_medium": 15,
                "seek_long": 45,
                "seek_xlong": 90,
            },
        )
        assert resp.status_code == 200
        assert resp.json()["ok"] is True

        resp = client.get("/api/settings")
        data = resp.json()
        assert data["seek_short"] == "5"
        assert data["seek_medium"] == "15"
        assert data["seek_long"] == "45"
        assert data["seek_xlong"] == "90"

    def test_doubletap_settings_removed(self):
        resp = client.get("/api/settings")
        assert resp.status_code == 200
        data = resp.json()
        assert "doubletap_left" not in data
        assert "doubletap_right_bottom" not in data
        assert "doubletap_right_mid" not in data
        assert "doubletap_right_top" not in data

    def test_transcode_enabled_default_is_true(self):
        resp = client.get("/api/settings")
        assert resp.status_code == 200
        assert resp.json()["transcode_enabled"] == "1"

    def test_transcode_enabled_can_be_disabled(self):
        resp = client.post("/api/settings", json={"transcode_enabled": False})
        assert resp.status_code == 200
        assert resp.json()["ok"] is True

        resp = client.get("/api/settings")
        assert resp.json()["transcode_enabled"] == "0"

    def test_transcode_enabled_can_be_re_enabled(self):
        client.post("/api/settings", json={"transcode_enabled": False})
        resp = client.post("/api/settings", json={"transcode_enabled": True})
        assert resp.status_code == 200

        resp = client.get("/api/settings")
        assert resp.json()["transcode_enabled"] == "1"

    def test_transcode_audio_only_default_is_false(self):
        resp = client.get("/api/settings")
        assert resp.status_code == 200
        assert resp.json()["transcode_audio_only"] == "0"

    def test_transcode_audio_only_can_be_enabled(self):
        resp = client.post("/api/settings", json={"transcode_audio_only": True})
        assert resp.status_code == 200

        resp = client.get("/api/settings")
        assert resp.json()["transcode_audio_only"] == "1"

    def test_transcode_audio_only_can_be_disabled(self):
        client.post("/api/settings", json={"transcode_audio_only": True})
        resp = client.post("/api/settings", json={"transcode_audio_only": False})
        assert resp.status_code == 200

        resp = client.get("/api/settings")
        assert resp.json()["transcode_audio_only"] == "0"

    def test_gamepad_enabled_default_is_true(self):
        resp = client.get("/api/settings")
        assert resp.status_code == 200
        assert resp.json()["gamepad_enabled"] == "1"

    def test_gamepad_enabled_can_be_toggled(self):
        resp = client.post("/api/settings", json={"gamepad_enabled": False})
        assert resp.status_code == 200
        resp = client.get("/api/settings")
        assert resp.json()["gamepad_enabled"] == "0"
        client.post("/api/settings", json={"gamepad_enabled": True})

    def test_gamepad_haptic_default_is_true(self):
        resp = client.get("/api/settings")
        assert resp.json()["gamepad_haptic"] == "1"

    def test_gamepad_deadzone_default(self):
        resp = client.get("/api/settings")
        assert resp.json()["gamepad_deadzone"] == "0.20"

    def test_gamepad_deadzone_can_be_set(self):
        resp = client.post("/api/settings", json={"gamepad_deadzone": 0.30})
        assert resp.status_code == 200
        resp = client.get("/api/settings")
        assert resp.json()["gamepad_deadzone"] == "0.3"

    def test_gamepad_deadzone_clamped(self):
        resp = client.post("/api/settings", json={"gamepad_deadzone": 0.99})
        assert resp.status_code == 422

    def test_gamepad_mapping_default(self):
        resp = client.get("/api/settings")
        assert resp.json()["gamepad_mapping"] == "{}"

    def test_gamepad_mapping_can_be_set(self):
        mapping = '{"0":"play_pause","1":"close_player"}'
        resp = client.post("/api/settings", json={"gamepad_mapping": mapping})
        assert resp.status_code == 200
        resp = client.get("/api/settings")
        assert resp.json()["gamepad_mapping"] == mapping

    def test_gamepad_mapping_invalid_json_rejected(self):
        resp = client.post("/api/settings", json={"gamepad_mapping": "{not valid json}"})
        assert resp.status_code == 422

    def test_fs_progress_zoom_default(self):
        resp = client.get("/api/settings")
        assert resp.status_code == 200
        assert resp.json()["fs_progress_zoom"] == "20"

    def test_fs_progress_zoom_can_be_updated(self):
        resp = client.post("/api/settings", json={"fs_progress_zoom": 30})
        assert resp.status_code == 200
        assert resp.json()["ok"] is True

        resp = client.get("/api/settings")
        assert resp.json()["fs_progress_zoom"] == "30"

    def test_fs_progress_zoom_rejects_too_small(self):
        resp = client.post("/api/settings", json={"fs_progress_zoom": 4})
        assert resp.status_code == 422

    def test_fs_progress_zoom_rejects_too_large(self):
        resp = client.post("/api/settings", json={"fs_progress_zoom": 51})
        assert resp.status_code == 422


# ── /api/initial-sweep ───────────────────────────────────────────────────────


class TestInitialSweep:
    def test_get_initial_sweep_uses_global_default(self, subdir_with_video):
        client.post("/api/settings", json={"initial_sweep_seconds": 600})

        resp = client.get("/api/initial-sweep?path=series")
        assert resp.status_code == 200
        data = resp.json()
        assert data == {
            "path": "series",
            "default_seconds": 600,
            "override_seconds": None,
            "effective_seconds": 600,
            "source": "default",
        }

    def test_post_override_and_read_back(self, subdir_with_video):
        client.post("/api/settings", json={"initial_sweep_seconds": 600})

        resp = client.post("/api/initial-sweep", json={"path": "series", "seconds": 120})
        assert resp.status_code == 200
        assert resp.json()["ok"] is True

        resp = client.get("/api/initial-sweep?path=series")
        assert resp.status_code == 200
        data = resp.json()
        assert data == {
            "path": "series",
            "default_seconds": 600,
            "override_seconds": 120,
            "effective_seconds": 120,
            "source": "override",
        }

    def test_override_zero_disables_folder_even_with_global_default(self, subdir_with_video):
        client.post("/api/settings", json={"initial_sweep_seconds": 600})
        client.post("/api/initial-sweep", json={"path": "series", "seconds": 0})

        resp = client.get("/api/initial-sweep?path=series")
        assert resp.status_code == 200
        data = resp.json()
        assert data == {
            "path": "series",
            "default_seconds": 600,
            "override_seconds": 0,
            "effective_seconds": 0,
            "source": "override",
        }

    def test_delete_override_reverts_to_global_default(self, subdir_with_video):
        client.post("/api/settings", json={"initial_sweep_seconds": 600})
        client.post("/api/initial-sweep", json={"path": "series", "seconds": 90})

        resp = client.delete("/api/initial-sweep?path=series")
        assert resp.status_code == 200
        assert resp.json()["ok"] is True

        resp = client.get("/api/initial-sweep?path=series")
        assert resp.status_code == 200
        data = resp.json()
        assert data == {
            "path": "series",
            "default_seconds": 600,
            "override_seconds": None,
            "effective_seconds": 600,
            "source": "default",
        }

    def test_override_rejects_file_path(self, video_file):
        resp = client.post("/api/initial-sweep", json={"path": video_file, "seconds": 90})
        assert resp.status_code == 404

    def test_override_rejects_large_value(self, subdir_with_video):
        resp = client.post("/api/initial-sweep", json={"path": "series", "seconds": 7201})
        assert resp.status_code == 422

    def test_get_initial_sweep_rejects_path_traversal(self):
        resp = client.get("/api/initial-sweep?path=../../etc")
        assert resp.status_code == 403

    def test_delete_override_for_nonexistent_folder_succeeds(self):
        # Clearing a stale override (folder deleted/renamed on disk) must not 404
        resp = client.delete("/api/initial-sweep?path=no_such_folder")
        assert resp.status_code == 200
        assert resp.json()["ok"] is True

    def test_delete_override_still_rejects_path_traversal(self):
        resp = client.delete("/api/initial-sweep?path=../../etc")
        assert resp.status_code == 403


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


# ── /api/segments ─────────────────────────────────────────────────────────────


class TestSegments:
    def _noop_thread(self, monkeypatch):
        import threading as _threading

        monkeypatch.setattr(
            _threading,
            "Thread",
            lambda target, args, daemon: type("T", (), {"start": lambda self: None})(),
        )

    def test_empty_initially(self, video_file):
        resp = client.get(f"/api/segments?path={video_file}")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_create_and_list(self, video_file):
        resp = client.post(
            f"/api/segments?path={video_file}",
            json={"seg_in": 5.0, "seg_out": 15.0},
        )
        assert resp.status_code == 200
        seg_id = resp.json()["id"]
        assert isinstance(seg_id, int)

        resp = client.get(f"/api/segments?path={video_file}")
        assert resp.status_code == 200
        segs = resp.json()
        assert len(segs) == 1
        assert segs[0]["id"] == seg_id
        assert segs[0]["seg_in"] == 5.0
        assert segs[0]["seg_out"] == 15.0

    def test_multiple_segments_ordered(self, video_file):
        client.post(f"/api/segments?path={video_file}", json={"seg_in": 30.0, "seg_out": 40.0})
        client.post(f"/api/segments?path={video_file}", json={"seg_in": 10.0, "seg_out": 20.0})
        resp = client.get(f"/api/segments?path={video_file}")
        segs = resp.json()
        assert len(segs) >= 2
        # Ordered by insertion (id ASC)
        ids = [s["id"] for s in segs]
        assert ids == sorted(ids)

    def test_delete_segment(self, video_file):
        r = client.post(f"/api/segments?path={video_file}", json={"seg_in": 1.0, "seg_out": 2.0})
        seg_id = r.json()["id"]
        resp = client.delete(f"/api/segments/{seg_id}")
        assert resp.status_code == 200
        assert resp.json() == {"ok": True}

        segs = client.get(f"/api/segments?path={video_file}").json()
        assert all(s["id"] != seg_id for s in segs)

    def test_delete_nonexistent_segment(self):
        resp = client.delete("/api/segments/999999")
        assert resp.status_code == 404

    def test_invalid_range_rejected(self, video_file):
        resp = client.post(
            f"/api/segments?path={video_file}",
            json={"seg_in": 20.0, "seg_out": 10.0},
        )
        assert resp.status_code == 400

    def test_equal_range_rejected(self, video_file):
        resp = client.post(
            f"/api/segments?path={video_file}",
            json={"seg_in": 10.0, "seg_out": 10.0},
        )
        assert resp.status_code == 400

    def test_export_no_segments_rejected(self, video_file):
        (MEDIA_ROOT / "dest").mkdir(exist_ok=True)
        resp = client.post(
            f"/api/files/export-segments?path={video_file}",
            json={"mode": "merged", "destination": "dest"},
        )
        assert resp.status_code == 400

    def test_export_dest_not_found(self, video_file):
        client.post(f"/api/segments?path={video_file}", json={"seg_in": 0.0, "seg_out": 5.0})
        resp = client.post(
            f"/api/files/export-segments?path={video_file}",
            json={"mode": "merged", "destination": "no_such_dir"},
        )
        assert resp.status_code == 404

    def test_export_source_not_found(self):
        (MEDIA_ROOT / "dest").mkdir(exist_ok=True)
        resp = client.post(
            "/api/files/export-segments?path=ghost.mp4",
            json={"mode": "merged", "destination": "dest"},
        )
        assert resp.status_code == 404

    def test_export_invalid_mode(self, video_file):
        client.post(f"/api/segments?path={video_file}", json={"seg_in": 0.0, "seg_out": 5.0})
        (MEDIA_ROOT / "dest").mkdir(exist_ok=True)
        resp = client.post(
            f"/api/files/export-segments?path={video_file}",
            json={"mode": "badmode", "destination": "dest"},
        )
        assert resp.status_code == 400

    def test_export_individual_returns_job_id(self, video_file, monkeypatch):
        self._noop_thread(monkeypatch)
        client.post(f"/api/segments?path={video_file}", json={"seg_in": 0.0, "seg_out": 5.0})
        client.post(f"/api/segments?path={video_file}", json={"seg_in": 10.0, "seg_out": 15.0})
        (MEDIA_ROOT / "dest").mkdir(exist_ok=True)
        resp = client.post(
            f"/api/files/export-segments?path={video_file}",
            json={"mode": "individual", "destination": "dest"},
        )
        assert resp.status_code == 200
        assert "job_id" in resp.json()

    def test_export_merged_returns_job_id(self, video_file, monkeypatch):
        self._noop_thread(monkeypatch)
        client.post(f"/api/segments?path={video_file}", json={"seg_in": 0.0, "seg_out": 5.0})
        client.post(f"/api/segments?path={video_file}", json={"seg_in": 10.0, "seg_out": 15.0})
        (MEDIA_ROOT / "dest").mkdir(exist_ok=True)
        resp = client.post(
            f"/api/files/export-segments?path={video_file}",
            json={"mode": "merged", "destination": "dest"},
        )
        assert resp.status_code == 200
        assert "job_id" in resp.json()

    def test_path_traversal_rejected(self):
        resp = client.get("/api/segments?path=../../etc/passwd")
        assert resp.status_code in (400, 403)

    def test_segments_isolated_per_path(self, video_file, tmp_path):
        other = "other_video.mp4"
        (MEDIA_ROOT / other).touch()
        client.post(f"/api/segments?path={video_file}", json={"seg_in": 0.0, "seg_out": 5.0})
        resp = client.get(f"/api/segments?path={other}")
        assert resp.json() == []


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
    """Run threading.Thread targets and queued download jobs synchronously."""
    import backend.main as main_mod

    class SyncThread:
        def __init__(self, target, args=(), daemon=True, **kwargs):
            self._target = target
            self._args = args

        def start(self):
            self._target(*self._args)

    monkeypatch.setattr(threading, "Thread", SyncThread)

    # Patch the download queue dispatcher to run the job inline instead of
    # enqueuing, so download tests complete synchronously without a worker.
    def sync_enqueue(job_id: str) -> None:
        job = main_mod._jobs[job_id]
        p = job["_params"]
        main_mod._run_download(
            job_id,
            p["url"],
            p["output_dir"],
            p["cookies"],
            p["cookies_file_path"],
            p.get("referer"),
            p.get("title"),
        )

    monkeypatch.setattr(main_mod, "_enqueue_download", sync_enqueue)


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
        import backend.main as main_mod

        monkeypatch.setitem(sys.modules, "yt_dlp", _make_yt_dlp_mock())
        # Prevent the worker from actually running the download
        monkeypatch.setattr(main_mod, "_enqueue_download", lambda job_id: None)
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

    def test_download_settings_persisted(self, tmp_path):
        cookies = tmp_path / "cookies.txt"
        cookies.write_text("# Netscape HTTP Cookie File\n")
        resp = client.post(
            "/api/settings",
            json={
                "download_folder": "WebVideos",
                "download_cookies_path": str(cookies),
            },
        )
        assert resp.status_code == 200
        settings = client.get("/api/settings").json()
        assert settings["download_folder"] == "WebVideos"
        assert settings["download_cookies_path"] == str(cookies)
        # Reset so other tests are unaffected
        client.post("/api/settings", json={"download_cookies_path": ""})

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

    def test_cancel_pending_job(self, monkeypatch):
        """Cancelling a pending job marks it as cancelled before it runs."""
        import backend.main as main_mod

        monkeypatch.setitem(sys.modules, "yt_dlp", _make_yt_dlp_mock())
        monkeypatch.setattr(main_mod, "_enqueue_download", lambda job_id: None)
        resp = client.post("/api/download", json={"url": "https://example.com/video"})
        job_id = resp.json()["job_id"]
        cancel_resp = client.post(f"/api/jobs/{job_id}/cancel")
        assert cancel_resp.status_code == 200
        jobs = {j["id"]: j for j in client.get("/api/jobs").json()}
        assert jobs[job_id]["status"] == "cancelled"

    def test_cancel_unknown_job_returns_404(self):
        resp = client.post("/api/jobs/nonexistent-id/cancel")
        assert resp.status_code == 404

    def test_cancel_already_done_is_noop(self, monkeypatch):
        """Cancelling a finished job returns 200 and leaves status as 'done'."""
        monkeypatch.setitem(sys.modules, "yt_dlp", _make_yt_dlp_mock())
        _sync_thread_patch(monkeypatch)
        resp = client.post("/api/download", json={"url": "https://example.com/video"})
        job_id = resp.json()["job_id"]
        assert client.get("/api/jobs").json()
        # Force done
        jobs_by_id = {j["id"]: j for j in client.get("/api/jobs").json()}
        assert jobs_by_id[job_id]["status"] == "done"
        cancel_resp = client.post(f"/api/jobs/{job_id}/cancel")
        assert cancel_resp.status_code == 200
        jobs_by_id2 = {j["id"]: j for j in client.get("/api/jobs").json()}
        assert jobs_by_id2[job_id]["status"] == "done"

    def test_cancel_running_job_sets_cancelled(self, monkeypatch):
        """When the cancel event fires mid-download, the job ends as 'cancelled'."""
        import backend.main as main_mod

        trigger = {"called": False}

        def intercepted_run(job_id, *a, **kw):
            # Cancel the job the first time progress hook would fire
            main_mod._jobs[job_id]["_cancel_event"].set()
            main_mod._jobs[job_id]["status"] = "cancelled"
            # Don't call original_run — simulates mid-run cancellation
            trigger["called"] = True

        monkeypatch.setitem(sys.modules, "yt_dlp", _make_yt_dlp_mock())
        # Run the preparation thread inline: without this the assertion below
        # races the daemon thread started by /api/download.
        _sync_thread_patch(monkeypatch)
        monkeypatch.setattr(main_mod, "_run_download", intercepted_run)
        monkeypatch.setattr(main_mod, "_enqueue_download", lambda job_id: intercepted_run(job_id))
        resp = client.post("/api/download", json={"url": "https://example.com/video"})
        job_id = resp.json()["job_id"]
        assert trigger["called"]
        jobs = {j["id"]: j for j in client.get("/api/jobs").json()}
        assert jobs[job_id]["status"] == "cancelled"

    def test_jobs_api_does_not_expose_private_fields(self, monkeypatch):
        """The /api/jobs response must not contain _cancel_event or _params."""
        import backend.main as main_mod

        monkeypatch.setitem(sys.modules, "yt_dlp", _make_yt_dlp_mock())
        monkeypatch.setattr(main_mod, "_enqueue_download", lambda job_id: None)
        resp = client.post("/api/download", json={"url": "https://example.com/video"})
        job_id = resp.json()["job_id"]
        jobs = {j["id"]: j for j in client.get("/api/jobs").json()}
        assert "_cancel_event" not in jobs[job_id]
        assert "_params" not in jobs[job_id]

    def test_sequential_queue_runs_one_at_a_time(self, monkeypatch):
        """Two jobs enqueued: second stays pending until first finishes."""
        import backend.main as main_mod

        execution_order = []
        barrier = threading.Event()

        def slow_run(job_id, *a, **kw):
            execution_order.append(("start", job_id))
            barrier.wait(timeout=5)
            main_mod._jobs[job_id]["status"] = "done"
            main_mod._jobs[job_id]["progress"] = 100
            execution_order.append(("end", job_id))

        monkeypatch.setitem(sys.modules, "yt_dlp", _make_yt_dlp_mock())

        # Patch _enqueue_download to use a local queue + worker so we test
        # sequencing without touching the global singleton queue.
        import queue as q

        local_q: q.Queue = q.Queue()

        def local_enqueue(job_id: str) -> None:
            local_q.put(job_id)

        def local_worker() -> None:
            while True:
                jid = local_q.get()
                job = main_mod._jobs.get(jid)
                if job:
                    p = job["_params"]
                    slow_run(jid, p["url"], p["output_dir"], p["cookies"], p["cookies_file_path"])
                local_q.task_done()

        monkeypatch.setattr(main_mod, "_enqueue_download", local_enqueue)
        worker_t = threading.Thread(target=local_worker, daemon=True)
        worker_t.start()

        resp1 = client.post("/api/download", json={"url": "https://example.com/video1"})
        resp2 = client.post("/api/download", json={"url": "https://example.com/video2"})
        job1 = resp1.json()["job_id"]
        job2 = resp2.json()["job_id"]

        # Give the worker time to start job1 before releasing the barrier
        import time as _time

        _time.sleep(0.05)
        # job2 must still be pending while job1 is running
        jobs = {j["id"]: j for j in client.get("/api/jobs").json()}
        assert jobs[job2]["status"] == "pending"

        barrier.set()  # let job1 finish → worker picks up job2
        local_q.join()

        jobs = {j["id"]: j for j in client.get("/api/jobs").json()}
        assert jobs[job1]["status"] == "done"
        # Verify execution order: job1 fully completed before job2 started
        job1_end = next(
            i for i, (ev, jid) in enumerate(execution_order) if ev == "end" and jid == job1
        )
        job2_start = next(
            i for i, (ev, jid) in enumerate(execution_order) if ev == "start" and jid == job2
        )
        assert job1_end < job2_start

    """Unit tests for _sniff_video_source HTML parsing strategies."""

    def _make_urlopen(self, html: str):
        """Return a mock for urllib.request.urlopen that serves *html*."""
        mock_resp = MagicMock()
        mock_resp.read.return_value = html.encode("utf-8")
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        return lambda req, timeout: mock_resp

    def test_detects_iframe_from_known_host(self, monkeypatch):
        """Detects <iframe src> pointing to a known video host in static HTML."""
        from backend.main import _sniff_video_source

        html = '<html><body><iframe src="https://iframe.mediadelivery.net/embed/99/xyz"></iframe></body></html>'
        monkeypatch.setattr("urllib.request.urlopen", self._make_urlopen(html))
        assert (
            _sniff_video_source("https://example.com/page", None)
            == "https://iframe.mediadelivery.net/embed/99/xyz"
        )

    def test_detects_video_src_tag(self, monkeypatch):
        """Detects <video src> in static HTML."""
        from backend.main import _sniff_video_source

        html = '<html><body><video src="https://cdn.example.com/video.mp4"></video></body></html>'
        monkeypatch.setattr("urllib.request.urlopen", self._make_urlopen(html))
        assert (
            _sniff_video_source("https://example.com/page", None)
            == "https://cdn.example.com/video.mp4"
        )

    def test_skips_blob_video_src(self, monkeypatch):
        """Ignores blob: URLs in <video src> and falls back to other strategies."""
        from backend.main import _sniff_video_source

        html = """<html><body>
            <video src="blob:https://example.com/fake"></video>
            <meta property="og:video" content="https://cdn.example.com/video.mp4">
        </body></html>"""
        monkeypatch.setattr("urllib.request.urlopen", self._make_urlopen(html))
        assert (
            _sniff_video_source("https://example.com/page", None)
            == "https://cdn.example.com/video.mp4"
        )

    def test_detects_og_video_meta(self, monkeypatch):
        """Detects <meta property="og:video" content="..."> (OpenGraph)."""
        from backend.main import _sniff_video_source

        html = '<html><head><meta property="og:video" content="https://iframe.mediadelivery.net/embed/1/abc"></head></html>'
        monkeypatch.setattr("urllib.request.urlopen", self._make_urlopen(html))
        assert (
            _sniff_video_source("https://example.com/page", None)
            == "https://iframe.mediadelivery.net/embed/1/abc"
        )

    def test_detects_og_video_url_meta(self, monkeypatch):
        """Detects <meta property="og:video:url" content="...">."""
        from backend.main import _sniff_video_source

        html = '<html><head><meta property="og:video:url" content="https://cdn.example.com/clip.mp4"></head></html>'
        monkeypatch.setattr("urllib.request.urlopen", self._make_urlopen(html))
        assert (
            _sniff_video_source("https://example.com/page", None)
            == "https://cdn.example.com/clip.mp4"
        )

    def test_detects_og_video_secure_url_meta(self, monkeypatch):
        """Detects <meta property="og:video:secure_url" content="...">."""
        from backend.main import _sniff_video_source

        html = '<html><head><meta property="og:video:secure_url" content="https://cdn.example.com/secure.mp4"></head></html>'
        monkeypatch.setattr("urllib.request.urlopen", self._make_urlopen(html))
        assert (
            _sniff_video_source("https://example.com/page", None)
            == "https://cdn.example.com/secure.mp4"
        )

    def test_detects_known_host_url_in_inline_script(self, monkeypatch):
        """Detects BunnyCDN embed URL in an inline <script> block."""
        from backend.main import _sniff_video_source

        html = '<html><head><script>var p={src:"https://iframe.mediadelivery.net/embed/42/vid-id"};</script></head></html>'
        monkeypatch.setattr("urllib.request.urlopen", self._make_urlopen(html))
        assert (
            _sniff_video_source("https://example.com/page", None)
            == "https://iframe.mediadelivery.net/embed/42/vid-id"
        )

    def test_detects_direct_mp4_in_inline_script(self, monkeypatch):
        """Detects a direct .mp4 URL in an inline <script> block."""
        from backend.main import _sniff_video_source

        html = '<html><head><script>var src="https://cdn.example.com/video.mp4?token=abc";</script></head></html>'
        monkeypatch.setattr("urllib.request.urlopen", self._make_urlopen(html))
        assert (
            _sniff_video_source("https://example.com/page", None)
            == "https://cdn.example.com/video.mp4?token=abc"
        )

    def test_detects_m3u8_in_inline_script(self, monkeypatch):
        """Detects an HLS .m3u8 manifest URL in an inline <script> block."""
        from backend.main import _sniff_video_source

        html = '<html><head><script>var hls="https://stream.example.com/live.m3u8";</script></head></html>'
        monkeypatch.setattr("urllib.request.urlopen", self._make_urlopen(html))
        assert (
            _sniff_video_source("https://example.com/page", None)
            == "https://stream.example.com/live.m3u8"
        )

    def test_detects_data_attribute_known_host(self, monkeypatch):
        """Detects a known-host URL in a data-* attribute."""
        from backend.main import _sniff_video_source

        html = '<html><body><div data-video-src="https://iframe.mediadelivery.net/embed/5/abc123"></div></body></html>'
        monkeypatch.setattr("urllib.request.urlopen", self._make_urlopen(html))
        assert (
            _sniff_video_source("https://example.com/page", None)
            == "https://iframe.mediadelivery.net/embed/5/abc123"
        )

    def test_detects_data_attribute_direct_mp4(self, monkeypatch):
        """Detects a direct .mp4 URL in a data-* attribute."""
        from backend.main import _sniff_video_source

        html = '<html><body><div data-src="https://cdn.example.com/clip.mp4"></div></body></html>'
        monkeypatch.setattr("urllib.request.urlopen", self._make_urlopen(html))
        assert (
            _sniff_video_source("https://example.com/page", None)
            == "https://cdn.example.com/clip.mp4"
        )

    def test_priority_iframe_over_video_tag(self, monkeypatch):
        """iframe from known host takes priority over <video src>."""
        from backend.main import _sniff_video_source

        html = """<html><body>
            <video src="https://cdn.example.com/video.mp4"></video>
            <iframe src="https://iframe.mediadelivery.net/embed/99/xyz"></iframe>
        </body></html>"""
        monkeypatch.setattr("urllib.request.urlopen", self._make_urlopen(html))
        assert (
            _sniff_video_source("https://example.com/page", None)
            == "https://iframe.mediadelivery.net/embed/99/xyz"
        )

    def test_priority_video_tag_over_meta(self, monkeypatch):
        """<video src> takes priority over og:video meta."""
        from backend.main import _sniff_video_source

        html = """<html><head>
            <meta property="og:video" content="https://cdn.example.com/meta.mp4">
        </head><body>
            <video src="https://cdn.example.com/direct.mp4"></video>
        </body></html>"""
        monkeypatch.setattr("urllib.request.urlopen", self._make_urlopen(html))
        assert (
            _sniff_video_source("https://example.com/page", None)
            == "https://cdn.example.com/direct.mp4"
        )

    def test_priority_meta_over_script(self, monkeypatch):
        """og:video meta takes priority over URLs found in inline scripts."""
        from backend.main import _sniff_video_source

        html = """<html><head>
            <meta property="og:video" content="https://cdn.example.com/meta.mp4">
            <script>var src="https://cdn.example.com/script.mp4";</script>
        </head></html>"""
        monkeypatch.setattr("urllib.request.urlopen", self._make_urlopen(html))
        assert (
            _sniff_video_source("https://example.com/page", None)
            == "https://cdn.example.com/meta.mp4"
        )

    def test_returns_none_on_no_video(self, monkeypatch):
        """Returns None when no video source is found anywhere."""
        from backend.main import _sniff_video_source

        html = "<html><body><p>No video here, just text.</p></body></html>"
        monkeypatch.setattr("urllib.request.urlopen", self._make_urlopen(html))
        assert _sniff_video_source("https://example.com/page", None) is None

    def test_returns_none_on_network_error(self, monkeypatch):
        """Returns None if the HTTP request fails."""
        from backend.main import _sniff_video_source

        def _fail(req, timeout):
            raise OSError("connection refused")

        monkeypatch.setattr("urllib.request.urlopen", _fail)
        assert _sniff_video_source("https://example.com/page", None) is None


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


# ── Security headers ──────────────────────────────────────────────────────────


class TestSecurityHeaders:
    def test_headers_present_on_api_response(self):
        resp = client.get("/api/settings")
        assert resp.headers["x-content-type-options"] == "nosniff"
        assert resp.headers["x-frame-options"] == "DENY"
        assert "default-src 'self'" in resp.headers["content-security-policy"]

    def test_csp_allows_google_fonts_and_blob(self):
        csp = client.get("/api/settings").headers["content-security-policy"]
        assert "https://fonts.googleapis.com" in csp
        assert "https://fonts.gstatic.com" in csp
        assert "worker-src 'self' blob:" in csp


# ── Database schema ─────────────────────────────────────────────────────────


class TestSchema:
    def _index_names(self):
        import sqlite3

        from backend.main import DB_PATH

        conn = sqlite3.connect(str(DB_PATH))
        try:
            return {
                r[0]
                for r in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'index'"
                ).fetchall()
            }
        finally:
            conn.close()

    def test_progress_active_index_exists(self):
        # Covering index supporting the /api/files progress-map scan (BL-035).
        assert "idx_progress_active" in self._index_names()

    def test_segments_path_index_exists(self):
        assert "idx_segments_path" in self._index_names()


# ── Delete / move DB-first atomicity (BL-034) ──────────────────────────────────


def _progress_position(rel):
    import backend.main as m

    with m.get_db() as conn:
        row = conn.execute("SELECT position FROM progress WHERE path = ?", (rel,)).fetchone()
    return None if row is None else row["position"]


class TestDeleteMoveAtomicity:
    def test_delete_removes_file_and_progress_row(self):
        f = MEDIA_ROOT / "todel.mp4"
        f.write_bytes(b"\x00" * 16)
        client.post("/api/progress?path=todel.mp4", json={"position": 1, "duration": 2})
        assert _progress_position("todel.mp4") == 1
        resp = client.delete("/api/files?path=todel.mp4")
        assert resp.status_code == 200
        assert not f.exists()
        assert _progress_position("todel.mp4") is None

    def test_delete_rolls_back_db_when_fs_fails(self, monkeypatch):
        import pathlib

        f = MEDIA_ROOT / "locked.mp4"
        f.write_bytes(b"\x00" * 16)
        client.post("/api/progress?path=locked.mp4", json={"position": 3, "duration": 6})

        def boom(self):
            raise PermissionError("locked")

        monkeypatch.setattr(pathlib.Path, "unlink", boom)
        resp = client.delete("/api/files?path=locked.mp4")
        assert resp.status_code == 423
        # FS delete failed → DB must be rolled back, row preserved, file intact.
        assert f.exists()
        assert _progress_position("locked.mp4") == 3


# ── Optional HTTP Basic auth (BL-011) ──────────────────────────────────────────


class TestBasicAuth:
    def test_disabled_by_default(self):
        # No HOARD_AUTH_* env in tests → auth off, normal access.
        assert client.get("/api/settings").status_code == 200

    def test_check_basic_auth_helper(self, monkeypatch):
        import base64

        import backend.main as m

        monkeypatch.setattr(m, "HOARD_AUTH_USER", "alice")
        monkeypatch.setattr(m, "HOARD_AUTH_PASS", "secret")
        good = "Basic " + base64.b64encode(b"alice:secret").decode()
        bad = "Basic " + base64.b64encode(b"alice:wrong").decode()
        assert m._check_basic_auth(good) is True
        assert m._check_basic_auth(bad) is False
        assert m._check_basic_auth("") is False

    def test_middleware_challenges_and_allows(self, monkeypatch):
        import base64

        import backend.main as m

        monkeypatch.setattr(m, "HOARD_AUTH_USER", "alice")
        monkeypatch.setattr(m, "HOARD_AUTH_PASS", "secret")
        monkeypatch.setattr(m, "_AUTH_ENABLED", True)
        resp = client.get("/api/settings")
        assert resp.status_code == 401
        assert resp.headers["www-authenticate"].startswith("Basic")
        token = base64.b64encode(b"alice:secret").decode()
        resp = client.get("/api/settings", headers={"Authorization": f"Basic {token}"})
        assert resp.status_code == 200


# ── PIN hashing: scrypt (BL-030) ───────────────────────────────────────────────


class TestPinHashing:
    def test_pin_stored_as_scrypt_and_verifies(self):
        import backend.main as m

        client.post("/api/settings", json={"pin": "4321"})
        with m.get_db() as conn:
            row = conn.execute("SELECT value FROM settings WHERE key='pin_hash'").fetchone()
        assert row["value"].startswith("scrypt$")
        assert client.post("/api/settings/check-pin", json={"pin": "4321"}).status_code == 200
        assert client.post("/api/settings/check-pin", json={"pin": "0000"}).status_code == 401
        client.post("/api/settings", json={"pin": ""})  # cleanup

    def test_legacy_sha256_pin_migrated_on_login(self):
        import hashlib

        import backend.main as m

        legacy = hashlib.sha256(b"1357").hexdigest()
        with m.get_db() as conn:
            m._write_setting(conn, "pin_hash", legacy)
            conn.commit()
        # Legacy PIN still verifies and is transparently upgraded.
        assert client.post("/api/settings/check-pin", json={"pin": "1357"}).status_code == 200
        with m.get_db() as conn:
            row = conn.execute("SELECT value FROM settings WHERE key='pin_hash'").fetchone()
        assert row["value"].startswith("scrypt$")
        client.post("/api/settings", json={"pin": ""})  # cleanup


# ── Rename (BL-006) ────────────────────────────────────────────────────────────


class TestRename:
    def test_rename_file_migrates_progress(self):
        f = MEDIA_ROOT / "old.mp4"
        f.write_bytes(b"\x00" * 16)
        client.post("/api/progress?path=old.mp4", json={"position": 4, "duration": 8})
        resp = client.post("/api/files/rename?path=old.mp4", json={"new_name": "new.mp4"})
        assert resp.status_code == 200
        assert not f.exists()
        assert (MEDIA_ROOT / "new.mp4").exists()
        assert _progress_position("old.mp4") is None
        assert _progress_position("new.mp4") == 4

    def test_rename_folder_migrates_children(self):
        d = MEDIA_ROOT / "season"
        d.mkdir()
        (d / "ep1.mp4").write_bytes(b"\x00" * 16)
        client.post("/api/progress?path=season/ep1.mp4", json={"position": 2, "duration": 10})
        resp = client.post("/api/files/rename?path=season", json={"new_name": "saison"})
        assert resp.status_code == 200
        assert (MEDIA_ROOT / "saison" / "ep1.mp4").exists()
        assert _progress_position("season/ep1.mp4") is None
        assert _progress_position("saison/ep1.mp4") == 2

    def test_rename_collision_409(self):
        (MEDIA_ROOT / "a.mp4").write_bytes(b"\x00" * 8)
        (MEDIA_ROOT / "b.mp4").write_bytes(b"\x00" * 8)
        resp = client.post("/api/files/rename?path=a.mp4", json={"new_name": "b.mp4"})
        assert resp.status_code == 409

    @pytest.mark.parametrize("new_name", ["sub/d.mp4", "a\\b.mp4", ".", "..", "   ", ""])
    def test_rename_invalid_name_400(self, new_name):
        (MEDIA_ROOT / "c.mp4").write_bytes(b"\x00" * 8)
        resp = client.post("/api/files/rename?path=c.mp4", json={"new_name": new_name})
        assert resp.status_code == 400

    def test_rename_not_found_404(self):
        resp = client.post("/api/files/rename?path=ghost.mp4", json={"new_name": "x.mp4"})
        assert resp.status_code == 404

    def test_rename_path_traversal_blocked(self):
        resp = client.post("/api/files/rename?path=../../etc/passwd", json={"new_name": "x"})
        assert resp.status_code == 403


# ── Subtitles (BL-008) ─────────────────────────────────────────────────────────


class TestSubtitles:
    def test_list_matches_sidecars_by_stem(self):
        (MEDIA_ROOT / "movie.mp4").write_bytes(b"\x00" * 16)
        (MEDIA_ROOT / "movie.srt").write_text("1\n00:00:01,000 --> 00:00:02,000\nHi\n")
        (MEDIA_ROOT / "movie.en.srt").write_text("1\n00:00:01,000 --> 00:00:02,000\nHi\n")
        (MEDIA_ROOT / "other.srt").write_text("x")  # different stem → excluded
        subs = client.get("/api/subtitles?path=movie.mp4").json()
        paths = {s["path"] for s in subs}
        assert "movie.srt" in paths
        assert "movie.en.srt" in paths
        assert "other.srt" not in paths
        labels = {s["label"] for s in subs}
        assert "en" in labels  # middle segment becomes the label

    def test_serve_srt_converted_to_vtt(self):
        (MEDIA_ROOT / "s.srt").write_text("1\n00:00:01,000 --> 00:00:04,000\nBonjour\n")
        resp = client.get("/api/subtitle?path=s.srt")
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/vtt")
        assert resp.text.startswith("WEBVTT")
        assert "00:00:01.000 --> 00:00:04.000" in resp.text  # comma → dot

    def test_serve_ass_converted_to_vtt_plaintext(self):
        ass = (
            "[Events]\n"
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
            "Dialogue: 0,0:00:01.00,0:00:03.00,Default,,0,0,0,,{\\i1}Hello{\\i0}\\Nworld\n"
        )
        (MEDIA_ROOT / "a.ass").write_text(ass)
        resp = client.get("/api/subtitle?path=a.ass")
        assert resp.status_code == 200
        assert resp.text.startswith("WEBVTT")
        assert "00:00:01.000 --> 00:00:03.000" in resp.text
        assert "Hello" in resp.text and "world" in resp.text
        assert "{" not in resp.text  # override tags stripped

    def test_serve_vtt_passthrough(self):
        (MEDIA_ROOT / "v.vtt").write_text("WEBVTT\n\n00:00:01.000 --> 00:00:02.000\nHey\n")
        resp = client.get("/api/subtitle?path=v.vtt")
        assert resp.status_code == 200
        assert resp.text.startswith("WEBVTT")

    def test_serve_rejects_non_subtitle(self):
        (MEDIA_ROOT / "note.txt").write_text("hello")
        assert client.get("/api/subtitle?path=note.txt").status_code == 404

    def test_serve_path_traversal_blocked(self):
        assert client.get("/api/subtitle?path=../../etc/passwd").status_code == 403


# ── Audit logging (BL-036) ─────────────────────────────────────────────────────


class TestAuditLogging:
    def test_delete_logs_audit_line(self, caplog):
        import logging

        f = MEDIA_ROOT / "audit.mp4"
        f.write_bytes(b"\x00" * 8)
        with caplog.at_level(logging.INFO, logger="hoard"):
            client.delete("/api/files?path=audit.mp4")
        assert any("file deleted" in r.getMessage() for r in caplog.records)

    def test_settings_update_logs_audit_line(self, caplog):
        import logging

        with caplog.at_level(logging.INFO, logger="hoard"):
            client.post("/api/settings", json={"sort_by": "name"})
        assert any("settings updated" in r.getMessage() for r in caplog.records)

    def test_wrong_pin_logs_warning(self, caplog):
        import logging

        client.post("/api/settings", json={"pin": "1234"})
        with caplog.at_level(logging.WARNING, logger="hoard"):
            resp = client.post("/api/settings/check-pin", json={"pin": "0000"})
        assert resp.status_code == 401
        assert any("PIN check failed" in r.getMessage() for r in caplog.records)
        client.post("/api/settings", json={"pin": ""})  # cleanup


# ── Job store TTL purge (BL-033) ───────────────────────────────────────────────


class TestJobPurge:
    def test_terminal_job_purged_after_ttl(self):
        import time

        import backend.main as m

        m._jobs.clear()
        m._jobs["old"] = {
            "id": "old",
            "status": "done",
            "_finished_at": time.monotonic() - m.JOB_TTL_SECONDS - 1,
        }
        m._purge_old_jobs()
        assert "old" not in m._jobs

    def test_terminal_job_gets_ttl_clock_then_survives(self):
        import backend.main as m

        m._jobs.clear()
        m._jobs["fresh"] = {"id": "fresh", "status": "done"}
        m._purge_old_jobs()  # first sighting: stamps the clock, keeps the job
        assert "fresh" in m._jobs
        assert "_finished_at" in m._jobs["fresh"]

    def test_active_job_never_purged(self):
        import time

        import backend.main as m

        m._jobs.clear()
        m._jobs["run"] = {
            "id": "run",
            "status": "running",
            "_finished_at": time.monotonic() - m.JOB_TTL_SECONDS - 1,
        }
        m._purge_old_jobs()
        assert "run" in m._jobs


# ── MEDIA_ROOT thread-safety (BL-032) ──────────────────────────────────────────


class TestMediaRootThreadSafety:
    def test_get_set_media_root_roundtrip(self, tmp_path):
        import backend.main as m

        original = m.get_media_root()
        try:
            newdir = tmp_path / "mr"
            newdir.mkdir()
            m.set_media_root(newdir)
            assert m.get_media_root() == newdir
        finally:
            m.set_media_root(original)

    def test_safe_path_resolves_against_current_root(self, tmp_path):
        import backend.main as m

        original = m.get_media_root()
        try:
            newdir = tmp_path / "mr2"
            newdir.mkdir()
            (newdir / "a.txt").write_text("x")
            m.set_media_root(newdir)
            assert m.safe_path("a.txt") == (newdir / "a.txt").resolve()
        finally:
            m.set_media_root(original)


# ── /api/search ──────────────────────────────────────────────────────────────


class TestSearch:
    def test_empty_query_rejected(self):
        resp = client.get("/api/search?q=")
        assert resp.status_code == 400

    def test_no_query_param_rejected(self):
        resp = client.get("/api/search")
        assert resp.status_code == 422  # FastAPI validation

    def test_search_finds_file(self):
        from tests.conftest import MEDIA_DIR

        (MEDIA_DIR / "holiday_2024.mp4").write_bytes(b"\x00" * 8)
        (MEDIA_DIR / "work_report.mp4").write_bytes(b"\x00" * 8)
        resp = client.get("/api/search?q=holiday")
        assert resp.status_code == 200
        data = resp.json()
        names = [e["name"] for e in data["entries"]]
        assert "holiday_2024.mp4" in names
        assert "work_report.mp4" not in names

    def test_search_case_insensitive(self):
        from tests.conftest import MEDIA_DIR

        (MEDIA_DIR / "MyMovie.mp4").write_bytes(b"\x00" * 8)
        resp = client.get("/api/search?q=mymovie")
        assert resp.status_code == 200
        names = [e["name"] for e in resp.json()["entries"]]
        assert "MyMovie.mp4" in names

    def test_search_recursive(self):
        from tests.conftest import MEDIA_DIR

        subdir = MEDIA_DIR / "shows"
        subdir.mkdir()
        (subdir / "episode01.mp4").write_bytes(b"\x00" * 8)
        resp = client.get("/api/search?q=episode")
        assert resp.status_code == 200
        names = [e["name"] for e in resp.json()["entries"]]
        assert "episode01.mp4" in names

    def test_search_path_traversal_blocked(self):
        resp = client.get("/api/search?q=test&path=../../../etc")
        assert resp.status_code == 403

    def test_search_scoped_to_subfolder(self):
        from tests.conftest import MEDIA_DIR

        subdir = MEDIA_DIR / "shows"
        subdir.mkdir(exist_ok=True)
        (subdir / "episode_sub.mp4").write_bytes(b"\x00" * 8)
        (MEDIA_DIR / "episode_root.mp4").write_bytes(b"\x00" * 8)
        resp = client.get("/api/search?q=episode&path=shows")
        assert resp.status_code == 200
        names = [e["name"] for e in resp.json()["entries"]]
        assert "episode_sub.mp4" in names
        assert "episode_root.mp4" not in names

    def test_search_nonexistent_path_returns_404(self):
        resp = client.get("/api/search?q=test&path=nonexistent_folder_xyz")
        assert resp.status_code == 404


class TestFileTags:
    def test_get_tags_empty(self):
        from tests.conftest import MEDIA_DIR

        f = MEDIA_DIR / "tagged.mp4"
        f.write_bytes(b"\x00" * 8)
        resp = client.get("/api/tags?path=tagged.mp4")
        assert resp.status_code == 200
        assert resp.json() == {"tags": []}

    def test_add_tag(self):
        from tests.conftest import MEDIA_DIR

        (MEDIA_DIR / "tagged.mp4").write_bytes(b"\x00" * 8)
        resp = client.post("/api/tags?path=tagged.mp4", json={"tag": "Excellent"})
        assert resp.status_code == 200
        assert resp.json()["ok"] is True
        # Tag is lowercased and returned
        tags_resp = client.get("/api/tags?path=tagged.mp4")
        assert "excellent" in tags_resp.json()["tags"]

    def test_add_empty_tag_rejected(self):
        from tests.conftest import MEDIA_DIR

        (MEDIA_DIR / "tagged.mp4").write_bytes(b"\x00" * 8)
        resp = client.post("/api/tags?path=tagged.mp4", json={"tag": "  "})
        assert resp.status_code == 400

    def test_add_duplicate_tag_idempotent(self):
        from tests.conftest import MEDIA_DIR

        (MEDIA_DIR / "tagged.mp4").write_bytes(b"\x00" * 8)
        client.post("/api/tags?path=tagged.mp4", json={"tag": "fav"})
        client.post("/api/tags?path=tagged.mp4", json={"tag": "fav"})
        tags = client.get("/api/tags?path=tagged.mp4").json()["tags"]
        assert tags.count("fav") == 1

    def test_remove_tag(self):
        from tests.conftest import MEDIA_DIR

        (MEDIA_DIR / "tagged.mp4").write_bytes(b"\x00" * 8)
        client.post("/api/tags?path=tagged.mp4", json={"tag": "toremove"})
        resp = client.delete("/api/tags?path=tagged.mp4&tag=toremove")
        assert resp.status_code == 200
        tags = client.get("/api/tags?path=tagged.mp4").json()["tags"]
        assert "toremove" not in tags

    def test_all_tags(self):
        from tests.conftest import MEDIA_DIR

        (MEDIA_DIR / "a.mp4").write_bytes(b"\x00" * 8)
        (MEDIA_DIR / "b.mp4").write_bytes(b"\x00" * 8)
        client.post("/api/tags?path=a.mp4", json={"tag": "alpha"})
        client.post("/api/tags?path=b.mp4", json={"tag": "beta"})
        resp = client.get("/api/all-tags")
        assert resp.status_code == 200
        tags = resp.json()["tags"]
        assert "alpha" in tags
        assert "beta" in tags

    def test_tags_included_in_files_list(self):
        from tests.conftest import MEDIA_DIR

        (MEDIA_DIR / "c.mp4").write_bytes(b"\x00" * 8)
        client.post("/api/tags?path=c.mp4", json={"tag": "mytag"})
        resp = client.get("/api/files")
        assert resp.status_code == 200
        entry = next((e for e in resp.json()["entries"] if e["name"] == "c.mp4"), None)
        assert entry is not None
        assert "mytag" in entry["tags"]

    def test_path_traversal_blocked_get(self):
        resp = client.get("/api/tags?path=../../../etc/passwd")
        assert resp.status_code == 403

    def test_path_traversal_blocked_post(self):
        resp = client.post("/api/tags?path=../../../etc/passwd", json={"tag": "x"})
        assert resp.status_code == 403


# ── /api/file ─────────────────────────────────────────────────────────────────


class TestFileEndpoint:
    def test_serve_image_returns_200(self):
        img = MEDIA_ROOT / "photo.jpg"
        img.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)
        resp = client.get("/api/file?path=photo.jpg")
        assert resp.status_code == 200
        assert "image" in resp.headers["content-type"]

    def test_serve_video_via_file_returns_200(self):
        vid = MEDIA_ROOT / "clip.mp4"
        vid.write_bytes(b"\x00" * 200)
        resp = client.get("/api/file?path=clip.mp4")
        assert resp.status_code == 200

    def test_file_range_returns_206(self):
        f = MEDIA_ROOT / "data.bin"
        f.write_bytes(b"A" * 500)
        resp = client.get("/api/file?path=data.bin", headers={"Range": "bytes=0-99"})
        assert resp.status_code == 206
        assert resp.headers["content-range"].startswith("bytes 0-99/")
        assert len(resp.content) == 100

    def test_file_not_found(self):
        resp = client.get("/api/file?path=ghost.jpg")
        assert resp.status_code == 404

    def test_file_path_traversal_blocked(self):
        resp = client.get("/api/file?path=../../etc/passwd")
        assert resp.status_code == 403

    def test_file_multi_range_rejected(self):
        f = MEDIA_ROOT / "multi.bin"
        f.write_bytes(b"B" * 500)
        resp = client.get("/api/file?path=multi.bin", headers={"Range": "bytes=0-9,20-29"})
        assert resp.status_code == 416


# ── /api/files list — media_type field ────────────────────────────────────────


class TestMediaType:
    def test_video_has_media_type_video(self, video_file):
        resp = client.get("/api/files?path=")
        assert resp.status_code == 200
        entries = resp.json()["entries"]
        vids = [e for e in entries if e["name"] == "sample.mp4"]
        assert vids, "video entry not found"
        assert vids[0]["media_type"] == "video"

    def test_image_has_media_type_image(self):
        img = MEDIA_ROOT / "cover.jpg"
        img.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 50)
        resp = client.get("/api/files?path=")
        entries = resp.json()["entries"]
        imgs = [e for e in entries if e["name"] == "cover.jpg"]
        assert imgs, "image entry not found"
        assert imgs[0]["media_type"] == "image"
        assert "progress" in imgs[0]

    def test_audio_has_media_type_audio(self):
        mp3 = MEDIA_ROOT / "track.mp3"
        mp3.write_bytes(b"\xff\xfb" + b"\x00" * 100)
        resp = client.get("/api/files?path=")
        entries = resp.json()["entries"]
        audios = [e for e in entries if e["name"] == "track.mp3"]
        assert audios, "audio entry not found"
        assert audios[0]["media_type"] == "audio"

    def test_pdf_has_media_type_pdf(self):
        pdf = MEDIA_ROOT / "doc.pdf"
        pdf.write_bytes(b"%PDF-1.4\n" + b"\x00" * 50)
        resp = client.get("/api/files?path=")
        entries = resp.json()["entries"]
        pdfs = [e for e in entries if e["name"] == "doc.pdf"]
        assert pdfs, "pdf entry not found"
        assert pdfs[0]["media_type"] == "pdf"

    def test_unknown_file_has_media_type_other_and_no_progress(self):
        txt = MEDIA_ROOT / "notes.txt"
        txt.write_text("hello")
        resp = client.get("/api/files?path=")
        entries = resp.json()["entries"]
        txts = [e for e in entries if e["name"] == "notes.txt"]
        assert txts, "txt entry not found"
        assert txts[0]["media_type"] == "other"
        assert "progress" not in txts[0]


# ── /api/archive ───────────────────────────────────────────────────────────────


class TestArchive:
    def _make_cbz(self, path, image_names):
        import zipfile as zf

        with zf.ZipFile(path, "w") as z:
            for name in image_names:
                z.writestr(name, b"\xff\xd8\xff\xe0" + b"\x00" * 50)

    def test_archive_list_cbz(self):
        cbz = MEDIA_ROOT / "comic.cbz"
        self._make_cbz(cbz, ["page1.jpg", "page2.jpg", "page3.jpg"])
        resp = client.get("/api/archive/list?path=comic.cbz")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 3
        assert "page1.jpg" in data["images"]

    def test_archive_list_zip(self):
        zp = MEDIA_ROOT / "images.zip"
        self._make_cbz(zp, ["a.png", "b.png"])
        resp = client.get("/api/archive/list?path=images.zip")
        assert resp.status_code == 200
        assert resp.json()["count"] == 2

    def test_archive_image_returns_bytes(self):
        cbz = MEDIA_ROOT / "pages.cbz"
        self._make_cbz(cbz, ["img0.jpg", "img1.jpg"])
        resp = client.get("/api/archive/image?path=pages.cbz&index=0")
        assert resp.status_code == 200
        assert "image" in resp.headers["content-type"]

    def test_archive_image_index_out_of_range(self):
        cbz = MEDIA_ROOT / "single.cbz"
        self._make_cbz(cbz, ["only.jpg"])
        resp = client.get("/api/archive/image?path=single.cbz&index=5")
        assert resp.status_code == 404

    def test_archive_list_not_found(self):
        resp = client.get("/api/archive/list?path=ghost.cbz")
        assert resp.status_code == 404

    def test_archive_unsupported_format(self):
        bad = MEDIA_ROOT / "file.tar"
        bad.write_bytes(b"x" * 10)
        resp = client.get("/api/archive/list?path=file.tar")
        assert resp.status_code == 415

    def test_archive_path_traversal_blocked(self):
        resp = client.get("/api/archive/list?path=../../etc/passwd")
        assert resp.status_code == 403

    def test_archive_image_path_traversal_blocked(self):
        resp = client.get("/api/archive/image?path=../../etc/passwd&index=0")
        assert resp.status_code == 403


# ── Progress for non-video media ───────────────────────────────────────────────


class TestProgressNonVideo:
    def test_save_and_read_progress_for_image(self):
        img = MEDIA_ROOT / "scene.jpg"
        img.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 50)
        resp = client.post("/api/progress?path=scene.jpg", json={"position": 2, "duration": 10})
        assert resp.status_code == 200
        resp = client.get("/api/progress?path=scene.jpg")
        assert resp.status_code == 200
        data = resp.json()
        assert data["position"] == 2
        assert data["duration"] == 10
        assert data["percent"] == 20.0

    def test_save_and_read_progress_for_pdf(self):
        pdf = MEDIA_ROOT / "manual.pdf"
        pdf.write_bytes(b"%PDF-1.4\n" + b"\x00" * 50)
        resp = client.post("/api/progress?path=manual.pdf", json={"position": 5, "duration": 20})
        assert resp.status_code == 200
        data = client.get("/api/progress?path=manual.pdf").json()
        assert data["position"] == 5
        assert data["duration"] == 20


class TestVersion:
    def test_app_version_matches_pyproject(self):
        import tomllib
        from pathlib import Path as _P

        pyproject = _P(main_mod.__file__).resolve().parent.parent / "pyproject.toml"
        with pyproject.open("rb") as fh:
            expected = tomllib.load(fh)["project"]["version"]
        assert main_mod.VERSION == expected != "0.0.0"
        assert client.get("/api/settings").json()["app_version"] == expected


# ── Download history (BL-075) ─────────────────────────────────────────────────


class TestDownloadHistory:
    def _run_one(self, monkeypatch, url="https://example.com/video"):
        monkeypatch.setitem(sys.modules, "yt_dlp", _make_yt_dlp_mock())
        _sync_thread_patch(monkeypatch)
        return client.post("/api/download", json={"url": url}).json()["job_id"]

    def test_history_empty_initially(self):
        data = client.get("/api/downloads").json()
        assert data == {"total": 0, "items": []}

    def test_successful_download_is_recorded(self, monkeypatch):
        job_id = self._run_one(monkeypatch)
        data = client.get("/api/downloads").json()
        assert data["total"] == 1
        entry = data["items"][0]
        assert entry["id"] == job_id
        assert entry["url"] == "https://example.com/video"
        assert entry["status"] == "done"
        assert entry["error"] is None
        assert entry["finished_at"] is not None

    def test_failed_download_records_the_error(self, monkeypatch):
        mock = _make_yt_dlp_mock()

        class _Boom:
            def __init__(self, *a, **kw):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def extract_info(self, *a, **kw):
                raise RuntimeError("network unreachable")

        mock.YoutubeDL = _Boom
        monkeypatch.setitem(sys.modules, "yt_dlp", mock)
        _sync_thread_patch(monkeypatch)
        client.post("/api/download", json={"url": "https://example.com/broken"})
        entry = client.get("/api/downloads").json()["items"][0]
        assert entry["status"] == "error"
        assert "network unreachable" in entry["error"]

    def test_history_survives_job_store_purge(self, monkeypatch):
        """The whole point: the entry outlives the in-memory job."""
        self._run_one(monkeypatch)
        main_mod._jobs.clear()
        assert client.get("/api/jobs").json() == []
        assert client.get("/api/downloads").json()["total"] == 1

    def test_non_terminal_rows_become_interrupted_at_startup(self):
        with main_mod.get_db() as conn:
            conn.execute(
                "INSERT INTO downloads (id, url, status) VALUES (?, ?, ?)",
                ("stuck-job", "https://example.com/x", "running"),
            )
            conn.execute(
                "INSERT INTO downloads (id, url, status) VALUES (?, ?, ?)",
                ("finished-job", "https://example.com/y", "done"),
            )
            conn.commit()
        main_mod.mark_interrupted_downloads()
        by_id = {e["id"]: e for e in client.get("/api/downloads").json()["items"]}
        assert by_id["stuck-job"]["status"] == "interrupted"
        assert by_id["stuck-job"]["finished_at"] is not None
        assert by_id["finished-job"]["status"] == "done"

    def test_status_filter_and_pagination(self, monkeypatch):
        self._run_one(monkeypatch, "https://example.com/a")
        self._run_one(monkeypatch, "https://example.com/b")
        assert client.get("/api/downloads").json()["total"] == 2
        assert len(client.get("/api/downloads?limit=1").json()["items"]) == 1
        page2 = client.get("/api/downloads?limit=1&offset=1").json()
        assert page2["total"] == 2 and len(page2["items"]) == 1
        assert client.get("/api/downloads?status=error").json()["items"] == []
        assert len(client.get("/api/downloads?status=done").json()["items"]) == 2

    def test_delete_single_entry(self, monkeypatch):
        job_id = self._run_one(monkeypatch)
        assert client.delete(f"/api/downloads/{job_id}").status_code == 200
        assert client.get("/api/downloads").json()["total"] == 0
        assert client.delete(f"/api/downloads/{job_id}").status_code == 404

    def test_clear_history(self, monkeypatch):
        self._run_one(monkeypatch, "https://example.com/a")
        self._run_one(monkeypatch, "https://example.com/b")
        resp = client.delete("/api/downloads")
        assert resp.status_code == 200 and resp.json()["deleted"] == 2
        assert client.get("/api/downloads").json()["total"] == 0

    def test_retention_purges_old_entries(self):
        with main_mod.get_db() as conn:
            conn.execute(
                "INSERT INTO downloads (id, url, status, created_at) "
                "VALUES (?, ?, ?, datetime('now', '-40 days'))",
                ("old-job", "https://example.com/old", "done"),
            )
            conn.commit()
        # Default retention (0) keeps everything
        main_mod._purge_download_history()
        assert client.get("/api/downloads").json()["total"] == 1
        client.post("/api/settings", json={"download_history_days": 30})
        main_mod._purge_download_history()
        assert client.get("/api/downloads").json()["total"] == 0

    def test_retention_setting_roundtrip(self):
        assert client.get("/api/settings").json()["download_history_days"] == "0"
        client.post("/api/settings", json={"download_history_days": 15})
        assert client.get("/api/settings").json()["download_history_days"] == "15"


# ── Logs (BL-076) ─────────────────────────────────────────────────────────────


class TestLogs:
    def test_reports_disabled_when_no_log_file(self):
        """The suite runs with an empty LOG_DIR — the endpoint must say so."""
        data = client.get("/api/logs").json()
        assert data["enabled"] is False
        assert data["lines"] == []
        assert data["retention_days"] == main_mod.LOG_RETENTION_DAYS

    def test_reads_tail_of_log_file(self, monkeypatch, tmp_path):
        log_file = tmp_path / "hoard.log"
        log_file.write_text(
            "\n".join(f"2026-01-01 00:00:0{i % 10} [INFO] hoard: line {i}" for i in range(50)),
            encoding="utf-8",
        )
        monkeypatch.setattr(main_mod, "LOG_FILE", log_file)
        data = client.get("/api/logs?lines=5").json()
        assert data["enabled"] is True
        assert len(data["lines"]) == 5
        assert data["lines"][-1].endswith("line 49")

    def test_level_filter_keeps_traceback_continuations(self, monkeypatch, tmp_path):
        log_file = tmp_path / "hoard.log"
        log_file.write_text(
            "2026-01-01 00:00:00 [INFO] hoard: routine\n"
            "2026-01-01 00:00:01 [ERROR] hoard: boom\n"
            "    File nowhere.py, line 1\n"
            "2026-01-01 00:00:02 [INFO] hoard: routine again\n",
            encoding="utf-8",
        )
        monkeypatch.setattr(main_mod, "LOG_FILE", log_file)
        lines = client.get("/api/logs?level=ERROR").json()["lines"]
        assert len(lines) == 2
        assert "boom" in lines[0]
        assert "File nowhere.py" in lines[1]

    def test_invalid_line_count_is_rejected(self):
        assert client.get("/api/logs?lines=0").status_code == 422
        assert client.get("/api/logs?lines=99999").status_code == 422


# ── Restart (BL-077) ──────────────────────────────────────────────────────────


class TestRestart:
    def _capture_terminate(self, monkeypatch):
        """Replace the real process kill with an event, so tests survive."""
        fired = threading.Event()
        monkeypatch.setattr(main_mod, "_terminate_process", fired.set)
        return fired

    def test_restart_answers_then_terminates(self, monkeypatch):
        fired = self._capture_terminate(monkeypatch)
        resp = client.post("/api/restart")
        assert resp.status_code == 200
        assert resp.json()["ok"] is True
        assert isinstance(resp.json()["supervised"], bool)
        assert fired.wait(timeout=5), "process termination was never triggered"

    def test_refuses_while_a_download_is_active(self, monkeypatch):
        fired = self._capture_terminate(monkeypatch)
        main_mod._jobs["live"] = {
            "id": "live",
            "type": "download",
            "status": "running",
            "url": "https://example.com/v",
        }
        resp = client.post("/api/restart")
        assert resp.status_code == 409
        assert "force=true" in resp.json()["detail"]
        assert not fired.is_set()

    def test_force_restarts_despite_active_download(self, monkeypatch):
        fired = self._capture_terminate(monkeypatch)
        main_mod._jobs["live"] = {
            "id": "live",
            "type": "download",
            "status": "running",
            "url": "https://example.com/v",
        }
        resp = client.post("/api/restart", json={"force": True})
        assert resp.status_code == 200
        assert fired.wait(timeout=5)

    def test_finished_downloads_do_not_block(self, monkeypatch):
        fired = self._capture_terminate(monkeypatch)
        main_mod._jobs["old"] = {
            "id": "old",
            "type": "download",
            "status": "done",
            "url": "https://example.com/v",
        }
        assert client.post("/api/restart").status_code == 200
        assert fired.wait(timeout=5)

    def test_supervised_flag_follows_env_override(self, monkeypatch):
        monkeypatch.setenv("RESTART_SUPERVISED", "0")
        assert main_mod._is_supervised() is False
        monkeypatch.setenv("RESTART_SUPERVISED", "1")
        assert main_mod._is_supervised() is True


# ── Download worker resilience (BL-078) ───────────────────────────────────────


class TestDownloadWorkerResilience:
    """A crashing job must not kill the worker thread for the whole process."""

    def _wait_for_terminal(self, job_id, timeout=5.0):
        """Wait until the real worker thread has settled this job.

        Polling the queue would race the preparation thread, which enqueues the
        job slightly after /api/download returns.
        """
        deadline = time.time() + timeout
        while time.time() < deadline:
            job = main_mod._jobs.get(job_id)
            if job and job.get("status") in main_mod._TERMINAL_DOWNLOAD_STATES:
                return True
            time.sleep(0.02)
        return False

    def test_worker_survives_a_crashing_job(self, monkeypatch):
        calls = []

        def exploding_run(job_id, *a, **kw):
            calls.append(job_id)
            if len(calls) == 1:
                raise RuntimeError("yt-dlp exploded")
            job = main_mod._jobs[job_id]
            job["status"] = "done"
            main_mod._persist_download(job)  # the real _run_download does this

        monkeypatch.setitem(sys.modules, "yt_dlp", _make_yt_dlp_mock())
        monkeypatch.setattr(main_mod, "_run_download", exploding_run)

        first = client.post("/api/download", json={"url": "https://example.com/one"})
        assert first.status_code == 200
        first_id = first.json()["job_id"]
        assert self._wait_for_terminal(first_id), "worker never picked up the first job"

        # The crashing job is reported as an error instead of vanishing
        entry = {e["id"]: e for e in client.get("/api/downloads").json()["items"]}[first_id]
        assert entry["status"] == "error"
        assert "yt-dlp exploded" in entry["error"]

        # ...and the worker is still alive to process the next one
        second = client.post("/api/download", json={"url": "https://example.com/two"})
        second_id = second.json()["job_id"]
        assert self._wait_for_terminal(second_id), "worker died after the first job crashed"
        assert len(calls) == 2
        entry2 = {e["id"]: e for e in client.get("/api/downloads").json()["items"]}[second_id]
        assert entry2["status"] == "done"

    def test_worker_thread_is_still_running(self):
        alive = [t for t in threading.enumerate() if t.name == "dl-worker" and t.is_alive()]
        assert alive, "the download worker thread is gone"


# ── Sourcery review follow-ups on PR #39 ──────────────────────────────────────


class TestDownloadHistoryReviewFixes:
    def _seed(self, rows):
        with main_mod.get_db() as conn:
            for i, (status, age_days) in enumerate(rows):
                conn.execute(
                    "INSERT INTO downloads (id, url, status, created_at) "
                    "VALUES (?, ?, ?, datetime('now', ?))",
                    (f"job-{i}", f"https://example.com/{i}", status, f"-{age_days} days"),
                )
            conn.commit()

    def test_total_respects_the_status_filter(self):
        """A filtered listing must report the filtered count, not the grand total."""
        self._seed([("done", 0), ("done", 0), ("error", 0), ("cancelled", 0)])
        assert client.get("/api/downloads").json()["total"] == 4
        done = client.get("/api/downloads?status=done").json()
        assert done["total"] == 2 and len(done["items"]) == 2
        error = client.get("/api/downloads?status=error").json()
        assert error["total"] == 1

    def test_filtered_total_survives_pagination(self):
        self._seed([("done", 0)] * 5 + [("error", 0)] * 3)
        page = client.get("/api/downloads?status=done&limit=2").json()
        assert page["total"] == 5, "total must count all matching rows, not the page"
        assert len(page["items"]) == 2

    def test_retention_is_applied_at_startup(self):
        """An instance that never receives a download must still purge old rows."""
        client.post("/api/settings", json={"download_history_days": 30})
        self._seed([("done", 40), ("done", 1)])
        assert client.get("/api/downloads").json()["total"] == 2
        # Simulates the module-level call made right after init_db()
        main_mod._purge_download_history()
        items = client.get("/api/downloads").json()["items"]
        assert len(items) == 1, "the 40-day-old entry should have been purged"
