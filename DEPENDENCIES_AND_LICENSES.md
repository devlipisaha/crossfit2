# Dependencies and licenses
| Item | Use | License |
|---|---|---|
| Montserrat, Oswald, Anton | Fonts via Google Fonts (internet needed; self-host possible) | SIL Open Font License 1.1 |
| Node.js (runtime for server.js only) | Optional server | MIT-style (Node.js license) |
| jsdom | Tests only (devDependency) | MIT |
| Playwright + Pillow | Browser tests only | Apache-2.0 / HPND |
Runtime JavaScript libraries: none. The only external network dependency of the delivered app is the Google Fonts stylesheet (see DEPLOYMENT_GUIDE.md section 6). `server.js` uses only Node built-in modules (http, fs, path, crypto). Custom code: written for this project (rights: see HANDOVER_CHECKLIST.md). No third-party images are bundled; the default kettlebell logo is original SVG code. No secrets are included.
