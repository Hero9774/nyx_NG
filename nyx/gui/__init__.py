# Copyright 2024, The Tor Project
# See LICENSE for licensing information

"""
PyQt6-basierte GUI für nyx.

Starten mit: nyx --gui
"""

import sys

import stem.util.log

DEFAULT_PORT = 9030


def _ask_control_port(app, style):
    """
    Zeigt einen Startdialog zur Eingabe des Kontrollports.
    Gibt den gewählten Port zurück, oder None bei Abbruch.
    """
    from PyQt6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel,
        QLineEdit, QPushButton, QMessageBox
    )
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QIntValidator

    dlg = QDialog()
    dlg.setWindowTitle('Nyx – Verbindung')
    dlg.setFixedSize(320, 140)
    dlg.setWindowFlags(dlg.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

    layout = QVBoxLayout(dlg)
    layout.setContentsMargins(20, 20, 20, 16)
    layout.setSpacing(12)

    layout.addWidget(QLabel('Tor Kontrollport:'))

    port_input = QLineEdit(str(DEFAULT_PORT))
    port_input.setValidator(QIntValidator(1, 65535, dlg))
    port_input.selectAll()
    layout.addWidget(port_input)

    btn_row = QHBoxLayout()
    btn_row.setSpacing(8)
    cancel_btn = QPushButton('Abbrechen')
    connect_btn = QPushButton('Verbinden')
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
            QMessageBox.warning(dlg, 'Ungültiger Port',
                                'Bitte einen gültigen Port (1–65535) eingeben.')
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
    Startet die PyQt6-Oberfläche.
    Die Tor-Verbindung wird über den Startdialog hergestellt.

    :param args: geparste Kommandozeilenargumente (nyx.arguments.Args)
    """
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
    except ImportError:
        print('PyQt6 ist nicht installiert. Bitte installieren mit:\n'
              '  pip install PyQt6')
        sys.exit(1)

    from nyx.gui.main_window import MainWindow
    from nyx.gui.theme import DARK_STYLE
    from nyx import init_controller

    app = QApplication(sys.argv)
    app.setApplicationName('Nyx Tor Monitor')
    app.setStyleSheet(DARK_STYLE)

    # Kontrollport abfragen – Schleife bis Verbindung klappt oder Abbruch
    controller = None
    while controller is None:
        port = _ask_control_port(app, DARK_STYLE)
        if port is None:
            sys.exit(0)

        try:
            controller = init_controller(control_port=('127.0.0.1', port))
            if controller is None:
                raise RuntimeError('Keine Verbindung möglich.')
        except Exception as exc:
            QMessageBox.critical(
                None,
                'Verbindungsfehler',
                'Konnte nicht mit Kontrollport %d verbinden:\n%s' % (port, exc)
            )
            controller = None

    # Tor-Tracker initialisieren – get_*_tracker() startet sie beim ersten Aufruf bereits
    import nyx.tracker
    nyx.tracker.get_connection_tracker()
    nyx.tracker.get_resource_tracker()
    nyx.tracker.get_consensus_tracker()

    window = MainWindow(controller)
    window.show()

    exit_code = app.exec()

    # Aufräumen
    try:
        nyx.tracker.stop_trackers()
    except Exception as exc:
        stem.util.log.debug('Fehler beim Stoppen der Tracker: %s' % exc)

    sys.exit(exit_code)
