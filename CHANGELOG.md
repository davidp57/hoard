# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Video download via yt-dlp: bookmarklet + 📥 button in the header let you send any web video to Hoard for download on the NAS
- `POST /api/download` endpoint: accepts a URL and an optional `cookies` string, creates a background job, returns a `job_id`
- Download progress tracked in the existing job cards (bottom-right of the screen)
- New settings: `download_folder` (target folder relative to `MEDIA_ROOT`, default `Downloads`) and `download_cookies_path` (path to a persistent Netscape cookies.txt file)
- Cookie passthrough: bookmarklet captures `document.cookie` and sends it with the request; a persistent cookies.txt file is also supported for authenticated sites
- Bookmarklet auto-generated in Settings → Downloads; drag-to-bookmark instructions provided
- SSRF protection on `/api/download`: `file://`, localhost, and RFC-1918 private network addresses are rejected
- **Smart video source detection**: bookmarklet now captures `<video>.currentSrc` from the page DOM — enables downloading from sites without a dedicated yt-dlp extractor (Patreon, etc.)
- Referer header passthrough: when downloading a direct video URL, the original page URL is sent as `Referer` so CDNs that check the origin accept the request

### Fixed
- Cloudflare anti-bot 403 errors: yt-dlp now impersonates Chrome via `curl-cffi` (`impersonate` option at top-level, `curl-cffi>=0.10.0,<0.15.0`)
- Invalid Netscape cookie file format: domain is now prefixed with `.` as required when `include_subdomains=TRUE`

## [1.0.0] - 2026-04-05

### Added
- Settings page with PIN lock (numeric, SHA-256 hashed), accessible via ⚙️ button in header
- Configurable touch gestures: enable/disable per category, edge zone %, swipe threshold, sensitivity, double-tap values
- Configurable privacy timeout (auto-close player after N minutes of inactivity)
- Configurable watched threshold (default 90%)
- Home folder and sort order are stored in backend DB (migrated from localStorage)
- Multi-tap seek accumulation: N taps = (N−1) × base seek value
- 3 vertical zones on both left and right seek edges (top=fastest, bottom=slowest)
- Fit/Fill toolbar button (replaces triple-tap gesture)
- Full bilingual documentation (EN + FR): user guide, installation, developer guide, getting-started guide
- Page Visibility API privacy: player auto-closes when device wakes after timeout
- Seek bar touch area extended (±20px) to prevent swipe conflict
- Double-tap right zone split into 3 vertical thirds (+30s / +60s / +90s base values)

### Changed
- Project renamed from MediaBrowser to Hoard
- Docker image: `ghcr.io/davidp57/nas-vid-bro` → `ghcr.io/davidp57/hoard`
- docker-compose service name: `mediabrowser` → `hoard`
- README rewritten as bilingual entry point

[Unreleased]: https://github.com/davidp57/hoard/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/davidp57/hoard/releases/tag/v1.0.0
