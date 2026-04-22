# Copyright 2024, The Tor Project
# See LICENSE for licensing information

"""
Header widget: displays Tor status, version, CPU, RAM and relay flags.
"""

import time

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt

from nyx.i18n import _


def _format_uptime(seconds):
    if seconds < 60:
        return '%ds' % seconds
    elif seconds < 3600:
        return '%dm %ds' % (seconds // 60, seconds % 60)
    elif seconds < 86400:
        return '%dh %dm' % (seconds // 3600, (seconds % 3600) // 60)
    else:
        return '%dd %dh' % (seconds // 86400, (seconds % 86400) // 3600)


def _format_bytes(b):
    if b < 1024:
        return '%d B' % b
    elif b < 1024 * 1024:
        return '%.1f KB' % (b / 1024)
    elif b < 1024 * 1024 * 1024:
        return '%.1f MB' % (b / (1024 * 1024))
    else:
        return '%.2f GB' % (b / (1024 * 1024 * 1024))


class _Separator(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.VLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setStyleSheet('color: #0f3460;')


class HeaderWidget(QWidget):
    """Permanently displays Tor status in the toolbar."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        self._status_dot = QLabel('●')
        self._status_dot.setObjectName('status_disconnected')
        self._status_dot.setToolTip(_('Connection status'))
        layout.addWidget(self._status_dot)

        self._status_text = QLabel(_('Disconnected'))
        self._status_text.setObjectName('status_label')
        layout.addWidget(self._status_text)

        layout.addWidget(_Separator())

        self._version_label = QLabel('Tor –')
        self._version_label.setObjectName('status_label')
        self._version_label.setToolTip(_('Tor version'))
        layout.addWidget(self._version_label)

        layout.addWidget(_Separator())

        self._nick_label = QLabel('–')
        self._nick_label.setObjectName('status_label')
        self._nick_label.setToolTip(_('Relay nickname'))
        layout.addWidget(self._nick_label)

        layout.addWidget(_Separator())

        self._cpu_label = QLabel('CPU: –')
        self._cpu_label.setObjectName('status_label')
        self._cpu_label.setToolTip(_('Tor CPU usage'))
        layout.addWidget(self._cpu_label)

        layout.addWidget(_Separator())

        self._ram_label = QLabel('RAM: –')
        self._ram_label.setObjectName('status_label')
        self._ram_label.setToolTip(_('Tor memory usage'))
        layout.addWidget(self._ram_label)

        layout.addWidget(_Separator())

        self._uptime_label = QLabel(_('Uptime: –'))
        self._uptime_label.setObjectName('status_label')
        self._uptime_label.setToolTip(_('Tor process uptime'))
        layout.addWidget(self._uptime_label)

        layout.addWidget(_Separator())

        self._flags_label = QLabel('')
        self._flags_label.setObjectName('status_label')
        self._flags_label.setToolTip(_('Relay flags from consensus'))
        layout.addWidget(self._flags_label)

        layout.addStretch()

        self._port_label = QLabel('')
        self._port_label.setObjectName('status_label')
        self._port_label.setToolTip(_('ORPort / DirPort'))
        layout.addWidget(self._port_label)

    def update_status(self, data):
        """Updates all labels with data from HeaderWorker."""
        connected = data.get('connected', False)

        if connected:
            self._status_dot.setObjectName('status_connected')
            self._status_dot.setStyleSheet('color: #2ecc71; font-weight: bold;')
            self._status_text.setText(_('Connected'))
        else:
            self._status_dot.setObjectName('status_disconnected')
            self._status_dot.setStyleSheet('color: #e74c3c; font-weight: bold;')
            self._status_text.setText(_('Disconnected'))
            return

        version = data.get('version', '')
        self._version_label.setText('Tor %s' % version if version else 'Tor –')

        nickname = data.get('nickname', '')
        fingerprint = data.get('fingerprint', '')
        if nickname:
            nick_text = nickname
            if fingerprint:
                nick_text += ' (%s…)' % fingerprint[:8]
            self._nick_label.setText(nick_text)

        cpu = data.get('cpu', 0.0)
        self._cpu_label.setText('CPU: %.1f%%' % cpu)

        memory = data.get('memory', 0)
        mem_pct = data.get('memory_percent', 0.0)
        self._ram_label.setText('RAM: %s (%.1f%%)' % (_format_bytes(memory), mem_pct))

        uptime = data.get('uptime', 0)
        if uptime:
            self._uptime_label.setText(_('Uptime: %s') % _format_uptime(uptime))

        flags = data.get('flags', [])
        if flags:
            self._flags_label.setText(' '.join('[%s]' % f for f in flags[:4]))
        else:
            self._flags_label.setText('')

        or_port = data.get('or_port', '')
        dir_port = data.get('dir_port', '')
        ports = []
        if or_port:
            ports.append('OR:%s' % or_port)
        if dir_port:
            ports.append('Dir:%s' % dir_port)
        if ports:
            self._port_label.setText(' | '.join(ports))
