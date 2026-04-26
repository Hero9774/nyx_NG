# Copyright 2024, The Tor Project
# See LICENSE for licensing information

"""
Log panel: displays Tor and nyx log messages with colour coding.
"""

import time
import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QLineEdit, QComboBox, QLabel, QPushButton, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont

from nyx_ng.gui.theme import LOG_COLORS
from nyx_ng.i18n import _

MAX_LOG_ENTRIES = 1000

_LEVEL_SEVERITY = {
    'ERR': 0, 'NYX_ERROR': 0,
    'WARN': 1, 'NYX_WARNING': 1,
    'NOTICE': 2, 'NYX_NOTICE': 2,
    'INFO': 3,
    'DEBUG': 4,
}
_FILTER_MIN_SEVERITY = {'ALL': 99, 'ERR': 0, 'WARN': 1, 'NOTICE': 2, 'INFO': 3, 'DEBUG': 4}


class LogWidget(QWidget):
    """Tab widget for the Tor log."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._all_entries = []
        self._auto_scroll = True
        self._filter_text = ''
        self._filter_level = 'NOTICE'
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        toolbar = QHBoxLayout()

        toolbar.addWidget(QLabel(_('Filter:')))

        self._filter_input = QLineEdit()
        self._filter_input.setPlaceholderText(_('Search term…'))
        self._filter_input.textChanged.connect(self._apply_filter)
        self._filter_input.setMaximumWidth(250)
        toolbar.addWidget(self._filter_input)

        toolbar.addWidget(QLabel(_('Level:')))

        self._level_combo = QComboBox()
        self._level_combo.addItems(['ALL', 'ERR', 'WARN', 'NOTICE', 'INFO', 'DEBUG'])
        self._level_combo.setCurrentText('NOTICE')
        self._level_combo.currentTextChanged.connect(self._on_level_change)
        self._level_combo.setMaximumWidth(110)
        toolbar.addWidget(self._level_combo)

        toolbar.addStretch()

        self._auto_scroll_cb = QCheckBox(_('Auto-Scroll'))
        self._auto_scroll_cb.setChecked(True)
        self._auto_scroll_cb.toggled.connect(self._toggle_scroll)
        toolbar.addWidget(self._auto_scroll_cb)

        clear_btn = QPushButton(_('Clear'))
        clear_btn.setMaximumWidth(80)
        clear_btn.clicked.connect(self._clear)
        toolbar.addWidget(clear_btn)

        layout.addLayout(toolbar)

        self._list = QListWidget()
        self._list.setFont(QFont('Courier New', 11))
        self._list.setWordWrap(False)
        self._list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        layout.addWidget(self._list)

        self._count_label = QLabel(_('0 entries'))
        self._count_label.setStyleSheet('color: #6666aa; font-size: 11px;')
        layout.addWidget(self._count_label)

    def _toggle_scroll(self, checked):
        self._auto_scroll = checked

    def _on_level_change(self, level):
        self._filter_level = level
        self._rebuild_list()

    def _apply_filter(self, text):
        self._filter_text = text.lower()
        self._rebuild_list()

    def _clear(self):
        self._all_entries.clear()
        self._list.clear()
        self._count_label.setText(_('0 entries'))

    def _entry_matches(self, level, message):
        if self._filter_level != 'ALL':
            min_sev = _FILTER_MIN_SEVERITY.get(self._filter_level, 99)
            entry_sev = _LEVEL_SEVERITY.get(level, 3)
            if entry_sev > min_sev:
                return False
        if self._filter_text and self._filter_text not in message.lower():
            return False
        return True

    def _rebuild_list(self):
        self._list.clear()
        shown = 0
        for level, ts, message in self._all_entries:
            if self._entry_matches(level, message):
                self._add_item(level, ts, message)
                shown += 1
        self._count_label.setText(_('%d / %d entries') % (shown, len(self._all_entries)))
        if self._auto_scroll:
            self._list.scrollToBottom()

    def _add_item(self, level, ts, message):
        time_str = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        text = '[%s] %s  %s' % (level.ljust(11), time_str, message)
        item = QListWidgetItem(text)

        color = LOG_COLORS.get(level, '#e0e0e0')
        item.setForeground(QColor(color))

        if level in ('ERR', 'NYX_ERROR'):
            item.setBackground(QColor('#2a0a0a'))
        elif level in ('WARN', 'NYX_WARNING'):
            item.setBackground(QColor('#2a1a0a'))

        self._list.addItem(item)

    def add_log_entry(self, entry):
        """Called by LogWorker via signal-slot."""
        level = entry.type
        ts = entry.timestamp
        message = entry.message

        self._all_entries.append((level, ts, message))

        if len(self._all_entries) > MAX_LOG_ENTRIES:
            self._all_entries.pop(0)

        if self._entry_matches(level, message):
            self._add_item(level, ts, message)
            total = self._list.count()
            self._count_label.setText(_('%d entries') % total)

            if self._auto_scroll:
                self._list.scrollToBottom()
