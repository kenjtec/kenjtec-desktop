#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 KENJTEC
# SPDX-License-Identifier: GPL-2.0-or-later
"""Die Sprachen des KENJTEC-Desktop-Clients: Nextclouds Übersetzungen, unsere Ergänzungen darüber.

WARUM ES DAS GIBT
-----------------
Nextclouds Sprachdateien (`translations/client_*.ts`) sind für mehrere unserer
zwölf Sprachen lückenhaft, und Hindi gibt es gar nicht (gemessen an v4.0.11,
18.11.2026: de 100 %, pt_BR 99 %, sv 91 %, es/it/ja 90 %, fr 87 %, ar 75 %,
nl 71 %, da 63 %, pt 30 %, hi fehlt). Was fehlt, zeigt der Client englisch —
mitten in einer deutschen, japanischen oder arabischen Oberfläche.

Wie die übrige Marke ändern wir Nextclouds Quellcode nicht. Unsere Texte liegen
je Sprache in `branding/sprachen/<code>.json` und werden beim Bau
(`anwenden.py quelle`) in Nextclouds `translations/` eingemischt. Fehlt eine
Sprache dort ganz (Hindi), entsteht ihre Datei aus der Liste der Texte neu;
Nextclouds CMake nimmt jede `translations/client_*.ts` auf (`file(GLOB …)`),
und der Client wählt sie über die Systemsprache (`hi_Deva_IN` → `client_hi`).

Was in `branding/sprachen/` steht, GILT — auch dort, wo Nextcloud schon etwas
hat. So bleibt die Anrede je Sprache einheitlich (es/pt/nl/da duzen wie
kenjtec.com, fr siezt), und „Nextcloud“ als Name des Dienstes heißt
„BusinessCloud“ (Einträge mit `"grund"`).

LAUT ABBRECHEN, wenn
  · eine Ergänzung auf einen Text zeigt, den Nextcloud nicht mehr hat
    (neue Fassung hat ihn geändert oder gestrichen) — sonst lägen unsere
    Übersetzungen still daneben;
  · eine Ergänzung Platzhalter, Markup, Tastenkürzel oder Mehrzahlformen
    verliert — Qt zeigte sonst „%1“ falsch oder gar nichts;
  · eine unserer Sprachen nach dem Einmischen unter 100 % liegt — dann hat
    Nextcloud neue Texte; `luecken` holt sie als Vorlage heraus.

AUFRUF
------
    python sprachen.py messen <nextcloud-quelle>
        Abdeckung je Sprache (mit unseren Ergänzungen), rot unter 100 %.
    python sprachen.py luecken <nextcloud-quelle> <code> <vorlage.json>
        Die offenen Texte einer Sprache als Vorlage zum Übersetzen.
    python sprachen.py aufnehmen <code> <uebersetzt.json>
        Übersetzte Texte (Vorlage mit "text"/"formen") in branding/sprachen/ aufnehmen.

Von `anwenden.py quelle` aufgerufen: `einmischen()` schreibt die Dateien,
danach `pruefen()` — beides gegen dieselbe Quelle.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

HIER = Path(__file__).resolve().parent.parent
SPRACHEN = HIER / "branding" / "sprachen"

#: Unsere zwölf Sprachen mit Nextclouds Kürzel (bei uns `se` → `sv`, `in` → `hi`).
#: Englisch ist Nextclouds Quellsprache: Es ist immer vollständig.
#: pt_BR ist keine unserer zwölf, steht aber neben pt im Client und wird
#: mitgeführt, damit Brasilien nicht schlechter dasteht als Portugal.
UNSERE = {
    "de": "de", "en": None, "es": "es", "fr": "fr", "it": "it", "nl": "nl",
    "pt": "pt", "da": "da", "se": "sv", "ja": "ja", "ar": "ar", "in": "hi",
}
MITGEFUEHRT = ["pt_BR"]

#: Sprachen, die Nextcloud nicht hat: ihre `language` in der .ts-Datei
#: (bestimmt in lrelease die Mehrzahlregel) und die Datei, deren Textliste
#: als Gerüst dient (vollständig, jede Fassung).
NEU = {"hi": "hi_IN"}
GERUEST = "de"

#: Mehrzahlformen je Sprache, wie Nextclouds Dateien (Transifex) sie führen.
#: es/fr/it/pt haben eine dritte („many“), die lrelease verwirft — Qt kennt dort
#: zwei; wir schreiben sie gleich der zweiten. hi: lrelease erwartet zwei
#: (gemessen mit lrelease aus Qt 6, 18.11.2026: drei → „Removed plural forms“).
FORMEN = {"de": 2, "es": 3, "fr": 3, "it": 3, "nl": 2, "pt": 3, "pt_BR": 3,
          "da": 2, "sv": 2, "ja": 1, "ar": 6, "hi": 2}

#: Schrift, die in einem übersetzten Satz vorkommen muss.
SCHRIFT = {
    "ja": re.compile(r"[぀-ヿ一-鿿]"),
    "ar": re.compile(r"[؀-ۿ]"),
    "hi": re.compile(r"[ऀ-ॿ]"),
}
#: Namen, die in jeder Sprache lateinisch bleiben — ein Satz nur aus ihnen
#: braucht keine fremde Schrift.
NAMEN = re.compile(r"\b(KENJTEC|BusinessCloud|Nextcloud|ownCloud|GmbH|Copyright|Talk|Windows|macOS|"
                   r"Linux|Finder|Explorer|WebDAV|HTTPS?|SSL|TLS|OAuth|URL|PIN|USB|VFS|E2EE|"
                   r"Client Push|GitHub|Qt|OpenSSL|ID|OK|KBytes|[KMGT]B)\b")

PLATZHALTER = re.compile(r"%L?\d+|%n")
TAG = re.compile(r"</?([a-zA-Z][a-zA-Z0-9]*)\b[^>]*>")
HREF = re.compile(r"""href=["']([^"']*)["']""")
KUERZEL = re.compile(r"&(?![&#]|[a-zA-Z]+;)\S")
VERBOTEN = re.compile(r"kostenlos|gratis|umsonst|gratuit|gratuito|無料|مجاني|मुफ़्त|मुफ्त", re.I)
STEUERZEICHEN = re.compile(r"[‎‏‪-‮⁦-⁩]")

#: So erkennt Nextclouds CMake die Sprachdateien. Ändert sich das, käme
#: client_hi.ts still nicht mehr in den Bau.
CMAKE_GLOB = "file( GLOB TRANS_FILES ${CMAKE_SOURCE_DIR}/translations/client_*.ts)"


class Fehler(Exception):
    pass


Schluessel = tuple  # (kontext, quelle, kommentar | None)


def schluessel(e: dict) -> Schluessel:
    return (e["kontext"], e["quelle"], e.get("kommentar"))


# ---------------------------------------------------------------- Ergänzungen

def ergaenzungen(code: str) -> dict[Schluessel, dict]:
    pfad = SPRACHEN / f"{code}.json"
    if not pfad.exists():
        return {}
    daten = json.loads(pfad.read_text(encoding="utf-8"))
    if daten.get("sprache") != code:
        raise Fehler(f"{pfad.name}: „sprache“ ist {daten.get('sprache')!r}, erwartet {code!r}.")
    aus: dict[Schluessel, dict] = {}
    for e in daten["texte"]:
        k = schluessel(e)
        if k in aus:
            raise Fehler(f"{pfad.name}: doppelt — {k[0]} / {k[1][:60]!r}")
        aus[k] = e
    return aus


def eintrag_pruefen(code: str, e: dict, numerus: bool) -> list[str]:
    """Was an einer Ergänzung nicht stimmt (leer = in Ordnung)."""
    quelle = e["quelle"]
    probleme: list[str] = []
    if numerus:
        werte = e.get("formen")
        if not isinstance(werte, list):
            return ["Mehrzahltext ohne „formen“"]
        if len(werte) != FORMEN[code]:
            probleme.append(f"{len(werte)} Formen statt {FORMEN[code]}")
    else:
        if "formen" in e:
            return ["„formen“ an einem Text ohne Mehrzahl"]
        werte = [e.get("text")]
    for w in werte:
        if not isinstance(w, str) or not w.strip():
            probleme.append("leer")
            continue
        soll = Counter(PLATZHALTER.findall(quelle))
        ist = Counter(PLATZHALTER.findall(w))
        if numerus and soll["%n"]:
            # %n gehört in jede Form (die Zahl steht sonst nur im Englischen da),
            # wie oft, entscheidet die Sprache. Manche Mehrzahltexte zählen mit
            # %1 („%1 files in conflict“) — dort gilt der Vergleich unten.
            soll.pop("%n", None)
            if not ist.pop("%n", 0):
                probleme.append("%n fehlt")
        if soll != ist:
            probleme.append(f"Platzhalter {dict(soll)} ≠ {dict(ist)}")
        if Counter(t.lower() for t in TAG.findall(quelle)) != Counter(t.lower() for t in TAG.findall(w)):
            probleme.append("Markup weicht ab")
        if sorted(HREF.findall(quelle)) != sorted(HREF.findall(w)):
            probleme.append("Adresse (href) weicht ab")
        if KUERZEL.search(quelle) and not KUERZEL.search(w):
            probleme.append("Tastenkürzel & fehlt")
        if VERBOTEN.search(w):
            probleme.append("Preiswort (kostenlos/gratis …)")
        if STEUERZEICHEN.search(w):
            probleme.append("unsichtbares Richtungszeichen")
        if "nextcloud" in w.lower() and "nextcloud" not in quelle.lower():
            probleme.append("„Nextcloud“, wo die Quelle es nicht nennt")
        schrift = SCHRIFT.get(code)
        if schrift and not schrift.search(w):
            rest = NAMEN.sub(" ", TAG.sub(" ", PLATZHALTER.sub(" ", quelle)))
            if re.search(r"[A-Za-z]{4,}", rest):
                probleme.append("keine Zeichen der Sprache")
    return probleme


# ------------------------------------------------------------------ .ts-Dateien

def nachrichten(wurzel: ET.Element):
    for ctx in wurzel.iter("context"):
        name = ctx.findtext("name")
        for m in ctx.iter("message"):
            yield (name, m.findtext("source"), m.findtext("comment")), m


def lebt(m: ET.Element) -> bool:
    return m.find("translation").get("type") not in ("vanished", "obsolete")


def fertig(m: ET.Element) -> bool:
    tr = m.find("translation")
    if tr.get("type") is not None:
        return False
    if m.get("numerus") == "yes":
        formen = tr.findall("numerusform")
        return bool(formen) and all((f.text or "").strip() for f in formen)
    return bool((tr.text or "").strip())


def setzen(m: ET.Element, e: dict) -> None:
    tr = m.find("translation")
    for kind in list(tr):
        tr.remove(kind)
    tr.attrib.pop("type", None)
    if m.get("numerus") == "yes":
        tr.text = None
        for wert in e["formen"]:
            ET.SubElement(tr, "numerusform").text = wert
    else:
        tr.text = e["text"]


def geruest(ordner: Path, sprache: str) -> ET.Element:
    """Eine leere .ts-Datei mit allen Texten — für Sprachen, die Nextcloud nicht hat."""
    wurzel = copy.deepcopy(lesen(ordner / f"client_{GERUEST}.ts"))
    wurzel.set("language", sprache)
    for _, m in nachrichten(wurzel):
        tr = m.find("translation")
        for kind in list(tr):
            tr.remove(kind)
        tr.text = None
        tr.attrib.clear()
        tr.set("type", "unfinished")
    return wurzel


def lesen(pfad: Path) -> ET.Element:
    return ET.parse(pfad).getroot()


def schreiben(pfad: Path, wurzel: ET.Element) -> None:
    text = ET.tostring(wurzel, encoding="unicode")
    pfad.write_text('<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE TS>\n' + text + "\n",
                    encoding="utf-8", newline="\n")


def codes() -> list[str]:
    return [c for c in UNSERE.values() if c] + MITGEFUEHRT


def mischen(ordner: Path, code: str) -> tuple[ET.Element, dict[str, int]]:
    """Unsere Ergänzungen in die .ts-Datei einer Sprache (im Speicher)."""
    pfad = ordner / f"client_{code}.ts"
    if pfad.exists():
        wurzel = lesen(pfad)
    elif code in NEU:
        wurzel = geruest(ordner, NEU[code])
    else:
        raise Fehler(f"{pfad} fehlt — Nextcloud hat die Sprache {code} gestrichen?")
    unsere = ergaenzungen(code)
    vorhanden = {k: m for k, m in nachrichten(wurzel) if lebt(m)}
    veraltet = [k for k in unsere if k not in vorhanden]
    if veraltet:
        zeilen = "\n".join(f"    {k[0]} / {k[1][:80]!r}" for k in veraltet[:15])
        raise Fehler(f"branding/sprachen/{code}.json: {len(veraltet)} Ergänzung(en) zeigen auf Texte, die "
                     f"Nextcloud nicht mehr hat — Quelle geändert oder gestrichen. Nachziehen:\n{zeilen}")
    falsch = []
    zahlen = {"gefuellt": 0, "ersetzt": 0}
    for k, e in unsere.items():
        m = vorhanden[k]
        probleme = eintrag_pruefen(code, e, m.get("numerus") == "yes")
        if probleme:
            falsch.append(f"    {k[0]} / {k[1][:60]!r}: {', '.join(probleme)}")
            continue
        zahlen["ersetzt" if fertig(m) else "gefuellt"] += 1
        setzen(m, e)
    if falsch:
        raise Fehler(f"branding/sprachen/{code}.json: {len(falsch)} Ergänzung(en) fehlerhaft:\n" + "\n".join(falsch[:30]))
    return wurzel, zahlen


def abdeckung(wurzel: ET.Element) -> tuple[int, int]:
    alle = [m for _, m in nachrichten(wurzel) if lebt(m)]
    return sum(fertig(m) for m in alle), len(alle)


def cmake_pruefen(quelle: Path) -> None:
    cmake = quelle / "CMakeLists.txt"
    if not cmake.exists() or CMAKE_GLOB not in cmake.read_text(encoding="utf-8"):
        raise Fehler("Nextclouds CMakeLists.txt sammelt die Sprachdateien nicht mehr über "
                     f"`{CMAKE_GLOB}` — client_hi.ts käme still nicht in den Bau. werkzeuge/sprachen.py nachziehen.")


# --------------------------------------------------------------------- Befehle

def einmischen(quelle: Path) -> None:
    """Schreibt unsere Ergänzungen in <quelle>/translations (vom Bau aufgerufen)."""
    cmake_pruefen(quelle)
    ordner = quelle / "translations"
    for code in codes():
        wurzel, zahlen = mischen(ordner, code)
        schreiben(ordner / f"client_{code}.ts", wurzel)
        print(f"KENJTEC-Sprachen: client_{code}.ts — {zahlen['gefuellt']} ergänzt, {zahlen['ersetzt']} ersetzt.")


def pruefen(quelle: Path) -> bool:
    """Abdeckung je Sprache mit unseren Ergänzungen. True = alle bei 100 %."""
    ordner = quelle / "translations"
    gesamt_ok = True
    print("KENJTEC-Sprachen: Abdeckung (fertige Texte / alle)")
    for unser, code in list(UNSERE.items()) + [(c, c) for c in MITGEFUEHRT]:
        if code is None:
            print(f"  {unser:5} {'en':6}  Quellsprache                 100.0 %")
            continue
        wurzel, _ = mischen(ordner, code)
        f, n = abdeckung(wurzel)
        ok = f == n
        gesamt_ok &= ok
        print(f"  {unser:5} {code:6}  {f:5} / {n:5}  {'ok ' if ok else 'ROT'}            {100 * f / n:5.1f} %")
    return gesamt_ok


def luecken(quelle: Path, code: str, ziel: Path) -> None:
    wurzel, _ = mischen(quelle / "translations", code)
    offen = []
    for k, m in nachrichten(wurzel):
        if lebt(m) and not fertig(m):
            e = {"kontext": k[0], "quelle": k[1]}
            if k[2]:
                e["kommentar"] = k[2]
            if m.findtext("extracomment"):
                e["hinweis"] = m.findtext("extracomment")
            if m.get("numerus") == "yes":
                e["formen"] = [""] * FORMEN[code]
            else:
                e["text"] = ""
            offen.append(e)
    ziel.write_text(json.dumps(offen, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(offen)} offene Texte für {code} → {ziel}")


def aufnehmen(code: str, datei: Path) -> None:
    neu = json.loads(datei.read_text(encoding="utf-8"))
    pfad = SPRACHEN / f"{code}.json"
    daten = json.loads(pfad.read_text(encoding="utf-8")) if pfad.exists() else {
        "sprache": code,
        "zweck": f"KENJTECs Texte über Nextclouds translations/client_{code}.ts — sie gelten vor Nextclouds "
                 "eigenen. Eingemischt von werkzeuge/sprachen.py; „grund“ nennt, warum ein fertiger Text "
                 "von Nextcloud ersetzt wird (anrede, marke).",
        "texte": [],
    }
    texte = {schluessel(e): e for e in daten["texte"]}
    for e in neu:
        sauber = {"kontext": e["kontext"], "quelle": e["quelle"]}
        for feld in ("kommentar", "text", "formen", "grund"):
            if e.get(feld) not in (None, ""):
                sauber[feld] = e[feld]
        if "text" not in sauber and "formen" not in sauber:
            raise Fehler(f"{datei}: ohne Übersetzung — {e['kontext']} / {e['quelle'][:60]!r}")
        texte[schluessel(sauber)] = sauber
    daten["texte"] = sorted(texte.values(), key=lambda e: (e["kontext"], e["quelle"], e.get("kommentar") or ""))
    SPRACHEN.mkdir(parents=True, exist_ok=True)
    pfad.write_text(json.dumps(daten, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(neu)} Texte in {pfad.relative_to(HIER)} aufgenommen ({len(texte)} insgesamt).")


def main() -> None:
    teiler = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    unter = teiler.add_subparsers(dest="befehl", required=True)
    m = unter.add_parser("messen")
    m.add_argument("quelle", type=Path)
    lu = unter.add_parser("luecken")
    lu.add_argument("quelle", type=Path)
    lu.add_argument("code")
    lu.add_argument("ziel", type=Path)
    a = unter.add_parser("aufnehmen")
    a.add_argument("code")
    a.add_argument("datei", type=Path)
    args = teiler.parse_args()
    try:
        if args.befehl == "messen":
            cmake_pruefen(args.quelle.resolve())
            if not pruefen(args.quelle.resolve()):
                print("KENJTEC-Sprachen: unter 100 % — `sprachen.py luecken` holt die offenen Texte.", file=sys.stderr)
                sys.exit(1)
        elif args.befehl == "luecken":
            luecken(args.quelle.resolve(), args.code, args.ziel)
        else:
            aufnehmen(args.code, args.datei)
    except Fehler as f:
        print(f"KENJTEC-Sprachen: {f}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
