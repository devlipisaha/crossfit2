# CrossFit Streaming Overlay & Control Dashboard

A browser-based streaming overlay (timer, event branding, workout board) with a control dashboard. Plain HTML/CSS/JavaScript: no build step, no framework, no accounts.

**Handover status: CONDITIONALLY READY — EXTERNAL VERIFICATION REQUIRED** (OBS, Streamlabs and Zoom have not been tested; see TEST_REPORT.md).

## Contents
| File | Purpose |
|---|---|
| `index.html` | The whole application (dashboard at `/`, overlay at `/#/overlay`) |
| `state.js` | Placeholder file written by the dashboard for the no-server OBS bridge (Option B) |
| `server.js` | Optional Node.js server: serves the app and syncs one session across devices |
| `tests/` | Automated tests and screenshots |
| `package.json`, `package-lock.json` | Node project files (test dependency only) |
| `*.md`, `CrossFit_Overlay_Audit_and_Scope.xlsx` | Documentation and scope/test spreadsheet |

## Requirements
- A current Chrome, Edge or Firefox-based browser (tested: Chromium only).
- For server mode: Node.js 18 or newer (no packages to install to run it).
- For tests only: `npm install`; for browser tests also Python 3 with `pip install -r tests/requirements.txt` and `playwright install chromium`.

## Quick start for OBS on Windows (most reliable)
1. Install Node.js (LTS) from nodejs.org once.
2. Double-click `start-server.bat` and keep the window open. It prints a **Control URL** and an **Overlay URL**; they stay the same after restarts (stored in `.session.json`, keep that file private).
3. Open the Control URL in Chrome. In OBS use the Overlay URL as the Browser Source (1920 x 1080).
Every dashboard change now reaches OBS. Without Node.js, use *Streaming > Connect to OBS* (OBS WebSocket) or *Link state file*; see OBS_ZOOM_SETUP.md.

## Installation and usage
**Option A, server mode (recommended for OBS and phones)**
1. Open a terminal in this folder and run `node server.js`.
2. The terminal prints a **Control URL** and an **Overlay URL**. Open the Control URL in your browser (or on a phone in the same network, replacing `localhost` with the computer's address).
3. Use the Overlay URL as the OBS Browser Source (see OBS_ZOOM_SETUP.md).
4. Set your own `SESSION_ID` and `SESSION_KEY` environment variables for stable links, for example `SESSION_ID=mygym SESSION_KEY=long-secret node server.js`. Without them, new random values are created at every start.

**Option B, local files only (no server)**
For OBS, the simplest no-file route is *Streaming > Connect to OBS* (needs OBS's built-in WebSocket server enabled; see OBS_ZOOM_SETUP.md, Method C; not verified in OBS).
Open `index.html` from disk. Windows in the same browser profile sync automatically. To feed OBS's built-in browser (a different program), open the dashboard in Chrome or Edge, go to *Streaming* > **Link state file** and pick `state.js` in the same folder; the overlay in OBS (`file:///.../index.html#/overlay`) then re-reads it every 500 ms. Exact steps: OBS_ZOOM_SETUP.md section 1. Not verified in OBS. Server mode (Option A) is more robust.

**Dashboard quick guide:** edit logo, event text, timer, workout and style on *Live Control*; the overlay updates immediately. Space starts/pauses the timer, R resets. Details: USER_GUIDE.md.

## Debug mode
Add `?debug=1` to the dashboard or overlay URL (before the `#`): events are logged to the browser console and the overlay shows a status line with the last sync channel. See OBS_ZOOM_SETUP.md section 1b. Settings are stored in localStorage under the key `CROSSFIT_OVERLAY_STATE`.

## Running the tests
- `npm install` then `npm test` (simulated browser, 74 checks (39 + 35))
- `python3 tests/browser_test.py` (real Chromium, 102 checks; starts its own server on port 8099)

## Documentation index
USER_GUIDE.md, OBS_ZOOM_SETUP.md, DEPLOYMENT_GUIDE.md, DEVELOPER_GUIDE.md, TEST_REPORT.md, FEATURE_SCOPE_DE.md, CLIENT_REQUIREMENTS_AUDIT.md, DEPENDENCIES_AND_LICENSES.md, HANDOVER_CHECKLIST.md.

## Known limitations (short)
Fonts load from Google Fonts (internet required; self-hosting steps in DEPLOYMENT_GUIDE.md). Server mode has one session, no built-in HTTPS, and anyone with the Control URL can control the overlay. Not built: pre-start countdown, zone positioning, per-element fonts, animations, sponsor logos, participant names, chat.
