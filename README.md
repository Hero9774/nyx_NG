# Nyx NG — Tor Command-line Monitor

Nyx ist ein Echtzeit-Statusmonitor für [Tor](https://www.torproject.org/) im Terminal. Er verbindet sich über den Tor Control Port und zeigt detaillierte Informationen zu Bandbreite, Verbindungen, Logs und der Konfiguration deines Relays an.

Dieses Repository ist ein Fork des originalen [nyx](https://git.torproject.org/nyx.git) mit folgenden Erweiterungen:
- **PyQt6-GUI** (`--gui`): grafisches Interface als Alternative zur Terminal-Ansicht
- Python 3.11+ Kompatibilität

---

## Funktionsübersicht

| Panel | Beschreibung |
|-------|--------------|
| **Header** | Immer sichtbar. Zeigt Tor-Version, IP-Adresse, Relay-Flags, Bandbreite, CPU/RAM und Accounting-Status. |
| **Graph** | Echtzeit-Graphen für Bandbreite (Up/Down), Verbindungsanzahl oder CPU/Speicher-Auslastung. |
| **Verbindungen** | Liste aller aktiven Tor-Verbindungen mit Typ, Ziel, Land und Nickname. |
| **Logs** | Tor-Event-Log in Echtzeit mit einstellbaren Log-Leveln und Deduplizierung. |
| **Konfiguration** | Übersicht und Live-Editor für alle Tor-Konfigurationsoptionen. |
| **Torrc** | Syntaxhervorhebung der aktiven `torrc`-Datei. |
| **Interpreter** | Direktzugriff auf den Tor Control Port mit Tab-Vervollständigung und Verlauf. |

---

## Voraussetzungen

- Python 3.8 oder neuer
- [`stem`](https://stem.torproject.org/) >= 1.7.0
- Für den GUI-Modus: `PyQt6`

**Tor muss mit aktiviertem Control Port konfiguriert sein** (`/etc/tor/torrc`):
```
ControlPort 9051
CookieAuthentication 1
```
Danach Tor neu starten: `sudo systemctl restart tor`

---

## Installation

### Empfohlen: pipx (kein venv nötig)

```bash
# pipx installieren falls nicht vorhanden
sudo apt install pipx

# Nyx NG installieren
pipx install git+https://github.com/Hero9774/nyx_NG.git

# Für GUI-Modus zusätzlich PyQt6 injizieren
pipx inject nyx PyQt6
```

### Aus dem Quellcode (für Entwicklung)

```bash
git clone https://github.com/Hero9774/nyx_NG.git
cd nyx_NG

# Virtuelle Umgebung erstellen
python3 -m venv .venv
source .venv/bin/activate

# Abhängigkeiten installieren
pip install -e .
pip install PyQt6          # optional, nur für --gui

# Starten
nyx
```

### Debian/Ubuntu Paket

```bash
sudo apt install nyx       # installiert die offizielle Version ohne GUI-Erweiterung
```

---

## Verwendung

```bash
# Starten (verbindet automatisch mit lokalem Control Port)
nyx

# Grafisches Interface (PyQt6 erforderlich)
nyx --gui

# Anderen Control Port angeben
nyx -i 9051
nyx -i 192.168.1.1:9051

# Unix Domain Socket verwenden
nyx -s /var/run/tor/control

# Eigene Konfigurationsdatei
nyx -c ~/.nyx/config

# Nur bestimmte Log-Events anzeigen
nyx -l WARN,ERR

# Debug-Ausgabe in Datei schreiben
nyx -d /tmp/nyx-debug.log
```

---

## Tastaturkürzel

### Global (auf allen Seiten)

| Taste | Funktion |
|-------|----------|
| `←` / `→` | Zwischen Seiten wechseln |
| `h` | Hilfe anzeigen |
| `m` | Menü öffnen |
| `p` | Anzeige pausieren / fortsetzen |
| `x` | Tor neu laden (SIGHUP) |
| `q` | Nyx beenden |

### Im Graph-Panel

| Taste | Funktion |
|-------|----------|
| `↑` / `↓` | Statistik wechseln (Bandbreite / Verbindungen / Ressourcen) |
| `i` | Zeitintervall ändern |
| `s` | Skalierungsmodus umschalten |
| `Enter` | Detailansicht öffnen |

### Im Verbindungs-Panel

| Taste | Funktion |
|-------|----------|
| `↑` / `↓` | Verbindung auswählen |
| `Enter` | Details anzeigen |
| `s` | Sortierung ändern |
| `d` | Descriptor anzeigen |
| `c` | Nach Verbindungstyp filtern |

### Im Log-Panel

| Taste | Funktion |
|-------|----------|
| `↑` / `↓` / `PgUp` / `PgDn` | Scrollen |
| `f` | Filter setzen |
| `e` | Event-Typen auswählen |
| `a` | Duplikate ein-/ausblenden |
| `c` | Log leeren |

### Im Konfigurations-Panel

| Taste | Funktion |
|-------|----------|
| `↑` / `↓` | Option auswählen |
| `Enter` | Option bearbeiten |
| `s` | Sortierung ändern |
| `f` | Filtern |
| `w` | Konfiguration in torrc speichern |

### Im Interpreter-Panel

| Taste | Funktion |
|-------|----------|
| `Enter` | Befehl senden |
| `↑` / `↓` | Befehlsverlauf |
| `Tab` | Auto-Vervollständigung |

---

## Konfiguration

Benutzer-Konfiguration: `~/.nyx/config`

```ini
# Anzahl gespeicherter Log-Einträge
cache.log_size 1000

# Standard-Graph beim Start (bandwidth, connections, resources)
graph_stat bandwidth

# Duplikate im Log ausblenden
features.log.showDuplicateEntries false
```

Kommentierte Beispielkonfiguration: [`nyxrc.sample`](nyxrc.sample)

---

## Alle CLI-Optionen

```
nyx [OPTION]

  -i, --interface [ADRESSE:]PORT   Control Port (Standard: 127.0.0.1:9051)
  -s, --socket PFAD                Unix Domain Socket (Standard: /var/run/tor/control)
  -c, --config PFAD                Konfigurationsdatei (Standard: ~/.nyx/config)
  -d, --debug PFAD                 Debug-Logs in Datei schreiben
  -l, --log EVENTS                 Kommagetrennte Event-Liste (z.B. NOTICE,WARN,ERR)
  -g, --gui                        PyQt6-GUI starten
  -v, --version                    Versionsinformation anzeigen
  -h, --help                       Hilfe anzeigen
```

---

## Lizenz

GPLv3 — basierend auf [nyx](https://nyx.torproject.org/) von Damian Johnson und The Tor Project.
