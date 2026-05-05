# Copyright 2024, The Tor Project
# See LICENSE for licensing information

"""
PyQt6-based GUI for nyx_ng. Start with: nyx --gui
"""

import os
import sys

import stem.util.log

from nyx_ng.i18n import _

DEFAULT_PORT = 9030


def _ask_control_port(app, style):
    """
    Shows a startup dialog to enter the control port.
    Returns the chosen port, or None if cancelled.
    """
    from PyQt6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel,
        QLineEdit, QPushButton, QMessageBox
    )
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QIntValidator

    dlg = QDialog()
    dlg.setWindowTitle(_('Nyx – Connection'))
    dlg.setFixedSize(320, 140)
    dlg.setWindowFlags(dlg.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

    layout = QVBoxLayout(dlg)
    layout.setContentsMargins(20, 20, 20, 16)
    layout.setSpacing(12)

    layout.addWidget(QLabel(_('Tor Control Port:')))

    port_input = QLineEdit(str(DEFAULT_PORT))
    port_input.setValidator(QIntValidator(1, 65535, dlg))
    port_input.selectAll()
    layout.addWidget(port_input)

    btn_row = QHBoxLayout()
    btn_row.setSpacing(8)
    cancel_btn = QPushButton(_('Cancel'))
    connect_btn = QPushButton(_('Connect'))
    connect_btn.setDefault(True)
    btn_row.addStretch()
    btn_row.addWidget(cancel_btn)
    btn_row.addWidget(connect_btn)
    layout.addLayout(btn_row)

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
    # Suppress a harmless Qt6/Wayland text-input protocol warning that fires
    # on every menu click: "Got leave event for surface 0x0 with focusing
    # surface ...".  This is Qt bug QTBUG-99331 and does not affect input.
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
