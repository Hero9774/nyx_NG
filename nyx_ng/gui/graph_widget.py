# Copyright 2024, The Tor Project
# See LICENSE for licensing information

"""
Bandwidth graph: draws download/upload curves via QPainter.
"""

import collections

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QPainterPath

from nyx_ng.i18n import _

MAX_POINTS = 300


def _format_bw(bps):
    if bps < 1024:
        return '%d B/s' % bps
    elif bps < 1024 * 1024:
        return '%.1f KB/s' % (bps / 1024)
    else:
        return '%.2f MB/s' % (bps / (1024 * 1024))


class _GraphCanvas(QWidget):
    """Draws the actual curves."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._read_data = collections.deque(maxlen=MAX_POINTS)
        self._written_data = collections.deque(maxlen=MAX_POINTS)
        self.setMinimumHeight(120)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def add_point(self, read_bytes, written_bytes):
        self._read_data.append(read_bytes)
        self._written_data.append(written_bytes)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        pad_left = 60
        pad_right = 10
        pad_top = 10
        pad_bottom = 25

        graph_w = w - pad_left - pad_right
        graph_h = h - pad_top - pad_bottom

        painter.fillRect(0, 0, w, h, QColor('#0d0d1a'))

        if not self._read_data and not self._written_data:
            painter.setPen(QColor('#8888bb'))
            font = QFont('Courier New', 11)
            painter.setFont(font)
            painter.drawText(QRect(0, 0, w, h), Qt.AlignmentFlag.AlignCenter,
                             _('Waiting for bandwidth data…'))
            return

        all_values = list(self._read_data) + list(self._written_data)
        max_val = max(all_values) if all_values else 1
        if max_val == 0:
            max_val = 1

        painter.setPen(QPen(QColor('#1a1a3e'), 1, Qt.PenStyle.DotLine))
        for i in range(1, 5):
            y = pad_top + graph_h * i // 4
            painter.drawLine(pad_left, y, pad_left + graph_w, y)

        painter.setPen(QColor('#6666aa'))
        font = QFont('Courier New', 9)
        painter.setFont(font)
        for i in range(5):
            val = max_val * (4 - i) / 4
            y = pad_top + graph_h * i // 4
            painter.drawText(2, y + 4, pad_left - 4, 14,
                             Qt.AlignmentFlag.AlignRight,
                             _format_bw(val))

        def _draw_curve(data, color):
            if len(data) < 2:
                return
            points = list(data)
            n = len(points)
            path = QPainterPath()
            for i, val in enumerate(points):
                x = pad_left + graph_w * i / (n - 1)
                y = pad_top + graph_h * (1.0 - val / max_val)
                if i == 0:
                    path.moveTo(x, y)
                else:
                    path.lineTo(x, y)
            pen = QPen(QColor(color), 2)
            painter.setPen(pen)
            painter.drawPath(path)

        _draw_curve(self._read_data, '#3498db')
        _draw_curve(self._written_data, '#2ecc71')

        painter.setPen(QColor('#555577'))
        painter.drawLine(pad_left, pad_top + graph_h,
                         pad_left + graph_w, pad_top + graph_h)
        painter.drawLine(pad_left, pad_top,
                         pad_left, pad_top + graph_h)

        painter.setPen(QColor('#3498db'))
        painter.drawText(pad_left, h - 5, _('▬ Download'))
        painter.setPen(QColor('#2ecc71'))
        painter.drawText(pad_left + 120, h - 5, _('▬ Upload'))


class GraphWidget(QWidget):
    """Tab widget for the bandwidth graph with statistics bar."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._total_read = 0
        self._total_written = 0
        self._count = 0
        self._sum_read = 0
        self._sum_written = 0
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 8)
        layout.setSpacing(4)

        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)

        self._cur_down = QLabel(_('↓ Current: –'))
        self._cur_down.setStyleSheet('color: #3498db; font-weight: bold;')
        stats_layout.addWidget(self._cur_down)

        self._cur_up = QLabel(_('↑ Current: –'))
        self._cur_up.setStyleSheet('color: #2ecc71; font-weight: bold;')
        stats_layout.addWidget(self._cur_up)

        self._avg_down = QLabel(_('↓ Avg: –'))
        self._avg_down.setStyleSheet('color: #2980b9;')
        stats_layout.addWidget(self._avg_down)

        self._avg_up = QLabel(_('↑ Avg: –'))
        self._avg_up.setStyleSheet('color: #27ae60;')
        stats_layout.addWidget(self._avg_up)

        stats_layout.addStretch()

        self._total_label = QLabel(_('Total: –'))
        self._total_label.setStyleSheet('color: #a0a0c0;')
        stats_layout.addWidget(self._total_label)

        layout.addLayout(stats_layout, 0)

        self._canvas = _GraphCanvas()
        layout.addWidget(self._canvas, 1)

    def add_bandwidth(self, read_bytes, written_bytes):
        """Called by BandwidthWorker via signal-slot."""
        self._canvas.add_point(read_bytes, written_bytes)

        self._total_read += read_bytes
        self._total_written += written_bytes
        self._count += 1
        self._sum_read += read_bytes
        self._sum_written += written_bytes

        self._cur_down.setText(_('↓ Current: %s') % _format_bw(read_bytes))
        self._cur_up.setText(_('↑ Current: %s') % _format_bw(written_bytes))

        avg_r = self._sum_read / self._count
        avg_w = self._sum_written / self._count
        self._avg_down.setText(_('↓ Avg: %s') % _format_bw(avg_r))
        self._avg_up.setText(_('↑ Avg: %s') % _format_bw(avg_w))

        def _fmt_total(b):
            if b < 1024 * 1024:
                return '%.1f KB' % (b / 1024)
            elif b < 1024 * 1024 * 1024:
                return '%.2f MB' % (b / (1024 * 1024))
            else:
                return '%.3f GB' % (b / (1024 * 1024 * 1024))

        self._total_label.setText(
            _('Total: ↓ %s  ↑ %s') % (_fmt_total(self._total_read), _fmt_total(self._total_written))
        )
