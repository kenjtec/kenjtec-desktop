# KENJTEC Desktop-Client

*English: This is the KENJTEC desktop sync client for Windows and macOS — the
[Nextcloud desktop client](https://github.com/nextcloud/desktop) (GPL-2.0-or-later)
built with KENJTEC branding and a fixed server address. This repository holds
only the branding and the build pipeline; the full corresponding source of
every build is attached to its release.*

Der KENJTEC-Desktop-Client hält einen Ordner auf dem Rechner mit der
BusinessCloud (`cloud.kenjtec.com`) im Gleichstand. Er ist Nextclouds Client,
nicht unser Nachbau. **Wir bauen nichts nach, was es fertig gibt** (Akte). Wir
ändern nur Name, Zeichen, Farben und die fest eingestellte Cloud.

Riza, 05.11.2026: *„kann man den nicht irgendwie mit kenjtec rausbringen aber
unter eigenem namen und eigenem Design“* und *„Zuerst Windows und macOS, mit
fest eingestellter Adresse, automatisch gebaut und aktualisiert.“* Android und
iPhone bekommen eine eigene, größere App, nicht diesen Client.

## Wo es liegt

| | |
|---|---|
| Quelle der Wahrheit | `apps/desktop/` im Monorepo `kenjtec-platform` |
| Öffentlich (GPL, Bauen) | `github.com/kenjtec/kenjtec-desktop`. Dieser Ordner ist dort die Wurzel. Hinüber kommt er mit `tools/desktop-spiegeln.sh` (nach dem Abliefern) |
| Update-Dienst | `kenjtec.com/api/desktop/update` → `apps/api/app/core/desktop_update.py` |
| Projektplan | T-47 |

## Wie die Marke darüberkommt

`werkzeuge/anwenden.py` ändert **keine Zeile** an Nextclouds Quellcode, sondern legt drei Dinge darüber:

1. `branding/marke.cmake` wird als letzte Zeile in `NEXTCLOUD.cmake` eingebunden. Darin stehen Name `KENJTEC`, Hersteller, feste Adresse, Update-Adresse, Farben, ein Konto je Installation und eigene Windows-GUIDs.
2. `branding/theme/` kommt über `theme/`: Programmsymbol, Logo im Anmelde-Assistenten (hellteal auf `#04342C`), Startmenü-Kachel, Ordnersymbol, Finder-Seitenleiste.
3. Das Craft-Rezept bekommt Firmen- und Programmnamen im Windows-Installer.

Findet einer der Schritte seine Stelle nicht mehr, **bricht er ab**. Ein halb
umbenannter Client ist schlechter als ein roter Bau.

Drei Entscheidungen, die man leicht wieder falsch macht:

- **Der Name hat kein Leerzeichen.** Nextclouds macOS-Bauwerkzeug setzt ihn ungeschützt in Shell-Befehle.
- **Die Adresse ist `cloud.kenjtec.com`, nicht `my.kenjtec.com`.** `my.` leitet nur weiter (302, auch für `/remote.php/dav`, gemessen 05.11.2026).
- **Die Urheberzeilen von Nextcloud bleiben**, im Info-Fenster und in den Dateiköpfen. Die GPL verlangt sie.

## Bauen und Aktualisieren

| Workflow | Wann | Was |
|---|---|---|
| `Bauen` | von Hand, bei jeder Änderung an `UPSTREAM`/`branding`/`werkzeuge`, vom Nachziehen | Windows (KDE Craft, NSIS-Installer) + macOS arm64 (mac-crafter, DMG) → Release `v<nextcloud>.<baunummer>` mit Installer, DMG und **vollständiger Quelle** |
| `Nachziehen` | jeden Montag | neuere stabile Nextcloud-Fassung **derselben Hauptnummer** → `UPSTREAM` nachziehen und bauen. Ein Sprung 4 → 5 wird nur gemeldet |

Die Baunummer hängt Nextclouds Fassung an (`4.0.11` → `4.0.11.12`). Daran
erkennt der Client, dass es etwas Neueres gibt.

**Updates:** Der Client fragt `kenjtec.com/api/desktop/update`. Der Kern
antwortet mit dem neuesten **echten** Release (nie mit einem Vorabrelease).
Windows lädt den Installer und spielt ihn ein. macOS zeigt vorerst nur einen
Hinweis mit Link, weil das automatische Einspielen (Sparkle) eine Signatur
braucht.

## Signieren (wartet auf den HRB-Eintrag)

Solange nicht signiert wird:

- ist **jedes Release ein Vorabrelease**. Der Update-Dienst übersieht es, also bekommt kein Kunde es von selbst;
- warnt Windows vor einem „unbekannten Herausgeber“, und macOS öffnet die App erst nach Rechtsklick → Öffnen.

Was dazukommt (CEO-Aufgabe „Entwicklerkonten anlegen“):

1. **Windows:** Azure Trusted Signing. Nach dem Installer-Schritt in `bauen.yml` mit `azure/trusted-signing-action` signieren (Anmeldung über OIDC, kein Schlüssel im Repo).
2. **macOS:** Apple Developer ID. `mac-crafter` kann es schon (`--code-sign-identity`, `--apple-id`, `--apple-team-id`, Notarisierung); `--disable-auto-updater` fällt dann weg, und Sparkle braucht einen eigenen Signierschlüssel.
3. Danach die Repo-Variable `SIGNIERT=ja` setzen. Ab dann sind Releases echte Releases, und Kunden bekommen Updates.

## Noch offen

- **Probe** (T-47.3): Der erste Bau ist am 05.11.2026 durchgelaufen (v4.0.11.6, Vorabrelease). Einmal installieren, anmelden und synchronisieren steht noch aus.
- **Fallen aus dem ersten Bau**, alle behoben: Quellordner für mac-crafter als Argument; Mac mit Nextclouds `next`-Rezepten; `zlib-1.3.1` liegt nicht mehr auf zlib.net (`werkzeuge/vorrat.py`); Inkscape nie in den Suchpfad (sein `python.exe`); Nextclouds Rezept importiert `os` nicht. Und ein Abbruch bei ffmpeg.org war nur eine Netzstörung: Lauf wiederholen.
- **Große Dateien:** Cloudflare nimmt höchstens 100 MB je Anfrage an. Der Client lädt in Stücken hoch; ob er bei großen Dateien unter der Grenze bleibt, zeigt erst die Probe.
- **Intel-Macs:** gebaut wird nur für Apple Silicon (arm64).
- **Datenschutzerklärung:** Der Update-Abruf schickt Betriebssystem und Fassung an `kenjtec.com`. Der Kern liest nur die Plattform und speichert nichts. Ein Satz dazu gehört in die Erklärung, bevor der Client beworben wird.
- **Download-Seite** erst, wenn signiert wird (Grundsatz 6).

## Lizenz

Die Bauskripte und das Branding stehen wie der Client unter der
GPL-2.0-or-later (`COPYING`). „KENJTEC“ und die KENJTEC-Zeichen sind Marken
von KENJTEC. Die Lizenz erlaubt den Code, nicht das Auftreten unter unserem
Namen.
