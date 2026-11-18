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

4. `branding/sprachen/<code>.json` wird in Nextclouds `translations/client_<code>.ts` eingemischt (`werkzeuge/sprachen.py`, siehe „Sprachen“).

Findet einer der Schritte seine Stelle nicht mehr, **bricht er ab**. Ein halb
umbenannter Client ist schlechter als ein roter Bau.

## Sprachen

Der Client spricht unsere zwölf Sprachen vollständig (seit dem 18.11.2026).
Nextclouds eigene Sprachdateien waren lückenhaft (v4.0.11: pt 30 %, da 63 %,
nl 71 %, ar 75 %, fr 87 %, es/it/ja 90 %, sv 91 %, pt_BR 99 %), Hindi fehlte
ganz. Was fehlt, zeigt der Client englisch, mitten in der eigenen Sprache.

- **Unsere Texte liegen in `branding/sprachen/<code>.json`** (Nextclouds Kürzel: `sv` für unser `se`, `hi` für unser `in`). Sie gelten vor Nextclouds eigenen. `anwenden.py quelle` mischt sie ein; Hindi entsteht dabei als `client_hi.ts` neu aus der Textliste. Nextclouds CMake sammelt jede `translations/client_*.ts` ein, und der Client nimmt die Datei, die zur Systemsprache passt (`hi_Deva_IN` → `client_hi`).
- **Einheitliche Anrede** wie auf kenjtec.com: es, pt, nl, da duzen (wo Nextcloud siezte, ersetzt, `"grund": "anrede"`), fr siezt, pt_BR bleibt bei você. Deutsch siezt noch, wie Nextcloud (offen, siehe unten).
- **„Nextcloud“ als Name des Dienstes** heißt „BusinessCloud“ (`"grund": "marke"`). Die Urheberzeile und die Adressen bleiben.
- **Der Bau bricht ab**, wenn eine Ergänzung auf einen Text zeigt, den Nextcloud nicht mehr hat, wenn Platzhalter, Markup, Tastenkürzel oder Mehrzahlformen nicht stimmen, wenn eine unserer Sprachen unter 100 % liegt, wenn Nextclouds CMake die Sprachdateien anders einsammelt, und wenn eine `client_<code>.qm` nicht im Installer (`bin\i18n`) bzw. im App-Paket (`Contents/Resources/Translations`) liegt.

Nachziehen, wenn eine neue Nextcloud-Fassung neue Texte bringt (der Bau ist dann rot):

```bash
python werkzeuge/sprachen.py messen <nextcloud-quelle>
python werkzeuge/sprachen.py luecken <nextcloud-quelle> hi vorlage-hi.json
python werkzeuge/sprachen.py aufnehmen hi vorlage-hi.json
```

`luecken` legt die offenen Texte mit leerem `text` (bzw. `formen`) ab; übersetzt nach den Regeln des Skills `uebersetzen` (Platzhalter `%1`/`%n` exakt, Mehrzahl in Qts Reihenfolge, Namen lateinisch), dann `aufnehmen`. Zeigt eine Ergänzung auf einen geänderten Text, die Zeile in `branding/sprachen/<code>.json` anpassen oder streichen.

Drei Entscheidungen, die man leicht wieder falsch macht:

- **Der Name hat kein Leerzeichen.** Nextclouds macOS-Bauwerkzeug setzt ihn ungeschützt in Shell-Befehle.
- **Die Adresse ist `cloud.kenjtec.com`, nicht `my.kenjtec.com`.** `my.` leitet nur weiter (302, auch für `/remote.php/dav`, gemessen 05.11.2026).
- **Die Urheberzeilen von Nextcloud bleiben**, im Info-Fenster und in den Dateiköpfen. Die GPL verlangt sie.
- **Im Infobereich steht unser Programmzeichen** (seit 18.11.2026, Rizas Wahl „B“). Der Abgleichstand ist eine kleine Plakette unten rechts (Pfeile, Pause, Ausrufezeichen, Kreuz), „offline“ ist das Zeichen in Grau, „alles abgeglichen“ das Zeichen allein. Die sechs `branding/theme/colored/state-*.svg` erzeugt `werkzeuge/status_symbole.py` aus `KENJTEC-icon.svg`, nie von Hand. `anwenden.py quelle` bricht ab, wenn sie nicht zum Erzeuger passen oder Nextcloud die Namen ändert. Dieselbe Datei zeigt das Schnellfenster neben „Alles synchronisiert!“.
- **Keine Begrüßungsseite von Nextcloud** (`WITH_PROVIDERS OFF`, seit 18.11.2026). Sonst startet das Anmelde-Fenster auf einer Diaschau mit Nextclouds Logo und den Knöpfen „Mit Provider anmelden“ und „Eigenen Server betreiben“. Ohne sie geht es bei fest eingestellter Adresse direkt zur Anmeldung im Browser. `anwenden.py quelle` und der Bau (Prüfung der fertigen `config.h`) brechen ab, wenn der Schalter nicht greift.

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

- **Probe** (T-47.3): **Windows bestanden am 18.11.2026 mit v4.0.11.9**: installieren ohne Verwalterrechte, Startmenü, Fassung in „Apps“, deutsche Oberfläche, Anmeldung (Webflow), Abgleich, 40 MiB hoch (zwei Stücke à 30 MiB + Rest) und als Platzhalter wieder herunter (Prüfsumme gleich), deinstallieren (Verknüpfung und Eintrag weg). Offen: die Probe auf einem Mac. Beim Aktualisieren über einen älteren Bau läuft dessen Deinstaller nicht mit (Crafts Vorlage): Dateien, die es in der neuen Fassung nicht mehr gibt, bleiben liegen — harmlos, solange sich nur Dateien ändern.
- **Fallen aus dem ersten Bau**, alle behoben: Quellordner für mac-crafter als Argument; Mac mit Nextclouds `next`-Rezepten; `zlib-1.3.1` liegt nicht mehr auf zlib.net (`werkzeuge/vorrat.py`); Inkscape nie in den Suchpfad (sein `python.exe`); Nextclouds Rezept importiert `os` nicht. Und ein Abbruch bei ffmpeg.org war nur eine Netzstörung: Lauf wiederholen.
- **Fallen des Installers** (18.11.2026), behoben in `anwenden.py rezept`: Nextclouds Packliste warf `kenjtec.exe` weg (`PACKLISTE_ALT`); Crafts NSIS-Packer legt eine Startmenü-Verknüpfung nur mit `defines["executable"]` an, und ohne `defines["version"]` steht in „Apps“ die Fassung `HEAD` (`REZEPT_INSTALLER`); die Übersetzungen lagen unter `i18n\`, der Client sucht sie neben `kenjtec.exe` in `bin\i18n\` und sprach nur Englisch (`REZEPT_I18N`, ein `install()` im Rezept). Qts eigene Grundtexte (`qtbase_*`) streicht Nextclouds Packliste absichtlich. Probeinstallation ohne Verwalterrechte: `__COMPAT_LAYER=RunAsInvoker`, dann `<installer> /S /D=%LOCALAPPDATA%\Programs\KENJTEC`.
- **Große Dateien:** Die Grenze ist nicht Cloudflare (100 MB), sondern **Cloud Run: 32 MiB je Anfrage** (gemessen 18.11.2026, darüber 413). Der Client nimmt als Stückgröße, was die Cloud ankündigt (`files.chunked_upload.max_size`), und schickt Dateien bis zu dieser Größe in EINER Anfrage. Deshalb kündigt die Cloud 30 MiB an (`apps/cloud/config/kenjtec.config.php`, live seit kenjtec-cloud-00173). Downloads über 32 MiB gehen durch (Nextcloud streamt; gemessen mit 40 MiB). Ein Client, der vorher an 413 scheiterte, sperrt die Datei bis zu 24 Stunden — oder bis sie sich ändert.
- **Intel-Macs:** gebaut wird nur für Apple Silicon (arm64).
- **Sprachen, am Gerät noch zu sehen:** Ob die arabische Oberfläche von rechts nach links läuft, entscheidet Qt über seine eigene Übersetzung (`QT_LAYOUT_DIRECTION` in `qtbase_ar`), und die streicht Nextclouds Packliste — einmal auf Arabisch ansehen. Brasilianisches Portugiesisch lädt unter Windows `client_pt` (die Systemsprache heißt dort `pt_Latn_BR`, Qt kürzt von hinten), also unser europäisches Portugiesisch. Deutsch siezt wie bei Nextcloud, kenjtec.com duzt — umstellen nur auf Rizas Ja.
- **Datenschutzerklärung:** Der Update-Abruf schickt Betriebssystem und Fassung an `kenjtec.com`. Der Kern liest nur die Plattform und speichert nichts. Ein Satz dazu gehört in die Erklärung, bevor der Client beworben wird.
- **Download-Seite** erst, wenn signiert wird (Grundsatz 6).

## Lizenz

Die Bauskripte und das Branding stehen wie der Client unter der
GPL-2.0-or-later (`COPYING`). „KENJTEC“ und die KENJTEC-Zeichen sind Marken
von KENJTEC. Die Lizenz erlaubt den Code, nicht das Auftreten unter unserem
Namen.
