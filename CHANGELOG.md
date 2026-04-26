# Changelog

## [1.0.3] – 2026-04-26

### Renamed (BREAKING)
- Python-Modul `nyx` → `nyx_ng`
- PyPI/Debian-Paket `nyx` → `nyx-ng`
- CLI-Befehl `nyx` → `nyx-ng`
- Manpage `nyx.1` → `nyx-ng.1`
- Begründung: ermöglicht parallele Installation neben dem offiziellen `nyx 2.1.0-3` aus den Debian/Ubuntu-Repositories ohne dpkg/APT-Konflikte
- `~/.nyx/nyxrc` bleibt als Konfigurationsdatei (kompatibel mit Original-Format)

### Changed
- Projekt-URL: `https://nyx.torproject.org/` → `https://github.com/Hero9774/nyx_NG`
- Bug-Tracker: `github.com/torproject/nyx/issues` → `github.com/Hero9774/nyx_NG/issues`
- About-Popup: „Nyx" → „Nyx NG", Maintainer-Zeile aktualisiert
- README.md, manpage, web/index.html und web/changelog/index.html auf eigenes Repo umgestellt
- Tor-Project-Links (Stem, Tor Browser, torrc-Doku) bleiben unverändert

### Fixed
- `nyx_ng/__init__.py`: `distutils.spawn.find_executable` durch `shutil.which` ersetzt (distutils wurde in Python 3.12 entfernt)
- `test/cache.py`: `assertRaisesRegexp` durch `assertRaisesRegex` ersetzt (in Python 3.12 entfernt)

### Packaging
- Neues `nyx-ng_1.0.3-1_all.deb` (kein Conflicts/Replaces nötig — eigenes Paket, eigener Pfad)

### Docs
- `CLAUDE.md`: Pfade `nyx/tracker/` → `nyx/tracker.py`, `nyx/cache` → `nyx/cache.py` korrigiert

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
- Author metadata updated: H.Ommen <kalkseniaya@gmail.com>
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
