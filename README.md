# Nyx — Tor Command-line Monitor

Nyx ist ein Echtzeit-Statusmonitor für [Tor](https://www.torproject.org/) im Terminal. Er verbindet sich über den Tor Control Port und zeigt detaillierte Informationen zu Bandbreite, Verbindungen, Logs und der Konfiguration deines Relays an.

---

## Funktionsübersicht

| Panel | Beschreibung |
|-------|--------------|
| **Header** | Immer sichtbar. Zeigt Tor-Version, IP-Adresse, Relay-Flags, Bandbreite, CPU/RAM, Dateideskriptoren und Accounting-Status. |
| **Graph** | Echtzeit-Graphen für Bandbreite (Up/Down), Verbindungsanzahl oder CPU/Speicher-Auslastung. Zeitintervall und Skalierung sind einstellbar. |
| **Verbindungen** | Liste aller aktiven Tor-Verbindungen mit Typ, Ziel, Land, Nickname und Bandbreite. |
| **Logs** | Tor-Event-Log in Echtzeit mit einstellbaren Log-Leveln und Deduplizierung. |
| **Konfiguration** | Übersicht und Live-Editor für alle Tor-Konfigurationsoptionen. |
| **Torrc** | Syntaxhervorhebung der aktiven `torrc`-Datei. |
| **Interpreter** | Direktzugriff auf den Tor Control Port mit Tab-Vervollständigung und Verlauf. |

---

## Installation

**Aus PyPI:**
```bash
pip install nyx
```

**Aus dem Quellcode:**
```bash
git clone https://git.torproject.org/nyx.git
cd nyx
pip install -e .
```

**Voraussetzungen:**
- Python 3.x
- [`stem`](https://stem.torproject.org/) >= 1.7.0 (wird automatisch installiert)
- Für den GUI-Modus: `PyQt6`

**Tor muss mit aktiviertem Control Port konfiguriert sein** (`/etc/tor/torrc`):
```
ControlPort 9051
CookieAuthentication 1
```

---

## Verwendung

```bash
# Starten (verbindet sich automatisch mit dem lokalen Control Port)
nyx

# Grafisches Interface (PyQt6)
nyx --gui

# Anderen Control Port angeben
nyx -i 9051
nyx -i 192.168.1.1:9051

# Unix Domain Socket verwenden
nyx -s /var/run/tor/control

# Eigene Konfigurationsdatei
nyx -c ~/.nyx/config

# Nur bestimmte Log-Events anzeigen (kommagetrennt)
nyx -l WARN,ERR

# Debug-Ausgabe in Datei schreiben
nyx -d /tmp/nyx-debug.log
```

---

## Tastaturkürzel

### Global (auf allen Seiten)

| Taste | Funktion |
|-------|----------|
| `←` / `→` | Zwischen Seiten/Panels wechseln |
| `h` | Hilfe anzeigen (kontextsensitiv) |
| `m` | Menü öffnen |
| `p` | Anzeige pausieren / fortsetzen |
| `x` | Tor neu laden (`SIGHUP`) |
| `q` | Nyx beenden |

### Im Graph-Panel

| Taste | Funktion |
|-------|----------|
| `↑` / `↓` | Angezeigte Statistik wechseln (Bandbreite / Verbindungen / Ressourcen) |
| `i` | Zeitintervall der Graphen ändern |
| `s` | Skalierungsmodus umschalten |
| `Enter` | Detailansicht öffnen |

### Im Verbindungs-Panel

| Taste | Funktion |
|-------|----------|
| `↑` / `↓` | Verbindung auswählen |
| `Enter` | Details zur Verbindung anzeigen |
| `s` | Sortierung ändern |
| `d` | Descriptor der ausgewählten Verbindung anzeigen |
| `c` | Verbindungstyp filtern |

### Im Log-Panel

| Taste | Funktion |
|-------|----------|
| `↑` / `↓` / `PgUp` / `PgDn` | Scrollen |
| `f` | Filter setzen (Suchbegriff) |
| `e` | Angezeigte Event-Typen auswählen |
| `a` | Alle Events anzeigen / Duplikate ausblenden |
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
| `↑` / `↓` | Befehlsverlauf durchsuchen |
| `Tab` | Auto-Vervollständigung |

---

## Konfiguration

Die Benutzer-Konfiguration liegt unter `~/.nyx/config`. Beispielkonfiguration:

```ini
# Anzahl der gespeicherten Log-Einträge
cache.log_size 1000

# Standard-Graphstatistik beim Start (bandwidth, connections, resources)
graph_stat bandwidth

# Log-Events beim Start
features.log.showDuplicateEntries false
```

Eine kommentierte Beispielkonfiguration liegt im Quellcode unter `nyxrc.sample`.

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
