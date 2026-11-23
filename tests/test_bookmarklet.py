"""Video-source selection of the download bookmarklet.

The bookmarklet is JavaScript embedded in frontend/index.html; the project has no
JS test framework. Its selection logic lives in a plain function between two
markers, which these tests extract and run under Node with a fake DOM. They run
the exact one-line source the bookmarklet embeds (_bookmarkletInline), so a
'//' comment or a missing ';' that would break it inside a javascript: URL fails
here too. Skipped when Node is not installed (it is on GitHub's ubuntu runners).
"""

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="Node.js not installed")

INDEX = Path(__file__).resolve().parent.parent / "frontend" / "index.html"
PAGE = "https://example.com/videos/some-title-123"

# Builds a fake document from a JSON spec and calls the embedded picker.
HARNESS = r"""
const spec = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const src = _bookmarkletInline(_bookmarkletPickVideo);
if (/%[0-9a-fA-F]{2}/.test(src)) throw new Error('percent escape in embedded code');
// eval is the point: run the very string the bookmarklet embeds (test-only, own code).
const pick = eval('(' + src + ')');
function video(v) {
  return {
    currentSrc: v.currentSrc || '',
    src: v.src || '',
    getBoundingClientRect: () => ({ width: v.w, height: v.h }),
    querySelectorAll: () => (v.sources || []).map((s) => ({ src: s })),
  };
}
const nodes = {
  video: (spec.videos || []).map(video),
  'iframe[src]': (spec.iframes || []).map((s) => ({ src: s })),
};
const doc = { querySelectorAll: (sel) => nodes[sel] || [] };
const perf = { getEntriesByType: () => spec.resources || [] };
process.stdout.write(JSON.stringify(pick(doc, perf)));
"""


def _picker_source():
    html = INDEX.read_text(encoding="utf-8")
    m = re.search(r"// BEGIN bookmarklet-pick.*?\n(.*?)// END bookmarklet-pick", html, re.S)
    assert m, "bookmarklet-pick markers not found in index.html"
    return m.group(1)


def _pick(spec):
    script = _picker_source() + HARNESS
    out = subprocess.run(
        [NODE, "-e", script],
        input=json.dumps(spec),
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


BIG_MP4 = "https://cdn.example.com/full/movie_1080p.mp4"
SMALL_MP4 = "https://thumb-ah.flixcdn.com/xc/19/heat-preview/fh_heatmap_preview_v6_a-352x220.mp4"
CAM_M3U8 = "https://edge-hls.saawsedge.com/hls/251503909/251503909_240p.m3u8"


def test_large_blob_video_sends_page_url():
    """xHamster, 2026-11-23: the main player is MSE (blob:), a seek-bar preview mp4
    and a cam widget are also on the page and in the network list. The page URL
    must win, so yt-dlp's extractor does the job."""
    spec = {
        "videos": [
            {"w": 352, "h": 220, "currentSrc": SMALL_MP4},
            {"w": 1280, "h": 720, "currentSrc": "blob:https://example.com/abc"},
        ],
        "resources": [
            {"name": CAM_M3U8, "initiatorType": "xmlhttprequest"},
            {"name": SMALL_MP4, "initiatorType": "video"},
        ],
    }
    assert _pick(spec) == ""


def test_largest_direct_video_wins_over_a_smaller_one_first_in_dom():
    spec = {
        "videos": [
            {"w": 352, "h": 220, "currentSrc": SMALL_MP4},
            {"w": 960, "h": 540, "currentSrc": BIG_MP4},
        ]
    }
    assert _pick(spec) == BIG_MP4


def test_two_large_videos_pick_the_larger():
    other = "https://cdn.example.com/ad/promo.mp4"
    spec = {
        "videos": [
            {"w": 480, "h": 270, "currentSrc": other},
            {"w": 1280, "h": 720, "currentSrc": BIG_MP4},
        ]
    }
    assert _pick(spec) == BIG_MP4


def test_main_video_source_element_used_when_no_current_src():
    spec = {"videos": [{"w": 800, "h": 450, "sources": [BIG_MP4]}]}
    assert _pick(spec) == BIG_MP4


def test_main_video_without_any_source_sends_page_url():
    spec = {
        "videos": [{"w": 800, "h": 450}],
        "resources": [{"name": BIG_MP4, "initiatorType": "video"}],
    }
    assert _pick(spec) == ""


def test_only_small_videos_are_ignored_even_in_performance_entries():
    spec = {
        "videos": [{"w": 352, "h": 220, "currentSrc": SMALL_MP4}],
        "resources": [{"name": SMALL_MP4, "initiatorType": "video"}],
    }
    assert _pick(spec) == ""


def test_preview_urls_skipped_by_performance_strategies():
    spec = {
        "resources": [
            {"name": BIG_MP4, "initiatorType": "xmlhttprequest"},
            {"name": "https://cdn.example.com/thumbs/clip_preview.mp4", "initiatorType": "video"},
        ]
    }
    assert _pick(spec) == BIG_MP4


def test_known_host_iframe_when_no_main_video():
    embed = "https://iframe.mediadelivery.net/embed/123/abc"
    spec = {"iframes": ["https://ads.example.com/x", embed]}
    assert _pick(spec) == embed


def test_nothing_found_sends_page_url():
    assert _pick({}) == ""


def test_largest_resource_fallback():
    spec = {
        "resources": [
            {"name": "https://cdn.example.com/app.js", "transferSize": 2_000_000},
            {"name": "https://cdn.example.com/stream/chunk", "transferSize": 900_000},
        ]
    }
    assert _pick(spec) == "https://cdn.example.com/stream/chunk"
