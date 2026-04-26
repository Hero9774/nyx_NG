# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run tests (including pyflakes/pycodestyle if installed)
./run_tests.py

# Start app directly (curses interface)
python -m nyx_ng

# After installation (pip install -e .)
nyx-ng

# Start GUI mode (requires PyQt6)
nyx-ng --gui

# Run a single test
python -m unittest test.<module>
```

## Architecture

Nyx NG is a terminal status monitor for Tor that communicates via the Tor Control Port (using the `stem` library). The package installs as `nyx-ng` and the Python module is `nyx_ng`, so it can coexist with the official `nyx` package from Debian/Ubuntu repositories.

### Two UI layers

- **`nyx_ng/panel/`** — Curses-based terminal interface (default)
- **`nyx_ng/gui/`** — PyQt6-based graphical interface (via `--gui` flag, optional)

Both layers share the same core modules for data and logic.

### Core singletons (`nyx_ng/__init__.py`)

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
nyx_ng/tracker.py  ← Background daemons (ConnectionTracker, ResourceTracker,
    ↓               PortUsageTracker, ConsensusTracker)
nyx_ng/cache.py
    ↓
nyx_ng/panel/ or nyx_ng/gui/   ← Rendering
```

### Key modules

- **`tracker.py`** — Background daemons that collect Tor data via polling/events
- **`log.py`** — Event logging with deduplication (configured via `nyx_ng/settings/dedup.cfg`)
- **`curses.py`** — Abstraction layer for terminal UI (colours, input, scrolling, subwindows)
- **`arguments.py`** — CLI argument parser
- **`starter.py`** — Startup logic for both UI modes
- **`i18n.py`** — Internationalisation: `_()` function, loads `nyx_ng/locale/<lang>.json`

### Configuration

- User config: `~/.nyx/nyxrc`
- Internal defaults: `nyx_ng/settings/attributes.cfg` (colours, UI attributes)
- Config access via `stem.util.conf` system; all defaults loaded with `@uses_settings` decorator

### Internationalisation

Language is set via `language en` or `language de` in `~/.nyx/nyxrc`.
Translation files live in `nyx_ng/locale/<lang>.json`.  English is the built-in
default (no JSON required).  All UI strings are wrapped with `_()` from
`nyx_ng.i18n`.

### Panel architecture (curses)

All panels in `nyx_ng/panel/` inherit from a shared base class and run as daemon threads. The `Interface` object organises panels into pages; `header.py` is always visible.
