#!/usr/bin/env python3
"""
Downloads all 4x3 SVG flags from lipis/flag-icons (GitHub) into nyx/flags/.
Run once; the SVGs are then versioned inside the package.

    python tools/download_flags.py
"""

import os
import sys
import urllib.request

BASE_URL = 'https://raw.githubusercontent.com/lipis/flag-icons/main/flags/4x3/{code}.svg'

# All ISO-3166-1 alpha-2 codes (including commonly used special codes)
CODES = [
    'ad', 'ae', 'af', 'ag', 'ai', 'al', 'am', 'ao', 'aq', 'ar', 'as', 'at',
    'au', 'aw', 'ax', 'az', 'ba', 'bb', 'bd', 'be', 'bf', 'bg', 'bh', 'bi',
    'bj', 'bl', 'bm', 'bn', 'bo', 'bq', 'br', 'bs', 'bt', 'bv', 'bw', 'by',
    'bz', 'ca', 'cc', 'cd', 'cf', 'cg', 'ch', 'ci', 'ck', 'cl', 'cm', 'cn',
    'co', 'cr', 'cu', 'cv', 'cw', 'cx', 'cy', 'cz', 'de', 'dj', 'dk', 'dm',
    'do', 'dz', 'ec', 'ee', 'eg', 'eh', 'er', 'es', 'et', 'fi', 'fj', 'fk',
    'fm', 'fo', 'fr', 'ga', 'gb', 'gd', 'ge', 'gf', 'gg', 'gh', 'gi', 'gl',
    'gm', 'gn', 'gp', 'gq', 'gr', 'gs', 'gt', 'gu', 'gw', 'gy', 'hk', 'hm',
    'hn', 'hr', 'ht', 'hu', 'id', 'ie', 'il', 'im', 'in', 'io', 'iq', 'ir',
    'is', 'it', 'je', 'jm', 'jo', 'jp', 'ke', 'kg', 'kh', 'ki', 'km', 'kn',
    'kp', 'kr', 'kw', 'ky', 'kz', 'la', 'lb', 'lc', 'li', 'lk', 'lr', 'ls',
    'lt', 'lu', 'lv', 'ly', 'ma', 'mc', 'md', 'me', 'mf', 'mg', 'mh', 'mk',
    'ml', 'mm', 'mn', 'mo', 'mp', 'mq', 'mr', 'ms', 'mt', 'mu', 'mv', 'mw',
    'mx', 'my', 'mz', 'na', 'nc', 'ne', 'nf', 'ng', 'ni', 'nl', 'no', 'np',
    'nr', 'nu', 'nz', 'om', 'pa', 'pe', 'pf', 'pg', 'ph', 'pk', 'pl', 'pm',
    'pn', 'pr', 'ps', 'pt', 'pw', 'py', 'qa', 're', 'ro', 'rs', 'ru', 'rw',
    'sa', 'sb', 'sc', 'sd', 'se', 'sg', 'sh', 'si', 'sj', 'sk', 'sl', 'sm',
    'sn', 'so', 'sr', 'ss', 'st', 'sv', 'sx', 'sy', 'sz', 'tc', 'td', 'tf',
    'tg', 'th', 'tj', 'tk', 'tl', 'tm', 'tn', 'to', 'tr', 'tt', 'tv', 'tw',
    'tz', 'ua', 'ug', 'um', 'us', 'uy', 'uz', 'va', 'vc', 've', 'vg', 'vi',
    'vn', 'vu', 'wf', 'ws', 'ye', 'yt', 'za', 'zm', 'zw',
]

def main():
    out_dir = os.path.join(os.path.dirname(__file__), '..', 'nyx', 'flags')
    out_dir = os.path.normpath(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    total = len(CODES)
    ok = 0
    fail = []

    for i, code in enumerate(CODES, 1):
        dest = os.path.join(out_dir, '%s.svg' % code)
        if os.path.exists(dest):
            ok += 1
            print('[%3d/%d] exists       %s' % (i, total, code))
            continue

        url = BASE_URL.format(code=code)
        try:
            urllib.request.urlretrieve(url, dest)
            ok += 1
            print('[%3d/%d] downloaded   %s' % (i, total, code))
        except Exception as e:
            fail.append(code)
            print('[%3d/%d] ERROR  %s  – %s' % (i, total, code, e), file=sys.stderr)

    print('\nDone: %d/%d successful.' % (ok, total))
    if fail:
        print('Failed: %s' % ', '.join(fail))


if __name__ == '__main__':
    main()
