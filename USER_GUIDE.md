# User guide
- Live Control: edit logo, event text, timer, workout, style; the overlay updates live. Space = start/pause, R = reset.
- Modes: Countdown (time cap), Stopwatch, Intervals (work/rest x rounds). Timer Settings: sequence `2m + 30 + 1:00` = 120 s, 30 s, 60 s alternating work/rest; plain numbers = seconds; `m:ss` also allowed.
- Logo: PNG/SVG up to 500 KB; unsafe SVG or fake images are rejected with a message.
- Scenes: save, load, rename (type new name first), duplicate, delete, export/import JSON, restore default (Overlay Settings).
- Backup: Scenes > Export; restore with Import.
- Remote control: open the Control URL printed by `node server.js` on a phone/tablet (same network or hosted). Anyone with that link can control the overlay: keep it private.
- Local OBS without a server: Streaming tab > Link state file (see OBS_ZOOM_SETUP.md, Method B).
