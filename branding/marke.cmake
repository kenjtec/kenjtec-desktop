# SPDX-FileCopyrightText: 2026 KENJTEC
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Die Marke des KENJTEC-Desktop-Clients.
#
# `werkzeuge/anwenden.py` haengt diese Datei als letzte Zeile an Nextclouds
# `NEXTCLOUD.cmake` an. CMake nimmt bei `set()` den zuletzt gesetzten Wert —
# deshalb ueberschreiben wir hier nur, statt Nextclouds Datei zu ersetzen.
# Kommt in einer neuen Nextcloud-Fassung ein Schalter dazu, bleibt seine
# Vorgabe stehen, und nichts bricht still.
#
# Bewusst OHNE Leerzeichen im Namen: Das macOS-Bauwerkzeug (mac-crafter)
# setzt den Namen ungeschuetzt in Shell-Befehle (`create-dmg --volname`,
# `packagesutil … name`). „KENJTEC Cloud.app“ zerfiele dort in zwei Woerter.

set( APPLICATION_NAME       "KENJTEC" )
set( APPLICATION_SHORTNAME  "KENJTEC" )
set( APPLICATION_EXECUTABLE "kenjtec" )
set( APPLICATION_ICON_NAME  "KENJTEC" )
set( APPLICATION_CONFIG_NAME "${APPLICATION_EXECUTABLE}" )
set( APPLICATION_DOMAIN     "kenjtec.com" )
set( APPLICATION_VENDOR     "KENJTEC" )
set( APPLICATION_REV_DOMAIN "com.kenjtec.desktopclient" )
set( APPLICATION_VIRTUALFILE_SUFFIX "kenjtec" )
set( APPLICATION_HELP_URL   "https://kenjtec.com/docs" )

# Die Cloud. ⚠️ cloud.kenjtec.com, NICHT my.kenjtec.com: my. leitet nur
# weiter (302, gemessen 05.11.2026 auch fuer /remote.php/dav). Eine
# Weiterleitung bei fest eingestellter Adresse waere eine Fehlerquelle.
set( APPLICATION_SERVER_URL "https://cloud.kenjtec.com" )
set( APPLICATION_SERVER_URL_ENFORCE ON )

# Nach Updates fragt der Client UNSEREN Kern (routers/desktop.py), nie
# updates.nextcloud.org — sonst boete er Nextclouds Fassung zum Einbau an.
set( APPLICATION_UPDATE_URL "https://kenjtec.com/api/desktop/update" )

set( LINUX_PACKAGE_SHORTNAME "kenjtec" )
set( LINUX_APPLICATION_ID "${APPLICATION_REV_DOMAIN}.${LINUX_PACKAGE_SHORTNAME}" )

# Farben aus apps/web/tailwind.config.ts: Kopf in teal.deep, Schrift paper.
# Das Logo darauf ist die hellteale Fassung (Regel „dunkel → hellteal“).
set( APPLICATION_WIZARD_HEADER_BACKGROUND_COLOR "#04342C" )
set( APPLICATION_WIZARD_HEADER_TITLE_COLOR "#F6FAF8" )
set( APPLICATION_WIZARD_USE_CUSTOM_LOGO ON )

# Ein Konto je Installation: Der Client ist fuer EINE Cloud gebaut.
set( ENFORCE_SINGLE_ACCOUNT ON )

if(WIN32)
    # Eigene Kennungen — Nextclouds Hinweis: „Generate new GUIDs for custom
    # builds“. Sonst stritten sich unser Client und ein installierter
    # Nextcloud-Client um dieselben Explorer-Erweiterungen.
    set( WIN_SHELLEXT_CONTEXT_MENU_GUID      "{2E830FE1-89CF-4627-A926-C490927F237C}" )
    set( WIN_SHELLEXT_OVERLAY_GUID_ERROR     "{018B1EAD-78E7-4512-BDE0-24DD34CCC895}" )
    set( WIN_SHELLEXT_OVERLAY_GUID_OK        "{EB06E716-A09F-4C42-B9A5-8C92B23C80D2}" )
    set( WIN_SHELLEXT_OVERLAY_GUID_OK_SHARED "{6B3E00E9-A9D5-494B-A674-43D901E0967E}" )
    set( WIN_SHELLEXT_OVERLAY_GUID_SYNC      "{BB84890A-A5B5-43A9-B03F-A8C217C3C0F8}" )
    set( WIN_SHELLEXT_OVERLAY_GUID_WARNING   "{17DDD982-4137-455F-8A02-77CE6631161C}" )
    set( WIN_MSI_UPGRADE_CODE                "50AF9C2F-3DA3-4C31-BAEB-C26F3CAF050E" )
endif()
