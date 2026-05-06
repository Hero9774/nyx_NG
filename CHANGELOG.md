# Changelog

## [1.0.4-3] – 2026-05-06

### Fixed
- `nyx_ng/gui/interpreter_widget.py`: Shell panel rendered raw ANSI escape
  sequences as literal text (e.g. `[34m`, `[0m`) instead of applying colours.
  Added `_print_ansi_line()` which parses ANSI colour/bold codes via regex and
  inserts each text segment with the corresponding `QTextCharFormat` colour.
  The curses panel already handled this correctly via `asci_to_curses()`; the
  GUI now has an equivalent implementation.

### Changed
- `nyx_ng/gui/interpreter_widget.py`: Hint bar text changed from the command
  list (`GETINFO, GETCONF, …`) to `/help for more info`; colour raised from
  `#555577` to `#8888aa` and font size from 10 px to 11 px for better
  legibility.

### Packaging
- New `nyx-ng_1.0.4-3_all.deb`

## [1.0.4-2] – 2026-05-05

### Fixed
- `nyx_ng/panel/connection.py`: Critical memory leak — `Entry.from_circuit()` used
  `CircuitEvent` objects as dict keys; since stem creates new objects with a fresh
  `arrived_at` timestamp on every `get_circuits()` call, each 5-second update cycle
  added a full batch of `CircuitEntry` objects to `ENTRY_CACHE`. At steady state this
  accumulated ~60× the number of active circuits (5 min TTL ÷ 5 s interval). Fixed by
  using the stable `circuit.id` string as cache key and updating the existing entry in
  place instead of inserting a duplicate.
- `nyx_ng/panel/connection.py`: `_counted_connections` set grew without bound (every
  unique remote IP address ever seen was stored permanently). Added an upper limit of
  50 000 entries; when exceeded the set and the associated locale/exit-port statistics
  are reset.

### Changed
- Added `SPDX-License-Identifier: GPL-3.0-or-later` and `Copyright 2026,
  H.Ommen <hero67097@gmail.com>` to all modified source files.

### Lint
- `nyx_ng/gui/connection_widget.py`: removed unused imports `QPushButton`, `Qt`
- `nyx_ng/gui/main_window.py`: removed unused imports `sys`, `QHBoxLayout`, `QIcon`;
  removed unused variable `halted_via_signal`
- `nyx_ng/gui/workers.py`: renamed loop variable `_` → `_i` to avoid shadowing the
  `_()` i18n import (affected `HeaderWorker` and `ConnectionWorker`)
- `nyx_ng/gui/log_widget.py`: removed unused import `time`
- `nyx_ng/gui/header_widget.py`: removed unused import `time`
- `nyx_ng/gui/config_widget.py`: removed unused imports `QPushButton`, `QPoint`
- `nyx_ng/gui/interpreter_widget.py`: removed unused import `QKeyEvent`

### Packaging
- `nyx_ng/__main__.py` hinzugefügt: `/usr/bin/nyx-ng` rief `python3 -m nyx_ng` auf,
  was ohne diese Datei mit „package cannot be directly executed" fehlschlug.
- New `nyx-ng_1.0.4-2_all.deb`

## [1.0.4] – 2026-04-28

### Added
- **"Start Tor" button** in the GUI toolbar: launches `sudo -S -u debian-tor tor` with a Qt password dialog (masked input). The button is only active when the Tor process is not running.
- **"Stop Tor" button** is now grayed out when the Tor process is not running.
- Process state is checked every 2 seconds via `pgrep -x tor`, independent of the control port connection.
- Green CSS styling for the new `start_button` (active/hover/pressed/disabled states).
- Disabled styling for `stop_button` when Tor is not running.
- German translations for all new UI strings.

### Packaging
- New `nyx-ng_1.0.4-1_all.deb`

## [1.0.3] – 2026-04-26

### Renamed (BREAKING)
- Python module `nyx` → `nyx_ng`
- PyPI/Debian package `nyx` → `nyx-ng`
- CLI command `nyx` → `nyx-ng`
- Manpage `nyx.1` → `nyx-ng.1`
- Rationale: enables side-by-side installation with the official `nyx 2.1.0-3` from Debian/Ubuntu repositories without dpkg/APT conflicts
- `~/.nyx/nyxrc` is kept as the configuration file (compatible with the original format)

### Changed
- Project URL: `https://nyx.torproject.org/` → `https://github.com/Hero9774/nyx_NG`
- Bug tracker: `github.com/torproject/nyx/issues` → `github.com/Hero9774/nyx_NG/issues`
- About popup: "Nyx" → "Nyx NG", maintainer line updated
- README.md, manpage, web/index.html and web/changelog/index.html updated to point to this repository
- Tor Project links (Stem, Tor Browser, torrc docs) left unchanged

### Fixed
- `nyx_ng/__init__.py`: replaced `distutils.spawn.find_executable` with `shutil.which` (distutils was removed in Python 3.12)
- `test/cache.py`: replaced `assertRaisesRegexp` with `assertRaisesRegex` (removed in Python 3.12)

### Packaging
- New `nyx-ng_1.0.3-1_all.deb` (no Conflicts/Replaces needed — distinct package, distinct install path)

### Docs
- `CLAUDE.md`: corrected paths `nyx/tracker/` → `nyx/tracker.py`, `nyx/cache` → `nyx/cache.py`

## [1.0.2] – 2026-04-26

### Added
- `VERSION_STATUS_COLORS` und `FLAG_COLORS` Dicts in `nyx/gui/header_widget.py`
- Tor-Versionsstatus (`status/version/current`) wird in `HeaderWorker` abgerufen (`nyx/gui/workers.py`)

### Changed
- Relay-Flags im Header-Widget werden farbig als RichText-HTML dargestellt
- Tor-Versions-Label zeigt Farbe passend zum Versionsstatus (recommended/obsolete/…)
- CPU- und RAM-Labels zeigen grün/gelb/rot je nach Auslastung
- `status_text`-Label bekommt eigenes `objectName` und CSS-Klasse (`nyx/gui/theme.py`)
- Toolbar in `theme.py`: `border-bottom` auf 2 px, `padding` auf 6 px, `min-height: 38px`
- `status_label` Farbe von `#a0a0c0` auf `#c0c0d8` angehoben, Schriftgröße auf 13 px
- Version bumped to 1.0.2

## [1.0.1] – 2026-04-22

### Added
- Internationalisation system (`nyx/i18n.py`): `_()` function, JSON-based translation files
- German translation (`nyx/locale/de.json`) with 118 translated strings
- Language setting persisted in `~/.nyx/nyxrc` (`language en` / `language de`)
- Language switch menu in GUI mode: View → Language
- Language switch menu in terminal mode: menu key `m` → Language
- `nyx.set_language()` function for runtime language switching with config persistence
- `pyproject.toml`: modern PEP 517 build system replacing legacy `setup.py`

### Changed
- Default log level in GUI log panel changed from ALL to NOTICE (consistent with terminal mode)
- GUI log level filter now works as minimum-level filter (NOTICE shows NOTICE + WARN + ERR)
- `nyx/country.py`: renamed `COUNTRY_NAMES` → `COUNTRY_NAMES_DE`, added `get_country_name()` with language awareness
- `nyx/arguments.py`: default config path changed from `~/.nyx/config` to `~/.nyx/nyxrc`
- `nyx/starter.py`: language loaded from config before UI initialisation
- `web/nyxrc.sample`: updated path reference and added `language` option
- All GUI widget strings wrapped with `_()` for translation support
- Author metadata updated: H.Ommen <hero67097@gmail.com>
- Version bumped to 1.0.1

### Fixed
- `nyx/panel/connection.py`: replaced removed `COUNTRY_NAMES` import with `get_country_name()`
- `nyx/locale/de.json`: removed duplicate `"Type"` key
- `nyx/starter.py`: eliminated dead `else: pass` branch and redundant `os.path.exists()` call
- `setup.py`/`package_data`: `locale/*.json` was missing from installed package (fixed in pyproject.toml)

### Removed
- `setup.py`: replaced by `pyproject.toml`
- Old `.deb` packages (`nyx_1.0_amd64.deb`, `nyx_2.1.0_amd64.deb`)

---

## [1.0] – 2026-04-01

### Added
- PyQt6-based graphical interface (`nyx --gui`)
- Country flag icons (lipis/flag-icons, MIT licence)
- apt pinning support for installation
- Python 3.11+ compatibility fixes
