# Test report

**Verdict: CONDITIONALLY READY — EXTERNAL VERIFICATION REQUIRED**

## Summary of what was actually run
| Suite | Environment | Result |
|---|---|---|
| `tests/regression.js` | jsdom (simulated browser) | 39 of 39 passed |
| `tests/advanced.js` | jsdom (simulated browser) | 35 of 35 passed |
| `tests/browser_test.py` | Real headless Chromium (Playwright), local server | 102 of 102 passed |
The first Chromium run found 3 real defects (overlay offset at wide viewports, clipped text, wrong timer-test measurement). Defects were fixed and all suites were rerun.

## Analysis of the OBS screenshot (12 Oct 2026)
The Chrome window shows `…/index.html#/overlay` with title ABC TEST and a running timer (03:56): windows of the same Chrome profile do synchronize. OBS 32.2.2 shows the same file with the defaults CROSSFIT OPEN, 05:00, round 2/5, work 01:00, rest 00:30, while its live clock (a local clock) runs. OBS therefore received no state at all: a different program, hence a different browser profile. The overlay is not using hardcoded text; those are its default values when nothing has been received. The fix is a transport that crosses programs (Methods A, B or C in OBS_ZOOM_SETUP.md). The warning added to the dashboard now says so on the first change.

## What these tests do NOT cover
No OBS, Streamlabs or Zoom test (the request to test the OBS Browser Source specifically could not be fulfilled: OBS is not available here). No real smartphone. No Firefox or Safari. No run longer than about 10 seconds. Screenshots were rendered with fallback fonts because Google Fonts was unreachable. A debug status line was added so the failing OBS step can be identified. Automated browser tests are not a substitute for real OBS or Zoom testing.

## A. Verified (PASS — TESTED)
| Feature | Status | Test method | Result | Known limitations | Remaining action |
|---|---|---|---|---|---|
| Dashboard warns that OBS cannot see changes when no OBS link, state file or server is active; separate-profile overlay stays at defaults (CROSSFIT OPEN, 05:00) as in the user's screenshot | PASS — TESTED | Real Chromium, two separate contexts | Warning shown after the first change; overlay unchanged without a link | Reproduces the symptom; says nothing about OBS itself | Connect via Method A, B or C and re-test in OBS |
| Server keeps the same Control/Overlay URLs after a restart | PASS — TESTED | Node process started twice | Identical URLs | Stored in `.session.json` | — |
| OBS WebSocket bridge: login with password, wrong-password message, emit_event requests (title ABC TEST, START, PAUSE, RESET), heartbeat, STATE SENT / STATE RECEIVED logs | PASS — TESTED (against a protocol test double) | Real Chromium plus `tests/mock_obs.js` (obs-websocket v5 handshake); OBS's delivery into the browser source was simulated with a CustomEvent | All 11 checks pass | Not real OBS: whether OBS 32 delivers `emit_event` as a window event is unverified | Test in OBS with `?debug=1` |
| Timer actions START / PAUSE / RESUME / RESET broadcast with elapsed, mode, rounds; overlay in a separate browser context follows (state-file bridge, stubbed file picker) | PASS — TESTED | Real Chromium, state.js content and overlay timer state checked | START, PAUSE, RESUME and RESET all reach the overlay | Not run in OBS; overlay has no timer of its own | Verify in OBS with `?debug=1` |
| Fixed storage key `CROSSFIT_OVERLAY_STATE`, 500 ms poll, debug mode (console logs and overlay status line); title CROSSFIT OPEN to TEST 123 in the same browser profile | PASS — TESTED | Real Chromium, two pages on file:// | Logs and status line appear only in debug mode; title updates without refresh | Same browser profile only; says nothing about OBS | Run the debug line check inside OBS |
| State-file bridge: dashboard writes state.js, overlay in a separate browser context re-reads it (title TEST to CROSSFIT CHAMPIONSHIP without refresh; text, WOD, timer settings, logo add/remove, show/hide, start/pause/reset, overlay refresh) | PASS — TESTED (with mocked file picker) | Real Chromium, two separate contexts on file://, disk write performed by test host | All 9 checks pass; update visible in about 1 s | The native file picker was replaced by a test stub; OBS not used | Test with the real picker in Chrome and the real OBS Browser Source |
| Local file:// mode: dashboard to overlay sync (same profile): text, WOD, exercise list, timer settings/mode/rounds, start, logo add/remove, show/hide, overlay refresh | PASS — TESTED | Real Chromium, two pages on file:// | All fields reach the overlay; refresh restores data | Same browser profile only | — |
| Storage-poll fallback (no BroadcastChannel, no storage events) | PASS — TESTED | Real Chromium, features disabled by script | Text and running timer sync within ~1 s | Same profile only | — |
| Different browser profile (Chrome vs OBS-style) in local mode | PASS — TESTED (limitation confirmed) | Real Chromium, separate contexts | Does NOT sync, as expected | Cannot be fixed in a web page; use server mode | — |
| Countdown, Stopwatch, Intervals, Start/Pause/Resume/Reset | PASS — TESTED | jsdom regression; Chromium (Playwright) | All pass | — | — |
| Runden, Work/Rest-Wechsel, Time Cap | PASS — TESTED | jsdom, fixed time points | Phasen/Runden korrekt, Ende erkannt | Work/Rest-Panel zeigt Soll-Werte, keine Live-Hervorhebung | — |
| Timer-Genauigkeit (monotone Uhr) | PASS — TESTED | Chromium (Playwright): 8 s Lauf, davon 8 s im Hintergrund-Tab; jsdom: Systemuhr-Sprung | Abweichung < 150 ms | Nur 8-s-Läufe automatisiert; Langzeitlauf (10+ min) nicht gemessen | Langzeittest in OBS |
| Zeitsequenz-Parser (2m + 30 + 1:00) | PASS — TESTED | jsdom: 9 Grenzfälle | Gültige Formen ok; 0, 1:60, negativ, h:mm:ss, leere Segmente abgelehnt | Wechselt nur Work/Rest ab | — |
| Tastaturkürzel (Leertaste, R) | PASS — TESTED | jsdom | Pass | — | — |
| Dashboard↔Overlay-Sync, gleiches Browserprofil | PASS — TESTED | Chromium (Playwright): zwei Seiten, BroadcastChannel; jsdom | Start/Pause/Resume/Reset/Text/Theme/Sichtbarkeit/Szene | Nicht für OBS-Browserquelle (anderes Profil) | — |
| Sync über Server (OBS/Handy/Dashboard getrennte Umgebungen) | PASS — TESTED | Chromium (Playwright): 3 getrennte Browser-Kontexte, inkl. Mobil-Emulation; HTTP-403-Tests | Start/Pause/Resume/Reset/Text/Theme/Sichtbarkeit; Overlay-Refresh stellt Zustand wieder her; Overlay-URL ohne Schlüssel kann nicht steuern | Nur emuliert, kein echtes Smartphone/OBS; eine Sitzung; Schlüssel in URL; kein TLS im Server | Test mit echtem Handy und HTTPS-Hosting |
| Transparente /overlay-Seite | PASS — TESTED | Chromium (Playwright): Computed Styles, Screenshot-Alpha=0 bei 1920×1080, 1600×900, 1280×720 | HTML/BODY transparent, kein Scrollbalken, keine Dashboard-Elemente | Transparenz in OBS selbst nicht gesehen | OBS-Test |
| 1920×1080 und 16:9-Skalierung, alle Zonen sichtbar | PASS — TESTED | Chromium (Playwright): Bounding-Boxes (Fehler gefunden: 124 px Versatz, behoben) | Alle Zonen im Viewport bei 3 Auflösungen | — | — |
| Responsives Dashboard (1920/1650/1440/1280/1024/768/390) | PASS — TESTED | Chromium (Playwright): Spaltenzahl, Überlauf, Vorschau, Timer-Zentrierung; Screenshots | 5 Spalten ab 1440, 3 bis 1024, 1 darunter; kein Überlauf | Screenshots mit Ersatzschriften (Google Fonts offline) | Sichtprüfung mit echten Schriften |
| Logo-Upload PNG/SVG, Ersetzen, Entfernen, Persistenz | PASS — TESTED | Chromium (Playwright): echter Dateiupload; jsdom | PNG/SVG ok; Skripte, on*-Attribute, externe Refs, foreignObject, falsches PNG, >500 KB abgelehnt | Dateiinhalt (PNG-Header, SVG-Parser) geprüft; Sanitizer ist Sperrliste | — |
| Event-Texte, WOD, Coach, Notizen, Zeilen hinzufügen/löschen/sortieren | PASS — TESTED | jsdom | Pass | — | — |
| Theme, Schrift, Deckkraft, Sichtbarkeitsschalter | PASS — TESTED | jsdom | Pass | — | — |
| Szenen: speichern/laden/umbenennen/duplizieren/löschen/zurücksetzen/Export/Import | PASS — TESTED | jsdom, fehlerhafte JSON-Fälle; Persistenz Chromium (Playwright) | Pass; fehlerhafte Importe repariert/abgelehnt | Nur lokaler Browserspeicher | — |
| Browser-Source-URL kopieren / Test in neuem Tab | PASS — TESTED | Chromium (Playwright) | URL ohne Steuerschlüssel in Zwischenablage; neuer Tab öffnet Overlay | Chromium mit gewährter Clipboard-Berechtigung | — |
| Statisches Hosting / Server-Hosting | PASS — TESTED | Chromium (Playwright): Auslieferung über server.js | index.html lädt und funktioniert über HTTP | Nur lokal geprüft, nicht auf zweitem Server | Deployment testen |

## B. Partially working
| Feature | Status | Test method | Result | Known limitations | Remaining action |
|---|---|---|---|---|---|
| Smartphone-/Tablet-Fernsteuerung | PARTIALLY WORKING | Chromium (Playwright) Mobil-Emulation 390×844 | Steuerung über Server-Sitzung funktioniert | Server-Hosting nötig (Kosten); nicht auf echtem Gerät getestet | Echtgerätetest, Hosting festlegen |

## C. Implemented, not verified
| Feature | Status | Test method | Result | Known limitations | Remaining action |
|---|---|---|---|---|---|
| State-file bridge with the real file picker and the real OBS Browser Source | IMPLEMENTED — NOT VERIFIED | Not run (no OBS, no interactive picker) | — | Depends on OBS allowing a file:// page to load another local script | Test in OBS (OBS_ZOOM_SETUP.md, Method B) |
| `postMessage` between dashboard and overlay | NOT APPLICABLE | — | — | Cannot cross from Chrome into OBS's separate browser process; not added | — |
| Sound-Signal bei Ende | IMPLEMENTED — NOT VERIFIED | Code-Review | — | Web Audio nicht automatisiert hörbar getestet | Manuell anhören |
| Dokumentation, Lizenzliste, Quellcode | IMPLEMENTED — NOT VERIFIED | Mit diesem Paket geliefert | — | Vom Kunden noch nicht geprüft | Kundenprüfung |

## D. Not implemented
| Feature | Status | Test method | Result | Known limitations | Remaining action |
|---|---|---|---|---|---|
| Pre-Start-Countdown | NOT IMPLEMENTED | — | — | Nicht gebaut | Optionale Erweiterung |
| Zonenposition/-breite, Schriftfarbe, Ausrichtung je Element | NOT IMPLEMENTED | — | — | Nicht gebaut | — |
| Schriften selbst hosten (DSGVO/Offline) | NOT IMPLEMENTED | — | — | Schriften kommen von Google Fonts (Internet nötig) | Schriftdateien herunterladen, @font-face einbinden |
| Animationen, Sponsor-Logos, Teilnehmernamen, Chat | NOT IMPLEMENTED | — | — | — | — |

## E. Blocked: external test required
| Feature | Status | Test method | Result | Known limitations | Remaining action |
|---|---|---|---|---|---|
| OBS Studio Browser Source | BLOCKED — EXTERNAL TEST REQUIRED | — | — | OBS nicht verfügbar | Test nach OBS_ZOOM_SETUP.md |
| Streamlabs Desktop Browser Source | BLOCKED — EXTERNAL TEST REQUIRED | — | — | Nicht verfügbar | Gleicher Test wie OBS |
| Zoom über OBS Virtual Camera | BLOCKED — EXTERNAL TEST REQUIRED | — | — | Nicht verfügbar | Zoom-Test |

Note: one timing check in `tests/advanced.js` (4 s run within 150 ms) failed once while the machine was busy (4.16 s vs 4.00 s) and passed on three reruns; treat it as load-sensitive.

## Remaining actions before client acceptance
1. Run the OBS_ZOOM_SETUP.md checklist for OBS, Streamlabs and Zoom and record results.
2. Test remote control on a real phone or tablet.
3. Check the layout once with the web fonts loaded.
4. Client confirms the scope conflicts listed in FEATURE_SCOPE_DE.md.
