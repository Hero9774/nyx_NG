# Nyx NG — Tor Command-line Monitor

Nyx NG is a real-time status monitor for [Tor](https://www.torproject.org/) in the terminal. It connects via the Tor Control Port and displays detailed information about bandwidth, connections, logs and the configuration of your relay.

This repository is a fork of the original [nyx](https://gitlab.torproject.org/tpo/core/nyx) with the following additions:
- **PyQt6 GUI** (`--gui`): graphical interface as an alternative to the terminal view
- Python 3.11+ compatibility

---

## Feature Overview

| Panel | Description |
|-------|-------------|
| **Header** | Always visible. Shows Tor version, IP address, relay flags, bandwidth, CPU/RAM and accounting status. |
| **Graph** | Real-time graphs for bandwidth (up/down), connection count or CPU/memory usage. |
| **Connections** | List of all active Tor connections with type, destination, country and nickname. |
| **Log** | Tor event log in real time with configurable log levels and deduplication. |
| **Configuration** | Overview and live editor for all Tor configuration options. |
| **Torrc** | Syntax-highlighted view of the active `torrc` file. |
| **Interpreter** | Direct access to the Tor Control Port with tab completion and history. |

---

## Requirements

- Python 3.8 or newer
- [`stem`](https://stem.torproject.org/) >= 1.7.0
- For GUI mode: `PyQt6`

**Tor must be configured with an active Control Port** (`/etc/tor/torrc`):
```
ControlPort 9051
CookieAuthentication 1
```
Then restart Tor: `sudo systemctl restart tor`

---

## Installation

### Recommended: pipx (no venv needed)

```bash
# Install pipx if not present
sudo apt install pipx

# Install Nyx NG
pipx install git+https://github.com/Hero9774/nyx_NG.git

# For GUI mode also inject PyQt6
pipx inject nyx-ng PyQt6
```

### From source (for development)

```bash
git clone https://github.com/Hero9774/nyx_NG.git
cd nyx_NG

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .
pip install PyQt6          # optional, only for --gui

# Start
nyx-ng
```

### Debian/Ubuntu package (this fork)

```bash
sudo dpkg -i nyx-ng_1.0.3-1_all.deb
```

The package installs as `nyx-ng` and can coexist with the official `nyx` package
from the Debian/Ubuntu repositories without conflict.

---

## Usage

```bash
# Start (connects automatically to local Control Port)
nyx-ng

# Graphical interface (PyQt6 required)
nyx-ng --gui

# Specify a different Control Port
nyx-ng -i 9051
nyx-ng -i 192.168.1.1:9051

# Use Unix Domain Socket
nyx-ng -s /var/run/tor/control

# Use a custom configuration file
nyx-ng -c ~/.nyx/nyxrc

# Show only specific log events
nyx-ng -l WARN,ERR

# Write debug output to file
nyx-ng -d /tmp/nyx-ng-debug.log
```

---

## Keyboard Shortcuts

### Global (on all pages)

| Key | Action |
|-----|--------|
| `←` / `→` | Switch between pages |
| `h` | Show help |
| `m` | Open menu |
| `p` | Pause / resume display |
| `x` | Reload Tor (SIGHUP) |
| `q` | Quit nyx-ng |

### In the Graph panel

| Key | Action |
|-----|--------|
| `↑` / `↓` | Switch statistic (bandwidth / connections / resources) |
| `i` | Change time interval |
| `s` | Toggle scaling mode |
| `Enter` | Open detail view |

### In the Connections panel

| Key | Action |
|-----|--------|
| `↑` / `↓` | Select connection |
| `Enter` | Show details |
| `s` | Change sort order |
| `d` | Show descriptor |
| `c` | Filter by connection type |

### In the Log panel

| Key | Action |
|-----|--------|
| `↑` / `↓` / `PgUp` / `PgDn` | Scroll |
| `f` | Set filter |
| `e` | Select event types |
| `a` | Toggle duplicate hiding |
| `c` | Clear log |

### In the Configuration panel

| Key | Action |
|-----|--------|
| `↑` / `↓` | Select option |
| `Enter` | Edit option |
| `s` | Change sort order |
| `f` | Filter |
| `w` | Save configuration to torrc |

### In the Interpreter panel

| Key | Action |
|-----|--------|
| `Enter` | Send command |
| `↑` / `↓` | Command history |
| `Tab` | Auto-completion |

---

## Configuration

User configuration: `~/.nyx/nyxrc`

```ini
# Interface language: en (English) or de (German)
language en

# Number of stored log entries
max_log_size 1000

# Default graph at startup (bandwidth, connections, resources)
graph_stat bandwidth

# Hide duplicate log entries
deduplicate_log true
```

Full commented example: [`nyxrc.sample`](web/nyxrc.sample)

---

## All CLI Options

```
nyx-ng [OPTION]

  -i, --interface [ADDRESS:]PORT   Control Port (default: 127.0.0.1:9051)
  -s, --socket PATH                Unix Domain Socket (default: /var/run/tor/control)
  -c, --config PATH                Configuration file (default: ~/.nyx/nyxrc)
  -d, --debug PATH                 Write debug logs to file
  -l, --log EVENTS                 Comma-separated event list (e.g. NOTICE,WARN,ERR)
  -g, --gui                        Start PyQt6 GUI
  -v, --version                    Show version information
  -h, --help                       Show help
```

---

## License

GPLv3 — based on [nyx](https://gitlab.torproject.org/tpo/core/nyx) by Damian Johnson and The Tor Project. Fork at [github.com/Hero9774/nyx_NG](https://github.com/Hero9774/nyx_NG).
