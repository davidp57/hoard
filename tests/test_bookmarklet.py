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


# --- Site-specific step: xHamster (_bookmarkletSiteStream) -------------------

SITE_HARNESS = r"""
const spec = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const src = _bookmarkletInline(_bookmarkletSiteStream);
if (/%[0-9a-fA-F]{2}/.test(src)) throw new Error('percent escape in embedded code');
const site = eval('(' + src + ')');
const win = spec.initials === undefined ? {} : { initials: spec.initials };
process.stdout.write(JSON.stringify(site({ hostname: spec.host }, win)));
"""

XH = "xhamster.com"
HLS = "https://video-nss.xhcdn.com/key=abc/media=hls4/multi=256x144:144p/001/024/807/_TPL_.av1.mp4.m3u8"
MP4_720 = "https://video-nss.xhcdn.com/key=abc/001/024/807/720p.h264.mp4"
MP4_480 = "https://video-nss.xhcdn.com/key=abc/001/024/807/480p.h264.mp4"


def _site(host, initials=None):
    script = _picker_source() + SITE_HARNESS
    spec = {"host": host} if initials is None else {"host": host, "initials": initials}
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


# Ciphertexts in xHamster's format, one per byte generator (1-7), made with the
# real yt-dlp 2026.08.19 (_ByteGenerator, XOR is its own inverse) and checked
# with its _decipher_hex_string. Frozen here because conftest replaces yt_dlp
# with a stub for the whole session. Each pair: (whole URL, path segment).
# URL seeds: 0x9E3779B9 as a negative int32 (odd algos), 0x1234ABCD (even).
# Segment seed: -123456789.
CIPHER_PLAIN_URL = "https://cdn.xhcdn.com/a/b.m3u8"
CIPHER_PLAIN_SEG = "key=abc,end=1700000000"
CIPHERS = {
    1: (
        "01b979379eac27e28d4b0d05ae8f3f906b98d7712d7a4d05e2e5689b3e5e45a3e645f7",
        "01eb32a4f82530c972033b87dfd3f33cea7b163ccb2ed5306f02d9",
    ),
    2: (
        "02cdab3412637dfa9c3f2c607d06f4f8be2212d19aa4f15f2aa3852db9a451f9caf25a",
        "02eb32a4f81c4ffe58670e67291cefa7c11c2a3c4c1ed6c3740674",
    ),
    3: (
        "03b979379e98d394f589318b1a69fcc5f06f31137d0cf31e71ab56f8e7df1a55dcaf6f",
        "03eb32a4f85977b68c70ad264848dbc774155e4695719e36c5cac5",
    ),
    4: (
        "04cdab34121f5588a1ccecd4bf2beaa8240c4472a614557e5040391030dea51fc9a008",
        "04eb32a4f875c383b92d636126ee6e7b8007f60fac2b62fac530b8",
    ),
    5: (
        "05b979379ef865d8a6bcca1cfaa8ab57d50faa28d3684da869f4a5ca1d4bac90b1e408",
        "05eb32a4f806575a9be56da6a77680855731d86248c6afaaa5f071",
    ),
    6: (
        "06cdab34126c6f1d16350fbc73da065ba37f6f19a1aeb7786476eeca6d0de85a3f159d",
        "06eb32a4f86605b3276f1e6086b6259d3301e0d245c264ca2b575c",
    ),
    7: (
        "07b979379ed93a997aefdd4a9ffcadad40b641361c0eeaaa39ffca702fbe57f14027ab",
        "07eb32a4f83ddc00f62a0f23c200c1651af03acd5cfe491412e371",
    ),
}


def _xplayer(sources):
    return {"xplayerSettings": {"sources": sources}}


def test_site_stream_ignores_other_sites():
    assert _site("example.com", _xplayer({"hls": {"url": HLS}})) == ""


@pytest.mark.parametrize(
    "host",
    ["xhamster.com", "fra.xhamster.com", "xhamster19.com", "m.xhamster.desi", "xhday.com"],
)
def test_site_stream_xhamster_mirrors_send_hls_master(host):
    assert _site(host, _xplayer({"hls": {"url": HLS}})) == HLS


def test_site_stream_hls_fallback_when_url_missing():
    assert _site(XH, _xplayer({"hls": {"url": "", "fallback": HLS}})) == HLS


def test_site_stream_hls_wins_over_standard():
    sources = {"standard": {"h264": [{"quality": "720p", "url": MP4_720}]}, "hls": {"url": HLS}}
    assert _site(XH, _xplayer(sources)) == HLS


def test_site_stream_standard_best_mp4_when_no_hls():
    sources = {
        "standard": {
            "h264": [
                {"quality": "480p", "url": MP4_480},
                {"quality": "720p", "url": MP4_720},
                {"quality": "240p", "url": "https://video-nss.xhcdn.com/240p.h264.mp4"},
            ]
        }
    }
    assert _site(XH, _xplayer(sources)) == MP4_720


def test_site_stream_standard_m3u8_wins_over_mp4_and_h264_over_av1():
    av1 = "https://video-nss.xhcdn.com/key=abc/_TPL_.av1.mp4.m3u8"
    h264 = "https://video-nss.xhcdn.com/key=abc/_TPL_.h264.mp4.m3u8"
    sources = {
        "standard": {
            "av1": [{"quality": "auto", "url": av1}],
            "h264": [{"quality": "1080p", "url": MP4_720}, {"quality": "auto", "url": h264}],
        }
    }
    assert _site(XH, _xplayer(sources)) == h264


@pytest.mark.parametrize("algo", range(1, 8))
def test_site_stream_deciphers_whole_hex_url(algo):
    """Every one of yt-dlp's seven generators, ported to JS int32 arithmetic."""
    cipher = CIPHERS[algo][0]
    assert _site(XH, _xplayer({"hls": {"url": cipher}})) == CIPHER_PLAIN_URL


@pytest.mark.parametrize("algo", range(1, 8))
def test_site_stream_deciphers_hex_path_segment(algo):
    rest = "/media=hls4/multi=256x144:144p/_TPL_.mp4.m3u8"
    url = f"https://video-nss.xhcdn.com/{CIPHERS[algo][1]}{rest}"
    expected = f"https://video-nss.xhcdn.com/{CIPHER_PLAIN_SEG}{rest}"
    assert _site(XH, _xplayer({"hls": {"url": url}})) == expected


def test_site_stream_skips_unknown_algorithm_and_dummy_ciphertext():
    bad = "09" + "00" * 20  # algorithm 9 does not exist
    sources = {
        "hls": {"url": bad, "fallback": "abcdef"},
        "standard": {"h264": [{"quality": "480p", "url": MP4_480}]},
    }
    assert _site(XH, _xplayer(sources)) == MP4_480


@pytest.mark.parametrize(
    "initials",
    [
        None,
        {},
        {"xplayerSettings": {}},
        _xplayer(None),
        _xplayer({}),
        _xplayer({"hls": {"url": ""}}),
    ],
)
def test_site_stream_missing_data_falls_back(initials):
    assert _site(XH, initials) == ""
