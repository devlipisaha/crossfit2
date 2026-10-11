# Deployment guide

Nothing in this guide has been tested on a second, external server. Everything below was verified only on a local machine; follow the check list in section 8 after deploying.

## 1. What you are deploying
- `index.html`: the complete application (dashboard at `/`, overlay at `/#/overlay`). Static file, no build step.
- `server.js`: optional Node.js server (built-in modules only, no packages to install). It serves `index.html` and relays one shared session so that OBS, phones and the dashboard stay in sync. Without it, sync works only inside one browser profile.

## 2. Requirements
| Mode | Needs |
|---|---|
| Static (`index.html` only) | Any web server (HTTPS recommended). Not `file://`. |
| Server mode | Node.js 18 or newer, a machine that stays on during streams, and inbound access on the chosen port (or an HTTPS reverse proxy). |
| Internet access | Visitors' browsers load fonts from Google Fonts unless you self-host them (section 6). |
No database, no developer account, no API keys, no licence fees.

## 3. Configuration (environment variables, all optional)
| Variable | Default | Meaning |
|---|---|---|
| `PORT` | 8080 | Listening port |
| `HOST` | 0.0.0.0 | Bind address (`127.0.0.1` if a reverse proxy runs on the same machine) |
| `SESSION_ID` | random at start | Public session name used in the Overlay URL |
| `SESSION_KEY` | random at start | Secret for control; anyone with it can control the overlay. Use a long random value |
If unset, the server creates the values once and keeps them in `.session.json` (private; delete the file to rotate the key). Setting both variables overrides the file.

## 4. Local run
`SESSION_ID=mygym SESSION_KEY=long-secret node server.js` prints the Control URL and the Overlay URL.

## 5. Hosting
**Static:** copy `index.html` to any static host. Open `https://your-host/` and `https://your-host/#/overlay`.
**Server on a VPS or any Node host:**
1. Copy `index.html` and `server.js` to the server (the other files are optional).
2. Start with `SESSION_ID=... SESSION_KEY=... node server.js` (use your process manager of choice to keep it running and restart it after reboots).
3. Put an HTTPS reverse proxy in front (for example Caddy or nginx). For the path `/api/events` disable response buffering and allow long-lived connections, otherwise live updates stall.
4. Use the HTTPS addresses in OBS and on phones.
The server keeps one session in memory. When it restarts, the next dashboard that opens the Control URL pushes its saved settings again.

## 6. Self-hosting the fonts (privacy / offline use)
1. Download Montserrat, Oswald and Anton (SIL Open Font License) as woff2 files from the font projects.
2. Put them in a `fonts/` folder next to `index.html`.
3. In `index.html` remove the `<link>` to fonts.googleapis.com and add matching `@font-face` rules in the `<style>` block.
4. Reload and confirm in the browser's network panel that no request goes to Google.
Without these steps the app still works but falls back to Arial, and some text spacing differs.

## 7. Backup, restore and migration
Settings live in each browser's storage per web address, and are not shared between devices.
- **Backup:** Dashboard > Scenes > *Export*, copy the JSON into a file.
- **Restore or migrate to a new address:** open the dashboard at the new address > Scenes > paste the JSON > *Import*.
- In server mode the current state is also held in the server's memory only.
To move the project to another server, copy the folder, set the same `SESSION_ID`/`SESSION_KEY`, start it, and update the OBS Browser Source URL.

## 8. Post-deployment check list
1. Dashboard loads at `/`, overlay at `/#/overlay` shows the three zones on a transparent background.
2. Start the timer in the Control URL; the Overlay URL follows within about a second.
3. Open the Overlay URL without the key and confirm it cannot change anything.
4. Run the OBS check list in OBS_ZOOM_SETUP.md.

## 9. Cost overview (estimates, not part of the fixed development fee)
Static hosting: free to low cost. Node VPS for server mode: small monthly fee set by the provider. Domain and TLS certificate: optional, TLS can be free. No recurring costs are required by the software itself.

## 10. Security notes
Keep the Control URL private (it contains the key and appears in browser history). The server has no rate limiting and no built-in HTTPS. One session only. Do not expose it publicly without the HTTPS proxy.
