#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 KENJTEC
# SPDX-License-Identifier: GPL-2.0-or-later
"""Legt Quellarchive in Crafts Download-Ordner, deren Adresse verschwunden ist.

WARUM ES DAS GIBT
-----------------
Craft holt Quellen von der Adresse im Rezept. Ziehen Projekte ältere
Fassungen um, läuft der Bau in einen 404, obwohl die Datei weiter existiert.
Erster Fall (05.11.2026): zlib.net hält `zlib-1.3.1.tar.xz` nicht mehr
vor, Nextcloud verlangt aber genau 1.3.1 (craftmaster.ini). Dieselbe Datei
liegt im offiziellen GitHub-Release von zlib.

Craft lädt nicht neu, wenn die Datei schon liegt UND ihre Prüfsumme zum
Rezept passt. Deshalb steht hier jede Datei mit der Prüfsumme AUS DEM
REZEPT. Passt sie nicht, bricht das Skript ab, statt etwas Fremdes
unterzuschieben.

AUFRUF
------
    python vorrat.py <craft-wurzel>      # z. B. mac-bau/macos-clang-arm64
"""
from __future__ import annotations

import hashlib
import sys
import urllib.request
from pathlib import Path

#: (Pfad unter download/archives, Ersatzadresse, SHA-256 aus dem Craft-Rezept)
VORRAT: list[tuple[str, str, str]] = [
    (
        "libs/zlib/zlib-1.3.1.tar.xz",
        "https://github.com/madler/zlib/releases/download/v1.3.1/zlib-1.3.1.tar.xz",
        "38ef96b8dfe510d42707d9c781877914792541133e1870841463bfa73f883e32",
    ),
]


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    wurzel = Path(sys.argv[1]) / "download" / "archives"
    for teil, adresse, soll in VORRAT:
        ziel = wurzel / teil
        if ziel.exists() and hashlib.sha256(ziel.read_bytes()).hexdigest() == soll:
            print(f"Vorrat: {teil} liegt schon.")
            continue
        ziel.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(adresse, timeout=120) as antwort:
            daten = antwort.read()
        ist = hashlib.sha256(daten).hexdigest()
        if ist != soll:
            sys.exit(f"Vorrat: {adresse} hat die Prüfsumme {ist}, das Rezept verlangt {soll} — nicht abgelegt.")
        ziel.write_bytes(daten)
        print(f"Vorrat: {teil} abgelegt ({len(daten)} Bytes, Prüfsumme wie im Rezept).")


if __name__ == "__main__":
    main()
