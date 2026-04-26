# Copyright 2024, The Tor Project
# See LICENSE for licensing information

"""
Minimal i18n system for nyx_ng.

Translation files live in ``nyx/locale/<lang>.json``.  English is the
built-in default; no JSON file is required for it.

Usage::

  from nyx_ng.i18n import _
  label = _('Connect')          # returns 'Verbinden' when language=de

  import nyx_ng.i18n as i18n
  i18n.set_language('de')       # called once at startup from nyxrc
"""

import json
import os

_LANG = 'en'
_TRANSLATIONS = {}
_LOCALE_DIR = os.path.join(os.path.dirname(__file__), 'locale')


def set_language(lang):
    """Load *lang* translation file and activate it.

    Silently falls back to English when the JSON file is missing or
    cannot be parsed.
    """
    global _LANG, _TRANSLATIONS
    lang = lang.strip().lower()
    if lang == 'en':
        _LANG = 'en'
        _TRANSLATIONS = {}
        return

    path = os.path.join(_LOCALE_DIR, '%s.json' % lang)
    try:
        with open(path, encoding='utf-8') as fh:
            data = json.load(fh)
        _TRANSLATIONS = data.get('translations', {})
        _LANG = lang
    except (OSError, ValueError):
        _LANG = 'en'
        _TRANSLATIONS = {}


def get_language():
    """Return the currently active language code."""
    return _LANG


def _(text):
    """Translate *text* from English to the active language."""
    if not _TRANSLATIONS:
        return text
    return _TRANSLATIONS.get(text, text)
