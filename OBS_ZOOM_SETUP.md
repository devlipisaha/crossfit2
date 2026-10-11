# OBS Studio, Streamlabs and Zoom: setup and manual test procedure

**Status: NOT VERIFIED.** No real test with OBS, Streamlabs or Zoom has been performed. Fill in the result table at the end after testing. Do not report these integrations as working until every step passed.

## 0. Quick diagnosis from your screenshot
If the Chrome page at `…/index.html#/overlay` is correct but the OBS source shows CROSSFIT OPEN / 05:00 and only its live clock moves, OBS is receiving nothing. Chrome and OBS are separate programs; connect them with Method A (double-click `start-server.bat`, most reliable), Method C (Streaming > Connect to OBS) or Method B (state file). A Chrome tab that merely opens `#/overlay` does not feed OBS. Console messages `STATE SENT` (dashboard, on every change) and `STATE RECEIVED [channel]` (overlay, on arrival) appear with `?debug=1`; in OBS they are only visible through the source's *Interact* window or the debug status line.

## 1. How synchronization works (read this first)
Chrome and OBS's built-in browser are different programs with separate storage. BroadcastChannel, localStorage events, storage polling and `postMessage` all stay inside one browser profile (or one window tree), so none of them can carry data from Chrome into OBS. This is a browser security rule. The only things both programs can reach are a **file on disk** or a **network connection**. The project therefore offers three methods (C needs the least setup):

- **Method C, live link through OBS's own WebSocket server (no files, no Node server; NOT verified in OBS).** OBS 28+ contains a WebSocket server. The dashboard connects to it from Chrome and asks OBS to hand the state to every browser source (obs-browser `emit_event`); the overlay receives it as an event. Setup:
  1. In OBS open *Tools > WebSocket Server Settings*, tick *Enable WebSocket server*, press *Show Connect Info* and note port (default 4455) and password.
  2. Add the Browser Source: URL `file:///C:/overlay/index.html?debug=1#/overlay`, width 1920, height 1080.
  3. In Chrome open the dashboard, go to *Streaming*, keep the address `ws://127.0.0.1:4455`, enter the password and press **Connect to OBS**. The label turns green: "Connected to OBS".
  4. Change the Event Title and press Start: the OBS source follows. The state is re-sent every 2 seconds, so a refreshed source recovers by itself.
  Limits: the dashboard tab must stay open and connected (reconnect after a browser restart); a wrong password shows "Wrong OBS WebSocket password"; if the label says it cannot reach OBS, the server is disabled or the port differs. Tested only against a protocol test double, not against real OBS; the debug line shows `last receive: obs-websocket` when it works.
- **Method A, server mode (recommended, most robust).** `node server.js` relays the state over the network. Chrome, phones and OBS can all connect.
- **Method B, state-file bridge (no server, local files only).** The dashboard in Chrome or Edge writes the current state into `state.js` next to `index.html`; the overlay in OBS re-reads that file every 500 ms. Setup:
  1. Keep `index.html` and `state.js` together in one folder, for example `C:\overlay\`.
  2. Open `file:///C:/overlay/index.html` in Chrome or Edge.
  3. Go to the **Streaming** tab, click **Link state file (local OBS sync)**, pick the `state.js` file in the same folder and confirm the overwrite/edit permission. The label next to the button shows the time of the last write. (Browsers that cannot write files, such as Firefox, cannot use this method.)
  4. In OBS, add a Browser Source with the URL field set to `file:///C:/overlay/index.html#/overlay` (use the URL field, not the "Local file" checkbox, because the `#/overlay` part is needed), width 1920, height 1080.
  5. Keep the Chrome dashboard window open. Change the Event Title; OBS should update within about one second without refreshing.
  Limits: step 3 must be repeated after every browser restart; dashboard and OBS must run on the same computer (same folder); the dashboard tab must stay open. **Not verified in OBS.** If OBS does not update, use Method A.

Control URL (`k=` key, Method A) = full control, keep it private. Overlay URL (`?s=...#/overlay`) = read-only.

## 1b. Debugging a source that does not update
Add `?debug=1` before the `#` in the OBS URL, for example `file:///C:/overlay/index.html?debug=1#/overlay`. The overlay then shows a green status line in its bottom-left corner:
`CFO debug | storage: has state/empty | last receive: <channel> <time> | count N | title: ...`
- `last receive: none` and `count 0` after you changed something in the dashboard: no channel reaches this OBS source. Chrome and OBS do not share storage, so the dashboard must either be linked to `state.js` (Method B) or use server mode (Method A). Typing in a Chrome dashboard alone can never reach OBS.
- `last receive: state.js` rising count: the bridge works.
- `state.js not loadable` in the line: the file is missing next to `index.html` or OBS blocks local file loading; use Method A.
- `last receive: storage-poll` or `storage-event`: the dashboard runs in the same browser as the source (for example as an OBS Custom Browser Dock) and sync works.
Also open the dashboard with `?debug=1`; the browser console (F12) then logs "Dashboard saved state" on every change and "Overlay received state [channel]" on receipt. The state is stored under the fixed key `CROSSFIT_OVERLAY_STATE`.
Send the status line text if the source still does not update; it identifies the failing step.

## 1c. Symptom: the live clock runs but the workout timer stays at 05:00
The LIVE clock is read from the computer's own clock, so it always runs. The workout timer is not an independent timer: the overlay only displays the shared timer state (running flag, accumulated time, start time, mode, rounds) that the dashboard saves. If the overlay shows 05:00, it has received no state at all, which is the same cause as text edits not arriving (section 1). With `?debug=1` the overlay status line shows `timer: STOP countdown el=0.0` and `last receive: none`. Fix it with Method A or Method B in section 1, then Start in the dashboard: the line must change to `timer: RUN ... el=` with a rising value. Every timer action is also written into `state.js` as `timer:{action:START|PAUSE|RESUME|RESET, elapsed, remaining, mode, round, rounds, phase}` and logged in debug mode.

## 2. OBS Studio setup (Method A, server mode; for Method B follow the steps in section 1)
1. Start the server: `SESSION_ID=mygym SESSION_KEY=long-secret node server.js`.
2. Open OBS Studio and select your scene.
3. In *Sources* click **+**, choose **Browser**, name it "CrossFit Overlay".
4. URL: `http://localhost:8080/?s=mygym#/overlay` (use the server's address if it runs elsewhere).
5. Width **1920**, Height **1080**.
6. Leave *Custom CSS* empty; the overlay is already transparent. Do not tick "Shutdown source when not visible".
7. Move the Browser Source **above** the camera/video source in the source list.
8. Open the Control URL (`http://localhost:8080/?s=mygym&k=long-secret`) in a normal browser.
9. Start the timer in the dashboard and watch the OBS preview.

## 3. Manual test checklist (OBS)
Run it once for Method A and, if you want to use it, once for Method B (state-file bridge: link the file first; step 8 means refreshing the OBS source and checking that it still shows the current data; skip step 10).
Mark each step PASS or FAIL.
1. Overlay appears above the camera with a see-through background (no black or white box).
2. All three zones are fully visible, nothing is cut off at 1920×1080.
3. Start: the timer counts down in OBS within about a second.
4. Pause, Resume and Reset are mirrored in OBS.
5. Change the event title, subtitle, location and date: OBS updates.
6. Edit, add, delete and reorder workout rows; change coach and notes: OBS updates.
7. Change theme colour, opacity and hide/show zones: OBS updates.
8. In OBS right-click the source > *Refresh*: the overlay returns with the current timer and texts.
9. Let a 10-minute countdown run; compare the OBS timer with a stopwatch at the end (expected difference under 1 s).
10. Open the Control URL on a phone (same Wi-Fi, use the computer's IP address): start and pause from the phone; OBS follows.
11. Start a 30-second test recording and check the recorded video shows the overlay correctly.

## 4. Streamlabs Desktop
Add Source > **Browser Source** with the same URL, width 1920 and height 1080, and run the same checklist. Differences from OBS are not known; record any you find.

## 5. Zoom via OBS Virtual Camera
Chain: overlay page > OBS Browser Source > OBS scene > OBS Virtual Camera > Zoom. Zoom cannot display a transparent HTML overlay itself.
1. In OBS click **Start Virtual Camera**.
2. In Zoom open *Settings > Video* and set *Camera* to **OBS Virtual Camera**.
3. Check in the Zoom preview: overlay visible, scaled correctly, timer digits and workout text readable, timer updates live.
4. Join a test meeting with a second device and confirm the other side sees the same.

## 6. Troubleshooting
- Blank or frozen overlay: wrong session ID in the URL, or the server stopped.
- Overlay does not update behind a proxy: disable response buffering for `/api/events`.
- "Remote control rejected": wrong key in the Control URL.
- Slight timer offsets between devices (tens of milliseconds) are normal: each device has its own clock.

## 7. Result table (to be completed by the tester)
| Integration | Tester | Date | Result (PASS/FAIL) | Notes |
|---|---|---|---|---|
| OBS Studio | | | | |
| Streamlabs Desktop | | | | |
| Zoom via OBS Virtual Camera | | | | |
| Phone remote control (real device) | | | | |
