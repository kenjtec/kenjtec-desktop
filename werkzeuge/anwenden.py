#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 KENJTEC
# SPDX-License-Identifier: GPL-2.0-or-later
"""Legt die KENJTEC-Marke über den unveränderten Nextcloud-Desktop-Client.

WARUM ES DAS GIBT
-----------------
Wir bauen keinen eigenen Sync-Client, sondern verteilen Nextclouds Client
unter unserem Namen (Riza, 05.11.2026). Damit jede neue Nextcloud-Fassung
ohne Handarbeit durchläuft, ändern wir NICHTS am Quellcode selbst, sondern
legen nur drei Dinge darüber:

  1. `branding/marke.cmake` → als letzte Zeile in `NEXTCLOUD.cmake`
     (Name, Hersteller, feste Cloud-Adresse, Update-Adresse, Farben, GUIDs);
  2. `branding/theme/` → über `theme/` (Programmsymbol, Logo im Assistenten,
     Startmenü-Kachel, Ordnersymbol);
  3. das Craft-Rezept `nextcloud-client.py` → Firmen- und Programmname im
     Windows-Installer (Nextcloud hat sie dort fest eingetragen).

Findet ein Schritt seine Stelle nicht mehr (neue Nextcloud-Fassung hat
etwas umbenannt), bricht er LAUT ab. Ein Client, der halb „Nextcloud GmbH“
heißt, ist schlechter als ein roter Bau.

AUFRUF
------
    python anwenden.py quelle <nextcloud-quellordner> --bau <nummer>
    python anwenden.py rezept <craft-wurzel>

`quelle` braucht Inkscape (das braucht der Nextcloud-Bau ohnehin), um das
Logo des Assistenten auch als PNG abzulegen — sonst bliebe dort Nextclouds
PNG liegen, und auf Bildschirmen ohne SVG-Vorzug sähe man ihr Logo.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent.parent
BRANDING = HIER / "branding"

#: Was Nextclouds Craft-Rezept fest einträgt → was bei uns dort stehen muss.
#: Links steht der Text WÖRTLICH, wie er im Rezept steht.
REZEPT_ERSETZUNGEN: list[tuple[str, str]] = [
    ('self.description = "Nextcloud Desktop Client"', 'self.description = "KENJTEC Desktop-Client"'),
    ('self.displayName = "Nextcloud"', 'self.displayName = "KENJTEC"'),
    ('self.webpage = "https://nextcloud.com"', 'self.webpage = "https://kenjtec.com"'),
    ('self.defines["appname"] = "nextcloud"', 'self.defines["appname"] = "kenjtec"'),
    ('self.defines["company"] = "Nextcloud GmbH"', 'self.defines["company"] = "KENJTEC"'),
    ('self.applicationExecutable = "nextcloud"', 'self.applicationExecutable = "kenjtec"'),
]

#: Hängt hinter die Ersetzungen: das Installer-Symbol. Craft nähme sonst sein
#: eigenes (craft.ico). Die .ico-Datei erzeugt Nextclouds CMake aus
#: `KENJTEC-icon.svg` (ecm_add_app_icon → <bau>/src/gui/KENJTEC.ico).
REZEPT_SYMBOL_ANKER = "        return super().createPackage()"
REZEPT_SYMBOL = (
    '        self.defines["icon"] = os.path.join(self.buildDir(), "src", "gui", "KENJTEC.ico")\n'
    '        self.defines["productname"] = "KENJTEC"\n'
)

EINBINDUNG = "include(${CMAKE_SOURCE_DIR}/kenjtec-marke.cmake)"


def fehler(satz: str) -> None:
    print(f"KENJTEC-Branding: {satz}", file=sys.stderr)
    sys.exit(1)


def inkscape() -> str:
    for name in ("inkscape", "inkscape.com", "inkscape.exe"):
        pfad = shutil.which(name)
        if pfad:
            return pfad
    for pfad in (
        Path(r"C:\Program Files\Inkscape\bin\inkscape.exe"),
        Path("/Applications/Inkscape.app/Contents/MacOS/inkscape"),
    ):
        if pfad.exists():
            return str(pfad)
    fehler("Inkscape fehlt — ohne es bliebe Nextclouds Logo als PNG im Assistenten.")
    return ""


def quelle(ordner: Path, bau: int) -> None:
    cmake = ordner / "NEXTCLOUD.cmake"
    if not cmake.exists():
        fehler(f"{cmake} fehlt — ist das ein Nextcloud-Desktop-Quellordner?")

    # 1. Marke + Baunummer. Die Baunummer macht aus 4.0.11 die 4.0.11.<bau>;
    #    daran erkennt der Update-Dienst, dass es etwas Neueres gibt.
    #    NEXTCLOUD.cmake wird VOR VERSION.cmake gelesen, das
    #    MIRALL_VERSION_BUILD nur setzt, wenn es noch fehlt.
    marke = (BRANDING / "marke.cmake").read_text(encoding="utf-8")
    marke += f"\n# Vom Bau gesetzt (werkzeuge/anwenden.py):\nset( MIRALL_VERSION_BUILD \"{bau}\" )\nset( MIRALL_VERSION_SUFFIX \"\" )\n"
    (ordner / "kenjtec-marke.cmake").write_text(marke, encoding="utf-8", newline="\n")
    text = cmake.read_text(encoding="utf-8")
    if EINBINDUNG not in text:
        cmake.write_text(text.rstrip("\n") + "\n\n# KENJTEC\n" + EINBINDUNG + "\n", encoding="utf-8", newline="\n")

    # 2. Bilder.
    ziel_theme = ordner / "theme"
    for datei in (BRANDING / "theme").rglob("*"):
        if datei.is_file():
            ziel = ziel_theme / datei.relative_to(BRANDING / "theme")
            ziel.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(datei, ziel)

    logo = ziel_theme / "colored" / "wizard_logo.svg"
    exe = inkscape()
    for name, hoehe in (("wizard_logo.png", 100), ("wizard_logo@2x.png", 200)):
        subprocess.run(
            [exe, str(logo), f"--export-height={hoehe}", f"--export-filename={ziel_theme / 'colored' / name}"],
            check=True,
        )

    # 3. Prüfen, dass nichts liegen blieb, was „Nextcloud“ als Programm nennt.
    for pflicht in ("KENJTEC-icon.svg", "KENJTEC-w10startmenu.svg", "KENJTEC-sidebar.svg",
                    "icons/KENJTEC-icon-win-folder.svg", "wizard_logo.svg", "wizard_logo.png"):
        if not (ziel_theme / "colored" / pflicht).exists():
            fehler(f"theme/colored/{pflicht} fehlt nach dem Anwenden.")
    print(f"KENJTEC-Branding: Quelle {ordner} gebrandet (Bau {bau}).")


def rezept(craft_wurzel: Path) -> None:
    treffer = [
        p for p in craft_wurzel.rglob("nextcloud-client.py")
        if p.parent.name == "nextcloud-client" and "blueprints" in p.parts
    ]
    if not treffer:
        fehler(f"Kein Craft-Rezept nextcloud-client.py unter {craft_wurzel} — erst `craft --add-blueprint-repository`.")
    for pfad in treffer:
        text = pfad.read_text(encoding="utf-8")
        if REZEPT_SYMBOL.strip().splitlines()[0] in text:
            print(f"KENJTEC-Branding: {pfad} ist schon angepasst.")
            continue
        for alt, neu in REZEPT_ERSETZUNGEN:
            if text.count(alt) != 1:
                fehler(f"Im Rezept {pfad} steht `{alt}` nicht genau einmal — Nextcloud hat es geändert. Liste in anwenden.py nachziehen.")
            text = text.replace(alt, neu)
        if text.count(REZEPT_SYMBOL_ANKER) != 1:
            fehler(f"Im Rezept {pfad} fehlt `{REZEPT_SYMBOL_ANKER.strip()}`.")
        text = text.replace(REZEPT_SYMBOL_ANKER, REZEPT_SYMBOL + REZEPT_SYMBOL_ANKER)
        # Nextclouds Rezept benutzt `os.path.join` in createPackage, importiert
        # `os` aber nicht (stable-4.0, gemessen 05.11.2026: NameError beim
        # Packen — Nextclouds eigene CI packt nie und merkt es nicht).
        if not re.search(r"^import os\b", text, re.M):
            text, n = re.subn(r"^(import info)(\r?\n)", r"\1\2import os\2", text, count=1, flags=re.M)
            if n != 1:
                fehler(f"Im Rezept {pfad} fehlt `import info` — `import os` lässt sich nicht einsetzen.")
        # Die Urheberzeile „Nextcloud GmbH and Nextcloud contributors“ bleibt
        # stehen — die GPL verlangt sie. Geprüft wird nur der Code.
        code = "\n".join(z for z in text.splitlines() if not z.lstrip().startswith("#"))
        if re.search(r"Nextcloud GmbH|\"nextcloud\"", code):
            fehler(f"Im Rezept {pfad} steht nach dem Anpassen noch Nextcloud als Hersteller oder Programm.")
        pfad.write_text(text, encoding="utf-8", newline="\n")
        print(f"KENJTEC-Branding: Rezept {pfad} angepasst.")


def main() -> None:
    teiler = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    unter = teiler.add_subparsers(dest="befehl", required=True)
    q = unter.add_parser("quelle")
    q.add_argument("ordner", type=Path)
    q.add_argument("--bau", type=int, required=True)
    r = unter.add_parser("rezept")
    r.add_argument("craft_wurzel", type=Path)
    args = teiler.parse_args()
    if args.befehl == "quelle":
        quelle(args.ordner.resolve(), args.bau)
    else:
        rezept(args.craft_wurzel.resolve())


if __name__ == "__main__":
    main()
