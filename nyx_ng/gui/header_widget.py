# Copyright 2024, The Tor Project
# Copyright 2026, H.Ommen <hero67097@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Header widget: displays Tor status, version, CPU, RAM and relay flags.
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QFrame,
    QPushButton, QDialog, QVBoxLayout, QDialogButtonBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

import nyx_ng
from nyx_ng.i18n import _

VERSION_STATUS_COLORS = {
    'recommended':    '#2ecc71',
    'new':            '#3498db',
    'new in series':  '#3498db',
    'obsolete':       '#e74c3c',
    'old':            '#e74c3c',
    'unrecommended':  '#e74c3c',
    'unknown':        '#c0c0d8',
}

FLAG_COLORS = {
    'Authority': '#e0e0e0', 'BadExit': '#e74c3c', 'BadDirectory': '#e74c3c',
    'Exit': '#1abc9c', 'Fast': '#f39c12', 'Guard': '#2ecc71',
    'HSDir': '#9b59b6', 'Named': '#3498db', 'Stable': '#3498db',
    'Running': '#2ecc71', 'Unnamed': '#9b59b6', 'Valid': '#2ecc71',
    'V2Dir': '#1abc9c', 'V3Dir': '#e0e0e0',
}


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
        self._status_text.setObjectName('status_text')
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
        self._flags_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(self._flags_label)

        layout.addStretch()

        self._port_label = QLabel('')
        self._port_label.setObjectName('status_label')
        self._port_label.setToolTip(_('ORPort / DirPort'))
        layout.addWidget(self._port_label)

        layout.addWidget(_Separator())

        info_btn = QPushButton('Info')
        info_btn.setFixedWidth(48)
        info_btn.setFixedHeight(22)
        info_btn.setStyleSheet(
            'QPushButton { background: #1a1a2e; color: #8888aa; border: 1px solid #2a2a4a;'
            ' border-radius: 3px; font-size: 11px; }'
            'QPushButton:hover { background: #16213e; color: #c0c0d8; }'
            'QPushButton:pressed { background: #0f3460; }'
        )
        info_btn.setToolTip(_('About nyx-ng'))
        info_btn.clicked.connect(self._show_about)
        layout.addWidget(info_btn)

    def update_status(self, data):
        """Updates all labels with data from HeaderWorker."""
        connected = data.get('connected', False)

        if connected:
            self._status_dot.setObjectName('status_connected')
            self._status_dot.setStyleSheet('color: #2ecc71; font-weight: bold;')
            self._status_text.setText(_('Connected'))
            self._status_text.setStyleSheet('color: #ffffff; font-weight: bold; font-size: 14px;')
        else:
            self._status_dot.setObjectName('status_disconnected')
            self._status_dot.setStyleSheet('color: #e74c3c; font-weight: bold;')
            self._status_text.setText(_('Disconnected'))
            self._status_text.setStyleSheet('color: #e74c3c; font-weight: bold; font-size: 14px;')
            return

        version = data.get('version', '')
        version_status = data.get('version_status', 'unknown')
        version_color = VERSION_STATUS_COLORS.get(version_status, '#c0c0d8')
        self._version_label.setText('Tor %s' % version if version else 'Tor –')
        self._version_label.setStyleSheet('color: %s;' % version_color)
        self._version_label.setToolTip(_('Tor version') + ' (%s)' % version_status)

        nickname = data.get('nickname', '')
        fingerprint = data.get('fingerprint', '')
        if nickname:
            nick_text = nickname
            if fingerprint:
                nick_text += ' (%s…)' % fingerprint[:8]
            self._nick_label.setText(nick_text)

        cpu = data.get('cpu', 0.0)
        if cpu >= 80:
            cpu_color = '#e74c3c'
        elif cpu >= 50:
            cpu_color = '#f39c12'
        else:
            cpu_color = '#2ecc71'
        self._cpu_label.setText('CPU: %.1f%%' % cpu)
        self._cpu_label.setStyleSheet('color: %s;' % cpu_color)

        memory = data.get('memory', 0)
        mem_pct = data.get('memory_percent', 0.0)
        if mem_pct >= 80:
            ram_color = '#e74c3c'
        elif mem_pct >= 50:
            ram_color = '#f39c12'
        else:
            ram_color = '#2ecc71'
        self._ram_label.setText('RAM: %s (%.1f%%)' % (_format_bytes(memory), mem_pct))
        self._ram_label.setStyleSheet('color: %s;' % ram_color)

        uptime = data.get('uptime', 0)
        if uptime:
            self._uptime_label.setText(_('Uptime: %s') % _format_uptime(uptime))

        flags = data.get('flags', [])
        if flags:
            parts = []
            for f in flags[:4]:
                color = FLAG_COLORS.get(f, '#c0c0d8')
                parts.append('[<span style="color: %s; font-weight: bold;">%s</span>]' % (color, f))
            self._flags_label.setText(' '.join(parts))
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

    def _show_about(self):
        dlg = QDialog(self)
        dlg.setWindowTitle(_('About nyx-ng'))
        dlg.setMinimumWidth(400)

        layout = QVBoxLayout(dlg)
        layout.setSpacing(10)
        layout.setContentsMargins(24, 20, 24, 16)

        title = QLabel('nyx-ng  v%s' % nyx_ng.__version__)
        f = QFont()
        f.setPointSize(14)
        f.setBold(True)
        title.setFont(f)
        title.setStyleSheet('color: #9b59b6;')
        layout.addWidget(title)

        body = QLabel(
            '<p style="color:#c0c0d8; line-height:1.5;">'
            'Terminal &amp; GUI status monitor for Tor relays.<br><br>'
            '<b style="color:#8888aa;">Author:</b>  H.Ommen '
            '&lt;<a href="mailto:hero67097@gmail.com" style="color:#5dade2;">'
            'hero67097@gmail.com</a>&gt;<br>'
            '<b style="color:#8888aa;">Repository:</b>  '
            '<a href="https://github.com/Hero9774/nyx_NG" style="color:#5dade2;">'
            'github.com/Hero9774/nyx_NG</a><br><br>'
            '<span style="color:#555577;">Licensed under the '
            '<b style="color:#8888aa;">GNU General Public License v3.0 or later</b>'
            ' (GPL-3.0-or-later).<br>'
            'This program is free software; you may redistribute and/or modify it '
            'under the terms of the GPL as published by the Free Software Foundation.'
            '</span></p>'
        )
        body.setOpenExternalLinks(True)
        body.setWordWrap(True)
        body.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(body)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        btns.accepted.connect(dlg.accept)
        layout.addWidget(btns)

        dlg.exec()
