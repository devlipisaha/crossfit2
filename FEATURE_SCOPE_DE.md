# Funktionsumfang (Festpreis maximal 200 €)

Stand der Umsetzung und Vertragsumfang sind getrennt zu lesen. Eine vorhandene Funktion ist nicht automatisch vertraglich vereinbart. Die Einordnung ist ein Vorschlag und muss vom Kunden bestätigt werden.

**Gesamtstatus: CONDITIONALLY READY — EXTERNAL VERIFICATION REQUIRED** (OBS-, Streamlabs- und Zoom-Tests stehen aus).

## 1. ENTHALTEN
Funktionen, die zum vereinbarten Kern gehören.

| Funktion | Umsetzungsstand | Hinweis |
|---|---|---|
| Live-Sync Dashboard zu Overlay im selben Browserprofil (auch file://) | PASS — TESTED | Kern; Chrome zu OBS-Browser nur über Servermodus |
| Countdown, Stopwatch, Intervals, Start/Pause/Resume/Reset | PASS — TESTED | Kern |
| Runden, Work/Rest-Wechsel, Time Cap | PASS — TESTED | Kern |
| Timer-Genauigkeit (monotone Uhr) | PASS — TESTED | Kern |
| Tastaturkürzel (Leertaste, R) | PASS — TESTED | Kern |
| Dashboard↔Overlay-Sync, gleiches Browserprofil | PASS — TESTED | Kern |
| Transparente /overlay-Seite | PASS — TESTED | Kern |
| 1920×1080 und 16:9-Skalierung, alle Zonen sichtbar | PASS — TESTED | Kern |
| Logo-Upload PNG/SVG, Ersetzen, Entfernen, Persistenz | PASS — TESTED | Kern |
| Event-Texte, WOD, Coach, Notizen, Zeilen hinzufügen/löschen/sortieren | PASS — TESTED | Kern |
| Theme, Schrift, Deckkraft, Sichtbarkeitsschalter | PASS — TESTED | Kern |
| Szenen: speichern/laden/umbenennen/duplizieren/löschen/zurücksetzen/Export/Import | PASS — TESTED | Kern |
| Browser-Source-URL kopieren / Test in neuem Tab | PASS — TESTED | Kern |
| OBS Studio Browser Source | BLOCKED — EXTERNAL TEST REQUIRED | Kern — Abnahme offen |
| Statisches Hosting / Server-Hosting | PASS — TESTED | Kern |
| Dokumentation, Lizenzliste, Quellcode | IMPLEMENTED — NOT VERIFIED | Kern |

## 2. EINGESCHRÄNKT ENTHALTEN
Funktionen mit Einschränkungen oder offener Bestätigung.

| Funktion | Umsetzungsstand | Hinweis |
|---|---|---|
| Live-Verbindung Chrome-Dashboard zu OBS über OBS-WebSocket (ohne Server/Datei) | IMPLEMENTED — NOT VERIFIED | Nur gegen Testattrappe geprüft; OBS-Test steht aus |
| OBS-Sync ohne Server über Statusdatei (Chrome-Dashboard schreibt state.js, OBS liest) | IMPLEMENTED — NOT VERIFIED | Mit simuliertem Dateidialog in Chromium getestet; echter Dateidialog und OBS nicht getestet; Servermodus als Alternative |
| Zeitsequenz-Parser (2m + 30 + 1:00) | PASS — TESTED | Basis |
| Sound-Signal bei Ende | IMPLEMENTED — NOT VERIFIED | Optional |
| Sync über Server (OBS/Handy/Dashboard getrennte Umgebungen) | PASS — TESTED | Optionaler Node-Server nötig |
| Responsives Dashboard (1920/1650/1440/1280/1024/768/390) | PASS — TESTED | Mobil: Layout nutzbar, nicht pixelgenau |
| Streamlabs Desktop Browser Source | BLOCKED — EXTERNAL TEST REQUIRED | Ungeprüft |
| Zoom über OBS Virtual Camera | BLOCKED — EXTERNAL TEST REQUIRED | Hängt von OBS ab |
| Schriften selbst hosten (DSGVO/Offline) | NOT IMPLEMENTED | Anleitung vorhanden |

## 3. SPÄTERE ERWEITERUNG
Nicht Teil des Festpreises; gesondert zu vereinbaren.

| Funktion | Umsetzungsstand | Hinweis |
|---|---|---|
| Pre-Start-Countdown | NOT IMPLEMENTED | Optional |
| Smartphone-/Tablet-Fernsteuerung | PARTIALLY WORKING | Umfang mit Kunde klären |
| Zonenposition/-breite, Schriftfarbe, Ausrichtung je Element | NOT IMPLEMENTED | Erweiterung |
| Animationen, Sponsor-Logos, Teilnehmernamen, Chat | NOT IMPLEMENTED | Erweiterung |

## Offene Umfangskonflikte (nicht vom Kunden freigegeben)
- Smartphone-Fernsteuerung: technisch vorhanden, benötigt aber einen laufenden Node-Server (Hosting, ggf. laufende Kosten) und wurde nur mit Browser-Emulation getestet. Kunde entscheidet: eingeschränkt enthalten oder kostenpflichtige Erweiterung.
- Zonenposition, Zonenbreite und Schrifteinstellungen je Element sind nicht umgesetzt.
- Die Abnahme von OBS, Streamlabs und Zoom erfordert Tests auf dem Rechner des Kunden.

## Vorgeschlagene Zahlungsmeilensteine
Vorschlag, keine bestätigte Vereinbarung, keine Terminzusagen.

| Meilenstein | Betrag | Abnahmekriterium |
|---|---|---|
| 1 Konzept und Architektur | 20 € | Architektur und Umfangsmatrix vom Kunden bestätigt |
| 2 Testbarer Prototyp | 70 € | Drei-Zonen-Overlay, Timer und Dashboard laufen im Browser |
| 3 Vereinbarte Erweiterungen | 70 € | Vom Kunden gewählte Punkte umgesetzt und geprüft |
| 4 Test, Dokumentation, Übergabe | 40 € | Quellcode, Doku, Testbericht; OBS-Test beim Kunden bestanden |
| Summe | 200 € | |
