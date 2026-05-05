# Copyright 2009-2019, Damian Johnson and The Tor Project
# Copyright 2026, H.Ommen <hero67097@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import nyx_ng
import nyx_ng.curses

if '--demo-glyphs' in sys.argv:
    nyx_ng.curses.demo_glyphs()
else:
    nyx_ng.main()
