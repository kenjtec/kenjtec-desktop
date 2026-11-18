#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 KENJTEC
# SPDX-License-Identifier: GPL-2.0-or-later
"""Zeichnet die Status-Symbole des Infobereichs aus unserem Programmzeichen.

WARUM ES DAS GIBT
-----------------
Im Infobereich (neben der Uhr) zeigt der Client nicht sein Programmzeichen,
sondern den Abgleichstand: `theme/colored/state-*.svg`. Ein gebrandeter
Nextcloud-Client nimmt dafür neutrale Symbole — ein grüner Kreis mit Haken,
der aussieht wie irgendein Prüfprogramm. Riza, 18.11.2026: „Ja, mach hier
bitte unser Logo“ — gewählt: das Programmzeichen (Variante B), wie im
Startmenü.

So sehen die sechs Zustände aus:
  ok       das Zeichen allein (der Normalfall soll ruhig aussehen)
  sync     Plakette unten rechts, Teal mit zwei Pfeilen
  pause    Plakette Grau mit zwei Strichen
  warning  Plakette Gelb mit Ausrufezeichen
  error    Plakette Rot mit Kreuz
  offline  das Zeichen in Grau

Die Plakette trägt einen weißen Rand, damit sie auf heller und dunkler
Taskleiste vom Zeichen abgesetzt ist. Bei 16 Pixeln trägt vor allem ihre
Farbe die Bedeutung.

⚠️ Qt zeichnet SVG Tiny: keine CSS-Filter, keine `style`-Tricks. Deshalb ist
„offline“ mit festen Grautönen gezeichnet, nicht mit grayscale().

AUFRUF
------
    python status_symbole.py            # schreibt branding/theme/colored/state-*.svg
    python status_symbole.py --pruefen  # bricht ab, wenn eine Datei nicht dem Erzeuger entspricht

Das Programmzeichen selbst kommt aus `branding/theme/colored/KENJTEC-icon.svg`.
Ändert es sich, diesen Erzeuger laufen lassen.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

FARBEN = Path(__file__).resolve().parent.parent / "branding" / "theme" / "colored"
QUELLE = FARBEN / "KENJTEC-icon.svg"

#: Nextclouds Namen, wie sie in theme.qrc.in stehen.
ZUSTAENDE = ("ok", "sync", "pause", "warning", "error", "offline")

TEAL_DUNKEL, MINT = "#04342C", "#1DE9B6"
GRAU_DUNKEL, GRAU_HELL = "#5F6B68", "#C9D2CF"

CX, CY, R = 48, 48, 15
STRICH = 'fill="none" stroke="#FFFFFF" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"'


def plakette(farbe: str, inhalt: str) -> str:
    return (f'<circle cx="{CX}" cy="{CY}" r="{R + 3}" fill="#FFFFFF"/>'
            f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="{farbe}"/>{inhalt}')


PLAKETTEN = {
    "ok": "",
    "sync": plakette("#0F6E56",
                     f'<g {STRICH}><path d="M40.6 47.2a7.6 7.6 0 0 1 13.6-4.3"/>'
                     '<path d="M55.4 48.8a7.6 7.6 0 0 1-13.6 4.3"/>'
                     '<path d="M54.6 38.6v4.8h-4.8"/><path d="M41.4 57.4v-4.8h4.8"/></g>'),
    "pause": plakette(GRAU_DUNKEL,
                      '<rect x="42" y="40.5" width="4.6" height="15" rx="1.4" fill="#FFFFFF"/>'
                      '<rect x="49.4" y="40.5" width="4.6" height="15" rx="1.4" fill="#FFFFFF"/>'),
    "warning": plakette("#F2A900",
                        '<rect x="45.7" y="39" width="4.6" height="11" rx="2.3" fill="#15201D"/>'
                        '<circle cx="48" cy="55.4" r="2.6" fill="#15201D"/>'),
    "error": plakette("#C62828", f'<g {STRICH}><path d="M43 43l10 10"/><path d="M53 43l-10 10"/></g>'),
    "offline": "",
}


def fehler(satz: str) -> None:
    print(f"Status-Symbole: {satz}", file=sys.stderr)
    sys.exit(1)


def zeichen() -> str:
    """Der Inhalt von KENJTEC-icon.svg ohne Hülle und Kommentar."""
    text = QUELLE.read_text(encoding="utf-8")
    treffer = re.search(r"<svg\b[^>]*>(.*)</svg>", text, re.S)
    if not treffer:
        fehler(f"{QUELLE} ist kein SVG.")
    inhalt = re.sub(r"<!--.*?-->", "", treffer.group(1), flags=re.S).strip()
    if TEAL_DUNKEL not in inhalt or MINT not in inhalt:
        fehler(f"{QUELLE} hat nicht mehr die Farben {TEAL_DUNKEL}/{MINT} — Grau für „offline“ nachziehen.")
    if 'viewBox="0 0 64 64"' not in text:
        fehler(f"{QUELLE} hat nicht mehr viewBox 0 0 64 64 — die Plakette sitzt sonst falsch.")
    return inhalt


def dateien() -> dict[str, str]:
    basis = zeichen()
    grau = basis.replace(TEAL_DUNKEL, GRAU_DUNKEL).replace(MINT, GRAU_HELL)
    aus = {}
    for name in ZUSTAENDE:
        inhalt = grau if name == "offline" else basis + PLAKETTEN[name]
        aus[f"state-{name}.svg"] = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">'
            f"<!-- KENJTEC: Abgleichstand „{name}“ im Infobereich. Erzeugt von "
            "apps/desktop/werkzeuge/status_symbole.py aus KENJTEC-icon.svg — nicht von Hand ändern. -->"
            f"{inhalt}</svg>\n"
        )
    return aus


def main() -> None:
    teiler = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    teiler.add_argument("--pruefen", action="store_true", help="nur vergleichen, nichts schreiben")
    args = teiler.parse_args()
    soll = dateien()
    if args.pruefen:
        falsch = [n for n, t in soll.items()
                  if not (FARBEN / n).exists() or (FARBEN / n).read_text(encoding="utf-8") != t]
        if falsch:
            fehler(f"veraltet oder fehlend: {', '.join(falsch)} — `python werkzeuge/status_symbole.py` laufen lassen.")
        print(f"Status-Symbole: {len(soll)} Dateien entsprechen dem Erzeuger.")
        return
    for name, text in soll.items():
        (FARBEN / name).write_text(text, encoding="utf-8", newline="\n")
    print(f"Status-Symbole: {len(soll)} Dateien geschrieben nach {FARBEN}.")


if __name__ == "__main__":
    main()
