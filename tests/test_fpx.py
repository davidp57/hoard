"""FramePlayerX handoff (FEAT-FPX-HANDOFF, BL-144), against a fake FPX.

The fake speaks FPX's DeoVR remote as read in its sources: 4-byte little-endian
length, then UTF-8 JSON; length 0 is a ping.
"""

import json
import socket
import sqlite3
import threading
import time
from contextlib import contextmanager
from urllib.parse import parse_qs, urlparse

import pytest
from starlette.testclient import TestClient

import backend.main as m
from backend.main import app

from .conftest import DATA_DIR, MEDIA_DIR

client = TestClient(app)
ORIGIN = "http://hoard.lan:8000"


class FakeFpx:
    """A one-client DeoVR server on 127.0.0.1 that records what it receives."""

    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(("127.0.0.1", 0))
        self.server.listen(1)
        self.port = self.server.getsockname()[1]
        self.conn: socket.socket | None = None
        self.received: list[dict] = []
        self._connected = threading.Event()
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    def _serve(self):
        try:
            conn, _ = self.server.accept()
        except OSError:
            return
        self.conn = conn
        self._connected.set()
        buf = b""
        conn.settimeout(0.1)
        while True:
            try:
                chunk = conn.recv(65536)
            except TimeoutError:
                continue
            except OSError:
                return
            if not chunk:
                return
            buf += chunk
            while len(buf) >= 4:
                size = int.from_bytes(buf[:4], "little")
                if len(buf) < 4 + size:
                    break
                payload, buf = buf[4 : 4 + size], buf[4 + size :]
                if payload:
                    self.received.append(json.loads(payload))

    def send(self, message: dict | None):
        """Send a status message; None sends a ping."""
        assert self._connected.wait(5), "Hoard never connected"
        payload = b"" if message is None else json.dumps(message).encode()
        self.conn.sendall(len(payload).to_bytes(4, "little") + payload)

    def wait_received(self, count: int = 1) -> list[dict]:
        _until(lambda: len(self.received) >= count, "FPX message never arrived")
        return self.received

    def drop(self):
        conn, self.conn = self.conn, None
        if conn:
            try:
                conn.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            conn.close()

    def close(self):
        self.drop()
        self.server.close()


def _until(cond, what: str, timeout: float = 5.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if cond():
            return
        time.sleep(0.02)
    raise AssertionError(what)


@contextmanager
def _db():
    conn = sqlite3.connect(str(DATA_DIR / "test.db"))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _video(rel: str = "films/movie.mp4") -> str:
    p = MEDIA_DIR / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"0123456789" * 100)
    return rel


def _progress(rel: str, position: float, duration: float, watched: int = 0):
    with _db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO progress (path, position, duration, watched) "
            "VALUES (?, ?, ?, ?)",
            (rel, position, duration, watched),
        )


def _row(rel: str):
    with _db() as conn:
        return conn.execute("SELECT * FROM progress WHERE path = ?", (rel,)).fetchone()


def _set_host(host: str = "frame.lan"):
    with _db() as conn:
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('fpx_host', ?)", (host,))


def _status(fake: FakeFpx, url: str, position: float, duration: float = 600.0, state: int = 0):
    fake.send(
        {
            "path": url,
            "duration": duration,
            "currentTime": position,
            "playbackSpeed": 1.0,
            "playerState": state,
        }
    )


@pytest.fixture()
def fake(monkeypatch):
    server = FakeFpx()
    monkeypatch.setattr(m, "FPX_PORT", server.port)
    monkeypatch.setattr(m, "_resolve_host", lambda host: ["127.0.0.1"])
    monkeypatch.setattr(m, "FPX_CONNECT_WINDOW", 0.5)
    monkeypatch.setattr(m, "FPX_CONNECT_RETRY_DELAY", 0.05)
    monkeypatch.setattr(m, "FPX_READ_POLL", 0.05)
    _set_host()
    yield server
    session = m._fpx_session
    if session is not None:
        session.stop("test teardown")
        session.thread.join(2)
    m._fpx_session = None
    server.close()


def _play(rel: str, origin: str = ORIGIN):
    return client.post("/api/fpx/play", json={"path": rel, "origin": origin})


def _session_ended():
    return m._fpx_session is not None and m._fpx_session.state == "ended"


# ── Open ──────────────────────────────────────────────────────────────────────


def test_play_sends_signed_url_and_resume_position(fake):
    rel = _video()
    _progress(rel, 125.0, 600.0)
    r = _play(rel)
    assert r.status_code == 200, r.text
    assert r.json()["state"] == "opening"
    msg = fake.wait_received()[0]
    assert msg["currentTime"] == 125.0
    assert msg["playerState"] == 0
    url = urlparse(msg["path"])
    assert f"{url.scheme}://{url.netloc}" == ORIGIN
    assert url.path == "/api/file"
    q = parse_qs(url.query)
    assert q["path"] == [rel]
    assert int(q["exp"][0]) > time.time() + 11 * 3600
    assert q["sig"][0]


def test_play_from_start_when_watched(fake):
    rel = _video()
    _progress(rel, 590.0, 600.0)  # 98% ≥ 90% threshold: watched, start over
    _play(rel)
    assert fake.wait_received()[0]["currentTime"] == 0.0


def test_play_refuses_a_non_video(fake):
    (MEDIA_DIR / "notes.txt").write_text("x")
    assert _play("notes.txt").status_code == 404


def test_play_refuses_a_bad_origin(fake):
    rel = _video()
    for origin in ("javascript:alert(1)", "http://u:p@hoard.lan", "http://hoard.lan/x?y"):
        assert _play(rel, origin).status_code == 422, origin


def test_play_without_host_is_refused(fake):
    _set_host("")
    rel = _video()
    r = _play(rel)
    assert r.status_code == 409
    assert fake.received == []


# ── Follow-up ─────────────────────────────────────────────────────────────────


def test_progress_saved_every_interval_and_on_pause(fake, monkeypatch):
    monkeypatch.setattr(m, "FPX_SAVE_INTERVAL", 0.3)
    rel = _video()
    _play(rel)
    url = fake.wait_received()[0]["path"]
    _status(fake, url, 0.0)
    _until(lambda: m._fpx_session.opened, "status never read")
    _status(fake, url, 42.0)
    _until(lambda: _row(rel) is not None and _row(rel)["position"] == 42.0, "no periodic save")
    snap = client.get("/api/fpx/status").json()
    assert snap["state"] == "playing"
    assert snap["position"] == 42.0
    assert snap["duration"] == 600.0

    monkeypatch.setattr(m, "FPX_SAVE_INTERVAL", 3600)
    _status(fake, url, 50.0, state=1)  # pause → immediate save
    _until(lambda: _row(rel)["position"] == 50.0, "no save on pause")
    assert client.get("/api/fpx/status").json()["state"] == "paused"


def test_empty_status_ends_the_session_and_saves(fake):
    rel = _video()
    _play(rel)
    url = fake.wait_received()[0]["path"]
    _status(fake, url, 300.0)
    _until(lambda: m._fpx_session.opened, "status never read")
    fake.send({})
    _until(_session_ended, "{} did not end the session")
    snap = client.get("/api/fpx/status").json()
    assert snap["active"] is False
    assert snap["reason"] == "closed"
    assert snap["path"] == rel
    row = _row(rel)
    assert row["position"] == 300.0
    assert row["duration"] == 600.0
    assert row["watched"] == 0


def test_close_past_threshold_marks_watched(fake):
    rel = _video()
    _play(rel)
    url = fake.wait_received()[0]["path"]
    _status(fake, url, 570.0)
    _until(lambda: m._fpx_session.opened, "status never read")
    fake.send({})
    _until(_session_ended, "{} did not end the session")
    assert _row(rel)["watched"] == 1


def test_empty_status_before_the_open_is_ignored(fake):
    rel = _video()
    _play(rel)
    fake.wait_received()
    fake.send({})  # FPX's state from before it processed the open
    fake.send({"path": "http://elsewhere/old.mp4", "duration": 10, "currentTime": 1})
    fake.send(None)
    time.sleep(0.3)
    assert m._fpx_session.state == "opening"
    assert _row(rel) is None


def test_another_path_after_the_open_ends_the_session(fake):
    rel = _video()
    _play(rel)
    url = fake.wait_received()[0]["path"]
    _status(fake, url, 12.0)
    _until(lambda: m._fpx_session.opened, "status never read")
    _status(fake, "http://elsewhere/other.mp4", 3.0)
    _until(_session_ended, "a new path did not end the session")
    assert m._fpx_session.reason == "replaced"
    assert _row(rel)["position"] == 12.0


def test_disconnect_ends_the_session_and_saves(fake):
    rel = _video()
    _play(rel)
    url = fake.wait_received()[0]["path"]
    _status(fake, url, 77.0)
    _until(lambda: m._fpx_session.opened, "status never read")
    fake.drop()
    _until(_session_ended, "disconnect did not end the session")
    assert m._fpx_session.reason == "disconnected"
    assert _row(rel)["position"] == 77.0


def test_silence_ends_the_session(fake, monkeypatch):
    monkeypatch.setattr(m, "FPX_SILENCE_TIMEOUT", 0.3)
    rel = _video()
    _play(rel)
    fake.wait_received()
    _until(_session_ended, "silence did not end the session")
    assert m._fpx_session.reason == "disconnected"


def test_seek_resent_when_the_open_lost_it(fake):
    rel = _video()
    _progress(rel, 200.0, 600.0)
    _play(rel)
    url = fake.wait_received()[0]["path"]
    _status(fake, url, 0.0)  # FPX loaded the file but dropped the seek
    msgs = fake.wait_received(2)
    assert msgs[1] == {"currentTime": 200.0}


def test_seek_not_resent_once_playback_moved_past_it(fake):
    rel = _video()
    _progress(rel, 200.0, 600.0)
    _play(rel)
    url = fake.wait_received()[0]["path"]
    _status(fake, url, 212.0)  # the seek held; FPX has been playing for a while
    _status(fake, url, 213.0)
    _until(lambda: m._fpx_session.position == 213.0, "status never read")
    time.sleep(0.2)
    assert len(fake.received) == 1


def test_stop_abandons_the_follow_up(fake):
    rel = _video()
    _play(rel)
    url = fake.wait_received()[0]["path"]
    _status(fake, url, 33.0)
    _until(lambda: m._fpx_session.opened, "status never read")
    r = client.post("/api/fpx/stop")
    assert r.json()["active"] is False
    assert r.json()["reason"] == "stopped"
    assert _row(rel)["position"] == 33.0


def test_new_play_replaces_the_previous_session(fake, monkeypatch):
    rel = _video()
    _play(rel)
    fake.wait_received()
    first = m._fpx_session
    second_fake = FakeFpx()
    try:
        monkeypatch.setattr(m, "FPX_PORT", second_fake.port)
        assert _play(_video("films/two.mp4")).status_code == 200
        assert first.state == "ended"
        assert first.reason == "replaced"
        assert m._fpx_session is not first
    finally:
        m._fpx_session.stop("test teardown")
        second_fake.close()


def test_status_without_session():
    m._fpx_session = None
    assert client.get("/api/fpx/status").json()["active"] is False


# ── Unreachable / refused hosts ───────────────────────────────────────────────


def test_unreachable_host_gives_a_clear_error_and_writes_nothing(fake, monkeypatch):
    closed = socket.socket()
    closed.bind(("127.0.0.1", 0))
    port = closed.getsockname()[1]
    closed.close()  # nothing listens there any more
    monkeypatch.setattr(m, "FPX_PORT", port)
    rel = _video()
    r = _play(rel)
    assert r.status_code == 502
    assert "injoignable" in r.json()["detail"]
    assert "frame.lan" in r.json()["detail"]
    assert _row(rel) is None
    assert m._fpx_session is None


def test_public_host_is_refused(fake, monkeypatch):
    monkeypatch.setattr(m, "_resolve_host", lambda host: ["1.1.1.1"])
    rel = _video()
    r = _play(rel)
    assert r.status_code == 400
    assert fake.received == []


def test_host_resolving_partly_public_is_refused(fake, monkeypatch):
    monkeypatch.setattr(m, "_resolve_host", lambda host: ["192.168.1.20", "8.8.8.8"])
    assert _play(_video()).status_code == 400


def test_unresolvable_host_is_refused(fake, monkeypatch):
    def fail(host):
        raise OSError("no such host")

    monkeypatch.setattr(m, "_resolve_host", fail)
    r = _play(_video())
    assert r.status_code == 502
    assert "ne se résout pas" in r.json()["detail"]


# ── Settings ──────────────────────────────────────────────────────────────────


def test_settings_defaults_are_empty():
    s = client.get("/api/settings").json()
    assert s["fpx_host"] == ""
    assert s["fpx_steam_gameid"] == ""


def test_settings_round_trip():
    r = client.post(
        "/api/settings",
        json={"fpx_host": " steam-frame.lan ", "fpx_steam_gameid": "5302428712275279872"},
    )
    assert r.status_code == 200
    s = client.get("/api/settings").json()
    assert s["fpx_host"] == "steam-frame.lan"
    assert s["fpx_steam_gameid"] == "5302428712275279872"


@pytest.mark.parametrize(
    "host", ["http://frame.lan", "frame.lan:23554", "frame.lan/x", "8.8.8.8", "a b"]
)
def test_settings_reject_bad_hosts(host):
    assert client.post("/api/settings", json={"fpx_host": host}).status_code == 422


@pytest.mark.parametrize("host", ["", "steam-frame.lan", "192.168.1.30", "fe80::1", "10.0.0.5"])
def test_settings_accept_lan_hosts(host):
    assert client.post("/api/settings", json={"fpx_host": host}).status_code == 200


def test_settings_reject_non_numeric_gameid():
    r = client.post("/api/settings", json={"fpx_steam_gameid": "steam://rungameid/1"})
    assert r.status_code == 422


# ── Signed URL ────────────────────────────────────────────────────────────────


@pytest.fixture()
def auth_on(monkeypatch):
    monkeypatch.setattr(m, "HOARD_AUTH_USER", "alice")
    monkeypatch.setattr(m, "HOARD_AUTH_PASS", "secret")
    monkeypatch.setattr(m, "_AUTH_ENABLED", True)


def _signed(rel: str) -> str:
    url, _ = m._fpx_signed_url("http://testserver", rel)
    return url[len("http://testserver") :]


def test_signed_url_opens_api_file_without_credentials(auth_on):
    rel = _video()
    r = client.get(_signed(rel))
    assert r.status_code == 200
    assert r.content == (MEDIA_DIR / rel).read_bytes()
    r = client.get(_signed(rel), headers={"Range": "bytes=10-19"})
    assert r.status_code == 206


def test_without_signature_api_file_still_needs_credentials(auth_on):
    rel = _video()
    assert client.get("/api/file", params={"path": rel}).status_code == 401


def test_signed_url_rejected_on_path_mismatch(auth_on):
    rel = _video()
    other = _video("films/other.mp4")
    q = parse_qs(urlparse(_signed(rel)).query)
    r = client.get("/api/file", params={"path": other, "exp": q["exp"][0], "sig": q["sig"][0]})
    assert r.status_code == 401


def test_signed_url_rejected_with_a_second_path(auth_on):
    rel = _video()
    other = _video("films/other.mp4")
    url = _signed(rel) + "&path=" + other
    assert client.get(url).status_code == 401


def test_signed_url_rejected_when_expired(auth_on, monkeypatch):
    rel = _video()
    url = _signed(rel)
    real_time = time.time
    monkeypatch.setattr(m.time, "time", lambda: real_time() + m.FPX_URL_TTL + 1)
    assert client.get(url).status_code == 401


def test_signed_url_rejected_with_a_bad_signature(auth_on):
    rel = _video()
    q = parse_qs(urlparse(_signed(rel)).query)
    bad = q["sig"][0][:-2] + ("AA" if not q["sig"][0].endswith("AA") else "BB")
    r = client.get("/api/file", params={"path": rel, "exp": q["exp"][0], "sig": bad})
    assert r.status_code == 401
    r = client.get("/api/file", params={"path": rel, "exp": "soon", "sig": q["sig"][0]})
    assert r.status_code == 401


def test_signed_url_rejected_by_every_other_route(auth_on):
    rel = _video()
    query = urlparse(_signed(rel)).query
    for route in ("/api/files", "/api/progress", "/api/transcode", "/api/thumbnail"):
        assert client.get(f"{route}?{query}").status_code == 401, route
    assert client.delete(f"/api/files?{query}").status_code == 401


def test_signed_url_dies_with_a_password_change(auth_on, monkeypatch):
    rel = _video()
    url = _signed(rel)
    monkeypatch.setattr(m, "HOARD_AUTH_PASS", "changed")
    assert client.get(url).status_code == 401


def test_fpx_routes_need_auth(auth_on):
    assert client.get("/api/fpx/status").status_code == 401
    assert client.post("/api/fpx/stop").status_code == 401
    r = client.post("/api/fpx/play", json={"path": "x.mp4", "origin": ORIGIN})
    assert r.status_code == 401
