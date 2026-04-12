# Copyright 2024, The Tor Project
# See LICENSE for licensing information

"""
Hauptfenster der nyx PyQt6-GUI.
"""

import os
import signal as posix_signal
import sys

from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QToolBar, QWidget, QHBoxLayout,
    QLabel, QPushButton, QMessageBox, QStatusBar, QLineEdit, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon

import stem
import stem.connection
import stem.util.log

import nyx.tracker
from nyx import tor_controller, init_controller

from nyx.gui.header_widget import HeaderWidget
from nyx.gui.graph_widget import GraphWidget
from nyx.gui.log_widget import LogWidget
from nyx.gui.connection_widget import ConnectionWidget
from nyx.gui.config_widget import ConfigWidget
from nyx.gui.interpreter_widget import InterpreterWidget
from nyx.gui.workers import (
    HeaderWorker, BandwidthWorker, LogWorker,
    ConnectionWorker, ConfigWorker
)


class MainWindow(QMainWindow):
    """
    Hauptfenster mit Header-Toolbar, Tab-Inhalt und STOP-Button.
    """

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self._controller = controller
        self._workers = []
        self._kill_timer = None

        self.setWindowTitle('Nyx – Tor Monitor')
        self.setMinimumSize(900, 600)
        self.resize(1100, 750)

        self._build_ui()
        self._start_workers()

    def _build_ui(self):
        # === Toolbar oben ===
        toolbar = QToolBar('Status', self)
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        self._header = HeaderWidget()
        toolbar.addWidget(self._header)

        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        # Kontrollport-Feld
        toolbar.addWidget(QLabel('Kontrollport:'))
        self._port_input = QLineEdit('9051')
        self._port_input.setMaximumWidth(80)
        self._port_input.setToolTip('Tor-Kontrollport (Standard: 9051)')
        self._port_input.returnPressed.connect(self._connect_to_tor)
        toolbar.addWidget(self._port_input)

        # Verbinden-Button
        self._connect_btn = QPushButton('Verbinden')
        self._connect_btn.setObjectName('connect_button')
        self._connect_btn.setToolTip('Mit dem angegebenen Tor-Kontrollport verbinden')
        self._connect_btn.clicked.connect(self._connect_to_tor)
        toolbar.addWidget(self._connect_btn)

        # Trenner
        sep = QWidget()
        sep.setMinimumWidth(12)
        toolbar.addWidget(sep)

        # STOP-Button
        self._stop_btn = QPushButton('TOR STOPPEN')
        self._stop_btn.setObjectName('stop_button')
        self._stop_btn.setToolTip('Tor-Prozess sicher beenden (SIGTERM → SIGKILL)')
        self._stop_btn.clicked.connect(self._stop_tor)
        toolbar.addWidget(self._stop_btn)

        # === Tab-Widget ===
        self._tabs = QTabWidget()
        self.setCentralWidget(self._tabs)

        self._graph_widget = GraphWidget()
        self._tabs.addTab(self._graph_widget, 'Graph')

        self._log_widget = LogWidget()
        self._tabs.addTab(self._log_widget, 'Log')

        self._conn_widget = ConnectionWidget()
        self._tabs.addTab(self._conn_widget, 'Verbindungen')

        self._config_widget = ConfigWidget()
        self._tabs.addTab(self._config_widget, 'Konfiguration')

        self._interpreter_widget = InterpreterWidget()
        self._tabs.addTab(self._interpreter_widget, 'Shell')

        # === Statusleiste ===
        self._statusbar = QStatusBar()
        self._statusbar.showMessage('Bereit.')
        self.setStatusBar(self._statusbar)

    def _start_workers(self):
        # Vor dem Erstellen neuer Worker: alte Signale trennen
        self._disconnect_worker_signals()

        # Header-Worker
        self._header_worker = HeaderWorker()
        self._header_worker.status_updated.connect(self._header.update_status)
        self._header_worker.start()
        self._workers.append(self._header_worker)

        # Bandbreiten-Worker
        self._bw_worker = BandwidthWorker()
        self._bw_worker.bw_updated.connect(self._graph_widget.add_bandwidth)
        self._bw_worker.start()
        self._workers.append(self._bw_worker)

        # Log-Worker
        self._log_worker = LogWorker()
        self._log_worker.log_entry.connect(self._log_widget.add_log_entry)
        self._log_worker.start()
        self._workers.append(self._log_worker)

        # Verbindungs-Worker
        self._conn_worker = ConnectionWorker()
        self._conn_worker.connections_updated.connect(self._conn_widget.update_connections)
        self._conn_worker.start()
        self._workers.append(self._conn_worker)

        # Konfigurations-Worker (einmalig)
        self._config_worker = ConfigWorker()
        self._config_worker.config_loaded.connect(self._config_widget.load_config)
        self._config_worker.start()
        self._workers.append(self._config_worker)

    def _disconnect_worker_signals(self):
        """Trennt Signale laufender Worker gezielt, um Doppel-Slots zu verhindern."""
        for worker in self._workers:
            try:
                if isinstance(worker, HeaderWorker):
                    worker.status_updated.disconnect()
                elif isinstance(worker, BandwidthWorker):
                    worker.bw_updated.disconnect()
                elif isinstance(worker, LogWorker):
                    worker.log_entry.disconnect()
                elif isinstance(worker, ConnectionWorker):
                    worker.connections_updated.disconnect()
                elif isinstance(worker, ConfigWorker):
                    worker.config_loaded.disconnect()
            except (TypeError, RuntimeError):
                pass

    def _stop_workers(self):
        self._disconnect_worker_signals()
        for worker in self._workers:
            try:
                if hasattr(worker, 'stop'):
                    worker.stop()
                worker.quit()
                worker.wait(2000)
            except Exception:
                pass

    # =========================================================
    # Verbinden: Verbindung zum Tor-Controller (neu) aufbauen
    # =========================================================

    def _connect_to_tor(self):
        port_text = self._port_input.text().strip()
        try:
            port = int(port_text)
            if not (1 <= port <= 65535):
                raise ValueError()
        except ValueError:
            QMessageBox.warning(self, 'Ungültiger Port',
                                'Bitte einen gültigen Port (1–65535) eingeben.')
            return

        self._connect_btn.setEnabled(False)
        self._connect_btn.setText('Verbinde…')
        self._statusbar.showMessage('Verbinde mit Kontrollport %d…' % port)

        try:
            controller = init_controller(control_port=('127.0.0.1', port))
            if controller is None:
                raise RuntimeError('Verbindung fehlgeschlagen.')
        except Exception as exc:
            self._connect_btn.setEnabled(True)
            self._connect_btn.setText('Verbinden')
            self._statusbar.showMessage('Verbindung fehlgeschlagen: %s' % exc)
            QMessageBox.critical(self, 'Verbindungsfehler',
                                 'Konnte nicht mit Port %d verbinden:\n%s' % (port, exc))
            return

        # Alte Worker stoppen
        self._stop_workers()
        self._workers.clear()

        # Neue Worker starten
        self._start_workers()

        self._connect_btn.setEnabled(True)
        self._connect_btn.setText('Verbinden')
        self._statusbar.showMessage('Verbunden mit Kontrollport %d.' % port)

    # =========================================================
    # STOP-Button: Graceful Shutdown mit Bestätigung
    # =========================================================

    def _stop_tor(self):
        reply = QMessageBox.question(
            self,
            'Tor beenden',
            'Tor-Server wirklich beenden?\n\n'
            'Der Prozess wird zuerst sauber beendet (SIGTERM).\n'
            'Falls nötig, wird nach 5 Sekunden SIGKILL gesendet.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self._stop_btn.setEnabled(False)
        self._stop_btn.setText('⏹  Beende…')
        self._statusbar.showMessage('Sende HALT an Tor…')

        controller = tor_controller()
        pid = controller.get_pid(None) if controller else None

        # 1. Sauberes Beenden via Control-Protokoll
        halted_via_signal = False
        if controller and controller.is_alive():
            try:
                controller.signal(stem.Signal.HALT)
                halted_via_signal = True
                stem.util.log.notice('HALT-Signal an Tor gesendet.')
            except Exception as exc:
                stem.util.log.warn('Konnte HALT-Signal nicht senden: %s' % exc)

        if pid:
            # 2. Nach 5s: SIGTERM wenn Prozess noch läuft
            self._pending_pid = pid
            self._kill_timer = QTimer(self)
            self._kill_timer.setSingleShot(True)
            self._kill_timer.timeout.connect(self._sigterm_tor)
            self._kill_timer.start(5000)
            self._statusbar.showMessage('Warte auf Tor-Prozess (PID %d)…' % pid)
        else:
            self._statusbar.showMessage('Tor-Prozess nicht gefunden.')

    def _sigterm_tor(self):
        pid = getattr(self, '_pending_pid', None)
        if pid is None:
            return

        if not _process_alive(pid):
            self._statusbar.showMessage('Tor (PID %d) wurde beendet.' % pid)
            self._stop_btn.setText('⏹  Tor gestoppt')
            return

        stem.util.log.notice('Sende SIGTERM an PID %d…' % pid)
        self._statusbar.showMessage('Sende SIGTERM an PID %d…' % pid)

        try:
            os.kill(pid, posix_signal.SIGTERM)
        except ProcessLookupError:
            self._statusbar.showMessage('Tor (PID %d) bereits beendet.' % pid)
            self._stop_btn.setText('⏹  Tor gestoppt')
            return

        # 3. Nach weiteren 5s: SIGKILL falls immer noch aktiv
        self._kill_timer = QTimer(self)
        self._kill_timer.setSingleShot(True)
        self._kill_timer.timeout.connect(self._sigkill_tor)
        self._kill_timer.start(5000)

    def _sigkill_tor(self):
        pid = getattr(self, '_pending_pid', None)
        if pid is None:
            return

        if not _process_alive(pid):
            self._statusbar.showMessage('Tor (PID %d) wurde beendet.' % pid)
            self._stop_btn.setText('⏹  Tor gestoppt')
            return

        stem.util.log.warn('Tor reagiert nicht – sende SIGKILL an PID %d.' % pid)
        self._statusbar.showMessage('Sende SIGKILL an PID %d…' % pid)

        try:
            os.kill(pid, posix_signal.SIGKILL)
            self._statusbar.showMessage('Tor (PID %d) zwangsbeendet.' % pid)
        except ProcessLookupError:
            self._statusbar.showMessage('Tor (PID %d) bereits beendet.' % pid)

        self._stop_btn.setText('⏹  Tor gestoppt')

    # =========================================================
    # Fenster schließen
    # =========================================================

    def closeEvent(self, event):
        self._stop_workers()
        super().closeEvent(event)


def _process_alive(pid):
    """Prüft ob ein Prozess mit der gegebenen PID noch existiert."""
    try:
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, PermissionError):
        return False
