# Pad convention — Hoard and PadView

This document is authoritative for **both** projects.
It mirrors PadView's `docs/convention-manette.md` (French): any change is carried to both repositories in the same move.
Set on 2026-10-07 (lot PAD-LEFT-HAND here, PV-35 in PadView).

## The rule: one function, one place

A function present in both applications sits in the same place in both.
What exists in only one keeps its own place: PadView's channel-hopping stays on A/B because it is its main function, as play/pause is Hoard's.

The Steam Frame's pad is **two separate controllers**, one per hand, which the system presents as one ordinary gamepad.
Hence the split:

- **Left hand — what you watch**: volume, speed, jumps in the video.
- **Right hand — the rest**: A/B/X/Y, R1, R2, Start.

## Shared

| Control | Function | PadView | Hoard |
|---|---|---|---|
| **Y** | Fullscreen | ✓ | ✓ |
| **L3** | Mute / unmute | ✓ | ✓ |
| **Start** | Pad help | ✓ | ✓ |
| **Select** | Context menu (commands without a button of their own) | ✓ | ✓ |
| **B** in a window | Close / back | ✓ | ✓ |
| **A** in a window | Confirm | ✓ | ✓ |
| **D-pad** in a window | Choose / scroll | ✓ | ✓ |
| **R2 held** | View layer: left stick ↕ zoom, right stick pans / looks, L3 resets the zoom | framing (Stripchat) | VR layer |
| **L1** | Modifier | ✓ | ✓ (with R1) |
| **Left stick ↕** | Volume | ✓ | ✓ |
| **Left stick ↔** (video) | Speed while held: 1× at rest, linear on each side, 0.25× fully left, 4× fully right; back to the previous speed on release | ThisVid | ✓ (2× max when transcoded) |
| **Right stick ↔** (video) | Fine seek, 5 % of the duration per second at full tilt | ThisVid | ✓ |
| **D-pad ← / →** (video) | −30 s / +30 s | ThisVid | ✓ (`seek_medium`) |
| **D-pad ↑** (video) | +60 s | ThisVid | ✓ (`seek_long`) |
| **D-pad ↓** (video) | +15 s | ThisVid | ✓ |

Stripchat is live: no speed, no jumps.
Its D-pad keeps the volume while watching (↑/↓ this model's level, ←/→ the global volume), and its left stick ↔ stays free.

## Specific to each application

| Control | PadView | Hoard (player) |
|---|---|---|
| **A** | Next | Play / pause |
| **B** | Previous | Close the player |
| **X** | Random | Toggle watched |
| **R1** | free (Stripchat), play / pause (ThisVid) | modifier |
| **R3** | Debug mode | free |
| **Guide** | Boss screen | — |
| **L1 + R1 + Select** | — | Side-by-side screen |

## Button names

Both help screens name the buttons **A, B, X, Y, L1, R1, L2, R2, L3, R3, Select, Start, Guide**, D-pad ↑ ↓ ← →.
No Share, Options, Back, View, Menu or Xbox.

## Engine settings

| Setting | Value | Note |
|---|---|---|
| Pad polling | every frame (`requestAnimationFrame`) | PadView keeps a 50 ms poll as a fallback when frames stop |
| Deadzone | 0.20, rescaled `(v − dz) / (1 − dz)` | configurable in Hoard |
| Vibration | short, on every command (40 to 100 ms) | can be turned off: Hoard *Settings → Gamepad*, PadView *Réglages → Vibration*; Chromium only |
| Held-modifier badge | "🎮 L1", "🎮 R2"… | Hoard top right, PadView top centre (its corners are taken) |
| Toasts | bottom centre | |
| Pad connection toast | Hoard yes, PadView no | PadView reloads the page on every navigation, so the toast would come back on every command (PV-6c) |

## Interface size

Both applications grow with the screen past 1920×1080 and do not change below it: one unit is `max(1px, min(100vw / 1920, 100dvh / 1080))`.
Hoard carries it through `rem` (BL-137); PadView, injected into another site's page whose `rem` it does not control, through the `--pv-u` variable (PV-35).
1-2 px hairlines stay in pixels in both.
