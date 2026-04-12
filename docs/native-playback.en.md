# Hoard - Native Playback Investigation

## Purpose

BL-019 is a research ticket. The goal is to decide when Hoard should keep using the browser's native playback path and when it should switch to `/api/transcode`, especially on iPad and other Safari-based clients.

This document is intentionally pragmatic: it does not try to list every codec profile ever shipped by every browser. It identifies the combinations Hoard can treat as safe, the ones that need probing, and the ones that should still default to a fallback.

## Current Hoard Behavior

Today Hoard uses this flow:

1. Fetch `/api/media-info` on demand for the selected file.
2. Build codec-aware MIME types from ffprobe metadata.
3. Use `video.canPlayType()` as the first gate.
4. When available, use `navigator.mediaCapabilities.decodingInfo()` with the exact file metadata.
5. Open the file with `/api/stream` only when support is confirmed or still plausible.
6. If probing rejects native playback, or if the browser later fails with `MEDIA_ERR_SRC_NOT_SUPPORTED`, retry with `/api/transcode`.

This keeps `/api/transcode` as the compatibility escape hatch, but moves most decisions earlier so Hoard does not always wait for a failed native load before switching.

## Compatibility Matrix

Container and codec must be evaluated together. A codec may be supported in one container but still fail in another.

| Combination | Hoard recommendation | Why |
|---|---|---|
| MP4 + H.264/AVC video + AAC audio | Prefer native by default | This is the broadest cross-browser baseline. Apple explicitly recommends H.264-encoded MP4 for static files, and MDN still treats MP4/H.264 as the widely compatible fallback. |
| MP4 + HEVC/H.265 video + AAC audio | Probe first, never assume | Safari and Safari on iOS support HEVC broadly on supported Apple hardware, but support outside Safari depends on OS, browser build, extensions, and hardware decoding. This is not a universal web baseline. |
| MP4 + AV1 video + AAC or Opus audio | Probe first, never assume | AV1 is broadly available in Chromium and Firefox, but Safari support is still hardware-limited on newer Apple devices only. |
| WebM + VP8/VP9 video + Opus/Vorbis audio | Probe first, but native is reasonable on modern browsers | WebM is broadly available now, including recent Safari releases, but older Safari and iOS versions were partial for years. Hoard should treat it as modern-native, not universal-native. |
| MKV / Matroska with browser codecs inside | Do not prefer native by default | Browser HTML5 support is not reliably defined by the container alone, and Matroska remains a poor default assumption for direct browser playback. Treat it as fallback territory until a probe proves otherwise. |
| MOV / legacy QuickTime / MPEG containers | Do not prefer native by default | Legacy or platform-specific containers are not a good web baseline, even when the embedded codec itself is common. |

## Practical Conclusions For Hoard

### Safe native-first baseline

If Hoard knows a file is `video/mp4` with H.264/AVC video and AAC audio, native playback can stay the default choice.

### Formats that must be device-checked

These formats should only be preferred natively after probing the current browser and device:

- HEVC / H.265
- AV1
- WebM / VP8 / VP9
- Anything that depends on newer Safari support
- Anything with unusual audio tracks, bit depth, HDR, or container quirks

### Formats that should stay on fallback paths

These should not be treated as browser-safe until Hoard has hard evidence otherwise:

- MKV / Matroska
- MOV and other legacy containers
- Unidentified container or codec combinations

## Implemented Detection Strategy

1. `/api/media-info` returns ffprobe-based metadata for a single selected file.
2. The frontend builds codec-aware MIME strings from that response.
3. `video.canPlayType(contentType)` rejects obviously unsupported combinations early.
4. `navigator.mediaCapabilities.decodingInfo()` is used when the browser supports it and the metadata is complete enough.
5. Native playback stays the default only for the safe baseline or for formats the browser probe does not reject.
6. `/api/transcode` remains the fallback when probing rejects native playback or when the native load still fails at runtime.

## Remaining Gaps

- Hoard still does not cache probe results across sessions.
- The fallback logic remains player-side only; file lists are not pre-annotated with codec support.
- Unknown or partially described files still rely on optimistic `/api/stream` plus runtime fallback.

## Rules To Keep

- Do not decide from user agent alone.
- Do not equate "iPad" with "all HEVC files play natively".
- Do not equate "Safari supports WebM" with "all WebM combinations are safe".
- Treat container, codecs, and hardware capability as separate inputs.
- Keep `/api/transcode` as the compatibility escape hatch even after probing is added.

## Current Product Rule

Hoard now follows this rule set:

1. MP4/H.264/AAC remains universally native-first.
2. HEVC, AV1, and WebM families are native only when browser probing does not reject them.
3. MKV and legacy containers remain conservative and usually end up on fallback paths unless the browser clearly accepts them.
4. `/api/transcode` stays mandatory as the last compatibility fallback.

## Sources Used

- Apple WebKit guidance for delivering video content in Safari, including the recommendation to use H.264 MP4 for static files.
- MDN documentation for `HTMLMediaElement.canPlayType()`.
- MDN documentation for `MediaCapabilities.decodingInfo()`.
- MDN guides for media containers, codec compatibility, and unsupported-media handling.
- Can I Use support tables for HEVC, WebM, and AV1, consulted on 2026-04-12 for trend validation.
