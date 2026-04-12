# Hoard - Native Playback Investigation

## Purpose

BL-019 is a research ticket. The goal is to decide when Hoard should keep using the browser's native playback path and when it should switch to `/api/transcode`, especially on iPad and other Safari-based clients.

This document is intentionally pragmatic: it does not try to list every codec profile ever shipped by every browser. It identifies the combinations Hoard can treat as safe, the ones that need probing, and the ones that should still default to a fallback.

## Current Hoard Behavior

Today Hoard uses this flow:

1. Open the file with `/api/stream`.
2. Let the browser try to play the original file with the native HTML5 `<video>` element.
3. If playback fails with `MEDIA_ERR_SRC_NOT_SUPPORTED`, retry with `/api/transcode`.

This is simple and already works, but the decision happens too late. The browser error arrives only after an attempted load, and Hoard has no structured knowledge of the file's container, codecs, bit depth, or other constraints.

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

## Recommended Detection Strategy

BL-019 does not implement this strategy yet, but it establishes the recommended direction.

1. Add a lightweight metadata endpoint backed by `ffprobe`.
2. Return at least: container, video codec, audio codec, width, height, bitrate, framerate, audio channels, sample rate, and bit depth when available.
3. Build a precise MIME string in the frontend, for example `video/mp4; codecs="avc1.640028, mp4a.40.2"`.
4. Call `video.canPlayType(contentType)` as a cheap first gate.
5. When metadata is complete and `navigator.mediaCapabilities.decodingInfo` is available, probe the exact file as `type: "file"`.
6. Use native playback only when the browser reports support.
7. Keep the current `video.onerror` retry to `/api/transcode` as a last-resort safety net.
8. Cache probe results by a media fingerprint plus browser signature so repeated opens do not re-run the full decision path unnecessarily.

## Rules To Keep

- Do not decide from user agent alone.
- Do not equate "iPad" with "all HEVC files play natively".
- Do not equate "Safari supports WebM" with "all WebM combinations are safe".
- Treat container, codecs, and hardware capability as separate inputs.
- Keep `/api/transcode` as the compatibility escape hatch even after probing is added.

## Product Decision After This Investigation

The immediate outcome for Hoard should be:

1. Keep the current optimistic `/api/stream` then `/api/transcode` fallback until metadata support exists.
2. Plan metadata extraction before changing native-versus-transcode heuristics.
3. After probing is added, only mark MP4/H.264/AAC as universally native-first.
4. Mark HEVC, AV1, and WebM families as conditional native playback based on runtime probing.
5. Keep MKV and legacy containers on conservative fallback rules.

## Sources Used

- Apple WebKit guidance for delivering video content in Safari, including the recommendation to use H.264 MP4 for static files.
- MDN documentation for `HTMLMediaElement.canPlayType()`.
- MDN documentation for `MediaCapabilities.decodingInfo()`.
- MDN guides for media containers, codec compatibility, and unsupported-media handling.
- Can I Use support tables for HEVC, WebM, and AV1, consulted on 2026-04-12 for trend validation.
