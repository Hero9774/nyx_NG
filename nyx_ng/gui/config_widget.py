# Copyright 2024, The Tor Project
# Copyright 2026, H.Ommen <hero67097@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Configuration table: displays Tor options and allows editing.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QLineEdit, QHeaderView, QInputDialog, QMessageBox,
    QMenu, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont

import stem.util.log
from nyx_ng import tor_controller
from nyx_ng.i18n import _


class ConfigWidget(QWidget):
    """Tab widget for Tor configuration options."""

    _DEFAULT_PROPORTIONS = [0.32, 0.40, 0.16, 0.12]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._all_data = []
        self._filter_text = ''
        self._show_only_set = False
        self._column_proportions = None
        self._resizing_programmatically = False
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel(_('Search:')))

        self._search = QLineEdit()
        self._search.setPlaceholderText(_('Option name…'))
        self._search.setMaximumWidth(250)
        self._search.textChanged.connect(self._apply_filter)
        toolbar.addWidget(self._search)

        self._set_only_cb = QCheckBox(_('Only modified'))
        self._set_only_cb.toggled.connect(self._toggle_set_only)
        toolbar.addWidget(self._set_only_cb)

        toolbar.addStretch()

        self._count_label = QLabel(_('Loading…'))
        self._count_label.setStyleSheet('color: #6666aa;')
        toolbar.addWidget(self._count_label)

        layout.addLayout(toolbar)

        columns = [_('Option'), _('Value'), _('Type'), _('Modified')]
        self._table = QTableWidget(0, len(columns))
        self._table.setHorizontalHeaderLabels(columns)
        self._table.setFont(QFont('Courier New', 11))
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSortingEnabled(True)

        header = self._table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setMinimumSectionSize(40)
        header.setStretchLastSection(False)
        header.sectionResized.connect(self._on_section_resized)

        self._table.doubleClicked.connect(self._edit_value)
        self._table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._context_menu)

        layout.addWidget(self._table)

        hint = QLabel(_('Double-click: edit value  |  Right-click: reset'))
        hint.setStyleSheet('color: #555577; font-size: 11px;')
        layout.addWidget(hint)

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

    def _toggle_set_only(self, checked):
        self._show_only_set = checked
        self._rebuild_table()

    def _apply_filter(self, text):
        self._filter_text = text.lower()
        self._rebuild_table()

    def _rebuild_table(self):
        self._table.setSortingEnabled(False)
        self._table.setRowCount(0)
        shown = 0

        for row_data in self._all_data:
            name = row_data.get('name', '')
            is_set = row_data.get('is_set', False)

            if self._show_only_set and not is_set:
                continue
            if self._filter_text and self._filter_text not in name.lower():
                continue

            row = self._table.rowCount()
            self._table.insertRow(row)
            self._fill_row(row, row_data)
            shown += 1

        self._table.setSortingEnabled(True)
        self._count_label.setText(_('%d / %d options') % (shown, len(self._all_data)))

    def _fill_row(self, row, data):
        name = data.get('name', '')
        value = data.get('value', '')
        vtype = data.get('type', '')
        is_set = data.get('is_set', False)

        color = QColor('#7b2fbe') if is_set else QColor('#e0e0e0')

        items = [name, value, vtype, '✓' if is_set else '']
        for col, text in enumerate(items):
            item = QTableWidgetItem(text)
            item.setForeground(color)
            self._table.setItem(row, col, item)

    def _edit_value(self, index):
        row = index.row()
        name_item = self._table.item(row, 0)
        value_item = self._table.item(row, 1)
        if not name_item:
            return

        name = name_item.text()
        current = value_item.text() if value_item else ''
        if current == '<default>':
            current = ''

        new_val, ok = QInputDialog.getText(
            self, _('Edit Value'),
            _('New value for "%s":') % name,
            text=current
        )

        if ok and new_val != current:
            try:
                controller = tor_controller()
                if controller is None:
                    QMessageBox.warning(self, _('Error'), _('No Tor connection available.'))
                    return
                controller.set_conf(name, new_val)
                value_item.setText(new_val)
                name_item.setForeground(QColor('#7b2fbe'))
                self._table.item(row, 3).setText('✓')
                stem.util.log.notice('Config set: %s = %s' % (name, new_val))
            except Exception as exc:
                QMessageBox.warning(self, _('Error'),
                                    _('Could not set "%s":\n%s') % (name, exc))

    def _context_menu(self, pos):
        row = self._table.rowAt(pos.y())
        if row < 0:
            return

        name_item = self._table.item(row, 0)
        if not name_item:
            return

        name = name_item.text()
        menu = QMenu(self)
        reset_action = menu.addAction(_('Reset "%s"') % name)
        action = menu.exec(self._table.mapToGlobal(pos))

        if action == reset_action:
            try:
                controller = tor_controller()
                if controller is None:
                    QMessageBox.warning(self, _('Error'), _('No Tor connection available.'))
                    return
                controller.reset_conf(name)
                self._table.item(row, 1).setText('<default>')
                name_item.setForeground(QColor('#e0e0e0'))
                self._table.item(row, 3).setText('')
                stem.util.log.notice('Config reset: %s' % name)
            except Exception as exc:
                QMessageBox.warning(self, _('Error'),
                                    _('Could not reset "%s":\n%s') % (name, exc))

    def load_config(self, config_list):
        """Called by ConfigWorker via signal-slot."""
        self._all_data = config_list
        self._rebuild_table()
