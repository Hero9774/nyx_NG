# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run tests (including pyflakes/pycodestyle if installed)
./run_tests.py

# Start app directly (curses interface)
python -m nyx

# After installation (pip install -e .)
nyx

# Start GUI mode (requires PyQt6)
nyx --gui

# Run a single test
python -m unittest test.<module>
```

## Architecture

Nyx is a terminal status monitor for Tor that communicates via the Tor Control Port (using the `stem` library).

### Two UI layers

- **`nyx/panel/`** — Curses-based terminal interface (default)
- **`nyx/gui/`** — PyQt6-based graphical interface (via `--gui` flag, optional)

Both layers share the same core modules for data and logic.

### Core singletons (`nyx/__init__.py`)

| Singleton | Purpose |
|-----------|---------|
| `nyx_interface()` | Returns the `Interface` instance (UI controller, pages/panels) |
| `tor_controller()` | Returns the active `stem` connection to the Tor Control Port |
| `cache()` | SQLite-based cache for relay information (nickname, address) |

### Data flow

```
Tor Daemon (Control Port)
    ↓
stem Library
    ↓
nyx/tracker/    ← Background daemons (ConnectionTracker, ResourceTracker,
    ↓               PortUsageTracker, ConsensusTracker)
nyx/cache
    ↓
nyx/panel/ or nyx/gui/   ← Rendering
```

### Key modules

- **`tracker/`** — Background daemons that collect Tor data via polling/events
- **`log.py`** — Event logging with deduplication (configured via `nyx/settings/dedup.cfg`)
- **`curses.py`** — Abstraction layer for terminal UI (colours, input, scrolling, subwindows)
- **`arguments.py`** — CLI argument parser
- **`starter.py`** — Startup logic for both UI modes
- **`i18n.py`** — Internationalisation: `_()` function, loads `nyx/locale/<lang>.json`

### Configuration

- User config: `~/.nyx/nyxrc`
- Internal defaults: `nyx/settings/attributes.cfg` (colours, UI attributes)
- Config access via `stem.util.conf` system; all defaults loaded with `@uses_settings` decorator

### Internationalisation

Language is set via `language en` or `language de` in `~/.nyx/nyxrc`.
Translation files live in `nyx/locale/<lang>.json`.  English is the built-in
default (no JSON required).  All UI strings are wrapped with `_()` from
`nyx.i18n`.

### Panel architecture (curses)

All panels in `nyx/panel/` inherit from a shared base class and run as daemon threads. The `Interface` object organises panels into pages; `header.py` is always visible.
