# Copyright 2024, The Tor Project
# See LICENSE for licensing information

"""
Main window of the nyx PyQt6 GUI.
"""

import os
import signal as posix_signal
import sys

from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QToolBar, QWidget, QHBoxLayout,
    QLabel, QPushButton, QMessageBox, QStatusBar, QLineEdit, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QAction, QActionGroup

import stem
import stem.connection
import stem.util.log

import nyx_ng
import nyx_ng.i18n
import nyx_ng.tracker
from nyx_ng import tor_controller, init_controller

from nyx_ng.gui.header_widget import HeaderWidget
from nyx_ng.gui.graph_widget import GraphWidget
from nyx_ng.gui.log_widget import LogWidget
from nyx_ng.gui.connection_widget import ConnectionWidget
from nyx_ng.gui.config_widget import ConfigWidget
from nyx_ng.gui.interpreter_widget import InterpreterWidget
from nyx_ng.gui.workers import (
    HeaderWorker, BandwidthWorker, LogWorker,
    ConnectionWorker, ConfigWorker
)
from nyx_ng.i18n import _


class MainWindow(QMainWindow):
    """Main window with header toolbar, tab content and STOP button."""

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self._controller = controller
        self._workers = []
        self._kill_timer = None

        self.setWindowTitle(_('Nyx – Tor Monitor'))
        self.setMinimumSize(900, 600)
        self.resize(1100, 750)

        self._build_ui()
        self._build_menu()
        self._start_workers()

    def _build_ui(self):
        toolbar = QToolBar('Status', self)
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        self._header = HeaderWidget()
        toolbar.addWidget(self._header)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        toolbar.addWidget(QLabel(_('Control Port:')))
        self._port_input = QLineEdit('9051')
        self._port_input.setMaximumWidth(80)
        self._port_input.setToolTip(_('Tor control port (default: 9051)'))
        self._port_input.returnPressed.connect(self._connect_to_tor)
        toolbar.addWidget(self._port_input)

        self._connect_btn = QPushButton(_('Connect'))
        self._connect_btn.setObjectName('connect_button')
        self._connect_btn.setToolTip(_('Connect to the specified Tor control port'))
        self._connect_btn.clicked.connect(self._connect_to_tor)
        toolbar.addWidget(self._connect_btn)

        sep = QWidget()
        sep.setMinimumWidth(12)
        toolbar.addWidget(sep)

        self._stop_btn = QPushButton(_('STOP TOR'))
        self._stop_btn.setObjectName('stop_button')
        self._stop_btn.setToolTip(_('Safely stop Tor process (SIGTERM → SIGKILL)'))
        self._stop_btn.clicked.connect(self._stop_tor)
        toolbar.addWidget(self._stop_btn)

        self._tabs = QTabWidget()
        self.setCentralWidget(self._tabs)

        self._graph_widget = GraphWidget()
        self._tabs.addTab(self._graph_widget, _('Graph'))

        self._log_widget = LogWidget()
        self._tabs.addTab(self._log_widget, _('Log'))

        self._conn_widget = ConnectionWidget()
        self._tabs.addTab(self._conn_widget, _('Connections'))

        self._config_widget = ConfigWidget()
        self._tabs.addTab(self._config_widget, _('Configuration'))

        self._interpreter_widget = InterpreterWidget()
        self._tabs.addTab(self._interpreter_widget, _('Shell'))

        self._statusbar = QStatusBar()
        self._statusbar.showMessage(_('Ready.'))
        self.setStatusBar(self._statusbar)

    def _build_menu(self):
        menubar = self.menuBar()
        view_menu = menubar.addMenu(_('View'))
        lang_menu = view_menu.addMenu(_('Language'))

        self._lang_group = QActionGroup(self)
        self._lang_group.setExclusive(True)
        current = nyx_ng.i18n.get_language()

        for code, label in [('en', 'English'), ('de', 'Deutsch')]:
            action = QAction(label, self)
            action.setCheckable(True)
            action.setChecked(code == current)
            action.triggered.connect(lambda checked, c=code: self._change_language(c))
            self._lang_group.addAction(action)
            lang_menu.addAction(action)

    def _change_language(self, lang):
        nyx_ng.set_language(lang)
        self._statusbar.showMessage(_('Language changed. Restart nyx for full effect.'))

    def _start_workers(self):
        self._disconnect_worker_signals()

        self._header_worker = HeaderWorker()
        self._header_worker.status_updated.connect(self._header.update_status)
        self._header_worker.start()
        self._workers.append(self._header_worker)

        self._bw_worker = BandwidthWorker()
        self._bw_worker.bw_updated.connect(self._graph_widget.add_bandwidth)
        self._bw_worker.start()
        self._workers.append(self._bw_worker)

        self._log_worker = LogWorker()
        self._log_worker.log_entry.connect(self._log_widget.add_log_entry)
        self._log_worker.start()
        self._workers.append(self._log_worker)

        self._conn_worker = ConnectionWorker()
        self._conn_worker.connections_updated.connect(self._conn_widget.update_connections)
        self._conn_worker.start()
        self._workers.append(self._conn_worker)

        self._config_worker = ConfigWorker()
        self._config_worker.config_loaded.connect(self._config_widget.load_config)
        self._config_worker.start()
        self._workers.append(self._config_worker)

    def _disconnect_worker_signals(self):
        """Disconnect signals from running workers to prevent duplicate slots."""
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

    def _connect_to_tor(self):
        port_text = self._port_input.text().strip()
        try:
            port = int(port_text)
            if not (1 <= port <= 65535):
                raise ValueError()
        except ValueError:
            QMessageBox.warning(self, _('Invalid Port'),
                                _('Please enter a valid port (1–65535).'))
            return

        self._connect_btn.setEnabled(False)
        self._connect_btn.setText(_('Connecting…'))
        self._statusbar.showMessage(_('Connecting to control port %d…') % port)

        try:
            controller = init_controller(control_port=('127.0.0.1', port))
            if controller is None:
                raise RuntimeError(_('Connection failed.'))
        except Exception as exc:
            self._connect_btn.setEnabled(True)
            self._connect_btn.setText(_('Connect'))
            self._statusbar.showMessage(_('Connection failed: %s') % exc)
            QMessageBox.critical(self, _('Connection Error'),
                                 _('Could not connect to port %d:\n%s') % (port, exc))
            return

        self._stop_workers()
        self._workers.clear()
        self._start_workers()

        self._connect_btn.setEnabled(True)
        self._connect_btn.setText(_('Connect'))
        self._statusbar.showMessage(_('Connected to control port %d.') % port)

    def _stop_tor(self):
        reply = QMessageBox.question(
            self,
            _('Stop Tor'),
            _('Really stop Tor?\n\nThe process will be terminated cleanly (SIGTERM).\nIf necessary, SIGKILL will be sent after 5 seconds.'),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self._stop_btn.setEnabled(False)
        self._stop_btn.setText(_('⏹  Stopping…'))
        self._statusbar.showMessage(_('Sending HALT to Tor…'))

        controller = tor_controller()
        pid = controller.get_pid(None) if controller else None

        halted_via_signal = False
        if controller and controller.is_alive():
            try:
                controller.signal(stem.Signal.HALT)
                halted_via_signal = True
                stem.util.log.notice('HALT signal sent to Tor.')
            except Exception as exc:
                stem.util.log.warn('Could not send HALT signal: %s' % exc)

        if pid:
            self._pending_pid = pid
            self._kill_timer = QTimer(self)
            self._kill_timer.setSingleShot(True)
            self._kill_timer.timeout.connect(self._sigterm_tor)
            self._kill_timer.start(5000)
            self._statusbar.showMessage(_('Waiting for Tor process (PID %d)…') % pid)
        else:
            self._statusbar.showMessage(_('Tor process not found.'))

    def _sigterm_tor(self):
        pid = getattr(self, '_pending_pid', None)
        if pid is None:
            return

        if not _process_alive(pid):
            self._statusbar.showMessage(_('Tor (PID %d) has exited.') % pid)
            self._stop_btn.setText(_('⏹  Tor stopped'))
            return

        stem.util.log.notice('Sending SIGTERM to PID %d…' % pid)
        self._statusbar.showMessage(_('Sending SIGTERM to PID %d…') % pid)

        try:
            os.kill(pid, posix_signal.SIGTERM)
        except ProcessLookupError:
            self._statusbar.showMessage(_('Tor (PID %d) already exited.') % pid)
            self._stop_btn.setText(_('⏹  Tor stopped'))
            return

        self._kill_timer = QTimer(self)
        self._kill_timer.setSingleShot(True)
        self._kill_timer.timeout.connect(self._sigkill_tor)
        self._kill_timer.start(5000)

    def _sigkill_tor(self):
        pid = getattr(self, '_pending_pid', None)
        if pid is None:
            return

        if not _process_alive(pid):
            self._statusbar.showMessage(_('Tor (PID %d) has exited.') % pid)
            self._stop_btn.setText(_('⏹  Tor stopped'))
            return

        stem.util.log.warn(_('Tor not responding – sending SIGKILL to PID %d.') % pid)
        self._statusbar.showMessage(_('Sending SIGKILL to PID %d…') % pid)

        try:
            os.kill(pid, posix_signal.SIGKILL)
            self._statusbar.showMessage(_('Tor (PID %d) force-killed.') % pid)
        except ProcessLookupError:
            self._statusbar.showMessage(_('Tor (PID %d) already exited.') % pid)

        self._stop_btn.setText(_('⏹  Tor stopped'))

    def closeEvent(self, event):
        self._stop_workers()
        super().closeEvent(event)


def _process_alive(pid):
    """Returns True if a process with the given PID still exists."""
    try:
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, PermissionError):
        return False
