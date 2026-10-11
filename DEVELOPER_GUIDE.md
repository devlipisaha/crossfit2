# Developer guide
All client code is in `index.html` (CSS, markup builders, script). `server.js` is an optional relay.
- State `S` (defaults `D`) is repaired by `clean()` on load, sync, import and scene load. localStorage keys `cfo_v1`, `cfo_scenes_v1`.
- Timer: `S.T={run,acc,t0}`; elapsed = acc + performance.now() - pa. `adopt()` converts a received wall-clock start into local monotonic time using `OFF` (server clock offset). Residual error ~ network latency.
- Sync: BroadcastChannel `cfo` + storage event + 500 ms poll of localStorage `CROSSFIT_OVERLAY_STATE` (old key `cfo_v1` is still read once for migration) (same browser profile only; `lastRaw` prevents echo loops); optional SSE/PUT via `server.js` (`?s=` session id, `&k=` key). Last write wins; echoes ignored by client id.
- Overlay: `ovHTML()` renders a 1672x460 design strip scaled by `fit()`; `.fit` elements shrink text to fit. Route `#/overlay`.
- Server: single in-memory session, constant-time key compare, 2 MB body limit, no TLS, no rate limit.
- Tests: `tests/regression.js`, `tests/advanced.js` (jsdom), `tests/browser_test.py` (Chromium).
- Future: multiple sessions, TLS, rate limiting, layout editor, pre-start countdown.
- State-file bridge: `fileWrite()` (dashboard, File System Access API) writes `window.__CFO={v,state}` to the user-linked `state.js`; the overlay on `file:` URLs injects `<script src=state.js?ts>` every 500 ms and adopts a changed `v`. Writes are atomic. Chromium-based dashboard only.
- Debug: `?debug=1` enables console logs (`Dashboard saved state`, `Overlay received state [channel]`) and an overlay status line (`got()`, `LS`, `DBG`).
- Timer broadcast: `tsnap(action)` (action, run, elapsed, remaining, mode, round, rounds, phase) is written into `state.js` and the debug log on every save. It is informational; the overlay renders from the shared `S.T` only and never keeps its own timer.
- OBS WebSocket bridge: `wsConnect()/wsSend()` speak obs-websocket v5 (Hello, SHA-256 auth, `CallVendorRequest` vendor `obs-browser`, request `emit_event`, event name `cfo-state`). The overlay listens for the `cfo-state` window event. State is re-sent every 2 s. `tests/mock_obs.js` is a test double (devDependency `ws`).
