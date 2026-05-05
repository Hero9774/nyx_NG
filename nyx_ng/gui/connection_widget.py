# Copyright 2024, The Tor Project
# Copyright 2026, H.Ommen <kalkseniaya@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Connection list: displays active Tor connections as a sortable table.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QLineEdit, QHeaderView, QDialog, QTextEdit,
    QDialogButtonBox
)
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QColor, QFont, QIcon

from nyx_ng.gui.theme import CONNECTION_COLORS
from nyx_ng.flags import get_flag_pixmap
from nyx_ng.i18n import _


class _DetailDialog(QDialog):
    """Shows details for a connection."""

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_('Connection Details'))
        self.setMinimumSize(500, 300)

        layout = QVBoxLayout(self)
        text = QTextEdit()
        text.setReadOnly(True)
        text.setFont(QFont('Courier New', 11))

        fields = [
            (_('Type'),        data.get('type', '')),
            (_('Local'),       data.get('local', '')),
            (_('Remote'),      data.get('remote', '')),
            ('Fingerprint',    data.get('fingerprint', '–')),
            ('Nickname',       data.get('nickname', '–')),
            (_('Country'),     data.get('country') or data.get('country_code') or '–'),
            (_('Uptime'),      '%ss' % data.get('uptime', 0)),
        ]
        width = max(len(k) for k, v in fields)
        lines = ['%-*s  %s' % (width, k + ':', v) for k, v in fields]
        text.setPlainText('\n'.join(lines))
        layout.addWidget(text)

        btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btn.rejected.connect(self.accept)
        layout.addWidget(btn)


class ConnectionWidget(QWidget):
    """Tab widget for active Tor connections."""

    _DEFAULT_PROPORTIONS = [0.08, 0.20, 0.20, 0.18, 0.20, 0.14]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_data = []
        self._column_proportions = None
        self._resizing_programmatically = False
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel(_('Search:')))

        self._search = QLineEdit()
        self._search.setPlaceholderText(_('IP, Nickname, Country…'))
        self._search.setMaximumWidth(250)
        self._search.textChanged.connect(self._apply_filter)
        toolbar.addWidget(self._search)

        toolbar.addStretch()
        self._count_label = QLabel(_('0 connections'))
        self._count_label.setStyleSheet('color: #6666aa;')
        toolbar.addWidget(self._count_label)
        layout.addLayout(toolbar)

        columns = [_('Type'), _('Local'), _('Remote'), 'Nickname', _('Country'), _('Uptime')]
        self._table = QTableWidget(0, len(columns))
        self._table.setHorizontalHeaderLabels(columns)
        self._table.setFont(QFont('Courier New', 11))
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(False)

        header = self._table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setMinimumSectionSize(40)
        header.setStretchLastSection(False)
        header.sectionResized.connect(self._on_section_resized)

        self._table.setSortingEnabled(True)
        self._table.doubleClicked.connect(self._show_details)
        self._table.verticalHeader().setDefaultSectionSize(26)
        self._table.setIconSize(QSize(28, 21))
        layout.addWidget(self._table)

    def _on_section_resized(self, logical_index, old_size, new_size):
        if self._resizing_programmatically:
            return
        total = sum(self._table.columnWidth(i) for i in range(self._table.columnCount()))
        if total > 0:
            self._column_proportions = [
                self._table.columnWidth(i) / total
                for i in range(self._table.columnCount())
            ]

    def _apply_column_widths(self):
        total = self._table.viewport().width()
        if total <= 0:
            return
        self._resizing_programmatically = True
        props = self._column_proportions or self._DEFAULT_PROPORTIONS
        for i, prop in enumerate(props):
            self._table.setColumnWidth(i, max(40, int(total * prop)))
        self._resizing_programmatically = False

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_column_widths()

    def showEvent(self, event):
        super().showEvent(event)
        self._apply_column_widths()

    def _apply_filter(self, text):
        text = text.lower()
        for row in range(self._table.rowCount()):
            match = False
            for col in range(self._table.columnCount()):
                item = self._table.item(row, col)
                if item and text in item.text().lower():
                    match = True
                    break
            self._table.setRowHidden(row, not match if text else False)

    def _show_details(self, index):
        row = index.row()
        if row < len(self._current_data):
            dlg = _DetailDialog(self._current_data[row], self)
            dlg.exec()

    def update_connections(self, connections):
        """Called by ConnectionWorker via signal-slot."""
        self._current_data = connections
        self._table.setSortingEnabled(False)
        self._table.setRowCount(len(connections))

        for row, data in enumerate(connections):
            conn_type = data.get('type', 'OUTBOUND')
            color = QColor(CONNECTION_COLORS.get(conn_type, '#e0e0e0'))

            values = [
                conn_type,
                data.get('local', ''),
                data.get('remote', ''),
                data.get('nickname', '–'),
                data.get('country', '–'),
                '%ds' % data.get('uptime', 0),
            ]

            for col, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setForeground(color)

                if col == 4:
                    code = data.get('country_code', '')
                    pixmap = get_flag_pixmap(code) if code else None
                    if pixmap:
                        item.setIcon(QIcon(pixmap))

                self._table.setItem(row, col, item)

        self._table.setSortingEnabled(True)
        self._count_label.setText(_('%d connections') % len(connections))

        text = self._search.text()
        if text:
            self._apply_filter(text)
