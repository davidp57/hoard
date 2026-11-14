"""HereSphere API for FramePlayerX (FEAT-HERESPHERE, BL-142 / BL-143)."""

import base64
import sqlite3
import time
from contextlib import contextmanager

import pytest
from starlette.testclient import TestClient

import backend.main as m
from backend.main import app

from .conftest import DATA_DIR, MEDIA_DIR

client = TestClient(app)


@contextmanager
def _db():
    conn = sqlite3.connect(str(DATA_DIR / "test.db"))
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _video(rel: str, size: int = 256) -> str:
    p = MEDIA_DIR / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"\x00" * size)
    return rel


def _progress(rel: str, position: float, duration: float, watched: int = 0, age: int = 0):
    with _db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO progress (path, position, duration, watched, updated_at) "
            "VALUES (?, ?, ?, ?, datetime('now', ?))",
            (rel, position, duration, watched, f"-{age} seconds"),
        )


def _row(rel: str):
    with _db() as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute("SELECT * FROM progress WHERE path = ?", (rel,)).fetchone()


def _scene_url(rel: str) -> str:
    return "/heresphere/scene/" + m._heresphere_id(rel)


@pytest.fixture(autouse=True)
def _no_ffprobe(monkeypatch):
    """No test reaches a real ffprobe: the probe answers what each test says."""
    m._heresphere_probe_cache.clear()
    monkeypatch.setattr(m, "_read_media_info", lambda file: {})
    yield
    m._heresphere_probe_cache.clear()


def _probe_returns(monkeypatch, duration=None, width=None, height=None):
    calls = []

    def fake(file):
        calls.append(file)
        return {"duration": duration, "video": {"width": width, "height": height}}

    monkeypatch.setattr(m, "_read_media_info", fake)
    return calls


# ── Scene ids ─────────────────────────────────────────────────────────────────


class TestSceneId:
    def test_round_trip_without_padding(self):
        rel = "VR/Été à la plage 180_LR.mp4"
        _video(rel)
        scene_id = m._heresphere_id(rel)
        assert "=" not in scene_id and "/" not in scene_id and "+" not in scene_id
        assert m._heresphere_file(scene_id) == (MEDIA_DIR / rel).resolve()

    @pytest.mark.parametrize(
        "rel",
        ["../outside.mp4", "../../etc/passwd", "/etc/passwd"],
    )
    def test_out_of_root_is_404(self, rel):
        resp = client.post(_scene_url(rel), json={})
        assert resp.status_code == 404

    def test_non_video_is_404(self):
        (MEDIA_DIR / "notes.txt").write_text("hi")
        assert client.post(_scene_url("notes.txt"), json={}).status_code == 404

    def test_missing_file_is_404(self):
        assert client.post(_scene_url("nope.mp4"), json={}).status_code == 404

    def test_garbage_id_is_404(self):
        assert client.post("/heresphere/scene/%%%not-base64", json={}).status_code == 404
        assert client.post("/heresphere/scene/_w", json={}).status_code == 404


# ── Library ───────────────────────────────────────────────────────────────────


class TestLibrary:
    def test_empty_library(self):
        resp = client.post("/heresphere", json={"username": "u", "password": "p"})
        assert resp.status_code == 200
        assert resp.json() == {"access": 1, "library": []}

    def test_accepts_a_post_without_body(self):
        assert client.post("/heresphere").status_code == 200

    def test_groups_in_order(self):
        a = _video("a.mp4")
        b = _video("b.mp4")
        _video("done.mp4")
        _video("VR/new1.mp4")
        _video("VR/sub/new2.mp4")
        _video("VR/started.mp4")
        _video("VR/cover.jpg")
        _progress(a, 30, 100, age=10)
        _progress(b, 50, 100, age=5)
        _progress("done.mp4", 95, 100, age=1)
        _progress("VR/started.mp4", 10, 100, age=20)
        _progress("gone.mp4", 10, 100)  # file deleted outside Hoard
        with _db() as conn:
            conn.execute("INSERT INTO quick_folders (path) VALUES ('VR')")

        lib = client.post("/heresphere", json={}).json()
        assert lib["access"] == 1
        groups = {g["name"]: g["list"] for g in lib["library"]}
        assert [g["name"] for g in lib["library"]] == [
            "En cours",
            "Récemment vus",
            "Non vus",
            "VR",
        ]
        assert groups["En cours"] == [_scene_url(b), _scene_url(a), _scene_url("VR/started.mp4")]
        assert groups["Récemment vus"] == [
            _scene_url("done.mp4"),
            _scene_url(b),
            _scene_url(a),
            _scene_url("VR/started.mp4"),
        ]
        assert sorted(groups["Non vus"]) == sorted(
            [_scene_url("VR/new1.mp4"), _scene_url("VR/sub/new2.mp4")]
        )
        assert groups["VR"] == [
            _scene_url("VR/new1.mp4"),
            _scene_url("VR/started.mp4"),
            _scene_url("VR/sub/new2.mp4"),
        ]

    def test_watched_threshold_decides_in_progress(self):
        rel = _video("almost.mp4")
        _progress(rel, 85, 100)
        groups = {g["name"]: g["list"] for g in client.post("/heresphere").json()["library"]}
        assert _scene_url(rel) in groups["En cours"]
        with _db() as conn:
            conn.execute("INSERT INTO settings (key, value) VALUES ('watched_threshold', '80')")
        groups = {g["name"]: g["list"] for g in client.post("/heresphere").json()["library"]}
        assert "En cours" not in groups

    def test_unmarked_file_is_not_recently_watched(self):
        rel = _video("unmarked.mp4")
        _progress(rel, 0, 0, watched=0)
        assert client.post("/heresphere").json()["library"] == []


# ── Scan ──────────────────────────────────────────────────────────────────────


class TestScan:
    def test_details_of_every_listed_scene(self):
        a = _video("Film 180_LR.mp4")
        _video("VR/clip.mp4")
        _progress(a, 30, 4893.5)
        with _db() as conn:
            conn.execute("INSERT INTO quick_folders (path) VALUES ('VR')")

        data = client.post("/heresphere/scan", json={}).json()
        by_link = {s["link"]: s for s in data["scanData"]}
        assert set(by_link) == {_scene_url(a), _scene_url("VR/clip.mp4")}
        film = by_link[_scene_url(a)]
        assert film["title"] == "Film 180_LR"
        assert film["duration"] == 4893.5  # seconds: FPX reads < 86400 as seconds
        assert isinstance(film["dateAdded"], int) and film["dateAdded"] > 1_000_000_000
        assert "duration" not in by_link[_scene_url("VR/clip.mp4")]

    def test_scan_never_probes(self, monkeypatch):
        calls = _probe_returns(monkeypatch, duration=60)
        _video("VR/clip.mp4")
        with _db() as conn:
            conn.execute("INSERT INTO quick_folders (path) VALUES ('VR')")
        client.post("/heresphere/scan")
        assert calls == []


# ── Scene ─────────────────────────────────────────────────────────────────────


class TestScene:
    def test_sbs_by_name(self):
        rel = _video("Beach_180_LR.mp4", size=4096)
        _progress(rel, 10, 1800)
        scene = client.post(_scene_url(rel), json={"needsMediaSource": True}).json()
        assert scene["title"] == "Beach_180_LR"
        assert scene["duration"] == 1_800_000
        assert scene["projection"] == "equirectangular"
        assert scene["stereo"] == "sbs"
        assert scene["fov"] == 180
        assert scene["eventServer"] == "/heresphere/events"
        assert scene["isFavorite"] is False
        assert "writeFavorite" not in scene
        assert "thumbnailImage" not in scene
        (source,) = scene["media"][0]["sources"]
        assert source["url"] == "/api/file?path=Beach_180_LR.mp4"
        assert source["size"] == 4096

    def test_flat_by_default(self, monkeypatch):
        _probe_returns(monkeypatch, duration=42.0, width=1920, height=1080)
        rel = _video("holiday.mp4")
        scene = client.post(_scene_url(rel), json={}).json()
        assert scene["projection"] == "perspective"
        assert scene["stereo"] == "mono"
        assert "fov" not in scene
        assert scene["duration"] == 42_000
        source = scene["media"][0]["sources"][0]
        assert (source["width"], source["height"], source["resolution"]) == (1920, 1080, 1080)

    def test_two_to_one_ratio_says_sbs(self, monkeypatch):
        _probe_returns(monkeypatch, duration=60.0, width=5760, height=2880)
        rel = _video("no clue in the name.mp4")
        scene = client.post(_scene_url(rel), json={}).json()
        assert (scene["projection"], scene["stereo"]) == ("equirectangular", "sbs")

    @pytest.mark.parametrize(
        ("mode", "projection", "stereo"),
        [
            ("off", "perspective", "mono"),
            ("flat", "equirectangular", "mono"),
            ("sbs", "equirectangular", "sbs"),
        ],
    )
    def test_vr_mode_wins_over_the_name(self, mode, projection, stereo):
        rel = _video("Beach_180_LR.mp4")
        client.post(f"/api/vr-mode?path={rel}", json={"mode": mode})
        scene = client.post(_scene_url(rel), json={}).json()
        assert (scene["projection"], scene["stereo"]) == (projection, stereo)

    def test_media_url_serves_the_file(self):
        rel = _video("dir with space/é & #.mp4", size=1000)
        scene = client.post(_scene_url(rel), json={}).json()
        url = scene["media"][0]["sources"][0]["url"]
        resp = client.get(url, headers={"Range": "bytes=0-99"})
        assert resp.status_code == 206
        assert len(resp.content) == 100

    def test_probe_is_cached(self, monkeypatch):
        calls = _probe_returns(monkeypatch, duration=60.0, width=1920, height=1080)
        rel = _video("cached.mp4")
        client.post(_scene_url(rel), json={})
        client.post(_scene_url(rel), json={})
        assert len(calls) == 1

    def test_unprobeable_file_still_answers(self):
        rel = _video("broken.mp4")
        scene = client.post(_scene_url(rel), json={}).json()
        assert "duration" not in scene
        assert scene["projection"] == "perspective"


# ── Events ────────────────────────────────────────────────────────────────────


def _event(rel: str, code: int, ms: float, host: str = "http://nas.example:8100"):
    return client.post(
        "/heresphere/events",
        json={
            "username": "",
            "id": host + _scene_url(rel),
            "title": rel,
            "event": code,
            "time": ms,
            "speed": 1.0,
            "utc": time.time() * 1000,
            "connectionKey": "",
        },
    )


class TestEvents:
    def test_sequence_open_play_pause_close(self, monkeypatch):
        _probe_returns(monkeypatch, duration=100.0)
        rel = _video("VR/movie.mp4")

        assert _event(rel, 0, 0).status_code == 200
        assert _row(rel) is None, "open writes nothing"

        assert _event(rel, 1, 0).status_code == 200
        row = _row(rel)
        assert (row["position"], row["duration"], row["watched"]) == (0, 100, 0)

        _event(rel, 2, 30_000)
        assert _row(rel)["position"] == 30

        _event(rel, 1, 30_000)
        _event(rel, 3, 45_500)
        row = _row(rel)
        assert (row["position"], row["watched"]) == (45.5, 0)

        progress = client.get(f"/api/progress?path={rel}").json()
        assert progress["percent"] == 45.5

    def test_watched_past_threshold(self):
        rel = _video("film.mp4")
        _progress(rel, 0, 200)
        _event(rel, 3, 179_000)  # 89.5 %
        assert _row(rel)["watched"] == 0
        _event(rel, 3, 180_000)  # 90 %
        assert _row(rel)["watched"] == 1
        assert client.get(f"/api/progress?path={rel}").json()["percent"] == 100

    def test_threshold_setting_applies(self):
        with _db() as conn:
            conn.execute("INSERT INTO settings (key, value) VALUES ('watched_threshold', '50')")
        rel = _video("film.mp4")
        _progress(rel, 0, 200)
        _event(rel, 2, 100_000)
        assert _row(rel)["watched"] == 1

    def test_updated_at_moves_to_recently_watched(self):
        old = _video("old.mp4")
        new = _video("new.mp4")
        _progress(old, 10, 100, age=10)
        _progress(new, 10, 100, age=3600)
        _event(new, 2, 20_000)
        groups = {g["name"]: g["list"] for g in client.post("/heresphere").json()["library"]}
        assert groups["Récemment vus"][0] == _scene_url(new)

    def test_out_of_root_refused_without_writing(self):
        resp = _event("../outside.mp4", 2, 10_000)
        assert resp.status_code == 404
        with _db() as conn:
            assert conn.execute("SELECT COUNT(*) FROM progress").fetchone()[0] == 0

    def test_unknown_file_refused_without_writing(self):
        assert _event("missing.mp4", 2, 10_000).status_code == 404
        with _db() as conn:
            assert conn.execute("SELECT COUNT(*) FROM progress").fetchone()[0] == 0

    def test_foreign_url_refused(self):
        resp = client.post(
            "/heresphere/events",
            json={"id": "http://elsewhere/video/1", "event": 2, "time": 1000},
        )
        assert resp.status_code == 404

    def test_unknown_event_code_refused(self):
        rel = _video("film.mp4")
        assert _event(rel, 7, 1000).status_code == 400
        assert _row(rel) is None

    def test_unknown_duration_keeps_the_position(self):
        rel = _video("unprobeable.mp4")
        _event(rel, 2, 12_000)
        row = _row(rel)
        assert (row["position"], row["duration"], row["watched"]) == (12, 0, 0)


# ── Authentication and the cross-site guard ───────────────────────────────────


class TestAuth:
    @pytest.fixture()
    def auth_on(self, monkeypatch):
        monkeypatch.setattr(m, "HOARD_AUTH_USER", "alice")
        monkeypatch.setattr(m, "HOARD_AUTH_PASS", "secret")
        monkeypatch.setattr(m, "_AUTH_ENABLED", True)
        token = base64.b64encode(b"alice:secret").decode()
        return {"Authorization": f"Basic {token}", "User-Agent": "FramePlayerX"}

    def _routes(self, rel):
        return [
            ("/heresphere", {"username": "alice", "password": "secret"}),
            ("/heresphere/scan", {"username": "alice", "password": "secret"}),
            (_scene_url(rel), {"needsMediaSource": True}),
            ("/heresphere/events", {"id": "http://h" + _scene_url(rel), "event": 2, "time": 1}),
        ]

    def test_refused_without_credentials(self, auth_on):
        rel = _video("film.mp4")
        for path, body in self._routes(rel):
            assert client.post(path, json=body).status_code == 401, path

    def test_basic_auth_without_sec_fetch_passes(self, auth_on):
        rel = _video("film.mp4")
        for path, body in self._routes(rel):
            resp = client.post(path, json=body, headers=auth_on)
            assert resp.status_code == 200, (path, resp.text)

    def test_body_credentials_alone_are_not_enough(self, auth_on):
        resp = client.post("/heresphere", json={"username": "alice", "password": "secret"})
        assert resp.status_code == 401

    def test_cross_site_browser_write_still_refused(self, auth_on):
        rel = _video("film.mp4")
        headers = {**auth_on, "Sec-Fetch-Site": "cross-site"}
        resp = client.post(
            "/heresphere/events",
            json={"id": "http://h" + _scene_url(rel), "event": 2, "time": 1},
            headers=headers,
        )
        assert resp.status_code == 403
        assert _row(rel) is None
