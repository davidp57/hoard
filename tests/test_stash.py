"""Stash integration (FEAT-STASH, BL-147 to BL-150), against a fake Stash.

The fake is a real HTTP server on 127.0.0.1: the client's headers, timeouts and
redirect refusal are exercised as they run in production. It answers the GraphQL
operations Hoard sends, evaluates path regexes with Python's `re` (so a `[` left
unescaped fails here as it would in Stash), and touches the test media folder
the way Stash touches the NAS: it moves and deletes the files it is asked to.
"""

import json
import re
import sqlite3
import threading
import time
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
from starlette.testclient import TestClient

import backend.main as m
from backend.main import app

from .conftest import DATA_DIR, MEDIA_DIR

client = TestClient(app)

KEY = "stash-secret-key"
FOLDER = "[[_keep"
PREFIX = "/data/[[_keep"


class FakeStash:
    def __init__(self):
        self.scenes: dict[str, dict] = {}
        self.contents: dict[str, bytes] = {}  # file id -> bytes: the fingerprint
        self.calls: list[tuple[str, dict]] = []
        self.keys_seen: list[str | None] = []
        self.next_id = 1
        self.job_status = "FINISHED"
        self.create_on_scan = True
        self.mode = "ok"  # ok | html | redirect | error500
        self.stash_boxes: list[str] = []
        self.fragment_scrapers: list[str] = []
        self.refuse: set[str] = set()  # operations answered with a GraphQL error
        self.tags: dict[str, dict] = {}  # tag id -> {id, name}
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), self._handler())
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()

    # ── paths ──
    @staticmethod
    def disk(spath: str) -> Path:
        assert spath == PREFIX or spath.startswith(PREFIX + "/"), spath
        return MEDIA_DIR / (FOLDER + spath[len(PREFIX) :])

    @staticmethod
    def spath(rel: str) -> str:
        return PREFIX + rel[len(FOLDER) :]

    def add_scene(self, rel: str, **fields) -> str:
        sid = str(self.next_id)
        self.next_id += 1
        self.scenes[sid] = {
            "id": sid,
            "title": "",
            "rating100": None,
            "interactive": False,
            "play_count": 0,
            "o_counter": 0,
            "resume_time": 0,
            "files": [{"id": f"f{sid}", "path": self.spath(rel), "duration": 60.0}],
            "studio": None,
            "performers": [],
            "tags": [],
            "scene_markers": [],
            "date": None,
            "details": None,
            "urls": [],
            **fields,
        }
        return sid

    def ops(self, name: str) -> list[dict]:
        return [v for op, v in self.calls if op == name]

    def scene_of(self, rel: str) -> dict | None:
        for scene in self.scenes.values():
            if any(f["path"] == self.spath(rel) for f in scene["files"]):
                return scene
        return None

    # ── GraphQL ──
    def graphql(self, query: str, variables: dict):
        ops = [
            "version",
            "findScenes",
            "metadataScan",
            "findJob",
            "sceneSaveActivity",
            "sceneAddPlay",
            "metadataIdentify",
            "moveFiles",
            "sceneDestroy",
            "deleteFiles",
            "configuration",
            "findTags",
            "tagCreate",
            "sceneUpdate",
        ]
        op = next(o for o in ops if o in query)
        self.calls.append((op, variables))
        if op in self.refuse:
            return {"errors": [{"message": f"{op} refused"}]}
        handler = getattr(self, "op_" + op)
        return {"data": handler(variables)}

    def op_version(self, v):
        return {"version": {"version": "v0.32.0"}}

    def op_findScenes(self, v):
        pattern = re.compile(v["f"]["path"]["value"])  # an unescaped `[[` raises here
        found = [
            s for s in self.scenes.values() if any(pattern.search(f["path"]) for f in s["files"])
        ]
        return {"findScenes": {"count": len(found), "scenes": found}}

    def op_metadataScan(self, v):
        for spath in v["in"]["paths"]:
            target = self.disk(spath)
            files = [target] if target.is_file() else sorted(target.rglob("*.mp4"))
            for f in files:
                rel = str(f.relative_to(MEDIA_DIR)).replace("\\", "/")
                if self.scene_of(rel) or not self.create_on_scan:
                    continue
                # Stash's rename detection: a known file gone from its path, with the
                # same content, is the same file moved.
                moved = False
                for scene in self.scenes.values():
                    for sf in scene["files"]:
                        old = self.disk(sf["path"])
                        if not old.exists() and self.contents.get(sf["id"]) == f.read_bytes():
                            sf["path"] = self.spath(rel)
                            moved = True
                if not moved:
                    sid = self.add_scene(rel)
                    self.contents[f"f{sid}"] = f.read_bytes()
        return {"metadataScan": "42"}

    def op_findJob(self, v):
        return {"findJob": {"status": self.job_status, "error": "boom"}}

    def op_sceneSaveActivity(self, v):
        return {"sceneSaveActivity": True}

    def op_sceneAddPlay(self, v):
        return {"sceneAddPlay": {"count": 1}}

    def op_metadataIdentify(self, v):
        for sid in v["in"]["sceneIDs"]:
            self.on_identify(self.scenes[sid])
        return {"metadataIdentify": "43"}

    def on_identify(self, scene):
        pass

    def op_configuration(self, v):
        return {
            "configuration": {
                "general": {"stashBoxes": [{"endpoint": e} for e in self.stash_boxes]}
            },
            "listScrapers": [
                {"id": s, "scene": {"supported_scrapes": ["FRAGMENT"]}}
                for s in self.fragment_scrapers
            ]
            + [{"id": "url-only", "scene": {"supported_scrapes": ["URL"]}}],
        }

    def add_tag(self, name: str) -> dict:
        tag = {"id": f"t{len(self.tags) + 1}", "name": name}
        self.tags[tag["id"]] = tag
        return tag

    def op_findTags(self, v):
        tags = [
            {
                **t,
                "scene_count": sum(
                    any(st["id"] == t["id"] for st in s["tags"]) for s in self.scenes.values()
                ),
            }
            for t in self.tags.values()
        ]
        return {"findTags": {"tags": tags}}

    def op_tagCreate(self, v):
        name = v["in"]["name"]
        # Stash refuses a second tag of the same name, whatever its case.
        if any(t["name"].lower() == name.lower() for t in self.tags.values()):
            raise AssertionError(f"duplicate tag {name}")
        return {"tagCreate": self.add_tag(name)}

    def op_sceneUpdate(self, v):
        scene = self.scenes[v["in"]["id"]]
        if "tag_ids" in v["in"]:
            scene["tags"] = [dict(self.tags[i]) for i in v["in"]["tag_ids"]]
        if "rating100" in v["in"]:
            scene["rating100"] = v["in"]["rating100"]
        for key in ("title", "date", "details", "urls"):
            if key in v["in"]:
                scene[key] = v["in"][key]
        if "studio_id" in v["in"]:
            sid = v["in"]["studio_id"]
            scene["studio"] = {"id": sid, "name": f"studio {sid}"} if sid else None
        if "performer_ids" in v["in"]:
            scene["performers"] = [{"id": i, "name": f"perf {i}"} for i in v["in"]["performer_ids"]]
        return {"sceneUpdate": {"id": scene["id"]}}

    def op_moveFiles(self, v):
        inp = v["in"]
        for scene in self.scenes.values():
            for f in scene["files"]:
                if f["id"] in inp["ids"]:
                    dest = inp["destination_folder"] + "/" + inp["destination_basename"]
                    self.disk(dest).parent.mkdir(parents=True, exist_ok=True)
                    self.disk(f["path"]).rename(self.disk(dest))
                    f["path"] = dest
        return {"moveFiles": True}

    def op_sceneDestroy(self, v):
        scene = self.scenes.pop(v["in"]["id"])
        if v["in"]["delete_file"]:
            for f in scene["files"]:
                self.disk(f["path"]).unlink()
        return {"sceneDestroy": True}

    def op_deleteFiles(self, v):
        for scene in self.scenes.values():
            for f in list(scene["files"]):
                if f["id"] in v["ids"]:
                    self.disk(f["path"]).unlink()
                    scene["files"].remove(f)
        return {"deleteFiles": True}

    # ── HTTP ──
    def _handler(self):
        fake = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def _send(self, code, body: bytes, ctype="application/json", headers=None):
                self.send_response(code)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(body)))
                for k, val in (headers or {}).items():
                    self.send_header(k, val)
                self.end_headers()
                self.wfile.write(body)

            def _auth(self) -> bool:
                fake.keys_seen.append(self.headers.get("ApiKey"))
                if fake.mode == "redirect":
                    self._send(302, b"", headers={"Location": "http://127.0.0.1:9/elsewhere"})
                    return False
                if self.headers.get("ApiKey") != KEY:
                    self._send(401, b'{"message":"unauthorized"}')
                    return False
                return True

            def do_POST(self):
                body = self.rfile.read(int(self.headers.get("Content-Length") or 0))
                if not self._auth():
                    return
                if fake.mode == "html":
                    self._send(200, b"<html>login</html>", "text/html")
                    return
                if fake.mode == "error500":
                    self._send(500, b"oops", "text/plain")
                    return
                req = json.loads(body)
                out = fake.graphql(req["query"], req.get("variables") or {})
                self._send(200, json.dumps(out).encode())

            def do_GET(self):
                if not self._auth():
                    return
                match = re.match(r"^/scene/(\d+)/(.+)$", self.path)
                if not match or match.group(1) not in fake.scenes:
                    self._send(404, b"not found", "text/plain")
                    return
                sid, kind = match.groups()
                if kind == "preview" and self.headers.get("Range"):
                    self._send(
                        206, b"PREV", "video/mp4", headers={"Content-Range": "bytes 0-3/100"}
                    )
                    return
                ctype = "image/jpeg" if kind == "screenshot" else "text/plain"
                self._send(200, f"{kind}-{sid}".encode(), ctype)

        return Handler


@pytest.fixture()
def stash():
    fake = FakeStash()
    (MEDIA_DIR / FOLDER).mkdir(exist_ok=True)
    (MEDIA_DIR / "[[_edit").mkdir(exist_ok=True)
    m._stash_invalidate()
    m._stash_last_sync.clear()
    resp = client.post(
        "/api/settings",
        json={"stash_url": fake.url, "stash_api_key": KEY, "stash_path_prefix": PREFIX},
    )
    assert resp.status_code == 200
    yield fake
    m._stash_wait_idle()
    m._stash_invalidate()
    m._stash_last_sync.clear()
    fake.close()


@contextmanager
def _db():
    conn = sqlite3.connect(str(DATA_DIR / "test.db"))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _video(rel: str, content: bytes | None = None) -> str:
    p = MEDIA_DIR / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(content if content is not None else rel.encode())
    return rel


def _progress(rel: str, position: float, duration: float, watched: int = 0):
    with _db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO progress (path, position, duration, watched) VALUES (?,?,?,?)",
            (rel, position, duration, watched),
        )


def _row(rel: str):
    with _db() as conn:
        return conn.execute("SELECT * FROM progress WHERE path = ?", (rel,)).fetchone()


def _wait_job(job_id: str, timeout: float = 10.0) -> dict:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        job = m._jobs[job_id]
        if job["status"] in ("done", "error"):
            return job
        time.sleep(0.02)
    raise AssertionError(f"job {job_id} still {m._jobs[job_id]['status']}")


def _move(rel: str, destination: str) -> dict:
    resp = client.post(f"/api/files/move?path={rel}", json={"destination": destination})
    assert resp.status_code == 200, resp.text
    job = _wait_job(resp.json()["job_id"])
    m._stash_wait_idle()
    return job


# ── BL-147: settings, connection, paths, proxy ───────────────────────────────
class TestSettings:
    def test_key_is_write_only(self, stash):
        s = client.get("/api/settings").json()
        assert "stash_api_key" not in s
        assert KEY not in json.dumps(s)
        assert s["stash_api_key_set"] is True
        assert s["stash_url"] == stash.url
        assert s["stash_folder"] == FOLDER

    def test_omitting_the_key_keeps_it_and_empty_clears_it(self, stash):
        client.post("/api/settings", json={"stash_url": stash.url})
        assert client.get("/api/settings").json()["stash_api_key_set"] is True
        client.post("/api/settings", json={"stash_api_key": ""})
        assert client.get("/api/settings").json()["stash_api_key_set"] is False

    def test_a_new_url_without_a_key_clears_the_stored_key(self, stash):
        client.post("/api/settings", json={"stash_url": "http://elsewhere.example:9999"})
        assert client.get("/api/settings").json()["stash_api_key_set"] is False

    def test_a_new_url_with_its_key_keeps_it(self, stash):
        client.post(
            "/api/settings",
            json={"stash_url": "http://elsewhere.example:9999", "stash_api_key": "k2"},
        )
        assert client.get("/api/settings").json()["stash_api_key_set"] is True

    def test_url_must_be_http(self):
        resp = client.post("/api/settings", json={"stash_url": "file:///etc/passwd"})
        assert resp.status_code == 422

    def test_folder_must_be_relative(self):
        resp = client.post("/api/settings", json={"stash_folder": "../escape"})
        assert resp.status_code == 422

    def test_off_by_default(self):
        assert client.get("/api/settings").json()["stash_url"] == ""
        assert m._stash_config() is None
        assert client.get("/api/stash/status").json() == {"enabled": False}


class TestConnection:
    def test_ok_gives_the_version(self, stash):
        resp = client.post("/api/stash/test", json={})
        assert resp.json() == {"ok": True, "version": "v0.32.0", "identify_sources": 0}

    def test_wrong_key_says_401(self, stash):
        resp = client.post("/api/stash/test", json={"url": stash.url, "api_key": "nope"})
        body = resp.json()
        assert body["ok"] is False and "401" in body["error"]

    def test_unreachable(self):
        resp = client.post("/api/stash/test", json={"url": "http://127.0.0.1:1", "api_key": "k"})
        body = resp.json()
        assert body["ok"] is False and "unreachable" in body["error"]

    def test_not_graphql(self, stash):
        stash.mode = "html"
        body = client.post("/api/stash/test", json={}).json()
        assert body["ok"] is False and "not GraphQL" in body["error"]

    def test_stored_key_never_goes_to_another_url(self, stash):
        other = FakeStash()
        try:
            client.post("/api/stash/test", json={"url": other.url})
            assert other.keys_seen == [None]
        finally:
            other.close()

    def test_redirect_is_refused_and_the_key_does_not_follow(self, stash):
        stash.mode = "redirect"
        body = client.post("/api/stash/test", json={}).json()
        assert body["ok"] is False and "redirect" in body["error"]

    def test_failure_is_logged_with_url_and_cause(self, stash, caplog):
        stash.mode = "error500"
        with caplog.at_level("WARNING", logger="hoard"):
            client.post("/api/stash/test", json={})
        assert any(
            r.getMessage().startswith("stash: ") and stash.url in r.getMessage()
            for r in caplog.records
        )

    def test_status_reports_identify_sources(self, stash):
        stash.stash_boxes = ["https://stashdb.org/graphql"]
        stash.fragment_scrapers = ["scraper-a"]
        body = client.get("/api/stash/status").json()
        assert body["ok"] is True and body["identify_sources"] == 2


class TestPaths:
    cfg = {"url": "x", "key": "", "folder": FOLDER, "prefix": PREFIX, "identify": False}

    def test_both_ways(self):
        rel = "[[_keep/sub dir/a [1].mp4"
        spath = m._stash_path_for(rel, self.cfg)
        assert spath == "/data/[[_keep/sub dir/a [1].mp4"
        assert m._hoard_rel_for(spath, self.cfg) == rel

    def test_outside_the_folder_maps_to_nothing(self):
        assert m._stash_path_for("[[_edit/a.mp4", self.cfg) is None
        assert m._stash_path_for("[[_keepsake/a.mp4", self.cfg) is None
        assert m._hoard_rel_for("/data/[[_keepsake/a.mp4", self.cfg) is None

    def test_windows_stash(self):
        cfg = {**self.cfg, "prefix": r"D:\stash\[[_keep"}
        spath = m._stash_path_for("[[_keep/a/b.mp4", cfg)
        assert spath == r"D:\stash\[[_keep\a\b.mp4"
        assert m._hoard_rel_for(spath, cfg) == "[[_keep/a/b.mp4"

    def test_regex_escape_takes_brackets_literally(self):
        text = "/data/[[_keep/a (1) [x].mp4"
        pattern = re.compile("^" + m._stash_regex_escape(text) + "$")
        assert pattern.match(text)
        assert not pattern.match("/data/k_keep/a (1) x.mp4")

    @pytest.mark.filterwarnings("ignore::FutureWarning")
    def test_unescaped_bracket_would_break(self):
        with pytest.raises(re.error):
            re.compile("^/data/[[_keep/a.mp4$")


class TestProxy:
    def test_serves_screenshot_with_the_key(self, stash):
        sid = stash.add_scene(_video("[[_keep/a.mp4"))
        resp = client.get(f"/api/stash/scene/{sid}/screenshot")
        assert resp.status_code == 200
        assert resp.content == f"screenshot-{sid}".encode()
        assert resp.headers["content-type"] == "image/jpeg"
        assert stash.keys_seen[-1] == KEY

    def test_passes_range(self, stash):
        sid = stash.add_scene(_video("[[_keep/a.mp4"))
        resp = client.get(f"/api/stash/scene/{sid}/preview", headers={"Range": "bytes=0-3"})
        assert resp.status_code == 206 and resp.content == b"PREV"
        assert resp.headers["content-range"] == "bytes 0-3/100"

    @pytest.mark.parametrize(
        "path",
        [
            "/api/stash/scene/1/stream",
            "/api/stash/scene/1/../../graphql",
            "/api/stash/scene/abc/screenshot",
            "/api/stash/scene/%C2%B2/screenshot",
        ],
    )
    def test_refuses_the_rest(self, stash, path):
        assert client.get(path).status_code == 404
        assert stash.keys_seen == []

    def test_unknown_scene_is_404(self, stash):
        assert client.get("/api/stash/scene/999/screenshot").status_code == 404

    def test_off_is_404(self):
        assert client.get("/api/stash/scene/1/screenshot").status_code == 404

    def test_signed_url_opens_without_credentials(self, stash, monkeypatch):
        sid = stash.add_scene(_video("[[_keep/a.mp4"))
        monkeypatch.setattr(m, "HOARD_AUTH_USER", "alice")
        monkeypatch.setattr(m, "HOARD_AUTH_PASS", "secret")
        monkeypatch.setattr(m, "_AUTH_ENABLED", True)
        anon = TestClient(app)
        assert anon.get(f"/api/stash/scene/{sid}/screenshot").status_code == 401
        signed = m._stash_media_url(sid, "screenshot")
        assert anon.get(signed).status_code == 200
        # The signature names one medium of one scene.
        other = signed.replace("/screenshot?", "/preview?")
        assert anon.get(other).status_code == 401


# ── BL-148: arrivals in the Stash folder ─────────────────────────────────────
class TestArrival:
    def test_by_quick_folder_move(self, stash):
        rel = _video("[[_review/movie.mp4")
        _progress(rel, 30.0, 100.0)
        job = _move(rel, FOLDER)
        assert job["status"] == "done"
        assert (MEDIA_DIR / FOLDER / "movie.mp4").exists()
        assert stash.ops("metadataScan")[0]["in"]["paths"] == [PREFIX + "/movie.mp4"]
        scene = stash.scene_of("[[_keep/movie.mp4")
        assert scene is not None
        assert stash.ops("sceneSaveActivity") == [{"id": scene["id"], "t": 30.0}]
        assert stash.ops("sceneAddPlay") == []

    def test_watched_video_adds_a_play(self, stash):
        rel = _video("[[_review/seen.mp4")
        _progress(rel, 0.0, 0.0, watched=1)
        _move(rel, FOLDER)
        assert len(stash.ops("sceneAddPlay")) == 1

    def test_whole_folder(self, stash):
        _video("dl/pack/a.mp4")
        _video("dl/pack/sub/b.mp4")
        _move("dl/pack", FOLDER)
        assert stash.ops("metadataScan")[0]["in"]["paths"] == [PREFIX + "/pack"]
        assert stash.scene_of("[[_keep/pack/a.mp4")
        assert stash.scene_of("[[_keep/pack/sub/b.mp4")

    def test_by_rename_of_a_file_stash_does_not_know(self, stash):
        _video("[[_keep/raw.mp4")
        resp = client.post("/api/files/rename?path=[[_keep/raw.mp4", json={"new_name": "nice.mp4"})
        assert resp.status_code == 200
        m._stash_wait_idle()
        assert stash.ops("moveFiles") == []
        assert stash.scene_of("[[_keep/nice.mp4")

    def test_by_segment_export(self, stash, monkeypatch):
        class _Proc:
            returncode = 0

            def __init__(self, cmd, **kwargs):
                Path(cmd[-1]).write_bytes(b"exported")
                self.stderr = iter(())

            def wait(self):
                return 0

        monkeypatch.setattr(m.subprocess, "Popen", _Proc)
        src = MEDIA_DIR / _video("[[_edit/long.mp4")
        m._jobs["j"] = {"id": "j", "status": "pending"}
        m._run_export_segments(
            "j", src, [{"seg_in": 0, "seg_out": 5}], "merged", MEDIA_DIR / FOLDER, False
        )
        m._stash_wait_idle()
        assert m._jobs["j"]["status"] == "done"
        paths = [p for op in stash.ops("metadataScan") for p in op["in"]["paths"]]
        assert PREFIX + "/long [1 segment].mp4" in paths
        assert PREFIX + "/long.mp4" in paths  # the original followed it

    def test_scan_failure_leaves_the_file(self, stash, caplog):
        stash.job_status = "FAILED"
        rel = _video("dl/x.mp4")
        with caplog.at_level("WARNING", logger="hoard"):
            job = _move(rel, FOLDER)
        assert job["status"] == "done"
        assert (MEDIA_DIR / FOLDER / "x.mp4").exists()
        assert any("stash: declaring [[_keep/x.mp4" in r.getMessage() for r in caplog.records)

    def test_scene_not_found_is_logged(self, stash, caplog):
        stash.create_on_scan = False
        with caplog.at_level("WARNING", logger="hoard"):
            _move(_video("dl/y.mp4"), FOLDER)
        assert any("not found in Stash" in r.getMessage() for r in caplog.records)

    def test_unreachable_stash_does_not_block_the_move(self, stash, caplog):
        client.post("/api/settings", json={"stash_url": "http://127.0.0.1:1"})
        with caplog.at_level("WARNING", logger="hoard"):
            job = _move(_video("dl/z.mp4"), FOLDER)
        assert job["status"] == "done"
        assert (MEDIA_DIR / FOLDER / "z.mp4").exists()
        assert any("unreachable" in r.getMessage() for r in caplog.records)

    def test_identify_with_a_source(self, stash):
        stash.stash_boxes = ["https://stashdb.org/graphql"]
        client.post("/api/settings", json={"stash_identify": True})
        _move(_video("dl/i.mp4"), FOLDER)
        (call,) = stash.ops("metadataIdentify")
        assert call["in"]["sources"] == [
            {"source": {"stash_box_endpoint": "https://stashdb.org/graphql"}}
        ]
        assert call["in"]["sceneIDs"] == [stash.scene_of("[[_keep/i.mp4")["id"]]

    def test_identified_details_reach_the_list(self, stash, monkeypatch):
        # BL-152: the list read the scene between the scan and the end of the
        # identification; what the identification found must still reach it.
        stash.stash_boxes = ["https://stashdb.org/graphql"]
        client.post("/api/settings", json={"stash_identify": True})
        rel = "[[_keep/id.mp4"
        real_wait = m._stash_wait_job

        def wait(cfg, job_id):
            if job_id == "43":  # the identify job of the fake
                assert client.get("/api/stash/folder?path=[[_keep").json()["scenes"][rel]
                scene = stash.scene_of(rel)
                scene.update(title="Found", studio={"name": "S"}, performers=[{"name": "P"}])
            return real_wait(cfg, job_id)

        monkeypatch.setattr(m, "_stash_wait_job", wait)
        _move(_video("dl/id.mp4"), FOLDER)
        scene = client.get("/api/stash/folder?path=[[_keep").json()["scenes"][rel]
        assert scene["title"] == "Found"
        assert scene["studio"] == "S" and scene["performers"] == ["P"]

    def test_identify_without_a_source(self, stash):
        client.post("/api/settings", json={"stash_identify": True})
        _move(_video("dl/j.mp4"), FOLDER)
        assert stash.ops("metadataIdentify") == []

    def test_no_identify_when_off(self, stash):
        stash.stash_boxes = ["https://stashdb.org/graphql"]
        _move(_video("dl/k.mp4"), FOLDER)
        assert stash.ops("metadataIdentify") == []

    def test_moves_elsewhere_say_nothing_to_stash(self, stash):
        _move(_video("dl/n.mp4"), "[[_edit")
        assert stash.calls == []


# ── BL-149: Stash's information in Hoard, progress in Stash ──────────────────
class TestDisplay:
    def _rich(self, stash, rel="[[_keep/rich.mp4"):
        _video(rel)
        return stash.add_scene(
            rel,
            title="Rich",
            rating100=80,
            interactive=True,
            studio={"name": "Studio A"},
            performers=[{"name": "Jane"}],
            tags=[{"name": "Outdoor"}],
            scene_markers=[
                {"id": "2", "title": "", "seconds": 90.0, "primary_tag": {"name": "B"}},
                {"id": "1", "title": "Intro", "seconds": 10.0, "primary_tag": {"name": "A"}},
            ],
        )

    def test_folder(self, stash):
        sid = self._rich(stash)
        stash.add_scene(_video("[[_keep/deeper/other.mp4"))
        body = client.get("/api/stash/folder?path=[[_keep").json()
        assert list(body["scenes"]) == ["[[_keep/rich.mp4"]
        scene = body["scenes"]["[[_keep/rich.mp4"]
        assert scene["id"] == sid and scene["rating"] == 80
        assert scene["studio"] == "Studio A" and scene["performers"] == ["Jane"]
        assert [mk["title"] for mk in scene["markers"]] == ["Intro", "B"]
        assert stash.url not in json.dumps(body)

    def test_folder_is_cached(self, stash):
        self._rich(stash)
        client.get("/api/stash/folder?path=[[_keep")
        client.get("/api/stash/folder?path=[[_keep")
        assert len(stash.ops("findScenes")) == 1

    def test_outside_the_folder_asks_nothing(self, stash):
        _video("[[_edit/a.mp4")
        assert client.get("/api/stash/folder?path=[[_edit").json() == {"scenes": {}}
        assert client.get("/api/stash/scene?path=[[_edit/a.mp4").json() == {"scene": None}
        assert stash.calls == []

    def test_unreachable_gives_an_empty_answer(self, stash):
        client.post("/api/settings", json={"stash_url": "http://127.0.0.1:1"})
        body = client.get("/api/stash/folder?path=[[_keep").json()
        assert body["scenes"] == {} and body["error"]
        # And the plain list does not depend on Stash at all.
        assert client.get("/api/files?path=[[_keep").status_code == 200

    def test_player_scene(self, stash):
        sid = self._rich(stash)
        body = client.get("/api/stash/scene?path=[[_keep/rich.mp4").json()
        assert body["scene"]["id"] == sid

    def test_heresphere_scene(self, stash, monkeypatch):
        monkeypatch.setattr(m, "_read_media_info", lambda file: {})
        sid = self._rich(stash)
        scene = client.post("/heresphere/scene/" + m._heresphere_id("[[_keep/rich.mp4")).json()
        assert scene["thumbnailImage"].startswith(f"/api/stash/scene/{sid}/screenshot?exp=")
        assert scene["thumbnailVideo"].startswith(f"/api/stash/scene/{sid}/preview?exp=")
        assert scene["rating"] == 4.0
        assert scene["scripts"][0]["url"].startswith(f"/api/stash/scene/{sid}/funscript?")
        names = [t["name"] for t in scene["tags"]]
        assert names[:3] == ["Performer:Jane", "Studio:Studio A", "Tag:Outdoor"]
        intro = next(t for t in scene["tags"] if t["name"] == "Marker:Intro")
        assert intro["start"] == 10000.0 and intro["end"] == 90000.0
        last = next(t for t in scene["tags"] if t["name"] == "Marker:B")
        assert last["end"] == last["start"] + 20000.0
        assert KEY not in json.dumps(scene)

    def test_heresphere_scan_carries_tags(self, stash):
        self._rich(stash)
        client.post("/api/quick-folders", json={"path": FOLDER})
        scan = client.post("/heresphere/scan").json()["scanData"]
        entry = next(e for e in scan if e["title"] == "rich")
        assert {"name": "Performer:Jane"} in entry["tags"]
        assert entry["rating"] == 4.0

    def test_heresphere_outside_the_folder_unchanged(self, stash, monkeypatch):
        monkeypatch.setattr(m, "_read_media_info", lambda file: {})
        _video("[[_edit/plain.mp4")
        scene = client.post("/heresphere/scene/" + m._heresphere_id("[[_edit/plain.mp4")).json()
        assert scene["tags"] == [] and "thumbnailImage" not in scene
        assert stash.calls == []


class TestProgressCopy:
    def _save(self, rel, pos, dur=100.0, final=False):
        resp = client.post(
            f"/api/progress?path={rel}", json={"position": pos, "duration": dur, "final": final}
        )
        assert resp.status_code == 200
        m._stash_wait_idle()

    def test_throttled_to_one_every_30_s(self, stash):
        rel = _video("[[_keep/p.mp4")
        sid = stash.add_scene(rel)
        self._save(rel, 10)
        self._save(rel, 15)
        self._save(rel, 20)
        assert stash.ops("sceneSaveActivity") == [{"id": sid, "t": 10.0}]

    def test_pause_and_close_go_at_once(self, stash):
        rel = _video("[[_keep/p.mp4")
        sid = stash.add_scene(rel)
        self._save(rel, 10)
        self._save(rel, 15, final=True)
        assert stash.ops("sceneSaveActivity")[-1] == {"id": sid, "t": 15.0}

    def test_window_reopens_after_30_s(self, stash, monkeypatch):
        rel = _video("[[_keep/p.mp4")
        stash.add_scene(rel)
        self._save(rel, 10)
        m._stash_last_sync[rel] -= m.STASH_SYNC_INTERVAL + 1
        self._save(rel, 40)
        assert len(stash.ops("sceneSaveActivity")) == 2

    def test_becoming_watched_adds_a_play(self, stash):
        rel = _video("[[_keep/p.mp4")
        stash.add_scene(rel)
        self._save(rel, 10)
        self._save(rel, 95)  # past the 90 % threshold, inside the 30 s window
        assert len(stash.ops("sceneAddPlay")) == 1
        self._save(rel, 96, final=True)  # already watched: no second play
        assert len(stash.ops("sceneAddPlay")) == 1

    def test_mark_watched_from_the_list(self, stash):
        rel = _video("[[_keep/p.mp4")
        stash.add_scene(rel)
        client.post(f"/api/progress/watched?path={rel}", json={"watched": True})
        m._stash_wait_idle()
        assert len(stash.ops("sceneAddPlay")) == 1

    def test_heresphere_events_are_copied(self, stash, monkeypatch):
        monkeypatch.setattr(m, "_read_media_info", lambda file: {"duration": 100.0})
        rel = _video("[[_keep/h.mp4")
        sid = stash.add_scene(rel)
        url = "http://nas/heresphere/scene/" + m._heresphere_id(rel)
        client.post("/heresphere/events", json={"id": url, "event": 2, "time": 42000})
        m._stash_wait_idle()
        assert stash.ops("sceneSaveActivity") == [{"id": sid, "t": 42.0}]

    def test_outside_the_folder_nothing_is_sent(self, stash):
        rel = _video("[[_edit/q.mp4")
        self._save(rel, 10, final=True)
        assert stash.calls == []

    def test_stash_down_never_blocks_the_write(self, stash):
        client.post("/api/settings", json={"stash_url": "http://127.0.0.1:1"})
        rel = _video("[[_keep/p.mp4")
        self._save(rel, 12, final=True)
        assert _row(rel)["position"] == 12.0

    def test_a_crashing_hook_never_blocks_the_write(self, stash, monkeypatch):
        def boom(*a, **k):
            raise RuntimeError("boom")

        monkeypatch.setattr(m, "_stash_config", boom)
        rel = _video("[[_keep/p.mp4")
        self._save(rel, 7)
        assert _row(rel)["position"] == 7.0


# ── BL-150: moving and deleting in the Stash folder ──────────────────────────
class TestFileOps:
    def test_move_within_goes_through_stash(self, stash):
        rel = _video("[[_keep/a.mp4")
        sid = stash.add_scene(rel)
        (MEDIA_DIR / FOLDER / "sub").mkdir()
        _progress(rel, 50.0, 100.0)
        job = _move(rel, "[[_keep/sub")
        assert job["status"] == "done"
        (call,) = stash.ops("moveFiles")
        assert call["in"] == {
            "ids": [f"f{sid}"],
            "destination_folder": PREFIX + "/sub",
            "destination_basename": "a.mp4",
        }
        assert (MEDIA_DIR / FOLDER / "sub" / "a.mp4").exists()
        assert _row("[[_keep/sub/a.mp4")["position"] == 50.0
        assert _row(rel) is None
        assert stash.ops("metadataScan") == []

    def test_rename_within_goes_through_stash(self, stash):
        rel = _video("[[_keep/a.mp4")
        stash.add_scene(rel)
        resp = client.post(f"/api/files/rename?path={rel}", json={"new_name": "b [x].mp4"})
        assert resp.status_code == 200
        (call,) = stash.ops("moveFiles")
        assert call["in"]["destination_basename"] == "b [x].mp4"
        assert call["in"]["destination_folder"] == PREFIX
        assert (MEDIA_DIR / FOLDER / "b [x].mp4").exists()

    def test_folder_moved_within_is_rescanned_and_keeps_its_scene(self, stash):
        rel = _video("[[_keep/pack/a.mp4", b"same-bytes")
        sid = stash.add_scene(rel)
        stash.contents[f"f{sid}"] = b"same-bytes"
        (MEDIA_DIR / FOLDER / "dest").mkdir()
        _move("[[_keep/pack", "[[_keep/dest")
        assert stash.ops("metadataScan")[0]["in"]["paths"] == [PREFIX + "/dest/pack"]
        assert stash.scene_of("[[_keep/dest/pack/a.mp4")["id"] == sid

    def test_delete_within_goes_through_stash(self, stash):
        rel = _video("[[_keep/a.mp4")
        sid = stash.add_scene(rel)
        _progress(rel, 5.0, 100.0)
        assert client.delete(f"/api/files?path={rel}").status_code == 200
        assert stash.ops("sceneDestroy") == [
            {"in": {"id": sid, "delete_file": True, "delete_generated": True}}
        ]
        assert not (MEDIA_DIR / rel).exists()
        assert _row(rel) is None

    def test_delete_of_a_multi_file_scene_deletes_this_file_only(self, stash):
        rel = _video("[[_keep/a.mp4")
        other = _video("[[_keep/a-copy.mp4")
        sid = stash.add_scene(rel)
        stash.scenes[sid]["files"].append({"id": "fx", "path": stash.spath(other)})
        assert client.delete(f"/api/files?path={rel}").status_code == 200
        assert stash.ops("sceneDestroy") == []
        assert (MEDIA_DIR / other).exists()

    def test_delete_of_an_unknown_file_is_a_disk_delete(self, stash):
        rel = _video("[[_keep/new.mp4")
        assert client.delete(f"/api/files?path={rel}").status_code == 200
        assert not (MEDIA_DIR / rel).exists()

    def test_delete_a_whole_folder(self, stash):
        a = stash.add_scene(_video("[[_keep/pack/a.mp4"))
        b = stash.add_scene(_video("[[_keep/pack/sub/b.mp4"))
        _video("[[_keep/pack/notes.txt")
        assert client.delete("/api/files?path=[[_keep/pack").status_code == 200
        assert sorted(c["in"]["id"] for c in stash.ops("sceneDestroy")) == sorted([a, b])
        assert not (MEDIA_DIR / FOLDER / "pack").exists()

    def test_delete_refused_by_stash_keeps_the_file(self, stash):
        rel = _video("[[_keep/a.mp4")
        stash.add_scene(rel)
        stash.refuse.add("sceneDestroy")
        resp = client.delete(f"/api/files?path={rel}")
        assert resp.status_code == 502
        assert resp.json()["detail"]["code"] == "stash_refused"
        assert (MEDIA_DIR / rel).exists()

    def test_move_out_forgets_the_scene_keeps_the_file(self, stash):
        rel = _video("[[_keep/a.mp4")
        sid = stash.add_scene(rel)
        job = _move(rel, "[[_edit")
        assert job["status"] == "done"
        assert (MEDIA_DIR / "[[_edit" / "a.mp4").exists()
        assert stash.ops("sceneDestroy") == [
            {"in": {"id": sid, "delete_file": False, "delete_generated": True}}
        ]

    def test_folder_moved_out(self, stash):
        a = stash.add_scene(_video("[[_keep/pack/a.mp4"))
        b = stash.add_scene(_video("[[_keep/pack/b.mp4"))
        _move("[[_keep/pack", "[[_edit")
        assert sorted(c["in"]["id"] for c in stash.ops("sceneDestroy")) == sorted([a, b])
        assert (MEDIA_DIR / "[[_edit" / "pack" / "a.mp4").exists()

    @pytest.mark.parametrize("op", ["move_within", "move_out", "delete", "rename"])
    def test_unreachable_refuses_and_nothing_moves(self, stash, op):
        rel = _video("[[_keep/a.mp4")
        (MEDIA_DIR / FOLDER / "sub").mkdir()
        client.post("/api/settings", json={"stash_url": "http://127.0.0.1:1"})
        if op == "delete":
            resp = client.delete(f"/api/files?path={rel}")
        elif op == "rename":
            resp = client.post(f"/api/files/rename?path={rel}", json={"new_name": "b.mp4"})
        else:
            dest = "[[_keep/sub" if op == "move_within" else "[[_edit"
            resp = client.post(f"/api/files/move?path={rel}", json={"destination": dest})
        assert resp.status_code == 503
        assert resp.json()["detail"]["code"] == "stash_unavailable"
        assert (MEDIA_DIR / rel).exists()

    def test_prefix_missing_refuses(self, stash):
        client.post("/api/settings", json={"stash_path_prefix": ""})
        rel = _video("[[_keep/a.mp4")
        resp = client.delete(f"/api/files?path={rel}")
        assert resp.status_code == 503
        assert (MEDIA_DIR / rel).exists()

    @pytest.mark.parametrize("op", ["delete", "rename", "move"])
    def test_the_folder_itself_is_protected(self, stash, op):
        if op == "delete":
            resp = client.delete(f"/api/files?path={FOLDER}")
        elif op == "rename":
            resp = client.post(f"/api/files/rename?path={FOLDER}", json={"new_name": "kept"})
        else:
            (MEDIA_DIR / "other").mkdir()
            resp = client.post(f"/api/files/move?path={FOLDER}", json={"destination": "other"})
        assert resp.status_code == 409
        assert resp.json()["detail"]["code"] == "stash_folder"
        assert (MEDIA_DIR / FOLDER).is_dir()

    def test_without_stash_everything_works_as_before(self):
        rel = _video("[[_keep/a.mp4")
        assert client.delete(f"/api/files?path={rel}").status_code == 200
        assert not (MEDIA_DIR / rel).exists()


# ── Review fixes (PR #90) ────────────────────────────────────────────────────
class TestReviewFixes:
    def test_folder_renamed_within_adds_no_play_and_no_identify(self, stash):
        stash.stash_boxes = ["https://stashdb.org/graphql"]
        client.post("/api/settings", json={"stash_identify": True})
        rel = _video("[[_keep/pack/a.mp4", b"bytes-a")
        sid = stash.add_scene(rel)
        stash.contents[f"f{sid}"] = b"bytes-a"
        _progress(rel, 0.0, 0.0, watched=1)
        resp = client.post("/api/files/rename?path=[[_keep/pack", json={"new_name": "renamed"})
        assert resp.status_code == 200
        m._stash_wait_idle()
        assert stash.scene_of("[[_keep/renamed/a.mp4")["id"] == sid
        assert stash.ops("sceneAddPlay") == []
        assert stash.ops("metadataIdentify") == []

    def test_scan_past_the_deadline_still_declares(self, stash, monkeypatch, caplog):
        monkeypatch.setattr(m, "STASH_SCAN_TIMEOUT", 0.2)
        monkeypatch.setattr(m, "STASH_JOB_POLL", 0.05)
        stash.job_status = "RUNNING"
        rel = _video("dl/slow.mp4")
        _progress(rel, 12.0, 100.0)
        with caplog.at_level("WARNING", logger="hoard"):
            _move(rel, FOLDER)
        scene = stash.scene_of("[[_keep/slow.mp4")
        assert stash.ops("sceneSaveActivity") == [{"id": scene["id"], "t": 12.0}]
        assert any("still running" in r.getMessage() for r in caplog.records)

    def test_a_long_scan_does_not_hold_a_progress_copy_back(self, stash):
        rel = _video("[[_keep/p.mp4")
        stash.add_scene(rel)
        gate = threading.Event()
        m._stash_submit(gate.wait, 10)  # the files worker is busy
        try:
            client.post(
                f"/api/progress?path={rel}", json={"position": 9, "duration": 100, "final": True}
            )
            deadline = time.monotonic() + 5
            while not stash.ops("sceneSaveActivity") and time.monotonic() < deadline:
                time.sleep(0.02)
            assert stash.ops("sceneSaveActivity")
        finally:
            gate.set()

    def test_partial_delete_purges_what_stash_deleted(self, stash):
        a = _video("[[_keep/pack/a.mp4")
        b = _video("[[_keep/pack/b.mp4")
        stash.add_scene(a)
        stash.add_scene(b)
        _progress(a, 5.0, 100.0)
        _progress(b, 6.0, 100.0)
        real = stash.op_sceneDestroy
        calls = []

        def second_fails(v):
            calls.append(v)
            if len(calls) == 2:
                raise RuntimeError("refused")
            return real(v)

        stash.op_sceneDestroy = second_fails
        resp = client.delete("/api/files?path=[[_keep/pack")
        assert resp.status_code == 502
        gone = [r for r in (a, b) if not (MEDIA_DIR / r).exists()]
        kept = [r for r in (a, b) if (MEDIA_DIR / r).exists()]
        assert len(gone) == 1 and len(kept) == 1
        assert _row(gone[0]) is None
        assert _row(kept[0]) is not None

    def test_signed_urls_are_stable_for_hours(self):
        assert m._stash_media_url("7", "screenshot") == m._stash_media_url("7", "screenshot")
        exp = int(m._stash_media_url("7", "screenshot").split("exp=")[1].split("&")[0])
        assert exp - time.time() >= m.FPX_URL_TTL


# ── BL-152: Stash's tags and rating, written from Hoard ──────────────────────
def _file_tags(rel: str) -> list[str]:
    with _db() as conn:
        return [r["tag"] for r in conn.execute("SELECT tag FROM file_tags WHERE path = ?", (rel,))]


class TestTagsAndRating:
    def test_reads_the_scene_tags(self, stash):
        rel = _video("[[_keep/a.mp4")
        outdoor = stash.add_tag("Outdoor")
        stash.add_scene(rel, tags=[dict(outdoor)], rating100=60)
        assert client.get(f"/api/stash/scene-tags?path={rel}").json() == {
            "tags": ["Outdoor"],
            "rating": 60,
        }

    def test_suggestions_most_used_first_case_kept(self, stash):
        rare, common = stash.add_tag("Rare"), stash.add_tag("POV")
        stash.add_tag("Unused")
        stash.add_scene(_video("[[_keep/a.mp4"), tags=[dict(common), dict(rare)])
        stash.add_scene(_video("[[_keep/b.mp4"), tags=[dict(common)])
        assert client.get("/api/stash/tags").json() == {"tags": ["POV", "Rare", "Unused"]}

    def test_add_an_existing_tag_whatever_its_case(self, stash):
        rel = _video("[[_keep/a.mp4")
        stash.add_tag("Outdoor")
        sid = stash.add_scene(rel)
        resp = client.post(f"/api/stash/scene-tags?path={rel}", json={"tag": "outdoor"})
        assert resp.status_code == 200, resp.text
        assert resp.json() == {"tags": ["Outdoor"]}
        assert stash.ops("tagCreate") == []
        assert [t["name"] for t in stash.scenes[sid]["tags"]] == ["Outdoor"]
        assert _file_tags(rel) == []

    def test_add_a_new_tag_creates_it_once(self, stash):
        rel, other = _video("[[_keep/a.mp4"), _video("[[_keep/b.mp4")
        stash.add_scene(rel)
        sid_b = stash.add_scene(other)
        resp = client.post(f"/api/stash/scene-tags?path={rel}", json={"tag": "  Night  Shot "})
        assert resp.json() == {"tags": ["Night Shot"]}
        client.post(f"/api/stash/scene-tags?path={other}", json={"tag": "night shot"})
        assert [v["in"]["name"] for v in stash.ops("tagCreate")] == ["Night Shot"]
        assert [t["name"] for t in stash.scenes[sid_b]["tags"]] == ["Night Shot"]
        # Adding a tag the scene already has writes nothing.
        before = len(stash.ops("sceneUpdate"))
        client.post(f"/api/stash/scene-tags?path={rel}", json={"tag": "NIGHT SHOT"})
        assert len(stash.ops("sceneUpdate")) == before

    def test_remove_a_tag(self, stash):
        rel = _video("[[_keep/a.mp4")
        a, b = stash.add_tag("A"), stash.add_tag("B")
        sid = stash.add_scene(rel, tags=[dict(a), dict(b)])
        resp = client.delete(f"/api/stash/scene-tags?path={rel}&tag=A")
        assert resp.json() == {"tags": ["B"]}
        assert [t["name"] for t in stash.scenes[sid]["tags"]] == ["B"]
        assert "t1" in stash.tags  # the tag itself stays in Stash

    def test_the_list_sees_the_write_at_once(self, stash):
        rel = _video("[[_keep/a.mp4")
        stash.add_scene(rel)
        assert client.get("/api/stash/folder?path=[[_keep").json()["scenes"][rel]["tags"] == []
        client.post(f"/api/stash/scene-tags?path={rel}", json={"tag": "New"})
        client.post(f"/api/stash/rating?path={rel}", json={"rating": 4})
        scene = client.get("/api/stash/folder?path=[[_keep").json()["scenes"][rel]
        assert scene["tags"] == ["New"] and scene["rating"] == 80

    def test_rating_and_clearing_it(self, stash):
        rel = _video("[[_keep/a.mp4")
        sid = stash.add_scene(rel)
        assert client.post(f"/api/stash/rating?path={rel}", json={"rating": 3}).json() == {
            "rating": 60
        }
        assert stash.scenes[sid]["rating100"] == 60
        client.post(f"/api/stash/rating?path={rel}", json={"rating": None})
        assert stash.scenes[sid]["rating100"] is None
        assert client.post(f"/api/stash/rating?path={rel}", json={"rating": 6}).status_code == 422

    def test_video_not_scanned_yet(self, stash):
        rel = _video("[[_keep/new.mp4")
        for resp in (
            client.get(f"/api/stash/scene-tags?path={rel}"),
            client.post(f"/api/stash/scene-tags?path={rel}", json={"tag": "x"}),
            client.post(f"/api/stash/rating?path={rel}", json={"rating": 2}),
        ):
            assert resp.status_code == 404
            assert resp.json()["detail"]["code"] == "stash_no_scene"
        assert stash.ops("tagCreate") == [] and stash.ops("sceneUpdate") == []
        assert _file_tags(rel) == []

    def test_unreachable_writes_nothing(self, stash):
        rel = _video("[[_keep/a.mp4")
        client.post("/api/settings", json={"stash_url": "http://127.0.0.1:1"})
        resp = client.post(f"/api/stash/scene-tags?path={rel}", json={"tag": "x"})
        assert resp.status_code == 502
        assert resp.json()["detail"]["code"] == "stash_unavailable"
        assert client.post(f"/api/stash/rating?path={rel}", json={"rating": 2}).status_code == 502
        assert client.get("/api/stash/tags").status_code == 502
        assert _file_tags(rel) == []

    def test_refused_write_is_reported(self, stash):
        rel = _video("[[_keep/a.mp4")
        stash.add_scene(rel)
        stash.refuse.add("sceneUpdate")
        resp = client.post(f"/api/stash/scene-tags?path={rel}", json={"tag": "x"})
        assert resp.status_code == 502
        assert resp.json()["detail"]["code"] == "stash_refused"

    def test_outside_the_folder_is_refused(self, stash):
        rel = _video("[[_edit/a.mp4")
        resp = client.post(f"/api/stash/scene-tags?path={rel}", json={"tag": "x"})
        assert resp.status_code == 409
        assert resp.json()["detail"]["code"] == "stash_not_here"
        assert stash.calls == []
        # Hoard's own tags are untouched there.
        assert client.post(f"/api/tags?path={rel}", json={"tag": "mine"}).status_code == 200
        assert _file_tags(rel) == ["mine"]

    def test_without_stash(self):
        assert client.get("/api/stash/tags").json() == {"tags": []}
        rel = _video("[[_keep/a.mp4")
        resp = client.get(f"/api/stash/scene-tags?path={rel}")
        assert resp.status_code == 409


# ── BL-153: keep / keep to edit, Identify and Edit, cuts inherit their source ──
def _names(scene) -> list[str]:
    return sorted(t["name"] for t in scene["tags"])


class _FakeFfmpeg:
    returncode = 0

    def __init__(self, cmd, **kwargs):
        Path(cmd[-1]).write_bytes(b"cut " + cmd[-1].encode())
        self.stderr = iter(())

    def wait(self):
        return 0


def _export(rel: str, destination: str, mode="merged", keep=False, segments=1):
    for i in range(segments):
        client.post(f"/api/segments?path={rel}", json={"seg_in": i * 10, "seg_out": i * 10 + 5})
    resp = client.post(
        f"/api/files/export-segments?path={rel}",
        json={"mode": mode, "destination": destination, "keep_original": keep},
    )
    if resp.status_code != 200:
        return resp
    job = _wait_job(resp.json()["job_id"])
    m._stash_wait_idle()
    return job


def _keep_to_edit(rel: str, destination: str = FOLDER):
    resp = client.post(
        f"/api/files/move?path={rel}", json={"destination": destination, "stash_edit": True}
    )
    if resp.status_code == 200:
        _wait_job(resp.json()["job_id"])
        m._stash_wait_idle()
    return resp


class TestKeepToEdit:
    def test_arrival_is_tagged_identify(self, stash):
        stash.add_tag("identify")  # an existing tag is reused whatever its case
        _move(_video("dl/a.mp4"), FOLDER)
        assert _names(stash.scene_of("[[_keep/a.mp4")) == ["identify"]
        assert stash.ops("tagCreate") == []

    def test_keep_to_edit(self, stash):
        _move(_video("dl/b.mp4"), FOLDER)
        _keep_to_edit(_video("dl/c.mp4"))
        assert _names(stash.scene_of("[[_keep/b.mp4")) == ["Identify"]
        assert _names(stash.scene_of("[[_keep/c.mp4")) == ["Edit", "Identify"]
        # Each tag is created once, then reused.
        assert sorted(v["in"]["name"] for v in stash.ops("tagCreate")) == ["Edit", "Identify"]

    def test_keep_to_edit_within_the_folder(self, stash):
        rel = _video("[[_keep/d.mp4")
        sid = stash.add_scene(rel)
        (MEDIA_DIR / FOLDER / "sub").mkdir()
        _keep_to_edit(rel, FOLDER + "/sub")
        assert _names(stash.scenes[sid]) == ["Edit", "Identify"]

    def test_keep_to_edit_a_folder_within(self, stash):
        # The folder is moved on disk and rescanned: the tags must come after the
        # rescan, once Stash knows the videos at their new paths.
        rels = [_video("[[_keep/pack/a.mp4"), _video("[[_keep/pack/b.mp4")]
        sids = []
        for rel in rels:
            sid = stash.add_scene(rel)
            stash.contents[f"f{sid}"] = (MEDIA_DIR / rel).read_bytes()
            sids.append(sid)
        (MEDIA_DIR / FOLDER / "sub").mkdir()
        _keep_to_edit("[[_keep/pack", FOLDER + "/sub")
        for sid in sids:
            assert stash.scenes[sid]["files"][0]["path"].startswith(PREFIX + "/sub/pack/")
            assert _names(stash.scenes[sid]) == ["Edit", "Identify"]

    def test_keep_to_edit_elsewhere_is_refused(self, stash):
        rel = _video("dl/e.mp4")
        resp = _keep_to_edit(rel, "[[_edit")
        assert resp.status_code == 409
        assert (MEDIA_DIR / rel).exists()

    def test_identification_never_removes_identify(self, stash):
        stash.stash_boxes = ["https://stashdb.org/graphql"]
        client.post("/api/settings", json={"stash_identify": True})
        stash.on_identify = lambda scene: scene.update(tags=[], title="Found")
        _keep_to_edit(_video("dl/f.mp4"))
        scene = stash.scene_of("[[_keep/f.mp4")
        assert scene["title"] == "Found"
        assert _names(scene) == ["Edit", "Identify"]

    def test_custom_tag_names(self, stash):
        client.post("/api/settings", json={"stash_tag_identify": "À vérifier"})
        _move(_video("dl/g.mp4"), FOLDER)
        assert _names(stash.scene_of("[[_keep/g.mp4")) == ["À vérifier"]


class TestExportToStash:
    @pytest.fixture(autouse=True)
    def _ffmpeg(self, monkeypatch):
        monkeypatch.setattr(m.subprocess, "Popen", _FakeFfmpeg)

    def _source(self, stash, rel="[[_keep/src.mp4", tags=("Identify", "Edit", "POV")):
        _video(rel)
        tags = [dict(stash.add_tag(n)) for n in tags]
        sid = stash.add_scene(
            rel,
            title="Source",
            date="2026-01-02",
            details="About it",
            urls=["https://example.org/x"],
            rating100=80,
            studio={"id": "s9", "name": "S"},
            performers=[{"id": "p1", "name": "Jane"}],
            tags=tags,
            stash_ids=[{"endpoint": "box", "stash_id": "abc"}],
        )
        return rel, sid

    def test_merged_cut_inherits_and_original_goes_to_edited(self, stash):
        rel, sid = self._source(stash)
        job = _export(rel, FOLDER)
        assert job["status"] == "done" and not job.get("move_error")
        cut = stash.scene_of("[[_keep/src [1 segment].mp4")
        assert cut["title"] == "Source" and cut["date"] == "2026-01-02"
        assert cut["details"] == "About it" and cut["urls"] == ["https://example.org/x"]
        assert cut["rating100"] == 80 and cut["studio"]["id"] == "s9"
        assert [p["id"] for p in cut["performers"]] == ["p1"]
        assert _names(cut) == ["Identify", "POV"]  # no Edit
        assert all("stash_ids" not in v["in"] for v in stash.ops("sceneUpdate"))
        assert stash.ops("metadataIdentify") == []
        # The original: in [[_edited, its scene forgotten, the file untouched.
        assert (MEDIA_DIR / "[[_edited" / "src.mp4").exists()
        assert not (MEDIA_DIR / rel).exists()
        (destroy,) = stash.ops("sceneDestroy")
        assert destroy["in"] == {"id": sid, "delete_file": False, "delete_generated": True}
        scanned = [p for op in stash.ops("metadataScan") for p in op["in"]["paths"]]
        assert scanned == [PREFIX + "/src [1 segment].mp4"]

    def test_individual_segments_each_inherit(self, stash):
        rel, _ = self._source(stash, tags=("POV",))
        _export(rel, FOLDER, mode="individual", segments=2)
        for i in (1, 2):
            cut = stash.scene_of(f"[[_keep/src [seg{i}].mp4")
            assert cut["title"] == "Source" and _names(cut) == ["POV"]  # Identify not had

    def test_source_without_scene_is_a_plain_arrival(self, stash):
        rel = _video("[[_edit/raw.mp4")
        _export(rel, FOLDER)
        cut = stash.scene_of("[[_keep/raw [1 segment].mp4")
        assert _names(cut) == ["Identify"] and cut["title"] == ""
        assert (MEDIA_DIR / "[[_edited" / "raw.mp4").exists()

    def test_keep_original_in_place(self, stash):
        rel, _ = self._source(stash)
        _export(rel, FOLDER, keep=True)
        assert (MEDIA_DIR / rel).exists()
        assert stash.ops("sceneDestroy") == []

    def test_collision_in_edited_moves_nothing(self, stash):
        rel, _ = self._source(stash)
        _video("[[_edited/src.mp4", b"older")
        job = _export(rel, FOLDER)
        assert "existe déjà" in job["move_error"]
        assert (MEDIA_DIR / rel).exists()
        assert (MEDIA_DIR / "[[_edited" / "src.mp4").read_bytes() == b"older"
        assert stash.ops("sceneDestroy") == []

    def test_custom_edited_folder(self, stash):
        client.post("/api/settings", json={"edited_folder": "trash/edited"})
        rel = _video("[[_edit/h.mp4")
        _export(rel, FOLDER)
        assert (MEDIA_DIR / "trash" / "edited" / "h.mp4").exists()

    def test_edited_folder_inside_the_stash_folder_is_refused(self, stash):
        client.post("/api/settings", json={"edited_folder": FOLDER + "/old"})
        rel = _video("[[_edit/i.mp4")
        resp = _export(rel, FOLDER)
        assert resp.status_code == 409 and (MEDIA_DIR / rel).exists()

    def test_unreachable_writes_nothing(self, stash):
        rel, _ = self._source(stash)
        client.post("/api/settings", json={"stash_url": "http://127.0.0.1:1"})
        resp = _export(rel, FOLDER)
        assert resp.status_code == 503
        assert (MEDIA_DIR / rel).exists()
        assert not (MEDIA_DIR / FOLDER / "src [1 segment].mp4").exists()

    def test_default_edited_folder_sits_beside_the_stash_folder(self):
        assert m._edited_folder({"stash_folder": "downloads/[[_keep"}) == "downloads/[[_edited"
        assert m._edited_folder({"stash_folder": "[[_keep"}) == "[[_edited"
        assert m._edited_folder({"edited_folder": "x/y"}) == "x/y"


def test_export_without_stash_keeps_its_behaviour(monkeypatch):
    monkeypatch.setattr(m.subprocess, "Popen", _FakeFfmpeg)
    rel = _video("in/v.mp4")
    (MEDIA_DIR / "out").mkdir()
    job = _export(rel, "out")
    assert job["status"] == "done"
    assert (MEDIA_DIR / "out" / "v.mp4").exists()  # the original follows the cut
