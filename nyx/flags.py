# Copyright 2024, The Tor Project
# See LICENSE for licensing information

"""
Stellt SVG-Flaggen-Icons aus dem mitgelieferten nyx/flags/-Verzeichnis
als QPixmap/QIcon für PyQt6 bereit (lipis/flag-icons, MIT-Lizenz).
"""

import os

_FLAGS_DIR = os.path.join(os.path.dirname(__file__), 'flags')

# Laufzeit-Cache: (code, width, height) → QPixmap | None
_pixmap_cache = {}


def get_flag_pixmap(code, width=28, height=21):
    """
    Gibt ein QPixmap der Flagge für den angegebenen ISO-3166-1-Alpha-2-Code zurück.
    Gibt None zurück, wenn keine passende SVG-Datei vorhanden ist.

    Erfordert PyQt6.QtSvg (im Standard-PyQt6-Paket enthalten).
    """
    if not code or len(code) != 2:
        return None

    code = code.upper()
    cache_key = (code, width, height)

    if cache_key in _pixmap_cache:
        return _pixmap_cache[cache_key]

    svg_path = os.path.join(_FLAGS_DIR, '%s.svg' % code.lower())
    if not os.path.exists(svg_path):
        _pixmap_cache[cache_key] = None
        return None

    try:
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtGui import QPixmap, QPainter
        from PyQt6.QtCore import Qt

        renderer = QSvgRenderer(svg_path)
        if not renderer.isValid():
            _pixmap_cache[cache_key] = None
            return None

        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        _pixmap_cache[cache_key] = pixmap
        return pixmap
    except Exception:
        _pixmap_cache[cache_key] = None
        return None
