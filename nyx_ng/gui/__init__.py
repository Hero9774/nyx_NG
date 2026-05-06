# Copyright 2024, The Tor Project
# Copyright 2026, H.Ommen <hero67097@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
PyQt6-based GUI for nyx_ng. Start with: nyx --gui
"""

import os
import re
import subprocess
import sys

import stem.util.log

from nyx_ng.i18n import _

DEFAULT_PORT = 9030


def _read_torrc_control_port():
    """Returns the ControlPort from /etc/tor/torrc, or None if not found."""
    try:
        with open('/etc/tor/torrc', 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#'):
                    continue
                m = re.match(r'^ControlPort\s+(\d+)', line, re.IGNORECASE)
                if m:
                    return int(m.group(1))
    except OSError:
        pass
    return None


def _tor_is_running():
    try:
        result = subprocess.run(['pgrep', '-x', 'tor'], capture_output=True, timeout=2)
        return result.returncode == 0
    except Exception:
        return False


def _ask_control_port(app, style):
    """
    Shows a startup dialog to enter the control port.
    Returns the chosen port, or None if cancelled.
    """
    from PyQt6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel,
        QLineEdit, QPushButton, QMessageBox, QInputDialog
    )
    from PyQt6.QtCore import Qt, QProcess, QTimer
    from PyQt6.QtGui import QIntValidator

    torrc_port = _read_torrc_control_port()
    default_port = torrc_port or DEFAULT_PORT

    dlg = QDialog()
    dlg.setWindowTitle(_('Nyx – Connection'))
    dlg.setMinimumWidth(340)
    dlg.setWindowFlags(dlg.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

    layout = QVBoxLayout(dlg)
    layout.setContentsMargins(20, 16, 20, 16)
    layout.setSpacing(10)

    # --- Tor status row ---
    status_row = QHBoxLayout()
    status_row.addWidget(QLabel(_('Tor-Status:')))
    status_dot = QLabel()
    status_row.addWidget(status_dot)
    status_row.addStretch()
    layout.addLayout(status_row)

    # --- Control port ---
    layout.addWidget(QLabel(_('Tor Control Port:')))
    port_input = QLineEdit(str(default_port))
    port_input.setValidator(QIntValidator(1, 65535, dlg))
    port_input.selectAll()
    layout.addWidget(port_input)

    # --- Button row ---
    btn_row = QHBoxLayout()
    btn_row.setSpacing(8)

    start_btn = QPushButton(_('Tor starten'))
    start_btn.setStyleSheet(
        'QPushButton:enabled { background: #1a4a1a; color: #2ecc71;'
        ' border: 1px solid #2ecc71; border-radius: 3px; padding: 3px 8px; }'
        'QPushButton:enabled:hover { background: #1e5c1e; }'
        'QPushButton:enabled:pressed { background: #0d3a0d; }'
        'QPushButton:disabled { color: #555566; border: 1px solid #333344;'
        ' border-radius: 3px; padding: 3px 8px; }'
    )

    cancel_btn = QPushButton(_('Cancel'))
    connect_btn = QPushButton(_('Connect'))
    connect_btn.setDefault(True)

    btn_row.addWidget(start_btn)
    btn_row.addStretch()
    btn_row.addWidget(cancel_btn)
    btn_row.addWidget(connect_btn)
    layout.addLayout(btn_row)

    _proc = [None]

    def _update_status():
        running = _tor_is_running()
        if running:
            status_dot.setText('●  ' + _('aktiv'))
            status_dot.setStyleSheet('color: #2ecc71; font-weight: bold;')
        else:
            status_dot.setText('●  ' + _('inaktiv'))
            status_dot.setStyleSheet('color: #e74c3c; font-weight: bold;')
        start_btn.setEnabled(not running)
        start_btn.setText(_('Tor starten'))

    def _start_tor():
        password, ok = QInputDialog.getText(
            dlg,
            _('Sudo Password'),
            _('Enter your sudo password to start Tor:'),
            QLineEdit.EchoMode.Password,
        )
        if not ok:
            return

        start_btn.setEnabled(False)
        start_btn.setText(_('▶ Startet…'))

        proc = QProcess(dlg)
        _proc[0] = proc
        proc.start('sudo', ['-S', '-u', 'debian-tor', 'tor'])

        if not proc.waitForStarted(3000):
            QMessageBox.warning(dlg, _('Fehler'),
                                _('Tor konnte nicht gestartet werden.'))
            _update_status()
            return

        proc.write((password + '\n').encode())
        proc.closeWriteChannel()
        del password

        QTimer.singleShot(3000, _update_status)

    _update_status()

    result = [None]

    def _connect():
        text = port_input.text().strip()
        try:
            port = int(text)
            if not (1 <= port <= 65535):
                raise ValueError()
        except ValueError:
            QMessageBox.warning(dlg, _('Invalid Port'),
                                _('Please enter a valid port (1–65535).'))
            return
        result[0] = port
        dlg.accept()

    start_btn.clicked.connect(_start_tor)
    connect_btn.clicked.connect(_connect)
    cancel_btn.clicked.connect(dlg.reject)
    port_input.returnPressed.connect(_connect)

    if dlg.exec() != QDialog.DialogCode.Accepted:
        return None
    return result[0]


def start_gui(args):
    """
    Starts the PyQt6 interface.
    The Tor connection is established via the startup dialog.

    :param args: parsed command line arguments (nyx_ng.arguments.Args)
    """
    os.environ.setdefault('QT_LOGGING_RULES', 'qt.qpa.wayland.textinput.warning=false')

    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
    except ImportError:
        print(_('PyQt6 is not installed. Please install with:\n  pip install PyQt6'))
        sys.exit(1)

    from nyx_ng.gui.main_window import MainWindow
    from nyx_ng.gui.theme import DARK_STYLE
    from nyx_ng import init_controller

    app = QApplication(sys.argv)
    app.setApplicationName('Nyx Tor Monitor')
    app.setStyleSheet(DARK_STYLE)

    controller = None
    while controller is None:
        port = _ask_control_port(app, DARK_STYLE)
        if port is None:
            sys.exit(0)

        try:
            controller = init_controller(control_port=('127.0.0.1', port))
            if controller is None:
                raise RuntimeError(_('No connection possible.'))
        except Exception as exc:
            QMessageBox.critical(
                None,
                _('Connection Error'),
                _('Could not connect to control port %d:\n%s') % (port, exc)
            )
            controller = None

    import nyx_ng.tracker
    nyx_ng.tracker.get_connection_tracker()
    nyx_ng.tracker.get_resource_tracker()
    nyx_ng.tracker.get_consensus_tracker()

    window = MainWindow(controller)
    window.show()

    exit_code = app.exec()

    try:
        nyx_ng.tracker.stop_trackers()
    except Exception as exc:
        stem.util.log.debug(_('Error stopping trackers: %s') % exc)

    sys.exit(exit_code)
