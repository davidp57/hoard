# Hoard — User Guide

## Overview

Hoard is a web-based media file browser. It lets you navigate a network drive (NAS), play videos, view images and comic archives, listen to audio files and read PDFs directly in the browser, and remember where you left off.

---

## Main Interface

The interface is split into two areas:

- **Left (or full-screen on mobile):** the file browser
- **Right (or full-screen overlay on mobile):** the video player

### File Browser

The browser displays the contents of a folder. A **breadcrumb** at the top lets you navigate up. The **🏠** button returns to the home screen.

### Home Screen and Home Roots

If no home roots are configured, the browser opens directly at `MEDIA_ROOT`. If home roots are defined (via **Settings → Home roots**), pressing **🏠** shows a selection screen listing each named home root. Click one to navigate directly to it.

Each file or folder is shown with:

- Its name
- A **watch status indicator** (for video files):
  - Neutral background → **unseen**
  - Yellow background + progress bar + percentage → **in progress**
  - Green background → **watched** (≥ 90 % viewed)

### Sorting the List

The sort bar offers five criteria, each reversible with the **↓ / ↑** button:

| Criterion | What it orders by |
|-----------|-------------------|
| **Date** | The file or folder date on disk (handy to spot newly arrived content) |
| **Nom** (Name) | Alphabetical order |
| **Taille** (Size) | File size |
| **État** (State) | Unseen, then in progress, then seen |
| **Vu** (Watched) | Date of the last viewing |

The **Vu** sort answers "what did I watch last". A folder takes the date of the most recently watched media found **anywhere below it**, however deep: resuming a video buried in a sub-folder lifts its whole top-level folder to the head of the list. Entries never opened have no watch date: they are grouped at the end of the list, ordered between themselves by file date.

The sort is **remembered**: the criterion and the direction picked in the bar are stored server-side and reapplied when the app reopens, including from another device. **Settings → Tri de la liste** (list sort) shows the current sort and lets you change it without using the bar.

### Search

A **🔍** field is available in the sort bar. The search is case-insensitive and recursive within the current folder. Results replace the list; clearing the field (or pressing ✕) returns to normal browsing.

### Tags and Tag Filtering

Any file or folder can carry **free-form text tags** (e.g. `excellent`, `to-finish`). Tags are stored in SQLite and displayed as coloured badges in the list.

| Action | How |
|--------|-----|
| Add / remove a tag | Click the **🏷** button next to the entry |
| Filter the list by a tag | Click a badge in the **tag filter bar** below the sort bar |
| Clear the filter | Click the same badge again, or navigate to another folder |

The tag filter bar appears automatically as soon as a folder contains at least one tagged file.
|--------|-------------|
| **▶ Play** | Opens the video in the player |
| **🏷 Tags** | Opens the tag management modal |
| **📁 Move** | Opens the move modal (pinned folders + free-pick browser) |
| **✏ Rename** | Opens the rename dialog (`R` key) |
| **🗑 Delete** | Deletes the file after confirmation |

### Moving to Any Folder

The move modal offers two modes:

- **Pinned folders**: one-tap move to a predefined folder.
- **📂 Browse…**: opens a destination picker that browses the full folder tree so you can choose any destination.

### A File of the Same Name Already Exists at the Destination

Hoard never replaces a file without asking. When the destination folder already
holds a file with the same name, a dialog opens and offers two choices:

- **Overwrite**: the moved file permanently replaces the one already there and
  takes its place in the list — watch progress, tags and segments follow the moved
  file.
- **Cancel**: nothing changes.

The dialog works with a gamepad (D-pad ↑/↓ to choose, **A** to confirm, **B** to
cancel) as well as with the keyboard (↑/↓, `Enter`, `Esc`). The cursor starts on
**Cancel**: overwriting cannot be undone, so it has to be a choice.

A **folder** already present at the destination cannot be replaced — Hoard says so
and leaves everything in place.

---

## Alternative Media Viewers

In addition to videos, Hoard can open several other file types directly in the interface.

### Images

JPG, PNG, GIF, WEBP, BMP, TIFF, and AVIF files open in an integrated image viewer.

- **← / →** (keyboard or buttons): previous / next image in the folder
- **▣ button**: toggle between fit-width and full-page display
- **✕**: close the viewer

### Galleries (image folders)

A folder containing several images (more than 3) and no video is treated as a
**gallery**: it shows up in the list as a single media (🖼️ icon, progress bar, watched
state), and opening it shows the first image right away instead of the file list.

- You read images one after another; the position is saved and resumed on reopen, just
  like a video.
- A gallery is a single image folder. A folder that **contains sub-folders** stays browsable and shows each sub-folder as its own gallery (so a folder of albums opens as a list of galleries, not one giant sequence).
- A **thumbnail strip** under the image acts as a seek bar: click a thumbnail to jump.
- **Zoom**: mouse wheel (zoom centered on the cursor), click-drag to pan, double-click to
  toggle zoom ↔ fit. Keyboard: `+` / `-` to zoom, `0` to reset; arrows pan while zoomed
  (otherwise they go to the previous / next image). Gamepad: left stick pans, right stick
  ↕ zooms.
- With a mouse (desktop), hover a thumbnail to reveal ✕ (delete that image) and › (move
  that image). With keyboard/gamepad, delete/move act on the **whole gallery** (like a
  movie), and `W` marks it watched / unwatched.
- A stray non-image file (PDF, text…) stays accessible as a **passenger**: it keeps its
  place in the sequence with a preview.

### Comic/manga archives (.cbz, .zip, .cbr)

Image archives are galleries too: they open page by page in the same viewer, with the
thumbnail strip.

- Navigation identical to the image viewer (← / →)
- Current page is saved so you can resume where you left off
- `.cbr` requires `unrar-free` to be installed on the server

### PDF

PDF files are rendered directly in the browser via PDF.js.

- **← / →**: previous / next page
- **− / +**: zoom out / zoom in
- **▣ button**: toggle between fit-width and original size
- Current page is saved

### Audio (.mp3, .flac, .ogg, .m4a, .aac, .wav, .opus)

Audio files open in a minimal player.

- Clickable progress bar
- ◀◀ / ▶ / ▶▶ buttons (seek ±10 s, play/pause)
- Position is saved

### Watch Progress

The **watched / in-progress / unwatched** status works for all media types, not just videos. The percentage is computed the same way (position / duration for video and audio; page / total for PDF and archives).

---

## Video Player

### Controls

| Element | Role |
|---------|------|
| **Progress bar** | Shows and controls position in the video |
| **⏮ / ⏭** | Seek back / forward — medium (30 s default, configurable) |
| **◀◀ / ▶▶** | Seek back / forward — short (10 s default, configurable) |
| **▶ / ⏸** | Play / Pause |
| **🔊** | Mute/unmute |
| **Volume** | Volume slider |
| **🐢 / 🐇** | Speed cycle: 0.5× → 1× → 1.5× → 2× (reset on each file open) |
| **⛶** | Fullscreen |

When you enter fullscreen, Hoard hides the controls automatically to maximize the video area.

- On desktop, move the mouse or use keyboard shortcuts to bring the controls back temporarily.
- On touch devices, only the existing bottom-centre tap zone near the controls should show or hide them.

### Video Metadata

When a file is playing, the codec, resolution, duration, and bitrate are shown below the filename (fetched from the server via `ffprobe`).

### Auto-resume

Position is saved automatically every 5 seconds. When you re-open a file, playback resumes from where you stopped.

### Smarter Native Playback Detection

Before falling back to server-side transcoding, Hoard now checks whether the current browser is likely able to play the original file natively.

- MP4/H.264/AAC remains the safest native baseline.
- For more variable formats such as HEVC, AV1, or WebM, Hoard probes browser support first when metadata is available.
- If native playback is not confirmed, Hoard switches to the transcoded stream automatically.

### Initial Sweep For New Videos

You can configure an **initial sweep** offset for videos that have **no saved progress yet**.

- A **global default** is available in **Settings → Player**.
- While playing a video, a single **folder start** action can save the **current playback position** as the default start for that folder.
- `0` means disabled.
- A folder override takes precedence over the global default.

This rule only applies to brand-new videos. Once a file has saved progress, Hoard always resumes from the real saved position instead.

### IN/OUT Markers (trim)

The `[IN` and `OUT]` buttons define a restricted playback zone (without modifying the file). The ✂ button triggers a physical file cut via ffmpeg.

### Auto-refresh File List

The file list refreshes automatically every 30 seconds when the tab is visible, the video is paused, and no search is active. This makes new files appear without a manual page reload.

### 180° Side-by-Side (VR) Videos

A VR 180° video holds two pictures side by side, one per eye, each stretched to cover half a horizon. Shown as-is it is unwatchable. The player's 🥽 button (or the **V** key) straightens the image and lets you look around.

Each press moves to the next state:

| State | What you see | When to use it |
|-------|--------------|----------------|
| Off | the raw file | ordinary video |
| **Flat** | a single straightened view you can pan | on a normal screen — computer, tablet |
| **Side by side** | two views, one per eye | with XR glasses in 3D mode, which split the two pictures themselves |

To look around: **drag your finger** on the image, **drag with the mouse**, or hold **R2** and push the **right stick** on the gamepad — without R2 that stick sets the volume. The mouse wheel zooms in and out. **Shift+V** re-centres the view.

While VR mode is on, dragging no longer seeks or changes the volume — it looks around. Seeking and volume stay available from the keyboard, the player buttons and the gamepad's left stick.

#### With XR glasses

Side-by-side mode goes fullscreen on its own: that is the only display that makes sense inside glasses. The player controls disappear while it is on — drawn once across a picture about to be split in two, they would land half in each eye and read as nothing anywhere. What you drive with, on the other hand, is written **once per eye** and so reads in both: the player's messages, the **Select** menu and the button map. Drive from the gamepad or the keyboard; leaving the mode brings everything back.

> **Unless the whole screen is already side by side** (see [The Whole Interface Side by Side](#the-whole-interface-side-by-side) below): each half then shows a whole picture, so the player bar, the volume bubble and the time readout stay, one set per eye. You keep your position in the file in front of you, which you do not otherwise.

Three settings, depending on what your glasses do:

- **Screen field of view** (**R2 + left stick up/down**, the mouse wheel, or **Settings → Player**). This is the setting that decides whether the depth is right, and despite appearances it is not a zoom: what belongs in it is the angle your glasses **actually** present to one eye. Too large and the world looks giant and distant, with anything approaching swelling enormously while your eyes insist it is far away; too small and the scene shrinks and the relief is overdone. XR glasses sit around **45°**, which is the default. Set it once on a 180° video by finding the point where the scene looks natural, then put that value in the settings. Mind the trade: the smaller the value, the truer the depth — and the less of the scene you see at once. The two go together and there is no separating them.
- **Stretched picture or not** (**B** key, **L2** on the pad, or the gamepad menu). **Hoard guesses it by default**, from the shape of the picture: to get 3D, glasses like the Viture Beast want an output twice as wide as usual — 3840×1080 — and on a picture that shape each half is already correctly proportioned, so nothing gets stretched. On an ordinary display each half is stretched back across the full width instead. Hoard announces what it guessed with a message as the mode comes on. If the picture still looks squashed or stretched twice over vertically, flip the setting — the effect is immediate, and your choice always wins over the guess. The shortcut cycles the three states: automatic, stretched, unstretched.
- **Convergence** (**R2 + left stick ←/→**, the D-pad for stepping, or the gamepad menu). This is the angle the two viewpoints are spread apart or brought together, which changes the distance your brain places the scene at. Leave it at zero, where the two views are exactly as the cameras took them — correct for a properly shot file. If one particular file tires your eyes, it was shot with a camera spacing that does not suit you, or mounted badly. The stick is proportional: a nudge trims, a full push crosses the range in a couple of seconds. **The tighter the field of view, the more you will need to correct** — the picture is more magnified, and so is any misalignment. The range goes to ±8°, wide enough that your eye decides rather than the bound. **The value is remembered for that file**, not globally: the strain comes from the shoot, and a badly mounted file must not contaminate the rest.

#### Adjusting the view from the pad

Everything is set by **holding R2**, without opening anything: the picture changes as you adjust, which is the only way to judge it.

| R2 held | Effect |
|---|---|
| **Left stick ↕** | Zoom |
| **Left stick ↔** | Convergence (proportional) |
| **D-pad ←/→** | Convergence, step by step |
| **Left stick click** | Reset the zoom |
| **Right stick click** | Recentre the view |
| **Right stick** | Look around |

While R2 is held the other buttons do nothing: the pad is driving the view and nothing else. **Release R2** and the sticks do exactly what they do on a flat screen, VR playback included: fine seeking, volume and playback speed (**R3**), each wherever your stick-swap setting puts them. On the keyboard, **Shift+V** resets both view and zoom at once.

#### Recognition and memory

A VR file is marked with a 🥽 in the list. Hoard guesses it two ways: from the name (studios almost always put `LR`, `3dh`, `180x180`, `VR180` or `SBS` in it), and from the picture's shape — two square eyes side by side are exactly twice as wide as they are tall. The name is readable from the list; the shape only once the file is open.

Recognising a file does **not** turn the mode on: the 🥽 button merely highlights. Opening a file to check something should not drop you into a headset view.

The mode you do choose, however, **is remembered for that file** and reapplied when you reopen it, including from another machine — a choice made on the laptop holds on the Deck. It works the other way too: if Hoard wrongly marks a file as VR, switch the mode off and it will not come back for that one.

Finally, VR mode is refused on a video played through transcoding: straightening a picture the server is already recomputing makes no sense, and the NAS could not afford it.

The defaults (field of view, look speed, stretched or not, convergence) live in **Settings → Player**.

> **What your machine has to manage.** These files are often very large (up to 8K) and encoded in HEVC. Hoard serves them untouched, without converting them: the device doing the watching has to decode them. If playback stutters or refuses to start, that is the limit you are hitting, not the VR mode.

---

## The Whole Interface Side by Side

XR glasses in 3D mode cut the picture in two **all the time**, not only while a video plays. An interface drawn once therefore sits astride the split and each eye gets half of it. Taking the glasses out of 3D costs ten seconds of black screen, and sometimes your settings.

This mode draws **the whole** application twice, once per eye: the PIN screen, the browser, the image and PDF viewers, video, settings and dialogs. Both eyes see **the same picture** — this is not 3D, and that is exactly what makes it readable rather than tiring.

### Turning it on and off

| How | Gesture |
|---|---|
| On the pad | **L1 + R1 + Select** — works everywhere, including on the PIN screen |
| On the keyboard | **Y** (or **Alt+Y** when the cursor sits in a text field) |
| From the **Select** menu | the *🥽 Side-by-side screen* line |
| From the settings | **Settings → XR glasses** |

**The same gesture turns it off.** Switching it on by mistake on an ordinary screen does not lock you into a screen you cannot read.

### One setting per device

Unlike everything else, this mode **does not follow you from one machine to another**: it is stored in the browser that uses it. The Deck with the glasses keeps it on; the laptop and the iPad never see it. It does survive a page reload, and it is in place before the PIN screen appears.

### With a video

An **ordinary video** is visible in both eyes with **one download and one decode**: the right eye gets a copy of the picture, not a second playback.

A **180° video** keeps all of its depth, and it is the one thing on screen that is not identical in both eyes — as it should be: that file holds two different pictures, one per eye, and that difference *is* the relief. Put the player in **side-by-side** (**V** key, or the **Select** menu) and each half of the screen gets the eye it is owed, whole.

One setting has nothing to act on in this mode: **stretched side-by-side picture or not** (**B** key). It exists to say whether your glasses stretch each half back to full width; here each eye already receives a whole picture, so there is nothing to stretch back. The line leaves the menu and the key says so.

### What it costs

There is twice as much interface to draw, so the machine works harder — measured on a 2 000-file folder, which is an extreme case. Moving the cursor stays instant there; changing the sort or the folder redraws the whole list and takes roughly twice as long as usual. On a folder of ordinary size it does not show.

---

## Touch Gestures

Gestures work directly on the video image.

> The first time you open a video on a touch device, a short help screen introduces the main gestures. Tap **Compris** (Got it) to dismiss it; it will not appear again.

### Single Tap

| Area | Action |
|------|--------|
| Narrow centre band (upper area) | Play / Pause |
| Narrow bottom-centre strip | Show / hide controls in fullscreen |

### Double Tap

| Area | Action |
|------|--------|
| Left edge (< 20 % width) | Seek back 30 s |
| Right edge — bottom third | Seek forward — medium (30 s default) |
| Right edge — middle third | Seek forward — long (60 s default) |
| Right edge — top third | Seek forward — extra-long (120 s default) |
| Centre | Fullscreen |

### Triple Tap

Toggle between **Fit** (full image visible) and **Fill** (cropped) display modes.

### Horizontal Swipe

Progressive seek through the video. **Speed depends on the vertical position of the finger**: a swipe at the top of the screen moves faster than at the bottom.

### Vertical Swipe

| Horizontal zone | Action |
|----------------|--------|
| Left edge (< 20 %) | Image brightness |
| Right edge (> 80 %) | Volume |

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `↑ / ↓` *(no media)* | Move cursor in the file list |
| `↑ / ↓` *(media playing)* | Volume +/− 10 % |
| `Enter` | Open the item under the cursor |
| `Space` | Play / Pause |
| `← / →` | Short seek (10 s default) |
| `Shift + ← / →` | Medium seek (30 s default) |
| `Ctrl + ← / →` | Long seek (60 s default) |
| `Alt + ← / →` | Extra-long seek (120 s default) |
| `F` | Fullscreen (in-window on desktop) |
| `Shift + F` | Real OS fullscreen (on desktop; otherwise use `F11`) |
| `Esc` | Exit fullscreen → close the player → go up one level in the tree |
| `M` | Mute / Unmute |
| `C` | Subtitles (cycle tracks / off) |
| `[ / ]` | Speed − / + (0.5× → 1× → 1.5× → 2×) |
| `A` | Cycle aspect ratio (Fit / Fill / …) |
| `W` | Toggle watched / unwatched |
| `PageDown / PageUp` | Next / previous video in folder |
| `I / O` | Set IN / OUT marker |
| `E` | Open Trim window |
| `D` | Open Move window |
| `R` | Rename (current file or selected entry) |
| `Delete` | Delete current file |
| `S` | Save folder start position |
| `?` | Show / hide keyboard help |

---

## Gamepad / Controller Support

Hoard supports game controllers via the browser's **Gamepad API** (Xbox, PlayStation DualSense, Switch Pro, Steam Deck, iPhone with a Bluetooth controller, etc.).

### Connecting

- Plug in or pair the controller, then press any button while Hoard is open.
- A « 🎮 Controller connected » toast confirms detection.
- **Steam Deck / Firefox**: Firefox only fires `gamepadconnected` after a button press. A toast « Press a button to activate the controller » appears if the device is detected but not yet active.

### Actions — Video Player

| Button | Base | + L1 | + R1 | + L1+R1 |
|--------|------|------|------|---------|
| **A** | Play / Pause | Subtitles | Move → Folder 1 | Jump to 0% |
| **B** | Close player | — | Move → Folder 2 | Delete the current file |
| **X** | Toggle watched | Aspect ratio | Move → Folder 3 | Move the current file |
| **Y** | Fullscreen | Mark segment IN | Confirm segment OUT | Open the Export dialog |
| **D-pad ←/→** | Seek medium | Seek long | Seek extra-long | — |
| **D-pad ↑/↓** | Volume ±10% | Prev/next file | Jump to 25%/75% | ↓: Jump to 100% |
| **Select** | Open the context menu | — | — | Side-by-side screen (XR glasses) |
| **Start** | Show button map | — | — | — |
| **L2** | Side-by-side layout: auto / stretched / not (VR mode) | — | — | — |
| **R2** (held) | VR layer: zoom, convergence, recentre — see above | — | — | — |
| **L3** (stick click) | Mute / Unmute | — | — | — |
| **R3** (stick click) | Cycle speed (0.5× → 1× → 1.5× → 2× → …) | — | — | — |
| **Left stick X** | Analog scrubbing | — | — | — |
| **Right stick Y** | Analog volume | — | — | — |

### Actions — File Browser (no video open)

| Button | Action |
|--------|--------|
| **D-pad ↑/↓** | Move cursor in the list |
| **Left stick Y** | Move cursor (analog) |
| **A** | Open the selected file or folder |
| **B** | Go up one level |
| **X** | Mark the selected entry watched / unwatched |
| **Select** | Open the **context menu** |
| **Start** | Show the button map |
| **L1+R1+B** | Delete the selected entry |
| **L1+R1+X** | Move the selected entry |

### Context Menu (Select)

Everything the sort bar and the row buttons offer is reachable from the pad through a single button: **Select** opens a menu listing what applies where you stand. **D-pad** to walk it, **A** to confirm, **B** to close.

The menu has two parts:

- **The entry under the cursor** (when one is set) — Open, Mark watched / unwatched, Rename, Tags, Quick folder, Move, Delete.
- **The current folder** — the five sort criteria and the direction, the tags present in the folder to filter by, New folder, Refresh, Search, Home screen, Downloads, Settings, Pad help.

Lines that do not apply to the entry are not shown: "Quick folder" only appears on a folder, "Mark watched" only on a media or a gallery.

**Select opens the menu during playback too**, with the player's own contents: folder start position, mark watched / unwatched, subtitles, fit/fill, playback speed, export segments (when there are any), rename, tags, move, delete, close the player, settings and pad help. It is the only pad path to the **folder start position**, which has no button of its own.

### Marking Watched Without Opening the File

From the list, **X** or the matching menu entry toggles a media's state without playing it — handy for a film watched elsewhere, or to reset a series you want to start over.

Marking **unwatched** also rewinds the saved position: an entry shown as unwatched must not resume mid-way. And reopening a file marked watched puts it back to "in progress" — actual playback has the last word.

### Modifier Layers (L1 / R1)

Hold **L1** or **R1** to access extra command layers. Holding both (L1+R1) activates a fourth layer. A small **corner badge** (e.g. « 🎮 L1 ») shows the active layer.

### Button Map Overlay

Press **Start** (or the « Show button map » button in Settings) to list every action, grouped by layer — the player, its three LB / RB / LB+RB layers, the browser and the sticks. Seek durations are the ones you configured, and quick folders appear under their real names.

The list flows into as many columns as the screen is wide: one on a phone, four on a desktop screen, six on a very wide display. **D-pad ↑/↓** scrolls, **B** or **Start** closes.

### Dialogs and the Pad

Every Hoard dialog (tags, rename, new folder, folder picker, download queue, PIN screen, login screen) can be driven from the pad: **D-pad** walks the fields and buttons, **A** activates the selected one, **B** closes the dialog. No screen asks you to reach back for the mouse.

### Controller Settings

In **Settings → 🎮 Controller**:

| Setting | Description |
|---------|-------------|
| **Controller enabled** | Enable / disable gamepad detection entirely |
| **Haptic feedback** | Short vibration on play/pause, seek, watched toggle (Chrome only) |
| **Dead zone** | Stick detection threshold (default 20%). Increase if sticks drift. |

---

## Signing In

When Hoard is configured with a username and password (`HOARD_AUTH_USER` /
`HOARD_AUTH_PASS`, see the installation guide), opening it shows a **login screen
in Hoard's own style** — no more grey browser dialog, which was barely steerable
with a gamepad on the Steam Deck and the Steam Frame.

- **Type it once.** The session lasts **30 days**, and the countdown restarts every
  time you use Hoard: in regular use you never retype anything. Each device has its
  own session.
- **On a gamepad**: **D-pad** moves between fields, **A** opens the keyboard on the
  selected field, then **A** on "Se connecter".
- **If the session expires** while you are browsing, the screen comes back and you
  carry on exactly where you were — no page reload, no lost playback position.
- **Sign every device out at once**: set the `HOARD_SECRET_KEY` variable and change
  its value. Every session, on every device, stops being valid immediately.

> **The PIN is a different thing.** It locks the screen of a session that is already
> open, on your own device; signing in decides whether the server answers you at all.
> The two stay independent.

> **`curl` still works** with `-u user:password`, as before — handy for scripts.

---

## Quick Folders (Pins)

**Quick folders** let you move a file to a frequently used folder in two taps.

- Click the 📌 icon next to a folder to pin / unpin it.
- Pinned folders appear in the move modal.

---

## Video Download

Hoard can download videos from the web using **yt-dlp** and save them directly to your NAS.

### Installing the Bookmarklet

1. Open **Settings** (⚙️ button in the header).
2. Scroll to the **Downloads** section.
3. **Drag** the "📥 Télécharger avec Hoard" link to your bookmarks bar.

> **The link contains a personal access token.** The bookmarklet runs on someone
> else's web page, so your browser never sends it your Hoard credentials — the
> token is what lets it reach Hoard. It can do two things and nothing else: start
> a download, and report that download's progress. It cannot browse, move or
> delete your files. Do not share the link. If you ever do by mistake, use
> **🔑 Nouveau jeton** in Settings: the old link stops working immediately, and
> you reinstall the bookmark by dragging the new link.

### Downloading a Video

**From any web page** — click the bookmarklet. It submits the download **in the background** and injects a live status dialog directly into the current page — no navigation, no opened tab. The dialog progresses through ⌛ "Analyse de l'URL…" → 📥 "Téléchargement… X%" → ✅ "Terminé !" (auto-closes after 4 s). If the queue is busy it shows ⏳ "En attente dans la file… — titre.mp4" until the slot is free. You can cancel the job from the dialog or from the Hoard download queue modal.

> **Sites with a restrictive CSP**: some sites (often ad-heavy streaming sites) block outgoing requests to a third-party domain like Hoard's via their `Content-Security-Policy`. In that case the bookmarklet shows ℹ️ "Hoard injoignable depuis cette page" and automatically opens Hoard in a new tab to finish the download there.

> **"Hoard : accès refusé"**: the bookmark was saved before the token was
> regenerated. Open Settings and drag the link again to replace it.

> **Smart video source detection**: if a `<video>` element is playing on the page, the bookmarklet captures its direct source URL instead of the page URL. This enables downloading from sites where yt-dlp has no dedicated extractor (Patreon, custom video players, BunnyCDN embeds, etc.). The modal shows a 🎬 hint when a direct source was detected. The original page URL is automatically sent as the `Referer` header so CDNs that verify the origin accept the request.

**From inside Hoard** — click the **📥** button in the header, paste a URL, and confirm.

**Filename hint**: the "Nom du fichier" field is pre-filled with the page title when using the bookmarklet. You can edit it freely before starting the download. If left empty, yt-dlp extracts the title automatically.

### Download Queue

All downloads are tracked in a central queue accessible from the **📥** button in the header:

- A **badge** on the button shows the number of active downloads.
  - Yellow badge = downloads in progress.
  - Green badge = all done (queue has items to dismiss).
- Click the button to open the **download queue modal**, which shows each download with its filename, progress bar, and status.
- Click **✕** next to a completed or failed download to dismiss it from the queue.
- Click **⏹** on a pending or running download to cancel it immediately. Any partial `.part` file left by yt-dlp is deleted automatically.
- **Sequential queue**: downloads run one at a time. New jobs wait in a "pending" state until the current download finishes, preventing bandwidth overload.
- **Downloads continue even if you close the tab**: they run as backend threads on the NAS. When you return to Hoard, the queue widget automatically reconnects to in-progress jobs.
- **Auto-refresh**: when a download completes, the file browser automatically refreshes if you are currently browsing the download folder.

### Download History

The **📥** modal has two parts:

- **In progress** — the current queue (progress, cancel, dismiss), which disappears once emptied.
- **History** — the **permanent** list of everything that was downloaded, stored in the database. Unlike the queue, it survives a NAS restart and never expires.

Each row shows the filename, the date, and the outcome:

| Status | Meaning |
|--------|---------|
| ✓ Done | The file made it. **Aller au fichier** opens its folder and highlights it. |
| ✗ Failed | The download failed. The error message is shown under the row. |
| ⊘ Cancelled | You stopped the download. |
| ⚠ Interrupted (restart) | Hoard stopped mid-download. The file did not make it — start it again. |

**Vider** clears the history (downloaded files are never touched); **✕** removes a single row.

History is kept **without any limit** by default — that is precisely what lets you find an old download again. To bound it: **Settings → Maintenance → Historique des téléchargements**, in days (`0` = unlimited).

### Retrying a Download

Every history row carries a **↻** button. It queues the same video again, with no need to find the original page.

Handy for **✗ Failed**, **⊘ Cancelled** and **⚠ Interrupted** entries: the file is not there, but its address was kept.

- On an entry that **succeeded**, Hoard asks for confirmation: retrying produces a **second** file next to the first, named `… (2)`.
- Hoard keeps the page the download came from and sends it along, without which many video hosts would reject the retry.
- Session cookies, however, are **not** kept — they are credentials. For a site requiring a login, the `cookies.txt` file set in Settings takes over.

### Where Files Land

The 📥 modal shows the destination twice: the relative name (e.g. `Downloads`) and the **full path** (e.g. `/media/Downloads`). When the folder does not exist yet, a "sera créé" note says so.

This matters because the destination folder is **created on demand**: a mistyped setting raises no error, it just creates a folder somewhere else where every download quietly piles up.

### Two Videos, Two Files

When the bookmarklet sends the page title as the filename, two different videos on the same site often carry the **same** title. Hoard now suffixes the name — `Ma video.mp4`, then `Ma video (2).mp4` — exactly like a browser does.

Without that, the downloader saw a file of the same name, **skipped the download silently**, and the video was lost while the UI displayed "Terminé". Should the case still arise (a download started with no filename), the entry now ends as a **failure** with a message explaining what to do, never as "done".

### Settings

| Setting | Description |
|---------|-------------|
| **Seek durations** | Four configurable levels in **Settings → Player**: short (default 10 s), medium (30 s), long (60 s), extra-long (120 s). Used by skip buttons, keyboard shortcuts, and double-taps. |
| **Enable transcoding** | When disabled, Hoard always serves the original file (`/api/file`) without calling the transcoder. Useful if your NAS is slow or your browser can play the format natively. |
| **Default initial sweep** | Start brand-new videos at N seconds instead of 0. Applies only when the file has no saved progress yet. `0` disables it globally. |
| **Home roots** | Named root folders shown on the home screen. Add or remove them in **Settings → Home roots**. |
| **Download folder** | Target folder, relative to the media root (default: `Downloads`). The **full path** is shown under the field, with a warning when the folder does not exist yet — it gets created on the first download. **📂 Parcourir…** picks it by browsing instead of typing. |
| **Cookies file path** | Absolute path to a Netscape `cookies.txt` file. Useful for sites that require authentication. |
| **Download history** | Days of download history kept (**Settings → Maintenance**). `0` = unlimited (default). |

### About Cookies

The bookmarklet forwards `document.cookie` from the source page. Note that **HttpOnly cookies are not accessible to JavaScript** — for sites where those are required (e.g. streaming platforms), export a `cookies.txt` file with a browser extension and specify its path in Settings.

---

## Maintenance

The **Settings → Maintenance** section covers everyday operational tasks.

### Log

Hoard records its events (downloads started, completed, failed, restart requests) in a file kept for **30 days**, on top of the container logs. The log can be read right here:

- Pick how many lines to show (100 / 500 / 2000).
- Filter by level: all, info, warnings, errors.
- **↻** refreshes, **Copier** puts the content on the clipboard (handy for pasting into an issue).

Lines are in chronological order, newest at the bottom.

### Restart Hoard

The **↻ Redémarrer Hoard** button restarts the application without going through Portainer or the NAS. Useful after a low-level setting change, or when something misbehaves.

- If a download is running, Hoard asks for an extra confirmation: restarting **permanently interrupts** it (it will show up as *Interrupted* in the history).
- Once triggered, the page waits for the server to come back and reloads on its own (up to 60 s). Past that, a message suggests checking the container.
- Hoard never restarts itself: the container does (`restart: unless-stopped` in `docker-compose.yml`). Outside a container the button **shuts the application down** — the confirmation message says so explicitly.

---

## Responsive Layout

| Screen width | Mode |
|-------------|------|
| > 700 px | Split view: list on the left, player on the right |
| ≤ 700 px | Full-screen list, player as overlay |

## Install As An App

On browsers that support web app install prompts, Hoard can now be installed as a standalone app instead of staying in a regular tab. On iPad and iPhone, use the browser's **Add to Home Screen** action to get the same standalone launch behavior.

The install shell only caches the app shell assets needed to reopen the interface faster. Hoard still expects a live connection to your NAS for API calls, browsing, and video playback.
