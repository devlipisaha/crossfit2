# Client requirements audit (confirmed against the actual code)
| Earlier finding | Confirmed? |
|---|---|
| Timer used Date.now() | Fixed: monotonic `performance.now()`; Date.now() only translates another window's/server's start time |
| BroadcastChannel + localStorage sync | Confirmed; works only inside one browser profile |
| Browser-local scenes | Confirmed (localStorage) |
| Basic sequence parser | Confirmed (`2m + 30 + 1:00`, alternating work/rest) |
| Hash-based /overlay route | Confirmed (`#/overlay`); a layout bug (124 px offset at >=1672 px width) was found in real Chromium and fixed |
| Google Fonts dependency | Confirmed; self-hosting steps in DEPLOYMENT_GUIDE.md |
| No true cross-device control | Changed: optional `server.js` relays one authenticated session; tested between separate browser contexts (emulated phone), NOT on a real phone |
| No OBS/Zoom verification | Unchanged: BLOCKED, no OBS/Zoom/Streamlabs in the test environment |
## Defects found and fixed in this pass
1. Overlay shifted 124 px right at >=1672 px viewport width (wrapped in the dashboard container) — found by real-browser geometry test.
2. Left-zone title/tagline/date clipped with wide fallback fonts — text now auto-shrinks to fit.
3. Missing font fallbacks gave serif text in the dashboard when web fonts were unavailable.
4. Red diagonal accent crossed the left-zone title.
5. Unvalidated stored/imported/synced data — now repaired by `clean()`.
6. Logo files checked by header/parse, not only MIME type.
