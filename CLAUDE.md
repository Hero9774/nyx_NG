# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Tests ausführen (inkl. pyflakes/pycodestyle wenn installiert)
./run_tests.py

# App direkt starten (Curses-Interface)
python -m nyx

# Nach Installation (`pip install -e .`)
nyx

# GUI-Modus starten (benötigt PyQt6)
nyx --gui

# Einzelnen Test ausführen
python -m unittest test.<modul>
```

## Architecture

Nyx ist ein Terminal-Statusmonitor für Tor, der über den Tor Control Port kommuniziert (via `stem`-Library).

### Zwei UI-Schichten

- **`nyx/panel/`** — Curses-basiertes Terminal-Interface (Standard)
- **`nyx/gui/`** — PyQt6-basiertes grafisches Interface (via `--gui`-Flag, optional)

Beide Schichten teilen sich dieselben Core-Module für Daten und Logik.

### Core-Singletons (`nyx/__init__.py`)

| Singleton | Funktion |
|-----------|----------|
| `nyx_interface()` | Gibt die `Interface`-Instanz zurück (UI-Controller, Seiten/Panels) |
| `tor_controller()` | Gibt die aktive `stem`-Verbindung zum Tor Control Port zurück |
| `cache()` | SQLite-basierter Cache für Relay-Informationen (Nickname, Adresse) |

### Datenfluss

```
Tor Daemon (Control Port)
    ↓
stem Library
    ↓
nyx/tracker/    ← Background-Daemons (ConnectionTracker, ResourceTracker,
    ↓               PortUsageTracker, ConsensusTracker)
nyx/cache
    ↓
nyx/panel/ oder nyx/gui/   ← Rendering
```

### Wichtige Module

- **`tracker/`** — Background-Daemons, die Tor-Daten polling/event-getrieben sammeln
- **`log.py`** — Event-Logging mit Deduplizierung (Konfiguration via `nyx/settings/dedup.cfg`)
- **`curses.py`** — Abstraktionslayer für Terminal-UI (Farben, Input, Scrolling, Subwindows)
- **`arguments.py`** — CLI-Argument-Parser
- **`starter.py`** — Startup-Logik für beide UI-Modi

### Konfiguration

- Benutzer-Config: `~/.nyx/config`
- Interne Defaults: `nyx/settings/attributes.cfg` (Farben, UI-Attribute)
- Konfigurationszugriff via `stem.util.conf`-System; alle Defaults werden mit `@uses_settings`-Dekorator geladen

### Panel-Architektur (Curses)

Alle Panels in `nyx/panel/` erben von einer gemeinsamen Basisklasse und laufen als Daemon-Threads. Das `Interface`-Objekt organisiert Panels in Seiten; `header.py` ist immer sichtbar.
