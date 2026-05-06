# Copyright 2024, The Tor Project
# Copyright 2026, H.Ommen <hero67097@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Control port shell: interactive Tor command interpreter.
"""

import re

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QLabel, QPushButton
)
from PyQt6.QtCore import Qt, QThread, QEvent, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QTextCharFormat, QTextCursor

import stem
import stem.interpreter.commands
import stem.interpreter.autocomplete
import stem.util.log

from nyx_ng import tor_controller
from nyx_ng.i18n import _

HISTORY_LIMIT = 100

_ANSI_RE = re.compile(r'\x1B\[([0-9;]+)m')
_ANSI_COLORS = {
    '30': '#4d4d4d',
    '31': '#e74c3c',
    '32': '#2ecc71',
    '33': '#f1c40f',
    '34': '#5dade2',
    '35': '#9b59b6',
    '36': '#1abc9c',
    '37': '#ecf0f1',
}
_ANSI_DEFAULT = '#e0e0e0'


class _CommandRunner(QThread):
    """Runs a Tor command in the background."""
    result_ready = pyqtSignal(str, str)

    def __init__(self, interpreter, command, parent=None):
        super().__init__(parent)
        self._interpreter = interpreter
        self._command = command

    def run(self):
        try:
            response = self._interpreter.run_command(self._command)
            self.result_ready.emit(self._command, response or '')
        except stem.SocketClosed:
            self.result_ready.emit(self._command, _('[Connection closed]'))
        except Exception as exc:
            self.result_ready.emit(self._command, _('[Error: %s]') % exc)


class InterpreterWidget(QWidget):
    """Tab widget for the Tor control port interpreter."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._history = []
        self._history_pos = -1
        self._runner = None
        self._autocompleter = None
        self._interpreter = None
        self._build_ui()
        self._init_interpreter()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        self._output = QTextEdit()
        self._output.setReadOnly(True)
        self._output.setFont(QFont('Courier New', 12))
        self._output.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self._output)

        input_layout = QHBoxLayout()
        self._prompt_label = QLabel('>>> ')
        self._prompt_label.setStyleSheet(
            'color: #2ecc71; font-family: "Courier New"; font-size: 12px; font-weight: bold;'
        )
        input_layout.addWidget(self._prompt_label)

        self._input = QLineEdit()
        self._input.setFont(QFont('Courier New', 12))
        self._input.setPlaceholderText(_('Enter Tor command (Tab = autocomplete)…'))
        self._input.returnPressed.connect(self._execute)
        self._input.installEventFilter(self)
        input_layout.addWidget(self._input)

        clear_btn = QPushButton(_('Clear'))
        clear_btn.setMaximumWidth(80)
        clear_btn.clicked.connect(self._clear)
        input_layout.addWidget(clear_btn)

        layout.addLayout(input_layout)

        hint = QLabel(_('↑↓ Verlauf  |  Tab: Autovervollständigung  |  /help für weitere Infos'))
        hint.setStyleSheet('color: #8888aa; font-size: 11px;')
        layout.addWidget(hint)

    def _init_interpreter(self):
        controller = tor_controller()
        if controller:
            try:
                self._autocompleter = stem.interpreter.autocomplete.Autocompleter(controller)
                self._interpreter = stem.interpreter.commands.ControlInterpreter(controller)
                self._print_line(_('Tor Control Port Shell ready. Type HELP for help.'), '#9b59b6')
            except Exception as exc:
                self._print_line(_('[Error initializing: %s]') % exc, '#e74c3c')
        else:
            self._print_line(_('[No Tor controller available]'), '#e74c3c')

    def _print_line(self, text, color='#e0e0e0'):
        cursor = self._output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cursor.insertText(text + '\n', fmt)
        self._output.setTextCursor(cursor)
        self._output.ensureCursorVisible()

    def _print_ansi_line(self, text):
        cursor = self._output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        pos = 0
        current_color = _ANSI_DEFAULT
        bold = False

        for match in _ANSI_RE.finditer(text):
            if match.start() > pos:
                fmt = QTextCharFormat()
                fmt.setForeground(QColor(current_color))
                if bold:
                    fmt.setFontWeight(700)
                cursor.insertText(text[pos:match.start()], fmt)

            codes = match.group(1).split(';')
            if '0' in codes:
                current_color = _ANSI_DEFAULT
                bold = False
            for code in codes:
                if code == '1':
                    bold = True
                elif code in _ANSI_COLORS:
                    current_color = _ANSI_COLORS[code]

            pos = match.end()

        if pos < len(text):
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(current_color))
            if bold:
                fmt.setFontWeight(700)
            cursor.insertText(text[pos:], fmt)

        cursor.insertText('\n', QTextCharFormat())
        self._output.setTextCursor(cursor)
        self._output.ensureCursorVisible()

    def _execute(self):
        command = self._input.text().strip()
        if not command:
            return

        if not self._history or self._history[-1] != command:
            self._history.append(command)
            if len(self._history) > HISTORY_LIMIT:
                self._history.pop(0)
        self._history_pos = -1

        self._input.clear()
        self._print_line('>>> ' + command, '#2ecc71')

        if self._interpreter is None:
            self._print_line(_('[No interpreter available]'), '#e74c3c')
            return

        self._runner = _CommandRunner(self._interpreter, command)
        self._runner.result_ready.connect(self._on_result)
        self._runner.start()

    def _on_result(self, command, response):
        if response:
            for line in response.splitlines():
                self._print_ansi_line(line)
        self._print_line('')

    def _clear(self):
        self._output.clear()

    def eventFilter(self, obj, event):
        if obj is self._input and event.type() == QEvent.Type.KeyPress:
            key = event.key()

            if key == Qt.Key.Key_Up:
                if self._history:
                    if self._history_pos == -1:
                        self._history_pos = len(self._history) - 1
                    elif self._history_pos > 0:
                        self._history_pos -= 1
                    self._input.setText(self._history[self._history_pos])
                return True

            elif key == Qt.Key.Key_Down:
                if self._history_pos != -1:
                    self._history_pos += 1
                    if self._history_pos >= len(self._history):
                        self._history_pos = -1
                        self._input.clear()
                    else:
                        self._input.setText(self._history[self._history_pos])
                return True

            elif key == Qt.Key.Key_Tab:
                self._autocomplete()
                return True

        return super().eventFilter(obj, event)

    def _autocomplete(self):
        if not self._autocompleter:
            return

        text = self._input.text()
        try:
            matches = self._autocompleter.matches(text)
            if len(matches) == 1:
                self._input.setText(matches[0] + ' ')
            elif len(matches) > 1:
                self._print_line('\n'.join(matches[:20]), '#3498db')
        except Exception:
            pass
